#!/usr/bin/env python3
"""Meta Marketing API - PAUSED-only campaign drafts with hard budget caps.

  meta_ads.py validate --plan data/ads/<slug>/plan.json
  meta_ads.py create   --plan data/ads/<slug>/plan.json [--dry-run | --live]
  meta_ads.py insights --campaign-id 123 [--days 7]

`create` defaults to --dry-run (prints payloads, no API calls). Everything is
created with status=PAUSED; this tool has no way to activate spend.
Requires META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, META_PAGE_ID (and IG_USER_ID
for Instagram placements) when --live.
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from graph_client import GUARDRAILS, env, request  # noqa: E402

PAUSED = "PAUSED"


def guardrails():
    return json.loads(GUARDRAILS.read_text())


def validate_plan(plan, rails=None):
    """Return a list of problems; empty list means the plan is within guardrails."""
    rails = rails or guardrails()
    errors = []
    for key in ("campaign", "adset", "creative", "ad"):
        if key not in plan:
            errors.append(f"missing section: {key}")
    if errors:
        return errors
    camp, adset = plan["campaign"], plan["adset"]
    if camp.get("objective") not in rails["allowed_objectives"]:
        errors.append(f"objective {camp.get('objective')} not in {rails['allowed_objectives']}")
    for section in ("campaign", "adset", "ad"):
        status = plan[section].get("status", PAUSED)
        if status not in rails["allowed_status"]:
            errors.append(f"{section}.status={status} is not allowed (PAUSED only)")
    daily, lifetime = adset.get("daily_budget"), adset.get("lifetime_budget")
    if daily is None and lifetime is None:
        errors.append("adset needs daily_budget or lifetime_budget (minor units)")
    if daily is not None and (not isinstance(daily, int) or daily <= 0 or daily > rails["max_daily_budget_minor_units"]):
        errors.append(f"daily_budget {daily} exceeds cap {rails['max_daily_budget_minor_units']} or is invalid")
    if lifetime is not None and (not isinstance(lifetime, int) or lifetime <= 0 or lifetime > rails["max_lifetime_budget_minor_units"]):
        errors.append(f"lifetime_budget {lifetime} exceeds cap {rails['max_lifetime_budget_minor_units']} or is invalid")
    if lifetime is not None and not adset.get("end_time"):
        errors.append("lifetime_budget requires adset.end_time")
    for f in ("optimization_goal", "billing_event", "targeting"):
        if not adset.get(f):
            errors.append(f"adset.{f} is required")
    if not (adset.get("targeting") or {}).get("geo_locations"):
        errors.append("adset.targeting.geo_locations is required")
    cr = plan["creative"]
    for f in ("link", "message"):
        if not cr.get(f):
            errors.append(f"creative.{f} is required")
    return errors


def payloads(plan, account="<META_AD_ACCOUNT_ID>", page="<META_PAGE_ID>", ig_user=None):
    camp, adset, cr, ad = plan["campaign"], plan["adset"], plan["creative"], plan["ad"]
    campaign = {"name": camp["name"], "objective": camp["objective"], "status": PAUSED,
                "special_ad_categories": camp.get("special_ad_categories", []),
                "is_adset_budget_sharing_enabled": False}
    adset_p = {k: adset[k] for k in ("name", "optimization_goal", "billing_event", "targeting") if k in adset}
    adset_p.update({"status": PAUSED, "bid_strategy": adset.get("bid_strategy", "LOWEST_COST_WITHOUT_CAP"),
                    "campaign_id": "<from campaign>"})
    for k in ("daily_budget", "lifetime_budget", "start_time", "end_time"):
        if adset.get(k) is not None:
            adset_p[k] = adset[k]
    link_data = {"link": cr["link"], "message": cr["message"]}
    if cr.get("image_hash"):
        link_data["image_hash"] = cr["image_hash"]
    elif cr.get("image_url"):
        link_data["picture"] = cr["image_url"]
    if cr.get("headline"):
        link_data["name"] = cr["headline"]
    if cr.get("call_to_action"):
        link_data["call_to_action"] = {"type": cr["call_to_action"], "value": {"link": cr["link"]}}
    story = {"page_id": page, "link_data": link_data}
    if ig_user:
        story["instagram_user_id"] = ig_user
    creative = {"name": cr.get("name", camp["name"] + " creative"), "object_story_spec": story}
    ad_p = {"name": ad.get("name", camp["name"] + " ad"), "status": PAUSED,
            "adset_id": "<from adset>", "creative": {"creative_id": "<from creative>"}}
    return {"account": f"act_{account}", "campaign": campaign, "adset": adset_p, "creative": creative, "ad": ad_p}


def assert_paused(p):
    for k in ("campaign", "adset", "ad"):
        if p[k].get("status") != PAUSED:
            raise SystemExit(f"refusing: {k} status is not PAUSED")


def load_plan(path):
    return json.loads(pathlib.Path(path).read_text())


def cmd_validate(args):
    errors = validate_plan(load_plan(args.plan))
    print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    sys.exit(1 if errors else 0)


def cmd_create(args):
    plan = load_plan(args.plan)
    errors = validate_plan(plan)
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        sys.exit(1)
    if not args.live:
        print(json.dumps({"mode": "dry-run", "payloads": payloads(plan)}, indent=2, ensure_ascii=False))
        return
    account, page = env("META_AD_ACCOUNT_ID").removeprefix("act_"), env("META_PAGE_ID")
    p = payloads(plan, account, page, os.environ.get("IG_USER_ID"))
    assert_paused(p)
    act = p["account"]
    camp = request("POST", f"{act}/campaigns", p["campaign"])
    p["adset"]["campaign_id"] = camp["id"]
    adset = request("POST", f"{act}/adsets", p["adset"])
    creative = request("POST", f"{act}/adcreatives", p["creative"])
    p["ad"]["adset_id"], p["ad"]["creative"] = adset["id"], {"creative_id": creative["id"]}
    ad = request("POST", f"{act}/ads", p["ad"])
    created = {"created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "status": PAUSED,
               "campaign_id": camp["id"], "adset_id": adset["id"], "creative_id": creative["id"], "ad_id": ad["id"]}
    out = pathlib.Path(args.plan).with_name("created.json")
    out.write_text(json.dumps(created, indent=2))
    print(json.dumps(created, indent=2))
    print("All objects are PAUSED. Review and activate them in Ads Manager.")


def cmd_insights(args):
    until = dt.date.today()
    since = until - dt.timedelta(days=args.days)
    res = request("GET", f"{args.campaign_id}/insights", {
        "level": "ad",
        "fields": "ad_name,impressions,reach,frequency,clicks,ctr,cpc,cpm,spend,actions",
        "time_range": {"since": since.isoformat(), "until": until.isoformat()},
    })
    print(json.dumps(res.get("data", []), indent=2))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate"); v.add_argument("--plan", required=True); v.set_defaults(func=cmd_validate)
    c = sub.add_parser("create"); c.add_argument("--plan", required=True)
    mode = c.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", default=True)
    mode.add_argument("--live", action="store_true")
    c.set_defaults(func=cmd_create)
    i = sub.add_parser("insights"); i.add_argument("--campaign-id", required=True); i.add_argument("--days", type=int, default=7)
    i.set_defaults(func=cmd_insights)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
