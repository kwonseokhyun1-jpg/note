#!/usr/bin/env python3
"""Companies complaining about high AI spend + Apollo CEO/CFO/Head of AI contacts."""

from __future__ import annotations

import csv
import os
import sys
import time
from typing import Any
from urllib.parse import quote

import requests

API_BASE = "https://api.apollo.io/api/v1"

# Public complaints about variable AI spend / budget blowouts (2025–2026)
COMPANIES: list[dict[str, str]] = [
    # --- Enterprise ---
    {
        "Company": "Uber",
        "Domain": "uber.com",
        "Stage": "Enterprise",
        "Complaint_Summary": "Burned entire 2026 AI coding budget by April; per-engineer costs $500–$2,000/mo on agentic tools; capped at $1,500/employee/tool.",
        "Source_URL": "https://www.developersdigest.tech/blog/enterprise-ai-coding-budget-blowouts-2026",
        "Complaint_Date": "2026-04",
    },
    {
        "Company": "Microsoft",
        "Domain": "microsoft.com",
        "Stage": "Enterprise",
        "Complaint_Summary": "Revoked Claude Code licenses across Experiences + Devices division; shifted engineers to Copilot CLI after token costs spiked.",
        "Source_URL": "https://advancedai.com/briefings/enterprise-ai-agent-token-cost-reckoning-2026/",
        "Complaint_Date": "2026-05",
    },
    {
        "Company": "Walmart",
        "Domain": "walmart.com",
        "Stage": "Enterprise",
        "Complaint_Summary": "Capped per-employee tokens on internal Code Puppy AI tool after employee demand exceeded budget projections.",
        "Source_URL": "https://www.businessinsider.com/walmart-ai-coding-tool-limit-duplicative-requests-2026-6",
        "Complaint_Date": "2026-06",
    },
    {
        "Company": "Priceline",
        "Domain": "priceline.com",
        "Stage": "Enterprise",
        "Complaint_Summary": "Cursor contract renewal came back 4–5x prior price; IT finance capping tokens by team and disputing vendor usage reports.",
        "Source_URL": "https://finance.yahoo.com/sectors/technology/articles/token-bill-comes-due-inside-144912278.html",
        "Complaint_Date": "2026-06",
    },
    {
        "Company": "Salesforce",
        "Domain": "salesforce.com",
        "Stage": "Enterprise",
        "Complaint_Summary": "Projecting $300M Anthropic token spend in 2026; built internal systems to tie every token to profitable outcomes after sticker shock.",
        "Source_URL": "https://www.businessinsider.com/marc-benioff-salesforce-anthropic-spend-tokens-slack-2026-5",
        "Complaint_Date": "2026-05",
    },
    {
        "Company": "Coinbase",
        "Domain": "coinbase.com",
        "Stage": "Enterprise",
        "Complaint_Summary": "Internal AI usage went parabolic after Claude Opus 4.6; instituted $500–$5,000 weekly employee caps before shifting to cheaper model routing.",
        "Source_URL": "https://www.businessinsider.com/ai-companies-raising-prices-internal-token-limits-openai-anthropic-ipo-2026-6",
        "Complaint_Date": "2026-06",
    },
    {
        "Company": "Amazon",
        "Domain": "amazon.com",
        "Stage": "Enterprise",
        "Complaint_Summary": "Shut internal AI token leaderboard; employees ran wasteful agent loops to inflate usage stats as bills climbed.",
        "Source_URL": "https://fortune.com/2026/05/28/tokenmaxxing-is-dead-companies-didnt-get-the-roi-from-ai-they-wanted-to-see/",
        "Complaint_Date": "2026-05",
    },
    {
        "Company": "Meta",
        "Domain": "meta.com",
        "Stage": "Enterprise",
        "Complaint_Summary": "Removed internal tokenmaxxing leaderboard as variable AI compute costs became unsustainable at scale.",
        "Source_URL": "https://fortune.com/2026/05/28/tokenmaxxing-is-dead-companies-didnt-get-the-roi-from-ai-they-wanted-to-see/",
        "Complaint_Date": "2026-05",
    },
    {
        "Company": "Deloitte",
        "Domain": "deloitte.com",
        "Stage": "Enterprise",
        "Complaint_Summary": "Engineers report GitHub Copilot usage-based billing (June 2026) burning through monthly quotas in days; token caps disrupting workflows.",
        "Source_URL": "https://www.businessinsider.com/ai-companies-raising-prices-internal-token-limits-openai-anthropic-ipo-2026-6",
        "Complaint_Date": "2026-06",
    },
    {
        "Company": "Booking Holdings",
        "Domain": "bookingholdings.com",
        "Stage": "Enterprise",
        "Complaint_Summary": "Parent of Priceline; same Cursor renewal shock and enterprise token governance rollout across portfolio brands.",
        "Source_URL": "https://finance.yahoo.com/sectors/technology/articles/token-bill-comes-due-inside-144912278.html",
        "Complaint_Date": "2026-06",
    },
    # --- Series A–C / growth startups ---
    {
        "Company": "8090",
        "Domain": "8090.ai",
        "Stage": "Series A",
        "Complaint_Summary": "CEO Chamath Palihapitiya: AI costs tripled since Nov 2025 (AWS inference, Cursor, Anthropic); trending toward $10M/yr while revenue lags.",
        "Source_URL": "https://www.businessinsider.com/chamath-palihapitiya-ai-costs-tokens-8090-2026-3",
        "Complaint_Date": "2026-03",
    },
    {
        "Company": "Lindy",
        "Domain": "lindy.ai",
        "Stage": "Series B",
        "Complaint_Summary": "CEO Flo Crivello: raw API costs surpassed total payroll; ditched Claude for DeepSeek calling prior spend unsustainable.",
        "Source_URL": "http://www.singularitymoments.com/content/anthropic-faces-a-pricing-revolt-as-startups-ditch-claude/",
        "Complaint_Date": "2026-02",
    },
    {
        "Company": "Pylon",
        "Domain": "usepylon.com",
        "Stage": "Series B",
        "Complaint_Summary": "CEO Marty Kausas: Anthropic bill jumping $400K to $1.4M/yr at 150 seats; accidental $4K in 3 days on Claude Code; imposing spend limits.",
        "Source_URL": "https://www.businessinsider.com/pylon-ceo-tokenmaxxing-era-coming-to-end-ai-spend-limits-2026-6",
        "Complaint_Date": "2026-06",
    },
    {
        "Company": "Yorby",
        "Domain": "yorby.ai",
        "Stage": "Seed",
        "Complaint_Summary": "Founder hit $13,999 Google Cloud bill in one month from unchecked LLM inference on viral-content feature; credits masked overspend.",
        "Source_URL": "https://frontiermodels.cc/video/vibecoding-cost-me-20000-and-heres-how-i-fixed-it/",
        "Complaint_Date": "2026-04",
    },
    {
        "Company": "Turbo AI",
        "Domain": "turbo.ai",
        "Stage": "Series A",
        "Complaint_Summary": "Co-founder Sarthak Dhawan accidentally spent ~$30,000 on AI tokens in one month during rapid product iteration.",
        "Source_URL": "https://timesofindia.indiatimes.com/technology/tech-news/a-21-year-old-founder-accidentally-spent-30000-on-ai-tokens-in-a-month-heres-why-he-says-it-was-worth-every-dollar/articleshow/132303498.cms",
        "Complaint_Date": "2026-01",
    },
    {
        "Company": "Vanta",
        "Domain": "vanta.com",
        "Stage": "Series C",
        "Complaint_Summary": "CFO John McCauley publicly discussed AI cost crisis and need for spend governance as token bills outpaced forecasts.",
        "Source_URL": "https://www.growthunhinged.com/p/the-ai-cost-crisis-is-entirely-self-inflicted-and-fable-5-just-made-it-worse",
        "Complaint_Date": "2026-06",
    },
    {
        "Company": "ClickUp",
        "Domain": "clickup.com",
        "Stage": "Series C",
        "Complaint_Summary": "CFO Dan Zhang shared framework for controlling runaway AI token spend across GTM teams as usage-based bills surged.",
        "Source_URL": "https://www.growthunhinged.com/p/the-ai-cost-crisis-is-entirely-self-inflicted-and-fable-5-just-made-it-worse",
        "Complaint_Date": "2026-06",
    },
    {
        "Company": "SentinelOne",
        "Domain": "sentinelone.com",
        "Stage": "Public",
        "Complaint_Summary": "CFO Sonalee Parekh joined peer finance leaders flagging AI token cost crisis and need for ROI-linked budgets.",
        "Source_URL": "https://www.growthunhinged.com/p/the-ai-cost-crisis-is-entirely-self-inflicted-and-fable-5-just-made-it-worse",
        "Complaint_Date": "2026-06",
    },
    {
        "Company": "Duolingo",
        "Domain": "duolingo.com",
        "Stage": "Public",
        "Complaint_Summary": "SEC filings: gross margins fell 190bps due to GenAI compute on Max tier; CEO scrapped AI-usage performance metric after tokenmaxxing backlash.",
        "Source_URL": "https://www.classcentral.com/report/genai-costs-hurt-duolingo-margins/",
        "Complaint_Date": "2025-11",
    },
]

