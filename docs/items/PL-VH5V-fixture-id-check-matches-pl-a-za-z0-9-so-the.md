---
id: PL-VH5V
title: fixture_id_check matches PL-[A-Za-z0-9]+, so the prose 'Every PL-prefixed token' in .claude/ or a .py message is read as an id, while the placeholders PL-XXXX and PL-ZZZZ are accepted as valid
priority: P3
effort: S
status: ready
classes: defect
feature: exact-gates
touches: tools/fixture_id_check.py, tests/unit/test_fixture_id_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-25
payoff: a sentence under .claude/ or a Python message that writes the PL- prefix as a word stops failing make check, while a malformed id written there is still refused
verify: grep -q 'def test_the_prose_token_pl_prefixed_is_not_read_as_an_id' tests/unit/test_fixture_id_check.py
---

**Problem.** fixture_id_check matches PL-[A-Za-z0-9]+, so the prose 'Every PL-prefixed token' in .claude/ or a .py message is read as an id, while the placeholders PL-XXXX and PL-ZZZZ are accepted as valid

Reproduced both false refusals and both false passes. 42 `not-an-id` exemptions exist, 35 in tests - the exemption count is itself the cost of the loose pattern.

Re-confirmed 2026-09-25 against 46954a81, for half of it: `fixture_id_check.malformed('Every PL-prefixed token')` yields `PL-prefixed`, so that prose in `.claude/`, or in a Python string value outside a docstring, fails the check. **The other half is not a defect.** `PL-XXXX` and `PL-ZZZZ` match `store.ID_RE` - X and Z are in `store.ID_ALPHABET` - so they are ids the store could mint, and they are the very placeholders `PL-DPY6` put into `generator_check.py`'s printed example when `docket check` refused the vowel ones; refusing them would undo that fix. The check promises a literal `ID_PATTERN` can see, not one naming a real item.

**The original done-when would switch the check off** (corrected at triage, 2026-09-25). `CANDIDATE_RE` is loose on purpose: it finds what looks like an id and `ID_RE` judges it. Made `ID_PATTERN`, it finds only tokens that pass, and `malformed()` can never yield. Of the 35 markers in tests, 28 are in `tests/unit/test_fixture_id_check.py`, the check's own rejection fixtures, malformed on purpose; no marker outside tests marks prose, so the false refusal has not been met outside the fuzz harness. Writing the prefix as code, a backticked `PL-` before `-prefixed`, already passes.

[superseded 2026-09-26] Blocked on `PL-GPJ7`: whether this check's `.claude/` text scan can be an exact rule, or goes to an advisory, is the head's rule to set, and the fix here follows from it. The head set it in its Done-when and took this item as step 4 of its Split, so it is worked there.

**Generator check.** The fact misread is whether a `PL-` token is an attempted id, recognised by the prefix - `PL-GPJ7`'s `misread:`, and a member of it correctly for the false-refusal half only. The false-pass half misreads nothing: it is `PL-ZJ6X`'s grammar, applied as that head left it.

**Why it matters.** A hard gate that refuses a correct sentence is paid for in rewording by whoever meets it. Here that is rare so far: only the fuzz harness has written such prose.

**Done when.** The `.claude/` text scan meets the rule `PL-GPJ7` sets for hard gates, and a test holds the prose token `PL-prefixed` under that rule.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
