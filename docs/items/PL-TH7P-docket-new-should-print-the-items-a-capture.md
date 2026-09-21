---
id: PL-TH7P
title: docket new should print the items a capture might duplicate, from title words and touches overlap
priority: P2
effort: S
status: dropped
classes: session-cost, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/concurrency.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
added: 2026-08-30
closed: 2026-09-21
reason: Same finding as PL-TZ7T (bin/docket new files a duplicate title without noticing), which shipped the whole of this item's Done when in #793 on 2026-09-20: cli.cmd_new searches before the write and prints after it, never prompting; test_new_names_an_existing_item_with_a_near_identical_title covers a capture that overlaps and test_new_says_nothing_about_an_item_declaring_a_different_path one that does not; subprojects/docket/README.md documents it under 'docket new'. PL-JKML's duplicate sweep already ruled this pair a high-confidence same-finding with PL-TZ7T as survivor, and left it standing for one stated reason - PL-TZ7T was in flight - which lapsed when that branch merged. The only clause not shipped is this item's title-word key, which PL-TZ7T measured and refuted: title closeness alone catches 0 of 13 known duplicate pairs at any threshold flagging fewer than 768, and fires hardest on the items meant to recur; the shipped key is the declared path selecting with the title only ranking inside it, top 3 for 8 of 9 pairs. Nothing here is lost - this item's two historical instances are recorded on the items themselves (PL-2R01 dropped as a duplicate of PL-68XK; PL-0TRS closed by PL-020's work), its verify: pinned a test name (test_new_prints_candidate_duplicates) that no longer describes any work owed, and this file stays for the pre-PL-TZ7T evidence in its brief.
verify: uv run pytest subprojects/docket/tests/test_cli.py -q && grep -rq 'def test_new_prints_candidate_duplicates' subprojects/docket/tests
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
