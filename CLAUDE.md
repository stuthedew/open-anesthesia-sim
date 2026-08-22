# Repository instructions

These instructions apply to all AI coding agents working on this repository.

## Instruction maintenance and behavior transfer

- Treat project-relevant standing behavior or process requests from the user as candidates for the canonical repository instructions. When a request should reasonably carry across future sessions or AI agents, proactively recommend updating `CLAUDE.md` or another appropriate project instruction/documentation file. Do not turn clearly one-off requests into permanent project policy.
- Before modifying `CLAUDE.md`, `AGENTS.md`, or another repository instruction file, read the current file in full and review any relevant companion instruction files.
- Integrate new instructions where they logically belong in the existing document. Prefer updating an appropriate existing section or creating a focused section over blindly appending new sentences at the end.
- On each instruction-file update, review the document as a whole for redundancy, overlap, conflicts, stale wording, and opportunities to consolidate. Do not perform unrelated rewriting merely because an update is being made.
- Prefer the smallest edit that fully captures the new intent while keeping the document coherent and reasonably concise.
- Preserve all previously established behavior when reorganizing, editing, or condensing instructions. Editorial changes made for clarity, concision, organization, or efficiency must not add, remove, weaken, strengthen, broaden, narrow, reprioritize, or otherwise change intended behavior unless the user explicitly requests that behavioral change.
- When combining overlapping instructions, retain every substantive constraint, exception, priority, and distinction. If semantic equivalence cannot be established confidently, keep the instructions separate rather than risk behavior drift.
- When a new explicit user instruction intentionally conflicts with older repository guidance, follow the newer instruction and revise the older wording as needed so the document remains internally consistent.
- Keep `CLAUDE.md` as the canonical shared behavior source. Keep `AGENTS.md` minimal and delegating to `CLAUDE.md` unless a genuinely agent-specific instruction is required.
- Before committing an instruction-file edit, review the revised document against the prior version for unintended semantic or behavioral drift.

## Architecture and development discipline

- Keep scientific/simulation code independent of Flet.
- Put no simulation calculations in UI callbacks.
- Treat simulation time as explicit state, never wall-clock time.
- Preserve deterministic results for identical inputs.
- Add or update tests with every core behavior change.
- Keep agent/model parameters in validated, versioned data files.
- Do not add executable equations to data files.
- Do not implement beyond the current milestone.
- Run pytest, Ruff, and the configured type checker before finishing.

## Safety-critical clinical-output standard

This application is intended as an educational/simulation tool and will carry appropriate disclaimers that it is not intended for clinical patient care. Nevertheless, assume that a clinician could use displayed values or model outputs to influence real-world patient management.

Therefore, any code path or displayed information that could plausibly affect patient management must be treated as safety-critical. Examples include:

- drug dose, infusion-rate, concentration, weight-based, or unit calculations;
- PK/PD state calculations and predictions;
- effect-site concentrations, predicted effects, MAC-equivalent values, interaction surfaces, and similar derived clinical values;
- model selection and model-compatibility logic;
- covariate transformations such as weight scalars, age adjustments, allometry, renal/hepatic modifiers, or unit conversions;
- thresholds, warnings, alarms, recommendation-like language, or other information a clinician might act on;
- values presented in graphs, tables, labels, or summaries where an error could alter clinical interpretation.

For safety-critical paths:

- Favor correctness, traceability, explicitness, and auditability over cleverness, abstraction, convenience, or development speed.
- Keep calculation logic pure and independent from presentation/UI code whenever feasible.
- Use explicit units and avoid implicit unit conversions. Prefer unit-aware types or equivalent safeguards where practical.
- Validate required inputs, units, ranges, model applicability, and model compatibility before calculation.
- Do not silently substitute defaults, coerce invalid data, or continue with missing required inputs when doing so could produce a plausible but incorrect clinical value.
- Version and record provenance for scientific models, equations, constants, parameter sets, and clinically meaningful transformations.
- Maintain deterministic behavior for identical inputs and model versions.
- Validate numerical implementations against published reference cases, analytic solutions, independently calculated test vectors, or other authoritative references whenever available.
- Include boundary, invalid-input, pathological-input, and regression tests in addition to ordinary nominal-case tests.
- When a safety-critical bug is found, add a regression test that would have caught it.
- Prefer an obvious failure/error state to displaying a plausible-looking number when correctness cannot be established.
- Treat presentation correctness as part of safety: the correct number with the wrong units, label, patient context, stale state, model name/version, or provenance is still a safety failure.
- Test the end-to-end path when appropriate: patient inputs -> model selection -> calculation -> units -> formatting -> displayed value.
- Make clinically meaningful displayed values traceable to the exact model/version, inputs, units, and transformations that produced them.

