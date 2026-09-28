---
id: PL-MTHC
title: A merge that resolves an add/add conflict on an item file by keeping one side drops the other side's edits and nothing reports it - #1210 overwrote the PL-8ZGY brief corrections #1199 had put on main
priority: P2
effort: M
status: ready
classes: defect
feature: queue-hygiene
touches: subprojects/docket/src/docket, .claude/skills/docket/modes/capture.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-28 triage pass
added: 2026-09-27
payoff: a merge can no longer silently drop an item brief's corrections by keeping the other branch's copy
not-delegable: the first step is finding which route made the copy, which decides the file the fix goes in and the test that proves it
---

**Problem.** A merge that resolves an add/add conflict on an item file by keeping one side drops the other side's edits and nothing reports it - #1210 overwrote the PL-8ZGY brief corrections #1199 had put on main

**Evidence, 2026-09-27.** `0207afd7` recovered `PL-8ZGY`'s file onto
`claude/cool-meitner-pjnueb` from `claude/pl-w40l-kidkwe` while `#1199` was
still open there, so two branches each held a copy. `9d71a82c` corrected the
copy on `#1199`'s branch, with the owner's agreement; `#1199` merged as
`30820c98`; `82f71f2a` resolved the add/add conflict that followed by keeping
the other branch's copy whole; and `#1210` (`887fd223`) then put the
uncorrected brief on `main`. Every check passed throughout. Add/add conflicts
on item files recur - `PL-KBFN`, `PL-8KPD` and `PL-MQH0` each work around one -
so the triage that takes this asks whether one mechanism explains them.
Restored on `claude/pl-8zgy-restore-brief`.

**Why it matters.** Every check passed while the owner's agreed corrections to
a brief were lost; they came back only because a session noticed (`#1215`,
`2d61cd3d` on `main`, records the loss). A brief is where decisions are
recorded, so a silent loss is a lost decision.

**Generator check.** `PL-KBFN`, `PL-8KPD` and `PL-MQH0` each waited on the fact
this merge misread - an item created on an unmerged branch exists nowhere else,
so a copy elsewhere is a second, independent add - rather than misreading it.
One misreading item is not a generator. The lead to check first is `PL-WNCT`'s
fact (whether pushed branch work has an open pull request that will carry it to
`main`): the copy was taken while `#1199` was open and would have carried it.

**Done when.** The route that put a second copy of the item on another branch
while an open pull request carried the first is found, and it refuses or
reports such a copy, held by a test; or this brief records why neither is
decidable and the capture skill's recovery step says to wait for the open pull
request.
