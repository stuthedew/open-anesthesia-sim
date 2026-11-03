---
id: PL-R7Q6
title: The plain-writing rule gives every kind of text one vague reader, so no writer or reviewer knows who a paragraph is for: name each kind's readers in one table, and print the reader beside each paragraph the prose review reads
priority: P1
owner-priority: P1, 2026-11-02
effort: S
status: done
feature: reader-tested-prose
touches: .claude/rules/plain-writing.md, tools/new_prose.py, tests/unit/test_new_prose.py, .claude/skills/docket/modes/close-out.md, docs/apparatus.md, docs/resident-instructions.md
added: 2026-11-02
closed: 2026-11-03
pr: 1957
payoff: every writer and reviewer knows who a paragraph is for, and what that reader knows and will do with it
verify: grep -q 'What they do not know' .claude/rules/plain-writing.md && grep -q 'def test_each_unit_names_its_reader' tests/unit/test_new_prose.py
---

**Problem.** `.claude/rules/plain-writing.md` names one reader for all prose:
"a careful newcomer, someone who knows anesthesia or Python but has not read
this repository". Because of the "or", a term passes when a Python reader might
know it. No document says which reader it is written for. A clinician reading
`docs/MODEL.md` and a developer changing one of its values need different
things, and the rule names neither (`PL-H76S`, faults 2 and 3).

**Why it matters.** A writer who does not know the reader cannot choose words
or facts for them, and a reviewer told to imagine a vague reader passes what an
expert understands.

**What to build.** Decided in `PL-H76S`'s design round (project owner,
2026-11-02, 23:41Z, ratified, over a sixth plain-writing pattern).

1. Replace the "careful newcomer" sentence with a table in the rule. Each row
   is one kind of text. For each of its readers, the row says what the reader
   knows, what they do not know, and what they will do with the text.
2. `docs/MODEL.md` has two readers. The first is a clinician or educator who
   wants to know whether to trust a displayed value, or to understand how the
   simulation works. The second is a developer, or someone who forked the
   project, who wants to change a value for a goal of their own. Neither is
   assumed to know numerical-methods terms such as "operator split" or
   "first-order method", software terms, or e-notation such as "4e-4".
3. The other rows cover `README.md`, docstrings and comments in `src/` and
   `tests/`, replies and questions to the owner, and item briefs, commit
   messages and pull request titles.
4. `tools/new_prose.py` reads the table from the rule and prints the reader
   line beside each unit it prints, so the writer and the reviewer use the
   same reader. The table has one home, the rule, and the tool reads it there.
5. The rule is resident, so the commit says what the table replaces, as
   `CLAUDE.md` requires of every edit to the resident set.

**Done when.** The rule holds the table, the "careful newcomer" sentence is
gone, and `tools/new_prose.py` prints each unit's reader from the table, with
a test that each kind of file it reads gets its own row's reader.

**Generator check.** Part of the fix for `PL-H76S`, the live generator for
prose that passes every check and fails its reader.
