---
id: PL-2PJ6
title: Move the history in the instructions loaded at launch to docs/resident-instructions.md, as PL-MR85's approved table marks it: rows 2, 5, 42, 46, 54, 117, 142-144, 147, 152, 156, 174, 178 and 192, and the history clauses of the rows it keeps
priority: P2
effort: M
status: done
classes: session-cost
feature: standing-weight
milestone: v0.6.19
touches: CLAUDE.md, .claude/rules/expert-review.md, .claude/rules/instruction-writing.md, .claude/rules/plain-writing.md, docs/resident-instructions.md, tools/new_prose.py, tools/rules_paths_check.py, tools/config_home_check.py, tests/unit/test_rules_paths_check.py, docs/apparatus.md
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
closed: 2026-11-21
pr: 2184
payoff: sessions load fewer lines of instructions before they read anything, so each rule that stays is likelier to be followed
verify: ! grep -q "Worked example, 2026-09-12" .claude/rules/expert-review.md && ! grep -q "RESIDENT BY NECESSITY" .claude/rules/instruction-writing.md
---

**Problem.** Move the history in the instructions loaded at launch to docs/resident-instructions.md, as PL-MR85's approved table marks it: rows 2, 5, 42, 46, 54, 117, 142-144, 147, 152, 156, 174, 178 and 192, and the history clauses of the rows it keeps

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** Each row's history goes to `docs/resident-instructions.md` under a dated section, with its sources and item ids kept word for word. The row keeps only the lines the table's "Keep" column gives it, and a rule that loses its evidence keeps a one-line citation.

**Built 2026-11-21.** Each row that the title lists now holds no more lines than the table gives it. `docs/resident-instructions.md` § "The sort of 2026-11-21, and the history it moved here" holds each paragraph as it stood before the move, word for word. `python3 tools/doc_check.py check` counts 1,086 lines and 84,205 characters loaded at launch, where it counted 1,340 lines and 100,977 characters before.

Four things differ from the title.

1. The table also keeps 25 rows of judgment at fewer lines and names no destination for what they lose: rows 14, 28, 29, 37, 47, 48, 50, 51, 55, 63, 69, 77, 118, 119, 145, 149, 151, 153, 155, 172c, 172j, 172k, 172m, 173 and 196. No item's title lists them, and `PL-G3KZ` sets its cap at the total after every row is done. This item shortened 23 of them, and the ledger holds their earlier text beside the history rows. Row 63 introduces the fix-in-place conditions that `PL-CYT1` moves, and row 69 introduces the four dispositions that `PL-GDN7` moves, so each of those two items shortens the row that leads into its own.
2. The three notes of row 178 on the reader table went to the docstring of `tools/new_prose.py`, as the table says. That file joined `touches`.
3. The ledger's blocks are fenced, so that a path cited inside one is not checked against a tree that has moved on. `tools/doc_check.py` reads a fenced line that starts with "make" as a command, so one line of row 172h's block is joined to the line before it. No word of it changed.
4. Row 118 keeps three lines of the scope paragraph of `.claude/rules/expert-review.md`, and its list of the apparatus's paths does not fit in them. `tools/rules_paths_check.py` and `tools/config_home_check.py` each compared that list with the one in `CLAUDE.md`, and four tests failed when it went. Both checks now compare the two lists that remain: the one in `CLAUDE.md` and the `paths:` of `.claude/rules/apparatus-standard.md`. `tools/config_home_check.py` lost its fact for the apparatus's paths, because its only copy was the removed list, and `tools/rules_paths_check.py` already compares the two that remain.

A shortened row keeps its rule sentences as they were wherever the line count allowed. The rows that needed new wording are 2, 5, 27, 28, 29, 33, 37, 47, 55, 77, 118, 119, 145, 148, 153, 196 and the citation lines of rows 142 and 143.

**Docs checked.** `python3 tools/doc_check.py candidates --base origin/main` named `.claude/skills/docket/modes/close-out.md` and `docs/apparatus.md` for `tools/new_prose.py`, and both still describe it correctly. `docs/apparatus.md` described the two checks of the fourth point by the three lists, and now names two. A search of the tree for the moved phrases found them cited only in the four instruction files, the ledger, closed items and `docs/pr-bodies/`.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Done when.** Each row listed in the title holds no more lines than `PL-MR85`'s table gives it, the moved text is in `docs/resident-instructions.md`, and `make check` passes.
