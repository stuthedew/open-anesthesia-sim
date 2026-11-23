---
id: PL-PZSF
title: Fields and arguments that nothing reads in the display modules, and three docstrings that misstate what their functions raise or print, found by sorting the mutation survivors of PL-00Y5
status: untriaged
added: 2026-11-23
filed-pr: 2281
---

**Problem.** Fields and arguments that nothing reads in the display modules, and three docstrings that misstate what their functions raise or print, found by sorting the mutation survivors of PL-00Y5

**What happens.** Sorting the survivors of the 2026-11-23 whole mutation run (`PL-00Y5`) found these in modules a learner's display is built from. None changes a displayed value today.

1. Fields and state that nothing reads: `RunFrame.agent_id` and `RunFrame.elapsed_s` in `app/chart_frame.py` (`_run_frame` mutants 43 and 46), `HoverReading.quantity` in the same module (`nearest_wash_in_point` 38), and the saved `Preferences` that `PreferencesStore.save` keeps in `_loaded.preferences` in `app/preferences.py` (`save` 40).
2. Arguments that do nothing: `_captions` in `app/agent_cost.py` calls `.format(unit=..., agent=...)` on two captions that hold no field since `PL-RJN9`, so its `agent` argument is unused (`_captions` 3 to 6, `delivered_shown` 34). `_read_node` in `layout/serialization.py` passes the nouns "an Area" and "a split" to `_fields`, which shows a noun only for a value that is not an object, and `_read_node` has already refused one (7 mutants).
3. Code that no input reaches: the guard for an empty time axis in `chart_frame._run_preview` (39), the `continue` for an empty stretch in `chart_frame._nearest_wash_in_point` (8), and the joined list of several branch names in `dashboard_frame.trunk_reset_question`, since `MAX_DISPLAYED_RUNS` allows one branch (8, 9 and 29).
4. Docstrings that misstate their function: `chart_frame.percent_axis_ticks` says a 0.5% step prints "0.5, 1 and 1.5", where the code and its test print "1.0". `WashInStretch.__post_init__` raises `ValueError` when its instants and ratios differ in length, and its Raises section names only `SimulationConfigurationError`. `PreferencesStore.save` raises a plain `ValueError` from `_to_json`'s `allow_nan=False` for a hand-built `RefusedEntry` holding NaN, and its docstring does not list it.
5. Lines in `layout/model.py` that no input reaches, found by sorting that module's survivors later on 2026-11-23: the `() if squeezed else` guard in `_dragged`, with its docstring sentence about a split with no extent; the `given <= 0` test in `LayoutModel.split`; the `isinstance(split, Area)` `continue` in `edges`, which exists only to narrow the type for mypy; and the `NotInLayout` guards in `_node_at`, `_rect_at`, `_replaced` and `_split_at`, whose callers have already found the node. A guard kept for mypy, or kept so that a future caller is refused rather than sent on, is a reason to keep it, and a comment says so.
6. The whole-steps guard in `SimulationController._resume_point` in `app/controller.py`, `step_count * SIMULATION_STEP_S != fork.instant_s`, cannot fire: a fork's instant is a whole-second `CaseInstant` and the step is 1 s (3 unreachable mutants and 1 equivalent in the controller sort of 2026-11-23). Keep it only with a comment that says it guards a future step that is not 1 s.
7. Two branches in `app/controller.py` that no learner reaches: `_axis_spacing_s` returns 0 for an axis of zero width, and both callers then raise the spacing to at least 1 with `max(spacing_s, 1)` (mutants 21 and 22); and `preview_window`'s empty prediction is reached only through the public method, never from the chart (mutant 18, which `test_controller_preview.py` now checks). The two preview caches, `_preview_memo` and `_prediction_memo`, change only the cost of a preview, so no test of a result can see them switched off (`preview_settings` 8 and 54, `preview_window` 30 and 126). Keep them, and say in a comment that a test would have to count calls.

**What to do.** Remove each field, argument and branch that nothing reads or reaches, or say in a comment why it stays. Correct the three docstrings.
