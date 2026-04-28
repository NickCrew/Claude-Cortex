#!/usr/bin/env python3
"""Extract SEO signals from a static HTML file into a single JSON document.

Stdlib only — no external dependencies.

Usage:
    python3 extract_seo_signals.py <path-to-html> [--pretty]
    python3 extract_seo_signals.py <path-to-directory>     # all *.html, recursive

Output: JSON to stdout. One object per file under "files" when a directory is given.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


SELF_CLOSING = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


class SEOExtractor(HTMLParser):
    """Walks an HTML document and records SEO-relevant elements with positions."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: dict[str, Any] | None = None
        self._in_title = False
        self._title_buf: list[str] = []
        self._title_pos: tuple[int, int] | None = None

        self.metas: list[dict[str, Any]] = []
        self.links: list[dict[str, Any]] = []
        self.scripts: list[dict[str, Any]] = []
        self._in_script = False
        self._script_attrs: dict[str, Any] = {}
        self._script_pos: tuple[int, int] | None = None
        self._script_buf: list[str] = []

        self.headings: list[dict[str, Any]] = []
        self._heading_stack: list[dict[str, Any]] = []
        self._heading_buf: list[str] = []

        self.images: list[dict[str, Any]] = []
        self.anchors: list[dict[str, Any]] = []
        self._anchor_stack: list[dict[str, Any]] = []
        self._anchor_buf: list[str] = []

        self.html_attrs: dict[str, str] = {}
        self.body_word_count = 0
        self._in_body = False
        self._in_text_skip = 0  # depth counter for <script>/<style>/<noscript>

    # ------- helpers -------

    @staticmethod
    def _attrs_to_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {k: (v if v is not None else "") for k, v in attrs}

    def _pos(self) -> dict[str, int]:
        line, col = self.getpos()
        return {"line": line, "col": col}

    # ------- handlers -------

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = self._attrs_to_dict(attrs)
        pos = self._pos()

        if tag == "html":
            self.html_attrs = a
        elif tag == "body":
            self._in_body = True
        elif tag == "title":
            self._in_title = True
            self._title_buf = []
            self._title_pos = (pos["line"], pos["col"])
        elif tag == "meta":
            self.metas.append({"attrs": a, **pos})
        elif tag == "link":
            self.links.append({"attrs": a, **pos})
        elif tag == "script":
            self._in_script = True
            self._script_attrs = a
            self._script_pos = (pos["line"], pos["col"])
            self._script_buf = []
            self._in_text_skip += 1
        elif tag in {"style", "noscript"}:
            self._in_text_skip += 1
        elif tag in HEADING_TAGS:
            entry = {"tag": tag, "level": int(tag[1]), "text": "", "attrs": a, **pos}
            self._heading_stack.append(entry)
            self._heading_buf = []
        elif tag == "img":
            self.images.append({"attrs": a, **pos})
        elif tag == "a":
            entry = {"attrs": a, "text": "", **pos}
            self._anchor_stack.append(entry)
            self._anchor_buf = []

        # treat self-closing tags consistently
        if tag in SELF_CLOSING:
            return

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self._in_title:
            self._in_title = False
            text = "".join(self._title_buf).strip()
            line, col = self._title_pos or (0, 0)
            self.title = {"text": text, "length": len(text), "line": line, "col": col}
        elif tag == "script" and self._in_script:
            self._in_script = False
            line, col = self._script_pos or (0, 0)
            self.scripts.append({
                "attrs": self._script_attrs,
                "content": "".join(self._script_buf),
                "line": line,
                "col": col,
            })
            self._in_text_skip = max(0, self._in_text_skip - 1)
        elif tag in {"style", "noscript"}:
            self._in_text_skip = max(0, self._in_text_skip - 1)
        elif tag in HEADING_TAGS and self._heading_stack:
            entry = self._heading_stack.pop()
            entry["text"] = "".join(self._heading_buf).strip()
            self.headings.append(entry)
            self._heading_buf = []
        elif tag == "a" and self._anchor_stack:
            entry = self._anchor_stack.pop()
            entry["text"] = "".join(self._anchor_buf).strip()
            self.anchors.append(entry)
            self._anchor_buf = []
        elif tag == "body":
            self._in_body = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_buf.append(data)
        if self._in_script:
            self._script_buf.append(data)
        if self._heading_stack:
            self._heading_buf.append(data)
        if self._anchor_stack:
            self._anchor_buf.append(data)
        if self._in_body and self._in_text_skip == 0:
            words = re.findall(r"\b\w+\b", data)
            self.body_word_count += len(words)


def _summarize_meta(metas: list[dict[str, Any]]) -> dict[str, Any]:
    """Pull commonly-checked meta tags into a flat summary."""
    summary: dict[str, Any] = {
        "description": None,
        "robots": None,
        "viewport": None,
        "charset": None,
        "og": {},
        "twitter": {},
        "other_named": {},
    }
    for m in metas:
        a = m["attrs"]
        if "charset" in a:
            summary["charset"] = a["charset"]
            continue
        name = (a.get("name") or "").lower()
        prop = (a.get("property") or "").lower()
        content = a.get("content", "")
        if name == "description":
            summary["description"] = {"content": content, "length": len(content), "line": m["line"]}
        elif name == "robots":
            summary["robots"] = {"content": content, "line": m["line"]}
        elif name == "viewport":
            summary["viewport"] = {"content": content, "line": m["line"]}
        elif prop.startswith("og:"):
            summary["og"][prop] = content
        elif name.startswith("twitter:"):
            summary["twitter"][name] = content
        elif name:
            summary["other_named"][name] = content
    return summary


