"""Generate the v3.10 engineering deployment diagram.

The layout uses explicit line breaks, generous padding, and manually routed
orthogonal connectors so every label remains inside its box at print size.
"""

from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
WIDTH, HEIGHT = 1860, 1080
PNG_SCALE = 2
FONT_SIZE = 20

# id, lines, x, y, width, height, fill
NODES = [
    ("pr", ("GitHub Pull", "Request"), 60, 165, 250, 120, "#E8F1FB"),
    ("runner", ("GitHub Actions", "／CLI"), 385, 165, 280, 120, "#E8F1FB"),
    ("tls", ("TLS", "反向代理"), 740, 165, 250, 120, "#FFF0E1"),
    ("api", ("FastAPI", "非同步工作 API"), 680, 390, 300, 120, "#FFF0E1"),
    ("cot", ("多階段 CoT", "審查管線"), 1080, 390, 300, 120, "#E7F6F1"),
    ("output", ("步驟產物與", "逐行 findings"), 1480, 390, 300, 120, "#E7F6F1"),
    ("lora", ("可選 LoRA", "適配器"), 680, 650, 280, 120, "#F1EAFE"),
    ("model", ("Gemma-4-31B-it", "推論模型"), 1080, 650, 300, 120, "#F1EAFE"),
    ("faiss", ("EmbeddingGemma", "＋FAISS 檢索"), 1450, 650, 330, 120, "#FCE8F1"),
    ("corpus", ("版本化", "規則語料"), 1450, 865, 330, 120, "#FCE8F1"),
]

# source, target, label, source side, target side, explicit intermediate points
EDGES = [
    ("pr", "runner", "觸發", "right", "left", ()),
    ("runner", "tls", "HTTPS", "right", "left", ()),
    ("tls", "api", "submit／poll", "bottom", "top", ((865, 335), (830, 335))),
    ("api", "cot", "排程", "right", "left", ()),
    ("cot", "output", "寫出", "right", "left", ()),
    ("cot", "model", "推論", "bottom", "top", ()),
    ("lora", "model", "掛載", "right", "left", ()),
    ("faiss", "cot", "相關規則", "top", "bottom", ((1615, 570), (1330, 570))),
    ("corpus", "faiss", "建立索引", "top", "bottom", ()),
]


def node(node_id):
    return next(item for item in NODES if item[0] == node_id)


def port(item, side):
    _, _, x, y, w, h, _ = item
    return {
        "left": (x, y + h / 2),
        "right": (x + w, y + h / 2),
        "top": (x + w / 2, y),
        "bottom": (x + w / 2, y + h),
    }[side]


def label_html(lines):
    return "&lt;br&gt;".join(escape(line) for line in lines)


