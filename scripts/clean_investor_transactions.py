"""
clean_investor_transactions.py
--------------------------------
Day 2 - Module 2: Clean investor_transactions.csv

Purpose : Standardise transaction_type values, validate amount > 0,
          fix date formats, and check kyc_status against expected enum.
Input   : data/raw/08_investor_transactions.csv
Output  : data/processed/investor_transactions_clean.csv
"""

from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/08_investor_transactions.csv")
OUTPUT_PATH = Path("data/processed/investor_transactions_clean.csv")

# Canonical values we expect. Maps common variants -> standard label.
TRANSACTION_TYPE_MAP = {
    "sip": "SIP",
    "lumpsum": "Lumpsum",
    "lump sum": "Lumpsum",
    "redemption": "Redemption",
    "redeem": "Redemption",
}

VALID_KYC_STATUSES = {"Verified", "Pending"}


def load_raw_transactions(path: Path) -> pd.DataFrame:
    """Load raw investor transactions and parse date column."""
    df = pd.read_csv(path)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    return df


def standardise_transaction_type(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise transaction_type to canonical SIP / Lumpsum / Redemption."""
    cleaned = df["transaction_type"].str.strip().str.lower().map(TRANSACTION_TYPE_MAP)
    unmapped = cleaned.isna().sum()
    if unmapped:
        print(f"  WARNING: {unmapped} rows had unrecognised transaction_type values")
        unmapped_values = df.loc[cleaned.isna(), "transaction_type"].unique()
        print(f"    Unrecognised values: {unmapped_values}")
    df["transaction_type"] = cleaned
    return df


def validate_amount_positive(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows where amount_inr <= 0 (invalid transaction)."""
    invalid = df[df["amount_inr"] <= 0]
    if len(invalid) > 0:
        print(f"  WARNING: {len(invalid)} rows with amount_inr <= 0 removed")
        df = df[df["amount_inr"] > 0]
    else:
        print("  All transaction amounts are positive")
    return df


def validate_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows where transaction_date could not be parsed."""
    invalid = df["transaction_date"].isna().sum()
    if invalid:
        print(f"  WARNING: {invalid} rows with unparseable dates removed")
        df = df.dropna(subset=["transaction_date"])
    else:
        print("  All transaction dates parsed successfully")
    return df


def check_kyc_status(df: pd.DataFrame) -> pd.DataFrame:
    """Flag any kyc_status values outside the expected enum (does not drop)."""
    invalid_mask = ~df["kyc_status"].isin(VALID_KYC_STATUSES)
    invalid_count = invalid_mask.sum()
    if invalid_count:
        print(f"  WARNING: {invalid_count} rows with unexpected kyc_status values:")
        print(f"    {df.loc[invalid_mask, 'kyc_status'].unique()}")
    else:
        print(f"  All kyc_status values valid: {VALID_KYC_STATUSES}")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop fully duplicate transaction rows."""
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed:
        print(f"  Removed {removed} duplicate rows")
    else:
        print("  No duplicate rows found")
    return df


def clean_investor_transactions() -> pd.DataFrame:
    """Run the full investor_transactions cleaning pipeline."""
    print("Cleaning investor_transactions.csv...")

    df = load_raw_transactions(RAW_PATH)
    print(f"  Loaded {len(df)} raw rows")

    df = remove_duplicates(df)
    df = standardise_transaction_type(df)
    df = validate_amount_positive(df)
    df = validate_dates(df)
    df = check_kyc_status(df)

    df = df.sort_values("transaction_date").reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"  Saved {len(df)} clean rows -> {OUTPUT_PATH}")
    return df


if __name__ == "__main__":
    clean_investor_transactions()