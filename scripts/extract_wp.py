#!/usr/bin/env python3
"""
WordPress XML -> Eleventy Markdown extractor
============================================

Reads the WordPress export XML and writes a Markdown file per published page
and post into the Eleventy `src/` tree, with YAML frontmatter and `permalink`
set to the original URL so SEO is preserved 1:1.

Also produces:
  - existing-leads.csv  — every Ninja Forms submission (`nf_sub`) for the user
  - media-manifest.txt  — list of every wp-content/uploads URL referenced,
                          fed to the media downloader in Phase 2
  - extraction-report.md — what got written and any items that need hand-review
"""
from __future__ import annotations
import csv
import os
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup
from markdownify import markdownify as md

# --------- paths ---------
ROOT = Path(__file__).resolve().parents[1]
XML_PATH = Path(os.environ.get(
    "WP_XML",
    "/sessions/magical-focused-rubin/mnt/uploads/controlaltdeleteca.WordPress.2026-05-07.xml",
))
SRC = ROOT / "src"
REPORT = ROOT / "extraction-report.md"
LEADS = ROOT / "existing-leads.csv"
MEDIA = ROOT / "media-manifest.txt"

NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}

# --------- helpers ---------
SHORTCODE_RE = re.compile(r"\[/?[a-z0-9_:-]+(?:\s[^\]]*)?\]", re.IGNORECASE)
SCRIPT_RE = re.compile(r"<script.*?</script>", re.IGNORECASE | re.DOTALL)
STYLE_RE = re.compile(r"<style.*?</style>", re.IGNORECASE | re.DOTALL)
WP_UPLOAD_RE = re.compile(r"https?://(?:www\.)?ctrl-alt-delete\.ca/wp-content/uploads/([^\s\"')]+)")
INTERNAL_LINK_RE = re.compile(r"https?://(?:www\.)?ctrl-alt-delete\.ca")


def text(el, tag, ns=None):
    if el is None:
        return ""
    e = el.find(tag, NS) if ns is None else el.find(tag, ns)
    return (e.text or "").strip() if e is not None else ""


def postmeta(item) -> dict[str, str]:
    out = {}
    for pm in item.findall("wp:postmeta", NS):
        k = pm.findtext("wp:meta_key", default="", namespaces=NS) or ""
        v = pm.findtext("wp:meta_value", default="", namespaces=NS) or ""
        out[k] = v
    return out


def yaml_escape(s: str) -> str:
    if s is None:
        return '""'
    s = str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()
    return f'"{s}"'


def slugify_url(link: str) -> str:
    """Strip protocol+domain; keep path with leading and trailing slashes."""
    p = re.sub(r"^https?://(?:www\.)?ctrl-alt-delete\.ca", "", link).strip()
    if not p.startswith("/"):
        p = "/" + p
    if not p.endswith("/"):
        p += "/"
    return p


# --------- categorization ---------
SERVICES = {
    "/it-consulting/", "/managed-it-support/", "/managed-cybersecurity/",
    "/managed-data-backups/", "/computer-support/", "/network-support/",
    "/server-support/", "/cloud-computing-services/",
}


def output_path(permalink: str, post_type: str) -> Path:
    """Decide where on disk to write the .md file based on URL."""
    p = permalink.strip("/")
    if permalink == "/":
        return SRC / "index.md"
    if post_type == "post":
        # /blog/<slug>/
        slug = p.split("/")[-1]
        return SRC / "blog" / "posts" / f"{slug}.md"
    parts = p.split("/")
    if permalink in SERVICES:
        return SRC / "services" / f"{parts[0]}.md"
    if parts[0] == "industries":
        if len(parts) == 1:
            return SRC / "industries" / "index.md"
        return SRC / "industries" / f"{parts[1]}.md"
    if parts[0] == "locations-served":
        if len(parts) == 1:
            return SRC / "locations-served" / "index.md"
        if len(parts) == 2:
            # /locations-served/british-columbia/
            return SRC / "locations-served" / parts[1] / "index.md"
        # /locations-served/british-columbia/vancouver/
        return SRC / "locations-served" / parts[1] / f"{parts[2]}.md"
    if parts[0] == "projects":
        if len(parts) == 1:
            return SRC / "projects" / "index.md"
        return SRC / "projects" / f"{parts[1]}.md"
    if permalink == "/blog/":
        return SRC / "blog" / "index.md"
    # one-off pages: /about/, /contact-us/, /privacy-policy/
    return SRC / f"{parts[0]}.md"


