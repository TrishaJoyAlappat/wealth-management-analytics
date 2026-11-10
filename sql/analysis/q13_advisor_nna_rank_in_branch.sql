-- Q13 | Net new assets (last 12 months) ranked within each branch
-- Business question: who is winning new money, compared with peers in the same branch?
-- Technique: RANK() OVER (PARTITION BY branch ...)
WITH nna AS (
    SELECT a.advisor_id, a.advisor_name, a.branch,
           SUM(CASE WHEN t.txn_type = 'Redemption' THEN -t.amount ELSE t.amount END) AS nna_12m
    FROM wm.transactions t
    JOIN wm.clients  c USING (client_id)
    JOIN wm.advisors a USING (advisor_id)
    WHERE t.txn_date > (SELECT MAX(snapshot_date) FROM wm.monthly_aum) - INTERVAL '12 months'
    GROUP BY a.advisor_id, a.advisor_name, a.branch
)
SELECT branch, advisor_name,
       ROUND(nna_12m / 1e7, 2)                              AS nna_cr,
       RANK() OVER (PARTITION BY branch ORDER BY nna_12m DESC) AS rank_in_branch
FROM nna
ORDER BY branch, rank_in_branch;
