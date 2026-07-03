"""HTML visualiser for the per-repo knowledge graph.

Reads the SQLite store built by ``prthinker build-kg`` and emits a
self-contained HTML page with a D3 force-directed graph: file nodes
radiate to their symbol nodes, methods link back to their enclosing
class. The page embeds the graph as inline JSON and pulls D3 from a
CDN, so the output is portable — open in any browser, no server.
"""

from __future__ import annotations

import json
from pathlib import Path

from prthinker.repo_kg import Import, KnowledgeGraphStore, Symbol


_KIND_FILE = "file"

_KIND_GROUP: dict[str, int] = {
    _KIND_FILE: 0,
    "class": 1,
    "function": 2,
    "method": 3,
    "const": 4,
    "ts_export": 5,
}


def _file_node_id(file_path: str) -> str:
    return f"file::{file_path}"


def _symbol_node_id(s: Symbol) -> str:
    parent = s.parent or "_"
    return f"sym::{s.file_path}::{parent}::{s.symbol}"


def _python_relative_candidates(
    target: str, from_file: str
) -> list[str]:
    """Candidate file paths for a Python relative import (`.x`, `..y`)."""
    dots = len(target) - len(target.lstrip("."))
    module = target[dots:]
    base_parts = from_file.split("/")[:-1]
    if dots - 1 > len(base_parts):
        return []
    if dots - 1 > 0:
        base_parts = base_parts[: -(dots - 1)]
    prefix = "/".join(base_parts) + ("/" if base_parts else "")
    if module:
        mod_path = module.replace(".", "/")
        return [prefix + mod_path + ".py", prefix + mod_path + "/__init__.py"]
    return [prefix + "__init__.py"]


def _python_absolute_candidates(target: str) -> list[str]:
    """Candidate file paths for a Python absolute import."""
    mod_path = target.replace(".", "/")
    return [mod_path + ".py", mod_path + "/__init__.py"]


def _walk_dotted_parents(target: str, file_set: set[str]) -> str | None:
    """Walk up a dotted target — ``from foo.bar.baz import X`` may name
    a symbol exported by ``foo/bar.py`` rather than its own module.
    """
    parts = target.lstrip(".").split(".")
    while len(parts) > 1:
        parts = parts[:-1]
        stem = "/".join(parts)
        for suf in (".py", "/__init__.py"):
            cand = stem + suf
            if cand in file_set:
                return cand
    return None


def _resolve_python_target(
    target: str, kind: str, from_file: str, file_set: set[str]
) -> str | None:
    """Resolve a Python import target string to a known file path.

    Tries both ``foo/bar.py`` (a module file) and
    ``foo/bar/__init__.py`` (a package's init). Relative imports
    (``kind == "py_relative"``) are walked up from ``from_file``'s
    directory. Returns ``None`` if no known file matches — those edges
    are dropped so external deps don't add orphan nodes.
    """
    if kind == "py_relative":
        candidates = _python_relative_candidates(target, from_file)
    else:
        candidates = _python_absolute_candidates(target)
    for cand in candidates:
        if cand in file_set:
            return cand
    return _walk_dotted_parents(target, file_set)


_TSJS_RESOLVE_SUFFIXES: tuple[str, ...] = (
    "", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    "/index.ts", "/index.tsx", "/index.js", "/index.jsx",
)


def _walk_relative_tsjs_path(
    target: str, from_file: str
) -> list[str] | None:
    """Walk a TS/JS relative specifier against ``from_file``'s directory.

    Returns the resolved path segments, or ``None`` if a ``../`` step
    would escape above the repo root.
    """
    base_parts = from_file.split("/")[:-1]
    for p in target.split("/"):
        if p in (".", ""):
            continue
        if p == "..":
            if not base_parts:
                return None
            base_parts = base_parts[:-1]
        else:
            base_parts.append(p)
    return base_parts


def _resolve_tsjs_target(
    target: str, from_file: str, file_set: set[str]
) -> str | None:
    """Resolve a TS/JS import specifier (relative paths only) to a file."""
    if not (target.startswith("./") or target.startswith("../")):
        return None  # bare module specifier → external dep, skip.
    parts = _walk_relative_tsjs_path(target, from_file)
    if parts is None:
        return None
    stem = "/".join(parts)
    for suf in _TSJS_RESOLVE_SUFFIXES:
        cand = stem + suf
        if cand in file_set:
            return cand
    return None


def _file_node(file_path: str) -> dict:
    """Build the D3 node dict for a file node."""
    return {
        "id": _file_node_id(file_path),
        "label": file_path,
        "kind": _KIND_FILE,
        "group": _KIND_GROUP[_KIND_FILE],
    }


def _add_file_nodes(
    symbols: list[Symbol], nodes: list[dict], seen_files: set[str]
) -> None:
    """Emit one file node per distinct file path that owns a symbol."""
    for s in symbols:
        if s.file_path not in seen_files:
            seen_files.add(s.file_path)
            nodes.append(_file_node(s.file_path))


