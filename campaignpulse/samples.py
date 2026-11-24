"""Fictional, aggregate-only demo scenarios."""
SAMPLES = {
    "Healthy campaign": {
        "campaign_name": "Spring customer newsletter", "metric_source": "synthetic_demo",
        "send_date": "2026-11-10", "reporting_date": "2026-11-18",
        "campaign_type": "newsletter", "audience_type": "customer", "industry": "Retail",
        "sent": 25000, "delivered": 24550, "hard_bounces": 180, "soft_bounces": 270,
        "other_errors": 0, "ignored_errors": 0, "unique_opens": 6150,
        "unique_clicks": 780, "unsubscribes": 95,
    },
    "Poor deliverability": {
        "campaign_name": "Fictional product announcement", "metric_source": "synthetic_demo",
        "send_date": "2026-11-10", "reporting_date": "2026-11-18",
        "campaign_type": "promotional", "audience_type": "mixed", "industry": "Technology",
        "sent": 30000, "delivered": 27000, "hard_bounces": 1200, "soft_bounces": 1800,
        "other_errors": 0, "ignored_errors": 0, "unique_opens": 5400,
        "unique_clicks": 540, "unsubscribes": 135,
    },
    "Declining engagement": {
        "campaign_name": "Fictional monthly digest", "metric_source": "synthetic_demo",
        "send_date": "2026-11-10", "reporting_date": "2026-11-18",
        "campaign_type": "newsletter", "audience_type": "customer", "industry": "Retail",
        "sent": 40000, "delivered": 39400, "hard_bounces": 200, "soft_bounces": 400,
        "other_errors": 0, "ignored_errors": 0, "unique_opens": 3940,
        "unique_clicks": 197, "unsubscribes": 160,
    },
}
