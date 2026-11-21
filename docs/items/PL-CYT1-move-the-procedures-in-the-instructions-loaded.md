---
id: PL-CYT1
title: Move the procedures in the instructions loaded at launch that the docket skill already holds or should hold into it, leaving one trigger line each, as PL-MR85's approved table marks them: rows 6, 38, 62, 64-67, 75, 172i and 172n, including the four fix-in-place conditions
priority: P2
effort: M
status: done
classes: session-cost
feature: standing-weight
touches: CLAUDE.md, .claude/rules/instruction-writing.md, .claude/rules/citation-drift.md, .claude/skills/docket/modes/start.md, .claude/skills/docket/modes/capture.md, .claude/skills/docket/modes/picking.md, docs/resident-instructions.md, tools/config_home_check.py
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
closed: 2026-11-21
pr: 2187
payoff: sessions load fewer lines of instructions before they read anything, so each rule that stays is likelier to be followed
verify: ! grep -q "It is a defect, not a choice" CLAUDE.md && grep -rq "It is a defect, not a choice" .claude/skills/docket/
---

**Problem.** Move the procedures in the instructions loaded at launch that the docket skill already holds or should hold into it, leaving one trigger line each, as PL-MR85's approved table marks them: rows 6, 38, 62, 64-67, 75, 172i and 172n, including the four fix-in-place conditions

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** Each procedure goes to the docket skill's mode that fires at its moment: triage for the generator rules, start for the reset and the fix-in-place conditions, capture for capture and housekeeping, and next or start for the check on other sessions. Where the mode already holds the rule, only the resident copy is deleted. One trigger line stays loaded at launch for each row.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Done when.** Each row listed in the title holds no more lines than `PL-MR85`'s table gives it, each moved rule reads the same in its new home, and `make check` passes.

**Built 2026-11-21.** Each row that the title lists now holds no more lines than the table gives it. `python3 tools/doc_check.py check` counts 944 lines and 73,844 characters loaded at launch, where it counted 1,086 lines and 84,205 characters after `PL-2PJ6` (move the history to the ledger). `docs/resident-instructions.md` § "The procedures that the `docket` skill holds" keeps each paragraph as it was loaded before the move.

Where each rule is now:

1. Rows 6 and 67, the pause on new workflow mechanisms and a generator's two endings. `.claude/skills/docket/modes/triage.md` § "Generators, how they rank, and the pause they set" already held both in full, so only the copies loaded at launch were cut.
2. Row 38, the reset at 150,000 tokens. `.claude/skills/docket/modes/start.md` § "Check the spend before starting, and reset in place" already held the procedure. It gained the sentence that asks for one topic per session.
3. Row 62, capture. `.claude/skills/docket/modes/capture.md` already held how to group titles under a feature. It gained one paragraph for the rest: that capture covers the owner's findings and the session's alike, and when to update `docs/WORKING_NOTES.md`.
4. Rows 63 to 65, fixing a small defect in place. `.claude/skills/docket/modes/start.md` § "Fix a small defect in place" holds the four conditions, the limit of two per branch and the repairs that count against neither, word for word apart from the opening sentence.
5. Rows 66 and 75, housekeeping and routing intent. `.claude/skills/docket/modes/capture.md` § "Mode: housekeeping nobody filed" and the table in `.claude/skills/docket/modes/ideas.md` already held them.
6. Row 172i, the closing block as a handover. `.claude/skills/docket/modes/capture.md` already held which branches a reply names. The sentences about how the harness carries the block are in the ledger only.
7. Row 172n, checking other sessions. `.claude/skills/docket/modes/picking.md` § "Check the other sessions before recommending work" holds the whole paragraph.

Two things differ from the table, and both correct it.

1. The table gives row 63 three lines and rows 64 and 65 none. `PL-TPXK` (the independent review of the four streamlining decisions) found that a session can fix a defect before it loads a skill. So the three lines that stay name `src/anesthesia_sim/core/`, `src/anesthesia_sim/data/`, `docs/MODEL.md` and `docs/INTERFACE.md` as the paths where a defect is always filed. `tools/config_home_check.py` compares that list, and the copy in the skill's section, with `protected_paths` in `docket.toml`.
2. The title names `.claude/skills/docket/SKILL.md`, and nothing in it changed. Every moved rule went to one of the skill's mode files, which `touches` now names.

Six sentences that pointed at `CLAUDE.md` or at rule 14 for a moved rule now say where it is: three in `.claude/skills/docket/modes/capture.md`, two in `.claude/skills/docket/modes/start.md` and one in `.claude/rules/citation-drift.md`.

**Docs checked.** `python3 tools/doc_check.py candidates --base origin/main` named `docs/apparatus.md` and `docs/maintainer.md` for `tools/config_home_check.py`, and both still describe it correctly. A search of the tree for "fix-now" and "fix-in-place" found `subprojects/docket/src/docket/vcs.py`, `subprojects/docket/src/docket/arming.py`, `subprojects/docket/README.md` and `tools/pr_body_check.py`. Each names the rule and not where it is written, apart from `arming.py`, which says that `CLAUDE.md` names the clinical paths, and it still does.

