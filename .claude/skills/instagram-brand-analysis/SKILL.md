---
name: instagram-brand-analysis
description: Analyse Instagram brand pages (your own via Insights, competitors via Business Discovery) - content mix, posting cadence, engagement rates, top formats, caption and hashtag themes, visual identity and audience response. Use for /brand-audit or any Instagram competitive analysis.
---

# Instagram Brand Analysis

## Data access (official API only)
- **Own account** (Instagram Business/Creator account linked to a Facebook Page):
  `python3 tools/instagram_api.py own-media --limit 50` and
  `python3 tools/instagram_api.py own-insights`
- **Competitors** (public Business/Creator accounts only), via Business Discovery:
  `python3 tools/instagram_api.py discover --username <handle> --limit 50`
- Needs `IG_USER_ID` and `META_ACCESS_TOKEN` in the environment. Without them,
  fall back to what's visible on the public web profile. Mark the audit
  "limited data", and **never** log in or scrape behind the login.
- Outputs are saved as JSON in `data/brand/<handle>-<D>.json`.

## Metrics to compute
`python3 tools/instagram_api.py analyze --file data/brand/<handle>-<D>.json` gives:
- Posts per week, and mix by media type (IMAGE / VIDEO=Reels / CAROUSEL_ALBUM)
- Engagement rate per post = (likes + comments) / followers. Report the median,
  not the mean.
- Top and bottom 10% of posts by engagement: what format, topic, hook and
  time of day they share
- Hashtag frequency and the top caption n-grams

## Qualitative audit (look at the top posts' permalinks)
1. **Positioning**: what promise does the brand make in 5 words?
2. **Voice**: tone, use of first person, emoji and CTA habits
3. **Visual identity**: palette, typography, faces vs. product, UGC share
4. **Content pillars**: 3-5 recurring themes and the share of each
5. **Community**: reply rate to comments, creator collaborations

## Output: `data/brand/<handle>-audit-<D>.md`
A benchmark table (own account vs. 3-5 competitors), 5 key insights each
backed by data, and a hand-off to the `branding-strategy` skill.
