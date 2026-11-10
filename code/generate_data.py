"""
generate_data.py  -  Synthetic wealth-management dataset generator
--------------------------------------------------------------------
Creates 5 CSV files in ./data :
    advisors.csv       40 relationship managers across 8 branches
    products.csv       14 investment products in 4 asset classes
    clients.csv        5,000 clients (with a few deliberate data defects)
    transactions.csv   SIP / Lumpsum / Redemption cash flows
    monthly_aum.csv    month-end AUM per client per asset class

Run:   python generate_data.py
Needs: pip install pandas numpy faker

All data is SYNTHETIC. Never describe it as real company data.
"""
import os

import numpy as np
import pandas as pd
from faker import Faker

# ----------------------------------------------------------------------
# 1. SETTINGS  (change these to experiment; keep SEED fixed for repeatable data)
# ----------------------------------------------------------------------
SEED = 42
N_CLIENTS = 5000
N_DUPLICATE_CLIENTS = 12      # deliberate "same person, two IDs" defects
N_MISSING_CITY = 30           # deliberate NULL city values
N_MESSY_CITY = 60             # deliberate lower/UPPER/extra-space city values
N_MONTHS = 24                 # Jan-2024 .. Dec-2025
OUT_DIR = "data"

rng = np.random.default_rng(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

ASSET_CLASSES = ["Equity", "Debt", "Gold", "Liquid"]
BRANCHES = ["Mumbai", "Delhi NCR", "Bengaluru", "Pune",
            "Hyderabad", "Chennai", "Kolkata", "Ahmedabad"]

# month-end dates: index 0 = opening balance (31-Dec-2023), 1..24 = Jan..Dec 2025
MONTH_ENDS = (pd.date_range("2023-12-01", periods=N_MONTHS + 1, freq="MS")
              + pd.offsets.MonthEnd(0))

# ----------------------------------------------------------------------
# 2. ADVISORS  (5 per branch)
# ----------------------------------------------------------------------
advisors = pd.DataFrame({
    "advisor_id": [f"ADV{i:03d}" for i in range(1, 41)],
    "advisor_name": [fake.name() for _ in range(40)],
    "branch": np.repeat(BRANCHES, 5),
    "join_date": (pd.Timestamp("2012-01-01")
                  + pd.to_timedelta(rng.integers(0, 3700, 40), unit="D")).date,
})
# Two advisors lose clients much faster than the rest (a hidden pattern to find)
ADVISOR_CHURN_MULT = {a: 1.0 for a in advisors["advisor_id"]}
ADVISOR_CHURN_MULT["ADV007"] = 2.5
ADVISOR_CHURN_MULT["ADV023"] = 2.5

# ----------------------------------------------------------------------
# 3. PRODUCTS
# ----------------------------------------------------------------------
product_rows = [
    ("Large Cap Equity Fund", "Equity", "Mutual Fund", "High", 1.10),
    ("Flexi Cap Equity Fund", "Equity", "Mutual Fund", "High", 1.25),
    ("Mid Cap Equity Fund", "Equity", "Mutual Fund", "Very High", 1.40),
    ("Small Cap Equity Fund", "Equity", "Mutual Fund", "Very High", 1.55),
    ("Large Cap Index Fund", "Equity", "Index Fund", "High", 0.20),
    ("Equity PMS - Growth", "Equity", "PMS", "Very High", 2.20),
    ("Corporate Bond Fund", "Debt", "Mutual Fund", "Moderate", 0.65),
    ("Government Securities Fund", "Debt", "Mutual Fund", "Moderate", 0.55),
    ("Short Duration Debt Fund", "Debt", "Mutual Fund", "Low", 0.45),
    ("Fixed Maturity Plan", "Debt", "Mutual Fund", "Low", 0.30),
    ("Gold ETF", "Gold", "ETF", "Moderate", 0.50),
    ("Sovereign Gold Bond", "Gold", "Bond", "Moderate", 0.00),
    ("Liquid Fund", "Liquid", "Mutual Fund", "Low", 0.20),
    ("Overnight Fund", "Liquid", "Mutual Fund", "Low", 0.15),
]
products = pd.DataFrame(product_rows, columns=[
    "product_name", "asset_class", "category", "risk_level", "expense_ratio_pct"])
products.insert(0, "product_id", [f"P{i:02d}" for i in range(1, len(products) + 1)])
PRODUCTS_BY_CLASS = {c: products.loc[products.asset_class == c, "product_id"].to_numpy()
                     for c in ASSET_CLASSES}

# ----------------------------------------------------------------------
# 4. CLIENT PROFILES
# ----------------------------------------------------------------------
n = N_CLIENTS
n_base = n - N_DUPLICATE_CLIENTS

segment = rng.choice(["Mass Affluent", "HNI", "UHNI"], size=n, p=[0.70, 0.24, 0.06])
risk = rng.choice(["Conservative", "Moderate", "Aggressive"], size=n, p=[0.30, 0.45, 0.25])
channel = rng.choice(["Referral", "Branch Walk-in", "Digital", "Corporate Tie-up"],
                     size=n, p=[0.35, 0.25, 0.25, 0.15])
city = rng.choice(BRANCHES, size=n, p=[0.25, 0.16, 0.14, 0.10, 0.10, 0.09, 0.09, 0.07])

# advisor = a random advisor from the client's home branch
advisor_ids = advisors["advisor_id"].to_numpy()
advisor_branch = advisors["branch"].to_numpy()
advisor_for_client = np.empty(n, dtype=object)
for b in BRANCHES:
    rows = np.where(city == b)[0]
    advisor_for_client[rows] = rng.choice(advisor_ids[advisor_branch == b], size=len(rows))

gender = rng.choice(["Male", "Female"], size=n, p=[0.58, 0.42])
full_name = np.array([fake.name_male() if g == "Male" else fake.name_female()
                      for g in gender], dtype=object)
age = rng.integers(25, 76, size=n)
dob = (pd.Timestamp("2025-12-31")
       - pd.to_timedelta(age * 365 + rng.integers(0, 365, n), unit="D")).date

# Deliberate defect: the last N_DUPLICATE_CLIENTS clients are clones of earlier
# people (same name / gender / dob / city) with a different client_id.
src = rng.choice(n_base, size=N_DUPLICATE_CLIENTS, replace=False)
dst = np.arange(n_base, n)
full_name[dst], gender[dst], city[dst] = full_name[src], gender[src], city[src]
dob = np.array(dob, dtype=object)
dob[dst] = dob[src]

# Onboarding: 85% joined before 2024, 15% joined during Jan-2024 .. Dec-2025
existing = rng.random(n) < 0.85
d_old = pd.Timestamp("2018-01-01") + pd.to_timedelta(rng.integers(0, 2191, n), unit="D")
d_new = pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 730, n), unit="D")
onboard = pd.DatetimeIndex(np.where(existing, d_old, d_new))
onboard_idx = np.where(existing, 0,
                       (onboard.year - 2024) * 12 + onboard.month).astype(int)

