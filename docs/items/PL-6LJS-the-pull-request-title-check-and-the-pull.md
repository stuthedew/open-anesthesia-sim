---
id: PL-6LJS
title: The pull-request title check and the pull-request number check refuse a branch for an item another pull request closed, when the branch was built on that pull request's branch before it merged
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** The pull-request title check and the pull-request number check refuse a branch for an item another pull request closed, when the branch was built on that pull request's branch before it merged

**Why it matters.** `PL-LY24`'s count found 28 refusals of `tools/pr_title_check.py` and 3 of `tools/pr_record_check.py` that blamed a branch for an item that another pull request had closed. Each is a red required check that the session must work around. Examples: `claude/pl-26bz-wash-in-label` (#2157) was refused for `PL-CBYS`, which #2134 closed; `claude/project-thread-474f8h` (#1921) was refused for `PL-2881`, which records `pr: 1918`. Both checks compare the branch with the base branch, so a closure on the branch below it reads as this branch's own.

**What to do.** Make both checks leave out a closure that already records another pull request's number, or that another open pull request carries, and test it with a stacked branch.

**Done when.** A branch built on another open pull request's branch passes both checks for the items that pull request closed.
