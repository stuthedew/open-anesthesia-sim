#!/usr/bin/env python3
"""Refuse a character the client cannot draw from any string that reaches a reader.

`PL-8XPQ` is what this exists for. `→` (U+2192) has no glyph in the Flutter
client this interface renders in, and drew as a replacement box in the
control-change list on 2026-09-04. The character that failed was the arrow in
`5.60% -> 0.95%` - the direction of a setting change, which is the one thing
that line exists to state.

**Nothing in the repository could have caught it.** Every string assertion here
compares text the same font-less Python process produced, so the whole test
suite is blind to whether the client can draw what it is given. The failure is
silent, it survives a green suite, and the next non-ASCII character somebody
reaches for hits it again. `CLAUDE.md` treats presentation correctness as part
of the safety standard: a displayed value whose meaning arrives as a missing
character is a presentation failure whatever the number beside it says.

**The rule is default-deny, and that is the whole design.** Every non-ASCII
character in a string that can reach a reader must appear in `CONFIRMED` below.
ASCII is allowed unconditionally - the client draws it, and `%` among the
characters `PL-8XPQ` lists confirmed is ASCII and needs no entry. Adding a
character to `CONFIRMED` is a deliberate act that says *I rendered this and saw
it*, and the entry records the evidence.

**What this must never decide** is whether an unlisted character would in fact
render. That needs a real client, and a tool guessing at it would be worse than
none, because its output would look authoritative and would not be. An
unlisted character is refused, never approved; the remedy is always to render
it, look at it, and write down what was seen. `tools/contrast_check.py` and
`tools/agent_identity_check.py` draw the same line for the same reason.

**Per character, never per Unicode block.** A block is the tempting shortcut
and it defeats the point: Latin-1 Supplement admits `¤`, `þ` and `ð` alongside
the `·`, `±` and `×` this interface has actually shown, and no one has rendered
any of them. A block set would admit thousands of characters on the evidence of
three.

**Three trees, because a displayed string comes from all three.** `app/` is
where `PL-8XPQ` expected the check to look, and it is not the whole set.
`core/` raises the text the view prints verbatim - `app/run_view.py`'s
`_apply_setting` reports a refused `SimulationConfigurationError` as
`Setting refused — {error}`, and its `_halt_run` passes `str(error)` into the
halted-run banner - so a validation message is a displayed string with one more
step in front of it. `data/` holds `display_name`, which reaches the readouts
through `AgentParameters`, and is the one place an edit lands without touching
Python. Measured 2026-09-14: `core/` and `data/` hold no non-ASCII character
that this check would refuse today, so covering them costs nothing now and
closes the two routes by which one could arrive unseen.

**Documentation is excluded, and the test is structural rather than a guess.**
A string that is a bare expression statement is documentation - a module,
class, function or attribute docstring - and never reaches a reader. Nothing
else is excluded. That one rule is what keeps `§`, which appears only in
attribute docstrings in `app/controller.py` and in two `core/` modules, out of
a list that is supposed to mean *this was rendered and seen*. Comments never
enter, `ast` not carrying them.

**No rot guard, unlike `KNOWN_SHORTFALLS` in `tools/contrast_check.py`,** and
the asymmetry is deliberate. A listed shortfall that starts passing is an
error there because the entry is an excuse and the excuse has expired. An entry
here is not an excuse but a record of something somebody rendered and looked
at, and that stays true after the last use of the character is deleted.
Dropping the entry would throw the observation away and make the next person
repeat it.

Standard library only, like every tool here. It parses `src/` with `ast`, so it
is invoked through `uv run python` rather than at the bare-`python3` floor, for
the reason `tests/unit/test_tools_portability.py` states: `ast.parse`'s
`feature_version` only ever narrows the syntax accepted, and `src/` targets
3.14 (`PL-L17Q`, `PL-FZ6T`).
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import unicodedata
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The Python trees whose string literals can reach a reader. `app/` draws
#: them; `core/` raises the text the view prints verbatim.
PYTHON_TREES = (Path("src/anesthesia_sim/app"), Path("src/anesthesia_sim/core"))

#: The data tree, read as JSON rather than parsed: `display_name` reaches the
#: readouts, and an edit here touches no Python.
DATA_TREE = Path("src/anesthesia_sim/data")

#: Every non-ASCII character confirmed to render in the client, by code point,
#: with the evidence for each. A character is added here only after somebody has
#: run the interface and looked at it - never because it seemed likely to work.
#:
#: Keyed by code point rather than by the character itself, because `ruff
#: format` rewrites a `\uXXXX` escape into the literal character, and a literal
#: U+00A0 in this file would be invisible to a reader and indistinguishable
#: from the space beside it. A number is legible, greppable and stable.
CONFIRMED: dict[int, str] = {
    0x00A0: (
        "NO-BREAK SPACE - EMPTY_METRIC_QUALIFIER and EMPTY_METRIC_SECONDARY_VALUE in "
        "app/dashboard_frame.py, which drew a full line of the qualifier's size where a "
        "blank string collapsed to zero height in Flutter. Its rendered height is what "
        "kept every reading in the readout row on one baseline, so it shipped rendered "
        "and observed on the Flet build; PL-L9RD's rider re-confirms the six under Qt."
    ),
    0x00B1: "PLUS-MINUS SIGN - rendered in the wash-in tolerance readout (PL-8XPQ, 2026-09-04).",
    0x00B7: "MIDDLE DOT - rendered in the control-change list (PL-8XPQ, 2026-09-04).",
    0x00D7: "MULTIPLICATION SIGN - rendered in the MAC-multiple readout (PL-8XPQ, 2026-09-04).",
    0x2013: "EN DASH - rendered in the control-change list (PL-8XPQ, 2026-09-04).",
    0x2014: "EM DASH - rendered in the halted-run banner (PL-8XPQ, 2026-09-04).",
    0x2022: (
        "BULLET - MARK_ROW_BULLET in app/theme.py, where each mark row starts. Rendered "
        "through app/qt_widgets.styled_label under PySide6's offscreen platform in "
        "DejaVu Sans at 12 px, which holds the glyph itself, and looked at beside the "
        "confirmed middle dot it must not be mistaken for (PL-FPY2, 2026-09-22)."
    ),
}


def documentation(tree: ast.Module) -> set[int]:
    """Every string node that is a bare expression statement, by identity.

    That is the whole definition of documentation here - module, class,
    function and attribute docstrings are all of them, and nothing else is one.
    Structural rather than positional: an attribute docstring is not the first
    statement of any scope, which is why testing for position would let `§`
    through into a list that is supposed to record what was rendered.
    """
    found: set[int] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            found.add(id(node.value))
    return found


def python_strings(path: Path) -> Iterator[tuple[int, str]]:
    """Every string literal in a module that is not documentation, with its line.

    f-strings are reached through their `Constant` parts, so the literal text
    around an interpolation is checked and the interpolated value - which this
    tool cannot see - is not.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    excluded = documentation(tree)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in excluded
        ):
            yield node.lineno, node.value


