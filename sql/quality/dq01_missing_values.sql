-- DQ1 | Missing values
-- Question: which columns have gaps that could break reports?
SELECT COUNT(*)                                                    AS total_clients,
       COUNT(*) FILTER (WHERE city IS NULL)                        AS missing_city,
       COUNT(*) FILTER (WHERE gender IS NULL)                      AS missing_gender,
       COUNT(*) FILTER (WHERE date_of_birth IS NULL)               AS missing_dob,
       COUNT(*) FILTER (WHERE status = 'Churned'
                          AND churn_date IS NULL)                  AS churned_without_date
FROM wm.clients;
