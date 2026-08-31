---
paths:
  - "src/**"
  - "docs/**"
  - "tests/**"
---

# Domains to review against, and the design principles they carry

`CLAUDE.md` requires review to reach past conventional software-engineering
concerns and to reflect the standard expected from a top-tier specialist in
the relevant field. This file is the list of fields that means here, and the
principles that follow from them. It loads when a session reads the
simulator, its tests, or its documentation, which is where they apply.

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

Apply these principles when working in or recommending changes to that code:

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

The principles governing what a **displayed clinical value** may imply —
false precision, modeled versus measured, misleading plots, visible model
limitations — are not here. They are in `CLAUDE.md`'s safety-critical
clinical-output standard, which loads in every session, because a session
that opens no file matching this rule must still see them.
