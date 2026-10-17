#!/usr/bin/env python3
"""Append-only feedback log and quality trends.

  feedback.py add --module news --date 2026-10-17 --rating 4 --keep "..." --change "..."
  feedback.py add --module startups --kind outcome --subject acme-quantum --comment "Raised Series B"
  feedback.py trend [--days 14]
  feedback.py list [--module news] [--limit 20]
"""
import argparse
import datetime as dt
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "memory" / "feedback" / "feedback.jsonl"
BENCH_DIR = ROOT / "memory" / "benchmarks"
MODULES = ("news", "startups", "brand")
KINDS = ("rating", "outcome")


def load(path=LOG):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def add(args):
    if args.rating is not None and not 1 <= args.rating <= 5:
        sys.exit("rating must be 1-5")
    entry = {
        "logged_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "module": args.module,
        "kind": args.kind,
        "date": args.date or dt.date.today().isoformat(),
        "subject": args.subject,
        "rating": args.rating,
        "keep": args.keep,
        "change": args.change,
        "comment": args.comment,
        "source": args.source,
    }
    entry = {k: v for k, v in entry.items() if v is not None}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(json.dumps(entry, ensure_ascii=False))


def bench_scores(since):
    out = {}
    for p in sorted(BENCH_DIR.glob("????-??-??.json")):
        day = p.stem
        if day < since:
            continue
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        if "overall" in data:
            out[day] = data["overall"]
    return out


def trend(args):
    today = dt.date.today()
    since = (today - dt.timedelta(days=args.days)).isoformat()
    half = (today - dt.timedelta(days=args.days // 2)).isoformat()
    ratings = [r for r in load() if r.get("module") == args.module
               and r.get("kind", "rating") == "rating"
               and r.get("rating") is not None and r.get("date", "") >= since]

    def avg(vals):
        return round(statistics.mean(vals), 2) if vals else None

    older = avg([r["rating"] for r in ratings if r["date"] < half])
    recent = avg([r["rating"] for r in ratings if r["date"] >= half])
    bench = bench_scores(since)
    b_older = avg([v for d, v in bench.items() if d < half])
    b_recent = avg([v for d, v in bench.items() if d >= half])

    def arrow(a, b):
        if a is None or b is None:
            return "–"
        return "↑" if b > a + 0.05 else "↓" if b < a - 0.05 else "→"

    result = {
        "window_days": args.days,
        "owner_rating_avg": avg([r["rating"] for r in ratings]),
        "owner_rating_trend": arrow(older, recent),
        "owner_ratings_n": len(ratings),
        "benchmark_avg": avg(list(bench.values())),
        "benchmark_trend": arrow(b_older, b_recent),
        "benchmark_days": len(bench),
        "recent_change_requests": [r["change"] for r in ratings if r.get("change")][-5:],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def list_cmd(args):
    rows = load()
    if args.module:
        rows = [r for r in rows if r.get("module") == args.module]
    for r in rows[-args.limit:]:
        print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--module", choices=MODULES, default="news")
    a.add_argument("--kind", choices=KINDS, default="rating")
    a.add_argument("--date")
    a.add_argument("--subject", help="startup id / brand handle / brief date")
    a.add_argument("--rating", type=int)
    a.add_argument("--keep")
    a.add_argument("--change")
    a.add_argument("--comment")
    a.add_argument("--source", default="cli", help="email | cli | chat")
    a.set_defaults(func=add)

    t = sub.add_parser("trend")
    t.add_argument("--module", choices=MODULES, default="news")
    t.add_argument("--days", type=int, default=14)
    t.set_defaults(func=trend)

    l = sub.add_parser("list")
    l.add_argument("--module", choices=MODULES)
    l.add_argument("--limit", type=int, default=20)
    l.set_defaults(func=list_cmd)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
