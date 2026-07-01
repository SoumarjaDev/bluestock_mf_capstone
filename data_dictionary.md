# Data Dictionary — Bluestock MF Analytics Platform

Reference documentation for `bluestock_mf.db`. Covers all 6 tables in the star schema: table purpose, column definitions, data types, and source lineage.

---

## dim_fund

Master reference table. One row per mutual fund scheme.

| Column | Type | Definition | Source |
|---|---|---|---|
| amfi_code | INTEGER (PK) | Unique AMFI scheme identifier | 01_fund_master.csv |
| fund_house | TEXT | Asset Management Company (AMC) name | 01_fund_master.csv |
| scheme_name | TEXT | Full official scheme name as registered with AMFI | 01_fund_master.csv |
| category | TEXT | Broad classification — Equity or Debt | 01_fund_master.csv |
| sub_category | TEXT | Fund style — Large Cap, Mid Cap, Small Cap, ELSS, Liquid, Gilt, etc. | 01_fund_master.csv |
| plan | TEXT | Regular or Direct plan | 01_fund_master.csv |
| launch_date | TEXT (ISO date) | Date the scheme was launched | 01_fund_master.csv |
| benchmark | TEXT | Official benchmark index used for performance comparison | 01_fund_master.csv |
| expense_ratio_pct | REAL | Annual fund management charge, expressed as a percentage | 01_fund_master.csv |
| exit_load_pct | REAL | Penalty charged on early redemption, as a percentage | 01_fund_master.csv |
| min_sip_amount | INTEGER | Minimum monthly SIP investment in INR | 01_fund_master.csv |
| min_lumpsum_amount | INTEGER | Minimum one-time investment in INR | 01_fund_master.csv |
| fund_manager | TEXT | Name of the scheme's primary fund manager | 01_fund_master.csv |
| risk_category | TEXT | SEBI-defined risk grade — Low, Moderate, Moderately High, High, Very High | 01_fund_master.csv |
| sebi_category_code | TEXT | Internal SEBI classification code (e.g. EC01 = Large Cap Equity) | 01_fund_master.csv |

---

## dim_date

Calendar dimension. One row per day, generated programmatically to cover the full date range spanned by the fact tables (2022-01-01 to 2026-05-31).

| Column | Type | Definition | Source |
|---|---|---|---|
| date_id | INTEGER (PK) | Date encoded as YYYYMMDD, e.g. 20220103 | Generated |
| full_date | TEXT (ISO date, unique) | Calendar date in YYYY-MM-DD format | Generated |
| year | INTEGER | Calendar year | Generated |
| month | INTEGER | Calendar month (1–12) | Generated |
| quarter | INTEGER | Fiscal quarter (1–4), calculated from month | Generated |
| month_name | TEXT | Three-letter month abbreviation (Jan, Feb, ...) | Generated |
| is_weekday | INTEGER | 1 if Monday–Friday, 0 if Saturday/Sunday | Generated |

---

## fact_nav

Daily Net Asset Value per fund. The largest fact table (46,000 rows).

| Column | Type | Definition | Source |
|---|---|---|---|
| nav_id | INTEGER (PK, autoincrement) | Surrogate key | Generated on load |
| amfi_code | INTEGER (FK → dim_fund) | Fund identifier | 02_nav_history.csv |
| nav_date | TEXT (ISO date) | Date the NAV was published | 02_nav_history.csv |
| nav | REAL | Net Asset Value in INR for that date | 02_nav_history.csv |
| daily_return_pct | REAL | Day-over-day percentage change in NAV — computed in Day 4 (Performance Analytics), null at load time | Computed |

Cleaning applied: duplicate (amfi_code, nav_date) pairs removed; missing business days forward-filled to handle market holidays; rows with nav ≤ 0 removed.

---

## fact_transactions

Individual investor transaction records — SIP contributions, lumpsum investments, and redemptions.

| Column | Type | Definition | Source |
|---|---|---|---|
| tx_id | INTEGER (PK, autoincrement) | Surrogate key | Generated on load |
| investor_id | TEXT | Unique investor identifier (format INV000001–INV005000) | 08_investor_transactions.csv |
| amfi_code | INTEGER (FK → dim_fund) | Fund the transaction relates to | 08_investor_transactions.csv |
| transaction_date | TEXT (ISO date) | Date the transaction occurred | 08_investor_transactions.csv |
| transaction_type | TEXT (CHECK: SIP/Lumpsum/Redemption) | Type of transaction | 08_investor_transactions.csv |
| amount_inr | INTEGER (CHECK > 0) | Transaction value in Indian Rupees | 08_investor_transactions.csv |
| state | TEXT | Investor's registered state | 08_investor_transactions.csv |
| city | TEXT | Investor's registered city | 08_investor_transactions.csv |
| city_tier | TEXT | T30 (top 30 cities) or B30 (beyond top 30), per AMFI classification | 08_investor_transactions.csv |
| age_group | TEXT | Investor age bracket (18-25, 26-35, 36-45, 46-55, 56+) | 08_investor_transactions.csv |
| gender | TEXT | Investor gender | 08_investor_transactions.csv |
| annual_income_lakh | REAL | Investor's declared annual income in INR lakh | 08_investor_transactions.csv |
| payment_mode | TEXT | UPI, Net Banking, Mandate, or Cheque | 08_investor_transactions.csv |
| kyc_status | TEXT (CHECK: Verified/Pending) | KYC compliance status | 08_investor_transactions.csv |

