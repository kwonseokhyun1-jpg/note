#!/usr/bin/env python3
"""
Find VP / Director / Manager contacts at n8n and Zapier customer companies,
prioritizing roles most likely to own workflow automation tooling.

Sources:
  - https://n8n.io/case-studies/
  - https://zapier.com/customer-stories

Usage:
  export APOLLO_API_KEY='your-key'
  python3 leads/apollo_n8n_zapier_leads.py --limit 200 --merge-existing
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
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
SENIORITIES = ["vp", "director", "head", "manager", "senior", "lead"]

# Titles most likely to configure / own Zapier or n8n
HIGH_INTENT_TITLES = [
    "marketing operations",
    "marketing automation",
    "rev ops",
    "revenue operations",
    "sales operations",
    "support operations",
    "business systems",
    "automation manager",
    "automation lead",
    "workflow automation",
    "workflow manager",
    "integrations manager",
    "integration manager",
    "director of integrations",
    "director of automation",
    "head of automation",
    "vp automation",
    "vp operations",
    "director of operations",
    "business operations",
    "gtm operations",
    "product operations",
    "systems manager",
    "platform operations",
    "no code",
    "low code",
    "process automation",
    "it operations",
    "digital operations",
]

BROAD_TITLES = [
    "operations",
    "automation",
    "integration",
    "workflow",
    "business systems",
    "information technology",
]

HIGH_INTENT_KEYWORDS = [
    "automation",
    "workflow",
    "integration",
    "zapier",
    "n8n",
    "no-code",
    "no code",
    "low-code",
    "low code",
    "ipaas",
    "rev ops",
    "revops",
    "revenue operations",
    "marketing operations",
    "marketing ops",
    "mops",
    "support operations",
    "sales operations",
    "business systems",
    "process automation",
    "gtm operations",
    "systems manager",
    "digital operations",
    "platform operations",
]

LOW_INTENT_KEYWORDS = [
    "security architect",
    "security engineer",
    "cyber",
    "auditor",
    "accountant",
    "recruiter",
    "recruiting",
    "human resources",
    " hr ",
    "legal counsel",
    "attorney",
    "nurse",
    "physician",
    "sales representative",
    "account executive",
    "customer success manager",
    "software engineer",
    "developer",
    "data scientist",
]


def api_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json",
        "x-api-key": api_key,
    }


def relevance_score(title: str | None) -> int:
    t = f" {(title or '').lower()} "
    if any(k in t for k in LOW_INTENT_KEYWORDS):
        return -5
    score = 0
    for kw in HIGH_INTENT_KEYWORDS:
        if kw in t:
            weight = 3 if kw in {"automation", "workflow", "integration", "zapier", "n8n", "marketing operations", "rev ops", "revops"} else 2
            score += weight
    if any(x in t for x in ["manager", "director", "head", "vp", "vice president", "lead"]):
        score += 1
    return score


def load_companies(path: Path) -> dict[str, Any]:
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


def match_by_linkedin(api_key: str, linkedin_url: str) -> dict[str, Any] | None:
    url = f"{API_BASE}/people/match?linkedin_url={quote(linkedin_url)}&reveal_personal_emails=false"
    resp = requests.post(url, headers=api_headers(api_key), timeout=60)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json().get("person")


def search_company(
    api_key: str,
    company: str,
    titles: list[str],
    per_page: int = 10,
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
    for title in titles:
        params.append(("person_titles[]", title))

    query = "&".join(f"{k}={quote(v)}" for k, v in params)
    resp = requests.post(
        f"{API_BASE}/mixed_people/api_search?{query}",
        headers=api_headers(api_key),
        timeout=60,
    )
    resp.raise_for_status()
    return [p["id"] for p in resp.json().get("people") or [] if p.get("id")]


def match_to_row(match: dict[str, Any], platform: str, company: str, note: str = "") -> dict[str, Any]:
    title = match.get("title", "")
    return {
        "Name": match.get("name", ""),
        "Title": title,
        "Company": (match.get("organization") or {}).get("name", company),
        "Automation Platform": platform,
        "Relevance Score": relevance_score(title),
        "Email": match.get("email", ""),
        "LinkedIn": match.get("linkedin_url", ""),
        "Location": ", ".join(
            x for x in [match.get("city"), match.get("state"), match.get("country")] if x
        ),
        "Apollo ID": match.get("id", ""),
        "Notes": note,
    }


def enrich_named_contacts(api_key: str, contacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for contact in contacts:
        linkedin = contact.get("linkedin", "").strip()
        if not linkedin:
            continue
        person = match_by_linkedin(api_key, linkedin)
        if not person:
            continue
        row = match_to_row(
            person,
            contact.get("platform", ""),
            contact.get("company", ""),
            contact.get("note", "Named in case study"),
        )
        if row["Relevance Score"] < 0:
            row["Relevance Score"] = 5
        rows.append(row)
        time.sleep(0.3)
    return rows


def fetch_company_leads(
    api_key: str,
    company: str,
    platform: str,
    seen_ids: set[str],
    per_company: int,
    us_only: bool,
    min_score: int,
) -> list[dict[str, Any]]:
    collected: list[tuple[int, dict[str, Any]]] = []

    for titles, us in [(HIGH_INTENT_TITLES, us_only), (HIGH_INTENT_TITLES, False), (BROAD_TITLES, us_only)]:
        if len(collected) >= per_company * 3:
            break
        try:
            ids = search_company(api_key, company, titles, per_page=15, us_only=us)
        except requests.HTTPError:
            continue

        new_ids = [pid for pid in ids if pid not in seen_ids]
        if not new_ids:
            continue

        matches = bulk_match(api_key, new_ids[:15])
        for match in matches:
            pid = match.get("id")
            if not pid or pid in seen_ids:
                continue
            row = match_to_row(match, platform, company)
            score = row["Relevance Score"]
            if score < min_score:
                continue
            seen_ids.add(pid)
            collected.append((score, row))

        time.sleep(0.35)

    collected.sort(key=lambda x: x[0], reverse=True)
    return [row for _, row in collected[:per_company]]


def collect_leads(
    api_key: str,
    companies: dict[str, Any],
    limit: int,
    per_company: int,
    us_only: bool,
    min_score: int,
) -> list[dict[str, Any]]:
    seen_ids: set[str] = set()
    rows: list[dict[str, Any]] = []

    named = companies.get("named_case_study_contacts") or []
    for row in enrich_named_contacts(api_key, named):
        pid = row.get("Apollo ID")
        if pid:
            seen_ids.add(pid)
        rows.append(row)
    print(f"named case study contacts: {len(rows)}")

    per_platform = (limit - len(rows)) // 2
    for platform in ("n8n", "zapier"):
        platform_count = 0
        names = companies.get(platform) or []
        for company in names:
            if platform_count >= per_platform or len(rows) >= limit:
                break
            found = fetch_company_leads(
                api_key, company, platform, seen_ids, per_company, us_only, min_score
            )
            rows.extend(found)
            platform_count += len(found)
            if found:
                print(f"{company} ({platform}): +{len(found)} | total {len(rows)}")
            time.sleep(0.3)

    rows.sort(key=lambda r: r.get("Relevance Score", 0), reverse=True)
    return rows[:limit]


def read_existing(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def merge_rows(existing: list[dict[str, Any]], new_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for row in existing + new_rows:
        key = row.get("Apollo ID") or f"{row.get('Name')}|{row.get('Company')}"
        if key not in by_id or int(row.get("Relevance Score") or 0) > int(by_id[key].get("Relevance Score") or 0):
            by_id[key] = row
    merged = list(by_id.values())
    merged.sort(key=lambda r: int(r.get("Relevance Score") or 0), reverse=True)
    return merged


def write_csv(path: str, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "Name",
        "Title",
        "Company",
        "Automation Platform",
        "Relevance Score",
        "Email",
        "LinkedIn",
        "Location",
        "Apollo ID",
        "Notes",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_google_sheet_csv(path: str, rows: list[dict[str, Any]]) -> None:
    fields = ["Name", "Company", "Account", "Role", "Department", "Phone", "Email", "LinkedIn", "Location", "Apollo ID", "Notes"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            notes = r.get("Notes", "")
            score = r.get("Relevance Score", "")
            if score:
                notes = f"Relevance: {score}" + (f" | {notes}" if notes else "")
            w.writerow({
                "Name": r.get("Name", ""),
                "Company": r.get("Company", ""),
                "Account": "",
                "Role": r.get("Title", ""),
                "Department": f"{r.get('Automation Platform', '')} customer",
                "Phone": "",
                "Email": r.get("Email", ""),
                "LinkedIn": r.get("LinkedIn", ""),
                "Location": r.get("Location", ""),
                "Apollo ID": r.get("Apollo ID", ""),
                "Notes": notes,
            })


def main() -> None:
    parser = argparse.ArgumentParser(description="Apollo leads at n8n/Zapier customer companies")
    parser.add_argument("--output", default="leads/n8n-zapier-vp-leads.csv")
    parser.add_argument("--google-sheet-output", default="leads/google-sheet-n8n-zapier-import.csv")
    parser.add_argument("--companies", default="leads/n8n_zapier_companies.json")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--per-company", type=int, default=3)
    parser.add_argument("--min-score", type=int, default=2, help="Minimum title relevance score")
    parser.add_argument("--include-global", action="store_true")
    parser.add_argument("--merge-existing", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not api_key:
        print("Set APOLLO_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    companies = load_companies(Path(args.companies))
    new_rows = collect_leads(
        api_key,
        companies,
        limit=args.limit,
        per_company=args.per_company,
        us_only=not args.include_global,
        min_score=args.min_score,
    )

    if args.merge_existing:
        existing = read_existing(Path(args.output))
        rows = merge_rows(existing, new_rows)
    else:
        rows = new_rows

    write_csv(args.output, rows)
    write_google_sheet_csv(args.google_sheet_output, rows)
    with_email = sum(1 for r in rows if r.get("Email"))
    high = sum(1 for r in rows if int(r.get("Relevance Score") or 0) >= 4)
    print(f"Wrote {len(rows)} rows ({with_email} emails, {high} high-intent) to {args.output}")


if __name__ == "__main__":
    main()
