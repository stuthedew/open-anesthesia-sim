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

| Version | Status | Milestone |
| --- | --- | --- |
| v0.0.1 | Completed | Initial runnable prototype: deterministic simulation clock, controller/view separation, basic charting and controls, and project quality tooling. |
| v0.0.2 | Completed | Analytically validated ideal breathing-circuit wash-in and washout with no patient uptake. |
| v0.1.0 | Completed | First patient sevoflurane uptake and distribution model - the "Sevo works" milestone. |
| v0.2.0 | Completed | Isoflurane and desflurane added as additional loadable volatile agents. |
| v0.2.1 | Completed | Validation hotfix: the vaporizer maximum is enforced in the core and rejects rather than clamps, the agent MAC cross-check fails closed, and the cited reference-adult defaults reach the running app. |
| v0.2.2 | Completed / current baseline | Hardening and interface-provenance release on the same model: a failed step halts the run visibly instead of leaving it reading "Running", the parameter schemas reject unknown keys, agent selection carries its ISO 5360 identification color, and a dead non-conservative ventilation path is deleted. |

There is no active v0.0.3 milestone. Any guide that labels the first patient
sevoflurane build as v0.0.3 is superseded by this roadmap.

## Current baseline: v0.2.2

v0.2.2 is a hardening and interface-provenance release on the v0.2.0 model.
Like the v0.2.1 hotfix before it, it changes no equation, parameter, or
numerical method: `docs/MODEL.md`'s specification of the model is unchanged,
and the v0.0.2 circuit and v0.1.0 sevoflurane reference tests still pass
unaltered. It carries four queue items:

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

## Next milestone

No milestone after v0.2.2 has been scoped yet. The next candidate, per
"Development pathway" below, is generalizing the patient's state from one
volatile agent to a set of simultaneously present substances — the change
that agent switching, nitrous oxide, and the second-gas effect all wait on,
and the one that decides how much refactoring intravenous agents cost later.
It must be fully specified here (goal, required scope, definition of done,
and explicit out-of-scope list) before implementation begins, per the
development rules below.

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

## Development pathway

The numbered list below is the catalogue; this is the order it is intended to
be worked in, and why. Phases are groupings of intent, not scoped milestones —
each item still has to be specified individually before implementation, per
the development rules above.

The organizing goal is a mature inhalational simulator before any intravenous
work begins: the science first, then an interface that can actually drive it,
then reproducibility, then IV.

**Phase 0 — foundation.** No new feature work until the existing queue is
closed out. Not because features are unwelcome, but because the last stretch
of work felt like whack-a-mole, and it is worth being precise about why: the
queue holds almost no defects. What it holds is decisions nobody has made.

At the time this was written, nine of twenty-four open items sat at
`needs-decision` — over a third of the queue could not be picked up by anyone,
so it never visibly shrank however much work got done. That is the thing to
fix before adding to it, because the same ratio applied to a larger queue is
what makes a backlog stop meaning anything.

"All bugs squashed" is not a closing condition, since absence of defects
cannot be demonstrated. This one can be checked:

- no open item classed `safety`, `science` or `defect`;
- no open item classed only as process work (`session-cost`, `docs`, `infra`)
  — the workflow is either finished or explicitly deferred;
- no item left at `needs-decision`: each is answered and made `ready`, or
  dropped with its reason recorded;
- every outstanding branch merged and a release cut, so the tree is not
  carrying half-landed work into Phase 1.

Implementing a planned milestone during this phase is fine where it falls out
of foundation work naturally. Starting one because it is more interesting than
the queue is the thing being deferred.

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

**Phase 2 — an interface that can drive the machine.** Consolidate the
display constants named in item 24 first, then item 24 itself, then items 5,
3 and 4 (end-tidal control, override mode, direct injection), then item 8
(scenario events), item 20 (accessibility), and item 25 (playback speed).

The consolidation leads because item 24 already names it as a prerequisite,
and because every control added before it spreads the same scattered defaults
further.

**Phase 3 — reproducibility and comparison.** Items 9, 10, 11 and 12 in that
order (save/load, deterministic replay, side-by-side comparison, forking).

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
implicitly drag others along with it. Exact version numbers after v0.2.2
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
8. Add scenario events (timed parameter or state changes during a run).
9. Add scenario save/load.
10. Add deterministic replay of a saved scenario, after item 9.
11. Add side-by-side comparison of multiple scenario runs.
12. Add simulation forking (branch a running simulation into an independent
    copy).
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

Item 1 (isoflurane and desflurane) has been promoted into a fully scoped
milestone, delivered as v0.2.0 — see "Completed: v0.2.0" above — so it no
longer appears here. Further volatile agents beyond isoflurane and desflurane (halothane,
enflurane, ether, xenon; not nitrous oxide, which is covered by items 6-7
above) remain an unscoped later idea, to be added back here as its own item
once someone is ready to scope it.
25. Add a playback speed multiplier, so a run can be advanced faster or slower
    than real time without changing the simulation's own time step. Kept
    separate from deterministic replay (item 10): replay reproduces a recorded
    run, while this changes the rate at which any run is displayed.

None of items 1-25 mix scientific-core and UI/tooling concerns within a
single milestone; where one depends on another (e.g. 2-5 on 1, 7 on 6, 10
on 9, 13 on 12), that dependency is noted inline rather than bundled into
one item.

Built-in profiles should remain read-only and support a future
"duplicate and customize" workflow with lineage and schema metadata.
