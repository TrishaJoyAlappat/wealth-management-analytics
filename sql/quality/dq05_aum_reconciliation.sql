-- DQ5 | AUM roll-forward reconciliation
-- Idea: closing AUM = opening AUM + net flows + market movement.
-- Market movement is the leftover, so dividing it by opening AUM gives an
-- "implied monthly return". Every client in an asset class got the same market
-- return, so the pattern must look realistic: Liquid ~0.5% every month,
-- Debt ~0.6%, Equity jumpy, with a visible sell-off in early 2025.
WITH closing AS (
    SELECT snapshot_date AS month_end, asset_class, SUM(aum_value) AS closing_aum
    FROM wm.monthly_aum
    GROUP BY snapshot_date, asset_class
),
flows AS (
    SELECT (DATE_TRUNC('month', t.txn_date) + INTERVAL '1 month - 1 day')::date AS month_end,
           p.asset_class,
           SUM(CASE WHEN t.txn_type = 'Redemption' THEN -t.amount ELSE t.amount END) AS net_flow
    FROM wm.transactions t
    JOIN wm.products p USING (product_id)
    GROUP BY 1, 2
),
bridge AS (
    SELECT c.month_end, c.asset_class, c.closing_aum,
           LAG(c.closing_aum) OVER (PARTITION BY c.asset_class ORDER BY c.month_end) AS opening_aum,
           COALESCE(f.net_flow, 0) AS net_flow
    FROM closing c
    LEFT JOIN flows f ON f.month_end = c.month_end AND f.asset_class = c.asset_class
),
implied AS (
    SELECT month_end, asset_class,
           100 * (closing_aum - opening_aum - net_flow) / NULLIF(opening_aum, 0) AS implied_return_pct
    FROM bridge
    WHERE opening_aum IS NOT NULL
)
SELECT month_end,
       ROUND(MAX(implied_return_pct) FILTER (WHERE asset_class = 'Equity'), 2) AS equity_pct,
       ROUND(MAX(implied_return_pct) FILTER (WHERE asset_class = 'Debt'),   2) AS debt_pct,
       ROUND(MAX(implied_return_pct) FILTER (WHERE asset_class = 'Gold'),   2) AS gold_pct,
       ROUND(MAX(implied_return_pct) FILTER (WHERE asset_class = 'Liquid'), 2) AS liquid_pct
FROM implied
GROUP BY month_end
ORDER BY month_end;