# Starting wealth by segment (rupees)
MEDIAN_WEALTH = {"Mass Affluent": 2.0e6, "HNI": 1.5e7, "UHNI": 1.0e8}
median = np.array([MEDIAN_WEALTH[s] for s in segment])
start_wealth = np.clip(rng.lognormal(np.log(median), 0.55), 3e5, 5e8)

# Target asset allocation depends on risk profile
BASE_ALLOC = {"Conservative": [0.20, 0.55, 0.10, 0.15],
              "Moderate": [0.45, 0.35, 0.10, 0.10],
              "Aggressive": [0.70, 0.15, 0.08, 0.07]}
alloc = np.zeros((n, 4))
for r, base in BASE_ALLOC.items():
    rows = np.where(risk == r)[0]
    alloc[rows] = rng.dirichlet(np.array(base) * 30, size=len(rows))
alloc_cum = alloc.cumsum(axis=1)

# SIP behaviour (40% of clients run a monthly SIP)
has_sip = rng.random(n) < 0.40
SIP_RANGE = {"Mass Affluent": (5e3, 5e4), "HNI": (5e4, 5e5), "UHNI": (5e5, 2.5e6)}
sip_amount = np.array([rng.uniform(*SIP_RANGE[s]) for s in segment]).round(-3)
sip_class = rng.choice([0, 1, 2], size=n, p=[0.70, 0.20, 0.10])
sip_day = rng.integers(1, 29, size=n)
sip_product = np.array([rng.choice(PRODUCTS_BY_CLASS[ASSET_CLASSES[c]]) for c in sip_class])

# Trading frequency: most clients trade in ~40% of months, 12% are "buy and hold"
event_prob = np.where(rng.random(n) < 0.12, 0.03, 0.40)

# Dormancy: 10% of clients stop all activity after some month between 14 and 18
dormant_after = np.where(rng.random(n) < 0.10, rng.integers(14, 19, n), 999)

# Monthly churn probability (hidden drivers: segment, channel, advisor, market stress)
BASE_HAZARD = 0.004
seg_mult = np.array([{"Mass Affluent": 1.3, "HNI": 0.9, "UHNI": 0.4}[s] for s in segment])
chan_mult = np.array([{"Digital": 1.8, "Branch Walk-in": 0.9, "Referral": 0.7,
                       "Corporate Tie-up": 0.8}[c] for c in channel])
