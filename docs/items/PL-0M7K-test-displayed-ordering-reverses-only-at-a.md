---
id: PL-0M7K
title: test_displayed_ordering_reverses_only_at_a_crossing in tests/reference/test_coupled_dynamics.py can fail only when the neighbouring absolute gate fails and never calls the shipped format_percent, yet its docstring and docs/MODEL.md's 'Displayed precision' cite it as evidence about the display path
priority: P2
effort: S
status: ready
classes: test, docs
feature: tests-detect-wrong-values
touches: tests/unit/test_formatting.py, tests/reference/test_coupled_dynamics.py, docs/MODEL.md
added: 2026-10-17
payoff: the claim that displayed concentrations keep their order is held by a test of the shipped formatter, so docs/MODEL.md cites evidence that can fail on the display path
verify: grep -q 'def test_format_percent_preserves_order' tests/unit/test_formatting.py
---

**Problem.** test_displayed_ordering_reverses_only_at_a_crossing in tests/reference/test_coupled_dynamics.py can fail only when the neighbouring absolute gate fails and never calls the shipped format_percent, yet its docstring and docs/MODEL.md's 'Displayed precision' cite it as evidence about the display path

**Severity: medium.** As a test that certifies nothing on its own it would
rate high, but the display-side risk is narrower than first claimed. Audit
finding ORC-1 (reference tier). The verifier rated it "partly" true and
corrected it; the corrected claim is what this item states.

**Evidence.** In `tests/reference/test_coupled_dynamics.py`,
`_displayed_percent` is a test-local `round(fraction * 100, 2)`. The file
takes only `CONCENTRATION_DISPLAY_DECIMALS` from `app/formatting.py` and never
calls `format_percent`. `test_displayed_ordering_reverses_only_at_a_crossing`
drives the same trajectories, the same six states and the same shipped steps
as the helper behind `test_exact_step_matches_the_independent_solution_everywhere`.
Its threshold, `MAX_INVERTED_GAP_IN_DISPLAY_COUNTS`, is twice
`EXACT_STEP_ORACLE_TOLERANCE` in display counts. Because `round()` is
monotone, the test adds nothing to the absolute gate. The comment above that
constant says so: "if the absolute gate passes, this one cannot fail".

The same comment still says the test checks "that the display path has not
acquired a transformation that reorders". `docs/MODEL.md` § "Displayed
precision" says the test "holds the claim" behind the interface marking
nothing when compartments are compared. Yet the shipped `format_percent`
renders with an f-string and maps positive values below the resolution to
'<0.01%', a branch that the test's model of the display does not have. No
test anywhere asserts that `format_percent` preserves order. `@given` appears
only in `test_supported_range_edges.py` and `test_exponential_approach.py`.

The display-side risk is narrower than the audit first said. Literal pins in
`tests/unit/test_formatting.py` catch truncation, significant-figure rendering
and a changed sub-resolution branch. Per-compartment decimals cannot live in
`format_percent`, which takes no compartment: `dashboard_frame.py` formats
every compartment through that one call, and `test_simulation_view.py`
compares the circuit, muscle and fat readouts with `format_percent` of their
own snapshot fields. What stays uncovered is a non-monotone `format_percent`
defect that misses every pinned literal, because no ordering property exists.

**Why it matters.** Fifteen green parametrizations read as verification of the
displayed ordering, and `docs/MODEL.md` cites them as such, while they can
fail only when the neighbouring gate fails. The citation claims more than the
suite enforces.

**Where.** `tests/reference/test_coupled_dynamics.py`
(`test_displayed_ordering_reverses_only_at_a_crossing`, `_displayed_percent`,
`MAX_INVERTED_GAP_IN_DISPLAY_COUNTS`); `tests/unit/test_formatting.py`;
`docs/MODEL.md` § "Displayed precision".

**Recommended fix.** Make the test parse the output of the shipped
`format_percent` instead of `_displayed_percent`, reading '<0.01%' as a value
strictly between 0 and 0.01, or delete the test. Add a derandomized Hypothesis
property to `tests/unit/test_formatting.py`: for fractions a <= b,
parsed(format_percent(a)) <= parsed(format_percent(b)), covering 0, the '<'
branch and the display-count boundaries. Point the `docs/MODEL.md` citation at
that property and at `test_exact_step_matches_the_independent_solution_everywhere`.

**Done when.** A test asserts that `format_percent` preserves order, and
`docs/MODEL.md` § "Displayed precision" cites only tests that can fail on the
display path.

**Related.** `PL-74TX` (done) cites this test as enforcing the claim.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.
