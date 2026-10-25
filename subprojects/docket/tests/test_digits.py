"""`docket.digits.whole_number` reads a whole number in ASCII digits and refuses everything else.

`PL-PNGQ`: `'²'.isdigit()` is true and `int('²')` raises `ValueError`, so a
count tested with one and read with the other crashed. `int` alone accepts
other scripts' digits, whitespace and `_`, none of which git or GitHub writes.
"""

from __future__ import annotations

import pytest

from docket.digits import whole_number


@pytest.mark.parametrize(("text", "number"), [("0", 0), ("7", 7), ("07", 7), ("1759", 1759)])
def test_ascii_digits_read_as_their_number(text: str, number: int) -> None:
    assert whole_number(text) == number


@pytest.mark.parametrize(
    "text",
    [
        "",
        "²",  # superscript two: `isdigit` is true and `int` raises
        "1²",
        "٣",  # Arabic-Indic three: `int` reads it as 3
        " 5",
        "5\n",
        "1_000",
        "-1",
        "+1",
        "3.0",
    ],
)
def test_a_superscript_or_any_other_non_ascii_digit_string_is_refused(text: str) -> None:
    assert whole_number(text) is None
