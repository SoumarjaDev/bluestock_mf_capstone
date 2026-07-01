"""
clean_scheme_performance.py
-----------------------------
Day 2 - Module 3: Clean scheme_performance.csv

Purpose : Validate all return/risk metric columns are numeric, flag
          statistical anomalies (e.g. negative Sharpe, positive drawdown),
          and check expense_ratio_pct falls within the realistic
          0.1%-2.5% range specified by the project.
Input   : data/raw/07_scheme_performance.csv
Output  : data/processed/scheme_performance_clean.csv
"""

from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/07_scheme_performance.csv")
OUTPUT_PATH = Path("data/processed/scheme_performance_clean.csv")

NUMERIC_COLUMNS = [
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct",
    "alpha", "beta", "sharpe_ratio", "sortino_ratio",
    "std_dev_ann_pct", "max_drawdown_pct", "expense_ratio_pct",
]

EXPENSE_RATIO_MIN = 0.1
EXPENSE_RATIO_MAX = 2.5


def load_raw_performance(path: Path) -> pd.DataFrame:
    """Load raw scheme performance data."""
    return pd.read_csv(path)


def validate_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce all metric columns to numeric; flag rows with invalid entries."""
    total_bad = 0
    for col in NUMERIC_COLUMNS:
        coerced = pd.to_numeric(df[col], errors="coerce")
        bad_count = coerced.isna().sum() - df[col].isna().sum()
        if bad_count > 0:
            print(f"  WARNING: {bad_count} non-numeric values found in '{col}'")
            total_bad += bad_count
        df[col] = coerced

    if total_bad == 0:
        print("  All metric columns are valid numeric values")
    return df


def flag_statistical_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag rows with statistically suspicious values. These are NOT dropped -
    they're flagged in a new column for manual review, since a fund CAN
    legitimately have negative Sharpe (poor performer) - it's rare, not invalid.
    """
    anomaly_flags = []

    negative_sharpe = df["sharpe_ratio"] < 0
    if negative_sharpe.any():
        print(f"  FLAG: {negative_sharpe.sum()} fund(s) with negative Sharpe ratio")
        anomaly_flags.append(negative_sharpe)

    positive_drawdown = df["max_drawdown_pct"] > 0
    if positive_drawdown.any():
        print(f"  FLAG: {positive_drawdown.sum()} fund(s) with positive max_drawdown (should be negative)")
        anomaly_flags.append(positive_drawdown)

    if not anomaly_flags:
        print("  No statistical anomalies detected (Sharpe, drawdown sign)")
        df["anomaly_flag"] = False
    else:
        combined = pd.concat(anomaly_flags, axis=1).any(axis=1)
        df["anomaly_flag"] = combined

    return df


def validate_expense_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """Check expense_ratio_pct falls within realistic 0.1%-2.5% range."""
    out_of_range = (df["expense_ratio_pct"] < EXPENSE_RATIO_MIN) | \
                    (df["expense_ratio_pct"] > EXPENSE_RATIO_MAX)

    if out_of_range.any():
        print(f"  WARNING: {out_of_range.sum()} fund(s) with expense_ratio_pct "
              f"outside {EXPENSE_RATIO_MIN}%-{EXPENSE_RATIO_MAX}% range:")
        print(df.loc[out_of_range, ["scheme_name", "expense_ratio_pct"]])
    else:
        print(f"  All expense_ratio_pct values within {EXPENSE_RATIO_MIN}%-{EXPENSE_RATIO_MAX}% range")

    return df


def clean_scheme_performance() -> pd.DataFrame:
    """Run the full scheme_performance cleaning pipeline."""
    print("Cleaning scheme_performance.csv...")

    df = load_raw_performance(RAW_PATH)
    print(f"  Loaded {len(df)} raw rows")

    df = validate_numeric_columns(df)
    df = flag_statistical_anomalies(df)
    df = validate_expense_ratio(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"  Saved {len(df)} rows -> {OUTPUT_PATH}")
    return df


if __name__ == "__main__":
    clean_scheme_performance()