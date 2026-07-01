"""
load_to_db.py
--------------
Day 2 - Module 5: Load all cleaned CSVs into SQLite using SQLAlchemy.

Purpose : Create bluestock_mf.db, run schema.sql to build the star
          schema, populate dim_date programmatically, load all
          cleaned datasets, and verify row counts match source CSVs.
Input   : 10 CSVs in data/processed/, sql/schema.sql
Output  : data/db/bluestock_mf.db
"""

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

PROCESSED_DIR = Path("data/processed")
SCHEMA_PATH = Path("sql/schema.sql")
DB_PATH = Path("data/db/bluestock_mf.db")

QUARTER_MAP = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def create_schema(engine) -> None:
    """Execute schema.sql to (re)create all tables."""
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    with engine.begin() as conn:
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
    print("  Schema created (6 tables)")


def build_dim_date(start: str, end: str) -> pd.DataFrame:
    """Generate a full calendar date dimension between start and end."""
    dates = pd.date_range(start=start, end=end, freq="D")
    df = pd.DataFrame({"full_date": dates})
    df["date_id"] = df["full_date"].dt.strftime("%Y%m%d").astype(int)
    df["year"] = df["full_date"].dt.year
    df["month"] = df["full_date"].dt.month
    df["quarter"] = df["month"].map(QUARTER_MAP)
    df["month_name"] = df["month"].apply(lambda m: MONTH_NAMES[m - 1])
    df["is_weekday"] = (df["full_date"].dt.dayofweek < 5).astype(int)
    df["full_date"] = df["full_date"].dt.strftime("%Y-%m-%d")
    return df[["date_id", "full_date", "year", "month", "quarter", "month_name", "is_weekday"]]


def load_table(engine, csv_name: str, table_name: str, column_map: dict = None,
                columns: list = None) -> int:
    """Load a cleaned CSV into a SQL table. Returns row count loaded."""
    df = pd.read_csv(PROCESSED_DIR / csv_name)
    if column_map:
        df = df.rename(columns=column_map)
    if columns:
        df = df[columns]
    df.to_sql(table_name, engine, if_exists="append", index=False)
    return len(df)


def verify_row_counts(engine, checks: list) -> None:
    """Compare source CSV row counts against loaded table row counts."""
    print("\nRow count verification:")
    all_match = True
    with engine.connect() as conn:
        for csv_name, table_name in checks:
            source_count = len(pd.read_csv(PROCESSED_DIR / csv_name))
            db_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            status = "OK" if source_count == db_count else "MISMATCH"
            if status == "MISMATCH":
                all_match = False
            print(f"  {table_name}: source={source_count}, db={db_count} [{status}]")
    print("\nAll row counts match!" if all_match else "\nWARNING: Row count mismatch detected!")


def main() -> None:
    print("Loading Bluestock MF data into SQLite...")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}")

    create_schema(engine)

    # dim_fund
    n = load_table(engine, "fund_master_clean.csv", "dim_fund")
    print(f"  Loaded {n} rows -> dim_fund")

    # dim_date: spans the widest range across all date-based fact tables
    dim_date_df = build_dim_date("2022-01-01", "2026-05-31")
    dim_date_df.to_sql("dim_date", engine, if_exists="append", index=False)
    print(f"  Loaded {len(dim_date_df)} rows -> dim_date")

    # fact_nav
    n = load_table(engine, "nav_history_clean.csv", "fact_nav",
                    column_map={"date": "nav_date"})
    print(f"  Loaded {n} rows -> fact_nav")

    # fact_transactions
    n = load_table(engine, "investor_transactions_clean.csv", "fact_transactions")
    print(f"  Loaded {n} rows -> fact_transactions")

    # fact_performance (subset of columns - scheme_name/fund_house/category/plan
    # already live in dim_fund, so we don't duplicate them here)
    performance_columns = [
        "amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio",
        "std_dev_ann_pct", "max_drawdown_pct", "aum_crore", "expense_ratio_pct",
        "morningstar_rating", "risk_grade", "anomaly_flag",
    ]
    n = load_table(engine, "scheme_performance_clean.csv", "fact_performance",
                    columns=performance_columns)
    print(f"  Loaded {n} rows -> fact_performance")

    # fact_aum
    n = load_table(engine, "aum_by_fund_house_clean.csv", "fact_aum",
                    column_map={"date": "aum_date"})
    print(f"  Loaded {n} rows -> fact_aum")

    verify_row_counts(engine, [
        ("fund_master_clean.csv", "dim_fund"),
        ("nav_history_clean.csv", "fact_nav"),
        ("investor_transactions_clean.csv", "fact_transactions"),
        ("scheme_performance_clean.csv", "fact_performance"),
        ("aum_by_fund_house_clean.csv", "fact_aum"),
    ])

    print(f"\nDatabase ready: {DB_PATH}")


if __name__ == "__main__":
    main()