#!/usr/bin/env python3
"""Batch-generate tech-configuration.md and tech-configuration.raw.json.

Workflow:
1. Extract "3. **技术步骤**" section from each arena's Original Documents/implementation-details.md.
2. Parse step tables and write tech-configuration.md in a stable markdown format.
3. Parse generated tech-configuration.md and write tech-configuration.raw.json.
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


SECTION_START_RE = re.compile(r"^\s*\d+\\\.\s*\*\*技术步骤\*\*\s*$", re.MULTILINE)
NEXT_SECTION_RE = re.compile(r"^\s*\d+\\\.\s*\*\*.*?\*\*\s*$", re.MULTILINE)


def normalize_label(text: str) -> str:
    return re.sub(r"\s+", "", text).strip("：:*- ").lower()


def split_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


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
        if self.in_nested_table:
            if tag == "table":
                self.nested_table_depth += 1
            if tag == "br":
                self.nested_parts.append("\n")
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

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.in_nested_table:
            if tag in ("p", "div", "li", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6"):
                self.nested_parts.append("\n")
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
        if self.in_nested_table:
            self.nested_parts.append(cleaned)
        elif self.in_outer_cell:
            self.current_text_parts.append(cleaned)


def extract_tech_steps_section(md_text: str) -> str:
    start_match = SECTION_START_RE.search(md_text)
    if not start_match:
        return ""
    start_idx = start_match.end()
    tail = md_text[start_idx:]
    next_match = NEXT_SECTION_RE.search(tail)
    if next_match:
        tail = tail[: next_match.start()]
    return tail.strip()


def parse_table_to_fields(rows: List[List[str]]) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    for row in rows:
        cells = [c for c in row if c]
        if len(cells) >= 4:
            pairs = [(cells[0], cells[1]), (cells[2], cells[3])]
        elif len(cells) >= 2:
            pairs = [(cells[0], cells[1])]
        else:
            pairs = []
        for key, value in pairs:
            if key and value:
                fields[key] = value
    return fields


def maybe_prefix_dash(line: str) -> str:
    if line.startswith("- ") or re.match(r"^\d+\.\s+", line):
        return line
    return f"- {line}"


FIELD_LABELS = [
    "角色名称",
    "技能要求",
    "角色数量",
    "输入名称",
    "输入介绍",
    "输入示例",
    "输出名称",
    "输出介绍",
    "资源链接",
]


def detect_field_label(line: str) -> str | None:
    stripped = line.strip()
    for label in FIELD_LABELS:
        if stripped.startswith(label):
            return label
    return None


def split_compound_field_line(line: str) -> List[str]:
    matches = list(
        re.finditer(
            r"(角色名称|技能要求|角色数量|输入名称|输入介绍|输入示例|输出名称|输出介绍|资源链接)\s*[：:]?",
            line,
        )
    )
    if len(matches) <= 1 or matches[0].start() != 0:
        return [line]
    points = [m.start() for m in matches] + [len(line)]
    out: List[str] = []
    for i in range(len(points) - 1):
        seg = line[points[i] : points[i + 1]].strip()
        if seg:
            out.append(seg)
    return out


def format_subsection_content(subsection_title: str, content_text: str) -> List[str]:
    raw_lines = split_lines_keep_blanks(content_text)
    expanded_lines: List[str] = []
    for line in raw_lines:
        expanded_lines.extend(split_compound_field_line(line))

    out: List[str] = []
    in_code = False
    skill_idx = 1
    after_skill_label = False
    after_resource_label = False
    resource_idx = 1

    for line in expanded_lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            out.append(stripped)
            in_code = not in_code
            after_resource_label = False
            continue

        if in_code:
            out.append(line)
            continue

        if stripped == "":
            continue
        if stripped in {"•", "·", "●", "▪"}:
            continue

        if subsection_title in ("参与人员", "本步输入", "本步产出"):
            label = detect_field_label(stripped)
            if label is not None:
                out.append(maybe_prefix_dash(stripped))
                after_skill_label = label == "技能要求"
                if label == "资源链接":
                    after_resource_label = True
                    resource_idx = 1
                else:
                    after_resource_label = False
                skill_idx = 1
                continue

            if subsection_title == "本步输入" and (
                stripped.startswith("将以下内容添加到")
                or stripped.startswith("创建 requirements.txt 文件")
                or stripped.startswith("创建相关服务 python 文件")
            ):
                out.append(maybe_prefix_dash(stripped))
                continue

            if after_skill_label and not stripped.startswith("角色数量："):
                out.append(f"{skill_idx}. {stripped}")
                skill_idx += 1
                continue

            if after_skill_label and stripped.startswith("角色数量："):
                out.append(maybe_prefix_dash(stripped))
                after_skill_label = False
                continue

            if after_resource_label and re.search(r"(GitHub|https?://|docs\.)", stripped):
                out.append(f"{resource_idx}. {stripped}")
                resource_idx += 1
                continue

        out.append(stripped)

    normalized: List[str] = out[:]

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

    return final_lines


def get_field(fields: Dict[str, str], labels: List[str]) -> str:
    if not fields:
        return ""
    normalized = {normalize_label(k): v for k, v in fields.items()}
    for label in labels:
        v = normalized.get(normalize_label(label))
        if v:
            return v
    return ""


def parse_steps_from_implementation(md_text: str) -> List[Dict[str, object]]:
    section = extract_tech_steps_section(md_text)
    if not section:
        return []

    steps: List[Dict[str, object]] = []
    parser = SectionTablesParser()
    parser.feed(section)
    for table_rows in parser.tables:
        fields = parse_table_to_fields(table_rows)
        number_raw = get_field(fields, ["步骤序号", "Step Number"])
        title = get_field(fields, ["步骤名称", "Step Name"]) or "未命名步骤"
        number_match = re.search(r"\d+", number_raw)
        number = int(number_match.group()) if number_match else len(steps) + 1

        subsection_specs: List[Tuple[str, List[str]]] = [
            ("步骤定义", ["步骤定义", "Step Definition"]),
            ("参与人员", ["参与人员", "Participants"]),
            ("本步输入", ["本步输入", "Step Input"]),
            ("本步产出", ["本步产出", "Step Output"]),
            ("预估时间", ["预估时间", "Estimated Time"]),
        ]
        subsections = []
        for output_title, candidates in subsection_specs:
            content_text = get_field(fields, candidates)
            if content_text:
                content = format_subsection_content(output_title, content_text)
                if content:
                    subsections.append({"title": output_title, "content": content})

        if subsections:
            steps.append({"number": number, "title": title, "subsections": subsections})

    return steps


def steps_to_markdown(steps: List[Dict[str, object]]) -> str:
    lines: List[str] = ["# 技术配置（原始提取）", ""]
    for step in steps:
        number = step["number"]
        title = step["title"]
        lines.append(f"## 步骤 {number}：{title}")
        lines.append("")
        for subsection in step["subsections"]:
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
    steps = parse_steps_from_implementation(md_text)
    if not steps:
        return False, "no parsable 技术步骤 tables found"

    tech_md_path = arena_dir / "tech-configuration.md"
    raw_json_path = arena_dir / "tech-configuration.raw.json"
    zh_json_path = arena_dir / "tech-configuration.zh.json"

    tech_md = steps_to_markdown(steps)
    tech_md_path.write_text(tech_md, encoding="utf-8")

    raw_json = {"steps": steps}
    raw_json_path.write_text(
        json.dumps(raw_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if write_zh_json:
        zh_json_path.write_text(
            json.dumps(raw_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return True, f"{len(steps)} steps"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch-generate tech-configuration.md and tech-configuration.raw.json"
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
        help="Write generated content to tech-configuration.zh.json (default: true)",
    )
    parser.add_argument(
        "--no-write-zh-json",
        dest="write_zh_json",
        action="store_false",
        help="Do not write tech-configuration.zh.json",
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
