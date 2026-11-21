---
id: PL-T51K
title: Move the pull request, Projects-thread and screenshot procedures in the instructions loaded at launch into the pull-request skill, the coordinator mode and the run-the-app skill, as PL-MR85's approved table marks them: rows 7, 45, 73, 167, 172d, 194 and 205-206
priority: P2
effort: M
status: ready
classes: session-cost
feature: standing-weight
touches: CLAUDE.md, .claude/rules/expert-review.md, .claude/rules/instruction-writing.md, .claude/rules/plain-writing.md, .claude/skills/pull-request/SKILL.md, .claude/skills/docket/modes/coordinator.md, .claude/skills/run-the-app/SKILL.md
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
payoff: sessions load fewer lines of instructions before they read anything, so each rule that stays is likelier to be followed
verify: ! grep -q "title names the change plainly" .claude/rules/plain-writing.md && grep -q "title names the change plainly" .claude/skills/pull-request/SKILL.md
---

**Problem.** Move the pull request, Projects-thread and screenshot procedures in the instructions loaded at launch into the pull-request skill, the coordinator mode and the run-the-app skill, as PL-MR85's approved table marks them: rows 7, 45, 73, 167, 172d, 194 and 205-206

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** Pull request titles, examples and the line that sorts a commit-producing answer go to `.claude/skills/pull-request/SKILL.md`. The Projects-trial clauses of product focus and the rule on filling a long wait go to `.claude/skills/docket/modes/coordinator.md`. The screenshot steps of rule 10 go to `.claude/skills/run-the-app/SKILL.md`.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Done when.** Each row listed in the title holds no more lines than `PL-MR85`'s table gives it, each moved rule reads the same in its new home, and `make check` passes.
