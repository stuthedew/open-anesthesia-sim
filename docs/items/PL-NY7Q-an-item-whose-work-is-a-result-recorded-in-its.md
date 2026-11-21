---
id: PL-NY7Q
title: An item whose work is a result recorded in its own brief closes with no verify: command
priority: P2
effort: S
status: untriaged
classes: infra
feature: standing-weight
touches: subprojects/docket/src/docket, subprojects/docket/tests, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md, .claude/skills/docket/modes/close-out.md
added: 2026-11-21
payoff: a count or a decision closes on its dated paragraph, with no command that only re-reads the item's own file
---

**Problem.** An item whose work is a result recorded in its own brief closes with no verify: command

**Why it matters.** The project owner chose this form on 2026-11-21 (`PL-LFJZ`, the count of what a test-named done-condition would have prevented). 79 of the 794 `grep` conditions that name no test only confirm that the item's own brief records its result, such as `PL-WKKH`'s `Answered 2026-11-20`. The closed status and the dated paragraph are already the record, so the command proves nothing more. Release items keep what they have, because `bin/docket release` writes the version and the notes.

**What to do.** A closed item that records no `tests:`, no `verify:` and no `not-delegable:` is accepted where its brief holds a paragraph that opens with a bold label carrying a date, such as `**Answered 2026-11-20.**` or `**Counted 2026-11-21**`. That paragraph is the record of the result. 82 of the 102 closed items whose command only read their own file already carry one (counted 2026-11-21 with `docket.model.parse_item` over `docs/items/`). An item with none of the four is still refused, so that no item closes with nothing to show for it. `bin/docket verify` accepts the same record.

**Done when.** An item whose brief holds a dated record paragraph closes with no command, and `bin/docket check` still fails a closed item that records nothing.

**Generator check.** None: work the project owner chose in `PL-LFJZ` (the count of what a test-named done-condition would have prevented).
