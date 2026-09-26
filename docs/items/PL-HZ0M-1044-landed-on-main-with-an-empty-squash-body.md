---
id: PL-HZ0M
title: #1044 landed on main with an empty squash body (6d2f0531) although a session armed its auto-merge, the path PL-WFFX's spent verdict credits with losing none since #918, and PL-WFFX says a new empty body reopens it
priority: P2
effort: S
status: ready
classes: defect
feature: pr-body-integrity
touches: docs/pr-bodies/1015.md, docs/pr-bodies/1044.md, docs/items/PL-WFFX-name-the-merge-client-that-sends-an-empty.md, docs/items/PL-979D-the-squash-commit-on-main-is-composed-by.md
blocked-by: PL-979D
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-26 triage pass
added: 2026-09-26
payoff: the two lost pull-request bodies are in the checkout, and PL-WFFX's record stops telling a session that a session-armed auto-merge never loses a body
verify: grep -qF 'commit: 6d2f0531' docs/pr-bodies/1044.md && grep -qF 'commit: fdc76b16' docs/pr-bodies/1015.md && grep -qF '#1044' docs/items/PL-WFFX-*.md
---

**Problem.** #1044 landed on main with an empty squash body (6d2f0531) although a session armed its auto-merge, the path PL-WFFX's spent verdict credits with losing none since #918, and PL-WFFX says a new empty body reopens it

**Evidence**, read 2026-09-26 01:52 UTC by the session that armed it:

- It was armed with the GitHub MCP tool `enable_pr_auto_merge` (SQUASH, no title or message) at 01:13:01Z. A second identical call at 01:33 returned the request already in place, still stamped 01:13:01Z.
- Its body was replaced with `update_pull_request` at 01:33:20, after arming, and read back intact. Whether an edit after arming is what emptied the squash body is not established; it is the one step on the session side this pull request is known to have had.
- The branch was brought up to date by two server-side merges, at 01:41:24 and 01:46:28, committed as the owner. Both the web *Update branch* button and a session's `update_pull_request_branch` produce that.
- `checks` went green at 01:50:53Z and the squash commit is stamped 01:51:21Z, 28 seconds later, which reads as auto-merge firing rather than a merge by hand. Owner-local time was 20:51 (-0500).
- `tools/pr_body_check.py` now reports two lost bodies, #1015 and #1044, and neither has a `docs/pr-bodies/` file yet; `--recover` writes them.

**A control, 2026-09-26 02:06 UTC.** #1050, this item's own capture, was armed the same way (`enable_pr_auto_merge`, SQUASH, no title or message) by the same session, called once, with its body left as created and one `update_pull_request_branch` merge. It landed as `ebfdefd3` with its body. So the arming tool alone does not empty a body; what #1044 had that #1050 did not is the body edit after arming, the second `enable_pr_auto_merge` call, and a second server-side branch update. One pair does not say which.

`PL-979D`, the live generator whose title says the squash commit is composed by whichever merge path lands it, is where this lands as an instance.

**Why it matters.** `PL-WFFX`'s spent verdict, written 2026-09-23 (#967), says
"sessions arm auto-merge with a tool that sends no title or message, so none of
the 47 squash merges since #918 lost its body; a new empty body reopens it".
Two have lost it since: #1015 (`fdc76b16`, 2026-09-25 14:32 -0500), whose merge
path is not established, and #1044 (`6d2f0531`, 20:51 -0500), which a session
armed. So the record a later session reads calls a path safe that is not, and
the reasoning for two pull requests exists only on GitHub.

[superseded 2026-09-26] **Why it waits on `PL-979D`.** `PL-979D` states the same fact as `PL-WFFX`, and
it is live. On 2026-09-26 its build held a claim on `claude/pl-979d-build-1y2bjk`,
with `PL-BZHX`, `PL-PNJF`, `PL-73G8` and `PL-M7W1`. That build records each pull
request's body before the merge, so which step emptied #1044's squash body stops
mattering: no answer would change what anyone does. It also changes the header
`--recover` writes. The current header says the body is what the squash commit
"should have carried, verbatim", which is the sentence `PL-73G8` and `PL-PNJF`
found untrue, so recovering now would write that sentence twice more. Adding this
item to `PL-979D`'s `root-cause-of:` edits a file that branch holds, so that
waits too. `PL-979D` closed 2026-09-26 (#1068) with
`generator: spent`, and its build put this item in its `root-cause-of:`. Its
header reaches `main` with #1068, so nothing holds this item, and the "live
head" in "Done when" now reads as the head that holds the fact, spent.

**Done when.** #1015's and #1044's bodies are recovered under the header
`PL-979D`'s build writes. `PL-WFFX`'s `generator:` line no longer says no squash
merge since #918 lost its body: it names #1015 and #1044, and `PL-979D` as the
live head for the fact. This item is in `PL-979D`'s `root-cause-of:`, unless its
build already put it there. Which step emptied #1044's body is out of scope.

**Generator check.** An instance of `PL-WFFX`'s fact, the squash commit's
subject and body as the merge sends them rather than as the pull request shows
them. It was filed 2026-09-26, after that head closed on 2026-09-22, and it is
the case that head's own `generator:` line says reopens it. `PL-979D` states the
same fact and is live, so this joins `PL-979D` instead of reopening `PL-WFFX` as
a second live head for one fact.
