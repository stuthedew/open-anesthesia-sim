---
id: PL-Q98K
title: The copy editor reads no interface text: src/ holds 131 string literals of 30 words or more (30 in app/controller.py), and the reader table matches rows by path, so an interface string and a docstring in one file cannot take different readers
priority: P2
effort: M
status: done
classes: feature
feature: copy-editor
touches: tools/new_prose.py, tests/unit/test_new_prose.py, .claude/rules/plain-writing.md
added: 2026-11-04
closed: 2026-11-04
pr: 2029
payoff: a long notice or refusal that a learner reads in the interface is reviewed for that reader, as a docstring is for a developer
verify: grep -qE 'def test_[a-z_]*string_literal' tests/unit/test_new_prose.py
---

**Problem.** The copy editor reads no interface text. `src/` holds 131 string literals of 30 words or more, 30 of them in `app/controller.py`. The reader table matches its rows to files by path, so an interface string and a docstring in the same file cannot have different readers.

**Checked 2026-11-04.** `tools/new_prose.py` reads two kinds of unit in a Python file, docstrings and runs of comment lines, so no string literal reaches the copy editor. An `ast` count of string constants and f-strings outside docstrings found 119 of 30 words or more under `src/`, 54 of them under `src/anesthesia_sim/app/` and 26 in `app/controller.py`. The capture's 131 and 30 came from a count it did not record. `PL-22T5`'s plan, point 6, left interface strings to this item.

**Why it matters.** Interface text is what a learner reads beside a value: a notice, a label, a refusal. `PL-J1ZM`'s design sends interface strings of 30 words or more through the copy editor, and none goes through it now. Some of the long strings under `core/` are refusal messages, which the safety-critical standard requires to name the condition and the value that failed it, so they need a reader row that says so. This is work on `PL-J1ZM`'s fix, so the pause on new workflow mechanisms does not hold it.

**Done when.** A changed string literal of `MIN_WORDS` words or more in a file under `src/` is printed for the copy editor as a unit of its own, with readers from a row of the reader table that a docstring in the same file does not take. A test in `tests/unit/test_new_prose.py` pins both.

**Generator check.** This item is a remainder of `PL-J1ZM`'s fix. The fact is which text the copy editor reads, and the reader table is its one record. With `PL-SMM2`, two items concern that fact, so it needs no new head. It is not a re-entry, because `PL-22T5` left it out of scope on purpose.

**Done 2026-11-04.** `tools/new_prose.py` now reads every string literal in a Python file that is not a docstring as a unit of its own. An f-string is one unit, and strings that Python joins because they stand side by side are one unit. Two new rows in the reader table, for string literals in `src/`, give those units a learner who reads a notice beside a value and a Python developer who reads a refusal in a log. A row whose first cell says "string literals" covers only string units, and every other row covers only docstrings and comments, so a notice and the docstring beside it get different readers. `--compare` counts a removed value inside a string literal where a string row names the file, so a refusal that loses the value it names is reported. Four tests in `tests/unit/test_new_prose.py` cover the units, both reader choices and the lost value.

A count on 2026-11-04 with `string_units`, which reads a joined string as one unit, found 69 string literals of 30 words or more under `src/`: 33 under `core/`, 26 under `app/` (10 of them in `app/controller.py`) and 10 under `layout/`. The `ast` method that "Checked 2026-11-04" names above, which counts each piece of a joined string on its own, found 71. Neither reproduces that paragraph's 119. The paragraph names its method in one clause and records no command, so the difference cannot be traced.
