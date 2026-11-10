-- =====================================================================
-- 06_control_totals.sql  -  "answer key" numbers used to test Power BI
-- Every Power BI measure must reproduce one of these values (Phase 6, validation step)
-- =====================================================================
WITH last_snap AS (SELECT MAX(snapshot_date) AS d FROM wm.monthly_aum),
     first_snap AS (SELECT MIN(snapshot_date) AS d FROM wm.monthly_aum),
     nna AS (SELECT SUM(signed_amount) AS total FROM wm.vw_fact_transactions),
     opening AS (SELECT SUM(aum_value) AS aum, COUNT(DISTINCT client_id) FILTER (WHERE aum_value > 0) AS clients
                 FROM wm.monthly_aum WHERE snapshot_date = (SELECT d FROM first_snap)),
     closing AS (SELECT SUM(aum_value) AS aum, COUNT(DISTINCT client_id) FILTER (WHERE aum_value > 0) AS clients
                 FROM wm.monthly_aum WHERE snapshot_date = (SELECT d FROM last_snap))
SELECT label, value
FROM (
    SELECT 1 AS ord, 'Opening AUM, 31-Dec-2023 (Rs Cr)' AS label,
           ROUND((SELECT aum FROM opening) / 1e7, 1)::text AS value
    UNION ALL SELECT 2, 'Closing AUM, 31-Dec-2025 (Rs Cr)', ROUND((SELECT aum FROM closing) / 1e7, 1)::text
    UNION ALL SELECT 3, 'Net new assets, 2024-2025 (Rs Cr)', ROUND((SELECT total FROM nna) / 1e7, 1)::text
    UNION ALL SELECT 4, 'Market movement, 2024-2025 (Rs Cr)',
           ROUND(((SELECT aum FROM closing) - (SELECT aum FROM opening) - (SELECT total FROM nna)) / 1e7, 1)::text
    UNION ALL SELECT 5, 'Net new assets, 2025 only (Rs Cr)',
           ROUND((SELECT SUM(signed_amount) FROM wm.vw_fact_transactions WHERE txn_date >= '2025-01-01') / 1e7, 1)::text
    UNION ALL SELECT 6, 'Active clients, 31-Dec-2023', (SELECT clients FROM opening)::text
    UNION ALL SELECT 7, 'Active clients, 31-Dec-2025', (SELECT clients FROM closing)::text
    UNION ALL SELECT 8, 'New clients onboarded 2024-2025',
           (SELECT COUNT(*) FROM wm.clients WHERE onboarding_date >= '2024-01-01')::text
    UNION ALL SELECT 9, 'Churned clients 2024-2025',
           (SELECT COUNT(*) FROM wm.clients WHERE status = 'Churned')::text
    UNION ALL SELECT 10, 'Churn rate 2024-2025 (%)',
           ROUND(100.0 * (SELECT COUNT(*) FROM wm.clients WHERE status = 'Churned')
                 / ((SELECT clients FROM opening)
                    + (SELECT COUNT(*) FROM wm.clients WHERE onboarding_date >= '2024-01-01')), 1)::text
    UNION ALL SELECT 11, 'Churned AUM 2024-2025 (Rs Cr)',
           ROUND((SELECT SUM(aum_lost) FROM wm.vw_dim_client) / 1e7, 1)::text
    UNION ALL SELECT 12, 'Dormant clients (as at 31-Dec-2025)',
           (SELECT COUNT(*) FROM wm.vw_dim_client WHERE is_dormant)::text
    UNION ALL SELECT 13, 'Dormant AUM (Rs Cr)',
           ROUND((SELECT SUM(aum_latest) FROM wm.vw_dim_client WHERE is_dormant) / 1e7, 1)::text
    UNION ALL SELECT 14, 'Equity share of AUM, 31-Dec-2025 (%)',
           ROUND(100 * (SELECT SUM(aum_value) FROM wm.monthly_aum
                        WHERE snapshot_date = (SELECT d FROM last_snap) AND asset_class = 'Equity')
                 / (SELECT aum FROM closing), 1)::text
    UNION ALL SELECT 15, 'Average AUM per active client, 31-Dec-2025 (Rs lakh)',
           ROUND((SELECT aum FROM closing) / (SELECT clients FROM closing) / 1e5, 1)::text
) x
ORDER BY ord;
