---
id: PL-P6TK
title: The approved-wording test records an Area's 'too small' notice at 13 event points, because the run-state scenarios it reuses lay their dashboard out at 1400 by 1000 px, so a font change that moves an Area's size across a power of ten fails it in 13 places with no change of wording
status: untriaged
feature: presentation-safety
added: 2026-11-22
---

**Problem.** The approved-wording test records an Area's 'too small' notice at 13 event points, because the run-state scenarios it reuses lay their dashboard out at 1400 by 1000 px, so a font change that moves an Area's size across a power of ten fails it in 13 places with no change of wording

**Found on 2026-11-22** by the blind review of `PL-4G79`'s pull request. `_in_the_run_state_scenario` in `tests/integration/test_interface_wording.py` records the dashboard that each of `_ONE_STATE_SCENARIOS` leaves, and those scenarios build it at `_WINDOW_WIDTH_PX` by `_WINDOW_HEIGHT_PX` (1400 by 1000 px) in `tests/integration/simulation_view/simulation_view_support.py`. Thirteen event points therefore record "It needs at least ### by ### px; this Area is #### by ###." with "Too small for Parameters." or "Too small for Concentrations.". The digits are masked, but their count is kept, so a font that moves a size from 980 to 1010 px fails all thirteen. Resizing the recorded dashboard to 1400 by 4000 px before recording did not remove the notices (tried 2026-11-22), so the Areas' sizes come from the scenarios' Workspace rather than the window alone.

**Done when.** The event points record no Area size notice that the default points' window would not show, or the test records the notice's wording without its sizes.
