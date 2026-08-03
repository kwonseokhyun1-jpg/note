#!/usr/bin/env python3
"""Companies with public AI incidents/bad moves + Apollo security/exec contacts."""

from __future__ import annotations

import csv
import os
import sys
import time
from typing import Any
from urllib.parse import quote

import requests

API_BASE = "https://api.apollo.io/api/v1"

COMPANIES: list[dict[str, str]] = [
    {
        "Company": "Air Canada",
        "Domain": "aircanada.com",
        "Stage": "Enterprise",
        "Incident_Summary": "Tribunal ruled airline liable after customer-service chatbot invented bereavement refund policy and misled passenger into buying full-fare tickets.",
        "Source_URL": "https://www.cbc.ca/news/canada/british-columbia/air-canada-chatbot-lawsuit-1.7116416",
        "Incident_Date": "2024-02",
    },
    {
        "Company": "Samsung Electronics",
        "Domain": "samsung.com",
        "Stage": "Enterprise",
        "Incident_Summary": "Semiconductor engineers leaked proprietary source code and meeting transcripts into ChatGPT; company banned public gen-AI tools groupwide.",
        "Source_URL": "https://www.ciodive.com/news/Samsung-Electronics-ChatGPT-leak-data-privacy/647137/",
        "Incident_Date": "2023-03",
    },
    {
        "Company": "DPD",
        "Domain": "dpd.com",
        "Stage": "Enterprise",
        "Incident_Summary": "Customer AI chatbot was manipulated to swear at users and write viral anti-company poem; AI features disabled after backlash.",
        "Source_URL": "https://drdaveheath.com/blog/ai-chatbot-legal-liability-air-canada-dpd-chevy",
        "Incident_Date": "2024-01",
    },
    {
        "Company": "Workday",
        "Domain": "workday.com",
        "Stage": "Enterprise",
        "Incident_Summary": "Class action Mobley v. Workday alleges AI applicant-screening tools discriminated by age, race, and disability across millions of job seekers.",
        "Source_URL": "https://www.cnn.com/2025/05/22/tech/workday-ai-hiring-discrimination-lawsuit",
        "Incident_Date": "2023-02",
    },
    {
        "Company": "UnitedHealth Group",
        "Domain": "unitedhealthgroup.com",
        "Stage": "Enterprise",
        "Incident_Summary": "Lawsuit alleges nH Predict AI algorithm wrongfully denied Medicare Advantage post-acute care; ~90% of appealed denials reversed.",
        "Source_URL": "https://www.reuters.com/legal/lawsuit-claims-unitedhealth-ai-wrongfully-denies-elderly-extended-care-2023-11-14/",
        "Incident_Date": "2023-11",
    },
    {
        "Company": "Cigna",
        "Domain": "cigna.com",
        "Stage": "Enterprise",
        "Incident_Summary": "ProPublica investigation and lawsuit over PxDx system allegedly batch-denying hundreds of thousands of claims in seconds.",
        "Source_URL": "https://news.bloomberglaw.com/daily-labor-report/ai-algorithm-based-health-insurer-denials-pose-new-legal-threat",
        "Incident_Date": "2023-03",
    },
    {
        "Company": "Humana",
        "Domain": "humana.com",
        "Stage": "Enterprise",
        "Incident_Summary": "Class action alleges insurer used AI tools to systematically deny Medicare Advantage claims for post-acute and rehab care.",
        "Source_URL": "https://www.healthcarefinancenews.com/news/class-action-lawsuit-against-unitedhealths-ai-claim-denials-advances",
        "Incident_Date": "2023-12",
    },
    {
        "Company": "General Motors",
        "Domain": "gm.com",
        "Stage": "Enterprise",
        "Incident_Summary": "Cruise robotaxi struck and dragged pedestrian 20 ft; GM unit fined for misleading regulators and wound down robotaxi operations.",
        "Source_URL": "https://www.reuters.com/business/autos-transportation/gm-cruise-robotaxi-unit-faces-us-probes-over-dragging-incident-vows-reforms-2024-01-25/",
        "Incident_Date": "2023-10",
    },
    {
        "Company": "Waymo",
        "Domain": "waymo.com",
        "Stage": "Enterprise",
        "Incident_Summary": "NHTSA opened probe into 22 incidents of unexpected robotaxi behavior and collisions; issued software recalls to fix detection issues.",
        "Source_URL": "https://www.reuters.com/legal/litigation/us-closes-probe-into-waymo-self-driving-collisions-unexpected-behavior-2025-07-25/",
        "Incident_Date": "2024-05",
    },
    {
        "Company": "Character.AI",
        "Domain": "character.ai",
        "Stage": "Series B",
        "Incident_Summary": "Wrongful-death lawsuits allege chatbot fostered emotional dependency and failed to intervene before teen suicides.",
        "Source_URL": "https://www.reuters.com/legal/mother-sues-ai-chatbot-company-characterai-google-sued-over-sons-suicide-2024-10-23/",
        "Incident_Date": "2024-10",
    },
    {
        "Company": "iTutor Group",
        "Domain": "itutorgroup.com",
        "Stage": "Enterprise",
        "Incident_Summary": "EEOC settlement: hiring software automatically rejected female applicants over 55 and male applicants over 60.",
        "Source_URL": "https://www.eeoc.gov/newsroom/eeoc-itutor-settle-age-discrimination-suit-over-hiring-software",
        "Incident_Date": "2023-05",
    },
    {
        "Company": "McDonald's",
        "Domain": "mcdonalds.com",
        "Stage": "Enterprise",
        "Incident_Summary": "Ended IBM AI drive-thru pilot after widespread order errors (wrong items, hundreds of nuggets); accuracy below operational threshold.",
        "Source_URL": "https://www.restaurantbusinessonline.com/technology/mcdonalds-removes-ai-drive-thrus",
        "Incident_Date": "2024-07",
    },
    {
        "Company": "The Arena Group",
        "Domain": "thearenagroup.net",
        "Stage": "Media",
        "Incident_Summary": "Sports Illustrated published articles under fake AI-generated author personas; CEO fired after scandal.",
        "Source_URL": "https://www.cnn.com/2023/11/27/media/sports-illustrated-deletes-articles-fake-author-names-ai-profile-photos",
        "Incident_Date": "2023-11",
    },
    {
        "Company": "Gannett",
        "Domain": "gannett.com",
        "Stage": "Media",
        "Incident_Summary": "USA Today and local papers published embarrassing AI-generated sports recaps with factual errors; journalists called it humiliating.",
        "Source_URL": "https://futurism.com/sports-illustrated-ai-generated-writers",
        "Incident_Date": "2023-08",
    },
    {
        "Company": "City of New York",
        "Domain": "nyc.gov",
        "Stage": "Government",
        "Incident_Summary": "MyCity business chatbot told owners to break labor, housing, and cashless-payment laws; city kept bot online with disclaimers.",
        "Source_URL": "https://themarkup.org/artificial-intelligence/2024/03/29/nycs-ai-chatbot-tells-businesses-to-break-the-law",
        "Incident_Date": "2024-03",
    },
    {
        "Company": "Replika",
        "Domain": "replika.ai",
        "Stage": "Series A",
        "Incident_Summary": "Users reported emotional harm after abrupt removal of romantic/ERP features; EU complaints over manipulative AI companion design.",
        "Source_URL": "https://www.wired.com/story/replika-ai-companion-erotic-roleplay/",
        "Incident_Date": "2023-02",
    },
    {
        "Company": "CNET",
        "Domain": "cnet.com",
        "Stage": "Media",
        "Incident_Summary": "Published dozens of AI-written finance articles with factual errors and plagiarism; issued corrections on more than half.",
        "Source_URL": "https://futurism.com/sports-illustrated-ai-generated-writers",
        "Incident_Date": "2023-01",
    },
    {
        "Company": "Chevrolet of Watsonville",
        "Domain": "watsonvillechevrolet.com",
        "Stage": "SMB",
        "Incident_Summary": "Dealership ChatGPT bot was prompt-injected into agreeing to sell a 2024 Tahoe for $1; went viral as cautionary AI commerce tale.",
        "Source_URL": "https://drdaveheath.com/blog/ai-chatbot-legal-liability-air-canada-dpd-chevy",
        "Incident_Date": "2023-11",
    },
    {
        "Company": "Duolingo",
        "Domain": "duolingo.com",
        "Stage": "Public",
        "Incident_Summary": "SEC filings show GenAI compute hurt gross margins; CEO scrapped internal AI-usage KPI after staff tokenmaxxing backlash.",
        "Source_URL": "https://www.classcentral.com/report/genai-costs-hurt-duolingo-margins/",
        "Incident_Date": "2025-11",
    },
    {
        "Company": "IBM",
        "Domain": "ibm.com",
        "Stage": "Enterprise",
        "Incident_Summary": "McDonald's ended IBM-powered AI drive-thru rollout after accuracy failures; Watson Health divestiture followed earlier AI overpromising.",
        "Source_URL": "https://www.restaurantbusinessonline.com/technology/mcdonalds-removes-ai-drive-thrus",
        "Incident_Date": "2024-07",
    },
]

