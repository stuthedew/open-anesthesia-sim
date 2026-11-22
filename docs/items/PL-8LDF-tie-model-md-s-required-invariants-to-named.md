---
id: PL-8LDF
title: Tie MODEL.md's required invariants to named tests and check the names resolve
priority: P2
effort: M
status: done
classes: docs, test
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tools/doc_check.py
added: 2026-08-25
closed: 2026-11-22
pr: 2248
tests: tests/integration/controller/test_controller_running.py::test_pause_stops_simulated_time_and_the_stored_state
---

> **Groomed 2026-09-22 (`PL-Y4YG`): still owed; the re-scope below holds.** §
> "Required invariants" carries 21 bullets now (eighteen when this was filed),
> none yet naming a test. `PL-036` closed on 2026-09-22 with `BOUND_FAMILIES`
> holding the hazard table and the minimum displayed outputs, and the comment
> above it names this item and `PL-2M9N` as the two passes still due. The
> family entry this pass adds is a `tools/doc_check.py` edit, so `touches` now
> names that file beside `docs/MODEL.md`.

**Problem.** `docs/VERIFICATION.md`'s eighteen "Required invariants" state what the
implementation must preserve, with nothing connecting each to the test that
holds it.

**Why it matters.** They are the model's safety spine. Annotating each with
its test answers "how do I know this holds?" for a future reviewer, and makes
a deleted or renamed test detectable rather than silent.

**Where.** `docs/VERIFICATION.md` § "Required invariants", `tools/doc_check.py`.

**Notes.** Raised while deciding PL-036. The check is the cheap half — the
same shape as the existing citation checks, finding `def test_...` across
`tests/` by reading files, no import needed — and it would report something
true and useful: every invariant names a test that exists. The work is the
annotation pass: eighteen judgments, some of which will have no single answer
and will need a test written or an honest "not directly tested" marker. As
with the provenance check, this validates linkage and claims nothing about
whether the test is any good.

**Done when.** Each invariant names its test, and `doc_check.py` fails when a
named test does not resolve.

**Re-scoped 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
This is the annotation pass for `docs/VERIFICATION.md` § "Required invariants" under
clause 2: every bullet gains a code-spanned test name, or the declared-none
form naming an open item, and the family joins `BOUND_FAMILIES` in
`tools/doc_check.py` as the pass lands. The check half is already built -
`check_named_tests` resolves the names and `check_bound_families` holds the
list complete - so what is left here is the lookup rather than a
test-writing project. Reading every invariant and required test against the
suite on 2026-09-19 found 36 of 38 held by a test whose body asserts the
statement directly, 2 held in part and none unheld, so the declared-none form
is expected to be needed nowhere.

**Checked 2026-11-22** against `d4e8200`: still applies. `docs/VERIFICATION.md` § "Required invariants" has 21 bullets and none names a test. `BOUND_FAMILIES` in `tools/doc_check.py` lists the hazard table, § "Minimum displayed outputs" and § "Required tests", but not § "Required invariants". `PL-6PPZ` (the move of the six verification sections to a new document) moves this section and is in flight, so the annotation pass should land after it and edit the new document.

**Closed 2026-11-22.** Each of the 21 entries of `docs/VERIFICATION.md` § "Required invariants" names the tests that hold it, and the section joins `BOUND_FAMILIES` in `tools/doc_check.py` as a list family of tests. Every named test was read before it was named, and each asserts its entry directly. One entry had no test that did: `test_pause_blocks_advancement` checks a run that never started, so a pause that still stepped a running run would pass it. `test_pause_stops_simulated_time_and_the_stored_state` now starts a run, pauses it after ten steps and asks for ten more. Wrong claims found: none. Files checked for statements this changed: `docs/VERIFICATION.md` § "What the documentation check confirms, and what only a review finds" (it said the invariants were not yet checked, and is corrected), `docs/ARCHITECTURE.md`, `docs/apparatus.md` and `README.md` (no mention).
