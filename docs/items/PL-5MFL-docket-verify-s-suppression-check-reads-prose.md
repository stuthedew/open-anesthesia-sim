---
id: PL-5MFL
title: docket verify's suppression check reads prose as code, so every release cut REJECTs: the assertion check narrows to files Python executes and the suppression check beside it does not
priority: P2
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests
added: 2026-09-19
verify: grep -q "def test_suppression_ignores_prose" subprojects/docket/tests/test_verify.py
---

**Problem.** docket verify's suppression check reads prose as code, so every release cut REJECTs: the assertion check narrows to files Python executes and the suppression check beside it does not

**Found 2026-09-19 closing `PL-SW0D`**, the v0.4.30 cut, whose
`bin/docket verify --self PL-SW0D` came back `REJECT` on correct work.

**What fired.** `_SUPPRESSION_RE` in
`subprojects/docket/src/docket/verify.py` matches any added diff line
containing one of `SUPPRESSIONS` - `# type: ignore`, `typing.no_type_check`,
`xfail`, `pytest.skip`, `@skip` - word-anchored on the left. The line it
caught was `ROADMAP.md`'s version-table row for `v0.4.29`, which narrates
`PL-VHVJ` in prose: "stopped `verify`'s suppression list substring-matching
`xfail` out of pytest's `--maxfail`". That is a genuine word-boundary match on
`xfail`, so `PL-VHVJ`'s own anchoring fix does not reach it - the row quotes
the bare token, not only `--maxfail`.

The edit that "added" the line changed one table cell:
`| v0.4.29 | Completed / current baseline |` became `| v0.4.29 | Completed |`.
A whole-line diff has no way to see that, so the 3,000-character prose row
re-enters the diff as an addition.

**The fix is already written down beside the bug.** The sibling check takes
the path and uses it: `is_assertion_line(path, line)` returns `False` for
anything whose name does not end in `ASSERTION_BEARING_SUFFIX`, and the
comment on that constant says why - "Only a file Python executes can hold an
assertion, so a removed line from anything else is prose whatever words it
uses. This is the larger half of the narrowing by count: every close-out edits
its own item's `.md`, and every release edits `ROADMAP.md`". The suppression
check is one comprehension, `suppressed = [line.strip() for _, line in added
if _SUPPRESSION_RE.search(line)]`, which discards the path and matches the
line alone. Every clause of that reasoning holds for suppressions too - only a
file Python executes can suppress anything - and the narrowing was applied to
one of the two.

**Why it matters.** It recurs by construction rather than by accident. Every
release cut edits exactly one version-table row, the departing baseline's, to
drop the `current baseline` mark; those rows narrate the apparatus defects the
release fixed, and this project fixes defects in suppression handling often
enough that two of the five tokens already appear in them. So a correct
close-out audit ends `REJECT` on a release cut, which is the specific harm
`PL-69JZ` and `PL-7XTS` identified for the four commission checks: a `REJECT`
a reader learns to expect is a `REJECT` they stop reading, and the suppression
line is one of the four integrity checks that `--self` deliberately does *not*
relax.

Worked around on `PL-SW0D` by reporting it to the project owner rather than
declaring an exemption on the item, per the `docket` skill's rule that a
session may not write the declaration that excuses its own work.

**Done when.** The suppression comprehension reads the path the way
`is_assertion_line` already does, a regression test asserts that a
`ROADMAP.md` line containing `xfail` is not reported, and
`bin/docket verify --self` on a release cut that edits the departing
baseline's row returns `ACCEPT`.