TARGET_TITLES = {
    "CEO": ["chief executive officer", "ceo"],
    "CFO": ["chief financial officer", "cfo"],
    "Head of AI": [
        "chief ai officer",
        "head of ai",
        "vp ai",
        "vice president ai",
        "vp artificial intelligence",
        "director of ai",
        "head of artificial intelligence",
    ],
}

# Prefer direct name match for known leaders (domain -> role -> first/last)
KNOWN_EXECUTIVES: dict[str, dict[str, tuple[str, str]]] = {
    "uber.com": {"CEO": ("Dara", "Khosrowshahi"), "CFO": ("Prashanth", "Mahendra-Rajah")},
    "microsoft.com": {"CEO": ("Satya", "Nadella"), "CFO": ("Amy", "Hood")},
    "walmart.com": {"CEO": ("Doug", "McMillon"), "CFO": ("John", "Rainey")},
    "salesforce.com": {"CEO": ("Marc", "Benioff"), "CFO": ("Amy", "Weaver")},
    "coinbase.com": {"CEO": ("Brian", "Armstrong"), "CFO": ("Alesia", "Haas")},
    "amazon.com": {"CEO": ("Andy", "Jassy"), "CFO": ("Brian", "Olsavsky")},
    "meta.com": {"CEO": ("Mark", "Zuckerberg"), "CFO": ("Susan", "Li")},
    "bookingholdings.com": {"CEO": ("Glenn", "Fogel"), "CFO": ("Ewout", "Steedman")},
    "8090.ai": {"CEO": ("Chamath", "Palihapitiya")},
    "lindy.ai": {"CEO": ("Flo", "Crivello")},
    "usepylon.com": {"CEO": ("Marty", "Kausas")},
    "yorby.ai": {"CEO": ("Andrew", "Meng")},
    "turbo.ai": {"CEO": ("Sarthak", "Dhawan")},
    "vanta.com": {"CEO": ("Christina", "Cacioppo"), "CFO": ("John", "McCauley")},
    "clickup.com": {"CEO": ("Zeb", "Evans"), "CFO": ("Dan", "Zhang")},
    "sentinelone.com": {"CEO": ("Tomer", "Weingarten"), "CFO": ("Sonalee", "Parekh")},
    "duolingo.com": {"CEO": ("Luis", "von Ahn"), "CFO": ("James", "Gear Jr.")},
    "priceline.com": {"CEO": ("Brigit", "Zimmerman"), "CFO": ("Matthew", "Tynan")},
}

