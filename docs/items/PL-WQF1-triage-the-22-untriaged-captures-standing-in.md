---
id: PL-WQF1
title: Triage the 22 untriaged captures standing in the queue on 2026-09-20
priority: P2
effort: S
status: done
classes: housekeeping
milestone: v0.4.34
touches: docs/items, ROADMAP.md
added: 2026-09-20
closed: 2026-09-20
pr: 757
payoff: the 22 captures standing in the queue stop being a second queue nobody reads, invisible to bin/docket next and uncounted by bin/docket gate
verify: ! grep -l '^status: untriaged' docs/items/PL-0RZ0-*.md docs/items/PL-3NKZ-*.md docs/items/PL-7JN7-*.md docs/items/PL-BHBZ-*.md docs/items/PL-BYMX-*.md docs/items/PL-D126-*.md docs/items/PL-FH61-*.md docs/items/PL-GJPD-*.md docs/items/PL-HJZW-*.md docs/items/PL-JQY1-*.md docs/items/PL-LPH9-*.md docs/items/PL-MFM4-*.md docs/items/PL-NGLM-*.md docs/items/PL-NWSK-*.md docs/items/PL-QYBW-*.md docs/items/PL-RR1N-*.md docs/items/PL-VHPR-*.md docs/items/PL-VJPJ-*.md docs/items/PL-W7WL-*.md docs/items/PL-WG7Q-*.md docs/items/PL-WJNS-*.md docs/items/PL-WQF1-*.md docs/items/PL-WQT0-*.md
---

**Problem.** Triage the 22 untriaged captures standing in the queue on 2026-09-20

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it.

> **Twelve more from the 2026-09-20 triage pass over the twenty-two captures open that day** (`PL-WQF1`). Nine of them lie wholly in the workflow lane, exactly where the first thirty do. Every one was captured on 2026-09-19 or 2026-09-20, well after the 2026-09-06 freeze. All are `P2`, none is `safety` or `science`, and all are apparatus held to `.claude/rules/apparatus-standard.md`'s deliberately lower bar. `PL-BHBZ` and `PL-HJZW` are two checks whose stated severity does not match what they do. `PL-GJPD` and `PL-WG7Q` are the two halves of how a closure's pull request is recovered, to be worked in that order. `PL-MFM4` and `PL-W7WL` are two ways in which `bin/docket release` loses to a second session or to a late merge. `PL-NWSK` is a fifth refusal that the required-checks reconciliation does not know about. `PL-RR1N` is a `verify:` phrase that a document's own line-wrapping can split. `PL-VJPJ` is a traceback on a closed pipe. The refilling-queue arithmetic in the four paragraphs above is unchanged and is still the reason. This gate holds three open entries and is nearly clear. Admitting nine apparatus items that cannot affect a reader of the simulator would reopen it days before the milestone it gates begins.

> Two of the nine are worth a sentence because they fired during this pass itself. `PL-HJZW` explains why this subsection has entries at all, in the shape it does. The gate-disposition failure prints under the advisory heading, which says that judgment is needed. But `tests/unit/test_doc_check.py` makes it a hard `make check` failure. So the pass that creates the advisory is the pass most likely to trust the label and be wrong. `PL-VJPJ` is the traceback that a session gets from `bin/docket next | head`. Neither is more urgent because this pass met it. Both are recorded so that the next session to meet them knows they are already known.

> **Three are not wholly apparatus and so need their own ground**. Each ground is stated here rather than stretched to fit.
