---
id: PL-X229
title: tools/doc_check.py candidates diffs --base against the working tree rather than from the merge base, so run with --base origin/main after main has moved it lists every file main changed since the fork as this branch's candidates, and the close-out docs sweep is handed other branches' documentation to review
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-22
payoff: the close-out docs sweep lists only the documentation this branch's own change could have made stale - 13 lines rather than 184 in the reproduction - so a session reads it instead of skimming past other branches' work
verify: grep -q 'def test_candidates_ignores_what_the_base_gained_after_the_fork' tests/unit/test_doc_check.py
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

**Reproduced 2026-09-23**, in a scratch clone detached at `cd5ad3f6` with one
edited file, while `origin/main`'s tip `a65b440c` stood two merges (`#932`,
`#933`) past it. `python3 tools/doc_check.py --root CLONE candidates --base
a65b440c` named 11 changed files and 184 documentation lines, 10 of the files
being those two merges' work (`tools/left_behind_check.py`,
`subprojects/docket/src/docket/verify.py` and eight more). With `--base` set to
`git merge-base a65b440c HEAD` it named the one edited file and 13 lines. Both
call sites read the same two-point diff: `_changed_paths` for the file list and
`changed_tokens` for each file's `git diff -U0 BASE` hunks. So a heading the
base gained in a document this branch never opened would also read as one this
branch removed, since `REMOVED_HEADING_RE` matches the `-` side.

**Why it matters.** The close-out sweep is where a session checks that nothing
its change touched has left a statement stale, and this project treats a stale
statement as a safety issue rather than tidiness. A list padded with other
sessions' files buries the lines this branch owes a reading and teaches the
reader to skim it. `CLAUDE.md` names that as the failure of a check that fires
without changing a decision. It is also the common case, not an edge one: a
branch open for an hour usually finds `main` has moved, and close-out asks for
a ref of the session's choosing.

**Done when.** `candidates --base BASE` diffs the working tree from `git
merge-base BASE HEAD` at both call sites, so a base that has moved past the
fork adds nothing to the list, and the default `--base HEAD` still reports only
uncommitted changes. `test_candidates_ignores_what_the_base_gained_after_the_fork`
in `tests/unit/test_doc_check.py` builds a repository whose base gained a
commit after the fork and asserts that commit's files are not reported.

**Generator check.** A one-off. `candidates` has diffed BASE against the
working tree since `PL-032` created the mode (2026-08-24), and the default
`--base HEAD` never meets a moved base. The store's merge-base items (`PL-8MJ3`,
`PL-MGNC`) concern docket's in-flight reads in `vcs.py`, a different fix site,
so they share no mechanism with this.
