-- Q10 | Dormant clients: active clients with no transaction in the last 180 days
-- Business question: how much AUM belongs to clients who have gone quiet?
-- (a retention opportunity: call them before they leave)
WITH params AS (SELECT MAX(snapshot_date) AS as_of FROM wm.monthly_aum),
last_txn AS (
    SELECT client_id, MAX(txn_date) AS last_txn_date
    FROM wm.transactions
    GROUP BY client_id
),
latest_aum AS (
    SELECT client_id, SUM(aum_value) AS aum
    FROM wm.monthly_aum
    WHERE snapshot_date = (SELECT as_of FROM params)
    GROUP BY client_id
)
SELECT c.segment,
       COUNT(*)                                             AS dormant_clients,
       ROUND(SUM(a.aum) / 1e7, 1)                           AS dormant_aum_cr,
       ROUND(100.0 * SUM(a.aum) / (SELECT SUM(aum) FROM latest_aum), 1) AS pct_of_firm_aum
FROM wm.clients c
JOIN latest_aum a USING (client_id)
LEFT JOIN last_txn lt USING (client_id)
CROSS JOIN params p
WHERE c.status = 'Active'
  AND COALESCE(lt.last_txn_date, DATE '1900-01-01') < p.as_of - 180
GROUP BY c.segment
ORDER BY dormant_aum_cr DESC;