def category_label(permalink: str, post_type: str) -> str:
    p = permalink.strip("/")
    if post_type == "post":
        return "blog-post"
    if permalink == "/":
        return "home"
    if permalink in SERVICES:
        return "service"
    if p.startswith("industries"):
        return "industry-index" if p == "industries" else "industry"
    if p.startswith("locations-served"):
        depth = len(p.split("/"))
        if depth == 1:
            return "locations-index"
        if depth == 2:
            return "province"
        return "city"
    if p.startswith("projects"):
        return "project-index" if p == "projects" else "project"
    if permalink == "/blog/":
        return "blog-index"
    return "page"


# --------- HTML cleanup ---------
def clean_html(raw: str) -> tuple[str, list[str]]:
    """Strip Beaver Builder shortcodes, scripts, styles. Track media URLs found."""
    if not raw:
        return "", []
    s = raw
    s = SCRIPT_RE.sub("", s)
    s = STYLE_RE.sub("", s)
    s = SHORTCODE_RE.sub("", s)
    media = WP_UPLOAD_RE.findall(s)
    # Rewrite WP upload URLs -> /assets/img/...
    s = WP_UPLOAD_RE.sub(lambda m: f"/assets/img/{m.group(1)}", s)
    # Rewrite remaining internal absolute links to relative paths
    s = INTERNAL_LINK_RE.sub("", s)
    # Strip Beaver-Builder-specific class soup but preserve structure
    soup = BeautifulSoup(s, "html.parser")
    for tag in soup.find_all(True):
        # drop empty divs that BB leaves behind
        if tag.name == "div" and not tag.get_text(strip=True) and not tag.find("img"):
            tag.decompose()
            continue
        # strip BB-specific classes; keep semantic content
        if "class" in tag.attrs:
            kept = [c for c in tag["class"] if not (
                c.startswith("fl-") or c.startswith("uabb-") or c.startswith("bb-")
                or c.startswith("wp-") or c == "elementor"
            )]
            if kept:
                tag["class"] = kept
            else:
                del tag["class"]
        for attr in ("style", "data-node", "data-template", "id"):
            if attr in tag.attrs and tag.name != "a":
                del tag[attr]
    return str(soup), media


def to_markdown(cleaned_html: str) -> str:
    if not cleaned_html.strip():
        return ""
    return md(cleaned_html, heading_style="ATX", bullets="-", strip=["script", "style"]).strip()


