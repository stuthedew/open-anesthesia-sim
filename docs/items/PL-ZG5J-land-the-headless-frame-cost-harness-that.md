---
id: PL-ZG5J
title: Land the headless frame-cost harness that measured all of the above, so the simulation-versus-UI split can be re-measured rather than re-derived
priority: P3
effort: M
status: done
classes: infra, perf
feature: frame-cost-harness
touches: tests/benchmarks/frame_cost.py, tests/benchmarks/test_frame_cost.py, docs/ARCHITECTURE.md, ROADMAP.md
added: 2026-09-08
closed: 2026-09-19
verify: grep -q 'def test_every_stage_is_timed_and_finite' tests/benchmarks/test_frame_cost.py
---

**Problem.** `PL-YSZN`, `PL-KP7H`, `PL-R2YM` and `PL-SQJ1` were all measured on
one throwaway harness: a real `SimulationController` and a real
`SimulationView` mounted on a real `flet.messaging.session.Session` whose
connection serializes each outbound message exactly as the WebSocket transport
does, driven frame by frame with `perf_counter` around each of
`controller.advance`, `_refresh_view` and `page.update()`. It answers "is this
the simulation or the interface" in about thirty seconds and needs no client,
no display and no browser.

`PL-0VM7`, `PL-Q197` and `PL-R460` each built something equivalent and each
discarded it; this is the fourth time the same scaffolding has been written.
`CLAUDE.md` asks for work that recurs to be moved out of the model.

**What is unresolved is where it goes.** New `tools/` scripts are required to
be standard-library only, so a hook or a bare checkout can run them without
the project virtualenv, and this one imports `PySide6`, `pyqtgraph` and the
package itself - `flet`, `flet_charts` and `msgpack` before the Qt port. It is also not a check: it produces timings, which are
a judgment rather than a pass/fail, and `CLAUDE.md` is explicit that a check
which cannot decide is worse than none. So it is a third thing — a measurement
script — and the project has no home for one.

**Why it matters.** Modest. Nothing is blocked on it, and the argument against
is that the project's precedent is to measure ad hoc and record the numbers in
the item, which does preserve the finding. The argument for is that the
*method* is what gets re-derived, and it is subtle enough to get wrong: the
serializing connection is what puts the session into the state an incremental
patch is computed against, and a stand-in that skipped it would answer a
question the running app never asks.

**Decision needed.** Whether a measurement script has a home in this
repository — `tests/benchmarks/`, a `bench/` tree, or nowhere — and whether the
stdlib-only rule is a property of `tools/` or of anything runnable.

**First step.** Answer that, or close this as declined and record in
`docs/WORKING_NOTES.md` that measuring ad hoc is deliberate.

**Done when.** The question in "Decision needed" is answered and acted on:
either the harness lands somewhere named, with the serializing connection and
the three-stage split intact and a note saying what it measures and what it does
not, or this is `dropped` and `docs/WORKING_NOTES.md` records that measuring ad
hoc and keeping the numbers in the item is deliberate.

**The port is done, so the toolkit question is settled and this is unblocked**
(`PL-V1F4`, 2026-09-19). This paragraph used to say to defer the harness and
build the Qt version once under `PL-YCWZ`. `PL-YCWZ` closed on 2026-09-15 with
the headless Qt rendering tests, `PL-QXSB`'s decision to leave Flet has been
carried out, and `tools/import_boundary_check.py` now refuses `flet` and
`flet_charts` in every module under `src/`. So the deferral's premise - do not
build a Flet harness the port will throw away - was satisfied rather than
refuted, and what was left behind was a first step pointing at finished work.
Nothing is waiting on anything: the decision above is the only thing between
this item and a harness.

**The method survives the port; its third stage now measures the paint.** Under
Flet the stages were `controller.advance`, `_refresh_view` and `page.update()`,
and the serializing connection was the subtle part - it put the session into the
state an incremental patch is computed against. Qt serializes nothing, and what
sits in that position is the *paint*. `ChartPlot.draw` is `setData`, `setPos`
and `setTicks` throughout: it schedules a repaint and rasterizes nothing, so
`_refresh_view` returns before the frame has been drawn and the frame is
complete only once the event loop dispatches the paint event. The three stages
under Qt are `controller.advance(SIMULATION_STEP_S)`,
`SimulationView.present(False)` and `QApplication.processEvents()`, and a
harness that timed the first two would report the interface 45% low, in the
flattering direction. Measured 2026-09-19 in the web container, one run warmed
to an hour of simulated time, 600 steps per frame at 300x against the 200 ms
`RENDER_INTERVAL_S` budget, medians over 20 frames: `advance` 14.9 ms,
`present` 18.8 ms, `processEvents` 15.5 ms - so the interface costs 34.3 ms and
the two-stage reading of it is 18.8 ms. A second `processEvents` immediately
after the first costs 0.10 ms, which is the control: the 15.5 ms is the paint
that first call dispatched, not fixed event-loop overhead. Getting this wrong
is the same class of error the serializing connection existed to prevent, which
is the argument for writing the method down rather than re-deriving it a fifth
time.

