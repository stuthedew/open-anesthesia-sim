---
id: PL-5PL5
title: Parallel builder subagents in one session share one scratchpad folder, so one builder's pull request body was published on another's pull request (#1735) and a builder's verify.log was overwritten; the builder brief names no per-item file prefix
priority: P2
effort: S
status: ready
classes: defect
feature: parallel-builders
touches: .claude/skills/docket/modes/picking.md
added: 2026-10-24
payoff: builders running side by side in one session can no longer publish each other's pull request bodies or overwrite each other's verify logs
verify: grep -qiF 'scratchpad' .claude/skills/docket/modes/picking.md
---

**Problem.** Parallel builder subagents in one session share one scratchpad folder, so one builder's pull request body was published on another's pull request (#1735) and a builder's verify.log was overwritten; the builder brief names no per-item file prefix

**Why it matters.** A pull request body is a record. `docs/pr-bodies/` keeps it, and a reviewer reads it as the account of the change. When one builder publishes a sibling's body, that pull request carries the wrong rationale and the wrong verification claim. The overwritten `verify.log` loses the evidence that a builder's `docket verify` passed. Both failures are silent. Nothing reports that the file came from another builder.

**Where the fix goes.** The fix belongs in `.claude/skills/docket/modes/picking.md` § "Mode: work several items at once", the section a session reads when it plans a batch. No checked-in builder brief exists: the parent session writes each brief fresh, so a lesson learnt in one session reaches the next only if it is written into that section. `PL-5PL5`, `PL-9K28` and `PL-GH8L` are one problem, grouped as the `parallel-builders` feature.

**Done when.** The batch section tells the parent to give each builder its own scratch file names, for example a subfolder or a prefix named after the item id, for the pull request body, the verify log and any other file a builder writes. It also tells the parent to say so in each builder's brief.

**Reproduced 2026-10-24.** `grep -ciE 'scratchpad|foreground|cores|load average' .claude/skills/docket/modes/picking.md` prints 0. The batch section says nothing about files that builders share.

**Generator check.** The fact that was misread is what parallel builder subagents in one container share: one scratch folder, the same cores, and a turn that ends while a background command is still running. No head's `misread:` states it. These are three different hazards, each found once, and a checked-in procedure would carry the fixes but would not have prevented the first discovery of each. So this is one group of three, not a generator.
