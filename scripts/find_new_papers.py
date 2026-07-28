#!/usr/bin/env python3
"""Report underwater papers on arXiv that this list does not cover yet.

Queries the arXiv API, drops anything whose arXiv ID already appears in
README.md, and writes a Markdown shortlist. Candidates still need a human to
check venue and code links before they are added -- see CONTRIBUTING.md.

Usage: python scripts/find_new_papers.py [--days N] [--out FILE]
"""

import argparse
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

ARXIV_API = "http://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"

# Each query targets a different slice; overlap is fine, results are deduplicated.
QUERIES = [
    'abs:underwater AND (abs:enhancement OR abs:restoration OR abs:"color correction" OR abs:dehazing)',
    'abs:underwater AND (abs:"gaussian splatting" OR abs:nerf OR abs:"radiance field" OR abs:"3d reconstruction")',
    'abs:underwater AND (abs:slam OR abs:"structure from motion" OR abs:"multi-view stereo" OR abs:photogrammetry)',
    'abs:"scattering media" AND (abs:rendering OR abs:reconstruction OR abs:"radiance field")',
]

# A candidate must look underwater-ish AND vision-ish to be worth a maintainer's time.
TOPIC_RE = re.compile(r"underwater|submerged|subsea|seafloor|sea-thru|seathru|marine|scattering media", re.I)
TASK_RE = re.compile(
    r"enhanc|restor|dehaz|color correct|colour correct|image quality|"
    r"reconstruct|radiance field|nerf|gaussian splat|splatting|slam|"
    r"structure.from.motion|multi.view stereo|photogramme|depth estimat|"
    r"stereo match|novel view|image generation|visual odometry",
    re.I,
)
# "underwater" also shows up in acoustics, comms and vehicle-design work that has
# nothing to do with imaging. Drop those before a maintainer has to read them.
OFF_TOPIC_RE = re.compile(
    r"wireless communicat|optical communicat|acoustic communicat|power transfer|"
    r"internet of things|waveform design|code-division|modulation|"
    r"glider|exoskeleton|manipulat|locomotion|flapping|thruster|propuls|"
    r"motion planning|model predictive control|trajectory tracking|"
    r"audio|speech|biolog|fish behavio|water quality",
    re.I,
)


def fetch(query, max_results=100):
    params = urllib.parse.urlencode(
        {
            "search_query": query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results,
        }
    )
    req = urllib.request.Request(
        "%s?%s" % (ARXIV_API, params),
        headers={"User-Agent": "awesome-underwater-list/1.0 (github actions link scan)"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return ET.fromstring(resp.read())


def entries_from(root):
    for e in root.findall(ATOM + "entry"):
        raw_id = e.findtext(ATOM + "id") or ""
        m = re.search(r"abs/([\d.]+)(v\d+)?$", raw_id)
        if not m:
            continue
        published = e.findtext(ATOM + "published") or ""
        try:
            when = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        yield {
            "id": m.group(1),
            "title": " ".join((e.findtext(ATOM + "title") or "").split()),
            "summary": " ".join((e.findtext(ATOM + "summary") or "").split()),
            "published": when,
            "comment": " ".join((e.findtext("{http://arxiv.org/schemas/atom}comment") or "").split()),
            "url": "https://arxiv.org/abs/%s" % m.group(1),
        }


def known_ids(readme_path):
    try:
        with open(readme_path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        sys.exit("cannot read %s: %s" % (readme_path, exc))
    # Match both 2505.01869 and older-style cs.CV/0601001 identifiers.
    return set(re.findall(r"arxiv\.org/(?:abs|pdf)/([\w.\-/]+?)(?:v\d+)?(?=[\s\)\]\"]|$)", text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=45, help="how far back to look")
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--out", default="new-papers.md")
    args = ap.parse_args()

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    have = known_ids(args.readme)

    found = {}
    for q in QUERIES:
        try:
            root = fetch(q)
        except Exception as exc:  # network hiccups should not fail the whole run
            print("query failed (%s): %s" % (q[:40], exc), file=sys.stderr)
            continue
        for entry in entries_from(root):
            if entry["published"] < cutoff:
                continue
            if entry["id"] in have or entry["id"] in found:
                continue
            blob = entry["title"] + " " + entry["summary"]
            if not (TOPIC_RE.search(blob) and TASK_RE.search(blob)):
                continue
            if OFF_TOPIC_RE.search(entry["title"]):
                continue
            found[entry["id"]] = entry
        time.sleep(3)  # arXiv asks for a few seconds between calls

    ordered = sorted(found.values(), key=lambda e: e["published"], reverse=True)

    lines = []
    if not ordered:
        lines.append("No new underwater papers on arXiv in the last %d days." % args.days)
        lines.append("")
        lines.append("_The list is up to date. Nothing to do._")
    else:
        lines.append("Found **%d** underwater paper(s) from the last %d days that are not in the list yet." % (len(ordered), args.days))
        lines.append("")
        lines.append("Each still needs its venue and official code link checked before it goes in — see [CONTRIBUTING.md](CONTRIBUTING.md). Close this issue once they are triaged.")
        lines.append("")
        for e in ordered:
            lines.append("- [ ] **[%s](%s)** — %s" % (e["title"], e["url"], e["published"].strftime("%Y-%m-%d")))
            if e["comment"]:
                lines.append("  - arXiv comments: %s" % e["comment"][:200])
        lines.append("")
        lines.append("_Generated automatically; false positives are expected — just untick and close._")

    body = "\n".join(lines) + "\n"
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(body)

    print(body)
    print("::notice::%d candidate(s)" % len(ordered), file=sys.stderr)
    # Exit code tells the workflow whether an issue is worth opening.
    return 0 if ordered else 1


if __name__ == "__main__":
    sys.exit(main())
