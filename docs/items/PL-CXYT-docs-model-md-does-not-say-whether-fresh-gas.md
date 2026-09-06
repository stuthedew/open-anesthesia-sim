---
id: PL-CXYT
title: docs/MODEL.md does not say whether fresh gas flow includes the vapor the vaporizer adds
priority: P1
effort: S
status: ready
classes: docs, science
feature: model-spec-accuracy
touches: docs/MODEL.md, src/anesthesia_sim/core/circuit.py
added: 2026-09-06
verify: python3 tools/doc_check.py check && grep -q 'common gas outlet' docs/MODEL.md
---

**Problem.** `docs/MODEL.md`'s symbol table defines `V̇_F` as "Fresh gas flow,
L gas/min" and says no more. On a real anesthesia machine that phrase has two
referents that differ by a known factor: the flowmeter setting, which is the
carrier gas alone, and the flow at the common gas outlet, which is the carrier
plus the vapour the vaporizer added. The model's own equations settle which one
it means — the circuit balance `dM_C/dt = V̇_F(F_D − F_I) − V̇_A(F_I − F_A)`
uses one `V̇_F` for both the agent arriving and the gas leaving, so mass
balance holds only if `V̇_F` is the total post-vaporizer flow — but the
document never says so, and the interface's fresh-gas-flow slider is the
control a user maps onto a flowmeter.

**Why it matters.** The gap is 1/(1 − F_D), which is negligible at ordinary
dial settings and is not negligible for desflurane: at the 18% Tec 6 maximum
this model already accepts, a flowmeter set to 2 L/min leaves the common gas
outlet at about 2.44 L/min, 22% higher. So the one agent whose dial reaches far
enough for the distinction to matter is the one this project ships, and a user
reading the slider as a flowmeter setting is off by that much in the circuit
time constant `V_C/V̇_F` — which is the quantity the wash-in curve is *for*.
Not a defect in the equations: they are self-consistent under the reading the
mass balance forces. It is one sentence of definition missing from a
safety-critical document, and `CLAUDE.md` requires a displayed value to be
traceable to the inputs and units that produced it.

Found while determining whether desflurane's Tec 6 vaporizer needs modelling
differently (`PL-5K5C`, record the model's sea-level assumption). It is not a
Tec 6 property — a variable-bypass vaporizer adds vapour to the carrier stream
in the same way — but its magnitude is set by the dial maximum, which is why
desflurane surfaces it.

**Where.** `docs/MODEL.md` § "Symbols" (the `V̇_F` row) and § "Governing
equations", where the circuit balance is stated. `core/circuit.py`'s
`fresh_gas_flow_l_min` and the interface's fresh-gas-flow control carry the same
ambiguity and should be checked for a docstring or label that needs the same
sentence.

**Done when.** `docs/MODEL.md` states that `V̇_F` is the total gas flow
delivered to the circuit including added agent vapour, not the flowmeter
setting; notes the 1/(1 − F_D) relationship between the two and that it reaches
about 22% at desflurane's 18% dial maximum; and any docstring or interface
label that could be read the other way is checked against that sentence.
