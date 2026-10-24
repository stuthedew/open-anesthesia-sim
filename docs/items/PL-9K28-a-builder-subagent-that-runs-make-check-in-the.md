---
id: PL-9K28
title: A builder subagent that runs make check in the background ends its turn and is not woken when the command finishes, so the PL-ZZ03 builder stopped twice with tested work unpushed until the parent resumed it; builder briefs do not say to run long checks in the foreground
priority: P3
effort: S
status: ready
classes: defect
feature: parallel-builders
touches: .claude/skills/docket/modes/picking.md
added: 2026-10-24
payoff: a builder's tested work is pushed when its checks finish, instead of waiting unpushed until the parent session notices and resumes it
verify: grep -qiF 'foreground' .claude/skills/docket/modes/picking.md
---

**Problem.** A builder subagent that runs make check in the background ends its turn and is not woken when the command finishes, so the PL-ZZ03 builder stopped twice with tested work unpushed until the parent resumed it; builder briefs do not say to run long checks in the foreground

**Why it matters.** Tested work that is not pushed is lost when the container is reclaimed. The parent cannot tell a builder that stopped early from one that finished, unless it reads the builder's transcript. Here the `PL-ZZ03` builder stopped twice, and each time the parent had to resume it by hand.

**Where the fix goes.** The fix belongs in `.claude/skills/docket/modes/picking.md` § "Mode: work several items at once", the section a session reads when it plans a batch. No checked-in builder brief exists: the parent session writes each brief fresh, so a lesson learnt in one session reaches the next only if it is written into that section. `PL-5PL5`, `PL-9K28` and `PL-GH8L` are one problem, grouped as the `parallel-builders` feature.

**Done when.** The batch section tells the parent to brief each builder to run `make check`, `bin/docket verify --self` and any other long command in the foreground, with a timeout long enough for the command to finish. A builder subagent is not woken when its background command finishes.

**Reproduced 2026-10-24.** `grep -ciE 'scratchpad|foreground|cores|load average' .claude/skills/docket/modes/picking.md` prints 0.

**Generator check.** This is one of the three hazards grouped in `PL-5PL5`, and it is not a generator for the reason that item gives.
