---
id: PL-351H
title: Pull-request facts are read twice in tools - whether a branch's newest pull request merged (open_pull_requests, left_behind_check), which are open (update_armed pages past 100), a failing CI conclusion (main_ci_status, update_armed) and commits past a merged head (vcs.carried_merge, left_behind_check) - and each pair parts on one input
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: tools/open_pull_requests.py, tools/left_behind_check.py, tools/update_armed.py, tools/main_ci_status.py, subprojects/docket/src/docket/vcs.py, tests/unit/test_left_behind_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
payoff: a pull request's state reads the same to the tools that arm, update and audit branches
verify: grep -q 'def test_an_entry_without_merged_at_is_declined_as_open_pull_requests_declines' tests/unit/test_left_behind_check.py
---

**Problem.** Pull-request facts are read twice in tools - whether a branch's newest pull request merged (open_pull_requests, left_behind_check), which are open (update_armed pages past 100), a failing CI conclusion (main_ci_status, update_armed) and commits past a merged head (vcs.carried_merge, left_behind_check) - and each pair parts on one input

- Whether a branch's newest pull request merged: `open_pull_requests.newest_pull_request` (feeding `vcs.NewestPullRequest`) beside `left_behind_check.github_lookup` and `_pull_request`, the same query with its own parse. On an entry with no `merged_at` key the tool declines and left_behind_check reads "closed without merging", the answer the tool's docstring exists to refuse. Found by three sweepers.
- Which pull requests are open: `open_pull_requests.open_pull_requests` beside `update_armed.open_pulls` and `parse_pull`. With 100 or more open the tool declines on a full page and update_armed reads page 2.
- A failing CI conclusion: `main_ci_status.VERDICTS` beside `update_armed.FAILED`. On `action_required` main_ci_status prints main red and update_armed reads the check as not failed.
- Commits past a merged pull request's head: `vcs.carried_merge` beside `left_behind_check.examine`. On a pull request merged by a merge commit and one more pushed commit, vcs returns none by design (`PL-8BR0`) and the check reports the commit left behind.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** Each tool reads these through `open_pull_requests` or `vcs`, or a shared helper, and a test pins each parting input.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
