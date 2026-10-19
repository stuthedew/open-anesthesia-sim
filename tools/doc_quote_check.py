#!/usr/bin/env python3
"""Report each recorded quotation of Claude Code's documentation that its page no longer contains.

Several rules here rest on a sentence of Claude Code's documentation, quoted
in a live file with a link to its page on code.claude.com. The pages change
over weeks. On 2026-10-19 `PL-124X` compared 16 quoted strings with their
pages and found 4 of them gone, one of which had been read from the page's own
markdown only 18 days before. A rule whose sentence has left the page still
reads as sourced, and nothing said so until a session happened to compare it
again (`PL-S7LT`).

`tools/doc_quotes.toml` is the record of those quotations. Each entry names
the file that quotes, the page it quotes, and the quoted text. This script
checks every entry in both directions:

- the text is still in the file, so a quotation edited without its entry is
  reported rather than left unchecked;
- the text is still on the page, read as markdown from
  https://code.claude.com/docs/en/PAGE.md, and fetched once per page.

Both comparisons ignore line wrapping, Markdown links and emphasis, backticks,
comment and quotation markers at the start of a line, curly quotation marks
and letter case. So a quotation wrapped inside a shell comment matches the
same sentence written on one line of the page.

**A report is a lead, not a verdict.** The script decides whether a string is
on a page, never whether the rule built on it still holds. When it reports a
quotation, a session reads the page and either corrects the quotation or
withdraws the claim, under an item of its own.

A page that cannot be read is reported too, and the run fails, because a
quotation that was not compared has not been shown to be current. The script
needs the network, so it is not part of `make check` or of `quality.yml`. The
`doc-quotes` job in `.github/workflows/drift.yml` runs it each week, and a
session can run it by hand before relying on a quotation. `--pages DIR` reads
`DIR/PAGE.md` instead of fetching, which is how the tests run it offline.

Standard library only, like every tool under `tools/`.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The record this script reads. Its header says how to add an entry.
QUOTE_RECORD = Path(__file__).resolve().with_name("doc_quotes.toml")

#: Where a page's markdown is served. The page name from the record follows it.
DOCS_URL = "https://code.claude.com/docs/en/"

#: Seconds to wait for one page before reporting it unreadable.
FETCH_TIMEOUT_S = 30

#: A comment, quotation or list marker at the start of a line, with one space after it.
_LINE_MARKER = re.compile(r"(?m)^[ \t]*(?:#+|>|//|[-*](?=\s))[ \t]?")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_SPACE = re.compile(r"\s+")
_CHARACTERS = str.maketrans({"`": None, "*": None, "‘": "'", "’": "'", "“": '"', "”": '"'})


@dataclass(frozen=True)
class Quote:
    """One quotation: the file that quotes it, the page it comes from, and its text."""

    file: str
    page: str
    text: str


def normalize(text: str) -> str:
    """Return `text` with its markup and wrapping removed, in lower case, for comparison."""
    text = _LINE_MARKER.sub("", text)
    text = _LINK.sub(r"\1", text)
    text = text.translate(_CHARACTERS)
    return _SPACE.sub(" ", text).strip().casefold()


def load(record: Path) -> list[Quote]:
    """Read the record's entries, and reject one that lacks a field or has an empty one."""
    entries = tomllib.loads(record.read_text(encoding="utf-8")).get("quote", [])
    quotes = []
    for number, entry in enumerate(entries, start=1):
        fields = {name: entry.get(name) for name in ("file", "page", "text")}
        empty = [
            name
            for name, value in fields.items()
            if not isinstance(value, str) or not value.strip()
        ]
        if empty:
            raise ValueError(f"{record.name}: entry {number} has no {', '.join(empty)}")
        quotes.append(Quote(**fields))
    return quotes


def fetch(page: str) -> str:
    """Return the markdown of one documentation page, read from the network."""
    request = urllib.request.Request(
        DOCS_URL + page + ".md", headers={"User-Agent": "doc_quote_check"}
    )
    with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_S) as response:
        body: bytes = response.read()
    return body.decode("utf-8")


def check(quotes: Sequence[Quote], root: Path, read_page: Callable[[str], str]) -> list[str]:
    """Return one line for each quotation that its file or its page no longer contains.

    `read_page` returns a page's markdown, or raises `OSError` when it cannot.
    Each page is read once, however many quotations it has.
    """
    pages: dict[str, str | None] = {}
    problems = []
    for quote in quotes:
        wanted = normalize(quote.text)
        try:
            in_file = wanted in normalize((root / quote.file).read_text(encoding="utf-8"))
        except OSError as error:
            problems.append(
                f"{quote.file}: could not be read ({error}), so {quote.text!r} was not checked"
            )
            continue
        if not in_file:
            problems.append(
                f"{quote.file}: no longer quotes {quote.text!r}; correct the entry in"
                f" {QUOTE_RECORD.name} or remove it"
            )
            continue
        if quote.page not in pages:
            try:
                pages[quote.page] = normalize(read_page(quote.page))
            except (OSError, UnicodeDecodeError) as error:
                pages[quote.page] = None
                problems.append(f"{DOCS_URL}{quote.page}.md: could not be read ({error})")
        page = pages[quote.page]
        if page is None:
            problems.append(
                f"{quote.file}: {quote.text!r} was not compared, because its page could not be read"
            )
        elif wanted not in page:
            problems.append(
                f"{quote.file}: quotes {quote.text!r}, which {DOCS_URL}{quote.page}.md no longer"
                " contains; read the page, then correct the quotation or withdraw its claim"
            )
    return problems


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pages", type=Path, help="read DIR/PAGE.md instead of fetching each page")
    parser.add_argument("--record", type=Path, default=QUOTE_RECORD, help=argparse.SUPPRESS)
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    arguments = parser.parse_args(argv)

    if arguments.pages is None:
        read_page = fetch
    else:
        directory: Path = arguments.pages

        def read_page(page: str) -> str:
            return (directory / f"{page}.md").read_text(encoding="utf-8")

    quotes = load(arguments.record)
    problems = check(quotes, arguments.root, read_page)
    for line in problems:
        print(line)
    pages = len({quote.page for quote in quotes})
    print(f"doc quotes: {len(quotes)} quotations from {pages} pages, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
