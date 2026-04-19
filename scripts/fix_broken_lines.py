#!/usr/bin/env python3
"""
Fixes PDF-copied notes in markdown files:
  1. Replaces bullet characters (•) with markdown list markers (-).
  2. Joins broken lines that were split due to PDF page/column width.
Only processes files with a .md extension or no extension (markdown notes).
"""

import os
import sys
import re

MARKDOWN_EXTENSIONS = {'', '.md', '.markdown', '.txt'}

SENTENCE_ENDINGS = re.compile(r'[.!?:]\s*$')
LIST_MARKER = re.compile(r'^\s*([-•*]|\d+\.)\s')
HEADING = re.compile(r'^\s*#+\s')
BOLD_HEADING = re.compile(r'^\s*\*\*')
SEPARATOR = re.compile(r'^\s*---\s*$')
BLANK = re.compile(r'^\s*$')


def is_continuation(line: str) -> bool:
    """Return True if the line looks like a continuation of the previous."""
    return not (
        BLANK.match(line)
        or HEADING.match(line)
        or BOLD_HEADING.match(line)
        or LIST_MARKER.match(line)
        or SEPARATOR.match(line)
    )


def fix_bullet_markers(text: str) -> str:
    """Replace • bullet characters with markdown - list markers."""
    # Step 1: replace "• " (bullet + space)
    text = text.replace('\u2022 ', '- ')
    # Step 2: replace bare "•" (bullet without space)
    text = text.replace('\u2022', '- ')
    return text


def fix_broken_lines(text: str) -> str:
    lines = text.splitlines()
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Keep joining while current line ends without sentence termination
        # and the next line is a continuation
        while (
            i + 1 < len(lines)
            and not SENTENCE_ENDINGS.search(line)
            and not BLANK.match(line)
            and not HEADING.match(line)
            and not SEPARATOR.match(line)
            and is_continuation(lines[i + 1])
        ):
            i += 1
            line = line.rstrip() + ' ' + lines[i].lstrip()
        result.append(line)
        i += 1
    return '\n'.join(result)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fix_broken_lines.py <file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    _, ext = os.path.splitext(filepath)
    if ext.lower() not in MARKDOWN_EXTENSIONS:
        print(f"Skipped (not a markdown file): {filepath}")
        sys.exit(0)

    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    fixed = fix_bullet_markers(original)
    fixed = fix_broken_lines(fixed)

    if fixed != original:
        # Preserve trailing newline if present
        if original.endswith('\n') and not fixed.endswith('\n'):
            fixed += '\n'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f"Fixed broken lines in: {filepath}")
    else:
        print(f"No broken lines found in: {filepath}")
