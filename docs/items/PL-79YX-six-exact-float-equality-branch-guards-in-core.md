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
