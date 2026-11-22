---
id: PL-GDN7
title: Move the procedures in the instructions loaded at launch that apply only with a known file open into path-scoped rules, as PL-MR85's approved table marks them: rows 23, 53, 70, 154, 179, 180 and 197-202, with a new rule that loads with CLAUDE.md and .claude/ for row 70's four dispositions
priority: P2
effort: M
status: done
classes: session-cost
feature: standing-weight
milestone: v0.6.19
touches: CLAUDE.md, .claude/rules/expert-review.md, .claude/rules/plain-writing.md, .claude/rules/citation-drift.md, .claude/rules/apparatus-standard.md, .claude/rules/sources-and-docstrings.md, .claude/rules/rule-routing.md, docs/resident-instructions.md
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
closed: 2026-11-21
pr: 2189
payoff: sessions load fewer lines of instructions before they read anything, so each rule that stays is likelier to be followed
verify: ! grep -qF 'reference implementation measured nothing' .claude/rules/expert-review.md
---

**Problem.** Move the procedures in the instructions loaded at launch that apply only with a known file open into path-scoped rules, as PL-MR85's approved table marks them: rows 23, 53, 70, 154, 179, 180 and 197-202, with a new rule that loads with CLAUDE.md and .claude/ for row 70's four dispositions

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** Each procedure goes to the path-scoped rule that loads with the file it governs: recording a decision's kind with `docs/items/`, a check's retirement test with `tools/`, the source hierarchy and a chosen value's reason with `src/` and `docs/MODEL.md`, and the "For developers" note and its examples with `docs/MODEL.md` and `docs/INTERFACE.md`. A new rule that loads with `CLAUDE.md` and `.claude/` carries the four dispositions for routing an instruction. `tools/rules_paths_check.py` must accept each new glob.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Checked 2026-11-21**, by `PL-TPXK` (the independent review of the four streamlining decisions). Two rows need more than the table gives them.

1. Row 180, "Take the reason for a chosen value from a record", moves to `.claude/rules/sources-and-docstrings.md`. That rule loads with `src/`, `docs/MODEL.md`, `docs/INTERFACE.md` and `docs/references/`. The row's own example is a tolerance in a test, so the rule's paths also need `/tests/**`.
2. Row 23, how to record whether the owner ratified or specified a decision, moves to `.claude/rules/citation-drift.md`. That rule loads with `docs/items/`, `docs/WORKING_NOTES.md`, `.claude/skills/` and `.claude/rules/`. Decisions are also recorded in `CLAUDE.md`, `ROADMAP.md`, `docs/MODEL.md` and `docs/INTERFACE.md`. So the one line that row 23 keeps in `CLAUDE.md` states the two forms themselves: `(project owner, DATE, ratified)` with what it was chosen over, and `(project owner, DATE)`.

**Done when.** Each row listed in the title holds no more lines than `PL-MR85`'s table gives it, each moved rule loads when a session reads a matching file, and `make check` passes.

**Built 2026-11-21.** Each row that the title lists now holds no more lines than the table gives it, apart from row 23, which point 2 below explains. `python3 tools/doc_check.py check` counts 863 lines and 68,292 characters loaded at launch, where it counted 943 lines and 73,482 characters after `PL-CYT1` (move procedures into the docket skill). `docs/resident-instructions.md` § "The procedures that load with the file they govern" keeps each paragraph as it was loaded before the move.

Where each rule is now:

1. Row 23, how to record whether the owner ratified or specified a decision. `.claude/rules/citation-drift.md` § "Record whether the owner ratified or specified a decision" holds the bullet, word for word.
2. Row 53, the test for retiring a check. `.claude/rules/apparatus-standard.md` § "A check earns its place every run, or it is retired" holds it. Its first clause now names the section of `CLAUDE.md` that decides whether to build a check, where it said "the gate above".
3. Rows 69 and 70, the four places a rule about sessions can go. `.claude/rules/rule-routing.md` is new, loads with `CLAUDE.md` and every file under `.claude/`, and holds them. `tools/rules_paths_check.py` accepts its two globs.
4. Row 154, a reference implementation measured nothing. `.claude/rules/sources-and-docstrings.md` § "A reference implementation is not a source" already held the rule and its examples. It gained one opening paragraph with the two sentences it lacked.
5. Rows 179, 180 and 197 to 202, the note for developers, the reason for a chosen value, and the examples of a `docs/MODEL.md` paragraph and of a docstring. `.claude/rules/sources-and-docstrings.md` § "Write these files plainly" holds all four, word for word.

Three things differ from the table. The first two correct it, as `PL-TPXK` (the independent review of the four streamlining decisions) found.

1. `.claude/rules/sources-and-docstrings.md` now loads with `tests/` as well, because the example in row 180 is a tolerance in a test.
2. Row 23 keeps two lines where the table gives it one. `.claude/rules/citation-drift.md` does not load with `CLAUDE.md`, `ROADMAP.md`, `docs/MODEL.md` or `docs/INTERFACE.md`, where decisions are also recorded. So the two lines give both forms: `(project owner, DATE, ratified)` with what it was chosen over, and the plain `(project owner, DATE)`.
3. The table gives row 69 two lines and row 70 one. They are one paragraph of three lines, and the title of this item lists only row 70.

The opening of `docs/resident-instructions.md` named `CLAUDE.md` as the place that holds the four dispositions, and now names `.claude/rules/rule-routing.md`.

**Docs checked.** A search of the tree for the opening words of each moved paragraph found them only in the rules that now hold them, the ledger, closed items and `docs/pr-bodies/`. `.claude/rules/sources-and-docstrings.md` said "Both rules below", and now says "The rules below", because it holds three sections.
