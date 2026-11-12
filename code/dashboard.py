"""
Northstar Wealth - Wealth Management Analytics dashboard (Streamlit)

Reads the reporting views in PostgreSQL (schema wm) and shows the same four
pages as the Power BI report. Measure logic mirrors powerbi/dax_measures.txt,
so every number reconciles to sql/06_control_totals.sql.

Run (from the project root, PowerShell):
    $env:PGPASSWORD = "<your password>"
    streamlit run code/dashboard.py

Optional env vars: PGHOST (localhost) PGPORT (5432) PGUSER (postgres) PGDATABASE (wm_analytics)
"""
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine

NAVY, TEAL, AMBER, GREY, RED = "#0B2545", "#1B998B", "#F4A259", "#8D99AE", "#D1495B"
ASSET_COLORS = {"Equity": NAVY, "Debt": TEAL, "Gold": AMBER, "Liquid": GREY}
CR = 10_000_000
LAKH = 100_000

st.set_page_config(page_title="Northstar Wealth Analytics", layout="wide")
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 1rem;}
    div[data-testid="stMetric"] {background:#F3F5F8; border-radius:8px; padding:10px 14px;}
    div[data-testid="stMetricValue"] {color:#0B2545; font-size:1.7rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- data
@st.cache_resource
def get_engine():
    url = "postgresql+psycopg2://{u}:{p}@{h}:{port}/{d}".format(
        u=os.getenv("PGUSER", "postgres"),
        p=os.getenv("PGPASSWORD", ""),
        h=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        d=os.getenv("PGDATABASE", "wm_analytics"),
    )
    return create_engine(url)


@st.cache_data(show_spinner="Loading data from PostgreSQL ...")
def load():
    e = get_engine()
    q = lambda t: pd.read_sql(f"SELECT * FROM wm.{t}", e)
    adv = q("vw_dim_advisor")
    cli = q("vw_dim_client")
    aum = q("vw_fact_monthly_aum")
    txn = q("vw_fact_transactions")
    for c in ["onboarding_date", "churn_date", "last_txn_date"]:
        cli[c] = pd.to_datetime(cli[c])
    aum["snapshot_date"] = pd.to_datetime(aum["snapshot_date"])
    txn["txn_date"] = pd.to_datetime(txn["txn_date"])
    for c in ["aum_value"]:
        aum[c] = aum[c].astype(float)
    for c in ["amount", "signed_amount"]:
        txn[c] = txn[c].astype(float)
    for c in ["aum_latest", "aum_lost"]:
        cli[c] = cli[c].astype(float)
    cli = cli.merge(adv[["advisor_id", "advisor_name", "branch"]], on="advisor_id", how="left")
    # attach client attributes to the fact tables once
    attrs = cli[["client_id", "segment", "branch", "advisor_id", "advisor_name", "risk_profile"]]
    aum = aum.merge(attrs, on="client_id", how="left")
    txn = txn.merge(attrs, on="client_id", how="left")
    return adv, cli, aum, txn


try:
    adv, cli, aum_all, txn_all = load()
except Exception as ex:  # friendly message if the database is unreachable
    st.error(
        "Could not read the database. Check that PostgreSQL is running and that "
        "PGPASSWORD (and PGUSER / PGDATABASE if different) are set.\n\n" + str(ex)
    )
    st.stop()

# --------------------------------------------------------------------------- sidebar filters
st.sidebar.title("Filters")
months_all = sorted(d for d in aum_all["snapshot_date"].unique() if pd.Timestamp(d) >= pd.Timestamp("2024-01-01"))
months_all = [pd.Timestamp(d) for d in months_all]
years = sorted({m.year for m in months_all})
sel_years = st.sidebar.multiselect("Year", years, default=years)
quarters = sorted({f"{m.year}-Q{(m.month - 1) // 3 + 1}" for m in months_all if m.year in sel_years})
sel_q = st.sidebar.multiselect("Year Quarter", quarters, default=quarters)
seg_opts = ["Mass Affluent", "HNI", "UHNI"]
sel_seg = st.sidebar.multiselect("Segment", [s for s in seg_opts if s in set(cli["segment"])] or sorted(cli["segment"].unique()),
                                 default=None, placeholder="All")
sel_branch = st.sidebar.multiselect("Branch", sorted(adv["branch"].unique()), default=None, placeholder="All")

period = [m for m in months_all if m.year in sel_years and f"{m.year}-Q{(m.month - 1) // 3 + 1}" in sel_q]
if not period:
    st.warning("No months selected. Pick at least one year and quarter.")
    st.stop()
pset = set(period)
last_snap, first_month = max(period), min(period)
prior_end = (first_month.replace(day=1) - pd.Timedelta(days=1))  # month-end before the period

cli_f = cli.copy()
if sel_seg:
    cli_f = cli_f[cli_f["segment"].isin(sel_seg)]
if sel_branch:
    cli_f = cli_f[cli_f["branch"].isin(sel_branch)]
ids = set(cli_f["client_id"])


def fil(df):
    return df[df["client_id"].isin(ids)]


aum = fil(aum_all)
txn = fil(txn_all)
txn["month"] = txn["txn_date"].dt.to_period("M").dt.to_timestamp("M")
txn_p = txn[txn["month"].isin(pset)]

# --------------------------------------------------------------------------- measures
client_month = aum.groupby(["client_id", "snapshot_date"], as_index=False)["aum_value"].sum()


def aum_at(d):
    return aum.loc[aum["snapshot_date"] == d, "aum_value"].sum()


def active_at(d):
    s = client_month[(client_month["snapshot_date"] == d) & (client_month["aum_value"] > 0)]
    return s["client_id"].nunique()


def in_period(series):
    return series.dt.to_period("M").dt.to_timestamp("M").isin(pset)


def churn_rate_for(c):
    churned = ((c["status"] == "Churned") & in_period(c["churn_date"].fillna(pd.Timestamp("1900-01-01")))).sum()
    new = in_period(c["onboarding_date"].fillna(pd.Timestamp("1900-01-01"))).sum()
    return churned, new


closing = aum_at(last_snap)
opening = aum_at(prior_end)
nna = txn_p["signed_amount"].sum()
market = closing - opening - nna
active = active_at(last_snap)
opening_active = active_at(prior_end)
churned, new_cl = churn_rate_for(cli_f)
churn_rate = churned / (opening_active + new_cl) if (opening_active + new_cl) else np.nan
churned_aum = cli_f.loc[(cli_f["status"] == "Churned") & in_period(cli_f["churn_date"].fillna(pd.Timestamp("1900-01-01"))), "aum_lost"].sum()
firm_cli = cli
f_churned, f_new = churn_rate_for(firm_cli)
firm_open_active = client_month_all = aum_all.groupby(["client_id", "snapshot_date"], as_index=False)["aum_value"].sum()
firm_open_active = client_month_all[(client_month_all["snapshot_date"] == prior_end) & (client_month_all["aum_value"] > 0)]["client_id"].nunique()
firm_churn = f_churned / (firm_open_active + f_new) if (firm_open_active + f_new) else np.nan
dormant = cli_f[cli_f["is_dormant"]]

fmt_cr = lambda v: f"Rs {v / CR:,.0f} Cr"
fmt_pct = lambda v: "n/a" if pd.isna(v) else f"{v * 100:.1f}%"

st.sidebar.caption(
    f"Period: {first_month:%b %Y} to {last_snap:%b %Y}  |  {len(ids):,} clients in selection"
)

# --------------------------------------------------------------------------- pages
st.title("Northstar Wealth | Wealth Management Analytics")
tabs = st.tabs(["1. Executive Summary", "2. Clients and Segments", "3. Advisor Performance", "4. Churn and Retention"])

layout = dict(margin=dict(l=10, r=10, t=40, b=40), height=340, plot_bgcolor="white", paper_bgcolor="white",
              font=dict(color="#1d2b3a"))

# ----- page 1
with tabs[0]:
    k = st.columns(5)
    k[0].metric("Closing AUM", fmt_cr(closing))
    k[1].metric("Net New Assets", fmt_cr(nna))
    k[2].metric("Market Movement", fmt_cr(market))
    k[3].metric("Active Clients", f"{active:,}")
    k[4].metric("Churn Rate", fmt_pct(churn_rate))

    c1, c2 = st.columns(2)
    trend = aum[aum["snapshot_date"].isin(pset)].groupby("snapshot_date", as_index=False)["aum_value"].sum()
    trend["Cr"] = trend["aum_value"] / CR
    f = px.line(trend, x="snapshot_date", y="Cr", markers=True, color_discrete_sequence=[NAVY],
                title="AUM trend by month-end (Rs Cr)")
    f.update_layout(**layout, xaxis_title=None, yaxis_title=None)
    f.add_annotation(x=trend["snapshot_date"].iloc[-1], y=trend["Cr"].iloc[-1], text=f"{trend['Cr'].iloc[-1]:,.0f}",
                     showarrow=False, yshift=14)
    c1.plotly_chart(f, width="stretch")

    wf = go.Figure(go.Waterfall(
        x=["Opening AUM", "Net New Assets", "Market Movement", "Closing AUM"],
        measure=["absolute", "relative", "relative", "total"],
        y=[opening / CR, nna / CR, market / CR, closing / CR],
        increasing=dict(marker=dict(color=TEAL)), decreasing=dict(marker=dict(color=RED)),
        totals=dict(marker=dict(color=NAVY)), text=[f"{v / CR:,.0f}" for v in [opening, nna, market, closing]],
        textposition="outside"))
    wf.update_layout(**layout, title="AUM bridge: where did growth come from? (Rs Cr)")
    c2.plotly_chart(wf, width="stretch")

    c3, c4 = st.columns(2)
    flows = txn_p.assign(kind=np.where(txn_p["txn_type"].isin(["SIP", "Lumpsum"]), "Inflows",
                                       np.where(txn_p["txn_type"] == "Redemption", "Outflows", None)))
    flows = flows.dropna(subset=["kind"]).groupby(["month", "kind"], as_index=False)["amount"].sum()
    flows["Cr"] = flows["amount"] / CR
    f = px.bar(flows, x="month", y="Cr", color="kind", barmode="group",
               color_discrete_map={"Inflows": TEAL, "Outflows": RED}, title="Monthly gross inflows and outflows (Rs Cr)")
    f.update_layout(**layout, xaxis_title=None, yaxis_title=None, legend_title=None, legend=dict(orientation="h", y=-0.12, x=0))
    c3.plotly_chart(f, width="stretch")

    mix = aum[aum["snapshot_date"] == last_snap].groupby(["segment", "asset_class"], as_index=False)["aum_value"].sum()
    mix["Cr"] = mix["aum_value"] / CR
    f = px.bar(mix, y="segment", x="Cr", color="asset_class", orientation="h", color_discrete_map=ASSET_COLORS,
               category_orders={"asset_class": ["Equity", "Debt", "Gold", "Liquid"]},
               title="Closing AUM by segment and asset class (Rs Cr)")
    f.update_layout(**layout, xaxis_title=None, yaxis_title=None, legend_title=None, legend=dict(orientation="h", y=-0.12, x=0))
    c4.plotly_chart(f, width="stretch")

# ----- page 2
with tabs[1]:
    a = cli_f[cli_f["client_id"].isin(set(client_month.loc[(client_month["snapshot_date"] == last_snap) & (client_month["aum_value"] > 0), "client_id"]))]
    k = st.columns(4)
    k[0].metric("Active clients", f"{active:,}")
    k[1].metric("Avg AUM per client", f"Rs {closing / active / LAKH:,.1f} L" if active else "n/a")
    k[2].metric("Equity share of AUM", fmt_pct(aum.loc[(aum["snapshot_date"] == last_snap) & (aum["asset_class"] == "Equity"), "aum_value"].sum() / closing if closing else np.nan))
    k[3].metric("Dormant clients", f"{len(dormant):,}")

    c1, c2 = st.columns(2)
    city = a.assign(city=a["city"].fillna("Unknown")).groupby("city", as_index=False).size().sort_values("size", ascending=False).head(10)
    f = px.bar(city.sort_values("size"), x="size", y="city", orientation="h", color_discrete_sequence=[NAVY],
               title="Active clients by city (top 10)")
    f.update_layout(**layout, xaxis_title=None, yaxis_title=None)
    c1.plotly_chart(f, width="stretch")

    al = aum[aum["snapshot_date"] == last_snap].groupby(["risk_profile", "asset_class"], as_index=False)["aum_value"].sum()
    al["share"] = al["aum_value"] / al.groupby("risk_profile")["aum_value"].transform("sum")
    f = px.bar(al, x="risk_profile", y="share", color="asset_class", color_discrete_map=ASSET_COLORS,
               category_orders={"risk_profile": ["Conservative", "Moderate", "Aggressive"],
                                "asset_class": ["Equity", "Debt", "Gold", "Liquid"]},
               title="Asset allocation by risk profile (does stated risk drive allocation?)")
    f.update_layout(**layout, xaxis_title=None, yaxis_title=None, legend_title=None, yaxis_tickformat=".0%",
                    legend=dict(orientation="h", y=-0.12, x=0))
    c2.plotly_chart(f, width="stretch")

    c3, c4 = st.columns(2)
    ab = a.groupby("age_band", as_index=False).size()
    f = px.bar(ab, x="age_band", y="size", color_discrete_sequence=[TEAL], title="Active clients by age band")
    f.update_layout(**layout, xaxis_title=None, yaxis_title=None)
    c3.plotly_chart(f, width="stretch")
    sg = a.groupby("segment", as_index=False).agg(clients=("client_id", "count"), aum=("aum_latest", "sum"))
    sg["aum_cr"] = sg["aum"] / CR
    f = px.pie(sg, names="segment", values="aum_cr", hole=0.55, color_discrete_sequence=[NAVY, TEAL, AMBER],
               title="Share of AUM by segment (small client count, large AUM)")
    f.update_layout(**layout)
    c4.plotly_chart(f, width="stretch")

    st.subheader("Top 15 clients by AUM (as at the latest snapshot; ignores the period filter)")
    t = cli_f.sort_values("aum_latest", ascending=False).head(15)[["client_id", "full_name", "segment", "city", "risk_profile", "advisor_name", "aum_latest"]]
    t["AUM (Lakh)"] = (t["aum_latest"] / LAKH).round(1)
    st.dataframe(t.drop(columns="aum_latest"), hide_index=True, width="stretch")

# ----- page 3
with tabs[2]:
    def advisor_table():
        base = cli_f.groupby(["advisor_id", "advisor_name", "branch"], as_index=False).agg(clients=("client_id", "count"))
        cl = aum[aum["snapshot_date"] == last_snap].groupby("advisor_id", as_index=False)["aum_value"].sum().rename(columns={"aum_value": "closing"})
        nn = txn_p.groupby("advisor_id", as_index=False)["signed_amount"].sum().rename(columns={"signed_amount": "nna"})
        t = base.merge(cl, on="advisor_id", how="left").merge(nn, on="advisor_id", how="left").fillna({"closing": 0, "nna": 0})
        rates = []
        for aid in t["advisor_id"]:
            c = cli_f[cli_f["advisor_id"] == aid]
            ch, nw = churn_rate_for(c)
            op = client_month[(client_month["snapshot_date"] == prior_end) & (client_month["aum_value"] > 0)
                              & client_month["client_id"].isin(set(c["client_id"]))]["client_id"].nunique()
            rates.append(ch / (op + nw) if (op + nw) else np.nan)
        t["churn_rate"] = rates
        t["Closing AUM (Cr)"] = (t["closing"] / CR).round(1)
        t["NNA (Cr)"] = (t["nna"] / CR).round(1)
        t["Churn rate %"] = (t["churn_rate"] * 100).round(1)
        t["Churn vs firm (pts)"] = ((t["churn_rate"] - firm_churn) * 100).round(1)
        t["AUM rank"] = t["closing"].rank(ascending=False, method="min").astype(int)
        return t

    at = advisor_table()
    st.caption(f"Firm churn rate benchmark for this period: {fmt_pct(firm_churn)} (not affected by the branch or segment filter)")
    c1, c2 = st.columns(2)
    sc = at.dropna(subset=["churn_rate"])
    f = px.scatter(sc, x="Closing AUM (Cr)", y="Churn rate %", hover_name="advisor_name", color_discrete_sequence=[NAVY],
                   title="Advisors: AUM vs churn rate (above the line = worse than firm)")
    f.add_hline(y=firm_churn * 100, line_dash="dash", line_color=RED, annotation_text="Firm churn rate")
    f.update_layout(**layout)
    c1.plotly_chart(f, width="stretch")
    nb = at.groupby("branch", as_index=False)["nna"].sum()
    nb["Cr"] = nb["nna"] / CR
    f = px.bar(nb.sort_values("Cr"), x="Cr", y="branch", orientation="h", color_discrete_sequence=[TEAL],
               title="Net new assets by branch (Rs Cr)")
    f.update_layout(**layout, xaxis_title=None, yaxis_title=None)
    c2.plotly_chart(f, width="stretch")
    st.subheader("Advisor scorecard")
    show = at.sort_values("Closing AUM (Cr)", ascending=False)[
        ["AUM rank", "advisor_name", "branch", "clients", "Closing AUM (Cr)", "NNA (Cr)", "Churn rate %", "Churn vs firm (pts)"]]
    st.dataframe(
        show.style.format({"Closing AUM (Cr)": "{:,.1f}", "NNA (Cr)": "{:,.1f}", "Churn rate %": "{:.1f}",
                           "Churn vs firm (pts)": "{:+.1f}"})
        .map(lambda v: "color:#D1495B;font-weight:600" if v > 5 else ("color:#1B998B;font-weight:600" if v < 0 else ""),
             subset=["Churn vs firm (pts)"]),
        hide_index=True, width="stretch", height=420)

# ----- page 4
with tabs[3]:
    k = st.columns(4)
    k[0].metric("Churned clients", f"{churned:,}")
    k[1].metric("Churn rate", fmt_pct(churn_rate))
    k[2].metric("AUM lost to churn", fmt_cr(churned_aum))
    k[3].metric("Dormant AUM", fmt_cr(dormant["aum_latest"].sum()))

    ch = cli_f[(cli_f["status"] == "Churned") & cli_f["churn_date"].notna()].copy()
    ch["month"] = ch["churn_date"].dt.to_period("M").dt.to_timestamp("M")
    ch = ch[ch["month"].isin(pset)]
    rows = []
    for m in period:
        pm = (m.replace(day=1) - pd.Timedelta(days=1))
        op = client_month[(client_month["snapshot_date"] == pm) & (client_month["aum_value"] > 0)]["client_id"].nunique()
        nw = (cli_f["onboarding_date"].dt.to_period("M").dt.to_timestamp("M") == m).sum()
        cn = (ch["month"] == m).sum()
        rows.append((m, cn, cn / (op + nw) if (op + nw) else np.nan, ch.loc[ch["month"] == m, "aum_lost"].sum() / CR))
    mon = pd.DataFrame(rows, columns=["month", "churned", "rate", "aum_lost_cr"])
    c1, c2 = st.columns(2)
    f = go.Figure()
    f.add_bar(x=mon["month"], y=mon["churned"], name="Churned clients", marker_color=NAVY)
    f.add_scatter(x=mon["month"], y=mon["rate"], name="Churn rate", yaxis="y2", line=dict(color=RED), mode="lines+markers")
    f.update_layout(**layout, title="Monthly churned clients and churn rate", yaxis2=dict(overlaying="y", side="right", tickformat=".1%"),
                    legend=dict(orientation="h", y=-0.12, x=0))
    c1.plotly_chart(f, width="stretch")
    f = px.bar(mon, x="month", y="aum_lost_cr", color_discrete_sequence=[RED], title="AUM lost to churn by month (Rs Cr)")
    f.update_layout(**layout, xaxis_title=None, yaxis_title=None)
    c2.plotly_chart(f, width="stretch")

    def rate_by(col):
        out = []
        for key, c in cli_f.groupby(col):
            ch_, nw_ = churn_rate_for(c)
            op = client_month[(client_month["snapshot_date"] == prior_end) & (client_month["aum_value"] > 0)
                              & client_month["client_id"].isin(set(c["client_id"]))]["client_id"].nunique()
            out.append((key, ch_ / (op + nw_) if (op + nw_) else np.nan))
        return pd.DataFrame(out, columns=[col, "rate"]).sort_values("rate")

    c3, c4 = st.columns(2)
    r1 = rate_by("acquisition_channel")
    f = px.bar(r1, x="rate", y="acquisition_channel", orientation="h", color_discrete_sequence=[AMBER],
               title="Churn rate by acquisition channel")
    f.update_layout(**layout, xaxis_title=None, yaxis_title=None, xaxis_tickformat=".0%")
    c3.plotly_chart(f, width="stretch")
    r2 = rate_by("risk_profile")
    f = px.bar(r2, x="rate", y="risk_profile", orientation="h", color_discrete_sequence=[NAVY], title="Churn rate by risk profile")
    f.update_layout(**layout, xaxis_title=None, yaxis_title=None, xaxis_tickformat=".0%")
    c4.plotly_chart(f, width="stretch")

    st.caption("Churn rate = churned clients / (clients on the books at the start of the period + new clients).")
    st.subheader("Dormant clients to call first (top 25 by AUM)")
    d = dormant.sort_values("aum_latest", ascending=False).head(25)[["client_id", "full_name", "segment", "city", "advisor_name", "last_txn_date", "aum_latest"]]
    d["AUM (Lakh)"] = (d["aum_latest"] / LAKH).round(1)
    d["last_txn_date"] = d["last_txn_date"].dt.date
    st.dataframe(d.drop(columns="aum_latest"), hide_index=True, width="stretch")