def json_strings(payload: object) -> Iterator[str]:
    """Every string anywhere in a decoded JSON document, keys included."""
    if isinstance(payload, str):
        yield payload
    elif isinstance(payload, dict):
        for key, value in payload.items():
            yield key
            yield from json_strings(value)
    elif isinstance(payload, list):
        for value in payload:
            yield from json_strings(value)


def describe(character: str) -> str:
    """`U+XXXX NAME`, or `U+XXXX unnamed` for a character Unicode does not name."""
    return f"U+{ord(character):04X} {unicodedata.name(character, 'unnamed')}"


def offenders(text: str) -> list[str]:
    """Every character in `text` that is neither ASCII nor confirmed, in order, once each."""
    seen: dict[str, None] = {}
    for character in text:
        if ord(character) > 127 and ord(character) not in CONFIRMED:
            seen.setdefault(character, None)
    return list(seen)


def problems(root: Path) -> list[str]:
    """One message per string carrying a character nobody has confirmed renders."""
    found: list[str] = []

    for tree in PYTHON_TREES:
        base = root / tree
        if not base.is_dir():
            found.append(f"{tree.as_posix()}: does not exist, so this check measured nothing there")
            continue
        for path in sorted(base.rglob("*.py")):
            for lineno, text in python_strings(path):
                for character in offenders(text):
                    found.append(
                        f"{path.relative_to(root).as_posix()}:{lineno}: "
                        f"{describe(character)} is not confirmed to render"
                    )

    data = root / DATA_TREE
    if not data.is_dir():
        found.append(
            f"{DATA_TREE.as_posix()}: does not exist, so this check measured nothing there"
        )
    else:
        for path in sorted(data.rglob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for text in json_strings(payload):
                for character in offenders(text):
                    found.append(
                        f"{path.relative_to(root).as_posix()}: "
                        f"{describe(character)} is not confirmed to render"
                    )

    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Hold displayed strings to characters the client draws."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to check")
    args = parser.parse_args(argv)

    found = problems(args.root)
    if not found:
        print(
            f"glyph: every non-ASCII character in a displayed string is one of the "
            f"{len(CONFIRMED)} confirmed to render"
        )
        return 0

    print(
        f"glyph: {len(found)} string(s) carry a character nobody has confirmed "
        f"the client can draw.\n"
        + "".join(f"  {problem}\n" for problem in found)
        + "  `→` (U+2192) drew as a replacement box in the control-change list on "
        "2026-09-04, and no test could see it (PL-8XPQ). Run the interface, look at "
        "the character, and either replace it or add it to CONFIRMED in "
        "tools/glyph_check.py with what you saw. Do not add one you have not "
        "rendered: this check refuses an unlisted character and never approves one.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
