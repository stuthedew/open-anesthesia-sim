---
id: PL-PB8V
title: vcs.BRANCH_ID_RE spells the item-id grammar a second time, in lower case, and tools/fixture_id_check.py cannot see it because its grammar rule matches PL- case-sensitively
priority: P3
effort: S
status: ready
classes: defect
feature: dev-tooling
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, tools/fixture_id_check.py, tests/unit/test_fixture_id_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: a change to the item-id alphabet can no longer leave branch-name attribution matching the old one, and the check that refuses second spellings of the grammar sees a lower-cased one
verify: ! grep -q 'bcdfghjklmnpqrstvwxyz' subprojects/docket/src/docket/vcs.py && grep -q 'def test_the_branch_id_pattern_is_the_stores_grammar' subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_lower_cased_restatement_is_refused' tests/unit/test_fixture_id_check.py
---

**Problem.** vcs.BRANCH_ID_RE spells the item-id grammar a second time, in lower case, and tools/fixture_id_check.py cannot see it because its grammar rule matches PL- case-sensitively

**Reproduced 2026-09-26 against 718b42ee.** `subprojects/docket/src/docket/vcs.py`'s
`BRANCH_ID_RE` is written out by hand as
`pl-(?:\d{3}|[0-9bcdfghjklmnpqrstvwxyz]{4})` with `re.I`. It agrees with
`store.ID_ALPHABET` today (`store.ID_ALPHABET.lower()` equals the class), so
nothing is wrong yet. But `tools/fixture_id_check.py`'s `GRAMMAR_RE`, which
exists to refuse a second spelling of the grammar, does not match its pattern:
`GRAMMAR_RE.search(vcs.BRANCH_ID_RE.pattern)` returns `None`, because the
rule opens with a case-sensitive `PL-` and this copy is spelled `pl-`. It is the
only spelling of the alphabet in the package or tools outside `store.py`.

**Why it matters.** `PL-ZJ6X` (the head for "which strings are valid item ids")
closed as spent on the ground that `store` exports the grammar and the check
refuses any copy. This copy is the one it missed. If `ID_ALPHABET` or
`ID_LENGTH` ever changes, `store` and the check move together and branch-name
attribution does not: `claims.py`'s branch-name read and
`tools/branch_id_check.py` then silently stop recognizing the items a branch
is named for, and nothing errors. Found while re-confirming `PL-GVC0` (the
hard-coded `PL-` prefix), where this was the one part worth doing now.

**Where.** `vcs.BRANCH_ID_RE`, which should be built from `store.ID_PATTERN`
the way `ANY_ID_RE` beside it already is; and `GRAMMAR_RE` in
`tools/fixture_id_check.py`, which should match the prefix case-insensitively so
a lower-cased copy is refused like any other.

**Done when.** `BRANCH_ID_RE` embeds `store.ID_PATTERN` and matches exactly the
branch names it matched before, with a test pinning both; and
`fixture_id_check` refuses a lower-cased restatement, with a test.