# --------- main ---------
def main():
    if not XML_PATH.exists():
        print(f"FATAL: WP XML not found at {XML_PATH}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {XML_PATH} ({XML_PATH.stat().st_size // 1024} KB)")
    tree = ET.parse(str(XML_PATH))
    root = tree.getroot()
    channel = root.find("channel")

    written = []
    skipped_nopublish = 0
    leads = []
    media_urls = set()
    needs_review = []

    for item in channel.findall("item"):
        post_type = text(item, "wp:post_type")
        status = text(item, "wp:status")

        if post_type == "nf_sub":
            # Ninja Forms submission — extract for leads CSV
            meta = postmeta(item)
            leads.append({
                "submitted_at": text(item, "wp:post_date_gmt") or text(item, "wp:post_date"),
                "title": text(item, "title"),
                "form_data": " | ".join(f"{k}={v}" for k, v in meta.items() if not k.startswith("_")),
            })
            continue

        if status != "publish":
            skipped_nopublish += 1
            continue

        if post_type not in ("page", "post"):
            continue

        title = text(item, "title")
        link = text(item, "link")
        date = text(item, "wp:post_date") or text(item, "pubDate")
        body = item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded", default="")
        excerpt = item.findtext(
            "{http://wordpress.org/export/1.2/excerpt/}encoded", default=""
        ) or ""
        meta = postmeta(item)
        seo_title = meta.get("_yoast_wpseo_title") or meta.get("_aioseo_title") or title
        seo_desc = meta.get("_yoast_wpseo_metadesc") or meta.get("_aioseo_description") or ""
        og_image = meta.get("_yoast_wpseo_opengraph-image") or ""

        permalink = slugify_url(link)
        category = category_label(permalink, post_type)
        out = output_path(permalink, post_type)
        out.parent.mkdir(parents=True, exist_ok=True)

        cleaned, found_media = clean_html(body)
        media_urls.update(found_media)
        markdown_body = to_markdown(cleaned)

        # If body is mostly Beaver Builder shortcodes, conversion may yield nothing useful
        if post_type == "page" and len(markdown_body) < 80 and len(body) > 500:
            needs_review.append((permalink, "body collapsed to <80 chars after shortcode strip — likely Beaver Builder layout, hand-rebuild needed"))

        front = [
            "---",
            f"title: {yaml_escape(title)}",
            f"permalink: {yaml_escape(permalink)}",
            f"date: {yaml_escape(date[:10] if date else '2026-05-07')}",
            f"description: {yaml_escape(seo_desc or excerpt[:160])}",
            f"og_title: {yaml_escape(seo_title)}",
            f"category: {yaml_escape(category)}",
        ]
        if og_image:
            front.append(f"og_image: {yaml_escape(og_image)}")
        if category == "city":
            parts = permalink.strip("/").split("/")
            front.append(f"province: {yaml_escape(parts[1])}")
            front.append(f"city: {yaml_escape(parts[2])}")
        front.append(f'layout: "layouts/{category.replace("-", "_")}.njk"')
        front.append("---")

        out.write_text("\n".join(front) + "\n\n" + markdown_body + "\n", encoding="utf-8")
        written.append((permalink, category, str(out.relative_to(ROOT))))

    # Leads CSV
    if leads:
        with LEADS.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["submitted_at", "title", "form_data"])
            w.writeheader()
            w.writerows(leads)

    # Media manifest
    MEDIA.write_text("\n".join(sorted(media_urls)) + "\n", encoding="utf-8")

    # Report
    by_cat: dict[str, int] = {}
    for _, c, _ in written:
        by_cat[c] = by_cat.get(c, 0) + 1
    lines = [
        "# Extraction report",
        "",
        f"- WP XML source: `{XML_PATH.name}`",
        f"- Items written: **{len(written)}**",
        f"- Form submissions exported to leads CSV: **{len(leads)}**",
        f"- Distinct wp-content media references found: **{len(media_urls)}**",
        f"- Skipped (status != publish): {skipped_nopublish}",
        "",
        "## By category",
    ]
    for c, n in sorted(by_cat.items()):
        lines.append(f"- {c}: {n}")
    if needs_review:
        lines.append("")
        lines.append("## Needs hand-review")
        for permalink, reason in needs_review:
            lines.append(f"- `{permalink}` — {reason}")
    lines.append("")
    lines.append("## Files written")
    for permalink, c, p in sorted(written):
        lines.append(f"- `{permalink}` [{c}] → `{p}`")
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {len(written)} content files")
    print(f"Wrote {len(leads)} leads to {LEADS.name}")
    print(f"Wrote {len(media_urls)} media URLs to {MEDIA.name}")
    print(f"Report at {REPORT.name}")


if __name__ == "__main__":
    main()
