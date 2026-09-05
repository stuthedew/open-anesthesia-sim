---
id: PL-028F
title: Work that lands between a release cut and its merge is inside the tag's span but absent from the release notes, and nothing reconciles the two
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: release-roadmap-seam
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/checks.py, ROADMAP.md
added: 2026-09-04
---

**Problem.** `bin/docket release` stamps the items finished since the last
release with `milestone: vX.Y.Z` and renders `docs/releases/vX.Y.Z.md` from
them. The tag then goes on the *merge* commit, per `ROADMAP.md` § "Tags".
Anything that merges to `main` between those two moments is inside the tag's
span and named in no release notes at all until the next release claims it.

Observed cutting v0.3.8 on 2026-09-04. Six items were stamped and the notes
written; `PL-D9WD` (the M4 aggregate cache) merged as `#311` about forty
minutes later, before the release branch did. `git describe --contains` on any
of its commits will answer `v0.3.8`, while `docs/releases/v0.3.8.md` does not
mention it and `docs/releases/v0.3.9.md` will.

**Why it matters.** It is a provenance divergence rather than a cosmetic one,
and provenance is what the tag exists for: `ROADMAP.md` records the whole
point of the tag span as making every commit up to a release resolvable to the
release it went out in. Two documents now answer "what shipped in v0.3.8"
differently, and neither is wrong on its own terms — the notes list what the
queue stamped, the tag covers what the history contains.

It is structural to a release-branch cut rather than a one-off, and this
project makes it likelier than most: two sessions run in parallel on purpose,
so the window between cutting and merging is exactly when a sibling session's
pull request lands.

**Not the fix: hand-editing the rendered notes.** That was considered at the
moment of observation and rejected. The release narrative is the one document
saying what a release was *for*, and writing an M-effort item's paragraph from
a skim of somebody else's branch is the "recommend first, research afterwards"
failure `CLAUDE.md` names. Whoever cuts v0.3.9 can describe `PL-D9WD`
properly.

**Where.** `subprojects/docket/` - the release path. The decidable part is
small and is exactly the kind `CLAUDE.md` says to move out of the model: at
cut time the set of stamped items is known, and at merge time the set of items
whose closing commit is an ancestor of the merge base is known too. Comparing
them is a `git merge-base --is-ancestor` walk over closed, unstamped items.

Three shapes, and choosing between them is the work:

1. **Re-stamp at merge.** The release branch absorbs whatever landed while it
   was open — re-render the notes from the stamped set plus the newcomers.
   Keeps the notes and the tag identical by construction, and costs the
   narrative a paragraph nobody has written.
2. **Report, do not act.** `docket check` raises an advisory on a branch
   carrying an unmerged release commit when a closed, unstamped item is
   already on the base. The session cutting the release decides whether to
   absorb it or let it go to the next one. Cheapest, and it puts the judgment
   where the context is.
3. **Move the tag off the merge commit** onto the release commit itself, so
   the span stops at the cut. Rejected on sight: it breaks
   `git describe --contains` for the merge commit itself and contradicts
   `ROADMAP.md` § "Tags", which is load-bearing for the v0.1.0/v0.2.0 gap
   that section records closing.

**Done when.** Either the notes and the tag span are reconciled by
construction, or a session cutting a release is told what landed in the window
and decides — and `ROADMAP.md` § "Tags" says which, since it is the document
that currently states the tag goes on the merge commit without saying what
that includes.

**Decision needed.** Which of the two live shapes above. *Re-stamp at merge* -
the release branch absorbs whatever landed while it was open - keeps the notes
and the tag span identical by construction and is the only one that closes the
divergence without a person, at the cost of a narrative paragraph nobody has
written. *Report, do not act* - an advisory on a branch carrying an unmerged
release commit when a closed, unstamped item is already on the base - is the
cheaper and puts the judgment where the context is. The third shape, moving the
tag off the merge commit, this item rejects on sight. Whichever is taken,
`ROADMAP.md` § "Tags" is where it is written down, since that is the section
saying the tag goes on the merge commit without saying what that includes.
