"""Final layout pass for the v3.10 engineering deployment diagram.

This wrapper keeps the main generator readable while applying the two details
found during visual verification: a centred host-band label and a fully
orthogonal FAISS-to-CoT route.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import ImageDraw

HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location(
    "deployment_base", HERE / "generate_deployment_diagram.py"
)
BASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BASE)

# Replace the one diagonal tail with a horizontal lane followed by a vertical
# entry into the CoT box.
BASE.EDGES = [
    (*edge[:5], ((1615, 570), (1230, 570)))
    if edge[0] == "faiss" and edge[1] == "cot"
    else edge
    for edge in BASE.EDGES
]


def final_png():
    image = BASE.png_image()
    draw = ImageDraw.Draw(image)
    scale = BASE.PNG_SCALE

    # Clear the former left-aligned host-band label without touching the top
    # border, then redraw the TLS connector that passes through this strip.
    draw.rectangle((630 * scale, 330 * scale, 1040 * scale, 380 * scale), fill="#FFFBEA")
    tls_edge = next(edge for edge in BASE.EDGES if edge[0] == "tls" and edge[1] == "api")
    src, dst, label, src_side, dst_side, mids = tls_edge
    points = [BASE.port(BASE.node(src), src_side), *mids, BASE.port(BASE.node(dst), dst_side)]
    BASE.draw_arrow(draw, points, "#36566F", 3 * scale)
    segs = list(zip(points, points[1:]))
    a, b = max(
        segs,
        key=lambda pair: abs(pair[1][0] - pair[0][0]) + abs(pair[1][1] - pair[0][1]),
    )
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    font = BASE.load_font(BASE.FONT_SIZE * scale)
    pos = BASE.scale_point((mx, my))
    bbox = draw.textbbox(pos, label, anchor="mm", font=font)
    draw.rectangle(
        (bbox[0] - 8 * scale, bbox[1] - 5 * scale, bbox[2] + 8 * scale, bbox[3] + 5 * scale),
        fill="white",
    )
    draw.text(pos, label, anchor="mm", font=font, fill="#36566F")

    bold = BASE.load_font(BASE.FONT_SIZE * scale, bold=True)
    draw.text(
        BASE.scale_point((1215, 350)),
        "DGX Spark／GB10 部署主機",
        anchor="mm",
        font=bold,
        fill="#7A6517",
    )
    return image


def main():
    drawio = BASE.drawio_xml().replace(
        'value="DGX Spark／GB10 部署主機" style=',
        'value="DGX Spark／GB10 部署主機" style=',
    )
    # draw.io already centres the band value; the replacement is intentionally
    # limited to the SVG, whose original label was explicitly left-aligned.
    svg = BASE.svg_xml().replace(
        '<text x="640" y="355" font-family=',
        '<text x="1215" y="355" text-anchor="middle" font-family=',
    )
    (HERE / "工程部署架構.drawio").write_text(drawio, encoding="utf-8")
    (HERE / "工程部署架構.svg").write_text(svg, encoding="utf-8")
    final_png().save(HERE / "工程部署架構.png", optimize=True)
    print("finalized", HERE)


if __name__ == "__main__":
    main()
