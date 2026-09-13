---
id: PL-WHQS
title: Centralize the closed-item filter now duplicated across twelve call sites
priority: P3
effort: S
status: ready
classes: refactor
feature: docket-store
touches: subprojects/docket, tools
added: 2026-09-13
verify: uv run pytest subprojects/docket/tests/test_checks.py && ! grep -q '"done", "dropped"' subprojects/docket/src/docket/checks.py
---

**Problem.** Centralize the closed-item filter now duplicated across twelve call sites
**Why it matters.** `CLOSED_STATUSES = ("done", "dropped")` is defined once in
`subprojects/docket/src/docket/model.py` and honoured by `vcs.py`,
`tools/pr_title_check.py` and `tools/doc_check.py` - and then written out again
as a bare literal in `subprojects/docket/src/docket/checks.py` at lines 419 and
1562, and in a third spelling as `CLOSED = ("status: done", "status: dropped")`
in `tools/item_reads.py`. Counted 2026-09-13; the capture's "twelve call sites"
is the count of readers, not of duplicated literals, and the literals are what
matter. A terminal status added or renamed would be honoured by some commands
and not others, and the ones that missed it would keep answering - a closed item
still counted open, with nothing failing. That is the failure the constant
exists to prevent, and it is halfway defeated already.

**Done when.** Every closed-status test in `subprojects/docket/` and `tools/`
reads `CLOSED_STATUSES` from `docket.model`; `tools/item_reads.py`'s
line-prefix form is derived from it rather than written out; and no bare
`("done", "dropped")` literal remains outside the definition.
