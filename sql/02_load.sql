-- =====================================================================
-- 02_load.sql  -  loads the CSV files (run from the PROJECT ROOT folder)
-- The order matters: parents first, children after (foreign keys)
-- =====================================================================
SET search_path TO wm;
\encoding UTF8

\copy advisors    FROM 'data/advisors.csv'     WITH (FORMAT csv, HEADER true)
\copy products    FROM 'data/products.csv'     WITH (FORMAT csv, HEADER true)
\copy clients     FROM 'data/clients.csv'      WITH (FORMAT csv, HEADER true)
\copy transactions FROM 'data/transactions.csv' WITH (FORMAT csv, HEADER true)
\copy monthly_aum FROM 'data/monthly_aum.csv'  WITH (FORMAT csv, HEADER true)

-- Indexes AFTER loading (faster than loading into an indexed table)
CREATE INDEX idx_txn_client      ON transactions (client_id);
CREATE INDEX idx_txn_date        ON transactions (txn_date);
CREATE INDEX idx_aum_date        ON monthly_aum  (snapshot_date);
CREATE INDEX idx_clients_advisor ON clients      (advisor_id);

ANALYZE;

-- Quick check: row counts
SELECT 'advisors' AS tbl, COUNT(*) FROM advisors
UNION ALL SELECT 'products',     COUNT(*) FROM products
UNION ALL SELECT 'clients',      COUNT(*) FROM clients
UNION ALL SELECT 'transactions', COUNT(*) FROM transactions
UNION ALL SELECT 'monthly_aum',  COUNT(*) FROM monthly_aum;
