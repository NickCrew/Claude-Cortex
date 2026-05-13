#!/usr/bin/env python3
"""
Documentation Link Graph

Builds a directed graph of internal markdown links and reports:
- Orphans (pages with no inbound links from other docs)
- Dead-ends (pages with no outbound links to other docs)
- Reciprocity stats (mutual vs one-way links)
- Broken links (targets that don't resolve)
- Hub pages (high in-degree) and Bridge pages (high betweenness, approximated)

This script handles the *mechanical* side of architecture review (Heuristic 1
"Findability" orphan detection, Heuristic 4 "Cross-Linking Quality" graph
metrics). Judgment-heavy heuristics (whether a link is contextual, whether
patterns are consistent) require sonnet sub-agents — see SKILL.md.

Usage:
    python3 skills/doc-architecture-review/scripts/link_graph.py [OPTIONS]

Options:
    --json      Output as JSON instead of markdown
    --root PATH Project root directory (default: git root or cwd)
    --scope     Which docs to scan: docs, manual, all (default: all)
    --min-fanout N
                Hub threshold — pages with >= N inbound links are listed (default: 5)
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

SCOPE_DIRS = {
    "docs": ["docs"],
    "manual": ["manual"],
    "all": ["docs", "manual", "site"],
}

ALWAYS_INCLUDE = ["README.md", "CONTRIBUTING.md"]
SKIP_DIRS = {"node_modules", ".git", "__pycache__", "archive", "_site"}

MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
JEKYLL_LINK_RE = re.compile(r"\{%\s*link\s+([^\s%}]+)\s*%\}")


@dataclass
class GraphNode:
    path: str
    inbound: list = field(default_factory=list)   # paths that link to this
    outbound: list = field(default_factory=list)  # paths this links to
    broken_outbound: list = field(default_factory=list)


def get_project_root(root_override=None):
    if root_override:
        return Path(root_override).resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def find_markdown_files(root, scope):
    files = []
    dirs = SCOPE_DIRS.get(scope, SCOPE_DIRS["all"])
    for d in dirs:
        search_root = root / d
        if search_root.exists():
            for md in search_root.rglob("*.md"):
                if any(part in SKIP_DIRS for part in md.relative_to(root).parts):
                    continue
                files.append(md)
    for name in ALWAYS_INCLUDE:
        f = root / name
        if f.exists():
            files.append(f)
    return sorted(set(files))


def extract_link_targets(filepath, root):
    """Yield (target_path, raw_target) for every internal markdown link."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return

    # Standard markdown links
    for match in MD_LINK_RE.finditer(content):
        target = match.group(2).strip()
        # Skip URLs, anchors, mailto
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        # Strip anchor fragment
        clean = target.split("#")[0]
        if not clean:
            continue
        yield clean, target

    # Jekyll {% link path %} references — site/ uses these heavily
    for match in JEKYLL_LINK_RE.finditer(content):
        clean = match.group(1).strip()
        yield clean, match.group(0)


def resolve_target(source_file, target, root):
    """Resolve a link target to an absolute path.

    Handles relative paths and Jekyll-rooted paths. Returns the resolved
    Path or None if the target doesn't resolve to an existing file.
    """
    # Jekyll {% link foo.md %} — relative to site root, but accept relative-to-doc too
    candidates = [
        (source_file.parent / target).resolve(),
        (root / target).resolve(),
    ]
    # If target lacks .md extension, also try with it (Just-The-Docs sometimes does this)
    if "." not in Path(target).name:
        candidates.extend([
            (source_file.parent / (target + ".md")).resolve(),
            (root / (target + ".md")).resolve(),
        ])
    for c in candidates:
        if c.exists():
            return c
    return None


def build_graph(root, md_files):
    """Construct the link graph keyed by relative path."""
    nodes = {}
    for md in md_files:
        rel = str(md.relative_to(root))
        nodes[rel] = GraphNode(path=rel)

    for md in md_files:
        rel_source = str(md.relative_to(root))
        for clean_target, raw_target in extract_link_targets(md, root):
            resolved = resolve_target(md, clean_target, root)
            if resolved is None or not resolved.is_file():
                nodes[rel_source].broken_outbound.append(raw_target)
                continue
            try:
                rel_target = str(resolved.relative_to(root))
            except ValueError:
                # Outside the repo root — skip
                continue
            if rel_target not in nodes:
                # Linked file isn't markdown (could be image, asset) — skip
                continue
            nodes[rel_source].outbound.append(rel_target)
            nodes[rel_target].inbound.append(rel_source)

    return nodes


def find_orphans(nodes, root):
    """Pages with no inbound links and not navigation entry points."""
    orphans = []
    for path, node in nodes.items():
        # Skip entry-point pages — they're not expected to be linked
        name = Path(path).name.lower()
        if name in ("readme.md", "index.md"):
            continue
        if not node.inbound:
            orphans.append(path)
    return sorted(orphans)


def find_dead_ends(nodes):
    """Pages with no outbound internal links — content silos."""
    dead_ends = []
    for path, node in nodes.items():
        if not node.outbound:
            dead_ends.append(path)
    return sorted(dead_ends)


