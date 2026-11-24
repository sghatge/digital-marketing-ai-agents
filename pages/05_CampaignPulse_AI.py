from __future__ import annotations

import io
import json
import os
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from campaignpulse.engine import analyze_campaign
from campaignpulse.samples import SAMPLES
from campaignpulse.reasoning import explain_with_optional_gemini

st.set_page_config(page_title="CampaignPulse AI", page_icon="◈", layout="wide")

# ModletHub-inspired: editorial, practical, creator-attributed and workflow-first.
st.markdown("""
<style>
.block-container{max-width:1180px;padding-top:1.4rem;padding-bottom:3rem}
.hero{background:linear-gradient(118deg,#172554 0%,#263B65 55%,#B4533C 100%);color:#fff;border-radius:20px;padding:2rem 2.1rem;margin-bottom:1.1rem}
.hero .eyebrow{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:#FCD9C9;font-weight:700}
.hero h1{color:#fff;font-size:2.45rem;letter-spacing:-.04em;margin:.35rem 0}
.hero p{color:#F4EDE8;font-size:1.03rem;max-width:760px;margin:0}
.step{background:#fff;border:1px solid #E7E5E4;border-radius:14px;padding:1rem;height:100%}
.step b{display:block;color:#1C2A44;margin:.3rem 0}
.step span{font-size:.85rem;color:#64748B}
.kpi{background:#fff;border:1px solid #E7E5E4;border-radius:14px;padding:1rem 1.05rem}
.kpi .label{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:#64748B;font-weight:700}
.kpi .value{font-size:1.8rem;font-weight:800;color:#172554}
.kpi .sub{font-size:.75rem;color:#78716C}
.finding{border:1px solid #E7E5E4;border-radius:13px;padding:1rem;margin:.55rem 0;background:#fff}
.finding h4{margin:.1rem 0 .4rem;color:#1C2A44}
.smallmuted{color:#64748B;font-size:.83rem}
.stTabs [data-baseweb="tab-list"]{gap:.35rem}
.stTabs [data-baseweb="tab"]{border-radius:9px 9px 0 0;background:#F5F5F4;padding:.55rem .9rem}
.stTabs [aria-selected="true"]{background:#1E3A5F!important;color:white!important}
section[data-testid="stSidebar"]{background:#F7F5F1}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E7E5E4;padding:.8rem;border-radius:12px}
</style>
""", unsafe_allow_html=True)

def pct(value):
    return "—" if value is None else f"{value:.2f}%"

def make_markdown(data, result, mode):
    lines = [
        "# CampaignPulse AI — Campaign Health Report",
        f"**Campaign:** {data.get('campaign_name') or 'Unnamed campaign'}",
        f"**Source:** {data.get('metric_source', 'manual_entry')} · **Mode:** {mode}",
        f"**Send date:** {data.get('send_date') or 'Not supplied'} · **Reporting date:** {data.get('reporting_date') or 'Not supplied'}",
        f"**Overall health:** {result['overall_health']}",
        "",
        "## KPI summary",
        "| Metric | Result |",
        "|---|---:|",
    ]
    labels = {"delivery_rate":"Delivery rate","hard_bounce_rate":"Hard-bounce rate","soft_bounce_rate":"Soft-bounce rate",
              "total_bounce_rate":"Total bounce rate","open_rate":"Unique open rate","click_rate":"Unique CTR",
              "ctor":"CTOR","unsubscribe_rate":"Unsubscribe rate"}
    for key, label in labels.items():
        lines.append(f"| {label} | {pct(result['metrics'].get(key))} |")
    lines += ["", "## Findings"]
    if not result["findings"]:
        lines.append("No configured threshold breaches were detected. This does not guarantee deliverability or campaign success.")
    for item in result["findings"]:
        lines += [f"### {item['severity'].upper()}: {item['title']}", f"- Evidence: {item['evidence']}",
                  f"- Confidence: {item['confidence']}", "- Recommended ACC checks:"]
        lines += [f"  - {x}" for x in item["acc_operational_checks"]]
    lines += ["", "## Data-quality notes"]
    lines += [f"- {x}" for x in result["validation"]["warnings"] + result["validation"]["reviews"]]
    lines += ["", "## Priority actions"]
    lines += [f"{i}. {x}" for i, x in enumerate(result["priority_actions"], 1)]
    lines += ["", "---", "Created by CampaignPulse AI · Sangram Ghatge",
              "Standalone decision support. No Adobe Campaign instance was accessed. Verify recommendations in your own environment."]
    return "\n".join(lines)

