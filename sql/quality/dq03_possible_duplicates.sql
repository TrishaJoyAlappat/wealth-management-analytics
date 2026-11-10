-- DQ3 | Possible duplicate clients
-- Question: is the same person stored under two client IDs?
SELECT LOWER(TRIM(full_name))                        AS client_name,
       date_of_birth,
       COUNT(*)                                      AS records,
       STRING_AGG(client_id, ', ' ORDER BY client_id) AS client_ids
FROM wm.clients
GROUP BY LOWER(TRIM(full_name)), date_of_birth
HAVING COUNT(*) > 1
ORDER BY client_name;
