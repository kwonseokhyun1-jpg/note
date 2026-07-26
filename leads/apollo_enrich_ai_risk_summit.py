#!/usr/bin/env python3
"""AI Risk Summit 2026: speakers + sponsor contacts enriched via Apollo (email + LinkedIn)."""

from __future__ import annotations

import csv
import os
import sys
import time
from typing import Any
from urllib.parse import quote

import requests

API_BASE = "https://api.apollo.io/api/v1"

SPEAKERS = [
    ("Ajit Joshi", "Senior Director, Engineering, Platform Security and Services", "Intel", "AI at the Edge of Trust: Securing the Next Wave of Enterprise Intelligence"),
    ("Alex Levinson", "CEO", "8oS Global", "The New Fog of War: Hidden Threats in an AI-Dominant World"),
    ("Allan Dabre", "Senior Manager, AI & Compliance", "PwC", "When AI Goes Wrong: A Practical Framework for Ethical Decision-Making"),
    ("Anant Somvanshi", "Sr. Specialist - AI Defense Office", "Vanguard", "Chain-of-Thought Monitorability in AI Governance"),
    ("Devashri Datta", "Security and Open Source Leader", "NVIDIA", "The Shadow Risk Problem: Governing Security Exceptions in AI-Driven Systems"),
    ("Ksheeraj Vepuri", "Senior Research Engineer", "Meta", "AI-Generated Media in the Wild: Risks, Failures, and Mitigations"),
    ("Michael Montoya", "Chief Technology Operations Officer", "F5", "Building the Defender Advantage in an AI-First World"),
    ("Saloni Garg", "Senior Machine Learning Engineer", "Adobe", "KV-Cache as Attack Surface: Side Channels in Shared LLM Inference Infrastructure"),
    ("Vaishnavi Gudur", "Senior Software Engineer", "Microsoft", "When Agents Go Rogue: A Threat Model and Defense Framework for Agentic AI Systems"),
    ("Advait Patel", "Senior Site Reliability Engineer (AIOps Security)", "Broadcom", "Attackers Figured Out That Your GenAI Deployment Is the Easiest Way Into Your Enterprise"),
    ("Akhil Sharma", "Senior Software Engineer", "Meta", "The Privacy-Personalization Paradox: Building Deep Memory Without Surveillance"),
    ("Alvina Antar", "Chief Digital Officer", "F5", "The Guardrail Paradox: Why the Most Secure AI Deployments Move the Fastest"),
    ("Chris Burger", "CISO", "F5", "From Strategy to Action: How CISOs Are Rewiring Security for the AI Era"),
    ("Anitha Dakamarri", "Manager/Lead Security Engineer", "Donnelley Financial Solutions (DFIN)", "Closing the AI Visibility Gap: Why SBOM Alone is No Longer Enough"),
    ("Ankita Gupta", "Co-Founder & CEO", "Akto IO", "5 Pillar Framework for Building an Enterprise AI Agents Governance and Security Program"),
    ("Anna Dudley", "Principal Advisor for Special Projects", "Altamira Corporation", "Red-Teaming Generative AI at Scale: The $14B Hallucination Scenario"),
    ("Anna Loshkareva", "Risk Officer Digital", "Navy Federal Credit Union", "Balancing Innovation and Control: How to Scale AI Safely Across the Enterprise"),
    ("Anshu Gupta", "CISO", "Fixin Security", "A Deep Dive into Model Context Protocol (MCP) Security"),
    ("Art Gilliland", "CEO", "Delinea", "Move Fast and Don't Break Things: A New Model for AI Governance"),
    ("Barak Sternberg", "Co-Founder & CEO", "Tenet Security", "Breaking the Agentic Sandbox"),
    ("Ben Goodman", "Founder & CEO", "CyRIsk", "The Underwriter in the Room: How Cyber Insurers Are Already Scoring Your AI Program"),
    ("Bethany Abbate", "Director, AI Policy", "Software & Information Industry Association (SIIA)", "Why Fragmented AI Policy is Fueling Public Skepticism"),
    ("Brandon Barnett", "CEO", "Trigate Coaching", "The Real Risk of AI Isn't Hallucinations - It's the Collapse of Business Models"),
    ("Bret Kinsella", "SVP & General Manager", "TELUS Digital", "The Good, the Sad and the Ugly: What Research Reveals About AI Safety and Security Gaps"),
    ("Cal Al-Dhubaib", "Principal Technologist, Cloud and AI", "Rubrik", "From AI Theory to Control"),
    ("David Abutbul", "AI Security Researcher", "Prompt Security (SentinelOne)", "When AI Agents Become the Supply Chain: Hidden Control Planes in Agentic Systems"),
    ("David Campbell", "Head of AI Security", "Scale AI", "Ignore Previous Instructions: Offensive Intelligence for the AI Era"),
    ("David Cass", "CISO", "Keyrock", "When AI Meets the Courtroom: Building Trustworthy AI Systems Through Legal and Technical Governance"),
    ("Deepanker Saxena", "Head of Product", "Socure", "When Face Value Is Dead, How Do You Get to Truth?"),
    ("Emily Ryan", "Commercial Client Security Director", "Intel", "Intel Executive Security Leadership Roundtable: Securing the AI-Driven Enterprise"),
    ("Eshaan Jain", "Senior Product Leader – AI & Enterprise Platforms", "Mphasis", "When AI Goes Wrong: A Practical Framework for Ethical Decision-Making"),
    ("Eti Rastogi", "Senior Applied Scientist", "Amazon AWS", "Beyond Vibes: Evaluation Strategies for Safe Multi-Turn AI Agents"),
    ("Jacob Rideout", "Chief Technology Officer", "HiddenLayer", "Allow? [Y/N] The Hidden Risks of AI Coding Tools"),
    ("James McCarthy", "Manager, Sales Engineering", "Horizon3.ai", "Proving Cyber Resilience: Measuring Outcomes, Not Effort"),
    ("Jerry Adams Franklin", "AI/ML Research Consultant", "Independent (Ex-DCG & Intel)", "Federated Learning as AI Risk Infrastructure"),
    ("Jose Toledo", "Principal Consultant", "Google (Mandiant)", "AI Agent Governance for Risk Leaders: Lessons from the Frontlines"),
    ("Joshua Copeland", "Director of Cybersecurity", "Crescendo", "AI Without Borders: The Collision of Regulation, Innovation, and Enterprise Reality"),
    ("Kayla Williams", "Co-Founder/Principal", "Williams Rose AI Cyber Advisory", "AI Without Borders: The Collision of Regulation, Innovation, and Enterprise Reality"),
    ("Keavy Murphy", "Vice President - Security", "Net Health", "Rethinking AI Risk Management as an Enabler"),
    ("Kellep Charles", "Cybersecurity Department Chair", "Capitol Technology University", "Securing AI Systems Through LLM Red Teaming"),
    ("Kunal Anand", "Chief Product Officer", "F5", "The New Security Model: When Software Stops Following Instructions"),
    ("Leah Siskind", "Director of Impact and AI Research Fellow", "Foundation for Defense of Democracies", "Iran Tested It First: What State-Sponsored Deepfakes Mean for Every CISO"),
    ("Mahesh Babu", "Chief Strategy Officer", "Kodem Security", "When AI Coding Agents Become an Attack Surface"),
    ("Malcolm Harkins", "Chief Security & Trust Officer", "HiddenLayer", "When Trust Has No Security: AI Risks Everything"),
    ("Mani Ganesan", "Vice President of Product Management", "F5", "Securing AI: From Guardrails to the Enterprise Control Plane"),
    ("Matt Fiedler", "Sr. Product Manager, AI Agent Security", "Check Point", "Breaking the Sound Barrier: End-to-End Red Teaming for AI Voice Agents"),
    ("Maulik Bhatt", "Senior Software Engineer", "Amazon AWS", "The Synthetic Insider: When Deepfakes and Autonomous AI Agents Collide"),
    ("Michael Howard", "CEO", "Protegrity", "Human in the Loop, Out of Control"),
    ("Millie Huang", "Principal Security Data Scientist", "Salesforce", "Stopping Rogue Agents in Flight: Real-Time Detection and Autonomous Containment"),
    ("Mudita Khurana", "Staff Security Engineer", "Airbnb", "Rethinking How we Evaluate Security Agents for Real-World Use"),
    ("Patrick Dillon", "CRO", "Nudge Security", "License to Govern: The Counterintelligence Playbook for AI Security"),
    ("Priyan Pattnayak", "Sr. Principal Scientist", "Oracle AI", "Chaos Testing for Chatbots: Simulating Customers to Evaluate AI Agents"),
    ("Raj Singh", "North America CISO", "Sagility Health", "Trustworthy AI in Healthcare: Defending the New Attack Surface"),
    ("Rakia Finley", "CEO", "Copper & Vine Studio", "From Prompt to Breach: Memory Forensics in AI-Augmented Attack Surfaces"),
    ("Ryan Fried", "Principal Security Consultant", "Google", "AI Agent Governance for Risk Leaders: Lessons from the Frontlines"),
    ("Sabah Rahman", "Design Leader / AI Explainability Researcher", "Amazon", "The EU AI Act Takes Effect This Year. Your Explainability Tools Aren't Ready."),
    ("Sanjeev Sharma", "Field CTO", "StackGen", "Governing the Intelligent Enterprise: AI Risk Management Frameworks"),
    ("Shruti Anand", "Product Lead Dev AI", "Google", "Why Responsible AI is a Hard Data Engineering Problem"),
    ("Soups Ranjan", "CEO", "Sardine", "The Rise of Agentic Fraud Ops: Fighting Fraud at Machine Speed"),
    ("Sourabh Kulkarni", "Research Scientist", "Meta", "AI-Generated Media in the Wild: Risks, Failures, and Mitigations"),
    ("Stephen Robinson", "Lead Threat Intelligence Researcher", "LRQA", "The Defender's Window"),
    ("Suraj Raghupathy Iswaran", "Senior Consultant, Cyber & Strategic Risk", "Deloitte", "Shadow AI and Third-Party Risk: Closing the Governance Gap"),
    ("Tricia Diamond", "Founder and Director", "Diamond PMO Solutions", "The Accountability Gap: Why AI Governance Fails Before the Breach Occurs"),
]

