import json
import os
import html
import pandas as pd
import streamlit as st
from agents import analyze_metrics, build_content, build_strategy, check_campaign_qa, enhance_with_ai

st.set_page_config(page_title="Digital Marketing AI Lab", page_icon="✦", layout="wide")

# ---------------------------------------------------------------- palette
AGENTS = {
    "strategy": {"num": "01", "icon": "🧭", "name": "Campaign Strategist", "color": "#4F46E5", "soft": "#EEF0FF"},
    "content": {"num": "02", "icon": "✍️", "name": "Content Studio", "color": "#DB2777", "soft": "#FDEEF6"},
    "qa": {"num": "03", "icon": "🛡️", "name": "Campaign QA", "color": "#0D9488", "soft": "#E6F7F5"},
    "perf": {"num": "04", "icon": "📈", "name": "Performance Analyst", "color": "#D97706", "soft": "#FEF4E6"},
}

st.markdown("""
<style>
.block-container {max-width: 1240px; padding-top: 1.6rem; padding-bottom: 3rem;}
h1, h2, h3, h4 {letter-spacing: -0.01em;}
.hero {background: linear-gradient(120deg, #312E81 0%, #6D28D9 45%, #DB2777 100%); color: #fff;
       border-radius: 22px; padding: 2rem 2.2rem 1.7rem; margin-bottom: 1.2rem; box-shadow: 0 12px 30px rgba(76,29,149,.25);}
.hero h1 {color: #fff; margin: .2rem 0 .4rem; font-size: 2.4rem; padding: 0;}
.hero p {color: rgba(255,255,255,.88); font-size: 1.05rem; margin: 0;}
.hero .eyebrow {font-size: .74rem; letter-spacing: .16em; text-transform: uppercase; color: rgba(255,255,255,.75);}
.steps {display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; margin-top: 1.3rem;}
.step {background: rgba(255,255,255,.13); border: 1px solid rgba(255,255,255,.22); border-radius: 14px; padding: .8rem 1rem;}
.step b {display: block; font-size: .95rem; color: #fff;}
.step span {font-size: .85rem; color: rgba(255,255,255,.82);}
.step .n {display: inline-block; background: #fff; color: #6D28D9; font-weight: 800; border-radius: 999px;
          width: 1.6rem; height: 1.6rem; line-height: 1.6rem; text-align: center; margin-bottom: .35rem; font-size: .8rem;}
.agents {display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin: .2rem 0 1.2rem;}
.agent {background: #fff; border-radius: 16px; padding: 1rem 1.05rem; border: 1px solid #ECEBFA; border-top: 5px solid var(--c);
        box-shadow: 0 4px 14px rgba(30,27,75,.06);}
.agent .ic {font-size: 1.5rem;}
.agent .nm {font-weight: 700; color: #1E1B4B; margin: .25rem 0 .2rem;}
.agent .ds {font-size: .84rem; color: #4B5070; min-height: 2.6rem;}
.agent .io {font-size: .74rem; margin-top: .55rem; color: var(--c); font-weight: 600;}
.banner {border-radius: 16px; padding: 1.1rem 1.3rem; margin-bottom: 1rem; background: var(--s); border-left: 6px solid var(--c);}
.banner .t {font-size: 1.35rem; font-weight: 800; color: #1E1B4B;}
.banner .t small {color: var(--c); font-size: .8rem; letter-spacing: .12em; margin-right: .5rem;}
.banner .row {display: grid; grid-template-columns: repeat(3, 1fr); gap: .9rem; margin-top: .7rem;}
.banner .lab {font-size: .7rem; text-transform: uppercase; letter-spacing: .12em; color: var(--c); font-weight: 700;}
.banner .val {font-size: .88rem; color: #33365A;}
.card {background: #fff; border: 1px solid #ECEBFA; border-radius: 14px; padding: 1rem 1.1rem; height: 100%;
       box-shadow: 0 3px 10px rgba(30,27,75,.04);}
.card .k {font-size: .7rem; text-transform: uppercase; letter-spacing: .12em; color: #8A8FB0; font-weight: 700;}
.card .v {font-size: 1rem; color: #1E1B4B; font-weight: 600; margin-top: .2rem;}
.big-msg {background: linear-gradient(90deg, #EEF0FF, #F7F0FF); border-radius: 14px; padding: 1rem 1.2rem;
          font-size: 1.08rem; color: #312E81; font-weight: 600; border: 1px dashed #A5B4FC; margin: .6rem 0 1rem;}
.pillar {border-radius: 14px; padding: .9rem 1rem; color: #fff; font-weight: 600; min-height: 84px;}
.pillar small {display: block; opacity: .8; font-weight: 500; font-size: .72rem; letter-spacing: .1em; text-transform: uppercase;}
.tl {border-left: 3px solid #C7D2FE; margin-left: .6rem; padding-left: 1.1rem;}
.tl div {position: relative; margin-bottom: .75rem; color: #33365A;}
.tl div:before {content: attr(data-n); position: absolute; left: -2.05rem; top: -.05rem; background: #4F46E5; color: #fff;
                width: 1.5rem; height: 1.5rem; border-radius: 999px; text-align: center; font-size: .75rem; line-height: 1.5rem; font-weight: 700;}
.post {background: #fff; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1rem 1.1rem; box-shadow: 0 4px 14px rgba(0,0,0,.05);}
.post .who {display: flex; align-items: center; gap: .6rem; margin-bottom: .7rem;}
.post .av {width: 2.4rem; height: 2.4rem; border-radius: 999px; background: linear-gradient(135deg,#DB2777,#7C3AED);
           color: #fff; font-weight: 800; display: flex; align-items: center; justify-content: center;}
.post .nm {font-weight: 700; color: #111827; font-size: .92rem;} .post .sub {font-size: .74rem; color: #6B7280;}
.post .body {color: #1F2937; font-size: .92rem; line-height: 1.5;}
.inbox {background: #fff; border: 1px solid #E5E7EB; border-radius: 12px; overflow: hidden;}
.inbox div {padding: .65rem .9rem; border-bottom: 1px solid #F1F1F5; font-size: .9rem; color: #1F2937;}
.inbox div b {color: #DB2777; margin-right: .5rem;}
.chk {display: flex; gap: .8rem; align-items: flex-start; background: #fff; border: 1px solid #ECEBFA; border-radius: 12px;
      padding: .7rem .9rem; margin-bottom: .5rem;}
.pill {font-size: .7rem; font-weight: 800; letter-spacing: .08em; border-radius: 999px; padding: .2rem .65rem; white-space: nowrap;}
.pass {background: #DCFCE7; color: #166534;} .review {background: #FEF3C7; color: #92400E;}
.chk .nm {font-weight: 700; color: #1E1B4B; font-size: .92rem;} .chk .dt {font-size: .84rem; color: #4B5070;}
.kpi {background: #fff; border-radius: 16px; padding: 1rem 1.1rem; border: 1px solid #F5E6CF; border-top: 5px solid #D97706;}
.kpi .k {font-size: .72rem; text-transform: uppercase; letter-spacing: .1em; color: #92400E; font-weight: 700;}
.kpi .v {font-size: 1.8rem; font-weight: 800; color: #1E1B4B;} .kpi .f {font-size: .74rem; color: #6B7280;}
.kpi {margin-bottom: 1.2rem;}
.funnel div.bar {height: 2.1rem; border-radius: 10px; margin: .35rem 0; color: #fff; font-weight: 700; font-size: .85rem;
                 display: flex; align-items: center; padding: 0 .8rem; white-space: nowrap; min-width: 8.5rem;}
.note {background: #F8F7FF; border-radius: 12px; padding: .7rem .9rem; font-size: .86rem; color: #3F3D66; margin-bottom: .4rem;}
.stTabs [data-baseweb="tab-list"] {gap: .4rem;}
.stTabs [data-baseweb="tab"] {background: #F1EEFF; border-radius: 12px 12px 0 0; padding: .55rem 1rem; font-weight: 600;}
.stTabs [aria-selected="true"] {background: #6D28D9 !important; color: #fff !important;}
section[data-testid="stSidebar"] {background: linear-gradient(180deg, #F5F3FF 0%, #FDF2F8 100%);}
@media (max-width: 900px) {.agents, .steps, .banner .row {grid-template-columns: 1fr;}}
</style>
""", unsafe_allow_html=True)

