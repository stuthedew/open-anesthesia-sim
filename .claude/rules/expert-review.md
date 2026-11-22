# Domains to review against, and the design principles they carry

**Scope.** This is the standard for the **simulator** — `src/`, `tests/`,
`docs/MODEL.md`, `docs/INTERFACE.md`, `docs/VERIFICATION.md`,
`docs/PARAMETERS.md`, `README.md` — and for any decision about them. `.claude/rules/apparatus-standard.md` is the
apparatus's standard.

This file lists the fields that review reaches, and the principles they carry.

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
- **Parse, don't validate.** A quantity with a check of its own is checked
  once, by building a type only that check produces, and every signature past
  that point takes the type. `.claude/rules/core-domain.md` has the pattern.
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

OMB Circular A-4 names the count break-even analysis. The side with a number
wins on fluency, not merit (Chang et al. 2024, doi:10.1073/pnas.2400215121).

## Count what undoing it would cost, before taking the cheaper route

This is the other half of the trade above: two routes to one end state, the
durable one slower, the cheap one destined to be redone. Doing it twice costs
more than doing it once, so the cheap route is a loan.

State it. **Name what would have to change to switch routes later, and count
what is already downstream of the choice.** One file and nothing stored yet:
take the cheap route, say that is what you did, and move on. Every item file,
every stored parameter entry, every citation in the tree: the cheap route is
not cheaper, because the principal grows with each instance added before it is
repaid, and the durable route is taken now.

**The count runs both ways.** A mechanism with nothing downstream fails this
test as surely as a stop-gap under a thousand call sites passes it, so it is
never a licence to build the larger thing. Reversibility is the discriminator
rather than size or effort (Bezos, 2015 letter to Amazon shareholders).

**Waiting for another instance is the cheap route, not a third one.** A
recommendation to build the durable route only if another instance turns up
builds nothing now, so the count applies to it, and is taken before the wait is
recommended. The rule of three applies only while the abstraction is unknown.

**Where the count cannot be taken, the horizon decides.** The project owner's
form of it, and the one to quote back: *of these options, which will we be glad
we implemented in five years?* It is the tie-breaker and not the opening move:
reach for it where the count is not available, never to avoid taking one.

## Say what would falsify it, then record the instance rather than the rule

An argument licenses the narrowest rule that removes the hazard, never the
widest rule the hazard could motivate. So before writing a rule into
`ROADMAP.md` or `docs/MODEL.md` — the two documents a later session cites to
refuse work — say what would have to change for the sentence to stop being
true: a new substance, a new toolkit, a new mechanism. **If the answer is
already on the roadmap, it is an instance and not a rule.** Write it as one,
with its condition named, and pitch the rule at the altitude that survives.

It fails quietly. A wrongly permanent sentence trips no check and never can,
because altitude is judgment rather than a fact about the tree.

What a displayed clinical value may imply is in `CLAUDE.md`'s safety standard.

Where a value came from, and what a docstring and an error message owe a
reader, are in `.claude/rules/sources-and-docstrings.md`. The bar for `core/`,
that it should read like the domain, is in `.claude/rules/core-domain.md`.
