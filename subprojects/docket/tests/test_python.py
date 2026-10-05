"""Where a Python statement ends: the one reading `verify` and doc_check share.

The integrity checks and doc_check's definition readers each hold the reading
to a case of their own; these hold what makes it one reading under every
interpreter that may run it (`PL-TC2D`).
"""

from __future__ import annotations

import tokenize
from collections.abc import Callable, Iterator

import pytest

from docket.python import UNTOKENIZABLE, read_logical_lines, refusal


def test_an_error_token_is_a_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    """3.11 hands back as an error token what 3.12 raises on, so it is refused.

    Read past, the token would leave a file split into statements one way by
    the bare `python3` docket runs on and another by the project's own. No
    source yields an error token under every interpreter, so the tokenizer is
    made to hand one back here, as 3.11's does.
    """
    real = tokenize.generate_tokens

    def handing_back_an_error(readline: Callable[[], str]) -> Iterator[tokenize.TokenInfo]:
        for token in real(readline):
            marked = token.string == "marked"
            yield token._replace(type=tokenize.ERRORTOKEN) if marked else token

    monkeypatch.setattr(tokenize, "generate_tokens", handing_back_an_error)

    with pytest.raises(UNTOKENIZABLE) as refused:
        read_logical_lines("ok = 1\nx = marked + 1\n")

    assert refusal(refused.value) == "an error token at 'marked + 1', line 2"


def test_a_formatted_string_is_one_piece_cut_as_written() -> None:
    """3.12 hands a formatted string over in parts and 3.11 as one token; both read it whole.

    Its text is the source as written, so a fold keyed on a statement's pieces
    says the same of it under either interpreter, and its code is blank.
    """
    source = 'value = f"{name!r:>{width}} {{kept}}" + "plain"\n'

    [line] = read_logical_lines(source)

    assert [piece.text for piece in line.pieces] == [
        "value",
        "=",
        'f"{name!r:>{width}} {{kept}}"',
        "+",
        '"plain"',
    ]
    assert line.code == 'value = "" + ""'
