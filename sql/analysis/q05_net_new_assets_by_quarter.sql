-- Q5 | Cash flows by quarter and type
-- Business question: how much is coming in via SIPs vs lump sums, and how much
-- is leaving through redemptions?
-- Technique: conditional aggregation with FILTER
SELECT DATE_TRUNC('quarter', txn_date)::date                                   AS quarter_start,
       ROUND(SUM(amount) FILTER (WHERE txn_type = 'SIP')        / 1e7, 1)      AS sip_cr,
       ROUND(SUM(amount) FILTER (WHERE txn_type = 'Lumpsum')    / 1e7, 1)      AS lumpsum_cr,
       ROUND(SUM(amount) FILTER (WHERE txn_type = 'Redemption') / 1e7, 1)      AS redemptions_cr,
       ROUND(SUM(CASE WHEN txn_type = 'Redemption' THEN -amount ELSE amount END) / 1e7, 1)
                                                                               AS net_new_assets_cr
FROM wm.transactions
GROUP BY 1
ORDER BY 1;
