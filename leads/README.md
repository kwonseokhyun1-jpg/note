# Apollo ERP / SAP / B2B / CIMS US Leads

## Files

| File | Description |
|------|-------------|
| `apollo-erp-sap-b2b-cims-us-leads.csv` | 38 US-first prospects with LinkedIn URLs (public research) |
| `apollo_enrich_leads.py` | Apollo API script to pull + enrich emails when `APOLLO_API_KEY` is set |

## Google Sheet

Target sheet: https://docs.google.com/spreadsheets/d/1MPK1t22VKc3Np47v7tK2tbN0xi0k0ygcQLF0LkUrPeA/edit

Import generated leads:

1. Run enrichment (see below) to create `leads/google-sheet-import.csv`
2. Open the sheet → **File → Import → Upload** → select `google-sheet-import.csv`
3. Choose **Replace current sheet** (or Insert new rows)

Sheet columns mapped: `Name`, `Company`, `Role`, `Department`, `Notes` (includes email + LinkedIn + location).

Apollo persona filter (UI only):  
https://app.apollo.io/#/people?qPersonPersonaIds[]=6a5083e1319cfc001052255d

## Apollo API enrichment

```bash
export APOLLO_API_KEY='your-master-key'
pip install requests
python3 leads/apollo_enrich_leads.py --output leads/apollo-enriched-leads.csv
python3 leads/apollo_enrich_leads.py \
  --input leads/apollo-erp-sap-b2b-cims-us-leads.csv \
  --output leads/apollo-enriched-leads.csv \
  --google-sheet-output leads/google-sheet-import.csv
```

Enrich the existing seed list:

```bash
python3 leads/apollo_enrich_leads.py \
  --input leads/apollo-erp-sap-b2b-cims-us-leads.csv \
  --output leads/apollo-enriched-leads.csv
```

`bulk_match` uses Apollo credits for verified emails.
