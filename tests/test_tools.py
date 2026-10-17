import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import benchmark  # noqa: E402
import instagram_api  # noqa: E402
import meta_ads  # noqa: E402
import startup_db  # noqa: E402

GOOD_PLAN = {
    "campaign": {"name": "Test", "objective": "OUTCOME_TRAFFIC"},
    "adset": {"name": "DE", "daily_budget": 1500, "optimization_goal": "LINK_CLICKS",
              "billing_event": "IMPRESSIONS", "targeting": {"geo_locations": {"countries": ["DE"]}}},
    "creative": {"link": "https://example.com", "message": "Hello"},
    "ad": {"name": "Ad 1"},
}


class MetaAdsGuardrails(unittest.TestCase):
    def test_good_plan_passes(self):
        self.assertEqual(meta_ads.validate_plan(GOOD_PLAN), [])

    def test_budget_over_cap_rejected(self):
        plan = json.loads(json.dumps(GOOD_PLAN))
        plan["adset"]["daily_budget"] = 10**6
        self.assertTrue(any("exceeds cap" in e for e in meta_ads.validate_plan(plan)))

    def test_active_status_rejected(self):
        plan = json.loads(json.dumps(GOOD_PLAN))
        plan["campaign"]["status"] = "ACTIVE"
        self.assertTrue(any("PAUSED only" in e for e in meta_ads.validate_plan(plan)))

    def test_payloads_always_paused(self):
        p = meta_ads.payloads(GOOD_PLAN)
        for k in ("campaign", "adset", "ad"):
            self.assertEqual(p[k]["status"], "PAUSED")


class StartupScoring(unittest.TestCase):
    def test_weighted_score_and_verdict(self):
        rubric = startup_db.load_rubric()
        scores = {d: 4 for d in rubric["dimensions"]}
        total, verdict = startup_db.weighted(scores, rubric)
        self.assertEqual(total, 4.0)
        self.assertTrue(verdict.startswith("Strong"))

    def test_missing_dimension_rejected(self):
        rubric = startup_db.load_rubric()
        with self.assertRaises(ValueError):
            startup_db.weighted({"team": 4}, rubric)

    def test_outcome_label(self):
        self.assertEqual(startup_db.outcome_label("Company filed for bankruptcy"), -1)
        self.assertEqual(startup_db.outcome_label("Raised a $40M Series B"), 1)


class Benchmark(unittest.TestCase):
    def test_recall_and_missed(self):
        brief = [{"topic": "Q", "title": "IonQ signs quantum networking contract with US Air Force",
                  "outlets": [{"url": "https://www.reuters.com/x", "domain": "reuters.com"}]}]
        ref = [{"topic": "Q", "title": "IonQ wins US Air Force quantum networking contract", "importance": 3},
               {"topic": "Q", "title": "PsiQuantum raises new funding round", "importance": 1}]
        res = benchmark.score(brief, ref, benchmark.trusted_domains())
        self.assertAlmostEqual(res["recall_weighted"], 0.75)
        self.assertEqual(res["precision_trusted"], 1.0)
        self.assertEqual(res["missed"][0]["title"], "PsiQuantum raises new funding round")

    def test_overall(self):
        data = {"recall_weighted": 0.8, "precision_trusted": 1.0,
                "judged": {"accuracy": 4, "insight": 4, "concision": 4, "feedback_fit": 4}}
        self.assertAlmostEqual(benchmark.overall(data), 0.30 * 4 + 0.15 * 5 + 0.55 * 4, places=2)


class Instagram(unittest.TestCase):
    def test_analyze(self):
        data = {"username": "x", "followers_count": 1000, "media": [
            {"media_type": "VIDEO", "media_product_type": "REELS", "like_count": 90, "comments_count": 10,
             "timestamp": "2026-10-01T10:00:00+0000", "caption": "Deep tech #quantum"},
            {"media_type": "IMAGE", "like_count": 20, "comments_count": 0,
             "timestamp": "2026-10-08T10:00:00+0000", "caption": "Team photo #hiring"}]}
        res = instagram_api.analyze_data(data)
        self.assertEqual(res["format_mix"], {"REELS": 1, "IMAGE": 1})
        self.assertEqual(res["median_er_by_format"]["REELS"], 0.1)


class AdsGuardHook(unittest.TestCase):
    def run_hook(self, event):
        return subprocess.run([sys.executable, str(ROOT / ".claude/hooks/ads_guard.py")],
                              input=json.dumps(event), capture_output=True, text=True).returncode

    def test_blocks_activation(self):
        cmd = "curl -X POST https://graph.facebook.com/v23.0/123 -d status=ACTIVE"
        self.assertEqual(self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}}), 2)

    def test_blocks_guardrail_edit(self):
        ev = {"tool_name": "Edit", "tool_input": {"file_path": "/repo/config/ads_guardrails.json"}}
        self.assertEqual(self.run_hook(ev), 2)

    def test_allows_normal_commands(self):
        ev = {"tool_name": "Bash", "tool_input": {"command": "python3 tools/meta_ads.py validate --plan p.json"}}
        self.assertEqual(self.run_hook(ev), 0)


if __name__ == "__main__":
    unittest.main()
