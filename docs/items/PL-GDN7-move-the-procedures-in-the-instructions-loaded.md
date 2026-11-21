---
id: PL-GDN7
title: Move the procedures in the instructions loaded at launch that apply only with a known file open into path-scoped rules, as PL-MR85's approved table marks them: rows 23, 53, 70, 154, 179, 180 and 197-202, with a new rule that loads with CLAUDE.md and .claude/ for row 70's four dispositions
priority: P2
effort: M
status: ready
classes: session-cost
feature: standing-weight
touches: CLAUDE.md, .claude/rules/expert-review.md, .claude/rules/instruction-writing.md, .claude/rules/plain-writing.md, .claude/rules/citation-drift.md, .claude/rules/apparatus-standard.md, .claude/rules/sources-and-docstrings.md
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
payoff: sessions load fewer lines of instructions before they read anything, so each rule that stays is likelier to be followed
verify: ! grep -q "reference implementation measured nothing" .claude/rules/expert-review.md && grep -q "reference implementation measured nothing" .claude/rules/sources-and-docstrings.md
---

**Problem.** Move the procedures in the instructions loaded at launch that apply only with a known file open into path-scoped rules, as PL-MR85's approved table marks them: rows 23, 53, 70, 154, 179, 180 and 197-202, with a new rule that loads with CLAUDE.md and .claude/ for row 70's four dispositions

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** Each procedure goes to the path-scoped rule that loads with the file it governs: recording a decision's kind with `docs/items/`, a check's retirement test with `tools/`, the source hierarchy and a chosen value's reason with `src/` and `docs/MODEL.md`, and the "For developers" note and its examples with `docs/MODEL.md` and `docs/INTERFACE.md`. A new rule that loads with `CLAUDE.md` and `.claude/` carries the four dispositions for routing an instruction. `tools/rules_paths_check.py` must accept each new glob.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Done when.** Each row listed in the title holds no more lines than `PL-MR85`'s table gives it, each moved rule loads when a session reads a matching file, and `make check` passes.
