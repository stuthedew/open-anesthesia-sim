---
id: PL-B8V1
title: ROADMAP.md's declined-to-Gate-2 argument says 'Gate 1 stands at 132 entries ... with 89 still open' in the present tense, and it is now 159 with 94 open
priority: P2
effort: S
status: done
classes: defect, docs
feature: gate-list-integrity
milestone: v0.4.35
touches: ROADMAP.md
added: 2026-09-13
closed: 2026-09-20
pr: 774
verify: python3 tools/doc_check.py check && grep -qF 'stood at 132 entries' ROADMAP.md
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

**Decided 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
The decision is made and it is the item's own recommendation: **date the claim
in place**, which is clause 4 - a dated statement is a record, held to its date
and never to the tree, and a later fact is appended with its own date rather
than written over the earlier one. Restating the argument in ratios is refused
for the reason the item gives: it loses the audit trail to the 2026-09-08
decision. Promoted from `needs-decision` to `ready`, with a `verify:` command
run on 2026-09-19 and watched to fail (exit 1: `doc_check` is green, the
past-tense phrase is absent).
