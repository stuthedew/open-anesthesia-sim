---
id: PL-351H
title: Pull-request facts are read twice in tools - whether a branch's newest pull request merged (open_pull_requests, left_behind_check), which are open (update_armed pages past 100), a failing CI conclusion (main_ci_status, update_armed) and commits past a merged head (vcs.carried_merge, left_behind_check) - and each pair parts on one input
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
milestone: v0.5.24
touches: tools/open_pull_requests.py, tools/left_behind_check.py, tools/update_armed.py, tools/main_ci_status.py, tools/fact_home_check.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs_silence.py, tests/unit/test_left_behind_check.py, tests/unit/test_open_pull_requests.py, tests/unit/test_update_armed.py, tests/unit/test_main_ci_status.py, docs/apparatus.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-12
pr: 1456
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

**Resolved 2026-10-12.** Each pair now reads one record, and the parting input
of each is pinned by a test. Which side was right was decided per pair:

- *Whether the newest pull request merged.* `open_pull_requests` was right: an
  entry with no `merged_at` is unreadable, not unmerged. `left_behind_check`'s
  request and parse are gone; its lookup is `open_pull_requests.newest`, which
  raises `ListingFailed` with the kind (`NO_PERMISSION`, `NO_NETWORK`,
  `UNREADABLE_ANSWER`) the check names a decline by, and returns docket's own
  `vcs.NewestPullRequest` with `vcs.PULL_*` states rather than a second
  dataclass. Pinned by
  `test_an_entry_without_merged_at_is_declined_as_open_pull_requests_declines`.
- *Which pull requests are open.* `update_armed` was right that the answer is
  every page; `open_pull_requests` was right that a page read later can miss
  an entry. `open_pull_requests.every_page` takes both: it reads oldest first
  to a short page, so only a close can shift a page, then reads every page but
  the last again and declines on any change. One page - 3 open on 2026-10-12 -
  is still one request. `update_armed.open_pulls` pages through it with its own
  retrying calls. Pinned on both sides at 100 open, and on a close mid-read.
- *A failing conclusion.* `update_armed` was right: `action_required` ran no
  step to a verdict. `main_ci_status.FAILED` is the one set, `VERDICTS` is
  `success` plus it, and `update_armed` imports it. An `action_required` run
  newer than every verdict now prints the line a cancelled one does - no
  whole-store verdict for that commit - since passing over it silently would
  report an older commit's verdict as `main`'s (`PL-JTHW`).
  `pick_cancelled`/`cancelled_advisory` are `pick_unjudged`/`unjudged_advisory`.
- *Commits past a merged head.* Not a parting on re-confirmation: on a
  merge-commit merge `carried_merge`'s None is its restart guard, and docket's
  counts reading reports the commit ahead, as the check reports it left
  behind. What was duplicated was the reading itself - each wrote its own
  `log` and landing loop. `vcs.past_head` is that one reading; `carried_merge`
  and `left_behind_check.examine` both call it, and the check's runner reaches
  it through `vcs.git_answer`, `_run_git`'s exit classification split out, so a
  failed `log` declines rather than reading as no commits. Pinned by the
  merge-commit test and the failed-`log` test.

`fact_home_check` refused the two names the move first gave the shared
constants (`UNREADABLE` is `doc_check`'s exception tuple, `REFUSED` claiming's
exit status), so they are `UNREADABLE_ANSWER` and `_REFUSAL_CODES`, and the
baseline fell from 107 to 105.
