-- DQ2 | Inconsistent text values
-- Question: are there city spellings that do not match the official branch list?
-- Technique: compare each raw value with a trusted reference list (advisors.branch)
SELECT c.city        AS raw_value,
       b.branch      AS standard_value,
       COUNT(*)      AS clients
FROM wm.clients c
LEFT JOIN (SELECT DISTINCT branch FROM wm.advisors) b
       ON LOWER(TRIM(c.city)) = LOWER(b.branch)
WHERE c.city IS DISTINCT FROM b.branch
   OR c.city IS NULL
GROUP BY c.city, b.branch
ORDER BY clients DESC, raw_value;
