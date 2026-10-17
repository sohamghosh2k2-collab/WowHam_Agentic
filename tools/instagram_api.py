#!/usr/bin/env python3
"""Instagram Graph API helpers for brand analysis (official API only).

  instagram_api.py own-media [--limit 50] [--out file.json]
  instagram_api.py own-insights [--metrics reach,follower_count] [--period day]
  instagram_api.py discover --username competitor [--limit 50] [--out file.json]
  instagram_api.py analyze --file data/brand/<handle>-<date>.json

Requires IG_USER_ID (your Business/Creator account id) and META_ACCESS_TOKEN.
`discover` only works for public Business/Creator accounts (Business Discovery).
"""
import argparse
import collections
import datetime as dt
import json
import pathlib
import re
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from graph_client import ROOT, env, request  # noqa: E402

MEDIA_FIELDS = "id,caption,media_type,media_product_type,like_count,comments_count,timestamp,permalink"
STOP = set("the and for you your with this that our are from have will just more all what about into".split())


def save(data, out, handle):
    path = pathlib.Path(out) if out else ROOT / "data" / "brand" / f"{handle}-{dt.date.today().isoformat()}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"saved {path}")


def own_media(args):
    ig = env("IG_USER_ID")
    profile = request("GET", ig, {"fields": "username,followers_count,media_count"})
    media = request("GET", f"{ig}/media", {"fields": MEDIA_FIELDS, "limit": args.limit}).get("data", [])
    save({"username": profile.get("username"), "followers_count": profile.get("followers_count"),
          "media_count": profile.get("media_count"), "media": media, "source": "own"}, args.out, profile.get("username", "own"))


def own_insights(args):
    ig = env("IG_USER_ID")
    print(json.dumps(request("GET", f"{ig}/insights", {"metric": args.metrics, "period": args.period}), indent=2))


def discover(args):
    ig = env("IG_USER_ID")
    if not re.fullmatch(r"[A-Za-z0-9._]{1,30}", args.username):
        sys.exit("invalid username")
    fields = (f"business_discovery.username({args.username})"
              f"{{username,name,biography,followers_count,media_count,"
              f"media.limit({args.limit}){{caption,media_type,media_product_type,like_count,comments_count,timestamp,permalink}}}}")
    bd = request("GET", ig, {"fields": fields}).get("business_discovery", {})
    data = {k: bd.get(k) for k in ("username", "name", "biography", "followers_count", "media_count")}
    data["media"] = (bd.get("media") or {}).get("data", [])
    data["source"] = "business_discovery"
    save(data, args.out, args.username)


def analyze_data(data):
    media = data.get("media") or []
    followers = data.get("followers_count") or 0
    if not media:
        return {"username": data.get("username"), "error": "no media"}
    for m in media:
        eng = (m.get("like_count") or 0) + (m.get("comments_count") or 0)
        m["_eng"] = eng
        m["_er"] = eng / followers if followers else None
        m["_fmt"] = "REELS" if m.get("media_product_type") == "REELS" else m.get("media_type", "UNKNOWN")
    times = sorted(dt.datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00")) for m in media if m.get("timestamp"))
    weeks = max((times[-1] - times[0]).days / 7, 1) if len(times) > 1 else 1
    by_fmt = collections.defaultdict(list)
    for m in media:
        if m["_er"] is not None:
            by_fmt[m["_fmt"]].append(m["_er"])
    ranked = sorted(media, key=lambda m: m["_eng"], reverse=True)
    k = max(1, len(media) // 10)
    hashtags = collections.Counter(h.lower() for m in media for h in re.findall(r"#(\w+)", m.get("caption") or ""))
    words = collections.Counter(w for m in media for w in re.findall(r"[a-z]{4,}", re.sub(r"#\w+", "", (m.get("caption") or "").lower())) if w not in STOP)
    hours = collections.Counter(t.hour for t in times)

    def brief(m):
        return {"permalink": m.get("permalink"), "format": m["_fmt"], "engagement": m["_eng"],
                "caption": (m.get("caption") or "")[:120], "timestamp": m.get("timestamp")}

    ers = [m["_er"] for m in media if m["_er"] is not None]
    return {
        "username": data.get("username"),
        "followers": followers,
        "posts_analyzed": len(media),
        "posts_per_week": round(len(media) / weeks, 2),
        "format_mix": dict(collections.Counter(m["_fmt"] for m in media)),
        "median_engagement_rate": round(statistics.median(ers), 4) if ers else None,
        "median_er_by_format": {f: round(statistics.median(v), 4) for f, v in by_fmt.items()},
        "top_posts": [brief(m) for m in ranked[:k]],
        "bottom_posts": [brief(m) for m in ranked[-k:]],
        "top_hashtags": hashtags.most_common(15),
        "top_caption_terms": words.most_common(20),
        "posting_hours_utc": dict(sorted(hours.items())),
    }


def analyze(args):
    print(json.dumps(analyze_data(json.loads(pathlib.Path(args.file).read_text())), ensure_ascii=False, indent=2))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("own-media"); a.add_argument("--limit", type=int, default=50); a.add_argument("--out"); a.set_defaults(func=own_media)
    b = sub.add_parser("own-insights"); b.add_argument("--metrics", default="reach,follower_count"); b.add_argument("--period", default="day"); b.set_defaults(func=own_insights)
    c = sub.add_parser("discover"); c.add_argument("--username", required=True); c.add_argument("--limit", type=int, default=50); c.add_argument("--out"); c.set_defaults(func=discover)
    d = sub.add_parser("analyze"); d.add_argument("--file", required=True); d.set_defaults(func=analyze)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