def normalize_csv_row(row):
    data = {}
    for key in ["campaign_id","campaign_name","metric_source","send_date","reporting_date","campaign_type","audience_type","industry"]:
        value = row.get(key)
        if pd.notna(value):
            data[key] = str(value).strip()
    for key in ["sent","delivered","hard_bounces","soft_bounces","ignored_errors","other_errors","unique_opens","unique_clicks","unsubscribes"]:
        value = row.get(key)
        if pd.notna(value) and str(value).strip() != "":
            data[key] = int(float(value))
    return data

st.markdown("""
<div class="hero">
  <div class="eyebrow">Independent MarTech intelligence · Creator: Sangram Ghatge</div>
  <h1>CampaignPulse AI</h1>
  <p>Turn campaign numbers into a clear diagnosis and practical next steps. Built for Adobe Campaign practitioners, with no platform connection required.</p>
</div>
""", unsafe_allow_html=True)

s1,s2,s3=st.columns(3)
for col,number,title,desc in [
    (s1,"01","Bring the numbers","Paste aggregate metrics or upload a CSV."),
    (s2,"02","Understand the signal","Validate, calculate and diagnose with transparent rules."),
    (s3,"03","Decide what to check","Get prioritized Adobe Campaign operational checks.")
]:
    with col:
        st.markdown(f'<div class="step"><span>{number}</span><b>{title}</b><span>{desc}</span></div>',unsafe_allow_html=True)

st.caption("V1 · Standalone · Aggregate data only · Human approval required")
with st.sidebar:
    st.markdown("### Campaign input")
    scenario=st.selectbox("Start with a demo scenario",["Manual entry",*SAMPLES.keys()])
    base=SAMPLES.get(scenario,{})
    if scenario!="Manual entry":
        st.info("Fictional demonstration data. Selecting a scenario pre-fills the form.")
    source_options=["manual_entry","adobe_campaign_v8","adobe_campaign_v7","other_esp","synthetic_demo"]
    default_source=base.get("metric_source","manual_entry")
    metric_source=st.selectbox("Metric source",source_options,index=source_options.index(default_source))
    campaign_name=st.text_input("Campaign name",value=base.get("campaign_name",""))
    campaign_type=st.selectbox("Campaign type",["newsletter","promotional","transactional","lifecycle","re_engagement","other"],
                               index=["newsletter","promotional","transactional","lifecycle","re_engagement","other"].index(base.get("campaign_type","newsletter")))
    audience_type=st.selectbox("Audience type",["prospect","customer","mixed","unknown"],
                               index=["prospect","customer","mixed","unknown"].index(base.get("audience_type","unknown")))
    industry=st.text_input("Industry (optional)",value=base.get("industry",""))
    send_date=st.text_input("Send date (YYYY-MM-DD)",value=base.get("send_date",""))
    reporting_date=st.text_input("Reporting date (YYYY-MM-DD)",value=base.get("reporting_date",""))
    st.divider()
    st.caption("Use synthetic or sanitized aggregate metrics only. Do not paste recipient records, addresses, broadlogs, credentials or confidential client data.")

st.subheader("Campaign metrics")
st.caption("Required counts are marked *. All counts must be whole numbers and non-negative.")
with st.form("campaignpulse_metrics"):
    a,b,c=st.columns(3)
    with a:
        sent=st.number_input("Sent *",min_value=0,value=int(base.get("sent",25000)),step=100)
        delivered=st.number_input("Delivered *",min_value=0,value=int(base.get("delivered",24550)),step=100)
        hard_bounces=st.number_input("Hard bounces *",min_value=0,value=int(base.get("hard_bounces",180)),step=1)
    with b:
        soft_bounces=st.number_input("Soft bounces *",min_value=0,value=int(base.get("soft_bounces",270)),step=1)
        unique_opens=st.number_input("Unique opens *",min_value=0,value=int(base.get("unique_opens",6150)),step=10)
        unique_clicks=st.number_input("Unique clicks *",min_value=0,value=int(base.get("unique_clicks",780)),step=10)
    with c:
        unsubscribes=st.number_input("Unsubscribes *",min_value=0,value=int(base.get("unsubscribes",95)),step=1)
        other_errors=st.number_input("Other errors",min_value=0,value=int(base.get("other_errors",0)),step=1)
        ignored_errors=st.number_input("Ignored errors",min_value=0,value=int(base.get("ignored_errors",0)),step=1)
    tolerance_count=st.number_input("Reconciliation tolerance (count)",min_value=0,value=10,step=1)
    tolerance_percentage=st.number_input("Reconciliation tolerance (%)",min_value=0.0,max_value=10.0,value=0.5,step=0.1)
    submitted=st.form_submit_button("Analyse campaign",type="primary",use_container_width=True)

