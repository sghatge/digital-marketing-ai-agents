"""Optional LLM narrative adapter. Deterministic metrics and findings remain authoritative."""
from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def explain_with_optional_gemini(analysis: dict, api_key: str | None = None,
                                 model: str | None = None) -> str | None:
    """Return a bounded narrative, or None when no model is configured/available.

    Only aggregate metrics and precomputed findings are sent. The model is not
    allowed to alter KPI values, severity, evidence, or recommended checks.
    """
    key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    if not key:
        return None
    model_name = (model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")).strip()
    evidence = {
        "overall_health": analysis.get("overall_health"),
        "metrics": analysis.get("metrics", {}),
        "findings": [
            {"title": x.get("title"), "severity": x.get("severity"),
             "evidence": x.get("evidence"), "checks": x.get("acc_operational_checks")}
            for x in analysis.get("findings", [])
        ],
        "priority_actions": analysis.get("priority_actions", []),
        "warnings": analysis.get("validation", {}).get("warnings", []),
    }
    prompt = (
        "You are an Adobe Campaign email operations practitioner. Explain this supplied "
        "campaign diagnostic in plain language for a marketing operator. Use only the "
        "provided evidence. Distinguish observations from possible explanations. Do not "
        "invent root causes, benchmarks, or platform observations. Do not change metrics, "
        "severity, or actions. State that the user must verify any ACC checks in their own "
        "instance. Mention that open rates can be affected by privacy protections. "
        "Keep the answer under 220 words.\n\n"
        + json.dumps(evidence, ensure_ascii=False)
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 700},
    }
    req = Request(url, data=json.dumps(payload).encode("utf-8"),
                  headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, ValueError):
        return None
