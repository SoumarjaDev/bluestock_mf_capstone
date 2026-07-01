"""
copy_remaining_datasets.py
----------------------------
Day 2: Copy the 7 datasets that already passed Day 1 anomaly checks
(no nulls, no duplicates) into data/processed/, with date columns
properly parsed. These don't need the heavier cleaning logic used
for nav_history, investor_transactions, and scheme_performance.

Purpose : Standardise date columns and move already-clean datasets
          into the processed folder for the SQLite load step.
Input   : 7 CSVs in data/raw/
Output  : 7 CSVs in data/processed/
"""

from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

# filename -> (output name, date column to parse, or None)
DATASETS = {
    "01_fund_master.csv": ("fund_master_clean.csv", "launch_date"),
    "03_aum_by_fund_house.csv": ("aum_by_fund_house_clean.csv", "date"),
    "04_monthly_sip_inflows.csv": ("monthly_sip_inflows_clean.csv", None),  # month = YYYY-MM
    "05_category_inflows.csv": ("category_inflows_clean.csv", None),       # month = YYYY-MM
    "06_industry_folio_count.csv": ("industry_folio_count_clean.csv", None),  # month = YYYY-MM
    "09_portfolio_holdings.csv": ("portfolio_holdings_clean.csv", "portfolio_date"),
    "10_benchmark_indices.csv": ("benchmark_indices_clean.csv", "date"),
}


def process_dataset(raw_filename: str, output_filename: str, date_col: str | None) -> None:
    """Load, parse date column if present, drop exact duplicates, save."""
    df = pd.read_csv(RAW_DIR / raw_filename)

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])

    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)

    output_path = PROCESSED_DIR / output_filename
    df.to_csv(output_path, index=False)

    note = f" (removed {removed} duplicates)" if removed else ""
    print(f"  {raw_filename} -> {output_path} ({len(df)} rows){note}")


def copy_remaining_datasets() -> None:
    """Process all 7 pre-validated datasets into data/processed/."""
    print("Copying remaining pre-validated datasets to data/processed/...")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for raw_filename, (output_filename, date_col) in DATASETS.items():
        process_dataset(raw_filename, output_filename, date_col)

    print("Done.")


if __name__ == "__main__":
    copy_remaining_datasets()