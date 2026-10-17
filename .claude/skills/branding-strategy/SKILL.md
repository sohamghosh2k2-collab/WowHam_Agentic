---
name: branding-strategy
description: Turn Instagram audits and market intelligence into a branding strategy - positioning, audience personas, messaging house, content pillars, 30-day content calendar and paid-amplification plan with measurable KPIs. Use after instagram-brand-analysis or when asked for brand/marketing strategy.
---

# Branding Strategy

## Inputs
The latest audits in `data/brand/`, relevant market signals from recent briefs
(`memory/briefs/`), `## Brand & ads rules` in `memory/learned_rules.md`, and
the owner's goals. Ask for goals once if they're unknown: awareness, leads,
sales, recruiting.

## Deliverable: `data/brand/strategy-<D>.md`

1. **Diagnosis**: 3 findings from the audit, each with a number
   ("Competitor Reels get 2.4x the median engagement of our carousels").
2. **Positioning statement**: For <audience> who <need>, <brand> is the
   <category> that <key benefit>, because <reason to believe>.
3. **Audience personas (2-3)**: jobs-to-be-done, objections, and where they
   spend time online.
4. **Messaging house**: one core message, 3 pillars, and the proof points for each.
5. **Content system**: pillars mapped to formats, with the posting cadence and
   formats taken from what works in the audit data, not general best practice.
6. **30-day calendar**: date, pillar, format, hook, CTA, and whether to
   promote it with paid ads (Y/N).
7. **Paid plan**: which organic winners to boost, the audiences, and a test
   budget that stays within `config/ads_guardrails.json`. Hand off to
   `meta-ads-campaigns`.
8. **KPIs and review dates**: median engagement rate, follower growth, CTR,
   CPC/CPL, and the target for each.

## Rules
- Every recommendation must point back to a data point or a cited source.
- Stay within Meta's advertising standards. No claims you can't substantiate.