SPONSORS = [
    ("F5", "Presenting Sponsor", "f5.com"),
    ("TELUS Digital", "Diamond Sponsor", "telusdigital.com"),
    ("HiddenLayer", "Platinum Sponsor", "hiddenlayer.com"),
    ("Nudge Security", "Platinum Sponsor", "nudgesecurity.com"),
    ("Intel", "Gold Sponsor", "intel.com"),
    ("Kodem Security", "Gold Sponsor", "kodemsecurity.com"),
    ("Horizon3.ai", "Gold Sponsor", "horizon3.ai"),
    ("Rubrik", "Gold Sponsor", "rubrik.com"),
    ("Fleak", "Gold Sponsor", "fleak.ai"),
    ("Sardine", "Gold Sponsor", "sardine.ai"),
    ("Factory", "Gold Sponsor", "factory.ai"),
    ("Delinea", "Gold Sponsor", "delinea.com"),
    ("Socure", "Gold Sponsor", "socure.com"),
    ("Commvault", "Gold Sponsor", "commvault.com"),
    ("Adaptive Security", "Gold Sponsor", "adaptivesecurity.com"),
    ("ThreatLocker", "Silver Sponsor", "threatlocker.com"),
]

DOMAIN_MAP = {
    "Intel": "intel.com",
    "PwC": "pwc.com",
    "Vanguard": "vanguard.com",
    "NVIDIA": "nvidia.com",
    "Meta": "meta.com",
    "F5": "f5.com",
    "Adobe": "adobe.com",
    "Microsoft": "microsoft.com",
    "Broadcom": "broadcom.com",
    "Donnelley Financial Solutions (DFIN)": "dfinsolutions.com",
    "Akto IO": "akto.io",
    "Navy Federal Credit Union": "navyfederal.org",
    "Delinea": "delinea.com",
    "Scale AI": "scale.com",
    "Amazon AWS": "amazon.com",
    "Amazon": "amazon.com",
    "Google": "google.com",
    "Google (Mandiant)": "google.com",
    "Salesforce": "salesforce.com",
    "Airbnb": "airbnb.com",
    "Deloitte": "deloitte.com",
    "Oracle AI": "oracle.com",
    "Check Point": "checkpoint.com",
    "Sagility Health": "sagility.com",
    "HiddenLayer": "hiddenlayer.com",
    "Nudge Security": "nudgesecurity.com",
    "Rubrik": "rubrik.com",
    "Socure": "socure.com",
    "Kodem Security": "kodemsecurity.com",
    "Horizon3.ai": "horizon3.ai",
    "Sardine": "sardine.ai",
    "TELUS Digital": "telusdigital.com",
    "Protegrity": "protegrity.com",
    "Mphasis": "mphasis.com",
    "Net Health": "nethealth.com",
    "Crescendo": "crescendo.ai",
    "StackGen": "stackgen.com",
    "LRQA": "lrqa.com",
    "Keyrock": "keyrock.eu",
    "Tenet Security": "tenetsecurity.ai",
    "Prompt Security (SentinelOne)": "sentinelone.com",
    "Fixin Security": "fixinsecurity.com",
    "CyRIsk": "cyrisk.com",
    "Software & Information Industry Association (SIIA)": "siia.net",
    "Capitol Technology University": "captechu.edu",
    "Foundation for Defense of Democracies": "fdd.org",
    "Commvault": "commvault.com",
    "Fleak": "fleak.ai",
    "Factory": "factory.ai",
    "Adaptive Security": "adaptivesecurity.com",
    "ThreatLocker": "threatlocker.com",
}

