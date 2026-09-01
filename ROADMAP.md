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
| v0.2.6 | Completed | Delegation and release-tooling release on the same model: work whose success a command can prove now has to name that command and have run it, `docket` computes the debt gate and the cadence beat instead of a session transcribing them, and the release path stopped leaving `uv.lock` stale, while drift between this table and the version file became something a check catches - caught, not prevented, since nothing writes the row. The one scientific item widened the splitting-error bound to the whole settings envelope. No equation, parameter, or numerical method changed. |
| v0.2.7 | Completed / current baseline | Session-discipline and applicability-domain release on the same model: the simulation step now refuses inputs outside the operator split's stated applicability domain and the splitting-error bound is measured across setting changes rather than one held operating point, while ten process items closed the three channels by which product work leaked into discussions that were not about it, gave multi-step instructions a written standard, and cleared three live tooling defects. No equation or parameter changed, and the numerical method is unchanged - it is now guarded at the domain it was always specified for. |
| v0.2.8 | Planned / scoped | The workflow works: thirty-eight entries of development machinery the project already runs on - the merge path, the release script, the queue's ranking, the type-check and lint gates, and the instructions a session reads before it does anything. No simulator change, and no equation, parameter, numerical method or displayed value changes. |
| v0.3.0 | Planned / scoped | The foundation: Gate 0's inherited backlog cleared — the splitting-error bound widened across setting changes, the simulation step made transactional and bounded to the split's applicability domain, the `core/` boundary refactors, and the live tooling defects. No new capability; see the versioning exception above for why it is a minor. |
| v0.4.0 | Planned / scoped | The teachable case: compressed playback at a fixed simulation step, MAC multiples as a displayed unit, a case-length time base, and a recorded control-input timeline. No equation, parameter, or numerical-method change. |

**Tags.** Every version the table above marks Completed carries an annotated
tag. Which ones those are is deliberately not restated here - the table is the
list, and a second copy is a second thing to keep true, which it twice was not.
`tools/doc_check.py` reads the completed rows against `git tag` instead, so a
release that shipped without one fails the check rather than waiting to be
noticed. `git describe --contains` therefore resolves for every commit up to
and including the latest release - verified on 2026-08-30 across the whole of
`main`; the commits it does not resolve are the unreleased ones after the
newest tag, which the next release's tag will cover. That span is the
provenance guarantee PL-J3ZK was opened to restore.

The tag goes on the merge commit, so between cutting a release and pushing its
tag the newest version is Completed and carries none. That window is reported
as an advisory rather than an error: failing it would turn `make check` red on
every release branch, which is the failure PL-8HJ2 removed arriving by another
door. `bin/docket release` refuses to cut the *next* release while that tag is
still missing, which is what stops the window from staying open.

A version that has genuinely gone out untagged is named in a bold sentence
here, and the checker holds the count that sentence states to the versions it
names. There are none.

**The gap is closed, 2026-08-30.** v0.1.0 (`97cc66a`) and v0.2.0 (`796bf4f`)
were the last two, and were recorded for a time as untaggable: `main` appeared
to have three unrelated roots and `git merge-base 796bf4f 97cc66a` returned
nothing. That was measured in a shallow checkout, where boundary commits
report as parentless. In the full history there is one root, `97cc66a`
(v0.1.0) is an ancestor of `796bf4f` (v0.2.0), and that is an ancestor of
`bc5f823` — so the tags were placed where the release commits actually are.
The superseded reasoning is kept here because a shallow checkout will produce
it again for anyone who repeats the measurement.

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
what the app actually runs. The harness that reproduced these findings was
retired by PL-STNV once every check it carried had become a closed item, a
reference test, or an open queue entry; it survives in git history alone.

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
existing, already-validated model — preceded by the v0.2.8 patch, which
makes the loop they will be built through reliable, and by v0.3.0, which
adds no capability and exists to clear the ground they are built on:

- **v0.3.0, the foundation** — Gate 0's inherited backlog cleared. No new
  capability; see the versioning exception under "Versioning decision".
- **v0.4.0, the teachable case** — one case end to end, in clinical units, at
  a speed and on a time base that make its lessons observable at all.
- **v0.5.0, the case you can branch** — bookmarks, forking from them, and
  side-by-side comparison of the branches.

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.2.8 — the workflow works** | Scoped below. Its own frozen list of thirty-eight entries: the development machinery the project already runs on, fixed before two long milestones are run through it. No simulator change. | 2 M, 35 S |
| 2 | **v0.3.0 — the foundation** | Gate 0's frozen debt list, recorded under v0.4.0 below: the entries outside that milestone's own scope, released as a minor by deliberate exception. | 3 M, 17 S |
| — | **v0.3.x — `core/` reads like the domain** | Planned-milestone item 29. A patch, not a milestone: no behavior changes. Placed here deliberately, ahead of the substance generalization that would otherwise force the vocabulary to be invented and restructured at once. Not yet scoped. | — |
| 3 | **v0.4.0 — the teachable case** | Scoped below. 11 items, of which 6 are gate-0 debt the milestone clears itself. | 5 M, 6 S |
| 4 | **Gate 1** | Frozen when v0.5.0 is scoped. Contents unknown by construction: v0.4.0's own findings land here. Ships inside v0.5.0, not as its own release. | — |
| 5 | **v0.5.0 — the case you can branch** | Planned-milestone items 8 (replay half), 26 (bookmarks), 12 (forking), 11 (comparison). | — |
| — | **MVP complete** | A learner can run, branch, and compare a case. | — |
| 6 | **Gate 2** | Frozen when v0.6.0 is scoped; ships inside it. | — |
| 7 | **v0.6.0 — the schematic** | Planned-milestone item 27: Gas Man's Picture, showing where the agent *is* rather than where its tension is. | — |
| 8 | **Gate 3** | Frozen when v0.7.0 is scoped; ships inside it. | — |
| 9 | **v0.7.0 — multi-substance and nitrous oxide** | Planned-milestone items 6 and 7, and the substance generalization Phase 1 describes. | — |
| 10+ | **Beyond** | The machine and its interlocks (items 1-5), save/load and replay (9, 10), then intravenous agents (13-15), in "Development pathway" order. | — |

**Rows 1 and 2 are the only releases whose whole content is a frozen list,
and they are not the same kind of thing.** Row 2 is Gate 0's release: that
gate earns a version of its own because it clears the backlog inherited from
before the debt gate existed, which is the exception recorded under
"Versioning decision" above, and an exception rather than a pattern. Row 1
is not a gate at all — v0.2.8's frozen list is its own scope, recorded under
a gate heading because that subsection is what `bin/docket wave` reads, and
the second of the two groups it lists is new workflow capability rather than
debt.
Gates 1 onward hold one milestone's findings and ship inside the milestone
they gate, which is why rows 4, 6 and 8 carry no version.

Rows 5 to 9 are the intended order and are not yet scoped; each becomes real
only when it gets its own goal, required scope, definition of done and
out-of-scope list here, per the development rules. Row 5's internal ordering —
forking and comparison ahead of save/load and replay — is a deliberate
departure from "Development pathway"'s Phase 3 sequence, on the grounds that
branching within one session is the teaching payload while persistence is a
convenience; it is recorded here as a proposal rather than a decision, and
Phase 3's stated order stands until v0.5.0 is scoped.

### Why the gates are on this list and not behind it

A gate that lives in a separate document, or in a session's memory, is
renegotiated every time it is inconvenient. Put on the timeline it is a step
with a size, and skipping it is visible as skipping a step. The cadence that
generates rows 2, 4, 6 and 8 is specified under "The debt gate" below; the
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

## Next release: v0.2.8 - the workflow works

### Goal

