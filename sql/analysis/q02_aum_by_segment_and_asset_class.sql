-- Q2 | AUM by segment and asset class (latest month)
-- Business question: where does the money sit, and how is each segment allocated?
-- Technique: SUM() OVER (PARTITION BY ...) for percentage-of-total
WITH base AS (
    SELECT c.segment, m.asset_class, SUM(m.aum_value) AS aum
    FROM wm.monthly_aum m
    JOIN wm.clients c USING (client_id)
    WHERE m.snapshot_date = (SELECT MAX(snapshot_date) FROM wm.monthly_aum)
    GROUP BY c.segment, m.asset_class
)
SELECT segment,
       asset_class,
       ROUND(aum / 1e7, 1)                                  AS aum_cr,
       ROUND(100 * aum / SUM(aum) OVER (PARTITION BY segment), 1) AS pct_of_segment,
       ROUND(100 * aum / SUM(aum) OVER (), 1)                     AS pct_of_firm
FROM base
ORDER BY segment, aum DESC;
