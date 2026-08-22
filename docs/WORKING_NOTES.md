# Working notes

This file is a running, cross-session log of open threads, diagnoses, and
plans that have not yet been promoted into `ROADMAP.md` (version/milestone
decisions) or `docs/MODEL.md` (scientific model specification). It exists so
that a new conversation can pick up context without re-deriving it, and so
that decisions made in one conversation are visible to another.

Any session working on this repository should read this file at the start
of a task that touches one of its open threads, and update the relevant
section (not just append) as the thread progresses. Write entries so a
reader with no memory of the originating conversation can act on them:
state facts and decisions, not "the user said" or "we discussed."

When a thread here is fully resolved (implemented, tested, and merged), its
outcome belongs in `ROADMAP.md`/`docs/MODEL.md`/commit history as
appropriate, and its entry here should be deleted rather than left stale.

## Repository state as of this writing

- Active development branch: `build/v0.1.0-sevo-patient` (not yet merged to
  `main`, which is still at v0.0.2). `pyproject.toml` already reports
  version `0.1.0`.
- `docs/MODEL.md` and `ROADMAP.md` are up to date with the v0.1.0
  implementation: the arterial-blood simplification is documented
  explicitly (flow-limited, `F_a \equiv F_A`, no separate compartment,
  matching the Gas Man reference simulator's mammillary structure), the
  parameter provenance table is filled from the cited data files, and the
  three previously-missing required tests (equilibrium, directional
  solubility, deterministic replay) have been added.
- `simulation_view.py` test coverage is 92% (up from 32%), using a minimal
  fake `Page`/`Controller` pattern documented at the top of
  `tests/unit/test_simulation_view.py` rather than a live Flet client.
  Uncovered: `mount()`'s layout composition and the async timer loop, which
  have no formatting/domain logic to verify.
- Known dead field: `SimulationSnapshot.circuit_time_constant_s` is still
  computed but has had no corresponding display widget since the v0.1.0 UI
  rewrite (v0.0.2 showed it; v0.1.0 doesn't). Not yet decided whether to
  restore the display or remove the field.

## Open thread: performance (slow live graph, unresponsive buttons)

Not yet profiled or fixed. Diagnosis so far, from reading the code (not yet
confirmed by a profiler):

The per-step physics is not the likely bottleneck. Every compartment update
in `core/*.py` is a closed-form exact solution, not an iterative solver;
benchmarking showed thousands of steps across the full 6-compartment system
completing in well under a second. Two other things in the `app/` layer are
more likely causes:

1. `SimulationController._concentration_history` grows without bound —
   every `advance()` call appends a sample and nothing ever trims it. The
   chart rebuilds full point arrays for all 6 series from that entire
   history on every `_refresh_view()` call, so the render payload sent to
   the Flet client on every `page.update()` grows for as long as the
   simulation runs.
2. Simulation-step cadence and render cadence are coupled at the same 10 Hz
   in `SimulationView._run_simulation_timer` — `advance()` and
   `page.update()` happen back-to-back in one coroutine on Python's single
   asyncio event loop. If `page.update()` is slow to serialize/flush, it
   blocks that same loop from servicing the next button click until it
   yields, which would explain "buttons feel unresponsive" specifically.

Working hypothesis for a fix (not yet validated or implemented):
decouple simulation-step cadence from render cadence, and cap or downsample
what's sent to the chart (a rolling window or point decimation) independent
of how much history the controller keeps for accounting. This also happens
to be the natural foundation for the later "faster than real time" goal
(see next section), since sim time is already explicit state independent
of wall-clock time — going faster mostly means calling `advance()` more
times per render tick, which only pays off once the render side stops
being the bottleneck.

Multithreading is probably not the right lever: the loop isn't blocked on
CPU-bound math (which is cheap), and Python's GIL means threads wouldn't
give real parallelism for that math anyway. The likely fix is async/
architectural (decoupling cadences, bounding payload size), not concurrency.

Next step when this is picked up: profile first to confirm the diagnosis
before implementing anything.

## Open thread: playback speed (target: real-time up to ~120x and beyond, "like Gas Man")

Not scoped yet. Depends on the performance thread above being resolved
first, since a faster-than-real-time mode multiplies whatever the render
bottleneck currently is. No design decisions made yet on how speed
multiplier would be exposed in the UI or how it interacts with the fixed
`SIMULATION_STEP_S = 0.1` step size.

## Open thread: documentation pass

Plan (as stated by the project owner): go file-by-file, generate or update
documentation for one file, get explicit approval, then move to the next
file. Not yet started. Scope not yet defined — which files/layers
(docstrings in `src/`, `README.md`, an architecture overview, something
else) has not been decided.

## Open thread: UI structure/form mockups

Goal: mock up overall interface structure and form to inform function,
separate from polishing the current Flet implementation — i.e., work at
the level of layout, information hierarchy, and interaction flow before
committing to pixel-level styling. Not yet started.

Baseline for comparison — the current v0.1.0 interface (`app/
simulation_view.py`), as actually implemented:

- Header: app name, version, and "Sevoflurane patient model" subtitle.
- Run controls: Start / Pause / Reset buttons plus a running/paused status
  indicator.
- Four parameter panels, each a slider plus a live value readout: fresh gas
  flow (0-10 L/min), delivered sevoflurane (0-10%), alveolar ventilation
  (0-12 L/min), cardiac output (0-10 L/min). Circuit volume is a
  controller/model parameter but has no slider in the v0.1.0 UI (v0.0.2 did
  expose it).
- Seven concentration metric panels: simulated time, circuit/inspired,
  alveolar/end-tidal, mixed venous, vessel-rich, muscle, fat — each a
  formatted percent (or seconds, for time).
- One multi-series line chart (6 traces: circuit, alveolar, mixed venous,
  vessel-rich, muscle, fat) with a legend describing each trace's line
  style, and a rolling x-axis window.
- An agent-accounting validation panel: pass/fail status, a one-line
  explanation, and delivered/exhausted/stored/unaccounted/absolute-error
  amounts.
- A fixed disclaimer line: "Educational simulation only... not a clinical
  prediction, monitoring, or dosing tool."

Nothing about this baseline is settled as "correct" — it's recorded here
only so a mockup session has an accurate starting point rather than
guessing at the current implementation from memory.
