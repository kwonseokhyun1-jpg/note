#!/usr/bin/env python3
"""
Find VP / Director / Manager contacts at companies listed as n8n or Zapier customers.

Sources:
  - https://n8n.io/case-studies/
  - https://zapier.com/customer-stories (and related blog case studies)

Usage:
  export APOLLO_API_KEY='your-key'
  python3 leads/apollo_n8n_zapier_leads.py --output leads/n8n-zapier-vp-leads.csv --limit 100
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)

API_BASE = "https://api.apollo.io/api/v1"
SENIORITIES = ["vp", "director", "head", "manager", "senior"]
TITLE_KEYWORDS = [
    "operations",
    "automation",
    "integration",
    "rev ops",
    "revenue operations",
    "marketing operations",
    "support operations",
    "business systems",
    "information technology",
    "workflow",
    "digital",
    "platform",
    "engineering manager",
    "technical program",
    "product operations",
    "sales operations",
    "IT",
]


def api_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json",
        "x-api-key": api_key,
    }


def load_companies(path: Path) -> dict[str, list[str]]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def bulk_match(api_key: str, person_ids: list[str]) -> list[dict[str, Any]]:
    all_matches: list[dict[str, Any]] = []
    for i in range(0, len(person_ids), 10):
        chunk = person_ids[i : i + 10]
        payload = {
            "details": [{"id": pid} for pid in chunk],
            "reveal_personal_emails": False,
            "reveal_phone_number": False,
        }
        resp = requests.post(
            f"{API_BASE}/people/bulk_match",
            headers=api_headers(api_key),
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        all_matches.extend(m for m in resp.json().get("matches") or [] if m)
        time.sleep(0.35)
    return all_matches


def search_company(
    api_key: str,
    company: str,
    per_page: int = 6,
    us_only: bool = True,
) -> list[str]:
    params: list[tuple[str, str]] = [
        ("q_organization_name", company),
        ("per_page", str(per_page)),
        ("page", "1"),
    ]
    if us_only:
        params.append(("person_locations[]", "United States"))
    for seniority in SENIORITIES:
        params.append(("person_seniorities[]", seniority))
    for title in TITLE_KEYWORDS[:10]:
        params.append(("person_titles[]", title))

    query = "&".join(f"{k}={quote(v)}" for k, v in params)
    resp = requests.post(
        f"{API_BASE}/mixed_people/api_search?{query}",
        headers=api_headers(api_key),
        timeout=60,
    )
    resp.raise_for_status()
    return [p["id"] for p in resp.json().get("people") or [] if p.get("id")]


def collect_leads(
    api_key: str,
    companies: dict[str, list[str]],
    limit: int,
    per_company: int,
    us_only: bool,
) -> list[dict[str, Any]]:
    seen_ids: set[str] = set()
    rows: list[dict[str, Any]] = []
    per_platform = limit // 2

    for platform, names in companies.items():
        platform_count = 0
        for company in names:
            if platform_count >= per_platform or len(rows) >= limit:
                break
            try:
                ids = search_company(api_key, company, per_page=per_company, us_only=us_only)
            except requests.HTTPError as exc:
                print(f"skip {company}: {exc}", file=sys.stderr)
                continue

            new_ids = [pid for pid in ids if pid not in seen_ids][:per_company]
            if not new_ids:
                if us_only:
                    try:
                        ids = search_company(api_key, company, per_page=per_company, us_only=False)
                        new_ids = [pid for pid in ids if pid not in seen_ids][:per_company]
                    except requests.HTTPError:
                        continue
                if not new_ids:
                    continue

            for pid in new_ids:
                seen_ids.add(pid)

            matches = bulk_match(api_key, new_ids)
            for match in matches:
                rows.append(
                    {
                        "Name": match.get("name", ""),
                        "Title": match.get("title", ""),
                        "Company": (match.get("organization") or {}).get("name", company),
                        "Automation Platform": platform,
                        "Email": match.get("email", ""),
                        "LinkedIn": match.get("linkedin_url", ""),
                        "Location": ", ".join(
                            x
                            for x in [match.get("city"), match.get("state"), match.get("country")]
                            if x
                        ),
                        "Apollo ID": match.get("id", ""),
                    }
                )
                platform_count += 1
                if platform_count >= per_platform or len(rows) >= limit:
                    break

            print(f"{company} ({platform}): +{len(matches)} | total {len(rows)}")
            time.sleep(0.4)

    return rows[:limit]


def write_csv(path: str, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "Name",
        "Title",
        "Company",
        "Automation Platform",
        "Email",
        "LinkedIn",
        "Location",
        "Apollo ID",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apollo leads at n8n/Zapier customer companies")
    parser.add_argument("--output", default="leads/n8n-zapier-vp-leads.csv")
    parser.add_argument("--companies", default="leads/n8n_zapier_companies.json")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--per-company", type=int, default=4)
    parser.add_argument("--include-global", action="store_true", help="Include non-US contacts")
    args = parser.parse_args()

    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not api_key:
        print("Set APOLLO_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    companies = load_companies(Path(args.companies))
    rows = collect_leads(
        api_key,
        companies,
        limit=args.limit,
        per_company=args.per_company,
        us_only=not args.include_global,
    )
    write_csv(args.output, rows)
    with_email = sum(1 for r in rows if r.get("Email"))
    print(f"Wrote {len(rows)} rows ({with_email} with email) to {args.output}")


if __name__ == "__main__":
    main()
