"""Where a line ends in the text this package and `tools/` read: at `\\n`, and nowhere else.

`str.splitlines()` also breaks at `\\x0b`, `\\x0c`, `\\x1c`-`\\x1e`, `\\x85`,
U+2028 and U+2029 (https://docs.python.org/3/library/stdtypes.html#str.splitlines),
and none of the formats read here ends a line at any of them. Git ends its
records at a newline and prints those characters raw inside a subject or a ref
name; a JSON-lines transcript ends a record at a newline and JSON leaves U+2028
and U+2029 unescaped inside a string (RFC 8259 section 7 requires escaping only
U+0000-U+001F); and Python's tokenizer ends a physical line at a newline alone
(https://docs.python.org/3/reference/lexical_analysis.html#physical-lines).
So `splitlines()` read one record as two at four readers filed by four sessions
(`PL-139L`, `PL-PK4B`, `PL-K1D6`, `PL-LRBV`, under the head `PL-4YVK`), and
`tests/unit/test_line_splits.py` now refuses it in the trees those readers live in.

**The text must already be decoded the way Python decodes text.** `read_text`
and `subprocess.run(text=True)` both translate `\\r\\n` and a lone `\\r` into
`\\n` before anything here sees them, which is why one character is enough. A
reader decoding bytes itself translates first, as `vcs`'s blob batch does, or
reads a carriage return as part of a line.
"""

from __future__ import annotations


def split_lines(text: str) -> list[str]:
    """`text`'s lines, broken at `\\n` alone, with no terminator kept.

    The same list `str.splitlines()` returns for text holding no other break,
    a final newline included: `""` has no lines and `"a\\n"` has one. That
    keeps every caller converted from `splitlines()` reading the same lines it
    did on every file in the tree, which held none of those characters when
    this was written (measured 2026-10-05).
    """
    parts = text.split("\n")
    if parts[-1] == "":
        parts.pop()
    return parts
