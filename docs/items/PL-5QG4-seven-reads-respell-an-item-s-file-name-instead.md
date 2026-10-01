---
id: PL-5QG4
title: Seven reads respell an item's file name instead of vcs.ITEM_FILE_RE - generator_check three times, item_reads, dead_ends, doc_check's brief lookup and claiming's pathspec - and six of them answer differently from it on a file name with no slug
status: untriaged
feature: read-facts-through-docket
touches: tools/generator_check.py, tools/item_reads.py, tools/dead_ends.py, tools/doc_check.py, subprojects/docket/src/docket/claiming.py
added: 2026-10-01
---

**Problem.** Seven reads respell an item's file name instead of vcs.ITEM_FILE_RE - generator_check three times, item_reads, dead_ends, doc_check's brief lookup and claiming's pathspec - and six of them answer differently from it on a file name with no slug

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/generator_check.py:250`, `:270` and `:294`; `tools/item_reads.py:62`; `tools/dead_ends.py:155`; `tools/doc_check.py:4150`; `subprojects/docket/src/docket/claiming.py:728`, which agrees. The other six take a slug-less `PL-K7QX.md` as an item, which `vcs.ITEM_FILE_RE` does not, while the store's `ITEM_GLOB` reads every `*.md`; which of the three is the grammar is part of the fix.
