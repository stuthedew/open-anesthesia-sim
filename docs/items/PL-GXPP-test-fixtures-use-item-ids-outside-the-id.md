---
id: PL-GXPP
title: Test fixtures use item ids outside the id alphabet, so a test routing one through id-aware machinery silently exercises nothing
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_roadmap.py
added: 2026-09-02
verify: uv run pytest subprojects/docket/tests --collect-only -q && ! grep -qE 'PL-[A-Z0-9]*[AEIOU]' subprojects/docket/tests/*.py
recurrences: 2026-09-19 PL-R77L
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

**On the `verify:` command.** The grep is the specification, not a proxy for
one: the alphabet excludes the vowels, so a vowel between `PL-` and the end of
an id is exactly the condition, and it lists the six offenders today with no
false positive - `PL-1`, `PL-B1B`, `PL-M0` and `PL-M01` carry none. It is
paired with `--collect-only` rather than a run because a rename breaks
collection, which that catches in 0.5 s, while running the three files takes
30 s inside every `make check` - the cost `PL-LXR3` was explicitly reasoned out
of and `PL-PRHN` records. The suite itself is already gated: `make check` runs
`uv run pytest` in full two steps earlier.

**Done when.** No test fixture that is meant to read as a valid item id fails
`store.ID_RE`, and the deliberately-invalid ones are still there.

**`PL-R77L` is this same finding and is dropped in its favour** (`PL-JKML`'s
duplicate sweep, 2026-09-20, confirmed on independent refutation against the
tree). This item named the literal `PL-STUV` in `test_roadmap.py` among its
offenders on 2026-09-02, seventeen days before `PL-R77L` re-found the same
fixture string at the same location with line numbers.

**Containment here is mechanical rather than argued.** `ID_ALPHABET` at
`subprojects/docket/src/docket/store.py:31` is
`0123456789BCDFGHJKLMNPQRSTVWXYZ` - vowels excluded - so `PL-STUV` is an id the
store could never mint. This item's `verify:` grep for `PL-[A-Z0-9]*[AEIOU]`
over `subprojects/docket/tests/*.py` matches `PL-STUV`, so **no tree state
satisfies this item's command while `PL-R77L`'s `! grep -q PL-STUV` still
fails**. One cannot be finished without the other.

**Two things from `PL-R77L` carried here.** Its occurrences, so whoever takes
this does not re-find them: `subprojects/docket/tests/test_roadmap.py:105` (a
prose mention inside a frozen-list entry) and `:508-509` (the two assertions in
`test_an_id_named_for_exclusion_or_for_reference_is_placed_nowhere`). And its
stronger acceptance method: renaming to an in-alphabet id turns
`scope.placement(...) == UNPLACED` into a real assertion by construction - if
the placement rule did place prose mentions, the renamed test goes red and
`make check` blocks the branch. That is a mutation-proof bar for the rename,
and it is the one to meet.

**Not superseded by `PL-2DTK`**: it corrected the same fixture id to `PL-RSTW`
at `:625` and `:672-673` on the `PL-HWW1` branch and records that `:105` and
`:508-509` were not reached, so both items are live on the occurrences that
remain.
