---
id: PL-PH3N
title: Docstrings, code comments and one data note that the check of docs/INTERFACE.md against the code found stale
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
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
11. `tissue.py`: a refusal message says the perfusion fractions are checked "only when it is built", and they are also checked when a tissue group is replaced. A message is on screen, so this one needs its test.

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
