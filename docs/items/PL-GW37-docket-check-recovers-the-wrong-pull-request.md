---
id: PL-GW37
title: docket check recovers the wrong pull request for an item closed as a rider on another item's PR, and advises writing that number in
priority: P2
effort: S
status: ready
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_rider_closure_recovers_no_pull_request_number' subprojects/docket/tests/test_vcs.py
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-09-02
---

**Problem.** `docket check` recovers a closed item's pull request number by
taking the newest commit on the default branch whose subject names the item's
id (`subprojects/docket/README.md`, "the newest such commit wins"). For an
item closed on its own pull request that is right. For an item closed as a
*rider* on another item's pull request it is wrong, because the closing
commit's subject leads with the other item's id and so does not name this
one — leaving the item's own triage or capture commit as the newest match.

Observed 2026-09-02. `PL-YLZQ` was closed in `#204` alongside `PL-026`, whose
id leads that commit's subject. `docket check` advised:

    PL-YLZQ: marked done on `origin/main` and records no `pr`, but #159 is
    recoverable from its merge commit; write `pr: 159` into the item so the
    file carries it too

`#159` is `fce85ff`, the commit that *triaged* `PL-YLZQ` into the queue. The
correct number is `204`.

**Why it matters.** The advisory does not merely fail to find a number, which
would be harmless — it names a specific wrong one and instructs a session to
write it into the item. `subprojects/docket/README.md` says a closed item's
whole traceability is the pointer from it to the work, so obeying the
advisory replaces "no provenance" with *false* provenance, which is worse:
a reader following `pr: 159` lands on a triage commit that contains none of
the work, and has no cue that they are in the wrong place. A session has no
reason to doubt the advisory, because the number it prints is real and
resolvable.

The blind spot is the same shape. `PL-KQKM` was closed in `#204` too and got
no advisory at all, because no commit subject names it. That half is safe —
silence, not a wrong answer.

Rider closures are not an edge case here: `CLAUDE.md`'s capture rule and the
`docket` skill both direct that a finding an in-progress item needs in order
to be properly finished is worked with it, on one branch, closed together.
That is exactly the shape that produces them.

**Where.** The recovery lives in `subprojects/docket/src/docket/`; the rule is
documented in `subprojects/docket/README.md` under the `pr` field. The three
items it fired on are `PL-026`, `PL-YLZQ` and `PL-KQKM`, all closed in `#204`
and all now carrying `pr: 204`, verified against `git log origin/main` rather
than taken from the advisory.

**Where it goes wrong, read from the source.** `_merges_naming` in
`subprojects/docket/src/docket/vcs.py` walks `git log --format=%s <base>` and,
for each subject carrying a pull request number, records that number against
every id in `_leading_ids(subject)` — the run of ids the subject *opens* with.
`found.setdefault` keeps the first hit, so the newest such commit wins. Its
docstring already anticipates half of this ("an id that led an earlier subject
too, most often the capture that filed it, was not the merge that landed its
work") and answers it with recency, which is not enough: for a rider the
closing commit does not name the id at all, so recency picks the newest of the
*wrong* commits rather than the right one.

**Two fixes, and they are complementary rather than alternatives.**

*The convention half, which costs no code.* `_leading_ids` already reads a
comma-separated run — `#159`'s subject is "PL-X2XX, PL-8B1K, PL-7QKY,
PL-YLZQ: triage the four working-notes captures", and all four were recovered
from it. So a closing commit subject that led with every id it closes
("PL-026, PL-KQKM, PL-YLZQ Make the simulation step transactional…") would
have worked with the code exactly as it stands. `CLAUDE.md` says to put "that
id" at the front of every commit subject, singular, which is what the session
that produced this defect followed. One clarification there and in the
`docket` skill's close-out mode fixes every future rider closure.

**The convention half landed on 2026-09-02**, approved by the project owner,
and is no longer part of this item. `CLAUDE.md`'s "Name the work after the
item" bullet and the `docket` skill's close-out step both now say that a
commit closing more than one item leads with all of them, comma-separated.
What remains here is the guard.

*The guard half, which is what makes it safe when a session forgets.* A
recovered commit older than the item's own `closed:` date cannot be the commit
that closed it. `fce85ff` is dated 2026-09-01; `PL-YLZQ` carries `closed:
2026-09-02`. Rejecting that pairing suppresses the wrong answer and keeps
every right one, since a closing commit is never older than the closure it
carries. It needs one more field out of the same `git log` (`--format=%ad %s`)
and the `closed` date the store already parses — no diff inspection, no
containment test, and no history the shallow clone may not hold, which is what
makes it affordable where the diff-based test considered first is not.

Silence is the correct outcome when the guard rejects everything: that is
already what happens for `PL-KQKM`, and it is what the check does elsewhere
when the checkout cannot answer.

**Done when.** `docket check` either recovers a rider-closed item's real
pull request number or says nothing, and never advises writing in the number
of a commit that does not contain the item's work.
`subprojects/docket/tests/test_vcs.py` carries
`test_a_rider_closure_recovers_no_pull_request_number`: an item marked done in
a commit whose subject leads with a different item's id, with an older commit
naming this one, recovers nothing rather than the older number.

The convention half of this - `CLAUDE.md` and the `docket` skill saying to
lead a closing subject with every id it closes - is already done, so what is
left is only the guard that catches a session forgetting.
