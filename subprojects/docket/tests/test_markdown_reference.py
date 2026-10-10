"""`docket.markdown` reads every tracked Markdown file as markdown-it-py reads it (`PL-0C2S`).

The reader is written by hand because docket and the tools run on the standard
library alone. The tests can use what they cannot, so markdown-it-py, a dev
dependency, is the reference its block reading is held to: each leaf block's
kind, its span of lines, how many containers hold it and a heading's level,
over every tracked Markdown file and over the fixtures below, which hold forms
no tracked file need. Before this, the two were compared once, on 2026-10-04,
and `PL-B83V`'s closing `pre` tag was found by a sweep two days later.

The reference is set to the reader's three departures, as its docstring names
them:

- A block nothing closes is compared as CommonMark reads it, run to the end of
  the document, by comparing the reading `read` starts from before it re-reads
  that block as written. Wherever nothing is left open, that reading is the one
  `read` returns.
- Tabs are expanded to four-column stops before markdown-it-py reads a line.
- markdown-it-py's link reference definition rule is off.

It is also set to cmark-gfm's reading in the one place markdown-it-py departs
from it, which `_gfm_table` names.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest
from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock, table

from docket import markdown
from docket.lines import record_text, split_lines

ROOT = Path(__file__).resolve().parents[3]

#: markdown-it-py's block tokens, by the kind of leaf block each one is.
LEAVES = {
    "paragraph_open": markdown.PARAGRAPH,
    "heading_open": markdown.HEADING,
    "table_open": markdown.TABLE,
    "fence": markdown.FENCE,
    "code_block": markdown.CODE,
    "html_block": markdown.HTML,
    "hr": markdown.BREAK,
}
#: The tokens opening and closing a container: a block quote or a list item.
OPENS = frozenset({"blockquote_open", "list_item_open"})
CLOSES = frozenset({"blockquote_close", "list_item_close"})

#: A setext heading's `-` underline, past the indent markdown-it-py has read.
UNDERLINE = re.compile(r"-+[ \t]*")

#: Each leaf block as (kind, first line, one past its last, depth, heading level).
Reading = list[tuple[str, int, int, int, int]]


def _gfm_table(state: StateBlock, start: int, end: int, silent: bool) -> bool:
    """markdown-it-py's table rule, refused where its delimiter row is a setext underline.

    A bare run of hyphens is both, and cmark-gfm tries the underline first, so
    under a line holding a pipe it reads a setext heading where markdown-it-py
    reads a one-column table: cmark-gfm 0.29.0.gfm.13 renders `| a |` over
    `---` as an `h2` (measured 2026-10-10). `docket.markdown` follows cmark-gfm,
    and three item files' front matter holds the form, a `verify:` line with a
    pipe in it directly over the closing `---`.
    """
    below = start + 1
    if below < end:
        text = state.src[state.bMarks[below] + state.tShift[below] : state.eMarks[below]]
        if UNDERLINE.fullmatch(text):
            return False
    return table(state, start, end, silent)


REFERENCE = MarkdownIt("commonmark").enable("table").disable("reference")
REFERENCE.block.ruler.at("table", _gfm_table, {"alt": ["paragraph", "reference"]})


def theirs(lines: Sequence[str]) -> Reading:
    """Each leaf block markdown-it-py reads in `lines`, their tabs expanded first."""
    depth = 0
    found: Reading = []
    for token in REFERENCE.parse("".join(line.expandtabs(4) + "\n" for line in lines)):
        if token.type in OPENS:
            depth += 1
        elif token.type in CLOSES:
            depth -= 1
        elif token.type in LEAVES:
            assert token.map is not None
            level = int(token.tag[1:]) if token.type == "heading_open" else 0
            found.append((LEAVES[token.type], token.map[0], token.map[1], depth, level))
    return found


def ours(lines: Sequence[str]) -> Reading:
    """Each leaf block `docket.markdown` reads in `lines`, before it re-reads an unclosed one."""
    blocks = markdown._parse(tuple(lines), len(lines), frozenset())[0]
    return [(block.kind, block.start, block.end, block.depth, block.level) for block in blocks]


def _first_difference(found: Reading, expected: Reading) -> str:
    """The first block the two readings disagree on, as the failure names it."""
    at = next(
        (
            index
            for index, pair in enumerate(zip(found, expected, strict=False))
            if pair[0] != pair[1]
        ),
        min(len(found), len(expected)),
    )
    return f"docket {found[at : at + 1]}, markdown-it-py {expected[at : at + 1]}"


def test_every_tracked_document_reads_as_markdown_it_py_reads_it() -> None:
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md"], cwd=ROOT, capture_output=True, check=True
    )
    names = [name for name in record_text(listed.stdout).split("\0") if name]
    assert names, "git ls-files listed no Markdown file, so nothing was compared"

    differing = []
    for name in names:
        lines = split_lines((ROOT / name).read_text(encoding="utf-8"))
        found, expected = ours(lines), theirs(lines)
        if found != expected:
            differing.append(f"{name}: {_first_difference(found, expected)}")
    assert not differing, "\n".join(differing)


#: Forms no tracked document need hold, by what each one is.
FIXTURES = {
    # `PL-B83V`: a closing tag of § 4.6's kind 1 names is kind 7's, as markdown-it-py
    # and cmark-gfm 0.29.0.gfm.13 both read it, so the line under it is literal.
    "a line holding a closing pre tag": ("para", "", "</pre>", "*not emphasis*"),
    "a line holding a closing script tag": ("para", "", "</script>", "*not emphasis*"),
    "a line holding a closing style tag": ("para", "", "</style>", "*not emphasis*"),
    "a line holding a closing textarea tag": ("para", "", "</textarea>", "*not emphasis*"),
    # `_gfm_table`'s form, so the reference keeps cmark-gfm's reading of it.
    "a bare run of hyphens under a line holding a pipe": ("| a |", "---"),
}


@pytest.mark.parametrize("lines", FIXTURES.values(), ids=FIXTURES.keys())
def test_each_fixture_reads_as_markdown_it_py_reads_it(lines: tuple[str, ...]) -> None:
    assert ours(lines) == theirs(lines)
