#!/usr/bin/env python3
"""
Write leads/google-sheet-import.csv into a Google Sheet.

Setup (one time):
1. Google Cloud Console → create service account → download JSON key
2. Share the target sheet with the service account email (Editor)
3. export GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/key.json

Usage:
  python3 leads/populate_google_sheet.py \
    --spreadsheet-id 1MPK1t22VKc3Np47v7tK2tbN0xi0k0ygcQLF0LkUrPeA \
    --input leads/google-sheet-import.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Install: pip install gspread google-auth", file=sys.stderr)
    sys.exit(1)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def load_credentials() -> Credentials:
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        print("Set GOOGLE_SERVICE_ACCOUNT_JSON to your service account JSON file path.", file=sys.stderr)
        sys.exit(1)
    if os.path.isfile(raw):
        return Credentials.from_service_account_file(raw, scopes=SCOPES)
    return Credentials.from_service_account_info(json.loads(raw), scopes=SCOPES)


def read_csv_rows(path: str) -> list[list[str]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate Google Sheet from CSV")
    parser.add_argument(
        "--spreadsheet-id",
        default="1MPK1t22VKc3Np47v7tK2tbN0xi0k0ygcQLF0LkUrPeA",
    )
    parser.add_argument("--input", default="leads/google-sheet-import.csv")
    parser.add_argument("--worksheet", default=None, help="Tab name (default: first sheet)")
    args = parser.parse_args()

    values = read_csv_rows(args.input)
    if not values:
        print("CSV is empty.", file=sys.stderr)
        sys.exit(1)

    creds = load_credentials()
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(args.spreadsheet_id)
    ws = sh.worksheet(args.worksheet) if args.worksheet else sh.sheet1

    ws.clear()
    ws.update(values, value_input_option="USER_ENTERED")
    print(f"Wrote {len(values) - 1} data rows to spreadsheet {args.spreadsheet_id}")


if __name__ == "__main__":
    main()
