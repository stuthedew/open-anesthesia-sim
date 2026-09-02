---
id: PL-GXPP
title: Test fixtures use item ids outside the id alphabet, so a test routing one through id-aware machinery silently exercises nothing
status: untriaged
touches: subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_roadmap.py
added: 2026-09-02
---

**Problem.** `store.ID_ALPHABET` is Crockford base32 *minus the vowels*, so
`PL-U1U1`, `PL-U2U2`, `PL-E1E1`, `PL-EEEE` and `PL-AAAA` in `test_cli.py`,
`PL-STUV` in `test_roadmap.py`, and most of `test_verify.py`'s mnemonic ids
(`PL-CAP`, `PL-DONE`, `PL-FAIL`, `PL-PASS`, `PL-SLOW`, and the rest) do not
match `ID_PATTERN` at all. `read_items` parses them anyway - it takes the `id`
field verbatim - so they work as fixtures right up to the moment one is fed to
something that applies the pattern.

**Why it matters.** Observed 2026-09-02 while doing `PL-PRHN`. A new test put
`UNTRIAGED`'s own `PL-U1U1` at the front of a branch commit subject and
asserted the resulting in-flight mark. `LEADING_IDS_RE` matched nothing, the
flight report came back empty, and the test failed against a correct
implementation - which is the *lucky* direction. The unlucky one is a test
whose assertion is satisfied by the silence: any test asserting that an id is
*absent* from a listing, excluded from `next`, or not recognised in prose
passes vacuously when the id could never have been recognised in the first
place. Nothing in the suite currently fails, so this is a trap rather than a
bug, and it costs a debugging round to whoever springs it.

The distinction that matters is intent, not validity: `PL-1`, `PL-B1B` and
`PL-M0` are deliberately malformed ids in tests that assert rejection, and
those are correct as they stand. The ones above are meant to be ordinary valid
ids and are not.

**Where.** `subprojects/docket/tests/test_cli.py`,
`subprojects/docket/tests/test_verify.py`,
`subprojects/docket/tests/test_roadmap.py`. The alphabet is
`subprojects/docket/src/docket/store.py:31`.

**Approach.** Rename the fixtures meant to be valid, leaving the
deliberately-malformed ones alone. Then consider whether the deterministic
half is worth having: a check that every `PL-`-prefixed literal in the test
tree either matches `ID_RE` or sits in a test whose name says it is invalid is
the kind of thing that answers identically every run - but it needs a way to
tell the two apart that is not a hand-maintained allowlist, and if that costs
more than the renames save, the renames alone are the answer.

**Done when.** No test fixture that is meant to read as a valid item id fails
`store.ID_RE`, and the deliberately-invalid ones are still there.
