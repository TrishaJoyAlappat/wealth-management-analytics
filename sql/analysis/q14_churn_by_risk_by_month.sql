-- Q14 | BQ6: did churn change when markets fell, and which clients reacted?
-- For every month: clients on the books at the start of the month (the "at risk"
-- base) and the % of them who left that month, split by risk profile.
-- Technique: generate_series builds the month list; a range join finds who was
-- on the books; FILTER pivots the three risk profiles into columns.
WITH months AS (
    SELECT GENERATE_SERIES(DATE '2024-01-01', DATE '2025-12-01',
                           INTERVAL '1 month')::date AS month_start
),
on_books AS (                      -- one row per client per month they were on the books
    SELECT m.month_start, c.risk_profile, c.client_id,
           COALESCE(c.churn_date >= m.month_start
                    AND c.churn_date < m.month_start + INTERVAL '1 month',
                    FALSE) AS left_this_month      -- NULL churn_date -> FALSE
    FROM months m
    JOIN wm.clients c
      ON c.onboarding_date < m.month_start
     AND (c.churn_date IS NULL OR c.churn_date >= m.month_start)
)
SELECT month_start,
       COUNT(*)                                                       AS clients_at_start,
       COUNT(*) FILTER (WHERE left_this_month)                        AS churned,
       ROUND(100.0 * AVG(left_this_month::int)
             FILTER (WHERE risk_profile = 'Aggressive'),   2)         AS aggressive_pct,
       ROUND(100.0 * AVG(left_this_month::int)
             FILTER (WHERE risk_profile = 'Moderate'),     2)         AS moderate_pct,
       ROUND(100.0 * AVG(left_this_month::int)
             FILTER (WHERE risk_profile = 'Conservative'), 2)         AS conservative_pct
FROM on_books
GROUP BY month_start
ORDER BY month_start;
