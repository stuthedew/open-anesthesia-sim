"""doc_check's inline Markdown reads as markdown-it-py reads it (`PL-R417`).

`tools/doc_check.py` reads three things inside a statement by hand, because the
tools run on the standard library alone: its code spans, its links and images,
and the line ending a phrase reader crosses where a sentence wraps
(`doc_check.SOFT_BREAK`). Each of `PL-R417`'s inline members was one of those
meeting a rule of CommonMark 0.31.2 § 6 one capture at a time - an escaped
backtick opening a span, a `]` inside a code span closing link text, a link
wrapped onto a line opening with `2026.` - and each was found by an audit after
it had merged. This holds all three to markdown-it-py, set as
`subprojects/docket/tests/test_markdown_reference.py` sets it to hold
`docket.markdown`'s blocks, so a form the reference reads another way fails on
the pull request that first writes it, rather than at the next audit. It is the
parsing review's inline differential (C1), ratified 2026-10-10.

It reads every example in the CommonMark 0.31.2 and GitHub Flavored Markdown
0.29 specifications, vendored unmodified under `tests/unit/markdown-specs/`, and
every tracked Markdown file. An example is the Markdown half of one of a
specification's `example` blocks, each `→` read as the tab it stands for; the
two GFM examples marked `disabled`, which cmark-gfm's own runner skips, are
left out. Both readers are handed the text with its tabs expanded to
four-column stops, as the block test hands markdown-it-py, and a source
`docket.markdown` reads with an unclosed block re-read as written is passed
over: that is the block reader's declared departure, and the block test covers
it.

The two must agree on which lines each paragraph, heading and table row
holds, and then on what is in each:

- each code span, by its content with every run of whitespace read as one
  space. A line ending inside a span is a space to both, but markdown-it-py
  keeps the indent of the line it carries on to, which CommonMark 0.31.2 § 4.8
  strips. In a table row a `\\|` is read as `|`, as GitHub Flavored Markdown
  0.29 § 4.10 reads it before any inline;
- each link and image, by the destination a renderer follows, normalized as
  markdown-it-py normalizes an `href`;
- each line ending inside a paragraph or heading, by where `SOFT_BREAK`,
  matched from the end of the line's text, leaves the next line: where
  markdown-it-py's content line begins.

The specifications' licence, CC-BY-SA 4.0, is recorded in `docs/apparatus.md`
§ "Third-party text (`tests/unit/markdown-specs/`)".
"""

from __future__ import annotations

import bisect
import hashlib
import re
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

import doc_check
import pytest
from docket import markdown
from docket.lines import record_text, split_lines

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "subprojects" / "docket" / "tests"))

from test_markdown_reference import REFERENCE

ROOT = Path(__file__).resolve().parents[2]
SPECIFICATIONS = Path(__file__).resolve().parent / "markdown-specs"
#: Each vendored specification, by its name here: where it was published, at a
#: release tag, and the SHA-256 of what was fetched from there on 2026-10-10.
PUBLISHED = {
    "commonmark-0.31.2.txt": (
        "https://raw.githubusercontent.com/commonmark/commonmark-spec/0.31.2/spec.txt",
        "257c41ad946f7a1414a499aca402a1aa8fdac3678532266611348c1cf54f4b80",
    ),
    "gfm-0.29.0.gfm.13.txt": (
        "https://raw.githubusercontent.com/github/cmark-gfm/0.29.0.gfm.13/test/spec.txt",
        "7d8e5814befec287ac116786d81ff14e0adc9b13295b4494649e995408fd871c",
    ),
}
#: The fence around a specification's example: its opening line carries
#: `example` and the example's extension, if any.
EXAMPLE_FENCE = "`" * 32
SOFT_BREAK = re.compile(doc_check.SOFT_BREAK)

#: The lines of a paragraph, heading or table row, as markdown-it-py maps the
#: inline token reading it: first, and one past its last.
Key = tuple[int, int]


@dataclass
class Reading:
    """What one reader finds inside each paragraph, heading and table row of a source."""

    spans: dict[Key, list[str]] = field(default_factory=dict)
    links: dict[Key, list[str]] = field(default_factory=dict)

    def add(self, key: Key) -> None:
        """Record a statement, so one holding nothing still compares."""
        self.spans.setdefault(key, [])
        self.links.setdefault(key, [])