TARGET_ROLES = ("CEO", "CSO", "CISO", "CIO", "VP Cybersecurity")

TARGET_TITLES: dict[str, list[str]] = {
    "CEO": [
        "chief executive officer",
        "ceo",
        "president and ceo",
        "president & ceo",
        "founder",
        "co-founder",
    ],
    "CSO": [
        "chief security officer",
        "cso",
        "chief strategy officer",
    ],
    "CISO": [
        "chief information security officer",
        "ciso",
        "vp information security",
        "vice president information security",
        "head of information security",
        "director information security",
    ],
    "CIO": [
        "chief information officer",
        "cio",
        "chief technology officer",
        "cto",
        "chief digital officer",
    ],
    "VP Cybersecurity": [
        "vp cybersecurity",
        "vice president cybersecurity",
        "vp security",
        "vice president security",
        "head of cybersecurity",
        "director cybersecurity",
        "vp cyber security",
    ],
}

KNOWN_EXECUTIVES: dict[str, dict[str, tuple[str, str]]] = {
    "aircanada.com": {"CEO": ("Michael", "Rousseau")},
    "workday.com": {"CEO": ("Carl", "Eschenbach"), "CIO": ("Sayan", "Chakraborty")},
    "unitedhealthgroup.com": {"CEO": ("Andrew", "Witty")},
    "cigna.com": {"CEO": ("David", "Cordani")},
    "humana.com": {"CEO": ("Jim", "Rechtin")},
    "gm.com": {"CEO": ("Mary", "Barra")},
    "waymo.com": {"CEO": ("Tekedra", "Mawakana")},
    "character.ai": {"CEO": ("Karandeep", "Anand")},
    "mcdonalds.com": {"CEO": ("Chris", "Kempczinski")},
    "gannett.com": {"CEO": ("Mike", "Reed")},
    "duolingo.com": {"CEO": ("Luis", "von Ahn")},
    "ibm.com": {"CEO": ("Arvind", "Krishna"), "CISO": ("Chris", "Hendricks")},
    "samsung.com": {"CEO": ("Jong-Hee", "Han")},
    "nyc.gov": {"CIO": ("Matthew", "Fraser")},
    "replika.ai": {"CEO": ("Eugenia", "Kuyda")},
}

