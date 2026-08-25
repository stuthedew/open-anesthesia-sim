# Working notes

This file is a running, cross-session log of open threads, diagnoses, and
rationale: the narrative context behind decisions, too long to fit in a
queue item and not yet promoted into `ROADMAP.md` (version/milestone
decisions) or `docs/MODEL.md` (scientific model specification). It exists so
that a new conversation can pick up context without re-deriving it, and so
that decisions made in one conversation are visible to another.

It is not the task queue. Discrete, actionable work is tracked and
prioritized in `docs/items/`; threads here that have a corresponding
task cite its `PL-` id, and a queue item that needs more background
than its brief allows points back here. The split is deliberate: the punch
list stays short enough to read at the start of every session, and this file
absorbs the depth.

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
  remote branch deleted; `main` is now the v0.2.0 baseline (isoflurane and
  desflurane added as additional loadable agents, all loaded through
  `load_agent_parameters(agent_id)` in `core/parameters.py`). All three are
  selectable in the running app: a basic picker was added in `00791b1`,
  after v0.2.0 closed and outside its scope. It restarts the run at the new
  agent's 1 MAC rather than switching mid-run — residual-agent washout
  across a switch is still the anesthesia-machine milestone's work, and
  `SimulationController.set_agent`'s docstring is the place that says so.
  Work now happens on a per-session branch merged into `main` by pull
  request, not directly on `main`; `CLAUDE.md` says how that branch, its
  commits, and the pull request carry the queue item's ID.
