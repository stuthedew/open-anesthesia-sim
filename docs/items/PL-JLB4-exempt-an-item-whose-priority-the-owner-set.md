---
id: PL-JLB4
title: Exempt an item whose priority the owner set from the advisory telling sessions to demote process work in a band
priority: P2
effort: S
status: done
classes: defect
milestone: v0.6.2
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, subprojects/docket/tests/test_checks.py, docs/items/PL-8349-outside-contributor-accessibility-find-what.md, docs/items/PL-JRVV-review-claude-md-for-instructions-that-a-script.md
added: 2026-10-20
closed: 2026-10-24
pr: 1721
payoff: the band advisory stops telling sessions to demote items the owner placed on purpose, so obeying it can no longer overturn the owner's decision
verify: grep -q 'def test_owner_set_priority' subprojects/docket/tests/test_checks.py
---

**Skeleton, to be fleshed out** (project owner, 2026-10-20: "Owner designated
status get white listed").

**Problem.** `bin/docket check` gives this advisory when process work
outnumbers product work in a band: "process work (...) outnumbers the product
work beside it; demote it". The rule is in `_groom` in
`subprojects/docket/src/docket/checks.py`. It fires on items whose priority the
owner set on purpose. On 2026-10-20 the owner put `PL-8349` (making quick fixes
possible for outside developers) and `PL-JRVV` (retiring `CLAUDE.md` rules a
check already enforces) at P1. The advisory then told every session to demote
both.

**Why it matters.** An advisory that fires on a decision already taken changes
no decision. `CLAUDE.md` § "Prefer deterministic tooling over repeated model
work" calls that a defect in the check: it trains sessions to skim the output,
where a real advisory also appears. Worse, a session that obeys it overrides
the owner's decision.

**Goal (the owner's).** An item whose priority the owner set is exempt from
this advisory. The advisory still fires on process work a session promoted on
its own judgment.

**Design question to settle.** Nothing records today who set an item's
priority. Prose such as "Priority P1 is the owner's" in a brief is not a record
a check can read reliably. `.claude/rules/apparatus-standard.md` § "Read the
fact from its record; where none exists, write one" says the fix is a place to
write the fact. The likely shape is a frontmatter field, for example
`priority-set-by: owner (2026-10-20)`. `model.py` would parse it, the
advisory would skip items that carry it, and `subprojects/docket/README.md`
would document it. Settle the field's name and form, and whether the ratified
versus specified split in `CLAUDE.md` applies to it.

**Done when.** An item with the owner's priority record does not count toward
the advisory. An item without one still does. A test pins both cases, and
`PL-8349` and `PL-JRVV` carry the record.

**Constraint.** A new item field may count as a new workflow mechanism. While
any open workflow-lane item carries `generator: live`, `CLAUDE.md` § "What this
project is" pauses new mechanisms unless the owner lifts the pause for this
request. Check that before building.

**Generator check.** One-off, asked for by the owner. No head's `misread:` states who set an item's priority, and no other open item misreads it.

**Triage 2026-10-20:** the field's name and form are the building session's to settle, under the read-the-record rule cited above. The generator pause does not apply: `bin/docket generators` lists no head still generating, and the owner asked for this.

**Built 2026-10-24.** The record is a front-matter field, `owner-priority: P1, 2026-10-20`, with `, ratified` after the date where the owner agreed with a session's recommendation. `parse_owner_priority` and `owner_set_priority` in `subprojects/docket/src/docket/model.py` read it. The field names the priority rather than only who set it, unlike the brief's `priority-set-by: owner (2026-10-20)`. So a later change to the priority shows as a mismatch, which `docket check` refuses, instead of a record that describes a priority the item no longer has. `docket set --priority` therefore refuses to move an owner-set priority unless the same call records the owner's new one. The ratified and specified split from `CLAUDE.md` § "Working with the project owner" is recorded, since any owner decision records its kind. Both kinds exempt the item, because either way the priority is the owner's decision and the advisory is not evidence that reopens it. `_groom` in `subprojects/docket/src/docket/checks.py` leaves an owner-set item out of the process count and out of the product count. `bin/docket set` writes the field with `--owner-priority`, and `subprojects/docket/README.md` § "`owner-priority:` records that the project owner set the priority" documents it.

The new-mechanism pause did not apply. `bin/docket generators` listed no head still generating on 2026-10-24, and the owner asked for this.

**Re-checked 2026-10-24.** The brief's two examples have moved since filing. The owner corrected `PL-8349` from P1 to P3 on 2026-10-20 ("should not be p1. Can be untriaged or P3"), so its record is `P3, 2026-10-20`. `PL-JRVV` closed on 2026-10-24 at P1, and carries `P1, 2026-10-20`. Neither now sits in a band the advisory reads, but both carry the record as the Done-when asks.
