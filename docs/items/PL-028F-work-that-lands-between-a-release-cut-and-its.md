---
id: PL-028F
title: Work that lands between a release cut and its merge is inside the tag's span but absent from the release notes, and nothing reconciles the two
priority: P2
effort: M
status: done
closed: 2026-09-14
classes: defect, infra
feature: release-roadmap-seam
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_checks.py, ROADMAP.md
verify: uv run pytest subprojects/docket/tests/test_checks.py subprojects/docket/tests/test_vcs.py && grep -q 'def test_the_cut_window_names_what_landed_since_the_cut' subprojects/docket/tests/test_checks.py
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

## Decided and built 2026-09-14: report, do not act - and the count is what made it worth building

**Decided: shape 2.** `bin/docket check` raises an advisory on a checkout
carrying an unmerged cut, naming what the base has taken since and both
dispositions. `ROADMAP.md` § "Tags" records what the span includes, which this
brief's **Done when.** requires under either shape.

### First, the number, because "structural rather than a one-off" was an assertion

This brief rests on one observation. Measured across every tagged span, by
matching each `(#N)` on the base against the `pr:` of the item it closed and
asking whether that item's `milestone:` is a later release:

| | |
| --- | --- |
| tagged spans examined | **47** |
| spans whose tag covers a closing pull request its own notes never name | **11 (23%)** |
| such pull requests in total | **12** |

Close to one release in four, so the brief's claim holds and the build is
justified. `PL-D9WD` reproduces exactly as recorded: `#311` merged 2026-09-04
17:00:40, v0.3.8's release merge landed 17:15:00, and `git describe --contains`
on it answers `v0.3.8~1` while `docs/releases/v0.3.8.md` names it nowhere.

**A second measurement changed where the check had to go.** The window leaves
no trace: a squash merge gives the release commit the same author and commit
date on all 42 releases, so `main`'s own history cannot say how long a branch
was open, and the divergence is recoverable only by matching pull request
numbers against stamps. Anything that reconciles *after* the fact would be
working from a record that cannot describe the thing it is reconciling. So the
report has to happen while the cut is unmerged, which is also the only moment
anything can still be done about it.

**One recurring instance is a convention rather than a defect**, and it is
excluded deliberately: a release's own cut item closes inside its own span and
is stamped with the next release, which happens every time and which this
project already writes down ("Twenty-one items, one of which is the v0.4.10 cut
itself").

### Why shape 1 loses, and it is not on cost

*Re-stamp at merge* keeps the notes and the tag identical by construction, and
it has no trigger here. `PL-N5WZ` established that a push made with
`GITHUB_TOKEN` starts no workflow, so `main`'s required status checks can never
report on a commit a merge-fired job pushes - the same wall the merge-time `pr:`
write hit, and the reason that job was withdrawn. Every variant that does land
needs a person at the merge, which is shape 2 with extra machinery.

The judgment is also genuinely the person's. Absorbing a newcomer means the
release narrative describing work this session did not do, which this brief
already rejected on sight as the "recommend first, research afterwards"
failure; letting it go to the next release is often right. `CLAUDE.md`: a tool
that guesses at the judgment half is worse than no tool.

Shape 3 stays rejected on the brief's own reasoning.

### Built

- `vcs.cut_window` reads the checkout's own `HEAD` for a notes file the base
  lacks, and returns the version being cut with the ids the base gained since
  the fork. It reads `HEAD` alone rather than every ref, unlike
  `cuts_in_flight`: the question is what *this* session is about to tag.
- `checks._check_cut_window` subtracts what the notes already name and what
  this cut stamped, and advises on the rest. Advisory rather than error,
  because both dispositions are legitimate; it fires only on a checkout
  carrying an unmerged cut, so every other run pays one `git diff`.
- The advisory names the remedy that already exists - re-running
  `make release VERSION=X`, which reclaims what the cut stamped rather than
  shipping the remainder - and says the ids are read from commit subjects, so
  one may be in-progress work rather than a closure. That accuracy is right for
  something a person looks at and was the wrong accuracy for `PL-8M8H`, which
  had to refuse the same read because its verdict acts.
- A `declined` window is said out loud rather than read as empty: silence there
  would mean "nothing landed in the window", which is the one wrong answer.

### Not done here, and named rather than folded in

The 11 historical spans are not repaired. Re-tagging is destructive and the
notes are a record of what each cut stamped, so the fix would be a sentence per
release pointing at where the work is described - twelve edits to shipped
history, which is a scoping call rather than this item's work. `ROADMAP.md`
§ "Tags" now states the general rule instead, which is what makes the existing
divergences legible without rewriting them.
