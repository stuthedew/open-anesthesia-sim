---
id: PL-T51K
title: Move the pull request, Projects-thread and screenshot procedures in the instructions loaded at launch into the pull-request skill, the coordinator mode and the run-the-app skill, as PL-MR85's approved table marks them: rows 7, 45, 73, 167, 172d, 194 and 205-206
priority: P2
effort: M
status: done
classes: session-cost
feature: standing-weight
touches: CLAUDE.md, .claude/rules/instruction-writing.md, .claude/rules/plain-writing.md, .claude/skills/pull-request/SKILL.md, .claude/skills/docket/modes/coordinator.md, .claude/skills/docket/modes/start.md, .claude/skills/run-the-app/SKILL.md, docs/resident-instructions.md
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
closed: 2026-11-21
pr: 2192
payoff: sessions load fewer lines of instructions before they read anything, so each rule that stays is likelier to be followed
verify: ! grep -qF 'title names the change plainly' .claude/rules/plain-writing.md
---

**Problem.** Move the pull request, Projects-thread and screenshot procedures in the instructions loaded at launch into the pull-request skill, the coordinator mode and the run-the-app skill, as PL-MR85's approved table marks them: rows 7, 45, 73, 167, 172d, 194 and 205-206

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** Pull request titles, examples and the line that sorts a commit-producing answer go to `.claude/skills/pull-request/SKILL.md`. The Projects-trial clauses of product focus and the rule on filling a long wait go to `.claude/skills/docket/modes/coordinator.md`. The screenshot steps of rule 10 go to `.claude/skills/run-the-app/SKILL.md`.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Done when.** Each row listed in the title holds no more lines than `PL-MR85`'s table gives it, each moved rule reads the same in its new home, and `make check` passes.

**Built 2026-11-21.** Each row that the title lists now holds no more lines than the table gives it. `python3 tools/doc_check.py check` counts 812 lines and 64,971 characters loaded at launch, where it counted 864 lines and 68,553 characters after `PL-GDN7` (move procedures into path-scoped rules). `docs/resident-instructions.md` § "The procedures that the pull-request skill, the coordinator mode and the run-the-app skill hold" keeps each paragraph as it was loaded before the move.

Where each rule is now:

1. Row 7, product focus. `CLAUDE.md` keeps the rule in four lines. `.claude/skills/docket/modes/coordinator.md` § "Product focus and the Projects trial" holds who decided it, who works a root cause while the trial runs, and how the focus ends.
2. Row 45, filling a long wait with work. `.claude/skills/docket/modes/coordinator.md` § "What every brief tells its thread" holds it, word for word.
3. Row 73, commit and push as you go. `.claude/skills/pull-request/SKILL.md` already held when a pull request opens, arms and merges.
4. Row 167, rule 10. `.claude/rules/instruction-writing.md` keeps ten lines. `.claude/skills/run-the-app/SKILL.md` § "Compare interface approaches for the owner" now states the screenshot rule itself, where it pointed at rule 10. `.claude/skills/docket/modes/coordinator.md` § "What every brief tells its thread" holds which questions go to the coordinator.
5. Row 172d, a closing-block line whose answer makes a commit. `.claude/skills/pull-request/SKILL.md` § "Ask `bin/docket arm` before arming and before every later push" holds the whole bullet.
6. Rows 194, 205 and 206, pull request titles and the examples. `.claude/skills/pull-request/SKILL.md` § "Write the title and body" holds the title rule and the owner's chosen title, word for word. It already held the two bodies.

`.claude/skills/docket/modes/start.md` pointed at `.claude/rules/plain-writing.md` for the title rule, and now points at the pull-request skill.

**Docs checked.** A search of the tree for the opening words of each moved paragraph found them only in the three files that now hold them, the ledger, closed items and `docs/pr-bodies/`.
