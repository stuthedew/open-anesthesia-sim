"""Tests for `tools/doc_quote_check.py`, the weekly comparison of quoted Claude Code docs.

Every test reads pages from a fixture directory or a stub, so none needs the
network. What is pinned is what the script reports: a quotation its page no
longer contains, one its file no longer contains, and a page it could not read.
The real record is held to the tree as well, since an entry naming a file that
does not quote it fails the weekly job for a reason that is not the page's.
"""

from __future__ import annotations

from pathlib import Path

import doc_quote_check
import pytest
from doc_quote_check import QUOTE_RECORD, ROOT, Quote, check, load, main, normalize


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_normalize_ignores_wrapping_markup_comment_markers_and_case() -> None:
    wrapped = (
        '# "For most fetches, it then runs the prompt against the content in a\n'
        '# separate model call", and the [`raw page`](https://example.com) **is not** seen\n'
    )
    page = "For most fetches, it then runs the prompt against the content in a separate model call"
    assert normalize(page) in normalize(wrapped)
    assert "raw page is not seen" in normalize(wrapped)
    assert normalize("Don’t") == normalize("don't")


def test_normalize_keeps_a_hyphen_inside_a_line() -> None:
    assert normalize("knowledge-work - evaluations") == "knowledge-work - evaluations"


def test_a_quotation_on_its_page_and_in_its_file_passes(tmp_path: Path) -> None:
    _write(tmp_path / "docs/a.md", "It says the rule is\n`loaded unconditionally`.\n")
    quotes = [Quote("docs/a.md", "memory", "the rule is loaded unconditionally")]
    assert (
        check(quotes, tmp_path, lambda page: "## Rules\n\nThe rule is **loaded unconditionally**.")
        == []
    )


def test_a_quotation_its_page_no_longer_contains_is_reported(tmp_path: Path) -> None:
    _write(tmp_path / "docs/a.md", '"if two rules contradict each other"')
    quotes = [Quote("docs/a.md", "memory", "if two rules contradict each other")]
    [problem] = check(quotes, tmp_path, lambda page: "if two instructions contradict each other")
    assert "docs/a.md" in problem
    assert "https://code.claude.com/docs/en/memory.md no longer contains" in problem


def test_a_quotation_its_file_no_longer_contains_is_reported_before_the_page_is_read(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "docs/a.md", "The quotation was reworded here.")
    quotes = [Quote("docs/a.md", "memory", "the old quotation")]

    def unread(page: str) -> str:
        raise AssertionError("the page was read for a quotation its file no longer holds")

    [problem] = check(quotes, tmp_path, unread)
    assert "docs/a.md: no longer quotes 'the old quotation'" in problem


def test_a_missing_file_is_reported(tmp_path: Path) -> None:
    [problem] = check([Quote("docs/gone.md", "memory", "text")], tmp_path, lambda page: "text")
    assert problem.startswith("docs/gone.md: could not be read")


def test_an_unreadable_page_is_reported_for_each_quotation_and_read_once(tmp_path: Path) -> None:
    _write(tmp_path / "a.md", "first quote and second quote")
    quotes = [Quote("a.md", "hooks", "first quote"), Quote("a.md", "hooks", "second quote")]
    reads = []

    def offline(page: str) -> str:
        reads.append(page)
        raise OSError("no route to host")

    problems = check(quotes, tmp_path, offline)
    assert reads == ["hooks"]
    assert (
        problems[0]
        == "https://code.claude.com/docs/en/hooks.md: could not be read (no route to host)"
    )
    assert len(problems) == 3
    assert all("was not compared" in line for line in problems[1:])


def test_load_rejects_an_entry_with_an_empty_field(tmp_path: Path) -> None:
    record = _write(tmp_path / "quotes.toml", '[[quote]]\nfile = "a.md"\npage = ""\ntext = "x"\n')
    with pytest.raises(ValueError, match="entry 1 has no page"):
        load(record)


def test_main_reads_pages_from_a_directory_and_fails_on_a_problem(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(tmp_path / "root/docs/a.md", "quotes 'kept text' and 'dropped text'")
    record = _write(
        tmp_path / "quotes.toml",
        '[[quote]]\nfile = "docs/a.md"\npage = "memory"\ntext = "kept text"\n'
        '[[quote]]\nfile = "docs/a.md"\npage = "memory"\ntext = "dropped text"\n',
    )
    _write(tmp_path / "pages/memory.md", "Only the kept text is here.")
    argv = [
        "--pages",
        str(tmp_path / "pages"),
        "--record",
        str(record),
        "--root",
        str(tmp_path / "root"),
    ]
    assert main(argv) == 1
    out = capsys.readouterr().out.splitlines()
    assert "'dropped text'" in out[0]
    assert out[-1] == "doc quotes: 2 quotations from 1 pages, 1 problems"


def test_every_entry_in_the_real_record_is_quoted_by_its_file() -> None:
    quotes = load(QUOTE_RECORD)
    assert quotes
    on_every_page = lambda page: " ".join(normalize(quote.text) for quote in quotes)  # noqa: E731
    assert check(quotes, ROOT, on_every_page) == []


def test_the_fetch_url_is_the_pages_markdown(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = []

    class Response:
        def __enter__(self) -> Response:
            return self

        def __exit__(self, *exc: object) -> None:
            return None

        def read(self) -> bytes:
            return b"page text"

    def urlopen(request: object, timeout: float) -> Response:
        seen.append(request.full_url)  # type: ignore[attr-defined]
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    assert doc_quote_check.fetch("memory") == "page text"
    assert seen == ["https://code.claude.com/docs/en/memory.md"]