e = html.escape


def banner(key, what, gives, gets):
    a = AGENTS[key]
    st.markdown(
        f'<div class="banner" style="--c:{a["color"]};--s:{a["soft"]}">'
        f'<div class="t"><small>AGENT {a["num"]}</small>{a["icon"]} {a["name"]}</div>'
        f'<div class="row"><div><div class="lab">What it does</div><div class="val">{what}</div></div>'
        f'<div><div class="lab">You give it</div><div class="val">{gives}</div></div>'
        f'<div><div class="lab">You get</div><div class="val">{gets}</div></div></div></div>',
        unsafe_allow_html=True)


# ---------------------------------------------------------------- sample briefs
PRESETS = {
    "BrightPath · local business marketing": dict(brand="BrightPath", goal="Increase qualified website enquiries",
        audience="Small business owners exploring digital marketing", channel="LinkedIn", voice="Clear and helpful", budget=500.0),
    "FitFuel · healthy snack launch": dict(brand="FitFuel", goal="Drive first orders for a new protein snack",
        audience="Busy professionals who work out", channel="Instagram", voice="Bold and energetic", budget=1200.0),
    "CloudNest · B2B software trial": dict(brand="CloudNest", goal="Grow free-trial sign-ups",
        audience="IT managers at mid-size companies", channel="Email", voice="Expert and practical", budget=800.0),
}
CHANNELS = ["LinkedIn", "Email", "Instagram", "Paid search", "Multi-channel"]
VOICES = ["Clear and helpful", "Expert and practical", "Bold and energetic", "Warm and conversational"]


