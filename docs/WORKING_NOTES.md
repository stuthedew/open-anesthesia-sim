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

## Open thread: the v0.2.8 gate's membership test - PL-MGNC, PL-H8MQ, PL-HXYY

**What the gate's admission test actually is** (project owner, 2026-08-31).
The frozen list is a *scope*, not a set of items: a finding is inside it if it
contributes to the goal the release states — a low-friction workflow before
the two long milestones are run through it — and outside it if it is a
different goal. `ROADMAP.md`'s "What the freeze closes, and what it does not"
now carries that test, with the two limits that keep it from reopening the
list for everything: the finding must be a **defect** in machinery the goal
names, and it must be **workable in this tree**.

Why it needed writing down: the paragraph previously offered only two
dispositions, "new scope" and "completes a frozen entry", and a finding that
was neither went to the queue. The nine captures triaged on 2026-08-31 were
all triaged that way and all excluded, each with a correct answer to the
completion question. Seven of them were defects in the session-start digest,
the release script, the merge path and the lint gate — the machinery the
release's own goal enumerates — and are now entries. The reassessment did not
change intent; it recorded a test that was being applied from memory in one
place and from the written rule in another.

**The two excluded, and why.** `PL-KKX4` (a web session started with no
checkout) fails the workable-here limit: its cause is outside the repository
and its own `not-delegable:` field says the only action available is to record
a second sighting, so it would hold the gate open indefinitely. `PL-SRCP` was
dropped at triage as a duplicate of `PL-3CBS`.

**Two more admitted on the same reading, 2026-08-31,** bringing the list to
thirty-one entries with eleven open. `PL-MGNC` was found while reassessing: a
shallow clone's incomplete `^base` walk made the digest report twenty-seven
ids in flight, eighteen of them closed and one of them `PL-NSN9`, an open
entry of this gate. `PL-3CBS` (docket has no way to notice that an open item's
work already landed on main) was not one of the nine and qualified on the same
reading.

**The `vcs.py` cluster is one piece of work, not three.** `PL-CPSY`,
`PL-S1P1` and `PL-MGNC` are three holes in `branches_in_flight` and its return
value — a stale ref never excluded, the unreadable refs dropped from the ids,
and a walk that under-excludes when the merge-base resolves but the history
does not reach it. They collide on `touches` by construction. Taking them
together is one design pass over that function; taking them separately is
three, each invalidating the last.

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

Half of this is now decided rather than open. PL-VP7N put the operator
split's applicability domain in the core as `MAXIMUM_SIMULATION_STEP_S`, and
a step above it is refused, so the multiplier cannot be a larger step even
if someone wanted it to be: it is steps per tick, and that is enforced
rather than merely written down. What "a larger step is a model-fidelity
question" was pointing at has an answer - `docs/MODEL.md` § "Supported
simulation step" - and the answer is that the supported step and the shipped
step are the same number.

Still undecided, and the reason this stays `needs-decision` rather than
`ready`: how the multiplier is exposed without creating a hidden mode - a
learner who does not notice a 120x setting will misread the time axis
entirely. Being an `L`, it needs scoping into a `ROADMAP.md` milestone
before implementation.

## Open thread: what the v0.2.0 architecture review left behind - PL-024, PL-6GS0

An independent architecture review of the v0.2.0 baseline (commit `3251ebf`)
reported 21 findings and shipped an executable harness under `tools/` rather
than a prose write-up alone, so that every numeric claim could be re-run
instead of trusted. Eight findings had a crisp programmatic reproduction; the
rest were design, presentation and documentation judgements a script cannot
adjudicate.

**The harness is retired** (PL-STNV, 2026-08-30). Seven of its eight defect
checks reported FIXED and each is a closed item: `P1-1` PL-018, `P1-2` PL-015,
`P1-3` PL-017, `P1-4` PL-021, `P1-5` PL-016, `P1-6` PL-022. The eighth, `P2-1`,
had two halves and both are closed - the step-size half by PL-VP7N's
applicability-domain guard, which now refuses the coarse step the check itself
used and so stops it running at all, and the mass-balance half by PL-023's
independent RK4 oracle. Its three physics checks were CONFIRMED and two of
them are now release gates in `tests/reference/test_coupled_dynamics.py`. What
was left was a second verification path for checks the reference suite already
makes, plus a script reporting a defect nobody could act on because it was
never in the queue - which is worse than no harness, because it looks like
tracking. Recover it with `git log --diff-filter=D -- tools/review-verification`
if a claim ever needs re-running.

That mass balance cannot detect a wrong *rate* is not a defect and will not
be re-found: it is a standing property of equal-and-opposite accounting,
recorded in `docs/MODEL.md` § "Selected method (as implemented)" and gated by
the independent-solution test beside it.

**PL-024 - the venous pool's grip on the first minute.** The one check that
still reproduced at retirement, and a documentation and presentation gap
rather than a defect: 1.0 L is the Gas Man reference value and is cited twice
in `reference_adult.json`, so the number is right and its meaning is unstated.
Its mixing time constant is 60 - V/Q̇ = 12 s at the reference 1.0 L and
5 L/min, which dominates the displayed mixed-venous value early in wash-in.
Measured against a near-instant 0.01 L pool, sevoflurane at 5% delivered:

```text
t=  30 s   pooled 0.00013   near-instant 0.00030    -55.5%
t=  60 s   pooled 0.00100   near-instant 0.00152    -34.5%
t= 120 s   pooled 0.00482   near-instant 0.00582    -17.2%
```

**PL-6GS0 - the exact-step question.** The review's central architectural
recommendation was that the coupled system is linear and time-invariant within
a step, so one matrix exponential is exact where the pairwise split is
\(O(\Delta t)\). The review itself deferred it in favour of promoting the RK4
oracle into CI, which landed as `tests/reference/test_coupled_dynamics.py`. The
deferral was never revisited, and the measured comparison it rests on is
carried in the item rather than here, since the harness that produced it is
gone. It bears on the playback-speed thread above: an exact step would make a
larger step a fidelity-free choice, which is exactly what that thread assumes
it is not.

## Open thread: scenario branching, bookmarks, and what a snapshot is for - PL-DHV7, ROADMAP items 8, 11, 12 and 26

**Where the work went, 2026-08-25.** Triaged after capture. Only PL-DHV7
(MAC as a displayed unit) is startable against the code as it stands and
stays in the queue. The other four items named below were promoted into
`ROADMAP.md`'s planned milestones and dropped from the queue, each with its
reason recorded in its file: PL-WRKL into item 8, PL-RRWV into items 11 and
12, PL-JW30 into item 12 as a required property, PL-PFM1 into item 26 as one,
and PL-X9R0 into item 26 itself. The measurements and reasoning below are
what those roadmap entries were written from, and are kept here because a
scoped milestone will need them again. The thread stays open until item 26 is
scoped.


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
Recorded as PL-WRKL, now `ROADMAP.md` item 8.

**Two correctness traps, recorded so they are not discovered late,** and
now carried as required properties of the roadmap items they constrain.
PL-PFM1 (item 26): a threshold bookmark must be tested every simulation step, not once
per rendered frame, or it overshoots by a speed-dependent amount and halts at
a concentration other than the one asked for - which also makes any branch
taken there unreproducible. PL-JW30 (item 12): a branch created by resimulation while
its parent was simulated straight through can diverge from the parent
*before* the branch point by floating-point rounding, which is precisely the
divergence a strategy comparison is meant to rule out; it is a required
property of item 12.

**Bookmark set, settled 2026-08-25.** The owner names the reference
simulator's two kinds as the floor: absolute time points, and percent of MAC
on *every* graphed compartment - circuit, alveolar, VRG, muscle, fat, venous -
not the alveolar trace alone. The vendor documentation could not be checked
from the capturing session (gasmanweb.com and its help mirror are both
refused by the environment's network egress policy), so this is recorded as
the owner's account rather than as a citation. Full detail in PL-X9R0, now `ROADMAP.md` item 26.

That answers the MAC question by forcing it: MAC-per-compartment bookmarks
cannot be built while MAC is internal-only, so making MAC a displayed unit
(PL-DHV7) moves from "someday" to a prerequisite. Its hard part is not the
division - it is that a MAC multiple on a tissue compartment asserts
something narrower than it appears to, and the label has to say which.

## Decided, not yet implemented - PL-026

Decided in conversation on 2026-08-24 rather than in a session, and waiting on
implementation. The rejected options are recorded so they are not re-argued.

The brief costed the transactional option as "capturing and restoring six
compartments plus the accounting validator on every step", and that estimate
is what pushed the item toward the two cheaper options. It is wrong. A run's
dynamic state - everything `advance()` mutates - is eight floats:

| Where | Field |
| --- | --- |
| `BreathingCircuit` | `circuit_concentration_fraction` |
| `AlveolarCompartment` | `agent_amount_l` |
| `TissueGroup` (x3) | `agent_amount_l` |
| `VenousBloodCompartment` | `agent_amount_l` |
| `AgentSimulationValidator` | `delivered_agent_l`, `exhausted_agent_l` |

Everything else on those dataclasses is a setting or a parameter that a step
never touches. Eight reads before `_advance_step` and eight writes on the
failure path is free against a 0.1 s step, and it is explicit rather than
clever, which is what the safety-critical standard asks for.

Rejected, both for the same reason: keeping the banner as the only cue, and
blanking or greying the metrics. Each leaves `core/` holding a state that is
not a solution of the model, and leaves the run resettable but not
resumable. The brief credited the partial numbers with teaching value; they
do not have it. A partially applied step is an artifact of the order the
five sub-exchanges were applied in - step 5 having run against step 2's
output - not evidence of where the model broke down. The diagnosis belongs
in the `SimulationNumericalError` message, where it can say which invariant
failed at which step size, and where a reader can act on it.

The one real risk in rollback is a snapshot that silently stops covering
everything: a field added to a compartment later, with no matching capture,
would leave a partial restore that looks like a complete one. That is why
capture belongs on each compartment rather than in `RespiratorySystem` - a
missing field is then a local, reviewable omission - and why the regression
test asserts bit-identical state rather than approximate agreement.

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
