"""
Sales Report Generator — Advanced Web Version (v2.3)
=====================================================
Upload CSV(s) → get polished Excel + PDF reports with insights.
Supports: Combined mode (1 report for all files) OR Separate mode
(one report per file, for branches/regions).

Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import xlsxwriter
import plotly.express as px
from datetime import datetime
from io import BytesIO
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Sales Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .hero {
        background: linear-gradient(135deg, #1F4E78 0%, #2E75B6 100%);
        padding: 2.5rem 2rem; border-radius: 16px; color: white;
        margin-bottom: 2rem; box-shadow: 0 8px 24px rgba(31,78,120,0.25);
    }
    .hero h1 { margin: 0 0 0.5rem 0; font-size: 2.2rem; }
    .hero p { margin: 0; opacity: 0.9; font-size: 1.05rem; }
    .metric-card {
        background: white; padding: 1.25rem; border-radius: 12px;
        border: 1px solid #E5E9F0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        text-align: center; height: 100%;
    }
    .metric-card .label {
        color: #6B7280; font-size: 0.8rem; text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .value {
        color: #1F4E78; font-size: 1.5rem; font-weight: 700; margin-top: 0.35rem;
    }
    .metric-card .delta-up { color: #16A34A; font-size: 0.85rem; margin-top: 0.25rem; }
    .metric-card .delta-down { color: #DC2626; font-size: 0.85rem; margin-top: 0.25rem; }
    .stButton>button {
        background: #1F4E78; color: white; border-radius: 8px;
        padding: 0.6rem 1.5rem; font-weight: 600; border: none;
    }
    .stButton>button:hover { background: #2E75B6; color: white; }
    .stDownloadButton>button {
        background: #16A34A; color: white; border-radius: 8px;
        padding: 0.7rem 1.5rem; font-weight: 600; border: none; font-size: 1rem;
    }
    .stDownloadButton>button:hover { background: #15803D; color: white; }
    div[data-testid="stFileUploader"] {
        background: #F8FAFC; padding: 1rem; border-radius: 12px;
        border: 2px dashed #CBD5E1;
    }
    .step-badge {
        display: inline-block; background: #1F4E78; color: white;
        border-radius: 50%; width: 28px; height: 28px; text-align: center;
        line-height: 28px; font-weight: 700; margin-right: 0.5rem;
    }
    .insight {
        background: #F0F9FF; border-left: 4px solid #1F4E78;
        padding: 0.75rem 1rem; border-radius: 6px; margin: 0.4rem 0;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================
if "history" not in st.session_state:
    st.session_state.history = []


# ============================================================
# HELPERS
# ============================================================
def safe_filename(text, fallback="Sales_Report"):
    """Strip anything that isn't safe for a filename."""
    cleaned = re.sub(r"[^A-Za-z0-9 _-]", "", str(text)).strip().replace(" ", "_")
    return cleaned if cleaned else fallback


# ============================================================
# DATA PIPELINE
# ============================================================
STANDARD_COLS = ["order_id", "date", "customer", "product",
                 "quantity", "unit_price", "revenue"]


def load_csv_safely(uploaded_file):
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    separators = [",", ";", "\t", "|"]
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    for enc in encodings:
        for sep in separators:
            try:
                df = pd.read_csv(BytesIO(raw), encoding=enc, sep=sep)
                if df.shape[1] >= 2:
                    return df, f"{uploaded_file.name}: loaded ({enc}, sep='{sep}')"
            except Exception:
                continue
    return None, f"{uploaded_file.name}: could not be read"


