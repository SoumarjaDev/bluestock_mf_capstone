# Data Quality Report — Day 1

**Project:** Bluestock MF Analytics Capstone
**Date:** Day 1 — Data Ingestion
**Prepared by:** Data Analyst Intern, Bluestock Fintech

---

## 1. Dataset Inventory

| # | Dataset | Rows | Columns | Status |
|---|---------|------|---------|--------|
| 1 | fund_master | 40 | 15 | OK |
| 2 | nav_history | 46,000 | 3 | OK |
| 3 | aum_by_fund_house | 90 | 5 | OK |
| 4 | monthly_sip_inflows | 48 | 6 | Missing values found |
| 5 | category_inflows | 144 | 3 | OK |
| 6 | industry_folio_count | 21 | 6 | OK |
| 7 | scheme_performance | 40 | 19 | OK |
| 8 | investor_transactions | 32,778 | 13 | OK |
| 9 | portfolio_holdings | 322 | 8 | OK |
| 10 | benchmark_indices | 8,050 | 3 | OK |

**Result:** 10/10 datasets loaded successfully. No files missing or corrupted.

---

## 2. Anomalies Found

### 2.1 Missing Values — `monthly_sip_inflows`
- Column `yoy_growth_pct` has **12 missing values (25%)**.
- **Root cause:** YoY (year-over-year) growth cannot be calculated for the first 12 months of the dataset (Jan–Dec 2022), since there is no prior-year data to compare against.
- **Verdict:** Not a data error — expected behavior. No action needed on Day 1; will be documented as-is during Day 2 cleaning (left as null, not imputed, since inventing a YoY figure would be misleading).

### 2.2 Duplicate Rows
- **None found** across any of the 10 datasets.

---

## 3. AMFI Code Validation

- Total unique AMFI codes in `fund_master`: **40**
- Total unique AMFI codes in `nav_history`: **40**
- **Result: PASS** — every fund in `fund_master` has complete matching NAV history. No orphan or missing codes.

This confirms it's safe to join `fund_master` and `nav_history` on `amfi_code` without data loss in later SQL/analytics steps.

---

## 4. Fund Master Profile

- **Fund houses:** 10 (SBI, HDFC, ICICI Prudential, Nippon India, Kotak Mahindra, Axis, Aditya Birla Sun Life, UTI, Mirae Asset, DSP)
- **Categories:** 2 (Equity, Debt)
- **Sub-categories:** 12 (Large Cap, Mid Cap, Small Cap, Flexi Cap, Value, ELSS, Large & Mid Cap, Liquid, Gilt, Short Duration, Index, Index/ETF)
- **Risk grades:** 5 (Low, Moderate, Moderately High, High, Very High)

---

## 5. Live API Data

Successfully fetched live NAV history from **mfapi.in** (no auth required) for 6 schemes:

| Scheme | AMFI Code | Records Fetched |
|--------|-----------|------------------|
| HDFC Top 100 | 125497 | 3,111 |
| SBI Bluechip | 119551 | 3,256 |
| ICICI Bluechip | 120503 | 3,327 |
| Nippon Large Cap | 118632 | 3,318 |
| Axis Bluechip | 119092 | 3,585 |
| Kotak Bluechip | 120841 | (see script output) |

All saved to `data/raw/live_nav_<code>.csv`.

---

## 6. Overall Verdict

**Data quality: GOOD.** No corrupted files, no duplicate rows, no broken foreign keys (AMFI codes). One expected null pattern identified and explained. Dataset is ready to proceed to Day 2 (cleaning + SQL schema design).

---

## 7. Open Items for Day 2

- Decide handling for `yoy_growth_pct` nulls (recommend: leave as null, flag in documentation).
- Standardize `transaction_type` values in `investor_transactions`.
- Validate `expense_ratio_pct` is within realistic range (0.1%–2.5%) per project spec.