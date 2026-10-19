---
id: PL-391Y
title: LayoutModel.split and the layout reader accept sizes that place an Area with no width: split(1, ROW, 5e-324) is taken, and a file with sizes (1.0, 5e-10) sums to one within the tolerance while its second child lies between 1.0 and 1.0; a drag can then no longer give that Area room
priority: P2
effort: S
status: done
classes: defect, ux
feature: layout-sliver-areas
touches: src/anesthesia_sim/layout/model.py, src/anesthesia_sim/layout/serialization.py, tests/unit/test_layout_model.py, tests/unit/test_layout_serialization.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
closed: 2026-10-19
pr: 1674
payoff: A View a reader asked for can no longer end up hidden at zero width with no drag that brings it back
verify: grep -q 'def test_a_split_that_leaves_an_area_no_width_is_refused' tests/unit/test_layout_model.py && grep -q 'def test_a_file_whose_sizes_leave_an_area_no_width_is_refused' tests/unit/test_layout_serialization.py
---

**Problem.** LayoutModel.split and the layout reader accept sizes that place an Area with no width: split(1, ROW, 5e-324) is taken, and a file with sizes (1.0, 5e-10) sums to one within the tolerance while its second child lies between 1.0 and 1.0; a drag can then no longer give that Area room

Found by the adversarial review of `#1579` (PL-5HSG, PL-G60V), 2026-10-18.
`#1579` made `resize` refuse a drag that would round an Area to no width, and
refuse a drag inside a split of no extent rather than divide by zero. It did
not change `split` or the reader. So a layout can still arrive holding an Area
of no width. Once it holds one against the window's edge, every drag that
would give it width is refused, where `origin/main` before `#1579` let a root
drag recover it. The likely fix is to refuse, in `split` and in
`layout/serialization.py`, any size whose boundary `_boundaries` places on
its neighbour's. Reproducers are in the review's scratch scripts, restated
here: `split(AreaId(1), ROW, 5e-324)`, then `split(1, COLUMN, 0.5)` and
`split(1, ROW, 0.5)` alternately, then drag the innermost handle.

**Reproduced 2026-10-19** on `main` at the triage pass, from a scratch script
using the helpers in `tests/unit/test_layout_model.py`:
`layout(area(1)).split(AreaId(1), Orientation.ROW, 5e-324)` returns a row with
sizes `(5e-324, 1.0)`, and `layout(row((1.0, 5e-10), area(1), area(2)))` is
built without a refusal.

**Why it matters.** A layout file or a split can leave an Area that cannot be
seen and, since `#1579`, cannot be dragged back open. A reader then has a View
they asked for that is gone from the screen with no way to recover it short of
resetting the Workspace.

**Done when.** `LayoutModel.split` refuses an `at` that would leave either part
with no width, and the layout reader in `layout/serialization.py` refuses a
file whose sizes do the same. Each refusal names the Area and the size. A test
in each module pins the refusal with the reproducers above. Decide in the work
whether the smallest width allowed is "boundaries that do not coincide" or
`BORDER_ALIGNMENT_TOLERANCE`. The second also makes `PL-25D9` (a join refused
beside an Area narrower than the tolerance) impossible to reach, so say which
was chosen in that item.

**Checked 2026-10-19:** still reproduced on `main` at `6fd84bd5`.
`split(AreaId(1), ROW, 5e-324)` returned sizes `(5e-324, 1.0)`, and
`layout_from_dict` read a row with sizes `(1.0, 5e-10)`, placing Area 2 at
`left=1.0, right=1.0`.

**Fixed 2026-10-19.** The smallest width chosen is `BORDER_ALIGNMENT_TOLERANCE`,
not "boundaries that do not coincide". An Area no wider than the tolerance has
its two edges read as one line by `borders()` and `join`, so a layout could
hold an Area that every geometric query treats as having no width. The rule is
held once, in `LayoutModel.__post_init__` (`_too_narrow`), which measures each
Area against its window, however its sizes are nested. The reader already turns
an `InvalidLayout` from that constructor into a `LayoutFormatError`, so it
refuses such a file with no second copy of the rule. `split` refuses the cut
first, as a `LayoutRefused`, and `resize`'s `_squeezed` uses the same bound, so
a drag never builds such a layout either. Each refusal names the Area and its
size. Two existing tests built Areas narrower than the tolerance on purpose.
`test_a_drag_refuses_a_gap_the_stored_sizes_would_round_away` now drags to
within the tolerance rather than reading a sliver from a file, and
`test_a_drag_moves_every_handle_on_its_line_or_is_refused` uses a middle Area
1.5 times the tolerance wide. Their assertions are unchanged.

**Regression record.** Against `model.py` from `6fd84bd5`,
`uv run pytest -p no:randomly tests/unit/test_layout_model.py tests/unit/test_layout_serialization.py -k "no_width or alignment_tolerance"`
fails `test_a_split_that_leaves_an_area_no_width_is_refused` and
`test_a_layout_holding_an_area_no_wider_than_the_alignment_tolerance_is_refused`
with "DID NOT RAISE LayoutRefused" and "DID NOT RAISE InvalidLayout", and
`test_a_file_whose_sizes_leave_an_area_no_width_is_refused` with "DID NOT
RAISE LayoutFormatError".
