import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from dotenv import load_dotenv

# ───────────────────────────────────────────────────────────────────────────────
#                             LOAD ENVIRONMENT VARIABLES
# ───────────────────────────────────────────────────────────────────────────────

# Load values from .env file in current directory
load_dotenv()

# Path to your downloaded service-account JSON key file
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# Spreadsheet identifier: by title
SPREADSHEET_TITLE = os.getenv("SPREADSHEET_TITLE")

# The OAuth scopes required by gspread for Sheets + Drive access
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Optional overrides (leave None to use title)
SPREADSHEET_ID  = None
SPREADSHEET_URL = None

# Which worksheet to target inside the spreadsheet:
WORKSHEET_INDEX = 0
WORKSHEET_NAME  = None

# API settings
API_URL   = "https://alerts.vulmon.com/api/v1/recent_vulnerabilities"
API_TOKEN = os.getenv("VULMON_ALERTS_API_TOKEN")

# ───────────────────────────────────────────────────────────────────────────────
#                                 SCRIPT LOGIC
# ───────────────────────────────────────────────────────────────────────────────

def authenticate():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE,
        SCOPES
    )
    return gspread.authorize(creds)


def open_spreadsheet(client):
    if SPREADSHEET_ID:
        return client.open_by_key(SPREADSHEET_ID)
    if SPREADSHEET_URL:
        return client.open_by_url(SPREADSHEET_URL)
    return client.open(SPREADSHEET_TITLE)


def select_worksheet(spreadsheet):
    if WORKSHEET_NAME is not None:
        return spreadsheet.worksheet(WORKSHEET_NAME)
    return spreadsheet.get_worksheet(WORKSHEET_INDEX)


def fetch_data_from_api():
    """
    Fetches recent vulnerabilities from the API and returns
    a list of rows suitable for writing to the sheet.
    Each row corresponds to one vulnerability entry.
    """
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    data = response.json()

    # Build header row and data rows
    header = [
        "cve_id", "description", "cvssv2", "cvssv3",
        "cvssv4", "vmscore", "epss", "kev", "URL"
    ]
    rows = [header]

    # The API returns a list of objects, each with a "vulnerabilities" list
    for entry in data:
        for vuln in entry.get("vulnerabilities", []):
            rows.append([
                vuln.get("cve_id", ""),
                vuln.get("description", ""),
                vuln.get("cvssv2", ""),
                vuln.get("cvssv3", ""),
                vuln.get("cvssv4", ""),
                vuln.get("vmscore", ""),
                vuln.get("epss", ""),
                vuln.get("kev", ""),
                vuln.get("URL", "")
            ])
    return rows


def main():
    # 1. Authenticate and build client
    client      = authenticate()

    # 2. Open the target spreadsheet
    spreadsheet = open_spreadsheet(client)

    # 3. Select the worksheet
    worksheet   = select_worksheet(spreadsheet)

    # 4. Fetch latest data from API and prepare rows
    data_rows   = fetch_data_from_api()

    # 5. Clear existing contents
    worksheet.clear()

    # 6. Write the fetched rows, starting at A1
    worksheet.update("A1", data_rows)

    print("✅ Data fetched from API and written to sheet successfully!")

if __name__ == "__main__":
    main()
