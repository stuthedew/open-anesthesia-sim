---
id: PL-4GN8
title: The mass-balance release gate's absolute tolerance tracks whichever dial its test happens to run at
status: untriaged
added: 2026-09-02
---

**Problem.** The mass-balance release gate's absolute tolerance tracks whichever dial its test happens to run at

**Why it matters.**

**Where.**

**Done when.**

**Problem.** Three reference tests assert `validation.absolute_error_l <=
1e-12` on a mass-balance total that scales with the delivered concentration.
The tolerance does not, so how demanding the gate is depends on the dial the
test happens to be written at, and moving a dial silently moves the gate.

**Measured** while working PL-019, isoflurane and desflurane over 600 s
wash-in plus 600 s washout:

| Dial | Delivered | `absolute_error_l` | Headroom under 1e-12 |
| --- | --- | --- | --- |
| 8% | 3.2 L | 1.73e-13 / 1.80e-13 | x5.8 / x5.5 |
| 4% | 1.6 L | 8.64e-14 / 9.02e-14 | x11.6 / x11.1 |

Halving the dial halves the error and doubles the headroom. Nothing about
the numerics changed.

**Why it matters.** The gate still has 5-12x headroom either way and a real
conservation defect is orders of magnitude, not factors of two, so this is
not a defect in what shipped. It is a gate that does not mean a fixed thing:
`docs/MODEL.md` documents 1e-12 as a release tolerance, and what that
sentence certifies now varies with an unrelated test-setup choice.

**Approach.** Assert on the relative quantity the validator already carries
(`absolute_error_l / delivered_agent_l`, or an equivalent) so the gate is
dial-independent, and restate the documented tolerance in those terms. Check
whether `AgentSimulationValidator`'s own halt threshold has the same shape
before changing only the tests.

**Where.** `tests/reference/test_multi_agent.py`,
`tests/reference/test_sevo_patient.py`,
`src/anesthesia_sim/core/agent_simulation_validation.py`, `docs/MODEL.md`.
