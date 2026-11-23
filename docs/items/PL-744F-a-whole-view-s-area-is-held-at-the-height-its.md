---
id: PL-744F
title: A whole View's Area is held at the height its View needs at the Area's least width, which overstates it at a wider drawn width; at 1366x768 with a branch, Induction's Parameters Area is held about 30 px taller than it needs, so the page scrolls that much more
status: untriaged
feature: window-is-the-frame
added: 2026-11-23
filed-pr: 2282
---

**Problem.** `AreaLayout._view_need` in `src/anesthesia_sim/app/area_layout.py`
measures a `whole` View's content height at the Area's least width, so that
the need does not depend on the last layout. An Area drawn wider than its
least width then needs fewer lines of wrapped text, but is still held at the
taller height. The page grows by the difference whenever the Areas do not fit
the window.

**Measured 2026-11-23** (Inter, 1366 by 768, a branch open, 300 s of one run),
by reading each whole View's least height at the width its Area is drawn:

| Workspace | View | Held, px | Needed at drawn width, px | Drawn width, px |
| --- | --- | --- | --- | --- |
| Default | Branch | 137 | 100 | 541 |
| Induction | Parameters | 323 | 293 | 656 |
| Maintenance | Parameters | 323 | 293 | 592 |

So the page scrolls about 30 to 37 px more than the Views need in each
shipped Workspace. The blind review of `PL-5J1X` (hold the page's scroll to
what the Areas lack) found it.

**What a fix has to keep.** The need was measured at the least width so that
one settle gives the same sizes as the next. A need taken at the drawn width
can feed back: a shorter need can remove the page's scroll bar, which widens
the Areas, which shortens the need again. The widths of the Areas come from
their width needs and the window, not from their heights, so a second pass
that re-measures each whole View at the width the first pass drew it should
settle. The fix must show that it does, including at a page height where the
scroll bar just appears or disappears.
