---
id: PL-2GQW
title: PL-L9JS's not-delegable reason rests on the recursion claim PL-20CQ disproved, so the item may be delegable after all
priority: P2
effort: S
status: dropped
classes: defect, infra
feature: dev-tooling
touches: docs/items/PL-L9JS-eight-open-items-carry-a-verify-command-that.md
added: 2026-09-07
closed: 2026-09-21
reason: `.claude/rules/citation-drift.md`'s closed-brief clause. `PL-L9JS` is `done` - closed 2026-09-02, shipped v0.3.1 - so its `not-delegable:` reason is a historical record of why that item was not delegated, and correcting it changes nothing: `bin/docket next` and `bin/docket delegable` read the field on open items only. Checked 2026-09-21 that the disproved recursion claim survives nowhere live - `grep` over the tree finds it in two `done` briefs (`PL-L9JS`, `PL-71P4`) and in this item, and in no standing document - so dropping it strands no reader. Re-judged in `PL-PT7M`'s pass
---

**Problem.** PL-L9JS's not-delegable reason rests on the recursion claim PL-20CQ disproved, so the item may be delegable after all

**Why it matters.** `PL-L9JS` records `not-delegable: the command that would
prove this is `bin/docket check` itself, which cannot be a `verify:` command
because `docket check` runs every open item's `verify:` command - it would
recurse.` `PL-20CQ` checked that and it is false: `docket check` replays the
commands only under `--verify`, which nothing in the store passes, and a nested
run is stopped by `LANDED_GUARD` anyway. Ten open items already record
`bin/docket check && grep -q ...` without incident.

So the field is withholding an item on a reason that does not hold, and
`not-delegable` is read by `docket next` when it decides which model the work
wants. The second half of the recorded reason - that what is left is eight
judgments no command makes - may well still stand on its own; that is the part
to re-examine.

**Done when.** `PL-L9JS` either carries a `verify:` command, or carries a
`not-delegable:` reason that is true of the tree as it now stands.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". No paragraph there named it apart from this entry line, so it rested on the section's opening ground, which is quoted in `PL-36R4`'s brief.

> - PL-2GQW (S) PL-L9JS's not-delegable reason rests on the recursion claim PL-20CQ disproved, so the item may be delegable after all — dropped 2026-09-21
