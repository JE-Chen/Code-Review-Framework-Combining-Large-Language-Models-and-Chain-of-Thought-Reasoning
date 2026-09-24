from __future__ import annotations

from docx import Document

import _temporarily_remove_table11_v3_27_standalone as base
from _rename_appendix_sections_v3_28 import NEW_RE, TARGET


REPLACEMENTS = {
    "附錄 2-11Reviewer": "附錄 2-11 Reviewer",
    "附錄 2-12Risk": "附錄 2-12 Risk",
}


def replace_spanning(paragraph, old: str, new: str) -> bool:
    nodes = paragraph._p.xpath(".//w:t")
    texts = [node.text or "" for node in nodes]
    combined = "".join(texts)
    start = combined.find(old)
    if start < 0:
        return False
    end = start + len(old)
    cursor = 0
    start_index = start_offset = end_index = end_offset = None
    for index, value in enumerate(texts):
        next_cursor = cursor + len(value)
        if start_index is None and start < next_cursor:
            start_index = index
            start_offset = start - cursor
        if end <= next_cursor:
            end_index = index
            end_offset = end - cursor
            break
        cursor = next_cursor
    if None in (start_index, start_offset, end_index, end_offset):
        raise ValueError(f"cannot map heading text: {combined}")
    if start_index == end_index:
        value = texts[start_index]
        texts[start_index] = value[:start_offset] + new + value[end_offset:]
    else:
        texts[start_index] = texts[start_index][:start_offset] + new
        for index in range(start_index + 1, end_index):
            texts[index] = ""
        texts[end_index] = texts[end_index][end_offset:]
    for node, value in zip(nodes, texts):
        node.text = value
    return True


def main() -> None:
    doc = Document(TARGET)
    counts = {old: 0 for old in REPLACEMENTS}
    for paragraph in doc.paragraphs:
        if paragraph.style.name != "Heading 2":
            continue
        for old, new in REPLACEMENTS.items():
            if replace_spanning(paragraph, old, new):
                counts[old] += 1
    if any(value != 1 for value in counts.values()):
        raise ValueError(f"unexpected replacement counts: {counts}")
    base.APPENDIX_SECTION = NEW_RE
    base.apply_formatting(doc)
    doc.save(TARGET)
    print(counts)


if __name__ == "__main__":
    main()