Make the development loop reliable before two long milestones are run through
it. Everything in this release is machinery the project already depends on:
the merge path, the release script, the queue's ranking, the session-start
digest, the type-check and lint gates, and the instructions a session reads
before it does anything else. None of it touches the simulator.

It comes first because of `CLAUDE.md`'s standing decision of 2026-08-30 —
workflow work outranks product work until the workflow is settled — and that
decision exists because friction in the loop is paid again in every future
session, while a deferred feature is paid for once. v0.3.0 clears twenty
entries of inherited product debt and v0.4.0 builds the first teachable case
on top of it. Both are long runs through the same loop, and running them
through a merge path that does not wait for CI, a release script that stops
halfway, and a `docket next` that ranks work the current milestone excludes
costs more than fixing those does.

It is a patch by the ordinary rule under "Versioning decision" above: it
crosses no capability boundary, adds nothing to the simulator, and changes no
equation, parameter, numerical method, unit or displayed value. Gate 0's
minor-version exception is not extended to it and is not needed.

### Debt gate: the frozen list

**Frozen 2026-08-30, the day this release was scoped, at seventeen entries.**
More have been admitted since — under the completion rule and the scope test
beneath this list, and one at the project owner's direction — so the entries
below, rather than that original seventeen, are its whole content. What the freeze does and does not close is set
out beneath the list; an entry records its own outcome as it closes, per
"The cadence" below.

**It is a frozen scope, not a fourth gate in the cadence.** The first group
below is debt by "What counts", all classed `defect`, and the second is new
workflow capability, which
that section says explicitly is *not* debt and does not hold a gate. The list
is recorded under a heading named "Debt gate" because that subsection is what
`bin/docket wave` reads: a release records a gate to say that it comes ahead
of one already open, and the beat then follows it rather than contradicting it
(queue item `PL-NSN9`, a self-gating milestone reporting the wrong beat). The
numbered gates are unaffected — Gate 0 is still recorded under v0.4.0 below,
still binds v0.4.0, and becomes the nearest gate again the moment this release
ships.

How many entries are closed is **not recorded here**, for the reason given in
the v0.4.0 section: a count written into a document goes stale the next time an
item closes. `bin/docket wave` reads these entries against `docs/items/` and
reports the split.

Nor is the list's *size* restated in prose here, for the same reason. It is
stated in the group headings below and in the two table rows naming this
release, and `tools/doc_check.py` holds those three to the entries.

*The loop is visibly broken without these — twenty-two entries:*

- PL-J786 (S) Require a green `checks` run before any merge into main
- PL-64LS (S) Detect items stranded on an unmerged branch
- PL-8HJ2 (S) `make release` stops mid-way on the ROADMAP table it does not
  write, so every release ends in a red test
- PL-M5FK (S) This file's tag statements go stale on every release, and no
  check reads them
- PL-1TPM (S) `docket next` ranks work the current milestone excludes, with no
  sign that it does
- PL-019F (S) The "what should we work on next" rule answers one level below
  the roadmap step that should decide it
- PL-5YK8 (S) The `verify:` advisory nags about grandfathered items, so it can
  never reach zero
- PL-H7XN (M) `CLAUDE.md` keeps every rule resident whether or not a session
  needs it, which reduces adherence to the ones it does
- PL-NSN9 (S) A milestone that gates itself reports `implement` when its gate
  clears, where `release` is due
- PL-J295 (S) The release-train check reads a tag missing from a shallow clone
  as a release that was never tagged, so `make check` fails on unmodified
  `main` in every web-session container. Added after the freeze because it
  completes `PL-XCYB`, further down this list: that entry established that a
  check must refuse to answer in a shallow checkout rather than answer
  wrongly, and fixed the pull-request reader; the tag reader has the identical
  exposure and was missed. See the rule beneath this list.