def normalize_columns(df):
    df.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_")
                  for c in df.columns]
    aliases = {
        "order_id": ["order_id","order_no","orderno","invoice_no","invoice_id",
                     "invoice","id","order","receipt_no","transaction_id","txn_id"],
        "date": ["date","order_date","invoice_date","sale_date","sales_date",
                 "transaction_date","created_at","timestamp","day"],
        "customer": ["customer","customer_name","client","client_name","buyer",
                     "buyer_name","name","cust_name","account"],
        "product": ["product","product_name","item","item_name","description",
                    "sku","product_description","goods"],
        "quantity": ["quantity","qty","units","unit","count","amount_sold",
                     "quantity_sold","num_units"],
        "unit_price": ["unit_price","price","price_per_unit","rate","unit_cost",
                       "cost","unit_amount"],
        "revenue": ["revenue","total","amount","total_price","sales","total_amount",
                    "total_sales","grand_total","line_total","net_amount","gross_amount"],
    }
    rename_map, used = {}, set()
    for std, opts in aliases.items():
        for o in opts:
            if o in df.columns and std not in df.columns and std not in used:
                rename_map[o] = std
                used.add(std)
                break
    return df.rename(columns=rename_map)


def validate_and_clean(df):
    warnings = []
    if "date" not in df.columns:
        return None, ["Could not find a date column. Expected: date, order_date, invoice_date…"]
    if "revenue" not in df.columns:
        if "quantity" in df.columns and "unit_price" in df.columns:
            df["revenue"] = df["quantity"] * df["unit_price"]
        else:
            return None, ["Cannot compute revenue. Need 'revenue' OR both 'quantity' & 'unit_price'."]
    for col in ["quantity", "unit_price", "revenue"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad_d = df["date"].isna().sum()
    if bad_d:
        warnings.append(f"Dropped {bad_d} row(s) with unreadable dates.")
        df = df.dropna(subset=["date"])
    bad_r = df["revenue"].isna().sum()
    if bad_r:
        warnings.append(f"Dropped {bad_r} row(s) with invalid revenue.")
        df = df.dropna(subset=["revenue"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    for col, default, msg in [
        ("order_id", range(1, len(df)+1), "No order ID column — generated sequential."),
        ("customer", "Unknown Customer", "No customer column — labeled 'Unknown'."),
        ("product", "Unknown Product", "No product column — labeled 'Unknown'."),
        ("quantity", 1, "No quantity column — defaulted to 1."),
    ]:
        if col not in df.columns:
            df[col] = default
            warnings.append(msg)
    if len(df) == 0:
        return None, ["No valid rows after cleaning."]
    return df, warnings


# ============================================================
# ANALYTICS
# ============================================================
def compute_insights(df):
    insights = []
    monthly = df.groupby("month")["revenue"].sum().sort_index()
    if len(monthly) >= 2:
        last, prev = monthly.iloc[-1], monthly.iloc[-2]
        if prev > 0:
            change = (last - prev) / prev * 100
            arrow = "📈" if change >= 0 else "📉"
            insights.append(f"{arrow} Revenue moved {change:+.1f}% from {monthly.index[-2]} to {monthly.index[-1]}.")

    top_prod = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    if len(top_prod) > 0:
        share = top_prod.iloc[0] / df["revenue"].sum() * 100
        insights.append(f"🏆 '{top_prod.index[0]}' drives {share:.0f}% of total revenue.")

    top_cust = df.groupby("customer")["revenue"].sum().sort_values(ascending=False)
    if len(top_cust) > 0:
        share = top_cust.iloc[0] / df["revenue"].sum() * 100
        insights.append(f"👤 Top customer '{top_cust.index[0]}' accounts for {share:.0f}% of revenue.")

    if len(monthly) > 0:
        best_month = monthly.idxmax()
        insights.append(f"⭐ Best month: {best_month} (${monthly.max():,.0f}).")

    return insights


def apply_filter(df, choice):
    """Apply the period filter to a dataframe."""
    if len(df) == 0:
        return df
    now = df["date"].max()
    if choice == "Last 30 days":
        return df[df["date"] >= now - pd.Timedelta(days=30)]
    if choice == "Last 90 days":
        return df[df["date"] >= now - pd.Timedelta(days=90)]
    if choice == "This year":
        return df[df["date"].dt.year == now.year]
    return df


# ============================================================
# EXCEL BUILDER
# ============================================================
def build_excel_bytes(df, company_name):
    out = BytesIO()
    wb = xlsxwriter.Workbook(out, {"in_memory": True})

    title_fmt = wb.add_format({"bold": True, "font_size": 16, "font_color": "#1F4E78"})
    header_fmt = wb.add_format({"bold": True, "bg_color": "#1F4E78",
                                "font_color": "white", "border": 1,
                                "align": "center", "valign": "vcenter"})
    money_fmt = wb.add_format({"num_format": "$#,##0.00", "border": 1})
    cell_fmt = wb.add_format({"border": 1})
    bold_fmt = wb.add_format({"bold": True, "border": 1})

    # Summary
    ws = wb.add_worksheet("Summary")
    ws.set_column("A:A", 28); ws.set_column("B:B", 24)
    ws.write("A1", f"{company_name} — Sales Report", title_fmt)
    ws.write("A2", f"Generated: {datetime.now():%Y-%m-%d %H:%M}")
    ws.write("A3", f"Data range: {df['date'].min():%Y-%m-%d} to {df['date'].max():%Y-%m-%d}")

    total_rev = float(df["revenue"].sum())
    total_orders = int(df["order_id"].nunique())
    total_units = int(df["quantity"].sum())
    avg_order = total_rev / total_orders if total_orders else 0
    top_prod = df.groupby("product")["revenue"].sum().idxmax()

    ws.write("A5", "Key Metrics", header_fmt); ws.write("B5", "", header_fmt)
    rows = [("Total Revenue", total_rev, True), ("Total Orders", total_orders, False),
            ("Total Units Sold", total_units, False), ("Avg Order Value", avg_order, True),
            ("Top Product", top_prod, False)]
    r = 6
    for lab, val, money in rows:
        ws.write(r, 0, lab, bold_fmt)
        if money: ws.write_number(r, 1, val, money_fmt)
        elif isinstance(val, (int, float)): ws.write_number(r, 1, val, cell_fmt)
        else: ws.write(r, 1, str(val), cell_fmt)
        r += 1

    insights = compute_insights(df)
    if insights:
        ws.write("A13", "Highlights", header_fmt); ws.write("B13", "", header_fmt)
        for i, txt in enumerate(insights):
            ws.write(14 + i, 0, re.sub(r"[^\x00-\x7F]+", "", txt).strip(), cell_fmt)

    # Monthly
    ws2 = wb.add_worksheet("Monthly Trends")
    for c, w in zip("ABCD", [15, 18, 15, 15]): ws2.set_column(f"{c}:{c}", w)
    monthly = df.groupby("month").agg(
        Revenue=("revenue", "sum"), Orders=("order_id", "nunique"),
        Units=("quantity", "sum")).reset_index()
    ws2.write("A1", "Monthly Performance", title_fmt)
    for c, h in enumerate(["Month", "Revenue", "Orders", "Units"]):
        ws2.write(3, c, h, header_fmt)
    for i, row in monthly.iterrows():
        ws2.write(i+4, 0, row["month"], cell_fmt)
        ws2.write_number(i+4, 1, float(row["Revenue"]), money_fmt)
        ws2.write_number(i+4, 2, int(row["Orders"]), cell_fmt)
        ws2.write_number(i+4, 3, int(row["Units"]), cell_fmt)
    chart = wb.add_chart({"type": "column"})
    chart.add_series({"name": "Revenue",
                      "categories": ["Monthly Trends", 4, 0, 4+len(monthly)-1, 0],
                      "values": ["Monthly Trends", 4, 1, 4+len(monthly)-1, 1],
                      "fill": {"color": "#1F4E78"}})
    chart.set_title({"name": "Monthly Revenue"})
    chart.set_size({"width": 720, "height": 400})
    ws2.insert_chart("F4", chart)

    # Products
    ws3 = wb.add_worksheet("Top Products")
    for c, w in zip("ABCD", [30, 15, 15, 18]): ws3.set_column(f"{c}:{c}", w)
    prods = df.groupby("product").agg(
        Units=("quantity", "sum"), Orders=("order_id", "nunique"),
        Revenue=("revenue", "sum")).sort_values("Revenue", ascending=False).reset_index()
    ws3.write("A1", "Product Performance", title_fmt)
    for c, h in enumerate(["Product", "Units Sold", "Orders", "Revenue"]):
        ws3.write(3, c, h, header_fmt)
    for i, row in prods.iterrows():
        ws3.write(i+4, 0, str(row["product"]), cell_fmt)
        ws3.write_number(i+4, 1, int(row["Units"]), cell_fmt)
        ws3.write_number(i+4, 2, int(row["Orders"]), cell_fmt)
        ws3.write_number(i+4, 3, float(row["Revenue"]), money_fmt)
    pchart = wb.add_chart({"type": "bar"})
    pchart.add_series({"name": "Revenue",
                       "categories": ["Top Products", 4, 0, 4+len(prods)-1, 0],
                       "values": ["Top Products", 4, 3, 4+len(prods)-1, 3],
                       "fill": {"color": "#2E75B6"}})
    pchart.set_title({"name": "Revenue by Product"})
    pchart.set_size({"width": 720, "height": 400})
    ws3.insert_chart("F4", pchart)

    # Customers
    ws4 = wb.add_worksheet("Top Customers")
    for c, w in zip("ABCD", [30, 15, 15, 18]): ws4.set_column(f"{c}:{c}", w)
    custs = df.groupby("customer").agg(
        Orders=("order_id", "nunique"), Units=("quantity", "sum"),
        Revenue=("revenue", "sum")).sort_values("Revenue", ascending=False).reset_index()
    ws4.write("A1", "Customer Performance", title_fmt)
    for c, h in enumerate(["Customer", "Orders", "Units", "Revenue"]):
        ws4.write(3, c, h, header_fmt)
    for i, row in custs.iterrows():
        ws4.write(i+4, 0, str(row["customer"]), cell_fmt)
        ws4.write_number(i+4, 1, int(row["Orders"]), cell_fmt)
        ws4.write_number(i+4, 2, int(row["Units"]), cell_fmt)
        ws4.write_number(i+4, 3, float(row["Revenue"]), money_fmt)

    # Raw
    ws5 = wb.add_worksheet("Raw Data")
    for c, h in enumerate(["Order ID", "Date", "Customer", "Product",
                            "Qty", "Unit Price", "Revenue"]):
        ws5.write(0, c, h, header_fmt)
    for i, row in df.iterrows():
        ws5.write(i+1, 0, str(row["order_id"]), cell_fmt)
        ws5.write(i+1, 1, row["date"].strftime("%Y-%m-%d"), cell_fmt)
        ws5.write(i+1, 2, str(row["customer"]), cell_fmt)
        ws5.write(i+1, 3, str(row["product"]), cell_fmt)
        ws5.write_number(i+1, 4, float(row["quantity"]), cell_fmt)
        ws5.write_number(i+1, 5, float(row.get("unit_price", 0)), money_fmt)
        ws5.write_number(i+1, 6, float(row["revenue"]), money_fmt)

    wb.close()
    out.seek(0)
    return out.getvalue()


# ============================================================
# PDF BUILDER
# ============================================================
def build_pdf_bytes(df, company_name, brand_color="#1F4E78"):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"],
                                 textColor=colors.HexColor(brand_color), fontSize=22)
    h2 = ParagraphStyle("H2X", parent=styles["Heading2"],
                        textColor=colors.HexColor(brand_color), spaceAfter=8)
    body = styles["BodyText"]

    story = []
    story.append(Paragraph(f"{company_name} — Sales Report", title_style))
    story.append(Paragraph(f"Generated {datetime.now():%Y-%m-%d %H:%M}", body))
    story.append(Paragraph(
        f"Data range: {df['date'].min():%Y-%m-%d} to {df['date'].max():%Y-%m-%d}", body))
    story.append(Spacer(1, 0.5*cm))

    total_rev = float(df["revenue"].sum())
    total_orders = int(df["order_id"].nunique())
    avg_order = total_rev / total_orders if total_orders else 0
    story.append(Paragraph("Key Metrics", h2))
    kpi_data = [
        ["Metric", "Value"],
        ["Total Revenue", f"${total_rev:,.2f}"],
        ["Total Orders", f"{total_orders:,}"],
        ["Average Order Value", f"${avg_order:,.2f}"],
    ]
    t = Table(kpi_data, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(brand_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    insights = compute_insights(df)
    if insights:
        story.append(Paragraph("Highlights", h2))
        for ins in insights:
            clean = re.sub(r"[^\x00-\x7F]+", "", ins).strip()
            story.append(Paragraph(f"• {clean}", body))
        story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Top Products", h2))
    prods = df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(10)
    prod_data = [["Product", "Revenue"]]
    for name, rev in prods.items():
        prod_data.append([str(name)[:40], f"${rev:,.2f}"])
    t2 = Table(prod_data, colWidths=[11*cm, 5*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(brand_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


# ============================================================
# HELPER — process one file
# ============================================================
def process_file(uploaded_file, filter_choice):
    """Load, clean, filter a single uploaded file. Returns (clean_df, warnings) or (None, errors)."""
    raw, note = load_csv_safely(uploaded_file)
    if raw is None:
        return None, [note]
    raw = normalize_columns(raw)
    clean, notes = validate_and_clean(raw)
    if clean is None:
        return None, notes
    clean = apply_filter(clean, filter_choice)
    if len(clean) == 0:
        return None, [f"{uploaded_file.name}: no data in the selected period."]
    return clean, notes


# ============================================================
# UI — HERO
# ============================================================
st.markdown("""
<div class="hero">
    <h1>📊 Sales Report Generator</h1>
    <p>Upload your sales CSV → get a polished Excel + PDF report in seconds.</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.2, 1.2, 0.8], gap="large")

with col1:
    st.markdown("### <span class='step-badge'>1</span> Business Details", unsafe_allow_html=True)
    company_name = st.text_input("Company name", placeholder="e.g. Nairobi Electronics Ltd")
    brand_color = st.color_picker("Brand color (for PDF)", "#1F4E78")

with col2:
    st.markdown("### <span class='step-badge'>2</span> Upload Sales Data", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Choose one or more CSV files",
        type=["csv"],
        accept_multiple_files=True,
        help="Upload multiple files — e.g. one per branch.",
    )

with col3:
    st.markdown("### <span class='step-badge'>3</span> Filter (optional)", unsafe_allow_html=True)
    filter_choice = st.selectbox("Period", ["All time", "Last 30 days", "Last 90 days", "This year"])

# ---- Report mode selector (only if 2+ files) ----
separate_mode = False
if uploaded_files and len(uploaded_files) > 1:
    report_mode = st.radio(
        "📚 How should I generate reports?",
        ["Combine all files into ONE report", "Generate a SEPARATE report per file"],
        horizontal=True,
        help="Combine = company-wide total. Separate = one report per branch/file.",
    )
    separate_mode = report_mode.startswith("Generate a SEPARATE")

st.markdown("---")
generate = st.button("🚀 Generate Reports", width="stretch")


# ============================================================
# MAIN ACTION
# ============================================================
if generate:
    if not company_name.strip():
        st.error("⚠️ Please enter your company name.")
        st.stop()
    if not uploaded_files:
        st.error("⚠️ Please upload at least one CSV.")
        st.stop()

    # ============================================
    # MODE A — SEPARATE REPORTS PER FILE
    # ============================================
    if separate_mode:
        st.success(f"✅ Generating {len(uploaded_files)} separate reports...")

        results = []
        with st.spinner("Processing each file..."):
            for f in uploaded_files:
                clean, notes = process_file(f, filter_choice)
                if clean is None:
                    st.warning(f"⚠️ Skipped '{f.name}': {'; '.join(notes)}")
                    continue
                # Label used ONLY in the UI (not in downloads/titles)
                label = re.sub(r"\.csv$", "", f.name, flags=re.IGNORECASE)
                results.append((label, clean, notes))

        if not results:
            st.error("❌ No valid files to generate reports from.")
            st.stop()

        # Clean company-only filename base
        safe_company = safe_filename(company_name.strip(), fallback="Sales_Report")
        stamp = datetime.now().strftime("%Y-%m-%d")

        for idx, (label, df, notes) in enumerate(results, start=1):
            with st.expander(
                f"📄 {label}  —  {len(df):,} rows  |  ${df['revenue'].sum():,.0f} revenue",
                expanded=(idx == 1)
            ):
                c1, c2, c3 = st.columns(3)
                c1.metric("Revenue", f"${df['revenue'].sum():,.0f}")
                c2.metric("Orders", f"{df['order_id'].nunique():,}")
                c3.metric("Products", f"{df['product'].nunique()}")

                mdf = df.groupby("month")["revenue"].sum().reset_index()
                fig = px.bar(mdf, x="month", y="revenue",
                             color_discrete_sequence=["#1F4E78"])
                fig.update_layout(margin=dict(l=0, r=0, t=10, b=0),
                                  height=220, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig, width="stretch")

                if notes:
                    with st.expander("⚠️ Data notes"):
                        for n in notes: st.write(f"- {n}")

                # Report title uses ONLY the company name — no file label
                report_title = company_name.strip()
                excel_bytes = build_excel_bytes(df, report_title)
                pdf_bytes = build_pdf_bytes(df, report_title, brand_color)

                # Download filenames also use only the company name (+ index)
                file_tag = f"_{idx:02d}"
                d1, d2 = st.columns(2)
                with d1:
                    st.download_button(
                        f"⬇️ Excel — {label}",
                        data=excel_bytes,
                        file_name=f"{safe_company}{file_tag}_{stamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch",
                        key=f"xlsx_{idx}",
                    )
                with d2:
                    st.download_button(
                        f"⬇️ PDF — {label}",
                        data=pdf_bytes,
                        file_name=f"{safe_company}{file_tag}_{stamp}.pdf",
                        mime="application/pdf",
                        width="stretch",
                        key=f"pdf_{idx}",
                    )

        total_rows = sum(len(df) for _, df, _ in results)
        total_rev = sum(df["revenue"].sum() for _, df, _ in results)
        st.session_state.history.append({
            "company": company_name,
            "mode": "Separate",
            "files": len(results),
            "rows": total_rows,
            "revenue": total_rev,
            "time": datetime.now().strftime("%H:%M:%S"),
        })
        st.stop()

    # ============================================
    # MODE B — COMBINED (single report)
    # ============================================
    with st.spinner("Processing your data..."):
        frames, notes = [], []
        for f in uploaded_files:
            raw, note = load_csv_safely(f)
            notes.append(note)
            if raw is not None:
                frames.append(raw)

        if not frames:
            st.error("❌ None of the uploaded files could be read.")
            st.stop()

        combined = pd.concat(frames, ignore_index=True)
        combined = normalize_columns(combined)
        clean_df, result = validate_and_clean(combined)

        if clean_df is None:
            st.error("❌ Could not build the report:")
            for m in result: st.write(f"- {m}")
            st.stop()

        clean_df = apply_filter(clean_df, filter_choice)
        if len(clean_df) == 0:
            st.error("No data in the selected period.")
            st.stop()

    st.success(f"✅ Report ready! {len(clean_df):,} rows analyzed.")

    # ---- KPIs ----
    total_rev = clean_df["revenue"].sum()
    total_orders = clean_df["order_id"].nunique()
    avg_order = total_rev / total_orders if total_orders else 0
    monthly = clean_df.groupby("month")["revenue"].sum().sort_index()
    growth = 0
    if len(monthly) >= 2 and monthly.iloc[-2] > 0:
        growth = (monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2] * 100

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="metric-card"><div class="label">Total Revenue</div>
            <div class="value">${total_rev:,.0f}</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="metric-card"><div class="label">Orders</div>
            <div class="value">{total_orders:,}</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="metric-card"><div class="label">Avg Order</div>
            <div class="value">${avg_order:,.0f}</div></div>""", unsafe_allow_html=True)
    with k4:
        cls = "delta-up" if growth >= 0 else "delta-down"
        arrow = "▲" if growth >= 0 else "▼"
        st.markdown(f"""<div class="metric-card"><div class="label">MoM Growth</div>
            <div class="value">{arrow} {growth:+.1f}%</div>
            <div class="{cls}">vs previous month</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Charts ----
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📈 Monthly Revenue")
        mdf = clean_df.groupby("month")["revenue"].sum().reset_index()
        fig = px.bar(mdf, x="month", y="revenue", color_discrete_sequence=["#1F4E78"])
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300,
                          xaxis_title="", yaxis_title="Revenue ($)")
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.markdown("#### 🏆 Top Products")
        pdf_chart = clean_df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(8).reset_index()
        fig2 = px.bar(pdf_chart, x="revenue", y="product", orientation="h",
                      color_discrete_sequence=["#2E75B6"])
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300,
                           xaxis_title="Revenue ($)", yaxis_title="")
        fig2.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig2, width="stretch")

    # ---- Insights ----
    insights = compute_insights(clean_df)
    if insights:
        st.markdown("#### 💡 Insights")
        for ins in insights:
            st.markdown(f"<div class='insight'>{ins}</div>", unsafe_allow_html=True)

    # ---- Warnings ----
    if result or any("could not" in n for n in notes):
        with st.expander("⚠️ Data notes"):
            for w in result: st.write(f"- {w}")
            for n in notes:
                if "could not" in n: st.write(f"- {n}")

    # ---- Download ----
    st.markdown("---")
    st.markdown("### 📥 Download Your Reports")
    d1, d2 = st.columns(2)

    excel_bytes = build_excel_bytes(clean_df, company_name.strip())
    pdf_bytes = build_pdf_bytes(clean_df, company_name.strip(), brand_color)
    safe_company = safe_filename(company_name.strip(), fallback="Sales_Report")
    stamp = datetime.now().strftime("%Y-%m-%d")

    with d1:
        st.download_button(
            "⬇️  Download Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"{safe_company}_Sales_Report_{stamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
    with d2:
        st.download_button(
            "⬇️  Download PDF",
            data=pdf_bytes,
            file_name=f"{safe_company}_Sales_Report_{stamp}.pdf",
            mime="application/pdf",
            width="stretch",
        )

    st.session_state.history.append({
        "company": company_name,
        "mode": "Combined",
        "files": len(uploaded_files),
        "rows": len(clean_df),
        "revenue": total_rev,
        "time": datetime.now().strftime("%H:%M:%S"),
    })

# ---- Session history ----
if st.session_state.history:
    with st.expander(f"🕘 Session history ({len(st.session_state.history)} reports)"):
        st.dataframe(pd.DataFrame(st.session_state.history), width="stretch")

# ---- Footer ----
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#94A3B8; font-size:0.85rem;'>"
    "Sales Report Generator v2.3</div>",
    unsafe_allow_html=True,
)
