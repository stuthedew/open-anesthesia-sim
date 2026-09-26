---
id: PL-Y2L6
title: vcs.working_paths and doc_check._changed_paths read untracked files with ls-files, which still quotes a non-ASCII path, while their diff reads through changed_path_args now print it as written, so each reader names one file two ways
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, tools/doc_check.py, subprojects/docket/tests/test_vcs.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-26 with the path-listing step of PL-PVW2
added: 2026-09-25
closed: 2026-09-26
pr: 1078
payoff: an untracked non-ASCII file is found by bin/docket new's near-duplicate search and by the close-out sweep instead of being missed
verify: grep -q 'def test_working_paths_names_an_untracked_non_ascii_file_as_written' subprojects/docket/tests/test_vcs.py && grep -q 'def test_changed_paths_names_an_untracked_non_ascii_file_as_written' tests/unit/test_doc_check.py
---

**Problem.** vcs.working_paths and doc_check._changed_paths read untracked files with ls-files, which still quotes a non-ASCII path, while their diff reads through changed_path_args now print it as written, so each reader names one file two ways

Found 2026-09-25 by PL-8HSX, git 2.43.0. `git ls-files --others --exclude-standard` prints an untracked `src/anesthesia_sim/core/new é.py` as `"src/anesthesia_sim/core/new \303\251.py"`, and `-z` or `-c core.quotePath=false` prints it as written. PL-8HSX put `core.quotePath=false` into `vcs.changed_path_args`, so the `diff` halves of `vcs.working_paths` (the near-duplicate search `bin/docket new` runs) and `tools/doc_check.py`'s `_changed_paths` (the close-out sweep's list of changed files) now print such a path verbatim while their `ls-files` half does not. Not the protected-path audit, which reads `status --porcelain -z`. Consequence is mild: a near-duplicate or a stale citation of an untracked non-ASCII file is missed. An instance of PL-PVW2's "which files a branch changed", and a candidate member of its `root-cause-of:`.

**Why it matters.** One reader names one file two ways, so an untracked non-ASCII file is missed by `bin/docket new`'s near-duplicate search and by the close-out sweep's list of changed files.

**Done when.** The untracked half of `vcs.working_paths` and of `tools/doc_check.py`'s `_changed_paths` reads `ls-files -z` through the same parse as the diff half, and `test_working_paths_names_an_untracked_non_ascii_file_as_written` and `test_changed_paths_names_an_untracked_non_ascii_file_as_written` each see an untracked `new é.py` named as written.

**Generator check.** An instance of `PL-PVW2`'s fact, which spelling of a repeated predicate is the answer, here for which files a change touched: before this, one reader split git's listing with `.split()`, eleven with `splitlines()`, three on `\n` alone and two on NUL, and the untracked half read `ls-files` quoted. Fixed at the head, as step 3 of its split, so it is not a head of its own.
