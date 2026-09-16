---
id: PL-7CSP
title: bin/docket wave reports 'blocked outside the gate' identically for a blocker the plan schedules before the gate and one nothing schedules at all: PL-W8DQ and PL-NGF7 wait on PL-L9RD, which is in v0.4.26's own Required scope, so they read as stranded when they are merely sequenced
status: untriaged
added: 2026-09-15
---

**Problem.** bin/docket wave reports 'blocked outside the gate' identically for a blocker the plan schedules before the gate and one nothing schedules at all: PL-W8DQ and PL-NGF7 wait on PL-L9RD, which is in v0.4.26's own Required scope, so they read as stranded when they are merely sequenced

**Why it matters.** The line is what a session reads to learn whether a gate
can close, and the two cases it merges want opposite reactions. A blocker the
plan schedules *earlier* than the gate needs nothing from anybody - it clears
in the ordinary course. A blocker nothing schedules means the entry is excused
indefinitely, and somebody should decide whether that is acceptable. Printed
identically, the second hides behind the first.

It has already misled a reader. On 2026-09-15 a session reported all five of
Gate 1's remaining entries to the project owner as blocked outside the gate,
twice, without distinguishing them - and the owner's reply was to ask whether
blockers should be auto-imported into the gate, which is the question the
conflation provokes. Two of the five did not need importing or anything else.

**Where.** `subprojects/docket/src/docket/roadmap.py`'s `_blocked_outside` and
the `blocked outside the gate:` line `render.py:1416` prints.

**The split, measured 2026-09-15** against Gate 1 (recorded under v0.5.0 - the
case you can branch):

| Entry | Blocked by | Where the blocker sits |
| --- | --- | --- |
| `PL-W8DQ` | `PL-L9RD` | v0.4.26's own `Required scope` |
| `PL-NGF7` | `PL-L9RD` | v0.4.26's own `Required scope` |
| `PL-8PS6` | `PL-FG9D` -> `PL-4DCG` | placed by no section |
| `PL-WZVZ` | `PL-FG9D`, `PL-4DCG` | placed by no section |
| `PL-Z34C` | 15 ids | scattered; none placed as a set |

`PL-W8DQ` and `PL-NGF7` are *themselves* in v0.4.26's `Required scope`
alongside their blocker, and `ROADMAP.md`'s timeline puts v0.4.26 before
v0.5.0. So the first two rows are sequenced work inside the milestone being
implemented right now, and the last three are genuinely unscheduled.

**Approach.** `_blocked_outside` already walks the chain and already knows the
one fact this needs: whether the blocker it stopped on is placed by a
milestone section the timeline puts *before* the gate's own milestone.
`roadmap.py` reads both structures already - the frozen list and `Required
scope` - so this is a second answer from a walk that is already happening
rather than a new traversal.

Two verdicts rather than one, and the wording is the deliverable: something
like `sequenced ahead of the gate` against `blocked on unscheduled work`. The
count line wants the same split, so `0 this gate can clear, 5 waiting on work
outside it` stops reading as five dead ends.

**Not** a change to what the gate *counts*. Both verdicts stay carved out of
`clearable`, and the gate closes exactly when it closes today. This is the
report, not the rule - `CLAUDE.md`'s own line about not scripting the
judgment half applies: which of the two a reader should act on is theirs, and
the tool's job is to stop hiding that there are two.

**Done when.** `bin/docket wave` distinguishes the two cases in both the count
line and the id list, and a test pins the split against a gate holding one of
each.

