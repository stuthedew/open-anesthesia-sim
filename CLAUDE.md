# Repository instructions

These instructions apply to all AI coding agents working on this repository.

## Architecture and development discipline

- Keep scientific/simulation code independent of Flet.
- Put no simulation calculations in UI callbacks.
- Treat simulation time as explicit state, never wall-clock time.
- Preserve deterministic results for identical inputs.
- Add or update tests with every core behavior change.
- Keep agent/model parameters in validated, versioned data files.
- Do not add executable equations to data files.
- Do not implement beyond the current milestone. `ROADMAP.md` is the
  authoritative version and milestone map.
- Run pytest, Ruff, and the configured type checker before finishing.

## Session and tool-use efficiency

Session cost scales with the number of turns multiplied by the size of the
context, because the whole conversation is resent on every turn. Long
sessions are therefore disproportionately expensive, and the practices
below work mainly by keeping context small rather than by choosing a
cheaper model. They never override the safety-critical verification
requirements below — trimming applies to routine, low-risk iteration, not
to skipping a check before a commit or before finishing a task.

- Keep a session short and scoped to one topic. Start a fresh session for
  an unrelated topic rather than continuing a long one, and prefer a fresh
  session over compacting an existing one: compaction costs a summarization
  pass and drops detail that this repository's provenance and safety
  requirements depend on. `docs/PUNCH_LIST.md` and `docs/WORKING_NOTES.md`
  exist so that a new session can pick up cold — read them and `CLAUDE.md`
  at the start of a task instead of relying on a long prior conversation,
  and update them before ending a session with a thread still open.
- Batch related questions, and related edits, into one turn rather than
  spreading them across several. Each turn resends the entire context.
- Prefer targeted reads (an offset/limit range) over whole-file reads for
  large docs (`docs/MODEL.md`, `docs/WORKING_NOTES.md`) once you know
  roughly where the relevant section is. Read the whole file when editing
  it or when its overall structure matters.
- Delegate broad codebase search and file lookup to exploration subagents,
  whose transcripts stay out of the main context; a small, fast model is
  appropriate for them (`CLAUDE_CODE_SUBAGENT_MODEL` in Claude Code). Treat
  what they return as leads to verify against the source, not as findings
  to rely on.
- Edit `CLAUDE.md` and the core docs in their own session where practical.
  They sit in the cached prefix of every request, so editing one partway
  through a session invalidates that cache for the rest of it.
- Batch related edits before rerunning the full quality suite (`ruff
  format`, `ruff check`, `mypy`, `pytest`) rather than rerunning all four
  after every individual small edit. Still run the full suite before
  finishing or committing. Use `pytest -q` for routine reruns during
  iteration; reserve `--cov` for changes where coverage is actually the
  question (a new test, a new module, a coverage-focused task).
- Match model capability to the work rather than pinning one model for a
  whole session. Reasoning-heavy work — architecture and design decisions,
  new scientific-model design, ambiguous problems or genuine trade-offs,
  non-obvious debugging and root-cause analysis, and anything within the
  scope of "Safety-critical clinical-output standard" below — warrants the
  strongest available model at a high effort setting, both for its design
  and for the review of the final diff. Executing an already-agreed plan
  does not. Presentation of clinical values, and the scientific content of
  `docs/MODEL.md`, are safety-critical work rather than routine execution.
- Claude Code's `opusplan` mode is a reasonable default for that split, with
  two caveats: it returns to the cheaper model for execution, so the
  strong-model review of a safety-critical diff is a deliberate step and not
  an automatic one; and switching models mid-session starts a cold cache, so
  group design and execution into runs rather than alternating between them.
  Model choice never changes what a change must satisfy before it lands, and
  the maintainer still reviews every safety-critical diff regardless of which
  model drafted it.

## Punch list and work selection

`docs/PUNCH_LIST.md` is the prioritized queue of discrete development
tasks. It carries the format spec, the priority/effort/status definitions,
and the current items; read it rather than relying on a restatement here.
The division of labor is: `ROADMAP.md` holds releases, `docs/PUNCH_LIST.md`
holds tasks, `docs/WORKING_NOTES.md` holds the narrative behind them.

- **Capture, always.** Any defect, risk, cleanup, optimization,
  inconsistency, or feature idea identified in a session and not fixed in
  that same session gets an entry in `docs/PUNCH_LIST.md` before the
  session ends. This applies equally to findings the project owner raises
  and to findings you make on your own while working on something else.
  Do not ask whether to record it — recording is cheap and losing it is
  not. Prefer capturing at `P3` over dropping it, and say in your reply
  that you did.
- **Reprioritize, don't just append.** A new entry can demote what was
  previously next, and resolving a blocker promotes what it blocked. Place
  a new item at its correct priority rather than at the end of the file.
- **Close the loop.** When work lands, move its entry to "Recently
  completed" with the commit reference in the same change, and delete any
  now-stale `docs/WORKING_NOTES.md` thread for it.
- **Answer "what should we work on next?" from the file.** Read
  `docs/PUNCH_LIST.md` first and recommend from it, matching effort to the
  session time available rather than re-deriving the options from the
  codebase. `P0` items come first and are handled as hotfixes: their own
  branch and a patch version bump. When nothing is pressing, the
  alternative is milestone work, which means scoping the next milestone in
  `ROADMAP.md` — not starting unscoped feature work.
- **Do not start an `L` item from a punch-list entry.** Promote it into a
  scoped `ROADMAP.md` milestone first, per the development rules there.

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
- Version and record provenance for scientific models, equations, constants, parameter sets, and clinically meaningful transformations. `docs/MODEL.md` is the authoritative specification for the currently implemented model: equations, units, assumptions, parameter provenance, numerical method, and known limitations.
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
