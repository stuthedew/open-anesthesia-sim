---
id: PL-CSV0
title: Triage the 12 untriaged captures standing in the queue on 2026-09-19
priority: P2
effort: S
status: done
classes: infra
milestone: v0.4.30
touches: docs/items, ROADMAP.md
added: 2026-09-19
closed: 2026-09-19
pr: 720
verify: ! grep -l '^status: untriaged' docs/items/PL-04KR-*.md docs/items/PL-3GKR-*.md docs/items/PL-9KSY-*.md docs/items/PL-CSV0-*.md docs/items/PL-G424-*.md docs/items/PL-HCTF-*.md docs/items/PL-R5HK-*.md docs/items/PL-STC4-*.md docs/items/PL-TZ7T-*.md docs/items/PL-VKGJ-*.md docs/items/PL-WPDB-*.md docs/items/PL-X3NY-*.md docs/items/PL-YRYR-*.md
---

**Problem.** Triage the 12 untriaged captures standing in the queue on 2026-09-19

**Why it matters.** An untriaged item is invisible to `bin/docket next`, which
ranks on `priority`, and absent from `bin/docket gate`, which counts debt by
`classes` and `status`. Twelve of them is a second queue nobody reads -
`docket.toml`'s `untriaged_stale_days = 14` is the standing judgment that this
state is a defect rather than a backlog. All twelve were captured on
2026-09-19, so none is stale yet; the number is what makes the pass worth a
commit of its own.

**Filed before the work, not after.** `CLAUDE.md`'s housekeeping rule: every
in-flight guard this project has matches a `PL-` id, so a triage pass carrying
none reads as nobody's work to `flight`, `show`, `next` and `concurrent` alike,
and keeps reading that way after the commit has landed.

**The pass owes the gate a disposition, which is why `ROADMAP.md` is in
`touches`.** `tools/doc_check.py`'s `check_gate_dispositions` advisory names
every open item that is `needs-decision` or carries a class in
`docket.toml`'s `debt_classes` and that v0.5.0's frozen gate neither places nor
defers. Classing an item is what makes it debt, so the pass creates the
advisory it then has to answer - the lesson `PL-2P9L` paid for on 2026-09-19.
Everything this pass seats was captured on 2026-09-19, well after the gate was
frozen on 2026-09-06, and none is `safety`- or `science`-classed, so each
defers under `ROADMAP.md` § "The gate is a snapshot, not a moving target".

**Premises checked against the tree rather than read off the briefs.** Three
of the twelve rest on a statement that has moved or was never true, and a
triage that seats them without checking hands the next session a false
starting point:

- `PL-3GKR` says "the order is `PL-Y5JX` first". `PL-Y5JX` closed on
  2026-09-19 and merged as `#714`, so the blocker it names has cleared and the
  item is `ready` rather than `blocked`.
- `PL-9KSY` says `store.write_item`'s `replace=` has no caller left. Confirmed:
  `grep -rn 'replace=' subprojects/docket` returns one hit, `test_store.py:113`,
  and no production caller.
- `PL-X3NY` says "this project already reads that API - `docket record`
  recovers a `pr` number from a merge commit". The second clause is git rather
  than the API: `merged_pull_requests` in `vcs.py` parses merge-commit
  subjects, and no module under `subprojects/docket/src/docket/` imports
  `urllib` or names `api.github`. The two scripts that do read the API are
  `tools/pr_title_check.py` and `tools/main_ci_status.py`, neither of which
  `bin/docket` runs. That moves the item from `ready` to `needs-decision`.

**Done when.** Every item this pass took carries `priority`, `effort`,
`classes` and `touches`, sits at a status past `untriaged`, and satisfies
`bin/docket check`; each item newly counted as debt carries a gate disposition
in `ROADMAP.md`; and the items left untriaged are the ones another session is
demonstrably holding, named in the reply with the branch that holds them.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it.

> **Eight more from the 2026-09-19 triage pass over the twelve untriaged captures** (`PL-CSV0`). `PL-9KSY`, `PL-G424`, `PL-STC4`, `PL-VKGJ`, `PL-X3NY` and `PL-YRYR` sit exactly where the first thirty do. They were captured on 2026-09-19, well after the 2026-09-06 freeze. They are `P2` or `P3`, neither `safety` nor `science`, and wholly in the workflow lane. Every `touches` path they declare is inside `docket.toml`'s `workflow_paths`, so none can affect a reader of the simulator. The paragraph above says that the arithmetic now argues harder. That arithmetic is unchanged, and it argues the same way here. This gate stands at 170 cleared of 175, with two entries it can clear. Admitting eight would take that remainder from two to ten, at the beat where the milestone is one step from starting.
