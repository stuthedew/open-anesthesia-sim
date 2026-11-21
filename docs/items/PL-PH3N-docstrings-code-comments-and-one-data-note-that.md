---
id: PL-PH3N
title: Docstrings, code comments and one data note that the check of docs/INTERFACE.md against the code found stale
priority: P3
effort: M
status: done
classes: defect, docs
feature: interface-matches-its-spec
touches: .claude/rules/ui-color.md, .claude/rules/where-new-code-goes.md, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/control_record.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/playback.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/view_contract.py, src/anesthesia_sim/core/rounding.py, src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/data/machines/reference_circle_system.json, src/anesthesia_sim/layout/model.py, src/anesthesia_sim/layout/run_identity.py, src/anesthesia_sim/layout/store.py, tests/integration/controller/test_controller_branching.py, tests/integration/simulation_view/test_simulation_view_foreground.py, tests/unit/test_bookmarks.py, tests/unit/test_formatting.py
added: 2026-11-21
closed: 2026-11-21
pr: 2200
payoff: A developer reading these docstrings and comments finds what the code does today
verify: ! grep -qF 'There are five possible results' src/anesthesia_sim/app/controller.py
---

**Problem.** Docstrings, code comments and one data note that the check of docs/INTERFACE.md against the code found stale

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). Each entry below is a docstring, a comment or a data note that the check found to disagree with the code or with the document it names. None changes what the program does. A mention of `docs/MODEL.md` that means `docs/INTERFACE.md` is listed in `PL-10BC` (the re-pointing of those mentions) and not here.

In `src/anesthesia_sim/app/`:

1. `controller.py`: `SimulationSnapshot.bookmark_standings` says "five possible results". `add_mac_target` describes a "direction". `advance` says a setting is applied "unconditionally", and `playback.py` repeats it. `begin_control_adjustment` says a key press on a slider "becomes an adjustment of its own" (`PL-0T2H` decides which is right). `BranchedCase.fork_points_s` says "every setting change the model was actually stepped under", and a keyframe is listed as soon as a setting is changed.
2. `bookmarks.py`: the docstring of `HEIGHT_BAND` and a comment in `tests/unit/test_bookmarks.py` say "965 times in its tenth minute". `_time_bookmark_standing` gives a reason that no longer applies.
3. `run_view.py` and `dashboard_frame.py`: `RunView._handle_reset`, `trunk_reset_question` and one more docstring point at § "Agent-change behavior" for the Reset question, which is under § "Discarding a run, and the questions that guard it". `status_word` says "The two cannot both arise from one run" (`PL-3DHK`).
4. `control_record.py`: the docstring of `ControlChange`.
5. `qt_chart.py` and `chart_frame.py`: the docstrings of `WashInChart`, `WashInChart.draw`, `_drawn_wash_in` and `wash_in_state`, and a comment in `qt_chart.py` that says "fastest curve".
6. `formatting.py`: the comment above `CONCENTRATION_DISPLAY_DECIMALS` still gives the between-patient spread as the reason for two decimals, which `PL-W51N` (what limits each displayed precision) removed. The comment above `COMPARTMENT_AMOUNT_SIGNIFICANT_FIGURES` says "about a litre", and two docstrings say "six figures". `format_mac_awake_reference` and `mac_awake_caption` say "both are named".
7. `layout/model.py`: `LayoutModel.resize` describes Blender's behaviour as this project's. The module docstrings of `view_contract.py` and `area_layout.py`, and the docstrings of `SimulationView._build_page` and `layout_container`.
8. `qt_widgets.py` and `theme.py`: `declare_application_colours` says "all 24" requirements, and there are 27. The comment above `WARNING` lists fewer uses than the code has.
9. `layout/store.py`: the module docstring gives the Linux directory as `~/.local/share/<App>`, and Qt adds the organization name. The docstring and the notice in `_load` say "the second save" would overwrite a previous file that a newer build wrote. `save` copies the current file over it whenever a current file exists, so check whether the first save does.

In `src/anesthesia_sim/core/`:

