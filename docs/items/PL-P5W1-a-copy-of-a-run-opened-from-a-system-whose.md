---
id: PL-P5W1
title: A copy of a run opened from a system whose amounts were written directly can be refused before its first step, because about one amount in eight does not survive the fraction round trip that the copy's check makes (found at blind review of PL-DQWL)
status: untriaged
feature: replay-findings
added: 2026-11-22
---

**Problem.** A copy of a run opened from a system whose amounts were written directly can be refused before its first step, because about one amount in eight does not survive the fraction round trip that the copy's check makes (found at blind review of PL-DQWL)

**Found by.** The first blind review pass on the second design of `PL-DQWL`,
2026-11-22. A run built with no opening record stores the fraction it reads,
amount divided by volume. Since `PL-HXNL`, a copy or a pickle rebuilds the run
through its constructor, which checks with `AgentUptakeSystem.stands_at` that
the system stands at that state. That check writes the fraction back, and for
about one amount in eight the product differs from the amount in the last bit,
so the copy is refused. Checked in this session: 36 of 300 random alveolar
amounts from 0.001 to 0.2 L, written directly with the accounting anchored to
match, were refused.

**Why it matters.** Only a direct write to a compartment's amount reaches it,
which no code in `src/` makes, and a trunk opens from an empty system whose
fractions are exactly 0. The refusal is the safe side.

**What was tried.** Placing the system at the stored state when the run opens
(`resume_at`) removed the refusal, but it writes through each compartment's
guard when the run is built, so a system that a test builds to fail inside a
step failed at construction instead
(`tests/unit/test_uptake_system_failure.py::test_simulation_time_does_not_advance_through_a_failed_step`).
A fix has to make the copy's check compare what the run itself last read
(`SimulationState._resting_state`) rather than writing a state into the system.
