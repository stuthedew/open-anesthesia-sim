---
id: PL-7K31
title: Nothing refuses an email address in a pull request body before it is sent: no hook in .claude/settings.json matches create_pull_request or update_pull_request (the only GitHub matcher is merge_pull_request), and tools/pr_body_check.py recovers and anchors bodies rather than screening them, so an address a session writes into a body is public on GitHub at once, stays in the description's edit history after it is removed, and would land in main's history at the merge because the squash message is the body (found when #1480 opened with the owner's address, 2026-10-17)
status: untriaged
added: 2026-10-17
---

**Problem.** Nothing refuses an email address in a pull request body before it is sent: no hook in .claude/settings.json matches create_pull_request or update_pull_request (the only GitHub matcher is merge_pull_request), and tools/pr_body_check.py recovers and anchors bodies rather than screening them, so an address a session writes into a body is public on GitHub at once, stays in the description's edit history after it is removed, and would land in main's history at the merge because the squash message is the body (found when #1480 opened with the owner's address, 2026-10-17)