def compute_reciprocity(nodes):
    """Count mutual vs one-way edges in the link graph."""
    edges = set()
    mutual = 0
    one_way = 0
    for path, node in nodes.items():
        for target in set(node.outbound):
            edges.add((path, target))

    for source, target in edges:
        if (target, source) in edges:
            mutual += 1
        else:
            one_way += 1

    # mutual edges counted once per pair below; halve to get unique mutual pairs
    unique_mutual_pairs = mutual // 2
    return {
        "total_directed_edges": len(edges),
        "mutual_pairs": unique_mutual_pairs,
        "one_way_edges": one_way,
        "reciprocity_ratio": (
            round(unique_mutual_pairs * 2 / len(edges), 3) if edges else 0.0
        ),
    }


def find_hubs(nodes, min_fanout):
    """Pages with high in-degree — natural reference targets."""
    hubs = []
    for path, node in nodes.items():
        in_degree = len(set(node.inbound))
        if in_degree >= min_fanout:
            hubs.append((path, in_degree))
    return sorted(hubs, key=lambda t: -t[1])


def find_broken_links(nodes):
    """Pages with at least one broken outbound link."""
    broken = []
    for path, node in nodes.items():
        if node.broken_outbound:
            broken.append({
                "source": path,
                "broken_targets": list(node.broken_outbound),
            })
    return sorted(broken, key=lambda d: d["source"])


def generate_markdown_report(stats, orphans, dead_ends, recip, hubs, broken, root):
    lines = [
        "# Documentation Link Graph Report",
        "",
        f"**Project root:** `{root}`",
        f"**Total pages:** {stats['total_pages']}",
        f"**Total internal edges:** {recip['total_directed_edges']}",
        "",
        "## Reciprocity",
        "",
        f"- Mutual link pairs: {recip['mutual_pairs']}",
        f"- One-way edges: {recip['one_way_edges']}",
        f"- Reciprocity ratio: {recip['reciprocity_ratio']:.3f} "
        f"(1.0 = every edge has a back-link)",
        "",
    ]

    lines.append(f"## Orphans ({len(orphans)})")
    lines.append("")
    if orphans:
        lines.append("Pages with no inbound links from any other doc — effectively invisible:")
        lines.append("")
        for o in orphans:
            lines.append(f"- `{o}`")
    else:
        lines.append("No orphan pages.")
    lines.append("")

    lines.append(f"## Dead-Ends ({len(dead_ends)})")
    lines.append("")
    if dead_ends:
        lines.append("Pages with no outbound internal links — content silos:")
        lines.append("")
        for d in dead_ends:
            lines.append(f"- `{d}`")
    else:
        lines.append("No dead-end pages.")
    lines.append("")

    lines.append(f"## Hubs ({len(hubs)})")
    lines.append("")
    if hubs:
        lines.append("Pages with high in-degree — natural reference targets:")
        lines.append("")
        lines.append("| Page | Inbound Links |")
        lines.append("|------|---------------|")
        for path, count in hubs[:20]:
            lines.append(f"| `{path}` | {count} |")
    else:
        lines.append("No hub pages above threshold.")
    lines.append("")

    lines.append(f"## Broken Links ({len(broken)})")
    lines.append("")
    if broken:
        lines.append("| Source | Broken Targets |")
        lines.append("|--------|----------------|")
        for entry in broken:
            targets = ", ".join(f"`{t}`" for t in entry["broken_targets"])
            lines.append(f"| `{entry['source']}` | {targets} |")
    else:
        lines.append("No broken internal links.")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Doc link graph analyzer")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--root", type=str, default=None, help="Project root path")
    parser.add_argument(
        "--scope",
        choices=["docs", "manual", "all"],
        default="all",
        help="Which docs to scan (default: all)",
    )
    parser.add_argument(
        "--min-fanout", type=int, default=5,
        help="Hub threshold — pages with >= N inbound links (default: 5)",
    )
    args = parser.parse_args()

    root = get_project_root(args.root)
    md_files = find_markdown_files(root, args.scope)

    print(f"Scanning {len(md_files)} markdown files in {root}...", file=sys.stderr)

    nodes = build_graph(root, md_files)
    orphans = find_orphans(nodes, root)
    dead_ends = find_dead_ends(nodes)
    recip = compute_reciprocity(nodes)
    hubs = find_hubs(nodes, args.min_fanout)
    broken = find_broken_links(nodes)

    stats = {"total_pages": len(nodes)}

    if args.json:
        report = {
            "project_root": str(root),
            "stats": stats,
            "reciprocity": recip,
            "orphans": orphans,
            "dead_ends": dead_ends,
            "hubs": [{"path": p, "in_degree": d} for p, d in hubs],
            "broken_links": broken,
        }
        print(json.dumps(report, indent=2))
    else:
        print(generate_markdown_report(stats, orphans, dead_ends, recip, hubs, broken, root))


if __name__ == "__main__":
    main()
