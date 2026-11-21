"""Print `docs/dead-ends.md`'s entries for the session-start digest.

`emit` is the one subcommand. It prints the entry lines and nothing else.
`.claude/hooks/docket-digest.sh` calls it at session start, and a
`SessionStart` hook's output is resent on every turn for the life of the
session, so every session pays for what `emit` prints on every turn. The
file's preamble is instructions for somebody adding an entry. A session
reading the entries never needs it, so it is not printed and not budgeted.
The file can therefore explain itself at any length while the always-loaded
half stays small.

**The budget is 30 entries and 4,000 bytes of printed text, and a test
enforces it.** `tests/unit/test_dead_ends.py` fails when the shipped file
reaches `NUDGE_FRACTION` of either number, so a session that adds an entry
makes room for it in the same commit. A larger budget is the owner's decision,
put to them with its cost, and only once every entry has to stay resident
(`PL-5J1S`). The section under `RETIRED` is not printed and not budgeted.

**Nothing checks an entry's format.** A `check` subcommand ran in `make check`
and CI from `PL-NB35` until 2026-11-21. It refused an entry citing an id that
no item holds, an entry wrapped onto a second line, a bullet that opens like
an entry and is not in an entry's shape, and an entry removed with no record
of where it went. `PL-LY24` counted no refusal from it in CI, and `PL-8F5B`
removed it. `emit` still prints a line naming an entry that a line carries on
from the margin (`PL-DQ9C`). A bullet that opens like an entry and that
`ENTRY` cannot read is not printed, and nothing reports it. `docs/dead-ends.md`
states the rules for editing the list, and the grooming pass in
`.claude/skills/docket/modes/triage.md` re-tests each entry.

**Why the entries are resident at all, which is the load-bearing choice here.**
Not because records like this go unread - that argument comes from human
lessons-learned systems (NASA's LLIS, audited 2012: neither searched nor
contributed to outside JPL over five years) and it does not transfer. Its
mechanism was tedium, and an agent does not get bored of `grep`; the C compiler
harness's own lesson is the opposite one, log the detail to a file and make it
greppable.

What transfers is narrower and is not about effort: **there is no event that
would cause a session to look.** A test failure announces itself, so `grep
ERROR` finds it. A dead end announces nothing - a session about to re-propose
partitioning the store has no signal telling it to check. And a pointer read
once at session start does not solve that, because the proposal comes forty
turns later. A `SessionStart` hook's output is resent on every turn, so the
entries are in context at the moment of the proposal rather than at the moment
of the greeting. That is what is being bought, and it is what the budget is
paying for.

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

**The budget forces removal rather than saturating.** Appending deltas and
never rewriting sounds like it fills up, but the operations the file allows are
add-one, merge-two and remove-one; only rewriting the whole thing into a
summary is the failure mode ACE measured, and its own prescription is delta
updates *plus periodic de-duplication*. An entry earns its line only while a
session could plausibly propose that approach again, so one whose code or
design question no longer exists comes out. Reaching the nudge band means that
pass is due.

Standard library only, and parses at the floor
`tests/unit/test_tools_portability.py` holds this directory to.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.lines import split_lines  # noqa: E402
from docket.roadmap import document_entry_lines  # noqa: E402

DEAD_ENDS = ROOT / "docs" / "dead-ends.md"

#: The heading of the section that records retired entries. A bullet below it
#: names an entry that left the list and why its question no longer exists. It
#: is not emitted and not budgeted (`PL-5J1S`).
RETIRED = "## Retired"

# Both budgets bind, and they bind in different directions: many short entries
# reach the count, and one essay reaches the bytes.
MAX_ENTRIES = 30
MAX_EMITTED_BYTES = 4000

# The share of either budget that `tests/unit/test_dead_ends.py` keeps the
# shipped file below. Anthropic's own always-loaded index warns near its limit
# and not at it - "if the file is near a limit, Claude Code reminds Claude
# to shorten it: keep one line per entry, move detail into topic files, and
# merge or drop stale entries" - because a decision forced at the cap is taken
# by whoever happens to reach it, mid-task, with no slack to think.
NUDGE_FRACTION = 0.8

# regex: an entry is this file's own fixed line syntax: a bullet, a bold title, a dash and a reason.
ENTRY = re.compile(r"^- \*\*(?P<what>.+?)\*\* [-—] (?P<why>.+)$")
#: What an entry opens with, before its title is known to close: a bullet and a
#: bolded approach. A bullet opening this way is read as one entry even where
#: its title wraps (`PL-F5B9`). Every bullet form CommonMark 0.31.2 opens
#: (§ 5.2) counts - a dash, a plus or a star, after up to three spaces - though
#: `ENTRY` reads only the dash at the margin, so no other form is printed.
# regex: this finds the opening of an entry, a bullet and a bold run, wherever the title goes on to
# wrap.
OPENING = re.compile(r"^ {0,3}[-+*] \*\*")

HEADER = (
    "Dead ends - approaches already tried here and refuted. "
    "`bin/docket show <id>` for the reasoning."
)


def _bullets(text: str) -> list[tuple[int, int, str, int]]:
    """Every top-level bullet opening like an entry, as (line number, lines spanned, text, lazy).

    Read through `docket.roadmap.document_entry_lines`, section by section, so a
    bullet is what CommonMark makes one: an indented line carries it on and is
    joined into it, and a line carrying it on from the margin is declined
    rather than ending it short (`PL-F5B9`, `PL-R417`). `lazy` is that line's
    number, and 0 where no line is declined: the walker ends the bullet at the
    line before it, so its text is short of the entry CommonMark makes. Read a
    line at a time, an entry whose bolded title wrapped was no entry at all,
    and a margin line opening `#1234`, `*` or a pipe ended one with its ids
    unread.
    """
    lines = split_lines(text)
    spans, unread = document_entry_lines(lines)
    declined = {lazy.line for lazy in unread}
    bullets: list[tuple[int, int, str, int]] = []
    for first, end in spans:
        if OPENING.match(lines[first]):
            joined = " ".join([lines[first], *(line.strip() for line in lines[first + 1 : end])])
            bullets.append((first + 1, end - first, joined, end + 1 if end + 1 in declined else 0))
    return bullets


def _retired_from(text: str) -> int:
    """The line number of the `RETIRED` heading, or one past the last line when there is none."""
    lines = split_lines(text)
    for number, line in enumerate(lines, start=1):
        if line.rstrip() == RETIRED:
            return number
    return len(lines) + 1


def _live_bullets(text: str) -> list[tuple[int, int, str, int]]:
    """The bullets above the retired section, which the digest prints and the budget counts."""
    cut = _retired_from(text)
    return [bullet for bullet in _bullets(text) if bullet[0] < cut]


def _printed(text: str) -> list[str]:
    """The lines the digest prints under its header, in the file's order.

    Each entry whole, and in place of a bullet a line carries on from the
    margin, a line naming it. Printed as the walker reads it, that bullet ended
    short of whatever the declined line held, its retrieval id included, and
    nothing said so (`PL-DQ9C`).
    """
    printed: list[str] = []
    for number, _, joined, lazy in _live_bullets(text):
        if lazy:
            printed.append(
                f"- docs/dead-ends.md:{number}: not printed, since line {lazy} carries it on "
                f"from the margin and it would read short; read it in the file."
            )
        elif ENTRY.match(joined):
            printed.append(joined)
    return printed


def emitted(text: str) -> str:
    """What `emit` prints for the file `text`: the header and each line, or nothing."""
    lines = _printed(text)
    if not lines:
        return ""
    return "\n".join([HEADER, *lines])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("emit",))
    parser.parse_args(argv)

    # Silent where the file is missing, so a checkout without it starts
    # cleanly - the same promise every other line of the digest hook makes.
    if DEAD_ENDS.exists():
        out = emitted(DEAD_ENDS.read_text(encoding="utf-8"))
        if out:
            print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