def _summarize_links(links: list[dict[str, Any]]) -> dict[str, Any]:
    canonical = None
    alternates: list[dict[str, Any]] = []
    stylesheets: list[dict[str, Any]] = []
    preloads: list[dict[str, Any]] = []
    for l in links:
        a = l["attrs"]
        rel = (a.get("rel") or "").lower()
        if rel == "canonical":
            canonical = {"href": a.get("href", ""), "line": l["line"]}
        elif rel == "alternate":
            alternates.append({"hreflang": a.get("hreflang"), "href": a.get("href", ""), "line": l["line"]})
        elif rel == "stylesheet":
            stylesheets.append({"href": a.get("href", ""), "media": a.get("media"), "line": l["line"]})
        elif rel == "preload":
            preloads.append({"href": a.get("href", ""), "as": a.get("as"), "line": l["line"]})
    return {"canonical": canonical, "alternates": alternates, "stylesheets": stylesheets, "preloads": preloads}


def _classify_anchors(anchors: list[dict[str, Any]], page_origin: str | None = None) -> dict[str, Any]:
    internal = []
    external = []
    fragment = []
    empty = []
    for a in anchors:
        href = a["attrs"].get("href", "").strip()
        text = a["text"]
        rel = a["attrs"].get("rel", "")
        line = a["line"]
        record = {"href": href, "text": text, "rel": rel, "line": line}
        if not href or href == "#":
            empty.append(record)
        elif href.startswith("#"):
            fragment.append(record)
        elif re.match(r"^https?://", href):
            external.append(record)
        else:
            internal.append(record)
    return {"internal": internal, "external": external, "fragment": fragment, "empty_or_hash": empty}


def _scripts_summary(scripts: list[dict[str, Any]]) -> dict[str, Any]:
    jsonld: list[dict[str, Any]] = []
    blocking_in_head = []
    deferred_async = []
    other = []
    for s in scripts:
        a = s["attrs"]
        s_type = (a.get("type") or "").lower()
        if s_type == "application/ld+json":
            try:
                parsed = json.loads(s["content"])
                jsonld.append({"line": s["line"], "valid": True, "data": parsed})
            except json.JSONDecodeError as e:
                jsonld.append({"line": s["line"], "valid": False, "error": str(e)})
            continue
        has_src = "src" in a
        has_async = "async" in a
        has_defer = "defer" in a
        record = {
            "src": a.get("src"),
            "async": has_async,
            "defer": has_defer,
            "type": a.get("type"),
            "line": s["line"],
        }
        if has_src and not (has_async or has_defer):
            blocking_in_head.append(record)
        elif has_async or has_defer:
            deferred_async.append(record)
        else:
            other.append(record)
    return {
        "jsonld": jsonld,
        "render_blocking_candidates": blocking_in_head,
        "async_or_defer": deferred_async,
        "inline_or_other": other,
    }


def extract_signals(html: str, source_path: str | None = None, file_size: int | None = None) -> dict[str, Any]:
    parser = SEOExtractor()
    parser.feed(html)

    images_summary = []
    for img in parser.images:
        a = img["attrs"]
        images_summary.append({
            "src": a.get("src", ""),
            "alt": a.get("alt"),
            "alt_present": "alt" in a,
            "alt_empty": "alt" in a and a.get("alt", "") == "",
            "width": a.get("width"),
            "height": a.get("height"),
            "loading": a.get("loading"),
            "line": img["line"],
        })

    h1s = [h for h in parser.headings if h["level"] == 1]

    return {
        "source": source_path,
        "file_size_bytes": file_size,
        "lang": parser.html_attrs.get("lang"),
        "title": parser.title,
        "meta": _summarize_meta(parser.metas),
        "links": _summarize_links(parser.links),
        "scripts": _scripts_summary(parser.scripts),
        "headings": {
            "all": sorted(parser.headings, key=lambda h: (h["line"], h["col"])),
            "h1_count": len(h1s),
            "outline": [{"level": h["level"], "text": h["text"], "line": h["line"]} for h in sorted(parser.headings, key=lambda h: (h["line"], h["col"]))],
        },
        "images": {
            "all": images_summary,
            "total": len(images_summary),
            "missing_alt": [i for i in images_summary if not i["alt_present"]],
            "empty_alt": [i for i in images_summary if i["alt_empty"]],
            "missing_dimensions": [i for i in images_summary if not (i["width"] and i["height"])],
            "no_lazy_loading": [i for i in images_summary if i["loading"] != "lazy"],
        },
        "links_audit": _classify_anchors(parser.anchors),
        "body_word_count": parser.body_word_count,
    }


def _gather_paths(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(p for p in target.rglob("*.html") if p.is_file())
    raise FileNotFoundError(f"Not a file or directory: {target}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract SEO signals from static HTML.")
    ap.add_argument("target", help="Path to .html file or directory of HTML files")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    paths = _gather_paths(target)
    if not paths:
        print(json.dumps({"error": "no HTML files found", "target": str(target)}))
        return 1

    results = []
    for p in paths:
        try:
            html = p.read_text(encoding="utf-8", errors="replace")
            size = p.stat().st_size
            results.append(extract_signals(html, source_path=str(p), file_size=size))
        except Exception as e:
            results.append({"source": str(p), "error": f"{type(e).__name__}: {e}"})

    payload = results[0] if (target.is_file() and len(results) == 1) else {"files": results}
    indent = 2 if args.pretty else None
    print(json.dumps(payload, indent=indent, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
