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
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
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


def add_tie_out_block(ws):
    """Add tie-out block in rows 10-21 of the Summary sheet using openpyxl formulas."""
    header_fill = PatternFill("solid", fgColor="0B2545")
    header_font = Font(bold=True, color="FFFFFF")
    bold_font = Font(bold=True)
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")

    thin_border = Side(style="thin", color="000000")
    double_border = Side(style="double", color="000000")
    total_border = Border(top=thin_border, bottom=double_border)

    # Headers in row 10
    headers = [
        ("A10", "City / Branch"),
        ("B10", "AUM (Rs Cr)"),
        ("C10", "Dormant Clients"),
        ("D10", "Dormant AUM (Rs Cr)"),
    ]
    for cell_ref, text_val in headers:
        cell = ws[cell_ref]
        cell.value = text_val
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    # Nine cities A11:A19 incl. Unknown
    cities = [
        "Ahmedabad",
        "Bengaluru",
        "Chennai",
        "Delhi NCR",
        "Hyderabad",
        "Kolkata",
        "Mumbai",
        "Pune",
        "Unknown",
    ]

    for idx, city in enumerate(cities, start=11):
        cell_a = ws[f"A{idx}"]
        cell_a.value = city
        cell_a.alignment = left_align

        cell_b = ws[f"B{idx}"]
        cell_b.value = f"=SUMIFS(Advisor_Scorecard!D:D, Advisor_Scorecard!B:B, A{idx})"
        cell_b.number_format = "#,##0.0"
        cell_b.alignment = right_align

        cell_c = ws[f"C{idx}"]
        cell_c.value = f"=COUNTIFS(Dormant_Clients!D:D, A{idx})"
        cell_c.number_format = "#,##0"
        cell_c.alignment = right_align

        cell_d = ws[f"D{idx}"]
        cell_d.value = f"=SUMIFS(Dormant_Clients!G:G, Dormant_Clients!D:D, A{idx})/100"
        cell_d.number_format = "#,##0.0"
        cell_d.alignment = right_align

    # Row 20: Totals
    ws["A20"].value = "Total"
    ws["A20"].font = bold_font
    ws["A20"].alignment = left_align
    ws["A20"].border = total_border

    ws["B20"].value = "=SUM(B11:B19)"
    ws["B20"].font = bold_font
    ws["B20"].number_format = "#,##0.0"
    ws["B20"].alignment = right_align
    ws["B20"].border = total_border

    ws["C20"].value = "=SUM(C11:C19)"
    ws["C20"].font = bold_font
    ws["C20"].number_format = "#,##0"
    ws["C20"].alignment = right_align
    ws["C20"].border = total_border

    ws["D20"].value = "=SUM(D11:D19)"
    ws["D20"].font = bold_font
    ws["D20"].number_format = "#,##0.0"
    ws["D20"].alignment = right_align
    ws["D20"].border = total_border

    # Row 21: Check cells using 0.1% tolerance
    ws["A21"].value = "Tie-out Check"
    ws["A21"].font = bold_font
    ws["A21"].alignment = left_align

    ws["B21"].value = '=IF(ABS(B20-B3)/B3<=0.001, "OK", "DIFF")'
    ws["B21"].font = bold_font
    ws["B21"].alignment = center_align

    ws["C21"].value = '=IF(ABS(C20-B7)/B7<=0.001, "OK", "DIFF")'
    ws["C21"].font = bold_font
    ws["C21"].alignment = center_align

    ws["D21"].value = '=IF(ABS(D20-B8)/B8<=0.001, "OK", "DIFF")'
    ws["D21"].font = bold_font
    ws["D21"].alignment = center_align

    # Remove auto-filter on Summary and adjust column widths
    ws.auto_filter.ref = None
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 24


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
        add_tie_out_block(writer.sheets["Summary"])
    log.info("Wrote %s  (%d sheets)", out, 1 + len(tables))


if __name__ == "__main__":
    main()
