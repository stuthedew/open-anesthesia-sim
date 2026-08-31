---
id: PL-MGNC
title: A readable merge-base does not make the in-flight commit walk complete, so a shallow clone reports merged items as in flight
priority: P2
effort: S
status: ready
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-08-31
verify: uv run pytest subprojects/docket/tests/test_vcs.py -k contained
---

**Problem.** `branches_in_flight` splits candidate refs on whether `git
merge-base <base> <ref>` returns anything, and treats the readable half as
answerable: `_unmerged_commits` then walks `<ref> ^base` and reads the id at
the front of every subject it sees. In a shallow clone the walk is the part
that is incomplete, not the merge-base — `^base` can only exclude commits the
checkout actually holds, so every commit below the shallow boundary reads as
the branch's own work.

**Observed 2026-08-31, in this repository's own session digest.** The
session-start hook reported twenty-seven ids in flight:

    In flight on a branch: PL-019F, PL-020, PL-4CW7, PL-64LS, PL-69J3,
    PL-8MZN, PL-921W, PL-CMCB, PL-CPSY, PL-D2GW, PL-DGM4, PL-DL1X, PL-FBCC,
    PL-H7XN, PL-J295, PL-KKX4, PL-KWC1, PL-N7R9, PL-NSN9, PL-Q2BJ, PL-S1P1,
    PL-S4M2, PL-SRCP, PL-V5XM, PL-W5LG, PL-WFJ9, PL-ZN0N
    - do not start these again.

Eighteen of those twenty-seven are closed — fifteen `done` and three
`dropped` — so the line was 67% false positives. The nine that are open
include `PL-NSN9`, one of the two remaining entries of v0.2.8's frozen list,
so `docket next` was withholding the gate's own unfinished work at the moment
a session asked what to do next, under the words "do not start these again".
After `git fetch origin main` deepened the clone enough for the walk to
exclude correctly, `bin/docket flight` in the same checkout reported "No
branch carries an item id".

**Why it matters.** It is the failure `PL-CPSY` describes — startable work
made invisible with no line of output saying so — arriving through a
mechanism the shallow-checkout discipline was supposed to have closed.
`PL-XCYB` and `PL-J295` are both frozen v0.2.8 entries and both stand for one
rule: a check must refuse to answer in a shallow checkout rather than answer
wrongly. `branches_in_flight` applies that rule to the merge-base probe and
then answers wrongly anyway, because a resolvable merge-base was taken as
proof the history needed for the walk is present. It is the second place the
same hazard applies, missed the same way `PL-J295` was missed.

The direction is the dangerous one: false positives here do not merely add
noise, they remove items from `docket next`, and the digest presents them
with "do not start these again".

**Not reproduced on demand.** A `--depth 1` clone with every branch tip
fetched takes the *declined* path instead — merge-base returns nothing, and
`flight` correctly reports the refs as unread. The trigger is an intermediate
depth where the merge-base resolves but the walk does not reach it, which is
what the container held at session start and what a deepening fetch then
removed. The evidence above is a single observation plus the code path; a
reproduction is part of the work.

**Where.** `subprojects/docket/src/docket/vcs.py` — the `readable` /
`unreadable` split in `branches_in_flight`, and `_unmerged_commits`.

**Done when.** A checkout that cannot prove a commit is contained in the
default branch does not report that commit's id as in-flight work, and a test
covers the intermediate-depth case rather than only the depth-1 one.

**Relations.** `PL-CPSY` (a squash-merged branch whose ref survives reports
its items in flight forever) is the same output going wrong by a different
mechanism, and `PL-S1P1` (the refs that went unread never reach `docket
next`) is the third hole in the same function. All three are `vcs.py` and
collide on `touches`: one session, or serialized.

**Triaged and admitted to v0.2.8's frozen list, 2026-08-31.** P2, `defect`/
`infra`, `parallel-sessions` beside `PL-CPSY` and `PL-S1P1`. Admitted under
the scope test in `ROADMAP.md`'s "What the freeze closes, and what it does
not" — the session-start digest and the queue's ranking are both machinery
this release's goal names — and it is the only one of the three `vcs.py` holes
observed firing.

The `verify:` command keys on `contained`, matching the word the Done-when
uses, and selects nothing in `test_vcs.py` today: the three existing tests
that mention a shallow clone (`-k shallow`) all pass already, so that key
would have proved nothing. Confirmed before it was written down — `-k
contained` collects 40 items and deselects all 40.

Work it with `PL-CPSY` and `PL-S1P1`: all three change `branches_in_flight`
and its return value, so serializing them or taking them in one session is the
difference between one design pass over that function and three conflicting
ones.
