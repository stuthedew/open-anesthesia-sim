---
id: PL-N4FP
title: tools/fact_home_check.py refuses a constant defined twice and a git or GitHub reader outside its home but no predicate written inline, so three filings since PL-4S6C closed spent (PL-Q80R, PL-TSXD, PL-JT7Y) respell a fact that one module owns
priority: P1
effort: M
status: ready
classes: defect
feature: one-source-of-truth
touches: tools/fact_home_check.py, tests/unit/test_fact_home_check.py, CLAUDE.md, .claude/rules/apparatus-standard.md
added: 2026-10-24
payoff: a hand test of an item's status set or of a pr: number fails make check, so the next copy of Item.is_open or model.pr_number is refused instead of filed
verify: grep -q 'def test_a_status_set_tested_by_hand_outside_model_is_refused' tests/unit/test_fact_home_check.py && grep -q 'def test_a_pr_field_read_by_hand_is_refused' tests/unit/test_fact_home_check.py
root-cause-of: PL-Q80R, PL-TSXD, PL-JT7Y
generator: live - three filings since PL-4S6C closed spent on 2026-10-12 (PL-Q80R, PL-TSXD, PL-JT7Y) respell a fact one module owns in a form tools/fact_home_check.py has no rule for, so its baseline cannot hold them and make check passes each
misread: Which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it
reenters: PL-5DZ8, PL-4S6C
---

**Problem.** tools/fact_home_check.py refuses a constant defined twice and a git or GitHub reader outside its home but no predicate written inline, so three filings since PL-4S6C closed spent (PL-Q80R, PL-TSXD, PL-JT7Y) respell a fact that one module owns

**The record, read 2026-10-24 at 3f1e5913.** `bin/docket inflow` lists
`PL-5DZ8` as re-entered by three filings: `PL-4S6C`, `PL-Q80R` and `PL-TSXD`.
It names `PL-4S6C` as the line's successor head. `PL-4S6C` closed `spent` on
2026-10-12 on the ground that `tools/fact_home_check.py` refuses a copy. Its
own verdict said that a member the check cannot see "is evidence for a new
head rather than this one". Three such members have been filed since:

- `PL-Q80R` (filed 2026-10-12, after `#1445` merged, closed by `#1546`):
  `release.code_spans` and `doc_check`'s `_InlineReader` each scanned code
  spans, and read an autolink differently.
- `PL-TSXD` (filed 2026-10-19): about 44 lines test an item's status against
  `OPEN_STATUSES` or `CLOSED_STATUSES` by hand instead of reading
  `Item.is_open`.
- `PL-JT7Y` (filed 2026-10-19): `verify.py` and `cli.py` read a pull request
  number with their own regexes and `isdigit()` instead of `model.pr_number`.
  That is the reading `PL-4DK2` replaced in `vcs` and `tools/pr_body_check.py`
  on 2026-10-18.

All three misread the fact the three earlier heads state: which spelling of a
repeated predicate is the answer.

**Why it matters.** The check names primitives (git, a tree walk, the GitHub
API, the default branch, a shell lexer) and constants defined in two files. A
predicate written inline over a constant that one module owns is neither, so
the check passes it. A membership test of `CLOSED_STATUSES` imports the set
from its home and still answers "is this item open?" by hand. Each copy then
costs an item, and a fourth head on this fact would be the fourth time a
`spent` verdict did not hold.

**Done when.** `tools/fact_home_check.py` refuses, with an empty baseline, a
membership test against `OPEN_STATUSES` or `CLOSED_STATUSES` outside
`docket/model.py`, and the hand forms of reading a pull request number that a
check can decide. Each owned predicate is one table entry. A regression test
shows one refused site and one accepted site for each fact. Where a form
cannot be decided by a check, this brief says why. `PL-TSXD` and `PL-JT7Y`
drain the sites, and `generator:` then names the check as what refuses the
next copy.

**Generator check.** This is the head: three filings re-enter the fact that
`PL-5DZ8`'s and `PL-4S6C`'s `misread:` state, after `PL-4S6C`'s fix, so it is
recorded as a generator whose fix did not hold, with `reenters:` naming both.
