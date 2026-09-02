---
id: PL-2HTF
title: MODEL.md's numerical requirements contradict the operator split it implements
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-08-30
verify: python3 tools/doc_check.py check
---

**Problem.** `docs/MODEL.md:514-522` states a normative requirement list — "The
implementation must: … 2. evaluate every transfer from one consistent state" —
that the implementation does not satisfy and is not intended to satisfy. Two
paragraphs below, `:532-534` describes the first-order operator split actually
used, in which each sub-step sees the state the previous sub-step left.
Concretely:

- `core/uptake_system.py:157-166` reads the *post-fresh-gas* circuit
  fraction for the circuit/alveolar exchange, and hands the *post-ventilation*
  alveolar fraction to the tissues;
- `core/patient.py:129-135` evaluates `tissue_return_fraction` after the tissue
  loop has already mutated the tissues, so venous mixing sees end-of-step
  tissue state rather than start-of-step.

Neither ordering is stated anywhere in the document.

**Why it matters.** `docs/MODEL.md` is this project's authoritative
specification, and a normative `must` the code deliberately violates is worse
than a missing one: a reader checking the implementation against it concludes
the code is wrong, or — the likelier failure — a later change "restores"
simultaneous evaluation and silently alters every modelled value. The
sub-step ordering is also not a detail: it is what the splitting error measured
in `tests/reference/test_coupled_dynamics.py` is the error *of*, so a reader
cannot reason about that bound without it.

**Where.** `docs/MODEL.md:514-522` (the requirement list) and `:532-534` (the
implemented split); `core/uptake_system.py:157-166`;
`core/patient.py:129-135`.

**Approach.** Rewrite the requirement list to describe the split actually used,
and name the sub-step ordering explicitly — including that venous mixing
follows tissue advance within the patient sub-step, which today is visible only
by reading `patient.py`. Requirement 2 as written should become a statement of
what *is* held consistent (settings are piecewise-constant across the step;
each pairwise exchange is solved exactly) rather than a claim of simultaneity.

**Scope note.** This is an instance of the class PL-036 (extend `doc_check.py`
to the statements it currently cannot decide) describes, and PL-036's Decided
section deliberately scopes that item to one link only — the fifteen "Minimum
displayed outputs" bullets naming their snapshot field. Do not re-scope PL-036
to swallow this; fix the instance here and cite it in PL-036 as evidence for a
later extension.

**Class note.** Captured with a suggested `science` class, filed as
`defect`/`docs`: `docket check` will not seat a `science`-classed item below
`P1`, and this changes no equation, parameter or modelled value — the artifact
that is wrong is the document. That matches PL-KQKM and PL-MS54, the two other
document-versus-code contradictions found in the same review.

**Done when.** `docs/MODEL.md`'s numerical requirement list describes the
operator split the code implements, names the sub-step ordering including the
tissue-then-venous order inside the patient step, and no longer requires
simultaneous evaluation.
