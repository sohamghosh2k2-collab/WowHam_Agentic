---
name: deeptech-startup-evaluation
description: Evaluate a deep-tech startup with a weighted 9-dimension rubric, compare it with historical trajectories of similar companies and industry patterns, and write an investment-style memo with risks, comparables and a verdict. Includes calibration from outcomes and owner feedback. Use for /evaluate or any startup due-diligence question.
---

# Deep-Tech Startup Evaluation

## Inputs
- A profile from `data/startups/<id>.json`. If it's missing, run `startup-sourcing` first.
- Rubric: `config/startup_scoring.json`
- Patterns: `references/trajectory-patterns.md`
- Historical cases: `data/trajectories/reference_cases.jsonl`
- Lessons: `## Startup evaluation rules` in `memory/learned_rules.md`

## Procedure

1. **Fill the gaps.** Run targeted searches for anything the rubric needs that
   the profile lacks: team background, TRL evidence, customers, competitors,
   regulatory path. Update the profile.
2. **Score each dimension 1-5** with a one-line justification and a source.
   If the evidence is missing, score 2 and say "insufficient evidence". Never
   give a 3 by default.
3. **Compute the weighted score:**
   `python3 tools/startup_db.py score --id <id> --scores '{"team":4,...}'`
   It returns the weighted score, the verdict band, and stores the evaluation
   with a timestamp so it can be checked against outcomes later.
4. **Find comparables.** Pick 3-5 reference cases with the same sector,
   business model (hardware / platform / software-on-science) and capital
   profile. For each one, say what this startup shares with it and how it
   differs. Use the patterns file to name which pattern applies.
5. **Stress-test.** Write the bear case: the most likely way this company fails,
   based on the patterns (e.g. "valley of death between pilot and
   manufacturing scale-up"). Then list the 3 milestones in the next 18 months
   that would prove the bear case wrong.
6. **Write the memo** to `data/startups/<id>-memo.md`:

```
# <Name> — <Verdict> (<score>/5)
One-liner · Stage · Last round · HQ
## Thesis (3 bullets)
## Scorecard (table: dimension | score | why | source)
## Comparables & pattern match
## Bear case & key risks
## Milestones to watch (with dates)
## Open questions for founders
## Sources
```

## Calibration (monthly, or when outcomes come in)
- `python3 tools/startup_db.py calibrate` lists past evaluations that now have
  outcomes (from `memory/feedback/feedback.jsonl`, kind=outcome) and shows how
  each dimension score related to the outcome.
- If one dimension keeps failing to predict outcomes, propose a weight change
  of at most ±0.05 and record it in `memory/learned_rules.md`. Weights must
  still sum to 1.0.
- Owner feedback on memos ("you overrated the team") goes into
  `## Startup evaluation rules`.
