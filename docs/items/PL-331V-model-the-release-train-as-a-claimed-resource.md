---
id: PL-331V
title: Model the release train as a claimed resource, so the release collision guard sees a session that has filed a release item but not cut
priority: P2
effort: M
status: ready
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_release.py, .claude/skills/docket/modes/release.md, subprojects/docket/README.md
blocked-by: PL-NST2, PL-0TD9
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
verify: grep -qF 'resource: release-train' .claude/skills/docket/modes/release.md && grep -qE 'def test_\w*release_train' subprojects/docket/tests/test_release.py
---

**Problem.** Model the release train as a claimed resource, so the release collision guard sees a session that has filed a release item but not cut

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

Add `resource: release-train`, stamped by release mode when it files the item. cmd_release refuses in three cases: another live holder, a cut hold that is not mine, or HEAD holding no train claim. Fix the 'no item id by design' lines at vcs.py:4066, cli.py:2570 and README.md:1535. Release mode claims the release item when it files it. Closes `PL-MFM4` (two release items filed for one release, each passing every guard).

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- A second session filing a release item while a live `release-train` claim is held elsewhere is refused.
- `PL-MFM4` is closed against this item.

**Build order.** After `PL-NST2`, `PL-0TD9`.

**The fault, reproduced 2026-09-24 on `b1d1b665`.** `release-train` appears nowhere in `cli.py`, `checks.py`, `claims.py`, `test_release.py` or release mode, so nothing stamps the resource and `cmd_release` consults no train claim.
