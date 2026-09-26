---
id: PL-RLTK
title: vcs.landed_whole reads a commit that restores a file to content the default branch held earlier in its history as a commit the base took whole, because _base_blobs collects every blob the base's history ever held rather than its tip's: bin/docket branch told #1118's session its open pull request had merged, not to merge and push, and to restart the branch on origin/main, since c69bad17 put pr-title.yml back to the blob #1056 wrote and #1068 replaced
status: untriaged
added: 2026-09-26
---

**Problem.** vcs.landed_whole reads a commit that restores a file to content the default branch held earlier in its history as a commit the base took whole, because _base_blobs collects every blob the base's history ever held rather than its tip's: bin/docket branch told #1118's session its open pull request had merged, not to merge and push, and to restart the branch on origin/main, since c69bad17 put pr-title.yml back to the blob #1056 wrote and #1068 replaced

**Observed 2026-09-26 on `claude/pr-body-storage-cnnpme`, `#1118` open.** Found
by running `landed_whole`'s own pieces against the branch: `_landing_split`
put `.github/workflows/pr-title.yml` and
`.claude/skills/docket/modes/close-out.md` in `landed`, though neither file had
changed on `origin/main` since the fork point. Each had been put back,
byte for byte, to its content from before `#1068`
(`git log --find-object` on the branch's `pr-title.yml` blob names `#1056`,
which wrote it, and `#1068`, which replaced it). `c69bad17` touched
`pr-title.yml` alone, so `_commits_by_landing` counted it as taken whole, and
`format_branch_state` printed the merged verdict and the restart recipe. The
session-start digest's `left_behind_check.py` line contradicted it ("#1118 is
open on it ... this ref comparison wins"), but `bin/docket branch` run on its
own prints no second opinion. Any branch that reverts a file to an earlier
version of itself is exposed: retiring a feature is the common case.

A lead, not a decision: a squash merge of this branch writes its blobs onto
the base *after* the fork point, so asking only for blobs the base gained
since then (`rev-list --objects <fork>..<base>`) would exclude a restored
earlier blob. Whether that costs `orphaned`, which shares `_base_blobs`, any
recall is the fixer's to measure.
