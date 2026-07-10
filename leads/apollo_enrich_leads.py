#!/usr/bin/env python3
"""
Fetch US ERP/SAP/B2B/CIMS leads from Apollo and enrich with email + LinkedIn.

Requires: APOLLO_API_KEY (master key from Apollo Settings > Integrations > API)

Usage:
  export APOLLO_API_KEY='your-key'
  python3 leads/apollo_enrich_leads.py --output leads/apollo-enriched-leads.csv

Optional: enrich an existing CSV of LinkedIn URLs
  python3 leads/apollo_enrich_leads.py --input leads/apollo-erp-sap-b2b-cims-us-leads.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from typing import Any
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)

API_BASE = "https://api.apollo.io/api/v1"
US_LOCATIONS = ["United States"]

# Title groups aligned to the requested personas (US-first)
SEARCH_GROUPS: dict[str, list[str]] = {
    "VP ERP": [
        "vp erp",
        "vice president erp",
        "vp of erp",
        "vp enterprise resource planning",
    ],
    "ERP Director": [
        "director erp",
        "director enterprise resource planning",
        "director erp applications",
        "director erp transformation",
    ],
    "ERP Manager": [
        "erp manager",
        "manager erp",
        "manager enterprise resource planning",
        "manager of erp",
    ],
    "SAP": [
        "director sap",
        "sap director",
        "global sap director",
        "vp sap",
        "sap erp director",
        "sap manager",
    ],
    "B2B Integration": [
        "b2b integration",
        "director b2b integration",
        "b2b edi",
        "director edi",
        "director digital integrations",
        "edi manager",
    ],
    "CIMS / CIMdata": [
        "cimdata",
        "computer integrated manufacturing",
        "cims",
        "manufacturing execution systems",
        "mes director",
    ],
}


def api_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json",
        "x-api-key": api_key,
    }


def search_people(
    api_key: str,
    titles: list[str],
    page: int = 1,
    per_page: int = 25,
) -> dict[str, Any]:
    params: list[tuple[str, str]] = [("per_page", str(per_page)), ("page", str(page))]
    for title in titles:
        params.append(("person_titles[]", title))
    for loc in US_LOCATIONS:
        params.append(("person_locations[]", loc))

    query = "&".join(f"{k}={quote(v)}" for k, v in params)
    url = f"{API_BASE}/mixed_people/api_search?{query}"
    resp = requests.post(url, headers=api_headers(api_key), timeout=60)
    resp.raise_for_status()
    return resp.json()


def bulk_match(api_key: str, person_ids: list[str]) -> dict[str, Any]:
    all_matches: list[dict[str, Any]] = []
    for i in range(0, len(person_ids), 10):
        chunk = person_ids[i : i + 10]
        payload = {
            "details": [{"id": pid} for pid in chunk],
            "reveal_personal_emails": False,
            "reveal_phone_number": False,
        }
        url = f"{API_BASE}/people/bulk_match"
        resp = requests.post(url, headers=api_headers(api_key), json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        all_matches.extend(data.get("matches") or [])
        time.sleep(0.3)
    return {"matches": all_matches}


def match_by_linkedin(api_key: str, linkedin_url: str) -> dict[str, Any] | None:
    url = f"{API_BASE}/people/match?linkedin_url={quote(linkedin_url)}&reveal_personal_emails=false"
    resp = requests.post(url, headers=api_headers(api_key), timeout=60)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    data = resp.json()
    return data.get("person")


def person_to_row(category: str, match: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "Category": category,
        "First Name": match.get("first_name", ""),
        "Last Name": match.get("last_name", ""),
        "Title": match.get("title", ""),
        "Company": (match.get("organization") or {}).get("name", ""),
        "Location": ", ".join(
            x
            for x in [match.get("city"), match.get("state"), match.get("country")]
            if x
        ),
        "LinkedIn URL": match.get("linkedin_url", ""),
        "Email": match.get("email", ""),
        "Email Source": source,
        "Notes": f"Apollo id: {match.get('id', '')}",
    }


def write_google_sheet_csv(path: str, rows: list[dict[str, Any]]) -> None:
    fieldnames = ["Name", "Company", "Account", "Role", "Department", "Phone", "Notes"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            name = " ".join(
                part
                for part in [row.get("First Name", ""), row.get("Last Name", "")]
                if part
            ).strip()
            notes_parts = []
            if row.get("Email"):
                notes_parts.append(f"Email: {row['Email']}")
            if row.get("LinkedIn URL"):
                notes_parts.append(f"LinkedIn: {row['LinkedIn URL']}")
            if row.get("Location"):
                notes_parts.append(f"Location: {row['Location']}")
            if row.get("Notes"):
                notes_parts.append(str(row["Notes"]))
            writer.writerow(
                {
                    "Name": name,
                    "Company": row.get("Company", ""),
                    "Account": "",
                    "Role": row.get("Title", ""),
                    "Department": row.get("Category", ""),
                    "Phone": row.get("Phone", ""),
                    "Notes": " | ".join(notes_parts),
                }
            )


def collect_search_results(api_key: str, max_per_group: int = 50) -> list[dict[str, Any]]:
    seen_ids: set[str] = set()
    rows: list[dict[str, Any]] = []

    for category, titles in SEARCH_GROUPS.items():
        page = 1
        collected = 0
        while collected < max_per_group:
            data = search_people(api_key, titles, page=page, per_page=25)
            people = data.get("people") or []
            if not people:
                break

            ids_to_enrich: list[str] = []
            for person in people:
                pid = person.get("id")
                if not pid or pid in seen_ids:
                    continue
                seen_ids.add(pid)
                ids_to_enrich.append(pid)

            if ids_to_enrich:
                enriched = bulk_match(api_key, ids_to_enrich)
                matches = enriched.get("matches") or []
                for match in matches:
                    if not match:
                        continue
                    rows.append(person_to_row(category, match, "Apollo bulk_match"))
                    collected += 1
                    if collected >= max_per_group:
                        break

            if len(people) < 25:
                break
            page += 1
            time.sleep(0.5)

    return rows


def enrich_csv_input(api_key: str, input_path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            linkedin = (row.get("LinkedIn URL") or "").strip()
            if linkedin and not (row.get("Email") or "").strip():
                person = match_by_linkedin(api_key, linkedin)
                if person and person.get("email"):
                    row["Email"] = person["email"]
                    row["Email Source"] = "Apollo people/match"
            rows.append(row)
            time.sleep(0.3)
    return rows


def write_csv(path: str, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "Category",
        "First Name",
        "Last Name",
        "Title",
        "Company",
        "Location",
        "LinkedIn URL",
        "Email",
        "Email Source",
        "Notes",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apollo ERP/SAP/B2B/CIMS US lead export")
    parser.add_argument("--output", default="leads/apollo-enriched-leads.csv")
    parser.add_argument("--input", help="Enrich existing CSV via LinkedIn URLs")
    parser.add_argument("--max-per-group", type=int, default=50)
    parser.add_argument(
        "--google-sheet-output",
        help="Also write CSV formatted for Google Sheet columns",
    )
    args = parser.parse_args()

    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not api_key:
        print("Set APOLLO_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    if args.input:
        rows = enrich_csv_input(api_key, args.input)
    else:
        rows = collect_search_results(api_key, max_per_group=args.max_per_group)

    write_csv(args.output, rows)
    print(f"Wrote {len(rows)} rows to {args.output}")
    if args.google_sheet_output:
        write_google_sheet_csv(args.google_sheet_output, rows)
        print(f"Wrote Google Sheet CSV to {args.google_sheet_output}")


if __name__ == "__main__":
    main()
