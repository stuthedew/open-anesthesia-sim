---
id: PL-RD3B
title: app/controller.py holds the run's trace vocabulary and drawn window as well as the UI-to-core boundary, and they are separable
priority: P2
effort: M
status: ready
classes: refactor
feature: teachable-case
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_series.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, tests/integration/test_chart_patching.py, tests/integration/test_controller.py, docs/ARCHITECTURE.md, docs/MODEL.md
added: 2026-09-04
verify: uv run pytest -q tests/unit/test_simulation_view.py tests/integration/test_chart_patching.py && ! grep -q 'app.controller import' src/anesthesia_sim/app/chart_series.py
---

**Problem.** `app/controller.py` is 1 411 lines, of which the controller proper
is the last 1 052. The module docstring says what the file is for - "the boundary
between the UI and the scientific core. Owns run/pause/reset state, applies
user-facing settings to the core, and exposes read-only `SimulationSnapshot`s
for the view to render" - and 325 of those lines are neither that nor used by
it: they are the vocabulary a run's values are *addressed* by and the window a
frame *draws*, which `app/chart_series.py` and `app/control_timeline.py`
consume without touching the controller at all.

**Re-briefed 2026-09-14 under `PL-5328`.** The original was written on
2026-09-04 against `RunHistory`, `HistoryWindow` and `SimulationHistorySample`,
and `PL-2FM6` has since deleted all three along with the columnar store and its
dyadic aggregate ladder. The three queue items it cited as reasons - `PL-011`,
`PL-WRKL` and `PL-RRWV` - are all `dropped`. What survived is the argument: the
seam is a fact about the imports rather than one this item invents, and the
file keeps growing - 930 lines when the item was filed, 1 064 at the re-brief,
and 1 411 once `PL-B9PY` (`#567`) and `PL-J2TD` (`#568`) landed. What follows
is measured on `f692f51`.

**Why it matters.** The seam is already there. Measured against the tree, no
consumer of the drawn-run half needs the controller and no consumer of the
controller needs the drawn-run half:

| Importer | What it imports from `app/controller.py` |
| --- | --- |
| `app/chart_series.py` | `DrawnWindow`, `RecordedSeries` - and nothing else |
| `app/control_timeline.py` | `ControlChange`, `ControlInput` - and nothing else |
| `app/main.py` | `SimulationController` - and nothing else |
| `app/simulation_view.py` | all of it |

So three of the four importers already use one half or the other. Only the
view, which renders everything, wants the whole module.

Three consequences, in order of consequence:

- **The branched-run milestone is entirely work on this half.** v0.5.0's
  `PL-J2TD` (open a run at a keyframe), `PL-TFX5` (fork a run), `PL-Z3W6`
  (assert element-wise reproduction) and `PL-8PSW` (overlay two branches) all
  operate on how a run is addressed and drawn, and every one of them will read
  as work on the controller for as long as that vocabulary lives inside it.
  `bin/docket concurrent` says the same: seven open items declare
  `app/controller.py`, so each collides with all the others whether or not
  they touch the same half.
- **`PL-CNCF` is a `perf` item on precisely the extracted half** -
  `controller.drawn_window` costing 6.2 ms a frame, about eighty times the
  simulation at 1x - and it is filed against the controller because that is
  where the code sits.
- **Reading either half means paging past the other.** That is the cost
  `PL-WB0X` already paid to remove from `app/simulation_view.py`, splitting the
  displayed-value formatters and the chart-series shaping into smaller modules
  for exactly this reason, and naming those modules as where such things
  belong. The precedent is set; this is the same move one file over.

Against that: it is a move rather than a change, so it buys no behavior and
carries the ordinary risk of touching every importer. It is maintainability
work, not a defect, and nothing is wrong today.

**Where.** Out of `src/anesthesia_sim/app/controller.py`, the drawn-run half -
lines 126 to 359 on `f692f51`, unmoved by either of the two milestone items
that landed after the re-brief:

