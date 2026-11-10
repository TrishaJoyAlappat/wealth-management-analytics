-- Q11 | AUM concentration: how much do the top clients hold?
-- Business question: how dependent is the firm on its biggest clients?
-- Technique: NTILE(10) splits clients into 10 equal groups; a running SUM()
-- OVER (ORDER BY ...) gives the cumulative share.
WITH client_aum AS (
    SELECT client_id, SUM(aum_value) AS aum
    FROM wm.monthly_aum
    WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM wm.monthly_aum)
    GROUP BY client_id
    HAVING SUM(aum_value) > 0
),
ranked AS (
    SELECT client_id, aum, NTILE(10) OVER (ORDER BY aum DESC) AS decile
    FROM client_aum
)
SELECT decile,
       COUNT(*)                                   AS clients,
       ROUND(SUM(aum) / 1e7, 1)                   AS aum_cr,
       ROUND(100 * SUM(aum) / SUM(SUM(aum)) OVER (), 1)               AS pct_of_aum,
       ROUND(100 * SUM(SUM(aum)) OVER (ORDER BY decile)
                 / SUM(SUM(aum)) OVER (), 1)                          AS cumulative_pct
FROM ranked
GROUP BY decile
ORDER BY decile;
