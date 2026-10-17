---
name: boolean-query-builder
description: Turn a topic definition from config/topics.yaml into advanced boolean search queries (web search, Google News, GDELT, NewsAPI dialects) with synonyms, proximity, exclusions and source filters. Use whenever news or market signals must be searched for a topic.
---

# Boolean Query Builder

## Inputs
- A topic block from `config/topics.yaml` (`must`, `exclude`, `regions`, `intent`)
- `memory/learned_rules.md` (query lessons, e.g. "drop 'GPU' alone — too much gaming noise")
- Optional: last run's query log in `memory/briefs/<date>-queries.json`

## Procedure

1. **Expand concepts.** For every `must` group add synonyms, acronyms, spelling
   variants (US/UK), and key entity names (leading companies, agencies). Keep
   groups mutually distinct: one group = one concept.
2. **Build the core query.**
   `(A1 OR A2 OR "a three") AND (B1 OR B2) NOT (X1 OR X2)`
   Quote multi-word phrases. Bracket every OR group.
3. **Make a precision variant and a recall variant.**
   - *Precision*: add proximity or title restriction (`intitle:`, `NEAR/5`, GDELT `near10:"…"`).
   - *Recall*: drop the weakest AND group, keep exclusions.
4. **Add source variants.** One query per trusted tier:
   `<core> (site:reuters.com OR site:ft.com OR site:bloomberg.com)`, using
   `config/trusted_sources.yaml`.
5. **Add region/language variants** when `regions` is not global (e.g.
   `sourcecountry:DE`, local-language terms for the key concepts).
6. **Render dialects** (only the ones the current runtime can use):

| Dialect | AND / OR / NOT | Phrase | Proximity | Site/source | Time |
|---|---|---|---|---|---|
| Web search tool | implicit / `OR` / `-term` | `"…"` | — | `site:` | ask for "past 24 hours" |
| Google News | `AND` `OR` `-` | `"…"` | `AROUND(5)` | `site:` | `when:1d` |
| GDELT DOC 2.0 | space / `OR` in `()` / `-` | `"…"` | `near10:"a b"` | `domain:` `sourcecountry:` `sourcelang:` | `timespan=24h` |
| NewsAPI | `AND` `OR` `NOT` | `"…"` | — | `domains=` param | `from=` |

7. **Log** every query with its hit count and the number of stories kept to
   `memory/briefs/<YYYY-MM-DD>-queries.json`:
   `{"topic": "...", "dialect": "...", "query": "...", "hits": 0, "kept": 0}`.
   A query with 0 hits or < 10% kept rate gets fixed next run (step 8).
8. **Self-tune.** If yesterday's log shows a noisy query, tighten it by adding an
   AND group or exclusion. If it found nothing, loosen it by dropping the
   tightest group. Write any lasting lesson to `memory/learned_rules.md` under
   `## Query rules`.

## Example

Topic: *Quantum computing commercialisation*

```
Core:      ("quantum computing" OR "quantum computer" OR qubit* OR "quantum processor")
           AND (raises OR funding OR "Series A" OR "Series B" OR contract OR partnership OR deploy*)
           -"quantum of solace" -crypto
Precision: intitle:(quantum) AND ("raises" OR "contract" OR "partnership")
Trusted:   <core> (site:reuters.com OR site:ft.com OR site:bloomberg.com OR site:technologyreview.com)
GDELT:     ("quantum computing" OR "quantum computer") (raises OR funding OR contract) sourcelang:english
```
