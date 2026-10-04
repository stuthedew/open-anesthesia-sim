---
id: PL-QFFF
title: tools/dead_ends.py's ENTRY pattern does not match docs/dead-ends.md line 74, whose bold title is followed by a parenthetical before its dash, so the session-start digest drops that dead end with nothing reported and shows 10 of the 11
status: untriaged
added: 2026-10-04
---

**Problem.** tools/dead_ends.py's ENTRY pattern does not match docs/dead-ends.md line 74, whose bold title is followed by a parenthetical before its dash, so the session-start digest drops that dead end with nothing reported and shows 10 of the 11

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`).** Line 74 opens `- **Detecting duplicate captures by shared cited referents** (item ids, shas, ...) — refuted 2026-09-16`, and the digest of this session listed ten dead ends without it. Not a `PL-R417` member: the entry is on one line, and the fault is which shapes the pattern admits, not where the entry ends.
