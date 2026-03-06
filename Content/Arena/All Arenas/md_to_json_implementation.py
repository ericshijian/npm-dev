#!/usr/bin/env python3
"""Batch-generate implementation.md and implementation.raw.json from Original Documents/implementation-details.md.

Workflow:
1. Extract "1. **方案概览**" section from each arena's Original Documents/implementation-details.md.
2. Parse PHASE tables into implementation JSON structure.
3. Write implementation.md, implementation.raw.json (and optionally implementation.zh.json).
"""

from __future__ import annotations

import argparse
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Tuple

from md_to_json_common import (
    format_embedded_json_fragments,
    format_json_code_lines,
    infer_code_language,
    language_from_label,
)


SECTION_START_RE = re.compile(r"^\s*1\\\.\s*\*\*方案概览\*\*\s*$", re.MULTILINE)
NEXT_SECTION_RE = re.compile(r"^\s*2\\\.\s*\*\*.*?\*\*\s*$", re.MULTILINE)


def split_lines_keep_blanks(text: str) -> List[str]:
    lines = [line.strip() for line in text.replace("\r", "").split("\n")]
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    return lines


class SectionTablesParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.table_depth = 0
        self.tables: List[List[List[str]]] = []
        self.current_table: List[List[str]] | None = None
        self.in_outer_row = False
        self.in_outer_cell = False
        self.current_text_parts: List[str] = []
        self.current_cell_lines: List[str] = []
        self.current_row: List[str] = []
        self.in_nested_table = False
        self.nested_table_depth = 0
        self.nested_parts: List[str] = []

        self.link_href: str | None = None
        self.link_text_parts: List[str] = []
        self.link_href_nested: str | None = None
        self.link_text_parts_nested: List[str] = []

    def _append_text(self, text: str) -> None:
        if self.in_nested_table:
            self.nested_parts.append(text)
        else:
            self.current_text_parts.append(text)

    def flush_text(self) -> None:
        text = "".join(self.current_text_parts)
        lines = split_lines_keep_blanks(html.unescape(text))
        if lines:
            self.current_cell_lines.extend(lines)
        self.current_text_parts = []

    def flush_nested_as_code_block(self) -> None:
        lines = split_lines_keep_blanks(html.unescape("".join(self.nested_parts)))
        if not lines:
            self.nested_parts = []
            return
        lang = language_from_label(lines[0])
        code_lines = lines[1:] if len(lines) > 1 else []
        lang = infer_code_language(lines[0], code_lines) if lang == "text" else lang
        self.current_cell_lines.append(f"```{lang}")
        self.current_cell_lines.extend(code_lines)
        self.current_cell_lines.append("```")
        self.nested_parts = []

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        attrs_dict = {k.lower(): v for k, v in attrs}

        if self.in_nested_table:
            if tag == "table":
                self.nested_table_depth += 1
            elif tag == "br":
                self.nested_parts.append("\n")
            elif tag == "a":
                self.link_href_nested = attrs_dict.get("href") or ""
                self.link_text_parts_nested = []
            return

        if tag == "table":
            self.table_depth += 1
            if self.table_depth == 1:
                self.current_table = []
            elif self.table_depth >= 2 and self.in_outer_cell:
                self.flush_text()
                self.in_nested_table = True
                self.nested_table_depth = 1
                self.nested_parts = []
                return
        if self.table_depth == 1 and tag == "tr":
            self.in_outer_row = True
            self.current_row = []
        if self.table_depth == 1 and self.in_outer_row and tag in ("td", "th"):
            self.in_outer_cell = True
            self.current_text_parts = []
            self.current_cell_lines = []
        if self.in_outer_cell and tag == "br":
            self.current_text_parts.append("\n")
        if self.in_outer_cell and tag == "a":
            self.link_href = attrs_dict.get("href") or ""
            self.link_text_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if self.in_nested_table:
            if tag in ("p", "div", "li", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6"):
                self.nested_parts.append("\n")
            if tag == "a" and self.link_href_nested is not None:
                text = "".join(self.link_text_parts_nested).strip()
                href = (self.link_href_nested or "").strip()
                if text and href:
                    self.nested_parts.append(f"[{text}]({href})")
                elif text:
                    self.nested_parts.append(text)
                self.link_href_nested = None
                self.link_text_parts_nested = []
            if tag == "table":
                self.nested_table_depth -= 1
                if self.nested_table_depth == 0:
                    self.in_nested_table = False
                    self.flush_nested_as_code_block()
                    self.table_depth -= 1
            return

        if (
            self.in_outer_cell
            and tag in ("p", "div", "li", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6")
        ):
            self.current_text_parts.append("\n")
        if tag == "a" and self.link_href is not None:
            text = "".join(self.link_text_parts).strip()
            href = (self.link_href or "").strip()
            if text and href:
                self.current_text_parts.append(f"[{text}]({href})")
            elif text:
                self.current_text_parts.append(text)
            self.link_href = None
            self.link_text_parts = []
        if self.table_depth == 1 and self.in_outer_row and tag in ("td", "th") and self.in_outer_cell:
            self.flush_text()
            self.current_row.append("\n".join(self.current_cell_lines))
            self.in_outer_cell = False
            self.current_text_parts = []
            self.current_cell_lines = []
        if self.table_depth == 1 and tag == "tr" and self.in_outer_row:
            if self.current_row and self.current_table is not None:
                self.current_table.append(self.current_row)
            self.in_outer_row = False
            self.current_row = []
        if tag == "table":
            if self.table_depth == 1 and self.current_table is not None:
                self.tables.append(self.current_table)
                self.current_table = None
            self.table_depth -= 1

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        cleaned = data.replace("\r", "").strip("\n\t")
        if not cleaned:
            return

        if self.in_nested_table and self.link_href_nested is not None:
            self.link_text_parts_nested.append(cleaned)
            return
        if self.in_outer_cell and self.link_href is not None:
            self.link_text_parts.append(cleaned)
            return
        if self.in_nested_table:
            self.nested_parts.append(cleaned)
        elif self.in_outer_cell:
            self.current_text_parts.append(cleaned)


def extract_overview_section(md_text: str) -> str:
    start_match = SECTION_START_RE.search(md_text)
    if not start_match:
        return ""
    start_idx = start_match.end()
    tail = md_text[start_idx:]
    next_match = NEXT_SECTION_RE.search(tail)
    if next_match:
        tail = tail[: next_match.start()]
    return tail.strip()


def parse_phase_table(rows: List[List[str]]) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    if not rows:
        return fields

    header_cells = [c for c in rows[0] if c]
    phase_title = header_cells[0] if header_cells else ""
    if phase_title:
        fields["__phase_title__"] = phase_title

    for row in rows[1:]:
        cells = [c for c in row if c]
        if len(cells) >= 2:
            key = cells[0]
            value = cells[1]
            if key and value:
                fields[key] = value
    return fields


def parse_phase_number_and_title(raw_title: str, default_number: int) -> Tuple[int, str]:
    raw_title = raw_title.strip()
    if not raw_title:
        return default_number, f"PHASE {default_number}"

    m = re.search(r"phase\s*(\d+)\s*(.*)$", raw_title, flags=re.IGNORECASE)
    if not m:
        return default_number, raw_title

    number = int(m.group(1))
    rest = m.group(2).strip()
    title = f"PHASE {number}"
    if rest:
        title = f"{title} {rest}"
    return number, title


def _strip_existing_list_prefix(line: str) -> str:
    stripped = line.strip()
    stripped = re.sub(r"^-\s+", "", stripped)
    stripped = re.sub(r"^\d+\.\s+", "", stripped)
    return stripped.strip()


def _normalize_template_prefix(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("模板："):
        return stripped
    if stripped.startswith("[") and "模板" in stripped:
        return f"模板：{stripped}"
    return stripped


def apply_list_style(subsection_title: str, lines: List[str]) -> List[str]:
    unordered_titles = {"团队构成", "相关资源"}
    ordered_titles = {"实施内容", "结果产出"}
    if subsection_title not in unordered_titles and subsection_title not in ordered_titles:
        return lines

    out: List[str] = []
    in_code = False
    order_idx = 1

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            out.append(stripped)
            in_code = not in_code
            continue

        if in_code:
            out.append(line)
            continue

        if stripped == "":
            continue

        body = _strip_existing_list_prefix(stripped)
        if subsection_title == "相关资源":
            body = _normalize_template_prefix(body)

        if subsection_title in unordered_titles:
            out.append(f"- {body}")
        else:
            out.append(f"{order_idx}. {body}")
            order_idx += 1

    return out


def format_subsection_content(subsection_title: str, content_text: str) -> List[str]:
    normalized: List[str] = []
    raw_lines = split_lines_keep_blanks(content_text)

    for line in raw_lines:
        stripped = line.strip()
        if stripped in {"•", "·", "●", "▪"}:
            continue
        normalized.append(stripped)

    def clean_code_block(lines: List[str]) -> List[str]:
        if not lines:
            return lines
        result: List[str] = []
        for val in lines:
            if val != "":
                fixed = re.sub(r"(?<!\s)--header", " --header", val)
                result.append(fixed)
            else:
                result.append("")
        return result

    final_lines: List[str] = []
    i = 0
    while i < len(normalized):
        line = normalized[i]
        if line.startswith("```"):
            fence = line
            final_lines.append(fence)
            i += 1
            block: List[str] = []
            while i < len(normalized) and not normalized[i].startswith("```"):
                block.append(normalized[i])
                i += 1
            cleaned_block = clean_code_block(block)
            if fence.strip().lower() == "```json":
                cleaned_block = format_json_code_lines(cleaned_block)
            else:
                cleaned_block = format_embedded_json_fragments(cleaned_block)
            final_lines.extend(cleaned_block)
            if i < len(normalized):
                final_lines.append(normalized[i])
                i += 1
            continue
        final_lines.append(line)
        i += 1

    final_lines = [line for line in final_lines if line != ""]
    return apply_list_style(subsection_title, final_lines)


def parse_phases_from_implementation(md_text: str) -> List[Dict[str, object]]:
    section = extract_overview_section(md_text)
    if not section:
        return []

    parser = SectionTablesParser()
    parser.feed(section)
    phases: List[Dict[str, object]] = []

    subsection_order = ["团队构成", "实施内容", "相关资源", "结果产出", "实施周期"]

    for table_rows in parser.tables:
        fields = parse_phase_table(table_rows)
        raw_title = fields.get("__phase_title__", "")
        if "PHASE" not in raw_title.upper():
            continue

        number, title = parse_phase_number_and_title(raw_title, len(phases) + 1)
        subsections = []

        for subsection_title in subsection_order:
            content_text = fields.get(subsection_title, "")
            if not content_text:
                continue
            content = format_subsection_content(subsection_title, content_text)
            if content:
                subsections.append({"title": subsection_title, "content": content})

        if subsections:
            phases.append({"number": number, "title": title, "subsections": subsections})

    return phases


def phases_to_markdown(phases: List[Dict[str, object]]) -> str:
    lines: List[str] = ["# 实施方案（原始提取）", ""]
    for phase in phases:
        number = phase["number"]
        title = phase["title"]
        lines.append(f"## 阶段 {number}：{title}")
        lines.append("")
        for subsection in phase["subsections"]:
            lines.append(f"### {subsection['title']}")
            in_code = False
            for item in subsection["content"]:
                if item.startswith("```"):
                    in_code = not in_code
                    lines.append(item)
                elif in_code:
                    lines.append(item)
                else:
                    lines.append(item)
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def process_arena(arena_dir: Path, write_zh_json: bool) -> Tuple[bool, str]:
    impl_path = arena_dir / "Original Documents" / "implementation-details.md"
    if not impl_path.exists():
        return False, "missing Original Documents/implementation-details.md"

    md_text = impl_path.read_text(encoding="utf-8")
    phases = parse_phases_from_implementation(md_text)
    if not phases:
        return False, "no parsable 方案概览 PHASE tables found"

    impl_md_path = arena_dir / "implementation.md"
    raw_json_path = arena_dir / "implementation.raw.json"
    zh_json_path = arena_dir / "implementation.zh.json"

    impl_md = phases_to_markdown(phases)
    impl_md_path.write_text(impl_md, encoding="utf-8")

    payload = {"phases": phases}
    raw_json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if write_zh_json:
        zh_json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return True, f"{len(phases)} phases"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch-generate implementation.md and implementation.raw.json from Original Documents/implementation-details.md"
    )
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent),
        help="Arena root dir (default: script directory)",
    )
    parser.add_argument(
        "--write-zh-json",
        dest="write_zh_json",
        action="store_true",
        default=True,
        help="Write generated content to implementation.zh.json (default: true)",
    )
    parser.add_argument(
        "--no-write-zh-json",
        dest="write_zh_json",
        action="store_false",
        help="Do not write implementation.zh.json",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"[ERROR] Invalid root: {root}")
        return 1

    arena_dirs = sorted(
        [
            p
            for p in root.iterdir()
            if p.is_dir() and not p.name.startswith(".") and not p.name.startswith("__")
        ]
    )
    processed = 0
    skipped = 0

    for arena in arena_dirs:
        ok, message = process_arena(arena, write_zh_json=args.write_zh_json)
        if ok:
            processed += 1
            print(f"[OK] {arena.name}: {message}")
        else:
            skipped += 1
            print(f"[SKIP] {arena.name}: {message}")

    print(f"\nDone. processed={processed}, skipped={skipped}, total={len(arena_dirs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
