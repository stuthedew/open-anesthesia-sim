---
id: PL-GW37
title: docket check recovers the wrong pull request for an item closed as a rider on another item's PR, and advises writing that number in
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.3.6
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-09-02
closed: 2026-09-04
pr: 285
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_rider_closure_recovers_the_pull_request_that_closed_it' subprojects/docket/tests/test_vcs.py
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

**Worked 2026-09-04. The guard built is not the one briefed, and the reason is
measured.** The project owner chose it from three options after the date test
was shown to fail.

*What was built.* The subject scan keeps its cheap single history read, but its
answer is now **confirmed** before it is believed: the commit it found must read
`status: done` in its own tree and not in its parent's - the same test
`_number_closing` already applies to the file. An unconfirmed hit falls through
to that file reading rather than being recorded. Two `git show` per id the scan
answered, asked only of items whose `pr` is missing.

*Why that and not the date test.* Rejecting a commit older than `closed:` keeps
84 of 122, correctly rejects 6, and **wrongly rejects 32** - a timezone skew,
since `closed:` is the session's today in UTC and the squash merge carries the
owner's local date at `-0500`. The confirmation has no such failure: over the
same 122 it agreed with the file reading wherever both could answer, and
disagreed nowhere.

*What it fixes, measured over all 209 closed items carrying a `pr`.* Recovery
goes from **101 correct and 25 wrong** to **114 correct and 12 wrong**, with 20
fixed and 7 regressed. `PL-YLZQ` - the case this item was raised for - goes from
`159`, the commit that triaged it, to `204`, the merge that closed it.

*The defect was wider than the brief.* Only `PL-YLZQ` is the rider shape. The
commoner one is a *later* commit winning by recency: `PL-1TF4` and `PL-J49T`
recovered `250`, whose subject reads "record #249"; `PL-B0YN` and `PL-G1MF`
recovered `188` from "record their pull request" against a true `186`. Both
shapes are one defect - the scan answers with any commit leading with the id,
and a closure is only one kind - and both are fixed by the same confirmation.

*The seven regressions are two known shapes, each captured rather than fixed
here.* Four recover the renaming commit, because the fallback walks `git log`
without rename detection and the parent does not hold the path at all
(`PL-S5LB`). Three are items whose work landed in one pull request and whose
`status: done` was written in a later one, so the file reading answers with the
closure rather than the work (`PL-YDL6`) - the shape `PL-D2GW` closed by
requiring the two to travel together, so it exists only in items predating that
rule.

*The brief's named test was not written, deliberately.* It specifies
`test_a_rider_closure_recovers_no_pull_request_number` - silence for a rider.
Silence was the best the date test could have managed; the confirmation does
better, so the test asserts the real number instead. Reality outranks the
brief here.

**Done when.** `docket check` either recovers a rider-closed item's real
pull request number or says nothing, and never advises writing in the number
of a commit that does not contain the item's work.
`subprojects/docket/tests/test_vcs.py` carries
`test_a_rider_closure_recovers_no_pull_request_number`: an item marked done in
a commit whose subject leads with a different item's id, with an older commit
naming this one, recovers nothing rather than the older number.

**The date guard proposed above does not work, measured 2026-09-04.** Rejecting
a recovered commit older than the item's own `closed:` date was expected to
"suppress the wrong answer and keep every right one". Run against all 122 closed
items on `origin/main` that carry a `pr` and are named by a leading-id subject,
it keeps 84, correctly rejects 6 - and **wrongly rejects 32**.

The cause is a timezone skew, not a flaw in the reasoning. A session writes
`closed:` as its own today in UTC; the squash merge carries the project owner's
local date at `-0500`, so `%cs` reads one day earlier for anything merged after
19:00 Central. `PL-MC8Z` is the case in miniature: `closed: 2026-09-04`, merge
`%cs` 2026-09-03, `pr: 279`, entirely correct and rejected by the test. A guard
that suppresses 32 correct recoveries to catch 6 wrong ones is worse than none.

**The six wrong answers are also not all riders.** Only `PL-YLZQ` is the shape
this item describes. The other five are a *later* commit winning by recency -
`PL-1TF4`/`PL-J49T` recovered `250`, the bookkeeping merge whose subject reads
"record #249"; `PL-B0YN`/`PL-G1MF` recovered `188` from "record their pull
request" against a true `186`; `PL-X0RG` recovered `192` from a follow-up fix
against a true `187`. The defect is therefore wider than the brief states: the
subject scan answers with *any* commit whose subject leads with the id, and a
closure is only one of the kinds of commit that do.

**And the fix now available did not exist when this was written.** `PL-2XTF`
added `_number_closing`, which finds the commit that actually flipped `status:
done` in the item's own file and rejects later edits by comparing against the
parent. Run against all six wrong cases it answers all six correctly, `PL-YLZQ`
included (`204`, the number this item says is right). It is already the
fallback in `_merges_naming`; it simply never runs for these items, because the
subject scan answered first and `found.setdefault` kept that answer.

So the remaining question is not how to reject a bad subject-scan hit by date,
but whether to confirm the hit at all. See the decision below.

The convention half of this - `CLAUDE.md` and the `docket` skill saying to
lead a closing subject with every id it closes - is already done, so what is
left is only the guard that catches a session forgetting.