def _spaced(content: str) -> str:
    """A code span's content with each whitespace run one space, as both read it."""
    return " ".join(content.split())


def theirs(text: str) -> tuple[Reading, dict[Key, str]]:
    """markdown-it-py's reading of `text`, and each paragraph's and heading's content."""
    reading = Reading()
    contents: dict[Key, str] = {}
    container = ""
    for token in REFERENCE.parse(text):
        if token.nesting == 1:
            container = token.type
        if token.type != "inline":
            continue
        assert token.map is not None
        key = (token.map[0], token.map[1])
        reading.add(key)
        for child in token.children or ():
            if child.type == "code_inline":
                reading.spans[key].append(_spaced(child.content))
            elif child.type == "link_open" and child.markup != "autolink":
                reading.links[key].append(str(child.attrs["href"]))
            elif child.type == "image":
                reading.links[key].append(str(child.attrs["src"]))
        if container in ("paragraph_open", "heading_open"):
            contents[key] = token.content
    return reading, contents


def ours(text: str) -> Reading:
    """`doc_check`'s reading of `text`, keyed as markdown-it-py keys its own."""
    lines = split_lines(text)
    keys: dict[int, Key] = {}
    rows: set[int] = set()
    for block in markdown.read(lines).blocks:
        if block.kind == markdown.PARAGRAPH:
            keys.update(dict.fromkeys(range(block.start, block.end), (block.start, block.end)))
        elif block.kind == markdown.HEADING:
            # A setext heading's underline is no part of its text.
            end = block.end - 1 if block.end - block.start > 1 else block.end
            keys.update(dict.fromkeys(range(block.start, end), (block.start, end)))
        elif block.kind == markdown.TABLE:
            rows.update(
                index for index in range(block.start, block.end) if index != block.start + 1
            )
    keys.update({row: (row, row + 1) for row in rows})
    reading = Reading()
    for key in keys.values():
        reading.add(key)
    starts = _line_starts(text)
    for span in doc_check._code_spans(text):
        line = bisect.bisect_right(starts, span.start()) - 1
        if line in keys:
            content = span["content"].replace("\\|", "|") if line in rows else span["content"]
            reading.spans[keys[line]].append(_spaced(content))
    for link in doc_check._links(text):
        line = bisect.bisect_right(starts, link.start) - 1
        if line in keys:
            reading.links[keys[line]].append(REFERENCE.normalizeLink(link.target))
    return reading


def _line_starts(text: str) -> list[int]:
    """Each line's offset into `text`."""
    starts = [0]
    for line in split_lines(text, keepends=True):
        starts.append(starts[-1] + len(line))
    return starts


def _soft_break_misses(text: str, contents: dict[Key, str]) -> Iterator[str]:
    """Each line `SOFT_BREAK` leaves anywhere but where markdown-it-py's content line begins."""
    lines = split_lines(text)
    starts = _line_starts(text)
    for (first, end), content in contents.items():
        expected = content.split("\n")
        if len(expected) != end - first:
            yield f"lines {first + 1}-{end}: markdown-it-py reads {len(expected)} lines of text"
            continue
        for index in range(first + 1, end):
            found = SOFT_BREAK.match(text, starts[index - 1] + len(lines[index - 1].rstrip(" \t")))
            landed = "" if found is None else text[found.end() : starts[index] + len(lines[index])]
            if landed.strip() != expected[index - first].strip():
                yield f"line {index + 1}: lands on {landed!r}, not {expected[index - first]!r}"


