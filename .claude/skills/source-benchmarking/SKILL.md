---
name: source-benchmarking
description: Benchmark a news brief against what trusted industry sources covered in the same window - coverage recall, factual accuracy, source quality, timeliness and owner-feedback fit - and produce a quality scorecard. Use after drafting any brief or research summary.
---

# Source Benchmarking

The goal is to answer one question: **would a professional analyst reading the
trusted sources today have produced a better brief?**

## 1. Build the benchmark set (independent of the brief)
Don't look at the draft brief yet. For each topic, search only the tier-1 and
tier-2 domains in `config/trusted_sources.yaml` for the same window, using the
trusted-source query variant. List the 3-8 most important stories per topic.
Save them as `memory/benchmarks/<D>-reference.json`:
`[{"topic": "...", "title": "...", "url": "...", "outlet": "...", "importance": 1-3}]`

## 2. Compare
Match brief items to reference stories (same event = match, even with different
outlets). Then run:

```
python3 tools/benchmark.py score --brief memory/briefs/<D>-stories.json \
   --reference memory/benchmarks/<D>-reference.json --out memory/benchmarks/<D>.json
```

The tool computes **importance-weighted recall**, **precision** (share of brief
items backed by a tier 1-2 source), and lists **missed** stories.

## 3. Judge what the tool can't
Score each 1-5 and add to `memory/benchmarks/<D>.json` under `"judged"`:

| Dimension | 5 means |
|---|---|
| accuracy | Every number/name checks out against the cited source (spot-check ≥ 5 claims) |
| insight | "So what" lines add analysis, not just a paraphrase of the headline |
| concision | Fits the reading time in `config/delivery.json`, no filler |
| feedback_fit | Follows every rule in `memory/learned_rules.md` |

## 4. Overall score and trend
```
python3 tools/benchmark.py overall --file memory/benchmarks/<D>.json \
   --judged '{"accuracy":4,"insight":3,"concision":4,"feedback_fit":5}'
```
`overall = 0.30*recall_5 + 0.15*precision_5 + 0.25*accuracy + 0.15*insight + 0.10*concision + 0.05*feedback_fit`
(`recall_5` and `precision_5` = tool fractions × 5.)

Then `python3 tools/feedback.py trend` gives the 14-day owner-rating and
benchmark trend. Add a 3-line scorecard to the brief:

```
Quality: 4.2/5 (7-day avg 3.9 ↑) · Coverage vs. Reuters/FT/Bloomberg: 82% · Missed: <title> (<outlet>)
Your avg rating (14d): 4.0/5 · Rules learned from feedback: 6
```

## 5. Learn
Any important story that was missed two days running for the same topic means
a query problem. Add a `## Query rules` line to `memory/learned_rules.md`.
