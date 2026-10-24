---
id: PL-N4FP
title: tools/fact_home_check.py refuses a constant defined twice and a git or GitHub reader outside its home but no predicate written inline, so three filings since PL-4S6C closed spent (PL-Q80R, PL-TSXD, PL-JT7Y) respell a fact that one module owns
priority: P1
effort: M
status: done
classes: defect
feature: one-source-of-truth
touches: tools/fact_home_check.py, tests/unit/test_fact_home_check.py, CLAUDE.md, .claude/rules/apparatus-standard.md
added: 2026-10-24
closed: 2026-10-24
pr: 1738
payoff: a hand test of an item's status set or of a pr: number fails make check, so the next copy of Item.is_open or model.pr_number is refused instead of filed
verify: grep -q 'def test_a_status_set_tested_by_hand_outside_model_is_refused' tests/unit/test_fact_home_check.py && grep -q 'def test_a_pr_field_read_by_hand_is_refused' tests/unit/test_fact_home_check.py
root-cause-of: PL-Q80R, PL-TSXD, PL-JT7Y
generator: spent - tools/fact_home_check.py's third rule refuses, with an empty baseline, a membership test of OPEN_STATUSES or CLOSED_STATUSES outside docket.model and an isdigit, int or pattern match of the pr field, one PREDICATES entry each, so the next copy of either fails make check instead of becoming a member; a second scanner of one grammar, as PL-Q80R was, has no form a check can name and stays the resident bullet's judgment half
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

**Built 2026-10-24.** `tools/fact_home_check.py` has a third rule, with an
empty baseline. Its table, `PREDICATES`, has one entry per owned predicate,
and both entries name `docket/model.py` as the home:

- `item-status` refuses `in` or `not in` against `OPEN_STATUSES` or
  `CLOSED_STATUSES`. That covers a bare name, a module attribute, a set or
  list display that unpacks one (`{"", *CLOSED_STATUSES}`), and a sum that
  adds to one. On the base tree (3f1e5913) it found 48 sites outside
  `model.py`, which `PL-TSXD` replaced.
- `pr-number` refuses `isdigit()`, `isdecimal()`, `isnumeric()`, `int()` or a
  pattern's `match`, `fullmatch` or `search` applied to the `pr` field itself:
  `x.pr`, `x["pr"]` or `x.get("pr", ...)`, read through any `strip`-like
  trim. This is the form `PL-4DK2` removed from `vcs` and
  `tools/pr_body_check.py` on 2026-10-18. On the base tree it found none.

`tests/unit/test_fact_home_check.py` has a refused case and an accepted case
for each fact.

**Not decidable, and so not refused.** None of the nine readers that `PL-JT7Y`
replaced applied a test to the `pr` field itself. Each read digits from
somewhere else: a front-matter pair keyed `pr`, a record's file name, a forge
command's output, a commit subject, the `PR_NUMBER` variable or a
`refs/pull/N/head` ref. Whether those digits are a pull request number is
decided by where they were read, and the syntax of the test does not show it.
`isdigit()` and a pattern of digits also read counts, line numbers and
versions at about 15 other apparatus sites. A rule keyed on the test
would refuse those, and a rule keyed on a variable name would be a guess. So
those sources reach `model.pr_number` by review, and the module docstring
says so.

**A checked type was weighed and not built.** A `PullRequestNumber` type that
only `pr_number` produces would let mypy refuse a hand-parsed number where it
reaches a typed structure such as `NewestPullRequest` or
`SubjectPullRequest`. It would still miss a yes-or-no test like
`PR_VALUE_RE.fullmatch`, which produces no number, and it means retyping each
structure that holds a pull request number and every test that builds one.
That is more than these two facts need, so it is filed as its own item.
