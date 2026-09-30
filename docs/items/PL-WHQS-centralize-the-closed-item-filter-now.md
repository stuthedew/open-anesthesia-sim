---
id: PL-WHQS
title: Centralize the closed-item filter now duplicated across twelve call sites
priority: P3
effort: S
status: done
classes: refactor
feature: docket-store
touches: subprojects/docket, tools
added: 2026-09-13
closed: 2026-09-30
pr: 1243
verify: ! grep -rqF --exclude=model.py '"done", "dropped"' subprojects/docket/src tools && grep -qF 'CLOSED_STATUSES' tools/item_reads.py
---

**Problem.** Centralize the closed-item filter now duplicated across twelve call sites
**Why it matters.** `CLOSED_STATUSES = ("done", "dropped")` is defined once in
`subprojects/docket/src/docket/model.py` and honoured by most of its readers -
and then written out again at four sites: twice as a bare tuple in
`subprojects/docket/src/docket/checks.py` (`_check_item`'s missing-`closed:`
error, and the `resolved` set `_groom` reads its blocker advisories from), as a
frozenset of its own, `CLOSED_ITEM_STATUSES`, in `tools/doc_check.py`, which
imports `CLOSED_STATUSES` for another check in the same file, and in a
line-prefix spelling as `CLOSED = ("status: done", "status: dropped")` in
`tools/item_reads.py`. The capture's "twelve call sites" is the count of
readers, not of duplicated literals, and the literals are what matter. A
terminal status added or renamed would be honoured by some commands and not
others, and the ones that missed it would keep answering - a closed item still
counted open, with nothing failing. That is the failure the constant exists to
prevent, and it is halfway defeated already.

Re-confirmed 2026-09-30, on starting it. Counted 2026-09-13, the brief placed
the two `checks.py` literals by line number, and both numbers had moved; it
named no `doc_check.py` copy, because `CLOSED_ITEM_STATUSES` arrived after the
capture (`PL-G424`, 2026-09-19). Test fixtures that write `done` and `dropped`
as inputs are not closed-status tests and stay written out: an input derived
from the constant under test passes whatever the constant says.

**Done when.** Every closed-status test in `subprojects/docket/src/` and
`tools/` reads `CLOSED_STATUSES` from `docket.model`; `tools/item_reads.py`'s
line-prefix form is derived from it rather than written out; and no
`"done", "dropped"` pair remains in either outside the definition, in any
spelling.