- PL-KWC1 (S) `docket flight` reads item ids from branch names only, so a
  branch the web harness named carries none and is invisible — and `docket
  next` therefore hands out items another session is already implementing.
  Added after the freeze because it completes PL-64LS above: that entry made a
  branch's stranded items visible to a session, reading the same refs through
  the same module, and left the in-flight signal blind on every branch this
  project actually produces.
- PL-1CYR (S) Nothing re-checks the branch against `main` once a session is
  underway, so a discussion that becomes implementation builds on a base that
  moved while it was talking. Added 2026-08-31 at the project owner's
  direction rather than under the completion rule: it is new scope, admitted
  because the staleness is paid by every session that opens as a discussion,
  which is how this project is normally worked. Closed 2026-08-31 (pull request
  125): the check is `bin/docket branch`, so the question can be asked again at
  any moment rather than only at session start, and the hook keeps only the
  fetch.
- PL-D2GW (S) The session digest offers a release whose version names a
  milestone whose gate is still open, so the line every session reads first
  tells it to cut v0.2.8 while entries of v0.2.8 are unfinished. Admitted
  2026-08-31 under the scope test: the digest and the release script are both
  machinery this release's goal names. It reopens on every later release that
  records a gate — v0.3.0 shipping Gate 0 is the next — which is exactly the
  run this release exists to protect.
- PL-Q2BJ (S) The digest's `Top:` line still leads with work the current step
  excludes, contradicting the beat printed two lines below it. Admitted
  2026-08-31 under the scope test: it is `PL-1TPM`'s defect on the surface
  every session reads whether it asked or not.
- PL-CPSY (S) A squash-merged branch whose ref survives reports its items in
  flight forever, so `docket next` withholds work that is finished and
  startable. Admitted 2026-08-31 under the scope test: squash-merge is the
  merge path `PL-S4M2` installed for this release, and the queue's ranking is
  what reads it. Closed 2026-08-31 (pull request 121): a branch is finished
  when its content has landed, which is asked before the commit walk rather
  than inside it.
- PL-S1P1 (S) The refs whose history could not be read are dropped before the
  in-flight ids reach `docket next`, so a partial answer is presented as a
  complete one everywhere except `docket flight`. Admitted 2026-08-31 under
  the scope test. `PL-CPSY` and `PL-MGNC`, the other two holes in that
  function, both closed on 2026-08-31 ahead of it - one answered before the
  commit walk and one inside it, neither needing this one's lines. What they
  left is a larger `unreadable` half for this item to carry to the callers,
  and `PL-YSXF` (an unread ref loses the id its own branch name carries) is
  the same hole from inside the function: one pass. Closed 2026-08-31 (pull
  request 123): `in_flight_ids` is gone and every caller takes the
  `FlightReport` itself, so the gap travels with the answer rather than being
  dropped at the boundary, and one sentence appears under all six.
- PL-YSXF (S) A ref named as unread loses the item id its own branch name
  carries, which needs no history to read, so `docket next` offers an item a
  live session is holding. Admitted 2026-08-31 under the scope test, at the
  project owner's direction once `PL-S1P1` had closed: it is the fourth and
  last hole in the function the three entries above are about, and the only
  one where the checkout knew the answer for certain and threw it away. The
  guards `PL-MGNC` added are what widened it, so it grew rather than staying
  where `PL-KWC1` left it.
- PL-MGNC (S) A readable merge-base does not make the in-flight commit walk
  complete, so a shallow clone — the normal state of a session container —
  reports merged items as in flight. Admitted 2026-08-31 under the scope test,
  and the only member of this family observed firing: the digest that opened
  the session reassessing this gate named twenty-seven ids, eighteen of them
  closed and one of them `PL-NSN9`, an open entry of this list. Closed
  2026-08-31 (pull request 122): the walk now has to stop against a commit the
  default branch accounted for rather than because the checkout ran out of
  history, and the reproduction the brief asked for builds the intermediate
  depth with real git.
