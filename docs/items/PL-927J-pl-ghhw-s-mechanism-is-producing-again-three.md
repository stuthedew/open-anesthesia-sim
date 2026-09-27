---
id: PL-927J
title: PL-GHHW's mechanism is producing again: three readers of whether the base took a branch's change, left off vcs.change_landed by its fix, were filed after it closed - PL-8BR0 (landed_whole refuses queue-only commits as merge evidence), PL-RLTK (_base_blobs holds every blob the base ever held) and PL-P64J (claims._landed_through, the same ever-held set) - so a live head wants recording with root-cause-of and generator: live once PL-P64J reaches main with #1133
priority: P2
effort: M
status: done
classes: defect
feature: pre-fork-content
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_claims.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-27
closed: 2026-09-27
payoff: whether a branch's change reached main gets one answer every docket command reads, so a restore stops being taken for a merge and a squash merge for unmerged work, and the family stops filing a member a day
verify: grep -q 'def test_every_landed_reader_answers_from_the_branch_s_own_history' subprojects/docket/tests/test_vcs.py
root-cause-of: PL-8BR0, PL-RLTK, PL-P64J, PL-WVSX
generator: spent - every reader of whether the base took a branch's change answers from vcs._Landings, which reads the ref's own history since its fork; a reader added beside it would have to re-derive a blob set of its own, and test_every_landed_reader_answers_from_the_branch_s_own_history pins the three that existed to that one function
misread: Whether the base already holds or has superseded a branch commit's change, by whatever route
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

[superseded 2026-09-27: `PL-P64J` reached `main` with #1133, and this triage
recorded the head - see below] **Why it is not recorded yet.** `docket check`
holds `root-cause-of:` to three items the store holds, and `PL-P64J` exists
only on `claude/dazzling-brahmagupta-b1psew` (#1133). Once that merges, triage
records `root-cause-of: PL-8BR0, PL-RLTK, PL-P64J` and `generator: live` here -
three members in two days after the head closed - which ranks it and starts the
pause on new workflow mechanisms.

**What the fixes in flight do and do not settle.** `PL-8BR0`'s fix makes the
forge's newest pull request the merge evidence for `branch` and `arm`.
`PL-RLTK`'s narrows the blob set to what the base wrote since the fork. Both
close their members. Neither gives the merged verdict one test that every
reader shares, which is the mechanism, and that is this item's work.

**Recorded at triage 2026-09-27**, once `PL-P64J` and `PL-WVSX` were on `main`:
`root-cause-of: PL-8BR0, PL-RLTK, PL-P64J, PL-WVSX`, `generator: live`, and the
family heads' own `misread:` wording, so the four heads stating the fact sort
together. Live rather than spent, the verdict `PL-P813` wrote before it was
dropped as this item's duplicate: that verdict counted only the readers of
`_base_blobs`, and `PL-8BR0` read no blob set at all. `PL-WVSX`'s reproduction
adds the reason the mechanism has not stopped - telling a restoring branch from
a stale one needs whether the branch itself wrote a blob after its fork, which
no reader has and each would re-derive.

**Why it matters.** Each reader deciding for itself has misread the fact in
both directions - a squash-merged branch taken for unmerged (`PL-8BR0`), a
restored earlier blob taken for a merge (`PL-RLTK`, `PL-P64J`, `PL-WVSX`) - and
every wrong answer lands on a session's next move: restart or keep committing,
hold or release a claim, report abandoned work or lose it. Fixing each reader
where it is met has produced a member a day since `PL-GHHW` closed.

**Done when.** Every reader deciding whether the base took a branch's change -
`vcs.landed_whole`, `claims._landed_through` and `stranded`'s item filter among
them - answers from one function that reads the branch's own history since its
fork, so content the base held before the fork counts as landed only where the
base wrote it after; `PL-P64J` and `PL-WVSX` close through it; and the
generator's verdict is rewritten to say why it cannot produce another.

**Fixed 2026-09-27**, closing `PL-P64J` and `PL-WVSX` through it.
`vcs._Landings` is the one test: a ref's own fork, its net change since it
(`_landing_split`), judged against what the base wrote after that fork
(`_written_since`). `_base_blobs` and `_Refs.base_blobs` are gone.
`_unlanded_refs`, `landed_whole`, `claims._landed_through` - each commit's own
fork, and no ever-held prefilter - and `stranded`'s item filter all answer
from it, and `test_every_landed_reader_answers_from_the_branch_s_own_history`
pins the routing: patching the one function moves all three readers at once.
Measured on this checkout: `bin/docket flight --no-fetch` 2.06 s against
2.08 s before, `stranded` 1.07 s against 1.30 s.
