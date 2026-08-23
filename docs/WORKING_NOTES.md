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

- `build/v0.1.0-sevo-patient` was fast-forward merged into `main` and the
  remote branch deleted; `main` is now the v0.1.0 baseline. Work happens
  directly on `main` unless a session has reason to branch.
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

## Open thread: startup window sizing

`app/main.py` sets `page.window.full_screen = True` on startup. Per prior
project decision (previously recorded in `README.md`, moved here as part of
the documentation pass so it isn't lost): replace this with an adequately
sized, centered window that remains fully visible on different displays.
Avoid magic pixel dimensions, monitor-specific assumptions, and native
display-probing dependencies. Not yet implemented.

## Open thread: documentation pass

Plan (as stated by the project owner): go file-by-file, generate or update
documentation for one file, get explicit approval, then move to the next
file. Not yet started. Scope not yet defined — which files/layers
(docstrings in `src/`, `README.md`, an architecture overview, something
else) has not been decided.

## Shelved: UI structure/form mockups

Explored, then explicitly shelved (project owner's call) in favor of
maturing the scientific core first. Do not resume this without the
project owner asking again.

What happened: three static wireframe directions were built as a Claude
Design canvas artifact (today's screen recreated faithfully, a
"vitals-first" restructure, and a zoned Inputs/Monitor/Diagnostics
layout) — https://claude.ai/code/artifact/cb5e540b-5e87-4812-ae29-ec2d1a45ef5e.
The project owner's assessment: the current v0.1.0 interface is
intentionally minimal ("hello world"), and the three mockups were just
better-organized versions of that same shallow functionality. A mature
UI cannot be designed on top of functionality this early — see "Long-term
vision" below. The artifact link is kept here only as a record of what
was tried; it is not a starting point to resume from, since real UI work
later should be informed by whatever the scientific core looks like at
that point, not by these sketches.

## Long-term vision (aspirational north star, not a scoped milestone)

The project owner's stated ambition, for future planning only - explicitly
not to be turned into near-term scope or used to justify any UI work now:
something with the scientific credibility of Gas Man (gasmanweb.com, the
flow-limited mammillary uptake/distribution model this project's own
sevoflurane/patient parameters are already drawn from) combined with
SimTiva (simtiva.app, an open-source TIVA/TCI simulator built on
STANPUMP/Shafer PK-PD - effect-site concentration, Cp/Ce target-controlled
infusion, propofol-opioid interaction) - at a level of execution and
interaction quality neither reference tool actually has, phrased by the
owner as "what version 18 would look like if version 6 incorporated
SimTiva functionality" against Gas Man's real-world v4.x.

Concretely, this points at IV/TIVA pharmacokinetic and effect-site
modeling integrated with the existing inhaled-agent model. That is not a
new idea - it is already `ROADMAP.md`'s "Later roadmap" item 5 ("Add IV
pharmacokinetic and effect-site models after simulation forking is
available"). The vision here is the same destination with much higher
ambition on execution and UX quality, and possibly a different order,
not a different target.

Explicit sequencing principle from this discussion: UI/UX ambition
follows scientific-core maturity, not the other way around. High
production values on top of a not-yet-validated model would be a worse
outcome than the current honestly-minimal interface, not a better one -
consistent with `CLAUDE.md`'s standard that presentation polish must
never imply more certainty or completeness than the model actually
supports. This vision should only move into `ROADMAP.md` as a real,
scoped milestone (goal, required scope, definition of done, explicit
out-of-scope list) once the project owner is ready to schedule it - not
before.

Also noted, further down the road than the above: mature figure export -
generating a publication-quality static graph from a simulation run, of
the kind someone would put in a paper, as opposed to the live interactive
dashboard chart. This implies its own rendering path (vector/high-res
output, print-appropriate axis and label sizing, customizable styling)
separate from the Flet live chart, and - per the same presentation-
correctness standard above - exported figures should carry the model
name/version, parameter provenance, and units they were generated from,
not just the plotted curve. Aspirational only; not scoped.
