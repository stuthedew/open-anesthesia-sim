---
id: PL-K1WS
title: verify's 'no existing assertion removed' check never asks whether a replacement exists, so any function-signature change REJECTs for every call site it updates in place
priority: P2
effort: S
status: done
classes: defect, infra
feature: verify-assertion-check
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
added: 2026-09-17
closed: 2026-09-19
verify: grep -q 'def test_an_assertion_rewritten_in_place_is_not_reported_as_removed' subprojects/docket/tests/test_verify.py
---

**Problem.** verify's 'no existing assertion removed' check never asks whether a replacement exists, so any function-signature change REJECTs for every call site it updates in place

`verify.py` collects removed lines containing `assert` and reports them. It
never asks whether the same assertion appears among the *added* lines, so an
assertion edited in place is indistinguishable from one deleted. Adding a
parameter to a function that tests call inside an `assert` therefore fails the
check once per call site, on a diff that removed no coverage at all.

**Found 2026-09-17** on `PL-MN4J`'s close-out. `format_trace_hover` and
`format_wash_in_hover` gained a required `run_count` parameter, so all 11
existing call sites were updated; `bin/docket verify --self PL-MN4J` returned
`REJECT` on `no existing assertion removed - 11 line(s)`, with `make check` and
the item's own `verify:` command both passing. Every one of the 11 removed lines
had a replacement differing only by the appended argument, confirmed by
normalising the added lines and matching: 11 removed, 0 unmatched.

**Why the existing exemptions do not cover it.** `falsifies:` names an
assertion the work makes *untrue* - a string the item was asked to delete. Here
nothing was made untrue and nothing was deleted; the assertions were rewritten
to the new signature and still assert exactly what they did. And because both
exemptions are read from the base's copy of the item, a session cannot declare
one for the work in hand, correctly. So there is no honest way to clear this
today except the project owner reading the diff.

**Not a reason to default the parameter.** The obvious way to avoid the churn -
give `run_count` a default of 1 - would mean a caller that forgot it produced a
hover naming no run on a two-run chart, silently. That is the failure `PL-MN4J`
exists to remove, and `CLAUDE.md`'s safety-critical standard refuses a default
that could produce a plausible but incorrect clinical value. The check should
learn the pattern rather than the code avoiding a required parameter.

**Why it matters.** The four integrity checks are the part of `verify --self` a
session may not relax, so a `REJECT` from one is meant to stop the close-out.
This one fires on a diff that removed no coverage, and it fires once per call
site, so the correct response to it is to read eleven lines and talk past the
check - which is exactly how a session is trained to skim the block where a real
removal would be printed. It also has no honest clearing route: both exemptions
are read from the base's copy of the item, correctly, so the only way past it
today is the project owner reading the diff.

**Done when.** A removed `assert` line whose normalised form appears among the
diff's added lines is not reported as an assertion removed, a genuinely removed
assertion still is, and `subprojects/docket/tests/test_verify.py` drives both
directions - including the signature-change shape that `PL-MN4J` hit, where the
replacement differs only by an appended argument.

**A third mode of the same defect.** `PL-L40Z` is the check reading Markdown
prose containing the word "assert"; `PL-QJQL` is it failing to see
`pytest.raises` blocks. All three are one check being wrong about what an
assertion is, and the three belong under one `feature:` - `PL-L40Z` is edited on
`origin/claude/blissful-edison-mafspv`, so whoever lands that branch is the
cheapest place to group them.

**Where.** `subprojects/docket/src/docket/verify.py:886`.

**A cheap fix exists.** Match each removed assertion against the added lines
after normalising whitespace and argument lists, and report only those with no
counterpart - the same comparison this item's own diff was audited by hand with.
