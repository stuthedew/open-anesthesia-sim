---
id: PL-WK0N
title: The digest now says 'Offer 0.5.0 before taking new work' while the roadmap still gives 0.5.0 to the unfinished 'case you can branch', because the Qt port moved between the current step and that milestone and neither of release.py's two reserving carriers reaches a row two positions ahead
status: untriaged
added: 2026-09-15
---

**Problem.** The digest now says 'Offer 0.5.0 before taking new work' while the roadmap still gives 0.5.0 to the unfinished 'case you can branch', because the Qt port moved between the current step and that milestone and neither of release.py's two reserving carriers reaches a row two positions ahead

**Why it matters, and it is `CLAUDE.md`'s compounding-friction test twice
over.** The line gives a wrong answer silently - an advisory telling every
session to offer a release the roadmap's own rule forbids - and it sits in the
session-start digest, which every session reads before anything else. Acting on
it stamps `milestone: 0.5.0` onto 38 items and tags "the case you can branch"
with the branching interface unbuilt, which is exactly the outcome `PL-6T4L`
was filed to prevent.

**Observed 2026-09-15**, on the branch carrying `PL-16ZC`'s closure. The digest
read:

```
Releasable: 38 finished item(s) since 0.4.25. Offer 0.5.0 before taking new work.
Plan: 0.4.25, between numbered steps (v0.4.x - the code is the model). Beat:
implement v0.4.26 - the interface moves to Qt - the timeline puts it before
v0.5.0 - the case you can branch, whose gate is clear, 19 of 26 Required scope
ids closed and 7 still open.
```

The offer and the beat contradict each other in adjacent lines: one says cut
0.5.0, the next says the milestone holding that number has not been reached and
the one before it has 7 open scope ids.

**The mechanism, read from the source rather than inferred from the output.**
`subprojects/docket/src/docket/release.py` builds `reserved` from two carriers
and offers the suggested version when neither matches it:

1. `plan.step` - the row the project stands on. Here that is the `v0.4.x - the
   code is the model` patch-track row, which carries `(0, 4, -1)`, a track
   marker matching no suggestion. The comment above the code already says this
   carrier is "dead in this arrangement while looking alive".
2. `plan.milestone` - the milestone the beat is *about*. Here that is
   **v0.4.26**, the Qt port, guarded by `supported = plan.beat != IMPLEMENT or
   plan.own_scope is not None`, which passes because `bin/docket wave` reports
   v0.4.26's own `Required scope` of 26 ids.

`suggested` is `0.5.0`. `reserved` holds `0.4.26`. Neither carrier names
**v0.5.0**, so the loop falls through to `STANDS` and the digest offers it.

**What changed to expose it was the roadmap, not the code.** `PL-RKWB` moved
the Qt port ahead of v0.5.0 on 2026-09-14, inserting a row *between* the step
the project stands on and the milestone reserving `0.5.0`. Both carriers reach
one position; nothing reaches two. While Gate 1 still had a clearable entry the
beat was `clear`, and the suppression happened to fire through a different
path - so closing `PL-16ZC` did not cause this, it only removed the last thing
hiding it.

**It is not live on `main` yet.** It needs Gate 1's clearable count at zero,
which only the branch closing `PL-16ZC` has. Every session's digest says it the
moment that merges.

**This is the third visit to the same house.** `PL-KD98` taught the release
beat to read the version off the beat rather than off `step` and left this
comparison on `step`; `PL-6T4L` added the `plan.milestone` carrier after the
digest offered `0.5.0` above a beat reading `implement v0.5.0`; `PL-J45M` added
the `own_scope` guard. Each fix added a carrier for the arrangement that had
just bitten. The recurrence suggests the shape is wrong rather than
incomplete - a fix here should say why enumerating carriers terminates, or
replace them with something that asks the roadmap directly which sections
reserve a version, rather than adding a third.

**Done when.** The digest does not offer a version any unshipped roadmap
section reserves, however many timeline rows sit between that section and the
row the project stands on, and a regression test pins this arrangement:
patch-track step, `implement` beat about an intermediate milestone, and the
suggested version reserved by a milestone two rows ahead.
