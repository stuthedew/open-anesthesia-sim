---
id: PL-615L
title: "Drop PL-W8NH as a duplicate of PL-ZM8P once #864 and #866 both land: both name check_quoted_sources holding closed briefs to current prose, PL-ZM8P is the one implemented"
priority: P3
effort: S
status: untriaged
classes: housekeeping
feature: dev-tooling
added: 2026-09-21
---

**Problem.** Two sessions found the same defect inside an hour on 2026-09-21
and recorded it twice. `PL-ZM8P` (in #866, implemented) and `PL-W8NH` (filed in
#864, untriaged) both say that `_quoting_sources` yields every
`docs/items/*.md` with no status filter, so `check_quoted_sources` holds a
closed brief to current prose against `.claude/rules/citation-drift.md`'s
ratified rule that such drift is not a finding.

Neither session could see the other: both items were filed on unmerged
branches, where `bin/docket stranded` reports them but `bin/docket next` does
not rank them.

**`PL-W8NH`'s `Done when` is satisfied clause-for-clause by `PL-ZM8P`**, which
is what makes this a duplicate rather than two items on one theme:

| `PL-W8NH` asks for | `PL-ZM8P` ships |
| --- | --- |
| `check_quoted_sources` skips `done`/`dropped` briefs | `_quoting_sources` yields `_live_item_briefs(root)` |
| a closed brief quoting absent text passes | `test_a_closed_brief_quoting_a_deleted_heading_is_not_an_error` |
| the same quotation in an open brief is reported | `test_an_open_brief_quoting_a_deleted_heading_is_still_an_error` |
| the exemption names `.claude/rules/citation-drift.md` | named in `_quoting_sources`'s docstring |

**Worth keeping from `PL-W8NH` before it is dropped.** It carries a
measurement `PL-ZM8P` does not: widening `CITATION_CONNECTIVE` to admit the
possessive produces 37-40 errors, **34 of them in closed briefs**. That number
belongs to `PL-316G`, which already holds it, so nothing is lost by dropping
`PL-W8NH` itself - but check `PL-316G` still carries it before doing so.

**Why it matters beyond the tidy-up.** `PL-316G`'s recommended shape 4 is "one
alternative added to `CITATION_CONNECTIVE`, one status filter in
`_quoting_sources`". `PL-ZM8P` lands that status filter, so shape 4's remaining
work is the connective widening and the three handle dispositions - and its
backlog drops from ~40 findings to ~6, because the 34 closed-brief findings
stop being reported. Whoever implements `PL-316G` should start from a tree that
has `PL-ZM8P` in it, or they will write the same filter a second time.

**Done when.** `PL-W8NH` is `dropped` with a `reason` naming `PL-ZM8P`, or - if
#864 merges first and #866's fix is what actually lands - the two are
reconciled in whichever direction leaves one implemented item and no second
brief describing unfinished work that is finished.
