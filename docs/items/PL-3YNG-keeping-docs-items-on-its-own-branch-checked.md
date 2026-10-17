---
id: PL-3YNG
title: Keeping docs/items on its own branch, checked out as a worktree inside the project, would end item-only pull requests but break closure-with-the-work and per-commit provenance: analysed 2026-10-17, recommended against
status: dropped
added: 2026-10-17
closed: 2026-10-17
reason: the owner agreed with the recommendation to drop it, 2026-10-17; recorded as a dead end
---

**Problem.** Keeping docs/items on its own branch, checked out as a worktree inside the project, would end item-only pull requests but break closure-with-the-work and per-commit provenance: analysed 2026-10-17, recommended against

**Analysed 2026-10-17, at the owner's question, read-only.** What it would
buy: no item-only pull requests (8-10 a week now, each a full `checks` run, but
they auto-merge, so no one's attention); captures that cannot strand (already
at zero: `bin/docket stranded` found none, and `PL-WNCT`'s generator drained
2026-09-22). What it would cost:

1. Closure stops travelling with its work: 808 of 809 `main` commits in the
   30 days to 2026-10-17 touched `docs/items/`; the docket README § "The number
   is written before the merge, by the branch that closes the item" records the
   100-second window that split once opened.
2. Provenance splits from the code citing it: 767 distinct ids cited in `src/`,
   `tests/`, `docs/MODEL.md` and `README.md`; an old tag would no longer carry
   the items explaining its constants.
3. `flight`, `stranded`, `claim`, `record`, `arm`, `verify --self` and the
   merge-loss walk all assume an item rides its branch.
4. Worktree setup in every ephemeral container; git refuses one branch in two
   worktrees (measured, git 2.43.0); an in-tree path reopens `PL-2P5L` and
   `PL-M9QW`'s class; push contention on one shared ref; and whether a session
   may push outside `claude/*` is unmeasured.
5. Item edits would land with no pre-merge `bin/docket check`.

Precedent: beads added a sync branch on hidden worktrees in v0.28.0
(2025-12-01) and deleted it, about 11,000 lines, in v0.53.0 (2026-02-18), as
part of a move to Dolt storage (https://github.com/steveyegge/beads/blob/main/CHANGELOG.md).

**Recommendation: drop it, and add a line to `docs/dead-ends.md` citing this
item.** Awaiting the owner's word; the CI-time motive behind it is `PL-H9KW`
and `PL-DXD4`.

**Answered 2026-10-17: dropped, and recorded in `docs/dead-ends.md` under
"Store and queue design"** (project owner, 2026-10-17, ratified, over keeping
`docs/items/` on a branch of its own checked out as a worktree).
