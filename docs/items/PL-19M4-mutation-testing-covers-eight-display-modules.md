---
id: PL-19M4
title: Mutation testing covers eight display modules that pyproject.toml names by hand, and no Qt-free module added or left out since: app/agent_cost.py, app/compartment_schematic.py, app/bookmarks.py, app/playback.py and app/controller.py build values a learner sees and are in no mutation run, and a hand probe of 14 one-line changes on 2026-11-11 left three uncaught
status: untriaged
added: 2026-11-11
---

**Problem.** Mutation testing covers eight display modules that pyproject.toml names by hand, and no Qt-free module added or left out since: app/agent_cost.py, app/compartment_schematic.py, app/bookmarks.py, app/playback.py and app/controller.py build values a learner sees and are in no mutation run, and a hand probe of 14 one-line changes on 2026-11-11 left three uncaught

**What happens.** `[tool.mutmut] only_mutate` in `pyproject.toml` lists `core/*` and eight files under `app/`. `docs/mutation-testing.md` calls those eight "the display modules" and says the mutation run leaves out the Qt widget modules. These modules import no Qt, build a value or a state that a learner sees, and are not in the list: `app/agent_cost.py` (added 2026-11-02), `app/compartment_schematic.py` (added 2026-11-01), `app/bookmarks.py`, `app/playback.py`, `app/controller.py`, `app/display_units.py`, `app/unconditional_set.py`, `app/control_record.py`, `app/compartment_selection.py`, `app/view_registry.py` and every module under `layout/`. A branch that changes one of them passes `bin/docket verify`'s mutation check with nothing measured.

**Evidence, 2026-11-11, at `e084968ac`.** A hand probe made 14 one-line changes, one at a time, and ran the test files that import the changed module with `uv run pytest -q -x -n 4`. Eleven failed a test. Three passed every test:

1. `app/bookmarks.py`, `MacTarget._side_of`: `if reading < height - band:` changed to `<=`. Tests run: `tests/unit/test_bookmarks.py`, `tests/integration/test_controller.py`, `tests/unit/test_chart_frame.py` (453 passed). The docstring says the band includes its edges, and no test places a reading exactly on the lower edge.
2. The same function: `if reading > height + band:` changed to `>=` (453 passed). No test places a reading exactly on the upper edge.
3. `app/controller.py`: `if horizon_s <= reached_s:` changed to `<`, in the method that returns an empty `DrawnWindow`. Tests run: `tests/integration/test_controller.py`, `tests/integration/test_sevo_controller.py`, `tests/unit/test_chart_frame.py`, `tests/unit/test_wash_in.py`, `tests/integration/test_qt_chart.py` (415 passed). This one may make no observable difference; check it against the whole suite before writing a test.

The probe ran neither the whole suite nor mutmut, so it is a sample and not a kill rate.

**Recommendation.** State the rule once and derive the list from it: every module under `app/` and `layout/` that imports neither `PySide6` nor `pyqtgraph` is mutated, and a test fails when a module that meets the rule is missing from `only_mutate`. `app/controller.py`'s tests are in `tests/integration/`, which the mutation run does not use, so decide for that module whether to move its Qt-free tests to `tests/unit/` or to leave it out by name with the reason.
