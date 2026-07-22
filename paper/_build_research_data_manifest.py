from hashlib import sha256
from pathlib import Path


root = Path(__file__).resolve().parents[1] / "datas" / "Research_Data"
manifest = root / "MANIFEST.sha256"
lines = []
for path in sorted(p for p in root.rglob("*") if p.is_file() and p != manifest):
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    relative = path.relative_to(root).as_posix()
    lines.append(f"{digest.hexdigest()}  {relative}")
manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"{manifest}: {len(lines)} files")
