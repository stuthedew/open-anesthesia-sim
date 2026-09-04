---
id: PL-JX2T
title: Decide what to do with origin/Review_articles: one unattributed commit ahead of main that no guard can see
status: untriaged
added: 2026-09-04
---

**Problem.** `origin/Review_articles` holds one commit `main` does not — `556d454
Added review articles on math models`, from before the `claude/` branch
convention. Its name carries no item id, its subject leads with none, and it has
never merged, so `docket flight`, `show`, `next`, `concurrent` and the digest all
read it as nobody's work. It is the exact shape `PL-CP74` is about, sitting on
the remote right now.

**Why it matters.** It is the only branch in the repository that `PL-CP74`'s new
`tools/branch_id_check.py` would refuse, and it cannot be refused retroactively —
the check runs against `HEAD`, so it fires for the session that is on a branch,
never for one somebody left behind. So this needs a person: the commit is the
project owner's own, from a naming era that predates the convention, and only
they know whether the articles it adds are wanted.

Three outcomes and they are not equivalent. Merge it, if the content belongs —
filing an item first so the merge is attributed. Delete the branch, if it does
not. Or leave it, which is a real answer for an owner's scratch branch, and then
it becomes the standing counter-example any future work on `PL-B73C` has to
tolerate: naming unattributed refs in the digest would print this one in every
session forever.

**Where.** `origin/Review_articles`. Nothing in the tree.

**Done when.** The branch is merged behind an item, deleted, or explicitly kept
with that decision recorded here, so the next session that notices it does not
re-open the question.
