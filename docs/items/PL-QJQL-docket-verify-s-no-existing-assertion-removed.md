---
id: PL-QJQL
title: docket verify's no existing assertion removed check cannot see pytest.raises or pytest.warns, so deleting a with pytest.raises block removes an assertion the check reports as none
priority: P2
effort: S
status: ready
classes: defect, infra
feature: verify-assertion-check
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-17
verify: grep -q 'def test_a_removed_pytest_raises_block_is_an_assertion_removed' subprojects/docket/tests/test_verify.py
---

**Problem.** docket verify's no existing assertion removed check cannot see pytest.raises or pytest.warns, so deleting a with pytest.raises block removes an assertion the check reports as none

**Where.** `ASSERTION_RE` in `subprojects/docket/src/docket/verify.py` matches
two shapes and no others: the `assert` keyword opening a statement, and a call
whose name begins `assert` - `assertEqual(`, `assert_called_once_with(`,
`assert_allclose(`. A context manager asserting by expectation carries the word
nowhere, so `with pytest.raises(ValueError):` matches neither alternative and
`is_assertion_line` returns `False` for it.

**How much is invisible.** Measured 2026-09-19 across this repository's test
trees: **227** occurrences of `pytest.raises` or `pytest.warns`, spread over
more than twenty files, including every compartment rejection test the
simulator's guards are held by. Deleting the whole of one - the body as well as
the `with` line - removes the only assertion in that test and the check reports
none removed.

**Why it matters.** The check is one of the four integrity checks `verify
--self` will not relax, which is what makes a clean run mean something. Its
blind spot is not a random one: `pytest.raises` is how this project asserts that
an invalid input is *rejected*, so the assertions it cannot see are
disproportionately the safety guards. A delegated or self-audited diff can
delete one and pass the audit that exists to notice.

**Not the same finding as `PL-7TYC`, which narrowed the matcher the other way.**
That item removed false positives - prose and definitions read as assertions -
and its `is_assertion_line` is what this item extends. `PL-K1WS` is the third
mode: an assertion rewritten in place, reported as removed. All three are one
check being wrong about what an assertion is, which is why they share
`feature: verify-assertion-check`.

**Done when.** A removed `with pytest.raises(...)` or `with pytest.warns(...)`
line in a `.py` file is reported as an assertion removed, prose containing those
words is still not, and `subprojects/docket/tests/test_verify.py` drives both
directions.
