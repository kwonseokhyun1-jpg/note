# Apollo ERP / SAP / B2B / CIMS US Leads

## Files

| File | Description |
|------|-------------|
| `apollo-erp-sap-b2b-cims-us-leads.csv` | 38 US-first prospects with LinkedIn URLs (public research) |
| `apollo_enrich_leads.py` | Apollo API script to pull + enrich emails when `APOLLO_API_KEY` is set |

## Google Sheet

Target sheet: https://docs.google.com/spreadsheets/d/1MPK1t22VKc3Np47v7tK2tbN0xi0k0ygcQLF0LkUrPeA/edit

### Automatic populate (recommended)

The cloud agent cannot write to Google Sheets without a **service account**. One-time setup:

1. [Google Cloud Console](https://console.cloud.google.com/) → IAM → Service Accounts → Create → JSON key
2. Share the sheet with the service account email (e.g. `...@....iam.gserviceaccount.com`) as **Editor**
3. Run:

```bash
export GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
pip install gspread google-auth
python3 leads/populate_google_sheet.py
```

### Manual import

1. Open `leads/google-sheet-import.csv` in Cursor and download it
2. Sheet → **File → Import → Upload** → **Replace current sheet**

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
