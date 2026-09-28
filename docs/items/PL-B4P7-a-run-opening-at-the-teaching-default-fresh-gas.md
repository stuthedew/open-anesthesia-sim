---
id: PL-B4P7
title: A run opening at the teaching-default fresh gas flow records nothing saying so, so once a second machine profile can reach a run nothing can label that flow as the project's teaching choice rather than the machine's
priority: P2
effort: M
status: blocked
classes: safety, anticipated, ux
feature: machine-profile-framework
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/circuit.py
blocked-by: PL-2FZ9
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21); safety, but anticipated and blocked behind PL-2FZ9, which is what makes it live, so the carve-out for a concern whose feature does not exist yet applies
added: 2026-09-27
---

**Problem.** A run opening at the teaching-default fresh gas flow records nothing saying so, so once a second machine profile can reach a run nothing can label that flow as the project's teaching choice rather than the machine's

**Found by PL-QW19's review, 2026-09-27; not live yet.** Since `PL-QW19` a
machine profile may state no startup fresh gas flow, and
`AgentUptakeSystem.for_agent()` then opens the run at
`TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN` (`core/circuit.py`). Nothing records
which happened: the circuit holds a flow, not where it came from. Today the one
shipped profile states its 4.0 L/min, so the question cannot arise. Once
`PL-2FZ9` (load a machine profile by id) lets a silent profile reach a run, a
machine-parameter display such as `PL-WZVZ`'s could not tell "this machine's
flow" from "the project's teaching choice", and a learner could read 4 L/min as
a property of, or a recommendation for, the selected machine.

**Three places to settle together, when it goes live.**

- `for_agent()` should carry the flow's origin (stated by the profile, or the
  teaching default) where a display can read it.
- `SimulationController._build_state`'s docstring
  (`src/anesthesia_sim/app/controller.py`) says a `None` override "leaves that
  data-file value in place". With a silent profile it leaves the teaching
  default, which is not a data-file value of that profile.
- A silent profile whose declared deliverable range excludes the teaching
  default is refused by `BreathingCircuit` as "fresh_gas_flow_l_min of 4.0 is
  outside what this machine can deliver", which never says the 4.0 was the
  fallback. `PL-QW19`'s brief asked for that refusal in the circuit's own words,
  so this is about what the message says, not whether it refuses.

**Also worth weighing then.** The teaching default's rationale is a 90 s circuit
time constant at the reference profile's 6.0 L. At a smaller assembled volume
the same flow opens a shorter lag, about 50 s at the 3.3 L the survey records
for a Perseus A500 with its patient circuit (`docs/machine-survey.md` § "(a1)").

**Why it matters.** Once a silent profile can reach a run, a machine-parameter
display could show the teaching default as the selected machine's own flow or as
a recommendation for it: the correct number with the wrong provenance, which the
safety-critical standard counts as a safety failure. Blocked on `PL-2FZ9`, which
makes that reachable, and classed `anticipated` so it waits at that item's band.
