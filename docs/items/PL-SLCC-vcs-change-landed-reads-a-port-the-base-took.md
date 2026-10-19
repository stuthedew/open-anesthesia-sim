---
id: PL-SLCC
title: vcs.change_landed reads a port the base took together with an edit to the adjacent line as a git merge conflict, so orphaned and left_behind_check still report that commit as left behind; a per-hunk replay at zero context would clear it, at a false-match risk on short hunks that needs measuring first
priority: P3
effort: M
status: dropped
classes: defect
feature: landed-elsewhere
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; recall in an apparatus check, read in the safe direction
added: 2026-09-23
closed: 2026-10-18
reason: Counted 2026-10-18: no commit a reader reports on a live branch has the adjacent-line shape, so the brief's own rule drops it; the measured design is recorded in the brief
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

**Counted 2026-10-18 at `4bf48585`, and dropped on the count.** The brief's
rule is to drop this item if no commit a reader reports on a live branch has
this shape. None does. The checkout's 12 branch refs carry no commit that
`stranded`, `orphaned` or the digest's left-behind line reports, and no item
filed since `PL-GHHW` on 2026-09-23 reports a commit wrongly left behind.

The shape itself is not rare, so the count is recorded for whoever meets one.
Over the head commits of the 196 pull requests merged as #1400 to #1595,
fetched as `refs/pull/*/head`, 938 single-parent commits were replayed onto
their own pull request's squash. `change_landed` found 383 and missed 555.
242 of the misses were merge conflicts, and replaying each hunk on its own at
zero context (`git apply --cached --check -R --unidiff-zero` against the
squash's tree) found 61 of those 242. All 242 were also replayed the same way
onto their fork point, where the change had not landed, and none matched
there. Those commits are not ports. They are commits whose own pull request
later edited the neighbouring line, and the readers already treat such a
branch as landed by other means, so none of them is reported.

**If a reported commit of this shape turns up, the design is ready.** Replay
each hunk at zero context against the candidate's tree and require every hunk
to hold. Decline the fallback for a hunk with no added line, because the
reverse of a pure deletion is an insertion, which applies anywhere at zero
context and so proves nothing. Decline it as well for a hunk whose added lines
hold no letter or digit, such as a blank line or a lone brace, which is the
short-hunk false match this brief warns of. The script that took the count
would need rewriting, since it lived in the session's scratch space.

