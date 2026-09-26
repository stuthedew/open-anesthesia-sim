---
id: PL-X8SV
title: Stale claude/ branches stop accumulating and today's 14 are cleared once: nothing deletes a branch whose own pull request never merges, so each hand-off between sessions leaves one behind
status: untriaged
added: 2026-09-26
---

**Problem.** Stale claude/ branches stop accumulating and today's 14 are cleared once: nothing deletes a branch whose own pull request never merges, so each hand-off between sessions leaves one behind

**The owner's request, 2026-09-26:** "Ideally, the stale branches wouldn't
happen anymore and clean up is a one time thing." That lifts the generator
pause for this request.

**Why they happen** (traced 2026-09-26 by the session that filed this). A branch
is deleted only by GitHub's automatic deletion, and that fires only when the
branch's own pull request merges. A session cannot delete a branch
(`docs/worker.md` § "Ref operations a session cannot perform"). Of the 14 stale
branches on 2026-09-26:

- **6 were branches carrying only captured items**, from before `PL-WNCT`
  landed (2026-09-23 01:54 UTC). None have appeared since.
- **7 were hand-offs.** The successor session copies its predecessor's commits
  onto its own harness-named branch and merges from there. `PL-J6HP` landed via
  #937, `PL-N162` via #1002, `PL-979D` via #1068 and `PL-R17X` via #1102. This
  is still happening: since `PL-YJG1` (2026-09-25), hand-offs go to Projects
  threads.
- **1 was a branch reused after its merge.** Its pull request, #1045, was closed
  unmerged.

`PL-P99G` lists 13 of them with their tips. The 14th is
`claude/filed-findings-g90x9s`, tip `64c03cf86d`; its work (`PL-R17X`) landed
via #1102.

**Routes to weigh in the design round.** These are leads, not yet researched:

1. **A repository workflow that deletes a `claude/` branch** once all of these
   hold:
   - no pull request is open on it;
   - `bin/docket` reads it as settled;
   - `bin/docket stranded` finds nothing that exists only on it;
   - it is older than a grace period.

   This covers every source, including ones not yet seen, and its first run is
   the one-time cleanup. To verify:
   - that a workflow token can delete a branch (GitHub REST "Delete a
     reference", with `contents: write`);
   - how a deleted tip is restored;
   - whether settled plus stranded is safe as a deletion test. A branch holding
     the only copy of unlanded code must never pass it.
2. **A successor session continues on its predecessor's branch.** Look at
   `create_session`'s `outcome_branch`, and at how Projects threads get their
   branch. This removes only the hand-off source.
3. **Delete the head branch when a pull request closes unmerged.** This would
   have covered 2 of the 14 (#1045, #1101), which is not enough on its own.

**Deleting branches automatically risks deleting work nobody carried forward.**
So the chosen route goes to the owner before it is built, as a material risk of
breaking what works (`CLAUDE.md` § "The queue"). If route 1 lands, `PL-S8LZ`'s
cleanup sentences become a fallback and are a candidate for retirement.
