---
id: PL-CYT1
title: Move the procedures in the instructions loaded at launch that the docket skill already holds or should hold into it, leaving one trigger line each, as PL-MR85's approved table marks them: rows 6, 38, 62, 64-67, 75, 172i and 172n, including the four fix-in-place conditions
priority: P2
effort: M
status: ready
classes: session-cost
feature: standing-weight
touches: CLAUDE.md, .claude/rules/expert-review.md, .claude/rules/instruction-writing.md, .claude/rules/plain-writing.md, .claude/skills/docket/SKILL.md
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
payoff: sessions load fewer lines of instructions before they read anything, so each rule that stays is likelier to be followed
verify: ! grep -q "It is a defect, not a choice" CLAUDE.md && grep -rq "It is a defect, not a choice" .claude/skills/docket/
---

**Problem.** Move the procedures in the instructions loaded at launch that the docket skill already holds or should hold into it, leaving one trigger line each, as PL-MR85's approved table marks them: rows 6, 38, 62, 64-67, 75, 172i and 172n, including the four fix-in-place conditions

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** Each procedure goes to the docket skill's mode that fires at its moment: triage for the generator rules, start for the reset and the fix-in-place conditions, capture for capture and housekeeping, and next or start for the check on other sessions. Where the mode already holds the rule, only the resident copy is deleted. One trigger line stays loaded at launch for each row.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Done when.** Each row listed in the title holds no more lines than `PL-MR85`'s table gives it, each moved rule reads the same in its new home, and `make check` passes.