def _differences(text: str) -> list[str]:
    """Where the two readings of `text` disagree; empty where they agree or it is passed over."""
    lines = split_lines(text)
    parsed = markdown._parse(tuple(lines), len(lines), frozenset())[0]
    if [_shape(block) for block in parsed] != [
        _shape(block) for block in markdown.read(lines).blocks
    ]:
        return []
    expected, contents = theirs(text)
    found = ours(text)
    if set(found.spans) != set(expected.spans):
        only_ours = sorted(set(found.spans) - set(expected.spans))
        only_theirs = sorted(set(expected.spans) - set(found.spans))
        return [f"statements: docket {only_ours}, markdown-it-py {only_theirs}"]
    differences = [
        f"{what} in lines {key[0] + 1}-{key[1]}: docket {mine}, markdown-it-py {reference}"
        for what, mine_by_key, reference_by_key in (
            ("spans", found.spans, expected.spans),
            ("links", found.links, expected.links),
        )
        for key in sorted(reference_by_key)
        if (mine := mine_by_key[key]) != (reference := reference_by_key[key])
    ]
    differences.extend(_soft_break_misses(text, contents))
    return differences


def _shape(block: markdown.Block) -> tuple[str, int, int, int, int]:
    """A block as the block test compares one."""
    return (block.kind, block.start, block.end, block.depth, block.level)


def _expanded(text: str) -> str:
    """`text` with its tabs expanded to four-column stops, as both readers are handed it."""
    return "".join(line.expandtabs(4) + "\n" for line in split_lines(text))


def _examples(path: Path) -> Iterator[tuple[str, str]]:
    """Each example's Markdown in a specification, named by its file and number."""
    lines = path.read_text(encoding="utf-8").split("\n")
    number = 0
    index = 0
    while index < len(lines):
        opening = lines[index].split()
        index += 1
        if opening[:2] != [EXAMPLE_FENCE, "example"]:
            continue
        number += 1
        end = lines.index(".", index)
        body = lines[index:end]
        index = lines.index(EXAMPLE_FENCE, end) + 1
        if "disabled" not in opening[2:]:
            yield f"{path.name} example {number}", "".join(f"{line}\n" for line in body)


def test_the_vendored_specifications_are_the_published_ones() -> None:
    """Each specification is byte for byte what its tag published, line endings aside."""
    assert sorted(path.name for path in SPECIFICATIONS.iterdir()) == sorted(PUBLISHED)
    for name, (url, digest) in PUBLISHED.items():
        text = (SPECIFICATIONS / name).read_text(encoding="utf-8")
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == digest, f"{name} is not {url}"


def test_every_specification_example_reads_as_markdown_it_py_reads_it() -> None:
    examples = [
        example for name in sorted(PUBLISHED) for example in _examples(SPECIFICATIONS / name)
    ]
    assert len(examples) == 1322, "the examples were not all found, so not all were compared"

    differing = []
    for name, markdown_text in examples:
        text = _expanded(markdown_text.replace("→", "\t"))
        differing.extend(f"{name}: {difference}" for difference in _differences(text))
    assert not differing, "\n".join(differing)


def test_every_tracked_document_reads_as_markdown_it_py_reads_it() -> None:
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md"], cwd=ROOT, capture_output=True, check=True
    )
    names = [name for name in record_text(listed.stdout).split("\0") if name]
    assert names, "git ls-files listed no Markdown file, so nothing was compared"

    differing = []
    for name in names:
        text = _expanded((ROOT / name).read_text(encoding="utf-8"))
        differing.extend(f"{name}: {difference}" for difference in _differences(text))
    assert not differing, "\n".join(differing)


@pytest.mark.parametrize(
    ("text", "spans", "links"),
    [
        # An escaped backtick opens no span, so the one after it has nothing to close.
        ("\\`not code`\n", [], []),
        # A `]` inside a code span closes no link text.
        ("[a `]` b](x.md)\n", ["]"], ["x.md"]),
        # Raw HTML and an autolink are read whole, backticks and all.
        ('<a href="`">`code`\n', ["code"], []),
        # A link inside link text: the inner one is the link.
        ("[a [b](y.md)](x.md)\n", [], ["y.md"]),
        # A table row splits at an unescaped pipe before any span is read.
        ("| a |\n| - |\n| `x | y` |\n", [], []),
    ],
)
def test_the_comparison_reads_each_rule_it_names(
    text: str, spans: list[str], links: list[str]
) -> None:
    """The comparison's own reading, on forms whose answer CommonMark 0.31.2 § 6 states."""
    found = ours(text)
    assert [span for row in found.spans.values() for span in row] == spans
    assert [link for row in found.links.values() for link in row] == links
    assert _differences(text) == []
