---
id: PL-5QG4
title: Seven reads respell an item's file name instead of vcs.ITEM_FILE_RE - generator_check three times, item_reads, dead_ends, doc_check's brief lookup and claiming's pathspec - and six of them answer differently from it on a file name with no slug
priority: P3
effort: M
status: ready
classes: defect
feature: read-facts-through-docket
touches: tools/generator_check.py, tools/item_reads.py, tools/dead_ends.py, tools/doc_check.py, subprojects/docket/src/docket/claiming.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: every reader agrees on which files in docs/items are items, so a slug-less file is an item everywhere or nowhere
verify: ! grep -qF 'parts = path.name.split("-")' tools/item_reads.py && ! grep -qF 'parts = path.name.split("-")' tools/dead_ends.py
---

**Problem.** Seven reads respell an item's file name instead of vcs.ITEM_FILE_RE - generator_check three times, item_reads, dead_ends, doc_check's brief lookup and claiming's pathspec - and six of them answer differently from it on a file name with no slug

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/generator_check.py:250`, `:270` and `:294`; `tools/item_reads.py:62`; `tools/dead_ends.py:155`; `tools/doc_check.py:4150`; `subprojects/docket/src/docket/claiming.py:728`, which agrees. The other six take a slug-less `PL-K7QX.md` as an item, which `vcs.ITEM_FILE_RE` does not, while the store's `ITEM_GLOB` reads every `*.md`; which of the three is the grammar is part of the fix.

**Why it matters.** Each site answers from its own spelling of a fact docket exports, so the next change to that fact reaches the export and not the copy, and the two then answer differently with nothing to say so - the mechanism `PL-KGYT` closed as spent.

**Done when.** Each site under **Sites** reads the export instead of its own spelling, and where a site answered differently from the export, a test pins that input.

**Generator check.** A member of `PL-KGYT` (done 2026-10-01), filed by that head's closing sweep and named in its `root-cause-of:`; its fix, the write-time rule in `.claude/rules/apparatus-standard.md` (`PL-HC8P`), covers new readers and these predate it, so this is neither a post-close instance nor a new generator.
