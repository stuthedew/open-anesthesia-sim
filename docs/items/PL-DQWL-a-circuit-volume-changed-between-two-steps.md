---
id: PL-DQWL
title: A circuit volume changed between two steps leaves the run's uptake system off the state its record stores for the second it has reached, so a deep copy or a pickle of that run is refused with a message that names resume_at, and a branch opened at that second would start from a different circuit fraction than the parent now holds; the app offers no mid-run volume control yet (found at blind review of PL-HXNL)
status: untriaged
feature: replay-findings
touches: src/anesthesia_sim/core/simulation.py, src/anesthesia_sim/core/circuit.py
added: 2026-11-22
---

**Problem.** A circuit volume changed between two steps leaves the run's uptake system off the state its record stores for the second it has reached, so a deep copy or a pickle of that run is refused with a message that names resume_at, and a branch opened at that second would start from a different circuit fraction than the parent now holds; the app offers no mid-run volume control yet (found at blind review of PL-HXNL)

**Found by.** The first blind review pass on `PL-HXNL`, 2026-11-22. The
reviewer stepped a sevoflurane run 20 s, then called
`system.circuit.set_circuit_volume` with 1.5 times the volume. The circuit
keeps its agent amount, so its fraction changes, and the system no longer
stands at the state that `StoredStates` holds for 20 s. `advance()` still
steps. Since `PL-HXNL`, `SimulationState.__setstate__` runs the constructor
with the stored states as the opening record, and the constructor's
`stands_at` check refuses the copy with a message that tells the caller to use
`resume_at`, which is not the cause.

**Why it matters.** No learner can reach it today: the interface sets the
circuit volume only when a run is built. A mid-run volume control, or a
branch opened at that second, would meet it. The refusal is the safe side of
the choice, so a learner would see an error rather than a wrong value.

**What a fix has to decide.** Whether a volume change between steps should be
recorded as a setting change, so the record holds the state the next step
starts from, or refused once a run has stepped.
