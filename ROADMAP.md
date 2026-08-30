# Project roadmap

This file is the authoritative version and milestone map for the project. If a
build guide, issue, or conversation conflicts with this file, update the
conflicting artifact or amend this file deliberately in the same change.

Scope of this file: releases only. Discrete tasks — defects, fixes,
cleanups, optimizations, and small features — are tracked and prioritized
in `docs/items/`, not here. An item is a milestone rather than a
queue item when it needs its own goal, required scope, definition of
done, and explicit out-of-scope list.

## Versioning decision

The project uses milestone-based semantic versioning during early development.
The next release number is chosen for the capability boundary it crosses, not
by mechanically incrementing the patch number.

**One deliberate exception, v0.3.0 (project owner, 2026-08-26).** That rule
would make clearing Gate 0 a patch: it crosses no capability boundary — two
safety fixes, four refactors, two tooling defects and a perf fix, after which
the simulator does nothing it could not do before. It is nonetheless released
as the minor v0.3.0, because clearing the inherited pre-MVP backlog is the
boundary this project most needs to be able to point at, and a patch number
would bury it.

**This is an exception and not a precedent.** It applies to Gate 0 alone,
which is unlike every gate that follows it: Gate 0 is the accumulated backlog
from before the debt gate existed, twenty items deep, while Gate 1 onward hold
the findings of a single milestone. Later gates ship *inside* the milestone
they gate and take no version of their own — see "The cadence" under "The
debt gate". Absent a further deliberate exception recorded here, the
capability-boundary rule above governs.

| Version | Status | Milestone |
| --- | --- | --- |
| v0.0.1 | Completed | Initial runnable prototype: deterministic simulation clock, controller/view separation, basic charting and controls, and project quality tooling. |
| v0.0.2 | Completed | Analytically validated ideal breathing-circuit wash-in and washout with no patient uptake. |
| v0.1.0 | Completed | First patient sevoflurane uptake and distribution model - the "Sevo works" milestone. |
| v0.2.0 | Completed | Isoflurane and desflurane added as additional loadable volatile agents. |
| v0.2.1 | Completed | Validation hotfix: the vaporizer maximum is enforced in the core and rejects rather than clamps, the agent MAC cross-check fails closed, and the cited reference-adult defaults reach the running app. |
| v0.2.2 | Completed | Hardening and interface-provenance release on the same model: a failed step halts the run visibly instead of leaving it reading "Running", the parameter schemas reject unknown keys, agent selection carries its ISO 5360 identification color, and a dead non-conservative ventilation path is deleted. |
| v0.2.3 | Completed | Hardening and verification release on the same model: displayed concentrations are rounded to the resolution the solver actually supports, the chart payload is bounded and the render cadence decoupled from the simulation's, and the coupled dynamics are gated on an independent RK4 solution rather than on mass balance alone. Six further items rebuilt the development queue, swept the documentation, and recorded release provenance. |
| v0.2.4 | Completed | Verification and delegation release on the same model: fourteen previously untested capacity and validation guards in the scientific core and the controller now have tests, `_halt_run`'s deliberate suppression is covered by a test rather than only a comment, and work whose success a command can prove can be handed to a cheaper model and verified in one step. |
| v0.2.5 | Completed | Licensing, documentation and planning release: the project is licensed Apache-2.0, v0.3.0 through the MVP is scoped onto one timeline with its debt gates, Phase 0 is retired in favour of the standing debt gate, and `docs/worker.md` states what a delegated worker decides for itself. No source file changed. |
| v0.2.6 | Completed | Delegation and release-tooling release on the same model: work whose success a command can prove now has to name that command and have run it, `docket` computes the debt gate and the cadence beat instead of a session transcribing them, and the release path itself stopped breaking `make check` and leaving this table behind. The one scientific item widened the splitting-error bound to the whole settings envelope. No equation, parameter, or numerical method changed. |
| v0.2.7 | Completed / current baseline | Session-discipline and applicability-domain release on the same model: the simulation step now refuses inputs outside the operator split's stated applicability domain and the splitting-error bound is measured across setting changes rather than one held operating point, while ten process items closed the three channels by which product work leaked into discussions that were not about it, gave multi-step instructions a written standard, and cleared three live tooling defects. No equation or parameter changed, and the numerical method is unchanged - it is now guarded at the domain it was always specified for. |
| v0.3.0 | Planned / scoped | The foundation: Gate 0's inherited backlog cleared — the splitting-error bound widened across setting changes, the simulation step made transactional and bounded to the split's applicability domain, the `core/` boundary refactors, and the live tooling defects. No new capability; see the versioning exception above for why it is a minor. |
| v0.4.0 | Planned / scoped | The teachable case: compressed playback at a fixed simulation step, MAC multiples as a displayed unit, a case-length time base, and a recorded control-input timeline. No equation, parameter, or numerical-method change. |

**Tags.** v0.0.1, v0.0.2, v0.2.3, v0.2.4, v0.2.5 and v0.2.6 carry annotated tags.
`bin/docket release` now refuses to cut a release while the version it is
releasing from is untagged, so the practice cannot lapse again (PL-J3ZK).

**Four versions are untagged, in two different situations.** v0.2.1
(`bc5f823`) and v0.2.2 (`3099980`) are settled and only await the two
commands, which PL-J3ZK records. v0.1.0 and v0.2.0 are an open decision in the
same item: it recorded them as untaggable because `main` had three unrelated
roots and `git merge-base 796bf4f 97cc66a` returned nothing, but that was
measured in a shallow checkout, where boundary commits report as parentless.
In the full history there is one root, and `97cc66a` (v0.1.0) is an ancestor
of `796bf4f` (v0.2.0), which is an ancestor of `bc5f823` — so tagging them
would work after all. Nothing is lost by deciding later: all four commits are
ordinary ancestors of `main` and can be tagged at any time.

There is no active v0.0.3 milestone. Any guide that labels the first patient
sevoflurane build as v0.0.3 is superseded by this roadmap.

## Current baseline: v0.2.7

v0.2.7 is a session-discipline and applicability-domain release on the v0.2.0
model, carrying fourteen items. Four are scientific or safety-classed: the
simulation step refuses an input outside the operator split's stated
applicability domain rather than integrating past it (PL-VP7N), the splitting
error is bounded across setting changes instead of one held operating point
(PL-SLHS), the two-decimal readout was re-decided against that widened
measurement (PL-74TX), and the cardiac-output slider's lower bound was settled
(PL-629Z).

The remaining ten are process work, and they share one subject: keeping a
session's output addressed to the question it was asked. Three separate
channels sent simulator work into discussions that were not about it - the
release offer and the "what next" ranking (PL-36SC), and the gate-progress
report, which fired on every closed item and now fires only for items the gate
contains (PL-5GFK). Multi-step instructions gained a written standard in
`.claude/rules/instruction-writing.md` (PL-R5GN), the closing action block
carries its order structurally rather than annotating it (PL-HZC2), and an
action the owner must take outside the repository now arrives as its exact
steps (PL-5Q71). The session digest surfaces the roadmap beat, not only the
queue (PL-F58L), a branch is no longer pushed before the discussion has settled
(PL-FY68), and the two readings of the gate's re-entry rule were reconciled
(PL-9PMV). Two tooling defects were live and silent: `make docket` was a phony
target with no recipe (PL-ZRFC), and `docket verify` defaulted to a local `main`
that a fresh checkout leaves stale (PL-0999). Full notes are in
`docs/releases/v0.2.7.md`.

Like every release since v0.2.0 it changes no equation, parameter, or
numerical method: `docs/MODEL.md`'s specification of the model is unchanged,
and the v0.0.2 circuit and v0.1.0 sevoflurane reference tests still pass
unaltered. That is why it is a patch rather than a new minor — it crosses no
model capability boundary, no new agent and no new physiology.

**What the model currently is** is described under "The model as it stands"
below, and does not change release to release while the patch series
continues.

### Release narrative

