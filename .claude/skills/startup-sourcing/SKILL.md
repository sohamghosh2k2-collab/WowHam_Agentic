---
name: startup-sourcing
description: Discover and profile early-stage and growth-stage deep-tech startups from public sources (funding news, accelerators, research/patent and hiring signals, government grants) into structured profiles in data/startups/. Use for /scout or when building a deal-flow list.
---

# Startup Sourcing

## Scope
Read `config/startup_focus.yaml` for sectors, stages, regions and allowed sources.

## Discovery passes (run the ones that fit the request)
1. **Funding news** (last 7-30 days) using the `boolean-query-builder`:
   `(startup OR spinout) AND (<sector terms>) AND (raises OR "seed round" OR "Series A" OR "Series B")`
2. **Accelerator batches**: the public company directories listed in the config.
3. **Research to company**: arXiv/patent authors who show up as founders or
   CTOs; university spinout announcements.
4. **Government signals**: SBIR/STTR awards, EIC Accelerator, Horizon Europe
   (CORDIS) and ARPA-E selections. These are strong signals of technical
   credibility.
5. **Hiring signals**: public careers pages. A jump in hiring for manufacturing,
   regulatory or sales roles usually means a move from R&D toward commercial work.

## Rules
- Use only public pages that allow access. Follow robots.txt, don't log in, and
  don't get around paywalls. Use paid APIs only when their key is in the
  environment.
- Every field carries a `source` URL. Unknown values are `null`, never guessed.
- Be careful with people's data: only founders' public professional
  information (role, prior company, degree). No personal contact details.

## Profile schema (save with `tools/startup_db.py upsert`)

```json
{
  "id": "slug-of-name",
  "name": "...", "website": "...", "hq_country": "DE",
  "sector": "quantum", "subsector": "trapped-ion hardware",
  "stage": "series-a", "founded": 2021,
  "one_liner": "...",
  "founders": [{"name": "...", "role": "CEO", "background": "...", "source": "..."}],
  "funding": [{"date": "2025-03-01", "round": "Series A", "amount_usd": 20000000,
               "lead": "...", "investors": ["..."], "source": "..."}],
  "signals": {"trl": 4, "patents": 3, "gov_grants": ["EIC 2024"], "pilots": ["..."],
              "headcount_trend": "up", "hiring_focus": ["manufacturing"]},
  "sources": ["..."],
  "last_updated": "YYYY-MM-DD"
}
```

```
python3 tools/startup_db.py upsert --file /path/profile.json
python3 tools/startup_db.py list --sector quantum --stage series-a
```

## Output
A table of new and updated companies (name, sector, stage, last round, why it's
interesting), followed by a hand-off to `startup-evaluator` for the top 3-5.
