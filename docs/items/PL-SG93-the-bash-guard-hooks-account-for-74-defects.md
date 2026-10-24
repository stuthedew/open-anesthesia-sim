---
id: PL-SG93
title: The Bash guard hooks account for 74 defects across 100 items, but nothing records what they block, so their cost cannot be weighed against what they prevent
priority: P2
effort: M
status: ready
classes: infra
feature: defect-review-2026-10
touches: .claude/hooks
added: 2026-10-19
payoff: each Bash guard hook either shows what it blocked in return for its defect cost, or is simplified or retired
verify: grep -qE '^\*\*Block counts\.' docs/items/PL-SG93-*.md
---

**Problem.** The Bash guard hooks account for 74 defects across 100 items, but nothing records what they block, so their cost cannot be weighed against what they prevent

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Evidence.** Items whose `touches` include `.claude/hooks/` number 100, and 74 of them are defects, filed mostly in the week of 2026-09-21 (38). `PL-61FT` (the guards decide what a command does from its spelling) re-entered 8 times and closed by recording known gaps in a table rather than fixing more spellings. Nothing records what the guards blocked.

**What to do.** Measure before deciding anything. Count each guard's blocks across recent session transcripts, or have the hooks log them, then weigh each guard's defect cost against what it prevented. Keep any guard against an irreversible action whatever the count.

**Done when.** Each guard has a block count and a keep, simplify or retire verdict recorded here.

**Why it matters.** A guard that blocks nothing still costs a defect every time a session meets one of its gaps. A guard against an irreversible action may be worth that cost. Without a block count, nobody can tell which guard is which.

**Generator check.** One-off. The 74 defects are `PL-61FT`'s mechanism (drained 2026-09-27). This item measures them and misreads nothing. Record the counts under a `**Block counts.**` heading here.