10. `run_definition.py`: the module docstring's "70 KiB" and "3.16 GB", the `opened_at_s` entry of `RunDefinition.__init__` ("the fork itself"), and `DisplayState`.
11. `tissue.py`: a refusal message says the perfusion fractions are checked "only when it is built", and they are also checked when a tissue group is replaced. A message is on screen, so this one needs its test. `PL-XXXJ` (three refusal messages that pointed at the wrong section) corrected this message and the docstring beside it on pull request #2190, with a test of the whole message, so this entry needs no more work once #2190 has merged.

In `src/anesthesia_sim/data/`:

12. `machines/reference_circle_system.json`: the `provenance_gap` note.

In `tests/`:

13. `tests/unit/test_formatting.py`: two docstrings that give the removed precision reason.
14. `tests/reference/test_coupled_dynamics.py`: the comment above `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS`.
15. `tests/reference/test_mac_awake_washout_figures.py`: the module docstring names `docs/MODEL.md` and "six figures".
16. `tests/reference/test_canonical_evaluation.py`: the module docstring says "six decimals of a litre", and the docstring of `test_a_branch_reproduces_its_parent_at_every_instant_they_share`.
17. `tests/integration/simulation_view/test_simulation_view_foreground.py`: `FOREGROUND_NOT_DECLARED["QScrollBar"]` says `PL-KRZW` is open.

In `.claude/rules/`:

18. `ui-color.md` says "exactly one declared exception". `where-new-code-goes.md` says "which of the three test trees", and `docs/ARCHITECTURE.md` § "Tests (`tests/`)" describes four directories.

The reports that hold the quoted text and the evidence for each entry are summarized in `PL-5FMC`'s brief, one paragraph for each section of the documents.

**Why it matters.** A developer reads a docstring before the document, and each of these states something the code does not do.

**Done when.** Each entry is corrected or shown to be right, entries 10 to 12 go through the review that `core/` and `data/` changes need, and entry 11's message has a test.

**Corrected 2026-11-21.** Each entry was checked again against the code at `f644db85` before it was edited, and the reports of `PL-5FMC` gave the evidence. What each entry needed:

1. `SimulationSnapshot.bookmark_standings` now says six results, which is the number of `MarkStanding` members. `add_mac_target` names no direction. `advance` and `app/playback.py` say the setters accept a change while a run is paused, because a stopped run refuses one (`PL-3B34`). `begin_control_adjustment` and `ControlChange` say that a key press, a wheel notch or a track click joins the open adjustment on the same control, which is what `_record_in_timeline` does today, and point at `PL-0T2H`, which changes that. `fork_points_s` says a keyframe is listed from the moment a change is made.
2. `HEIGHT_BAND` lives in `core/rounding.py`, so its docstring was corrected there: 965 halts in ten minutes, as `PL-QVBR` records. The comment in `tests/unit/test_bookmarks.py` matches. `_time_bookmark_standing` and `test_the_cap_answers_for_a_run_standing_at_it_that_then_failed` now say that a run at the cap refuses every setting, so its error came from something other than a step or a setting.
3. Four pointers name § "Discarding a run, and the questions that guard it": `RunView._handle_reset`, `trunk_reset_question`, `SimulationController.change_agent`'s docstring and the module docstring of `layout/run_identity.py`. `status_word` was already corrected by `PL-3DHK`.
4. `ControlChange`: see entry 1. Its example is now eight arrow-key presses, since a drag records one change (`PL-5B1N`).
5. `WashInChart`, `WashInChart.draw`, `_drawn_wash_in` and the module docstring of `app/chart_frame.py` say that the F_A/F_I plot keeps its own window and shares the compartment chart's frame only while both show the same window. `wash_in_state` says that the caption and the trace come from two evaluations that agree to within rounding. The legend comment says "fastest patient trace".
6. The comment above `CONCENTRATION_DISPLAY_DECIMALS` and the module docstring of `app/formatting.py` give legibility as the reason for two decimals (`PL-W51N`). The amount comment says "several litres": desflurane's fat holds 6.7 L at 24 h. `format_agent_residual` says six decimal places, as the `.6e` format prints. `format_mac_awake_reference` and `mac_awake_caption` say that the divisor is on the 1 MAC line beside the label.
7. `LayoutModel.resize` records that `PL-RQT1` Q3 read the Manual wrongly and that `PL-GJFL` holds the decision. `app/view_contract.py` names the provenance entry by its whole bold title and states that splitting, swapping and pinning are built. `app/area_layout.py` names `app/workspace_tabs.py`. `SimulationView._build_page` and `layout_container` say that the controls, the marks and the branch control are Views, and that a reader can close an Area.
8. `declare_application_colours` says 27 requirements, measured on the panel, the page, the three agent fills and the filled button, which `tools/contrast_check.py` printed. The comment above `WARNING` lists the uses that `docs/INTERFACE.md` now lists.
9. `layout/store.py` gives the Linux path PySide6 returns, `~/.local/share/<Org>/<App>`, rerun on 2026-11-21, and leaves macOS to `PL-RH43`. `save` copies the current file over the previous generation whenever a current file exists, so the docstring and the notice in `_load` now say "the first save".
10. `core/run_definition.py` gives the re-measured 1.6 MiB and 3.16 GiB from `PL-T691`, and `opened_at_s` names the keyframe before the fork (`PL-ZR49`). `DisplayState`'s pointer to `docs/MODEL.md` is in `PL-10BC`, which re-points every such mention, and is left to it.
11. Done by `PL-XXXJ` on pull request #2190.
12. The `provenance_gap` note of `data/machines/reference_circle_system.json` says that `docs/machine-abstraction.md` lists only the range under (b8) and says the two minimums are not fields.
13. The two docstrings in `tests/unit/test_formatting.py` give legibility as the reason, and keep their assertions.
14. to 16. Three of these are tests under `tests/reference/`, whose existing lines wait on the project owner's read when edited. They move to the pull request for `PL-7M65`, which edits `tests/reference/test_mac_awake_washout_figures.py` anyway: the comment above `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS` with the figures rerun on 2026-11-21 (8e-9 counts, a largest pairwise differential of 2.06e-14, a smallest nonzero true gap of 1.12e-15, over 1 485 000 pairs), the module docstring of `test_mac_awake_washout_figures.py`, and the module docstring of `test_canonical_evaluation.py` (the accounting View shows the totals to 0.1 L). The docstring of `test_a_branch_reproduces_its_parent_at_every_instant_they_share` is in `tests/integration/` and is corrected here.
17. `FOREGROUND_NOT_DECLARED["QScrollBar"]` says that `PL-KRZW` is decided.
18. `.claude/rules/ui-color.md` names two declared disabled colours, the transport button's label and a header menu's unavailable entry. `.claude/rules/where-new-code-goes.md` says four test trees.

**Closed 2026-11-21.** Every entry above is corrected on this branch except entry 10, which `PL-10BC` owns, and entries 14 to 16, whose reference-test docstrings ride `PL-7M65`'s pull request because an edit under `tests/reference/` waits for the owner's read. Only docstrings, comments, one data note and one notice string change, so no displayed value moves. The notice string is the store's refusal to save when a newer build wrote the previous file: it now says "the first save from this build would overwrite" it, which is what `WorkspaceStore` does, and no test or document quotes it. Documents checked against the changed files, from `python3 tools/doc_check.py candidates --base origin/main`: `docs/ARCHITECTURE.md` (the package map and § "User state: the saved Workspaces"), `docs/INTERFACE.md` (the lines naming `run_identity.py`, `test_simulation_view_foreground.py` and `test_formatting.py`), `docs/MODEL.md` (the line naming `test_controller_branching.py`), `docs/apparatus.md`, `.claude/rules/ui-color.md` and `.claude/rules/dead-ends-apparatus.md`. None states something the corrected text contradicts.

**Generator check.** One-off. The fact misread is what each function and rule now does: the changes that moved the code left these docstrings, comments and two rule files as they were. Whether prose still matches behaviour is judgment that no check can make, and `PL-5FMC`'s sweep is the session that made it.
