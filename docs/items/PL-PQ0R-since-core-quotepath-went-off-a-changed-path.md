---
id: PL-PQ0R
title: Since core.quotePath went off, a changed-path read that splits git's listing with splitlines reads a path holding U+2028, U+2029 or U+0085 as two paths
priority: P3
effort: M
status: done
classes: defect
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/verify.py, tools/doc_check.py, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-26 with the path-listing step of PL-PVW2
added: 2026-09-26
closed: 2026-09-26
pr: 1078
payoff: every changed-path read reports the paths a change touched whatever characters they hold, so arm, change_landed and the protected-path audit decide on paths that exist
verify: grep -q 'def test_a_path_listing_is_read_one_way' subprojects/docket/tests/test_vcs.py
---

**Problem.** Since core.quotePath went off, a changed-path read that splits git's listing with splitlines reads a path holding U+2028, U+2029 or U+0085 as two paths

**Found 2026-09-26 while closing `PL-139L`.** `vcs.changed_path_args` has put
`-c core.quotePath=false` on every changed-path read since `PL-8HSX`
(2026-09-25). Off, git prints a byte above 0x80 as written, and U+2028, U+2029
and U+0085 are all such bytes in UTF-8, so a path holding one reaches the reader
unquoted. A reader that then splits with `str.splitlines()` breaks it in two.
Measured on git 2.43.0 in a scratch repository: `git -c core.quotePath=false
diff --no-renames --name-only` printed `'a\u2028b.py\nc\x85d.py\n"e\\ff.py"\n'`,
which `splitlines()` read as `['a', 'b.py', 'c', 'd.py', '"e\\ff.py"']`. A form
feed or `\x0b` in a path is still quoted either way. `changed_path_args` has 19
call sites: 13 in `vcs.py` (`change_landed` and `_superseded` among them), two
each in `claims.py` and `verify.py`, one each in `arming.py` and
`tools/doc_check.py`. Both in `verify.py` are `changed_paths`, which reads with
`-z` and is safe. `change_landed` and `_superseded` split with `splitlines()`;
the other 15 have not been read for which split they use.

No path in the tree holds such a character today, so this is a paste risk, not
routine. It is the path-side twin of `PL-139L`'s subject readers. It is also a
candidate member of `PL-PVW2`'s "which files a branch changed", as `PL-NK1L` is.

**Why it matters.** A listing split at a character that is not git's separator reports paths that do not exist, and every read `changed_path_args` builds is such a listing: `arm` decides auto-merge from one, `change_landed` whether a commit's change is on the default branch, and `verify`'s protected-path audit what a delegated branch touched.

**Done when.** Every read `changed_path_args` builds asks git for its `-z` form, the one in which git quotes no path and ends each with NUL, and every reader takes its paths from that through one parse in `vcs.py`. `test_a_path_listing_is_read_one_way` commits paths holding a space, U+2028, U+0085, a non-ASCII letter, a tab, a newline, `"` and `\` and sees each reader name each one as written.

**Generator check.** An instance of `PL-PVW2`'s fact, which spelling of a repeated predicate is the answer, here for which files a change touched: before this, one reader split git's listing with `.split()`, eleven with `splitlines()`, three on `\n` alone and two on NUL, and the untracked half read `ls-files` quoted. Fixed at the head, as step 3 of its split, so it is not a head of its own.
