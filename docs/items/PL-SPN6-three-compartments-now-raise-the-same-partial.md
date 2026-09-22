---
id: PL-SPN6
title: Three compartments now raise the same 'partial_pressure_fraction must be between 0 and 1', so a refused step no longer says which one refused
priority: P2
effort: S
status: done
classes: defect, test
feature: core-guard-coverage
milestone: v0.5.4
touches: src/anesthesia_sim/core, tests/unit/test_uptake_system_failure.py
added: 2026-09-13
closed: 2026-09-22
pr: 889
verify: uv run pytest tests/unit/test_uptake_system_failure.py -q
---

**Problem.** Three compartments now raise the same 'partial_pressure_fraction must be between 0 and 1', so a refused step no longer says which one refused

Every compartment setter passes its own parameter name to
`require_concentration_fraction`, which raises `f"{name} must be between 0 and
1"`. After `PL-9SH6` gave three compartments the same accessor name, three of
them pass the same string:

| Compartment | Message before `PL-9SH6` | Message now |
| --- | --- | --- |
| `AlveolarCompartment` | `concentration_fraction must be…` | `partial_pressure_fraction must be…` |
| `VenousBloodCompartment` | `concentration_fraction must be…` | `partial_pressure_fraction must be…` |
| `TissueGroup` | `partial_pressure_fraction must be…` | `partial_pressure_fraction must be…` |

So a `SimulationConfigurationError` escaping a refused step no longer says
which compartment refused. The ambiguity is not new — alveolar and venous were
already indistinguishable from each other — but it went from two-way to
three-way, and it swallowed the one compartment that had been distinguishable.

**Why it matters beyond tidiness.** `AgentUptakeSystem._advance_step` wraps a
compartment guard's message into the `SimulationNumericalError` a caller sees,
and `tests/unit/test_uptake_system_failure.py` exists to keep that message
"diagnosable back to the invariant that broke". A message naming a guard that
three classes share is diagnosable back to three invariants.

It also silently loosened three assertions in that file, at lines 216, 220 and
471. They match `"partial_pressure_fraction must be between 0 and 1"` as a
substring against a run rigged so that the **fat tissue group** refuses. Before
`PL-9SH6` that string could only have come from a `TissueGroup`; now it would
also pass if a future change made the alveolar or venous compartment refuse
first, and the substring also matches `inspired_partial_pressure_fraction`'s
message. The tests still prove what their names claim — that the guard's text
survives the wrap and the rollback — but they no longer pin the compartment.

**The likely fix, and why it is a decision.** Pass a compartment-qualified name
(`"AlveolarCompartment.partial_pressure_fraction"`), so the message says where
it came from. That changes user-visible error text and three test assertions,
which is why it was not folded into `PL-9SH6` — a rename item whose defence is
that no behavior changed cannot also change what an error says. Weigh it
against giving `require_concentration_fraction` an optional owner argument, and
against leaving it: the wrapped `SimulationNumericalError` already names the
step, and a reader with a traceback has the frame.

**Where.** `core/alveolar.py`, `core/blood.py`, `core/tissue.py`,
`core/circuit.py`, `core/validation.py`, and
`tests/unit/test_uptake_system_failure.py`.

**Not blocked by anything.** The two items touch `core/validation.py` and
would collide there, so whichever runs second resolves against the first;
neither has to wait for the other, and this one is startable on its own.
**Done when.** A decision is recorded among the three the brief weighs - a
compartment-qualified name passed to the guard, an optional owner argument on
`require_concentration_fraction`, or leaving the message as it is because the
wrapped `SimulationNumericalError` already names the step - and whichever is
chosen, the three assertions at `tests/unit/test_uptake_system_failure.py` lines
216, 220 and 471 are made to pin the compartment that actually refused rather
than a string three classes now share. The test half is owed under every answer:
an assertion that would still pass if a different compartment refused first no
longer proves what its name claims, and that file exists to keep a refused step
diagnosable back to the invariant that broke.

**Decision needed.** Does the guard take a compartment-qualified name, an optional owner argument, or neither - leaving the message as it is because the wrapped `SimulationNumericalError` already names the step?

**Recommended, and taken: a compartment-qualified name built at the call
site.** The brief's first option, with one correction to it and one to the
count above.

*The collision is five-way, not three.* `AgentUptakeSystem._write_state_vector`
writes all three tissue groups through the same `TissueGroup.
set_partial_pressure_fraction`, so `vessel_rich`, `muscle` and `fat` share the
string with the alveolar compartment and the venous pool. A class-qualified
name - `TissueGroup.partial_pressure_fraction` - would have taken it from five
to three and stopped there. The instance's own `name` takes it to one.

*And the message is read on a banner, not in a traceback*, which is what
retires the third option. `app/dashboard_frame.py`'s `refused_setting_notice`
renders a `SimulationConfigurationError` verbatim into "Setting refused —
{error}", and `halt_disposition` puts the wrapped `SimulationNumericalError`
into the halted-run notice. The brief's "a reader with a traceback has the
frame" is true of a developer and false of the person the message was written
for. It is reachable outside the injected test failures, too:
`resume_at` writes all five from a state vector that
`require_canonical_state` checks for shape, finiteness and the unit constant
but not for range, so the compartment setters are the only thing enforcing
[0, 1] on a resume, and whichever is reached first is the one that refuses.

*Why not the optional owner argument.* `core/governing_equations.py` already
solved this problem for the twin class at the call site -
`TissueGroupEquationSettings.__post_init__` passes `f"{self.name} volume_l"`,
pinned by `tests/unit/test_governing_equations.py`'s `"^muscle volume_l must be
positive and finite$"` - so an `owner=` parameter would be a second mechanism
for a job `core/` has a convention for. It also puts the formatting decision
inside the guard, where the line that raises no longer shows the sentence a
reader will see. And it would edit `core/validation.py`'s signature and body,
which is the one file this item and `PL-T137` (each guard's message should
carry the rejected value) were expected to collide in; qualifying at the call
site leaves that function untouched, so the two items compose instead.

*Form.* `f"{self.name} partial_pressure_fraction"` on `TissueGroup`, and the
compartment's domain word where the class holds no instance name - `"alveolar
partial_pressure_fraction"`, `"venous partial_pressure_fraction"`. Lowercase
and space-separated rather than dotted, matching the existing convention and
`.claude/rules/core-domain.md`'s test: a reader who knows uptake recognizes
`fat partial_pressure_fraction` and has to translate
`TissueGroup.partial_pressure_fraction`.

*Scope held.* Only the three colliding `require_fraction` call sites changed.
The same ambiguity runs through the rest of `core/`'s guard surface -
`agent_amount_l`, `volume_l`, `blood_flow_l_min`, `simulation_step_s` and
`blood_gas_partition_coefficient` are each passed unqualified by several
classes, and every `TissueGroup` guard but this one is three-way ambiguous
across its instances - which is `PL-2TZT` rather than this item.
The convention is stated in `core/validation.py`'s module docstring so the
next caller has it.

*Tests.* The three assertions now pin `fat partial_pressure_fraction must be
between 0 and 1`, through one named constant so they cannot drift apart, and
`test_every_compartment_guarding_a_fraction_says_which_one_refused` asserts the
five messages are pairwise distinct and each prefixed by its owner - the check
that would have caught `PL-9SH6`'s collision, and the one that catches the next
one. Asserted as a prefix rather than as five literal sentences so it survives
`PL-T137` adding the rejected value to the same message. All four fail against
the pre-fix source and pass against this one.
