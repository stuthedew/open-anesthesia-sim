---
id: PL-B667
title: MODEL.md's required invariants say derived fractions stay finite and nonnegative, but core/ enforces the upper bound of 1 in five places and the list never states it
status: untriaged
added: 2026-09-13
---

**Problem.** MODEL.md's required invariants say derived fractions stay finite and nonnegative, but core/ enforces the upper bound of 1 in five places and the list never states it

`docs/MODEL.md` § "Required invariants" is the authoritative list of what the
implementation must preserve. Its line on concentrations reads:

> derived concentration fractions remain finite and nonnegative;

That is the lower bound and nothing else. The code enforces both bounds, in
five places:

| Where | Form |
| --- | --- |
| `core/validation.py` `require_concentration_fraction` | `not 0.0 <= value <= 1.0` raises |
| `AlveolarCompartment.__post_init__` | `agent_amount_l > gas_volume_l` raises |
| `VenousBloodCompartment.__post_init__` | `agent_amount_l > capacity_l` raises |
| `TissueGroup.__post_init__` | `agent_amount_l > capacity_l` raises |
| `BreathingCircuit.set_agent_amount` / `set_circuit_volume` | `> circuit_volume_l` raises |

The first is the load-bearing one. `AgentUptakeSystem._write_state` writes every
solved step back through the validated setters, so the upper bound is checked on
**every step's output**, and its docstring already states the reason in exactly
the terms this list should use: "an exact solution of the equations cannot leave
the physical range, so a value that does is evidence the run is no longer
trustworthy rather than a number to display."

**Why the omission matters rather than being a wording nit.** § "Concentrations"
does say fractions run "from 0 through 1", but that is a statement about
*representation* — what the number means — where this list is the statement of
what the implementation *must preserve*. A reader checking the code against the
spec finds a guard the spec does not ask for, which is the shape of a guard
somebody deletes as over-engineering. It is also the direction of divergence
that matters: the spec currently under-promises what the code guarantees, so
nothing in `make check` can catch the day the guarantee is dropped.

`PL-FZ6T` is about to build checks that hold `core/` to `docs/MODEL.md`, which
is the reason to settle this now rather than later.

**Proposed fix, and it is one line.** Change the invariant to name both bounds —
"derived partial-pressure-equivalent fractions remain finite and within 0 through
1" — and, if a second line is wanted, state that a step producing a value outside
it is refused and rolled back rather than displayed, which the "a simulation step
that cannot be completed" invariant below already half-says.

**What was checked and found adequate, so this item is not about it.** The
runtime enforcement itself needs nothing added. The three per-compartment closed
forms (`TissueGroup.advance`, `VenousBloodCompartment.advance`,
`BreathingCircuit.advance_fresh_gas`) write `agent_amount_l` directly rather than
through the guarded setter, but each computes a convex combination of two
in-range values, so the result is in range by construction. And the bound is not
close: the highest fraction any supported run reaches is the vaporizer dial
maximum, 0.18 for desflurane, so operating states sit about 5x below it. A test
sweeping the supported domain for a bound violation would be a check that cannot
fail, which `CLAUDE.md` says to retire rather than build.

**Where.** `docs/MODEL.md` § "Required invariants", one line.