Disclaimers do not lower the engineering standard for these paths.

## Proactive expert review and domain best practices

Do not limit review or recommendations to conventional software-engineering concerns. Treat development of this application as a multidisciplinary professional product-design problem and proactively identify material improvements anywhere they affect scientific validity, safety, interpretability, usability, educational value, maintainability, or reliability.

Recommendations should reflect the standard expected from a top-tier specialist in the relevant field, not merely common or minimally acceptable practice. When the user's proposed approach is materially weaker than a better established approach, say so clearly and recommend the stronger approach with the reasoning behind it.

Relevant domains include, but are not limited to:

- pharmacokinetic, pharmacodynamic, physiologic, and inhaled-anesthetic modeling;
- numerical simulation methods, solver choice, timestep behavior, stability, interpolation, and error handling;
- model verification, validation, applicability domains, uncertainty, sensitivity analysis, and reproducibility;
- anesthesia and critical-care domain conventions where they affect terminology, units, workflow, interpretation, or safety;
- simulation and medical-education best practices, including choosing fidelity appropriate to the learning objective and making model limitations visible;
- human factors, cognitive ergonomics, mode awareness, error prevention, attention management, and prevention of stale-state or wrong-context interpretation;
- information architecture, interaction design, UI/UX, visual hierarchy, responsive behavior, and cross-platform interaction patterns;
- scientific and clinical data visualization, including axis choice, scale, normalization, reference ranges, uncertainty, annotations, and avoidance of misleading visual encodings;
- accessibility, typography, color use, contrast, keyboard/touch interaction, and color-vision deficiencies;
- software architecture, APIs, data schemas, testing strategy, performance, security, privacy, packaging, dependency management, and maintainability;
- provenance, citations, versioning, documentation, reproducible examples, and long-term scientific stewardship;
- product-level risks such as ambiguous terminology, false precision, inappropriate defaults, overconfident presentation, and features that could encourage unintended clinical use.

Apply the following principles when making recommendations:

- Proactively surface important domain-specific concerns even if the user did not explicitly ask about that discipline.
- Prioritize recommendations by consequence. Safety, scientific correctness, misleading output, and irreversible architectural problems outrank visual polish or minor code style.
- Distinguish a required correctness/safety issue from a high-value recommendation and from optional polish.
- Do not create scope creep by silently implementing out-of-milestone ideas. Recommend them and explain their value; implement them only when they fit the current milestone or the user approves the scope change.
- Prefer established standards, validated methods, and authoritative primary sources over convention-by-habit. When a recommendation depends on current standards, guidance, libraries, or evidence, verify the current source rather than relying on memory.
- Make uncertainty and model limitations visible rather than allowing numerical precision or polished graphics to imply more certainty than the model supports.
- Avoid false precision in displayed outputs. Formatting precision should be justified by model fidelity, input precision, and practical interpretability.
- Clearly distinguish modeled/internal states from measured or directly observable quantities. Do not present a predicted value in a way that could reasonably be mistaken for a measurement.
- Design clinically meaningful displays so units, model identity, relevant assumptions, simulation state, and context cannot be easily misread.
- Favor interfaces that prevent errors over interfaces that merely warn after an error occurs.
- Minimize hidden modes, surprising defaults, context-dependent behavior, and stale UI state.
- Consider how an expert, trainee, distracted clinician, color-blind user, keyboard user, and touch-device user could each interpret or misuse an interface.
- For plots and dashboards, optimize first for accurate interpretation and comparison, then aesthetics. A visually attractive but misleading graph is a defect.
- For simulation behavior, separate verification (the implementation solves the intended equations correctly) from validation (the equations/model adequately represent the intended phenomenon).
- Preserve enough provenance and metadata that a future reviewer can determine exactly why a model, equation, constant, UI convention, or design decision exists.
- Challenge assumptions when warranted. Do not preserve a weak design solely because it was proposed earlier.

The goal is not to maximize the number of suggestions. Surface the few recommendations that would materially improve the quality of the product, and explain them at the level needed to make a sound engineering or design decision.
