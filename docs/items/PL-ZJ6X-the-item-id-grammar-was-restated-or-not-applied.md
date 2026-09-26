---
id: PL-ZJ6X
title: The item-id grammar was restated or not applied wherever an id was hand-written - seven items, spent since tools/fixture_id_check.py imports store.ID_RE
priority: P3
effort: S
status: done
classes: defect
milestone: v0.5.9
touches: tools/fixture_id_check.py, subprojects/docket/src/docket/store.py
added: 2026-09-23
closed: 2026-09-23
pr: 969
reason: Recorded for the audit: the mechanism is closed by tools/fixture_id_check.py
verify: python3 tools/fixture_id_check.py
root-cause-of: PL-GXPP, PL-CY8B, PL-DPY6, PL-3BZS, PL-7922, PL-L609, PL-KYW3, PL-PB8V
generator: spent - PL-KYW3 made the restating sites import store.ID_PATTERN and tools/fixture_id_check.py, wired into make check, refuses an unmintable literal in any Python file or .claude/ text; nothing has arrived since 2026-09-21
misread: Which strings are valid item ids
---

**Problem.** The item-id grammar was restated or not applied wherever an id was hand-written - seven items, spent since tools/fixture_id_check.py imports store.ID_RE

**Found 2026-09-23** by `PL-T7Y1`'s generator audit. It came up in the inflow
sweep and survived three skeptics, all three of whom judged it spent. Recorded
for the audit: the count decides the record.

**The mechanism.** A hand-written `PL-` literal, or a tool regex restating the
id grammar (`store.ID_ALPHABET`, `store.ID_PATTERN`), was held to nothing.
Two channels produced the members: literals in Python or `.claude/` text
(`PL-GXPP`, `PL-CY8B`, `PL-DPY6`, `PL-3BZS`, `PL-7922`, `PL-L609`), and a
counted-quantifier regex in a tool (`PL-KYW3`).

**Why it is spent.** `PL-KYW3` (#875) made the six restating sites import
`store.ID_PATTERN`. `tools/fixture_id_check.py` (`PL-7922` #865, widened by
`PL-L609` #870) applies `store.ID_RE` to every Python string and keyword name
and to all `.claude/` text, and it is wired into `make check` (`Makefile:308`).
Nothing new has arrived since 2026-09-21. `PL-CY8B` is still open as a member.
The mechanism that produced it is closed.
