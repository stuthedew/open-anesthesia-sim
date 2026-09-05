---
id: PL-R6D8
title: git log --source does not attribute a shared commit to the ref named first, and _unmerged_commits' docstring says it does
priority: P3
effort: S
status: ready
classes: defect, docs
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-04
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_flight_names_the_local_branch_where_the_checkout_holds_both' subprojects/docket/tests/test_vcs.py
---

**Problem.** `_unmerged_commits` passes refs to `git log --source` in candidate
order and its docstring states the consequence as a guarantee: "Refs are passed
in the order they will be reported in, so a commit two refs share - a local
branch and its own tracking ref - is attributed to the one that will be named."

Git does not promise that, and measured on this repository it does not do it.
On 2026-09-04, with `claude/next-workflow-item-knjkkt` and its tracking ref
holding identical history, one walk credited the branch's newest `PL-YHD3`
commit to the local ref and its oldest to `origin/...`. Attribution varies per
commit within a single walk.

**Why it matters.** `branches_in_flight` survives it, because it needs only
*some* ref per id - which is why this has never shown as a bug. What it costs
is smaller and real: `flight` and `triage` print whichever ref the walk
happened to credit, so a session can be shown `origin/claude/...` for work its
own local branch is carrying, which is the exact confusion those lines exist to
remove. And a false guarantee in a docstring is worse than none, because the
next reader builds on it: `PL-YHD3`'s `precedence` did, found the split in
testing, and had to identify a claim by its commit and match `HEAD` by
containment instead.

**Where.** `subprojects/docket/src/docket/vcs.py` - `_unmerged_commits`'s
docstring, and the ref-naming half of `branches_in_flight`.

**Done when.** The docstring says what git actually guarantees, and `flight`
names a local branch rather than its tracking ref where the checkout holds
both - or records why that is not worth buying.
