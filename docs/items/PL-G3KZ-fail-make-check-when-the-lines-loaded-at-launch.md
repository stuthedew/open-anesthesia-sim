---
id: PL-G3KZ
title: Fail make check when the lines loaded at launch pass a cap set at the total after PL-MR85's moves, a cap that can only go down, and retire the rule that each edit to those files names what it replaces
priority: P2
effort: M
status: blocked
classes: session-cost
feature: standing-weight
touches: CLAUDE.md, .claude/rules/expert-review.md, .claude/rules/instruction-writing.md, .claude/rules/plain-writing.md, tools/doc_check.py, tests/unit/test_doc_check.py, docs/resident-instructions.md
blocked-by: PL-2PJ6, PL-CYT1, PL-GDN7, PL-T51K, PL-PNB2
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
payoff: the lines every session loads at launch can no longer grow unnoticed
---

**Problem.** Fail make check when the lines loaded at launch pass a cap set at the total after PL-MR85's moves, a cap that can only go down, and retire the rule that each edit to those files names what it replaces

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** `tools/doc_check.py` already prints the total but deliberately never fails on it, and `CLAUDE.md` records that a ceiling was refused. The owner's answer to `PL-MR85` on 2026-11-20 reopened that: the growth from 60,199 characters on 2026-09-19 to 92,660 on 2026-11-20 is the new evidence. The cap is set at the total once the five moves have merged, and lowering it is the only edit allowed. The rule that each edit to the resident set names what it replaces, and the docstring of `check_resident_instructions` that argues against a limit, are rewritten to match.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Done when.** `make check` fails when the lines loaded at launch exceed the cap, a test shows it failing one line over the cap, and `CLAUDE.md` and `docs/resident-instructions.md` describe the cap instead of the refused ceiling.
