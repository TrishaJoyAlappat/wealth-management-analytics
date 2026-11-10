-- DQ4 | Business-rule checks (every violation count should be 0)
WITH last_snap AS (SELECT MAX(snapshot_date) AS d FROM wm.monthly_aum)
SELECT 'Transaction dated before onboarding' AS check_name, COUNT(*) AS violations
FROM wm.transactions t
JOIN wm.clients c USING (client_id)
WHERE t.txn_date < c.onboarding_date
UNION ALL
SELECT 'Churned client without churn_date', COUNT(*)
FROM wm.clients WHERE status = 'Churned' AND churn_date IS NULL
UNION ALL
SELECT 'Active client WITH a churn_date', COUNT(*)
FROM wm.clients WHERE status = 'Active' AND churn_date IS NOT NULL
UNION ALL
SELECT 'Churn date before onboarding date', COUNT(*)
FROM wm.clients WHERE churn_date < onboarding_date
UNION ALL
SELECT 'Churned client still holding AUM at last snapshot', COUNT(DISTINCT m.client_id)
FROM wm.monthly_aum m
JOIN wm.clients c USING (client_id)
WHERE c.status = 'Churned'
  AND m.snapshot_date = (SELECT d FROM last_snap)
  AND m.aum_value > 0
UNION ALL
SELECT 'Active client with zero AUM at last snapshot', COUNT(*)
FROM (SELECT c.client_id
      FROM wm.clients c
      JOIN wm.monthly_aum m USING (client_id)
      WHERE c.status = 'Active'
        AND m.snapshot_date = (SELECT d FROM last_snap)
      GROUP BY c.client_id
      HAVING SUM(m.aum_value) = 0) x;
