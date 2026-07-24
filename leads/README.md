# Apollo ERP / SAP / B2B / CIMS US Leads

## Files

| File | Description |
|------|-------------|
| `apollo-erp-sap-b2b-cims-us-leads.csv` | 39 US-first prospects with LinkedIn URLs (public research) |
| `ai-agent-eo-insurance-providers.csv` | AI / agent insurance providers, brokers, and certified insured AI vendors |
| `apollo_enrich_leads.py` | Apollo API script to pull + enrich emails when `APOLLO_API_KEY` is set |
| `vendor-customers-raw.csv` | Public customers of Rex, Nanonets, TRM, Medius, Giga, etc. (87 vendor-customer pairs) |
| `vendor-customer-finance-it-contacts.csv` | Apollo-enriched CIO / VP Finance / VP Security at those customer companies |
| `apollo_enrich_vendor_customers.py` | Regenerate vendor customer contact enrichment via Apollo |
| `populate_google_sheet.py` | Writes CSV to Google Sheets via service account |

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

Sheet columns: `Name`, `Company`, `Role`, `Department`, `Email`, `LinkedIn`, `Location`, `Apollo ID`, `Notes`.

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
