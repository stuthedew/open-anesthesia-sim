---
id: PL-G3KZ
title: Fail make check when the lines loaded at launch pass a cap set at the total after PL-MR85's moves, a cap that can only go down, and retire the rule that each edit to those files names what it replaces
priority: P2
effort: M
status: ready
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

**Checked 2026-11-21**, by `PL-TPXK` (the independent review of the four streamlining decisions). **Recommendation:** cap the character total and not the line count. Lines in the four files run from 80 to 1,264 characters, so a line count does not bound what a session loads, and joining two lines would meet a line cap. At `2b17061` the 39 non-blank lines of the safety standard and the expert-review section are 7% of `CLAUDE.md`'s 583 non-blank lines and 18% of its 47,286 characters. `tools/doc_check.py` already prints the character total, and the growth this item cites, from 60,199 to 92,660, is in characters. Claude Code's documentation states its target in lines and gives none in characters or tokens (https://code.claude.com/docs/en/memory, read through a fetching agent on 2026-11-21), so the line count can still be printed beside the cap.

**Done when.** `make check` fails when the lines loaded at launch exceed the cap, a test shows it failing one line over the cap, and `CLAUDE.md` and `docs/resident-instructions.md` describe the cap instead of the refused ceiling.
