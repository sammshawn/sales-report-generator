"""
Landing Page — Sales Report Generator (Premium v3)
===================================================
Beautiful, animated landing page with sidebar hidden. Entry point for the app.
Includes: hero, trust strip, features, how-it-works, pricing, and a
clarifying note about the free trial + paid monthly service.
"""

import streamlit as st

st.set_page_config(
    page_title="Sales Report Generator — Turn CSVs Into Client-Ready Reports",
    page_icon="📊",
    layout="wide",
)

# ============================================================
# HIDE STREAMLIT CHROME + CUSTOM STYLES
# ============================================================
st.markdown("""
<style>
    /* Hide sidebar + its toggle button */
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"],
    section[data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
    }
    /* Hide top header bar */
    [data-testid="stHeader"] { display: none !important; }
    /* Hide the "Made with Streamlit" footer */
    footer { visibility: hidden; }
    /* Widen the main container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* ---------- ANIMATIONS ---------- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50%      { transform: translateY(-10px); }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 8px 24px rgba(31,78,120,0.35); }
        50%      { transform: scale(1.03); box-shadow: 0 12px 32px rgba(31,78,120,0.5); }
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ---------- HERO ---------- */
    .hero {
        background: linear-gradient(-45deg, #0F2E4F, #1F4E78, #2E75B6, #1F4E78);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 5rem 2rem 4rem 2rem;
        border-radius: 24px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 20px 60px rgba(15,46,79,0.35);
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: "";
        position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
        animation: float 8s ease-in-out infinite;
    }
    .hero h1 {
        font-size: 3.5rem; margin: 0 0 1rem 0; font-weight: 800;
        animation: fadeInUp 0.8s ease both;
        letter-spacing: -0.02em;
        position: relative; z-index: 1;
    }
    .hero .subtitle {
        font-size: 1.35rem; opacity: 0.95; margin: 0 0 2.5rem 0;
        animation: fadeInUp 0.8s ease 0.15s both;
        max-width: 720px; margin-left: auto; margin-right: auto;
        position: relative; z-index: 1;
    }
    .hero .badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        padding: 0.4rem 1rem; border-radius: 100px;
        font-size: 0.85rem; font-weight: 600;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        animation: fadeInUp 0.8s ease both;
        position: relative; z-index: 1;
    }
    .cta {
        display: inline-block;
        background: linear-gradient(135deg, #FFD93D, #FFB800);
        color: #0F2E4F;
        padding: 1.1rem 3rem;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.15rem;
        text-decoration: none;
        animation: pulse 2.5s ease-in-out infinite, fadeInUp 0.8s ease 0.3s both;
        position: relative; z-index: 1;
        transition: transform 0.2s ease;
    }
    .cta:hover { transform: translateY(-3px) scale(1.02); color: #0F2E4F; }
    .cta-secondary {
        display: inline-block;
        background: #1F4E78; color: white;
        padding: 1rem 2.5rem;
        border-radius: 12px;
        font-weight: 700; font-size: 1.05rem;
        text-decoration: none;
        box-shadow: 0 8px 24px rgba(31,78,120,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .cta-secondary:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(31,78,120,0.45);
        color: white;
    }

    /* ---------- SECTION TITLES ---------- */
    .section-title {
        text-align: center;
        font-size: 2.2rem; font-weight: 800;
        color: #0F2E4F;
        margin: 3rem 0 0.5rem 0;
        animation: fadeInUp 0.6s ease both;
        letter-spacing: -0.02em;
    }
    .section-subtitle {
        text-align: center;
        font-size: 1.1rem; color: #64748B;
        margin: 0 0 2.5rem 0;
        animation: fadeInUp 0.6s ease 0.1s both;
    }

    /* ---------- FEATURE CARDS ---------- */
    .feature {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
        padding: 2rem 1.75rem;
        border-radius: 16px;
        border: 1px solid #E5E9F0;
        height: 100%;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease both;
    }
    .feature:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 40px rgba(31,78,120,0.15);
        border-color: #2E75B6;
    }
    .feature .icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }
    .feature h3 {
        color: #0F2E4F; margin: 0 0 0.6rem 0; font-size: 1.25rem;
        font-weight: 700;
    }
    .feature p { color: #475569; margin: 0; font-size: 0.98rem; line-height: 1.6; }

    /* ---------- STEP CARDS ---------- */
    .step-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 16px;
        border: 1px solid #E5E9F0;
        height: 100%;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        text-align: center;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease both;
        position: relative;
    }
    .step-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 40px rgba(31,78,120,0.12);
    }
    .step-card .num {
        background: linear-gradient(135deg, #1F4E78, #2E75B6);
        color: white;
        border-radius: 50%;
        width: 48px; height: 48px;
        display: inline-flex;
        align-items: center; justify-content: center;
        font-weight: 800; font-size: 1.3rem;
        margin: 0 auto 1.25rem auto;
        box-shadow: 0 6px 16px rgba(31,78,120,0.3);
    }
    .step-card h4 {
        color: #0F2E4F; margin: 0 0 0.5rem 0;
        font-size: 1.15rem; font-weight: 700;
    }
    .step-card p { color: #64748B; margin: 0; font-size: 0.95rem; line-height: 1.5; }

    /* ---------- PRICING ---------- */
    .pricing {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        border: 2px solid #E5E9F0;
        text-align: center;
        height: 100%;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease both;
    }
    .pricing:hover {
        border-color: #2E75B6;
        transform: translateY(-6px);
        box-shadow: 0 20px 50px rgba(31,78,120,0.15);
    }
    .pricing h3 { color: #0F2E4F; margin: 0 0 0.5rem 0; font-size: 1.3rem; }
    .pricing .price {
        font-size: 2.5rem; color: #1F4E78; font-weight: 800; margin: 1.25rem 0;
        background: linear-gradient(135deg, #1F4E78, #2E75B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .pricing ul {
        text-align: left; color: #475569; padding-left: 0;
        list-style: none; margin: 1.5rem 0;
    }
    .pricing li {
        margin-bottom: 0.7rem; font-size: 0.95rem;
        padding-left: 1.75rem; position: relative;
    }
    .pricing li::before {
        content: "✓"; position: absolute; left: 0;
        color: #16A34A; font-weight: 800;
    }

    /* ---------- TRUST STRIP ---------- */
    .trust-strip {
        display: flex; justify-content: center; gap: 2.5rem;
        flex-wrap: wrap; padding: 1.5rem 0;
        color: #64748B; font-size: 0.95rem;
    }
    .trust-strip span { display: flex; align-items: center; gap: 0.5rem; }

    /* ---------- CLARIFYING NOTE ---------- */
    .pricing-note {
        background: linear-gradient(135deg, #F0F9FF, #E0F2FE);
        border-left: 4px solid #2E75B6;
        padding: 1.25rem 1.75rem;
        border-radius: 12px;
        margin: 1.5rem auto 3rem auto;
        max-width: 900px;
        text-align: center;
        color: #0F2E4F;
        font-size: 1rem;
        line-height: 1.6;
        animation: fadeInUp 0.6s ease both;
        box-shadow: 0 4px 16px rgba(31,78,120,0.08);
    }
    .pricing-note strong { color: #1F4E78; }
    .pricing-note a {
        color: #1F4E78; font-weight: 700;
        text-decoration: none; border-bottom: 2px solid #2E75B6;
    }

    /* ---------- FOOTER ---------- */
    .footer {
        text-align: center; color: #94A3B8; font-size: 0.85rem;
        padding: 3rem 0 1rem 0; border-top: 1px solid #E5E9F0;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero">
    <div class="badge">⚡ 30-Second Reports</div>
    <h1>📊 Sales Report Generator</h1>
    <p class="subtitle">
        Turn your messy sales CSV into a polished, client-ready report.
        Excel + PDF, with charts, insights, and KPIs — automatically.
    </p>
    <a class="cta" href="/Generator" target="_self">🚀 Try It Free →</a>
</div>
""", unsafe_allow_html=True)

