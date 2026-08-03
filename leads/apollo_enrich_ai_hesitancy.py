#!/usr/bin/env python3
"""Companies with public AI adoption hesitancy + Apollo security/exec contacts."""

from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ai_hesitancy_companies_extra import EXTRA_COMPANIES, EXTRA_KNOWN_EXECUTIVES

API_BASE = "https://api.apollo.io/api/v1"

COMPANIES: list[dict[str, str]] = [
    {
        "Company": "Match Group",
        "Domain": "matchgroup.com",
        "Stage": "Public",
        "Hesitancy_Summary": "CFO Steve Bailey said there is no 'blank check' for AI; each department needs a business case and ROI before scaling spend.",
        "Source_URL": "https://www.cfodive.com/news/match-group-cfo-sets-higher-bar-ai-spending-2026/808575/",
        "Statement_Date": "2026-01",
    },
    {
        "Company": "ePlus",
        "Domain": "eplus.com",
        "Stage": "Public",
        "Hesitancy_Summary": "CFO Elaine Marion said AI budgets must go to targeted investments with clear ROI, not open-ended experimentation.",
        "Source_URL": "https://www.cfodive.com/news/top-5-ai-adoption-challenges-facing-cfos-in-2026/810277/",
        "Statement_Date": "2026-01",
    },
    {
        "Company": "JPMorgan Chase",
        "Domain": "jpmorganchase.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "CFO Jeremy Barnum urged employees to use cheaper models for routine tasks and avoid expensive frontier models when unnecessary.",
        "Source_URL": "https://www.pymnts.com/news/artificial-intelligence/2026/jpmorgan-wants-employees-to-go-easy-on-ai-usage/",
        "Statement_Date": "2026-07",
    },
    {
        "Company": "Goldman Sachs",
        "Domain": "gs.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "2025 shareholder letter flagged uncertain AI regulation and questioned how quickly the technology can be deployed at scale.",
        "Source_URL": "https://www.businessinsider.com/goldman-sachs-lays-out-ai-ambitions-biggest-risks-shareholder-letter-2026-3",
        "Statement_Date": "2026-03",
    },
    {
        "Company": "Uber",
        "Domain": "uber.com",
        "Stage": "Public",
        "Hesitancy_Summary": "COO Andrew Macdonald said rising AI token spend is getting harder to justify without a clear link to productivity gains.",
        "Source_URL": "https://www.theaiconsultingnetwork.com/blog/enterprise-ai-roi-sticker-shock-cre-investors-2026",
        "Statement_Date": "2026-05",
    },
    {
        "Company": "Microsoft",
        "Domain": "microsoft.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "Slowing/pausing some AI data-center projects; Nadella also warned against outsourcing core thinking to a single AI provider.",
        "Source_URL": "https://techcrunch.com/2026/07/27/satya-nadella-says-companies-that-trust-one-ai-for-everything-may-not-survive/",
        "Statement_Date": "2026-07",
    },
    {
        "Company": "Box",
        "Domain": "box.com",
        "Stage": "Public",
        "Hesitancy_Summary": "CEO Aaron Levie posted that the OpenAI agent sandbox escape will slow enterprise AI diffusion timelines and add governance friction.",
        "Source_URL": "https://theagenttimes.com/articles/box-ceo-levie-warns-openai-agent-sandbox-escape-will-slow-en-10678735",
        "Statement_Date": "2026-07",
    },
    {
        "Company": "Accenture",
        "Domain": "accenture.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "Chief AI Officer Lan Guan warned CFOs are hitting a 'cost wall' on AI tokens and lack visibility into what drives ballooning bills.",
        "Source_URL": "https://fortune.com/2026/07/29/cfo-hitting-cost-wall-ai-tokens-accenture/",
        "Statement_Date": "2026-07",
    },
    {
        "Company": "McDonald's",
        "Domain": "mcdonalds.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "After a thoughtful review, leadership ended the IBM AI drive-thru pilot citing accuracy gaps and the need to explore alternatives.",
        "Source_URL": "https://www.cnbc.com/2024/06/17/mcdonalds-to-end-ibm-ai-drive-thru-test.html",
        "Statement_Date": "2024-06",
    },
    {
        "Company": "Samsung Electronics",
        "Domain": "samsung.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "Banned employee use of ChatGPT and other gen-AI tools after engineers leaked proprietary code; 65% of staff cited security risks.",
        "Source_URL": "https://techcrunch.com/2023/05/02/samsung-bans-use-of-generative-ai-tools-like-chatgpt-after-april-internal-data-leak/",
        "Statement_Date": "2023-05",
    },
    {
        "Company": "Amazon",
        "Domain": "amazon.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "Corporate counsel warned employees not to share confidential code with ChatGPT after outputs mirrored internal Amazon data.",
        "Source_URL": "https://www.businessinsider.com/amazon-chatgpt-openai-warns-employees-not-share-confidential-information-microsoft-2023-1",
        "Statement_Date": "2023-01",
    },
    {
        "Company": "Apple",
        "Domain": "apple.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "CEO Tim Cook personally approved delaying key AI features, choosing caution over speed rather than shipping unready products.",
        "Source_URL": "https://www.thewealthadvisor.com/article/tim-cook-personally-approved-apples-ai-delay-company-chose-caution-over-speed",
        "Statement_Date": "2026-07",
    },
    {
        "Company": "Ford Motor",
        "Domain": "ford.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "Killed the FNV4 next-gen vehicle software 'brain' project after ballooning costs and delays; refocused on narrower skunkworks bets.",
        "Source_URL": "https://www.cnbc.com/2025/04/30/ford-kills-project-to-develop-tesla-like-electronic-brain.html",
        "Statement_Date": "2025-04",
    },
    {
        "Company": "Klarna",
        "Domain": "klarna.com",
        "Stage": "Series D+",
        "Hesitancy_Summary": "CEO Sebastian Siemiatkowski said over-reliance on AI customer service hurt quality and began hiring humans again after AI-first push.",
        "Source_URL": "https://fortune.com/2025/05/09/klarna-ai-humans-return-on-investment/",
        "Statement_Date": "2025-05",
    },
    {
        "Company": "Walmart",
        "Domain": "walmart.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "CFO John David Rainey said Walmart will not join the AI infrastructure arms race and will stay disciplined on high-ROI retail AI bets.",
        "Source_URL": "https://corporate.walmart.com/content/dam/corporate/documents/newsroom/2026/02/19/walmart-releases-q4-fy26-earnings/q4-fy26-earnings-call-transcript.pdf",
        "Statement_Date": "2026-02",
    },
    {
        "Company": "Duolingo",
        "Domain": "duolingo.com",
        "Stage": "Public",
        "Hesitancy_Summary": "CEO Luis von Ahn scrapped an internal AI-usage KPI after employees gamed token spend; filings show GenAI compute hurt margins.",
        "Source_URL": "https://www.classcentral.com/report/genai-costs-hurt-duolingo-margins/",
        "Statement_Date": "2025-11",
    },
    {
        "Company": "Bank of America",
        "Domain": "bankofamerica.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "CEO Brian Moynihan acknowledged AI spending is significant and said the industry focus is shifting from broad deployment to cost control.",
        "Source_URL": "https://finance.biggo.com/news/d5c016f8-3426-42c3-a82c-03f97dddce0b",
        "Statement_Date": "2026-07",
    },
    {
        "Company": "Morgan Stanley",
        "Domain": "morganstanley.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "Leadership highlighted rising token expenses and the need for disciplined model routing as AI costs scale across the firm.",
        "Source_URL": "https://diginomica.com/tokenomics-direction-investment-travel-goldman-sachs-jp-morgan-chase-and-morgan-stanley",
        "Statement_Date": "2026-07",
    },
    {
        "Company": "Disney",
        "Domain": "disney.com",
        "Stage": "Enterprise",
        "Hesitancy_Summary": "CEO Bob Iger paused a major metaverse/AI lab project and said the company will be selective about where it applies generative AI.",
        "Source_URL": "https://www.wsj.com/articles/disney-shuts-down-metaverse-division-11675811400",
        "Statement_Date": "2023-03",
    },
    {
        "Company": "Spotify",
        "Domain": "spotify.com",
        "Stage": "Public",
        "Hesitancy_Summary": "CEO Daniel Ek said AI will not replace human creators and Spotify limited AI-generated music on the platform over fraud concerns.",
        "Source_URL": "https://www.bloomberg.com/news/articles/2023-04-30/spotify-removes-tens-of-thousands-of-ai-made-songs",
        "Statement_Date": "2023-04",
    },
    *EXTRA_COMPANIES,
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
    "matchgroup.com": {"CEO": ("Bernard", "Kim")},
    "eplus.com": {"CEO": ("Mark", "Marron")},
    "jpmorganchase.com": {"CEO": ("Jamie", "Dimon")},
    "gs.com": {"CEO": ("David", "Solomon")},
    "uber.com": {"CEO": ("Dara", "Khosrowshahi")},
    "microsoft.com": {"CEO": ("Satya", "Nadella")},
    "box.com": {"CEO": ("Aaron", "Levie")},
    "accenture.com": {"CEO": ("Julie", "Sweet")},
    "mcdonalds.com": {"CEO": ("Chris", "Kempczinski")},
    "samsung.com": {"CEO": ("Jong-Hee", "Han")},
    "amazon.com": {"CEO": ("Andrew", "Jassy")},
    "apple.com": {"CEO": ("Tim", "Cook")},
    "ford.com": {"CEO": ("Jim", "Farley")},
    "klarna.com": {"CEO": ("Sebastian", "Siemiatkowski")},
    "walmart.com": {"CEO": ("John", "Furner")},
    "duolingo.com": {"CEO": ("Luis", "von Ahn")},
    "bankofamerica.com": {"CEO": ("Brian", "Moynihan")},
    "morganstanley.com": {"CEO": ("Ted", "Pick")},
    "disney.com": {"CEO": ("Bob", "Iger")},
    "spotify.com": {"CEO": ("Daniel", "Ek")},
    **EXTRA_KNOWN_EXECUTIVES,
}

