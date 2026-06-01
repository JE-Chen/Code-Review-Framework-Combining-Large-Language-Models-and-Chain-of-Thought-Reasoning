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

from prthinker.repo_kg import KnowledgeGraphStore, Symbol


_KIND_GROUP: dict[str, int] = {
    "file": 0,
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


def build_graph_data(store: KnowledgeGraphStore, workdir: Path) -> dict:
    """Convert KG rows into ``{nodes, links}`` for the D3 force layout."""
    symbols = store.all_symbols(workdir)

    nodes: list[dict] = []
    links: list[dict] = []
    seen_files: set[str] = set()
    # Map (file_path, class_name) → symbol node id so methods can link
    # to their enclosing class node, not to a stale string.
    class_index: dict[tuple[str, str], str] = {}

    for s in symbols:
        if s.file_path not in seen_files:
            seen_files.add(s.file_path)
            nodes.append({
                "id": _file_node_id(s.file_path),
                "label": s.file_path,
                "kind": "file",
                "group": _KIND_GROUP["file"],
            })

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

    for s in symbols:
        if s.parent and (s.file_path, s.parent) in class_index:
            links.append({
                "source": class_index[(s.file_path, s.parent)],
                "target": _symbol_node_id(s),
                "rel": "method-of",
            })

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
  .force("link", d3.forceLink(data.links).id(d => d.id).distance(d => d.rel === "method-of" ? 40 : 60).strength(0.4))
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


__all__ = ["build_graph_data", "render_html"]
