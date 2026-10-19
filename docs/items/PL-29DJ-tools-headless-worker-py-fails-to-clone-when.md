---
id: PL-29DJ
title: tools/headless_worker.py fails to clone when its checkout is a linked git worktree: git clone --reference names the worktree, which has a .git file rather than a repository, so five of tests/unit/test_headless_worker.py's tests fail under bin/docket verify run from a worktree
status: untriaged
added: 2026-10-19
---

**Problem.** tools/headless_worker.py fails to clone when its checkout is a linked git worktree: git clone --reference names the worktree, which has a .git file rather than a repository, so five of tests/unit/test_headless_worker.py's tests fail under bin/docket verify run from a worktree