def drawio_xml():
    cells = [
        '<mxCell id="0"/>',
        '<mxCell id="1" parent="0"/>',
        '<mxCell id="title" value="工程部署架構（v3.10）" '
        'style="text;html=1;align=center;verticalAlign=middle;fontSize=20;fontStyle=1;" '
        'vertex="1" parent="1"><mxGeometry x="700" y="45" width="460" height="50" as="geometry"/></mxCell>',
        '<mxCell id="host-band" value="DGX Spark／GB10 部署主機" '
        'style="rounded=1;whiteSpace=wrap;html=1;fontSize=20;fontStyle=1;verticalAlign=top;'
        'spacingTop=14;fillColor=#FFF5CC;fillOpacity=20;strokeColor=#C9A227;dashed=1;" '
        'vertex="1" parent="1"><mxGeometry x="610" y="320" width="1210" height="700" as="geometry"/></mxCell>',
    ]
    for node_id, lines, x, y, w, h, colour in NODES:
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fontSize={FONT_SIZE};fontStyle=1;"
            "align=center;verticalAlign=middle;spacing=14;"
            f"fillColor={colour};strokeColor=#36566F;strokeWidth=2;"
        )
        cells.append(
            f'<mxCell id="{node_id}" value="{label_html(lines)}" style="{style}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" '
            f'height="{h}" as="geometry"/></mxCell>'
        )
    side_xy = {
        "left": ("0", "0.5"), "right": ("1", "0.5"),
        "top": ("0.5", "0"), "bottom": ("0.5", "1"),
    }
    for i, (src, dst, label, src_side, dst_side, points) in enumerate(EDGES, 1):
        ex, ey = side_xy[src_side]
        ix, iy = side_xy[dst_side]
        style = (
            "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=24;html=1;"
            f"exitX={ex};exitY={ey};exitDx=0;exitDy=0;entryX={ix};entryY={iy};entryDx=0;entryDy=0;"
            f"endArrow=block;endFill=1;fontSize={FONT_SIZE};labelBackgroundColor=#FFFFFF;"
            "strokeColor=#36566F;strokeWidth=2;"
        )
        point_xml = ""
        if points:
            point_xml = '<Array as="points">' + "".join(
                f'<mxPoint x="{x}" y="{y}"/>' for x, y in points
            ) + "</Array>"
        cells.append(
            f'<mxCell id="e{i}" value="{escape(label)}" style="{style}" edge="1" '
            f'parent="1" source="{src}" target="{dst}"><mxGeometry relative="1" '
            f'as="geometry">{point_xml}</mxGeometry></mxCell>'
        )
    return (
        '<mxfile host="app.diagrams.net" version="24.7.17">'
        '<diagram id="v310-engineering-deployment" name="Page-1">'
        f'<mxGraphModel dx="{WIDTH}" dy="{HEIGHT}" grid="1" gridSize="10" page="1" '
        f'pageWidth="{WIDTH}" pageHeight="{HEIGHT}"><root>'
        + "".join(cells)
        + "</root></mxGraphModel></diagram></mxfile>"
    )


def svg_multiline(lines, x, y, w, h):
    line_height = 28
    first_y = y + h / 2 - (len(lines) - 1) * line_height / 2 + 7
    tspans = "".join(
        f'<tspan x="{x + w / 2}" y="{first_y + i * line_height}">{escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return (
        f'<text text-anchor="middle" font-family="Microsoft JhengHei, sans-serif" '
        f'font-size="20" font-weight="bold" fill="#17324D">{tspans}</text>'
    )


def svg_xml():
    items = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" '
        'orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#36566F"/></marker></defs>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#FFFFFF"/>',
        '<text x="930" y="77" text-anchor="middle" font-family="Microsoft JhengHei, sans-serif" '
        'font-size="20" font-weight="bold" fill="#17324D">工程部署架構（v3.10）</text>',
        '<rect x="610" y="320" width="1210" height="700" rx="22" fill="#FFF5CC" '
        'fill-opacity="0.2" stroke="#C9A227" stroke-width="2" stroke-dasharray="8 6"/>',
        '<text x="640" y="355" font-family="Microsoft JhengHei, sans-serif" font-size="20" '
        'font-weight="bold" fill="#7A6517">DGX Spark／GB10 部署主機</text>',
    ]
    for src, dst, label, src_side, dst_side, mids in EDGES:
        points = [port(node(src), src_side), *mids, port(node(dst), dst_side)]
        path = "M" + " L".join(f"{x},{y}" for x, y in points)
        items.append(
            f'<path d="{path}" stroke="#36566F" stroke-width="2" fill="none" '
            'marker-end="url(#arrow)"/>'
        )
        segs = list(zip(points, points[1:]))
        a, b = max(segs, key=lambda pair: abs(pair[1][0] - pair[0][0]) + abs(pair[1][1] - pair[0][1]))
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        label_w = max(92, len(label) * 24)
        items.append(f'<rect x="{mx-label_w/2}" y="{my-18}" width="{label_w}" height="30" fill="#FFFFFF"/>')
        items.append(
            f'<text x="{mx}" y="{my+5}" text-anchor="middle" font-family="Microsoft JhengHei, sans-serif" '
            f'font-size="20" fill="#36566F">{escape(label)}</text>'
        )
    for _, lines, x, y, w, h, colour in NODES:
        items.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{colour}" '
            'stroke="#36566F" stroke-width="2"/>'
        )
        items.append(svg_multiline(lines, x, y, w, h))
    items.append("</svg>")
    return "".join(items)


