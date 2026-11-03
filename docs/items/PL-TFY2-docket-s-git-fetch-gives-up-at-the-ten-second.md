---
id: PL-TFY2
title: docket's git fetch gives up at the ten-second limit, and a fetch from this cloud container took 15 s on 2026-11-03, so show, branch, triage and the session digest all reported nothing refreshed and answered from refs up to a minute old
priority: P2
effort: S
status: done
classes: defect
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/gitargv.py, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md, tools/left_behind_check.py, tools/blind_review_report.py, docs/items/PL-TFY2-docket-s-git-fetch-gives-up-at-the-ten-second.md
deferred-from: v0.7.0 - filed after the gate froze; an apparatus-only fix to how long a git call that reaches the remote may run, with no effect on what a learner sees
added: 2026-11-03
closed: 2026-11-03
pr: 1977
payoff: docket's read commands and the session-start summary refresh the refs from a remote that answers in up to a minute, so they stop reporting stale refs from a slow cloud container
verify: grep -q 'def test_a_git_call_that_reaches_the_remote_gets_the_network_timeout' subprojects/docket/tests/test_vcs.py
---

**Problem.** docket's git fetch gives up at the ten-second limit, and a fetch from this cloud container took 15 s on 2026-11-03, so show, branch, triage and the session digest all reported nothing refreshed and answered from refs up to a minute old

**Generator check.** One-off. The ten-second bound was written for local reads and was never split for a call that reaches the remote. Two tools had already worked around it with their own bounds, which this fix removes. No other item names the timeout.

**Fix, 2026-11-03.** `docket.vcs` now holds two bounds. `GIT_TIMEOUT`, ten seconds, applies to a read of this checkout. `NETWORK_GIT_TIMEOUT`, sixty seconds, applies to a fetch, `ls-remote`, push, pull or clone. `call_git` chooses between them from the command name when its caller names no bound, so every caller gets the right one without passing anything. The set of network commands moved from `docket.verify` to `docket.gitargv`, where `vcs` and `verify` both read it.

- **The value.** Fetches from this container took 12 s and 15 s on 2026-11-03, measured with `time git fetch --quiet origin`. Sixty seconds is four times the slower one. It is also the bound `tools/blind_review_report.py` already gave its fetches.
- **The cost.** A remote that hangs without refusing now holds a command for up to a minute per call. The session-start summary makes two such calls, a fetch and an `ls-remote`, so it waits at most two minutes. Claude Code gives a command hook 600 seconds by default (https://code.claude.com/docs/en/hooks, "Common fields", `timeout`), and `.claude/settings.json` sets no shorter one for the summary.
- **Second copies removed.** `tools/left_behind_check.py` had its own 30 s bound and `tools/blind_review_report.py` its own 60 s bound. Both now take `call_git`'s default. Left-behind's local reads (`cat-file`, `merge-base`) drop from 30 s to the 10 s every other local read gets.
- **Unchanged.** `docket.claiming` keeps its 120 s bound for a claim's fetch and push, since a failed write is reported and not retried. `tools/tag_release.py` keeps the long bound it gives every call.
- **Test.** `test_a_git_call_that_reaches_the_remote_gets_the_network_timeout` fails on the old code and passes on the new.
