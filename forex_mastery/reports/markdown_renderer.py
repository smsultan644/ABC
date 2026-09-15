"""
A small, dependency-free Markdown parser for the teaching documents.

WHY WRITE ONE INSTEAD OF USING A LIBRARY
----------------------------------------
The handbooks are the product. Authoring them as plain Markdown means:

* they are readable in VS Code, on GitHub, and in any editor;
* they diff cleanly, so a correction to a lesson is a one-line change;
* they can be converted to PDF/DOCX for printing **without** locking the
  content into a binary format.

Only the subset of Markdown actually used in ``docs/`` is supported, and each
construct is handled explicitly rather than heuristically. Unsupported syntax is
passed through as literal text instead of being silently dropped - in teaching
material, silent data loss is worse than ugly output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

__all__ = ["Block", "parse_markdown", "plain_text_length"]


@dataclass
class Block:
    """One parsed markdown block."""

    kind: str                      # h1..h4, p, ul, ol, code, table, hr, quote
    text: str = ""
    items: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    header: list[str] = field(default_factory=list)
    level: int = 0


_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_BULLET = re.compile(r"^\s*[-*+]\s+(.*)$")
_ORDERED = re.compile(r"^\s*(\d+)[.)]\s+(.*)$")
_RULE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
_QUOTE = re.compile(r"^\s*>\s?(.*)$")
_TABLE_SEP = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]*$")


def parse_markdown(text: str) -> list[Block]:
    """Parse markdown into a flat list of :class:`Block` objects."""
    blocks: list[Block] = []
    lines = text.replace("\r\n", "\n").split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]

        # ---- fenced code ------------------------------------------------
        if line.strip().startswith("```"):
            index += 1
            buffer: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                buffer.append(lines[index])
                index += 1
            index += 1  # closing fence
            blocks.append(Block(kind="code", text="\n".join(buffer)))
            continue

        # ---- horizontal rule -------------------------------------------
        if _RULE.match(line):
            blocks.append(Block(kind="hr"))
            index += 1
            continue

        # ---- heading ----------------------------------------------------
        heading = _HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            blocks.append(Block(kind=f"h{min(level, 4)}", text=heading.group(2).strip(), level=level))
            index += 1
            continue

        # ---- table -------------------------------------------------------
        if "|" in line and index + 1 < len(lines) and _TABLE_SEP.match(lines[index + 1]):
            header = _split_row(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(_split_row(lines[index]))
                index += 1
            blocks.append(Block(kind="table", header=header, rows=rows))
            continue

        # ---- block quote --------------------------------------------------
        if _QUOTE.match(line):
            buffer = []
            while index < len(lines) and _QUOTE.match(lines[index]):
                buffer.append(_QUOTE.match(lines[index]).group(1))
                index += 1
            blocks.append(Block(kind="quote", text=" ".join(buffer).strip()))
            continue

        # ---- lists ---------------------------------------------------------
        if _BULLET.match(line) or _ORDERED.match(line):
            ordered = bool(_ORDERED.match(line))
            items: list[str] = []
            while index < len(lines):
                bullet = _BULLET.match(lines[index])
                number = _ORDERED.match(lines[index])
                if bullet:
                    items.append(bullet.group(1).strip())
                elif number:
                    items.append(number.group(2).strip())
                elif lines[index].startswith(("  ", "\t")) and items:
                    # continuation line of the previous item
                    items[-1] += " " + lines[index].strip()
                else:
                    break
                index += 1
            blocks.append(Block(kind="ol" if ordered else "ul", items=items))
            continue

        # ---- blank / paragraph ------------------------------------------
        if not line.strip():
            index += 1
            continue
        buffer = [line.strip()]
        index += 1
        while index < len(lines) and lines[index].strip() and not _starts_block(lines[index], lines, index):
            buffer.append(lines[index].strip())
            index += 1
        blocks.append(Block(kind="p", text=" ".join(buffer)))
    return blocks


def _starts_block(line: str, lines: list[str], index: int) -> bool:
    if _HEADING.match(line) or _BULLET.match(line) or _ORDERED.match(line):
        return True
    if _RULE.match(line) or _QUOTE.match(line) or line.strip().startswith("```"):
        return True
    if "|" in line and index + 1 < len(lines) and _TABLE_SEP.match(lines[index + 1]):
        return True
    return False


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def plain_text_length(blocks: Iterable[Block]) -> int:
    """Approximate rendered word count, used for progress/reporting."""
    total = 0
    for block in blocks:
        total += len(block.text.split())
        total += sum(len(item.split()) for item in block.items)
        total += sum(len(cell.split()) for row in block.rows for cell in row)
    return total
