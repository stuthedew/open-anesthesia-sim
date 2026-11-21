---
id: PL-2PJ6
title: Move the history in the instructions loaded at launch to docs/resident-instructions.md, as PL-MR85's approved table marks it: rows 2, 5, 42, 46, 54, 117, 142-144, 147, 152, 156, 174, 178 and 192, and the history clauses of the rows it keeps
priority: P2
effort: M
status: ready
classes: session-cost
feature: standing-weight
touches: CLAUDE.md, .claude/rules/expert-review.md, .claude/rules/instruction-writing.md, .claude/rules/plain-writing.md, docs/resident-instructions.md
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
payoff: sessions load fewer lines of instructions before they read anything, so each rule that stays is likelier to be followed
verify: ! grep -q "Worked example, 2026-09-12" .claude/rules/expert-review.md && ! grep -q "RESIDENT BY NECESSITY" .claude/rules/instruction-writing.md
---

**Problem.** Move the history in the instructions loaded at launch to docs/resident-instructions.md, as PL-MR85's approved table marks it: rows 2, 5, 42, 46, 54, 117, 142-144, 147, 152, 156, 174, 178 and 192, and the history clauses of the rows it keeps

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** Each row's history goes to `docs/resident-instructions.md` under a dated section, with its sources and item ids kept word for word. The row keeps only the lines the table's "Keep" column gives it, and a rule that loses its evidence keeps a one-line citation.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Done when.** Each row listed in the title holds no more lines than `PL-MR85`'s table gives it, the moved text is in `docs/resident-instructions.md`, and `make check` passes.
