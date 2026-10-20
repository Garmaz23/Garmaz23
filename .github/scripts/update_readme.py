"""Refresh the auto-updated section of the profile README.

kev - newest entries in CISA's Known Exploited Vulnerabilities catalog,
      written between <!--START_SECTION:kev--> and <!--END_SECTION:kev-->.

Standard library only.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USERNAME", "Garmaz23")
README = os.environ.get("README_PATH", "README.md")
MAX_KEV = int(os.environ.get("MAX_KEV", "3"))

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
KEV_PAGE = "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-readme-updater", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def cell(s):
    return (s or "—").replace("|", "\\|").replace("\n", " ").strip()


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


def short_date(iso):
    """'2026-10-16' or '2026-10-16T15:00:00Z' -> 'Oct 16, 2026' (no hyphens, so no ugly wrapping)."""
    try:
        return datetime.fromisoformat((iso or "")[:10]).strftime("%b %-d, %Y").replace(" ", "&nbsp;")
    except ValueError:
        return "—"


def build_kev(catalog):
    vulns = sorted(
        catalog.get("vulnerabilities", []),
        key=lambda v: (v.get("dateAdded", ""), v.get("cveID", "")),
        reverse=True,
    )[:MAX_KEV]

    if not vulns:
        return "_No entries available right now._"

    rows = ["| CVE | Affected | Weakness | Added |", "|---|---|---|---|"]
    for v in vulns:
        cve = v.get("cveID", "")
        vendor, product = (v.get("vendorProject") or "").strip(), (v.get("product") or "").strip()
        affected = cell(f"{vendor} {product}".strip())
        what = cell(weakness(v.get("vulnerabilityName"), vendor, product))
        if str(v.get("knownRansomwareCampaignUse", "")).lower() == "known":
            what += " <sub>⚠️ used by ransomware</sub>"
        rows.append(
            f"| [{cve}](https://nvd.nist.gov/vuln/detail/{cve}) | {affected} "
            f"| {what} | {short_date(v.get('dateAdded'))} |"
        )

    total = catalog.get("count") or len(catalog.get("vulnerabilities", []))
    released = short_date(catalog.get("dateReleased"))
    rows.append("")
    rows.append(
        f"<sub>Newest of {total:,} entries in the [CISA KEV catalog]({KEV_PAGE}), "
        f"last updated by CISA on {released}. CISA adds entries a few times a week; "
        "this section is checked every day.</sub>"
    )
    return "\n".join(rows)


# ---------------------------------------------------------------- main

SECTIONS = [
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
        except Exception as exc:  # keep the old section
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
