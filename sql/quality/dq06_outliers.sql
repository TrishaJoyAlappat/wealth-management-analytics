-- DQ6 | Outlier scan on client-level AUM (latest month)
-- Look at the spread: huge gaps between p99 and max deserve a second look.
WITH client_aum AS (
    SELECT client_id, SUM(aum_value) AS aum
    FROM wm.monthly_aum
    WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM wm.monthly_aum)
    GROUP BY client_id
    HAVING SUM(aum_value) > 0
)
SELECT COUNT(*)                                                       AS clients,
       ROUND(MIN(aum) / 1e5, 1)                                       AS min_lakh,
       ROUND((PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY aum))::numeric / 1e5, 1) AS median_lakh,
       ROUND((PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY aum))::numeric / 1e5, 1) AS p99_lakh,
       ROUND(MAX(aum) / 1e5, 1)                                       AS max_lakh
FROM client_aum;
