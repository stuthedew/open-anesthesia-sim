#!/usr/bin/env python3
"""Refuse a tracked document file, such as a PDF, whose licence nobody recorded.

This repository is public, so every file it tracks is redistributed by each
clone and fork. `docs/references/README.md` § "Redistribution" therefore allows
a third party's full text here only where the file's own licence permits that.
Two publisher-copyright PDFs sat in the tree until 2026-09-06 under that rule
in prose alone (`PL-SHG5`). Since 2026-11-10 sessions can fetch from any host,
on the condition that nothing fetched from a third party is committed
(`PL-6VZF`). This check is the part of that condition that can be decided from
the tree (`PL-KQBM`).

**One rule, exact.** A tracked file whose name ends in one of
`FULL_TEXT_SUFFIXES`, in any letter case, fails unless the licensed-files list
in the references README names it. That list sits between the
`LICENSED_BEGIN` and `LICENSED_END` markers, one line per file: the path in
backticks, a colon, and the licence. The README is the one place the list is
written, so a file is allowed in the same edit that records why it may be
held. A line between the markers that does not have that shape fails the run
too, because a list this check cannot read is one it cannot vouch for.

**What it cannot decide stays with the rule in prose.** Text pasted from a
source, and a figure or screenshot of another party's page, have no extension
that tells them apart from this project's own files.

Standard library only and floor-parseable, like every tool under `tools/`.
It reads the tracked file list and one Markdown file, so it runs with bare
`python3`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from docket.lines import split_lines  # noqa: E402
from docket.vcs import tracked_files  # noqa: E402

from doc_check import REFERENCES  # noqa: E402

#: The extensions of formats that hold a whole document: a paper, a book or a
#: chapter. Compared in lower case.
FULL_TEXT_SUFFIXES = (
    ".azw",
    ".azw3",
    ".djv",
    ".djvu",
    ".doc",
    ".docx",
    ".epub",
    ".mobi",
    ".odt",
    ".pdf",
    ".ps",
    ".rtf",
    ".xps",
)

#: The markers around the licensed-files list in the references README.
LICENSED_BEGIN = "<!-- full-text-check: licensed files begin -->"
LICENSED_END = "<!-- full-text-check: licensed files end -->"

#: One line of that list: a path in backticks, a colon, then the licence.
LICENSED_LINE_RE = re.compile(r"^- `(?P<path>[^`]+)`: (?P<licence>\S.*)$")


def licensed_files(root: Path) -> tuple[set[str], list[str]]:
    """Read the licensed-files list, and return its paths and any problems in it.

    A missing README, a missing marker or a line of the wrong shape is a
    problem, because the check cannot then say which files are allowed.
    """
    readme = root / REFERENCES
    try:
        lines = split_lines(readme.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        return set(), [
            f"{REFERENCES}: cannot be read ({error}), so no file is known to be licensed"
        ]
    stripped = [line.strip() for line in lines]
    if stripped.count(LICENSED_BEGIN) != 1 or stripped.count(LICENSED_END) != 1:
        return set(), [
            f"{REFERENCES}: needs exactly one {LICENSED_BEGIN!r} and one {LICENSED_END!r} "
            'line in § "Redistribution", around the list of licensed files'
        ]
    begin, end = stripped.index(LICENSED_BEGIN), stripped.index(LICENSED_END)
    if end < begin:
        return set(), [f"{REFERENCES}: the licensed-files list ends before it begins"]
    paths: set[str] = set()
    problems: list[str] = []
    for number, line in enumerate(stripped[begin + 1 : end], start=begin + 2):
        if not line:
            continue
        match = LICENSED_LINE_RE.match(line)
        if match is None:
            problems.append(
                f"{REFERENCES}:{number}: write each licensed file as "
                "- `path/to/file.pdf`: the licence"
            )
            continue
        paths.add(match.group("path"))
    return paths, problems


def problems(root: Path) -> list[str]:
    """Return one line for each tracked full text no licence covers, or for an unreadable list."""
    allowed, found = licensed_files(root)
    if found:
        return found
    for path in tracked_files(root):
        if path.lower().endswith(FULL_TEXT_SUFFIXES) and path not in allowed:
            found.append(
                f"{path}: a tracked document file with no recorded licence. If it is a "
                "third party's text, remove it with `git rm --cached` and keep it in the "
                'private corpus (§ "Where owner-supplied full texts live now"). If its '
                "licence permits redistribution, record that in "
                f"{REFERENCES} and add the file to its licensed-files list"
            )
    return found


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=split_lines(__doc__)[0])
    parser.parse_args(argv)
    found = problems(root)
    for line in found:
        print(line)
    print(f"full texts: {len(found)} errors")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
