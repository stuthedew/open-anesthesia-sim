---
id: PL-BBMG
title: RunDefinition accepts a delivered concentration above the agent's vaporizer maximum - 20% sevoflurane against an 8% maximum ran on 2026-10-04 - because UptakeEquationSettings carries no agent and no vaporizer maximum, so a run built from a settings record bounds the dial only at 100%, and the BreathingCircuit that refuses it is never built
status: untriaged
feature: numerical-domain
added: 2026-10-04
---

**Problem.** RunDefinition accepts a delivered concentration above the agent's vaporizer maximum - 20% sevoflurane against an 8% maximum ran on 2026-10-04 - because UptakeEquationSettings carries no agent and no vaporizer maximum, so a run built from a settings record bounds the dial only at 100%, and the BreathingCircuit that refuses it is never built

**Measured 2026-10-04** on `main` at `45f8e9f3`, while working `PL-HSFV` (the
settings record refusing flows outside the supported ranges), under Python
3.14.7. `AgentUptakeSystem.for_agent("sevoflurane")` refuses
`set_delivered_concentration_percent(20.0)` with "delivered_concentration_percent
exceeds the vaporizer maximum (20% requested, 8% maximum)", but
`RunDefinition(dataclasses.replace(system.equation_settings(),
delivered_concentration_percent=20.0), system.state_vector(), opened_at_s=0.0)`
opens, and after `advance_to(60.0)` its `state_at(60.0)` returned an alveolar
fraction of 0.033306.

**Why `PL-HSFV` does not close it.** The three flows' bounds are the model's own
constants in `core/supported_ranges.py`, so the settings record can call the
guards a compartment calls. The dial's bound is the agent's
`max_delivered_concentration_percent`, which `docs/MODEL.md` § "Supported input
ranges" lists as declared and refused by `BreathingCircuit`, and the settings
record holds no agent and no maximum - only `require_percent`'s 0 to 100. So
closing it is a decision about what a run definition records - the agent, the
maximum, or a check wherever a run is built from stored settings - rather than
a guard to add.

**Exposure.** As for `PL-HSFV`: nothing in the application reaches it, because
`app/controller.py` builds every run definition from compartments that refuse
such a dial. A direct caller does, and so would the first path that builds a
run from a stored record, such as a saved run restored by a deserializer.
