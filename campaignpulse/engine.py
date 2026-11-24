"""Deterministic campaign KPI, validation and diagnostic engine.

All rates are returned as percentages (0–100). The engine never calls an LLM.
"""
from __future__ import annotations

from datetime import date
from typing import Any

DEFAULT_THRESHOLDS = {
    "delivery_rate": {"warning_below": 95.0, "critical_below": 90.0},
    "hard_bounce_rate": {"warning_above": 2.0, "critical_above": 3.0},
    "soft_bounce_rate": {"warning_above": 5.0, "critical_above": 8.0},
    "unsubscribe_rate": {"warning_above": 0.30, "critical_above": 0.50},
    "open_rate": {"warning_below": 15.0, "healthy_above": 20.0},
    "click_rate": {"warning_below": 1.0, "healthy_above": 2.0},
    "ctor": {"warning_below": 8.0, "healthy_above": 12.0},
}

REQUIRED_COUNTS = (
    "sent", "delivered", "hard_bounces", "soft_bounces",
    "unique_opens", "unique_clicks", "unsubscribes",
)
OPTIONAL_COUNTS = (
    "ignored_errors", "other_errors", "excluded_before_send", "new_quarantines",
)


def _number(value: Any, field: str, required: bool = False):
    if value is None or value == "":
        return (None, f"{field} is required." if required else None)
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None, f"{field} must be a whole number."
    if number < 0:
        return None, f"{field} cannot be negative."
    return number, None


def _pct(numerator: int | None, denominator: int | None):
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 2)


def validate_campaign(data: dict[str, Any], tolerance_count: int = 10,
                      tolerance_percentage: float = 0.5) -> dict[str, Any]:
    """Return hard errors, warnings and review notes without mutating input."""
    errors, warnings, reviews = [], [], []
    counts = {}
    for field in REQUIRED_COUNTS:
        value, error = _number(data.get(field), field, required=True)
        if error:
            errors.append(error)
        else:
            counts[field] = value
    for field in OPTIONAL_COUNTS:
        value, error = _number(data.get(field), field)
        if error:
            errors.append(error)
        elif value is not None:
            counts[field] = value

    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings, "reviews": reviews, "counts": counts}

    sent, delivered = counts["sent"], counts["delivered"]
    hard, soft = counts["hard_bounces"], counts["soft_bounces"]
    opens, clicks, unsub = counts["unique_opens"], counts["unique_clicks"], counts["unsubscribes"]
    ignored = counts.get("ignored_errors", 0)
    other = counts.get("other_errors", 0)

    if sent == 0:
        errors.append("sent must be greater than zero to calculate campaign rates.")
    if delivered > sent:
        errors.append("delivered cannot exceed sent.")
    if hard + soft + ignored + other > sent:
        errors.append("Recorded failure counts exceed sent.")
    if opens > delivered:
        errors.append("unique_opens cannot exceed delivered.")
    if clicks > delivered:
        errors.append("unique_clicks cannot exceed delivered.")
    if unsub > delivered:
        errors.append("unsubscribes cannot exceed delivered.")

    if clicks > opens:
        reviews.append("Unique clicks exceed unique opens. Confirm both metrics use compatible unique-recipient definitions before relying on CTOR.")
    if sent and delivered == 0:
        warnings.append("No delivered messages were supplied; engagement rates cannot be calculated.")
    if sent < 500:
        warnings.append("Small send volume (<500): percentage-based conclusions may be statistically unstable.")

    failures = hard + soft + ignored + other
    unaccounted = sent - delivered - failures
    tolerance = max(int(tolerance_count), round(sent * max(0.0, float(tolerance_percentage)) / 100))
    if abs(unaccounted) > tolerance:
        warnings.append(
            f"Reconciliation mismatch: {unaccounted:,} messages are not explained by delivered plus recorded failures "
            f"(tolerance ±{tolerance:,}). Check pending retries, exclusions, omitted error categories or report timing."
        )
    elif unaccounted != 0:
        warnings.append(f"Minor reconciliation difference: {unaccounted:,} messages, within configured tolerance.")

    if opens == 0 and clicks > 0:
        reviews.append("Clicks are present but opens are zero. Check tracking configuration and metric definitions.")
    if unsub == 0 and sent >= 10000:
        reviews.append("No unsubscribes were recorded on a large send. Confirm unsubscribe tracking and export completeness.")

    send_date = data.get("send_date")
    reporting_date = data.get("reporting_date")
    if send_date and reporting_date:
        try:
            elapsed = (date.fromisoformat(str(reporting_date)[:10]) - date.fromisoformat(str(send_date)[:10])).days
            if elapsed < 0:
                errors.append("reporting_date cannot be earlier than send_date.")
            elif elapsed < 1:
                warnings.append("Early reporting snapshot (<24 hours): engagement and bounce metrics may still be maturing.")
            elif elapsed < 7:
                warnings.append("Reporting snapshot is less than seven days after send; asynchronous bounce processing may still be incomplete.")
        except ValueError:
            errors.append("send_date and reporting_date must use YYYY-MM-DD format.")

    return {"valid": not errors, "errors": errors, "warnings": warnings, "reviews": reviews,
            "counts": counts, "unaccounted_messages": unaccounted, "reconciliation_tolerance": tolerance}


