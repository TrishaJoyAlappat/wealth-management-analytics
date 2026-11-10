# Interview Preparation Guide — 12 Grounded Q&A

*Project: Northstar Wealth Analytics Portfolio Project (100 % Synthetic Data)*

---

### 1. Can you walk me through the architecture and business purpose of this project?
**Answer:**  
"Northstar Wealth is a full-service wealth management firm managing ₹7,360.9 Cr across 4,419 active clients and 40 advisors across 8 Indian branches. The business objective was to provide executive visibility into AUM growth drivers, client attrition, advisor productivity, and portfolio compliance.  
Technically, the architecture is a modular, four-stage analytics pipeline:
1. **Raw Storage:** PostgreSQL 18 relational schema (`wm` schema) containing raw tables for clients, advisors, products, transactions, and monthly AUM snapshots.
2. **Quality & Cleaning:** Automated data-quality audit scripts (`dq01` to `dq06`) validating completeness, uniqueness, consistency, and roll-forward logic.
3. **Dimensional Reporting Layer:** Star-schema views (`vw_dim_client`, `vw_fact_transactions`, etc.) that handle standardization (e.g., branch names, age bands, dormancy flags) without altering raw tables.
4. **Consumption Layer:** Python-automated Excel packs with formulaic tie-outs for senior leadership, and an interactive Power BI dashboard for branch managers."

---

### 2. How did you audit and clean data quality without altering raw database tables?
**Answer:**  
"I enforced an immutable raw-data rule: raw tables are never modified directly; all remediation logic is encapsulated in SQL reporting views. During the initial audit:
* **Missing Cities:** 30 clients had NULL city fields, resolved in `vw_dim_client` using `COALESCE(ref_city.branch, 'Unknown')`.
* **Inconsistent City Text:** 60 records had case or spacing errors (e.g., `'MUMBAI'`, `'  Delhi NCR'`). These were standardized by joining against the canonical branch list using `LOWER(TRIM(c.city)) = LOWER(b.branch)`.
* **Duplicates:** 12 duplicate client pairs (24 records sharing identical name and date of birth) were identified. Rather than deleting records—which would corrupt historical transactional audit trails—I created a boolean flag `is_possible_duplicate` using window functions: `COUNT(*) OVER (PARTITION BY LOWER(TRIM(full_name)), date_of_birth) > 1`."

---

### 3. What is an AUM Bridge, and how did you calculate it using SQL window functions?
**Answer:**  
"An AUM Bridge explains why firm AUM moved between two periods using the identity:
$$\text{Closing AUM} = \text{Opening AUM} + \text{Net New Assets (NNA)} + \text{Market Movement}$$
In SQL (`sql/analysis/q04_aum_bridge.sql`), I aggregated month-end AUM snapshots and calculated Opening AUM using `LAG(closing_aum) OVER (ORDER BY month_end)`. I then aggregated transactions by calendar month to compute signed Net New Assets (Inflows minus Redemptions). Market movement was derived as the residual plug: `closing_aum - opening_aum - net_new_assets`.  
Over 2024–2025, Northstar grew from ₹5,161.0 Cr to ₹7,360.9 Cr (+₹2,199.9 Cr). The bridge proved that growth was balanced: ₹1,134.6 Cr came from advisor-won new assets, and ₹1,065.2 Cr came from market performance."

---

### 4. How did you verify that synthetic market movements and asset class returns were realistic?
**Answer:**  
"I built an AUM roll-forward reconciliation check (`sql/quality/dq05_aum_reconciliation.sql`). By taking monthly market movement per asset class and dividing by opening AUM, I calculated the implied monthly return.  
The data confirmed expected economic behavior:
* **Liquid Funds:** Steady, low-volatility returns of ~0.50 % to 0.58 % per month.
* **Debt Funds:** Consistent yields averaging ~0.60 % per month.
* **Equity:** Realistic market volatility, including positive momentum in late 2024 followed by a market correction of −7.00 % in March 2025 and −5.00 % in April 2025.  
This confirmed that synthetic portfolio valuation followed rigorous macroeconomic logic."

---

### 5. What did the data reveal about client churn across different acquisition channels?
**Answer:**  
"Firm-wide churn over two years was 11.6 % (581 out of 5,000 clients), resulting in ₹574.4 Cr of lost capital. However, segmenting by acquisition channel revealed stark divergence:
* **Digital Channel:** Suffered the highest churn at **18.2 %** (239 churned out of 1,314).
* **Referrals:** Showed strong stickiness with only **8.0 % churn** (140 churned out of 1,746).
* **Corporate Tie-ups & Walk-ins:** Recorded 10.5 % and 10.4 % churn, respectively.  
This demonstrates that digital client acquisition without personalized advisory touchpoints creates a 'leaky bucket' dynamic where upfront customer acquisition cost is forfeited."

---

### 6. How did market drawdowns impact client behavior, particularly by risk profile?
**Answer:**  
"Using a range-join with `GENERATE_SERIES` in SQL (`sql/analysis/q14_churn_by_risk_by_month.sql`), I tracked monthly client cohorts against stated risk profiles: Aggressive, Moderate, and Conservative.  
When the equity market contracted in March (−7.0 %) and April (−5.0 %) 2025, monthly churn among **Aggressive-profile clients surged to an average of 1.49 % per month from April to July 2025** (peaking at 1.82 % in July), compared to their historical baseline of ~0.48 % per month. Moderate and Conservative clients stayed relatively stable (~0.40 %–0.60 %). This proved that supposedly 'aggressive' investors panicked during drawdowns and redeemed at market bottoms, highlighting the need for proactive advisory outreach during corrections."

