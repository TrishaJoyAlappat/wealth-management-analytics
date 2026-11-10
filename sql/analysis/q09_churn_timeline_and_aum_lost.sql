-- Q9 | Churn over time and the AUM walking out of the door
-- Business question: when did clients leave, and how much money left with them?
-- A churned client redeems every holding on the churn date, so the sum of those
-- redemptions is the AUM lost.
WITH lost AS (
    SELECT c.client_id, c.churn_date, SUM(t.amount) AS aum_lost
    FROM wm.clients c
    JOIN wm.transactions t
      ON t.client_id = c.client_id
     AND t.txn_date  = c.churn_date
     AND t.txn_type  = 'Redemption'
    WHERE c.status = 'Churned'
    GROUP BY c.client_id, c.churn_date
)
SELECT DATE_TRUNC('month', churn_date)::date  AS churn_month,
       COUNT(*)                               AS churned_clients,
       ROUND(SUM(aum_lost) / 1e7, 1)          AS aum_lost_cr,
       ROUND(AVG(aum_lost) / 1e5, 1)          AS avg_aum_lost_lakh
FROM lost
GROUP BY 1
ORDER BY 1;
