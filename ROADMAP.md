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
"Planned milestones" below, is expanding the volatile model with additional
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

## Planned milestones

This section is, in practice, the current milestone plan: with no
milestone after v0.1.0 formally scoped yet (see "Next milestone" above),
this ordering is what gets picked up next. Each item is still deliberately
left unspecified (no goal, required scope, or definition of done) until it
is actually promoted into a scoped milestone per the development rules
above — and each item is kept to one improvement, so scoping one does not
implicitly drag others along with it. Exact version numbers after v0.1.0
remain provisional and must be assigned when each milestone is fully
specified.

1. Expand the volatile model with validated, data-driven agent definitions and
   broader reference cases. When this is scoped: consider migrating
   `core/parameters.py`'s JSON validation to Pydantic — the boilerplate in
   its `_require_*` helpers compounds with each new agent/patient schema,
   and the module is isolated behind plain dataclass returns, so the switch
   is low-risk whenever it happens.
2. Add a modular anesthesia-machine abstraction with normal
   single-halogenated-agent interlock behavior — the safety baseline every
   later machine feature below builds on.
3. Add agent switching with residual washout accounting, after item 2.
4. Add an optional experimental-override mode that can bypass standard
   interlocks, clearly labeled as non-standard, after item 2.
5. Add direct agent injection into the circuit, bypassing the vaporizer and
   its interlocks, after item 2.
6. Add automated end-tidal control (closed-loop titration to a target
   end-tidal concentration), after item 2.
7. Add nitrous oxide coadministration as a second inhaled gas, only after
   coupled-gas equations and reference cases are defined.
8. Add concentration and second-gas effects for coadministered gases, after
   item 7.
9. Add scenario events (timed parameter or state changes during a run).
10. Add scenario save/load.
11. Add deterministic replay of a saved scenario, after item 10.
12. Add side-by-side comparison of multiple scenario runs.
13. Add simulation forking (branch a running simulation into an independent
    copy).
14. Add IV pharmacokinetic and effect-site models, after item 13 (simulation
    forking) is available.
15. Add a modular hypnosis/eBIS effect model, with explicit model version and
    provenance.
16. Add a modular nociceptive-response effect model, with explicit model
    version and provenance.
17. Add validated renal/hepatic dysfunction modifiers, where supported by the
    selected model.
18. Add validated cardiopulmonary bypass modeling, where supported by the
    selected model.
19. Add validated ECMO modeling, where supported by the selected model.
20. Add species-specific patient/model profiles without treating non-human
    patients as scaled humans.
21. Improve accessibility (keyboard navigation, contrast, screen-reader
    support, color-vision-safe encodings).
22. Improve performance, starting with the open threads already logged in
    `docs/WORKING_NOTES.md` (unbounded history growth, coupled
    simulation/render cadence).
23. Continue documentation work.
24. Add packaging, signing, and distribution work for shipping the app.
25. Add a user-facing preferences/settings panel (theme, chart window, slider
    ranges, and similar display settings). Pre-requisite: consolidate the
    UI/display constants currently scattered across `app/theme.py`,
    `app/simulation_view.py`'s module-level constants, and the default
    values duplicated between `core/*.py` dataclasses and
    `app/controller.py`, into one settings module the panel can read from
    and write to, rather than adding a fourth scattered location. This
    panel must never expose the scientific parameters in `data/*.json`
    (partition coefficients, tissue volumes, etc.) for editing — those stay
    validated, versioned, and cited, changed only through deliberate
    scientific review per `CLAUDE.md`'s safety-critical standard, not an ad
    hoc settings screen.

None of items 2-24 mix scientific-core and UI/tooling concerns within a
single milestone; where one depends on another (e.g. 3-6 on 2, 8 on 7, 11
on 10, 14 on 13), that dependency is noted inline rather than bundled into
one item.

Built-in profiles should remain read-only and support a future
"duplicate and customize" workflow with lineage and schema metadata.
