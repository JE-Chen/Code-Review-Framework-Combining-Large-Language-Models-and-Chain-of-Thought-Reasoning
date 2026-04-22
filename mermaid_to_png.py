"""
Mermaid to PNG converter.

Usage:
    python mermaid_to_png.py                          # default: architecture.md -> output/
    python mermaid_to_png.py -i architecture.md -o output/

Prerequisites:
    npm install -g @mermaid-js/mermaid-cli
"""

import argparse
import os
import re
import subprocess
import sys
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile


def _find_node_dir() -> str | None:
    """Find the directory containing node executable."""
    found = shutil.which("node")
    if found:
        return str(Path(found).parent)
    if sys.platform == "win32":
        # Common Node.js install locations on Windows
        candidates = [
            Path(os.environ.get("ProgramFiles", "")) / "nodejs",
            Path(os.environ.get("ProgramFiles(x86)", "")) / "nodejs",
            Path("D:/nodejs"),
        ]
        for candidate in candidates:
            if (candidate / "node.exe").is_file():
                return str(candidate)
    return None


def _find_mmdc() -> str | None:
    """Find the mmdc executable, checking Windows npm global bin as fallback."""
    found = shutil.which("mmdc")
    if found:
        return found
    if sys.platform == "win32":
        # npm global bin on Windows: %APPDATA%/npm/mmdc.cmd
        npm_bin = Path(os.environ.get("APPDATA", "")) / "npm" / "mmdc.cmd"
        if npm_bin.is_file():
            return str(npm_bin)
    return None


def _build_env() -> dict[str, str]:
    """Build subprocess env with node on PATH."""
    env = os.environ.copy()
    node_dir = _find_node_dir()
    if node_dir and node_dir not in env.get("PATH", ""):
        env["PATH"] = node_dir + os.pathsep + env.get("PATH", "")
    return env


def extract_mermaid_blocks(markdown_path: Path) -> list[dict]:
    """Extract all ```mermaid ... ``` blocks from a markdown file."""
    content = markdown_path.read_text(encoding="utf-8")

    pattern = re.compile(
        r"(?:^|\n)##\s+(.+?)\n"        # capture the heading before the block
        r"[\s\S]*?"                      # any content between heading and code fence
        r"```mermaid\s*\n([\s\S]*?)```", # the mermaid block
        re.MULTILINE,
    )

    blocks = []
    for match in pattern.finditer(content):
        title = match.group(1).strip()
        code = match.group(2).strip()
        # sanitize title for filename
        safe_name = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_").lower()
        blocks.append({"title": title, "filename": safe_name, "code": code})

    if not blocks:
        # fallback: just grab all mermaid blocks without titles
        simple_pattern = re.compile(r"```mermaid\s*\n([\s\S]*?)```")
        for i, match in enumerate(simple_pattern.finditer(content)):
            blocks.append({
                "title": f"diagram_{i + 1}",
                "filename": f"diagram_{i + 1}",
                "code": match.group(1).strip(),
            })

    return blocks


def convert_with_mmdc(
    mermaid_code: str, output_path: Path, mmdc_path: str = "mmdc", env: dict | None = None,
) -> bool:
    """Convert mermaid code to PNG using mmdc (Mermaid CLI)."""
    with NamedTemporaryFile(mode="w", suffix=".mmd", delete=False, encoding="utf-8") as tmp:
        tmp.write(mermaid_code)
        tmp_path = Path(tmp.name)

    try:
        config_file = Path(__file__).parent / "mermaid_config.json"
        cmd = [mmdc_path, "-i", str(tmp_path), "-o", str(output_path),
               "-b", "white", "-s", "3"]
        if config_file.is_file():
            cmd += ["-c", str(config_file)]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, shell=True, env=env,
        )
        if result.returncode != 0:
            print(f"  [ERROR] mmdc failed: {result.stderr.strip()}")
            return False
        return True
    except FileNotFoundError:
        print("[ERROR] mmdc not found. Install it with:")
        print("        npm install -g @mermaid-js/mermaid-cli")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("  [ERROR] mmdc timed out")
        return False
    finally:
        tmp_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Convert Mermaid diagrams in Markdown to PNG")
    parser.add_argument("-i", "--input", default="architecture.md",
                        help="Input markdown file (default: architecture.md)")
    parser.add_argument("-o", "--output", default="output",
                        help="Output directory (default: output/)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}")
        sys.exit(1)

    mmdc_path = _find_mmdc()
    if not mmdc_path:
        print("[ERROR] mmdc not found. Install it with:")
        print("        npm install -g @mermaid-js/mermaid-cli")
        sys.exit(1)

    env = _build_env()

    output_dir.mkdir(parents=True, exist_ok=True)

    blocks = extract_mermaid_blocks(input_path)
    if not blocks:
        print("No mermaid blocks found.")
        sys.exit(0)

    print(f"Found {len(blocks)} mermaid diagram(s) in {input_path}\n")

    for i, block in enumerate(blocks, 1):
        out_file = output_dir / f"{block['filename']}.png"
        print(f"[{i}/{len(blocks)}] {block['title']} -> {out_file}")
        success = convert_with_mmdc(block["code"], out_file, mmdc_path, env)
        if success:
            print(f"  OK ({out_file.stat().st_size / 1024:.1f} KB)")
        else:
            print(f"  FAILED")

    print("\nDone.")


if __name__ == "__main__":
    main()