FIELDNAMES = [
    "Company", "Domain", "Stage", "Complaint_Summary", "Source_URL", "Complaint_Date",
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


def match_person(
    api_key: str,
    first: str,
    last: str,
    org: str,
    domain: str,
) -> dict[str, Any] | None:
    resp = requests.post(
        f"{API_BASE}/people/match",
        headers=headers(api_key),
        json={
            "first_name": first,
            "last_name": last,
            "organization_name": org,
            "domain": domain,
            "reveal_personal_emails": False,
        },
        timeout=60,
    )
    if resp.status_code not in (200, 201):
        return None
    return resp.json().get("person")


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


def search_by_role(api_key: str, domain: str, role: str) -> list[dict[str, Any]]:
    url = f"{API_BASE}/mixed_people/api_search?q_organization_domains_list[]={quote(domain)}&per_page=15&page=1"
    for title in TARGET_TITLES[role]:
        url += f"&person_titles[]={quote(title)}"
    resp = requests.post(url, headers=headers(api_key), timeout=60)
    if resp.status_code != 200:
        return []
    return resp.json().get("people") or []


def person_row(co: dict[str, str], role: str, person: dict[str, Any]) -> dict[str, str]:
    return {
        "Company": co["Company"],
        "Domain": co["Domain"],
        "Stage": co["Stage"],
        "Complaint_Summary": co["Complaint_Summary"],
        "Source_URL": co["Source_URL"],
        "Complaint_Date": co["Complaint_Date"],
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
            return person_row(co, role, person)

    for candidate in search_by_role(api_key, domain, role):
        pid = candidate.get("id")
        if not pid:
            continue
        if not candidate.get("has_email") and not candidate.get("linkedin_url"):
            continue
        person = enrich_person(api_key, pid)
        time.sleep(0.35)
        if person and (person.get("email") or person.get("linkedin_url")):
            return person_row(co, role, person)
    return None


def main() -> None:
    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not api_key:
        print("Set APOLLO_API_KEY", file=sys.stderr)
        sys.exit(1)

    raw_path = "leads/ai-overspend-companies-raw.csv"
    out_path = "leads/ai-overspend-contacts.csv"

    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["Company", "Domain", "Stage", "Complaint_Summary", "Source_URL", "Complaint_Date"],
        )
        w.writeheader()
        w.writerows(COMPANIES)

    seen: set[str] = set()
    rows: list[dict[str, str]] = []

    for co in COMPANIES:
        print(f"Searching {co['Company']} ({co['Domain']})...")
        found: dict[str, dict[str, str]] = {}
        for role in ("CEO", "CFO", "Head of AI"):
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

        rows.extend(found[r] for r in ("CEO", "CFO", "Head of AI") if r in found)
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
