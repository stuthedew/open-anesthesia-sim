---
id: PL-PQ0R
title: Since core.quotePath went off, a changed-path read that splits git's listing with splitlines reads a path holding U+2028, U+2029 or U+0085 as two paths
status: untriaged
added: 2026-09-26
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
