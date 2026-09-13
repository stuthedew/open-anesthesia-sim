---
id: PL-79YX
title: Six exact float-equality branch guards in core/ are correct and nowhere explained
status: done
priority: P3
effort: S
classes: docs
touches: src/anesthesia_sim/core/__init__.py, tests/unit/test_compartment_primitives.py
added: 2026-09-02
closed: 2026-09-13
verify: uv run pytest tests/unit/test_compartment_primitives.py -q
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

**Inventory changed by `PL-GS5X`, 2026-09-06.** This item's own note predicted
that three of its seven exact-float-equality guards sit in code the exact step
deletes or restructures. Two of the three are gone:
`uptake_system.py`'s `_exchange_circuit_and_alveoli` no longer exists, and
`AlveolarCompartment.apply_blood_uptake` went with it (`PL-LKRP`).
`tissue.py`'s and `blood.py`'s `advance()` guards survive, but both methods now
have no production caller at all — see `PL-74R0`, which decides whether they
stay. Re-run the item's own walk before deciding; the decision may be smaller
than the brief describes, or moot.

**Decided 2026-09-13: yes, it is worth the words — and the walk was re-run as
the note above asked, which changed the answer twice over.**

The brief expected one sentence about a singular point and a continuous limit.
Re-measured on the post-`PL-GS5X` tree, the six surviving guards do not share
one reason, and two of the three reasons are not about singular points at all.
The explanation lives in `core/__init__.py`, once, and
`tests/unit/test_compartment_primitives.py` re-runs every number in it.

**The inventory, and what each guard is actually for.** Six, in three files,
and the "reader who knows the domain will work it out unaided" answer would
have had them work out three different arguments:

| Site | Without the guard |
| --- | --- |
| `circuit.py`, `tissue.py`, `blood.py` — `time_constant_s` | `ZeroDivisionError`. Python raises on `V/0.0` rather than returning `inf`, so the branch is the only route to the `inf` `docs/MODEL.md` states. |
| `circuit.py` — `advance_fresh_gas` | `nan`. The exhausted-agent integral carries `tau * (1 - exp(-dt/tau))`, which at `tau = inf` is `inf * 0.0` — for *every* circuit state, including one already at the dial. The circuit would report a `nan` exhaust to the mass-balance check. |
| `tissue.py`, `blood.py` — `advance` | One unit in the last place. The fraction comes back right, but the amount is written as `capacity_l * next_fraction`, and that round trip is not bit exact. |

**Why the test is an equality and never a tolerance.** Walked upward from
zero, the general path lands the *same* distance from the branch at 5e-324, at
1e-300 and at 1e-30 — that distance being one rounding of `d + (i - d)`, not
flow moving agent. Nothing changes across 294 orders of magnitude, so there is
no band of nearly-zero flows for an epsilon to catch. The first magnitude at
which the difference moves is a flow of 1e-12 L/min, twelve orders below
anything the model supports, where a real flow moves a real 1e-15 L of agent.
An epsilon would not remove a discontinuity; it would introduce one.

**The 2026-09-02 table was right and its state was too easy**, which is the
finding worth carrying forward. `d + (i - d)` returns `i` bit for bit whenever
`i` and `d` are within a factor of two of each other, and that walk was run at
a loaded fraction comparable to the fraction driving it. Measured today at a
loaded fraction well below its input — the ordinary case, a compartment at the
start of a wash-in — the same walk is one rounding out instead. Both halves
were then tested: deleting either `advance` guard left the whole suite green,
and left the first draft of the new module green too.

So the third reason in the table above is the one the old table could not see,
and the tests now pin it at a state where it is visible. All seven mutations —
each guard deleted, each `time_constant_s` widened to a `< 1e-9` tolerance,
and `PatientCompartments.advance` reinstated — now fail.

**`core/validation.py` was the wrong home**, of the two the brief offered. It
guards caller-supplied values and raises `SimulationConfigurationError`; a
physical zero in a model quantity is not a rejected input, and filing the two
together would have made both harder to read. The package docstring in
`core/__init__.py` is where all six sites can be read against one statement,
and it is where `PL-74R0`'s neighbouring rule about what an `advance()` is
already had to go.
