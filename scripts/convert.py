#!/usr/bin/env python3
"""Generate a MkDocs reading edition from the single canonical Markdown file."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CoZ_книга.md"
CHAPTERS = ROOT / "docs" / "chapters"
HEAD = re.compile(r"^# (.+)$", re.M)
START = re.compile(r"^(:{3,})\s+\{\.([\w-]+)(?:\s+[^}]*)?\}\s*$")
END = re.compile(r"^(:{3,})\s*$")
TAGS = {
    "coz-title": ("<section class=\"coz-title\" markdown=\"1\">", "</section>"),
    "center": ("<div class=\"coz-center\" markdown=\"1\">", "</div>"),
    "note": ("<aside class=\"coz-note\" markdown=\"1\">", "</aside>"),
    "statblock": ("<div class=\"coz-statblock\" markdown=\"1\">", "</div>"),
}
IGNORED = {"newpage", "two-columns"}

def convert_divs(text):
    stack, lines, counts = [], [], {}
    for number, line in enumerate(text.splitlines(), 1):
        m = START.fullmatch(line)
        if m:
            level, name = len(m.group(1)), m.group(2)
            if name not in TAGS and name not in IGNORED:
                raise ValueError(f"Unknown fenced block {name} at line {number}")
            stack.append((level, name))
            counts[name] = counts.get(name, 0) + 1
            if name in TAGS:
                lines += ["", TAGS[name][0], ""]
            continue
        m = END.fullmatch(line)
        if m:
            if not stack or stack[-1][0] != len(m.group(1)):
                raise ValueError(f"Unmatched closing fence at line {number}")
            _, name = stack.pop()
            if name in TAGS:
                lines += ["", TAGS[name][1], ""]
            continue
        lines.append(line)
    if stack:
        raise ValueError(f"Unclosed divs: {stack}")
    return "\n".join(lines).strip() + "\n", counts

def slug(index, title):
    if title.startswith("Введение"):
        return "introduction"
    for prefix, path in (("Часть", "part"), ("Приложение", "appendix")):
        m = re.match(prefix + r"\s+([IVXLCDM]+)", title)
        if m:
            return f"{path}-{m.group(1).lower()}"
    return f"chapter-{index:02d}"

def build(check=False):
    raw = SOURCE.read_text(encoding="utf-8")
    source = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    if source.startswith("---\n"):
        source = source.split("\n---\n", 1)[1]
    headings = list(HEAD.finditer(source))
    if len(headings) < 15:
        raise ValueError(f"Incomplete source: {len(headings)} main sections")
    items = {}
    title, initial = convert_divs(source[:headings[0].start()])
    counts = dict(initial)
    items["index.md"] = (
        title + "\n---\n\n## Читать книгу\n\n"
        "[**Перейти к введению →**](chapters/introduction.md)\n"
    )
    nav = ['nav:', '  - "Титульная страница": index.md']
    for i, h in enumerate(headings):
        heading = h.group(1).strip()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(source)
        body, sub = convert_divs(source[h.start():end])
        for key, value in sub.items():
            counts[key] = counts.get(key, 0) + value
        filename = "chapters/" + slug(i+1, heading) + ".md"
        if filename in items:
            raise ValueError(f"Duplicate filename: {filename}")
        items[filename] = body
        nav.append(f"  - {json.dumps(heading, ensure_ascii=False)}: {filename}")
    count_tables = lambda s: len(re.findall(r"^\|[^\n]+\|\s*\n\|\s*:?-{3}", s, flags=re.M))
    before = count_tables(raw)
    after = sum(count_tables(content) for content in items.values())
    if before != after:
        raise ValueError(f"Missing tables: {before} -> {after}")
    report = {"chapters":len(headings), "pages":len(items), "tables":before,
              "blocks":counts, "sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
    if not check:
        CHAPTERS.mkdir(parents=True, exist_ok=True)
        for old in CHAPTERS.glob("*.md"):
            old.unlink()
        for path, content in items.items():
            output = ROOT / "docs" / path
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text("<!-- Generated; edit CoZ_книга.md instead -->\n" + content, encoding="utf-8")
        config = (ROOT / "mkdocs.base.yml").read_text(encoding="utf-8").rstrip()
        (ROOT / "mkdocs.yml").write_text(config + "\n" + "\n".join(nav) + "\n", encoding="utf-8")
        (ROOT / "build-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    build(args.check)
