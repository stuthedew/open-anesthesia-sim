---
id: PL-HZ0M
title: #1044 landed on main with an empty squash body (6d2f0531) although a session armed its auto-merge, the path PL-WFFX's spent verdict credits with losing none since #918, and PL-WFFX says a new empty body reopens it
status: untriaged
touches: docs/pr-bodies/1044.md, docs/items/PL-WFFX-name-the-merge-client-that-sends-an-empty.md
added: 2026-09-26
---

**Problem.** #1044 landed on main with an empty squash body (6d2f0531) although a session armed its auto-merge, the path PL-WFFX's spent verdict credits with losing none since #918, and PL-WFFX says a new empty body reopens it

**Evidence**, read 2026-09-26 01:52 UTC by the session that armed it:

- It was armed with the GitHub MCP tool `enable_pr_auto_merge` (SQUASH, no title or message) at 01:13:01Z. A second identical call at 01:33 returned the request already in place, still stamped 01:13:01Z.
- Its body was replaced with `update_pull_request` at 01:33:20, after arming, and read back intact. Whether an edit after arming is what emptied the squash body is not established; it is the one step on the session side this pull request is known to have had.
- The branch was brought up to date by two server-side merges, at 01:41:24 and 01:46:28, committed as the owner. Both the web *Update branch* button and a session's `update_pull_request_branch` produce that.
- `checks` went green at 01:50:53Z and the squash commit is stamped 01:51:21Z, 28 seconds later, which reads as auto-merge firing rather than a merge by hand. Owner-local time was 20:51 (-0500).
- `tools/pr_body_check.py` now reports two lost bodies, #1015 and #1044, and neither has a `docs/pr-bodies/` file yet; `--recover` writes them.

`PL-979D`, the live generator whose title says the squash commit is composed by whichever merge path lands it, is where this lands as an instance.
