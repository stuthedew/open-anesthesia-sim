---
id: PL-006
title: Clarify what `RespiratorySystem` actually owns
priority: P2
effort: M
status: ready
classes: refactor
feature: core-boundaries
touches: src/anesthesia_sim/core/respiratory_system.py, src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/app/controller.py, docs/ARCHITECTURE.md, docs/MODEL.md, docs/WORKING_NOTES.md, tests/integration/test_controller.py, tests/unit/test_simulation.py, tests/unit/test_respiratory_system_failure.py
added: 2026-08-23
---

**Problem.** `core/respiratory_system.py` bundles concerns beyond what its
name suggests. "Respiratory system" clinically means the patient's own lungs
and airways, which maps only to `alveoli`. `circuit` is the anesthesia
machine's breathing circuit — equipment, not patient physiology — and the
class also owns `PatientCompartments`, which holds the vessel-rich, muscle,
and fat tissue compartments.

**Why it matters.** The class is the entry point to the scientific core, so a
misleading name and boundary is what a cold reader hits first. It is also a
safety concern rather than a tidiness one: `total_stored_agent_l` sums circuit
plus alveoli plus all three tissue compartments and feeds the conservation
check that can halt a run. A reader who takes "respiratory system" at face
value reads that quantity as agent in the lungs. At steady state most of the
agent is in fat and muscle, so the misreading is wrong by a large factor, on
an accounting quantity.

**Where.** `core/respiratory_system.py` and its call sites; the four
documentation files that name the class.

**Decided.** Rename the class, keep the setter facade, and move the
circuit-volume conservation logic into core. Three parts:

1. `RespiratorySystem` becomes `AgentUptakeSystem` in `core/uptake_system.py`;
   `RespiratoryStepResult` becomes `UptakeStepResult`;
   `SimulationState.respiratory_system` becomes `.uptake_system`. "Uptake" is
   the canonical term in inhaled-anesthetic pharmacology for agent moving from
   circuit through alveoli into tissues, and "agent" is already this
   codebase's word for the volatile.
2. The four forwarding setters stay, with a class docstring stating what
   defines the set: the live user-controllable inputs. Fresh gas flow and
   delivered concentration are machine controls, alveolar ventilation and
   cardiac output are patient state, and the four are exactly the sliders the
   interface exposes. Under an accurate name they are the system's control
   surface rather than leakage.
3. `SimulationController.set_circuit_volume` currently reads stored agent,
   rejects a volume too small to hold it, and restores the amount after the
   change — mass-conservation logic in the app layer, raising the core
   `SimulationConfigurationError` from outside core. It moves to core as a
   method that changes volume while preserving stored agent, and the
   controller calls it.

4. `SimulationState` exposes `circuit`, `alveoli` and `patient` as properties
   forwarding to the system it owns, so each of those objects has two reachable
   paths. That is a second facade stacked on the one part 2 keeps, and it is
   the redundant one: the setters hide composition behind an intention-revealing
   verb, while these merely re-export attributes under shorter names. Drop them
   and let callers reach `uptake_system.circuit`.

The item originally offered dropping the setters *or* renaming, as
alternatives. Dropping them cannot satisfy this item's own closing condition:
the name is wrong independently of the setters, because the class still owns
the patient's fat compartment either way. And the real boundary defect runs
the other direction — simulation logic has leaked out into the controller,
which is part 3.

**Done when.** The naming and the delegation boundary agree with each other,
the circuit-volume conservation lives in core, call sites and the four
documentation files are updated, and the reference tests pass unchanged in
behavior.
