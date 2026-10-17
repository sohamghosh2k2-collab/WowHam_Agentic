---
name: daily-news-brief
description: End-to-end workflow for the daily 10:00 CET global news brief - collect feedback replies, build boolean queries, gather and de-duplicate stories, summarise, benchmark against trusted sources, and email the report. Use for /daily-brief and for the scheduled daily run.
---

# Daily News Brief

Run these steps in order. Each step writes a file so a failed run can resume.
`<D>` = today's date in Europe/Berlin (YYYY-MM-DD).

## 0. Learn from yesterday (feedback first)
1. Search Gmail for replies to previous briefs: subject contains the
   `subject_prefix` from `config/delivery.json`, newer than the last entry in
   `memory/feedback/feedback.jsonl`.
2. For each reply, extract the rating and comments (format in the
   `feedback-learning` skill) and log it:
   `python3 tools/feedback.py add --date <brief-date> --rating N --comment "..." --source email`
3. Apply the `feedback-learning` skill to update `memory/learned_rules.md`.

## 1. Plan queries
For each topic in `config/topics.yaml`, use the `boolean-query-builder` skill.
Save queries to `memory/briefs/<D>-queries.json`.

## 2. Collect (delegate to `news-analyst`)
- Search window: last 24 hours (Monday: since Friday 10:00).
- Run the precision, recall and trusted-source variants for each topic.
- For each candidate keep: title, outlet, URL, published time, 1-2 key facts.
- **De-duplicate**: one story = one event. Merge coverage from several outlets
  into one item and list all of them. More outlets = higher confidence.
- **Verify**: a story whose only source is low-trust (see
  `config/trusted_sources.yaml`) goes under "Unconfirmed".
- Save to `memory/briefs/<D>-stories.json`.

## 3. Rank and summarise
Score each story: relevance to the topic `intent` (0-3) + impact (0-3) +
novelty vs. the last 7 briefs (0-2) + source strength (0-2). Keep the top
`max_stories_per_topic`. Follow every style rule in `memory/learned_rules.md`.

Brief template (HTML email; keep the plain-text version identical):

```
Wowham Daily Brief — <D>
Top 3 today (one line each, why it matters)

## <Topic name>
• <Headline-style sentence>. <So-what in one sentence>. [Outlet1] [Outlet2]
...
Signals to watch: <1-2 forward-looking bullets>

## Unconfirmed / single-source
## Quality scorecard   ← from step 4
## How to give feedback ← fixed footer, see feedback-learning skill
```

Save as `memory/briefs/<D>-brief.md`.

## 4. Benchmark (delegate to `report-critic`)
Use the `source-benchmarking` skill. Add the scorecard to the brief and save
`memory/benchmarks/<D>.json`.
If the critic's overall score is < 3.5/5, fix the problems it lists **once**,
then score again before sending.

## 5. Deliver
Send the brief with the Gmail connector to `email_to` in `config/delivery.json`,
subject `"<subject_prefix> — <D>"`. Send it from the owner's own account to
themselves. Never send it to anyone else.
If sending fails, save the brief and report the error. Never claim it was sent.

## 6. Persist
`git add memory/ && git commit -m "brief: <D>" && git push`.
