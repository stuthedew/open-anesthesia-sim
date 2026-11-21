---
id: PL-XXXJ
title: Three refusal messages in core/ send a reader to docs/MODEL.md § Tissue groups for a reason that section does not give
priority: P2
effort: S
status: done
classes: defect
feature: model-spec-accuracy
touches: src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/patient.py, tests/unit/test_patient.py, tests/unit/test_supported_ranges.py, docs/items/PL-PH3N-docstrings-code-comments-and-one-data-note-that.md
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
closed: 2026-11-21
pr: 2190
payoff: a developer sent to a section by one of three refusals finds there the reason the refusal gives
tests: tests/unit/test_patient.py::test_a_perfusion_fraction_written_on_a_built_patient_is_refused, tests/unit/test_patient.py::test_a_tissue_blood_quotient_outside_the_envelope_is_refused_where_the_patient_forms_it, tests/unit/test_supported_ranges.py::test_a_cardiac_output_written_past_set_cardiac_output_is_refused_at_the_write
---

**Problem.** Three refusal messages in core/ send a reader to docs/MODEL.md § Tissue groups for a reason that section does not give

**Why it matters.** A refusal tells its reader where to read why the limit is where it is. A developer who follows these three pointers finds a section that gives no reason, and has to search the code for it.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. The messages are in `src/anesthesia_sim/core/`, which is outside what a session may fix in place.

**The three messages.**

1. `TissueGroup.__setattr__`, on a tissue:gas coefficient: "the patient checks the group's tissue:blood coefficient only when the group is put in its place (docs/MODEL.md, \"Tissue groups\")".
2. `PatientCompartments.__setattr__`, on the cardiac output: "Change the output with set_cardiac_output, the one way a cardiac output is changed (docs/MODEL.md, \"Tissue groups\")".
3. `TissueGroup.__setattr__`, on the perfusion fraction: "the patient checks that its tissue fractions sum to 1 only when it is built".

§ "Tissue groups" states only $`f_i > 0`$, the rule that the fractions sum to 1, and $`\sum_i Q_i = Q`$. It does not say when the patient checks a coefficient or the sum, or that `set_cardiac_output` is the one way to change the output. A reader sent there by a refusal finds no reason. `.claude/rules/sources-and-docstrings.md` requires a refusal to say where to read why the limit sits where it does.

**What to do.** Either point each message at the place that does give the reason (§ "Mass-balance identity" describes which fields refuse a later write, and the class docstrings give the rest), or add the missing sentence to § "Tissue groups". The first is smaller and changes no document.

**Done when.** Each of the three messages names a section or a docstring that states the reason it gives.

**What was done, 2026-11-21.**

1. The tissue:gas coefficient refusal now names `docs/MODEL.md` § "The numerical envelope". Its paragraph "The tissue:blood coefficient is checked where it is formed" says when the patient checks the quotient, and that a group's tissue:gas coefficient cannot be changed after the group is built.
2. The cardiac output refusal now names `docs/INTERFACE.md` § "Supported input ranges", which says that the write is refused "so that cardiac output has one way in".
3. The perfusion fraction refusal now names `TissueGroup.__setattr__` in `core/tissue.py`, whose docstring gives the reason. The message and that docstring also said that the patient checks the sum "only when it is built". `PatientCompartments.__setattr__` checks it again when a tissue group is replaced, so both now say so. The check of the interface documents listed the same wording as entry 11 of its item `PL-PH3N` (stale docstrings and comments), and pull request #2181 corrected the matching sentence of `docs/INTERFACE.md` § "Supported input ranges" on `main` while this branch was open.

**The tests fail on the messages as they were.** With `core/tissue.py` and `core/patient.py` restored to `012db5bfc`, `uv run pytest -q tests/unit/test_patient.py tests/unit/test_supported_ranges.py` gave 3 failed and 210 passed, and the three failures are the tests in `tests:`. Each now compares the whole message.

**Documents checked.** `docs/MODEL.md` §§ "Tissue groups", "Blood compartments", "Tissue compartments", "Mass-balance identity" and "The numerical envelope"; `docs/INTERFACE.md` § "Supported input ranges"; and a search of `docs/`, `README.md`, `src/` and `tests/` for each message's words.

**Generator check.** Filed by `PL-RMNP` (the check of `docs/MODEL.md` against the code), a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.
