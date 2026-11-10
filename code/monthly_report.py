"""
monthly_report.py  -  one command builds the Excel stakeholder pack
--------------------------------------------------------------------
What it does
  1. connects to PostgreSQL (settings come from environment variables)
  2. runs the data-quality gate  -> stops if any business rule is violated
  3. pulls the report tables with SQL
  4. writes a formatted Excel workbook into ./exports

Run:    python code/monthly_report.py
Needs:  pip install pandas sqlalchemy psycopg2-binary openpyxl

Connection settings (all optional except the password on most PCs):
  PGHOST (default localhost)   PGPORT (default 5432)   PGUSER (default postgres)
  PGPASSWORD                   PGDATABASE (default wm_analytics)
"""
import logging
import os
import sys
from datetime import date

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(message)s")
log = logging.getLogger("monthly_report")

# ----------------------------------------------------------------------
# 1. CONNECTION
# ----------------------------------------------------------------------
url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("PGUSER", "postgres"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST", "localhost"),
    port=int(os.getenv("PGPORT", "5432")),
    database=os.getenv("PGDATABASE", "wm_analytics"),
)
engine = create_engine(url)

# ----------------------------------------------------------------------
# 2. DATA-QUALITY GATE  (each rule must return 0 violations)
# ----------------------------------------------------------------------
GATE_SQL = """
SELECT 'Transaction dated before onboarding' AS rule, COUNT(*) AS violations
FROM wm.transactions t JOIN wm.clients c USING (client_id)
WHERE t.txn_date < c.onboarding_date
UNION ALL
SELECT 'Churned client without churn_date', COUNT(*)
FROM wm.clients WHERE status = 'Churned' AND churn_date IS NULL
UNION ALL
SELECT 'Active client with a churn_date', COUNT(*)
FROM wm.clients WHERE status = 'Active' AND churn_date IS NOT NULL
UNION ALL
SELECT 'Negative AUM rows', COUNT(*) FROM wm.monthly_aum WHERE aum_value < 0
"""

# ----------------------------------------------------------------------
# 3. REPORT TABLES  (sheet name -> SQL)
# ----------------------------------------------------------------------
REPORTS = {
    "AUM_Trend": """
        SELECT snapshot_date AS month_end,
               ROUND(SUM(aum_value) / 1e7, 1) AS aum_cr
        FROM wm.monthly_aum
        GROUP BY snapshot_date
        ORDER BY snapshot_date""",
    "Segment_Mix": """
        SELECT c.segment, m.asset_class, ROUND(SUM(m.aum_value) / 1e7, 1) AS aum_cr
        FROM wm.monthly_aum m JOIN wm.clients c USING (client_id)
        WHERE m.snapshot_date = (SELECT MAX(snapshot_date) FROM wm.monthly_aum)
        GROUP BY c.segment, m.asset_class
        ORDER BY c.segment, aum_cr DESC""",
    "Advisor_Scorecard": """
        WITH latest AS (
            SELECT client_id, SUM(aum_value) AS aum
            FROM wm.monthly_aum
            WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM wm.monthly_aum)
            GROUP BY client_id)
        SELECT a.advisor_name, a.branch,
               COUNT(*) FILTER (WHERE l.aum > 0)                     AS active_clients,
               ROUND(SUM(l.aum) / 1e7, 1)                            AS aum_cr,
               COUNT(*) FILTER (WHERE c.status = 'Churned')          AS churned_clients,
               ROUND(100.0 * COUNT(*) FILTER (WHERE c.status = 'Churned') / COUNT(*), 1)
                                                                     AS churn_rate_pct
        FROM wm.advisors a
        JOIN wm.clients c USING (advisor_id)
        JOIN latest l USING (client_id)
        GROUP BY a.advisor_name, a.branch
        ORDER BY aum_cr DESC""",
    "Dormant_Clients": """
        SELECT client_id, full_name, segment, city, advisor_id,
               last_txn_date, ROUND(aum_latest / 1e5, 1) AS aum_lakh
        FROM wm.vw_dim_client
        WHERE is_dormant
        ORDER BY aum_latest DESC""",
}


def style_sheet(ws, df):
    """Header colours, number formats, column widths, frozen header row, filter."""
    header_fill = PatternFill("solid", fgColor="0B2545")
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for i, col in enumerate(df.columns, start=1):
        longest = max([len(str(col))] + [len(str(v)) for v in df[col].head(200)])
        ws.column_dimensions[get_column_letter(i)].width = min(max(12, longest + 3), 40)
        if col.endswith(("_cr", "_lakh")) or col.endswith("_pct"):
            for row in ws.iter_rows(min_row=2, min_col=i, max_col=i):
                row[0].number_format = "#,##0.0"
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def main():
    log.info("Connecting to %s@%s/%s", url.username, url.host, url.database)
    with engine.connect() as conn:
        gate = pd.read_sql(text(GATE_SQL), conn)
        log.info("Data-quality gate:\n%s", gate.to_string(index=False))
        if gate["violations"].sum() > 0:
            log.error("Gate FAILED - report not produced.")
            sys.exit(1)
        log.info("Gate passed (0 violations).")

        tables = {name: pd.read_sql(text(sql), conn) for name, sql in REPORTS.items()}
        kpi = pd.read_sql(text("""
            SELECT ROUND(SUM(aum_value) / 1e7, 1) AS total_aum_cr,
                   COUNT(DISTINCT client_id) FILTER (WHERE aum_value > 0) AS active_clients
            FROM wm.monthly_aum
            WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM wm.monthly_aum)"""), conn)
        churn = pd.read_sql(text(
            "SELECT COUNT(*) FILTER (WHERE status = 'Churned') AS churned, COUNT(*) AS total "
            "FROM wm.clients"), conn)

    summary = pd.DataFrame({
        "metric": ["Report date", "Total AUM (Rs Cr)", "Active clients",
                   "Churned clients (since Jan 2024)", "Churn rate (%)",
                   "Dormant clients", "Dormant AUM (Rs Cr)"],
        "value": [str(date.today()),
                  float(kpi.total_aum_cr[0]), int(kpi.active_clients[0]),
                  int(churn.churned[0]), round(100 * churn.churned[0] / churn.total[0], 1),
                  len(tables["Dormant_Clients"]),
                  round(float(tables["Dormant_Clients"]["aum_lakh"].sum()) / 100, 1)],
    })

    os.makedirs("exports", exist_ok=True)
    out = os.path.join("exports", f"WM_Monthly_Report_{date.today():%Y%m%d}.xlsx")
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        for name, df in tables.items():
            df.to_excel(writer, sheet_name=name, index=False)
        style_sheet(writer.sheets["Summary"], summary)
        for name, df in tables.items():
            style_sheet(writer.sheets[name], df)
    log.info("Wrote %s  (%d sheets)", out, 1 + len(tables))


if __name__ == "__main__":
    main()
