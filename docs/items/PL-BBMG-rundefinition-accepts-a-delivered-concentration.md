---
id: PL-BBMG
title: RunDefinition accepts a delivered concentration above the agent's vaporizer maximum - 20% sevoflurane against an 8% maximum ran on 2026-10-04 - because UptakeEquationSettings carries no agent and no vaporizer maximum, so a run built from a settings record bounds the dial only at 100%, and the BreathingCircuit that refuses it is never built
priority: P1
effort: M
status: ready
classes: defect, safety
feature: parse-dont-validate
touches: src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/validation.py, tests/unit/test_governing_equations.py, tests/unit/test_run_definition.py, docs/MODEL.md
added: 2026-10-04
payoff: a run built from a settings record refuses a dial above the vaporizer maximum exactly as the circuit does, so no caller gets a trace for a setting the machine cannot deliver
verify: grep -q "max_delivered_concentration_percent" src/anesthesia_sim/core/governing_equations.py && grep -q "test_rejects_a_dial_above_the_vaporizer_maximum" tests/unit/test_governing_equations.py && grep -q "test_a_run_cannot_open_or_change_under_a_dial_above_the_vaporizer_maximum" tests/unit/test_run_definition.py
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

**Answered 2026-10-04: the maximum.** (project owner, 2026-10-04, ratified,
over the agent's name and over a check wherever a run is built; "Agree with
recs" in the project chat at 17:53 UTC, answering the design round's summary
of § "Design round 2026-10-04" below). `UptakeEquationSettings` carries
`max_delivered_concentration_percent`, required, and refuses a dial above it
through the guard `BreathingCircuit` uses; the vaporizer pair record the round
weighs waits for the saved-run format.

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

**Done when.** `UptakeEquationSettings` carries
`max_delivered_concentration_percent`, required, and refuses a dial above it
through the guard `BreathingCircuit` uses, so neither `RunDefinition(...)` nor
`record_change` can be handed such a record; regression tests replay the 20%
sevoflurane reproduction at both entry points and pin the maximum and the first
value past it; and `docs/MODEL.md` § "Supported input ranges" names both records
as where the dial's bound is enforced.

**Gate.** On v0.6.0's frozen list, in the product lane, with the rest of the
`parse-dont-validate` feature (project owner, 2026-10-04). Classed `safety`, it
would have joined under the exception on its own.

## Design round 2026-10-04

Run by the Ship v0.6.0 project's design thread, on `main` at `63bc149a` under
Python 3.14.7, with no code changed.

**Re-measured 2026-10-04 on that tree.** The reproduction above still holds at
both of `RunDefinition`'s entry points: the circuit refuses the 20% dial with
"delivered_concentration_percent exceeds the vaporizer maximum (20% requested,
8% maximum)", a run opened under the replaced settings gives an alveolar
fraction of 0.033306 at 60 s, and a run that records the change at 30 s gives
0.015975 at 60 s. The first percent past sevoflurane's maximum is
`8.000000000000002`.

**Recommendation (design round, 2026-10-04): the maximum, as recommended
above, with two refinements.**

1. **One guard, shared with the circuit.** `BreathingCircuit._require_deliverable`
   and the record's `__post_init__` call the same module-level function - in
   `core/circuit.py`, since the circuit owns the delivery limit, or
   `core/validation.py`; the builder's call - so both refuse in the one sentence
   quoted above and the relation is written once. That is the shape
   `.claude/rules/core-domain.md` § "A quantity with a check of its own is a
   type, checked once" admits for a guard shared by the records that hold the
   field, and it is the duplication the alternative below would otherwise be
   the only way to remove.
2. **The field is `max_delivered_concentration_percent: Percent`, required,
   beside the dial.** `AgentUptakeSystem.equation_settings()` passes
   `self.circuit.max_delivered_concentration_percent`; `_propagator_cache_key`
   gains the matching entry, so
   `test_the_propagator_cache_key_covers_every_equation_setting` holds and the
   key stays a bijection of the settings. The matrix never reads it, so the
   entry costs one matrix exponential per run at most, when a run's maximum
   differs from the last run's.