- PL-3CBS (S) Nothing notices that an open item's work already landed on
  `main`, so `docket next` offers work that is finished and the gate's own open
  count overstates what is left. Admitted 2026-08-31 under the scope test: it
  corrupts the two numbers this release is steered by, in the direction nobody
  double-checks. It was not among the nine captures reassessed that day and was
  admitted on the same reading immediately afterwards.
- PL-3576 (S) `docket check`'s offered-item advisory is computed from an
  in-flight answer that may be partial and says nothing about it, so a shallow
  checkout is told to groom an item that is not the one about to be offered.
  Admitted 2026-09-01 under the scope test: `PL-S1P1` above carried the unread
  refs to six readers of that answer and left `check` out as a placement
  question rather than as out of scope, so this is the seventh and last of them.
- PL-1Q3S (S) A merged pull request leaves a stale remote-tracking ref, so the
  stop hook counts every commit landed since as unpushed and tells the session
  to push a branch identical to `main`. Admitted 2026-09-01 under the scope
  test: the hook is outside the repository, but the deliverable is a line in the
  instructions a session reads — one of the six pieces of machinery the goal
  names — and it fires after every merged pull request, several times a session.
  The "workable here" limit below excludes a finding *nothing in the tree can
  close*; this one closes with a repository edit and is marked `not-delegable`
  only because confirming it means ending a session.
- PL-HDY6 (S) The scope reader counts any id a milestone's section names, so
  `docket next` reports an id the section names *to exclude* as in scope for
  the current step. Admitted 2026-09-01 under the scope test, after the four
  above and on the same reading: it is the queue's ranking misdirecting a
  session on `main` today, telling it that `PL-68XK` clears this gate on the
  strength of the paragraph below that says `PL-68XK` does not. The fix is not
  simply to prefer this subsection - v0.4.0 names nine open ids as its own
  Required scope rather than as gate entries, and those are in scope - so the
  item carries both candidate rules and what each costs.

*Stops new debt being introduced — sixteen entries:*

- PL-ZQ9C (M) Record an item's pull request, so provenance survives
  squash-merge
- PL-S4M2 (S) Switch main to squash-merge, so each item lands as one commit.
  Blocked by PL-ZQ9C above and ordered after it deliberately: squash-merge
  discards the branch history that today is the only record of which pull
  request closed an item, so the provenance has to be recorded before it is
  discarded, not after.
- PL-F5HB (S) The project runs a Python 3.14 release candidate, not 3.14 final
- PL-020 (S) Widen the type-check gate past `src`, and ship a `py.typed`
  marker
- PL-W5LG (S) Hold CI config to the same path checks as the documentation
- PL-ZN0N (S) Enable ruff RUF100 so inert `noqa` directives fail the build
- PL-69J3 (S) Clear the inert `noqa` directives RUF100 will catch, and record
  why the deliberate suppressions exist
- PL-STNV (S) Retire the review-verification harness and capture its last live
  finding
- PL-XCYB (S) A provenance check must refuse to answer in a shallow checkout,
  not answer wrongly. Added after the freeze because it completes PL-ZQ9C
  above: that item's check asserts a `(#N)` subject on a commit reachable from
  main, and a web session's checkout is shallow, so the check as specified
  reports sound provenance as broken. See the rule beneath this list.
- PL-WFJ9 (S) `render.py` reads `Readiness` and `Feature` through `object`
  annotations and twelve `type: ignore[attr-defined]`, so the widened gate
  passes over the digest and `status` outputs without checking them. Added
  after the freeze because it completes PL-020 above: that entry's whole claim
  is that `subprojects/docket/src` is type-checked, and it was not, in the two
  outputs every session reads first. See the rule beneath this list.
- PL-DL1X (S) `docket release` stamps every item file before it bumps the
  version, so a failed bump leaves the store recording a release that did not
  happen. Admitted 2026-08-31 under the scope test: the release script is
  machinery this release's goal names, and the residue is a provenance error
  of the kind the release path exists to prevent.
