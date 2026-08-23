# Project roadmap

This file is the authoritative version and milestone map for the project. If a
build guide, issue, or conversation conflicts with this file, update the
conflicting artifact or amend this file deliberately in the same change.

## Versioning decision

The project uses milestone-based semantic versioning during early development.
The next release number is chosen for the capability boundary it crosses, not
by mechanically incrementing the patch number.

| Version | Status | Milestone |
| --- | --- | --- |
| v0.0.1 | Completed | Initial runnable prototype: deterministic simulation clock, controller/view separation, basic charting and controls, and project quality tooling. |
| v0.0.2 | Completed | Analytically validated ideal breathing-circuit wash-in and washout with no patient uptake. |
| v0.1.0 | Completed / current baseline | First patient sevoflurane uptake and distribution model - the "Sevo works" milestone. |

There is no active v0.0.3 milestone. Any guide that labels the first patient
sevoflurane build as v0.0.3 is superseded by this roadmap.

## Current baseline: v0.1.0

The repository currently models the first patient sevoflurane uptake and
distribution system: a constant-volume breathing circuit, an alveolar gas
compartment, cardiac-output-dependent perfusion to vessel-rich, muscle, and
fat tissue groups, and mixed-venous return, coupled back to the lungs. Every
compartment step is solved by exact analytic solution and composed by
operator splitting; the v0.0.2 circuit reference tests are preserved
unchanged. Sevoflurane and reference-adult parameters are loaded from
schema-validated, cited data files rather than hardcoded. Full equations,
units, assumptions, parameter provenance, numerical method, and known
limitations are documented in `docs/MODEL.md`.

The current model does not include metabolism, other volatile agents, IV
anesthetics, effect-site models, or clinical predictions or recommendations
of any kind. See `docs/MODEL.md`'s "Known limitations" for the complete list.

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

## Next milestone

No milestone after v0.1.0 has been scoped yet. The next candidate, per
"Later roadmap" below, is expanding the volatile model with additional
validated, data-driven agent definitions and broader reference cases. It
must be fully specified here (goal, required scope, definition of done, and
explicit out-of-scope list) before implementation begins, per the
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
  scoped release.

## Later roadmap

The ordering below records current project decisions. Exact version numbers
after v0.1.0 remain provisional and must be assigned when each milestone is
fully specified.

1. Expand the volatile model with validated, data-driven agent definitions and
   broader reference cases. When this is scoped: consider migrating
   `core/parameters.py`'s JSON validation to Pydantic — the boilerplate in
   its `_require_*` helpers compounds with each new agent/patient schema,
   and the module is isolated behind plain dataclass returns, so the switch
   is low-risk whenever it happens.
2. Add modular anesthesia-machine profiles and capabilities, including normal
   single-halogenated-agent interlock behavior, agent switching with residual
   washout, optional experimental overrides, direct injection, and eventually
   automated end-tidal control.
3. Add multi-gas behavior, including nitrous oxide coadministration and
   concentration/second-gas effects, only after coupled-gas equations and
   reference cases are defined.
4. Add scenario events, save/load, deterministic replay, comparison runs, and
   simulation forking.
5. Add IV pharmacokinetic and effect-site models after simulation forking is
   available.
6. Add modular effect models such as hypnosis/eBIS and nociceptive-response
   predictions, each with explicit model version and provenance.
7. Add validated physiologic modifiers such as renal or hepatic dysfunction,
   cardiopulmonary bypass, and ECMO where supported by the selected model.
8. Add species-specific patient/model profiles without treating non-human
   patients as scaled humans.
9. Continue accessibility, performance, documentation, packaging, signing, and
   distribution work without mixing those concerns into the scientific core.

Built-in profiles should remain read-only and support a future
"duplicate and customize" workflow with lineage and schema metadata.
