---
id: PL-P813
title: vcs._base_blobs answers whether the default branch ever held a blob, and three readers took that for whether the base took or superseded a branch's change: PL-RLTK's landing split (fixed by reading what the base wrote since the fork), claims._landed_through (PL-P64J) and stranded's item filter
status: untriaged
feature: pre-fork-content
added: 2026-09-27
root-cause-of: PL-RLTK, PL-P64J, PL-WVSX
generator: spent - PL-RLTK moved the landing split off the ever-held set, and its two remaining readers each hold an item (PL-P64J, PL-WVSX); another member needs a new reader of _base_blobs
misread: Whether the base already holds or has superseded a branch commit's change, by whatever route
---

**Problem.** vcs._base_blobs answers whether the default branch ever held a blob, and three readers took that for whether the base took or superseded a branch's change: PL-RLTK's landing split (fixed by reading what the base wrote since the fork), claims._landed_through (PL-P64J) and stranded's item filter
