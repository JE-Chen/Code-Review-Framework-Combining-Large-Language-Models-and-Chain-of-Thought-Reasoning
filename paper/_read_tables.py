import sys
from pathlib import Path
from docx import Document

sys.stdout.reconfigure(encoding="utf-8")
doc = Document(Path(__file__).parent / "TCSE_v1.9.docx")

for i, t in enumerate(doc.tables):
    print(f"\n=== TABLE {i} ({len(t.rows)} rows x {len(t.columns)} cols) ===")
    for r_idx, row in enumerate(t.rows):
        cells = [c.text.strip().replace("\n", " | ") for c in row.cells]
        print(f"  r{r_idx}: {cells}")
