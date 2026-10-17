# Learned rules

Rules distilled from owner feedback and benchmark results. The agent reads this
file before every run. Format:
`- <rule> [confidence: low|medium|high] [evidence: YYYY-MM-DD, ...]`

## Style rules
- Lead every bullet with the fact, then the implication. [confidence: low] [evidence: default]

## Query rules
- Don't put reuters.com, ft.com, wsj.com, apnews.com or economist.com in web-search domain filters; the search tool rejects them. Reach their coverage through syndication (e.g. WSJ via Placera, Bloomberg via The Star) or general queries. [confidence: high] [evidence: 2026-10-17]
- For the trusted-source benchmark pass, use bloomberg.com, techcrunch.com, technologyreview.com, sifted.eu, nature.com and spectrum.ieee.org. [confidence: medium] [evidence: 2026-10-17]
- Page fetches failed for hpcwire.com and thenextweb.com; verify their stories through a second outlet instead. [confidence: low] [evidence: 2026-10-17]

## Startup evaluation rules

## Brand & ads rules

## Change log
- 2026-10-17: first (test) run. Precision vs tier-1/2 was 29% because funding news lives in trade press (tech.eu, dealroom). Owner to decide whether to add tech.eu/dealroom.co to tier 2.

## Retired
