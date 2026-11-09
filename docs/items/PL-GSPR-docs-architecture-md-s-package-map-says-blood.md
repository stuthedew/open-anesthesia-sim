---
id: PL-GSPR
title: docs/ARCHITECTURE.md's package map says blood.py, tissue.py and circuit.py advance their own amounts, but § 'Data flow' says one exact propagation advances the whole coupled system; the map may be stale (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: done
classes: defect, docs
feature: architecture-md-structure
touches: docs/ARCHITECTURE.md
added: 2026-11-05
closed: 2026-11-09
pr: 2072
payoff: a contributor looking for how a run advances goes to the one exact propagation, not to per-compartment methods that no run calls
verify: grep -qF 'not how a run advances' docs/ARCHITECTURE.md
reenters: PL-4FBP
---

**Problem.** docs/ARCHITECTURE.md's package map says blood.py, tissue.py and circuit.py advance their own amounts, but § 'Data flow' says one exact propagation advances the whole coupled system; the map may be stale (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, how a step is advanced.** The file contradicts itself. Package map 93 says `blood.py` and `tissue.py` "advance their amount" by the first-order approach, and `circuit.py` "advances its fraction". Data flow 185-206 says `advance()` moves the whole coupled system in one exact propagation, "not by a sequence of sub-exchanges", with one matrix-vector product for the six fractions. Is `exponential_approach.py` still used when a step is advanced, and if so, where?

**Checked 2026-11-09:** `grep -n 'exponential_approach.py' docs/ARCHITECTURE.md` finds the package map entry: it is "the first-order approach to a held input that blood.py and tissue.py advance their amount by, and circuit.py its fraction". § "Data flow" says that `AgentUptakeSystem.advance()` moves the whole coupled system in one exact propagation. Both are true of the code, but the map reads as if a run's step used the first-order approach. In the code, `exponential_approach` is called only from each compartment's own `advance` method (`VenousBloodCompartment.advance`, `TissueGroup.advance`, and the circuit's). The docstrings of the first two say that the method "is not how a run advances". A run advances through `AgentUptakeSystem.advance()` and `core/run_definition.py`, which use `matrix_exponential` only. So `exponential_approach.py` is used when a single compartment is advanced on its own, as its own closed-form solution, and never inside a run's step.

**Why it matters.** A contributor who reads the map will look in `exponential_approach.py` and the compartments' `advance` methods for how a run moves forward. A change made there does not change any run.

**Done when.** The package map entries for `exponential_approach.py`, `blood.py`, `tissue.py` and `circuit.py` say that the first-order approach is each compartment's own closed-form solution for a held input and "not how a run advances", and that a run advances only through `AgentUptakeSystem.advance()`.

**Generator check.** Instance of `PL-4FBP`'s fact, "The link between a document sentence and the tree fact it restates": the map entry describes how the code advances, and no check holds that description to the code.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/ARCHITECTURE.md` already has the package map entry saying `blood.py` and `tissue.py` "advance their amount by" the first-order approach (row 85), beside § "Data flow"'s "one exact propagation" (row 169). That tree's `AgentUptakeSystem.advance` already used `matrix_exponential` only. So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.
