---
id: PL-8BR0
title: A merged captures-only pull request is never recognised as merged, because vcs.landed_whole refuses queue-only commits as merge evidence (PL-JBRC), so branch tells its session to merge the base in, arm says arm for a pull request that already merged, and the next capture there lands nowhere
priority: P2
effort: M
status: ready
classes: defect, infra
feature: one-snapshot
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-snapshot batch
added: 2026-09-25
payoff: a session whose pull request already squash-merged is told to restart instead of merging the base in, so its next capture is not stranded on a branch nothing will merge again
verify: grep -q 'def test_a_merged_captures_only_branch_is_told_to_restart' subprojects/docket/tests/test_vcs.py
---

**Problem.** A merged captures-only pull request is never recognised as merged, because vcs.landed_whole refuses queue-only commits as merge evidence (PL-JBRC), so branch tells its session to merge the base in, arm says arm for a pull request that already merged, and the next capture there lands nowhere

Reproduced (scenario f): capture, push, PR; `arm` says arm; squash-merge; fetch; `branch` says "1 behind, 1 ahead ... git merge origin/main", `arm` says behind 1; capture again, `arm` says "arm - mark its pull request ready and arm it" for a merged PR. `stranded` does catch the lost capture. PRs carrying only item files are exactly the ones PL-WNCT auto-merges. A gap in PL-8M8H.

**Why it matters.** A lost-capture path on the one kind of pull request the process arms automatically.

**Done when.** A captures-only branch whose pull request merged is told to restart; the forge's merged state, where available, is the evidence; a test holds scenario f.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Seen again, 2026-09-25, on a pull request that was not captures-only.** `PL-P0FP`'s pull request 1007 carried `docs/stress-2026-09-25/evidence.tar.gz` beside its items. It squash-merged and GitHub deleted the branch. The next session-start digest in that session still reported the branch 2 behind and 9 ahead and told it to run `git merge origin/main` before its first edit, while listing `PL-P0FP` itself among the items landed on `origin/main`. Every path the branch changed already matched `origin/main`. So the captures-only reading above may not be the whole cause: check whether the digest and `branch` consult `landed_whole` at all before advising a merge.

Reproduced 2026-09-25 against 46954a81, in scratch clones: a branch carrying one capture was pushed and squash-merged onto `origin/main`; after a fetch, `branch` said `claude/scratch-cap is 1 behind origin/main and 1 ahead`, advised `git merge origin/main`, and listed the branch's own capture as landed, and `arm` said `behind 1`. On the question the paragraph above leaves open: `branch_state` does consult `landed_whole` (vcs.py:2136), but only when it would advise a merge, and `landed_whole` still refuses a queue-only commit as merge evidence. `arm`'s verdict is `arming.arm`, so `touches` now carries `arming.py`.

**Generator check.** PL-GHHW's fact, whether the base already holds a branch commit's change by whatever route, in an instance filed once that head had closed (2026-09-23, spent): `landed_whole` is a reader its fix did not move onto `vcs.change_landed`. Not PL-XBV4's freshness fact, since the refs here were fresh, so it is removed from that head's `root-cause-of`.
