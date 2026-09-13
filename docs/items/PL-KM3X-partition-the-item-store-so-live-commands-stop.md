---
id: PL-KM3X
title: Partition closed item bodies out of the live store
status: dropped
added: 2026-09-13
closed: 2026-09-13
reason: measurement and prior art both refute it; this store's records are cross-referenced, and cross-referenced stores stay flat
---

**Problem as filed.** 70.8% of `docs/items/` is terminal and still parsed on
every invocation; closed bodies are 68% of the bytes and no command reads them.

**Why it is dropped.** Three independent lines refute the proposal.

1. **No measurable cost.** `store.read_items` is 76 ms for 820 items (93 us/item,
   linear to 6,512) against a 819-840 ms `bin/docket next` whose real cost is
   ~380 ms of git subprocesses. `git status` on this repo is 5 ms. A synthetic
   flat directory shows no knee to 100,000 files (15.9-16.4 us/file, flat).
   Git's own many-files perf test starts at ~1,000,000 index entries.
2. **Partitioning would not fix the one real threshold.** git-sizer's guidance
   is "avoid creating directories with more than a couple of thousand entries
   each" - an *entry count*, ~32 days away at 37/day. Moving bodies to sibling
   files leaves 820 entries and adds a second file per item, making it worse.
3. **This store is the wrong shape for a state partition.** The convention in
   real record stores splits on whether records cite each other: cross-referenced
   stores keep a flat directory forever (Python PEPs - 738 docs, 81% terminal,
   26 years, flat, generated index; Rust RFCs - 645 docs, no status field at
   all), while independent-record stores partition by state (Maildir, Jekyll,
   Taskwarrior 2.x, Backlog.md). Re-derived this session under an explicit rule
   (unique resolvable ids, body only, self excluded): **706/820 = 86.1% of items
   cite another, 2,773 edges, max in-degree 49.** This store is PEP-shaped.
   Moving files invalidates every cross-reference path and breaks
   `git log --follow`, which is single-file only.

**What was right in it.** Nothing reads a closed item's body - that finding
holds and is worth keeping. It argues for a bounded startup tier, not for a
partition; see the replacement item.

**Reversal note.** Filed and dropped the same day. The prior art that appeared
to support it (Backlog.md `completed/`, todo.txt `done.txt`, Taskwarrior
`completed.data`, OpenSpec archive) is real but belongs to the independent-record
family. The agent-facing evidence that a growing store hurts is about what enters
*context*, not what sits on *disk*.
