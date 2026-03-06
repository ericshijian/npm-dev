#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import posixpath
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

OUTPUT_ZH_JSON_NAME = "page.zh.json"
JSON_FIELDS = [
    "arena_no",
    "title",
    "champion",
    "verification_status",
    "highlights",
    "industry",
    "category",
    "speed",
    "quality",
    "security",
    "cost",
    "challenger",
]

# Source worksheet columns: B~M (A is ignored)
XLSX_COLS = {
    "arena_no": 1,
    "title": 2,
    "champion": 3,
    "verification_status": 4,
    "highlights": 5,
    "industry": 6,
    "category": 7,
    "speed": 8,
    "quality": 9,
    "security": 10,
    "cost": 11,
    "challenger": 12,
}


def get_relationship_id(sheet: ET.Element) -> str | None:
    for key, value in sheet.attrib.items():
        if key == "r:id" or key.endswith("}id"):
            return value
    return None


def col_letters_to_index(ref: str) -> int:
    match = re.match(r"([A-Za-z]+)", ref)
    if not match:
        return 0
    letters = match.group(1).upper()
    index = 0
    for ch in letters:
        index = index * 26 + (ord(ch) - ord("A") + 1)
    return max(index - 1, 0)


def load_xml(zipf: zipfile.ZipFile, name: str) -> ET.Element:
    with zipf.open(name) as f:
        return ET.parse(f).getroot()


def parse_shared_strings(zipf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zipf.namelist():
        return []

    root = load_xml(zipf, "xl/sharedStrings.xml")
    items: list[str] = []
    for si in root.findall("{*}si"):
        text_parts = [t.text or "" for t in si.findall(".//{*}t")]
        items.append("".join(text_parts))
    return items


def parse_sheet_paths(zipf: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook = load_xml(zipf, "xl/workbook.xml")
    rels = load_xml(zipf, "xl/_rels/workbook.xml.rels")

    rel_map: dict[str, str] = {}
    for rel in rels.findall("{*}Relationship"):
        rel_id = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if rel_id and target:
            full_path = posixpath.normpath(posixpath.join("xl", target))
            rel_map[rel_id] = full_path

    results: list[tuple[str, str]] = []
    for sheet in workbook.findall("{*}sheets/{*}sheet"):
        name = sheet.attrib.get("name", "Sheet")
        rel_id = get_relationship_id(sheet)
        if not rel_id:
            continue
        path = rel_map.get(rel_id)
        if path and path in zipf.namelist():
            results.append((name, path))

    return results


def read_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")

    if cell_type == "inlineStr":
        parts = [t.text or "" for t in cell.findall(".//{*}t")]
        return "".join(parts)

    v = cell.find("{*}v")
    if v is None or v.text is None:
        return ""

    raw = v.text
    if cell_type == "s":
        try:
            return shared_strings[int(raw)]
        except (ValueError, IndexError):
            return raw
    if cell_type == "b":
        return "TRUE" if raw == "1" else "FALSE"
    return raw


def parse_sheet_rows(zipf: zipfile.ZipFile, sheet_path: str, shared_strings: list[str]) -> list[list[str]]:
    root = load_xml(zipf, sheet_path)

    row_maps: list[dict[int, str]] = []
    max_col = 0

    for row in root.findall("{*}sheetData/{*}row"):
        row_map: dict[int, str] = {}
        for cell in row.findall("{*}c"):
            ref = cell.attrib.get("r", "")
            col_idx = col_letters_to_index(ref)
            row_map[col_idx] = read_cell_value(cell, shared_strings)
            if col_idx + 1 > max_col:
                max_col = col_idx + 1
        row_maps.append(row_map)

    if max_col == 0:
        return []

    rows: list[list[str]] = []
    for row_map in row_maps:
        values = [""] * max_col
        for idx, val in row_map.items():
            if 0 <= idx < max_col:
                values[idx] = val
        rows.append(values)

    return rows


def clean_value(value: str) -> str:
    text = value.strip()
    if text.endswith(".0"):
        number_text = text[:-2]
        if number_text.isdigit():
            return number_text
    return text


def normalize_arena_no(text: str) -> str:
    value = clean_value(text)
    if value.isdigit():
        return str(int(value))
    try:
        f = float(value)
        if math.isfinite(f) and f.is_integer():
            return str(int(f))
    except ValueError:
        pass
    return value


def build_zh_rows(xlsx_path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(xlsx_path, "r") as zipf:
        shared_strings = parse_shared_strings(zipf)
        sheets = parse_sheet_paths(zipf)
        if not sheets:
            raise ValueError("No worksheets found in workbook.")

        _, sheet_path = sheets[0]
        rows = parse_sheet_rows(zipf, sheet_path, shared_strings)

    result: list[dict[str, str]] = []
    for row in rows:
        arena_no = normalize_arena_no(row[XLSX_COLS["arena_no"]] if len(row) > XLSX_COLS["arena_no"] else "")
        title = clean_value(row[XLSX_COLS["title"]] if len(row) > XLSX_COLS["title"] else "")

        if not arena_no or not arena_no.isdigit():
            continue
        if not title or "敬请期待" in title:
            continue

        item: dict[str, str] = {}
        for key in JSON_FIELDS:
            idx = XLSX_COLS[key]
            item[key] = clean_value(row[idx] if len(row) > idx else "")
        item["arena_no"] = arena_no
        result.append(item)

    return result


def to_json(xlsx_path: Path) -> Path:
    if not xlsx_path.exists():
        raise FileNotFoundError(f"File not found: {xlsx_path}")

    output_path = xlsx_path.parent / OUTPUT_ZH_JSON_NAME
    zh_rows = build_zh_rows(xlsx_path)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(zh_rows, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return output_path


def main() -> None:
    default_file = Path(__file__).resolve().parent / "List of Arenas.xlsx"

    parser = argparse.ArgumentParser(
        description="Generate 'page.zh.json' from List of Arenas.xlsx."
    )
    parser.add_argument(
        "xlsx",
        nargs="?",
        default=str(default_file),
        help="Path to the .xlsx file (default: Content/Arena/List of Arenas.xlsx)",
    )
    args = parser.parse_args()

    xlsx_path = Path(args.xlsx).expanduser().resolve()
    output = to_json(xlsx_path)

    print(f"Input: {xlsx_path}")
    print(f"Generated: {output}")


if __name__ == "__main__":
    main()
