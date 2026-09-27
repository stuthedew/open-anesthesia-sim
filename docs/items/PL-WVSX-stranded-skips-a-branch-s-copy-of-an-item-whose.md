---
id: PL-WVSX
title: stranded skips a branch's copy of an item whose blob the default branch's history ever held, because its item filter reads _base_blobs' ever-held set: a branch that restores an item file to an earlier version, reopening a closed item for one, reads as behind the base, so its change is never reported if the branch is abandoned (reasoned from the code 2026-09-27, not yet run)
status: untriaged
feature: pre-fork-content
added: 2026-09-27
---

**Problem.** stranded skips a branch's copy of an item whose blob the default branch's history ever held, because its item filter reads _base_blobs' ever-held set: a branch that restores an item file to an earlier version, reopening a closed item for one, reads as behind the base, so its change is never reported if the branch is abandoned (reasoned from the code 2026-09-27, not yet run)

**A member for `PL-927J`'s head.** `PL-927J`, filed on
`claude/vibrant-heisenberg-vhf99e` and not yet on main, records PL-GHHW's
misread producing again through `PL-8BR0`, `PL-RLTK` and `PL-P64J`; this is the
same misread in `stranded`. It bears on whether that head is recorded live or
spent: after `PL-RLTK`'s fix `_base_blobs` has two readers left,
`claims._landed_through` (`PL-P64J`) and this filter, and each now holds an
item. `PL-P813`, a head filed for it in the session that fixed `PL-RLTK`, was
dropped as a duplicate once `PL-927J` was found.