def calculate_metrics(counts: dict[str, int]) -> dict[str, float | None]:
    sent, delivered = counts["sent"], counts["delivered"]
    hard, soft = counts["hard_bounces"], counts["soft_bounces"]
    errors = counts.get("ignored_errors", 0) + counts.get("other_errors", 0)
    opens, clicks, unsub = counts["unique_opens"], counts["unique_clicks"], counts["unsubscribes"]
    return {
        "delivery_rate": _pct(delivered, sent),
        "hard_bounce_rate": _pct(hard, sent),
        "soft_bounce_rate": _pct(soft, sent),
        "total_bounce_rate": _pct(hard + soft + errors, sent),
        "open_rate": _pct(opens, delivered),
        "click_rate": _pct(clicks, delivered),
        "ctor": _pct(clicks, opens),
        "unsubscribe_rate": _pct(unsub, delivered),
    }


def _finding(metric: str, value: float, severity: str, message: str,
             evidence: str, checks: list[str], causes: list[str] | None = None):
    return {
        "id": metric, "title": message, "metric": metric, "value_pct": value,
        "severity": severity, "evidence_status": "observed_from_supplied_data",
        "evidence": evidence, "confidence": "medium",
        "possible_explanations": causes or [],
        "acc_operational_checks": checks,
        "verification_boundary": "These are recommended checks. CampaignPulse AI has not accessed or inspected an Adobe Campaign instance.",
    }


def diagnose(metrics: dict[str, float | None], thresholds: dict[str, Any] | None = None):
    t = thresholds or DEFAULT_THRESHOLDS
    findings = []
    checks = {
        "delivery_rate": ["Review delivery summary and delivery logs by failure type and reason.", "Confirm the reporting snapshot is mature and all asynchronous errors are included."],
        "hard_bounce_rate": ["Review hard-bounce failure reasons and invalid-address patterns.", "Inspect quarantine records and suppression handling in Adobe Campaign."],
        "soft_bounce_rate": ["Review delivery logs by domain and temporary failure reason.", "Check retry behavior, bounce mailbox processing and sender reputation signals."],
        "unsubscribe_rate": ["Review unsubscribe trend by segment and campaign frequency.", "Check content relevance, preference handling and audience selection."],
        "open_rate": ["Review subject line, send time and audience relevance.", "Interpret opens cautiously because privacy features can inflate open tracking."],
        "click_rate": ["Review CTA visibility, link destination and content-to-audience relevance.", "Check tracking configuration and unique-click definitions."],
        "ctor": ["Review message-to-landing-page continuity and CTA prominence.", "Confirm opens and clicks use compatible unique-recipient definitions."],
    }
    for key, rule in t.items():
        value = metrics.get(key)
        if value is None:
            continue
        if "critical_below" in rule and value < rule["critical_below"]:
            findings.append(_finding(key, value, "critical", f"{key.replace('_', ' ').title()} is critically low",
                                     f"{value:.2f}% is below {rule['critical_below']:.2f}%.", checks.get(key, [])))
        elif "critical_above" in rule and value > rule["critical_above"]:
            findings.append(_finding(key, value, "critical", f"{key.replace('_', ' ').title()} is critically high",
                                     f"{value:.2f}% is above {rule['critical_above']:.2f}%.", checks.get(key, [])))
        elif "warning_below" in rule and value < rule["warning_below"]:
            findings.append(_finding(key, value, "warning", f"{key.replace('_', ' ').title()} needs attention",
                                     f"{value:.2f}% is below the configured {rule['warning_below']:.2f}% threshold.", checks.get(key, [])))
        elif "warning_above" in rule and value > rule["warning_above"]:
            findings.append(_finding(key, value, "warning", f"{key.replace('_', ' ').title()} needs attention",
                                     f"{value:.2f}% is above the configured {rule['warning_above']:.2f}% threshold.", checks.get(key, [])))
    priority = {"critical": 0, "warning": 1, "review": 2, "info": 3}
    findings.sort(key=lambda x: priority.get(x["severity"], 9))
    critical = sum(x["severity"] == "critical" for x in findings)
    warning = sum(x["severity"] == "warning" for x in findings)
    health = "Critical" if critical else ("At risk" if warning >= 2 else ("Watch" if warning else "Healthy"))
    return {"overall_health": health, "findings": findings,
            "priority_actions": [x["acc_operational_checks"][0] for x in findings[:3] if x["acc_operational_checks"]],
            "health_basis": "Configurable V1 thresholds; not an Adobe-certified score."}


def analyze_campaign(data: dict[str, Any], thresholds: dict[str, Any] | None = None):
    validation = validate_campaign(
        data,
        tolerance_count=int(data.get("tolerance_count", 10) or 0),
        tolerance_percentage=float(data.get("tolerance_percentage", 0.5) or 0),
    )
    if not validation["valid"]:
        return {"valid": False, "validation": validation}
    metrics = calculate_metrics(validation["counts"])
    diagnosis = diagnose(metrics, thresholds)
    return {"valid": True, "validation": validation, "metrics": metrics, **diagnosis}