KNOWN_LINKEDIN: dict[str, dict[str, str]] = {
    "gm.com": {"CEO": "http://www.linkedin.com/in/mary-barra-8a85433"},
    "unitedhealthgroup.com": {"CEO": "http://www.linkedin.com/in/andrew-witty"},
    "workday.com": {"CEO": "http://www.linkedin.com/in/carl-eschenbach"},
}

FIELDNAMES = [
    "Company", "Domain", "Stage", "Incident_Summary", "Source_URL", "Incident_Date",
    "Contact_Role", "First_Name", "Last_Name", "Title", "Email", "LinkedIn_URL",
    "Location", "Apollo_ID",
]


def headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json",
        "x-api-key": api_key,
    }


def apollo_post(
    api_key: str,
    url: str,
    *,
    json_payload: dict | None = None,
    retries: int = 3,
) -> requests.Response | None:
    for attempt in range(retries):
        try:
            return requests.post(
                url,
                headers=headers(api_key),
                json=json_payload,
                timeout=90,
            )
        except requests.RequestException as exc:
            if attempt + 1 == retries:
                print(f"  Apollo request failed: {exc}", file=sys.stderr)
                return None
            time.sleep(2 ** attempt)
    return None


def match_person(
    api_key: str,
    first: str,
    last: str,
    org: str,
    domain: str,
) -> dict[str, Any] | None:
    resp = apollo_post(
        api_key,
        f"{API_BASE}/people/match",
        json_payload={
            "first_name": first,
            "last_name": last,
            "organization_name": org,
            "domain": domain,
            "reveal_personal_emails": False,
        },
    )
    if resp is None or resp.status_code not in (200, 201):
        return None
    return resp.json().get("person")


def match_by_linkedin(api_key: str, linkedin_url: str) -> dict[str, Any] | None:
    url = (
        f"{API_BASE}/people/match?linkedin_url={quote(linkedin_url)}"
        "&reveal_personal_emails=false"
    )
    resp = apollo_post(api_key, url)
    if resp is None or resp.status_code not in (200, 201):
        return None
    return resp.json().get("person")


def enrich_person(api_key: str, person_id: str) -> dict[str, Any] | None:
    resp = apollo_post(
        api_key,
        f"{API_BASE}/people/match",
        json_payload={"id": person_id, "reveal_personal_emails": False},
    )
    if resp is None or resp.status_code not in (200, 201):
        return None
    return resp.json().get("person")


def search_by_role(api_key: str, domain: str, role: str) -> list[dict[str, Any]]:
    url = f"{API_BASE}/mixed_people/api_search?q_organization_domains_list[]={quote(domain)}&per_page=15&page=1"
    for title in TARGET_TITLES[role]:
        url += f"&person_titles[]={quote(title)}"
    resp = apollo_post(api_key, url)
    if resp is None or resp.status_code != 200:
        return []
    return resp.json().get("people") or []