def _add_symbol_nodes(
    symbols: list[Symbol],
    nodes: list[dict],
    links: list[dict],
    class_index: dict[tuple[str, str], str],
) -> None:
    """Emit a symbol node + ``file-of`` link for each symbol; index classes."""
    for s in symbols:
        nid = _symbol_node_id(s)
        nodes.append({
            "id": nid,
            "label": s.symbol,
            "kind": s.kind,
            "file": s.file_path,
            "line": s.line,
            "parent": s.parent,
            "group": _KIND_GROUP.get(s.kind, 99),
        })
        links.append({
            "source": _file_node_id(s.file_path),
            "target": nid,
            "rel": "file-of",
        })
        if s.kind == "class":
            class_index[(s.file_path, s.symbol)] = nid


def _add_method_links(
    symbols: list[Symbol],
    links: list[dict],
    class_index: dict[tuple[str, str], str],
) -> None:
    """Emit a ``method-of`` link from each method to its enclosing class."""
    for s in symbols:
        if s.parent and (s.file_path, s.parent) in class_index:
            links.append({
                "source": class_index[(s.file_path, s.parent)],
                "target": _symbol_node_id(s),
                "rel": "method-of",
            })


def _resolve_import_target(imp: Import, seen_files: set[str]) -> str | None:
    """Resolve an import to a known workdir file, or ``None`` if external."""
    if imp.kind == "tsjs":
        return _resolve_tsjs_target(imp.target, imp.from_file, seen_files)
    if imp.kind == "generic":
        stem = imp.target.replace("::", "/").replace(".", "/").lstrip("/")
        candidates = [stem, *(
            stem + suffix for suffix in (".java", ".go", ".rs", ".c", ".h", ".cpp", ".cs", ".kt")
        )]
        for candidate in candidates:
            if candidate in seen_files:
                return candidate
        basename = stem.rsplit("/", 1)[-1]
        matches = [path for path in seen_files if path.rsplit("/", 1)[-1].split(".")[0] == basename]
        return matches[0] if len(matches) == 1 else None
    return _resolve_python_target(
        imp.target, imp.kind, imp.from_file, seen_files,
    )


def _add_import_links(
    imports: list[Import],
    nodes: list[dict],
    links: list[dict],
    seen_files: set[str],
) -> None:
    """Emit deduplicated file→file ``imports`` links for resolved targets."""
    seen_edges: set[tuple[str, str]] = set()
    for imp in imports:
        resolved = _resolve_import_target(imp, seen_files)
        if not resolved or resolved == imp.from_file:
            continue
        # A symbol-less source file (e.g. __main__.py, __init__.py, or an
        # example script with no def/class) gets no node from the symbol
        # passes above, but can still originate an import edge. Add its
        # file node here so the edge endpoint is not dangling — d3's
        # forceLink throws on a link to a missing node id, which blanks
        # the entire graph. (`resolved` is always a seen file already.)
        if imp.from_file not in seen_files:
            seen_files.add(imp.from_file)
            nodes.append(_file_node(imp.from_file))
        edge = (imp.from_file, resolved)
        if edge in seen_edges:
            continue
        seen_edges.add(edge)
        links.append({
            "source": _file_node_id(imp.from_file),
            "target": _file_node_id(resolved),
            "rel": "imports",
        })


def build_graph_data(store: KnowledgeGraphStore, workdir: Path) -> dict:
    """Convert KG rows into ``{nodes, links}`` for the D3 force layout.

    Three edge families are emitted:

    - ``file-of``: a symbol belongs to a file (every symbol star).
    - ``method-of``: a method belongs to its enclosing class.
    - ``imports``: a file imports a symbol / module that resolves to
      another file in the workdir. These are the connectivity edges
      that make the graph one connected component instead of N
      disconnected per-file stars. External deps that don't resolve
      to a known file are dropped (no orphan boxes).
    """
    symbols = store.all_symbols(workdir)
    imports = store.all_imports(workdir)

    nodes: list[dict] = []
    links: list[dict] = []
    seen_files: set[str] = set()
    class_index: dict[tuple[str, str], str] = {}

    _add_file_nodes(symbols, nodes, seen_files)
    _add_symbol_nodes(symbols, nodes, links, class_index)
    _add_method_links(symbols, links, class_index)
    _add_import_links(imports, nodes, links, seen_files)

    return {"nodes": nodes, "links": links}


