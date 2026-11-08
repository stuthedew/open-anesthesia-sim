---
id: PL-3B47
title: Quality pass over the 46 untriaged captures and the triaged tooling items, and repair the apparatus defects it finds
priority: P2
effort: M
status: done
classes: infra, defect
feature: queue-hygiene
milestone: v0.4.14
touches: docs/items, subprojects/docket, tools, .claude, Makefile, docket.toml, tests/unit
added: 2026-09-12
closed: 2026-09-12
pr: 496
not-delegable: A queue-wide grooming pass has no command that can prove it: 'bin/docket check reports no untriaged items' passes on any tree where nobody has captured anything, and the apparatus repairs it carries are each proven by their own item's verify: command. The pass is judged by those, plus make check.
---

**Problem.** Quality pass over the 46 untriaged captures and the triaged tooling items, and repair the apparatus defects it finds

**Why it matters.** Captures had reached 46 untriaged - past `docket.toml`'s
`untriaged_stale_days` horizon for the oldest of them - which is the state that
turns the capture half of the queue into a second queue nobody reads. Untriaged
items are invisible to `bin/docket next`, so work sitting in them is neither
scheduled nor visible as backlog, and `bin/docket next`'s own open count
understates the total by exactly that number (`PL-ZWBK`).

Two costs compound while it sits. Duplicates accumulate unnoticed - two pairs
were filed three days apart, each costing a second session the same diagnosis -
and captures go stale as ordinary work overtakes them, so a later session spends
a pass rediscovering that a filed defect was fixed four releases ago. Both are
only visible when the pile is read end to end, which is what this pass is.

**Done when.** `bin/docket check` reports zero untriaged items with no errors;
every item that stayed carries `priority`, `effort`, `classes`, `touches` and a
`feature`, with a `verify:` command that was run and watched fail for any set to
`ready`; every item that left carries a `reason` naming what replaced it or what
fixed it; and the apparatus defects this pass found to be real are repaired with
tests, `make check` clean.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it.

> **Eleven more from the 2026-09-12 triage pass, and six of them are not in the workflow lane** (`PL-3B47`, which closed with that pass). The refilling-queue arithmetic above is unchanged and is still the reason. The six that are apparatus sit exactly where the first thirty do, and admitting them would grow a gate that is not draining. The other six need a ground of their own, because "wholly in the workflow lane" is not true of them. So their ground is stated below, rather than the first ground being stretched to cover them.
