# Apollo ERP / SAP / B2B / CIMS US Leads

## Files

| File | Description |
|------|-------------|
| `apollo-erp-sap-b2b-cims-us-leads.csv` | 38 US-first prospects with LinkedIn URLs (public research) |
| `apollo_enrich_leads.py` | Apollo API script to pull + enrich emails when `APOLLO_API_KEY` is set |

## Google Sheet

Target sheet: https://docs.google.com/spreadsheets/d/1-tdoLKJuzffG7Do0fYXFUEqRxstcUtGH3_o0C70aJ_U/edit

The sheet is currently private (sign-in required). To populate it:

1. **Quick import:** File → Import → Upload `apollo-erp-sap-b2b-cims-us-leads.csv`
2. **Share for agent access:** Sheet → Share → "Anyone with the link" → Editor
3. **Apollo UI export:** Open your persona search and export CSV, then merge with this file

Apollo persona filter (UI only):  
https://app.apollo.io/#/people?qPersonPersonaIds[]=6a5083e1319cfc001052255d

## Apollo API enrichment

```bash
export APOLLO_API_KEY='your-master-key'
pip install requests
python3 leads/apollo_enrich_leads.py --output leads/apollo-enriched-leads.csv
```

Enrich the existing seed list:

```bash
python3 leads/apollo_enrich_leads.py \
  --input leads/apollo-erp-sap-b2b-cims-us-leads.csv \
  --output leads/apollo-enriched-leads.csv
```

`bulk_match` uses Apollo credits for verified emails.
