-- Q1 | Headline KPIs
-- Business question: how big is the book today?
WITH latest AS (SELECT MAX(snapshot_date) AS as_of FROM wm.monthly_aum)
SELECT l.as_of,
       ROUND(SUM(m.aum_value) / 1e7, 1)                                       AS total_aum_cr,
       COUNT(DISTINCT m.client_id) FILTER (WHERE m.aum_value > 0)            AS active_clients,
       ROUND(SUM(m.aum_value)
             / COUNT(DISTINCT m.client_id) FILTER (WHERE m.aum_value > 0) / 1e5, 1) AS avg_aum_per_client_lakh
FROM wm.monthly_aum m
JOIN latest l ON m.snapshot_date = l.as_of
GROUP BY l.as_of;
