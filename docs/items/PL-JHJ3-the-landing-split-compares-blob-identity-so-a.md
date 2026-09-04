---
id: PL-JHJ3
title: The landing split compares blob identity, so a squash that merged content reads as unlanded and two sessions writing one record line read as landed
status: untriaged
feature: parallel-sessions
added: 2026-09-04
---

**Problem.** The landing split compares blob identity, so a squash that merged content reads as unlanded and two sessions writing one record line read as landed

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `vcs._landing_split` asks whether the default branch has ever held
each blob a ref introduces. Blob identity is not the same question as "did this
work land", and it is wrong in both directions:

- **A squash merge writes merged content.** GitHub squashes the *result* of
  merging the branch into the base, so where the base moved on a file the branch
  also touched, what lands is neither side's blob. Measured across this
  repository's 204 merged pull requests, comparing each head's blobs against
  every blob `main` has ever held: **9 read as not fully landed**, and reading
  them showed the cause to be exactly this plus two item files renamed by a
  title edit.
- **Identical content from two sessions reads as landed.** Two sessions running
  `bin/docket record` write the same tool-dictated line, so a live branch can
  hold a blob another branch landed and read as partly landed - the false alarm
  `PL-3D2M`'s docstring documents.

**The precise test, already measured.** `git merge-tree --write-tree <base>
<ref>` performs the three-way merge and returns the resulting tree; comparing it
to the base's own tree answers "does the base already contain everything this
ref introduces" without touching blob identity at all. Run against all 204
merged pull requests, each head compared against the commit that landed it:
**0 discrepancies and 0 conflicts.** Run against a synthetic branch with one
commit left behind, it fires and names exactly the file left behind.

**What it costs.** `git merge-tree --write-tree` needs git 2.38 (2022), where
the current read needs 2.16. A conflict has to be reported as "cannot say"
rather than as an answer, which is a third state neither caller has today. And
`_landing_split` returns *paths on each side*, which a tree comparison gives for
the outstanding side but not for the landed one - so the "how much of its work
already landed" count in the report would need a different source or would go.

**Not urgent.** The current rule was silent on every branch this repository had
when it was written, and it errs toward reporting rather than toward silence,
which is the safe direction for a check whose whole point is that the silent
failure is the expensive one.