- PL-921W (S) The formatter target applies to `tools/`, which must run under
  bare `python3`, and nothing guards it the way `subprojects/docket/` is
  guarded. Admitted 2026-08-31 under the scope test: the lint gate is named in
  the goal, and this is the same second-site miss as `PL-J295`, one tool over.
- PL-QDH7 (S) `tools/` promises standard-library-only imports and nothing
  guards it, the way the parse floor now is. Admitted 2026-09-01 under the
  scope test: the lint gate is named in the goal, and this is the other half
  of `PL-921W`'s promise, left unguarded where that item guarded the first.
- PL-CMCB (S) All ten `type: ignore` directives sit under `tests/`, outside
  `[tool.mypy] files`, so `warn_unused_ignores` has never evaluated one.
  Admitted 2026-08-31 under the scope test: it is the mypy half of what
  `PL-ZN0N` and `PL-69J3` did for `noqa`. The weakest of the seven — inert
  reporting rather than a loop that misfires — and the first to drop if this
  list needs shortening.
- PL-RWZV (S) The brief check tests for a literal marker, so an elaborated
  heading fails and an empty section passes. Admitted 2026-09-01 under the
  scope test: it is a `docket check` misfire, the same machinery as `PL-5YK8`
  above, and it is the gate deciding whether an item may reach `ready` at all.
  Two of the captures triaged on 2026-09-01 carried exactly the empty-section
  stub it accepts.
- PL-H8MQ (S) `ROADMAP.md` states this release's entry count in six places, and
  its group and debt splits in three more, with nothing holding any of them to
  the list. Admitted 2026-09-01 under the scope test: measured that day, three
  different totals — eighteen, thirty-one and thirty-two — were live in this
  file at once, so a session reading it to learn how much of the release is left
  read a number that was wrong. Every admission pays the correction by hand,
  the four of 2026-09-01 included.

**Two items on the approved list are not entries.** `PL-J3ZK` (restore the tag
provenance) and `PL-20ZR` (the workflow-before-features ordering is
re-explained every session) were on the list the project owner approved and
closed before it was written here. Recording a closed item as a frozen entry
would make this release report a size it never had to clear.

**Seven entries are marked `not-delegable`,** which is high for a
release this size and is worth knowing before the work is planned: PL-J786 and
PL-S4M2 change GitHub repository configuration that no session in this project
can reach; PL-8HJ2 can only be proved by cutting a release; PL-ZQ9C leaves a
migration choice open that rewrites the provenance of every closed item;
PL-1Q3S fixes a repository-side habit whose effect is only visible when a
session ends, in a hook no session can read; and
PL-H7XN's test is that no rule was lost, which is a reading of the file rather
than a command; and PL-CMCB's deliverable is a verdict on ten suppressions
rather than an exit code.

**What the freeze closes, and what it does not** (project owner, 2026-08-30).
The list is closed to new *scope*: new behavior, new capability, another
workflow idea raised while this release runs. It is not closed to what an entry
already on it needs in order to actually be done. A finding made after the
freeze that addresses something a frozen entry is fixing belongs here, recorded
with what it completes. Freezing exists to fix a specific set of problems, so
shipping an entry known to be half-fixed would keep the list's length at the
cost of its purpose.

This is "The gate is a snapshot, not a moving target" read correctly rather
than a new rule: that section already says a finding which continues or
completes an item inside the frozen list belongs to the same list. This
paragraph said the opposite when the section was first written, and was wrong.

**The list is a scope, not a set of items** (project owner, 2026-08-31). That
is what decides membership, and the completion rule above is one case of it
rather than the test itself. This release's scope is the goal stated at the
top of this section: a development loop reliable enough to run two long
milestones through, across the machinery the goal names — the merge path, the
release script, the queue's ranking, the session-start digest, the type-check
and lint gates, and the instructions a session reads before it does anything.
A finding that a *named* piece of that machinery misfires is inside this scope
however late it is found and whatever entry it does or does not complete,
because leaving it out ships a release titled "the workflow works" while the
workflow it names does not.

