---
id: PL-D16Y
title: tools/pr_body_check.py screens only title and body, so an address in a merge's commit_message, which becomes the squash commit on main, or in push_files content passes; it also refuses git@github.com remotes and GitHub's own users.noreply.github.com addresses
priority: P2
effort: S
status: done
classes: defect
feature: guards-keyed-on-the-action
milestone: v0.6.15
touches: tools/pr_body_check.py, .claude/hooks/pr-body-email-guard.sh, tests/unit/test_pr_body_check.py, tests/unit/test_hook_blocks.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1991
payoff: an email address cannot reach main through a squash commit message or pushed file content, and GitHub's own addresses stop being refused
verify: grep -q 'def test_an_address_in_any_field_github_publishes_is_refused_and_its_field_named' tests/unit/test_pr_body_check.py
---

**Problem.** tools/pr_body_check.py screens only title and body, so an address in a merge's commit_message, which becomes the squash commit on main, or in push_files content passes; it also refuses git@github.com remotes and GitHub's own users.noreply.github.com addresses

**Why it matters.** The squash commit's message becomes part of `main`'s
history, and `push_files` content is public as soon as GitHub has it, so an
email address in either is as published as one in a pull request body. The
check also refuses `git@github.com` remote URLs and GitHub's own
`users.noreply.github.com` addresses, which publish nobody's address, so it
blocks correct work.

**Done when.** `screen` reads every field that GitHub publishes as text,
including a merge's `commit_message` and `push_files` content, and admits the
two GitHub addresses, and a test covers each.

**Generator check.** Misreads which fields and clients carry text GitHub
publishes, with `PL-3986`. Grouped with the `PL-61FT` re-entry (`PL-82J5`).
