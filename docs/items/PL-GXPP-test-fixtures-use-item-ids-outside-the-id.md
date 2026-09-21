---
id: PL-GXPP
title: Test fixtures use item ids outside the id alphabet, so a test routing one through id-aware machinery silently exercises nothing
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.5.1
touches: subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_duplicates.py, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_notes.py, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/tests/test_store.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_verify.py
added: 2026-09-02
closed: 2026-09-21
pr: 855
verify: uv run pytest subprojects/docket/tests/test_store.py -q -k test_every_fixture_id_is_one_the_store_could_mint
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

## What it turned out to be (2026-09-21)

**Ten files, not three.** The `touches` this item was filed with named
`test_cli.py`, `test_verify.py` and `test_roadmap.py`; the offenders were in
those plus `test_checks.py`, `test_duplicates.py`, `test_model.py`,
`test_notes.py`, `test_plan.py`, `test_store.py` and `test_vcs.py` - 52
literals over 261 occurrences, against the six this item counted on
2026-09-02. `touches` is widened to what the work reached. The growth is the
argument for the deterministic half below: nineteen days of ordinary fixture
writing took it from six to 261, because nothing was saying no.

**The `verify:` grep is retired rather than kept**, on `CLAUDE.md`'s rule that
a check earns its place every run. It was a proxy for `ID_RE` and a strictly
weaker one: `ID_PATTERN` accepts four alphabet characters *or* three digits,
so length is half the rule and the grep reads none of it. `PL-CAP`,
`PL-OTHER` and `PL-RUN{n}` all fail `ID_RE` on length, and the grep caught
them only because they happened to carry a vowel as well. It is replaced by
`test_store.py::test_every_fixture_id_is_one_the_store_could_mint`, which
imports the real `ID_RE` rather than restating it, so the two cannot drift.

**The deterministic half was worth having, and the allowlist this item feared
is avoided by putting the marker inline.** A fixture malformed on purpose
carries `# not-an-id` on the line its literal opens; there are four, and each
sits where the reader already is. A list kept in the check could name a
literal the tree no longer holds and nothing would say so. Comments never
reach the tree and docstrings are dropped before the scan, so an id merely
discussed in prose - `PL-M01` is, three times - needs no marker at all.

**`PL-R77L`'s stronger bar was met and the evidence is recorded.** With the
placement rule mutated to admit prose heads as gate entries,
`scope.placement("PL-STVW")` returns `in-scope` and
`test_an_id_named_for_exclusion_or_for_reference_is_placed_nowhere` goes red;
under the same mutation the old `PL-STUV` returns `unplaced` and the test
stays green. That is the vacuity this item describes, measured rather than
argued: before the rename the assertion could not detect the defect it exists
to detect. `PL-R77L`'s own `! grep -q PL-STUV` is satisfied too.

**One workaround went with it.** Three tests in `test_cli.py` wrote
`UNTRIAGED.replace("PL-U1U1", "PL-N3W1")` under a comment explaining that
`UNTRIAGED`'s own id carried no id at all in a commit subject. `UNTRIAGED` now
carries `PL-V1V1` and the tests use it directly.

**Mapping, for anyone reading a blame.** `A` has no in-alphabet letter, so
`PL-AAAA` became `PL-8888` - digits sort before letters, which preserves every
ordering it had against `PL-BBBB`, `PL-CCCC` and `PL-ZZZZ`. `E` went to `G`,
`U` to `V`, `O` to `Q` where the doubled-letter shape mattered; word mnemonics
took their vowels' digit lookalikes (`PL-SLOW` to `PL-SL0W`); and the
three-character ones gained the fourth the pattern requires. The
deliberately-malformed `PL-1` and `PL-M0{number}` are untouched, as this item
asked.

## The close-out `REJECT`, and what was done about it

`bin/docket verify --self PL-GXPP` ends `REJECT` on one check: `no existing
assertion removed - 86 line(s), 78 differing by one string`. It is the shape
the close-out records as settled and expected - a rename is indistinguishable
in a diff from an expectation quietly dropped, and the tool refuses to guess
which added line replaced which removed one. `falsifies:` is deliberately not
added: the base's copy of this item reads `status: ready`, not
`needs-decision`, so a declaration written here would fold nothing and count
only as this session's own word for it.

What the tool will not guess is decidable anyway, and was decided rather than
asserted. Applying the rename map to each of the 86 removed assertion lines
and looking for the result among the added ones: **83 reappear with their ids
respelled, 3 reappear unchanged but for the `# not-an-id` marker, and 0 are
unaccounted for.** No assertion was deleted, and the suite went from 1,468 to
1,469 tests.

The other three commission checks report rather than refuse under `--self`, as
designed: the diff stayed inside `touches` (17 paths, the 3 captures and 3 `pr`
writes sanctioned), no protected path was touched, and the front-matter edit -
`closed`, `status`, `touches`, `verify` - is the `NOTE` a self-audit prints.
