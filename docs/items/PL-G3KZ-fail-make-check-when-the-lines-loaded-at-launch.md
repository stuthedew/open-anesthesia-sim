---
id: PL-G3KZ
title: Fail make check when the lines loaded at launch pass a cap set at the total after PL-MR85's moves, a cap that can only go down, and retire the rule that each edit to those files names what it replaces
priority: P2
effort: M
status: done
classes: session-cost
feature: standing-weight
touches: CLAUDE.md, tools/doc_check.py, tests/unit/test_doc_check.py, docs/resident-instructions.md, docs/apparatus.md
blocked-by: PL-2PJ6, PL-CYT1, PL-GDN7, PL-T51K, PL-PNB2
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
closed: 2026-11-21
pr: 2194
payoff: the lines every session loads at launch can no longer grow unnoticed
tests: tests/unit/test_doc_check.py::test_instruction_files_at_the_cap_pass_and_one_character_over_fails, tests/unit/test_doc_check.py::test_a_rule_with_no_paths_counts_against_the_cap_and_a_scoped_one_does_not, tests/unit/test_doc_check.py::test_a_skill_description_is_printed_and_not_counted_against_the_cap, tests/unit/test_doc_check.py::test_a_cap_above_the_default_branch_s_is_refused, tests/unit/test_doc_check.py::test_a_default_branch_that_states_no_cap_is_not_compared
---

**Problem.** Fail make check when the lines loaded at launch pass a cap set at the total after PL-MR85's moves, a cap that can only go down, and retire the rule that each edit to those files names what it replaces

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** `tools/doc_check.py` already prints the total but deliberately never fails on it, and `CLAUDE.md` records that a ceiling was refused. The owner's answer to `PL-MR85` on 2026-11-20 reopened that: the growth from 60,199 characters on 2026-09-19 to 92,660 on 2026-11-20 is the new evidence. The cap is set at the total once the five moves have merged, and lowering it is the only edit allowed. The rule that each edit to the resident set names what it replaces, and the docstring of `check_resident_instructions` that argues against a limit, are rewritten to match.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Checked 2026-11-21**, by `PL-TPXK` (the independent review of the four streamlining decisions). **Recommendation:** cap the character total and not the line count. Lines in the four files run from 80 to 1,264 characters, so a line count does not bound what a session loads, and joining two lines would meet a line cap. At `2b17061` the 39 non-blank lines of the safety standard and the expert-review section are 7% of `CLAUDE.md`'s 583 non-blank lines and 18% of its 47,286 characters. `tools/doc_check.py` already prints the character total, and the growth this item cites, from 60,199 to 92,660, is in characters. Claude Code's documentation states its target in lines and gives none in characters or tokens (https://code.claude.com/docs/en/memory, read through a fetching agent on 2026-11-21), so the line count can still be printed beside the cap.

**Done when.** `make check` fails when the lines loaded at launch exceed the cap, a test shows it failing one line over the cap, and `CLAUDE.md` and `docs/resident-instructions.md` describe the cap instead of the refused ceiling.

**Built 2026-11-21.** `make check` now fails when `CLAUDE.md` and the three rules with no `paths:` together hold more than 55,120 characters, the total once the five moves had merged. With this change they hold 55,114, because the line in `CLAUDE.md` that names the cap is six characters shorter than the line it replaces. It also fails when a branch sets the cap higher than the default branch holds, so the cap only goes down. `check_resident_cap` in `tools/doc_check.py` does both, and `RESIDENT_CAP` in that file is the one place the number is written.

**The cap counts characters, and the owner approved a cap on lines.** `PL-TPXK` (the independent review of the four streamlining decisions) recommended characters: lines in the four files run from 80 to 1,264 characters, so a line count does not bound what a session loads, and joining two lines would meet it. `tools/doc_check.py` already measured characters, and still prints the line count beside the total.

How it works, and what was decided in building it:

1. The cap covers the four instruction files alone, the total that `ResidentInstructions.instruction_total` already held. A skill's description and the session-start digest are still printed in the launch total and are not capped, because `PL-MR85`'s sort covered the instruction files alone and the digest changes with the queue.
2. The cap is a constant in `tools/doc_check.py`, as this repository's other limits that only go down are. A key in `docket.toml` was the alternative. It would have put the number beside settings that the owner edits freely, where this one changes only downward.
3. A raise is refused, as an error. The check reads the default branch's copy of `tools/doc_check.py` with Python's `ast` module and compares the two values. An advisory was the alternative, and an advisory is easy to skim past. When the default branch cannot be read, or its copy states no cap, the comparison is skipped and the cap itself still applies.
4. A branch that shrinks the files is not made to lower the cap. Forcing that would make two branches that both shrink them conflict on the one constant. A session that wants the gain kept lowers the number in the same change.
5. The error says what to do: move a rule to a check, a skill or a path-scoped rule, as `.claude/rules/rule-routing.md` says, and never delete a rule to reach the number.
6. The two advisories that name growth and shrinkage against the default branch are unchanged.

`CLAUDE.md` now says in one line that `tools/doc_check.py` caps the files loaded at launch. `docs/resident-instructions.md` § "The cap of 2026-11-21" records the cap, why it counts characters, and that it replaces the rule that each edit to these files names what it replaces. The two bullets of § "Reductions considered and refused" that argue against a ceiling each carry a note that points there. The module's docstring, `check_resident_instructions`'s docstring and `docs/apparatus.md` describe the cap where they argued against a limit.

One thing differs from **Done when**. It asks for a test that fails one line over the cap, and the test fails one character over it, because the cap counts characters.

**Docs checked.** `CLAUDE.md`, `docs/resident-instructions.md`, `docs/apparatus.md` and the docstrings in `tools/doc_check.py`. A search of the tree for "never a gate", "resident-growth series" and "names what it replaces" found the remaining mentions only in the ledger's fenced history, closed items and `docs/pr-bodies/`.
