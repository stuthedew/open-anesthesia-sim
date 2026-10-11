---
id: PL-544D
title: AlveolarCompartment and TissueGroup admit a direct write of agent_amount_l past the compartment's capacity, so the quotient the display reads can leave 0 to 1 while every setter refuses it: PL-7DJK's case 1 is reproduced by that write, and test_a_halt_is_shown_when_the_snapshot_itself_is_refused depends on it staying open
status: untriaged
added: 2026-10-11
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
