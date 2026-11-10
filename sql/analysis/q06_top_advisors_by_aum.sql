-- Q6 | Top 10 advisors by AUM
-- Business question: who manages the most client money?
-- Technique: RANK() window function over an aggregate
WITH latest AS (
    SELECT client_id, SUM(aum_value) AS aum
    FROM wm.monthly_aum
    WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM wm.monthly_aum)
    GROUP BY client_id
)
SELECT RANK() OVER (ORDER BY SUM(l.aum) DESC)                      AS aum_rank,
       a.advisor_id,
       a.advisor_name,
       a.branch,
       COUNT(*) FILTER (WHERE l.aum > 0)                           AS active_clients,
       ROUND(SUM(l.aum) / 1e7, 1)                                  AS aum_cr,
       ROUND(SUM(l.aum) / COUNT(*) FILTER (WHERE l.aum > 0) / 1e5, 1) AS avg_aum_per_client_lakh
FROM wm.advisors a
JOIN wm.clients c USING (advisor_id)
JOIN latest l USING (client_id)
GROUP BY a.advisor_id, a.advisor_name, a.branch
ORDER BY aum_rank
LIMIT 10;
