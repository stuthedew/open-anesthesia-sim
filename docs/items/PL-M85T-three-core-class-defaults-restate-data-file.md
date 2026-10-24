---
id: PL-M85T
title: Three core class defaults restate data-file values (alveolar gas volume 2.5 L and ventilation 4.0 L/min in alveolar.py, circuit volume 6.0 L in circuit.py), and a fourth, the 100% maximum delivered concentration, matches no agent's vaporizer: decide whether they become required arguments
priority: P1
effort: M
status: needs-decision
classes: safety, defect
feature: one-source-of-truth
touches: src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/circuit.py, tools/literal_home_check.py, tests/unit/test_circuit.py, tests/unit/test_alveolar.py
added: 2026-10-19
payoff: no core compartment can be built with a clinical parameter nobody stated, including a circuit with no vaporizer limit
---

**Problem.** Three class defaults in `core/` repeat values that the data files own. `AlveolarCompartment` defaults `gas_volume_l` to 2.5 L and `alveolar_ventilation_l_min` to 4.0 L/min, which `data/patients/reference_adult.json` stores as `alveolar_gas_volume_l` and `default_alveolar_ventilation_l_min`. `BreathingCircuit` defaults `circuit_volume_l` to 6.0 L, which `data/machines/reference_circle_system.json` stores. No check ties a default to its data value. Tests pin each side to the same literal separately, so changing the data file leaves the default behind without failing anything.

The fourth default is a different case. `BreathingCircuit.max_delivered_concentration_percent` defaults to 100%, and no agent file holds that value: the agent files hold 5% (isoflurane), 8% (sevoflurane) and 18% (desflurane). So this default does not restate a data value. It is a permissive placeholder: a circuit built without the argument accepts any dial setting up to 100%. The production path builds the circuit from the agent's data, so no shipped run uses the placeholder today. The decision is whether a placeholder like this should exist at all, under the safety-critical rule against silently substituting defaults.

Corrected at review on 2026-10-24. The worker's capture called all four "data-file values held equal only by tests", which is false for the 100% maximum.

**Why it matters.** A default that restates a data file is a second copy of a clinical parameter. Change the data file and the default stays behind, and no test fails. The 100% default is worse. A circuit built without the argument has no vaporizer limit, so it accepts a dial setting no vaporizer can deliver. `CLAUDE.md`'s safety-critical standard says not to silently substitute defaults where doing so could produce a plausible but incorrect clinical value. No shipped run reaches these defaults today, so the harm is latent: it reaches a future caller, or a test that relies on a default and so does not test the shipped values.

**Decision needed.** Should the four defaults become required arguments, or stay and be tied to their data files by a check?

**Recommendation:** make all four required, with no default. A check could keep the three restated values equal to the data, but it cannot fix the 100% placeholder, which restates nothing. A required argument fixes all four the same way, and makes every caller state the clinical value it means. The cost is updating the call sites that rely on the defaults: about 32 `BreathingCircuit(` and 13 `AlveolarCompartment(` constructions in `tests/unit/test_circuit.py` and `tests/unit/test_alveolar.py` alone, counted 2026-10-24. This applies a rule `CLAUDE.md` already states, so the session that starts the item can take it. It goes to the owner only if the work finds a caller that genuinely needs a default.

**Done when** (under the recommendation). `AlveolarCompartment` and `BreathingCircuit` have no default for any of the four fields. Every caller passes them, and `BASELINE` in `tools/literal_home_check.py` has no `core/alveolar.py` or `core/circuit.py` entry. A test shows that building either class without one of them is refused.

**Checked 2026-10-24.** `alveolar.py` defaults `gas_volume_l: float = 2.5` and `alveolar_ventilation_l_min = AlveolarVentilation(4.0)`. `circuit.py` defaults `circuit_volume_l: float = 6.0` and `max_delivered_concentration_percent = Percent(100.0)`.

**Generator check.** Bookkeeping. It touches `tools/literal_home_check.py` only to remove the four `core/` entries its `BASELINE` recorded when `PL-40SJ`'s check landed. The defaults themselves are the second copies `PL-H8QP` described, not new inflow.