So "new scope" means a different goal — a new workflow capability, a better
tool nobody is blocked by, an idea raised because this release made someone
think of it. It does not mean a newly discovered instance of the goal already
frozen. A defect in already-named machinery is the third case, and it is
admitted: this paragraph previously offered only "new scope" and "completes an
entry", and nine findings triaged on 2026-08-31 were sent to the queue for
being neither, when seven of them were defects in the digest, the release
script, the merge path and the lint gate that this release exists to make
reliable.

Two limits keep that from reopening the list for everything. The finding must
be a **defect** in machinery this section's goal names — not an improvement to
it, and not machinery the goal is silent about; and it must be **workable
here**, so a finding whose cause is outside this repository is captured and
left out however well it fits, because an entry nothing in the tree can close
would hold the gate open forever.

A `safety`- or `science`-classed finding goes to Gate 0 rather than here — it
is about the simulator, which this release does not touch. A `P0` is a hotfix
on its own branch under the `docket` skill and joins no list.

**Four entries were added under the completion rule — PL-J295, PL-KWC1,
PL-XCYB and PL-WFJ9, all above.** The rest were added under the scope test
rather than this one, each marked as such in the list with the date and the
reasoning; that test is beneath it. PL-XCYB is paired with PL-ZQ9C rather than queued behind it. It was found while handing
PL-ZQ9C to a session, by checking whether that item's proposed migration was
feasible, and it makes the difference between a provenance check that is right
and one that fails loudly against correct data in the environment most sessions
run in. Shipping PL-ZQ9C without it would close an entry known to be
half-fixed, which is the outcome the rule above exists to prevent, so the two
are worked together and closed together.

PL-WFJ9 is the same case a step later, and was found by the entry it completes
rather than before it: widening the type-check gate to `subprojects/docket/src`
made `render.py`'s suppressions visible for the first time, and they are why
the widened gate passes over that file. PL-020 could be reported closed without
it, which is exactly the half-fixed close the rule prevents - the gate would
assert that docket's source is checked while the digest and `status` renderers,
the first thing a session reads and the answer to "what next", were not. It is
worked with PL-020 rather than behind it.

PL-68XK (check that a recorded commit hash resolves) is a different case and is
*not* admitted by this rule: it predates the freeze and was excluded from the
approved list deliberately. It was nonetheless entangled with PL-ZQ9C, so its
brief has been refreshed rather than worked - and what the refresh had to say
changed once PL-ZQ9C landed. `commit:` was not replaced: `pr:` sits beside it
and `commit:` became optional, so PL-68XK is no longer "validate the field that
makes a closure traceable" - `docket check` already holds every recorded `pr`
to a pull request the default branch names. It is now the narrower job of
holding a `commit` that is *present* to one that resolves, because a hash
leading nowhere reads as provenance whether or not a number sits beside it.
Its brief carries that scope, and the shallow-checkout discipline PL-XCYB
built, so whoever picks it up does not build either half twice.

### Definition of done

- Every entry on the frozen list above is `done`, or `dropped` with its reason
  recorded. `bin/docket wave` reports the split against `docs/items/`.
- `make check` passes: `ruff format`, `ruff check`, `mypy`, `pytest`,
  `docket check`, and `tools/doc_check.py`.
- The two entries that change repository configuration rather than the tree —
  PL-J786 (a green `checks` run required before merge) and PL-S4M2
  (squash-merge) — are confirmed in effect on a real pull request, not merely
  described as done. Neither can be verified by a command in this repository,
  which is why both are marked `not-delegable`.
