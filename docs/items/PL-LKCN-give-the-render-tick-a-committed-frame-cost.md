---
id: PL-LKCN
title: Give the render tick a committed frame-cost benchmark
status: untriaged
added: 2026-09-02
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
`SIMULATION_STEP_S` and `MAX_CHART_POINTS_PER_SERIES`; needs no Flet client.

**Open question worth settling before building it.** Whether it should assert
a ceiling (a regression test that fails when a frame gets slower) or only
report. A timing assertion on shared CI is a flaky test; a report nobody runs
is documentation. A third option is to assert something machine-independent -
that a frame allocates no `LineChartDataPoint` when the drawn count is
unchanged - which is what actually regressed, and is deterministic. That last
one may be the whole item.

**Done when.** A committed command re-measures the frame cost at the
saturated window, and the numbers PL-010 recorded can be reproduced or
contradicted without rebuilding anything.
