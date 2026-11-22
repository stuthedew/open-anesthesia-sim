---
id: PL-P6TK
title: The approved-wording test records an Area's 'too small' notice at 13 event points, because the run-state scenarios it reuses lay their dashboard out at 1400 by 1000 px, so a font change that moves an Area's size across a power of ten fails it in 13 places with no change of wording
priority: P2
effort: S
status: done
classes: defect, test
feature: presentation-safety
touches: tests/integration/test_interface_wording.py, tests/integration/approved_interface_strings.json
added: 2026-11-22
closed: 2026-11-22
pr: 2227
tests: tests/integration/test_interface_wording.py::test_every_string_the_view_shows_is_on_the_approved_list
---

**Problem.** The approved-wording test records an Area's 'too small' notice at 13 event points, because the run-state scenarios it reuses lay their dashboard out at 1400 by 1000 px, so a font change that moves an Area's size across a power of ten fails it in 13 places with no change of wording

**Found on 2026-11-22** by the blind review of `PL-4G79`'s pull request. `_in_the_run_state_scenario` in `tests/integration/test_interface_wording.py` records the dashboard that each of `_ONE_STATE_SCENARIOS` leaves, and those scenarios build it at `_WINDOW_WIDTH_PX` by `_WINDOW_HEIGHT_PX` (1400 by 1000 px) in `tests/integration/simulation_view/simulation_view_support.py`. Thirteen event points therefore record "It needs at least ### by ### px; this Area is #### by ###." with "Too small for Parameters." or "Too small for Concentrations.". The digits are masked, but their count is kept, so a font that moves a size from 980 to 1010 px fails all thirteen. Resizing the recorded dashboard to 1400 by 4000 px before recording did not remove the notices (tried 2026-11-22), so the Areas' sizes come from the scenarios' Workspace rather than the window alone.

**Done when.** The event points record no Area size notice that the default points' window would not show, or the test records the notice's wording without its sizes.

**Fixed on 2026-11-22, in the same pull request.** CI then failed on exactly this: its font found the Parameters Area too small where the container's found the concentration chart's Area too small, in three event points. `_strings_but_area_notices` in `tests/integration/test_interface_wording.py` leaves the title and body of every `AreaNotice` out of the two kinds of point that reuse a dashboard built in the run-state tests' window, the run-state scenarios and the compared runs with marks. A notice is about the layout and not about the run's state. No default point shows one, so the approved list holds no Area notice now, as it held none before `PL-4G79`.

**Generator check.** A follow-on of `PL-4G79` in the same pull request, found by its review, so it is not a fix that failed to hold. The misread fact is that a string recorded from a dashboard depends only on the run's state, when an Area notice depends on the layout and the fonts. `PL-K4CZ`, which measured layout tests under both fonts, met the same font difference, and no head names it.
