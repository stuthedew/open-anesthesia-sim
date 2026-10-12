---
id: PL-544D
title: AlveolarCompartment and TissueGroup admit a direct write of agent_amount_l past the compartment's capacity, so the quotient the display reads can leave 0 to 1 while every setter refuses it: PL-7DJK's case 1 is reproduced by that write, and test_a_halt_is_shown_when_the_snapshot_itself_is_refused depends on it staying open
priority: P1
effort: M
status: done
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/patient.py, src/anesthesia_sim/core/simulation.py, docs/MODEL.md, tests/unit/test_alveolar.py, tests/unit/test_tissue.py, tests/unit/test_uptake_system_failure.py, tests/integration/test_simulation_view.py, tests/integration/test_controller.py, docs/items/PL-19Y0-a-direct-write-to-a-checked-field-of.md
added: 2026-10-11
closed: 2026-10-12
pr: 1428
payoff: an impossible above-one-atmosphere fraction is refused where it is written, instead of living in the model until the display refuses it
verify: grep -q 'def test_an_agent_amount_past_capacity_is_refused_at_the_write' tests/unit/test_alveolar.py
---

**Problem.** AlveolarCompartment and TissueGroup admit a direct write of agent_amount_l past the compartment's capacity, so the quotient the display reads can leave 0 to 1 while every setter refuses it: PL-7DJK's case 1 is reproduced by that write, and test_a_halt_is_shown_when_the_snapshot_itself_is_refused depends on it staying open

**Problem.** `AlveolarCompartment.__setattr__` guards only
`alveolar_ventilation_l_min`, and `TissueGroup` guards no write of
`agent_amount_l`, so `alveoli.agent_amount_l = alveoli.gas_volume_l *
1.0000001` is accepted while `set_partial_pressure_fraction` refuses the same
quotient; the quotient the display reads is then outside 0 to 1 and
`SimulationController.snapshot()` refuses it, which `PL-7DJK` made a visible
halt. No supported setting takes the write - it is the reproduction's own
route, and `tests/integration/test_simulation_view.py`'s
`test_a_halt_is_shown_when_the_snapshot_itself_is_refused` and
`tests/integration/test_controller.py`'s
`test_a_snapshot_whose_quotient_is_refused_names_the_compartment_and_the_status_answers`
use it, so a guard here has to give those two tests another route to a
refusing snapshot in the same change (patching `snapshot` on the instance is
the obvious one).

**What a fix probably wants.** Either refuse the write as the ventilation
guard does, or admit the amount only through a setter; `PL-7DJK`'s recorded
answer says why the fraction itself cannot be the stored type without
changing what the propagator consumes.

**Reproduced 2026-10-11** on `main` at `16a20a4f`: `a = AlveolarCompartment();
a.agent_amount_l = a.gas_volume_l * 1.0000001` is accepted, and
`a.partial_pressure_fraction` then answers `1.0000001` - a partial pressure
above one atmosphere, stopped only by the snapshot's refusal two layers later.

**Why it matters.** A fraction above 1 is physically impossible, and the only
thing between it and the screen is `snapshot()`. `.claude/rules/core-domain.md`
asks for a quantity's own check to be made once, where it is built: here every
setter makes it and the field does not, so the one way in nobody guarded - a
direct write - is the one that reaches the display path. No supported setting
takes it today, which makes this a hole rather than a wrong number; it is the
shape `PL-LBQY` closed for the flows, and is classed the same way.

**Done when.** A write of `agent_amount_l` that puts the quotient outside 0 to 1
is refused at the write on both `AlveolarCompartment` and `TissueGroup`, with a
unit test for each; and the two integration tests that use the write today reach
a refusing snapshot by another route, still passing.

**Review, 2026-10-12** (three adversarial passes over `#1428`'s simulator
diff; the core-invariants pass found two things, both fixed here). The
rollback: `restore_state` on both compartments wrote the amount through the
new guard, so a capacity written under a held amount - `PL-19Y0`'s hole, which
no setting reaches - had the step refused at fat, the rollback refused at fat
too, and the venous pool, restored after fat, left holding the failed step
under a `SimulationConfigurationError` that had replaced the
`SimulationNumericalError`: the partial state `AgentUptakeSystem.restore_state`
says cannot happen. Both now write the slot with `object.__setattr__`, with a
test per compartment and one on the system
(`tests/unit/test_uptake_system_failure.py`), each red without the fix. The
message: the guard read the volume before `__post_init__` had required it, so
`AlveolarCompartment(gas_volume_l="2.5")` was refused in the comparison's own
words, naming neither the field nor its constraint, the shape `PL-3800` had
removed; `require_a_number` on the capacity's factors inside the guard gives
`__post_init__`'s message byte for byte, with a test per compartment. The
pass checked and found sound: field order on both classes, `replace`, copy,
deepcopy and pickle writing through the guard, every refusal message otherwise
byte-identical to `main` (a blank name beside an over-capacity amount now
refuses the amount first), an amount exactly at capacity accepted by field,
setter and `advance`, 100% branch coverage of both modules, and some 400,000
replica pairs and 60,000 real advances across capacities from 2^-16 to 2^16
finding no amount carried past capacity by rounding. What it found and this
item does not fix is on `PL-19Y0`.
