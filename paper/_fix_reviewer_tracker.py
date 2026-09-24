from pathlib import Path


path = Path(__file__).with_name("REVIEWER_ISSUES.md")
text = path.read_text(encoding="utf-8")
text = text.replace("- 已完成：17 項。\n- 部分完成：4 項。", "- 已完成：16 項。\n- 部分完成：5 項。")
path.write_text(text, encoding="utf-8")