def load_font(size, bold=False):
    names = ["msjhbd.ttc", "msjh.ttc"] if bold else ["msjh.ttc", "arial.ttf"]
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def scale_point(point):
    return tuple(int(value * PNG_SCALE) for value in point)


def draw_arrow(draw, points, colour, width):
    scaled = [scale_point(p) for p in points]
    draw.line(scaled, fill=colour, width=width, joint="curve")
    (x1, y1), (x2, y2) = scaled[-2], scaled[-1]
    angle = math.atan2(y2 - y1, x2 - x1)
    length = 15 * PNG_SCALE
    wings = [
        (x2 + length * math.cos(angle + delta), y2 + length * math.sin(angle + delta))
        for delta in (2.65, -2.65)
    ]
    draw.polygon([(x2, y2), *wings], fill=colour)


def draw_centered_lines(draw, lines, box, font, fill):
    x, y, w, h = box
    spacing = 8 * PNG_SCALE
    bboxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    heights = [b[3] - b[1] for b in bboxes]
    total = sum(heights) + spacing * (len(lines) - 1)
    cursor = y + (h - total) / 2
    for line, bbox, line_h in zip(lines, bboxes, heights):
        line_w = bbox[2] - bbox[0]
        if line_w > w - 28 * PNG_SCALE:
            raise RuntimeError(f"label overflow: {line!r}, {line_w} > {w - 28 * PNG_SCALE}")
        draw.text((x + w / 2, cursor), line, anchor="ma", font=font, fill=fill)
        cursor += line_h + spacing


def png_image():
    image = Image.new("RGB", (WIDTH * PNG_SCALE, HEIGHT * PNG_SCALE), "white")
    draw = ImageDraw.Draw(image)
    font = load_font(FONT_SIZE * PNG_SCALE)
    bold = load_font(FONT_SIZE * PNG_SCALE, bold=True)
    edge_font = load_font(FONT_SIZE * PNG_SCALE)
    draw.text(scale_point((WIDTH / 2, 72)), "工程部署架構（v3.10）", anchor="mm", font=bold, fill="#17324D")
    draw.rounded_rectangle(scale_point((610, 320, 1820, 1020)), radius=22 * PNG_SCALE,
                           fill="#FFFBEA", outline="#C9A227", width=3 * PNG_SCALE)
    draw.text(scale_point((640, 345)), "DGX Spark／GB10 部署主機", anchor="la", font=bold, fill="#7A6517")
    for src, dst, label, src_side, dst_side, mids in EDGES:
        points = [port(node(src), src_side), *mids, port(node(dst), dst_side)]
        draw_arrow(draw, points, "#36566F", 3 * PNG_SCALE)
        segs = list(zip(points, points[1:]))
        a, b = max(segs, key=lambda pair: abs(pair[1][0] - pair[0][0]) + abs(pair[1][1] - pair[0][1]))
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        pos = scale_point((mx, my))
        bbox = draw.textbbox(pos, label, anchor="mm", font=edge_font)
        pad_x, pad_y = 8 * PNG_SCALE, 5 * PNG_SCALE
        draw.rectangle((bbox[0]-pad_x, bbox[1]-pad_y, bbox[2]+pad_x, bbox[3]+pad_y), fill="white")
        draw.text(pos, label, anchor="mm", font=edge_font, fill="#36566F")
    for _, lines, x, y, w, h, colour in NODES:
        box = scale_point((x, y, w, h))
        draw.rounded_rectangle(scale_point((x, y, x + w, y + h)), radius=16 * PNG_SCALE,
                               fill=colour, outline="#36566F", width=3 * PNG_SCALE)
        draw_centered_lines(draw, lines, box, bold, "#17324D")
    return image


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "工程部署架構.drawio").write_text(drawio_xml(), encoding="utf-8")
    (OUT / "工程部署架構.svg").write_text(svg_xml(), encoding="utf-8")
    png_image().save(OUT / "工程部署架構.png", optimize=True)
    print("generated", OUT)


if __name__ == "__main__":
    main()
