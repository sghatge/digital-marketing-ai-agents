import json
import os
import html
import pandas as pd
import streamlit as st
from agents import analyze_metrics, build_content, build_strategy, check_campaign_qa, enhance_with_ai

st.set_page_config(page_title="Digital Marketing AI Lab", page_icon="✦", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1240px; padding-top: 2rem; padding-bottom: 3rem;}
.hero {padding: 1.5rem 1.7rem; border: 1px solid rgba(128,128,128,.25); border-radius: 18px; margin-bottom: 1rem;}
.eyebrow {font-size: .76rem; letter-spacing: .14em; text-transform: uppercase; opacity: .72;}
.metric-card {border: 1px solid rgba(128,128,128,.25); border-radius: 14px; padding: 1rem; min-height: 100px;}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="eyebrow">A practical multi-agent marketing prototype</div><h1>Digital Marketing AI Lab</h1><p>One brief in. Strategy, content, campaign checks, and performance insights out.</p></div>', unsafe_allow_html=True)

api_ready = bool(os.getenv("GEMINI_API_KEY", "").strip())
st.caption("AI-assisted copy is optional. Without an API key, the core demo runs locally using built-in workflows.")
if api_ready:
    st.success("Optional AI key detected. Review all generated output before use.")
else:
    st.info("Demo mode is ready. No API key or external account is required.")

with st.sidebar:
    st.header("Campaign brief")
    brand = st.text_input("Brand / project", "BrightPath", help="Use a fictional brand for public demos.")
    goal = st.text_input("Business goal", "Increase qualified website enquiries")
    audience = st.text_input("Target audience", "Small business owners exploring digital marketing")
    channel = st.selectbox("Primary channel", ["LinkedIn", "Email", "Instagram", "Paid search", "Multi-channel"])
    voice = st.selectbox("Brand voice", ["Clear and helpful", "Expert and practical", "Bold and energetic", "Warm and conversational"])
    budget = st.number_input("Campaign budget (optional)", min_value=0.0, value=500.0, step=50.0)
    st.divider()
    st.markdown("**Responsible-use rules**")
    st.caption("Use synthetic data. Verify claims and links. Human approval is required before publishing or spending.")

strategy = build_strategy(brand, goal, audience, channel, budget, voice)
content = build_content(brand, goal, audience, channel, voice)
tab1, tab2, tab3, tab4 = st.tabs(["01 · Strategy", "02 · Content Studio", "03 · Campaign QA", "04 · Performance Analyst"])

with tab1:
    st.subheader("Agent 1 — Campaign Strategist")
    c1, c2, c3 = st.columns(3)
    c1.metric("Primary channel", channel)
    c2.metric("Budget input", f"{budget:,.2f}", help="Currency is not specified.")
    c3.metric("Content pillars", len(strategy["content_pillars"]))
    st.markdown("#### Campaign blueprint")
    st.write("**Campaign:**", strategy["campaign_name"])
    st.write("**Objective:**", strategy["objective"])
    st.write("**Audience:**", strategy["audience"])
    st.write("**Core message:**", strategy["core_message"])
    st.write("**Content pillars**")
    for item in strategy["content_pillars"]: st.write("•", item)
    st.write("**Test plan**")
    for item in strategy["test_plan"]: st.write("•", item)
    st.write("**Suggested metrics:**", ", ".join(strategy["success_metrics"]))
    st.warning("No baseline or uplift data was supplied. Set numeric targets only after checking historical results.")
    if st.button("Enhance strategy and content with AI", type="primary"):
        with st.spinner("Preparing draft..."):
            st.session_state["ai_result"] = enhance_with_ai(brand, goal, audience, channel, voice)
    if "ai_result" in st.session_state:
        st.caption(st.session_state["ai_result"]["mode"])
        st.json(st.session_state["ai_result"])
    st.download_button("Download strategy JSON", json.dumps(strategy, indent=2), "campaign_strategy.json", "application/json")

