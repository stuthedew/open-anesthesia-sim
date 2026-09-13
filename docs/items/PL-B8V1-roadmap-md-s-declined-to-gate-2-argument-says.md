---
id: PL-B8V1
title: ROADMAP.md's declined-to-Gate-2 argument says 'Gate 1 stands at 132 entries ... with 89 still open' in the present tense, and it is now 159 with 94 open
status: needs-decision
added: 2026-09-13
priority: P2
effort: S
classes: defect, docs
feature: planning-cadence
touches: ROADMAP.md
---

**Problem.** ROADMAP.md's declined-to-Gate-2 argument says 'Gate 1 stands at 132 entries ... with 89 still open' in the present tense, and it is now 159 with 94 open

**Where.** `ROADMAP.md` § "Declined to Gate 2 on the refilling-queue ground",
the paragraph opening "The arithmetic is the argument."

**Why it is a decision rather than a stale statistic.** Those numbers are the
recorded arithmetic of a decision the project owner took on 2026-09-08: 42
findings were declined to Gate 2 because admitting them would have grown a gate
that was not draining by 31%. As the arithmetic of a dated argument they are
correct and should not be recomputed - recomputing them would rewrite the
reasoning to numbers the decision was not taken on. What is wrong is the
*tense*: "Gate 1 stands at 132 entries ... with 89 still open" reads as a
current fact, and a reader sizing the gate today would take 132 and 89 from it,
where `bin/docket wave` says 159 and 94.

So the fix is one of two shapes and the choice is the item: date the claim in
place ("stood ... on 2026-09-08"), which preserves the argument exactly and
costs two words; or restate the argument in ratios that do not go stale, which
reads better and loses the audit trail to the specific decision. Dating it in
place is the recommendation.

**Found** 2026-09-13 while closing `PL-WSDY` (the current-baseline section's
hardcoded gate count), sweeping the second half of its done-when - that no other
release narrative carries a live gate count. The release narratives are clean;
this one is not a release narrative, which is why it was out of that item's
scope and is filed rather than fixed there.

**Note for whoever takes it.** This paragraph was being edited concurrently on
2026-09-13 by `claude/ready-vcs-batch-closure-xrvfya`, which was moving the
section heading's own count from 59 to 60 entries. Check what landed before
editing.


**Why it matters.** `ROADMAP.md` is where a session reads how big the gate is
before choosing what to do about it, and this paragraph states 132 and 89 in
the present tense where `bin/docket wave` says 159 and 75. A reader sizing the
gate today takes the wrong pair, and the wrongness grows with every entry
added - which is the property that makes it worth fixing rather than
recomputing once.

**Decision needed.** Which of the two shapes in the brief above: **date the
claim in place** ("stood at 132 entries ... with 89 open on 2026-09-08"), which
preserves the 2026-09-08 arithmetic exactly and costs two words - **the
recommendation** - or **restate the argument in ratios** that do not go stale,
which reads better and loses the audit trail to the decision actually taken.

**Done when.** The paragraph can no longer be read as a current gate count, the
2026-09-08 decision's own arithmetic is still recoverable from it, and
`make check` is green.
