#!/usr/bin/env python3
"""Parse AI Risk Summit speakers and enrich with Apollo emails."""

from __future__ import annotations

import csv
import os
import re
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
    "Intel": "intel.com", "PwC": "pwc.com", "Vanguard": "vanguard.com", "NVIDIA": "nvidia.com",
    "Meta": "meta.com", "F5": "f5.com", "Adobe": "adobe.com", "Microsoft": "microsoft.com",
    "Broadcom": "broadcom.com", "Donnelley Financial Solutions (DFIN)": "dfinsolutions.com",
    "Akto IO": "akto.io", "Navy Federal Credit Union": "navyfederal.org",
    "Delinea": "delinea.com", "Scale AI": "scale.com", "Amazon AWS": "amazon.com",
    "Amazon": "amazon.com", "Google": "google.com", "Salesforce": "salesforce.com",
    "Airbnb": "airbnb.com", "Deloitte": "deloitte.com", "Oracle AI": "oracle.com",
    "Check Point": "checkpoint.com", "Sagility Health": "sagilityhealth.com",
    "HiddenLayer": "hiddenlayer.com", "Nudge Security": "nudgesecurity.com",
    "Rubrik": "rubrik.com", "Socure": "socure.com", "Kodem Security": "kodemsecurity.com",
    "Horizon3.ai": "horizon3.ai", "Sardine": "sardine.ai", "TELUS Digital": "telusdigital.com",
    "Intel": "intel.com", "Protegrity": "protegrity.com", "Mphasis": "mphasis.com",
    "Net Health": "nethealth.com", "Crescendo": "crescendo.ai", "StackGen": "stackgen.com",
    "LRQA": "lrqa.com", "Keyrock": "keyrock.eu", "Tenet Security": "tenetsecurity.com",
    "Prompt Security (SentinelOne)": "prompt.security",
}


def headers(api_key: str) -> dict[str, str]:
    return {"Content-Type": "application/json", "Cache-Control": "no-cache", "accept": "application/json", "x-api-key": api_key}


def match_person(api_key: str, first: str, last: str, org: str, domain: str | None) -> dict | None:
    payload: dict[str, Any] = {
        "first_name": first,
        "last_name": last,
        "reveal_personal_emails": False,
    }
    if domain:
        payload["organization_name"] = org
        payload["domain"] = domain
    resp = requests.post(f"{API_BASE}/people/match", headers=headers(api_key), json=payload, timeout=60)
    if resp.status_code not in (200, 201):
        return None
    return resp.json().get("person")


def split_name(full: str) -> tuple[str, str]:
    parts = full.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def main() -> None:
    api_key = os.environ.get("APOLLO_API_KEY", "").strip()
    out = "leads/ai-risk-summit-2026-attendees.csv"

    rows: list[dict[str, str]] = []

    for name, title, company, session in SPEAKERS:
        first, last = split_name(name)
        domain = DOMAIN_MAP.get(company)
        email, linkedin, location, apollo_id = "", "", "", ""
        if api_key and last:
            person = match_person(api_key, first, last, company, domain)
            if person:
                email = person.get("email") or ""
                linkedin = person.get("linkedin_url") or ""
                location = ", ".join(x for x in [person.get("city"), person.get("state"), person.get("country")] if x)
                apollo_id = person.get("id") or ""
            time.sleep(0.4)
        rows.append({
            "Role_Type": "Speaker",
            "Name": name,
            "Title": title,
            "Company": company,
            "Session": session,
            "Email": email,
            "LinkedIn_URL": linkedin,
            "Location": location,
            "Apollo_ID": apollo_id,
            "Source_URL": "https://www.airisksummit.com/speakers/",
            "Notes": "Confirmed speaker Aug 11-12 2026 Half Moon Bay",
        })

    for company, tier, website in SPONSORS:
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
            "Notes": f"Sponsor booth staff likely attending; website {website}",
        })

    fieldnames = ["Role_Type", "Name", "Title", "Company", "Session", "Email", "LinkedIn_URL", "Location", "Apollo_ID", "Source_URL", "Notes"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    emails = sum(1 for r in rows if r["Email"])
    print(f"Wrote {len(rows)} rows ({emails} with emails) to {out}")


if __name__ == "__main__":
    main()
