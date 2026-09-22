---
id: PL-X229
title: tools/doc_check.py candidates diffs --base against the working tree rather than from the merge base, so run with --base origin/main after main has moved it lists every file main changed since the fork as this branch's candidates, and the close-out docs sweep is handed other branches' documentation to review
status: untriaged
added: 2026-09-22
---

**Problem.** tools/doc_check.py candidates diffs --base against the working tree rather than from the merge base, so run with --base origin/main after main has moved it lists every file main changed since the fork as this branch's candidates, and the close-out docs sweep is handed other branches' documentation to review

**Seen 2026-09-22 closing `PL-SZJ2`.** `format_candidates` reads
`git diff --name-only BASE` (`tools/doc_check.py`, `_git(root, "diff",
"--name-only", base)`), which compares BASE's tree with the working tree. With
`--base origin/main` fetched after `#905` (`PL-FPY2`) merged, the output named
`app/dashboard_frame.py`, `app/qt_widgets.py` and `app/theme.py` - files this
branch never touched - ahead of the three it did. `--base` set to the merge
base gave the right list. The close-out mode tells a session to run it with a
ref of its choosing, and a session that runs for an hour usually finds `main`
has moved. It over-reports rather than under-reports, so nothing is missed, but
the extra lines are other sessions' work, which trains a reader to skim the
sweep. The likely fix is to diff from `git merge-base BASE HEAD` (plus the
working tree), keeping the help text's meaning of `--base`.
