---
id: PL-53Y6
title: status and release --dry-run ignore a release cut in flight on another branch, which the digest reports, and status offers the tag item PL-08D4 as next though origin already carries refs/tags/v0.5.10 on the cut commit
priority: P3
effort: S
status: ready
classes: defect, infra
feature: release-process
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-snapshot batch
added: 2026-09-25
payoff: status stops offering a version another branch is already cutting, so the double-cut collision is turned away before a session starts on it rather than at the cut
verify: grep -q 'def test_status_names_a_release_cut_in_flight' subprojects/docket/tests/test_release.py
---

**Problem.** status and release --dry-run ignore a release cut in flight on another branch, which the digest reports, and status offers the tag item PL-08D4 as next though origin already carries refs/tags/v0.5.10 on the cut commit

Reproduced 2026-09-25 with PR #1003 cutting v0.5.11: the digest said a release is being cut; `status` said `Next version would be 0.5.11`; `release --dry-run` printed notes without mentioning it. `status` offered PL-08D4 (Tag v0.5.10), which has no `verify:` so nothing notices the tag exists. PL-QHCW family.

**Why it matters.** The PL-66FP double-cut path, one command away from the one that guards it.

**Done when.** `status` and `release --dry-run` read `cuts_in_flight`; a tag item whose tag exists on the remote is reported done or carries a `verify:` that says so.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

Re-checked 2026-09-25 against 46954a81, with a scratch branch carrying `docs/releases/v0.5.12.md`: `status` said `Next version would be 0.5.12.` while the digest said `A release is already being cut on origin/claude/scratch-cut (v0.5.12)`. `release --dry-run` with no version named stopped at the manual version policy (`Name the version to cut it`) before reaching the cut guard, and never mentioned the cut; `release 0.5.12 --dry-run` did print `A release is already being cut on a branch nothing has merged`. So the dry-run half holds only on the unnamed-version path, and the real cut is still refused. `PL-08D4` has since closed; the same shape is live as `PL-HZWB` (Tag v0.5.11), `ready` while `origin` carries `refs/tags/v0.5.11`. The tag half is PL-QHCW's open question, and a `verify:` reading the remote is not an admitted shape, so this item's `verify:` holds the `status` half.

**Generator check.** PL-QHCW's fact, which commit a release was cut on and whether it was cut at all, as this brief's "PL-QHCW family" says: `status` reads `readiness` alone, never the cut state the digest reads. Not PL-XBV4's freshness fact, so it is removed from that head's `root-cause-of` and moved to feature `release-process`; PL-QHCW is not in this pass and does not yet list it.
