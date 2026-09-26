---
id: PL-0T5X
title: tools/doc_check.py's _git names a failed changed-path read as git -c, since changed_path_args now opens every read with -c core.quotePath=false, and a changed path that is not UTF-8 raises UnicodeDecodeError out of it instead of GitUnanswered
status: untriaged
feature: one-answer
added: 2026-09-26
---

**Problem.** tools/doc_check.py's _git names a failed changed-path read as git -c, since changed_path_args now opens every read with -c core.quotePath=false, and a changed path that is not UTF-8 raises UnicodeDecodeError out of it instead of GitUnanswered

Found 2026-09-25 by PL-8HSX, which put `-c core.quotePath=false` ahead of the subcommand in `vcs.changed_path_args`. `tools/doc_check.py`'s `_git` names a failed read by `args[0]`, so when `_changed_paths`' diff read fails it reports `` `git -c` exited 128: ... `` rather than `` `git diff` ``; git's own stderr line still names the cause. And git now prints a changed path as written, so a path whose bytes are not UTF-8 raises `UnicodeDecodeError` out of `subprocess.run(text=True)` as a traceback, where `vcs._run_git` and `verify._git` answer it as unread since PL-8HSX.

The fix was written and tested inside PL-8HSX, then taken out so that pull request stayed inside `subprojects/docket/` and `bin/docket arm` could arm it on green: import `subcommand_of` from `docket.vcs` beside `changed_path_args`, build `` command = f"`git {subcommand_of(args)}`" `` at the top of `_git` and use it in both messages, and add `except UnicodeDecodeError as error: raise GitUnanswered(f"{command} printed a path this cannot read: {error}") from error` after the `GIT_UNAVAILABLE` clause. `verify._git` in `subprojects/docket/src/docket/verify.py` is the same fix already landed. The wider question, one helper for "which subcommand an argv names" that `tools/` imports, is PL-PVW2's.
