-- Q3 | Monthly AUM trend with growth rates
-- Business question: how fast is the book growing?
-- Technique: LAG() looks at the previous row (1 month back, or 12 months back)
WITH monthly AS (
    SELECT snapshot_date, SUM(aum_value) AS aum
    FROM wm.monthly_aum
    GROUP BY snapshot_date
)
SELECT snapshot_date,
       ROUND(aum / 1e7, 1)                                                    AS aum_cr,
       ROUND(100 * (aum / LAG(aum)     OVER (ORDER BY snapshot_date) - 1), 2) AS mom_growth_pct,
       ROUND(100 * (aum / LAG(aum, 12) OVER (ORDER BY snapshot_date) - 1), 1) AS yoy_growth_pct
FROM monthly
ORDER BY snapshot_date;
