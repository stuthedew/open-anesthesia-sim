# Working notes

This file is a running, cross-session log of open threads, diagnoses, and
rationale: the narrative context behind decisions, too long to fit in a
punch-list entry and not yet promoted into `ROADMAP.md` (version/milestone
decisions) or `docs/MODEL.md` (scientific model specification). It exists so
that a new conversation can pick up context without re-deriving it, and so
that decisions made in one conversation are visible to another.

It is not the task queue. Discrete, actionable work is tracked and
prioritized in `docs/PUNCH_LIST.md`; threads here that have a corresponding
task cite its `PL-` id, and a punch-list entry that needs more background
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
  Work happens directly on `main` unless a session has reason to branch.
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
- Known dead field: `SimulationSnapshot.circuit_time_constant_s` is still
  computed but has had no corresponding display widget since the v0.1.0 UI
  rewrite (v0.0.2 showed it; v0.1.0 doesn't). Not yet decided whether to
  restore the display or remove the field; tracked as PL-004.

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

## Open thread: the unmerged architecture review - PL-013

An independent architecture review of the v0.2.0 baseline (commit
`3251ebf`) produced an executable harness under `tools/review-verification/`
rather than a prose write-up alone: every numeric claim it makes is
reproduced by a script, so a later reader can re-run the claim instead of
trusting the text.

The harness is now on the development line (`655e429`, the cherry-pick of
`0ccfa44` from `claude/repo-architecture-review-3h39kh`), so the branch is
no longer the only record and can be deleted. The three safety-critical
findings it carried were fixed in v0.2.1 (`bc5f823`) and their checks now
report FIXED: `P1-2`, `P1-3`, and `P1-5`. Both scripts now run at 5% delivered
rather than 8%, since 8% is no longer a deliverable isoflurane dial
position.

Re-run after those fixes, `verify_physics.py` confirms all three physics
claims and `verify_findings.py` reproduces the six checks behind the five
remaining findings (`P1-1` accounts for two of them). The physics side
matters independently of the defects: it re-derives the
`docs/MODEL.md` equations from the parameter files with a from-scratch RK4
that imports no solver from `core/`, so agreement is genuine verification
rather than a tautology. It also shows a single matrix exponential is exact
(~1e-15) where the shipped pairwise split is not (~2e-5), which is the
evidence behind the review's central architectural recommendation. The
review's own note is that the remedy for the splitting error is not to adopt
`expm` outright but to promote the RK4 oracle into `tests/reference/` with
pinned vectors, so the coupled model is checked against an independent
solution on every CI run.

`P1-1` is filed as PL-018. The four that remain to triage under PL-013, in
the harness's own numbering:

- `P1-4` - no Pydantic model in `core/parameters.py` sets
  `extra='forbid'`, so a misspelled key in a safety-critical data file
  loads clean and the intended value silently does not apply.
- `P1-6` - `advance_ventilation` has no call site inside `core/` and does
  not conserve agent mass (alveolar amount rises 0.005263 L with no
  matching circuit debit). Dead code that models the same physics
  incorrectly is a trap for the next reader.
- `P2-1` - the mass-balance check passes (residual 2.22e-15 L) while the
  dynamics are visibly wrong: `dt=10 s` differs from `dt=0.1 s` by 0.157
  percentage points of alveolar fraction. Conservation is necessary but
  nowhere near sufficient as a correctness gate, and it is currently the
  only one.
- `P2-4` - the 1.0 L venous pool dominates early mixed-venous values,
  depressing them 55% at 30 s and 34% at 60 s against a near-instant-mixing
  comparison. This is a modelling choice to document or revisit, not
  necessarily a defect.

Fixing a finding flips its check to FIXED and makes the harness exit `1`,
which is the intended signal that the review write-up is stale for that
item - not a build failure. The scripts live outside `src/` and `tests/`
deliberately and are not part of the test suite.

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
- The existing Pydantic validation (ranges, required fields, the
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
