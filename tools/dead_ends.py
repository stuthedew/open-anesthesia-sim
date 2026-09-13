"""Emit `docs/dead-ends.md`'s entries into session context, and hold them to a budget.

Two subcommands, and the split between them is the whole design.

`emit` prints the entry lines and nothing else. `.claude/hooks/docket-digest.sh`
calls it at session start, and a `SessionStart` hook's output is resent on
every turn for the life of the session - so what `emit` prints is paid once per
turn, by every session, forever. The file's preamble is instructions for
somebody *adding* an entry; a session reading the entries never needs it, so it
is not emitted and not budgeted. That separation is the point: the file may
explain itself at whatever length is useful, and the always-loaded half stays
small.

`check` holds the emitted half to a budget, and `make check` runs it.

**Why a budget rather than a style note.** The cost of an unbounded
always-loaded store is measured, and it is large. Xu et al. (ACL 2026,
arXiv:2505.16067) compared memory-curation policies on an agent benchmark:
add-all reached 13.04% accuracy over 2,411 records where strict selective
addition reached 38.86% over 1,012 - a threefold difference from policy alone,
with the add-all curve flat or declining as records accumulated. Chroma's
*Context Rot* (2025-07, 18 models) found a focused ~300-token prompt beat the
full ~113,000-token prompt by 30-60 points on identical questions. Anthropic's
own always-loaded index is bounded at 200 lines or 25 KB with detail in topic
files deliberately not loaded at startup. A file in this position without a cap
does not stay small; it stays small until the first session with a good reason
to add eleven lines.

The numbers here are far under Anthropic's, and deliberately: this is one of
several things the digest emits, and that hook's own comment calls its few
lines the one cost it is careful about.

**The cap forces removal rather than saturating, and that is the intended
mechanism.** Appending deltas and never rewriting sounds like it fills up, but
the two operations the file allows are add-one and remove-one; only rewriting
the whole thing into a summary is the failure mode ACE measured, and its own
prescription is delta updates *plus periodic de-duplication*. An entry earns
its line only while a session could plausibly propose that approach again, so
one whose code or design question no longer exists comes out. Hitting the cap
means that pass is overdue - which is why this fails rather than warning, and
why raising the number is the one repair that is never right.

**What is checked is arithmetic, and only arithmetic.** Entry count, emitted
bytes, one line per entry, and that every `PL-` id an entry cites resolves to a
real item. Whether an approach *deserves* a line - whether a future session
would plausibly propose it again, which is the file's own admission test - is
judgment, and a tool guessing at it would be the "worse than no tool" case
`CLAUDE.md` names: its output would look authoritative and would not be. The
file states that test in prose for a reader; this refuses only what a reader
cannot see at a glance.

**Why a dangling id is an error rather than an advisory.** An entry's whole
retrieval path is `bin/docket show <id>`. An id resolving to nothing leaves a
claim with no reasoning behind it, in a file every session reads and no session
can check - strictly worse than the entry not being there. The tree answers the
question outright, so there is no reading under which a dangling id is
intended. Same argument `tools/rules_paths_check.py` makes for a `paths:` glob
pointing at nothing.

Standard library only, and parses at the floor
`tests/unit/test_tools_portability.py` holds this directory to.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEAD_ENDS = REPO / "docs" / "dead-ends.md"
ITEMS = REPO / "docs" / "items"

# Both budgets bind, and they fail in different directions: many short entries
# trip the count, one essay trips the bytes. Measured against the seeded file
# on 2026-09-13 - 12 entries, 2,447 emitted bytes - so each leaves room for
# roughly what is there again before anybody has to choose what to drop.
# Making that choice is the intended outcome of hitting either.
MAX_ENTRIES = 30
MAX_EMITTED_BYTES = 4000

ENTRY = re.compile(r"^- \*\*(?P<what>.+?)\*\* [-—] (?P<why>.+)$")
ITEM_ID = re.compile(r"\bPL-[A-Z0-9]{3,4}\b")

HEADER = (
    "Dead ends - approaches already tried here and refuted. "
    "`bin/docket show <id>` for the reasoning."
)


def entries(text: str) -> list[tuple[int, str]]:
    """Return `(line number, line)` for every bullet that is an entry.

    An entry is a top-level bullet opening with a bolded approach. Prose
    bullets in the preamble are not entries, are not emitted, and do not count
    against either budget.
    """
    return [
        (number, line)
        for number, line in enumerate(text.splitlines(), start=1)
        if ENTRY.match(line)
    ]


def emitted(text: str) -> str:
    lines = [line for _, line in entries(text)]
    if not lines:
        return ""
    return "\n".join([HEADER, *lines])


def known_ids() -> set[str]:
    ids = set()
    for path in ITEMS.glob("*.md"):
        parts = path.name.split("-")
        if len(parts) >= 2:
            ids.add(f"{parts[0]}-{parts[1]}")
    return ids


def check(text: str) -> list[str]:
    problems: list[str] = []
    found = entries(text)

    size = len(emitted(text).encode("utf-8"))
    if size > MAX_EMITTED_BYTES:
        problems.append(
            f"docs/dead-ends.md emits {size} bytes, over the {MAX_EMITTED_BYTES}-byte budget. "
            f"That text is resent on every turn of every session. Drop the entry a session "
            f"is least likely to propose again, or shorten one."
        )

    if len(found) > MAX_ENTRIES:
        problems.append(
            f"docs/dead-ends.md has {len(found)} entries, over the {MAX_ENTRIES} budget. "
            f"Drop one rather than raising the cap: the cap is the mechanism."
        )

    ids = known_ids()
    for number, line in found:
        for cited in ITEM_ID.findall(line):
            if cited not in ids:
                problems.append(
                    f"docs/dead-ends.md:{number}: cites {cited}, which is not an item. "
                    f"An entry's whole retrieval path is `bin/docket show {cited}`."
                )

    # A wrapped entry reads as an entry plus a stray prose line, and the stray
    # line is then outside everything above - unemitted, unbudgeted and citing
    # nothing. Cheap to catch, and invisible to a reader scanning for bullets.
    lines = text.splitlines()
    for number, _ in found:
        if number < len(lines):
            following = lines[number]
            if following.strip() and not following.lstrip().startswith(("-", "#", "*", "|")):
                problems.append(
                    f"docs/dead-ends.md:{number + 1}: continuation of the entry above. "
                    f"One line per entry - shorten it instead."
                )

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("emit", "check"))
    args = parser.parse_args(argv)

    if not DEAD_ENDS.exists():
        # `emit` stays silent, so a checkout without the file starts cleanly -
        # the same promise every other line of the digest hook makes.
        if args.command == "emit":
            return 0
        print("docs/dead-ends.md: missing", file=sys.stderr)
        return 1

    text = DEAD_ENDS.read_text(encoding="utf-8")

    if args.command == "emit":
        out = emitted(text)
        if out:
            print(out)
        return 0

    problems = check(text)
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
