import unittest
from agents import analyze_metrics, build_content, build_strategy, check_campaign_qa

class AgentTests(unittest.TestCase):
    def test_strategy_uses_brief(self):
        x = build_strategy("Northstar", "Grow trials", "Founders", "LinkedIn", 250, "Direct")
        self.assertIn("Northstar", x["campaign_name"])
        self.assertEqual(x["objective"], "Grow trials")
    def test_content_has_three_subjects(self):
        self.assertEqual(len(build_content("A", "Grow", "Founders", "LinkedIn", "Clear")["email_subjects"]), 3)
    def test_qa_flags_missing_utm(self):
        x = check_campaign_qa("https://example.com", "https://example.com/offer", "", "social", "launch", "Copy")
        self.assertEqual({r["check"]: r["status"] for r in x}["UTM source"], "REVIEW")
    def test_metrics(self):
        x = analyze_metrics(1000, 900, 90, 9, 45)
        self.assertEqual(x["delivery_rate_pct"], 90.0)
        self.assertEqual(x["click_through_rate_pct"], 10.0)
        self.assertEqual(x["conversion_rate_pct"], 1.0)
        self.assertEqual(x["cost_per_conversion"], 5.0)
    def test_bad_delivery_warns(self):
        x = analyze_metrics(100, 120, 10, 1)
        self.assertTrue(any("Delivered exceeds sent" in n for n in x["data_quality_notes"]))

if __name__ == "__main__":
    unittest.main()
