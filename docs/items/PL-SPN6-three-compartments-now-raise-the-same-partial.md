---
id: PL-SPN6
title: Three compartments now raise the same 'partial_pressure_fraction must be between 0 and 1', so a refused step no longer says which one refused
status: untriaged
added: 2026-09-13
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
