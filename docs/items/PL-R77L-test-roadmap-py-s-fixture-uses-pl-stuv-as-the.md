---
id: PL-R77L
title: test_roadmap.py's fixture uses PL-STUV as the id a section mentions in prose, but U is outside ID_ALPHABET so it is not an id at all and two assertions pass for the wrong reason
priority: P2
effort: S
status: ready
classes: defect, test
touches: subprojects/docket/tests/test_roadmap.py
added: 2026-09-19
verify: ! grep -q 'PL-STUV' subprojects/docket/tests/test_roadmap.py
---

**Problem.** test_roadmap.py's fixture uses PL-STUV as the id a section mentions in prose, but U is outside ID_ALPHABET so it is not an id at all and two assertions pass for the wrong reason

**Confirmed against the tree at triage, 2026-09-19.** `ID_ALPHABET` in
`subprojects/docket/src/docket/store.py:31` is
`"0123456789BCDFGHJKLMNPQRSTVWXYZ"` - the vowels are excluded - so `U` is not in
it and `ID_PATTERN` cannot match `PL-STUV`. The fixture still uses that string as
the prose mention an entry excludes
(`subprojects/docket/tests/test_roadmap.py:105`), and
`test_an_id_named_for_exclusion_or_for_reference_is_placed_nowhere` still asserts
on it at lines 508-509:

```python
assert not placed & {"PL-VWXY", "PL-STUV", "PL-Z7LY"}
assert scope.placement("PL-STUV") == UNPLACED
```

**Why it matters.** Both assertions pass, and neither tests what the test is named
for. `PL-STUV` is missing from `placed` because the parser never saw an id there
at all, not because a prose mention is correctly refused placement; its placement
is `UNPLACED` for the same reason. So the case that test's own docstring singles
out - an id mentioned inside another entry, the shape that "would survive a rule
that read the section's lists and skipped its prose" - is covered by nothing. The
placement rule could be rewritten to place prose mentions and this test would stay
green. `PL-VWXY` and `PL-Z7LY` are valid ids and do carry the assertion, which is
what hides the gap: the line is doing real work for two of its three members.

**Not `PL-2DTK`**, which corrected this same fixture id elsewhere in the file - it
is `PL-RSTW` at lines 625 and 672-673 - and records the audit arithmetic that the
correction tripped. The two occurrences at 105 and 508-509 were not reached.

**Done when.** The prose mention and both assertions use an id inside
`ID_ALPHABET`, and the test goes red when the placement rule is changed to place a
prose mention - proved by making that change locally and watching it fail, not by
inspection.
