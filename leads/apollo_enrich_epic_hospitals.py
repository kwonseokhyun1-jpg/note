#!/usr/bin/env python3
"""Apollo enrichment for Bay Area Epic hospital IT contacts."""

from __future__ import annotations

import csv
import os
import sys
import time
from typing import Any
from urllib.parse import quote

import requests

API_BASE = "https://api.apollo.io/api/v1"

ORG_DOMAINS: dict[str, str] = {
    "UCSF Health": "ucsfhealth.org",
    "Zuckerberg SF General / SF Health Network": "sfdph.org",
    "SF Health Network": "sfdph.org",
    "Kaiser Permanente NorCal": "kaiserpermanente.org",
    "Sutter Health / CPMC": "sutterhealth.org",
    "Sutter Health": "sutterhealth.org",
    "Stanford Health Care": "stanfordhealthcare.org",
    "Stanford Children's Health": "stanfordchildrens.org",
    "El Camino Health": "elcaminohealth.org",
    "Alameda Health System": "alamedahealthsystem.org",
    "John Muir Health": "johnmuirhealth.com",
    "San Mateo County Health": "smchealth.org",
}

TITLES = [
    "chief information officer",
    "cio",
    "chief medical information officer",
    "cmio",
    "vp information technology",
    "director information technology",
    "director clinical informatics",
    "director information services",
    "epic analyst",
    "epic application analyst",
    "epic director",
    "director epic",
    "vice president it",
    "associate chief medical information officer",
]


def headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json",
        "x-api-key": api_key,
    }


def search_domain(api_key: str, domain: str, page: int = 1) -> dict[str, Any]:
    params: list[tuple[str, str]] = [
        ("per_page", "25"),
        ("page", str(page)),
        ("q_organization_domains_list[]", domain),
        ("person_locations[]", "California, US"),
        ("person_locations[]", "San Francisco, US"),
        ("person_locations[]", "Oakland, US"),
        ("person_locations[]", "Palo Alto, US"),
    ]
    for title in TITLES:
        params.append(("person_titles[]", title))
    query = "&".join(f"{k}={quote(v)}" for k, v in params)
    url = f"{API_BASE}/mixed_people/api_search?{query}"
    resp = requests.post(url, headers=headers(api_key), timeout=60)
    resp.raise_for_status()
    return resp.json()


def enrich_person(api_key: str, person_id: str) -> dict[str, Any] | None:
    url = f"{API_BASE}/people/match"
    resp = requests.post(
        url,
        headers=headers(api_key),
        json={"id": person_id, "reveal_personal_emails": False},
        timeout=60,
    )
    if resp.status_code in (404, 422):
        return None
    resp.raise_for_status()
    return resp.json().get("person")


def main() -> None:
    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not api_key:
        print("Set APOLLO_API_KEY", file=sys.stderr)
        sys.exit(1)

    hospitals_path = "leads/bay-area-epic-hospitals.csv"
    out_path = "leads/bay-area-epic-hospital-it-contacts.csv"

    with open(hospitals_path, newline="", encoding="utf-8") as f:
        hospitals = list(csv.DictReader(f))

    seen: set[str] = set()
    rows: list[dict[str, str]] = []

    for system, domain in ORG_DOMAINS.items():
        print(f"Searching {system} ({domain})...")
        page = 1
        found_for_org = 0
        while page <= 3 and found_for_org < 8:
            data = search_domain(api_key, domain, page=page)
            people = data.get("people") or []
            if not people:
                break
            for person in people:
                pid = person.get("id")
                if not pid or pid in seen:
                    continue
                if not person.get("has_email"):
                    continue
                seen.add(pid)
                enriched = enrich_person(api_key, pid)
                if not enriched:
                    continue
                email = enriched.get("email") or ""
                org = (enriched.get("organization") or {}).get("name", "")
                hospital_matches = [
                    h["Hospital"]
                    for h in hospitals
                    if h["Health_System"] == system
                    or system in h["Health_System"]
                    or h["Health_System"] in system
                ]
                hospital = hospital_matches[0] if hospital_matches else ""
                rows.append(
                    {
                        "Hospital": hospital,
                        "Health_System": system,
                        "First_Name": enriched.get("first_name", ""),
                        "Last_Name": enriched.get("last_name", ""),
                        "Title": enriched.get("title", ""),
                        "Email": email,
                        "LinkedIn_URL": enriched.get("linkedin_url", ""),
                        "Location": ", ".join(
                            x
                            for x in [
                                enriched.get("city"),
                                enriched.get("state"),
                                enriched.get("country"),
                            ]
                            if x
                        ),
                        "Apollo_ID": enriched.get("id", ""),
                        "Organization": org,
                    }
                )
                found_for_org += 1
                time.sleep(0.35)
            if len(people) < 25:
                break
            page += 1
            time.sleep(0.5)

    fieldnames = [
        "Hospital",
        "Health_System",
        "First_Name",
        "Last_Name",
        "Title",
        "Email",
        "LinkedIn_URL",
        "Location",
        "Apollo_ID",
        "Organization",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} contacts to {out_path}")


if __name__ == "__main__":
    main()
