---
id: PL-SLCC
title: vcs.change_landed reads a port the base took together with an edit to the adjacent line as a git merge conflict, so orphaned and left_behind_check still report that commit as left behind; a per-hunk replay at zero context would clear it, at a false-match risk on short hunks that needs measuring first
priority: P3
effort: M
status: ready
classes: defect
feature: landed-elsewhere
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; recall in an apparatus check, read in the safe direction
added: 2026-09-23
payoff: a port whose landing squash also touched the neighbouring line stops reading as lost work in stranded and on the digest's left-behind line
verify: grep -q 'def test_a_change_the_base_took_beside_an_adjacent_edit_has_landed' subprojects/docket/tests/test_vcs.py
---

**Problem.** vcs.change_landed reads a port the base took together with an edit to the adjacent line as a git merge conflict, so orphaned and left_behind_check still report that commit as left behind; a per-hunk replay at zero context would clear it, at a false-match risk on short hunks that needs measuring first

**Found 2026-09-23, building `PL-GHHW`.** `change_landed` replays a commit
onto each base commit as a three-way merge (`git merge-tree --write-tree
--merge-base=<commit>^`) and calls it landed where the result is the base's
own tree. git merges changes to adjacent lines as one hunk, so where the base
took the port's line *and* edited the line next to it in the same commit, the
replay conflicts, git exits 1, and the commit reads as not landed.
Reproduced in a scratch repository on 2026-09-23: the port changes line 10;
the base's commit changes lines 10 and 11; `change_landed` returns `None`.
The direction is the safe one - the commit stays reported, exactly as before
`PL-GHHW` - so this is recall, not a wrong answer.

**Why it matters.** A port is what the drive-to-green rules prescribe for a
red base, and a landing squash that also touches the neighbouring line is an
ordinary shape for a fix, so this is the one route by which the
landed-elsewhere generator `PL-GHHW` closed can still hand a reader a finding
that is not lost work.

**Done when.** A commit whose change the base took beside an edit to an
adjacent line is recognised as landed by `change_landed`, with a test in
`test_vcs.py` built on that shape, and no short hunk is matched where it never
landed - or, if the count below finds no such commit, the item is dropped.

**A lead, not a finding.** Replaying each hunk on its own at zero context
(`git apply --reverse --check --unidiff-zero` against the base's copy) would
clear it, but zero context can match a short hunk - a blank line, a lone
brace - somewhere it never landed, which is the expensive direction for
`orphaned`. Count how often the conflict case occurs before building: if no
reported commit on a live branch is ever this shape, drop this item.