adv_mult = np.array([ADVISOR_CHURN_MULT[a] for a in advisor_for_client])
hazard = BASE_HAZARD * seg_mult * chan_mult * adv_mult
is_aggressive = risk == "Aggressive"

# ----------------------------------------------------------------------
# 5. MARKET RETURNS PER MONTH  (shape: 25 x 4; row 0 unused)
# ----------------------------------------------------------------------
ret = np.zeros((N_MONTHS + 1, 4))
ret[:, 0] = np.clip(rng.normal(0.009, 0.018, N_MONTHS + 1), -0.045, 0.055)  # Equity
ret[:, 1] = rng.normal(0.0058, 0.004, N_MONTHS + 1)                         # Debt
ret[:, 2] = np.clip(rng.normal(0.009, 0.014, N_MONTHS + 1), -0.04, 0.05)    # Gold
ret[:, 3] = rng.normal(0.0052, 0.0003, N_MONTHS + 1)                        # Liquid
ret[15, 0], ret[16, 0] = -0.070, -0.050               # equity sell-off Mar/Apr 2025
ret[17:20, 0] = [0.040, 0.035, 0.030]                 # recovery May-Jul 2025
ret = ret.round(4)

# ----------------------------------------------------------------------
# 6. MONTH-BY-MONTH SIMULATION
# ----------------------------------------------------------------------
aum = np.zeros((N_MONTHS + 1, n, 4))
aum[0] = np.where(existing[:, None], start_wealth[:, None] * alloc, 0.0).round(2)

churn_date = np.full(n, np.datetime64("NaT", "ns"), dtype="datetime64[ns]")
churned = np.zeros(n, dtype=bool)
txn_parts = []   # list of DataFrames, concatenated at the end


def pick_class(rows):
    """Pick an asset class for each client, weighted by that client's allocation."""
    u = rng.random(len(rows))
    return np.minimum((u[:, None] > alloc_cum[rows]).sum(axis=1), 3)


def add_txns(rows, classes, kind, amounts, days=None, dates=None, products_fixed=None):
    """Append one block of transactions."""
    if len(rows) == 0:
        return
    if dates is None:
        dates = month_start + pd.to_timedelta(days - 1, unit="D")
    if products_fixed is None:
        prod = np.empty(len(rows), dtype=object)
        for c, name in enumerate(ASSET_CLASSES):
            m = classes == c
            prod[m] = rng.choice(PRODUCTS_BY_CLASS[name], size=m.sum())
    else:
        prod = products_fixed
    txn_parts.append(pd.DataFrame({
        "client_id": client_ids[rows], "product_id": prod, "txn_date": pd.DatetimeIndex(dates),
        "txn_type": kind, "amount": np.round(amounts, 2)}))


client_ids = np.array([f"C{i:05d}" for i in range(1, n + 1)])

for t in range(1, N_MONTHS + 1):
    month_start = MONTH_ENDS[t].replace(day=1)
    value = aum[t - 1] * (1 + ret[t])              # balances after market movement
    inflow = np.zeros((n, 4))
    outflow = np.zeros((n, 4))

    live = (onboard_idx < t) & ~churned            # clients on the books at month start
    can_trade = live & (dormant_after >= t)

    # --- churn: full redemption of every holding --------------------
    p = hazard.copy()
    if 16 <= t <= 19:
        p = np.where(is_aggressive, p * 3, p)      # aggressive clients flee after sell-off
    churn_now = live & (rng.random(n) < p)
    rows = np.where(churn_now)[0]
    if len(rows):
        day = rng.integers(1, 29, size=len(rows))
        churn_date[rows] = (month_start + pd.to_timedelta(day - 1, unit="D")).to_numpy()
        for c in range(4):
            amt = value[rows, c].round(2)
            keep = amt > 0
            add_txns(rows[keep], np.full(keep.sum(), c), "Redemption", amt[keep],
                     days=day[keep])
        outflow[rows] = value[rows]
        churned[rows] = True
    can_trade &= ~churn_now

    # --- monthly SIPs ------------------------------------------------
    sip_now = can_trade & has_sip & (rng.random(n) < 0.95)
    rows = np.where(sip_now)[0]
    inflow[rows, sip_class[rows]] += sip_amount[rows]
    add_txns(rows, sip_class[rows], "SIP", sip_amount[rows], days=sip_day[rows],
             products_fixed=sip_product[rows])

    # --- lumpsum investments -----------------------------------------
    trades = can_trade & (rng.random(n) < event_prob)
    is_buy = rng.random(n) < 0.50
    lump_now = trades & is_buy
    rows = np.where(lump_now)[0]
    cls = pick_class(rows)
    amt = (rng.uniform(0.01, 0.06, len(rows)) * value[rows].sum(axis=1)).round(2)
    inflow[rows, cls] += amt
    add_txns(rows, cls, "Lumpsum", amt, days=rng.integers(1, 29, len(rows)))

    # --- partial redemptions -----------------------------------------
    red_now = trades & ~is_buy
    rows = np.where(red_now)[0]
    cls = pick_class(rows)
    amt = np.minimum(rng.uniform(0.03, 0.12, len(rows)) * value[rows, cls],
                     value[rows, cls]).round(2)
    keep = amt > 0
    outflow[rows[keep], cls[keep]] += amt[keep]
    add_txns(rows[keep], cls[keep], "Redemption", amt[keep],
             days=rng.integers(1, 29, keep.sum()))

    # --- new clients make their first investment on the onboarding date
    rows = np.where(onboard_idx == t)[0]
    for c in range(4):
        amt = (start_wealth[rows] * alloc[rows, c]).round(2)
        inflow[rows, c] += amt
        add_txns(rows, np.full(len(rows), c), "Lumpsum", amt,
                 dates=onboard[rows])

    aum[t] = np.maximum(value + inflow - outflow, 0).round(2)