- `docs/MODEL.md` and `ROADMAP.md` are up to date with the v0.2.0
  implementation: the arterial-blood simplification is documented
  explicitly (flow-limited, `F_a \equiv F_A`, no separate compartment,
  matching the Gas Man reference simulator's mammillary structure), the
  parameter provenance table covers all three agents from the cited data
  files, and `tests/reference/test_multi_agent.py` covers directional
  solubility and mass-balance closure for isoflurane and desflurane.
- `simulation_view.py` is tested through a minimal fake `Page`/`Controller`
  pattern documented at the top of `tests/unit/test_simulation_view.py`
  rather than a live Flet client. The simulation and render loops are now
  covered too (started as tasks, driven for a bounded slice of real time,
  then cancelled); `mount()`'s layout composition remains uncovered and has
  no formatting or domain logic to verify.
- Rendering is bounded and independent of run length: the chart is sent
  only the samples inside its visible window, decimated to at most
  `MAX_CHART_POINTS_PER_SERIES` per trace by min/max envelope selection
  (`app/chart_downsampling.py`), and the simulation and render loops run at
  separate cadences. A live Flet client was not available in the session that
  did this work, so the repaint mechanism was deliberately left unchanged —
  see PL-010 before optimizing it further.
- Two uncalled descriptive quantities remain in the core:
  `SimulationSnapshot.circuit_time_constant_s`, still computed but with no
  display widget since the v0.1.0 UI rewrite (v0.0.2 showed it; v0.1.0
  doesn't), and `AlveolarCompartment.time_constant_s`, whose only consumer
  went with `advance_ventilation`. Neither is the coupled time constant.
  Not yet decided whether to delete them or label them; tracked together as
  PL-004.

## Open thread: playback speed (target: real-time up to ~120x and beyond, "like Gas Man") - PL-009

Not scoped yet. The performance blocker this waited on has landed: render
cadence is now independent of simulation cadence, and frame cost no longer
grows with run length, so a multiplier no longer multiplies a growing
bottleneck.

What a speed multiplier now costs is bounded and known. Stepping the model
is nearly free (~0.011 ms per step, flat), so going faster means calling
`advance()` more times per render tick rather than rendering more often. A
frame currently costs ~17 ms of which ~15 ms is chart-point construction, so
PL-010 (point reuse, measured 20x cheaper) is the headroom to spend if a
high multiplier makes the render rate the constraint again.

Still undecided, and the reason this stays `needs-decision` rather than
`ready`: how the multiplier is exposed without creating a hidden mode - a
learner who does not notice a 120x setting will misread the time axis
entirely - and how it interacts with the fixed `SIMULATION_STEP_S = 0.1`.
Stepping is exact-closed-form per step, so a larger step is a model-fidelity
question, not just a performance one. Being an `L`, it needs scoping into a
`ROADMAP.md` milestone before implementation.

## Open thread: the architecture review harness - PL-024

An independent architecture review of the v0.2.0 baseline (commit
`3251ebf`) produced an executable harness under `tools/review-verification/`
rather than a prose write-up alone: every numeric claim it makes is
reproduced by a script, so a later reader can re-run the claim instead of
trusting the text.

The harness is on the development line (`655e429`, the cherry-pick of
`0ccfa44` from `claude/repo-architecture-review-3h39kh`); that branch has
since been deleted, so the harness is the whole record. The three
safety-critical findings it carried were fixed in v0.2.1 (`bc5f823`) and
their checks now report FIXED: `P1-2`, `P1-3`, and `P1-5`. Both scripts now
run at 5% delivered rather than 8%, since 8% is no longer a deliverable
isoflurane dial position. `P1-1`'s two checks were fixed after that, by the
exception-hierarchy and guarded-loop work, `P1-6` after that when the dead
`advance_ventilation` method was deleted, and `P1-4` when the parameter-file
schemas were made strict; seven of the harness's nine checks are now FIXED
and two still reproduce. The work landed since v0.2.1 is released as
v0.2.2.

Re-run after those fixes, `verify_physics.py` confirms all three physics
claims and `verify_findings.py` reproduces the two checks behind the two
remaining findings. The physics side
matters independently of the defects: it re-derives the
`docs/MODEL.md` equations from the parameter files with a from-scratch RK4
that imports no solver from `core/`, so agreement is genuine verification
rather than a tautology. It also shows a single matrix exponential is exact
(~1e-15) where the shipped pairwise split is not (~2e-5), which is the
evidence behind the review's central architectural recommendation. The
review's own note was that the remedy for the splitting error is not to
adopt `expm` outright but to promote the RK4 oracle into `tests/reference/`
with pinned vectors. That promotion has landed as
`tests/reference/test_coupled_dynamics.py`, so the coupled model is now
checked against an independent solution on every CI run; the oracle here
stays as the exploratory version, and is still where the `expm` comparison
lives.

Every finding that still reproduces is tracked. In the harness's own
numbering (`P1-1`, `P1-4` and `P1-6` are closed; see the punch list's
completed section):

`P2-1` is closed but will keep reporting REPRODUCED, and that is not a
regression. Its check measures whether mass balance alone can detect a wrong
rate, and mass balance still cannot: the fix was to add a second, independent
gate beside it, not to make the accounting validator into something it is
not. Read that check as a standing statement about what conservation buys,
not as an open defect.

- `P2-4` - PL-024, the venous pool's 12 s mixing time constant shaping the
  first minute of the displayed mixed-venous trace. Judged a documentation
  and presentation gap rather than a defect: 1.0 L is the Gas Man reference
  value and is cited twice in `reference_adult.json`, so the number is
  right and its meaning is unstated.

Fixing a finding flips its check to FIXED and makes the harness exit `1`,
which is the intended signal that the review write-up is stale for that
item - not a build failure. The scripts live outside `src/` and `tests/`
deliberately and are not part of the test suite.

## Open thread: splitting error outside the gate's operating point - PL-042

Found while deciding the interface's displayed precision, which needed a
number for how far the shipped operator split can be from the truth before
it could choose how many decimals to show.

`tests/reference/test_coupled_dynamics.py` runs its oracle at one operating
point: 5% delivered, 4 L/min fresh gas, and the reference adult's default
alveolar ventilation and cardiac output. That is a deliberate choice — the
governing equations are linear in the delivered fraction, and the test says
so — but linearity in the *dial* does not extend to the flows, which enter
the split's error nonlinearly through the sub-exchange rates.

Re-running the same oracle construction parameterized over every slider the
interface exposes gives the worst disagreement in any of the six displayed
states over an hour of simulated time:

| Operating point | Worst error |
| --- | --- |
| Default flows, dial at 1 MAC | 1.7e-3 percentage points |
| Default flows, dial at the agent's maximum | 5.0e-3 percentage points |
| Maximum flows, dial at the agent's maximum | 1.2e-2 percentage points |

The last row is desflurane at an 18% dial with 10 L/min fresh gas, 12 L/min
alveolar ventilation, and 10 L/min cardiac output; the worst state is mixed
venous at about 90 s, during the wash-in transient. As a first-order
coefficient that is roughly 1.2e-3 s^-1 against the documented C_max of
5e-4 s^-1 — the gate's bound is exceeded by a factor of about 2.4 in a
configuration the sliders can reach, and the gate does not fail because it
never runs there.

Two things follow, and they were deliberately separated:

- The precision decision needed the *magnitude*, and 1.2e-2 percentage
  points is disclosed in `docs/MODEL.md` § "Displayed precision" as the
  reason the second displayed decimal is the uncertain digit rather than a
  certain one. No displayed value is wrong; the display simply must not
  claim more than that.
- PL-042 needs the *gate*, which is a change to a release gate and to a
  documented bound, and is not something to fold into a formatting change.
  The bound must follow a fresh measurement over the corners rather than
  being set to today's worst number plus a margin, because the corner that
  matters may not be one of the ones measured here — only three flow values
  per axis were swept.

The exploratory sweep itself was not kept: it is a parameterized rewrite of
the `_build_derivative` / `_integrate_rk4` pair already in
`tests/reference/test_coupled_dynamics.py`, and reconstructing it is a
smaller job than maintaining a second copy of the oracle outside the suite.
Parameterizing the one in the test file is PL-042's first step regardless.

## Open thread: scenario branching, bookmarks, and what a snapshot is for - PL-X9R0, PL-WRKL, PL-RRWV, PL-PFM1, PL-JW30

Raised by the project owner 2026-08-25, as context behind an earlier
suggestion (from a different assistant) that the simulation store periodic
history snapshots. Captured here because the mechanism and the goal came
apart on inspection, and the reasoning should not have to be re-derived.

**The goal.** Compare two managements of the *same* case without rebuilding
the case. The owner's worked example: run three simulated hours, then wake
the patient by turning the vaporizer off and coasting on low flow for fifteen
minutes before opening the flows, and watch what the vessel-rich group does.
Then go back to just before the coast, branch, and instead hold 0.5 MAC on
normal flows until 3:15 before turning everything off - and compare time to
the wake-up threshold. Same case, one variable, two curves. The wash-in
equivalent is the same shape: branch at t=0 and compare low-flow/high-dial
against high-flow/maintenance-dial.

**How the owner expects it to be driven.** Bookmarks, in the Gas Man sense:
set a target - an absolute simulated time, or a monitored concentration
crossing a threshold ("VRG reaches 0.8 MAC") - run at high playback speed,
and the run halts there. Build the case as a sequence of bookmark-to-bookmark
fast-forwards, and branch at a bookmark. Branching from an arbitrary
mid-interval time is the rare case, not the normal one. Sub-forks of forks
are explicitly out of initial scope: one trunk, N branches off it.

**The mechanism that was proposed, and why it does not survive contact.**
Snapshot at fixed intervals; to reach an arbitrary point, restore the nearest
prior snapshot and resimulate the remainder. The stated aim was to avoid
duplicate simulation time - "storage rather than resimulation". Three
measurements, taken 2026-08-25 against the code as it stands, put that
trade-off somewhere other than where it was assumed to be:

- *A snapshot is nearly free.* The complete dynamic state is six
  concentrations (circuit, alveolar, mixed-venous, VRG, muscle, fat) plus
  `elapsed_s` and the four control settings. That is about the size of one
  `SimulationHistorySample` (88 B as an object). Snapshot density is not a
  cost worth optimizing at this model size.
- *Resimulation is nearly free too.* `SimulationState.advance` measures
  8.9 us per 0.1 s step. Reconstructing a 3-hour run from t=0 costs about
  1 s; 24 hours about 8 s. The interactive case the owner described would not
  perceptibly benefit from a snapshot at all.
- *The per-step history is the expensive thing.* 36 000 samples per simulated
  hour, ~88-256 B each: single-digit MB per hour, ~2.3-6.6 GB at the 30-day
  run-time cap the owner is considering. That is PL-011, and it is the
  storage question that actually needs an answer.

So the snapshot-interval design optimizes the cheap axis. It is not wrong,
it is just not where the constraint is.

**What the mechanism was missing.** Resimulating from a snapshot to an
arbitrary later point requires re-applying the control inputs over that
interval - and nothing currently records them. `SimulationController` records
concentrations, never the fresh-gas-flow, vaporizer, ventilation, or cardiac
output changes that produced them. Without that timeline the fallback path in
any interval-snapshot scheme cannot be built, and neither can replay or
export-with-provenance. `ROADMAP.md`'s planned-milestone order already
encodes this - scenario events (8), save/load (9), replay (10), comparison
(11), forking (12) - which is worth knowing before anyone reorders it.
Recorded as PL-WRKL.

**Two correctness traps, recorded so they are not discovered late.**
PL-PFM1: a threshold bookmark must be tested every simulation step, not once
per rendered frame, or it overshoots by a speed-dependent amount and halts at
a concentration other than the one asked for - which also makes any branch
taken there unreproducible. PL-JW30: a branch created by resimulation while
its parent was simulated straight through can diverge from the parent
*before* the branch point by floating-point rounding, which is precisely the
divergence a strategy comparison is meant to rule out.

**Open question for the owner**, not yet answered: whether MAC-denominated
bookmarks ("0.8 MAC") are wanted before MAC is a first-class displayed
quantity. `mac_percent` exists per agent in `core/parameters.py` and the
agent data files, but MAC presentation was explicitly out of scope for
v0.1.0.

## Aspirational: power-user custom agents (not scoped, not started)

The project owner's stated future direction, raised while discussing
whether `core/parameters.py`'s `AGENT_DATA_FILENAMES` dict should stay a
hardcoded enumeration of built-in agents (decision: yes, for now - see
that conversation's reasoning; a directory-scan loader alone wouldn't
give power users this anyway since it only reaches packaged files).

The idea: eventually let power users (e.g. for research use) add their
own custom agent parameter sets, analogous to how 3D-printer slicers
handle filament profiles - built-in presets, "duplicate an existing
profile and modify it," and "create from scratch," gated behind an
explicit warning since these aren't the vetted built-in agents.

Not scoped or designed. Key considerations for whoever scopes this,
noted now so they aren't lost:

- **Provenance/trust must stay visible everywhere the agent appears**
  (dropdown, header, charts, any export) - a custom agent has none of
  the peer-reviewed citation backing the built-in `sources` field
  requires, and presenting a user-authored curve with the same visual
  authority as a cited built-in one would violate this repo's
  presentation-correctness standard (CLAUDE.md). Likely needs a
  first-class "verified built-in vs. user-supplied" distinction in the
  data model itself, not just a UI label bolted on after the fact.
- Storage has to live outside the installed package - `core/parameters.py`
  currently only loads via `importlib.resources` against packaged
  `data/agents/*.json`; custom agents need a separate on-disk location
  (e.g. a user config directory) and their own load path.
- The existing Pydantic validation (ranges, required fields, rejection of
  keys the schema does not declare, the
  mac_percent <= max_delivered_concentration_percent cross-check) should
  still apply to custom agents - it catches structurally invalid data
  (typos, absurd values) even though it can't and shouldn't try to
  verify real-world plausibility the way a citation does.
- "Duplicate and modify" falls out naturally once custom-agent storage
  exists, since every built-in agent's JSON is already fully
  self-contained - cloning one as a starting point is close to free.

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
new idea - it is already `ROADMAP.md`'s "Planned milestones" item 13 ("Add
IV pharmacokinetic and effect-site models, after item 12 (simulation
forking) is available"). The vision here is the same destination with much higher
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