SPONSOR_TITLES = [
    "chief information security officer",
    "ciso",
    "vp security",
    "vice president security",
    "head of ai security",
    "head of security",
    "vp product security",
    "director security",
    "chief technology officer",
    "cto",
    "chief executive officer",
    "ceo",
    "chief revenue officer",
    "cro",
    "vp sales",
    "head of marketing",
]

FIELDNAMES = [
    "Role_Type", "Name", "Title", "Company", "Session", "Email", "LinkedIn_URL",
    "Location", "Apollo_ID", "Source_URL", "Notes",
]


def headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json",
        "x-api-key": api_key,
    }


def person_fields(person: dict[str, Any]) -> dict[str, str]:
    return {
        "Email": person.get("email") or "",
        "LinkedIn_URL": person.get("linkedin_url") or "",
        "Location": ", ".join(
            x for x in [person.get("city"), person.get("state"), person.get("country")] if x
        ),
        "Apollo_ID": person.get("id") or "",
    }


def match_person(
    api_key: str,
    first: str,
    last: str,
    org: str,
    domain: str | None,
) -> dict[str, Any] | None:
    payload: dict[str, Any] = {
        "first_name": first,
        "last_name": last,
        "reveal_personal_emails": False,
    }
    if domain:
        payload["organization_name"] = org
        payload["domain"] = domain
    resp = requests.post(
        f"{API_BASE}/people/match",
        headers=headers(api_key),
        json=payload,
        timeout=60,
    )
    if resp.status_code not in (200, 201):
        return None
    return resp.json().get("person")


