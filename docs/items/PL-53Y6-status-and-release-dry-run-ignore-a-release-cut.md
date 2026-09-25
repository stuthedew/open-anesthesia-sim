---
id: PL-53Y6
title: status and release --dry-run ignore a release cut in flight on another branch, which the digest reports, and status offers the tag item PL-08D4 as next though origin already carries refs/tags/v0.5.10 on the cut commit
status: untriaged
feature: one-snapshot
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
added: 2026-09-25
---

**Problem.** status and release --dry-run ignore a release cut in flight on another branch, which the digest reports, and status offers the tag item PL-08D4 as next though origin already carries refs/tags/v0.5.10 on the cut commit

Reproduced 2026-09-25 with PR #1003 cutting v0.5.11: the digest said a release is being cut; `status` said `Next version would be 0.5.11`; `release --dry-run` printed notes without mentioning it. `status` offered PL-08D4 (Tag v0.5.10), which has no `verify:` so nothing notices the tag exists. PL-QHCW family.

**Why it matters.** The PL-66FP double-cut path, one command away from the one that guards it.

**Done when.** `status` and `release --dry-run` read `cuts_in_flight`; a tag item whose tag exists on the remote is reported done or carries a `verify:` that says so.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
