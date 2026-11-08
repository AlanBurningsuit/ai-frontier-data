"""Scrape the public DAXBench leaderboard (https://www.daxbench.com) into a CSV.

Runs daily on tilion. Reads the public page only (robots.txt allows /, blocks /api/).
Credit: DAXBench by Maxim Anatsko in collaboration with SQLBI.
Usage: python3 daxbench_scrape.py OUT.csv
Exits non-zero and leaves OUT.csv untouched if the page shape changes.
"""
import csv, json, sys, urllib.request
from datetime import datetime, timezone

URL = "https://www.daxbench.com/"
UA = "burningsuit-showcase/0.1 (+https://burningsuit.co.uk; daily, page only)"
FIELDS = ["modelId", "modelName", "provider", "pointsScore", "overallScore", "accuracyScore",
          "syntaxScore", "tasksCorrect", "totalTasks", "evaluatedAt", "benchmarkVersionId", "scrapedAt"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def entries(html):
    h = html.replace('\\"', '"')
    key = '"initialEntries":'
    i = h.find(key)
    if i < 0:
        raise ValueError("initialEntries not found: page shape changed")
    i += len(key)
    depth = 0
    for j in range(i, len(h)):
        if h[j] == "[":
            depth += 1
        elif h[j] == "]":
            depth -= 1
            if depth == 0:
                return json.loads(h[i:j + 1])
    raise ValueError("unterminated initialEntries array")


def main(out):
    rows = entries(fetch(URL))
    if len(rows) < 20:
        raise ValueError(f"only {len(rows)} entries: refusing to overwrite")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for e in rows:
            r = {k: e.get(k) for k in FIELDS}
            r["evaluatedAt"] = (e.get("evaluatedAt") or "")[:19].replace("T", " ")
            r["scrapedAt"] = now
            w.writerow(r)
    print(f"{len(rows)} models written to {out}")


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception as ex:
        print(f"daxbench scrape failed: {ex}", file=sys.stderr)
        sys.exit(1)
