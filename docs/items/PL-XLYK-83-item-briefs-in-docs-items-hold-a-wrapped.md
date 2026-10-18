---
id: PL-XLYK
title: 83 item briefs in docs/items hold a wrapped clause that renders as a list item, which PL-LNNL's check skips because the item store was outside its measured scope; fix the open ones and decide whether the check reads the store
status: untriaged
feature: prose-renders-as-written
added: 2026-10-18
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
