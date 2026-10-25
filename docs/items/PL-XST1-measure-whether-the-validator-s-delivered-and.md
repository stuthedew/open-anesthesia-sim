---
id: PL-XST1
title: Measure whether the validator's delivered and exhausted totals, summed by plain += over the 8.64e7 steps of a 24 h run at the 1 ms step floor and 10 L/min, drift past AGENT_ACCOUNTING_RELATIVE_TOLERANCE, and compensate the sums if they do
priority: P2
effort: S
status: done
classes: defect
feature: floating-point-domain
touches: src/anesthesia_sim/core/agent_simulation_validation.py, docs/MODEL.md, tests/unit
deferred-from: v0.7.0 - split from the generator head PL-58D7 on 2026-10-25, which this gate defers for the same reason; the generator tier ranks it, not the gate
added: 2026-10-25
closed: 2026-10-25
pr: 1826
payoff: the accounting check's running totals are measured against an exactly rounded sum at the worst case, so it cannot halt a correct 24 h run
verify: grep -rq 'def test_the_running_agent_totals_stay_within_a_tenth_of_the_accounting_tolerance' tests/unit
---

**Problem.** Measure whether the validator's delivered and exhausted totals, summed by plain += over the 8.64e7 steps of a 24 h run at the 1 ms step floor and 10 L/min, drift past AGENT_ACCOUNTING_RELATIVE_TOLERANCE, and compensate the sums if they do

**Where it is.** `AgentSimulationValidator.record_external_agent_transfer` adds each step's delivered and exhausted amounts to running totals with plain `+=`. The worst case in the supported envelope is desflurane at its 18% vaporizer maximum, 10 L/min and the 1 ms step floor for 24 h. That run delivers about 2592 L of agent over 8.64e7 additions. At that size one unit in the last place is about 4.5e-13 L, and a nearly constant increment can round the same way each time. The `PL-58D7` inventory estimated the drift at up to about 4e-6 L, or 1.6e-9 of the total, which is above `AGENT_ACCOUNTING_RELATIVE_TOLERANCE = 1e-9`. That would be a false `AgentSimulationValidationError`, an obvious halt rather than a wrong value. This is an estimate made on 2026-10-25 by reading the code. Nothing has measured it.

**What to do.** Measure the drift first: drive the totals with the worst-case increments, compare them against an exactly rounded sum (`math.fsum` of the same increments), and record the largest relative difference. If it reaches a tenth of the tolerance, use compensated summation for the two totals. Otherwise record the measurement and its margin in `docs/MODEL.md` § "Mass-balance identity" and close the item.

**Why it matters.** A false accounting failure halts a correct run at the edge of the supported envelope. A guard that fires on correct runs cannot be trusted when it fires on a wrong one.

**Done when.** The worst-case drift is measured and recorded with its margin. If the margin was less than ten times, the totals use compensated summation and a test pins the drift below a tenth of the tolerance.

**Generator check.** A member of the `floating-point-domain` feature, split from `PL-58D7`, the generator head.

**Outcome (2026-10-25).** Measured with the real `AgentUptakeSystem` over four full 24 h runs at the 1 ms step, desflurane at 18% and 10 L/min. With plain `+=`, each total drifted up to 1.0e-9 from an exactly rounded sum, and at the reference adult's ventilation and cardiac output the accounting residual reached 9.77e-10 at 18.96 h, within 2.4% of the halt threshold. The margin was far below ten times, so both totals now use Kahan compensated summation. Each total then stays within 1e-16 of the exact sum, and the residual left, the model's own, is 3.73e-11 at 24 h. `docs/MODEL.md` § "Mass-balance identity" has the table, and `test_the_running_agent_totals_stay_within_a_tenth_of_the_accounting_tolerance` pins the totals within Kahan's bound against an exact sum.

The close-out audit's mutation check found 7 survivors on lines this branch did not change, the field names in the two input refusals of `record_external_agent_transfer`. They are filed as `PL-B3YV`.
