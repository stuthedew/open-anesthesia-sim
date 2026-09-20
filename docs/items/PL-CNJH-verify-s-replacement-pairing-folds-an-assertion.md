---
id: PL-CNJH
title: verify's replacement pairing folds an assertion whose inserted argument loosens it - approx(2.05) to approx(2.05, rel=0.5) - reporting the pair without refusing it; 4 of the 56 it folds across 905 commits change what the line asserts
priority: P2
effort: M
status: blocked
classes: defect
feature: verify-assertion-check
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
blocked-by: PL-4W2L
added: 2026-09-19
verify: grep -q 'def test_a_replacement_that_loosens_the_assertion_is_not_folded_away' subprojects/docket/tests/test_verify.py
---

**Problem.** verify's replacement pairing folds an assertion whose inserted argument loosens it - approx(2.05) to approx(2.05, rel=0.5) - reporting the pair without refusing it; 4 of the 56 it folds across 905 commits change what the line asserts

**Why it matters.** This is the assertion check failing in the one direction that
leaves no trace. A false `REJECT` is loud and gets argued with; a false fold is
silent, and what it folds away is exactly the edit the check exists to catch - an
assertion whose replacement still passes because it now asserts less.
`approx(2.05)` to `approx(2.05, rel=0.5)` is the whole shape: same line, same
symbol, same test name, and a 50% tolerance where there was none. The audit prints
the pair and accepts the branch, so a reader who has been shown `ACCEPT` has been
told the coverage held when it did not.

The 4-of-56 measurement across 905 commits is what makes it worth fixing rather
than noting: the pairing is right about 52 of them, so it cannot simply be
removed, and it is wrong often enough that the silence is load-bearing.

**Where.** The replacement pairing in `subprojects/docket/src/docket/verify.py`,
and `subprojects/docket/tests/test_verify.py` for the case.

**Done when.** A replacement that inserts an argument weakening what the line
asserts - a tolerance, a widened bound, a negation - is separated from one that
merely restates the assertion: refused outright if the separation is exact, and
otherwise reported under its own heading so a reader of `ACCEPT` is told which
pairs were folded on a changed assertion. A test drives the `approx(2.05)` to
`approx(2.05, rel=0.5)` case. Reporting is always available, so "leave it folded
and say why" is not one of the endings here - the 52 correct folds are the reason
to keep the pairing, not a reason to keep it silent.

**Not `PL-2DTK`**, which is the same check refusing a removal its item did not
make. That one is a false `REJECT` and this is a false `ACCEPT` - opposite
failures of one mechanism, and only this one is silent.
