---
id: PL-15TY
title: tools/headless_worker.py reports a failed git clone by the first line of git's stderr, which is the 'Cloning into ...' progress line, so the real cause (authentication, a missing reference repository) is never shown: report the last non-progress line, or the whole stderr
priority: P2
effort: S
status: ready
classes: defect
touches: tools/headless_worker.py, subprojects/docket/src/docket/vcs.py, tests/unit/test_headless_worker.py
added: 2026-10-20
payoff: a failed clone says why it failed, so the owner does not rerun it by hand to find out
verify: grep -q 'PL-15TY' tests/unit/test_headless_worker.py
---

**Problem.** tools/headless_worker.py reports a failed git clone by the first line of git's stderr, which is the 'Cloning into ...' progress line, so the real cause (authentication, a missing reference repository) is never shown: report the last non-progress line, or the whole stderr

**Why it matters.** On 2026-10-20 the project owner's MacBook printed `headless_worker: \`git clone\` exited 128: Cloning into '/Users/.../pl-k88z-worker-20261020T041633'...` and nothing else. `GitCall.said` in `subprojects/docket/src/docket/vcs.py` keeps the first non-empty stderr line, and `git clone` always writes its progress line first. So every clone failure reads the same, and the owner has to rerun the clone by hand to learn why. That breaks the apparatus rule that an answer must be true or say what it could not read.

**Done when.** A failed clone's message names git's actual error line, such as `fatal: could not read Username` or `fatal: reference repository ... is not a local repository`, and a test pins that against stderr that opens with `Cloning into`.

**Generator check.** Not a head: one reader of `GitCall.said` whose first stderr line is progress, not the error.

**Worked.** The fix is in `GitCall.said` in `subprojects/docket/src/docket/vcs.py`, not in `tools/headless_worker.py`, so every reader of `GitCall.reason` gets it and `headless_worker.py` itself is unchanged. The brief offered "the last non-progress line, or the whole stderr"; I chose neither literally. `said` now returns the first stderr line that starts with `fatal:` or `error:`, the prefixes git puts on its failure messages, and falls back to the first non-empty line as before. I chose that over "the last line" because git often writes `hint:` lines after an `error:` line, as on a rejected push, and the last line would then be a hint. The new module constant is `_GIT_FAILURE_PREFIXES`. There are two tests. One builds a `GitCall` by hand from the brief's own example, `Cloning into` followed by `fatal: could not read Username ...`, and pins the whole reason string. The other runs a real `git clone --reference <missing path>` through `headless_worker.git_or_refuse`. It asserts only that the message carries a `fatal:` line and no `Cloning into`, because the exact wording is git's and varies by version (git printed `fatal: path '...' does not exist` here). Both tests fail against the code before the fix: run `git stash push subprojects/docket/src/docket/vcs.py && uv run pytest -q tests/unit/test_headless_worker.py -k "failed_clone or missing_reference"`, and both fail with the reason `` `git clone` exited 128: Cloning into '...'... ``. The test file now imports `docket.vcs.GitCall`.

**Blocked.** `make check` exited 2 on this host, for a cause outside this item. pytest reported "2 failed, 10096 passed, 3 skipped". The two failures were `tests/unit/test_makefile_reference.py::test_the_makefile_readers_read_generated_makefiles_as_make_does` and `::test_the_makefile_readers_read_the_tracked_makefile_as_make_does`, each with "AssertionError: /usr/bin/make is GNU Make 3.81; the comparison needs version 4 or newer". `PL-44R1` already records this failure; that item is only on `origin/claude/pl-70m6-worker` so far. Because the failure stopped `make check` at pytest, I ran the gate's remaining steps one at a time after committing. All passed except `bin/docket check --verify --verify-base origin/main`, which exited 1 with the error "PL-15TY is open but its `verify:` command already passes". That error is what a finished item reports while its status stays open, and this file's status is the reviewer's to change, not mine. I filed it as `PL-WJJ8`. The work above is complete, and its own tests and `verify:` pass. The gate needs a host with GNU Make 4 or newer before it can report green.
