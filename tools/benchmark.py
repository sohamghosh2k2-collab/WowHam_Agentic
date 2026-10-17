#!/usr/bin/env python3
"""Score a brief's stories against a trusted-source reference set.

  benchmark.py score --brief memory/briefs/D-stories.json \
      --reference memory/benchmarks/D-reference.json --out memory/benchmarks/D.json

Matching: a reference story matches a brief story when they share a URL, or
when their titles are similar enough (token Jaccard >= --threshold) within the
same topic. Precision = share of brief stories with at least one tier-1/2
outlet (from config/trusted_sources.yaml).
"""
import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = ROOT / "config" / "trusted_sources.yaml"
STOP = set("a an the of to in on for and or with by at from as is are was be its it that this new says after over".split())


def trusted_domains(path=SOURCES):
    """Minimal parser for trusted_sources.yaml (tier1/tier2 list items)."""
    domains, in_trusted = set(), False
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        key = line.strip().rstrip(":")
        if line.strip().endswith(":"):
            in_trusted = key.startswith(("tier1", "tier2"))
            continue
        if in_trusted and line.strip().startswith("- "):
            domains.add(line.strip()[2:].strip().split("/")[0])
    return domains


def tokens(text):
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t not in STOP and len(t) > 1}


def jaccard(a, b):
    ta, tb = tokens(a), tokens(b)
    return len(ta & tb) / len(ta | tb) if ta and tb else 0.0


def domain_of(url):
    m = re.match(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1).lower() if m else ""


def story_urls(story):
    urls = {o.get("url") for o in story.get("outlets", []) if o.get("url")}
    if story.get("url"):
        urls.add(story["url"])
    return urls


def is_trusted(story, trusted):
    for o in story.get("outlets", []):
        d = (o.get("domain") or domain_of(o.get("url"))).lower()
        if any(d == t or d.endswith("." + t) for t in trusted):
            return True
    return False


def score(brief, reference, trusted, threshold=0.35):
    matched, missed = [], []
    total_w = sum(r.get("importance", 1) for r in reference) or 1
    hit_w = 0
    for ref in reference:
        best, best_sim = None, 0.0
        for s in brief:
            if ref.get("topic") and s.get("topic") and ref["topic"] != s["topic"]:
                continue
            sim = 1.0 if ref.get("url") in story_urls(s) else jaccard(ref.get("title"), s.get("title"))
            if sim > best_sim:
                best, best_sim = s, sim
        if best is not None and best_sim >= threshold:
            hit_w += ref.get("importance", 1)
            matched.append({"reference": ref.get("title"), "brief": best.get("title"), "similarity": round(best_sim, 2)})
        else:
            missed.append({k: ref.get(k) for k in ("topic", "title", "outlet", "url", "importance")})
    recall = hit_w / total_w if reference else None
    precision = (sum(is_trusted(s, trusted) for s in brief) / len(brief)) if brief else None
    missed.sort(key=lambda m: -(m.get("importance") or 1))
    return {
        "recall_weighted": round(recall, 3) if recall is not None else None,
        "precision_trusted": round(precision, 3) if precision is not None else None,
        "brief_items": len(brief),
        "reference_items": len(reference),
        "matched": matched,
        "missed": missed,
    }


WEIGHTS = {"recall": 0.30, "precision": 0.15, "accuracy": 0.25, "insight": 0.15, "concision": 0.10, "feedback_fit": 0.05}


def overall(data):
    """Combine tool metrics (fractions) and judged 1-5 scores into one 1-5 score."""
    judged = data.get("judged", {})
    parts = {
        "recall": (data.get("recall_weighted") or 0) * 5,
        "precision": (data.get("precision_trusted") or 0) * 5,
        **{k: judged.get(k) for k in ("accuracy", "insight", "concision", "feedback_fit")},
    }
    missing = [k for k, v in parts.items() if v is None]
    if missing:
        raise ValueError(f"missing judged scores: {', '.join(missing)}")
    return round(sum(WEIGHTS[k] * v for k, v in parts.items()), 2)


def cmd_overall(args):
    path = pathlib.Path(args.file)
    data = json.loads(path.read_text())
    if args.judged:
        data.setdefault("judged", {}).update(json.loads(args.judged))
    try:
        data["overall"] = overall(data)
    except ValueError as e:
        raise SystemExit(str(e))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(json.dumps({"overall": data["overall"], "judged": data["judged"]}, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("--brief", required=True)
    s.add_argument("--reference", required=True)
    s.add_argument("--out")
    s.add_argument("--threshold", type=float, default=0.35)
    o = sub.add_parser("overall", help="add judged 1-5 scores and compute overall")
    o.add_argument("--file", required=True)
    o.add_argument("--judged", help='JSON, e.g. {"accuracy":4,"insight":3,"concision":4,"feedback_fit":5}')
    args = p.parse_args(argv)

    if args.cmd == "overall":
        return cmd_overall(args)

    brief = json.loads(pathlib.Path(args.brief).read_text())
    reference = json.loads(pathlib.Path(args.reference).read_text())
    result = score(brief, reference, trusted_domains(), args.threshold)
    if args.out:
        out = pathlib.Path(args.out)
        existing = json.loads(out.read_text()) if out.exists() else {}
        existing.update(result)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
