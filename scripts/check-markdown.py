#!/usr/bin/env python3
"""Check the Markdown layout rules that keep Persian pages rendering well on GitHub.

- every <div> is closed, and code fences never sit inside <div dir="rtl">
- code fences are closed and never sit inside <details>
- every file with Persian text has the right-to-left wrapper

Fix most problems with:  python3 scripts/rtl.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FENCE = re.compile(r"^(```+|~~~+)")
DIV_OPEN = re.compile(r"^<div\b[^>]*>$")
PERSIAN = re.compile(r"[؀-ۿ]")
INLINE_CODE = re.compile(r"`[^`]*`")


def check(path):
    errors = []
    stack, details, in_code, fence = [], 0, False, ""
    text = path.read_text(encoding="utf-8")
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if in_code:
            if s.startswith(fence) and s.strip(fence[0]) == "":
                in_code = False
            continue
        m = FENCE.match(s)
        if m and not line.startswith((" ", "\t")):
            if "rtl" in stack:
                errors.append(f"{n}: code fence inside <div dir=\"rtl\">")
            if details:
                errors.append(f"{n}: code fence inside <details>")
            in_code, fence = True, m.group(1)[:3]
            continue
        if DIV_OPEN.match(s):
            stack.append("rtl" if 'dir="rtl"' in s else "other")
        elif s == "</div>":
            if not stack:
                errors.append(f"{n}: </div> without an open <div>")
            else:
                stack.pop()
        bare = INLINE_CODE.sub("", s)
        details += bare.count("<details") - bare.count("</details>")
    if in_code:
        errors.append("end of file: code fence never closed")
    if stack:
        errors.append(f"end of file: {len(stack)} <div> left open")
    if details:
        errors.append("end of file: <details> not balanced")
    if PERSIAN.search(text) and '<div dir="rtl">' not in text:
        errors.append("Persian text without the right-to-left wrapper (run scripts/rtl.py)")
    return errors


def main():
    files = sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts and "node_modules" not in p.parts)
    bad = 0
    for f in files:
        for e in check(f):
            print(f"{f.relative_to(ROOT)}:{e}")
            bad += 1
    print(f"checked {len(files)} files, {bad} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
