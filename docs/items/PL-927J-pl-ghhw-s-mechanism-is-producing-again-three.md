---
id: PL-927J
title: PL-GHHW's mechanism is producing again: three readers of whether the base took a branch's change, left off vcs.change_landed by its fix, were filed after it closed - PL-8BR0 (landed_whole refuses queue-only commits as merge evidence), PL-RLTK (_base_blobs holds every blob the base ever held) and PL-P64J (claims._landed_through, the same ever-held set) - so a live head wants recording with root-cause-of and generator: live once PL-P64J reaches main with #1133
status: untriaged
added: 2026-09-27
---

**Problem.** PL-GHHW's mechanism is producing again: three readers of whether the base took a branch's change, left off vcs.change_landed by its fix, were filed after it closed - PL-8BR0 (landed_whole refuses queue-only commits as merge evidence), PL-RLTK (_base_blobs holds every blob the base ever held) and PL-P64J (claims._landed_through, the same ever-held set) - so a live head wants recording with root-cause-of and generator: live once PL-P64J reaches main with #1133

**Why it is one mechanism.** `PL-GHHW` (closed 2026-09-23, `generator:
spent`) moved the readers that report a change as *unlanded* work -
`vcs.orphaned` and `tools/left_behind_check.py` - onto one change-level test,
`vcs.change_landed`. The readers that decide a branch *merged* were left on
blob sets: `vcs.landed_whole` reads `_landing_split` over `_base_blobs` and
refuses queue-only commits (`PL-JBRC`), and `claims._landed_through` reads the
same ever-held set. Each has since misread the one fact the heads `PL-R808`,
`PL-BHVM` and `PL-GHHW` name - whether the base already holds a branch
commit's change, by whatever route - in both directions: `PL-8BR0` (filed
2026-09-25) misses a squash-merged captures-only branch, and `PL-RLTK` and
`PL-P64J` (both 2026-09-26) take a restored earlier blob for a merge.
`PL-RLTK`'s triage counted two post-close instances, "one short of the three".
`PL-8BR0` is the third.

**Why it is not recorded yet.** `docket check` holds `root-cause-of:` to three
items the store holds, and `PL-P64J` exists only on
`claude/dazzling-brahmagupta-b1psew` (#1133). Once that merges, triage records
`root-cause-of: PL-8BR0, PL-RLTK, PL-P64J` and `generator: live` here - three
members in two days after the head closed - which ranks it and starts the
pause on new workflow mechanisms.

**What the fixes in flight do and do not settle.** `PL-8BR0`'s fix makes the
forge's newest pull request the merge evidence for `branch` and `arm`.
`PL-RLTK`'s narrows the blob set to what the base wrote since the fork. Both
close their members. Neither gives the merged verdict one test that every
reader shares, which is the mechanism, and that is this item's work.
