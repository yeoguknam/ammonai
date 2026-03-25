# ============================================================
# AMMONAI — Weekly AI Tool Discovery (Automated)
# ============================================================
# Runs every Monday at 9:00 AM PST (= 17:00 UTC)
# Discovers new AI tools, rates them, and updates the site.
#
# SETUP:
#   1. Go to your GitHub repo → Settings → Secrets → Actions
#   2. Add secret: ANTHROPIC_API_KEY = sk-ant-...
#   3. This workflow will run automatically every Monday
# ============================================================

name: Weekly AI Tool Update

on:
  schedule:
    # Every Monday at 17:00 UTC = 9:00 AM PST
    - cron: '0 17 * * 1'
  
  # Also allow manual trigger
  workflow_dispatch:

jobs:
  discover-tools:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install anthropic requests

      - name: Run weekly discovery
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/weekly_update.py

      - name: Commit and push changes
        run: |
          git config --local user.email "ammonai-bot@ammonai.ai"
          git config --local user.name "AMMONAI Bot"
          git add data/
          git diff --staged --quiet || git commit -m "🔄 Weekly update: $(date +'%Y-%m-%d')"
          git push