| Symbol | Line | What it is |
| --- | --- | --- |
| `RecordedQuantity` | 126 | which quantity a trace holds |
| `COMPARTMENT_QUANTITIES` | 162 | the six compartment quantities |
| `COMPARTMENT_STATE_INDEX` | 191 | quantity to state-vector index |
| `RecordedSeries` | 204 | one trace's address: substance and quantity |
| `DrawnWindow` | 230 | the states one frame draws |

Proposed destination `src/anesthesia_sim/app/run_series.py`, which sits beside
`app/chart_series.py` the way the two divide: what a trace *is* against how it
is drawn in Flet. The name is the implementing session's to confirm -
`docs/ARCHITECTURE.md` § "Where new code belongs" governs it, and
`.claude/rules/where-new-code-goes.md` requires one existing instance be read
end to end first. **Not `run_history.py`**, which the original named: there is
no history to move, and a module named for the store `PL-2FM6` deleted is how
a later session reintroduces it.

**The control-input half may ride along**, at the implementing session's
discretion: `ControlInput` (35), `CONTROL_INPUT_UNITS` (89) and `ControlChange`
(98) are lines 35 to 125, the same argument and the same clean consumer in
`app/control_timeline.py`. Taking both leaves `app/controller.py` at about 1 086
lines; taking the drawn-run half alone leaves about 1 177. Two passes over one
set of importers costs more than one, so prefer both - but either is a complete
answer to this item.

What stays: `SimulationSnapshot` (360), `ResumePoint` (502, added by
`PL-J2TD`) and `SimulationController` (542), which are the boundary the
docstring describes. `SimulationController` alone is now 870 lines.

Importers to update: `app/chart_series.py`, `app/simulation_view.py`,
`tests/unit/test_simulation_view.py`, `tests/integration/test_chart_patching.py`,
`tests/integration/test_controller.py`, `tests/integration/test_sevo_controller.py`.
`docs/ARCHITECTURE.md`'s package map gains a row - `tools/doc_check.py`'s
`check_package_maps` holds that tree to the files on disk in both directions,
so `make doc-check` fails until it does. `docs/MODEL.md` § "What a drawn window is" (headed *What a recorded sample
is* until `PL-27H0` renamed it) cites `app/controller.py`'s `RecordedQuantity` by module and needs
re-pointing; that section has a second, separate problem, which is `PL-27H0`.

**Sequencing: satisfied 2026-09-14.** `PL-B9PY` (decompose `SimulationView` so
two runs render) was in flight when this was re-briefed and has since merged as
`#567`, so there is nothing left to wait for and no branch to resolve against.
Measured after it landed, the importer list above is **unchanged** - the
decomposition stayed inside `app/simulation_view.py` and added no module to
`app/` - so this item's scope is exactly what it was. The note is kept because
it records why the item was left `ready` rather than blocked: a shared file is a
sequencing note rather than a refusal (`PL-VRMK`).

**Done when.** The drawn-run vocabulary is its own module, `app/chart_series.py`
imports it without importing `app/controller.py` at all, `app/controller.py` is
back to the boundary its docstring describes, the package map names the new
module, `docs/MODEL.md`'s citation points at it, and no behavior changed - the
existing tests pass with no change but their imports.

**Blocked on `PL-G59B`, 2026-09-14** (project owner, in the session that cut
v0.4.25). Not for anything in this brief: `ROADMAP.md` § "v0.4.26 - the
interface moves to Qt" records that "nothing new is built in
`app/simulation_view.py` or `app/chart_series.py` before this port", and this
item's `touches` names both. Its durable half is in `app/controller.py`, so it
could be narrowed to that and started now; the owner chose to hold it whole
rather than split it, because the split's *point* is where the drawn-run
vocabulary lands, and that module is the one the chart port rewrites. The
field encodes the roadmap's own freeze so `bin/docket next` stops offering it
as the product lane's pick.

**Promoted to `ready`, 2026-09-14**, `PL-G59B` having closed. The Qt chart reads `controller.drawn_window` through `app/chart_frame.py`, so the split this item makes now has two readers to keep working: `chart_frame.py` for the Qt chart and `chart_series.py` for the Flet one until `PL-7SVX`.
