"""`docket.lines.split_lines`: where a line ends in the text docket and `tools/` read."""

from __future__ import annotations

import pytest

from docket.lines import split_lines


def test_a_line_ends_at_a_newline_and_at_nothing_else_splitlines_breaks_at() -> None:
    held = "a\x0bb\x0cc\x1cd\x1de\x1ef\x85g h i"

    assert split_lines(f"{held}\nj\n") == [held, "j"]


@pytest.mark.parametrize("text", ["", "\n", "a", "a\n", "a\n\n", "\na", "a\nb"])
def test_on_text_holding_only_newlines_it_reads_what_splitlines_read(text: str) -> None:
    """Every caller was converted from `splitlines()` on that promise."""
    assert split_lines(text) == text.splitlines()
