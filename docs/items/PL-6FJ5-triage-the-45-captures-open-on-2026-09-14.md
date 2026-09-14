---
id: PL-6FJ5
title: Triage the 45 captures open on 2026-09-14
priority: P2
effort: M
status: done
classes: planning
feature: queue-hygiene
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