**What it costs to build now: 42 lines, no new dependency, about 3 seconds to
run.** The scaffolding is already in the tree.
`tests/integration/test_qt_rendering.py`'s `dashboard` fixture builds a real
`SimulationController`, advances it, mounts a real `SimulationView` at a fixed
size, shows it and presents one frame - every line the harness needs before its
first `perf_counter` - and `tests/conftest.py` supplies the `offscreen`
platform. The numbers above came off 42 non-blank, non-comment lines written
against that fixture's shape. One environment fact belongs with the decision:
`tests/conftest.py` sets `QT_QPA_PLATFORM` for the test tree only, so a script
run outside pytest must set it itself or `QApplication([])` aborts on the
missing `xcb` plugin - measured the same day, and an argument for the test tree
over a `bench/` one rather than a decision on its own.

**Answered and landed, 2026-09-19: `tests/benchmarks/frame_cost.py`, and the
standard-library rule is a property of `tools/` rather than of anything
runnable.**

The second half of the question was already decided in the tree and needed no
new judgment. `tests/unit/test_tools_portability.py` holds the rule by
*directory*, and says why in its own docstring: "Two directories qualify, for
one reason. `tools/` is invoked by `make check` and CI; `.claude/hooks/` is
invoked by Claude Code ... Neither goes through the project virtualenv." The
promise is about how a file is invoked, not about its being runnable. A harness
importing `PySide6` and the package itself can only ever run inside the
virtualenv, so it is outside that set and needs no exemption from it - and
nothing in `CLAUDE.md` had to change, its sentence being scoped to "new tools"
already.

`tests/benchmarks/` over a `bench/` tree, because the test tree already carries
everything this needs and a new top-level tree would re-declare all of it:
`tests/conftest.py` selects the `offscreen` platform;
`tools/workflow_paths_check.py` puts both files on the product side of the lane
boundary from their imports, with no `docket.toml` edit;
`tests/integration/test_qt_rendering.py` is the instance the setup copies; and
pytest collects nothing whose name does not begin `test_`, so the harness
itself stays out of `make check` while sitting beside the suite that keeps it
alive. What a `bench/` tree would have bought - "this is not a test" stated by
the path - the module docstring states in a sentence.

**What landed.** `uv run python tests/benchmarks/frame_cost.py`, about three
seconds, no new dependency. Steps per frame are derived from
`SIMULATION_STEP_S`, `SIMULATION_TICK_INTERVAL_S` and `RENDER_INTERVAL_S`
rather than written in, so a cadence change moves the measurement with it, and
the rate is validated through `app/playback.py`'s own ladder. Two
configurations are refused rather than measured: a rate the interface does not
offer, and a run whose elapsed simulated time does not match the steps asked
for - which is what a halted or capped controller leaves, since `advance` then
returns immediately and would report the simulation as free.

Measured on this container at the defaults, medians over three runs: `advance`
12.0 ms, `present` 15.3 ms, `processEvents` 13.1 ms, so the interface costs
28.4 ms of a 40.4 ms frame against the 200 ms budget, and a two-stage harness
would have reported the interface at 15.3 ms - 46% low, in the flattering
direction. The control, a second `processEvents`, costs 0.08 ms. That
reproduces the 2026-09-19 throwaway reading above within the spread between
runs, which is the point: the numbers differ by the container, the split does
not.

`tests/benchmarks/test_frame_cost.py` is the decidable half - that the harness
still runs and still reports the stages it names - and asserts nothing about a
duration, since a threshold would measure the runner rather than the code. It
runs at 1x over a 30 s warm-up and costs the suite about a second.

`docs/ARCHITECTURE.md` § "Tests (`tests/`)" gains the fourth tree, which is
where `.claude/rules/where-new-code-goes.md` sends a session that asks the same
question again. `docs/WORKING_NOTES.md` is deliberately untouched: the stale
frame-cost prose in it is `PL-4HKS`'s, the other half of `feature:
frame-cost-harness`, and that item now names the command that supplies its
numbers.
