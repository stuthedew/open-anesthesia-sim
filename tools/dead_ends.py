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

`check` reports two different things, and the split is deliberate. A
*structural* fault fails the build: an entry citing an id that resolves to
nothing, or an entry wrapped across two lines. Both are silent otherwise - a
dangling id leaves a claim with no reasoning behind it, and a wrapped entry's
second line is emitted by nothing and budgeted by nothing.

**Size never fails, and that is a decision rather than laxity.** Going over
budget does not make a commit on an unrelated task wrong, and a red gate that
blocks one is how a session learns to raise the cap to get moving - which is
the one repair that is never right. It warns instead, in two bands.

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
pass is due, and raising the number is the one repair that is never right.

**What is decided here is arithmetic, and only arithmetic.** Entry count,
emitted bytes, one line per entry, and that every `PL-` id an entry cites
resolves to a real item. Whether an approach *deserves* a line - whether a
future session would plausibly propose it again, which is the file's own
admission test - is judgment, and a tool guessing at it would be the "worse
than no tool" case `CLAUDE.md` names: its output would look authoritative and
would not be. The file states that test in prose for a reader; this refuses
only what a reader cannot see at a glance.

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
sys.path.insert(0, str(REPO / "subprojects" / "docket" / "src"))

from docket.store import ID_PATTERN  # noqa: E402

DEAD_ENDS = REPO / "docs" / "dead-ends.md"
ITEMS = REPO / "docs" / "items"

# Both budgets bind, and they bind in different directions: many short entries
# trip the count, one essay trips the bytes. Neither fails the build; both
# warn, and both warn at NUDGE_FRACTION before they are reached.
MAX_ENTRIES = 30
MAX_EMITTED_BYTES = 4000

# The nudge band. Anthropic's own always-loaded index warns *near* its limit
# rather than at it - "if the file is near a limit, Claude Code reminds Claude
# to shorten it: keep one line per entry, move detail into topic files, and
# merge or drop stale entries" - which is the property that matters, because a
# decision forced at the cap is taken by whoever happens to trip it, mid-task,
# with no slack to think.
NUDGE_FRACTION = 0.8

ENTRY = re.compile(r"^- \*\*(?P<what>.+?)\*\* [-—] (?P<why>.+)$")
#: The store's own grammar, so that "cites X, which is not an item" is
#: refused on the same tokens `bin/docket check` calls ids. `PL-[A-Z0-9]{3,4}`
#: stood here and read a three-letter token as an id (`PL-KYW3`).
ITEM_ID = re.compile(ID_PATTERN)

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


def budget(text: str) -> list[str]:
    """Advisories about size. Never errors - see the module docstring for why.

    Two bands, and the first is the one that does the work. At `NUDGE_FRACTION`
    of either budget this names the headroom and the three repairs, so the
    decision about what to drop arrives while there is still slack. Over
    budget it says what is now silently true - the emitted text is past what
    the always-loaded half should carry - and still does not fail, because
    nothing about being over it makes a commit on an unrelated task wrong.
    """
    advisories: list[str] = []
    found = entries(text)
    size = len(emitted(text).encode("utf-8"))

    over_bytes = size > MAX_EMITTED_BYTES
    over_entries = len(found) > MAX_ENTRIES
    near = size >= MAX_EMITTED_BYTES * NUDGE_FRACTION or len(found) >= MAX_ENTRIES * NUDGE_FRACTION

    if over_bytes or over_entries:
        advisories.append(
            f"docs/dead-ends.md is over budget: {len(found)}/{MAX_ENTRIES} entries, "
            f"{size}/{MAX_EMITTED_BYTES} emitted bytes. This text is resent on every turn "
            f"of every session. Three repairs, cheapest first: shorten an entry to one "
            f"line, merge two related entries into one, or drop the entry a session is "
            f"least likely to propose again."
        )
    elif near:
        advisories.append(
            f"docs/dead-ends.md is near budget: {len(found)}/{MAX_ENTRIES} entries, "
            f"{size}/{MAX_EMITTED_BYTES} emitted bytes. Decide now while there is slack - "
            f"shorten, merge, or drop the entry a session is least likely to propose again."
        )

    return advisories


def check(text: str) -> list[str]:
    """Structural errors only. Size is `budget()` above, and it never fails."""
    problems: list[str] = []
    found = entries(text)

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

    for advisory in budget(text):
        print(advisory, file=sys.stderr)

    problems = check(text)
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
