---
id: PL-8LDF
title: Tie MODEL.md's required invariants to named tests and check the names resolve
status: untriaged
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
