-- =====================================================================
-- 05_reporting_views.sql  -  the clean "reporting layer" Power BI connects to
-- Power BI never touches the raw tables: it reads these views.
-- =====================================================================
SET search_path TO wm;

-- ---------- dimension: advisors -------------------------------------
CREATE OR REPLACE VIEW vw_dim_advisor AS
SELECT advisor_id, advisor_name, branch, join_date
FROM advisors;

-- ---------- dimension: products -------------------------------------
CREATE OR REPLACE VIEW vw_dim_product AS
SELECT product_id, product_name, asset_class, category, risk_level, expense_ratio_pct
FROM products;

-- ---------- dimension: asset class (small lookup, so slicers filter BOTH facts) ----
CREATE OR REPLACE VIEW vw_dim_asset_class AS
SELECT asset_class, sort_order
FROM (VALUES ('Equity', 1), ('Debt', 2), ('Gold', 3), ('Liquid', 4)) AS v (asset_class, sort_order);

-- ---------- dimension: clients (cleaned + enriched) -----------------
CREATE OR REPLACE VIEW vw_dim_client AS
WITH params AS (
    SELECT MAX(snapshot_date) AS as_of FROM monthly_aum
),
ref_city AS (                       -- trusted spelling of each city
    SELECT DISTINCT branch FROM advisors
),
last_txn AS (
    SELECT client_id, MAX(txn_date) AS last_txn_date
    FROM transactions
    GROUP BY client_id
),
latest_aum AS (
    SELECT client_id, SUM(aum_value) AS aum_latest
    FROM monthly_aum
    WHERE snapshot_date = (SELECT as_of FROM params)
    GROUP BY client_id
),
churn_loss AS (                     -- money redeemed on the day the client left
    SELECT c.client_id, SUM(t.amount) AS aum_lost
    FROM clients c
    JOIN transactions t
      ON t.client_id = c.client_id
     AND t.txn_date  = c.churn_date
     AND t.txn_type  = 'Redemption'
    WHERE c.status = 'Churned'
    GROUP BY c.client_id
),
same_person AS (
    SELECT client_id,
           COUNT(*) OVER (PARTITION BY LOWER(TRIM(full_name)), date_of_birth) AS records
    FROM clients
),
base AS (
    SELECT c.client_id, c.full_name, c.gender, c.date_of_birth,
           DATE_PART('year', AGE((SELECT as_of FROM params), c.date_of_birth))::int AS age,
           COALESCE(rc.branch, 'Unknown')          AS city,
           c.segment, c.risk_profile, c.acquisition_channel, c.advisor_id,
           c.onboarding_date, c.status, c.churn_date,
           COALESCE(la.aum_latest, 0)              AS aum_latest,
           cl.aum_lost,
           lt.last_txn_date,
           (c.status = 'Active'
            AND COALESCE(lt.last_txn_date, DATE '1900-01-01')
                < (SELECT as_of FROM params) - 180)  AS is_dormant,
           (sp.records > 1)                          AS is_possible_duplicate
    FROM clients c
    LEFT JOIN ref_city    rc ON LOWER(TRIM(c.city)) = LOWER(rc.branch)
    LEFT JOIN last_txn    lt ON lt.client_id = c.client_id
    LEFT JOIN latest_aum  la ON la.client_id = c.client_id
    LEFT JOIN churn_loss  cl ON cl.client_id = c.client_id
    LEFT JOIN same_person sp ON sp.client_id = c.client_id
)
SELECT base.*,
       CASE WHEN age < 35 THEN '25-34'
            WHEN age < 45 THEN '35-44'
            WHEN age < 55 THEN '45-54'
            WHEN age < 65 THEN '55-64'
            ELSE '65+' END AS age_band
FROM base;

-- ---------- fact: transactions --------------------------------------
CREATE OR REPLACE VIEW vw_fact_transactions AS
SELECT t.txn_id, t.client_id, t.product_id, p.asset_class,
       t.txn_date, t.txn_type, t.amount,
       CASE WHEN t.txn_type = 'Redemption' THEN -t.amount ELSE t.amount END AS signed_amount
FROM transactions t
JOIN products p USING (product_id);

-- ---------- fact: month-end AUM -------------------------------------
CREATE OR REPLACE VIEW vw_fact_monthly_aum AS
SELECT client_id, snapshot_date, asset_class, aum_value
FROM monthly_aum;

-- ---------- sanity check --------------------------------------------
SELECT 'vw_dim_client' AS view_name, COUNT(*) AS row_count FROM vw_dim_client
UNION ALL SELECT 'vw_fact_transactions', COUNT(*) FROM vw_fact_transactions
UNION ALL SELECT 'vw_fact_monthly_aum',  COUNT(*) FROM vw_fact_monthly_aum
UNION ALL SELECT 'vw_dim_advisor',       COUNT(*) FROM vw_dim_advisor
UNION ALL SELECT 'vw_dim_product',       COUNT(*) FROM vw_dim_product
UNION ALL SELECT 'vw_dim_asset_class',   COUNT(*) FROM vw_dim_asset_class;
