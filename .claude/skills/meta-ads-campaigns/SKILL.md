---
name: meta-ads-campaigns
description: Plan and create Meta (Facebook/Instagram) ad campaigns through the Marketing API as PAUSED drafts within hard budget caps - campaign, ad set, creative and ad - plus read-only performance reporting and optimisation suggestions. Use for /ads-draft or any Meta ads task. Never activates spend.
---

# Meta Ads Campaigns (drafts only)

## Safety model (non-negotiable)
- Everything is created with `status=PAUSED`. The owner activates it in Ads Manager.
- Budgets must be ≤ the caps in `config/ads_guardrails.json`. `tools/meta_ads.py`
  refuses anything over the caps, and the PreToolUse hook blocks any command
  that tries to set ACTIVE.
- The default is `--dry-run`, which prints the API payloads only. Pass `--live`
  only once the owner has approved the plan in this session.
- Never change the caps file yourself.

## Prerequisites (environment)
`META_ACCESS_TOKEN` (a system-user token with `ads_management`), `META_AD_ACCOUNT_ID`
(without `act_`), `META_PAGE_ID`, and `IG_USER_ID` for Instagram placements.

## Workflow
1. **Plan**: write `data/ads/<campaign-slug>/plan.json`:
```json
{
  "campaign": {"name": "Q4 Awareness - Reels winners", "objective": "OUTCOME_TRAFFIC"},
  "adset": {"name": "DE 25-44 deep-tech interest", "daily_budget": 1500,
            "optimization_goal": "LINK_CLICKS", "billing_event": "IMPRESSIONS",
            "targeting": {"geo_locations": {"countries": ["DE"]}, "age_min": 25, "age_max": 44,
                          "publisher_platforms": ["instagram"]},
            "start_time": "2026-11-01T09:00:00+0100"},
  "creative": {"name": "Reel winner 1", "link": "https://example.com",
               "message": "...", "image_url": "https://...", "call_to_action": "LEARN_MORE"},
  "ad": {"name": "Ad 1"}
}
```
   Write 2-3 creative variants for A/B testing. Base the copy on the
   `branding-strategy` messaging house.
2. **Validate**: `python3 tools/meta_ads.py validate --plan data/ads/<slug>/plan.json`
3. **Show the owner** the plan and the dry-run payloads:
   `python3 tools/meta_ads.py create --plan ... --dry-run`
4. **Create the PAUSED drafts** after approval:
   `python3 tools/meta_ads.py create --plan ... --live`. The returned IDs go to
   `data/ads/<slug>/created.json`.
5. **Report** (read-only, any time):
   `python3 tools/meta_ads.py insights --campaign-id <id> --days 7`
   Report CTR, CPC, CPM, frequency and results per creative. Suggest changes:
   pause the losers, move budget to the winners, refresh creatives when
   frequency is above 3. **Suggest only.** Changes to spend need the owner.
6. **Learn**: log the owner's feedback on the ad results with `tools/feedback.py`
   (`--module brand`). Add lasting lessons to `## Brand & ads rules`.

## Policy
Follow Meta's advertising standards. Declare `special_ad_categories` (housing,
employment, credit, social issues/politics) when they apply. Target
broad-interest audiences only. Never target sensitive personal traits.
