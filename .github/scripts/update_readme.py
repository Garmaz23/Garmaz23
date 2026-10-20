"""Refresh the auto-updated sections of the profile README.

Two sections, each between its own markers:
  recent  - public repos with the most recent pushes
  kev     - newest entries in CISA's Known Exploited Vulnerabilities catalog

Standard library only. If one source fails, the other is still updated.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USERNAME", "Garmaz23")
TOKEN = os.environ.get("GITHUB_TOKEN")
README = os.environ.get("README_PATH", "README.md")
MAX_REPOS = int(os.environ.get("MAX_REPOS", "5"))
MAX_KEV = int(os.environ.get("MAX_KEV", "3"))
EXCLUDE = {r.strip().lower() for r in os.environ.get("EXCLUDE_REPOS", "").split(",") if r.strip()}

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
KEV_PAGE = "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-readme-updater", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def cell(s):
    return (s or "—").replace("|", "\\|").replace("\n", " ").strip()


# ---------------------------------------------------------------- repos

def time_ago(iso):
    pushed = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - pushed).days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 30:
        return f"{days} days ago"
    months = days // 30
    if months < 12:
        return f"{months} month{'s' if months > 1 else ''} ago"
    years = days // 365
    return f"{years} year{'s' if years > 1 else ''} ago"


def fetch_repos():
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return get_json(
        f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&direction=desc&per_page=50",
        headers,
    )


def build_recent(repos):
    picked = [
        r for r in repos
        if not r.get("fork")
        and not r.get("archived")
        and not r.get("private")
        and r["name"].lower() != USER.lower()
        and r["name"].lower() not in EXCLUDE
    ][:MAX_REPOS]

    if not picked:
        return "_Nothing public right now._"

    rows = ["| Repo | What it is | Language | Last push |", "|---|---|---|---|"]
    for r in picked:
        rows.append(
            f"| [**{r['name']}**]({r['html_url']}) | {cell(r.get('description'))} "
            f"| {r.get('language') or '—'} | {time_ago(r['pushed_at'])} |"
        )
    return "\n".join(rows)


# ---------------------------------------------------------------- KEV

def fetch_kev():
    return get_json(KEV_URL)


def weakness(name, vendor, product):
    """'Fortinet FortiOS Path Traversal Vulnerability' -> 'Path Traversal'."""
    name = (name or "").strip()
    for prefix in (f"{vendor} {product}", product, vendor):
        if prefix and name.lower().startswith(prefix.lower() + " "):
            name = name[len(prefix):].strip()
            break
    if name.lower().endswith(" vulnerability"):
        name = name[: -len(" vulnerability")].strip()
    return name or None


def build_kev(catalog):
    vulns = sorted(
        catalog.get("vulnerabilities", []),
        key=lambda v: (v.get("dateAdded", ""), v.get("cveID", "")),
        reverse=True,
    )[:MAX_KEV]

    if not vulns:
        return "_No entries available right now._"

    rows = ["| CVE | Affected | Weakness | Added | Ransomware |", "|---|---|---|---|---|"]
    for v in vulns:
        cve = v.get("cveID", "")
        vendor, product = (v.get("vendorProject") or "").strip(), (v.get("product") or "").strip()
        affected = cell(f"{vendor} {product}".strip())
        ransomware = "⚠️ known" if str(v.get("knownRansomwareCampaignUse", "")).lower() == "known" else "—"
        rows.append(
            f"| [`{cve}`](https://nvd.nist.gov/vuln/detail/{cve}) | {affected} "
            f"| {cell(weakness(v.get('vulnerabilityName'), vendor, product))} | {v.get('dateAdded', '—')} | {ransomware} |"
        )

    total = catalog.get("count") or len(catalog.get("vulnerabilities", []))
    released = (catalog.get("dateReleased") or "")[:10]
    rows.append("")
    rows.append(
        f"<sub>Newest of {total:,} entries in the [CISA KEV catalog]({KEV_PAGE})"
        + (f", catalog updated {released}" if released else "")
        + ". Refreshed daily by a GitHub Action.</sub>"
    )
    return "\n".join(rows)


# ---------------------------------------------------------------- main

SECTIONS = [
    ("recent", fetch_repos, build_recent),
    ("kev", fetch_kev, build_kev),
]


def replace_section(content, name, body):
    start, end = f"<!--START_SECTION:{name}-->", f"<!--END_SECTION:{name}-->"
    if start not in content or end not in content:
        print(f"[{name}] markers not found, skipping")
        return content
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    return pattern.sub(lambda _: f"{start}\n{body}\n{end}", content)


def main():
    with open(README, encoding="utf-8") as f:
        original = f.read()

    content, failures = original, 0
    for name, fetch, build in SECTIONS:
        try:
            content = replace_section(content, name, build(fetch()))
        except Exception as exc:  # keep the old section, carry on with the next
            failures += 1
            print(f"[{name}] failed, keeping previous content: {exc}", file=sys.stderr)

    if content != original:
        with open(README, "w", encoding="utf-8") as f:
            f.write(content)
        print("README updated.")
    else:
        print("No changes.")

    if failures == len(SECTIONS):
        sys.exit(1)


if __name__ == "__main__":
    main()
