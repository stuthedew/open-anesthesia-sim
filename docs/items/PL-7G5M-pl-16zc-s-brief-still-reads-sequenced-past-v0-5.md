---
id: PL-7G5M
title: PL-16ZC's brief still reads 'sequenced past v0.5.0, not clearable before it begins' after PL-G59B closed and promoted it to ready, so the one entry wave says Gate 1 can clear tells the session that opens it not to build it
priority: P3
effort: S
status: done
classes: docs
feature: teachable-case
touches: docs/items/
added: 2026-09-15
closed: 2026-09-15
verify: python3 tools/doc_check.py check && grep -qF 'The deferral this item carried is discharged' docs/items/PL-16ZC-the-two-clinical-references-and-the-control.md
---

**Problem.** PL-16ZC's brief still reads 'sequenced past v0.5.0, not clearable before it begins' after PL-G59B closed and promoted it to ready, so the one entry wave says Gate 1 can clear tells the session that opens it not to build it

**Why it matters.** `bin/docket wave` reports Gate 1 as `1 this gate can clear`
and that one entry is `PL-16ZC`, so it is what the beat `clear the gate` points
every session at. The item's fields are correct: `PL-G59B` (port the
concentration chart to pyqtgraph) closed, the promotion advisory fired, and
`status` is now `ready` with no `blocked-by`. What is stale is the prose above
the problem statement, which is a project-owner block reading:

> **And therefore sequenced past v0.5.0, not clearable before it begins**
> (project owner, 2026-09-14, on `PL-NR2K`).

A session that reaches the item the way the owner usually starts one - by name,
or off `bin/docket next`, which ranks it second - reads a standing instruction
not to build it, against a field set that says it is the next thing to do. The
two readings cannot both be acted on, and the block is the louder of them.

**Why the deferral expired rather than being wrong.** The reason of record was
that building the control on Flet first is the one piece of open Gate 1 work the
port throws away whole, because the legend table it extends lives in
`app/simulation_view.py`, which the port rewrites from scratch. `blocked-by:
PL-G59B` was chosen deliberately over the port's version so the deferral would
expire exactly when the chart port landed - which it has. The item's own
`verify:` already names `tests/integration/test_qt_chart.py`, so the field set
has moved on and only the sentence has not.

**Where the fix is not.** `ROADMAP.md` § "Sequenced past v0.5.0, so not
clearable before it begins" is a frozen snapshot and says in terms that its
counts and entries stay as the freeze wrote them - "Do not 'fix' the count to
agree with the prose". Nothing in that section is to be edited. The stale
sentence is in the item file.

**Done when.** `PL-16ZC`'s brief says what is true now: the deferral is
discharged, `PL-G59B` having landed, and the build is open. The project-owner
block is amended rather than deleted - it is the record of why the item waited -
and the decision half it names ("whether the references and the control marks
are hideable at all", which can close the item writing no code) survives
unchanged, because nothing about it depended on the toolkit.

**Closed 2026-09-15 with `PL-16ZC` itself.** The amended block records the
deferral as discharged rather than deleting it, names `PL-G59B` as the blocker
whose closing discharged it, and leaves `ROADMAP.md` Gate 1 § "Sequenced past
v0.5.0" untouched as that section requires. `PL-16ZC` closed in the same commit
on the project owner's delegated call, so the contradiction this item names is
gone in both directions: the prose no longer says stop, and the fields no longer
say go.
