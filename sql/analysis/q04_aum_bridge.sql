-- Q4 | AUM bridge: why did AUM change each month?
-- Business question: is growth coming from advisors winning money (net new
-- assets) or just from markets going up?
--   closing AUM = opening AUM + net new assets + market movement
WITH closing AS (
    SELECT snapshot_date AS month_end, SUM(aum_value) AS closing_aum
    FROM wm.monthly_aum
    GROUP BY snapshot_date
),
flows AS (
    SELECT (DATE_TRUNC('month', txn_date) + INTERVAL '1 month - 1 day')::date AS month_end,
           SUM(CASE WHEN txn_type = 'Redemption' THEN -amount ELSE amount END) AS net_new_assets
    FROM wm.transactions
    GROUP BY 1
),
bridge AS (
    SELECT c.month_end,
           LAG(c.closing_aum) OVER (ORDER BY c.month_end) AS opening_aum,
           COALESCE(f.net_new_assets, 0)                  AS net_new_assets,
           c.closing_aum
    FROM closing c
    LEFT JOIN flows f USING (month_end)
)
SELECT month_end,
       ROUND(opening_aum / 1e7, 1)                                    AS opening_cr,
       ROUND(net_new_assets / 1e7, 1)                                 AS net_new_assets_cr,
       ROUND((closing_aum - opening_aum - net_new_assets) / 1e7, 1)   AS market_movement_cr,
       ROUND(closing_aum / 1e7, 1)                                    AS closing_cr
FROM bridge
WHERE opening_aum IS NOT NULL
ORDER BY month_end;
