-- Q12 | Suitability check: conservative clients holding a lot of equity
-- Business question: which clients' portfolios no longer match their stated risk
-- profile? (A real compliance and client-care topic.)
WITH latest AS (
    SELECT client_id,
           SUM(aum_value)                                        AS total_aum,
           SUM(aum_value) FILTER (WHERE asset_class = 'Equity')  AS equity_aum
    FROM wm.monthly_aum
    WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM wm.monthly_aum)
    GROUP BY client_id
    HAVING SUM(aum_value) > 0
)
SELECT c.client_id, c.full_name, c.segment, a.advisor_name,
       ROUND(100 * l.equity_aum / l.total_aum, 1) AS equity_pct,
       ROUND(l.total_aum / 1e5, 1)                AS aum_lakh
FROM latest l
JOIN wm.clients  c USING (client_id)
JOIN wm.advisors a USING (advisor_id)
WHERE c.risk_profile = 'Conservative'
  AND l.equity_aum / l.total_aum > 0.40
ORDER BY l.total_aum DESC
LIMIT 15;