---

### 7. How did you define and quantify account dormancy, and why is it critical for wealth managers?
**Answer:**  
"Dormancy was defined as an **Active client with zero transactions in the last 180 days** relative to the latest snapshot date. In SQL, this was calculated via `COALESCE(MAX(txn_date), '1900-01-01') < as_of - INTERVAL '180 days'`.  
The query uncovered **776 dormant accounts holding ₹1,357.6 Cr (18.4 % of total firm AUM)**. Crucially, **53 UHNI clients alone held ₹804.3 Cr of this dormant pool**. Dormancy is the primary leading indicator of attrition—clients stop transacting months before transferring their assets away. Surfacing these specific accounts gave branch managers an actionable re-engagement pipeline."

---

### 8. How did you detect portfolio suitability violations and compliance risks?
**Answer:**  
"In wealth management, portfolio drift can expose firms to SEBI/regulatory penalties if client holdings deviate significantly from their documented risk tolerance.  
I created a suitability screening query (`sql/analysis/q12_suitability_flags.sql`) identifying clients registered with a **Conservative** risk profile whose current portfolio held **greater than 40 % in equity**.  
The check flagged **166 Conservative clients** exceeding this threshold. The highest-exposure account was a UHNI client holding ₹16.8 Cr with 44.9 % equity, and another holding ₹16.5 Cr with 56.4 % equity. This became a dedicated remediation dashboard view for compliance officers."

---

### 9. What is the difference between client-level AUM skew and data errors?
**Answer:**  
"In `sql/quality/dq06_outliers.sql`, I analyzed the distribution of client AUM. The median client held ₹35.9 lakh, the 99th percentile was ₹2,054.2 lakh, and the maximum account was ₹4,851.2 lakh.  
While this is an extreme right-skew, it is **economically authentic rather than an anomaly or data error**. Private wealth management inherently exhibits Pareto distributions: our decile concentration analysis (`q11`) showed that the top 10 % of clients (442 accounts) held 64.5 % of total firm AUM (₹4,748.6 Cr). Understanding this distinction prevents analysts from mistakenly trimming or winsorizing real high-net-worth relationships."

---

### 10. How did you automate the monthly reporting package and ensure data integrity?
**Answer:**  
"I built `code/monthly_report.py` in Python using `SQLAlchemy`, `pandas`, and `openpyxl`. The script executes in four strict stages:
1. **Quality Gate:** Before generating reports, it executes four business-rule tests (negative AUM, transactions prior to onboarding, churn date mismatches). If violations > 0, the script aborts immediately with an error log.
2. **Extraction:** Queries summary KPIs, AUM trends, segment mixes, advisor scorecards, and dormant client rosters.
3. **Excel Formatting:** Generates a 5-sheet workbook styled in corporate navy (`0B2545`), formatted numbers, frozen panes, and auto-filters.
4. **Formulaic Tie-Outs:** Uses `openpyxl` to inject live Excel formulas (`SUMIFS`, `COUNTIFS`) matching branch-level scorecard AUM and dormant assets back to headline KPIs, asserting a 0.1 % tolerance check (`OK`/`DIFF`)."

---

### 11. What are control totals, and how did they guarantee consistency across SQL, Excel, and Power BI?
**Answer:**  
"Control totals are an established financial engineering control: a standardized 'answer key' of 15 immutable benchmark metrics calculated directly from database facts (`sql/06_control_totals.sql`).  
These included Opening AUM (₹5,161.0 Cr), Closing AUM (₹7,360.9 Cr), 2-year NNA (₹1,134.6 Cr), Active Clients (4,419), Churn Rate (11.6 %), Churned Capital (₹574.4 Cr), and Dormant AUM (₹1,357.6 Cr).  
Whenever a DAX measure was authored in Power BI or an Excel formula was added, it was validated against [docs/control_totals.md](docs/control_totals.md). This prevented the common enterprise problem of conflicting numbers between BI dashboards and board presentations."

---

### 12. If you were deploying this pipeline into enterprise cloud production, what would you do next?
**Answer:**  
"I would implement four production enhancements:
1. **Orchestration & Data Contracts:** Migrate raw SQL views to **dbt (data build tool)** with automated schema and freshness tests running in an Airflow or GitHub Actions CI/CD pipeline.
2. **Machine Learning Churn Scoring:** Train an XGBoost classification model leveraging transactional recency, frequency, monetary value (RFM), and drawdown velocity to output a daily 'Churn Propensity Score' (0–100) per client.
3. **Automated Event-Driven Alerts:** Establish a webhook that automatically pings advisors on Microsoft Teams or Salesforce CRM when a portfolio breaches risk suitability or crosses the 120-day transaction inactivity mark.
4. **Row-Level Security (RLS):** Configure Power BI RLS so branch managers only view clients and advisors within their respective cities (e.g., Mumbai vs. Delhi NCR), while executive leadership retains firm-wide visibility."
