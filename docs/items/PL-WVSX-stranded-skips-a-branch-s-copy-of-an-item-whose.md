---
id: PL-WVSX
title: stranded skips a branch's copy of an item whose blob the default branch's history ever held, because its item filter reads _base_blobs' ever-held set: a branch that restores an item file to an earlier version, reopening a closed item for one, reads as behind the base, so its change is never reported if the branch is abandoned (reasoned from the code 2026-09-27, not yet run)
status: untriaged
feature: pre-fork-content
added: 2026-09-27
---

**Problem.** stranded skips a branch's copy of an item whose blob the default branch's history ever held, because its item filter reads _base_blobs' ever-held set: a branch that restores an item file to an earlier version, reopening a closed item for one, reads as behind the base, so its change is never reported if the branch is abandoned (reasoned from the code 2026-09-27, not yet run)