Cleaning applied: transaction_type values standardised to canonical labels; rows with amount_inr ≤ 0 removed; unparseable dates removed; kyc_status validated against expected enum.

---

## fact_performance

One snapshot row per fund with pre-computed risk and return metrics.

| Column | Type | Definition | Source |
|---|---|---|---|
| amfi_code | INTEGER (PK, FK → dim_fund) | Fund identifier | 07_scheme_performance.csv |
| return_1yr_pct | REAL | Trailing 1-year absolute return | 07_scheme_performance.csv |
| return_3yr_pct | REAL | 3-year CAGR | 07_scheme_performance.csv |
| return_5yr_pct | REAL | 5-year CAGR | 07_scheme_performance.csv |
| benchmark_3yr_pct | REAL | Benchmark index 3-year CAGR, for comparison | 07_scheme_performance.csv |
| alpha | REAL | Excess return over benchmark (return_3yr_pct − benchmark_3yr_pct) | 07_scheme_performance.csv |
| beta | REAL | Sensitivity to market movement; 1.0 = moves with the market | 07_scheme_performance.csv |
| sharpe_ratio | REAL | Risk-adjusted return relative to a risk-free rate; higher is better | 07_scheme_performance.csv |
| sortino_ratio | REAL | Like Sharpe, but penalises only downside volatility | 07_scheme_performance.csv |
| std_dev_ann_pct | REAL | Annualised standard deviation of daily returns | 07_scheme_performance.csv |
| max_drawdown_pct | REAL | Worst peak-to-trough decline, expressed as a negative percentage | 07_scheme_performance.csv |
| aum_crore | INTEGER | Scheme-level assets under management, in INR crore | 07_scheme_performance.csv |
| expense_ratio_pct | REAL | Annual fund management charge | 07_scheme_performance.csv |
| morningstar_rating | INTEGER | Star rating (1–5), based on risk-adjusted performance | 07_scheme_performance.csv |
| risk_grade | TEXT | SEBI risk category assigned to the scheme | 07_scheme_performance.csv |
| anomaly_flag | INTEGER (default 0) | 1 if the row was flagged during cleaning (e.g. negative Sharpe, positive drawdown) | Computed during Day 2 cleaning |

Note: scheme_name, fund_house, category, and plan are not duplicated here — they live in dim_fund and are retrieved via join on amfi_code.

---

## fact_aum

Quarterly assets under management, aggregated at the fund-house level.

| Column | Type | Definition | Source |
|---|---|---|---|
| aum_id | INTEGER (PK, autoincrement) | Surrogate key | Generated on load |
| fund_house | TEXT | Asset Management Company name | 03_aum_by_fund_house.csv |
| aum_date | TEXT (ISO date) | Quarter-end reporting date | 03_aum_by_fund_house.csv |
| aum_lakh_crore | REAL | Total AUM in INR lakh crore | 03_aum_by_fund_house.csv |
| aum_crore | INTEGER | Total AUM in INR crore | 03_aum_by_fund_house.csv |
| num_schemes | INTEGER | Number of schemes managed by the fund house at that date | 03_aum_by_fund_house.csv |

---

## Datasets not loaded into the database

The following provided CSVs were retained in `data/processed/` but not loaded into `bluestock_mf.db`, as they fell outside the 6-table schema defined for this project:

- **04_monthly_sip_inflows.csv** — industry-level SIP data. SIP trend analysis in this project is instead derived directly from `fact_transactions`, which offers transaction-level granularity.
- **05_category_inflows.csv** — category-level inflow data, reserved for Day 3 EDA work directly from the processed CSV.
- **06_industry_folio_count.csv** — industry-level folio counts, reserved for Day 3 EDA.
- **09_portfolio_holdings.csv** — equity holdings detail, reserved for Day 6 sector concentration analysis.
- **10_benchmark_indices.csv** — daily benchmark index values, reserved for Day 4 alpha/beta computation.

These remain available as clean CSVs and will be brought into later analysis stages as the relevant tasks require them.