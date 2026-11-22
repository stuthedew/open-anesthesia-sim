---
id: PL-N046
title: An item that deletes code or changes only a document keeps one grep -qF or ! grep -qF condition, checked once when it closes and not replayed afterwards
priority: P2
effort: S
status: done
classes: infra
feature: standing-weight
milestone: v0.6.19
touches: subprojects/docket/src/docket, subprojects/docket/tests, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md, .claude/skills/docket/modes/close-out.md
added: 2026-11-21
closed: 2026-11-21
pr: 2182
payoff: a document or deletion item is checked once, on the branch that closes it, and its text search is never run again
tests: subprojects/docket/tests/test_done.py::test_words_a_document_wraps_over_two_lines_are_found, subprojects/docket/tests/test_done.py::test_any_other_command_is_refused_by_name, subprojects/docket/tests/test_done.py::test_words_no_file_holds_are_a_fault
---

**Problem.** An item that deletes code or changes only a document keeps one grep -qF or ! grep -qF condition, checked once when it closes and not replayed afterwards

**Why it matters.** The project owner chose this form on 2026-11-20 (`PL-LFJZ`, the count of what a test-named done-condition would have prevented). Of the 794 `grep` conditions that name no test, 407 check a document and 79 more check only that code text is gone. A sentence in a developer document that restates a fact of the tree takes the form agreed under `PL-WKKH`: the requirement, then the test that checks it. Checking once at close ends the faults of `PL-RR1N` (a phrase split by line-wrapping) and `PL-205P` (a condition that read the remote), which both came from the replay running a condition long after the work.

**What to do.** When an item closes carrying a `verify:`, `bin/docket check` on the closing branch holds the command to one clause, `grep -qF 'words' path` or `! grep -qF 'words' path`, and evaluates it once by reading the files itself. It refuses a `grep -qF` that reads a Python file for text the work adds, because that work is shown by a test in `tests:` (`PL-FN11`). An item already closed on the default branch is never read again. A release item, which carries `resource: release-train`, keeps the command it has.

`.claude/skills/docket/modes/triage.md` says which kind of item uses which form. It also says that a sentence in a developer document that restates a fact of the tree is written as the requirement and then the test that checks it, as `PL-WKKH` (the streamlining questions) agreed.

**Done when.** `bin/docket check` on a branch that closes an item fails when the item's `verify:` is not one `grep -qF` or `! grep -qF` clause, or when that clause does not hold on the branch.

**Generator check.** None: work the project owner chose in `PL-LFJZ` (the count of what a test-named done-condition would have prevented).

**Built 2026-11-21, in `PL-FN11`'s pull request.** docket reads the words and the files from the command and compares them itself, with each run of white space treated as one space, so no shell runs and a phrase wrapped over two lines is found. A file the tree does not hold is a fault under `! grep` too. A search for words added to a Python file is refused, because a test shows that work. `PL-FN11` (code items record their tests when they close) lists the documents checked.