def match_by_linkedin(api_key: str, linkedin_url: str) -> dict[str, Any] | None:
    url = (
        f"{API_BASE}/people/match?linkedin_url={quote(linkedin_url)}"
        "&reveal_personal_emails=false"
    )
    resp = requests.post(url, headers=headers(api_key), timeout=60)
    if resp.status_code not in (200, 201):
        return None
    return resp.json().get("person")


def enrich_by_id(api_key: str, person_id: str) -> dict[str, Any] | None:
    resp = requests.post(
        f"{API_BASE}/people/match",
        headers=headers(api_key),
        json={"id": person_id, "reveal_personal_emails": False},
        timeout=60,
    )
    if resp.status_code not in (200, 201):
        return None
    return resp.json().get("person")


def search_sponsor_contacts(api_key: str, domain: str) -> list[dict[str, Any]]:
    url = f"{API_BASE}/mixed_people/api_search?q_organization_domains_list[]={quote(domain)}&per_page=15&page=1"
    for title in SPONSOR_TITLES:
        url += f"&person_titles[]={quote(title)}"
    resp = requests.post(url, headers=headers(api_key), timeout=60)
    if resp.status_code != 200:
        return []
    return resp.json().get("people") or []


def split_name(full: str) -> tuple[str, str]:
    parts = full.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def enrich_speaker(api_key: str, name: str, company: str) -> dict[str, str]:
    first, last = split_name(name)
    domain = DOMAIN_MAP.get(company)
    person: dict[str, Any] | None = None

    if last:
        person = match_person(api_key, first, last, company, domain)
        time.sleep(0.35)

    if person and not person.get("email") and person.get("linkedin_url"):
        linked = match_by_linkedin(api_key, person["linkedin_url"])
        time.sleep(0.35)
        if linked:
            person = linked

    if person and not person.get("email") and person.get("id"):
        enriched = enrich_by_id(api_key, person["id"])
        time.sleep(0.35)
        if enriched:
            person = enriched

    if not person or (not person.get("email") and not person.get("linkedin_url")):
        if last and domain:
            person = match_person(api_key, first, last, company, None)
            time.sleep(0.35)

    if not person:
        return {"Email": "", "LinkedIn_URL": "", "Location": "", "Apollo_ID": ""}
    return person_fields(person)


