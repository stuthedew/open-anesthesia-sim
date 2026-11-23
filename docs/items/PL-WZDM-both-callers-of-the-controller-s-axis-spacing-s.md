---
id: PL-WZDM
title: Both callers of the controller's _axis_spacing_s raise its result to one second, where the function could return that minimum itself
status: untriaged
feature: tests-detect-wrong-values
added: 2026-11-23
filed-pr: 2306
---

**Problem.** `_axis_spacing_s` in `src/anesthesia_sim/app/controller.py` returns 0 for an axis of zero width, and both of its callers, `drawn_window` and `preview_window`, then raise the spacing to one second with `max(spacing_s, 1)`. The one-second minimum is stated in three places, and mutants 21 and 22 of the 2026-11-23 mutation run, which change those `max` calls, survive because the chart never asks for a zero-width axis.

`PL-PZSF` found it on 2026-11-23, and recorded the reason in the function's docstring.

**What to do.** Have `_axis_spacing_s` return at least one second, remove the two `max` calls, and update its docstring. Check that `drawn_window` and `preview_window` return the same instants as before for a zero-width axis, with a test for each.
