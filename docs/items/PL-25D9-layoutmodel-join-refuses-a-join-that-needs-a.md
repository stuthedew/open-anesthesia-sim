---
id: PL-25D9
title: LayoutModel.join refuses a join that needs a cut beside an Area narrower than BORDER_ALIGNMENT_TOLERANCE, though a tree holding the result exists: column[row(0.5, 5e-10, 0.5-5e-10)[1,2,3], row[4,5]] refuses joining 1 and 4, where a 2e-9 sliver joins
priority: P3
effort: S
status: blocked
classes: defect
feature: layout-sliver-areas
touches: src/anesthesia_sim/layout/model.py, tests/unit/test_layout_model.py
blocked-by: PL-391Y
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
---

**Problem.** LayoutModel.join refuses a join that needs a cut beside an Area narrower than BORDER_ALIGNMENT_TOLERANCE, though a tree holding the result exists: column[row(0.5, 5e-10, 0.5-5e-10)[1,2,3], row[4,5]] refuses joining 1 and 4, where a 2e-9 sliver joins

**Reproduced 2026-10-19** on `main`: with
`column((0.5, 0.5), row((0.5, 5e-10, 0.5 - 5e-10), area(1), area(2), area(3)), row((0.5, 0.5), area(4), area(5)))`,
`join(AreaId(1), AreaId(4))` raises `LayoutRefused` ("no straight cut divides
the Areas the join would leave"). The same tree with a `2e-9` middle Area joins.

**Why it matters.** The case needs an Area narrower than
`BORDER_ALIGNMENT_TOLERANCE` (1e-9 of the window), which only `PL-391Y`'s gap
lets a layout hold. A reader who reaches it is refused a join that a valid
layout could hold.

**Done when.** One of two outcomes. If `PL-391Y` refuses any Area narrower than
`BORDER_ALIGNMENT_TOLERANCE`, this case cannot be built, and the item closes as
unreachable with that test named. Otherwise `join` takes the case above, and a
test in `tests/unit/test_layout_model.py` pins it. Blocked on `PL-391Y` because
its choice decides which outcome applies.
