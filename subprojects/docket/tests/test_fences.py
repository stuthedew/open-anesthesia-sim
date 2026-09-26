"""Where a fenced block is: the one reading `checks`, `instructions` and doc_check share.

Each case below is a line two of the five spellings this module replaced read
differently (`PL-92MY`), so a reading drifting back toward any one of them fails
here before it fails in a brief.
"""

from __future__ import annotations

from docket.fences import Block, blocks, fenced_lines, without_fences


def test_a_closed_block_is_its_two_fence_lines_and_everything_between() -> None:
    text = "before\n```python\nx = 1\n```\nafter\n"

    assert blocks(text) == [Block(1, 3)]
    assert fenced_lines(text) == frozenset({1, 2, 3})


def test_a_triple_backtick_code_span_at_a_line_start_opens_no_block() -> None:
    """A backtick fence's info string holds no backtick, so this line is a code span.

    `PL-6SRZ`'s brief wraps one to a line's start. Read as an opener, it was
    closed by the next real fence and every line between was skipped, or,
    with that fence gone, nothing closed it and the rest of the brief was.
    """
    text = "The pattern\n``` `(test_\\w+)` ```, which cannot match.\n\n```\nbin/docket check\n```\n"

    assert blocks(text) == [Block(3, 5)]


def test_a_tilde_fence_is_closed_by_tildes_alone() -> None:
    text = "~~~\n```\n~~~\nafter\n"

    assert blocks(text) == [Block(0, 2)]


def test_a_tilde_opener_may_carry_a_backtick_in_its_info_string() -> None:
    """The info-string rule is the backtick fence's own; a tilde fence has no such limit."""
    assert blocks("~~~ `lang`\nx\n~~~\n") == [Block(0, 2)]


def test_a_closing_run_is_at_least_as_long_as_the_opening_one() -> None:
    """A shorter run inside is content, which is how a fence shows a fence."""
    text = "````markdown\n```\nshown\n```\n````\n"

    assert blocks(text) == [Block(0, 4)]


def test_a_closing_line_holds_nothing_but_its_run() -> None:
    assert blocks("```\n``` python\n```\n") == [Block(0, 2)]


def test_an_indented_fence_is_a_fence() -> None:
    """A fence under a list item is indented to sit inside it."""
    text = "- An item\n\n  ```text\n  shown\n  ```\n"

    assert blocks(text) == [Block(2, 4)]


def test_an_opener_nothing_closes_opens_no_block() -> None:
    """A fence nothing closes is not a fence: its lines are read as written.

    CommonMark runs the block to the end of the document, and every reader
    here skips a literal, so that reading would skip the rest of the file
    silently - the heading below is a section a writer can see.
    """
    text = "```\nan example never closed\n\n**Why it matters.** y\n"

    assert blocks(text) == []
    assert fenced_lines(text) == frozenset()
    assert without_fences(text) == text


def test_nothing_after_an_unclosed_opener_is_a_block() -> None:
    """Resuming after it would pair the fences below it the other way round.

    Here the four-backtick opener is closed by mistake with three. Started
    again from the line after the opener, the `closing` run would open a block
    of its own and the next fence would close it, so the prose between them -
    the one line a writer meant as prose - would be the part skipped.
    """
    text = "````\ncode\n```\n\nProse to read.\n\n```\nmore code\n```\n"

    assert blocks(text) == []


def test_without_fences_blanks_each_fenced_line_and_keeps_its_terminator() -> None:
    """A line's terminator is what `str.splitlines()` cut, and it survives the blanking.

    Blanked with the line, a form feed or a U+2028 would join two lines into
    one and move every line number below it.
    """
    text = "a\r\n```\fx\u2028```\nb"

    assert without_fences(text) == "a\r\n   \f \u2028   \nb"


def test_without_fences_keeps_every_offset_and_line_number() -> None:
    text = 'one\n  ```text\n  `docs/MODEL.md`, "A heading"\n  ```\ntwo `x`\n'
    blanked = without_fences(text)

    assert len(blanked) == len(text)
    assert blanked.count("\n") == text.count("\n")
    assert blanked.splitlines()[0] == "one"
    assert blanked.splitlines()[4] == "two `x`"
    assert blanked.splitlines()[1:4] == [" " * len(line) for line in text.splitlines()[1:4]]
