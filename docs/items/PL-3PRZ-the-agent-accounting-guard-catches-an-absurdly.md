---
id: PL-3PRZ
title: The agent-accounting guard catches an absurdly small alveolar volume at 1e-9 L but stops catching it by 1e-300 L, where the run returns a concentration of exactly zero with accounting passing
priority: P2
effort: M
status: ready
classes: defect
feature: core-guard-coverage
touches: src/anesthesia_sim/core/agent_simulation_validation.py, src/anesthesia_sim/core/alveolar.py, tests/unit/test_agent_simulation_validation.py, docs/MODEL.md
added: 2026-09-06
verify: uv run pytest tests/unit/test_agent_simulation_validation.py && grep -q 'def test_an_alveolar_volume_that_underflows_the_accounting_residual_is_refused' tests/unit/test_agent_simulation_validation.py
---

**Problem.** Measured 2026-09-06 on sevoflurane at the shipped 0.1 s step,
driving `AlveolarCompartment.gas_volume_l` downward and advancing three steps:

| `gas_volume_l` | Outcome |
| --- | --- |
| 0.005 L (and 1e-6 L) | advances, accounting passes |
| 1e-9, 1e-12, 1e-15, 1e-30 L | `AgentSimulationValidationError` - the run halts |
| 1e-100 L | `SimulationNumericalError` - the step is rolled back |
| **1e-300 L** | **advances, returns a concentration of exactly 0, accounting passes** |

The last row is the defect. Every row above it fails obviously, which is the
required behavior; the bottom one succeeds quietly and hands back a number.

**Why it matters, and why it is small.** A concentration of zero from a lung
of 1e-300 L is a plausible-looking value produced where every intermediate
guard has been passed - `CLAUDE.md`'s "prefer an obvious failure to a
plausible-looking number" inverted, in the one regime the guard was expected
to cover most easily. Against that: no caller reaches 1e-300 L by mistake,
and `docs/MODEL.md` § "What is not bounded this way" now states in terms
that the accounting guard is a backstop rather than a declared bound, so
nothing in the documentation relies on it.

Worth understanding rather than worth fixing blind. The likely mechanism is
that the amounts involved underflow to exactly zero, so the residual the
accounting check forms is zero and passes - which would mean the check is
comparing a quantity that has itself been annihilated. If that is what
happens, the same shape could arise wherever an amount underflows, which is
the part that generalizes beyond an absurd volume.

**Where.** `src/anesthesia_sim/core/agent_simulation_validation.py`;
`src/anesthesia_sim/core/alveolar.py`.

**Done when.** The mechanism is established rather than assumed - whether the
amounts underflow to exactly zero, so the residual the accounting check forms
is itself annihilated and passes - and then either the guard refuses the
regime, or `docs/MODEL.md` records the bound below which the accounting check
stops being evidence, with the reason. A regression test at 1e-300 L pins
whichever it turns out to be.

**Found by** `PL-GYH2`, while checking a claim written into `docs/MODEL.md`
rather than asserting it.

**Classed `defect` rather than `science`, and it can be overruled.** No
interface path reaches an alveolar volume of 1e-300 L - the circuit and
alveolar volumes are not user-settable - so no clinician can be misled by this
today, and `docs/MODEL.md` § "What is not bounded this way" already states that
the accounting guard is a backstop rather than a declared bound. What would
change the class is the generalization the brief names: if an amount
underflowing to zero can annihilate the residual anywhere else, the guard is
weaker than the specification says it is.
