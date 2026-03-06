#!/usr/bin/env python3
"""Shared utilities for md-to-json converters."""

from __future__ import annotations

import json
from typing import List


def language_from_label(label: str) -> str:
    mapping = {
        "plain text": "text",
        "text": "text",
        "bash": "bash",
        "shell": "bash",
        "python": "python",
        "json": "json",
        "xml": "xml",
        "yaml": "yaml",
        "yml": "yaml",
        "sql": "sql",
    }
    return mapping.get(label.strip().lower(), "text")


def infer_code_language(label: str, code_lines: List[str]) -> str:
    lang = language_from_label(label)
    if lang != "text":
        return lang

    non_empty = [line for line in code_lines if line.strip()]
    if not non_empty:
        return "text"

    joined = "\n".join(non_empty)
    if non_empty[0].startswith("{") or non_empty[0].startswith("["):
        return "json"
    if any('":' in line or line.strip().endswith("{") for line in non_empty) and "{" in joined:
        return "json"

    cmd_prefixes = (
        "#",
        "npm ",
        "pip ",
        "python ",
        "python3 ",
        "node ",
        "claude ",
        "echo ",
        "vim ",
        "export ",
        "git ",
        "cd ",
        "npx ",
    )
    if sum(1 for line in non_empty if line.startswith(cmd_prefixes)) >= 1:
        return "bash"
    if any("http://" in line or "https://" in line for line in non_empty):
        return "text"
    return "text"


def format_json_code_lines(code_lines: List[str]) -> List[str]:
    raw = "\n".join(code_lines).strip()
    if not raw:
        return code_lines
    try:
        obj = json.loads(raw)
    except Exception:
        return code_lines
    return json.dumps(obj, ensure_ascii=False, indent=2).splitlines()


def format_embedded_json_fragments(code_lines: List[str]) -> List[str]:
    result: List[str] = []
    i = 0
    n = len(code_lines)

    while i < n:
        line = code_lines[i]
        stripped = line.strip()

        if stripped not in ("{", "["):
            result.append(line)
            i += 1
            continue

        frag: List[str] = []
        j = i
        depth = 0
        started = False

        while j < n:
            cur = code_lines[j]
            frag.append(cur.strip())
            for ch in cur:
                if ch in "{[":
                    depth += 1
                    started = True
                elif ch in "}]":
                    depth -= 1
            if started and depth == 0:
                break
            j += 1

        if not started or depth != 0:
            result.append(line)
            i += 1
            continue

        raw = "\n".join(frag).strip()
        try:
            obj = json.loads(raw)
        except Exception:
            result.append(line)
            i += 1
            continue

        result.extend(json.dumps(obj, ensure_ascii=False, indent=2).splitlines())
        i = j + 1

    return result