KNOWN_LINKEDIN: dict[str, dict[str, str]] = {
    "amazon.com": {"CEO": "http://www.linkedin.com/in/andrew-r-jassy-12384421a"},
    "morganstanley.com": {"CEO": "http://www.linkedin.com/in/tedpantaleev"},
    "duolingo.com": {"CEO": "http://www.linkedin.com/in/luis-von-ahn-duolingo"},
    "uber.com": {"CEO": "http://www.linkedin.com/in/dara-k"},
    "box.com": {"CEO": "http://www.linkedin.com/in/aaronlevie"},
    "klarna.com": {"CEO": "http://www.linkedin.com/in/sebastiansiemiatkowski"},
    "spotify.com": {"CEO": "http://www.linkedin.com/in/ekd"},
}

FIELDNAMES = [
    "Company",
    "Domain",
    "Stage",
    "Hesitancy_Summary",
    "Source_URL",
    "Statement_Date",
    "Contact_Role",
    "First_Name",
    "Last_Name",
    "Title",
    "Email",
    "LinkedIn_URL",
    "Location",
    "Apollo_ID",
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
            time.sleep(2**attempt)
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
        if any(x in t for x in ["ceo office", "assistant to", "strategy -"]):
            return False
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
    if role == "CIO":
        if "executive assistant" in t or "assistant to" in t:
            return False
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
        "Hesitancy_Summary": co["Hesitancy_Summary"],
        "Source_URL": co["Source_URL"],
        "Statement_Date": co["Statement_Date"],
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


def email_plausible(email: str, domain: str) -> bool:
    if not email or "@" not in email:
        return True
    local, _, host = email.lower().partition("@")
    if not host:
        return False
    bad_hosts = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "munsen.net", "opsline.com"}
    if host in bad_hosts:
        return False
    root = domain.lower().removeprefix("www.").split("/")[0]
    base = root.split(".")[0]
    return base in host or host.endswith(root) or host.endswith(root.split(".", 1)[-1])


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
                row = person_row(co, role, person)
                if email_plausible(row["Email"], domain):
                    return row

    linkedin = KNOWN_LINKEDIN.get(domain, {}).get(role)
    if linkedin:
        person = match_by_linkedin(api_key, linkedin)
        time.sleep(0.35)
        if person and (person.get("email") or person.get("linkedin_url")):
            row = person_row(co, role, person)
            if email_plausible(row["Email"], domain):
                return row

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
                row = person_row(co, role, person)
                if email_plausible(row["Email"], domain):
                    return row
    return None


def main() -> None:
    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not api_key:
        print("Set APOLLO_API_KEY", file=sys.stderr)
        sys.exit(1)

    raw_path = "leads/ai-hesitancy-companies-raw.csv"
    out_path = "leads/ai-hesitancy-contacts.csv"

    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "Company",
                "Domain",
                "Stage",
                "Hesitancy_Summary",
                "Source_URL",
                "Statement_Date",
            ],
        )
        w.writeheader()
        w.writerows(COMPANIES)

    seen: set[str] = set()
    rows: list[dict[str, str]] = []

    for co in COMPANIES:
        print(f"Searching {co['Company']} ({co['Domain']})...")
        found: dict[str, dict[str, str]] = {}
        for role in TARGET_ROLES:
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

        rows.extend(found[r] for r in TARGET_ROLES if r in found)
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
