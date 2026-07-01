"""
clean_nav_history.py
---------------------
Day 2 - Module 1: Clean nav_history.csv

Purpose : Parse dates, sort chronologically per fund, forward-fill NAV
          gaps (market holidays), remove duplicates, validate NAV > 0.
Input   : data/raw/02_nav_history.csv
Output  : data/processed/nav_history_clean.csv
"""

from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/02_nav_history.csv")
OUTPUT_PATH = Path("data/processed/nav_history_clean.csv")


def load_raw_nav(path: Path) -> pd.DataFrame:
    """Load raw NAV history and parse date column."""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate (amfi_code, date) rows, keep first occurrence."""
    before = len(df)
    df = df.drop_duplicates(subset=["amfi_code", "date"], keep="first")
    removed = before - len(df)
    if removed:
        print(f"  Removed {removed} duplicate rows")
    return df


def fill_missing_business_days(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reindex each fund to a full business-day range and forward-fill NAV.
    This handles market holidays where no NAV was published.
    """
    filled_frames = []
    total_filled = 0

    for amfi_code, group in df.groupby("amfi_code"):
        group = group.sort_values("date").set_index("date")
        full_range = pd.bdate_range(group.index.min(), group.index.max())
        reindexed = group.reindex(full_range)

        filled_count = reindexed["nav"].isna().sum()
        total_filled += filled_count

        reindexed["nav"] = reindexed["nav"].ffill()
        reindexed["amfi_code"] = amfi_code
        reindexed.index.name = "date"
        filled_frames.append(reindexed.reset_index())

    if total_filled:
        print(f"  Forward-filled {total_filled} missing NAV values (holidays)")
    else:
        print("  No missing business days found - nothing to forward-fill")

    return pd.concat(filled_frames, ignore_index=True)


def validate_nav_positive(df: pd.DataFrame) -> pd.DataFrame:
    """Flag and remove rows where NAV <= 0 (invalid)."""
    invalid = df[df["nav"] <= 0]
    if len(invalid) > 0:
        print(f"  WARNING: {len(invalid)} rows with NAV <= 0 found and removed")
        df = df[df["nav"] > 0]
    else:
        print("  All NAV values are positive")
    return df


def clean_nav_history() -> pd.DataFrame:
    """Run the full nav_history cleaning pipeline."""
    print("Cleaning nav_history.csv...")

    df = load_raw_nav(RAW_PATH)
    print(f"  Loaded {len(df)} raw rows")

    df = remove_duplicates(df)
    df = fill_missing_business_days(df)
    df = validate_nav_positive(df)

    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    df["nav"] = df["nav"].round(4)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"  Saved {len(df)} clean rows -> {OUTPUT_PATH}")
    return df


if __name__ == "__main__":
    clean_nav_history()