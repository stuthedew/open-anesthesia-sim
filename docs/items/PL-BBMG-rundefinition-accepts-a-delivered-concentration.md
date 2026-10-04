---
id: PL-BBMG
title: RunDefinition accepts a delivered concentration above the agent's vaporizer maximum - 20% sevoflurane against an 8% maximum ran on 2026-10-04 - because UptakeEquationSettings carries no agent and no vaporizer maximum, so a run built from a settings record bounds the dial only at 100%, and the BreathingCircuit that refuses it is never built
priority: P1
effort: M
status: needs-decision
classes: defect, safety
feature: parse-dont-validate
touches: src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/core/uptake_system.py, tests/unit/test_governing_equations.py, tests/unit/test_run_definition.py, docs/MODEL.md
added: 2026-10-04
payoff: a run built from a settings record refuses a dial above the vaporizer maximum exactly as the circuit does, so no caller gets a trace for a setting the machine cannot deliver
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

**Why it matters.** A dial above the vaporizer maximum is a setting the machine
cannot deliver, and a run built from it gave a precise-looking trace, an
alveolar fraction of 0.033306 at 60 s, where `CLAUDE.md`'s safety-critical
standard asks for an obvious refusal. It is `PL-HSFV`'s gap for the one setting
that gap's fix cannot reach.

**Decision needed.** What does a run definition record, so that the dial's
bound travels with it: the maximum, the agent the maximum is read from, or
neither, with a check wherever a run is built from stored settings?

**Recommendation: the maximum.** `UptakeEquationSettings` carries the maximum
its dial is bounded by, required and with no default, and refuses a dial above
it in `__post_init__`.

- **It is the shape `BreathingCircuit` already has.** That record holds the
  dial and `max_delivered_concentration_percent` side by side and refuses the
  one above the other.
- **The bound is a relation between two values, so it belongs to the record
  that holds both.** That is where `PL-M7QH`'s section of
  `.claude/rules/core-domain.md` (pull request 1346) stops the
  checked-type pattern, and the record that refuses it is then a parsed type
  for its dial.
- **No default.** `BreathingCircuit` defaults its maximum to 100%. A record
  field defaulting the same way would be today's gap with a field added.
- **The two alternatives are weaker.** A record carrying the agent's name
  cannot check itself without loading that agent's data. A check wherever a run
  is built from stored settings is the hand-checked pattern this feature
  removes.
- **Where the number comes from does not change this answer.** It is the
  agent's today, and the vaporizer's if `PL-JQY1` (a vaporizer's maximum stored
  as an agent property) moves it. The record holds the number either way.

**Done when.** The decision is recorded beneath the question; a run definition
refuses a dial above its maximum at `RunDefinition(...)` and at
`record_change`, with regression tests replaying the 20% sevoflurane
reproduction at both and pinning the maximum and the first value past it; and
`docs/MODEL.md` § "Supported input ranges" says where the dial's bound is
enforced.

**Gate.** On v0.6.0's frozen list, in the product lane, with the rest of the
`parse-dont-validate` feature (project owner, 2026-10-04). Classed `safety`, it
would have joined under the exception on its own.
