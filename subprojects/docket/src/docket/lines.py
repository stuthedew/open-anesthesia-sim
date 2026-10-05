"""Where a line ends in the text this package and `tools/` read: at `\\n`, and nowhere else.

`str.splitlines()` also breaks at `\\x0b`, `\\x0c`, `\\x1c`-`\\x1e`, `\\x85`,
U+2028 and U+2029 (https://docs.python.org/3/library/stdtypes.html#str.splitlines),
and none of the formats read here ends a line at any of them. Git ends its
records at a newline and prints those characters raw inside a subject or a ref
name; a JSON-lines transcript ends a record at a newline and JSON leaves U+2028
and U+2029 unescaped inside a string (RFC 8259 section 7 requires escaping only
U+0000-U+001F); and Python's tokenizer ends a physical line at a newline alone
(https://docs.python.org/3/reference/lexical_analysis.html#physical-lines).
The documents read here end one nowhere else either: CommonMark 0.31.2 section
2.1 ("Characters and lines") and YAML 1.2.2 section 5.4 end one at a line feed
or a carriage return alone, the second naming a form feed, U+0085, U+2028 and
U+2029 non-break characters, and GNU make 4.3 ran a recipe line holding a form
feed, a U+0085 and a U+2028 as one line (measured 2026-10-05, `PL-BBYJ`).
So `splitlines()` read one record as two at four readers filed by four sessions
(`PL-139L`, `PL-PK4B`, `PL-K1D6`, `PL-LRBV`, under the head `PL-4YVK`), and
`tests/unit/test_line_splits.py` now refuses it in the trees those readers live in.

**Text reaches here decoded one of two ways, by whose carriage return it is.**
File content - a file read with `read_text`, a blob, a patch whose `+` and `-`
lines are file lines - has `\\r\\n` and a lone `\\r` translated into `\\n`
first, as `read_text` and `subprocess.run(text=True)` both do, which is why one
character is enough: `file_text` does that for text a reader decoded itself.
Git's own records - hashes, subjects, bodies, trailers, ref names, `-z` path
listings - are decoded as written by `record_text`, with nothing translated,
because a raw `\\r` in one is part of the record git wrote. Text mode turned
it into a newline before any split saw it, so a subject holding one read as two
lines (`PL-0R4M`).
"""

from __future__ import annotations

import locale

#: The encoding text mode decodes with (`subprocess._text_encoding`: the
#: locale's, or UTF-8 in UTF-8 mode), so bytes decoded with it are the `str`
#: `subprocess.run(text=True)` returned, minus the newline translation.
ENCODING = locale.getpreferredencoding(False)


def split_lines(text: str, *, keepends: bool = False) -> list[str]:
    """`text`'s lines, broken at `\\n` alone, each without its `\\n` unless `keepends`.

    The same list `str.splitlines(keepends)` returns for text holding no other
    break, a final newline included: `""` has no lines and `"a\\n"` has one.
    That keeps every caller converted from `splitlines()` reading the same
    lines it did on every file in the tree, which held none of those
    characters when this was written (measured 2026-10-05). With `keepends`
    the lines join back into `text`, which is what a reader counting each
    line's offset needs.
    """
    parts = text.split("\n")
    last = parts.pop()  # what follows the final newline: "" where `text` ends with one
    lines = [part + "\n" for part in parts] if keepends else parts
    if last:
        lines.append(last)
    return lines


def record_text(raw: bytes) -> str:
    """One of git's own records, decoded as text mode decoded it, with no line end translated.

    For what git writes rather than what a file holds: hashes, subjects,
    bodies, trailers, ref names, `-z` path listings and config values. A raw
    `\\r` in a subject, a body or a `-z` path is part of the record, and the
    translation text mode applies turned it into a line end before any split
    saw it (`PL-0R4M`). Strict, so bytes that are not text in `ENCODING` still
    raise `UnicodeDecodeError` where text mode raised it.
    """
    return raw.decode(ENCODING)


def file_text(text: str) -> str:
    """File content with `\\r\\n` and a lone `\\r` read as `\\n`, as `read_text` reads a file.

    For a blob, or a patch whose `+` and `-` lines are file lines: the same
    translation `read_text` and `subprocess.run(text=True)` apply, so a blob
    or a patch git printed reads line for line as the file it came from
    (`PL-0R4M`).
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")
