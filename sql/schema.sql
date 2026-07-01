-- ============================================================
-- schema.sql
-- Bluestock MF Analytics - SQLite Star Schema
-- Day 2: Data Cleaning + SQL Database Design
--
-- Design: 2 dimension tables + 4 fact tables (star schema).
-- Dimensions are looked up by fact tables via foreign keys,
-- enabling fast filtering/joining in BI tools (Power BI/Tableau).
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- DIMENSION: dim_fund
-- One row per mutual fund scheme. Master reference table.
-- ------------------------------------------------------------
DROP TABLE IF EXISTS dim_fund;
CREATE TABLE dim_fund (
    amfi_code           INTEGER PRIMARY KEY,
    fund_house          TEXT NOT NULL,
    scheme_name         TEXT NOT NULL,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         TEXT,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

-- ------------------------------------------------------------
-- DIMENSION: dim_date
-- One row per calendar date across the full project date range.
-- Enables year/month/quarter rollups without date-parsing in SQL.
-- ------------------------------------------------------------
DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date_id      INTEGER PRIMARY KEY,   -- YYYYMMDD as integer, e.g. 20220103
    full_date    TEXT NOT NULL UNIQUE,  -- ISO format YYYY-MM-DD
    year         INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    quarter      INTEGER NOT NULL,
    month_name   TEXT NOT NULL,
    is_weekday   INTEGER NOT NULL       -- 1 = Mon-Fri, 0 = Sat/Sun
);

-- ------------------------------------------------------------
-- FACT: fact_nav
-- Daily NAV per fund. Largest fact table (~46K+ rows).
-- ------------------------------------------------------------
DROP TABLE IF EXISTS fact_nav;
CREATE TABLE fact_nav (
    nav_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code         INTEGER NOT NULL,
    nav_date          TEXT NOT NULL,
    nav               REAL NOT NULL,
    daily_return_pct  REAL,             -- computed on Day 4 (Performance Analytics)
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    UNIQUE (amfi_code, nav_date)
);

CREATE INDEX idx_fact_nav_amfi_date ON fact_nav (amfi_code, nav_date);

-- ------------------------------------------------------------
-- FACT: fact_transactions
-- Individual investor SIP/Lumpsum/Redemption transactions.
-- ------------------------------------------------------------
DROP TABLE IF EXISTS fact_transactions;
CREATE TABLE fact_transactions (
    tx_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT NOT NULL,
    amfi_code           INTEGER NOT NULL,
    transaction_date    TEXT NOT NULL,
    transaction_type    TEXT NOT NULL CHECK (transaction_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount_inr          INTEGER NOT NULL CHECK (amount_inr > 0),
    state                TEXT,
    city                 TEXT,
    city_tier            TEXT,
    age_group            TEXT,
    gender                TEXT,
    annual_income_lakh   REAL,
    payment_mode         TEXT,
    kyc_status           TEXT CHECK (kyc_status IN ('Verified', 'Pending')),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX idx_fact_tx_amfi ON fact_transactions (amfi_code);
CREATE INDEX idx_fact_tx_date ON fact_transactions (transaction_date);
CREATE INDEX idx_fact_tx_state ON fact_transactions (state);

-- ------------------------------------------------------------
-- FACT: fact_performance
-- One snapshot row per fund with pre-computed risk/return metrics.
-- ------------------------------------------------------------
DROP TABLE IF EXISTS fact_performance;
CREATE TABLE fact_performance (
    amfi_code           INTEGER PRIMARY KEY,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           INTEGER,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    anomaly_flag        INTEGER DEFAULT 0,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- ------------------------------------------------------------
-- FACT: fact_aum
-- Quarterly AUM per fund house (industry-level, not per-scheme).
-- ------------------------------------------------------------
DROP TABLE IF EXISTS fact_aum;
CREATE TABLE fact_aum (
    aum_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house        TEXT NOT NULL,
    aum_date          TEXT NOT NULL,
    aum_lakh_crore    REAL,
    aum_crore         INTEGER,
    num_schemes       INTEGER
);

CREATE INDEX idx_fact_aum_house_date ON fact_aum (fund_house, aum_date);