v0.2.5 was a licensing, documentation and planning release carrying seven
items and changing no source file. The project became licensed Apache-2.0;
v0.3.0 through the MVP was scoped onto one timeline with its debt gates ("The
plan" below); Phase 0 was retired in favour of the standing debt gate; and
`docs/worker.md` came to state what a delegated worker decides for itself
before what it may not touch.

v0.2.4 was a verification and delegation release. Fourteen previously
untested capacity and validation guards in the scientific core and the
controller gained tests; `_halt_run`'s deliberate suppression became covered
by a test rather than only a comment; and work whose success a command can
prove became handable to a cheaper model and verifiable in one step.

The per-release detail below is history rather than current state, kept for
the reasoning behind each change; the one-line item lists are in
`docs/releases/`. Only the section heading above tracks which release is
current, so adding a release means adding a paragraph here and editing one
heading — not restating the baseline in three places, which is what left this
file naming v0.2.3 as current two releases on (PL-SWFM).

v0.2.3 was a hardening and verification release carrying nine queue items,
three of which reach the running application:

- **PL-040.** Concentrations were rendered to thousandths of a percentage
  point, but the shipped operator split disagrees with an independent
  solution by 1.7e-3 percentage points at default flows and 1 MAC and 1.2e-2
  at the corner of the slider envelope, so two of the three displayed
  decimals were solver noise presented as model output. Every modeled
  concentration and the delivered-agent setting now read at a fixed 0.01
  percentage points, with a positive value that would round to `0.00%` shown
  as `<0.01%` so an empty compartment stays distinguishable from an
  unresolved one.
- **PL-001.** The chart was handed the entire recorded history every frame
  while its axis only ever showed the last window, so frame cost grew with
  run length and redraws overran the frame budget after about 90 s of
  simulated time. The payload is now bounded and decimated to a fixed
  per-trace budget, and stepping the model is independent of drawing it.
  Nothing about the simulation's own time step changed.
- **PL-023.** Mass balance could not detect a wrong rate: every internal
  transfer is applied as an equal-and-opposite pair, so the accounting
  residual stays at ~2e-15 L whatever the rates are — scaling the
  circuit/alveolar exchange by 1.01 left all 345 tests green. An independent
  RK4 oracle that re-derives the `docs/MODEL.md` equations from the parameter
  files now runs in CI (`tests/reference/test_coupled_dynamics.py`) and
  requires all six states to agree across the three agents at 60 s, 600 s and
  3600 s; the same mutation fails 8 of its 22 cases. The tolerance is a bound
  on the first-order splitting coefficient rather than a value fitted to
  today's run.

The remaining six are documentation and development-infrastructure work:
PL-008 swept the documentation to match what the interface actually does,
PL-033 added the reference patient's 70 kg to `docs/MODEL.md`'s provenance
table with a statement that no equation consumes it, and PL-3QGR, PL-041,
PL-032 and PL-034 replaced the single-file punch list with the per-item queue
in `docs/items/`, mechanized the decidable half of the close-out
documentation sweep, and split the queue workflow between `CLAUDE.md`, the
skill and the tool. Full notes are in `docs/releases/v0.2.3.md`.

The preceding v0.2.2 was a hardening and interface-provenance release on the
same model, changing no equation, parameter, or numerical method either. It
carried four queue items:

- **PL-018.** A failure inside a step no longer leaves the interface reading
  "Running" over numbers that have stopped advancing. A run now has a third
  state, halted; `SimulationSnapshot` carries a `failure_reason`; the
  interface labels the run "Stopped — simulation error" and warns that the
  values shown may not reflect a completed step; and Reset clears it. `core/`
  raises one documented exception hierarchy for this path. What a halted run
  should *display* beyond that banner is a separate open question (PL-026).
- **PL-021.** The agent and patient parameter schemas reject unknown keys
  rather than ignoring them, so a misspelled or obsolete field in a data file
  fails loudly instead of silently leaving a default in place.
- **PL-002.** Agent selection carries each agent's ISO 5360:2016 Table 2
  identification color, with its Munsell-original-to-Pantone-to-sRGB
  provenance chain and the measured deviation of each screen approximation
  recorded in `docs/MODEL.md`. The agent name appears everywhere the color
  does, so color is never the only cue.
- **PL-022.** `AlveolarCompartment.advance_ventilation` — a dead,
  non-conservative single-mechanism path that no shipped code called — is
  deleted.

The preceding v0.2.1 was a validation hotfix on the v0.2.0 model, likewise
changing no equation, parameter, or numerical method. It closed three defects
found by the architecture review of the v0.2.0 baseline (PL-015, PL-016,
PL-017): a delivered concentration above the agent's real vaporizer maximum
is rejected by `core/`, at construction and at every change, rather than
clamped in the controller; the agent-file check that 1 MAC is deliverable
runs after every field is populated, so field declaration order cannot defeat
it; and the controller no longer keeps its own copies of the reference
adult's cited ventilation and cardiac-output defaults, so the data file is
what the app actually runs. The review harness that reproduces these findings
is in `tools/review-verification/`.

### The model as it stands

The repository currently models patient uptake and distribution for
sevoflurane, isoflurane, or desflurane: a constant-volume breathing circuit,
an alveolar gas compartment, cardiac-output-dependent perfusion to
vessel-rich, muscle, and fat tissue groups, and mixed-venous return, coupled
back to the lungs. Every compartment step is solved by exact analytic
solution and composed by operator splitting; the v0.0.2 circuit and v0.1.0
sevoflurane reference tests are preserved unchanged. Agent and
reference-adult parameters are loaded from schema-validated, cited data
files rather than hardcoded. Full equations, units, assumptions, parameter
provenance, numerical method, and known limitations are documented in
`docs/MODEL.md`.

A basic agent-selection control was added to the interface after the v0.2.0
milestone closed (commit `00791b1`, outside that milestone's scope — see its
out-of-scope list below). It restarts the run at the selected agent's own
1 MAC rather than switching agent mid-run: residual-agent washout across a
switch, and the interlock behavior that governs it on a real machine, remain
the anesthesia-machine milestone's work.

The current model does not include mid-run agent switching, other volatile
agents beyond these three, metabolism, IV anesthetics, effect-site models,
or clinical predictions or recommendations of any kind. See
`docs/MODEL.md`'s "Known limitations" for the complete list.

## The plan

One timeline. Debt clearing and feature milestones are steps on the same
plan, in the order they happen — the gates are not a background assumption
behind the features, they are half the work.

### What MVP means here

**The MVP is complete when a learner can run a case, branch it at a decision
point, and compare the two managements side by side — in the unit clinicians
reason in, on a time base that spans a case.**

That is the Graph and the Overlay of the Gas Man reference simulator, which
is the design this project is building on. Everything after it extends a
working teaching tool rather than working toward one. The boundary is drawn
there because comparison is what isolates the variable under study: running
one case teaches a curve, and running the same case two ways teaches why the
curve moved. A simulator that cannot do the second is a demonstration, not a
teaching tool.

Two *feature* releases reach it, and both are interface releases on the
existing, already-validated model — preceded by v0.3.0, which adds no
capability and exists to clear the ground they are built on:

- **v0.3.0, the foundation** — Gate 0's inherited backlog cleared. No new
  capability; see the versioning exception under "Versioning decision".
- **v0.4.0, the teachable case** — one case end to end, in clinical units, at
  a speed and on a time base that make its lessons observable at all.
- **v0.5.0, the case you can branch** — bookmarks, forking from them, and
  side-by-side comparison of the branches.

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.3.0 — the foundation** | Gate 0's frozen debt list, recorded under v0.4.0 below: the 14 items outside that milestone's own scope, released as a minor by deliberate exception. | 2 M, 12 S |
| — | **v0.3.x — `core/` reads like the domain** | Planned-milestone item 29. A patch, not a milestone: no behavior changes. Placed here deliberately, ahead of the substance generalization that would otherwise force the vocabulary to be invented and restructured at once. Not yet scoped. | — |
| 2 | **v0.4.0 — the teachable case** | Scoped below. 11 items, of which 6 are gate-0 debt the milestone clears itself. | 5 M, 6 S |
| 3 | **Gate 1** | Frozen when v0.5.0 is scoped. Contents unknown by construction: v0.4.0's own findings land here. Ships inside v0.5.0, not as its own release. | — |
| 4 | **v0.5.0 — the case you can branch** | Planned-milestone items 8 (replay half), 26 (bookmarks), 12 (forking), 11 (comparison). | — |
| — | **MVP complete** | A learner can run, branch, and compare a case. | — |
| 5 | **Gate 2** | Frozen when v0.6.0 is scoped; ships inside it. | — |
| 6 | **v0.6.0 — the schematic** | Planned-milestone item 27: Gas Man's Picture, showing where the agent *is* rather than where its tension is. | — |
| 7 | **Gate 3** | Frozen when v0.7.0 is scoped; ships inside it. | — |
| 8 | **v0.7.0 — multi-substance and nitrous oxide** | Planned-milestone items 6 and 7, and the substance generalization Phase 1 describes. | — |
| 9+ | **Beyond** | The machine and its interlocks (items 1-5), save/load and replay (9, 10), then intravenous agents (13-15), in "Development pathway" order. | — |

**Only row 1 is a release of gate work.** Gate 0 earns v0.3.0 because it
clears the backlog inherited from before the debt gate existed; Gates 1
onward hold one milestone's findings and ship inside the milestone they gate,
which is why rows 3, 5 and 7 carry no version. The reasoning, and the fact
that this is an exception rather than a pattern, is under "Versioning
decision" above.

Rows 4 to 8 are the intended order and are not yet scoped; each becomes real
only when it gets its own goal, required scope, definition of done and
out-of-scope list here, per the development rules. Row 4's internal ordering —
forking and comparison ahead of save/load and replay — is a deliberate
departure from "Development pathway"'s Phase 3 sequence, on the grounds that
branching within one session is the teaching payload while persistence is a
convenience; it is recorded here as a proposal rather than a decision, and
Phase 3's stated order stands until v0.5.0 is scoped.

### Why the gates are on this list and not behind it

A gate that lives in a separate document, or in a session's memory, is
renegotiated every time it is inconvenient. Put on the timeline it is a step
with a size, and skipping it is visible as skipping a step. The cadence that
generates rows 1, 3, 5 and 7 is specified under "The debt gate" below; the
rule is that scoping a milestone freezes its gate, and the gate clears before
that milestone's implementation begins.

## Completed: v0.1.0 - first patient sevo model

### Goal

Extend the existing circuit model into the smallest useful, testable
volatile-anesthetic patient model:

```text
delivered sevo -> breathing circuit -> alveoli -> blood
               -> vessel-rich group / muscle / fat -> mixed venous return
```

This milestone uses sevoflurane only. It should demonstrate recognizable
wash-in, uptake, tissue distribution, mixed-venous return, and washout while
preserving deterministic behavior and explicit units.

### Required scope

- Keep the v0.0.2 circuit model and its analytic regression tests.
- Add an explicit alveolar gas compartment driven by alveolar ventilation.
- Add sevoflurane blood:gas and tissue:blood partition data with source
  provenance and validation.
- Add cardiac output and perfusion-limited vessel-rich, muscle, and fat tissue
  groups.
- Compute mixed-venous return from tissue outflow and couple it back to the
  lung-blood exchange.
- Allow fresh gas flow, delivered sevo concentration, alveolar ventilation,
  and cardiac output to change during a run without resetting state.
- Expose at least delivered, circuit/inspired, alveolar/end-tidal, and
  mixed-venous or representative tissue concentrations in snapshots and the
  interface.
- Track agent delivered, exhausted, and stored in gas, blood, and tissue
  compartments so mass balance can be checked within a documented numerical
  tolerance.
- Preserve explicit simulation time, deterministic results, and separation of
  the scientific core from Flet.
- Document equations, units, assumptions, parameter sources, numerical method,
  and model limitations in `docs/MODEL.md`.
- Add unit, integration, invariant, and independent reference tests before the
  release is tagged.

### Definition of done

v0.1.0 is complete only when:

- the locked Python 3.14 environment passes Ruff formatting and linting, strict
  mypy, pytest, and GitHub Actions;
- the v0.0.2 circuit reference behavior remains unchanged;
- zero-flow and zero-ventilation limits behave safely;
- concentrations remain finite and nonnegative;
- increasing ventilation or cardiac output produces the expected directional
  effects in documented reference scenarios;
- wash-in and washout are stable across supported step sizes;
- total sevoflurane mass closes within the stated tolerance;
- Start, Pause, Reset, and live parameter changes behave deterministically;
- the user interface states that this is an educational model, not a clinical
  prediction; and
- no deferred feature has entered the release accidentally.

All criteria above were met at tag time; see `docs/MODEL.md`'s "Release
gate" section for the corresponding scientific-documentation checklist.

### Explicitly out of scope for v0.1.0

- Desflurane, isoflurane, nitrous oxide, or simultaneous gases.
- Vaporizer interlocks, agent switching, direct injection, flush, or automated
  end-tidal control.
- Multiple alveolar units, dead space, shunt, or ventilation-perfusion
  mismatch.
- Metabolism, renal or hepatic clearance, ECMO, or cardiopulmonary bypass.
- MAC, BIS/eBIS, nociceptive response, hemodynamic response, or decision
  support.
- IV anesthetics and effect-site models.
- Scenario persistence, replay, comparison, or forking.
- Packaging, signing, or release installers beyond what is needed to run and
  test the milestone.

## Completed: v0.2.0 - isoflurane and desflurane

### Goal

Prove that the v0.1.0 patient model (circuit, alveolar, tissue, and venous
compartments; the governing equations in `docs/MODEL.md`) is agent-generic
rather than sevoflurane-specific, by adding isoflurane and desflurane as
additional validated, data-driven volatile agents with independent
reference cases. No governing equation changes for this milestone; only new
per-agent data and the loading capability to select among agents.

### Required scope

- Add `data/agents/isoflurane.json` and `data/agents/desflurane.json`,
  schema-validated like `data/agents/sevoflurane.json`, with cited
  blood:gas and tissue:gas partition coefficients and source provenance.
- Extend `core/parameters.py`'s agent loading so an agent can be selected
  by id rather than only ever loading sevoflurane
  (`load_sevoflurane_parameters()` is currently the sole, hardcoded path
  `RespiratorySystem.default()` uses). Consider migrating this module's
  JSON validation to Pydantic while touching it: the boilerplate in its
  `_require_*` helpers compounds with each new agent schema, and the
  module is isolated behind plain dataclass returns, so the switch is
  low-risk here.
- Add independent reference tests for isoflurane and desflurane wash-in,
  uptake, and washout, following the same directional-solubility,
  equilibrium, and mass-balance pattern already used for sevoflurane in
  `tests/reference/test_sevo_patient.py`.
- Document both new agents' parameter provenance in `docs/MODEL.md`, and
  note any agent-specific numerical considerations worth recording (e.g.
  desflurane's low blood:gas solubility) even though they don't change the
  governing equations.
- Preserve the v0.0.2 circuit and v0.1.0 sevoflurane reference tests
  unchanged.

### Definition of done

v0.2.0 is complete only when:

- `isoflurane.json` and `desflurane.json` pass the same schema and range
  validation as `sevoflurane.json`;
- each new agent has independent reference tests demonstrating correct
  directional solubility behavior and mass-balance closure within the
  documented tolerance;
- the v0.0.2 circuit and v0.1.0 sevoflurane reference tests remain
  unchanged and passing;
- `docs/MODEL.md` documents both new agents' parameter provenance;
- Ruff formatting and linting, strict mypy, pytest, and GitHub Actions all
  pass.

### Explicitly out of scope for v0.2.0

- A UI control for selecting which agent is running. Agent switching and
  interlock behavior belong to the anesthesia-machine milestone (item 1 in
  "Planned milestones" below); this milestone only needs the model to be
  capable of running as isoflurane or desflurane, not to expose that choice
  in the interface yet. (Recorded as this milestone's scope at tag time. A
  basic picker was in fact added afterwards in commit `00791b1`; it restarts
  the run rather than switching mid-run, so the interlock and
  residual-washout work this excluded is still outstanding.)
- Vaporizer-specific delivery-device physics (e.g. desflurane's heated,
  pressurized vaporizer requirement) — this milestone models uptake and
  distribution only, not the delivery device.
- Halothane, enflurane, ether, or xenon: a further-future stretch beyond
  this milestone. Halothane has reasonable modern published data despite
  being clinically obsolete, but enflurane, ether, and xenon are sparser to
  source and should each get their own provenance check before being
  added, not be assumed available just because the Gas Man reference
  simulator depicts them.
- Nitrous oxide: not a halogenated volatile, so out of scope here; covered
  separately by items 6-7 in "Planned milestones" below.
- Any change to the v0.1.0 governing equations themselves — this milestone
  proves they are agent-generic, not that they change per agent.

All criteria above were met at tag time. `isoflurane.json` and
`desflurane.json` load through the same `load_agent_parameters(agent_id)`
path added for this milestone (`load_sevoflurane_parameters()` is now a
thin wrapper over it, so no existing call site changed behavior);
`tests/reference/test_multi_agent.py` covers directional solubility and
mass-balance closure for both new agents; and `docs/MODEL.md`'s parameter
provenance table and new "v0.2.0: isoflurane and desflurane" subsection
record both agents' sourcing.

## Next milestone: v0.3.0 - the foundation

### Goal

Clear the inherited backlog, so feature work starts from a codebase whose
known defects are closed rather than carried. This release adds no
capability: after it the simulator does what it did before, correctly, with
its verification gate widened to the inputs the interface can actually reach
and its failure path unable to leave partial state behind.

Its contents are exactly Gate 0's items that fall outside the teachable
case's own scope — the fourteen listed under "Debt gate: the frozen list" in
the v0.4.0 section below. It has no scope of its own to specify, which is why
this section is short: the frozen list *is* the specification, and nothing
may be added to it (see "The gate is a snapshot, not a moving target").

It is a minor rather than a patch by deliberate exception, recorded under
"Versioning decision" above. That exception covers Gate 0 alone.

### Definition of done

- Every item on Gate 0's frozen list that is outside the v0.4.0 milestone's
  Required scope is `done`, or `dropped` with its reason recorded.
- `make check` passes: `ruff format`, `ruff check`, `mypy`, `pytest`,
  `docket check`, and `tools/doc_check.py`.
- No equation, parameter, or numerical method has changed, and the v0.0.2
  circuit and v0.1.0 sevoflurane reference tests still pass unaltered. The
  two safety items on the list tighten a verification bound and make the step
  transactional; neither is licensed to change a modelled value, and if
  either turns out to require one, that is a finding for the next gate and a
  scoped item of its own, not this release's work.

### Explicitly out of scope for v0.3.0

- Anything in the v0.4.0 milestone's Required scope, including the six gate-0
  items that milestone clears itself.
- Any item captured after Gate 0 was frozen whose problem did not already
  exist at the freeze. A finding that *was* present re-enters by the
  presumption in "The gate is a snapshot, not a moving target", as does
  anything at `P0` or classed `safety`/`science` regardless of presence. This
  bullet previously named only the `P0`/`safety`/`science` half, which made it
  narrower than "The gate is a snapshot" and than step 4 of "The cadence";
  those two agreed with each other and this one did not (queue item PL-9PMV).
- New capability of any kind. A release whose whole claim is "the ground is
  now solid" cannot also be the one that moves the ground.

## Milestone after next: v0.4.0 - the teachable case

### Goal

Make the model teachable. The science is sound and its lessons are currently
unreachable, for three measurable reasons:

- the run advances at 1x real time (`app/simulation_view.py`, one 0.1 s step
  per 0.1 s sleep), while the compartments that make uptake and distribution
  worth teaching have time constants of 135 min (muscle) and 42 h (fat) for
  sevoflurane at reference settings - so the reservoirs that cause
  context-sensitive emergence cannot be observed at all;
- the chart shows a rolling five-minute window on an axis labelled in
  seconds and scaled to the vaporizer's dial maximum, so a 1 MAC run occupies
  the bottom quarter of the plot and everything slower than the vessel-rich
  group scrolls away flat; and
- every value is a percentage of an atmosphere, so three agents whose MACs
  differ threefold are displayed as though their numbers were comparable.

The end state: a learner runs one case from induction to emergence - in
compressed time they can sit through, in the unit clinicians reason in, on a
time base that spans a case - changes something, sees on the record when they
changed it, turns the vaporizer off, and watches it come down against a
labelled reference.

This milestone changes no equation, parameter, or numerical method. It is a
minor rather than a patch because it adds a displayed clinical unit, a new
time base, and a run-rate control: capability boundaries in what the
interface asserts, even though the model behind them is untouched.

It promotes planned-milestone item 25 (playback multiplier) in full and the
recording half of item 8 (control-input timeline). It does not promote item
26 (bookmarks) or item 12 (forking), but it is designed so that neither is
blocked - see "Designed for forking" below.

### Debt gate: the frozen list

**Frozen 2026-08-25, the day this milestone was scoped.** Twenty open items
are debt by "The debt gate" below — classed `defect`, `safety`, `science`,
`refactor` or `perf`, or at `needs-decision`. Six of them are inside this
milestone's own Required scope and are cleared by it, per "Debt inside the
milestone's own scope". The other fourteen clear before implementation begins.
The list itself stays frozen; an entry records its own outcome as it closes,
per "The cadence" below.

**Cleared before v0.4.0 begins — 20 entries, 21 item ids** (14 and 15 at the
freeze; six were added later, per the two notes beneath this list). These are
exactly what v0.3.0, the foundation release, ships.

Count entries, not ids: the PL-Z4GF/PL-SWFM entry below holds two ids for one
problem, so both numbers above are true and only the first is the gate's size.

How many of them are closed is **not recorded here**, because a count written
into a document is a count that goes stale the next time an item closes — this
paragraph said "5 done and 9 remaining as of 2026-08-26" while one of the nine
it named had already been closed. `bin/docket wave` reads the entries below
against `docs/items/` and reports the split, so the answer is computed from the
same files that would be used to check it.

*Core correctness — all safety- or science-classed, all wanting the
strongest model:*

- PL-026 (M) Make the simulation step transactional so a halt leaves no
  partial state
- PL-042 (S) Bound the splitting error across the settings envelope, not one
  point
- PL-VP7N (M) Refuse a simulation step outside the operator split's
  applicability domain. Added after the freeze; see below.
- PL-SLHS (S) Bound the splitting error across setting changes, not one held
  operating point. Added after the freeze; see below.
- PL-9Y42 (S) Validate wash-in against a published human measurement. Added
  after the freeze; see below.

*Presentation safety — `safety`-classed, and the one entry whose defect is not
in `core/`:*

- PL-NV9W (S) Label the alveolar readout end-tidal-equivalent, as
  `docs/MODEL.md` requires. Added after the freeze; see below.

*Core boundaries — the whole `core-boundaries` feature, all `refactor`:*

- PL-006 (M) Clarify what `RespiratorySystem` actually owns
- PL-004 (S) Decide the fate of the two uncalled descriptive time constants
- PL-007 (S) Make the payload/public-dataclass pattern self-evident in
  `core/parameters.py`
- PL-019 (S) Remove `BreathingCircuit`'s agent-unaware delivered-concentration
  default

*Live process machinery that does not reliably work — `defect` by the rule
under "What counts":*

- PL-G049 (S) A `verify:` command that has never been run is not a
  specification
- PL-674D (S) `docket release` bumps `pyproject.toml` but leaves `uv.lock`
  stale, breaking `make check`
- PL-0RFH (S) `docs/worker.md` buries the carve-out that lets a worker decide
  anything at all
- PL-R0SR (S) `docs/worker.md` should say that corrections arrive by pulling
  the branch, never in chat
- PL-4F6P (S) A `**Worked.**` note said "nothing the brief did not specify"
  for a test that reached into a private class
- PL-N2N1 (S) — **done** (commit `ebefcc2`). `docket release` does not update
  this file's version table or baseline heading. Added after the freeze; see
  below.
- PL-K79K (S) — **done** (commit `54bdb5b`). The session-start digest told
  every session to run `bin/docket triage`, which did not exist. Added after
  the freeze; see below.

**Two entries added 2026-08-30 under the presence rule, both cleared in the
same batch that added them.** Per "The gate is a snapshot, not a moving
target", a finding re-enters this gate when the problem it describes was
already present at the freeze, whatever id it is filed under or however long
after the freeze it was noticed.

The first continues the PL-Z4GF/PL-SWFM entry's scope: the same document
drifting for the same reason, this time its mechanism half rather than one
more instance of it. That entry is the case the presence rule was written for.

The second advertised a command that does not exist, and had done so since
`6f1b5b1` on 2026-08-24 — the day before this list was frozen. Present at the
freeze by date, and `defect` by "What counts" above: a live mechanism `main`
depends on that does not work.

Neither extends what the gate has left to run: both are closed.

**Four entries added 2026-08-30 from an outside review of the repository,
which recorded nothing of its own.** All four re-enter this gate rather than
deferring to Gate 1, on both of the grounds "The gate is a snapshot, not a
moving target" allows, and they are the only findings of that review that do:

- *By the presence rule.* Each describes a problem present in the tree before
  2026-08-25. `core/` has never had an upper bound on the simulation step; the
  splitting-error gate has held one operating point constant since it was
  written; nothing in the repository has ever been compared to a published
  human measurement; and the unhedged `"Alveolar / end-tidal"` label has been
  in the interface since `74bec83` on 2026-08-23, two days before the freeze.
- *By the safety/science exception.* PL-VP7N is `safety`, PL-SLHS is
  `safety`/`science`, PL-9Y42 is `science`, PL-NV9W is `safety` — the classes
  this milestone's out-of-scope list names as re-entering regardless of when
  they were captured.

PL-NV9W was added three entries later than the others, and the delay is worth
recording because it shows where the rule is easy to miss. The review proposed
it at `P2`, which would have left it outside the exception; `docket check`
refuses to seat a `safety`-classed item below `P1`, so triaging it honestly
raised it — and *that* is what brought it inside this rule. The consequence was
followed through once the project owner confirmed the priority. A finding's
gate membership can therefore change as a side effect of classing it correctly,
which is a thing to check at triage rather than only at capture.

Unlike the two entries above, these four do extend what the gate has left to
run, by four items. That is the rule working as intended rather than a gate
being widened: each is a statement `docs/MODEL.md` already makes that the
implementation does not keep, and v0.3.0's whole claim is that the ground is
solid. Shipping that release with a `must fail` that does not fail, a release
bound a shipped trajectory exceeds, and no validation against a human
measurement would make the claim untrue on the day it was made.

The ten other findings from the same review are in the queue and clear at
Gate 1: they are either post-freeze in substance, or classed outside the
exception.

**One presence-qualifying finding deliberately deferred to Gate 1.** PL-WB0X
(split `simulation_view.py`) describes a module that has been oversized since
long before the freeze, so the presumption admits it. It is deferred anyway,
which "The gate is a snapshot" permits provided the reason is stated: it is an
`M` restructure of the interface layer with no connection to anything on the
frozen list, and v0.3.0's claim is that it adds no capability and clears only
inherited debt. Pulling in unrelated pre-existing debt because it is old is
the refilling-queue problem the gate replaced Phase 0 to solve. Its own brief
records where it does belong — a `v0.3.x` patch step, staged against the
interface work that follows.

*Documentation, performance, and the one decision that is the project
owner's:*

- PL-Z4GF **and PL-SWFM** (S) — **both done** (commits `d40ff83`, `6e19632`).
  One entry holding two ids: PL-Z4GF closed the README half of its original
  scope, and the remainder — this file's own duplicated v0.2.3 table row and
  stale "Current baseline" heading — surfaced later under the separate id
  PL-SWFM. Per "The gate is a snapshot, not a moving target" and its presence
  rule below (project owner, 2026-08-25), that problem was already inside
  this frozen scope, so it cleared here rather than at the next gate,
  regardless of which id or session it surfaced under.
- PL-010 (S) Stop rebuilding render objects on every frame
- PL-Y2GG (S) — **done.** Apache-2.0, chosen by the project owner (commit
  `d40ff83`).

**Cleared by v0.4.0 itself (6 items).** Each appears in Required scope above:
PL-DHV7 (MAC as a displayed unit), PL-VM40 (simulated time from a step count),
PL-F52R (the MAC-awake reference band), PL-ZRSP (the F_A/F_I trace), PL-R3KB
(agent selection discarding a run), PL-011 (bounding the concentration
history).

Findings made while clearing this gate go to Gate 1, except `P0` and
`safety`/`science` findings, which re-enter here.

### Required scope

- **Simulated time becomes an exact function of step count.**
  `SimulationState.elapsed_s` accumulates `+= simulation_step_s` per step
  today; derive it from an integer step counter instead, and fix the step at
  0.1 s. The run loop advances a fixed number of steps per tick and never
  catches up to the wall clock: a slow machine runs slower, it does not run
  differently.
- **A playback multiplier**, implemented as steps per tick and never as a
  larger step, with the current rate visible beside the clock at all times.
- **MAC multiples as a display unit** across every readout and both chart
  axes, alongside percent, with the agent's `mac_percent` provenance
  traceable from the display (queue item PL-DHV7).
- **A case-length time base**: minutes rather than seconds, selectable 15,
  30 and 60 minute scales plus a fit-the-run scale (queue item PL-SSBP).
- **A vertical scale that fits the run** rather than the vaporizer's dial
  maximum. In MAC mode the axis becomes agent-independent, which is what
  makes a cross-agent comparison honest.
- **A recorded control-input timeline**: every fresh gas flow, vaporizer
  dial, alveolar ventilation and cardiac-output change stamped with the
  simulated time it took effect, held with the state it describes, and
  marked on the chart. The recording half of planned-milestone item 8, not
  the replay half. Recorded as `(simulated_time, control, value)` entries
  rather than a fixed struct of named controls: nitrous oxide (planned item
  6) adds a control this milestone cannot enumerate in advance, and a struct
  would need a field added — and every past sample migrated or left with a
  meaningless default — when it lands. A tuple form costs nothing today and
  needs no such migration later.
- **`SimulationHistorySample` keyed by substance, not by six flat named
  compartment floats.** There is exactly one substance today, so this
  changes representation, not behavior. It matters because item 12
  (forking, promoted below to "Designed for forking") writes its
  element-wise reproducibility proof directly against this record's shape:
  reshaping it *after* that proof exists means reworking an
  already-validated safety property instead of a plain refactor. Nitrous
  oxide (planned item 6) needs a second substance in the same record, and
  the MAC readout becomes a fold over it rather than a rewrite.
- **Changing agent becomes an explicit new case** rather than a selector
  that silently discards the run and its history (queue item PL-R3KB).
- **A MAC-awake reference band** on the chart: a cited population median for
  return of responsiveness, drawn as a band and labelled as a population
  reference, never as a per-patient time prediction.
- **An F_A/F_I trace**, the ratio the uptake literature plots, with the
  interpretive caveat that it means what the textbook curve means only while
  inspired concentration is held constant.
- **A bounded concentration history** (queue item PL-011), which stops being
  optional once a four-hour run at 10 Hz records 144,000 samples.
- **A documentation sweep**: `docs/MODEL.md`'s interface boundary, minimum
  displayed outputs and displayed-precision sections, and `README.md`.

### Designed for forking

Forking a case at a point on it, to compare two managements of the same
patient, is planned-milestone item 12 and is not built here. Item 12's
required property - a branch reproduces its parent exactly at every recorded
sample up to the branch point, element-wise rather than within a tolerance -
is expensive to retrofit and cheap to preserve, so this milestone preserves
it:

- deriving elapsed time from an integer step count removes the accumulation
  order that would otherwise make a resimulated prefix differ from a
  straight-through one;
- fixing the step at 0.1 s regardless of playback rate removes the step-size
  divergence;
- never catching up to the wall clock removes the machine-speed dependence
  in the number of steps taken, which is the subtlest of the three and would
  otherwise make every run irreproducible on a different computer; and
- the control-input timeline is what lets a point *between* recorded samples
  be reached by resimulation at all; and
- the substance-keyed history record (above) is what keeps item 6 (nitrous
  oxide) from reshaping the record item 12's reproducibility proof is written
  against, after that proof exists.

What is deliberately *not* designed for in advance: per-compartment agent
amounts in the snapshot, a schematic view, run comparison, or a snapshot
policy. Those are cheap to add when their milestone arrives, and adding
unused structure now would be speculative generality rather than
groundwork. The distinction is whether retrofitting invalidates recorded
runs or merely adds a field.

### Definition of done

v0.4.0 is complete only when:

- two runs given identical inputs produce element-wise identical recorded
  history at every playback multiplier, asserted by test, and identical
  history on a machine of any speed;
- the simulation step is 0.1 s at every playback multiplier, asserted by
  test;
- a learner can read every graphed compartment in MAC multiples and in
  percent, and can trace the agent's MAC value to its cited source from the
  display;
- a three-hour case can be run, watched, and read end to end in a few
  minutes of wall clock, with the muscle and fat curves visibly diverging
  from the alveolar one;
- every control change during a run is recorded with the simulated time it
  took effect, and is visible on the chart;
- changing agent cannot discard a run without the user being told what will
  be lost and confirming;
- the MAC-awake band and the F_A/F_I trace each carry, at the point of
  display, what they do and do not assert;
- `docs/MODEL.md` states the MAC transformation, what a MAC multiple on a
  non-alveolar compartment does not claim, the reproducibility guarantee
  above, and the interface's new obligations;
- the v0.0.2 circuit, v0.1.0 sevoflurane and v0.2.0 multi-agent reference
  tests remain unchanged and passing, and no equation, parameter or
  numerical method has changed; and
- Ruff formatting and linting, strict mypy, pytest, and GitHub Actions all
  pass.

### Explicitly out of scope for v0.4.0

- Nitrous oxide, coadministered gases, and the concentration and second-gas
  effects (items 6-7). This milestone is deliberately taken ahead of them;
  see the note in "Development pathway".
- The multi-substance patient state (Phase 1). Nothing here requires it, and
  the view already consumes an immutable snapshot, so the MAC readout is the
  only piece that changes shape when a second substance lands.
- The anesthesia-machine abstraction, interlocks, agent switching with
  residual washout, direct injection, and end-tidal control (items 1-5).
- Run bookmarks (item 26), forking (item 12), save/load (item 9), replay
  (item 10) and run comparison (item 11) - the replay half of item 8's
  timeline included. Only recording is in scope.
- A schematic compartment view (item 27) and agent cost (item 28).
- A second patient, weight-based scaling, age-adjusted MAC, dead space,
  airway sampling delay, or any depth, BIS or effect-site model.
- Horizontal panning of the chart window (queue item PL-Z7LY), which the
  fit-run scale makes optional rather than necessary.

## Development rules for scientific milestones

- Define equations, units, assumptions, and reference cases before changing the
  scientific core.
- Keep simulation code independent of Flet, wall-clock time, filesystem state,
  and display dimensions.
- Store model parameters as validated data with schema version and provenance;
  do not place executable equations in data files.
- Preserve deterministic results for identical initial state, events, and time
  steps.
- Treat mass accounting and independent reference cases as release gates, not
  optional diagnostics.
- Keep each milestone narrow. New ideas belong below until promoted into a
  scoped release — or in `docs/items/` when they are a task rather
  than a release.

## The debt gate

**Recorded technical debt is cleared before a new milestone begins.** Phase 0
applies this once, to get out of a queue that had stopped shrinking. This
section makes it standing: it runs again before every milestone, not only the
first.

The reason is that debt is cheapest to clear while the code it describes is
still the code someone remembers. A defect carried across a milestone boundary
has to be re-diagnosed against a codebase that has since moved, and a decision
left unanswered stops being a decision anyone can make. Deferred debt is not
kept; it is paid for twice or silently dropped.

### What counts

Debt is what the queue already records, minus new work. An open item is debt
when it is classed `defect`, `safety`, `science`, `refactor` or `perf`, or when
its status is `needs-decision` — an unanswered decision is debt whatever it is
about.

An item classed `feature` or `planning` is **not** debt. It is the work the
gate exists to protect, and counting it would make the rule say "do everything
before doing anything", which no gate can open.

**Process work is debt once the mechanism is live, not before.** Building a new
capability into the tooling is new work and does not hold a gate. A mechanism
that `main` already depends on and that does not reliably work is debt, and is
classed `defect` like any other defect — the class carries the rule, so there
is nothing extra to track. The distinction is state, not layer: an unbuilt
tooling idea costs nothing to carry, while a half-working mechanism the project
is already running on charges interest every session, which is what debt means.
Half-finished process machinery must not be in production use; either it is
made to work reliably, or it is abandoned and removed.

A caution the first pass through this got wrong: classing tooling breakage as
`infra` rather than `defect` makes it indistinguishable from a capability
nobody has built yet. `docket release` leaving `uv.lock` stale and breaking
`make check` at every release is a defect; adding release tagging is not. If
the class does not separate them, the gate cannot either.

Clearing means `done` **or** `dropped` with the reason recorded. Deciding
something is not worth doing is a legitimate way to clear it, and often the
right one; what is not legitimate is leaving it open and starting anyway.

### The gate is a snapshot, not a moving target

**When a milestone is scoped, the debt list is frozen at that moment.** A
finding re-enters this gate — rather than waiting for the next one — when the
problem it describes was already *present* at that moment, whatever id it is
filed under or however long after the freeze it happened to be noticed. It
defers to the next gate only when the problem itself is new: introduced by
work done while clearing this gate or implementing the milestone it protects.

This is the part that makes the rule survivable rather than a deadlock. Work
generates findings — clearing thirteen items in one session generated fourteen
new ones, which is normal and is the capture rule doing its job. Against a
gate that reopens for everything noticed after freezing, that is a queue which
can never empty and a milestone which can never start; the rule would then be
abandoned rather than followed, which is worse than not having it. Presence
rather than discovery time is what keeps it from reopening for *that* kind of
finding while still closing the gap where a stranded branch or a slow session
means the same problem gets rediscovered under a new id (queue item `PL-64LS`).

**Presence is a presumption, not an absolute rule.** Favor it: a finding that
continues or completes an item already inside the frozen list belongs to this
gate, recorded with what it continues — `PL-SWFM` continuing `PL-Z4GF`'s
already-frozen scope is the case that motivated writing this down. Where a
specific reason argues otherwise — the finding has no real connection to
anything frozen, or pulling it in would recreate the refilling-queue problem
the debt gate replaced Phase 0 to solve — a session may defer a
presence-qualifying finding to the next gate anyway, or decline to pull in one
that only superficially resembles frozen scope. Either way it must say so and
say why: silently reinterpreting which gate a finding belongs to is the
renegotiation freezing the list exists to prevent.

Two further exceptions re-enter the current gate regardless of presence:
anything at `P0`, and anything classed `safety` or `science`. Those are not
deferrable by this project's own standard, and a gate that let them wait would
be inverting the reason it exists.

### The cadence

The gate is a recurring step on the plan, not a precondition assumed in the
background. Every milestone runs the same four beats, and "The plan" above
shows them on one timeline with the milestones they gate:

1. **Scope** the milestone here — goal, required scope, definition of done,
   explicit out-of-scope list. Scoping is the act that freezes the list.
2. **Freeze and record** the debt list in that milestone's own section, as
   item ids, on the day it was frozen.
3. **Clear** it — every item `done`, or `dropped` with its reason — before
   implementation of the milestone begins.
4. **Implement** the milestone. A finding made while clearing or implementing
   goes to the next gate unless the problem it describes predates the freeze
   (per "The gate is a snapshot" above) or is `P0`/`safety`/`science`, either
   of which re-enters this one.

A milestone whose gate has not been recorded has not been scoped, whatever
else has been written about it.

Which beat is due is computed rather than recalled: `bin/docket wave` reads
the version, the timeline above, the milestone sections and the frozen list
each one records, and reports the step and the beat that leaves. It reports
only what those files decide — not whether a gate should open early, and not
whether what is written beside a step is still true.

**A gate does not get a version.** Cleared gate work ships inside the
milestone it gates: it lands between that milestone's predecessor and its own
release, so the milestone's release notes carry it, and no interim release is
cut partway through clearing. `docket release` will offer one as soon as a
few gate items are finished — decline it, or the gate work scatters across
patch releases and the milestone ships carrying only its feature work.

Gate 0 is the single exception, released as v0.3.0 for the reason recorded
under "Versioning decision". It is exempt because it holds the backlog
inherited from before this mechanism existed; every later gate holds one
milestone's findings and is ordinary maintenance, which is not a thing to
version.

### Debt inside the milestone's own scope

**Debt that the milestone itself exists to clear is cleared *by* it, not
before it.** This carve-out is necessary rather than convenient: v0.4.0 was
scoped in part *because* six safety, science, defect and perf items were all
symptoms of the same thing, and requiring them to be cleared before the
milestone that clears them is a rule with no satisfying order.

The test is whether the item appears in the milestone's "Required scope". If
it does, it is milestone work and is listed in the frozen gate under a heading
that says so; the gate is open when everything *outside* the milestone's scope
is clear. If it does not, it is cleared first, whatever it is about.

This does not weaken the `safety`/`science` re-entry rule above. Such an item
inside the scope is still not deferrable — it just cannot be finished earlier
than the work it is part of, and the milestone's definition of done is what
holds it.

### Recording it

Record the frozen list in the milestone's own section here, as the item ids it
had to clear. A gate nobody wrote down is a gate that gets renegotiated, and
the point of freezing the list is that it cannot be.

## Development pathway

The numbered list below is the catalogue; this is the order it is intended to
be worked in, and why. Phases are groupings of intent, not scoped milestones —
each item still has to be specified individually before implementation, per
the development rules above.

The organizing goal is a mature inhalational simulator before any intravenous
work begins: the science first, then an interface that can actually drive it,
then reproducibility, then IV.

**Phase 0 — foundation. Superseded by the standing debt gate, 2026-08-25.**

Phase 0 is not closed, and on its own terms it cannot be. Its closing
conditions are reproduced below unchanged, followed by their state at the date
above.

Its original text: no new feature work until the existing queue is closed out.
Not because features are unwelcome, but because the last stretch of work felt
like whack-a-mole, and it is worth being precise about why: the queue holds
almost no defects. What it holds is decisions nobody has made. At the time
that was written, nine of twenty-four open items sat at `needs-decision` — over
a third of the queue could not be picked up by anyone, so it never visibly
shrank however much work got done. "All bugs squashed" is not a closing
condition, since absence of defects cannot be demonstrated. These were:

| Phase 0 closing condition | State on 2026-08-25 |
| --- | --- |
| no open item classed `safety`, `science` or `defect` | **Not met.** 6 safety/science and 8 defect-classed items open. |
| no open item classed only as process work (`session-cost`, `docs`, `infra`) | **Not met.** 11 such items open. |
| no item left at `needs-decision` | **Met**, and deliberately unmet again the same day: PL-Y2GG (the license choice) was moved *to* `needs-decision` because it holds a decision only the project owner can make, and recording that is more honest than a `ready` nobody can act on. |
| every outstanding branch merged and a release cut | **Met** for merges — `claude/pl-64ls-promote` is gone from the remote — and v0.2.4 is cut. |

**Why superseded rather than pursued.** The first two conditions ask the queue
to reach zero in categories that every working session refills. The queue held
24 open items when Phase 0 was written and holds 48 now: it doubled during the
period Phase 0 was meant to be draining it, which is not a failure of effort
but the capture rule working as designed. A gate that requires a refilling
queue to empty is a gate that never opens, and the honest outcomes for such a
rule are that it gets quietly abandoned or that it blocks all work forever.

"The debt gate" above is the mechanism that replaced it, and it is strictly
better for the same purpose: it freezes a list at a moment rather than chasing
a moving one, so it is always finite and always openable, and it recurs before
every milestone rather than once. Everything Phase 0 was trying to buy — debt
cleared while the code it describes is still fresh, decisions answered rather
than accumulated — the gate buys on a cadence instead of in one push.

So Phase 0 is retired as a phase. Its unmet conditions are not carried forward
as a backlog; the items behind them are in the current frozen gate, where they
can be worked and finished. Implementing a planned milestone is no longer held
by Phase 0, only by its own gate.

**Phase 1 — scientific maturity.** Generalize the patient's state from one
agent to N simultaneously present substances, then items 6 and 7 (nitrous
oxide, concentration and second-gas effects), then item 1 (machine abstraction
with interlocks), then item 2 (agent switching with residual washout).

The generalization leads because three separate items need the same thing:
holding more than one substance at once, with per-substance kinetics. Agent
switching needs the residual of the old agent while the new one washes in;
nitrous oxide needs a second gas throughout; the second-gas effect needs the
coupling between them. Doing it once, deliberately, is the difference between
one design decision and three special cases.

It also settles the intravenous question without a speculative abstraction.
"A substance with compartmental kinetics and an effect site" is the same shape
an intravenous agent needs, so IV becomes an extension rather than a rewrite —
but only if the generalization is designed as substances rather than as
"volatile agent, plus nitrous oxide as a special case". That framing is a
requirement of this phase, not an optional nicety.

Nitrous oxide sits before any interface work for two reasons: the second-gas
effect is the phenomenon this class of simulator is most used to teach, so
without it there is no credible inhalational simulator to build an interface
on; and it changes the core equations, so an interface built on a single-gas
core would be reworked when it lands.

**Reordering (project owner, 2026-08-25): the teachable case is taken ahead
of Phase 1.** As written below, Phase 1's substance generalization and nitrous
oxide precede all interface work, on the reasoning that an interface built on
a single-gas core would be reworked. That ordering was reconsidered once the
interface was measured against what a learner can actually do with it: the
run advances at 1x real time and the chart spans five minutes, so neither the
muscle nor the fat curve can be observed, and no lesson in uptake and
distribution currently reaches anyone. Building coupled-gas equations first
would produce a more capable engine that still teaches nobody, and would do it
without the feedback from real teaching use that should shape what the
multi-gas display looks like. The rework this accepts is bounded and known:
the view consumes an immutable `SimulationSnapshot`, so the time base,
playback, event marks and axis handling are substance-agnostic, and the MAC
readout - which becomes a MAC sum when a second substance lands - is the piece
that changes. v0.4.0 is that work; Phase 1 follows it unchanged.

**Phase 2 — an interface that can drive the machine.** Consolidate the
display constants named in item 24 first, then item 24 itself, then items 5,
3 and 4 (end-tidal control, override mode, direct injection), then item 8
(scenario events), item 20 (accessibility), item 25 (playback speed), and
item 26 (run bookmarks).

The consolidation leads because item 24 already names it as a prerequisite,
and because every control added before it spreads the same scattered defaults
further.

Item 26 comes last of those because it depends on both: bookmarks are what
make a playback multiplier usable, and their MAC-threshold kind waits on MAC
becoming a displayed unit at all (PL-DHV7 in the queue). Item 8 is the one
Phase 2 entry Phase 3 cannot start without — its control-input timeline is
what save/load, replay and forking each restore from.

**Phase 3 — reproducibility and comparison.** Items 9, 10, 11 and 12 in that
order (save/load, deterministic replay, side-by-side comparison, forking),
on top of item 8's control-input timeline.

This phase is also groundwork, which is why it precedes intravenous work
rather than following it. Save/load and forking both force the whole
simulation state to be explicit and copyable, and that discipline is enforced
by working features rather than by intention — a more reliable foundation for
adding a drug subsystem than any abstraction designed in advance of one.

**Phase 4 — intravenous agents.** Items 13, 14 and 15 (intravenous
pharmacokinetics and effect site, hypnosis/eBIS, nociceptive response).

**Alongside, as opportunity allows.** Items 21 and 22 (performance,
documentation) are continuous rather than phased. Items 16 to 19
(renal/hepatic dysfunction, cardiopulmonary bypass, ECMO, species profiles)
and item 23 (packaging and distribution) are deliberately later: each is an
extension of a mature model rather than a step toward one.

**The known risk** is that Phase 1 front-loads the hardest work in the plan.
Coupled-gas equations with reference cases are real scientific work and the
most likely place to stall. That is accepted deliberately: every milestone
built before the substance generalization is code written against the
single-agent assumption, and would have to be revisited afterwards.

## Planned milestones

This section is the catalogue of intent; "Development pathway" above gives
the order the items are intended to be worked in. Each item is deliberately
left unspecified (no goal, required scope, or definition of done) until it
is actually promoted into a scoped milestone per the development rules
above — and each item is kept to one improvement, so scoping one does not
implicitly drag others along with it. Exact version numbers after v0.2.3
remain provisional and must be assigned when each milestone is fully
specified.

1. Add a modular anesthesia-machine abstraction with normal
   single-halogenated-agent interlock behavior — the safety baseline every
   later machine feature below builds on.
2. Add agent switching with residual washout accounting, after item 1.
   Requires the multi-substance patient state described in "Development
   pathway" — residual washout means holding two agents at once.
3. Add an optional experimental-override mode that can bypass standard
   interlocks, clearly labeled as non-standard, after item 1.
4. Add direct agent injection into the circuit, bypassing the vaporizer and
   its interlocks, after item 1.
5. Add automated end-tidal control (closed-loop titration to a target
   end-tidal concentration), after item 1.
6. Add nitrous oxide coadministration as a second inhaled gas, only after
   coupled-gas equations and reference cases are defined. Model the patient's
   state as a set of substances rather than as a volatile agent with nitrous
   oxide bolted on: the same generalization is what items 2 and 7 need, and
   what decides whether item 13 is an extension or a rewrite.
7. Add concentration and second-gas effects for coadministered gases, after
   item 6.
8. Add scenario events (timed parameter or state changes during a run),
   built on a recorded control-input timeline: every fresh gas flow,
   vaporizer dial, ventilation and cardiac-output change stamped with the
   simulated time it took effect, held alongside the state it describes
   rather than in the view. The controller today records concentrations but
   nothing records *why* they moved, so a run's inputs are unrecoverable
   once made. This is the prerequisite under items 9 to 12, and it is easy
   to mistake for solved: a state snapshot lets a run be *restored*, but not
   a point *between* snapshots reached, because that needs the same inputs
   re-applied over the same interval — so "resimulate from the nearest prior
   snapshot", the fallback in every snapshot-interval design, cannot be
   implemented without it. It is also what makes a run reproducible and
   citable; a curve without its input history is not a result anyone can
   check. Hence the 8-to-12 ordering in "Development pathway" above is not
   negotiable.
9. Add scenario save/load.
10. Add deterministic replay of a saved scenario, after item 9.
11. Add side-by-side comparison of multiple scenario runs on a shared time
    axis, each curve unambiguously labelled as to which run and which
    settings produced it. Delivered with item 12, which produces the runs
    worth comparing.
12. Add simulation forking (branch a running simulation into an independent
    copy). This is the educational payload of the group: comparing two
    managements of the same case — coast on low flow versus hold 0.5 MAC,
    then compare time to a wake-up threshold — isolates the variable under
    study, where building the case twice differs by everything that was not
    reproduced identically.

    *Scope (project owner, 2026-08-25).* Flat, not a tree: one trunk run
    with N branches taken from points on it. Sub-forks of forks are
    deliberately out — they multiply without bound and buy little over
    re-branching from the trunk.

    *Branch points (project owner, 2026-08-25, confirmed against the Gas Man
    Owner's Manual, "Replaying Simulations" and "Edit menu — Rewind").*
    Supersedes this note's original framing, which treated bookmarks as the
    branch mechanism and an arbitrary point as a rare, resimulated fallback.
    A branch point is not only a placed bookmark: any recorded
    control-input-timeline event — a fresh-gas-flow, vaporizer, ventilation,
    or cardiac-output change, whether or not a bookmark sits there — is
    itself a valid branch point. This matches Gas Man's own behavior: making
    a substantive change during replay truncates the run at that point, and
    continuing extends it "with new, alternate results, just as it would
    have done had the original simulation included the revising adjustment."
    This project's forking generalizes that single-track truncate-and-continue
    behavior — Gas Man keeps one active timeline, overwritten past the change
    point — into true forking, where the pre-change branch is kept rather
    than discarded, so both are available for item 11's side-by-side
    comparison. Because item 8's control-input timeline already stamps every
    such change with its simulated time, resimulating from any of them is not
    a rare fallback but the ordinary case — cheap, per the measurement below,
    and needing nothing beyond item 8's own data. Bookmarks (item 26) remain
    useful as the *named, threshold-triggered* subset a learner can
    fast-forward to and fork from repeatably; they are not the only subset
    that qualifies.

    *Required property.* A branch taken at time t must reproduce its
    parent's state exactly at every recorded sample up to t — asserted
    element-wise, not within a tolerance. Resimulating from a stored point
    while the parent was simulated straight through can diverge *before* the
    branch point through accumulation order for `elapsed_s`, a different
    step size, or a different number of steps per frame; that divergence is
    subtle, will not show up in a nominal test, and destroys the one thing
    forking is for, since a learner reading the comparison cannot see it. If
    exactness is unreachable, the divergence must be bounded, documented in
    `docs/MODEL.md`, and shown to the user rather than implied to be absent.

    *Measured 2026-08-25, so the storage question is designed around the
    right cost.* The full dynamic state is six concentrations plus elapsed
    time and the control settings — a snapshot is about the size of one
    history sample, so snapshot density is nearly free. Resimulation is also
    cheap: `SimulationState.advance` measured at 8.9 us per 0.1 s step, so
    reconstructing a 3-hour run from t=0 is about 1 s and 24 hours about 8 s.
    What is *not* cheap is the per-step concentration history itself.
13. Add IV pharmacokinetic and effect-site models, after item 12 (simulation
    forking) is available.
14. Add a modular hypnosis/eBIS effect model, with explicit model version and
    provenance.
15. Add a modular nociceptive-response effect model, with explicit model
    version and provenance.
16. Add validated renal/hepatic dysfunction modifiers, where supported by the
    selected model.
17. Add validated cardiopulmonary bypass modeling, where supported by the
    selected model.
18. Add validated ECMO modeling, where supported by the selected model.
19. Add species-specific patient/model profiles without treating non-human
    patients as scaled humans.
20. Improve accessibility (keyboard navigation, contrast, screen-reader
    support, color-vision-safe encodings).
21. Improve performance, working from the open entries in
    `docs/items/`. The render payload and the simulation/render
    cadence coupling are both resolved; what remains there is the
    controller's still-unbounded concentration history and further headroom
    in how chart points are built.
22. Continue documentation work.
23. Add packaging, signing, and distribution work for shipping the app.
24. Add a user-facing preferences/settings panel (theme, chart window, slider
    ranges, and similar display settings). Pre-requisite: consolidate the
    UI/display constants currently scattered across `app/theme.py`,
    `app/simulation_view.py`'s module-level constants, and the default
    values duplicated between `core/*.py` dataclasses and
    `app/controller.py`, into one settings module the panel can read from
    and write to, rather than adding a fourth scattered location. This
    panel must never expose the scientific parameters in `data/**/*.json`
    (partition coefficients, tissue volumes, etc.) for editing — those stay
    validated, versioned, and cited, changed only through deliberate
    scientific review per `CLAUDE.md`'s safety-critical standard, not an ad
    hoc settings screen.

25. Add a playback speed multiplier, so a run can be advanced faster or slower
    than real time without changing the simulation's own time step. Kept
    separate from deterministic replay (item 10): replay reproduces a recorded
    run, while this changes the rate at which any run is displayed.
    *Promoted into the scoped v0.4.0 milestone - see "Milestone after next:
    v0.4.0 - the teachable case" above.*
26. Add run bookmarks that halt a run at a target, after item 25. There is
    currently no way to say "run fast until something happens, then stop": a
    learner comparing gas-management strategies has to watch the clock and
    pause by hand, which is neither repeatable nor possible at speed.
    Bookmarks are what make fast-forward usable, and they are the branch
    points a learner deliberately returns to by name — item 12's "Branch
    points" note treats every control-input-timeline event as a valid branch
    point, not bookmarks alone, but the bookmark set is still what a
    snapshot policy should key on: it is the subset a learner is expected to
    revisit repeatedly, so it is worth keeping cheap to reach even where an
    arbitrary timeline point is not.

    *Scope floor (project owner, 2026-08-25, confirmed against the Gas Man
    Owner's Manual, "Using Bookmarks," and current-application screenshots
    the project owner supplied).* The Gas Man reference simulator's bookmark
    set is the minimum, and is two distinct mechanisms under one dialog
    ("Place or Remove a Bookmark"), not one kind with two flavors: **time
    bookmarks** — an absolute simulated time (hours/min/sec), which is all
    the manual's own "Using Bookmarks" section describes and is the older of
    the two — and **MAC targets** — a percent of MAC on a chosen graphed
    compartment (circuit, alveolar, vessel-rich, muscle, fat or mixed-venous,
    not the alveolar trace only), added to the application after that manual
    text was written and confirmed only from the current UI, not the manual.
    Keep both as first-class, separately listed collections rather than
    merging them into one "bookmark" type with a kind field — that is the
    shape Gas Man's own dialog uses, and it is what lets a UI list bookmarks
    and targets separately the way the reference does. The MAC kind cannot
    be specified in a unit the application does not have, so PL-DHV7 (MAC as
    a displayed unit) lands first.

    *Required properties.* Crossings are tested on every simulation step,
    not once per rendered frame: testing per frame overshoots by the whole
    frame's worth of simulated time, and the faster the playback multiplier
    the worse it gets, so the same bookmark would halt at a different
    concentration depending on how fast the user was running and the
    displayed halt value would not be the value asked for — a
    presentation-correctness failure of the kind `CLAUDE.md` treats as
    safety-critical, and one that also breaks reproducibility of any branch
    taken from that bookmark. Crossing direction is explicit — rising,
    falling or either — and shown wherever a bookmark is listed, since the
    same threshold means opposite things during wash-in and washout. A
    threshold above a compartment's asymptote is unreachable, so a bookmark
    needs a distinct "not reached, run-time cap hit" outcome that reads
    differently from "reached" rather than stopping silently. Bookmarks are
    part of the saved scenario rather than session-local, so item 12 can
    branch from them.

27. Add a schematic compartment view alongside the graph - the interactive
    "Picture" of the Gas Man reference simulator, in which the machine,
    circuit, lungs and tissue groups are drawn to scale and fill as agent
    enters them. This teaches something the graph structurally cannot: the
    graph plots partial pressure, so fat reads near zero for hours while
    holding more agent than every other compartment combined. Where the drug
    *is*, in millilitres, and where the *tension* is are different questions,
    and confusing them is a standard novice error. Needs per-compartment agent
    amounts exposed on the snapshot, which the core already computes and the
    snapshot does not yet carry.
28. Add agent cost, from the exhausted-agent amount the model already tracks.
    The economic argument for low fresh gas flow is a standard teaching point
    and currently the one lesson in this class of simulator that the
    application has the numbers for and does not draw. Depends on nothing;
    kept out of the v0.4.0 scope because it is an addition rather than a
    prerequisite.

29. Make `core/` read like the domain, as one deliberate pass over the whole
    package rather than opportunistically. `CLAUDE.md` sets the bar — a
    clinician who knows uptake and distribution should recognize the
    physiology without a translation step — but it was written after most of
    `core/` was, so it governs new code and has never been applied backwards.
    The purpose is the project owner's own fluency in the code: reviewing the
    coupled-gas equations of items 6 and 7 is the hardest scientific work on
    this plan, and doing it against code that reads like the textbook is a
    different task from doing it against code that does not.

    *Placement (project owner, 2026-08-26).* After v0.3.0 and before v0.4.0.
    Deliberately ahead of item 6's substance generalization rather than
    after: that change restructures every compartment, and settling the
    vocabulary first makes it a transformation of well-named code instead of
    a renaming and a restructuring at once. The accepted cost is that some
    of this is revisited when compartments become per-substance; what
    survives is the convention, which is the part that is expensive to
    invent twice.

    *Not yet scoped, and three questions have to be answered before it is.*
    What "reads like the domain" means concretely, beyond the one-line bar —
    the likely spine is a mapping between `docs/MODEL.md` § "Symbols" and the
    code's identifiers, since that table is already the project's own
    notation. Whether equations belong *in* the code or are *cited* from it:
    restating `docs/MODEL.md` in docstrings creates a second source of truth
    that can drift, while a bare citation makes a five-line function
    unreadable without a second document open, so the answer is probably
    per-case and the citation is the part a check can verify. And how much
    of the bar is decidable rather than judgment — unit suffixes in
    identifiers and symbol-table coverage look checkable, in the spirit of
    `tools/doc_check.py`, while "would a reader who knows the domain guess
    this?" plainly is not.

    No behavior, equation, parameter, or numerical method changes, so it
    crosses no capability boundary and takes a patch version rather than a
    minor, per "Versioning decision".

Item 1 (isoflurane and desflurane) has been promoted into a fully scoped
milestone, delivered as v0.2.0 — see "Completed: v0.2.0" above — so it no
longer appears here. Further volatile agents beyond isoflurane and desflurane (halothane,
enflurane, ether, xenon; not nitrous oxide, which is covered by items 6-7
above) remain an unscoped later idea, to be added back here as its own item
once someone is ready to scope it.

None of items 1-29 mix scientific-core and UI/tooling concerns within a
single milestone; where one depends on another (e.g. 2-5 on 1, 7 on 6, 10
on 9, 13 on 12), that dependency is noted inline rather than bundled into
one item.

Built-in profiles should remain read-only and support a future
"duplicate and customize" workflow with lineage and schema metadata.
