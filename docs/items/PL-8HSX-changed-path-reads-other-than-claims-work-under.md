---
id: PL-8HSX
title: Changed-path reads other than claims.work_under_record leave core.quotePath on, so git prints a non-ASCII path in quoted octal and verify's protected-path audit compares that form: a new src/anesthesia_sim/core/café.py passes as 'none touched'
status: untriaged
feature: one-answer
added: 2026-09-25
---

**Problem.** Changed-path reads other than claims.work_under_record leave core.quotePath on, so git prints a non-ASCII path in quoted octal and verify's protected-path audit compares that form: a new src/anesthesia_sim/core/café.py passes as 'none touched'

Found 2026-09-25 by PL-KR69's triage, git 2.43.0, in a scratch worktree off `origin/main`: a commit adding `src/anesthesia_sim/core/café.py` gives `verify.changed_paths` the one path `"src/anesthesia_sim/core/caf\303\251.py"`, quotes included, and `_within` matches it against no protected path. The working-tree half reads `git status --porcelain`, which quotes the same way. `-c core.quotePath=false` still quotes a path holding a tab, newline, `"` or `\`; only `-z` output is verbatim. PL-KR69's `vcs.changed_path_args` is the one place every changed-path read now builds its argv, so the fix lands there, but moving `-c` ahead of the subcommand changes `args[0]` in every test fake keyed on it.
