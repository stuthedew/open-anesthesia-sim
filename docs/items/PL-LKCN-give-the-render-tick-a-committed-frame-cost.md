---
id: PL-LKCN
title: Pin PL-010's no-rebuild property with an allocation test on the render tick
priority: P2
effort: S
status: ready
classes: test, perf
feature: chart-readout
touches: tests/unit/test_simulation_view.py, src/anesthesia_sim/app/simulation_view.py
added: 2026-09-02
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_refresh_allocates_no_chart_points_when_drawn_count_unchanged' tests/unit/test_simulation_view.py
---

**Problem.** PL-010's claim - the render tick went from 16.6 ms to 2.6 ms at
the saturated window - was measured with a harness written in a scratch
directory and thrown away with the session. Nothing in the repository can
re-measure it, so the number is a historical assertion rather than something
a later change is held to. The next session to touch the render path either
rebuilds the harness or changes frame cost without knowing it.

**Why it matters.** PL-009 raises the render rate with a speed multiplier,
and PL-010's whole justification was buying headroom for it. Whether that
headroom survives is the question PL-009 has to answer, and it should not
have to build the instrument first. The harness is not difficult - a replay
controller handing `SimulationView._refresh_view` a history that grows one
render tick per call, timed over a few hundred frames at a saturated window -
but it is fiddly to get faithful. Flet's `Prop.__set__` early-returns when
the new value equals the old one, skipping the dirty-tracking it would
otherwise do, so a benchmark that replays one fixed snapshot measures a
cheaper write than the running app ever performs. The history has to advance
between calls. That trap is not hypothetical - it was hit while measuring
PL-010, and caught only because the whole-tick harness had been built to
advance and the per-part one had not.

**Why it matters more than a normal benchmark.** This is not a general
performance harness and should not become one. It answers one question - what
does one frame cost at the ceiling - and it exists because the answer is
otherwise unrecoverable.

**Where.** A `tools/` script, standard library only, or a `pytest` benchmark
kept out of the default run. Reads `SimulationView`, `RENDER_INTERVAL_S`,
`SIMULATION_STEP_S` and `CHART_COLUMN_BUDGET_PER_SERIES`; needs no Flet client.

**What to build, decided at triage 2026-09-02.** The brief left open whether
the instrument should assert a ceiling, only report, or assert something
machine-independent. Take the third: a test that a refresh allocates no new
`LineChartDataPoint` when the drawn count is unchanged. It is deterministic,
so it cannot flake on shared CI the way a wall-clock ceiling would; it tests
what actually regressed, which was allocation rather than milliseconds; and
it runs in the ordinary suite instead of being a report nobody executes. That
is the whole of what this item now owes.

The timing harness is deliberately **not** built. A number nobody re-measures
is documentation, and a timing assertion on shared CI is a flaky test - the
two options this replaces. If a frame-cost figure is wanted later (for
`PL-SN2C`, compressed playback, or whatever raises the render rate), it is a
separate item argued for on its own, and it inherits the trap below.

**The trap it has to avoid either way.** Flet's `Prop.__set__` early-returns
when the new value equals the old one, skipping the dirty-tracking it would
otherwise do, so a harness that replays one fixed snapshot measures a cheaper
write than the running app ever performs. The history has to advance between
calls. That is not hypothetical - it was hit while measuring PL-010, and
caught only because the whole-tick harness had been built to advance and the
per-part one had not.

**Done when.** `tests/unit/test_simulation_view.py` holds a test that fails
if a refresh allocates chart points when the drawn count has not changed,
so the property PL-010 bought is defended by the ordinary suite rather than
by a number in a closed item.
