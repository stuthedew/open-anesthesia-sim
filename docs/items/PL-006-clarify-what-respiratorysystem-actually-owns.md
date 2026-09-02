---
id: PL-006
title: Clarify what `AgentUptakeSystem` actually owns
priority: P2
effort: M
status: done
classes: refactor
feature: core-boundaries
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/exceptions.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/validation.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, docs/ARCHITECTURE.md, docs/MODEL.md, docs/WORKING_NOTES.md, tests/integration/test_controller.py, tests/unit/test_simulation.py, tests/unit/test_uptake_system_failure.py, tests/unit/test_circuit.py, tests/unit/test_parameters.py, tests/unit/test_simulation_view.py, tests/unit/test_supported_ranges.py, tests/reference/test_coupled_dynamics.py, tests/reference/test_multi_agent.py, tests/reference/test_published_wash_in.py, tests/reference/test_sevo_patient.py
added: 2026-08-23
closed: 2026-09-02
pr: 203
verify: uv run pytest tests/unit/test_circuit.py -k conserves_stored_agent && grep -q 'class AgentUptakeSystem' src/anesthesia_sim/core/uptake_system.py
---

**Problem.** `core/uptake_system.py` bundles concerns beyond what its
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

**Where.** `core/uptake_system.py` and its call sites; the four
documentation files that name the class.

**Decided.** Rename the class, keep the setter facade, and move the
circuit-volume conservation logic into core. Three parts:

1. `AgentUptakeSystem` becomes `AgentUptakeSystem` in `core/uptake_system.py`;
   `UptakeStepResult` becomes `UptakeStepResult`;
   `SimulationState.uptake_system` becomes `.uptake_system`. "Uptake" is
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

**Measured — what part 3's setter does today.** An outside review of the
repository reproduced this against the running code, recorded here as evidence
for part 3 rather than filed as a separate item. A sevoflurane system stepped
60 s holds 0.048288200 L of agent in the circuit. Calling
`BreathingCircuit.set_circuit_volume(3.0)` drops that to 0.024144100 L —
24.1 mL of equivalent agent gas destroyed by a setter — and the next
`advance(0.1)` raises `AgentSimulationValidationError`, blaming the numerics for
a setter's defect.

That violates two of `docs/MODEL.md`'s required invariants directly: `:735`
("no compartment creates agent spontaneously") and `:738` ("changing a setting
does not reset stored state"). Every sibling setter that conserves says so in
its docstring; this one documents nothing, so the non-conservation is invisible
at the call site.

`app/controller.py:280-290` compensates, so the shipped application is safe —
and that is itself the point part 3 makes. Mass-conservation logic lives in the
app layer while `core/` exposes the unconserving primitive publicly, so the
invariant holds only for callers who know to go the long way round. Moving the
conservation into `set_circuit_volume` is what makes the public primitive the
safe one.

**Done when.** The naming and the delegation boundary agree with each other,
the circuit-volume conservation lives in core, call sites and the four
documentation files are updated, and the reference tests pass unchanged in
behavior.

**Worked.** All four parts, as decided.

**1 — the rename.** `core/respiratory_system.py` is `core/uptake_system.py`,
`RespiratorySystem` is `AgentUptakeSystem`, `RespiratoryStepResult` is
`UptakeStepResult`, `SimulationState.respiratory_system` is `.uptake_system`.
The module docstring now carries the reason rather than the old pointer to a
"near-term to-dos" thread that `docs/WORKING_NOTES.md` no longer has — a
dangling citation `tools/doc_check.py` cannot currently see, because it reads
neither source docstrings nor section names (`PL-X2XX`).

**2 — the setter facade, kept and defined.** The class docstring states what
makes the four a set: they are the live user-controllable inputs, machine
controls and patient state alike, and exactly the sliders the interface
exposes. It also says what does *not* belong there and why, using circuit
volume as the worked example, so the set has a stated boundary rather than
being whatever accumulated.

**3 — conservation moved into `core/`.** `BreathingCircuit.set_circuit_volume`
now preserves `agent_amount_l` across a volume change and refuses a volume too
small to hold what is already there, checking before it mutates so a refused
volume leaves the circuit untouched. `SimulationController.set_circuit_volume`
is three lines of forwarding, and the controller no longer imports
`SimulationConfigurationError` at all — it had been raising a core exception
from outside core, which was the boundary defect stated the other way round.

The measurement in this brief reproduced exactly against the shipped code:
0.048288200 L in the circuit after 60 s, halved by the setter. Three unit
tests in `tests/unit/test_circuit.py` cover the primitive (conservation both
directions, refusal without mutation, the closed bound at exactly equal), and
`test_changing_circuit_volume_mid_run_does_not_break_the_next_step` in
`tests/unit/test_uptake_system_failure.py` is the end-to-end regression, sited
with the other failure tests because the visible symptom was a *later* step
raising `AgentSimulationValidationError` for a setter's defect. All four were
confirmed to fail against the old setter before being kept, along with the two
existing controller tests, which now prove the core path instead of the
controller's compensation — no assertion in them changed, including the exact
error message, which the core guard reuses deliberately.

**4 — the second facade dropped.** `SimulationState.circuit`, `.alveoli` and
`.patient` are gone; callers reach `uptake_system.circuit`. That removed three
imports from `core/simulation.py` as well.

**Scope note.** The rename reached 23 files rather than the 10 this brief's
`touches` predicted; `touches` is updated to what it actually was. Ten open
queue items named `RespiratorySystem` or the old module path, including
`PL-026`'s own `touches` line — those are repointed, because a `touches`
naming a deleted file makes `bin/docket concurrent` wrong. Closed items keep
their prose as the record of the code as it was; the one whose `verify:`
command named the moved test file (`PL-0MLQ`) had that line repointed, since a
command is not a record.

`ROADMAP.md`'s three mentions are left alone deliberately: two sit in
completed-milestone and released-baseline prose describing the code as it then
was, and the third is this item's own title inside the frozen debt gate.

**Doc sweep.** `docs/ARCHITECTURE.md` (package map, flow diagram, step
sequence, and the UI-direction paragraph, which gained a sentence stating that
conservation is core's on the same terms as bounds), `docs/MODEL.md` (nine
mentions, all mechanical; `:1315`'s note that `SimulationController` still
exposes `set_circuit_volume` outside the verified domain stays true and still
belongs to `PL-GYH2`), `docs/WORKING_NOTES.md` (one mention, in an open
thread about rollback capture).
