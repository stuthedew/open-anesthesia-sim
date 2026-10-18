"""`docket.markdown` reads every tracked Markdown file as markdown-it-py reads it (`PL-0C2S`).

The reader is written by hand because docket and the tools run on the standard
library alone. The tests can use what they cannot, so markdown-it-py, a dev
dependency, is the reference its block reading is held to: each leaf block's
kind, its span of lines, how many containers hold it and a heading's level,
over every tracked Markdown file and over the fixtures below, which hold forms
no tracked file need. Before this, the two were compared once, on 2026-10-04,
and `PL-B83V`'s closing `pre` tag was found by a sweep two days later. Its one
inline reading, `emphasis`, is held to markdown-it-py's pairing over every
example the vendored specifications hold (`PL-47NJ`).

The reference is set to the reader's three departures, as its docstring names
them:

- A block nothing closes is compared as CommonMark reads it, run to the end of
  the document, by comparing the reading `read` starts from before it re-reads
  that block as written. Wherever nothing is left open, that reading is the one
  `read` returns.
- Tabs are expanded to four-column stops before markdown-it-py reads a line.
- markdown-it-py's link reference definition rule is off.

It is also set to cmark-gfm's reading in the one place markdown-it-py departs
from it that a tracked file holds, which `_gfm_table` names. It departs on a
lazy table header row too, which no tracked file holds, so that form is pinned
to cmark-gfm's reading by a test of its own rather than compared (`PL-TJ1S`).
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest
from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock, table
from markdown_it.rules_inline import StateInline, backtick, emphasis

from docket import markdown
from docket.lines import record_text, split_lines
from docket.release import code_spans

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


@pytest.mark.reads_item_store
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


def test_a_lazy_header_row_over_a_delimiter_row_inside_a_container() -> None:
    """A lazy line is a table's header row where the delimiter row under it is in the container.

    cmark-gfm, which GitHub renders with, reads each form below as a paragraph
    and then a table inside the list item or the block quote (cmarkgfm
    2025.10.22, measured 2026-10-12), and so does `docket.markdown`, which read
    one paragraph over all four lines (`PL-TJ1S`). markdown-it-py 4.2.0 parts
    from cmark-gfm on both, so they are pinned here rather than compared: it
    reads the list form's table outside the list, and the block-quote form as
    one paragraph.
    """
    paragraph_then_table = [(markdown.PARAGRAPH, 0, 1, 1, 0), (markdown.TABLE, 1, 4, 1, 0)]

    assert ours(("- x", "a | b", "  --|--", "  c | d")) == paragraph_then_table
    assert ours(("> x", "a | b", "> --|--", "> c | d")) == paragraph_then_table


#: The vendored specifications, which `tests/unit/test_inline_reference.py`
#: holds to what their tags published.
SPECIFICATIONS = ROOT / "tests" / "unit" / "markdown-specs"

#: A span of emphasis as (where its opening delimiters start, one past its
#: closing ones, whether it is strong), and a literal as its two offsets.
Span = tuple[int, int, bool]
Literal = tuple[int, int]


class _EmphasisReference:
    """markdown-it-py, set as `REFERENCE` is, noting where each code span and emphasis stands.

    Its tokens carry no offsets, so the rules reading a code span and an
    emphasis delimiter are wrapped to note where each stood in the text the
    inline parser read, and a rule run once emphasis is paired reads each span
    back from them. A strong span's tokens are its inner delimiters: the outer
    two are the ones `emphasis.postProcess` empties.
    """

    def __init__(self, departing: tuple[str, ...] = ("link_open", "image", "html_inline")) -> None:
        #: The token types that keep a text out of the comparison. An
        #: autolink is a `link_open` whose markup is `autolink`, and is kept
        #: out only while `html_inline` is.
        self.departing = departing
        self.parser = MarkdownIt("commonmark").enable("table").disable("reference")
        self.parser.inline.ruler.at("backticks", self._backtick)
        self.parser.inline.ruler.at("emphasis", self._delimiter)
        self.parser.inline.ruler2.after("emphasis", "noted", self._noted)
        self.offsets: dict[tuple[int, int], int] = {}
        self.literals: dict[int, list[Literal]] = {}
        self.noted: list[tuple[str, list[Literal], set[Span]]] = []

    def read(self, text: str) -> list[tuple[str, list[Literal], set[Span]]]:
        """Each inline text of `text` holding none of the tokens `departing` names, as read."""
        self.noted = []
        self.parser.parse(text)
        return self.noted

    def _backtick(self, state: StateInline, silent: bool) -> bool:
        start, count = state.pos, len(state.tokens)
        found = backtick(state, silent)
        if found and not silent and len(state.tokens) > count:
            if state.tokens[-1].type == "code_inline":
                self.literals.setdefault(id(state), []).append((start, state.pos))
        return found

    def _delimiter(self, state: StateInline, silent: bool) -> bool:
        start, count = state.pos, len(state.delimiters)
        found = emphasis.tokenize(state, silent)
        if found and not silent:
            added = len(state.delimiters) - count
            for offset in range(added):
                self.offsets[(id(state), len(state.tokens) - added + offset)] = start + offset
        return found

    def _noted(self, state: StateInline) -> None:
        key = id(state)
        spans: set[Span] = set()
        opened: list[tuple[str, int]] = []
        departs = False
        for index, token in enumerate(state.tokens):
            departs = departs or (
                token.type in self.departing
                and not (token.markup == "autolink" and "html_inline" not in self.departing)
            )
            if token.type in ("em_open", "strong_open"):
                opened.append((token.type, self.offsets[(key, index)]))
            elif token.type in ("em_close", "strong_close"):
                kind, at = opened.pop()
                closed = self.offsets[(key, index)]
                strong = kind == "strong_open"
                spans.add((at - 1, closed + 2, True) if strong else (at, closed + 1, False))
        literals = self.literals.pop(key, [])
        self.offsets = {where: at for where, at in self.offsets.items() if where[0] != key}
        if not departs:
            self.noted.append((state.src, literals, spans))


def _examples(path: Path) -> Iterator[str]:
    """Each example's Markdown in a specification, each `→` read as the tab it stands for.

    An example's fence opens with `example`; the GFM examples marked
    `disabled`, which cmark-gfm's own runner skips, are left out, as the inline
    test leaves them.
    """
    lines = path.read_text(encoding="utf-8").split("\n")
    fence = "`" * 32
    for index, line in enumerate(lines):
        opening = line.split()
        if opening[:2] == [fence, "example"] and "disabled" not in opening[2:]:
            end = lines.index(".", index + 1)
            yield "".join(f"{text}\n" for text in lines[index + 1 : end]).replace("→", "\t")


def test_emphasis_pairs_every_specification_example_as_markdown_it_py_pairs_it() -> None:
    """`markdown.emphasis` against markdown-it-py, over every vendored example (`PL-47NJ`).

    CommonMark 0.31.2's and GitHub Flavored Markdown 0.29's examples, each
    inline text handed to both with markdown-it-py's own code spans as the
    literals, so what is compared is the pairing alone and not
    `release.code_spans`, which the next test compares. A text
    holding a link, an image, an autolink or raw HTML is passed over:
    `emphasis` reads none of them, the departure its docstring names. Measured
    over every tracked Markdown file as well on 2026-10-12, 2,613 files and the
    examples, the two agreed on all 54,404 texts compared.
    """
    reference = _EmphasisReference()
    examples = [
        example
        for name in ("commonmark-0.31.2.txt", "gfm-0.29.0.gfm.13.txt")
        for example in _examples(SPECIFICATIONS / name)
    ]
    assert len(examples) == 1322, "the examples were not all found, so not all were compared"

    differing = []
    for example in examples:
        for text, literals, expected in reference.read(example):
            found = {
                (span.start, span.end, span.strong) for span in markdown.emphasis(text, literals)
            }
            if found != expected:
                differing.append(
                    f"{text!r}: docket {sorted(found)}, markdown-it-py {sorted(expected)}"
                )
    assert not differing, "\n".join(differing)


def test_code_spans_finds_each_specification_example_span_markdown_it_py_finds() -> None:
    """`release.code_spans` against markdown-it-py, over every vendored example (`PL-T3GW`).

    The examples hold escaped backticks, runs no closer matches and runs of
    unequal length, each of which the pattern before this one read on its own
    terms. A text holding a link or an image is passed over: `code_spans`
    does not read a link's text and destination apart. An autolink or raw HTML
    opening first takes a backtick inside it, as `code_spans` reads (`PL-Q80R`).
    """
    reference = _EmphasisReference(departing=("link_open", "image"))
    differing = [
        f"{text!r}: docket {found}, markdown-it-py {literals}"
        for name in ("commonmark-0.31.2.txt", "gfm-0.29.0.gfm.13.txt")
        for example in _examples(SPECIFICATIONS / name)
        for text, literals, _ in reference.read(example)
        if (found := [span.span() for span in code_spans(text)]) != literals
    ]
    assert not differing, "\n".join(differing)
