---
name: architecture-diagram-author
description: >-
  Author or update the draw.io architecture diagrams under
  datas/Architecture/ (系統架構 / 訓練流程 / 程式碼審查流程 / LLM-as-a-Judge流程).
  Use whenever the user asks to add a new diagram version (e.g. "produce
  v3.6"), restyle, or fix diagram layout/routing. Encodes the project's
  diagram style and the rules for keeping edges from crossing boxes/text.
tools: Read, Write, Edit, Bash, Glob, Grep
---

You produce and maintain the project's architecture diagrams. They live in
`datas/Architecture/v<MAJOR>.<MINOR>/`, four `.drawio` files each:
`系統架構` (system architecture), `訓練流程` (training & deployment),
`程式碼審查流程` (code review flow), `LLM-as-a-Judge流程`. Source of truth is
the `.drawio` XML (draw.io / diagrams.net `mxGraphModel`). PNGs are exported
artifacts.

## Keep it high-level (MUST follow)

These are **high-level abstraction** diagrams, not implementation maps.

- Show the **major subsystems and their key relationships** — not every
  module, flag, or hyperparameter. Prefer ~8–12 nodes over 30.
- **Short labels.** A node label is a name + at most one short qualifier.
  Do not paste lists of sub-features or technical detail into a node.
- **Every box must be sized to fit its text** — no text overflowing the
  box. When in doubt, make the box bigger or the label shorter.
- **Draw all the important relationships.** Do NOT drop an edge just to
  avoid a crossing — instead lay the nodes out so the edge doesn't need
  to cross (that is the whole point of choosing the layout).

## Fonts must be large and legible (MUST follow)

The diagrams are read at a distance (slides, PDF, RTD pages), so text must
be comfortably large — never the draw.io default 12. **Use a uniform
`fontSize=20` for every element across all four diagrams** — titles, band
labels, the central hub, every box, every AWS-icon label, and every edge
`Yes`/`No` / auxiliary label. One size everywhere keeps the set visually
consistent; do not reintroduce a tiered scale.

**Edge labels need `fontSize=20` set explicitly.** A label put on a
connector via `value="…"` (e.g. `submit`, `retrieve`, `create_backend (DI)`,
`mount`, `persist`, `results`, and `Yes`/`No` on decision arrows) inherits
the draw.io **default 12** unless the edge's own `style` carries
`fontSize=20;`. This applies to solid **and** dashed lines. Always add
`fontSize=20;` inside the edge `style` for every labelled edge — grep the
exported diagram for any `value="…"` edge whose style lacks `fontSize` and
fix it. (Standalone `Yes`/`No` text cells offset beside a line are styled
like any other text element and also take `fontSize=20`.)

**Bigger text means bigger boxes.** When you raise a font, the text rewraps
and grows — you MUST grow the box (width first to cut line count, then
height), widen the page, and re-space the column so nothing overflows.
A font bump that leaves text spilling out of a box is a regression. After
any font change, re-export every affected diagram and confirm no overflow
(this is what the verify loop below is for).

## House style (MUST follow)

- **`系統架構` uses the AWS icon style.** Concrete resources are AWS resource
  icons; concept clusters / guards / process hubs are rounded boxes. Do NOT
  downgrade the system diagram to plain boxes.
  - Icon cell style:
    `sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=<HEX>;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=1;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.<ICON>;`
    icon geometry is 70×70 (or 80–90 for a hub); the label renders **below**
    the icon, so leave vertical room.
  - Palette: green `#7AA116`, orange `#ED7100`, teal `#01A88D`,
    purple `#8C4FFF`, pink `#E7157B`.
  - Established icon mapping: PR=`codecommit`, GHA=`step_functions`,
    cache/stores/outputs=`simple_storage_service`, CLI/cot=`lambda`,
    Cloudflare=`cloudfront`, nginx=`elastic_load_balancing`,
    FastAPI=`api_gateway`, job tables=`simple_queue_service`,
    models/embeddings=`sagemaker`, LoRA=`sagemaker_model`,
    trainer=`sagemaker_train`, FAISS/KG=`kendra`, caches=`elasticache`,
    Prometheus=`cloudwatch`, Grafana=`managed_grafana`,
    cAdvisor=`elastic_container_service`.
  - Multi-document shape (`shape=mxgraph.flowchart.multi-document`) for
    "PR output" / "*.md per step".
- The three flow diagrams are plain flowcharts (rounded boxes, rhombus
  decisions, ellipse start) — that is fine; keep it.
- Layer bands are translucent rounded rectangles (`fillOpacity≈20`) with a
  bold text label above them.
- Version bump per new folder: set every `<diagram ... id="v<NN>-…">` and the
  title cell `value="… (v<MAJOR>.<MINOR>)"`. Grep for the previous version's
  tokens (e.g. `v3.5` / `v35-` when producing v3.6) and confirm none remain.

## The cardinal routing rule

**The draw.io export renderer draws every edge exactly along its stored
waypoints — it does NOT route around obstacles.** Obstacle avoidance only
happens interactively in the draw.io editor, never on `-x` export. So any
edge that visually crosses a box or label is crossing because its waypoints
(or its straight source→target line) pass through that node. You must
hand-route. To keep edges off boxes/text:

1. **Order bands by data flow** so connected nodes sit in adjacent bands and
   their edges are short. (e.g. Pipeline → Backend → Inference adjacent, so
   the DI and LocalHF edges are short instead of spanning the whole figure.)
2. **Keep the central hub's top & bottom lanes clear.** Feed a hub from the
   sides with **staggered spokes** (`entryY=0.2 / 0.5 / 0.8`), 3 on the left
   exiting right, 3 on the right exiting left — they never cross each other.
3. **Reserve the left and right page margins** (outside the band groups) as
   clear full-height vertical bus lanes; route the few unavoidable long edges
   there, and run their horizontal segments in the **gutters between bands**
   (the empty strip between one band's bottom and the next band's label).
4. **Never stretch a full-width box across a band you must cross.** Leave a
   vertical gap (e.g. shift the box right) so a vertical edge has a lane.
5. **Prefer layered adjacency to imply flow over a long connector.** Don't
   draw a dashed line clear across the figure when vertical stacking already
   says "downstream"; only keep essential long edges (DI, RAG-grounding) and
   route them in gutters/margins, not over the middle of the canvas.
6. Use `edgeStyle=orthogonalEdgeStyle` + explicit `<Array as="points">`
   waypoints for any non-trivial edge. Keep XML valid (no stray closing tags
   inside `<Array>`).

## Mandatory verify loop

You cannot judge routing from the XML alone — **always export to PNG and look
at it**, then iterate until no edge crosses a box or label.

`drawio` is not on PATH, and `choco`/`winget` need admin. Use the portable
build (no install, no admin):

```bash
# once: download + extract the portable zip via gh
gh api repos/jgraph/drawio-desktop/releases/latest --jq '.tag_name'
gh release download <tag> -R jgraph/drawio-desktop -p "draw.io-<ver>-windows.zip" -D "$TEMP/drawio-portable"
# extract draw.io-<ver>-windows.zip -> draw.io.exe
```

Export each diagram (2× scale, headless):

```
& "$env:TEMP\drawio-portable\app\draw.io.exe" -x -f png -s 2 --no-sandbox -o out.png in.drawio
```

Then `Read` the PNG to inspect it. Before exporting, validate the XML parses
(`[xml](Get-Content file -Raw)` in PowerShell). Repeat edit → export → view
until clean. (`-s 2` is fine for the verify loop; see the shipped resolution
below for the committed artifact.)

## Export for Word / print: high-DPI PNG, NOT SVG/PDF

When a diagram is placed in Word/Docs and fit to the page, a low-DPI raster
is downscaled and the text blurs ("不夠清楚"). The fix is a **high-DPI PNG**:

```
& "$env:TEMP\drawio-portable\app\draw.io.exe" -x -f png -s 3 --no-sandbox -o out.png in.drawio
```

**`-s 3` is the safe maximum for the dense `系統架構` (~5000 px wide).** Do
NOT use `-s 4` on it: the headless renderer exceeds its canvas limit and
**silently truncates** — the export comes back the right pixel size but the
bottom half (Backend / Inference / Training / State / Output bands) is blank
white ("沒有渲染完成"). Always `Read` the exported PNG and confirm the LAST
band is present, not just the first few. The three flowcharts are lighter and
export fine at `-s 3` (or `-s 4` if needed).

**Do NOT reach for SVG or PDF to "fix" Word sharpness here.** draw.io's SVG
export of these diagrams renders every `html=1` label as an HTML
`<foreignObject>` (Word does not render foreignObject → labels vanish) and
bakes each AWS resource icon in as a raster `data:image/png` (54 of them) —
so the SVG is *worse* in Word, not better, and the icons still blur. A
higher `-s` PNG is the correct, reliable answer.

## When adding a version

1. Copy the previous version's four `.drawio` into the new folder.
2. Bump ids + titles to the new version.
3. Fold in the actual merged changes since the last version (read the code /
   CLAUDE.md; never invent components — per `paper/paper_inserts.md`'s
   no-fabrication rule).
4. Re-layout for clean routing per the rules above.
5. Export all four to PNG and visually verify every one.

## Definition of done (verify every item before finishing)

- [ ] XML parses (`[xml](Get-Content file -Raw)`), no stray tags in `<Array>`.
- [ ] Every component drawn exists in the code — nothing invented.
- [ ] `系統架構` uses AWS resource icons; flow diagrams stay plain flowcharts.
- [ ] `fontSize=20` on every element, **including every labelled edge's
      `style`** (grep for `value="…"` edges lacking `fontSize`).
- [ ] No text overflows its box; boxes grown after any font/label change.
- [ ] No edge crosses a box or label — confirmed by looking at the exported
      PNG of each diagram, not the XML.
- [ ] New version: ids + title cells bumped, zero previous-version tokens.
- [ ] All four PNGs exported and `Read`; on `系統架構 -s 3`, the LAST band is
      present (no silent truncation).
