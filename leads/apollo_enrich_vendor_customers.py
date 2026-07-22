#!/usr/bin/env python3
"""Enrich vendor customer companies with CIO / VP Finance / VP Security contacts via Apollo."""

from __future__ import annotations

import csv
import os
import sys
import time
from typing import Any
from urllib.parse import quote

import requests

API_BASE = "https://api.apollo.io/api/v1"

# Map customer names to likely domains for Apollo org search
CUSTOMER_DOMAINS: dict[str, str] = {
    "Synthesia": "synthesia.io",
    "Cedar": "cedar.com",
    "Schneider Electric": "se.com",
    "Roche": "roche.com",
    "Mondelez": "mondelezinternational.com",
    "UniPro Foodservice": "uniprofoodservice.com",
    "Asian Paints": "asianpaints.com",
    "SaltPay": "saltpay.co",
    "Coinbase": "coinbase.com",
    "Circle": "circle.com",
    "Cross River Bank": "crossriver.com",
    "PayPal": "paypal.com",
    "Robinhood": "robinhood.com",
    "Stripe": "stripe.com",
    "Visa": "visa.com",
    "Kraken": "kraken.com",
    "Ripple": "ripple.com",
    "Crypto.com": "crypto.com",
    "OKX": "okx.com",
    "DoorDash": "doordash.com",
    "Nestlé": "nestle.com",
    "LG Uplus": "lguplus.com",
    "Palo Alto Networks": "paloaltonetworks.com",
    "Lightmatter": "lightmatter.co",
    "Carrot": "get-carrot.com",
    "PUMA": "puma.com",
    "Nissan": "nissan-global.com",
    "Lush": "lush.com",
    "WD-40 Company": "wd40company.com",
    "Marshalls": "marshalls.com",
    "Cineplex": "cineplex.com",
    "SoftwareOne": "softwareone.com",
    "Victaulic": "victaulic.com",
    "CEVA Logistics": "cevalogistics.com",
    "Belron": "belron.com",
    "Virgin Active": "virginactive.com",
    "Crédit Agricole": "credit-agricole.com",
    "Kerry Logistics": "kerrylogistics.com",
    "OVHcloud": "ovhcloud.com",
    "Rimowa": "rimowa.com",
    "Barratt Developments": "barrattdevelopments.co.uk",
    "Universal Robots": "universal-robots.com",
    "David Lloyd Leisure": "davidlloyd.co.uk",
    "LifeHealthcare": "lifehealthcare.com.au",
    "R.M. Williams": "rmwilliams.com.au",
    "Mowi": "mowi.com",
    "Tikkurila": "tikkurila.com",
    "Dynapac": "dynapac.com",
    "Samuel Son & Co": "samuel.com",
    "Jusbrasil": "jusbrasil.com.br",
    "Mercos": "mercos.com",
    "ClickBus": "clickbus.com.br",
    "CarEdge": "caredge.com",
    "Pilot": "pilot.com",
    "Legion Health": "legion.health",
    "AG1": "drinkag1.com",
    "Swanson Health": "swansonvitamins.com",
    "Feastables": "feastables.com",
    "HIFI": "hifi.finance",
    "Jamaica Bearings Group": "jamaicabearings.com",
    "Maven Engineering Corporation": "mavenengineering.com",
    "FIEGE Logistik": "fiege.com",
    "Piping Technology & Products": "pipingtech.com",
    "Pilot": "pilot.com",
    "Nissan": "nissanusa.com",
}

TITLES = [
    "chief information officer",
    "cio",
    "vp finance",
    "vice president finance",
    "vp of finance",
    "chief financial officer",
    "cfo",
    "vp security",
    "vice president security",
    "chief information security officer",
    "ciso",
    "vp information security",
    "director information security",
    "head of finance",
    "head of security",
    "vp financial planning",
    "controller",
]


def headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json",
        "x-api-key": api_key,
    }


def search_org(api_key: str, domain: str) -> dict[str, Any] | None:
    url = f"{API_BASE}/mixed_people/api_search?q_organization_domains_list[]={quote(domain)}&per_page=10&page=1"
    for title in TITLES:
        url += f"&person_titles[]={quote(title)}"
    resp = requests.post(url, headers=headers(api_key), timeout=60)
    if resp.status_code != 200:
        return None
    return resp.json()


def enrich_person(api_key: str, person_id: str) -> dict[str, Any] | None:
    resp = requests.post(
        f"{API_BASE}/people/match",
        headers=headers(api_key),
        json={"id": person_id, "reveal_personal_emails": False},
        timeout=60,
    )
    if resp.status_code not in (200, 201):
        return None
    return resp.json().get("person")


def main() -> None:
    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not api_key:
        print("Set APOLLO_API_KEY", file=sys.stderr)
        sys.exit(1)

    vendors_path = "leads/vendor-customers-raw.csv"
    out_path = "leads/vendor-customer-finance-it-contacts.csv"

    with open(vendors_path, newline="", encoding="utf-8") as f:
        vendor_rows = list(csv.DictReader(f))

    # unique customers with vendor mapping
    customer_vendors: dict[str, list[str]] = {}
    for row in vendor_rows:
        customer_vendors.setdefault(row["Customer"], []).append(row["Vendor"])

    seen_person: set[str] = set()
    output: list[dict[str, str]] = []

    for customer, vendors in customer_vendors.items():
        domain = CUSTOMER_DOMAINS.get(customer)
        if not domain:
            print(f"SKIP (no domain): {customer}")
            continue
        print(f"Searching {customer} ({domain})...")
        data = search_org(api_key, domain)
        if not data:
            continue
        people = data.get("people") or []
        found = 0
        for person in people[:5]:
            pid = person.get("id")
            if not pid or pid in seen_person or not person.get("has_email"):
                continue
            enriched = enrich_person(api_key, pid)
            if not enriched or not enriched.get("email"):
                continue
            seen_person.add(pid)
            output.append(
                {
                    "Vendor": "; ".join(sorted(set(vendors))),
                    "Customer": customer,
                    "Customer_Domain": domain,
                    "First_Name": enriched.get("first_name", ""),
                    "Last_Name": enriched.get("last_name", ""),
                    "Title": enriched.get("title", ""),
                    "Email": enriched.get("email", ""),
                    "LinkedIn_URL": enriched.get("linkedin_url", ""),
                    "Location": ", ".join(
                        x for x in [enriched.get("city"), enriched.get("state"), enriched.get("country")] if x
                    ),
                    "Apollo_ID": enriched.get("id", ""),
                }
            )
            found += 1
            time.sleep(0.35)
        print(f"  -> {found} contacts")
        time.sleep(0.5)

    fieldnames = [
        "Vendor", "Customer", "Customer_Domain", "First_Name", "Last_Name",
        "Title", "Email", "LinkedIn_URL", "Location", "Apollo_ID",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)

    print(f"\nWrote {len(output)} contacts to {out_path}")


if __name__ == "__main__":
    main()
