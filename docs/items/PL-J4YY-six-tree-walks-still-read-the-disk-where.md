---
id: PL-J4YY
title: Six tree walks still read the disk where tracked_files asks git after PL-9NZ3 - glyph_check.problems (two), ignore_check.directives and doc_check.check_named_tests in tools, and docket's grep._walk and instructions._markdown_under, which cannot import tools/ - so the home for the tracked-file list wants to move into docket.vcs, which is already git's one runner and which tracked_files bypasses (fact_home_check baselines it as a git site)
status: untriaged
added: 2026-10-12
---

**Problem.** Six tree walks still read the disk where tracked_files asks git after PL-9NZ3 - glyph_check.problems (two), ignore_check.directives and doc_check.check_named_tests in tools, and docket's grep._walk and instructions._markdown_under, which cannot import tools/ - so the home for the tracked-file list wants to move into docket.vcs, which is already git's one runner and which tracked_files bypasses (fact_home_check baselines it as a git site)

**Found 2026-10-12, closing `PL-9NZ3`.** That item moved the walks it named
onto `workflow_paths_check.tracked_files` through one filter,
`tracked_under`, and drained them from `tools/fact_home_check.py`'s
`BASELINE`. The `walk` entries still there name these six, which no open
item names:

- `tools/glyph_check.py` `problems` (two), `tools/ignore_check.py`
  `directives`, and `tools/doc_check.py` `check_named_tests` - each an `rglob`
  that reads an untracked file, and the first two could take `tracked_under`
  as the others did. (`doc_check._markdown_under` is the seventh and is
  `PL-NNVJ`'s, which folds it into `docket.instructions`'s copy.)
- `subprojects/docket/src/docket/grep.py` `_walk` and
  `subprojects/docket/src/docket/instructions.py` `_markdown_under`, which
  cannot use the list at all: the docket package cannot import `tools/`.

**Why it matters.** Same as `PL-9NZ3`'s: a walk and the list part on the first
untracked file - a scratch module, another checkout under
`.claude/worktrees/` - and a check answers for a file the repository does not
hold. The docket pair is the design half. `tracked_files` runs git itself,
which `fact_home_check` baselines as a `git` site outside `docket.vcs`, so the
natural home for the list is `docket.vcs`, which both docket and every tool
already import; `tracked_under` and the non-checkout walk would move with it.

**Done when.** No `walk` entry is left in `fact_home_check.BASELINE`, the
walk home in its `HOMES` names where the list moved, and a test pins an
untracked file left out of a docket walk.

**Generator check.** A post-close instance of `PL-5DZ8`'s fact - which
spelling of a repeated predicate is the answer - and of the same predicate
`PL-9NZ3` fixed, which files the repository holds. Not a new head: it is the
remainder of a sweep that named its sites, filed so it is not lost.
