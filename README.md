# Wowham_AGENTIC

A business-intelligence and market-research agent for Claude Code, built in
the [ECC](https://github.com/affaan-m/ECC) format (agents, skills, commands,
hooks, memory).

| # | Module | What it does |
|---|---|---|
| 1 | **Global news brief** | Builds advanced boolean queries from your topics, collects and verifies the last 24 h of news, benchmarks the brief against Reuters/FT/Bloomberg/etc., and emails it to you at 10:00 CET. It learns from your email replies. |
| 2 | **Deep-tech startup intelligence** | Finds and profiles early and growth-stage deep-tech startups from public sources. Scores them on a weighted 9-dimension rubric, compares them with historical trajectories (patterns P1-P9), and writes investment memos. It calibrates itself against real outcomes. |
| 3 | **Instagram brand + Meta ads** | Analyses your account and competitor Instagram pages through the official Graph API, builds a data-backed branding strategy and content calendar, and creates Meta ad campaigns as **PAUSED drafts** within hard budget caps. |

## Layout

```
CLAUDE.md                     orchestrator rules (read first by Claude)
.claude/agents/               news-analyst, report-critic, startup-scout,
                              startup-evaluator, brand-strategist, meta-ads-operator
.claude/skills/               boolean-query-builder, daily-news-brief, source-benchmarking,
                              feedback-learning, startup-sourcing, deeptech-startup-evaluation,
                              instagram-brand-analysis, branding-strategy, meta-ads-campaigns
.claude/commands/             /daily-brief /feedback /scout /evaluate /brand-audit /ads-draft
.claude/hooks/ads_guard.py    blocks ad activation and edits to guardrail files
.claude/scheduled/daily-run.md   prompt used by the 09:40 CET scheduled task
config/                       topics, trusted sources, delivery, startup focus + scoring, ad caps
memory/                       learned_rules.md, feedback log, briefs, benchmarks (the agent's memory)
data/                         startups, trajectories, brand audits, ad drafts
tools/                        stdlib-only Python helpers (run with --help)
tests/                        python3 -m unittest discover -s tests
```

## Using it

Open the repo in Claude Code and run:

```
/daily-brief --no-email          # preview today's brief
/feedback news 3 too long, more on India deep tech
/scout quantum series-a EU
/evaluate <startup>
/brand-audit myhandle vs competitor1 competitor2 goal: leads
/ads-draft data/brand/strategy-<date>.md 15/day
```

### Giving feedback on the daily email
Reply to the email:
```
Rating: 4
Keep: the "so what" lines
Change: fewer chip stories, more on fusion
```
The next run reads your reply, logs it in `memory/feedback/feedback.jsonl`,
turns it into rules in `memory/learned_rules.md`, and tells you what changed in
the scorecard.

## How the learning works
- **News**: each brief gets two independent scores. One is your rating; the
  other is a benchmark (importance-weighted coverage of what trusted outlets
  reported, source quality, a fact-check, and fit with your rules). Missed
  stories feed back into the boolean queries.
- **Startups**: every evaluation is saved with a timestamp. When later news
  shows an outcome (new round, shutdown, exit), `startup_db.py calibrate` shows
  which rubric dimensions predicted it. Weights change by at most ±0.05 at a
  time, and every change is logged.
- **Brand/ads**: ad performance and your feedback turn into
  `## Brand & ads rules`.

## Setup

1. **Topics**: edit `config/topics.yaml`.
2. **Email**: the scheduled task uses the Gmail connector and sends from your
   own account to `config/delivery.json → email_to`.
3. **Meta (module 3)**: set the variables from `.env.example` as environment
   secrets. You need an Instagram Business/Creator account linked to a Facebook
   Page, plus a Meta app with a system-user token
   (`instagram_basic`, `instagram_manage_insights`, `pages_read_engagement`,
   `ads_management`, `ads_read`).
4. **Network**: the scheduled task uses web search and fetch. To call
   `graph.facebook.com` or other APIs directly from a cloud session, add those
   domains to the environment's allowed domains.

## Safety
- Ads are created **PAUSED only**, with caps of €20/day and €300 lifetime by
  default (`config/ads_guardrails.json`). Only you can raise them. You
  activate campaigns in Ads Manager.
- The agent uses official APIs and public, permitted pages only: no logins,
  no paywall workarounds, and no personal data beyond founders' public
  professional information.
- Everything it reports must have a source. Missing data is reported as
  missing, never estimated silently.
- Startup memos are research, not investment advice.

## ECC skills included
`market-research`, `competitive-platform-analysis` and `brand-voice` are
copied unchanged from [affaan-m/ECC](https://github.com/affaan-m/ECC) at commit
`76aaa77` (MIT license, see `.claude/skills/ECC-LICENSE`). Other ECC skills that
fit, such as `deep-research` (needs Exa/Firecrawl), `marketing-campaign`,
`investor-materials` and `continuous-learning-v2`, can be copied the same way.
