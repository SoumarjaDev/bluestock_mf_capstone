"""
data_ingestion.py
------------------
Day 1: Load all 10 raw Bluestock MF datasets, inspect their structure,
and run basic anomaly checks before cleaning (Day 2).

Purpose : Ingest CSVs from data/raw/ and print shape, dtypes, head, and
          basic data-quality flags for each.
Input   : 10 CSV files inside data/raw/
Output  : Console report + dict of pandas DataFrames (name -> df)
"""

from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
RAW_DATA_DIR = Path("data/raw")

DATASET_FILES = {
    "fund_master": "01_fund_master.csv",
    "nav_history": "02_nav_history.csv",
    "aum_by_fund_house": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "benchmark_indices": "10_benchmark_indices.csv",
}


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------
def load_csv(file_path: Path) -> pd.DataFrame:
    """Load a single CSV into a DataFrame with error handling."""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing file: {file_path}")
    except pd.errors.EmptyDataError:
        raise ValueError(f"File is empty: {file_path}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Could not parse {file_path}: {e}")


def inspect_dataframe(name: str, df: pd.DataFrame) -> None:
    """Print shape, dtypes, and head for a DataFrame."""
    print(f"\n{'=' * 70}")
    print(f"DATASET: {name}")
    print(f"{'=' * 70}")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print("\nDtypes:")
    print(df.dtypes)
    print("\nHead:")
    print(df.head(3))


def detect_anomalies(name: str, df: pd.DataFrame) -> None:
    """Flag basic data-quality issues: nulls and duplicate rows."""
    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0]

    dup_count = df.duplicated().sum()

    print("\nAnomaly Check:")
    if null_cols.empty:
        print("  - No missing values detected")
    else:
        print(f"  - Missing values found in {len(null_cols)} column(s):")
        for col, count in null_cols.items():
            pct = round(count / len(df) * 100, 2)
            print(f"      {col}: {count} missing ({pct}%)")

    if dup_count == 0:
        print("  - No duplicate rows detected")
    else:
        print(f"  - {dup_count} duplicate row(s) found")


def load_all_datasets() -> dict:
    """Load, inspect, and anomaly-check every dataset. Returns dict of DataFrames."""
    dataframes = {}

    for name, filename in DATASET_FILES.items():
        file_path = RAW_DATA_DIR / filename
        try:
            df = load_csv(file_path)
            inspect_dataframe(name, df)
            detect_anomalies(name, df)
            dataframes[name] = df
        except (FileNotFoundError, ValueError) as e:
            print(f"\n[ERROR] Skipping '{name}': {e}")

    return dataframes


def explore_fund_master(df: pd.DataFrame) -> None:
    """Task 11: Print unique fund houses, categories, sub-categories, risk grades."""
    print(f"\n{'=' * 70}")
    print("FUND MASTER EXPLORATION")
    print(f"{'=' * 70}")
    print(f"\nUnique fund houses ({df['fund_house'].nunique()}):")
    print(df['fund_house'].unique())

    print(f"\nUnique categories ({df['category'].nunique()}):")
    print(df['category'].unique())

    print(f"\nUnique sub-categories ({df['sub_category'].nunique()}):")
    print(df['sub_category'].unique())

    print(f"\nUnique risk categories ({df['risk_category'].nunique()}):")
    print(df['risk_category'].unique())


def validate_amfi_codes(fund_master: pd.DataFrame, nav_history: pd.DataFrame) -> None:
    """Task 12: Check every amfi_code in fund_master exists in nav_history."""
    print(f"\n{'=' * 70}")
    print("AMFI CODE VALIDATION")
    print(f"{'=' * 70}")

    master_codes = set(fund_master['amfi_code'])
    nav_codes = set(nav_history['amfi_code'])

    missing_in_nav = master_codes - nav_codes
    extra_in_nav = nav_codes - master_codes

    print(f"\nTotal codes in fund_master: {len(master_codes)}")
    print(f"Total unique codes in nav_history: {len(nav_codes)}")

    if not missing_in_nav:
        print("PASS: All fund_master codes have matching NAV history.")
    else:
        print(f"FAIL: {len(missing_in_nav)} code(s) in fund_master missing from nav_history:")
        print(missing_in_nav)

    if extra_in_nav:
        print(f"NOTE: {len(extra_in_nav)} code(s) in nav_history not present in fund_master:")
        print(extra_in_nav)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Starting Bluestock MF data ingestion...")
    all_data = load_all_datasets()
    print(f"\n{'=' * 70}")
    print(f"Ingestion complete. {len(all_data)}/{len(DATASET_FILES)} datasets loaded successfully.")
    print(f"{'=' * 70}")

    if "fund_master" in all_data:
        explore_fund_master(all_data["fund_master"])

    if "fund_master" in all_data and "nav_history" in all_data:
        validate_amfi_codes(all_data["fund_master"], all_data["nav_history"])