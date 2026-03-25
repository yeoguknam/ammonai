import os, json, argparse
from datetime import datetime, timedelta
from pathlib import Path

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TOOLS_FILE = Path(__file__).parent.parent / "data" / "tools.json"

CATEGORIES = [
    "Data Analysis", "Writing & Content",
    "Automation & Agents", "Design & Creative",
    "Video & Audio", "Coding & Development",
]

def load_existing_tools():
    if TOOLS_FILE.exists():
        with open(TOOLS_FILE) as f:
            return json.load(f)
    return []

def save_tools(tools):
    TOOLS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOOLS_FILE, "w") as f:
        json.dump(tools, f, indent=2, ensure_ascii=False)

def discover_new_tools():
    if not ANTHROPIC_API_KEY:
        print("[!] No ANTHROPIC_API_KEY set")
        return []
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = datetime.now().strftime("%Y-%m-%d")
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    existing = load_existing_tools()
    existing_names = [t["name"].lower() for t in existing]
    all_new = []
    for cat in CATEGORIES:
        print(f"Searching: {cat}")
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content": f"""Find NEW AI tools launched between {last_week} and {today} in category "{cat}".
Search Product Hunt, TechCrunch, GitHub trending, AI newsletters.
Already in our database: {', '.join(existing_names[:30])}
Return ONLY a JSON array of objects with: name, slug, company, category, description_en, description_ko, website, pricing, tags, rating (1-10).
If no new tools, return []."""}],
            )
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            new_tools = json.loads(text.strip())
            new_tools = [t for t in new_tools if t["name"].lower() not in existing_names]
            print(f"  Found {len(new_tools)} new tools")
            all_new.extend(new_tools)
        except Exception as e:
            print(f"  Error: {e}")
    return all_new

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()
    print("=" * 40)
    print("AMMONAI Weekly Discovery")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 40)
    new_tools = discover_new_tools()
    if not new_tools:
        print("No new tools found.")
        return
    for t in new_tools:
        t["added_date"] = datetime.now().strftime("%Y-%m-%d")
        print(f"  + {t['name']} ({t.get('rating','?')}/10)")
    if args.dry:
        print("[DRY RUN] No files changed.")
        return
    existing = load_existing_tools()
    all_tools = existing + new_tools
    all_tools.sort(key=lambda t: t.get("rating", 0), reverse=True)
    save_tools(all_tools)
    print(f"Saved {len(all_tools)} total tools.")

if __name__ == "__main__":
    main()
