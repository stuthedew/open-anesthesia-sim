---
id: PL-KL6B
title: Which branch HEAD is on, a ref's branch name without its remote, the agent namespace and a cut's date are each spelt by several readers - seven for HEAD's branch, removeprefix("origin/") in two tools, a case-sensitive claude/ in branch_sweep, %cI against %aI - and each pair parts on one input
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/cli.py, tools/branch_id_check.py, tools/pr_title_check.py, tools/branch_sweep.py, tools/left_behind_check.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
payoff: a branch's name and namespace read the same to docket and to the tools that sweep, title and attribute it
verify: grep -q 'def test_head_branch_is_read_by_one_function' subprojects/docket/tests/test_vcs.py
---

**Problem.** Which branch HEAD is on, a ref's branch name without its remote, the agent namespace and a cut's date are each spelt by several readers - seven for HEAD's branch, removeprefix("origin/") in two tools, a case-sensitive claude/ in branch_sweep, %cI against %aI - and each pair parts on one input

- Which branch HEAD is on: `vcs._branch_state`, `claims._checked_out`, `claiming._branch`, `arming.arm`, `cli._release_train`, `branch_id_check.branch_name` and `pr_title_check._branch`. On a detached HEAD with `GITHUB_HEAD_REF=claude/x`, branch_id_check answers `claude/x` and the other six none; vcs also skips the `_head_name` stripping four of them apply.
- A ref's branch name without its remote: `vcs._head_name` beside `removeprefix("origin/")` in `branch_sweep`'s `Readings.keep` and `note` and `left_behind_check.orphaned_branches`. On `upstream/claude/x` vcs gives `claude/x` and the tools keep the whole name.
- The agent namespace: `claims.AGENT_BRANCH_PREFIX` (lower-cased, read by `branch_id_check`) beside `branch_sweep.PREFIX` and its case-sensitive `for-each-ref`. On `Claude/x` claims reads an agent branch and branch_sweep never lists it.
- A release cut's date: `vcs.cuts_in_flight` and `_cut_date` take the committer date (`%cI`), `claims._cuts` the author date (`%aI`); they part on a rebased cut. The "mine" test agrees.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** Each fact has one function in `docket.vcs` or `claims` that the rest call, and a test pins each parting input.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
