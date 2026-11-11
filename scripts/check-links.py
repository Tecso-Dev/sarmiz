#!/usr/bin/env python3
"""Fail if any relative link in a Markdown file points at a file that does not exist.

External links (http, https, mailto) and pure in-page anchors are skipped.
Run from anywhere: the repository root is found from this script's location.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "#")


def main() -> int:
    broken = []
    files = sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)
    for md in files:
        in_code = False
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            for target in LINK.findall(line):
                if target.startswith(SKIP_PREFIXES):
                    continue
                path = unquote(target.split("#", 1)[0])
                if not path:
                    continue
                if not (md.parent / path).exists():
                    broken.append(f"{md.relative_to(ROOT)}:{lineno}: {target}")
    for item in broken:
        print(f"broken link: {item}")
    print(f"checked {len(files)} files, {len(broken)} broken links")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
