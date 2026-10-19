---
id: PL-25D9
title: LayoutModel.join refuses a join that needs a cut beside an Area narrower than BORDER_ALIGNMENT_TOLERANCE, though a tree holding the result exists: column[row(0.5, 5e-10, 0.5-5e-10)[1,2,3], row[4,5]] refuses joining 1 and 4, where a 2e-9 sliver joins
priority: P3
effort: S
status: done
classes: defect
feature: layout-sliver-areas
touches: src/anesthesia_sim/layout/model.py, tests/unit/test_layout_model.py
blocked-by: PL-391Y
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
closed: 2026-10-19
pr: 1674
payoff: A reader can never be refused a join beside a sliver Area, because no layout can hold an Area that narrow
verify: grep -q "PL-25D9's layout" tests/unit/test_layout_model.py
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
test in `tests/unit/test_layout_model.py` pins it. It was blocked on `PL-391Y`,
whose choice decided which outcome applied.

**Closed 2026-10-19 as unreachable.** `PL-391Y` chose
`BORDER_ALIGNMENT_TOLERANCE` as the smallest width an Area may have, so the
layout this item builds, whose Area 2 is 5e-10 of the window wide, is refused
when it is built. `test_a_layout_holding_an_area_no_wider_than_the_alignment_tolerance_is_refused`
in `tests/unit/test_layout_model.py` holds that refusal for this item's exact
tree. Without an Area narrower than the tolerance, the borders on each side of
an Area are never within the tolerance of each other, so a join cannot need a
cut beside one.
