"""
Landing Page — Sales Report Generator
======================================
Public-facing page. Clients see this first, then click "Try it free".
"""

import streamlit as st

st.set_page_config(
    page_title="Sales Report Generator — Turn CSVs Into Client-Ready Reports",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    .main { padding-top: 0; }
    .hero {
        background: linear-gradient(135deg, #1F4E78 0%, #2E75B6 100%);
        padding: 4rem 2rem; border-radius: 20px; color: white;
        text-align: center; margin-bottom: 2rem;
        box-shadow: 0 12px 32px rgba(31,78,120,0.3);
    }
    .hero h1 { font-size: 3rem; margin: 0 0 1rem 0; }
    .hero p { font-size: 1.3rem; opacity: 0.95; margin: 0 0 2rem 0; }
    .cta {
        display: inline-block; background: white; color: #1F4E78;
        padding: 1rem 2.5rem; border-radius: 10px; font-weight: 700;
        font-size: 1.1rem; text-decoration: none;
        box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    }
    .cta:hover { background: #F0F9FF; }
    .feature {
        background: white; padding: 1.75rem; border-radius: 14px;
        border: 1px solid #E5E9F0; height: 100%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    .feature .icon { font-size: 2rem; margin-bottom: 0.75rem; }
    .feature h3 { color: #1F4E78; margin: 0 0 0.5rem 0; font-size: 1.15rem; }
    .feature p { color: #475569; margin: 0; font-size: 0.95rem; line-height: 1.5; }
    .step-card {
        background: #F8FAFC; padding: 1.5rem; border-radius: 12px;
        border-left: 4px solid #1F4E78; height: 100%;
    }
    .step-card .num {
        background: #1F4E78; color: white; border-radius: 50%;
        width: 32px; height: 32px; display: inline-flex;
        align-items: center; justify-content: center;
        font-weight: 700; margin-bottom: 0.75rem;
    }
    .step-card h4 { color: #1F4E78; margin: 0 0 0.4rem 0; }
    .step-card p { color: #475569; margin: 0; font-size: 0.92rem; }
    .pricing {
        background: white; padding: 2rem; border-radius: 14px;
        border: 2px solid #1F4E78; text-align: center; height: 100%;
    }
    .pricing h3 { color: #1F4E78; margin: 0 0 0.5rem 0; }
    .pricing .price { font-size: 2rem; color: #1F4E78; font-weight: 700; margin: 1rem 0; }
    .pricing ul { text-align: left; color: #475569; padding-left: 1.5rem; }
    .pricing li { margin-bottom: 0.4rem; }
    .footer { text-align: center; color: #94A3B8; font-size: 0.85rem; padding: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div class="hero">
    <h1>📊 Sales Report Generator</h1>
    <p>Turn your messy sales CSV into a polished, client-ready report — in 30 seconds.</p>
    <a class="cta" href="/app" target="_self">🚀 Try It Free →</a>
</div>
""", unsafe_allow_html=True)

# PROBLEM / SOLUTION
st.markdown("## Stop Wasting Hours in Excel")
st.markdown(
    "Every month, you open last month's spreadsheet, copy formulas, paste data, "
    "fix broken dates, rebuild charts… **and repeat it all over again.** "
    "This tool does it in one click."
)
st.markdown("<br>", unsafe_allow_html=True)

# FEATURES
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="feature">
        <div class="icon">⚡</div>
        <h3>Instant Reports</h3>
        <p>Upload any sales CSV. Get a formatted multi-sheet Excel + PDF report in seconds — no formulas, no formatting, no stress.</p>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="feature">
        <div class="icon">🧠</div>
        <h3>Smart Auto-Detection</h3>
        <p>Works with any column names. "Invoice No", "Order Date", "Qty", "Total" — the tool figures it out automatically.</p>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="feature">
        <div class="icon">📈</div>
        <h3>Real Insights</h3>
        <p>Monthly trends, top products, top customers, growth %. Plain-English highlights that explain what the numbers mean.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# HOW IT WORKS
st.markdown("## How It Works")
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown("""
    <div class="step-card">
        <div class="num">1</div>
        <h4>Enter your business name</h4>
        <p>Used as the report header. Takes 5 seconds.</p>
    </div>
    """, unsafe_allow_html=True)
with s2:
    st.markdown("""
    <div class="step-card">
        <div class="num">2</div>
        <h4>Upload your sales CSV</h4>
        <p>Export from Shopify, POS, Excel, Google Sheets — anything goes.</p>
    </div>
    """, unsafe_allow_html=True)
with s3:
    st.markdown("""
    <div class="step-card">
        <div class="num">3</div>
        <h4>Download the report</h4>
        <p>Get Excel + PDF. Share with your team, accountant, or investors.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# CTA AGAIN
st.markdown("""
<div style='text-align:center; padding: 2rem 0;'>
    <a class="cta" href="/app" target="_self"
       style='background:#1F4E78; color:white;'>Generate My First Report →</a>
</div>
""", unsafe_allow_html=True)

# FOOTER
st.markdown("""
<div class="footer">
    Sales Report Generator — Built for small businesses that hate Excel.
</div>
""", unsafe_allow_html=True)