def enrich_sponsor_person(api_key: str, person: dict[str, Any]) -> dict[str, str] | None:
    pid = person.get("id")
    if not pid:
        return None
    enriched = enrich_by_id(api_key, pid)
    time.sleep(0.35)
    if not enriched:
        return None
    if not enriched.get("email") and not enriched.get("linkedin_url"):
        return None
    name = " ".join(x for x in [enriched.get("first_name"), enriched.get("last_name")] if x)
    return {
        "Role_Type": "Sponsor Contact",
        "Name": name,
        "Title": enriched.get("title") or "",
        "Company": enriched.get("organization", {}).get("name") or person.get("organization_name") or "",
        "Session": "",
        "Email": enriched.get("email") or "",
        "LinkedIn_URL": enriched.get("linkedin_url") or "",
        "Location": ", ".join(
            x for x in [enriched.get("city"), enriched.get("state"), enriched.get("country")] if x
        ),
        "Apollo_ID": enriched.get("id") or "",
        "Source_URL": "https://www.airisksummit.com/sponsors/",
        "Notes": "Likely sponsor booth attendee (Apollo security/exec search)",
    }


def main() -> None:
    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not api_key:
        print("Set APOLLO_API_KEY", file=sys.stderr)
        sys.exit(1)

    out = "leads/ai-risk-summit-2026-attendees.csv"
    rows: list[dict[str, str]] = []
    seen_apollo: set[str] = set()

    print("Enriching speakers...")
    for name, title, company, session in SPEAKERS:
        fields = enrich_speaker(api_key, name, company)
        if fields.get("Apollo_ID"):
            seen_apollo.add(fields["Apollo_ID"])
        rows.append({
            "Role_Type": "Speaker",
            "Name": name,
            "Title": title,
            "Company": company,
            "Session": session,
            "Email": fields["Email"],
            "LinkedIn_URL": fields["LinkedIn_URL"],
            "Location": fields["Location"],
            "Apollo_ID": fields["Apollo_ID"],
            "Source_URL": "https://www.airisksummit.com/speakers/",
            "Notes": "Confirmed speaker Aug 11-12 2026 Half Moon Bay",
        })
        has = "email" if fields["Email"] else ("linkedin" if fields["LinkedIn_URL"] else "none")
        print(f"  {name}: {has}")

    print("\nSearching sponsor companies...")
    for company, tier, domain in SPONSORS:
        rows.append({
            "Role_Type": "Sponsor",
            "Name": "",
            "Title": tier,
            "Company": company,
            "Session": "",
            "Email": "",
            "LinkedIn_URL": "",
            "Location": "",
            "Apollo_ID": "",
            "Source_URL": "https://www.airisksummit.com/sponsors/",
            "Notes": f"Sponsor booth staff likely attending; website {domain}",
        })

        people = search_sponsor_contacts(api_key, domain)
        time.sleep(0.5)
        added = 0
        for person in people:
            pid = person.get("id")
            if not pid or pid in seen_apollo:
                continue
            if not person.get("has_email") and not person.get("linkedin_url"):
                continue
            row = enrich_sponsor_person(api_key, person)
            if not row:
                continue
            row["Company"] = company
            row["Notes"] = f"{tier}; likely booth attendee ({domain})"
            seen_apollo.add(pid)
            rows.append(row)
            added += 1
            if added >= 4:
                break
        print(f"  {company}: {added} contacts")

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    speakers = [r for r in rows if r["Role_Type"] == "Speaker"]
    sponsor_contacts = [r for r in rows if r["Role_Type"] == "Sponsor Contact"]
    emails = sum(1 for r in rows if r["Email"])
    linkedins = sum(1 for r in rows if r["LinkedIn_URL"])
    print(
        f"\nWrote {len(rows)} rows to {out}\n"
        f"  Speakers: {len(speakers)} ({sum(1 for r in speakers if r['Email'])} emails, "
        f"{sum(1 for r in speakers if r['LinkedIn_URL'])} LinkedIn)\n"
        f"  Sponsor contacts: {len(sponsor_contacts)}\n"
        f"  Total with email: {emails}, with LinkedIn: {linkedins}"
    )


if __name__ == "__main__":
    main()
