#!/usr/bin/env python3
"""
Find people who recently attended automation/workflow efficiency conferences.

Sources:
  - LinkedIn posts about conference attendance (public web research)
  - Official speaker lists (ZapConnect 2025, etc.)
  - Named attendees mentioned in LinkedIn conference recaps

Enrichment via Apollo people/match (LinkedIn URL or name + organization).

Usage:
  export APOLLO_API_KEY='your-key'
  python3 leads/apollo_conference_leads.py --limit 100
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


def api_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json",
        "x-api-key": api_key,
    }


def match_by_linkedin(api_key: str, linkedin_url: str) -> dict[str, Any] | None:
    url = (
        f"{API_BASE}/people/match?linkedin_url={quote(linkedin_url)}"
        "&reveal_personal_emails=false"
    )
    resp = requests.post(url, headers=api_headers(api_key), timeout=60)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json().get("person")


def match_by_name(
    api_key: str,
    first_name: str,
    last_name: str,
    organization: str = "",
) -> dict[str, Any] | None:
    params: list[tuple[str, str]] = [
        ("first_name", first_name),
        ("last_name", last_name),
        ("reveal_personal_emails", "false"),
    ]
    if organization:
        params.append(("organization_name", organization))
    query = "&".join(f"{k}={quote(v)}" for k, v in params)
    url = f"{API_BASE}/people/match?{query}"
    resp = requests.post(url, headers=api_headers(api_key), timeout=60)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json().get("person")


def person_to_row(
    person: dict[str, Any],
    conference: str,
    source: str,
    note: str = "",
) -> dict[str, Any]:
    name = person.get("name") or " ".join(
        p for p in [person.get("first_name"), person.get("last_name")] if p
    )
    return {
        "Name": name.strip(),
        "Title": person.get("title", ""),
        "Company": (person.get("organization") or {}).get("name", ""),
        "Conference": conference,
        "Source": source,
        "Email": person.get("email", ""),
        "LinkedIn": person.get("linkedin_url", ""),
        "Location": ", ".join(
            x for x in [person.get("city"), person.get("state"), person.get("country")] if x
        ),
        "Apollo ID": person.get("id", ""),
        "Notes": note,
    }


def load_seeds(path: Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    seeds: list[dict[str, Any]] = []

    for item in data.get("linkedin_attendees") or []:
        seeds.append({
            "match_type": "linkedin",
            "linkedin": item["linkedin"],
            "conference": item["conference"],
            "source": item.get("source", "linkedin_post"),
            "note": item.get("note", ""),
        })

    for item in data.get("named_attendees") or []:
        seeds.append({
            "match_type": "name",
            "first_name": item["first_name"],
            "last_name": item["last_name"],
            "organization": item.get("organization", ""),
            "conference": item["conference"],
            "source": item.get("source", "linkedin_mention"),
            "note": item.get("note", ""),
        })

    for item in data.get("zapconnect_2025_speakers") or []:
        seeds.append({
            "match_type": "name",
            "first_name": item["first_name"],
            "last_name": item["last_name"],
            "organization": item.get("organization", ""),
            "conference": item["conference"],
            "source": item.get("source", "speaker"),
            "note": "ZapConnect 2025 speaker list",
        })

    return seeds


def enrich_seeds(
    api_key: str,
    seeds: list[dict[str, Any]],
    limit: int,
    max_per_conference: int | None = None,
) -> list[dict[str, Any]]:
    seen_ids: set[str] = set()
    conf_counts: dict[str, int] = {}
    rows: list[dict[str, Any]] = []
    matched = 0
    skipped = 0

    for i, seed in enumerate(seeds):
        if len(rows) >= limit:
            break

        conference = seed["conference"]
        if (
            max_per_conference
            and conf_counts.get(conference, 0) >= max_per_conference
        ):
            skipped += 1
            continue

        person: dict[str, Any] | None = None
        try:
            if seed["match_type"] == "linkedin":
                person = match_by_linkedin(api_key, seed["linkedin"])
            else:
                person = match_by_name(
                    api_key,
                    seed["first_name"],
                    seed["last_name"],
                    seed.get("organization", ""),
                )
        except requests.HTTPError as exc:
            print(f"  HTTP error on seed {i + 1}: {exc}", file=sys.stderr)
            skipped += 1
            time.sleep(0.5)
            continue

        if not person:
            skipped += 1
            time.sleep(0.25)
            continue

        name = person.get("name") or " ".join(
            p for p in [person.get("first_name"), person.get("last_name")] if p
        )
        if not name.strip():
            skipped += 1
            time.sleep(0.25)
            continue

        pid = person.get("id")
        if pid and pid in seen_ids:
            skipped += 1
            time.sleep(0.25)
            continue

        if pid:
            seen_ids.add(pid)

        row = person_to_row(
            person,
            conference,
            seed.get("source", ""),
            seed.get("note", ""),
        )
        rows.append(row)
        conf_counts[conference] = conf_counts.get(conference, 0) + 1
        matched += 1

        if matched % 10 == 0:
            with_email = sum(1 for r in rows if r.get("Email"))
            print(f"  enriched {matched} ({with_email} with email) | total target {limit}")

        time.sleep(0.3)

    print(f"Done: {matched} matched, {skipped} skipped/no-match/capped")
    return rows


def write_csv(path: str, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "Name", "Title", "Company", "Conference", "Source",
        "Email", "LinkedIn", "Location", "Apollo ID", "Notes",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_google_sheet_csv(path: str, rows: list[dict[str, Any]]) -> None:
    fields = [
        "Name", "Company", "Account", "Role", "Department",
        "Phone", "Email", "LinkedIn", "Location", "Apollo ID", "Notes",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            notes = r.get("Notes", "")
            conf = r.get("Conference", "")
            src = r.get("Source", "")
            if conf:
                notes = f"{conf} ({src})" + (f" | {notes}" if notes else "")
            w.writerow({
                "Name": r.get("Name", ""),
                "Company": r.get("Company", ""),
                "Account": "",
                "Role": r.get("Title", ""),
                "Department": "Automation conference",
                "Phone": "",
                "Email": r.get("Email", ""),
                "LinkedIn": r.get("LinkedIn", ""),
                "Location": r.get("Location", ""),
                "Apollo ID": r.get("Apollo ID", ""),
                "Notes": notes,
            })


def write_conference_summary(path: str, conferences_path: Path, rows: list[dict[str, Any]]) -> None:
    with open(conferences_path, encoding="utf-8") as f:
        conf_data = json.load(f)

    conf_counts: dict[str, int] = {}
    for row in rows:
        c = row.get("Conference", "Unknown")
        conf_counts[c] = conf_counts.get(c, 0) + 1

    summary_lines = ["# Automation Conference Leads Summary\n"]
    summary_lines.append(f"Total leads: {len(rows)}")
    summary_lines.append(f"With email: {sum(1 for r in rows if r.get('Email'))}\n")
    summary_lines.append("## Conferences tracked\n")
    for conf in conf_data.get("conferences") or []:
        count = conf_counts.get(conf["name"], 0)
        summary_lines.append(
            f"- **{conf['name']}** ({conf['date']}, {conf['location']}) — {count} leads"
        )
    summary_lines.append("\n## Leads per conference\n")
    for name, count in sorted(conf_counts.items(), key=lambda x: -x[1]):
        summary_lines.append(f"- {name}: {count}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apollo enrichment for conference attendees")
    parser.add_argument("--output", default="leads/automation-conference-leads.csv")
    parser.add_argument("--google-sheet-output", default="leads/google-sheet-conference-import.csv")
    parser.add_argument("--seeds", default="leads/automation_conference_attendees.json")
    parser.add_argument("--conferences", default="leads/automation_conferences.json")
    parser.add_argument("--summary", default="leads/automation-conference-summary.md")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--max-per-conference", type=int, default=0,
                        help="Cap leads per conference (0 = no cap)")
    args = parser.parse_args()

    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not api_key:
        print("Set APOLLO_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    seeds = load_seeds(Path(args.seeds))
    print(f"Loaded {len(seeds)} seeds; targeting {args.limit} leads")

    rows = enrich_seeds(
        api_key,
        seeds,
        args.limit,
        args.max_per_conference or None,
    )

    write_csv(args.output, rows)
    write_google_sheet_csv(args.google_sheet_output, rows)
    write_conference_summary(args.summary, Path(args.conferences), rows)

    with_email = sum(1 for r in rows if r.get("Email"))
    print(f"Wrote {len(rows)} rows ({with_email} emails) to {args.output}")


if __name__ == "__main__":
    main()