st.divider()
st.subheader("Or analyse a CSV")
st.caption("One campaign per row. Select a row after upload. Required columns: sent, delivered, hard_bounces, soft_bounces, unique_opens, unique_clicks, unsubscribes.")
uploaded=st.file_uploader("Upload campaign CSV",type=["csv"],key="campaignpulse_csv")
csv_data=None
if uploaded:
    try:
        frame=pd.read_csv(uploaded)
        required={"sent","delivered","hard_bounces","soft_bounces","unique_opens","unique_clicks","unsubscribes"}
        missing=required-set(frame.columns)
        if missing:
            st.error("Missing required CSV columns: "+", ".join(sorted(missing)))
        elif frame.empty:
            st.warning("The uploaded CSV contains no campaign rows.")
        else:
            selected=st.selectbox("Select campaign row",range(len(frame)),format_func=lambda i:f"Row {i+1}: "+str(frame.iloc[i].get("campaign_name","Unnamed campaign")))
            csv_data=normalize_csv_row(frame.iloc[selected].to_dict())
            st.success(f"Loaded {len(frame)} campaign row(s). Analysing row {selected+1}.")
            st.download_button("Download CSV template",data="campaign_name,metric_source,send_date,reporting_date,campaign_type,audience_type,industry,sent,delivered,hard_bounces,soft_bounces,other_errors,ignored_errors,unique_opens,unique_clicks,unsubscribes\nSpring Newsletter,synthetic_demo,2026-11-10,2026-11-18,newsletter,customer,Retail,25000,24550,180,270,0,0,6150,780,95\n",
                               file_name="campaignpulse_template.csv",mime="text/csv")
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")
else:
    st.download_button("Download CSV template",data="campaign_name,metric_source,send_date,reporting_date,campaign_type,audience_type,industry,sent,delivered,hard_bounces,soft_bounces,other_errors,ignored_errors,unique_opens,unique_clicks,unsubscribes\nSpring Newsletter,synthetic_demo,2026-11-10,2026-11-18,newsletter,customer,Retail,25000,24550,180,270,0,0,6150,780,95\n",
                       file_name="campaignpulse_template.csv",mime="text/csv")

if submitted or csv_data:
    if csv_data:
        data={**csv_data,"metric_source":csv_data.get("metric_source","manual_entry")}
        mode="CSV upload"
    else:
        data={
            "campaign_name":campaign_name,"metric_source":metric_source,"campaign_type":campaign_type,
            "audience_type":audience_type,"industry":industry,"send_date":send_date or None,
            "reporting_date":reporting_date or None,"sent":sent,"delivered":delivered,
            "hard_bounces":hard_bounces,"soft_bounces":soft_bounces,"other_errors":other_errors,
            "ignored_errors":ignored_errors,"unique_opens":unique_opens,"unique_clicks":unique_clicks,
            "unsubscribes":unsubscribes,"tolerance_count":tolerance_count,
            "tolerance_percentage":tolerance_percentage,
        }
        mode="Manual entry"
    result=analyze_campaign(data)
    if not result["valid"]:
        st.error("Please correct the following input errors before analysis.")
        for error in result["validation"]["errors"]:
            st.write("• "+error)
    else:
        st.session_state["campaignpulse_last"]={"data":data,"result":result,"mode":mode}
        st.rerun()

