---
id: PL-Y2L6
title: vcs.working_paths and doc_check._changed_paths read untracked files with ls-files, which still quotes a non-ASCII path, while their diff reads through changed_path_args now print it as written, so each reader names one file two ways
status: untriaged
feature: one-answer
added: 2026-09-25
---

**Problem.** vcs.working_paths and doc_check._changed_paths read untracked files with ls-files, which still quotes a non-ASCII path, while their diff reads through changed_path_args now print it as written, so each reader names one file two ways

Found 2026-09-25 by PL-8HSX, git 2.43.0. `git ls-files --others --exclude-standard` prints an untracked `src/anesthesia_sim/core/new é.py` as `"src/anesthesia_sim/core/new \303\251.py"`, and `-z` or `-c core.quotePath=false` prints it as written. PL-8HSX put `core.quotePath=false` into `vcs.changed_path_args`, so the `diff` halves of `vcs.working_paths` (the near-duplicate search `bin/docket new` runs) and `tools/doc_check.py`'s `_changed_paths` (the close-out sweep's list of changed files) now print such a path verbatim while their `ls-files` half does not. Not the protected-path audit, which reads `status --porcelain -z`. Consequence is mild: a near-duplicate or a stale citation of an untracked non-ASCII file is missed. An instance of PL-PVW2's "which files a branch changed", and a candidate member of its `root-cause-of:`.