_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>prthinker — repo knowledge graph</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<style>
  html, body { margin: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0f1115; color: #e6e6e6; }
  #toolbar { position: fixed; top: 12px; left: 12px; z-index: 10;
    background: rgba(20,22,28,0.85); padding: 10px 14px;
    border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.4); }
  #toolbar input { background: #1c1f26; border: 1px solid #2a2e38;
    color: #e6e6e6; padding: 6px 10px; border-radius: 4px;
    width: 220px; font-size: 13px; }
  #toolbar .legend { font-size: 12px; margin-top: 8px; line-height: 1.5; }
  #toolbar .legend span.swatch { display: inline-block; width: 10px;
    height: 10px; border-radius: 50%; margin: 0 4px 0 8px;
    vertical-align: middle; }
  #toolbar .stats { font-size: 11px; color: #8a8f9b; margin-top: 6px; }
  svg { width: 100vw; height: 100vh; cursor: grab; }
  .link { stroke: #353945; stroke-opacity: 0.5; }
  .link.method-of { stroke: #6c5ce7; stroke-opacity: 0.7; stroke-dasharray: 2 2; }
  .link.imports { stroke: #5fb3b3; stroke-opacity: 0.7; stroke-width: 1.4px; }
  .node text { font-size: 10px; fill: #c8cdd6; pointer-events: none; }
  .node.file text { font-weight: 600; fill: #f6c177; }
  .node circle { stroke: #0f1115; stroke-width: 1.5px; cursor: pointer; }
  .node.dim circle { opacity: 0.12; }
  .node.dim text { opacity: 0.15; }
  .tooltip { position: absolute; background: rgba(20,22,28,0.95);
    padding: 6px 10px; border-radius: 4px; font-size: 12px;
    pointer-events: none; border: 1px solid #2a2e38; }
</style>
</head>
<body>
<div id="toolbar">
  <input id="search" placeholder="search symbol or file…" autocomplete="off" />
  <div class="legend">
    <span class="swatch" style="background:#f6c177"></span>file
    <span class="swatch" style="background:#9aa5ce"></span>class
    <span class="swatch" style="background:#5fb3b3"></span>function
    <span class="swatch" style="background:#6c5ce7"></span>method
    <span class="swatch" style="background:#e58787"></span>const
    <span class="swatch" style="background:#bb9af7"></span>ts_export
  </div>
  <div class="stats" id="stats"></div>
</div>
<svg></svg>
<div class="tooltip" style="display:none"></div>
<script>
const data = __DATA__;

const KIND_COLOR = {
  file: "#f6c177",
  class: "#9aa5ce",
  function: "#5fb3b3",
  method: "#6c5ce7",
  const: "#e58787",
  ts_export: "#bb9af7",
};

document.getElementById("stats").textContent =
  data.nodes.length + " nodes · " + data.links.length + " edges";

const svg = d3.select("svg");
const width = window.innerWidth;
const height = window.innerHeight;
const g = svg.append("g");

svg.call(d3.zoom().scaleExtent([0.1, 8]).on("zoom", (e) => g.attr("transform", e.transform)));

const sim = d3.forceSimulation(data.nodes)
  .force("link", d3.forceLink(data.links).id(d => d.id)
    .distance(d => d.rel === "method-of" ? 40 : (d.rel === "imports" ? 140 : 60))
    .strength(d => d.rel === "imports" ? 0.15 : 0.4))
  .force("charge", d3.forceManyBody().strength(-90))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide().radius(d => d.kind === "file" ? 12 : 6));

const link = g.append("g")
  .selectAll("line")
  .data(data.links)
  .join("line")
  .attr("class", d => "link " + d.rel);

const node = g.append("g")
  .selectAll("g")
  .data(data.nodes)
  .join("g")
  .attr("class", d => "node " + d.kind)
  .call(d3.drag()
    .on("start", (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
    .on("drag", (e, d) => { d.fx = e.x; d.fy = e.y; })
    .on("end", (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }));

node.append("circle")
  .attr("r", d => d.kind === "file" ? 9 : 5)
  .attr("fill", d => KIND_COLOR[d.kind] || "#888");

node.append("text")
  .attr("x", d => d.kind === "file" ? 12 : 7)
  .attr("y", "0.32em")
  .text(d => d.label);

const tooltip = d3.select(".tooltip");
node.on("mouseenter", (e, d) => {
  tooltip.style("display", "block").html(
    d.kind === "file"
      ? "<b>" + d.label + "</b>"
      : "<b>" + d.label + "</b><br>" + (d.parent ? d.parent + " · " : "") + d.file + ":" + d.line + "<br><i>" + d.kind + "</i>"
  );
}).on("mousemove", (e) => {
  tooltip.style("left", (e.pageX + 10) + "px").style("top", (e.pageY + 10) + "px");
}).on("mouseleave", () => tooltip.style("display", "none"));

sim.on("tick", () => {
  link
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node.attr("transform", d => "translate(" + d.x + "," + d.y + ")");
});

document.getElementById("search").addEventListener("input", (e) => {
  const q = e.target.value.trim().toLowerCase();
  node.classed("dim", d => q && !d.label.toLowerCase().includes(q));
});
</script>
</body>
</html>
"""


def render_html(data: dict, output_path: Path) -> None:
    """Write the self-contained HTML page with the graph baked in."""
    payload = json.dumps(data, ensure_ascii=False)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        _HTML_TEMPLATE.replace("__DATA__", payload),
        encoding="utf-8",
    )


__all__ = ["Import", "Symbol", "build_graph_data", "render_html"]