- No equation, parameter, numerical method, unit or displayed value has
  changed, and the v0.0.2 circuit and v0.1.0 sevoflurane reference tests pass
  unaltered. Three entries reach into `src/` and `tests/` and are bounded to
  what their briefs describe: PL-020 may add type annotations, PL-ZN0N and
  PL-69J3 may add, remove or annotate `noqa` directives. If any of them turns
  out to require a change to a modelled value, that is a finding for Gate 0
  and a scoped item of its own, not this release's work.

### Explicitly out of scope for v0.2.8

- Anything on Gate 0's frozen list, recorded under v0.4.0 below. That gate is
  untouched by this release and clearing it is still what v0.3.0 ships.
- Any simulator change at all: `src/anesthesia_sim/core/`,
  `src/anesthesia_sim/app/`, and the scientific content of `docs/MODEL.md`. A
  release whose whole claim is that the loop is now reliable cannot also be
  the one that moves the model.
- Workflow capability beyond the entries on that list — new tools, better
  tools, an idea this release made someone think of. The queue holds more
  process items than this release ships, and they wait for the next one. What
  the scope test admits is a defect in machinery the goal already names, which
  is not this; a release that absorbs every workflow idea raised while it runs
  never ships.

## Next milestone: v0.3.0 - the foundation

### Goal

Clear the inherited backlog, so feature work starts from a codebase whose
known defects are closed rather than carried. This release adds no
capability: after it the simulator does what it did before, correctly, with
its verification gate widened to the inputs the interface can actually reach
and its failure path unable to leave partial state behind.

Its contents are exactly Gate 0's items that fall outside the teachable
case's own scope — those listed under "Debt gate: the frozen list" in
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

- **Simulated time becomes an exact function of step count** (queue item
  PL-VM40). `SimulationState.elapsed_s` accumulates `+= simulation_step_s`
  per step today; derive it from an integer step counter instead, and fix the
  step at 0.1 s. The run loop advances a fixed number of steps per tick and
  never catches up to the wall clock: a slow machine runs slower, it does not
  run differently.
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
- **A MAC-awake reference band** on the chart (queue item PL-F52R): a cited
  population median for return of responsiveness, drawn as a band and
  labelled as a population reference, never as a per-patient time
  prediction.
- **An F_A/F_I trace** (queue item PL-ZRSP), the ratio the uptake literature
  plots, with the interpretive caveat that it means what the textbook curve
  means only while inspired concentration is held constant.
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

**What a freeze closes is new scope, not the completeness of a fix** (project
owner, 2026-08-30). A frozen list exists to fix a specific set of problems;
refusing the finding that one of its entries needs in order to actually be
fixed preserves the list's length at the cost of its purpose. The rule below is
how that is applied, and it is deliberately not symmetric: new work is kept
out, and what an entry needs is let in.

**And it is worked with the entry it completes, not after it** (project owner,
2026-08-30). Admitting a finding to the list and then working it as a separate
piece of work later reintroduces exactly what admitting it prevented: the first
entry ships half-fixed while the thing that finishes it waits in the queue. So
pair them - one branch, one review, closed together - and the issue is fully
addressed before anything else starts.

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

**Friction that compounds is the clearest presence case** (project owner,
2026-08-30). A finding whose cost is paid again by every remaining entry - a
tool that answers the wrong question, a check that cries wolf, a command that
ends red on success - was almost always present at the freeze and merely
invisible until the gate's own work started paying it. Deferring one is a
decision to pay it once per remaining entry, so it re-enters, and it is worked
early rather than merely admitted.

The test is arithmetic, not enthusiasm: name what each remaining entry pays and
multiply by how many remain. `PL-0RS6` qualified at eighteen entries times a
twelve-command detour apiece, which is a large fraction of the saving the
release exists to deliver. Work that is merely valuable, cleaner or more
interesting - rewriting a working tool in another language, adopting a nicer
abstraction - makes no remaining entry cheaper, so it fails the test and waits
for the roadmap however appealing it is. If the per-entry saving cannot be
named, the finding does not qualify.

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
