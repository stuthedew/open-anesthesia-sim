---
id: PL-MFVV
title: docket's roadmap list walker (list_entry_lines, under list_entries) ends an entry at an unindented line CommonMark reads as that entry's lazy continuation (0.31.2 section 5.2), so a Required-scope or gate entry wrapped without an indent is read short and its declaration lost; doc_check's _list_members declines the shape by name since PL-R417 slice 1, the walker's other readers do not
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** docket's roadmap list walker (list_entry_lines, under list_entries) ends an entry at an unindented line CommonMark reads as that entry's lazy continuation (0.31.2 section 5.2), so a Required-scope or gate entry wrapped without an indent is read short and its declaration lost; doc_check's _list_members declines the shape by name since PL-R417 slice 1, the walker's other readers do not

**Found by** `PL-R417` slice 1 (`#1332`), which taught `doc_check`'s
`_list_members` to decline the shape by name and left the walker's own readers
in `docket.roadmap`, `_gate_entries` and `_scope_entries`, as they were: outside
that slice. A member of `PL-R417`'s head. Measured 2026-10-04: three lazy lines
follow list entries in `ROADMAP.md` (lines 2636, 2680 and 3989, the document
defects `PL-DSMK` holds), none inside a gate or Required-scope list, so the
fault is latent. The head's fix applies: the walker reports a lazy line itself,
so every reader of it declines by name from one place rather than one reader
at a time. `docket new` matched this capture to `PL-W9BK` on the shared path
alone; that item is about which entries `wave` counts as blocked outside the
gate, and this is not it.
