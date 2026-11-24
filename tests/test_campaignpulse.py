import unittest
from campaignpulse.engine import analyze_campaign, calculate_metrics, validate_campaign
from campaignpulse.samples import SAMPLES
from campaignpulse.reasoning import explain_with_optional_gemini


class CampaignPulseTests(unittest.TestCase):
    def test_healthy_sample_metrics(self):
        result = analyze_campaign(SAMPLES["Healthy campaign"])
        self.assertTrue(result["valid"])
        self.assertEqual(result["metrics"]["delivery_rate"], 98.2)
        self.assertEqual(result["metrics"]["open_rate"], 25.05)
        self.assertEqual(result["metrics"]["click_rate"], 3.18)
        self.assertEqual(result["metrics"]["ctor"], 12.68)
        self.assertEqual(result["metrics"]["unsubscribe_rate"], 0.39)

    def test_poor_deliverability_is_critical(self):
        result = analyze_campaign(SAMPLES["Poor deliverability"])
        self.assertEqual(result["overall_health"], "Critical")
        self.assertTrue(any(x["metric"] == "hard_bounce_rate" for x in result["findings"]))

    def test_declining_engagement_flags_metrics(self):
        result = analyze_campaign(SAMPLES["Declining engagement"])
        self.assertTrue(any(x["metric"] == "open_rate" for x in result["findings"]))
        self.assertTrue(any(x["metric"] == "click_rate" for x in result["findings"]))

    def test_zero_sent_rejected(self):
        data = dict(SAMPLES["Healthy campaign"], sent=0, delivered=0)
        result = analyze_campaign(data)
        self.assertFalse(result["valid"])

    def test_negative_value_rejected(self):
        data = dict(SAMPLES["Healthy campaign"], hard_bounces=-1)
        self.assertFalse(analyze_campaign(data)["valid"])

    def test_delivered_over_sent_rejected(self):
        data = dict(SAMPLES["Healthy campaign"], delivered=25001)
        self.assertFalse(analyze_campaign(data)["valid"])

    def test_failure_counts_over_sent_rejected(self):
        data = dict(SAMPLES["Healthy campaign"], hard_bounces=20000, soft_bounces=10000)
        self.assertFalse(analyze_campaign(data)["valid"])

    def test_unique_opens_over_delivered_rejected(self):
        data = dict(SAMPLES["Healthy campaign"], unique_opens=30000)
        self.assertFalse(analyze_campaign(data)["valid"])

    def test_unique_clicks_over_delivered_rejected(self):
        data = dict(SAMPLES["Healthy campaign"], unique_clicks=30000)
        self.assertFalse(analyze_campaign(data)["valid"])

    def test_unsubscribes_over_delivered_rejected(self):
        data = dict(SAMPLES["Healthy campaign"], unsubscribes=30000)
        self.assertFalse(analyze_campaign(data)["valid"])

    def test_clicks_over_opens_is_review_not_error(self):
        data = dict(SAMPLES["Healthy campaign"], unique_clicks=7000)
        result = analyze_campaign(data)
        self.assertTrue(result["valid"])
        self.assertTrue(result["validation"]["reviews"])

    def test_reconciliation_warning(self):
        data = dict(SAMPLES["Healthy campaign"], delivered=24000)
        result = analyze_campaign(data)
        self.assertTrue(result["valid"])
        self.assertTrue(result["validation"]["warnings"])

    def test_small_send_warning(self):
        data = dict(SAMPLES["Healthy campaign"], sent=400, delivered=390,
                    hard_bounces=4, soft_bounces=6, unique_opens=100,
                    unique_clicks=10, unsubscribes=1)
        result = analyze_campaign(data)
        self.assertTrue(any("Small send" in x for x in result["validation"]["warnings"]))

    def test_early_snapshot_warning(self):
        data = dict(SAMPLES["Healthy campaign"], reporting_date="2026-11-10")
        result = analyze_campaign(data)
        self.assertTrue(any("Early reporting" in x for x in result["validation"]["warnings"]))

    def test_canonical_nested_v11_input_is_accepted(self):
        nested = {
            "schema_version": "1.1",
            "input_metadata": {"input_mode": "manual_form", "metric_source": "manual_entry"},
            "campaign": {"channel": "email", "campaign_name": "Canonical test"},
            "delivery_metrics": {"sent": 25000, "delivered": 24550, "hard_bounces": 180, "soft_bounces": 270},
            "engagement_metrics": {"unique_opens": 6150, "unique_clicks": 780, "unsubscribes": 95},
            "reconciliation": {"tolerance_count": 10, "tolerance_percentage": 0.5}
        }
        result = analyze_campaign(nested)
        self.assertTrue(result["valid"])
        self.assertEqual(result["metrics"]["delivery_rate"], 98.2)

    def test_optional_llm_is_offline_without_key(self):
        self.assertIsNone(explain_with_optional_gemini({"overall_health": "Healthy"}, api_key=""))

    def test_zero_delivered_does_not_divide_by_zero(self):
        data = dict(SAMPLES["Healthy campaign"], delivered=0, hard_bounces=25000,
                    soft_bounces=0, unique_opens=0, unique_clicks=0, unsubscribes=0)
        result = analyze_campaign(data)
        self.assertTrue(result["valid"])
        self.assertIsNone(result["metrics"]["open_rate"])

if __name__ == "__main__":
    unittest.main()
