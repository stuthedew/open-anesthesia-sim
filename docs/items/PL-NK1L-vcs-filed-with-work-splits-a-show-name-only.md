---
id: PL-NK1L
title: vcs.filed_with_work splits a show --name-only listing on whitespace, so a path holding a space is reported as two paths
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-26 with the path-listing step of PL-PVW2
added: 2026-09-25
payoff: the work docket reports beside an item's filing names each path the filing commit changed, one holding a space included, instead of two paths that do not exist
verify: grep -q 'def test_filed_with_work_reads_a_path_holding_a_space' subprojects/docket/tests/test_vcs.py
---

**Problem.** vcs.filed_with_work splits a show --name-only listing on whitespace, so a path holding a space is reported as two paths

Found 2026-09-25 by PL-8HSX. `vcs.filed_with_work` reads the filing commit's paths with `run(changed_path_args("show", "--format=", "--name-only", commit), root).split()`. `--name-only` does not quote a space, so `src/a b.py` arrives as the two words `src/a` and `b.py`, and both are reported as work filed beside the item. Every other `--name-only` reader in `vcs.py` splits on lines. An instance of PL-PVW2's "which files a branch changed", and a candidate member of its `root-cause-of:`.

**Why it matters.** `filed_with_work` is how `docket` reports work committed beside an item's filing, so a path holding a space comes back as two paths, neither of which exists, and a reader chasing them finds nothing.

**Done when.** `filed_with_work` reads the filing commit's paths through `vcs.listed_paths`, and `test_filed_with_work_reads_a_path_holding_a_space` commits `src/a b.py` beside a filing and sees it reported once, as written.

**Generator check.** An instance of `PL-PVW2`'s fact, which spelling of a repeated predicate is the answer, here for which files a change touched: before this, one reader split git's listing with `.split()`, eleven with `splitlines()`, three on `\n` alone and two on NUL, and the untracked half read `ls-files` quoted. Fixed at the head, as step 3 of its split, so it is not a head of its own.
