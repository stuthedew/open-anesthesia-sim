---
id: PL-544D
title: AlveolarCompartment and TissueGroup admit a direct write of agent_amount_l past the compartment's capacity, so the quotient the display reads can leave 0 to 1 while every setter refuses it: PL-7DJK's case 1 is reproduced by that write, and test_a_halt_is_shown_when_the_snapshot_itself_is_refused depends on it staying open
priority: P1
effort: M
status: ready
classes: safety, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/tissue.py, tests/unit/test_alveolar.py, tests/unit/test_tissue.py, tests/integration/test_simulation_view.py, tests/integration/test_controller.py
added: 2026-10-11
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