with tab2:
    st.subheader("Agent 2 — Content Studio")
    st.write("Create editable drafts for a marketer to review.")
    post = st.text_area("Editable social post", content["social_post"], height=220)
    subjects = st.text_area("Email subject lines (one per line)", "\n".join(content["email_subjects"]), height=110)
    st.write("**Suggested call to action:**", content["cta"])
    st.caption(content["note"])
    st.download_button("Download content pack", json.dumps({"social_post": post, "email_subjects": subjects.splitlines(), "cta": content["cta"]}, indent=2), "content_pack.json", "application/json")

with tab3:
    st.subheader("Agent 3 — Campaign QA")
    st.write("Checks URL format, UTM field completeness, content presence, and common absolute-claim phrases.")
    with st.form("qa_form"):
        website_url = st.text_input("Brand website URL", "https://example.com")
        destination_url = st.text_input("Campaign destination URL", "https://example.com/offer")
        q1, q2, q3 = st.columns(3)
        utm_source = q1.text_input("UTM source", channel.lower().replace(" ", "_"))
        utm_medium = q2.text_input("UTM medium", "social" if channel == "LinkedIn" else channel.lower().replace(" ", "_"))
        utm_campaign = q3.text_input("UTM campaign", "brightpath_growth_sprint")
        qa_copy = st.text_area("Copy to review", content["social_post"], height=130)
        run_qa = st.form_submit_button("Run QA checks", type="primary")
    if run_qa:
        st.session_state["qa_checks"] = check_campaign_qa(website_url, destination_url, utm_source, utm_medium, utm_campaign, qa_copy)
    if "qa_checks" in st.session_state:
        checks = st.session_state["qa_checks"]
        passed = sum(x["status"] == "PASS" for x in checks)
        st.metric("Basic checks passed", f"{passed}/{len(checks)}")
        st.dataframe(pd.DataFrame(checks), use_container_width=True, hide_index=True)
        st.caption("PASS means a basic local check only. Links are not opened, tracking is not verified, and this is not legal or brand approval.")
        st.download_button("Download QA report", json.dumps(checks, indent=2), "campaign_qa_report.json", "application/json")

with tab4:
    st.subheader("Agent 4 — Performance Analyst")
    st.write("Calculate transparent baseline metrics from synthetic or aggregate campaign data.")
    with st.form("metrics_form"):
        left, right = st.columns(2)
        sent = left.number_input("Sent / reached", min_value=0, value=10000, step=100)
        delivered = left.number_input("Delivered / valid reach", min_value=0, value=9800, step=100)
        clicks = left.number_input("Clicks (unique or total—clarify in your report)", min_value=0, value=350, step=10)
        conversions = right.number_input("Conversions", min_value=0, value=45, step=1)
        spend = right.number_input("Spend (currency unspecified)", min_value=0.0, value=500.0, step=25.0)
        run_metrics = st.form_submit_button("Analyze performance", type="primary")
    if run_metrics:
        st.session_state["metrics_result"] = analyze_metrics(sent, delivered, clicks, conversions, spend)
    if "metrics_result" in st.session_state:
        result = st.session_state["metrics_result"]
        cols = st.columns(4)
        values = [
            ("Delivery rate", result["delivery_rate_pct"], "%"),
            ("CTR (approx.)", result["click_through_rate_pct"], "%"),
            ("Conversion rate", result["conversion_rate_pct"], "%"),
            ("Cost / conversion", result["cost_per_conversion"], "")
        ]
        for col, (label, value, suffix) in zip(cols, values):
            col.metric(label, f"{value:,.2f}{suffix}" if value is not None else "N/A")
        st.markdown("#### Data-quality notes")
        for note in result["data_quality_notes"]: st.write("•", note)
        st.caption("Arithmetic only: validate event definitions, deduplication, attribution, and reporting window.")
        st.download_button("Download analysis JSON", json.dumps(result, indent=2), "performance_analysis.json", "application/json")

st.divider()
st.markdown("**Prototype status:** Strategy, content drafts, basic QA, and KPI calculations are available. No campaigns are sent, published, or changed automatically.")
st.caption("Use fictional or sanitized data. Never commit API keys or customer data.")
