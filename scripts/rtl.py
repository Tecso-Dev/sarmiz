#!/usr/bin/env python3
"""Wrap the prose of Markdown files in <div dir="rtl"> so Persian reads right to left on GitHub.

Code fences (including mermaid) stay outside the wrapper, so code keeps its
left-to-right layout. The script is idempotent: it removes the wrappers it
added before and builds them again.

    python3 scripts/rtl.py              # every .md file in the repository
    python3 scripts/rtl.py FILE...      # only these files

Files with no Persian text are left untouched.

Rules for authors: put every HTML <div> on its own line, never put a code
fence inside <details>, and never indent a code fence inside a list.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPEN = '<div dir="rtl">'
CLOSE = "</div>"
FENCE = re.compile(r"^(```+|~~~+)")
DIV_OPEN = re.compile(r"^<div\b[^>]*>$")
LTR_SPAN = re.compile(r'<span dir="ltr">(`[^`\n]+`)</span>')
CODE_SPAN = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
LTR_HTML = re.compile(r'<span dir="ltr">(<code>[^<]+</code>)</span>')
HTML_CODE = re.compile(r"(?<!<span dir=\"ltr\">)<code>([^<]+)</code>")
PERSIAN = re.compile(r"[\u0600-\u06FF]")
WORDY = re.compile(r"^[A-Za-z0-9_]$|^[A-Za-z0-9_].*[A-Za-z0-9_]$")


def isolate_code(line):
    """Inline code that starts or ends with punctuation (/etc, --help, ~/.ssh) flips inside
    right-to-left text. Wrapping it in <span dir="ltr"> keeps it in order."""
    line = LTR_SPAN.sub(r"\1", line)

    def rep(m):
        return m.group(0) if WORDY.match(m.group(1)) else f'<span dir="ltr">{m.group(0)}</span>'

    line = CODE_SPAN.sub(rep, line)
    line = LTR_HTML.sub(r"\1", line)
    return HTML_CODE.sub(rep, line)


OPTION = re.compile(r"^(الف|ب|ج|د)\) ")


def option_breaks(lines):
    """Quiz options each sit on their own line: end the line before an option with <br>."""
    out = list(lines)
    for i in range(len(out) - 1):
        if OPTION.match(out[i + 1]) and out[i].strip() and not out[i].endswith("<br>"):
            out[i] += "<br>"
    return out


def strip_wrappers(lines):
    out, stack = [], []
    for line in lines:
        s = line.strip()
        if s == OPEN:
            stack.append("rtl")
            continue
        if DIV_OPEN.match(s):
            stack.append("other")
        elif s == CLOSE:
            if stack and stack.pop() == "rtl":
                continue
        out.append(line)
    return out


def segments(lines):
    """Yield ('code', lines) and ('prose', lines) in order."""
    buf, in_code, fence = [], False, ""
    for line in lines:
        m = FENCE.match(line.strip()) if not line.startswith((" ", "\t")) else None
        if not in_code and m:
            if buf:
                yield "prose", buf
            buf, in_code, fence = [line], True, m.group(1)[:3]
            continue
        buf.append(line)
        if in_code and line.strip().startswith(fence) and len(buf) > 1 and line.strip().strip(fence[0]) == "":
            yield "code", buf
            buf, in_code = [], False
    if buf:
        yield ("code" if in_code else "prose"), buf


def trim(block):
    while block and not block[0].strip():
        block = block[1:]
    while block and not block[-1].strip():
        block = block[:-1]
    return block


def wrap(text):
    lines = strip_wrappers(text.splitlines())
    out = []
    for kind, block in segments(lines):
        block = trim(block)
        if not block:
            continue
        if kind == "code":
            out += block + [""]
        else:
            out += [OPEN, ""] + option_breaks([isolate_code(l) for l in block]) + ["", CLOSE, ""]
    return "\n".join(out).rstrip() + "\n"


def main(argv):
    files = [Path(a) for a in argv] or sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts and "node_modules" not in p.parts)
    changed = 0
    for f in files:
        old = f.read_text(encoding="utf-8")
        if not PERSIAN.search(old):
            continue  # English-only files (AGENTS.md, CLAUDE.md) stay left to right
        new = wrap(old)
        if new != old:
            f.write_text(new, encoding="utf-8")
            changed += 1
    print(f"rtl: {changed} of {len(files)} files rewritten")


if __name__ == "__main__":
    main(sys.argv[1:])
