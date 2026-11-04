---
id: PL-BXD5
title: tools/new_prose.py's CONTEXT_ROWS = 4, the lines of code printed around each docstring or comment for the copy editor, has no recorded reason: PL-PRCS set it in 20eb2fd29 and neither the commit nor the item says why 4, or what fewer or more rows would cost or catch
priority: P3
effort: S
status: done
classes: docs
feature: reader-first-prose
touches: tools/new_prose.py
added: 2026-11-04
closed: 2026-11-04
pr: 2030
payoff: a session changing how much code the copy editor sees knows what four rows buy and what a different number would cost
verify: ! grep -qF 'recorded no reason for that number' tools/new_prose.py
---

**Problem.** tools/new_prose.py's CONTEXT_ROWS = 4, the lines of code printed around each docstring or comment for the copy editor, has no recorded reason: PL-PRCS set it in 20eb2fd29 and neither the commit nor the item says why 4, or what fewer or more rows would cost or catch

**Checked 2026-11-04.** `git log -S 'CONTEXT_ROWS = 4'` finds only `20eb2fd29` (`PL-PRCS`). The comment above the constant already says what the rows are for and that more rows lengthen the file the copy editor reads. It ends "`PL-PRCS` set it at 4 and recorded no reason for that number (`PL-22T5`)".

**Why it matters.** A session that changes how much code the copy editor sees cannot tell whether four rows are enough to show what a docstring's "it" points at, or whether fewer would do. The plain-writing rule asks each chosen value for its reason from a record, and this one has none.

**Done when.** The comment above `CONTEXT_ROWS` gives the reason for the number from a record: a measurement on the copy editor's test set or on a branch's units, or a stated choice with what fewer or more rows would cost. The sentence saying that no reason was recorded is gone.

**Generator check.** This is a one-off, about one missing fact: why `CONTEXT_ROWS` is 4. It was filed under the plain-writing rule's instruction to file an item when a trace of a value's history finds no reason. No other open item reports a missing reason.

**Done 2026-11-04.** The comment above `CONTEXT_ROWS` now gives its reason from a measurement, and the value stays 4. The line that a docstring most needs shown above it is the `def` or `class` it describes. An `ast` walk went over every Python file in `src/`, `tests/`, `tools/` and `subprojects/docket/src/docket/`. For each function and class whose body opens with a docstring, it counted the rows from the `def` or `class` line down to the docstring. Of 7,943 docstrings, 82.9% start 1 row below, 97.3% within 3 rows and 97.3% within 4, 98.0% within 6 and 99.2% within 8. The jump between 1 and 3 rows comes from signatures that wrap onto lines of their own. Three rows therefore show the `def` as often as 4 do, and the fourth row is a margin of one line on each side. Comments were not measured, because a comment has no single line it describes.