def apply_preset():
    for k, v in PRESETS[st.session_state["preset"]].items():
        st.session_state[k] = v


if "brand" not in st.session_state:
    st.session_state["preset"] = next(iter(PRESETS))
    apply_preset()

# ---------------------------------------------------------------- hero
st.markdown("""
<div class="hero">
  <div class="eyebrow">✦ A multi-agent marketing prototype</div>
  <h1>Digital Marketing AI Lab</h1>
  <p>Four specialist agents turn one campaign brief into a plan, ready-to-edit content, launch checks and clear performance numbers.</p>
  <div class="steps">
    <div class="step"><div class="n">1</div><b>Describe your campaign</b><span>Fill the brief on the left, or pick a sample to see it in action.</span></div>
    <div class="step"><div class="n">2</div><b>Walk through the agents</b><span>Open each numbered tab below. Every tab explains what it does.</span></div>
    <div class="step"><div class="n">3</div><b>Edit &amp; download</b><span>Tweak the drafts, run the checks, and download each output as JSON.</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

cards = {
    "strategy": ("Turns your goal into a campaign plan, message and test plan.", "Brief → Blueprint"),
    "content": ("Writes an editable social post and email subject lines.", "Blueprint → Drafts"),
    "qa": ("Checks links, UTM tags and risky claims before launch.", "Drafts → Go / Review"),
    "perf": ("Turns raw campaign numbers into rates, costs and warnings.", "Results → Insights"),
}
st.markdown('<div class="agents">' + "".join(
    f'<div class="agent" style="--c:{AGENTS[k]["color"]}"><div class="ic">{AGENTS[k]["icon"]}</div>'
    f'<div class="nm">{AGENTS[k]["num"]} · {AGENTS[k]["name"]}</div><div class="ds">{d}</div><div class="io">{io}</div></div>'
    for k, (d, io) in cards.items()) + "</div>", unsafe_allow_html=True)

api_ready = bool(os.getenv("GEMINI_API_KEY", "").strip())
if api_ready:
    st.success("✨ AI mode is available. Review everything it writes before you use it.")
else:
    st.info("🟢 Demo mode: everything runs instantly with built-in logic. No account or API key needed.")

# ---------------------------------------------------------------- sidebar brief
with st.sidebar:
    st.markdown("### 📝 Step 1 · Your campaign brief")
    st.caption("Everything on this page updates from these fields.")
    st.selectbox("Start from a sample", list(PRESETS), key="preset", on_change=apply_preset,
                 help="Fictional examples. Pick one, then change any field.")
    brand = st.text_input("Brand / project", key="brand", help="Use a fictional brand for public demos.")
    goal = st.text_input("What do you want to achieve?", key="goal")
    audience = st.text_input("Who is it for?", key="audience")
    channel = st.selectbox("Main channel", CHANNELS, key="channel")
    voice = st.selectbox("Brand voice", VOICES, key="voice")
    budget = st.number_input("Budget (optional)", min_value=0.0, step=50.0, key="budget")
    st.divider()
    st.markdown("**🛟 Safe-use rules**")
    st.caption("Use made-up data · check every claim and link · a human approves before anything is published or paid for.")

strategy = build_strategy(brand, goal, audience, channel, budget, voice)
content = build_content(brand, goal, audience, channel, voice)
tab1, tab2, tab3, tab4 = st.tabs([f'{a["icon"]} {a["num"]} · {a["name"]}' for a in AGENTS.values()])

# ---------------------------------------------------------------- 01 strategy
with tab1:
    banner("strategy", "Builds a simple, testable campaign plan.", "Your goal, audience, channel and budget.",
           "A blueprint, three content pillars and a test plan.")
    c1, c2, c3, c4 = st.columns(4)
    for col, (k, v) in zip((c1, c2, c3, c4), [("Campaign", strategy["campaign_name"]), ("Channel", channel),
                                             ("Budget", f"{budget:,.0f}"), ("Voice", voice)]):
        col.markdown(f'<div class="card"><div class="k">{k}</div><div class="v">{e(str(v))}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="big-msg">💡 Core message: {e(strategy["core_message"])}</div>', unsafe_allow_html=True)
    st.markdown("#### Content pillars — the three themes every post should fit into")
    pcols = st.columns(3)
    for col, p, bg in zip(pcols, strategy["content_pillars"], ["#4F46E5", "#7C3AED", "#DB2777"]):
        col.markdown(f'<div class="pillar" style="background:{bg}"><small>Pillar</small>{e(p)}</div>', unsafe_allow_html=True)
    st.markdown("#### Test plan — how to learn what works")
    st.markdown('<div class="tl">' + "".join(f'<div data-n="{i}">{e(t)}</div>' for i, t in enumerate(strategy["test_plan"], 1))
                + "</div>", unsafe_allow_html=True)
    st.markdown("**Measure success with:** " + " · ".join(strategy["success_metrics"]))
    with st.expander("ℹ️ Why are there no target numbers?"):
        st.write("No historical results were provided, so the agent doesn't invent targets. Set numeric goals from your own past campaigns.")
    b1, b2 = st.columns([1, 1])
    if b1.button("✨ Enhance with AI (optional)", type="primary", help="Uses Gemini only if an API key is configured on the server."):
        with st.spinner("Asking the AI for a sharper draft..."):
            st.session_state["ai_result"] = enhance_with_ai(brand, goal, audience, channel, voice)
    b2.download_button("⬇️ Download blueprint (JSON)", json.dumps(strategy, indent=2), "campaign_strategy.json", "application/json")
    if "ai_result" in st.session_state:
        st.caption(st.session_state["ai_result"]["mode"])
        st.json(st.session_state["ai_result"])

# ---------------------------------------------------------------- 02 content
with tab2:
    banner("content", "Drafts copy you can edit right here.", "The brief and chosen brand voice.",
           "A social post, three email subject lines and a call to action.")
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown("#### ✏️ Edit the draft")
        post = st.text_area("Social post", content["social_post"], height=230, help="Changes appear in the preview instantly.")
        n = len(post)
        st.progress(min(n / 3000, 1.0), text=f"{n} characters · LinkedIn allows up to 3,000")
        subjects = st.text_area("Email subject lines (one per line)", "\n".join(content["email_subjects"]), height=110)
    with right:
        st.markdown("#### 👀 Live preview")
        initials = e((brand or "B")[:1].upper())
        st.markdown(f'<div class="post"><div class="who"><div class="av">{initials}</div><div><div class="nm">{e(brand)}</div>'
                    f'<div class="sub">Sponsored · {e(channel)}</div></div></div><div class="body">{e(post).replace(chr(10), "<br>")}</div></div>',
                    unsafe_allow_html=True)
        st.markdown("#### 📬 Inbox preview")
        st.markdown('<div class="inbox">' + "".join(f"<div><b>{e(brand)}</b>{e(s)}</div>" for s in subjects.splitlines() if s.strip())
                    + "</div>", unsafe_allow_html=True)
        st.markdown(f"**Call to action:** `{content['cta']}`")
    st.caption("⚠️ " + content["note"])
    st.download_button("⬇️ Download content pack (JSON)", json.dumps(
        {"social_post": post, "email_subjects": subjects.splitlines(), "cta": content["cta"]}, indent=2),
        "content_pack.json", "application/json")

# ---------------------------------------------------------------- 03 QA
with tab3:
    banner("qa", "Runs a pre-launch checklist so mistakes don't go live.", "Your links, UTM tracking tags and copy.",
           "A pass / review result for every check, with how to fix it.")
    with st.expander("ℹ️ What are UTM tags?"):
        st.write("Small labels added to a link (source, medium, campaign) so analytics tools know which campaign sent a visitor. "
                 "Try clearing the *UTM source* box and running the checks to see a review flag.")
    with st.form("qa_form"):
        website_url = st.text_input("Brand website URL", "https://example.com")
        destination_url = st.text_input("Campaign landing page URL", "https://example.com/offer")
        q1, q2, q3 = st.columns(3)
        utm_source = q1.text_input("UTM source", channel.lower().replace(" ", "_"), help="Where traffic comes from, e.g. linkedin")
        utm_medium = q2.text_input("UTM medium", "social" if channel in ("LinkedIn", "Instagram") else channel.lower().replace(" ", "_"),
                                   help="Type of channel, e.g. social or email")
        utm_campaign = q3.text_input("UTM campaign", f"{(brand or 'brand').lower()}_growth_sprint", help="One consistent campaign name")
        qa_copy = st.text_area("Copy to check", content["social_post"], height=120,
                               help="Try adding 'guaranteed results' to see the claim check flag it.")
        run_qa = st.form_submit_button("🛡️ Run launch checks", type="primary")
    if run_qa:
        st.session_state["qa_checks"] = check_campaign_qa(website_url, destination_url, utm_source, utm_medium, utm_campaign, qa_copy)
    if "qa_checks" in st.session_state:
        checks = st.session_state["qa_checks"]
        passed = sum(x["status"] == "PASS" for x in checks)
        ready = passed == len(checks)
        st.markdown(f"### {'✅ Ready for human review' if ready else '🟠 Fix the flagged items'} — {passed}/{len(checks)} checks passed")
        st.progress(passed / len(checks))
        for c in checks:
            cls = "pass" if c["status"] == "PASS" else "review"
            st.markdown(f'<div class="chk"><span class="pill {cls}">{c["status"]}</span><div><div class="nm">{e(c["check"])}</div>'
                        f'<div class="dt">{e(c["detail"])}</div></div></div>', unsafe_allow_html=True)
        st.caption("A pass is a basic format check only: links aren't opened and this isn't legal or brand approval.")
        st.download_button("⬇️ Download QA report (JSON)", json.dumps(checks, indent=2), "campaign_qa_report.json", "application/json")
    else:
        st.markdown('<div class="note">👆 Press <b>Run launch checks</b> to see the results.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- 04 performance
with tab4:
    banner("perf", "Turns raw campaign numbers into the rates that matter.", "Sent, delivered, clicks, conversions and spend.",
           "Delivery, click and conversion rates, cost per conversion, and data warnings.")
    with st.form("metrics_form"):
        a, b, c = st.columns(3)
        sent = a.number_input("Sent / reached", min_value=0, value=10000, step=100, help="How many people the campaign was sent to")
        delivered = a.number_input("Delivered", min_value=0, value=9800, step=100, help="How many actually received it")
        clicks = b.number_input("Clicks", min_value=0, value=350, step=10, help="Say whether these are unique or total clicks")
        conversions = b.number_input("Conversions", min_value=0, value=45, step=1, help="Sign-ups, orders, or whatever counts as success")
        spend = c.number_input("Spend", min_value=0.0, value=500.0, step=25.0, help="Total cost (any currency)")
        c.markdown(" ")
        run_metrics = st.form_submit_button("📈 Analyse performance", type="primary")
    if run_metrics:
        st.session_state["metrics_result"] = analyze_metrics(sent, delivered, clicks, conversions, spend)
    if "metrics_result" in st.session_state:
        r = st.session_state["metrics_result"]
        fmt = lambda v, s="": f"{v:,.2f}{s}" if v is not None else "N/A"
        kcols = st.columns(4)
        for col, (k, v, f) in zip(kcols, [
            ("Delivery rate", fmt(r["delivery_rate_pct"], "%"), "delivered ÷ sent"),
            ("Click-through rate", fmt(r["click_through_rate_pct"], "%"), "clicks ÷ delivered"),
            ("Conversion rate", fmt(r["conversion_rate_pct"], "%"), "conversions ÷ delivered"),
            ("Cost per conversion", fmt(r["cost_per_conversion"]), "spend ÷ conversions")]):
            col.markdown(f'<div class="kpi"><div class="k">{k}</div><div class="v">{v}</div><div class="f">= {f}</div></div>',
                         unsafe_allow_html=True)
        st.markdown("#### The funnel — where people drop off")
        top = max(sent, delivered, clicks, conversions, 1)
        rows = [("Sent", sent, "#312E81"), ("Delivered", delivered, "#6D28D9"), ("Clicked", clicks, "#DB2777"), ("Converted", conversions, "#D97706")]
        st.markdown('<div class="funnel">' + "".join(
            f'<div class="bar" style="width:{max(v / top * 100, 1):.1f}%;background:{col}">{lab}: {v:,}</div>'
            for lab, v, col in rows) + "</div>", unsafe_allow_html=True)
        st.markdown("#### 🔍 Data-quality notes")
        for note in r["data_quality_notes"]:
            st.markdown(f'<div class="note">{e(note)}</div>', unsafe_allow_html=True)
        st.download_button("⬇️ Download analysis (JSON)", json.dumps(r, indent=2), "performance_analysis.json", "application/json")
    else:
        st.markdown('<div class="note">👆 Sample numbers are filled in. Press <b>Analyse performance</b>, then try setting Delivered higher than Sent to see a warning.</div>',
                    unsafe_allow_html=True)

st.divider()
st.caption("Prototype · nothing is sent, published or changed automatically · use fictional data · never commit API keys or customer data.")
