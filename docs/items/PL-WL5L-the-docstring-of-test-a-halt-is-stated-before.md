---
id: PL-WL5L
title: The docstring of test_a_halt_is_stated_before_its_dials_are_written says the circuit refuses at build a fresh-gas-flow range narrower than one dial step, but BreathingCircuit._require_the_two_flow_claims_overlap refuses only an empty overlap (found triaging PL-M3M2, 2026-10-17)
priority: P3
effort: S
status: ready
classes: docs, test
touches: tests/integration/test_simulation_view.py
added: 2026-10-17
payoff: the test's docstring no longer claims a build-time guard the circuit does not have, so nobody relies on it
verify: ! grep -qF 'and the circuit refuses at build' tests/integration/test_simulation_view.py
---

**Problem.** The docstring of test_a_halt_is_stated_before_its_dials_are_written says the circuit refuses at build a fresh-gas-flow range narrower than one dial step, but BreathingCircuit._require_the_two_flow_claims_overlap refuses only an empty overlap (found triaging PL-M3M2, 2026-10-17)

**Checked 2026-10-17.** The docstring at
`tests/integration/test_simulation_view.py`, `test_a_halt_is_stated_before_its_dials_are_written`,
says a fresh gas flow range narrower than the dial's 0.1 L/min step is one "the
circuit refuses at build". `core/circuit.py`'s `_require_the_two_flow_claims_overlap`
refuses only an empty overlap.

**Why it matters.** A reader trusting the docstring believes a guard exists that
does not. A narrow range that is not empty still reaches `setting_readouts` and
raises there.

**Done when.** The docstring says what the circuit actually refuses, and no
longer says it refuses a narrow range at build.
