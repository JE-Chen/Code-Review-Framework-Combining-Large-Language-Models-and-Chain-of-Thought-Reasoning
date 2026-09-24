from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt


SOURCE = Path(__file__).with_name("論文_v3.31.docx")
TARGET = Path(__file__).with_name("論文_v3.32.docx")
PREFIX_SIZES = {
    "人工評分用於檢查前代 Qwen 組態下": 14,
    "本表為前代 Qwen 學生模型組態（2026-02": 12,
    "雖已採用 LLM-as-a-Judge 進行大規模自動評估": 14,
    "分數彙整時，先對同一受評方法": 14,
    "（7） 人工評分適用範圍：": 14,
}


def main() -> None:
    if TARGET.exists():
        raise FileExistsError(f"refusing to overwrite: {TARGET}")
    doc = Document(SOURCE)
    counts = {prefix: 0 for prefix in PREFIX_SIZES}
    for paragraph in doc.paragraphs:
        for prefix, size in PREFIX_SIZES.items():
            if not paragraph.text.startswith(prefix):
                continue
            for run in paragraph.runs:
                if not run.text:
                    continue
                run.font.size = Pt(size)
                rfonts = run._element.get_or_add_rPr().get_or_add_rFonts()
                rfonts.set(qn("w:ascii"), "Times New Roman")
                rfonts.set(qn("w:hAnsi"), "Times New Roman")
                rfonts.set(qn("w:cs"), "Times New Roman")
                rfonts.set(qn("w:eastAsia"), "標楷體")
            counts[prefix] += 1
    if any(value != 1 for value in counts.values()):
        raise ValueError(f"unexpected formatting counts: {counts}")
    doc.save(TARGET)
    print(f"saved {TARGET}: {counts}")


if __name__ == "__main__":
    main()
