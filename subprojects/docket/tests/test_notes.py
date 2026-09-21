"""The threads parser: what splits a thread, and which ids each one names.

Every id below is spellable by `store.ID_ALPHABET`, which excludes vowels. An
invented id like `PL-8888` matches nothing, so a test written with one asserts
that the parser found no thread for an id it could never have parsed - which
passes, and proves nothing.
"""

from __future__ import annotations

from pathlib import Path

from docket.notes import concerning, read

NOTES = """# Working notes

Preamble mentioning PL-9ZZ9, which belongs to no thread.

## Open thread: the chart - PL-B1B1, PL-C2C2

Body citing PL-D3D3 in passing, and PL-B1B1 again.

### A subsection, not a thread - PL-K4K4

Still inside the chart thread.

## Settled: something else (2026-09-01)

Nothing here names an id.

## Open thread: PL-D3D3 in a heading this time

Body citing PL-B1B1.
"""


def _notes(tmp_path: Path, text: str = NOTES) -> Path:
    path = tmp_path / "NOTES.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_only_a_level_two_heading_starts_a_thread(tmp_path: Path) -> None:
    """`#` is the file's title and `###` is a subsection of a thread.

    The `###` heading below names `PL-K4K4`, which must be read as the chart
    thread's body rather than as a fourth thread of its own.
    """
    threads = read(_notes(tmp_path))

    assert [thread.title for thread in threads] == [
        "Open thread: the chart - PL-B1B1, PL-C2C2",
        "Settled: something else (2026-09-01)",
        "Open thread: PL-D3D3 in a heading this time",
    ]
    assert "PL-K4K4" in threads[0].mentions


def test_a_heading_id_is_about_and_a_body_id_is_a_mention(tmp_path: Path) -> None:
    """The distinction the output prints, and the reason bodies are read at all."""
    chart, _, third = read(_notes(tmp_path))

    assert chart.about == ("PL-B1B1", "PL-C2C2")
    assert chart.mentions == ("PL-D3D3", "PL-K4K4")
    assert third.about == ("PL-D3D3",)
    assert third.mentions == ("PL-B1B1",)


def test_an_id_in_both_the_heading_and_the_body_is_about_only(tmp_path: Path) -> None:
    """Otherwise one thread would be reported twice for the same id, and the
    weaker reading would be the one printed second."""
    chart = read(_notes(tmp_path))[0]

    assert "PL-B1B1" in chart.about
    assert "PL-B1B1" not in chart.mentions


def test_text_before_the_first_thread_belongs_to_no_thread(tmp_path: Path) -> None:
    """A preamble explains the file; it is not a thread anyone should be sent to."""
    assert concerning(read(_notes(tmp_path)), "PL-9ZZ9") == ()


def test_threads_the_id_is_about_are_ordered_first(tmp_path: Path) -> None:
    """A reader with one jump in them should spend it on the right thread."""
    ordered = concerning(read(_notes(tmp_path)), "PL-D3D3")

    assert [thread.line for thread in ordered] == [17, 5]


def test_a_thread_carries_the_line_its_heading_is_on(tmp_path: Path) -> None:
    """The pointer is a `file:line`, so the number has to be the heading's own."""
    assert read(_notes(tmp_path))[0].line == 5


def test_a_missing_file_is_no_threads_rather_than_an_error(tmp_path: Path) -> None:
    """`docket show` must not fail on a sound item because a notes file moved.

    The path is a project setting, the file may be deleted, and a truncated
    checkout may not carry it. In all three the honest answer is that no
    thread was found.
    """
    assert read(tmp_path / "absent.md") == ()


def test_a_file_with_no_level_two_headings_is_no_threads(tmp_path: Path) -> None:
    assert read(_notes(tmp_path, "# Title\n\nProse citing PL-B1B1.\n")) == ()
