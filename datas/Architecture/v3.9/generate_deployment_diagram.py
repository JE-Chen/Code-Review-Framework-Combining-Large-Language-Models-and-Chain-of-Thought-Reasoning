"""Generate the v3.9 engineering deployment diagram artifacts."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
WIDTH, HEIGHT = 1600, 900
FONT_SIZE = 20

NODES = [
    ("pr", "GitHub Pull Request", 70, 180, 230, 90, "#E8F1FB"),
    ("runner", "GitHub Actions／CLI", 360, 180, 240, 90, "#E8F1FB"),
    ("tls", "TLS 反向代理", 660, 180, 210, 90, "#FFF0E1"),
    ("api", "FastAPI 非同步工作 API", 940, 180, 280, 90, "#FFF0E1"),
    ("cot", "多階段 CoT 管線", 940, 370, 280, 90, "#E7F6F1"),
    ("model", "Gemma-4-31B-it", 620, 370, 230, 90, "#F1EAFE"),
    ("lora", "可選 LoRA 適配器", 350, 370, 220, 90, "#F1EAFE"),
    ("faiss", "EmbeddingGemma＋FAISS", 1270, 370, 270, 90, "#FCE8F1"),
    ("corpus", "版本化規則語料", 1270, 570, 270, 90, "#FCE8F1"),
    ("output", "步驟產物與逐行 findings", 900, 610, 340, 90, "#E7F6F1"),
]

EDGES = [
    ("pr", "runner", "觸發"),
    ("runner", "tls", "HTTPS"),
    ("tls", "api", "submit／poll"),
    ("api", "cot", "排程"),
    ("cot", "model", "推論"),
    ("lora", "model", "掛載"),
    ("faiss", "cot", "相關規則"),
    ("corpus", "faiss", "建立索引"),
    ("cot", "output", "寫出"),
]


def center(node):
    _, _, x, y, w, h, _ = node
    return x + w / 2, y + h / 2


def by_id(node_id):
    return next(node for node in NODES if node[0] == node_id)


def drawio_xml() -> str:
    cells = [
        '<mxCell id="0"/>',
        '<mxCell id="1" parent="0"/>',
        '<mxCell id="title" value="工程部署架構（v3.9）" '
        'style="text;html=1;align=center;verticalAlign=middle;fontSize=20;fontStyle=1;" '
        'vertex="1" parent="1"><mxGeometry x="600" y="35" width="400" height="45" as="geometry"/></mxCell>',
        '<mxCell id="host-band" value="DGX Spark／GB10 部署主機" '
        'style="rounded=1;whiteSpace=wrap;html=1;fontSize=20;fontStyle=1;'
        'verticalAlign=top;fillColor=#FFF5CC;fillOpacity=20;strokeColor=#C9A227;'
        'dashed=1;" vertex="1" parent="1"><mxGeometry x="300" y="300" '
        'width="1260" height="450" as="geometry"/></mxCell>',
    ]
    for node_id, label, x, y, w, h, colour in NODES:
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;fontSize={FONT_SIZE};fontStyle=1;"
            f"fillColor={colour};strokeColor=#36566F;strokeWidth=2;"
        )
        cells.append(
            f'<mxCell id="{node_id}" value="{escape(label)}" style="{style}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" '
            f'height="{h}" as="geometry"/></mxCell>'
        )
    for i, (src, dst, label) in enumerate(EDGES, 1):
        style = (
            "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;"
            f"jettySize=auto;html=1;endArrow=block;endFill=1;fontSize={FONT_SIZE};"
            "strokeColor=#36566F;strokeWidth=2;"
        )
        cells.append(
            f'<mxCell id="e{i}" value="{escape(label)}" style="{style}" edge="1" '
            f'parent="1" source="{src}" target="{dst}"><mxGeometry relative="1" '
            f'as="geometry"/></mxCell>'
        )
    return (
        '<mxfile host="app.diagrams.net" version="24.7.17">'
        '<diagram id="v39-engineering-deployment" name="Page-1">'
        f'<mxGraphModel dx="1600" dy="900" grid="1" gridSize="10" page="1" '
        f'pageWidth="{WIDTH}" pageHeight="{HEIGHT}"><root>'
        + "".join(cells)
        + "</root></mxGraphModel></diagram></mxfile>"
    )


def svg_xml() -> str:
    items = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" '
        'refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#36566F"/>'
        '</marker></defs>',
        '<rect width="1600" height="900" fill="#FFFFFF"/>',
        '<text x="800" y="65" text-anchor="middle" font-family="Microsoft JhengHei, sans-serif" '
        'font-size="20" font-weight="bold" fill="#17324D">工程部署架構（v3.9）</text>',
        '<rect x="300" y="300" width="1260" height="450" rx="22" fill="#FFF5CC" '
        'fill-opacity="0.2" stroke="#C9A227" stroke-width="2" stroke-dasharray="8 6"/>',
        '<text x="325" y="330" font-family="Microsoft JhengHei, sans-serif" '
        'font-size="20" font-weight="bold" fill="#7A6517">DGX Spark／GB10 部署主機</text>',
    ]
    for src, dst, label in EDGES:
        sx, sy = center(by_id(src))
        tx, ty = center(by_id(dst))
        s = by_id(src)
        d = by_id(dst)
        if abs(tx - sx) >= abs(ty - sy):
            x1 = s[2] + s[4] if tx > sx else s[2]
            y1 = sy
            x2 = d[2] if tx > sx else d[2] + d[4]
            y2 = ty
        else:
            x1 = sx
            y1 = s[3] + s[5] if ty > sy else s[3]
            x2 = tx
            y2 = d[3] if ty > sy else d[3] + d[5]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        items.append(
            f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#36566F" stroke-width="2" '
            'fill="none" marker-end="url(#arrow)"/>'
        )
        items.append(
            f'<rect x="{mx-55}" y="{my-16}" width="110" height="26" fill="#FFFFFF"/>'
            f'<text x="{mx}" y="{my+3}" text-anchor="middle" '
            f'font-family="Microsoft JhengHei, sans-serif" font-size="20" '
            f'fill="#36566F">{escape(label)}</text>'
        )
    for _, label, x, y, w, h, colour in NODES:
        items.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" '
            f'fill="{colour}" stroke="#36566F" stroke-width="2"/>'
        )
        items.append(
            f'<text x="{x+w/2}" y="{y+h/2+7}" text-anchor="middle" '
            'font-family="Microsoft JhengHei, sans-serif" font-size="20" '
            f'font-weight="bold" fill="#17324D">{escape(label)}</text>'
        )
    items.append("</svg>")
    return "".join(items)


def load_font(size: int):
    candidates = [
        Path("C:/Windows/Fonts/msjh.ttc"),
        Path("C:/Windows/Fonts/msjhbd.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def png_image() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    font = load_font(25)
    bold = load_font(27)
    draw.text((WIDTH / 2, 50), "工程部署架構（v3.9）", anchor="mm", font=bold, fill="#17324D")
    draw.rounded_rectangle((300, 300, 1560, 750), radius=22, fill="#FFFBEA",
                           outline="#C9A227", width=3)
    draw.text((325, 318), "DGX Spark／GB10 部署主機", anchor="la", font=font,
              fill="#7A6517")
    for src, dst, label in EDGES:
        sx, sy = center(by_id(src))
        tx, ty = center(by_id(dst))
        draw.line((sx, sy, tx, ty), fill="#36566F", width=3)
        angle = __import__("math").atan2(ty - sy, tx - sx)
        tip = (tx, ty)
        wings = []
        for delta in (2.65, -2.65):
            wings.append((tx + 16 * __import__("math").cos(angle + delta),
                          ty + 16 * __import__("math").sin(angle + delta)))
        draw.polygon([tip, *wings], fill="#36566F")
        mx, my = (sx + tx) / 2, (sy + ty) / 2
        box = draw.textbbox((mx, my), label, anchor="mm", font=font)
        draw.rectangle((box[0]-5, box[1]-3, box[2]+5, box[3]+3), fill="white")
        draw.text((mx, my), label, anchor="mm", font=font, fill="#36566F")
    for _, label, x, y, w, h, colour in NODES:
        draw.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=colour,
                               outline="#36566F", width=3)
        draw.text((x + w / 2, y + h / 2), label, anchor="mm", font=font,
                  fill="#17324D")
    return image


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "工程部署架構.drawio").write_text(drawio_xml(), encoding="utf-8")
    (OUT / "工程部署架構.svg").write_text(svg_xml(), encoding="utf-8")
    png_image().save(OUT / "工程部署架構.png")


if __name__ == "__main__":
    main()
