---
id: PL-SG93
title: The Bash guard hooks account for 74 defects across 100 items, but nothing records what they block, so their cost cannot be weighed against what they prevent
status: untriaged
feature: defect-review-2026-10
added: 2026-10-19
---

**Problem.** The Bash guard hooks account for 74 defects across 100 items, but nothing records what they block, so their cost cannot be weighed against what they prevent

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Evidence.** Items whose `touches` include `.claude/hooks/` number 100, and 74 of them are defects, filed mostly in the week of 2026-09-21 (38). `PL-61FT` (the guards decide what a command does from its spelling) re-entered 8 times and closed by recording known gaps in a table rather than fixing more spellings. Nothing records what the guards blocked.

**What to do.** Measure before deciding anything. Count each guard's blocks across recent session transcripts, or have the hooks log them, then weigh each guard's defect cost against what it prevented. Keep any guard against an irreversible action whatever the count.

**Done when.** Each guard has a block count and a keep, simplify or retire verdict recorded here.