# ============================================================
# TRUST STRIP
# ============================================================
st.markdown("""
<div class="trust-strip">
    <span>✅ No sign-up required</span>
    <span>✅ Works with any CSV</span>
    <span>✅ Excel + PDF output</span>
    <span>✅ 100% free to try</span>
</div>
""", unsafe_allow_html=True)

# ============================================================
# FEATURES
# ============================================================
st.markdown('<div class="section-title">Stop Wasting Hours in Excel</div>',
            unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Every month you rebuild the same report. Let this do it in 30 seconds.</div>',
            unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="feature">
        <div class="icon">⚡</div>
        <h3>Instant Reports</h3>
        <p>Upload any sales CSV. Get a formatted multi-sheet Excel + PDF in seconds — no formulas, no formatting.</p>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="feature">
        <div class="icon">🧠</div>
        <h3>Smart Auto-Detection</h3>
        <p>"Invoice No", "Order Date", "Qty", "Total" — the tool figures out your columns automatically.</p>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="feature">
        <div class="icon">📈</div>
        <h3>Real Insights</h3>
        <p>Monthly trends, top products, top customers, growth %. Plain-English highlights that explain the numbers.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================
# HOW IT WORKS
# ============================================================
st.markdown('<div class="section-title">How It Works</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Three steps. Under one minute.</div>',
            unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown("""
    <div class="step-card">
        <div class="num">1</div>
        <h4>Enter business name</h4>
        <p>Used as the report header. Takes 5 seconds.</p>
    </div>
    """, unsafe_allow_html=True)
with s2:
    st.markdown("""
    <div class="step-card">
        <div class="num">2</div>
        <h4>Upload your CSV</h4>
        <p>From Shopify, POS, Excel, Google Sheets — anything works.</p>
    </div>
    """, unsafe_allow_html=True)
with s3:
    st.markdown("""
    <div class="step-card">
        <div class="num">3</div>
        <h4>Download report</h4>
        <p>Get Excel + PDF. Share with your team, accountant, or investors.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================
# PRICING
# ============================================================
st.markdown('<div class="section-title">Simple Pricing</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Start free. Upgrade when you love it.</div>',
            unsafe_allow_html=True)

p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("""
    <div class="pricing">
        <h3>Free Trial</h3>
        <div class="price">Free</div>
        <ul>
            <li>1 report</li>
            <li>Excel + PDF output</li>
            <li>All charts & insights</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
with p2:
    st.markdown("""
    <div class="pricing" style="border-color:#2E75B6; box-shadow: 0 12px 40px rgba(31,78,120,0.18);">
        <h3>Starter</h3>
        <div class="price">KES 3,000<span style="font-size:1rem;">/mo</span></div>
        <ul>
            <li>Up to 5 reports/month</li>
            <li>Excel + PDF</li>
            <li>Custom brand color</li>
            <li>Email support</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
with p3:
    st.markdown("""
    <div class="pricing">
        <h3>Pro</h3>
        <div class="price">KES 6,000<span style="font-size:1rem;">/mo</span></div>
        <ul>
            <li>Unlimited reports</li>
            <li>Multi-branch support</li>
            <li>Priority support</li>
            <li>Custom branding</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# CLARIFYING NOTE — free trial vs paid service
# ============================================================
st.markdown("""
<div class="pricing-note">
    💡 <strong>How it works:</strong> Try the tool once for <strong>free</strong>.
    When you're ready for unlimited monthly reports, we run them for you —
    <strong>done-for-you from KES 3,000/month</strong>.
    WhatsApp <a href="https://wa.me/254723161563" target="_blank">+254 723 161 563</a>
    or email <a href="mailto:sammshawn1@gmail.com">sammshawn1@gmail.com</a>
    to get started.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# FINAL CTA
# ============================================================
st.markdown("""
<div style='text-align:center; padding: 2rem 0;'>
    <div style='font-size:1.6rem; color:#0F2E4F; font-weight:800; margin-bottom:1rem;'>
        Ready to save hours every month?
    </div>
    <a class="cta-secondary" href="/Generator" target="_self">
        Generate My First Report →
    </a>
</div>
""", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    Sales Report Generator — Built for small businesses that hate Excel.
</div>
""", unsafe_allow_html=True)
