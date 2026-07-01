"""
live_nav_fetch.py
------------------
Day 1: Fetch live/historical NAV data from the mfapi.in public API
and save as raw CSV files (simulates a real daily NAV refresh pipeline).

Purpose : Call mfapi.in for given scheme codes, parse the JSON NAV
          history, and save each as a CSV in data/raw/.
Input   : Scheme code(s) - e.g. 125497 for HDFC Top 100 Direct
Output  : data/raw/live_nav_<scheme_code>.csv per scheme
"""

from pathlib import Path
import requests
import pandas as pd

RAW_DATA_DIR = Path("data/raw")
API_BASE_URL = "https://api.mfapi.in/mf"

# Task 8: HDFC Top 100
# Task 10: 5 additional schemes
SCHEME_CODES = {
    "125497": "HDFC Top 100",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon Large Cap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip",
}


def fetch_nav_data(scheme_code: str) -> dict:
    """Call mfapi.in for a given scheme code. Returns parsed JSON."""
    url = f"{API_BASE_URL}/{scheme_code}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "SUCCESS":
            raise ValueError(f"API did not return SUCCESS status for {scheme_code}")
        return payload
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to fetch data for {scheme_code}: {e}")


def save_nav_to_csv(scheme_code: str, payload: dict) -> Path:
    """Convert mfapi.in JSON NAV history into a CSV file."""
    meta = payload.get("meta", {})
    nav_records = payload.get("data", [])

    if not nav_records:
        raise ValueError(f"No NAV records returned for {scheme_code}")

    df = pd.DataFrame(nav_records)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df["amfi_code"] = scheme_code
    df["scheme_name"] = meta.get("scheme_name", "Unknown")
    df["fund_house"] = meta.get("fund_house", "Unknown")

    df = df.sort_values("date").reset_index(drop=True)

    output_path = RAW_DATA_DIR / f"live_nav_{scheme_code}.csv"
    df.to_csv(output_path, index=False)
    return output_path


def fetch_and_save_all(scheme_codes: dict) -> None:
    """Loop through all scheme codes, fetch NAV data, and save as CSV."""
    for code, name in scheme_codes.items():
        print(f"\nFetching NAV data for {name} ({code})...")
        try:
            payload = fetch_nav_data(code)
            output_path = save_nav_to_csv(code, payload)
            record_count = len(payload.get("data", []))
            print(f"  Saved {record_count} NAV records -> {output_path}")
        except (ConnectionError, ValueError) as e:
            print(f"  [ERROR] {e}")


if __name__ == "__main__":
    print("Starting live NAV fetch from mfapi.in...")
    fetch_and_save_all(SCHEME_CODES)
    print("\nLive NAV fetch complete.")