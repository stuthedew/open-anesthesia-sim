---
id: PL-RD3B
title: app/controller.py now holds the run's storage as well as the UI-to-core boundary, and they are separable
status: untriaged
added: 2026-09-04
---

**Problem.** `PL-D9WD` added `RecordedQuantity`, `RunHistory` and a rewritten
`HistoryWindow` to `app/controller.py`, which went from 678 to 930 lines. The
module's own docstring says what it is for — "the boundary between the UI and
the scientific core. Owns run/pause/reset state, applies user-facing settings
to the core, and exposes read-only `SimulationSnapshot`s" — and a columnar
store with a dyadic aggregate ladder over it is not that. Two things now live
in one file: the controller, and the run's recorded history.

**Why it matters.** The seam is already there rather than being one this item
would invent. `RunHistory` reads no simulation state, holds no setting, and
touches nothing in `core/`; it takes a `SimulationHistorySample` and answers
windows over what it was given. It has its own unit test file
(`tests/unit/test_run_history.py`) written without the controller, and its
own consumer (`app/chart_series.py`) that never touches the controller at
all. The controller's remaining use of it is four lines.

Three consequences, in order of consequence:

- Two items in the queue are about what a run *retains* and what a run can be
  *branched from* — `PL-011`'s retention policy and the scenario-branching
  pair `PL-WRKL` / `PL-RRWV`. All of them are work on the store, and all of
  them will be read as work on the controller for as long as the store lives
  inside it. `bin/docket concurrent` says so too: every item declaring
  `app/controller.py` collides with every other, whether or not they touch
  the same half.
- Reading the store means loading a file that is mostly about run/pause/reset
  and setting forwarding, and reading the controller means paging past a
  dyadic ladder. That is the cost `PL-WB0X` paid to remove from the view.
- The precedent is set: `PL-WB0X` already split the displayed-value
  formatters and the chart-series shaping out of `app/simulation_view.py` for
  exactly this reason, and it named the smaller modules as where such things
  belong.

Against that: it is a move rather than a change, so it buys no behavior and
carries the ordinary risk of a rename touching every importer. It is
maintainability work, not a defect, and nothing is wrong today.

**Where.** `src/anesthesia_sim/app/controller.py` — `RecordedQuantity`,
`RunHistory` and `HistoryWindow` out to `src/anesthesia_sim/app/run_history.py`,
with `SimulationHistorySample` moving with them, since it is the row the store
records and reads back. Importers: `app/chart_series.py`,
`app/simulation_view.py`, `tests/unit/test_run_history.py`,
`tests/unit/test_simulation_view.py`, `tests/integration/test_chart_patching.py`,
`tests/integration/test_controller.py`, `tests/integration/test_sevo_controller.py`.
`docs/MODEL.md`'s package map names every module and would gain a row.

**Done when.** The run's storage is its own module, `app/controller.py` is
back to the boundary its docstring describes, the package map names the new
module, and no behavior changed — the existing tests pass unmodified except
for their imports.
