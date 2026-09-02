---
id: PL-TH7P
title: docket new should print the items a capture might duplicate, from title words and touches overlap
priority: P2
effort: S
status: ready
classes: session-cost, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/concurrency.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
verify: uv run pytest subprojects/docket/tests/test_cli.py -q && grep -rq 'def test_new_prints_candidate_duplicates' subprojects/docket/tests
added: 2026-08-30
---

**Problem.** `docket new` records a capture without looking at what is already
in the queue, so a finding that duplicates an existing item is written as a new
one and is only caught later, by a person noticing. It has happened at least
twice. PL-2R01 (fail `docket check` when a recorded commit hash is unreachable)
was dropped as a duplicate of PL-68XK. PL-0TRS, captured on 2026-08-30 while
closing PL-ZQ9C, duplicated PL-020 (bring tests and `tools/` under the
type-check gate) - which had measured the very subtree the capture was about,
five days earlier, and named it in its scope.

**Why it matters.** A duplicate is not merely untidy. The original carries
work already done - PL-020 held a measured error table and a recorded decision
- and the duplicate carries none of it, so whichever one a later session opens
decides how much context it starts from. It also splits the record: the new
fact in PL-0TRS (one live mypy error in `roadmap.py`) belonged in PL-020's
stale measurement, and filing it separately would have left PL-020 claiming
"already clean; free to gate" while a gate built from it landed red.

This is the cheapest possible instance of the rule in `CLAUDE.md` about
putting the decidable part in code. Whether two items overlap in the files
they declare is decidable from the tree; whether they are *the same work* is
not, and is left alone.

**Where.** `subprojects/docket/src/docket/cli.py`'s `cmd_new`, reusing the
`touches` overlap that `subprojects/docket/src/docket/concurrency.py` already
computes for `docket concurrent`.

**Approach.** After writing the file, print at most a few candidates: open
items sharing a significant word with the new title, and - once the capture
acquires `touches` at triage - items whose declared paths overlap. Advisory
text only. It must not prompt, block, or ask a question: `CLAUDE.md` requires
capture to stay cheap, because a capture that costs a detour is one that does
not happen. Printing lines after the file is written costs nothing and is read
or ignored at the session's discretion.

Title matching should be dumb on purpose - shared words above a stop list,
not similarity scoring. A tool that guessed at the judgment half would produce
output that looks authoritative and is not, and the failure mode of a dumb
matcher is a candidate line the reader dismisses in a second.

**Done when.** `docket new` prints candidate duplicates when any exist, prints
nothing when none do, never prompts, and has a test covering a capture that
overlaps an existing item's title and one that overlaps nothing.
