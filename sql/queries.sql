-- ============================================================
-- queries.sql
-- Bluestock MF Analytics - 10 Analytical Queries
-- Day 2: Data Cleaning + SQL Database Design
-- ============================================================


-- ------------------------------------------------------------
-- Q1: Top 5 funds by AUM
-- Business use: Identify the largest funds by assets under management -
-- useful for investors seeking established, high-trust funds.
-- ------------------------------------------------------------
SELECT f.scheme_name, f.fund_house, p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;


-- ------------------------------------------------------------
-- Q2: Average NAV per month for a given fund (example: amfi_code 119551)
-- Business use: Smooths daily NAV noise into a monthly trend line,
-- useful for dashboard summary views.
-- ------------------------------------------------------------
SELECT strftime('%Y-%m', nav_date) AS month, ROUND(AVG(nav), 2) AS avg_nav
FROM fact_nav
WHERE amfi_code = 119551
GROUP BY month
ORDER BY month;


-- ------------------------------------------------------------
-- Q3: SIP inflow year-over-year (from transaction-level data)
-- Business use: Tracks growth in SIP contributions year to year -
-- a key industry health indicator referenced throughout the project doc.
-- ------------------------------------------------------------
SELECT strftime('%Y', transaction_date) AS year,
       SUM(amount_inr) AS total_sip_inflow
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY year
ORDER BY year;


-- ------------------------------------------------------------
-- Q4: Transactions by state
-- Business use: Reveals geographic concentration of investor activity -
-- informs regional marketing/distribution strategy.
-- ------------------------------------------------------------
SELECT state, COUNT(*) AS tx_count, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;


-- ------------------------------------------------------------
-- Q5: Funds with expense_ratio < 1%
-- Business use: Low-cost funds are attractive to cost-conscious investors;
-- this surfaces candidates for a "low-cost fund" filter in the dashboard.
-- ------------------------------------------------------------
SELECT scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct;


-- ------------------------------------------------------------
-- Q6: Top 5 funds by Sharpe ratio (best risk-adjusted returns)
-- Business use: Sharpe ratio rewards return per unit of risk taken -
-- better fund-selection signal than raw returns alone.
-- ------------------------------------------------------------
SELECT f.scheme_name, p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 5;


-- ------------------------------------------------------------
-- Q7: Average expense ratio by category (Equity vs Debt)
-- Business use: Equity funds are typically costlier to manage than Debt;
-- this confirms/quantifies that pattern in the dataset.
-- ------------------------------------------------------------
SELECT category, ROUND(AVG(expense_ratio_pct), 3) AS avg_expense_ratio
FROM dim_fund
GROUP BY category;


-- ------------------------------------------------------------
-- Q8: Latest AUM snapshot by fund house
-- Business use: Ranks AMCs (fund houses) by current market share -
-- feeds the "Industry Overview" dashboard page (Day 5).
-- ------------------------------------------------------------
SELECT fund_house, aum_crore
FROM fact_aum
WHERE aum_date = (SELECT MAX(aum_date) FROM fact_aum)
ORDER BY aum_crore DESC;


-- ------------------------------------------------------------
-- Q9: SIP vs Lumpsum vs Redemption breakdown
-- Business use: Shows investor behaviour mix - high SIP transaction count
-- but lower average amount vs fewer, larger Lumpsum investments.
-- ------------------------------------------------------------
SELECT transaction_type, COUNT(*) AS tx_count, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount DESC;


-- ------------------------------------------------------------
-- Q10: Average investment ticket size by age group
-- Business use: Younger investors (18-25) show highest average ticket
-- size here - useful for demographic-targeted product design.
-- ------------------------------------------------------------
SELECT age_group, COUNT(*) AS tx_count, ROUND(AVG(amount_inr), 0) AS avg_ticket_size
FROM fact_transactions
GROUP BY age_group
ORDER BY avg_ticket_size DESC;