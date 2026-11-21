---
id: PL-NY7Q
title: An item whose work is a result recorded in its own brief closes with no verify: command
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** An item whose work is a result recorded in its own brief closes with no verify: command

**Why it matters.** The project owner chose this form on 2026-11-21 (`PL-LFJZ`, the count of what a test-named done-condition would have prevented). 79 of the 794 `grep` conditions that name no test only confirm that the item's own brief records its result, such as `PL-WKKH`'s `Answered 2026-11-20`. The closed status and the dated paragraph are already the record, so the command proves nothing more. Release items keep what they have, because `bin/docket release` writes the version and the notes.
