---
id: PL-8LDF
title: Tie MODEL.md's required invariants to named tests and check the names resolve
priority: P2
effort: M
status: ready
classes: docs, test
feature: dev-tooling
touches: docs/MODEL.md
added: 2026-08-25
---

**Problem.** `docs/MODEL.md`'s eighteen "Required invariants" state what the
implementation must preserve, with nothing connecting each to the test that
holds it.

**Why it matters.** They are the model's safety spine. Annotating each with
its test answers "how do I know this holds?" for a future reviewer, and makes
a deleted or renamed test detectable rather than silent.

**Where.** `docs/MODEL.md` § "Required invariants", `tools/doc_check.py`.

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
This is the annotation pass for `docs/MODEL.md` § "Required invariants" under
clause 2: every bullet gains a code-spanned test name, or the declared-none
form naming an open item, and the family joins `BOUND_FAMILIES` in
`tools/doc_check.py` as the pass lands. The check half is already built -
`check_named_tests` resolves the names and `check_bound_families` holds the
list complete - so what is left here is the lookup rather than a
test-writing project. Reading every invariant and required test against the
suite on 2026-09-19 found 36 of 38 held by a test whose body asserts the
statement directly, 2 held in part and none unheld, so the declared-none form
is expected to be needed nowhere.
