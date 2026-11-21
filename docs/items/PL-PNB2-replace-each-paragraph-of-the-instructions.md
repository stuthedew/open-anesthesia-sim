---
id: PL-PNB2
title: Replace each paragraph of the instructions loaded at launch that a check enforces with one line naming the check, as PL-MR85's approved table marks them: rows 30-35, 43, 71 and 72
priority: P2
effort: M
status: ready
classes: session-cost
feature: standing-weight
touches: CLAUDE.md, .claude/rules/expert-review.md, .claude/rules/instruction-writing.md, .claude/rules/plain-writing.md
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
payoff: sessions load fewer lines of instructions before they read anything, so each rule that stays is likelier to be followed
verify: grep -q "tools/import_boundary_check.py" CLAUDE.md
---

**Problem.** Replace each paragraph of the instructions loaded at launch that a check enforces with one line naming the check, as PL-MR85's approved table marks them: rows 30-35, 43, 71 and 72

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** Each row keeps one line that states the rule and names the check that enforces it, such as `tools/import_boundary_check.py` for simulation time held as explicit state. The co-author line in row 72 has no check, so it stays as it is.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Done when.** Each row listed in the title holds no more lines than `PL-MR85`'s table gives it, each named check runs in `make check` or in CI, and `make check` passes.
