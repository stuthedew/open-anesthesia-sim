---
id: PL-D42Z
title: docs/machine-abstraction.md's (b11) row calls delivery unchanged under a shut surplus gas valve, where the fresh gas flow stops being a free input and becomes an output
priority: P2
effort: S
status: ready
classes: docs
feature: circuit-boundary-docs
touches: docs/machine-abstraction.md
added: 2026-09-20
payoff: an implementer pairing a closed_circuit removal with fresh_gas_bypass is told the flow becomes an output, instead of reading a table row that calls delivery unchanged
verify: grep -qE '^\| \(b11\).*uptake' docs/machine-abstraction.md
---

**Problem.** docs/machine-abstraction.md's (b11) row calls delivery unchanged under a shut surplus gas valve, where the fresh gas flow stops being a free input and becomes an output

 — found while closing `PL-WJNS`, which argued the same boundary in
`docs/MODEL.md`.

`docs/machine-abstraction.md` § "The finding the whole design rests on" tabulates
what each surveyed machine behavior does to the two rates a machine supplies:

| Survey entry | Delivery | Removal |
| --- | --- | --- |
| (b11) surplus gas valve closed | unchanged | zero |

The removal half is right. The delivery half is right about the *form* — the
rate is still $`\dot m_{\mathrm{in}}`$ — and it is what a later implementer
will read, and it hides the coupling: with the valve shut, a closed circuit's
fresh gas flow **is** the patient's total uptake, so $`\dot V_F`$ stops being a
free control and becomes an output. `fresh_gas_bypass` fills
$`\dot m_{\mathrm{in}}`$ with $`\dot V_FF_D`$, so pairing it with a
`closed_circuit` removal leaves the vaporizer adding agent at whatever flow the
user dialled.

**Why it matters.** `docs/MODEL.md` § "Breathing circuit" now carries the
arithmetic: at the shipped 4.0 L/min that is about thirteen times the
0.3 L/min this patient's uptake would set, for the same dial. The trajectory is
plausible and the number is wrong, which is the failure mode the survey
predicted for this entry and the reason it called (b11) the one that reaches an
equation rather than a coefficient.

**Where.** `docs/machine-abstraction.md` § "The finding the whole design rests
on", the four-row behavior table; § "The closed set of behaviors", the
`closed_circuit` removal row, listed there as not implemented.

**Done when.** The table's (b11) row says what a shut valve does to the flow
that feeds delivery, rather than only to the removal rate, and the
`closed_circuit` row names the second thing an implementation of it owes.
