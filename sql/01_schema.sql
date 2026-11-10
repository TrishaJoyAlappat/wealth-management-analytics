-- =====================================================================
-- 01_schema.sql  -  creates the wm schema and the 5 base tables
-- Run inside the wm_analytics database (see the guide, Phase 2)
-- =====================================================================
DROP SCHEMA IF EXISTS wm CASCADE;
CREATE SCHEMA wm;
SET search_path TO wm;

CREATE TABLE advisors (
    advisor_id    VARCHAR(10)  PRIMARY KEY,
    advisor_name  VARCHAR(100) NOT NULL,
    branch        VARCHAR(30)  NOT NULL,
    join_date     DATE         NOT NULL
);

CREATE TABLE products (
    product_id         VARCHAR(10)  PRIMARY KEY,
    product_name       VARCHAR(60)  NOT NULL,
    asset_class        VARCHAR(10)  NOT NULL
                       CHECK (asset_class IN ('Equity', 'Debt', 'Gold', 'Liquid')),
    category           VARCHAR(20)  NOT NULL,
    risk_level         VARCHAR(12)  NOT NULL,
    expense_ratio_pct  NUMERIC(4,2) NOT NULL
);

-- city is intentionally NOT declared NOT NULL: the raw data has gaps (see Phase 3)
CREATE TABLE clients (
    client_id            VARCHAR(10)  PRIMARY KEY,
    full_name            VARCHAR(100) NOT NULL,
    gender               VARCHAR(10),
    date_of_birth        DATE,
    city                 VARCHAR(30),
    segment              VARCHAR(20)  NOT NULL
                         CHECK (segment IN ('Mass Affluent', 'HNI', 'UHNI')),
    risk_profile         VARCHAR(15)  NOT NULL
                         CHECK (risk_profile IN ('Conservative', 'Moderate', 'Aggressive')),
    acquisition_channel  VARCHAR(20)  NOT NULL,
    advisor_id           VARCHAR(10)  NOT NULL REFERENCES advisors (advisor_id),
    onboarding_date      DATE         NOT NULL,
    status               VARCHAR(10)  NOT NULL CHECK (status IN ('Active', 'Churned')),
    churn_date           DATE
);

CREATE TABLE transactions (
    txn_id      BIGINT        PRIMARY KEY,
    client_id   VARCHAR(10)   NOT NULL REFERENCES clients (client_id),
    product_id  VARCHAR(10)   NOT NULL REFERENCES products (product_id),
    txn_date    DATE          NOT NULL,
    txn_type    VARCHAR(12)   NOT NULL
                CHECK (txn_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount      NUMERIC(16,2) NOT NULL CHECK (amount > 0)
);

CREATE TABLE monthly_aum (
    client_id      VARCHAR(10)   NOT NULL REFERENCES clients (client_id),
    snapshot_date  DATE          NOT NULL,
    asset_class    VARCHAR(10)   NOT NULL,
    aum_value      NUMERIC(18,2) NOT NULL CHECK (aum_value >= 0),
    PRIMARY KEY (client_id, snapshot_date, asset_class)
);
