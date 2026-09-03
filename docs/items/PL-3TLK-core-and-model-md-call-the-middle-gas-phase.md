---
id: PL-3TLK
title: core/ and MODEL.md call the middle gas-phase state F_C (circuit), but the domain's symbol is F_I (inspired) and the F_A/F_I curve is the field's canonical teaching graph
touches: src/anesthesia_sim/core/circuit.py, docs/MODEL.md
added: 2026-09-03
priority: P2
effort: M
status: ready
classes: refactor, docs
feature: core-domain-language
verify: uv run pytest -q tests/unit/test_circuit.py tests/reference/test_circuit_wash_in.py && grep -q 'inspired_partial_pressure_fraction' src/anesthesia_sim/core/circuit.py
---

**Problem.** The model's gas-phase cascade is delivered -> circuit -> alveolar,
and `docs/MODEL.md` § "Symbols" names the middle state $`F_C`$, "Breathing-circuit
sevoflurane fraction". `core/circuit.py` carries it as
`BreathingCircuit.circuit_concentration_fraction`.

The inhaled-anesthetic literature has no $`F_C`$. Its gas-phase cascade is
$`F_D \rightarrow F_I \rightarrow F_A`$ — delivered, inspired, alveolar — and
the middle term is the inspired fraction. Under this model's stated boundary
(one ideal, perfectly mixed circuit, no dead space, no separate inspiratory and
expiratory limbs) the gas the patient inspires *is* the circuit gas, so
$`F_C \equiv F_I`$ identically. The model has named the state after its
container rather than after the clinical quantity it is.

**Why it matters.** Three reasons, in descending order.

First, the $`F_A/F_I`$ curve is the canonical teaching graph of this entire
subject — the one every trainee meets uptake through, and the one this
simulator exists to let a learner produce. Its denominator is the state this
project calls "circuit". A reader who knows the domain cannot find the curve's
denominator in the code, which is exactly the translation step
`.claude/rules/core-domain.md` exists to remove.

Second, naming the state $`F_I`$ makes the field's two teaching gradients fall
out of the model the project already has, where naming it $`F_C`$ hides them:

- $`F_D - F_I`$ is caused by rebreathing, and widens as fresh gas flow falls;
- $`F_I - F_A`$ is caused by patient uptake, and equals uptake divided by
  alveolar minute ventilation.

Both are computable today from the three gas-phase states already modelled.

Third, this is the clearest instance in the tree of the defect planned-milestone
item 29 exists to fix, so it is a worked example of the bar rather than an
isolated rename.

No behavior, equation, parameter or numerical method changes: the quantity, its
value and its dynamics are untouched. This is a naming and documentation change.

**Where.** `docs/MODEL.md` § "Symbols", § "Conventions", § "Breathing circuit"
and every equation carrying $`F_C`$; `core/circuit.py`
(`circuit_concentration_fraction`, `set_delivered_concentration`,
`BreathingCircuitState`); `core/uptake_system.py` where the circuit fraction is
read; and every reader in the interface layer. Grep for
`circuit_concentration_fraction` before scoping the size.

**The judgment this needs, and it is not a blind rename.** $`F_C \equiv F_I`$
holds *because of* this model's circuit assumptions. It would stop holding if
the circuit were ever split into inspiratory and expiratory limbs, as Lerou and
Booij's three-part breathing system does. So the change should name the state
$`F_I`$ **and record the assumption that makes the identity true**, in
`docs/MODEL.md` § "Model boundary" or § "Assumptions", so that a later
multi-limb circuit is a documented departure rather than a silent contradiction.
An alternative worth weighing is keeping both names — the state is $`F_I`$, the
compartment holding it is the circuit — which is what the code's own structure
already expresses, since the accessor hangs off `BreathingCircuit`.

**Found.** Scoping session for planned-milestone item 29 (`core/` reads like the
domain), 2026-09-03, from a reference supplied by the project owner: Hendrickx
JFA, De Wolf A. Special aspects of pharmacokinetics of inhalation anesthesia.
In: Schuttler J, Schwilden H (eds). Modern Anesthetics. Handbook of Experimental
Pharmacology 182. Springer, 2008:159-186. The cascade and the naming of
$`F_D`$, $`F_I`$ and $`F_A`$ are set out on pp. 161-162; the attribution of
$`F_D - F_I`$ to rebreathing and $`F_I - F_A`$ to uptake on pp. 169 and 171; the
$`F_A/F_I`$ curve's didactic role on p. 167.

The same source settles a naming question open in the same scoping round: "in
the gas phase, either 'fraction,' 'concentration,' or 'partial pressure' can be
used" (p. 160), so a code convention distinguishing "concentration" from
"partial pressure" among the gas compartments would encode a distinction the
domain does not make.

**Done when.** The middle gas-phase state carries the domain's name throughout
`core/` and `docs/MODEL.md`, the assumption making $`F_C \equiv F_I`$ is stated
where the model boundary is stated, `make check` passes, and no modelled value
changed.
