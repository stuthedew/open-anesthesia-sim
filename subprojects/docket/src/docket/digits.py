"""The one reading of a whole number written in ASCII digits, such as a count git or GitHub prints.

`str.isdigit()` is true for `'²'` and the other superscript digits, which
`int()` then refuses with `ValueError`, so a site that tested a count with
`isdigit()` and read it with `int()` crashed on one instead of treating it as
"not a number". `int()` on its own is no test either: it accepts other
scripts' decimal digits (`int('٣')` is 3), surrounding whitespace and `_`
between digits (https://docs.python.org/3/library/functions.html#int). Every
count read here comes from git, GitHub or a document, and each writes it in
ASCII digits, so anything else is not a count. About fifteen sites spelled
this reading by hand (`PL-PNGQ`), and `tools/fact_home_check.py` now refuses a
digit test outside this module.

It imports nothing, because `docket.shell` reads a redirection's descriptor
with it and every guard hook imports that module on each Bash call
(`PL-JNYL`). `tests/unit/test_shell_reader.py` holds a guard's import to the
modules it loads.
"""


def whole_number(text: str) -> int | None:
    """The whole number `text` spells in ASCII digits, or `None` where it spells none.

    Leading zeros are read (`07` is 7), as `git rev-list --count` never writes
    them and a document that does means the number. A pull request number,
    which GitHub never writes with a leading zero, has its own stricter reading
    in `model.pr_number`.
    """
    # Among ASCII characters, `isdigit` is true for 0-9 alone.
    return int(text) if text.isascii() and text.isdigit() else None
