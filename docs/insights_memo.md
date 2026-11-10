# Executive Insights Memo — Northstar Wealth

**To:** Head of Wealth Management  
**From:** Trisha Joy Alappat, Lead Wealth Analytics  
**Date:** 10 November 2026  
**Subject:** 2024–2025 Portfolio Performance, Retention Risks, and Strategic Opportunities  

---

### Executive Headline
Northstar Wealth expanded total assets under management by 42.6 % from Rs 5,161.0 Cr to Rs 7,360.9 Cr across 4,419 active clients over 2024–2025, but Rs 574.4 Cr in churned assets and Rs 1,357.6 Cr trapped in dormant accounts expose critical retention vulnerabilities.

---

### Key Findings

1. **Digital acquisition channels suffer from high attrition compared to relationship-driven channels.**  
   *Evidence:* Clients acquired through the Digital channel exhibited an 18.2 % churn rate (239 departures out of 1,314 clients), more than double the 8.0 % churn observed in the Referral channel (140 churned of 1,746) and substantially higher than Branch Walk-ins (10.4 %). Across the firm, 581 clients (11.6 % of total clients) departed over the two-year period, representing a direct loss of Rs 574.4 Cr in client capital.  
   *So what:* *Scaling customer acquisition through low-touch digital channels creates a leaky bucket; without high-touch onboarding, upfront marketing acquisition costs are forfeited before accounts achieve lifetime profitability.*

2. **Market corrections trigger sharp, concentrated churn spikes among aggressive-profile investors.**  
   *Evidence:* When equity markets dropped by 7.00 % in March 2025 and 5.00 % in April 2025—driving month-on-month firm AUM declines of 1.86 % and 1.29 %—churn among Aggressive-risk clients escalated to an average of 1.49 % per month between April and July 2025 (peaking at 1.82 % in July). In contrast, aggressive clients churned at just 0.48 % per month during baseline market conditions.  
   *So what:* *Aggressive investors lack adequate advisory buffer and panic during drawdowns, redeeming at market troughs and cementing portfolio losses that permanently damage firm fee income.*

3. **High portfolio concentration intersects with widespread dormancy and asset suitability drift.**  
   *Evidence:* The top decile of clients (442 accounts) holds 64.5 % of firm AUM (Rs 4,748.6 Cr), underscoring immense book concentration. At the same time, 776 active accounts (17.6 % of all active clients) holding Rs 1,357.6 Cr (18.4 % of firm AUM) have registered zero transactions in the last 180 days, led by 53 UHNI accounts holding Rs 804.3 Cr. Concurrently, 166 Conservative clients hold over 40 % in equity assets, representing an immediate regulatory suitability hazard.  
   *So what:* *Dormancy is the strongest precursor to outright churn; failing to re-engage even a dozen dormant UHNI clients creates severe downside risk to branch revenue targets and exposes the firm to compliance penalties.*

---

### Strategic Recommendations

| # | Strategic Initiative | Owner Role | Primary Target Metric | Timeframe |
|---|----------------------|------------|-----------------------|-----------|
| **1** | **Digital Onboarding & Retention Overhaul:** Introduce automated 30/60/90-day advisory check-ins, targeted risk-profiling validation, and assigned digital relationship managers. | Head of Digital Wealth | Reduce Digital channel churn from 18.2 % to < 12.0 %; lift 90-day active engagement to > 85 %. | Q1 2026 – Q4 2026 (Rollout in 60 days) |
| **2** | **Market Volatility Advisory Playbook:** Deploy automated drawdown alerts to advisors when client portfolios decline > 5 %, mandating proactive outreach and portfolio rebalancing consultations. | Head of Advisory / CIO | Lower market-drawdown churn in Aggressive portfolios from 1.49 %/mo to < 0.75 %/mo; remediate 100 % of the 166 conservative suitability exceptions. | Q1 2026 (Immediate implementation) |
| **3** | **High-Value Dormancy Reactivation Sprints:** Launch structured client reviews for the 776 dormant accounts, prioritizing the 53 UHNI accounts (Rs 804.3 Cr) and 201 HNI accounts (Rs 404.3 Cr). | National Sales Director / Branch Heads | Reactivate 40 % of dormant accounts (unlocking > Rs 500 Cr in active mandate flows) within 90 days. | Q1 2026 – Q2 2026 (90-day campaign) |

---

### Analytical Caveats
* **Synthetic Data:** All underlying database records and transaction histories were generated programmatically (seed=42) for analytical and demonstration purposes. Distributions and behavioral anomalies reflect synthetic modeling rather than real-world client psychology.
* **Small Advisor Sample Sizes:** Advisor-level metrics (e.g., Saumya Mall's 26.1 % churn or Anamika Kanda's 23.8 % churn) are based on modest portfolios of 80–275 clients each. Individual departures can distort percentage rankings.
* **Correlation vs. Causation:** Higher churn in the digital channel or specific branches reflects observable correlation; it may stem from client demographic differences, self-directed product selection, or vintage effects rather than advisory service deficits.

---

### Next Steps
1. Deploy the automated monthly reporting suite (`code/monthly_report.py`) with integrated cross-sheet tie-out validation for ongoing executive governance.
2. Publish Power BI reporting views (`sql/05_reporting_views.sql`) to production for branch manager self-service tracking.
3. Convene a branch leadership forum with Mumbai, Delhi NCR, and Hyderabad branch heads to address outlier churn and establish accountability for dormant UHNI mandates.
