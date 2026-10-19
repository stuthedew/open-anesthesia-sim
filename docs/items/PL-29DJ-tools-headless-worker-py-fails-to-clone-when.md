---
id: PL-29DJ
title: tools/headless_worker.py fails to clone when its checkout is a linked git worktree: git clone --reference names the worktree, which has a .git file rather than a repository, so five of tests/unit/test_headless_worker.py's tests fail under bin/docket verify run from a worktree
priority: P2
effort: S
status: done
classes: defect
touches: tools/headless_worker.py, tests/unit/test_headless_worker.py
deferred-from: v0.6.0 - a workflow-lane runner defect outside the layout release
added: 2026-10-19
closed: 2026-10-19
payoff: the runner and its tests work from a linked worktree, so reviewing a worker branch from a worktree does not fail on the runner's own tests
verify: grep -q 'git-common-dir' tools/headless_worker.py
---

**Problem.** `prepare_clone` in `tools/headless_worker.py` runs `git clone --reference <checkout>`. When the checkout is a linked git worktree, its `.git` is a file that points elsewhere, not a repository, so the clone fails with exit 128. On 2026-10-19 a review of `claude/pl-3r6l-worker` ran `bin/docket verify PL-3R6L` from a worktree, and five tests in `tests/unit/test_headless_worker.py` failed this way. The same tests pass from an ordinary clone.

**Why it matters.** A reviewer who checks a worker branch from a worktree gets a `REJECT` that has nothing to do with the worker's change. The runner itself also fails if the owner starts it from a worktree.

**Done when.** The runner passes `--reference` the repository that `git rev-parse --git-common-dir` names, and a test runs the clone from a linked worktree.

**Generator check.** A one-off: `prepare_clone` assumed a checkout is a plain repository, and no other reader of `--reference` exists to share the fact.
