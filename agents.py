"""Reusable workflows for the Digital Marketing AI Lab."""
import json
import os
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def build_strategy(brand, goal, audience, channel, budget, voice):
    brand = (brand or "").strip() or "Sample Brand"
    goal = (goal or "").strip() or "Improve campaign effectiveness"
    audience = (audience or "").strip() or "Prospective customers"
    channel = (channel or "").strip() or "LinkedIn"
    return {
        "campaign_name": f"{brand} | {channel} growth sprint",
        "objective": goal,
        "audience": audience,
        "primary_channel": channel,
        "budget": round(max(0, float(budget)), 2),
        "brand_voice": (voice or "").strip() or "Clear and helpful",
        "core_message": f"Lead with one clear customer problem, then show how {brand} helps solve it.",
        "content_pillars": ["Customer problem and insight", "Practical education or demonstration", "Proof, objections, and next step"],
        "test_plan": [
            "Test two message angles while keeping audience and offer consistent.",
            "Use one primary call to action to make results easier to interpret.",
            "Review delivery, engagement, and conversion metrics after the agreed measurement window."
        ],
        "success_metrics": ["Reach or delivered", "Click-through rate", "Conversion rate", "Cost per conversion (if spend is tracked)"],
        "assumptions": ["No baseline or uplift data was supplied; set numeric targets using verified historical results."]
    }


def build_content(brand, goal, audience, channel, voice):
    brand = (brand or "").strip() or "Sample Brand"
    goal = (goal or "").strip() or "make a useful improvement"
    audience = (audience or "").strip() or "people exploring solutions"
    channel = (channel or "").strip() or "LinkedIn"
    voice = (voice or "").strip() or "clear and helpful"
    post = (
        f"Trying to {goal.lower()}?\n\n"
        f"Start by understanding what matters most to {audience.lower()}, then make the next step simple. "
        f"{brand} is exploring practical ways to help—without unnecessary complexity.\n\n"
        "What is the biggest challenge you would solve first?\n\n"
        "#Marketing #CustomerExperience #Innovation"
    )
    return {
        "channel": channel,
        "social_post": post,
        "email_subjects": [f"A simpler way to {goal.lower()}", f"What matters most to {audience.lower()}?", f"One practical idea from {brand}"],
        "cta": "Explore the approach",
        "note": f"Draft in a {voice.lower()} voice. Verify all brand, product, pricing, and offer claims before publishing."
    }


def check_campaign_qa(website_url, destination_url, utm_source, utm_medium, utm_campaign, copy):
    checks = []
    def add(name, passed, detail):
        checks.append({"check": name, "status": "PASS" if passed else "REVIEW", "detail": detail})
    def valid_url(value):
        try:
            p = urlparse((value or "").strip())
            return p.scheme in {"http", "https"} and bool(p.netloc) and "." in p.netloc
        except Exception:
            return False
    add("Website URL format", valid_url(website_url), "URL format looks valid." if valid_url(website_url) else "Provide a complete HTTP(S) URL.")
    add("Destination URL format", valid_url(destination_url), "URL format looks valid; link was not opened." if valid_url(destination_url) else "Provide a complete destination URL.")
    add("UTM source", bool((utm_source or "").strip()), "Source supplied." if (utm_source or "").strip() else "Add a source such as linkedin or newsletter.")
    add("UTM medium", bool((utm_medium or "").strip()), "Medium supplied." if (utm_medium or "").strip() else "Add a medium such as social or email.")
    add("UTM campaign", bool((utm_campaign or "").strip()), "Campaign identifier supplied." if (utm_campaign or "").strip() else "Add a consistent campaign identifier.")
    add("Content present", bool((copy or "").strip()), "Copy supplied." if (copy or "").strip() else "Add copy for review.")
    suspicious = re.search(r"\b(guaranteed results|100% guaranteed|cure any|risk-free returns)\b", copy or "", re.I)
    if (copy or "").strip():
        add("Potential absolute claim", not bool(suspicious), "No common absolute-claim phrase detected; not legal approval." if not suspicious else "Review the absolute claim and confirm evidence/approval.")
    return checks


def analyze_metrics(sent, delivered, clicks, conversions, spend=0):
    sent, delivered, clicks, conversions = map(int, (sent, delivered, clicks, conversions))
    spend = float(spend)
    def pct(n, d):
        return round(n / d * 100, 2) if d > 0 else None
    notes = []
    if min(sent, delivered, clicks, conversions) < 0 or spend < 0:
        notes.append("Negative values are invalid for these inputs.")
    if delivered > sent:
        notes.append("Delivered exceeds sent; check source definitions.")
    if clicks > delivered:
        notes.append("Clicks exceed delivered; confirm whether clicks are total events.")
    if conversions > clicks:
        notes.append("Conversions exceed clicks; verify tracking and attribution definitions.")
    if not notes:
        notes.append("No basic arithmetic warning detected. Validate unique vs total events, attribution, deduplication, and reporting window.")
    return {
        "sent": sent, "delivered": delivered,
        "delivery_rate_pct": pct(delivered, sent),
        "click_through_rate_pct": pct(clicks, delivered),
        "conversion_rate_pct": pct(conversions, delivered),
        "spend": round(spend, 2),
        "cost_per_conversion": round(spend / conversions, 2) if spend > 0 and conversions > 0 else None,
        "data_quality_notes": notes,
        "definitions": {
            "delivery_rate_pct": "delivered / sent × 100",
            "click_through_rate_pct": "clicks / delivered × 100; clarify unique vs total clicks",
            "conversion_rate_pct": "conversions / delivered × 100; confirm attribution rules"
        }
    }


def _gemini_generate(prompt):
    """Optional server-side Gemini request. No key means offline demo mode."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.6, "maxOutputTokens": 1200}}
    req = Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=25) as res:
            data = json.loads(res.read().decode())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, ValueError):
        return None


def enhance_with_ai(brand, goal, audience, channel, voice):
    prompt = f"""Act as a careful digital marketing team. Return valid JSON only with keys:
strategy_summary (string), audience_insight (string), content_ideas (array of 3 strings),
social_post (string), email_subjects (array of 3 strings), CTA (string), risks (array of strings).
Brand: {brand}; goal: {goal}; audience: {audience}; channel: {channel}; voice: {voice}.
Use only supplied facts. Do not invent statistics, testimonials, features, prices, or guarantees.
Mark assumptions and advise human review."""
    response = _gemini_generate(prompt)
    if not response:
        return {"mode": "Demo mode", "message": "No API key is configured, or the model request was unavailable. All other tools remain usable."}
    try:
        match = re.search(r"\{.*\}", response, re.S)
        return {"mode": "AI-assisted — human review required", "result": json.loads(match.group(0) if match else response)}
    except (ValueError, TypeError):
        return {"mode": "Demo mode", "message": "The model response could not be parsed. Try again or use the built-in demo outputs."}