**Weighed and not taken: the dial and its maximum as one frozen record.** A
vaporizer setting holding both, refusing the one above the other in its own
`__post_init__`, held by `BreathingCircuit` and by `UptakeEquationSettings`
alike, with `equation_settings()` passing it through unchecked because holding
one is the proof. It is the purer parse-don't-validate shape, and the one to
take if a third holder of the pair appears. Refused now on
`.claude/rules/expert-review.md` § "Count what undoing it would cost, before
taking the cheaper route": downstream of the choice today are one builder in
`src/` and one in `tests/`, nothing stored depends on the record's shape, and
what the record form removes is, with the shared guard, two calls of one
function - at the cost of folding two of `BreathingCircuit`'s fields into one,
about ten construction sites in `src/` and the tests, and properties kept for
the thirty readers of the two names in `app/`. The saved-run format
(`ROADMAP.md`, planned item 9) is where the record's shape becomes a one-way
door, and this record's `__post_init__` checks a deserialized segment either
way; weigh the pair record again there.

**Rejected as above.** The agent's name, which cannot check itself without
loading the agent's data; and a check wherever a run is built, which is the
shotgun parsing this feature removes.

**What the build carries**, for the thread that takes it:

- `RunDefinition(...)` and `record_change` gain no code: a record whose dial
  is above its maximum cannot be built, so neither can be handed one. The
  reproduction's `dataclasses.replace(..., delivered_concentration_percent=20.0)`
  raises at the `replace`.
- Regression tests: in `tests/unit/test_governing_equations.py`, the record
  refuses a dial above its maximum, accepts the maximum itself (8.0) and zero,
  the vaporizer off, and refuses the first value past it,
  `math.nextafter(8.0, math.inf)`; in `tests/unit/test_run_definition.py`,
  the 20% sevoflurane reproduction replayed at both entry points, by replacing
  the dial on the settings a run opens from and on the settings a change is
  recorded with, each refused before the run is touched. Proposed names, which
  the `verify:` below greps for: `test_rejects_a_dial_above_the_vaporizer_maximum`
  and `test_a_run_cannot_open_or_change_under_a_dial_above_the_vaporizer_maximum`.
- `UptakeEquationSettings`' docstring, "Everything the governing equations need
  that a step does not change", widens by one clause: the record is also what
  a run holds per stretch (`core/run_definition.py`), and a stretch that
  cannot say its dial was deliverable is incomplete, so it carries the one
  field the matrix does not read and refuses a dial above it.
- `docs/MODEL.md` § "Supported input ranges": the table's delivered-concentration
  row names `BreathingCircuit` and `UptakeEquationSettings` as where the bound
  is declared and refused, and the paragraph "Enforced on the compartment, not
  on the coupled system", which `PL-0YYV` already revises for the flows, says
  the settings record is a second point every setting passes through.
- Where the number comes from does not move: the agent file today (`PL-JQY1`),
  the record carrying the number whatever file it is read from.
- With `PL-4R3W` ratified, `require_percent` leaves the record's
  `__post_init__` and the relation alone remains. Build this item first, being
  `P1` and `safety`-classed, then `PL-4R3W`; both after `PL-0YYV` (slice 1),
  with which this shares `core/governing_equations.py`,
  `core/run_definition.py`, `core/uptake_system.py` and `docs/MODEL.md`. It
  changes nothing in slice 1, which types the three flow fields of the same
  record; the two meet at a merge and nowhere else.
- Size stays M.
- Done-when, in the decided form, to replace the one above at the answer:
  `UptakeEquationSettings` carries `max_delivered_concentration_percent`,
  required, and refuses a dial above it through the guard `BreathingCircuit`
  uses, so neither `RunDefinition(...)` nor `record_change` can be handed such a
  record; regression tests replay the 20% sevoflurane reproduction at both
  entry points and pin the maximum and the first value past it; and
  `docs/MODEL.md` § "Supported input ranges" names both records as where the
  dial's bound is enforced.
- `verify:`, to set at the answer:
  `grep -q "max_delivered_concentration_percent" src/anesthesia_sim/core/governing_equations.py && grep -q "test_rejects_a_dial_above_the_vaporizer_maximum" tests/unit/test_governing_equations.py && grep -q "test_a_run_cannot_open_or_change_under_a_dial_above_the_vaporizer_maximum" tests/unit/test_run_definition.py`.