# ----------------------------------------------------------------------
# 7. BUILD TABLES
# ----------------------------------------------------------------------
# monthly_aum: one row per client x asset class x month-end, from the first
# month the client exists
first_idx = np.where(existing, 0, onboard_idx)
snap = []
for t in range(N_MONTHS + 1):
    rows = np.where(first_idx <= t)[0]
    for c, name in enumerate(ASSET_CLASSES):
        snap.append(pd.DataFrame({"client_id": client_ids[rows],
                                  "snapshot_date": MONTH_ENDS[t].date(),
                                  "asset_class": name,
                                  "aum_value": aum[t][rows, c]}))
monthly_aum = pd.concat(snap, ignore_index=True)
monthly_aum = monthly_aum.sort_values(["snapshot_date", "client_id", "asset_class"])

transactions = pd.concat(txn_parts, ignore_index=True)
transactions = transactions[transactions.amount > 0]
transactions = transactions.sort_values(["txn_date", "client_id"]).reset_index(drop=True)
transactions.insert(0, "txn_id", np.arange(1, len(transactions) + 1))
transactions["txn_date"] = transactions["txn_date"].dt.date

clients = pd.DataFrame({
    "client_id": client_ids, "full_name": full_name, "gender": gender,
    "date_of_birth": dob, "city": city, "segment": segment, "risk_profile": risk,
    "acquisition_channel": channel, "advisor_id": advisor_for_client,
    "onboarding_date": onboard.date,
    "status": np.where(churned, "Churned", "Active"),
    "churn_date": pd.Series(churn_date).dt.date,
})

# Deliberate defects in the city column (the clean-up happens later in SQL)
bad = rng.choice(n, size=N_MISSING_CITY + N_MESSY_CITY, replace=False)
clients["city"] = clients["city"].astype(object)
clients.loc[bad[:N_MISSING_CITY], "city"] = None
messy = bad[N_MISSING_CITY:]
styles = rng.integers(0, 3, len(messy))
for i, s in zip(messy, styles):
    v = clients.at[i, "city"]
    clients.at[i, "city"] = [v.lower(), v.upper(), "  " + v + " "][s]

# ----------------------------------------------------------------------
# 8. SAVE
# ----------------------------------------------------------------------
os.makedirs(OUT_DIR, exist_ok=True)
advisors.to_csv(f"{OUT_DIR}/advisors.csv", index=False)
products.to_csv(f"{OUT_DIR}/products.csv", index=False)
clients.to_csv(f"{OUT_DIR}/clients.csv", index=False)
transactions.to_csv(f"{OUT_DIR}/transactions.csv", index=False)
monthly_aum.to_csv(f"{OUT_DIR}/monthly_aum.csv", index=False)

print("Files written to ./" + OUT_DIR)
for name, df in [("advisors", advisors), ("products", products), ("clients", clients),
                 ("transactions", transactions), ("monthly_aum", monthly_aum)]:
    print(f"  {name:<13}{len(df):>9,} rows")
last = monthly_aum[monthly_aum.snapshot_date == MONTH_ENDS[-1].date()]
print(f"Total AUM at {MONTH_ENDS[-1].date()}: Rs {last.aum_value.sum() / 1e7:,.0f} crore")
print(f"Churned clients: {churned.sum():,} ({churned.mean():.1%})")
