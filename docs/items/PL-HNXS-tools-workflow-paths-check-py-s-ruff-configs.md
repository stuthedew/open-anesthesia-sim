---
id: PL-HNXS
title: tools/workflow_paths_check.py's ruff_configs and tools/fixture_id_check.py walk the filesystem rather than git's tracked files, so a worktree-isolated subagent's checkout under .claude/worktrees/ fails make check (6 ruff configs found where 3 are tracked; malformed-id hits inside the agent's copy of docs/items), seen 2026-10-03 during PL-YZ17's review
priority: P3
effort: S
status: ready
classes: defect
feature: agent-worktrees
touches: tools/workflow_paths_check.py, tests/unit/test_workflow_paths_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
payoff: the linter-config check counts the configs the repository holds, so a subagent's nested checkout neither inflates its count nor fails make check
verify: grep -q 'def test_ruff_configs_ignores_an_untracked_nested_checkout' tests/unit/test_workflow_paths_check.py
---

**Problem.** tools/workflow_paths_check.py's ruff_configs and tools/fixture_id_check.py walk the filesystem rather than git's tracked files, so a worktree-isolated subagent's checkout under .claude/worktrees/ fails make check (6 ruff configs found where 3 are tracked; malformed-id hits inside the agent's copy of docs/items), seen 2026-10-03 during PL-YZ17's review

**Narrowed at triage, 2026-10-03, to `ruff_configs`.** The `fixture_id_check.py`
half is `PL-QJ5F`'s, whose Done-when already says that check never walks
`.claude/worktrees/` and that asking git for the tracked files would do it.

**Reproduced 2026-10-03 at triage** on `81debc03`, with
`git worktree add --detach .claude/worktrees/repro-hnxs HEAD`: `uv run python
tools/workflow_paths_check.py` passed but reported "6 linter config(s), each
covered by gate_paths" where git tracks 3 (`.claude/hooks/ruff.toml`,
`subprojects/docket/ruff.toml`, `tools/ruff.toml`), and `uv run python
tools/fixture_id_check.py` failed on 121 ids, every one inside the copy. The
copies pass only because the `.claude` entry of `gate_paths` covers them.

**Why it matters.** The count is the check's own claim about the tree, and it
is wrong whenever a checkout sits inside this one. A nested checkout anywhere
no `gate_paths` entry covers fails `make check` on files the repository does
not hold. The module already answers which files those are: `tracked_files()`,
beside `ruff_configs`, reads `git ls-files` in a checkout.

**Done when.** `ruff_configs` lists only files `tracked_files(root)` returns,
so a `ruff.toml` in an untracked nested checkout is not counted, and a test
named `test_ruff_configs_ignores_an_untracked_nested_checkout` in
`tests/unit/test_workflow_paths_check.py` builds a git checkout holding one and
asserts it is left out. The walk that stands in for git in a tree that is not a
checkout stays.

**Generator check.** An instance of `PL-KGYT`'s fact, which spelling of a
repeated predicate is the answer, filed after KGYT closed on 2026-10-01. The
predicate is which files the repository holds: `tracked_files()` spells it as
git's list, while `ruff_configs`, `fixture_id_check._walk` (`PL-QJ5F`) and
`doc_check._walk` (`PL-2P5L`) each walk the tree with a skip list of their own.
It is the third post-close instance after `PL-P72R` and `PL-Z8RS`, which puts
`PL-74T0`'s cluster 1 at the count the triage rule reads as a fix that did not
hold. Recorded there, not as a second head here.
