---
id: PL-6FJ5
title: Triage the 45 captures open on 2026-09-14
priority: P2
effort: M
status: done
classes: planning
feature: queue-hygiene
milestone: v0.4.26
touches: docs/items, ROADMAP.md
added: 2026-09-14
closed: 2026-09-14
pr: 579
verify: ! grep -l '^status: untriaged' docs/items/PL-037Y-*.md docs/items/PL-0HPV-*.md docs/items/PL-0MLZ-*.md docs/items/PL-0PJG-*.md docs/items/PL-0R06-*.md docs/items/PL-27H0-*.md docs/items/PL-2K1R-*.md docs/items/PL-2M5T-*.md docs/items/PL-2MD9-*.md docs/items/PL-4K9V-*.md docs/items/PL-4PC5-*.md docs/items/PL-59WB-*.md docs/items/PL-66X4-*.md docs/items/PL-73ZN-*.md docs/items/PL-7TBQ-*.md docs/items/PL-7TXJ-*.md docs/items/PL-9KP5-*.md docs/items/PL-BMY5-*.md docs/items/PL-BXB2-*.md docs/items/PL-C4RS-*.md docs/items/PL-CY5H-*.md docs/items/PL-CZTR-*.md docs/items/PL-D1RT-*.md docs/items/PL-DBGT-*.md docs/items/PL-FT3M-*.md docs/items/PL-FWJF-*.md docs/items/PL-J45M-*.md docs/items/PL-JFYT-*.md docs/items/PL-JW9J-*.md docs/items/PL-LLBV-*.md docs/items/PL-MBTZ-*.md docs/items/PL-NC62-*.md docs/items/PL-P1P6-*.md docs/items/PL-P669-*.md docs/items/PL-PRQG-*.md docs/items/PL-R0P3-*.md docs/items/PL-S9X7-*.md docs/items/PL-SM5V-*.md docs/items/PL-V53R-*.md docs/items/PL-VFD8-*.md docs/items/PL-W3Q5-*.md docs/items/PL-WNQT-*.md docs/items/PL-XJ37-*.md docs/items/PL-YNYK-*.md docs/items/PL-Z85N-*.md
---

**Problem.** Triage the 45 captures open on 2026-09-14

**Why it matters.** 45 untriaged captures is a second queue nobody reads:
`bin/docket next` cannot rank them, `bin/docket gate` cannot count them as debt,
and `docket.toml`'s `untriaged_stale_days = 14` says so in the tool's own terms.
Several were also captured before `PL-2FM6` deleted the sample store and before
the Qt port was renumbered and moved ahead of v0.5.0, so a share of them
described a tree that no longer exists - which is why every finding was checked
against the code before its fields were set rather than after.

**Done when.** None of the 45 is `status: untriaged`, every one carries the
fields `docket check` requires at its status, each `ready` item names a
`verify:` command that was run and seen to fail for the right reason, and the
debt-classed results have a recorded gate disposition so `make check` passes.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it.

> **Thirty-four more from the 2026-09-14 triage pass** (`PL-6FJ5`). That pass took the 45 captures that the v0.4.2x range left untriaged. It checked each finding against the tree before assigning its fields. Two of the 36 results classed as debt are `safety`: `PL-27H0` and `PL-2K1R`, both admitted to the frozen list above. These thirty-four are declined on two different grounds, and the split between the grounds is stated rather than averaged.

> **Nine were introduced by this milestone's own implementation work, so the presence rule defers them by its own terms** rather than by the refilling-queue exception. "The gate is a snapshot" says that a finding "defers to the next gate only when the problem itself is new: introduced by work done while clearing this gate or implementing the milestone it protects". `PL-B9PY`, `PL-J2TD` and `PL-TFX5` all landed in the week before this pass. Each of the nine is a property of the branching machinery that those three items built: `PL-59WB`, `PL-7TBQ`, `PL-7TXJ`, `PL-CZTR`, `PL-JFYT`, `PL-LLBV`, `PL-NC62`, `PL-SM5V`, `PL-XJ37`.

> **9 predate the freeze and are declined on the refilling-queue ground**, the same ground on which the first twenty-nine were declined. The arithmetic is the argument here, as it was there. This gate stands at 166 entries with 15 open. Admitting these findings would take it past 180 just as it is finally draining. None of them can give a reader of the simulator a wrong number. Four document internal structure (`PL-9KP5`, `PL-C4RS`, `PL-D1RT`, `PL-DBGT`). One is a type that is not yet wrong (`PL-W3Q5`). Three are numerical-envelope findings that no shipped code path triggers (`PL-2MD9`, `PL-73ZN`, `PL-BMY5`). `PL-0MLZ` is the one to watch, and it is deferred with that said. It lets `uv run pytest` run stale bytecode after a source file is restored. That makes a verification step err in the direction of a false pass. It is declined only because a workaround is available by hand today: export `PYTHONDONTWRITEBYTECODE`, or run through `make`. It is recommended as the first item taken off this list. The full 9: `PL-0MLZ`, `PL-2MD9`, `PL-73ZN`, `PL-9KP5`, `PL-BMY5`, `PL-C4RS`, `PL-D1RT`, `PL-DBGT`, `PL-W3Q5`.

> **16 sit wholly in the workflow lane**, which is the group this section was written for. They are apparatus, held to `.claude/rules/apparatus-standard.md`'s lower bar, and none of them can affect a reader of the simulator. `PL-0HPV`, `PL-0PJG`, `PL-2M5T`, `PL-4PC5`, `PL-BXB2`, `PL-FT3M`, `PL-FWJF`, `PL-J45M`, `PL-JW9J`, `PL-MBTZ`, `PL-R0P3`, `PL-V53R`, `PL-VFD8`, `PL-WNQT`, `PL-YNYK`, `PL-Z85N`.
