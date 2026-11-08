#!/usr/bin/env bash
# Runs daily on tilion: scrape DAXBench, commit the CSV to the public data repo if it changed.
# Assumes the repo is cloned at ~/Projects/ai-frontier-data with push access.
set -euo pipefail
REPO="$HOME/Projects/ai-frontier-data"
cd "$REPO"
git pull -q --ff-only
python3 "$REPO/scripts/daxbench_scrape.py" "$REPO/data/daxbench.csv.new"
# ignore the scrapedAt column when deciding whether anything changed
if [ -f data/daxbench.csv ] && diff -q <(cut -d, -f1-11 data/daxbench.csv) <(cut -d, -f1-11 data/daxbench.csv.new) >/dev/null; then
  rm data/daxbench.csv.new; exit 0
fi
mv data/daxbench.csv.new data/daxbench.csv
mkdir -p data/history && cp data/daxbench.csv "data/history/daxbench-$(date -u +%F).csv"
git add data && git commit -qm "DAXBench snapshot $(date -u +%F)" && git push -q
