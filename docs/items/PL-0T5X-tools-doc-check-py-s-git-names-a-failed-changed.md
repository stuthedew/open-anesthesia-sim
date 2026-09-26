---
id: PL-0T5X
title: tools/doc_check.py's _git names a failed changed-path read as git -c, since changed_path_args now opens every read with -c core.quotePath=false, and a changed path that is not UTF-8 raises UnicodeDecodeError out of it instead of GitUnanswered
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-26 with the path-listing step of PL-PVW2
added: 2026-09-26
payoff: a close-out sweep that cannot read git names the command that failed and says so, instead of naming git -c or ending make check in a traceback
verify: grep -q 'def test_git_names_a_failed_read_by_its_subcommand' tests/unit/test_doc_check.py && grep -q 'def test_git_answers_an_undecodable_path_as_unanswered' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py's _git names a failed changed-path read as git -c, since changed_path_args now opens every read with -c core.quotePath=false, and a changed path that is not UTF-8 raises UnicodeDecodeError out of it instead of GitUnanswered

Found 2026-09-25 by PL-8HSX, which put `-c core.quotePath=false` ahead of the subcommand in `vcs.changed_path_args`. `tools/doc_check.py`'s `_git` names a failed read by `args[0]`, so when `_changed_paths`' diff read fails it reports `` `git -c` exited 128: ... `` rather than `` `git diff` ``; git's own stderr line still names the cause. And git now prints a changed path as written, so a path whose bytes are not UTF-8 raises `UnicodeDecodeError` out of `subprocess.run(text=True)` as a traceback, where `vcs._run_git` and `verify._git` answer it as unread since PL-8HSX.

The fix was written and tested inside PL-8HSX, then taken out so that pull request stayed inside `subprojects/docket/` and `bin/docket arm` could arm it on green: import `subcommand_of` from `docket.vcs` beside `changed_path_args`, build `` command = f"`git {subcommand_of(args)}`" `` at the top of `_git` and use it in both messages, and add `except UnicodeDecodeError as error: raise GitUnanswered(f"{command} printed a path this cannot read: {error}") from error` after the `GIT_UNAVAILABLE` clause. `verify._git` in `subprojects/docket/src/docket/verify.py` is the same fix already landed. The wider question, one helper for "which subcommand an argv names" that `tools/` imports, is PL-PVW2's.

**Why it matters.** The close-out sweep's error names the wrong git command, and a path git prints in bytes this cannot decode ends `make check` in a traceback instead of the sweep's own "could not read" message.

**Done when.** `tools/doc_check.py`'s `_git` names a failed read by `vcs.subcommand_of` and answers a path it cannot decode as `GitUnanswered`, and `test_git_names_a_failed_read_by_its_subcommand` and `test_git_answers_an_undecodable_path_as_unanswered` hold each.

**Generator check.** An instance of `PL-PVW2`'s fact, which spelling of a repeated predicate is the answer, here for which files a change touched: before this, one reader split git's listing with `.split()`, eleven with `splitlines()`, three on `\n` alone and two on NUL, and the untracked half read `ls-files` quoted. Fixed at the head, as step 3 of its split, so it is not a head of its own.
