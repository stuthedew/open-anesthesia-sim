---
id: PL-55DH
title: Build the PySide6 + pyqtgraph spike: the concentration chart and the readout row behind the existing controller, disposable and touching no shipped app/ module
priority: P2
effort: M
status: done
classes: perf, ux
feature: teachable-case
blocked-by: PL-QXSB
touches: spikes/qt, docs/WORKING_NOTES.md
verify: python3 tools/doc_check.py check && test -f spikes/qt/qt_spike.py && grep -q 'PL-55DH' docs/WORKING_NOTES.md
added: 2026-09-08
closed: 2026-09-08
---

**Problem.** Build the PySide6 + pyqtgraph spike: the concentration chart and the readout row behind the existing controller, disposable and touching no shipped app/ module

**Approved by the project owner, 2026-09-08.** `PL-QXSB` measured PySide6 with
pyqtgraph at 0.51 ms for the frame Flet does in 20.3 ms, flat in point count,
and established that PyQt is excluded by licensing. What it could not measure is
paint cost, because this container has no GPU. The spike is what answers that,
and it is a spike rather than a port: **it throws away cleanly and it changes
nothing shipped.**

**Scope.** The concentration chart and the readout row, driven by the *existing*
`SimulationController` — which needs no adaptation, because `core/` and
`app/controller.py` import no Flet and `tools/import_boundary_check.py` enforces
it. Six traces, the shipped column budget, the same 5 Hz cadence, the four
parameter sliders wired through the same setters.

**Out of scope, deliberately:** the agent selector, the wash-in plot, control
marks, the new-case dialog, the notice banner, theming beyond enough colour to
tell the traces apart. The question is frame cost and feel, not completeness.

**Why it matters.** `PL-QXSB` cannot be decided on this container's evidence
alone, and it is admitted to v0.5.0's gate — so a milestone waits on a question
whose remaining half is one bounded experiment. The spike is also the cheapest
way to be *wrong* about Qt: if the paint cost or the look does not hold up, that
is discovered for a few hours of work rather than after `app/` has been
rewritten. `CLAUDE.md` warns that the apparatus is at permanent risk of becoming
the work; a throwaway spike is the form of this investigation that cannot become
it.

**Where it lives.** Not in `src/anesthesia_sim/app/`. A spike that imports from
the shipped package but is not part of it — so deleting it is one `rm` and no
shipped module ever imported it. Its dependencies are not added to
`pyproject.toml`'s runtime set; `PL-QXSB` records the sizes (PySide6-Essentials
233 MB, numpy 33 MB, pyqtgraph 7.7 MB) that a real port would have to justify.

**Done when** the spike runs a real case end to end and `PL-X9T3` has something
to measure on the owner's machine. Not when it looks finished — that is
`PL-QXSB`'s decision to take afterwards, on evidence.

## Built, 2026-09-08

**It lives in `spikes/qt/`** - `qt_spike.py` (the window and its two loops),
`chart_sources.py` (what the six traces draw, Qt-free), `frame_timing.py` (the
rolling frame statistics, Qt-free) and a `README.md` with the one command that
runs it. Nothing under `src/anesthesia_sim/` imports it; `rm -rf spikes/`
removes the experiment whole. Its dependencies are not in `pyproject.toml`:
`uv run --with PySide6-Essentials --with pyqtgraph --with numpy` layers them
over the project environment for one command and writes nothing.

**The read path it was scoped against was deleted while it was being built.**
This brief says "the shipped column budget", meaning M4 selection over
recorded samples. `PL-2FM6`, `PL-4RBD` and `PL-8LXM` merged mid-session, so
`RunHistory`, `history_window` and the M4 module are gone and
`SimulationController.drawn_window` is the only read path. The spike was
rebuilt on it. The source selector that would otherwise have been needed
became a **column-budget control**: with M4 gone, `PL-QXSB`'s "would Qt make
decimation optional" is "can the column budget be raised", which is the same
question in the architecture that replaced it.

**What was added beyond the brief, and why.** This item's own "done when" is
that `PL-X9T3` has something to measure, and `PL-X9T3` asks for `PL-YSZN`'s
three-stage split, input latency, and how it looks. So the window instruments
its own frame in that split - `advance`, `refresh`, `handoff` - plus `paint`,
which no Flet measurement could reach because Flet renders out of process, and
render-timer lateness, which is what "laggy" named. Without those the owner
would have to write the instrumentation before they could run the experiment.

**What it is checked by.** No test under `tests/`: a test of a throwaway tree
is a shipped asset for something meant to be deleted, and `pytest`'s
`testpaths` does not reach here. `--self-check` is the substitute and runs
headless - it advances a real case at a real playback rate, draws real frames
through the real render path, and asserts that every trace's newest drawn
point agrees with the readout printed beneath it, which is what catches a
swapped compartment or a missing factor of a hundred. `--screenshot` writes
the running window to a PNG, which exercised `PL-QXSB`'s claim that Qt removes
`PL-2QMK`'s blindness in this container rather than repeating it.

**Measurements and the two findings they turned up** are in
`docs/WORKING_NOTES.md` under "Built and measured: the Qt spike runs, and the
frame's dominant cost moved". The headline holds: handing a frame to the
toolkit costs 1.0-1.2 ms against Flet's 26.6-45.5 ms. Two findings were filed
rather than fixed - `PL-C92D` (two of `PL-YSZN`'s three stages measure a tree
that no longer exists, so only the `page.update` row is a toolkit comparison)
and `PL-CNCF` (`drawn_window` is 6.2 ms of a 6.24 ms frame read, and about
eighty times the simulation at 1x).

**One result bears on a decision this item was not about.** `PL-GS3R` is `P1`,
`safety` and `needs-decision`, and its first route - buy chart fidelity with
more columns - is priced against Flet's per-point charge. The spike measures
what that route costs on a toolkit that transports arrays: `handoff` goes from
1.28 ms to 2.08 ms for sixteen times the points, so the whole cost is the score
evaluation and none of it is the toolkit. Four times the columns is 10.7 ms of
Python on Qt against about 88 ms of chart share on Flet. That makes the toolkit
choice partly a question of whether an open safety item can be closed by its
cheap route, which is a stronger argument than the speed one and is recorded in
`docs/WORKING_NOTES.md` beside the measurements.

**What this item does not settle**, deliberately: paint cost and feel on real
hardware. `paint` measured 24-34 ms offscreen here and means nothing - no GPU,
a software rasteriser - and timer lateness is zero because the check drives
its own frames. Both are `PL-X9T3`'s, on the owner's own machine, which is
what the spike was built to make possible.
