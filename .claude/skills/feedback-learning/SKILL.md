---
name: feedback-learning
description: Capture owner feedback (email replies or /feedback) on briefs, startup evaluations and brand strategies, and distil it into durable rules in memory/learned_rules.md. Use at the start of every run and whenever the owner comments on output quality.
---

# Feedback Learning

Pattern adapted from ECC's continuous-learning skill: observations →
instincts → rules, with confidence and evidence.

## Feedback format (printed in every brief footer)

```
Reply to this email with:
Rating: 1-5
Keep: <what was useful>
Change: <what to fix>
Topic+: <add/boost a topic>    Topic-: <drop/reduce a topic>
```
Free text is fine too. Interpret it and leave fields empty if they are unclear.

## Procedure

1. **Log raw feedback** (never edit past entries):
   `python3 tools/feedback.py add --module news|startups|brand --date <D> --rating N --keep "..." --change "..." --comment "..."`
2. **Extract candidate lessons.** One lesson = one actionable, testable rule.
   - "Too long" → `Style: keep each bullet ≤ 25 words` (concrete, not "be shorter").
   - "More on India" → topic config change, which needs step 4.
3. **Update `memory/learned_rules.md`.** Each rule carries
   `[confidence: low|medium|high] [evidence: <dates>]`.
   - New lesson → add as `low`.
   - Same lesson again, or the rating went up after applying it → raise confidence.
   - A later contradicting comment → lower confidence or remove the rule, and
     note why under `## Retired`.
   - Keep at most ~25 active rules. Merge similar ones.
4. **Config changes** (topics, sources, scoring weights): make the edit and
   record it under `## Change log` with the feedback date that caused it.
   Don't change a scoring weight by more than ±0.05 for one piece of feedback.
5. **Close the loop.** The next brief's scorecard says which rule changed:
   "Applied your feedback from <date>: <rule>".

## Outcome learning (startups module)
When later news confirms or refutes a past evaluation (new round, down round,
shutdown, exit), log it with
`python3 tools/feedback.py add --module startups --kind outcome ...`
and review it with the `deeptech-startup-evaluation` skill's calibration step.
