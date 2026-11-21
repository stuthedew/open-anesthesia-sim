---
id: PL-XXXJ
title: Three refusal messages in core/ send a reader to docs/MODEL.md § Tissue groups for a reason that section does not give
status: untriaged
feature: model-spec-accuracy
added: 2026-11-21
---

**Problem.** Three refusal messages in core/ send a reader to docs/MODEL.md § Tissue groups for a reason that section does not give

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. The messages are in `src/anesthesia_sim/core/`, which is outside what a session may fix in place.

**The three messages.**

1. `TissueGroup.__setattr__`, on a tissue:gas coefficient: "the patient checks the group's tissue:blood coefficient only when the group is put in its place (docs/MODEL.md, \"Tissue groups\")".
2. `PatientCompartments.__setattr__`, on the cardiac output: "Change the output with set_cardiac_output, the one way a cardiac output is changed (docs/MODEL.md, \"Tissue groups\")".
3. `TissueGroup.__setattr__`, on the perfusion fraction: "the patient checks that its tissue fractions sum to 1 only when it is built".

§ "Tissue groups" states only $`f_i > 0`$, the rule that the fractions sum to 1, and $`\sum_i Q_i = Q`$. It does not say when the patient checks a coefficient or the sum, or that `set_cardiac_output` is the one way to change the output. A reader sent there by a refusal finds no reason. `.claude/rules/sources-and-docstrings.md` requires a refusal to say where to read why the limit sits where it does.

**What to do.** Either point each message at the place that does give the reason (§ "Mass-balance identity" describes which fields refuse a later write, and the class docstrings give the rest), or add the missing sentence to § "Tissue groups". The first is smaller and changes no document.

**Done when.** Each of the three messages names a section or a docstring that states the reason it gives.
