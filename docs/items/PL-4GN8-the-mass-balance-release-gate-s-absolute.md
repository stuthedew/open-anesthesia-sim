---
id: PL-4GN8
title: The mass-balance release gate's absolute tolerance tracks whichever dial its test happens to run at
priority: P1
effort: S
status: ready
classes: science, test
feature: numerical-domain
touches: tests/reference/test_multi_agent.py, tests/reference/test_sevo_patient.py, src/anesthesia_sim/core/agent_simulation_validation.py, docs/MODEL.md
added: 2026-09-02
verify: uv run pytest tests/reference/test_multi_agent.py tests/reference/test_sevo_patient.py && grep -q 'relative_error <=' tests/reference/test_multi_agent.py && grep -q 'relative_error <=' tests/reference/test_sevo_patient.py
---

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
sentence certifies now varies with an unrelated test-setup choice. A later
session that lowers a dial for an unrelated reason strengthens the
conservation gate by a factor of two without knowing it, and one that raises
a dial weakens it the same way. That is the case `CLAUDE.md`'s
deterministic-tooling section calls a check passing while the guarantee it
stands for is void, and it is why this is classed `science` rather than as
test hygiene: what is wrong is the meaning of a documented scientific
guarantee, not the arithmetic under it.

**Approach.** Assert on the relative quantity the validator already carries
so the gate is dial-independent, and restate the documented tolerance in
those terms.

**The validator is already the right shape; only the tests are not.**
Checked 2026-09-02: `core/agent_simulation_validation.py` computes both
`absolute_error_l` and `relative_error` (`absolute_error_l /
max(initial_agent_l + delivered_agent_l, MINIMUM_RELATIVE_SCALE_L)`), and its
own halt threshold passes on `absolute <= AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L
or relative <= AGENT_ACCOUNTING_RELATIVE_TOLERANCE`. So the dial-independent
quantity exists and is exported on `AgentAccountingCheck`; the reference tests
simply ignore it. The change is to the assertions and to `docs/MODEL.md`, not
to the validator - confirm that reading before touching `core/`, and if the
halt threshold does turn out to need a change, that is a separate item.

**Where.** `tests/reference/test_multi_agent.py:77`,
`tests/reference/test_sevo_patient.py:222`,
`src/anesthesia_sim/core/agent_simulation_validation.py` (read only, unless
the halt threshold is wrong too), `docs/MODEL.md`.

**Done when.** Both reference tests assert a dial-independent conservation
bound, the numeric tolerance is stated as a relative one with the reasoning
for its value, and `docs/MODEL.md`'s release-gate sentence says the same
thing the tests now assert - so that changing a dial in a test cannot change
what the gate certifies.
