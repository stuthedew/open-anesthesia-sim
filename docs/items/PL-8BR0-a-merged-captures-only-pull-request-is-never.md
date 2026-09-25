---
id: PL-8BR0
title: A merged captures-only pull request is never recognised as merged, because vcs.landed_whole refuses queue-only commits as merge evidence (PL-JBRC), so branch tells its session to merge the base in, arm says arm for a pull request that already merged, and the next capture there lands nowhere
status: untriaged
feature: one-snapshot
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
added: 2026-09-25
---

**Problem.** A merged captures-only pull request is never recognised as merged, because vcs.landed_whole refuses queue-only commits as merge evidence (PL-JBRC), so branch tells its session to merge the base in, arm says arm for a pull request that already merged, and the next capture there lands nowhere

Reproduced (scenario f): capture, push, PR; `arm` says arm; squash-merge; fetch; `branch` says "1 behind, 1 ahead ... git merge origin/main", `arm` says behind 1; capture again, `arm` says "arm - mark its pull request ready and arm it" for a merged PR. `stranded` does catch the lost capture. PRs carrying only item files are exactly the ones PL-WNCT auto-merges. A gap in PL-8M8H.

**Why it matters.** A lost-capture path on the one kind of pull request the process arms automatically.

**Done when.** A captures-only branch whose pull request merged is told to restart; the forge's merged state, where available, is the evidence; a test holds scenario f.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
