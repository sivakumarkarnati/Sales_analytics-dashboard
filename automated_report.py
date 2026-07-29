"""
automated_report.py
Generates a weekly summary report (CSV + simple text summary) from the MySQL
database. Intended to be run on a schedule (cron / Windows Task Scheduler /
Python `schedule` library) to demonstrate automated reporting.

Usage:
    python automated_report.py
"""

from datetime import date, timedelta

import pandas as pd

from db_config import get_connection

REPORT_DIR = "reports"


def generate_weekly_report():
    import os
    os.makedirs(REPORT_DIR, exist_ok=True)

    end_date = date.today()
    start_date = end_date - timedelta(days=7)

    query = """
        SELECT
            o.order_date,
            o.region,
            p.category,
            (oi.quantity * oi.unit_price) AS line_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.order_date BETWEEN %s AND %s
          AND o.status = 'Completed'
    """
    conn = get_connection()
    df = pd.read_sql(query, conn, params=(start_date, end_date))
    conn.close()

    total_revenue = df["line_revenue"].sum()
    top_region = df.groupby("region")["line_revenue"].sum().idxmax() if not df.empty else "N/A"
    top_category = df.groupby("category")["line_revenue"].sum().idxmax() if not df.empty else "N/A"

    summary_path = f"{REPORT_DIR}/weekly_summary_{end_date}.txt"
    csv_path = f"{REPORT_DIR}/weekly_data_{end_date}.csv"

    with open(summary_path, "w") as f:
        f.write(f"Weekly Sales Report ({start_date} to {end_date})\n")
        f.write("=" * 50 + "\n")
        f.write(f"Total Revenue: ${total_revenue:,.2f}\n")
        f.write(f"Top Region: {top_region}\n")
        f.write(f"Top Category: {top_category}\n")
        f.write(f"Total Line Items: {len(df)}\n")

    df.to_csv(csv_path, index=False)
    print(f"Report generated: {summary_path}")
    print(f"Data exported: {csv_path}")


if __name__ == "__main__":
    generate_weekly_report()

# ---------------------------------------------------------------------------
# To automate this on a schedule, either:
#   1. Add a cron job (Linux/Mac):
#        0 8 * * MON  cd /path/to/project && python automated_report.py
#   2. Use the `schedule` library and run this as a long-lived process:
#        import schedule, time
#        schedule.every().monday.at("08:00").do(generate_weekly_report)
#        while True:
#            schedule.run_pending()
#            time.sleep(60)
# ---------------------------------------------------------------------------
