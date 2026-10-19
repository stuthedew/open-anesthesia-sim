---
id: PL-XLYK
title: 83 item briefs in docs/items hold a wrapped clause that renders as a list item, which PL-LNNL's check skips because the item store was outside its measured scope; fix the open ones and decide whether the check reads the store
priority: P3
effort: S
status: done
classes: docs
feature: prose-renders-as-written
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-18 triage pass
added: 2026-10-18
closed: 2026-10-19
pr: 1629
payoff: a wrap that renders as a stray list item in an open brief fails make check where it is written
verify: grep -q 'def test_an_open_brief_with_a_wrapped_clause_is_refused_and_a_closed_one_passes' tests/unit/test_doc_check.py
---

**Problem.** 83 item briefs in docs/items hold a wrapped clause that renders as a list item, which PL-LNNL's check skips because the item store was outside its measured scope; fix the open ones and decide whether the check reads the store

**Measured 2026-10-18** while building `PL-LNNL`. `check_wrapped_list_items`
in `tools/doc_check.py` refuses a list item that a wrap opened mid-sentence:
the line above ends with no `.`, `:`, `!` or `?`, and either the paragraph
above runs over more than one line or the item opens with a lower-case letter.
Applied to `docs/items/`, the same rule finds 83 such items in 82 briefs. Six
of the briefs are open, two `blocked` and four `ready` (`PL-05M4`, `PL-2M9N`,
`PL-507K`, `PL-DHJ7`, `PL-GQWP`, `PL-KZ99`); the other 76 are closed.
Every one read on that day was a spaced dash that a wrap moved to a line start,
such as "... the handle under the pointer" over "- because the chain is ...".
The check skips the store because `PL-LNNL`'s brief measured its 31 intended
lists outside it, and refusing 83 briefs at once would have turned `make check`
red with no fix in the same change.

**Recommendation.** Fix the six open briefs by moving each dash to the end of
the line above. Then decide whether the check reads the store: a closed brief
is a record, and rewrapping 76 of them is churn for a page few readers open.
Reading only open items would catch each new wrap where a session writes it.

**Decided at triage, 2026-10-18.** The check reads open briefs and skips
closed ones. `.claude/rules/citation-drift.md` already decides that a closed
brief is a historical record rather than a live statement, so its prose is not
a finding. Rewrapping 76 closed briefs would change records for no reader. An
open brief is live, and it is where a session writes new prose.

**Why it matters.** A brief renders on GitHub, and a wrap that opens a list
item there splits a sentence in two. Sessions keep writing such wraps, because
nothing in the raw text shows them.

**Done when.** `check_wrapped_list_items` in `tools/doc_check.py` reads every
open brief in `docs/items/` and skips closed ones. The six open briefs it would
refuse are rewrapped. A test in `tests/unit/test_doc_check.py` pins that an
open brief is refused and a closed one passes.

**Generator check.** Not owed beyond `PL-LNNL`'s: this is the scope `PL-LNNL`
left out on purpose, filed with it, not a re-entry of a fix.

**Closed 2026-10-19.** `check_wrapped_list_items` now reads the open briefs
through `_live_item_briefs`, which takes each status from the store's own
parse, and still skips the closed ones. On that day six open briefs held such
a wrap: `PL-2M9N`, `PL-507K`, `PL-DHJ7`, `PL-GQWP`, `PL-KZ99` and `PL-ZWQS`.
`PL-05M4` no longer held one, and `PL-ZWQS` was a numbered marker (`1.`)
rather than a dash. Each marker was moved to the end of the line above. The
test that pinned a store brief as skipped now pins a closed one, since an open
brief is no longer skipped.
