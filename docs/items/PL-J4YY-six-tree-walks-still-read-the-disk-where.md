---
id: PL-J4YY
title: Six tree walks still read the disk where tracked_files asks git after PL-9NZ3 - glyph_check.problems (two), ignore_check.directives and doc_check.check_named_tests in tools, and docket's grep._walk and instructions._markdown_under, which cannot import tools/ - so the home for the tracked-file list wants to move into docket.vcs, which is already git's one runner and which tracked_files bypasses (fact_home_check baselines it as a git site)
priority: P2
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/instructions.py, subprojects/docket/src/docket/grep.py, tools/workflow_paths_check.py, tools/fact_home_check.py, tools/glyph_check.py, tools/ignore_check.py, tools/doc_check.py, tests/unit/test_workflow_paths_check.py, tests/unit/test_glyph_check.py, tests/unit/test_ignore_check.py, tests/unit/test_doc_check.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_instructions.py, docs/items/PL-NNVJ-doc-check-roadmap-instructions-and-notes-copy.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-10-12
payoff: a check or the instruction-age advisory answers only for files the repository holds, so a scratch module or another checkout under .claude/worktrees/ no longer fails make check or reaches a grooming pass
verify: grep -q 'def tracked_files' subprojects/docket/src/docket/vcs.py && ! grep -q '("walk", ' tools/fact_home_check.py && grep -q 'def test_an_untracked_markdown_file_is_not_read' subprojects/docket/tests/test_instructions.py
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

**Reproduced 2026-10-12, at `dde2082c`.** An untracked
`src/anesthesia_sim/app/zz_scratch_untracked.py` holding U+2603 made
`python3 tools/glyph_check.py` exit 1 naming it, and an untracked
`.claude/skills/zz_scratch_untracked.md` holding "Measured 2025-01-01, a
fact." came back from `docket.instructions.read` as a dated assertion of the
instruction set.

**Re-confirmed 2026-10-12, and the shape changed in two places.**

- **`grep._walk` reads a different fact, and stays a walk.** It is the
  model of what `grep -r` reads, so `wrapped` can say why a `verify:`
  command's `grep` failed, and `grep -r` reads the disk: an untracked file,
  an ignored one, another checkout. Read from the tracked list, the model
  would explain a `grep` that reads other files than the one it models,
  which is the wrong answer this move exists to remove. So it leaves
  `BASELINE` by being named a home of its own beside the tracked list, with
  that reason, rather than by reading the list.
- **`doc_check._markdown_under` leaves `BASELINE` here too**, or Done when
  cannot hold. It is a verbatim copy of `docket.instructions`'s, so the fold
  `PL-NNVJ` names for it is the cheaper route than a second conversion: doc_check
  imports the one copy, and `PL-NNVJ`'s brief is told the part is done.

**What is built.** `tracked_files` and `tracked_under` move into
`docket.vcs`, asking `_run_git` for `ls-files -z` rather than running git
themselves, with `SKIP_DIRS` and the walk for a tree that is not a checkout;
`workflow_paths_check` re-exports both, so the nine tools importing them are
unchanged. A checkout git ran in and did not list still raises - as
`vcs.Unlisted` now, which `workflow_paths_check` reports as it reported the
`CalledProcessError` - except for `docket.instructions`, an advisory under a
package whose reads never raise on git, which walks it as a checkout git
cannot be launched in. `glyph_check.problems`, `ignore_check.directives` and
`doc_check.check_named_tests` read `tracked_under`.

**Generator check.** Draining `PL-4S6C`'s baseline, not a re-entry: the six
are entries `tools/fact_home_check.py` recorded the day it landed, so no new
reader arrived and that head's spent verdict - a new reader fails `make
check` - holds. The fact is `PL-5DZ8`'s, which spelling of a repeated
predicate is the answer, here which files the repository holds; the move into
`docket.vcs` is what lets docket reach the one spelling.
