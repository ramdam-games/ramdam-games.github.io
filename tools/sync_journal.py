"""Fill content/journal/<game>.json from each game's git history.

Versions come from tags (mode "tags") or from commit days (mode "days").
feat -> Nouveautés, fix -> Corrections, perf/style/ui/ux -> Améliorations,
everything else is counted as technical work. A version marked "edited"
was rewritten by hand and is never touched again; history older than the
newest edited version is left as it is.

Usage: python tools/sync_journal.py [--checkout slug=path ...]
"""
import argparse
import datetime
import fnmatch
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
          "septembre", "octobre", "novembre", "décembre"]
SUBJECT = re.compile(r"^(?P<type>[a-z]+)(\([^)]*\))?!?:\s*(?P<text>.+)$", re.I)
BUCKET = {"feat": "new", "fix": "fixed", "perf": "improved", "style": "improved", "ui": "improved", "ux": "improved"}


def git(path, *args):
    out = subprocess.run(["git", "-C", path, *args], check=True, capture_output=True, text=True, encoding="utf-8")
    return out.stdout


def clean(text):
    text = text.strip().replace(" — ", ", ").replace("—", ",").replace(" – ", ", ")
    text = text.rstrip(".")
    return text[:1].upper() + text[1:]


def commits(path, rev_range):
    raw = git(path, "log", "--no-merges", "--format=%H%x1f%cd%x1f%s", "--date=short", rev_range)
    out = []
    for line in raw.splitlines():
        sha, day, subject = line.split("\x1f", 2)
        out.append((sha, day, subject))
    return out


def classify(items):
    entry = {"new": [], "improved": [], "fixed": [], "tech": 0}
    seen = set()
    for _, _, subject in reversed(items):
        m = SUBJECT.match(subject)
        kind = BUCKET.get(m.group("type").lower()) if m else None
        if not kind or subject.lower().startswith("revert"):
            entry["tech"] += 1
            continue
        text = clean(m.group("text"))
        if text.lower() in seen:
            continue
        seen.add(text.lower())
        entry[kind].append(text)
    return entry


def by_tags(path, pattern):
    raw = git(path, "for-each-ref", "--sort=creatordate", "--format=%(refname:short)%1f%(creatordate:short)", "refs/tags")
    tags = [t.split("\x1f") for t in raw.splitlines() if fnmatch.fnmatch(t.split("\x1f")[0], pattern)]
    versions, prev = [], None
    for name, day in tags:
        rng = f"{prev}..{name}" if prev else name
        items = commits(path, rng)
        prev = name
        versions.append({"version": name.lstrip("v"), "date": day, **classify(items)})
    return versions


def by_days(path):
    days = {}
    for item in commits(path, "HEAD"):
        days.setdefault(item[1], []).append(item)
    versions = []
    for day in sorted(days):
        d = datetime.date.fromisoformat(day)
        label = f"Build du {'1er' if d.day == 1 else d.day} {MONTHS[d.month - 1]}"
        versions.append({"version": label, "date": day, **classify(days[day])})
    return versions


def merge(existing, fresh):
    edited = [v for v in existing if v.get("edited")]
    cutoff = max((v["date"] for v in edited), default="")
    keep = {v["version"]: v for v in existing}
    for v in fresh:
        old = keep.get(v["version"])
        if old and old.get("edited"):
            continue
        if not old and v["date"] <= cutoff:
            continue
        if not (v["new"] or v["improved"] or v["fixed"]):
            continue
        v["lang"] = "en"
        keep[v["version"]] = v
    return sorted(keep.values(), key=lambda v: (v["date"], v["version"]), reverse=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkout", action="append", default=[], help="slug=path of a clone of the game repository")
    args = ap.parse_args()
    checkouts = dict(c.split("=", 1) for c in args.checkout)
    with open(os.path.join(ROOT, "content", "games.json"), encoding="utf-8") as f:
        games = json.load(f)["games"]
    for g in games:
        src = g["source"]
        path = checkouts.get(g["slug"]) or os.path.expanduser(src["local"])
        if not os.path.exists(path):
            print(f"{g['slug']}: no checkout at {path}, skipped")
            continue
        fresh = by_tags(path, src.get("tag_glob", "v*")) if src["mode"] == "tags" else by_days(path)
        jpath = os.path.join(ROOT, "content", "journal", g["slug"] + ".json")
        with open(jpath, encoding="utf-8") as f:
            existing = json.load(f)
        merged = merge(existing, fresh)
        added = [v["version"] for v in merged if not v.get("edited")]
        with open(jpath, "w", encoding="utf-8", newline="\n") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"{g['slug']}: {len(merged)} versions, automatic: {', '.join(added) or 'none'}")


if __name__ == "__main__":
    main()
