---
id: PL-79YX
title: Six exact float-equality branch guards in core/ are correct and nowhere explained
status: needs-decision
priority: P3
effort: S
classes: docs
touches: src/anesthesia_sim/core
added: 2026-09-02
---

**Problem.** Seven `== 0.0` comparisons gate physics branches -
`circuit.py` twice, `tissue.py` twice, `blood.py` twice, and
`uptake_system.py` once. Each is correct: zero is the only singular point,
and the limit as the flow approaches zero from above is continuous with the
branch, since the time constant grows without bound, `exp(-dt/tau)` goes to
one, and the state is unchanged. The denormal and overflow cases were
checked and behave the same way.

**Why it matters.** Nothing here is broken. The finding is that in a
codebase which explains every other decision at length, an exact float
equality in a safety-critical path is where a reviewer stops - and nothing
tells them it was reasoned about. An unexplained correct thing costs a
re-derivation every time someone reads it, and invites a "fix" that would
introduce an epsilon where none belongs.

**Where.** `src/anesthesia_sim/core/circuit.py`,
`src/anesthesia_sim/core/tissue.py`, `src/anesthesia_sim/core/blood.py`,
`src/anesthesia_sim/core/uptake_system.py`.

**Decision needed.** Whether this is worth any words at all, and if so
where: one explanation in `core/validation.py` or a `core/` module docstring
that all six sites can be read against, rather than the same sentence six
times. The alternative - that a reader who knows the domain will work out the
limit argument unaided - is a legitimate answer for a project whose
`core-domain` rule says the equation should be visible rather than buried
under commentary.

**Done when.** The decision is recorded, and if a note is added it lives in
one place rather than at each site.

**Measured 2026-09-02: the guards are safe, as claimed.** A vessel-rich
tissue group was stepped at a range of blood flows approaching zero from
above, holding everything else fixed:

| `blood_flow_l_min` | resulting `agent_amount_l` | matches the `== 0.0` branch |
| --- | --- | --- |
| `0.0` | `0.066` | - |
| `5e-324` (smallest denormal) | `0.066` | yes |
| `1e-300` | `0.066` | yes |
| `1e-30` | `0.066` | yes |
| `1e-12` | `0.06600000000000002` | differs by `1.4e-17` |

The last row is the correct continuous behaviour rather than a discrepancy:
a real flow moves a real, tiny amount of agent. At the denormal end
`time_constant_s` overflows to `inf`, `exp(-0.1/inf)` is exactly `1.0`, and
the state is unchanged - which is what the branch returns. So the branch
agrees with the limit at every magnitude tested, and this item remains what
it was captured as: a documentation question, not a defect.

**What v0.4.1 does to this (added 2026-09-03).** The inventory shrinks. Counted today,
`core/` holds seven exact float-equality guards. Three are in `time_constant_s`
properties and survive as they are: `circuit.py:126`, `tissue.py:98`,
`blood.py:66`. Three sit inside sub-steps `PL-GS5X` deletes or restructures -
`uptake_system.py:392` (`_exchange_circuit_and_alveoli`), `tissue.py:131`
(`TissueGroup.advance`), `blood.py:92` (`VenousBloodCompartment.advance`) - and
the seventh, `circuit.py:195` in `advance_fresh_gas`, depends on whether that
method survives the swap. The matrix formulation also divides by *volume* rather
than by flow, so zero flow may not be a singularity in the new code at all.

So the "Measured 2026-09-02" table describes methods that are about to change.
Do this after `PL-GS5X`, when the count is three or four rather than seven, and
re-measure rather than trusting the table.