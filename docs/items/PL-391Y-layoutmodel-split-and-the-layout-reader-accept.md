---
id: PL-391Y
title: LayoutModel.split and the layout reader accept sizes that place an Area with no width: split(1, ROW, 5e-324) is taken, and a file with sizes (1.0, 5e-10) sums to one within the tolerance while its second child lies between 1.0 and 1.0; a drag can then no longer give that Area room
status: untriaged
feature: layout-sliver-areas
added: 2026-10-18
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
