---
id: PL-4CZW
title: docs/ARCHITECTURE.md § 'Data flow' says a run forked onto the supported run length is treated as stopped there, but the branch chapter says a fork there is refused; one is stale (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: done
classes: defect, docs
feature: architecture-md-structure
touches: docs/ARCHITECTURE.md
deferred-from: v0.7.0 - a new problem: at the freeze (817a4d88) a branch could still open on the supported run length, so the sentence was true; 2713d097 (PL-VHQX, 2026-10-31) made the controller refuse that fork and left the sentence stale
added: 2026-11-05
closed: 2026-11-09
pr: 2072
payoff: a contributor reads one answer to whether a branch can open on the supported run length, and it is the one the controller enforces
verify: ! grep -qF 'forked or reset onto that step' docs/ARCHITECTURE.md
reenters: PL-4FBP
---

**Problem.** docs/ARCHITECTURE.md § 'Data flow' says a run forked onto the supported run length is treated as stopped there, but the branch chapter says a fork there is refused; one is stale (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/ARCHITECTURE.md at cfb15a4a, before the line edit):

- **Query, a branch at the supported run length.** The file contradicts itself. Data flow 409-422 says "a run forked or reset onto that step is also treated as stopped there". Branch 572-589 and 590-601 say a fork at the supported run length is refused ("`_resume_point` rejects a fork there for every method"). Can a branch open there?

**Checked 2026-11-09:** `grep -n 'forked or reset onto that step' docs/ARCHITECTURE.md` still finds the sentence, now in § "Failures and halts" after the restructure: "a run that is forked or reset onto that step is also treated as stopped there (`PL-5291`)". The branch chapter still says that `_resume_point` rejects a fork on the supported run length for every method (`PL-VHQX`). The code agrees with the branch chapter. `SimulationController._resume_point` in `src/anesthesia_sim/app/controller.py` raises `SimulationConfigurationError` when the fork lies on the supported run length. `SimulationController.reset` says in its docstring that no branch opens on the limit, so a branch's Reset never returns it there. The sentence in § "Failures and halts" is the stale one: only a run that steps onto the limit stops there.

**Why it matters.** A contributor who reads that sentence will expect a branch or a reset to be able to land on the supported run length. They may then write code or a test for a state that the controller refuses to create.

**Done when.** § "Failures and halts" no longer says that a run can be forked or reset onto the supported run length. It says that a run which steps onto the limit stops there, and that no fork or reset lands on it, with a pointer to the branch chapter.

**Generator check.** Instance of `PL-4FBP`'s fact, "The link between a document sentence and the tree fact it restates": the sentence went stale when `PL-VHQX` changed the controller, after `PL-4FBP` closed. `PL-4FBP`'s convention binds only `docs/MODEL.md` and `README.md`, so nothing holds a `docs/ARCHITECTURE.md` sentence to the code.
