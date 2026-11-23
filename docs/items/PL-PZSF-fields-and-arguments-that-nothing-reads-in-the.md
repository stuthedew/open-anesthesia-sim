---
id: PL-PZSF
title: Fields and arguments that nothing reads in the display modules, and three docstrings that misstate what their functions raise or print, found by sorting the mutation survivors of PL-00Y5
priority: P3
effort: M
status: done
classes: refactor, defect
feature: tests-detect-wrong-values
touches: src/anesthesia_sim/app/agent_cost.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/preferences.py, src/anesthesia_sim/layout/model.py, src/anesthesia_sim/layout/serialization.py, docs/items/PL-VW5V-the-area-layout-adapter-walks-a-split-s-path.md, docs/items/PL-WZDM-both-callers-of-the-controller-s-axis-spacing-s.md, docs/items/PL-2890-the-agent-cost-panel-s-two-caption-constants.md, docs/items/PL-0DRD-runframe-agent-id-and-hoverreading-quantity-in.md
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
closed: 2026-11-23
pr: 2306
filed-pr: 2281
payoff: the display modules hold no field nobody reads and no docstring that misstates what its function raises
verify: ! grep -qF '0.5, 1 and 1.5' src/anesthesia_sim/app/chart_frame.py
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

**Why it matters.** A field that nothing reads, or a docstring that misstates what a function raises, leads the next developer to rely on something that is not true. None changes a displayed value today.

**Done when.** Each field, argument and branch in the list is removed or carries a comment saying why it stays, the three docstrings match their functions, and the mutation survivors listed are killed or recorded as equivalent.

**Generator check.** A one-off: the remainder of one mutation sort, not a misread fact.

**Done 2026-11-23.** Removed: the write of `PreferencesStore._loaded` at the end of `save`, which is already set and writable when a save succeeds, and which nothing reads afterwards; the `agent` argument of `_captions` in `app/agent_cost.py`, with the `.format` call, since both captions are plain strings with no fields (the caption text is unchanged); the empty-axis guard in `chart_frame._run_preview`, with a comment that says why a preview's window always ends after the reach; the `() if squeezed else` guard in `layout/model.py`'s `_dragged`, with its docstring sentence; and the `given <= 0` test in `LayoutModel.split`, with a comment that says why only the kept part can round to zero. `LayoutModel.edges` now calls `_split_at` instead of skipping an Area, so a broken tree raises `NotInLayout` instead of dropping a border. `_read_node` in `layout/serialization.py` checks an object's keys through a new `_exact_fields`, which takes no noun, and its messages are unchanged.

Kept, each with a comment that says why: `RunFrame.agent_id` and `HoverReading.quantity`, which tests read; `RunFrame.elapsed_s`, which `dashboard_frame.held_window_notice` now reads (`PL-Z7LY`, merged after the mutation run); the `continue` in `_nearest_wash_in_point`, for the type checker; the joins of several branch names in `trunk_reset_question`, for a higher `MAX_DISPLAYED_RUNS`; the `NotInLayout` guards in `_node_at`, `_rect_at`, `_split_at` and `_replaced`; the whole-steps check in `SimulationController._resume_point`, for a step that is not 1 s; the zero spacing in `_axis_spacing_s`, whose docstring now says the chart never asks for a zero-width axis; and the two preview caches. The mutation survivors on these kept lines are therefore recorded here as unreachable or as equivalent, each for the reason its comment gives. The survivors on the removed lines went with them.

Docstrings corrected: `percent_axis_ticks` now says a 0.5% step prints 0.0, 0.5, 1.0 and 1.5; `WashInStretch` lists the `ValueError` for instants and ratios of unequal length; and `PreferencesStore.save` lists the `ValueError` for a number that is not finite or an entry that holds itself, and the `TypeError` for a value JSON cannot write.

Documents checked: `docs/ARCHITECTURE.md` § on the preferences store (says when `PreferencesStore.save` writes, which is unchanged) and its two mentions of `_resume_point` (which still rejects a fork on the supported run length); and `docs/INTERFACE.md` § on the agent cost panel's captions, whose wording is unchanged. `docs/MODEL.md`, `docs/VERIFICATION.md` and `docs/PARAMETERS.md` name none of the changed code.

Found while doing it and filed: `PL-VW5V` (a second copy of the model's path walk in `app/area_layout.py`), `PL-WZDM` (the one-second minimum spacing applied twice outside `_axis_spacing_s`), `PL-2890` (two caption constants still named templates) and `PL-0DRD` (two fields that only tests read). A fifth candidate, that no test reaches the refusal of a cut whose kept part rounds to zero, was dropped: `tests/unit/test_layout_model.py::test_a_cut_outside_the_area_is_refused_and_the_layout_is_unchanged` already cuts at `5e-324` and checks that refusal.

**Blind review, 2026-11-23.** One pass. It found nothing.
