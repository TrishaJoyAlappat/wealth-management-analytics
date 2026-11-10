-- Q7 | Advisors with the highest client churn
-- Business question: are some advisors losing clients faster than the firm average?
WITH per_advisor AS (
    SELECT a.advisor_id, a.advisor_name, a.branch,
           COUNT(*)                                        AS total_clients,
           COUNT(*) FILTER (WHERE c.status = 'Churned')    AS churned_clients
    FROM wm.advisors a
    JOIN wm.clients c USING (advisor_id)
    GROUP BY a.advisor_id, a.advisor_name, a.branch
)
SELECT advisor_id, advisor_name, branch, total_clients, churned_clients,
       ROUND(100.0 * churned_clients / total_clients, 1) AS churn_rate_pct,
       ROUND(100.0 * churned_clients / total_clients
             - (SELECT 100.0 * SUM(churned_clients) / SUM(total_clients) FROM per_advisor), 1)
                                                         AS pts_vs_firm_average
FROM per_advisor
ORDER BY churn_rate_pct DESC
LIMIT 10;
