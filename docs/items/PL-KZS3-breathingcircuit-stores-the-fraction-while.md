---
id: PL-KZS3
title: BreathingCircuit stores the fraction while every other compartment stores the amount, so mass is not the primitive in one of four
priority: P3
effort: M
status: needs-decision
classes: refactor
feature: core-boundaries
touches: src/anesthesia_sim/core/circuit.py, docs/MODEL.md
added: 2026-09-03
---

**Problem.** Three of the four compartments store `agent_amount_l` and derive
the fraction from it: `AlveolarCompartment`, `VenousBloodCompartment` and
`TissueGroup` all hold the amount and expose the fraction as a property.
`BreathingCircuit` is the other way round — it stores
`circuit_concentration_fraction` as a field and derives `agent_amount_l` at
`circuit.py:117`.

**Why it matters.** Mass is the conserved quantity in this model. § "Conservation
of sevoflurane" balances amounts, the release gate checks an amount residual,
and every internal transfer is applied as an equal-and-opposite pair of amounts.
A reader who has learned that three compartments hold mass and derive
concentration meets a fourth that does the reverse, and there is no physical
reason for the asymmetry — it is where the code came from, the v0.0.2 circuit
model having existed before there was a patient to conserve mass with.

**Why it is deliberately outside the `core/` domain-readability pass.** Changing
which of the pair is stored changes which one carries the rounding, so
floating-point results move. Planned-milestone item 29 takes a patch version
precisely because it changes no behavior, and `PL-9SH6`'s wide rename is
reviewable only because the property "no number moves" holds across the whole
diff. Folding a numerical change into it destroys that property for the sake of
a consistency win, which is a bad trade. Project owner agreed to the exclusion,
2026-09-03.

**Decision needed.** Whether it is worth doing at all, and if so under
what version. Three things to weigh:

- The change is small and the argument for it is real, but nothing is currently
  wrong: the circuit's numbers are correct and its guards hold.
- It would move displayed values in the last digit, so it interacts with
  `PL-88GQ` (state every displayed decimal count as a presentation decision) and
  with § "Displayed precision", whose bounds are derived from the shipped
  numerical behavior.
- It is the kind of thing that becomes much cheaper to do while `PL-9SH6` is
  already touching every one of these files, and much more expensive afterwards
  — which argues for deciding it before that item starts rather than after.

**Where.** `core/circuit.py` — `circuit_concentration_fraction` becomes a
derived property, `agent_amount_l` becomes the stored field, `BreathingCircuitState`
captures the amount, and `set_agent_amount` / `advance_fresh_gas` change which
one they write. § "Compartment capacities" in `docs/MODEL.md` states
$`M_C = V_C F_C`$ in the direction that would then match.

**Done when.** The decision is recorded either way. If taken: mass is the stored
primitive in all four compartments, the reference tests' tolerances are re-derived
rather than loosened, and § "Displayed precision" is re-checked against the new
numbers.

**Found.** Scoping session for planned-milestone item 29 (`core/` reads like the
domain), 2026-09-03, while measuring what the pass would touch.
