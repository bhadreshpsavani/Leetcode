#!/usr/bin/env python3
"""
fetch_daily.py
 - Attempts to fetch LeetCode's "activeDailyChallengeQuestion" metadata using LeetCode's GraphQL endpoint.
 - Writes a small JSON with: { "title", "slug", "link", "date", "difficulty" }
Usage:
  python scripts/fetch_daily.py --out metadata.json
  python scripts/fetch_daily.py --slug two-sum --out metadata.json
"""

import argparse, json, requests, datetime, sys

GRAPHQL_URL = "https://leetcode.com/graphql"

DAILY_QUERY = """
query activeDailyChallengeQuestion {
  activeDailyCodingChallengeQuestion {
    date
    userStatus
    link
    question {
      title
      titleSlug
      difficulty
      content
    }
  }
}
"""

def fetch_active(session=None):
    s = session or requests.Session()
    r = s.post(GRAPHQL_URL, json={"query": DAILY_QUERY}, headers={"Content-Type":"application/json"})
    r.raise_for_status()
    data = r.json()
    try:
        node = data["data"]["activeDailyCodingChallengeQuestion"]
        q = node["question"]
        return {
            "title": q["title"],
            "slug": q["titleSlug"],
            "link": "https://leetcode.com/problems/" + q["titleSlug"] + "/",
            "date": node.get("date") or datetime.date.today().isoformat(),
            "difficulty": q.get("difficulty")
        }
    except Exception as e:
        raise RuntimeError("Could not parse LeetCode response: " + str(e))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--slug", required=False, help="Provide a slug (e.g. two-sum) to bypass fetching")
    args = ap.parse_args()

    if args.slug:
        meta = {
            "title": args.slug.replace("-", " ").title(),
            "slug": args.slug,
            "link": f"https://leetcode.com/problems/{args.slug}/",
            "date": datetime.date.today().isoformat(),
            "difficulty": "Unknown"
        }
    else:
        try:
            meta = fetch_active()
        except Exception as e:
            print("Warning: fetch_active failed:", e, file=sys.stderr)
            print("Falling back to a default placeholder.", file=sys.stderr)
            meta = {
                "title": "Manual placeholder",
                "slug": datetime.date.today().isoformat(),
                "link": "",
                "date": datetime.date.today().isoformat(),
                "difficulty": "Unknown"
            }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("Wrote", args.out)

if __name__ == "__main__":
    main()
