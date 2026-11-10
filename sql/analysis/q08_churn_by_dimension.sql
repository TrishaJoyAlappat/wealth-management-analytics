-- Q8 | Who churns? Segment, risk profile and acquisition channel side by side
-- Technique: UNION ALL stacks three small summaries into one result
WITH base AS (
    SELECT segment, risk_profile, acquisition_channel,
           (status = 'Churned')::int AS churned
    FROM wm.clients
)
SELECT 'segment' AS dimension, segment AS value,
       COUNT(*) AS clients, SUM(churned) AS churned,
       ROUND(100.0 * AVG(churned), 1) AS churn_rate_pct
FROM base GROUP BY segment
UNION ALL
SELECT 'risk_profile', risk_profile, COUNT(*), SUM(churned), ROUND(100.0 * AVG(churned), 1)
FROM base GROUP BY risk_profile
UNION ALL
SELECT 'acquisition_channel', acquisition_channel, COUNT(*), SUM(churned), ROUND(100.0 * AVG(churned), 1)
FROM base GROUP BY acquisition_channel
ORDER BY dimension, churn_rate_pct DESC;
