---
id: PL-MFM4
title: bin/docket release's collision guard reads unmerged refs for a cut in progress, so it cannot see a second session that has filed a release item and asked the owner for the version without cutting anything: PL-Z0C7 and PL-R5VS were two ids for one release and every guard matched both cleanly
priority: P2
effort: M
status: done
classes: defect
milestone: v0.5.11
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
added: 2026-09-19
closed: 2026-09-24
pr: 995
reason: Fixed by PL-331V: a release item names resource: release-train and its claim holds the train, so bin/docket new --resource refuses a second filing and bin/docket release refuses a cut beside another session's train claim
payoff: stops two sessions filing two release items for one release while every existing guard answers both cleanly
verify: grep -q 'def test_an_open_release_item_from_another_session' subprojects/docket/tests/test_release.py
---

**Problem.** bin/docket release's collision guard reads unmerged refs for a cut in progress, so it cannot see a second session that has filed a release item and asked the owner for the version without cutting anything: PL-Z0C7 and PL-R5VS were two ids for one release and every guard matched both cleanly

**The instance, confirmed at triage 2026-09-20.** `PL-Z0C7` ("Cut v0.4.31 from
the 10 items finished since v0.4.30") is `dropped`; `PL-R5VS` ("Cut v0.4.31
from the 14 finished items since v0.4.30") is `done`. Two ids, two sessions,
one release - and every guard this project has answered cleanly for both,
because neither session had cut anything yet when the other started.

**Why it matters.** `bin/docket release`'s collision guard is the one that
matters most, because a release is the single piece of work this project does
that cannot be merged twice: two cuts under different numbers stamp
`milestone:` onto overlapping sets of items, and the second to merge claims
work the first shipped (`PL-66FP`, where two sessions cut v0.3.7). The guard is
built for that and reads the right things - the default branch's notes file and
version field, and unmerged refs carrying a cut.

What it cannot see is the window before any of that exists. A release session's
first act is to file the release item and ask the project owner which version
to cut; the answer takes a turn, or several. Throughout that window the session
has written one item file and nothing else, so there is no notes file, no
version bump and no ref carrying a cut - and the second session to arrive gets
a clean answer from every guard and files a second release item. The window is
not incidental: § "Versioning decision" makes the version a named judgment
rather than an increment, so asking the owner *is* the procedure, and the
procedure is what opens the gap.

The `docket` skill already names the residual - "Neither read sees a session
that has pushed nothing" - and points at `list_sessions`, which is this harness
only and cannot reach `bin/docket`. So the store holds the evidence that would
close the gap and nothing reads it: a filed, open release item is exactly the
declaration the guard is missing.

**Likely shape of a fix**, not settled here: have the collision guard read the
store for an open item whose work is a cut - the same reading `bin/docket
release` already does to find what is releasable - and refuse, naming the id
and its session, rather than only reading refs. The cost to weigh is a stale
open release item blocking a legitimate cut, which is the same false-positive
shape `stranded` and `flight` already leave to the reader's judgment on a
branch's age.

**Done when.** A second `bin/docket release` refuses, or warns naming the id,
while an open release item filed by another session stands with nothing cut
yet, and a test drives that state.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". This item is also named in paragraphs quoted in the brief of `PL-WQF1`.

> - PL-MFM4 (M) `bin/docket release`'s collision guard reads refs for a cut in progress, so it cannot see a second session that has filed a release item and cut nothing
