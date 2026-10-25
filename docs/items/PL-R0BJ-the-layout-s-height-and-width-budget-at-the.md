---
id: PL-R0BJ
title: The layout's height and width budget at the 1366 by 700 reference, which the Qt port's compare mode dropped: four members from 2026-10-18 to 2026-10-20, now pinned by tests and one recorded decision
priority: P3
effort: S
status: done
classes: defect
feature: defect-review-2026-10
milestone: v0.6.4
touches: docs/items
added: 2026-10-25
closed: 2026-10-25
pr: 1783
payoff: the audit records that the reference window's budget was one mechanism behind four defects
verify: grep -qE '^generator: spent' docs/items/PL-R0BJ-*.md
root-cause-of: PL-F2YS, PL-JG82, PL-QLZ5, PL-NNML
generator: spent - the readout row, the region height and the viewport are now pinned by tests at the reference size, and the compare-mode chart height is a recorded decision in ROADMAP.md
misread: What must fit at the 1366 by 700 reference window, in compare mode too
---

**Problem.** The layout's height and width budget at the 1366 by 700 reference, which the Qt port's compare mode dropped: four members from 2026-10-18 to 2026-10-20, now pinned by tests and one recorded decision

**The fact the members misread.** `docs/MODEL.md` and the ratified layout decisions set what must fit at the 1366 by 700 reference window. The Qt port's compare mode was built without reading that budget:

- `PL-F2YS`: the record column width and the paired two-run readouts were dropped.
- `PL-JG82`: the chart fell below its 360 px minimum height in compare mode.
- `PL-QLZ5`: nothing said how much height the compare-mode unconditional region may spend.
- `PL-NNML`: the whole page sat inside a scroll area, so the unconditional region and the disclaimer could leave the viewport.

**Why it matters.** The audit of where product defects come from needs each shared cause recorded, so that a recurrence is recognised as one.

**Done when.** This head records its members and why it is spent.

**Generator check.** Recorded for the audit by `PL-R4Y2`'s defect review.