def title_matches_role(title: str, role: str) -> bool:
    t = title.lower()
    if role == "CEO":
        return any(
            x in t
            for x in [
                "chief executive",
                "ceo",
                "founder",
                "co-founder",
                "president & ceo",
                "president and ceo",
            ]
        )
    if role == "CSO":
        return "chief security officer" in t or t.strip() == "cso" or "cso," in t
    if role == "CISO":
        return any(
            x in t
            for x in [
                "chief information security",
                "ciso",
                "information security officer",
                "head of information security",
                "vp information security",
                "vice president information security",
            ]
        )
    if role == "CIO":
        return any(
            x in t
            for x in [
                "chief information officer",
                "cio",
                "chief technology officer",
                "chief digital officer",
            ]
        ) and "security" not in t
    if role == "VP Cybersecurity":
        return any(
            x in t
            for x in [
                "cybersecurity",
                "cyber security",
                "vp security",
                "vice president security",
                "head of security",
                "director security",
            ]
        )
    return True


def person_row(co: dict[str, str], role: str, person: dict[str, Any]) -> dict[str, str]:
    return {
        "Company": co["Company"],
        "Domain": co["Domain"],
        "Stage": co["Stage"],
        "Incident_Summary": co["Incident_Summary"],
        "Source_URL": co["Source_URL"],
        "Incident_Date": co["Incident_Date"],
        "Contact_Role": role,
        "First_Name": person.get("first_name") or "",
        "Last_Name": person.get("last_name") or "",
        "Title": person.get("title") or "",
        "Email": person.get("email") or "",
        "LinkedIn_URL": person.get("linkedin_url") or "",
        "Location": ", ".join(
            x for x in [person.get("city"), person.get("state"), person.get("country")] if x
        ),
        "Apollo_ID": person.get("id") or "",
    }


def find_role_contact(api_key: str, co: dict[str, str], role: str) -> dict[str, str] | None:
    domain = co["Domain"]
    company = co["Company"]
    known = KNOWN_EXECUTIVES.get(domain, {}).get(role)
    if known:
        first, last = known
        person = match_person(api_key, first, last, company, domain)
        time.sleep(0.35)
        if person and (person.get("email") or person.get("linkedin_url")):
            matched_last = (person.get("last_name") or "").lower()
            expected_last = last.lower()
            if matched_last.startswith(expected_last[:3]) or expected_last in matched_last:
                return person_row(co, role, person)

    linkedin = KNOWN_LINKEDIN.get(domain, {}).get(role)
    if linkedin:
        person = match_by_linkedin(api_key, linkedin)
        time.sleep(0.35)
        if person and (person.get("email") or person.get("linkedin_url")):
            return person_row(co, role, person)

    for candidate in search_by_role(api_key, domain, role):
        pid = candidate.get("id")
        if not pid:
            continue
        cand_title = candidate.get("title") or ""
        if not title_matches_role(cand_title, role):
            continue
        if not candidate.get("has_email") and not candidate.get("linkedin_url"):
            continue
        person = enrich_person(api_key, pid)
        time.sleep(0.35)
        if person and (person.get("email") or person.get("linkedin_url")):
            title = person.get("title") or cand_title
            if title_matches_role(title, role):
                return person_row(co, role, person)
    return None


def main() -> None:
    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not api_key:
        print("Set APOLLO_API_KEY", file=sys.stderr)
        sys.exit(1)

    raw_path = "leads/ai-incidents-companies-raw.csv"
    out_path = "leads/ai-incidents-contacts.csv"

    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["Company", "Domain", "Stage", "Incident_Summary", "Source_URL", "Incident_Date"],
        )
        w.writeheader()
        w.writerows(COMPANIES)

    seen: set[str] = set()
    rows: list[dict[str, str]] = []

    for co in COMPANIES:
        print(f"Searching {co['Company']} ({co['Domain']})...")
        found: dict[str, dict[str, str]] = {}
        skip_roles = {"nyc.gov": {"CEO", "CSO"}}
        roles = [r for r in TARGET_ROLES if r not in skip_roles.get(co["Domain"], set())]
        for role in roles:
            row = find_role_contact(api_key, co, role)
            if not row:
                continue
            apollo_id = row["Apollo_ID"]
            if apollo_id in seen:
                continue
            seen.add(apollo_id)
            found[role] = row
            print(f"  {role}: {row['First_Name']} {row['Last_Name']} ({row['Email'] or 'no email'})")
            time.sleep(0.2)

        rows.extend(found[r] for r in roles if r in found)
        if not found:
            print("  -> no contacts")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    emails = sum(1 for r in rows if r["Email"])
    print(f"\nWrote {len(COMPANIES)} companies to {raw_path}")
    print(f"Wrote {len(rows)} contacts ({emails} with email) to {out_path}")


if __name__ == "__main__":
    main()
