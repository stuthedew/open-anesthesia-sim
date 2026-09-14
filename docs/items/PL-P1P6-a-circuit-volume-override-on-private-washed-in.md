---
id: PL-P1P6
title: A circuit-volume override on _private_washed_in_system would let one test pin the direction that a larger circuit-side agent store can only slow the elimination
status: untriaged
added: 2026-09-13
---

**Problem.** A circuit-volume override on _private_washed_in_system would let one test pin the direction that a larger circuit-side agent store can only slow the elimination

**Where this came from.** `PL-XWCY` struck circuit-wall absorption as a
candidate for desflurane's elimination residual on two independent grounds,
and the second is a directional argument rather than a measurement: a wall
that dissolves agent through the administration gives it back through the
washout, holding the inspired fraction up and *slowing* the alveolar fall,
where the residual is the model washing out too fast. The same argument then
carries the sevoflurane/isoflurane half, and the paragraph in `docs/MODEL.md`
attributing most of the elimination departure to the rebreathing circuit rests
on it too.

**What would pin it.** One test over a range of circuit volumes at the shipped
operating point, asserting that the five-minute `F_A/F_A0` rises monotonically
with circuit volume - the executable form of "a larger circuit-side agent
store can only slow the elimination". Circuit volume is a proxy for the wall
store rather than the mechanism itself, and the test would have to say so:
both are circuit-side capacity returning agent to the inspired stream, which
is the property the argument turns on.

**Why it was not just written.** `_private_washed_in_system` in
`tests/reference/test_published_wash_in_and_elimination.py` takes exactly one
parameter override, and its docstring states that the override exists for one
named test and that "Every other caller leaves it `None` and gets the shipped
parameter set." Adding a second is a change to a documented invariant of a
shared safety-critical fixture, which is a decision rather than a fix.

**The alternative worth weighing first**, because it may make the override
unnecessary: `test_elimination_is_dominated_by_the_rebreathing_circuit` already
sweeps fresh gas flow and asserts the elimination ratio moves more than 10
published SD across it, and `test_removing_the_rebreathing_circuit_is_what_moves_the_elimination_comparison`
asserts the open-circuit contrast. Between them the circuit's effect on the
ratio is established and signed. What neither pins is monotonicity in the
*store* rather than in the flow, which is the exact claim. So the question to
settle is whether that gap is worth a fixture change, and the honest answer may
be no.
