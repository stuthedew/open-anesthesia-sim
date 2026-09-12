# Domains to review against, and the design principles they carry

**Resident by necessity; no `paths:`, deliberately.** It governs the moment an
approach is chosen — a design round, or any reply recommending one route over
another — and a reply is not preceded by a read. Path-scoped, it reached that
moment only when a session happened to open an item file (`PL-WWDT`);
`docs/resident-instructions.md` carries the argument.

**Scope, on sight rather than three sentences away.** This is the standard for
the **simulator** — `src/`, `tests/`, `docs/MODEL.md`, `README.md` — and for
any conversation deciding what goes into them. It is not the bar for the
apparatus (`subprojects/docket/`, `tools/`, `.claude/`, `docs/worker.md`,
`CLAUDE.md`), which is held to the deliberately lower
`.claude/rules/apparatus-standard.md`. `PL-6SBB` is what the mirror error cost:
a session applied the apparatus bar to `src/`, quoting it correctly from a
sentence whose scope sat too far away to travel.

`CLAUDE.md` requires review to reach past conventional software-engineering
concerns and to reflect the standard expected from a top-tier specialist in
the relevant field. This file is the list of fields that means here, and the
principles that follow from them.

Relevant domains include, but are not limited to:

- pharmacokinetic, pharmacodynamic, physiologic, and inhaled-anesthetic
  modeling;
- numerical simulation methods, solver choice, timestep behavior, stability,
  interpolation, and error handling;
- model verification, validation, applicability domains, uncertainty,
  sensitivity analysis, and reproducibility;
- anesthesia and critical-care domain conventions where they affect
  terminology, units, workflow, interpretation, or safety;
- simulation and medical-education best practices, including choosing
  fidelity appropriate to the learning objective and making model limitations
  visible;
- human factors, cognitive ergonomics, mode awareness, error prevention,
  attention management, and prevention of stale-state or wrong-context
  interpretation;
- information architecture, interaction design, UI/UX, visual hierarchy,
  responsive behavior, and cross-platform interaction patterns;
- scientific and clinical data visualization, including axis choice, scale,
  normalization, reference ranges, uncertainty, annotations, and avoidance of
  misleading visual encodings;
- accessibility, typography, color use, contrast, keyboard/touch interaction,
  and color-vision deficiencies;
- software architecture, APIs, data schemas, testing strategy, performance,
  security, privacy, packaging, dependency management, and maintainability;
- provenance, citations, versioning, documentation, reproducible examples, and
  long-term scientific stewardship;
- product-level risks such as ambiguous terminology, false precision,
  inappropriate defaults, overconfident presentation, and features that could
  encourage unintended clinical use.

Apply these principles when working in, or choosing an approach for, that
code:

- Proactively surface important domain-specific concerns even if the project
  owner did not explicitly ask about that discipline.
- Favor interfaces that prevent errors over interfaces that merely warn after
  an error occurs.
- Minimize hidden modes, surprising defaults, context-dependent behavior, and
  stale UI state.
- Consider how an expert, trainee, distracted clinician, color-blind user,
  keyboard user, and touch-device user could each interpret or misuse an
  interface.
- For simulation behavior, separate verification (the implementation solves
  the intended equations correctly) from validation (the equations and model
  adequately represent the intended phenomenon).
- Preserve enough provenance and metadata that a future reviewer can determine
  exactly why a model, equation, constant, UI convention, or design decision
  exists.

## Name the number that would change your mind, then go and count it

Before proposing to tighten anything — a bar, a filter, a threshold, a scope
cut, a check retirement — state what the suppressed side would have to be worth
for the proposal to be *wrong*, and then measure it. Not "this cuts inflow by
30%", but "this is worth it only if fewer than N% of what it suppresses would
have mattered", followed by the count.

This is not a reasoning failure and more careful reasoning does not fix it.
When one side of a trade carries a number and the other does not, the numbered
side wins on *fluency* rather than on merit — 21 preregistered experiments,
N ≈ 23,000, in Chang LW, Kirgios EL, Mullainathan S, Milkman KL, "Does counting
change what counts? Quantification fixation biases decision-making", PNAS
2024;121(46):e2400215121 (https://doi.org/10.1073/pnas.2400215121), who name it
*quantification fixation* and identify comparison fluency as the mechanism. A
session that has just finished computing a rate is at its most exposed, not its
least.

The form is OMB Circular A-4's threshold analysis (2003), which states the
failure and its remedy in one paragraph: "the most efficient alternative will
not necessarily be the one with the largest quantified and monetized net-benefit
estimate … Threshold or 'break-even' analysis answers the question, 'How small
could the value of the non-quantified benefits be (or how large would the value
of the non-quantified costs need to be) before the rule would yield zero net
benefits?'" What is scripted is the question, never the answer: A-4 leaves how
important the non-quantified side may be to professional judgment, which is
`CLAUDE.md`'s own refusal to script the judgment half arriving from regulatory
practice rather than from software.

**Worked example, 2026-09-12.** A session measured the workflow lane's
self-generation rate at 0.69 new items per item worked and proposed raising the
apparatus capture bar on the strength of it. The count it never ran — how many
open items that bar would have suppressed — was 67% still-real findings, which
killed the proposal. The project owner caught it by instinct first; the number
only confirmed what the objection already said (`PL-LKGL`, `PL-27S8`).

The principles governing what a **displayed clinical value** may imply —
false precision, modeled versus measured, misleading plots, visible model
limitations — are not here. They are in `CLAUDE.md`'s safety-critical
clinical-output standard, so that the safety floor is stated in exactly one
place.

A **reference implementation measured nothing**, and saying otherwise in a
reply is the same error as writing it into a file: "it comes from Gas Man"
describes a program's parameter set, not a measurement. It may still be
*adopted* as the authority for a constant, on a recorded decision, and this
project has done so for most of what it stores — the `tier` and `adopted`
fields on each entry under `src/anesthesia_sim/data/` are what say which, so a
reply ruling the practice out in general is wrong about the shipped set.
`docs/MODEL.md` § "Source hierarchy: what may be cited as the authority for a
value" is where that question is decided, and the only place it is. That rule
in full, and what a docstring and an error message owe a reader, are in
`.claude/rules/sources-and-docstrings.md`. Both fire with a file already open,
so both load on a path rather than at launch. The concrete bar for `core/` —
that it should read like the domain — is in `.claude/rules/core-domain.md`.
