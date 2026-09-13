---
id: PL-VZL0
title: Cite MODEL.md from every core/ function implementing a governing equation, and restate the solved form the spec lacks
priority: P2
effort: S
status: done
closed: 2026-09-13
classes: docs, refactor
feature: core-domain-language
touches: src/anesthesia_sim/core, tools/doc_check.py
added: 2026-09-03
verify: uv run pytest && grep -qF '`docs/MODEL.md` § "Tissue uptake and return"' src/anesthesia_sim/core/tissue.py
---

**Problem.** `docs/MODEL.md` § "Selected method (as implemented)" names the five
functions that compose a simulation step. None of those five names the section
back. The map is one-directional: a reader holding the document can find the
code, and a reader holding the code cannot find the document.

**Why it matters, and why restating is not duplication.** The scoping round's
worry was that restating equations in docstrings creates a second source of
truth that drifts from `docs/MODEL.md`. Measured against the tree, that worry
does not apply to the case at hand, because the two are not saying the same
thing.

`docs/MODEL.md` writes the **differential equations**. `core/` implements their
**analytic solutions**. The spec carries a solved exponential form in exactly
one place — the v0.0.2 circuit wash-in, at line 307. So `TissueGroup.advance`
and `VenousBloodCompartment.advance` both implement

$$F(t+\Delta t) = F_{\text{target}} + \left[F(t) - F_{\text{target}}\right]e^{-\Delta t/\tau}$$

which appears nowhere in the specification. A reader matching that code against
§ "Tissue uptake and return" has to perform the integration in their head to see
that they correspond. That is precisely the translation step
`.claude/rules/core-domain.md` forbids, and the restatement is the missing half
rather than a second copy.

**The emphasis inverted on 2026-09-03.** The owner's bar is that a reviewer
follows the code without going to another document, and a citation is precisely
a pointer to go to another document. So the equation visible at the site is the
deliverable and the citation is provenance — the reverse of how this item was
first written.

**And `PL-GS5X` now delivers most of it.** Under the exact matrix exponential,
the matrix assembly *is* the governing equations, so the alveolar, circuit,
tissue and venous balances need no restatement at all. What remains for this
item is the residue: the capacity and time-constant properties, and whatever
numerics the exponential needs, which are not domain equations and should be
labelled as numerics rather than dressed up as physiology. Re-measure the scope
after `PL-GS5X` lands rather than assuming this brief still describes it.

**The rule, in two parts.** Cite always: every function implementing a governing
equation names the `docs/MODEL.md` section it implements, in the form
`docs/MODEL.md § "Tissue uptake and return"`, so `PL-X2XX` can check the section
exists. Restate selectively: give the solved form only where the spec does not
carry it, and never restate what the spec already states — the circuit wash-in
already has its closed form at line 307 and needs a citation only.

**Where.** The five functions § "Selected method (as implemented)" already names
— `BreathingCircuit.advance_fresh_gas`,
`AgentUptakeSystem._exchange_circuit_and_alveoli`, `TissueGroup.advance`,
`VenousBloodCompartment.advance`, `AlveolarCompartment.apply_blood_uptake` —
plus the capacity and time-constant properties on `TissueGroup`,
`VenousBloodCompartment` and `AlveolarCompartment`, which implement
§ "Compartment capacities" and the $`\tau`$ definitions.

**Blocked on `PL-GS5X`** (the exact step, which changes what is left to do
here) **and on `PL-X2XX`** (doc_check's citation check reads neither
`docs/items/*.md` nor source docstrings). Without it these citations are
unenforced prose, and a section rename would silently orphan every one of them —
which is the failure mode the citation is being added to prevent. `PL-X2XX` is
already `ready` and is the machinery this item needs; `PL-GS5X` decides how
much of this item is left.

**Done when.** Every function named above cites its `docs/MODEL.md` section;
each solved form absent from the spec is stated once beside the code that
implements it and nowhere else; `PL-X2XX`'s check resolves all of them; `make
check` passes; and no modelled value changed.

**Closed 2026-09-13. The scope re-measured after `PL-GS5X`, as the brief
asked.** § "Selected method (as implemented)" now names exactly two modules -
`core/governing_equations.py`, which assembles $`A`$, and
`core/matrix_exponential.py`, which computes $`\\exp(A\\Delta t)`$ and carries no
physiology. The five functions this item was written against are down to those
two plus the capacity and time-constant properties, and the brief's prediction
held: **no solved form needed restating.** The matrix assembly *is* the
governing equations, entry by entry, and it already says so.

Cited, all in the section-mark form so the gate reads them:

- `TissueGroup.capacity_l` and `.time_constant_s` -> §§ "Tissue compartments",
  "Tissue uptake and return";
- `VenousBloodCompartment.capacity_l` and `.time_constant_s` -> §§ "Blood
  compartments", "Venous blood";
- `AlveolarCompartment.concentration_fraction` -> § "Gas compartments";
- `build_system_matrix` and `UptakeEquationSettings` -> §§ "Governing
  equations", "Selected method (as implemented)";
- `TissueGroupEquationSettings.washin_rate_s` -> § "Tissue uptake and return".

Each docstring states the expression as well as the pointer, which is the
2026-09-03 inversion: the equation visible at the site is the deliverable and
the citation is provenance. The two time constants now say what distinguishes
them - $`\\lambda_{b:g}`$ cancels in the venous pool because the pool and the
blood flowing through it are one phase - which is the question a reader of the
two adjacent files actually has.

`matrix_exponential.py` got the opposite treatment, per the brief: it is
labelled **numerics, not physiology**, in as many words, so a reader looking
for the model is sent back to `governing_equations.py`.

**`build_system_matrix` already cited § "Governing equations" - in the
possessive form, which `tools/doc_check.py` does not read.** It was unenforced
prose, which is the exact failure this item exists to prevent, sitting in the
one function that assembles the whole model. Converted.

**This item was blocked on a check that did not do what it was believed to
do.** The brief made `PL-X2XX` the prerequisite because "without it these
citations are unenforced prose, and a section rename would silently orphan
every one of them". `PL-X2XX` closed, but its pattern read `,` and `:` between
a document and its quotation and not `§` - the form this brief mandates - so
every citation written to this item's rule would have been invisible. `PL-V13T`
fixed that first; mutation-checked here afterwards, pointing this item's own
tissue citation at a section that does not exist, which now errors.

**The `verify:` command was wrong and is corrected rather than worked around.**
It grepped for `docs/MODEL.md § "..."` with no backticks around the path - the
brief's markdown code span lost them - and `doc_check` only reads the
**backticked** form, so the command specified a citation the gate cannot see.
Corrected to the backticked form and run: it fails on `origin/main` and passes
here. Both halves of the six-wrong-commands pattern in the `docket` skill, in
one field: written away from the work, and never executed.
