#!/usr/bin/env python3
"""Startup profile store, rubric scoring and outcome calibration.

  startup_db.py upsert --file profile.json
  startup_db.py list [--sector quantum] [--stage series-a]
  startup_db.py show --id acme-quantum
  startup_db.py score --id acme-quantum --scores '{"team":4,"technology_moat":3,...}'
  startup_db.py calibrate
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "startups"
EVALS = DB / "evaluations.jsonl"
RUBRIC = ROOT / "config" / "startup_scoring.json"
FEEDBACK = ROOT / "memory" / "feedback" / "feedback.jsonl"

POSITIVE = re.compile(r"\b(raised|series [b-f]|acquired|ipo|listed|profitab\w*|follow-on|up.?round|contract win)\b", re.I)
NEGATIVE = re.compile(r"\b(shut ?down|bankrupt\w*|insolven\w*|down.?round|layoffs?|wound down|ceased|failed)\b", re.I)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def merge(old, new):
    """Deep-ish merge: dicts merge, lists union (by JSON identity), scalars overwrite unless new is None."""
    out = dict(old)
    for k, v in new.items():
        if v is None and k in out:
            continue
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge(out[k], v)
        elif isinstance(v, list) and isinstance(out.get(k), list):
            seen = {json.dumps(x, sort_keys=True) for x in out[k]}
            out[k] = out[k] + [x for x in v if json.dumps(x, sort_keys=True) not in seen]
        else:
            out[k] = v
    return out


def path_for(sid):
    return DB / f"{sid}.json"


def upsert(args):
    new = json.loads(pathlib.Path(args.file).read_text())
    if not new.get("name"):
        sys.exit("profile needs a name")
    sid = new.get("id") or slug(new["name"])
    new["id"] = sid
    new["last_updated"] = dt.date.today().isoformat()
    p = path_for(sid)
    existed = p.exists()
    profile = merge(json.loads(p.read_text()), new) if existed else new
    DB.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(profile, ensure_ascii=False, indent=2))
    print(json.dumps({"id": sid, "status": "updated" if existed else "created", "path": str(p)}))


def profiles():
    for p in sorted(DB.glob("*.json")):
        try:
            yield json.loads(p.read_text())
        except json.JSONDecodeError:
            continue


def list_cmd(args):
    for pr in profiles():
        if args.sector and args.sector.lower() not in (pr.get("sector") or "").lower():
            continue
        if args.stage and args.stage != pr.get("stage"):
            continue
        last = (pr.get("funding") or [{}])[-1]
        print(json.dumps({k: pr.get(k) for k in ("id", "name", "sector", "stage", "hq_country")}
                         | {"last_round": last.get("round"), "last_round_usd": last.get("amount_usd")},
                         ensure_ascii=False))


def show(args):
    p = path_for(args.id)
    if not p.exists():
        sys.exit(f"no profile {args.id}")
    print(p.read_text())


def load_rubric():
    rubric = json.loads(RUBRIC.read_text())
    total = sum(d["weight"] for d in rubric["dimensions"].values())
    if abs(total - 1.0) > 1e-6:
        sys.exit(f"rubric weights sum to {total}, expected 1.0")
    return rubric


def weighted(scores, rubric):
    dims = rubric["dimensions"]
    unknown = set(scores) - set(dims)
    missing = set(dims) - set(scores)
    if unknown:
        raise ValueError(f"unknown dimensions: {sorted(unknown)}")
    if missing:
        raise ValueError(f"missing dimensions: {sorted(missing)}")
    for k, v in scores.items():
        if not 1 <= v <= 5:
            raise ValueError(f"{k} must be 1-5, got {v}")
    total = sum(dims[k]["weight"] * v for k, v in scores.items())
    verdict = next(b["label"] for b in rubric["verdict_bands"] if total >= b["min"])
    return round(total, 2), verdict


def score(args):
    rubric = load_rubric()
    scores = json.loads(args.scores)
    try:
        total, verdict = weighted(scores, rubric)
    except ValueError as e:
        sys.exit(str(e))
    entry = {
        "id": args.id,
        "evaluated_at": dt.date.today().isoformat(),
        "rubric_version": rubric.get("version"),
        "scores": scores,
        "weighted": total,
        "verdict": verdict,
    }
    if not args.no_save:
        EVALS.parent.mkdir(parents=True, exist_ok=True)
        with EVALS.open("a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(json.dumps(entry, ensure_ascii=False, indent=2))


def read_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def outcome_label(text):
    if NEGATIVE.search(text or ""):
        return -1
    if POSITIVE.search(text or ""):
        return 1
    return 0


def calibrate(args):
    evals = read_jsonl(EVALS)
    outcomes = [r for r in read_jsonl(FEEDBACK) if r.get("module") == "startups" and r.get("kind") == "outcome"]
    by_id = {}
    for o in outcomes:
        label = outcome_label(" ".join(filter(None, [o.get("comment"), o.get("change"), o.get("keep")])))
        if label and o.get("subject"):
            by_id.setdefault(o["subject"], []).append((o.get("date", ""), label))

    pairs = []
    for e in evals:
        later = [lab for d, lab in by_id.get(e["id"], []) if d >= e["evaluated_at"]]
        if later:
            pairs.append((e, later[-1]))
    if not pairs:
        print(json.dumps({"evaluations": len(evals), "with_outcomes": 0,
                          "note": "No outcomes after evaluations yet. Log them with feedback.py add --module startups --kind outcome --subject <id>."}, indent=2))
        return

    dims = load_rubric()["dimensions"]
    report = {}
    for d in dims:
        good = [e["scores"][d] for e, lab in pairs if lab > 0 and d in e["scores"]]
        bad = [e["scores"][d] for e, lab in pairs if lab < 0 and d in e["scores"]]
        gap = (statistics.mean(good) - statistics.mean(bad)) if good and bad else None
        report[d] = {"weight": dims[d]["weight"],
                     "mean_score_positive": round(statistics.mean(good), 2) if good else None,
                     "mean_score_negative": round(statistics.mean(bad), 2) if bad else None,
                     "separation": round(gap, 2) if gap is not None else None}
    hits = sum(1 for e, lab in pairs if (e["weighted"] >= 3.3) == (lab > 0))
    print(json.dumps({
        "evaluations": len(evals),
        "with_outcomes": len(pairs),
        "verdict_accuracy": round(hits / len(pairs), 2),
        "dimensions": report,
        "guidance": "Dimensions with separation <= 0 are not predicting outcomes; consider lowering weight by <=0.05 (keep sum 1.0). Need >=8 outcomes before changing weights.",
    }, indent=2))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("upsert"); u.add_argument("--file", required=True); u.set_defaults(func=upsert)
    l = sub.add_parser("list"); l.add_argument("--sector"); l.add_argument("--stage"); l.set_defaults(func=list_cmd)
    s = sub.add_parser("show"); s.add_argument("--id", required=True); s.set_defaults(func=show)
    sc = sub.add_parser("score"); sc.add_argument("--id", required=True); sc.add_argument("--scores", required=True)
    sc.add_argument("--no-save", action="store_true"); sc.set_defaults(func=score)
    c = sub.add_parser("calibrate"); c.set_defaults(func=calibrate)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
