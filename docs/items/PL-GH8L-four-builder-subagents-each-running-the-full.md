---
id: PL-GH8L
title: Four builder subagents each running the full suite at once drove the container's load average to about 30 on 4 cores, so bin/docket verify --self's make check step hit its fixed 1,800 s limit and gave no answer on three branches
priority: P2
effort: S
status: ready
classes: defect
feature: parallel-builders
touches: .claude/skills/docket/modes/picking.md
added: 2026-10-24
payoff: a batch of builders in one container gets an accept or reject from verify --self on every branch, instead of a timeout that sends the check round again
verify: grep -qiE 'cores|load average' .claude/skills/docket/modes/picking.md
---

**Problem.** Four builder subagents each running the full suite at once drove the container's load average to about 30 on 4 cores, so bin/docket verify --self's make check step hit its fixed 1,800 s limit and gave no answer on three branches

**Why it matters.** When `bin/docket verify --self` hits its limit, it reports a timeout and no verdict. The answer is honest, but the builder then has no accept or reject to go on, and three of the four branches needed the check run again. The limit is the fixed 1,800 s default of `_run` in `subprojects/docket/src/docket/verify.py`, and it does not scale with the load on the machine.

**Where the fix goes.** The fix belongs in `.claude/skills/docket/modes/picking.md` § "Mode: work several items at once", the section a session reads when it plans a batch. No checked-in builder brief exists: the parent session writes each brief fresh, so a lesson learnt in one session reaches the next only if it is written into that section. `PL-5PL5`, `PL-9K28` and `PL-GH8L` are one problem, grouped as the `parallel-builders` feature. A lock that lets only one `make check` run at a time in one container would enforce the limit in code rather than in prose. The session that works this item chooses between the lock and a written cap on concurrent full-suite runs.

**Done when.** Running several builders in one container cannot push `make check` past `verify --self`'s limit. Either the batch section caps how many builders run the full suite at once, by the container's core count, or full-suite runs are serialised. Whichever route is chosen, the batch section says which.

**Reproduced 2026-10-24.** `grep -ciE 'scratchpad|foreground|cores|load average' .claude/skills/docket/modes/picking.md` prints 0.

**Generator check.** This is one of the three hazards grouped in `PL-5PL5`, and it is not a generator for the reason that item gives.
