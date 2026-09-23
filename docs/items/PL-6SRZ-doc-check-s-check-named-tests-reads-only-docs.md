---
id: PL-6SRZ
title: doc_check's check_named_tests reads only docs/MODEL.md and its regex cannot match a backticked name broken across a line, so a dead test name in WORKING_NOTES.md or ARCHITECTURE.md is unreported and a wrapped one is unreported anywhere
priority: P3
effort: S
status: ready
classes: defect, infra
feature: doc-consistency-checks
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-2JRC's triage pass
added: 2026-09-21
payoff: make check's claim that documentation citations resolve becomes true for test names outside docs/MODEL.md, and a backticked name broken by a line wrap stops being invisible to the check everywhere.
verify: grep -q 'def test_a_test_name_cited_in_working_notes_is_resolved' tests/unit/test_doc_check.py
---

**Problem.** doc_check's check_named_tests reads only docs/MODEL.md and its regex cannot match a backticked name broken across a line, so a dead test name in WORKING_NOTES.md or ARCHITECTURE.md is unreported and a wrapped one is unreported anywhere

**Notes.** Found 2026-09-21 while closing `PL-DL4M`, which deleted a
`docs/WORKING_NOTES.md` section citing two test functions that no longer
exist. Neither was reported by anything. Two distinct gaps in
`tools/doc_check.py`'s `check_named_tests`, one live and one latent:

1. **Scope.** The function reads `MODEL` and nothing else - its own docstring
   says so, and the exclusion was deliberate: measured 2026-09-13, 161 test
   names were cited tree-wide, 21 resolved to nothing and all 21 sat in
   `docs/items/`, where a name is a forward reference to work not yet done.
   That reasoning is still right about `docs/items/`. What it did not
   anticipate is `PL-G424`'s citation-drift rule, adopted six days later on
   2026-09-19, whose fourth clause makes the *symbol* the mandated citation
   anchor across `docs/items/**`, `docs/WORKING_NOTES.md` and
   `.claude/skills/**` precisely because a symbol is greppable. The rule moved
   every citation onto an anchor nothing verifies, from one - a line number
   past its file's end - that `check_line_citations` does verify.
   `test_a_growing_run_does_not_grow_the_traffic_it_sends` sat dead in
   `docs/WORKING_NOTES.md` on one unbroken line and would have been caught by
   the existing regex had the file been in scope.

2. **The regex, inside its own declared scope.** `NAMED_TEST_RE` is
   ``` `(test_[A-Za-z0-9_]+)` ```, which cannot match a backticked name broken
   across a line. This repository wraps prose at about 76 columns and names
   its tests as sentences, so the longest names - the ones most worth citing -
   are systematically the ones a wrap breaks. The deleted section held the
   worked example: ``test_chart_payload_is_bounded_`` / ``however_long_the_run``
   across two lines, invisible to the check even in `docs/MODEL.md`.

**Measured before recommending, and the count says file rather than
interrupt.** The question is what widening the scope would be worth, so it was
counted rather than argued. Against 3,273 defined test functions, after
`PL-DL4M`'s deletion:

| Document | Cited | Dangling |
| --- | --- | --- |
| `docs/MODEL.md` | 64 | 0 |
| `ROADMAP.md` | 4 | 0 |
| `docs/ARCHITECTURE.md` | 1 | 0 |
| `docs/WORKING_NOTES.md` | 1 | 0 |
| `docs/items/` | 286 | 46, excluded by design |

So widening guards **six** citations outside `docs/MODEL.md` and would have
fired **once** in the tree's history as it stands - today, on the name
`PL-DL4M` deleted. That does not meet `CLAUDE.md`'s test for friction
recommended on sight, and it is recorded here rather than raised. Gap 2 has
**zero** live instances today; it is latent, and it is named here rather than
filed separately because the fix is the same function.

**Done when.** `check_named_tests` resolves cited test names in the standing
documents as well as in `docs/MODEL.md` - `docs/WORKING_NOTES.md`,
`docs/ARCHITECTURE.md` and `ROADMAP.md` are the candidates, and `docs/items/`
stays excluded for the reason its docstring already gives - and its regex
matches a backticked name a line wrap has broken. A test pins both, including
that a name cited in `docs/items/` is still not reported.

**Why it matters.** `make check` prints that "the citations in the
documentation, the queue and the source docstrings all resolve", which reads
wider than what is checked for test names. A reader takes the sentence at face
value; for a test name outside `docs/MODEL.md` the guarantee is void. That is
the silently-wrong-answer shape, at a small enough scale that the count above
is what decides its rank rather than the shape alone.
