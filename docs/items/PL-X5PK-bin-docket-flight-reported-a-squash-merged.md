---
id: PL-X5PK
title: bin/docket flight reported a squash-merged branch whose every change was already on the base, and _work_already_on_base is documented to have excluded it
status: untriaged
added: 2026-09-21
---
**Problem.** `bin/docket flight` reported a squash-merged branch whose every
change was already on the base, and `_work_already_on_base` is documented to
have excluded it

**Found 2026-09-21** on the branch that closed `PL-25DD`
(`claude/sharp-lamport-t545rs`, squash-merged as `#823`). **Narrowed twice
before filing, and most of what it first looked like is not real** - that is
recorded here so the next reader does not re-derive it.

**What was measured.** With the checkout at `01458030` (the merge commit
itself), `bin/docket flight` reported:

    PL-C3GS  origin/claude/sharp-lamport-t545rs  last commit today
    PL-TSZM  origin/claude/sharp-lamport-t545rs  last commit today

while `git diff origin/main origin/claude/sharp-lamport-t545rs` over both item
files reported no difference, and `git ls-remote --heads origin
claude/sharp-lamport-t545rs` returned **nothing**: GitHub auto-deleted the head
branch on merge, so the only thing that ref named was this checkout's own
unpruned remote-tracking pointer at `0d0e9ef8`.

**What is not the finding.**

- *Not a stale-ref bug.* `docket.vcs.fetch_remote` refuses `--prune` on purpose
  (`PL-HKF4` came within one prune of losing an item), and the refusal message
  prints the exact remedy for this case - `git branch -dr origin/<branch>`.
  Working as designed.
- *Not a second instance.* `PL-J870` on `origin/claude/epic-curie-3xncza` looked
  like the same shape after `#824` merged, and is not: that branch still exists
  on the remote and its session was live, which `PL-8JQQ` deliberately made
  report as in flight.
- *Not a cross-session harm.* The branch is gone from the remote, so no session
  fetching fresh ever saw these rows. The blast radius was one checkout.

**What survives.** `branches_in_flight`'s docstring states that branches whose
work has landed are excluded, asked twice, and that because "a squash merge
keeps none of the branch's commits, `_work_already_on_base` asks after the
content instead". Every change on `0d0e9ef8` was present on `01458030` when the
measurement was taken, so that second test had the content it needed and the
branch was reported anyway. Either the exclusion does not cover this shape, or
one of the two documented unread-guards (an unresolvable merge-base, a commit
walk running off a grafted history) fired silently on a shallow checkout and
the ref was reported unread rather than excluded - the container clones at
`clone_depth` 50, which makes the second reading the likelier one and also
makes it invisible in a full clone.

**Why it is worth a look rather than a drop.** If the guard is firing on clone
depth, every session in this harness gets a degraded `flight` read and none of
them can tell, which is the silent-wrong-answer shape `CLAUDE.md` asks to be
caught in code. If instead the exclusion simply misses this shape, it is a
narrow fix. Deciding which costs one read of
`subprojects/docket/src/docket/vcs.py` against a shallow checkout.

**Left untriaged deliberately.** Choosing its debt class is what would make
v0.5.0's gate owe it a disposition, and that judgment belongs with a session
that has read the code rather than with this one, which has not.

**Done when.** It is established whether the miss is the exclusion's shape or a
depth-triggered unread guard, and either a test in
`subprojects/docket/tests/test_vcs.py` holds the fix, or the item is dropped
with the reading that explains the observation.