if "campaignpulse_last" in st.session_state:
    saved=st.session_state["campaignpulse_last"]
    data,result,mode=saved["data"],saved["result"],saved["mode"]
    st.divider()
    st.subheader("Campaign health assessment")
    health=result["overall_health"]
    if health=="Healthy": st.success("Healthy · No configured threshold breaches detected.")
    elif health=="Watch": st.info("Watch · Review the observations and continue monitoring.")
    elif health=="At risk": st.warning("At risk · Multiple configured thresholds need attention.")
    else: st.error("Critical · One or more critical thresholds were breached.")
    st.caption("This classification uses configurable starter thresholds. It is not an industry benchmark or delivery guarantee.")
    labels=[("Delivery rate","delivery_rate"),("Open rate","open_rate"),("Unique CTR","click_rate"),("Hard bounce","hard_bounce_rate"),("Soft bounce","soft_bounce_rate"),("Unsubscribe","unsubscribe_rate")]
    cols=st.columns(3)
    for i,(label,key) in enumerate(labels):
        with cols[i%3]:
            st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{pct(result["metrics"].get(key))}</div><div class="sub">Calculated from supplied counts</div></div>',unsafe_allow_html=True)
    st.markdown("#### Complete KPI breakdown")
    metric_labels={"delivery_rate":"Delivery rate","hard_bounce_rate":"Hard-bounce rate","soft_bounce_rate":"Soft-bounce rate",
                   "total_bounce_rate":"Total bounce rate","open_rate":"Unique open rate","click_rate":"Unique CTR",
                   "ctor":"Click-to-open rate","unsubscribe_rate":"Unsubscribe rate"}
    kdf=pd.DataFrame([{"Metric":v,"Rate":pct(result["metrics"].get(k))} for k,v in metric_labels.items()])
    st.dataframe(kdf,use_container_width=True,hide_index=True)
    warnings=result["validation"]["warnings"]
    reviews=result["validation"]["reviews"]
    if warnings or reviews:
        with st.expander(f"Data-quality notes ({len(warnings)+len(reviews)})",expanded=True):
            for item in warnings: st.warning(item)
            for item in reviews: st.info(item)
    st.markdown("#### Diagnostic findings")
    if not result["findings"]:
        st.success("No configured threshold breaches were detected. This does not guarantee campaign success.")
    for item in result["findings"]:
        icon="🔴" if item["severity"]=="critical" else "🟠"
        st.markdown(f'<div class="finding"><h4>{icon} {item["title"]}</h4><div>{item["evidence"]}</div><div class="smallmuted">Evidence: observed in supplied data · Confidence: {item["confidence"]}</div></div>',unsafe_allow_html=True)
        with st.expander("Possible explanations and Adobe Campaign checks"):
            for cause in item["possible_explanations"]: st.write("Possible explanation: "+cause)
            for check in item["acc_operational_checks"]: st.write("☐ "+check)
            st.caption(item["verification_boundary"])
    st.markdown("#### Prioritized next actions")
    if result["priority_actions"]:
        for i,action in enumerate(result["priority_actions"],1):
            st.write(f"**{i}.** {action}")
    else:
        st.write("Continue monitoring and compare against a verified historical baseline.")
    st.markdown("#### Optional AI explanation")
    secret_key = os.getenv("GEMINI_API_KEY", "")
    try:
        secret_key = secret_key or st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass
    if secret_key:
        if st.button("Generate AI explanation", key="campaignpulse_ai_explain"):
            with st.spinner("Generating a bounded explanation from aggregate metrics..."):
                explanation = explain_with_optional_gemini(result, api_key=secret_key)
            if explanation:
                st.session_state["campaignpulse_ai_explanation"] = explanation
            else:
                st.warning("The optional model was unavailable. The deterministic report remains complete.")
        if st.session_state.get("campaignpulse_ai_explanation"):
            st.markdown(st.session_state["campaignpulse_ai_explanation"])
        st.caption("Optional Gemini explanation. It cannot change calculated metrics, evidence, severity or recommended checks.")
    else:
        st.info("Optional AI narrative is not configured. Deterministic analysis, findings and reports work without an API key. Add GEMINI_API_KEY to Streamlit secrets only if you want to enable model-generated explanations.")
    mode_view=st.radio("Report view",["Practitioner","Management"],horizontal=True,key="campaignpulse_report_mode")
    if mode_view=="Management":
        st.markdown("**Executive summary**")
        st.write(f"{data.get('campaign_name') or 'This campaign'} has a **{health.lower()}** assessment based on the supplied aggregate metrics. "
                 f"{len(result['findings'])} threshold finding(s) were identified. The recommended focus is to verify the highest-priority operational checks before the next comparable send.")
    else:
        st.markdown("**Practitioner checklist**")
        for action in result["priority_actions"]:
            st.checkbox(action,key="cp_action_"+str(abs(hash(action))))
    report=make_markdown(data,result,mode_view)
    st.download_button("Download campaign report (.md)",data=report,file_name="campaignpulse_campaign_report.md",mime="text/markdown",type="primary")
    payload={"schema_version":"1.1","input":data,"analysis":result,"report_mode":mode_view,"creator":"Sangram Ghatge"}
    st.download_button("Download analysis JSON",data=json.dumps(payload,indent=2,default=str),file_name="campaignpulse_analysis.json",mime="application/json")
    st.caption("CampaignPulse AI is standalone. It has not accessed, verified or changed your Adobe Campaign environment. Validate findings in your own instance.")
