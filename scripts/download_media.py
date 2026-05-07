#!/usr/bin/env python3
"""Download every media file in media-manifest.txt into src/assets/img/, preserving
the wp-content/uploads/<year>/<month>/ folder structure. Skip files already present."""
from __future__ import annotations
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "media-manifest.txt"
OUT = ROOT / "src" / "assets" / "img"
BASE = "https://ctrl-alt-delete.ca/wp-content/uploads/"

UA = "Mozilla/5.0 (CADMigration/1.0)"


def download(rel_path: str) -> tuple[str, int]:
    """Returns (status_label, bytes)."""
    dest = OUT / rel_path
    if dest.exists() and dest.stat().st_size > 0:
        return ("skip", dest.stat().st_size)
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = BASE + rel_path
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        dest.write_bytes(data)
        return ("ok", len(data))
    except urllib.error.HTTPError as e:
        return (f"http-{e.code}", 0)
    except Exception as e:
        return (f"err-{type(e).__name__}", 0)


def main():
    items = [l.strip() for l in MANIFEST.read_text().splitlines() if l.strip()]
    print(f"Downloading {len(items)} files to {OUT}")
    counts: dict[str, int] = {}
    total_bytes = 0
    failures = []
    for i, rel in enumerate(items, 1):
        status, n = download(rel)
        counts[status] = counts.get(status, 0) + 1
        total_bytes += n
        if status not in ("ok", "skip"):
            failures.append((rel, status))
        if i % 10 == 0:
            print(f"  [{i}/{len(items)}] {sum(counts.values())} done, last status: {status}")
        # gentle pace
        time.sleep(0.05)
    print()
    print("Summary:")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    print(f"  total bytes: {total_bytes // 1024} KB")
    if failures:
        print()
        print(f"Failures ({len(failures)}):")
        for rel, status in failures:
            print(f"  {status} — {rel}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
