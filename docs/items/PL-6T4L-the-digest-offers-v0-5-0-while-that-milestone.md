---
id: PL-6T4L
title: The digest offers v0.5.0 while that milestone has 8 of 22 Required scope entries open, because release_offer's reserved-version guard compares the bump against plan.step rather than the beat's milestone
priority: P2
effort: S
status: done
classes: defect, infra
feature: release-roadmap-seam
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-14
closed: 2026-09-14
verify: uv run pytest subprojects/docket/tests/test_release.py && grep -q 'def test_the_reservation_reads_the_milestone_the_beat_names_not_only_the_step' subprojects/docket/tests/test_release.py
---

**Problem.** The digest offers v0.5.0 while that milestone has 8 of 22 Required scope entries open, because release_offer's reserved-version guard compares the bump against plan.step rather than the beat's milestone

**Found 2026-09-14, on the session-start digest immediately after `#569` merged.**
The digest read `Releasable: 4 finished item(s) since 0.4.24. Offer 0.5.0
before taking new work.` directly above its own `Beat: implement v0.5.0 - the
case you can branch - its gate is clear, 14 of 22 Required scope ids closed and
8 still open.` Two lines of one digest, disagreeing about the same store.

**What acting on it would ship.** `v0.5.0` is the milestone named "the case you
can branch". Cut now, it would go out with the fork (`PL-TFX5`), the overlay
(`PL-8PSW`), the bookmarks (`PL-LPLD`), the crossing detection (`PL-CTD7`), the
element-wise reproduction assertion (`PL-Z3W6`) and the comparison
documentation (`PL-W7H9`) all unbuilt - the release whose defining feature is
branching, without branching - and would stamp `milestone: 0.5.0` onto the four
items that did land, which is the one field a later release cannot re-cut.

**The mechanism, measured rather than argued.** `release_offer` in
`subprojects/docket/src/docket/release.py:511-516` is the reserved-version
guard. It compares the bump's suggestion against **`plan.step.version`** - the
timeline row the project is *standing on* - and nothing else:

```
suggested (bump) : 0.5.0
offer.kind       : stands            <- anything but RESERVED prints an offer
guard compares   : '0.5.0' vs step '0.4.-1'         -> no match, offer stands
counterfactual   : '0.5.0' vs milestone '0.5.0'     -> MATCH, offer suppressed
```

`plan.step` is the `v0.4.x` patch-track row, whose version is `(0, 4, -1)` - the
`-1` marking a track rather than a number anything can be cut at. So the
comparison can never match, and the guard is dead in this arrangement while
looking alive.

**This is `PL-KD98`'s own lesson, applied to one branch and not the other.**
The comment at `release.py:497-505` records it exactly: reading the version from
`plan.step` "names the version in two of the three release arrangements and not
in the third", and left on `step` the digest "offered `0.4.21` directly above a
beat reading `release v0.5.0`". That fix taught the `RELEASE` branch (491-509)
to read `plan.release_version` from the beat. The `RESERVED` branch five lines
below still reads `plan.step`, and it is the same defect in the opposite
direction - there the offer was mis-numbered, here it is not suppressed at all.

**Why it is compounding friction rather than a queue item to rank.** It meets
`CLAUDE.md`'s first test: it gives a wrong answer silently. The guard exists
solely to stop a milestone version being cut before its milestone is finished,
and `bin/docket release` will accept `VERSION=0.5.0` without complaint because
naming the version is the operator's job in this project. So nothing between
the digest's instruction and a mislabelled permanent release is working. It
also sits upstream of everything, in the line the skill says to offer
proactively and the only line in the digest that tells a session to *do*
something - `render.py:1457-1465`'s own docstring says so.

**Where.** `subprojects/docket/src/docket/release.py:511-516`. The guard should
consult the beat's milestone as well as the step - `plan.gate.milestone.version`
when the beat is `implement`, which is the arrangement `plan.step.version`
cannot express. The `RESERVED` message already reads correctly for this case:
"No release to offer: the roadmap gives 0.5.0 to "v0.5.0 - the case you can
branch", which is unfinished - the beat below is what is due."

**Owed a regression test**, which is why this is not a fix-now: the case is a
project standing on a patch-track row while the beat is `implement` on a
milestone whose number the bump has just arrived at. `subprojects/docket/tests/test_release.py`
already holds the `PL-KD98` fixtures this can be built from - line 906 and 924
assert `"No release to offer" not in digest`, and line 938 asserts the
`RESERVED` wording, so the shape is there.

**Why it matters.** The offer is the only line in the digest that tells a
session to *do* something, and nothing downstream of it objects: `bin/docket
release` takes the version from whoever runs it, because naming it is the
operator's job in this project (`docket.toml`'s `version_policy = "manual"`).
So the path from a wrong digest line to a permanent, mislabelled tag has no
second check on it. `.claude/rules/apparatus-standard.md`'s floor is the rule
it breaks: what this apparatus tells a session must be true, or must say what
it could not read - and here it was neither true nor hedged.

**Done when.** `release_offer` withholds the offer where the bump's suggestion
is the version the roadmap has given to the milestone the beat is about, and
not only to the timeline row the project stands on; a test pins the arrangement
that produced this - the step a patch track, the beat `implement`, the
suggestion equal to that milestone's version - and the digest's release line
and beat line can no longer disagree on it.

**Not the same as `PL-1BS2`**, which is the digest's readiness line missing the
*interrupted-cut* resume. This is the reserved-version guard.

**Fixed 2026-09-14.** The guard now reads two carriers rather than one:
`plan.step` as before, and `plan.milestone` - the field `Wave` documents as
"the milestone the beat is about". No new state, and nothing cuttable is
suppressed: a `release` beat returns from the branch above it, because `wave`
sets `release_version` whenever it sets that beat, and every other beat is one
whose own wording says its target is unfinished. Measured against the live
roadmap immediately after: `ReleaseOffer(kind='reserved', version='0.5.0',
milestone='the case you can branch')`, so the digest now reads `No release to
offer: the roadmap gives 0.5.0 to "the case you can branch", which is
unfinished - the beat below is what is due.`

**Widened past the brief, deliberately and by one word.** The brief proposed
`plan.gate.milestone.version` *when the beat is `implement`*. The guard reads
`plan.milestone` on every beat that reaches it, which is the same object on
`implement` and covers `clear` as well - Gate 0's shape, where the step is an
earlier milestone than the section recording the gate, so a bump arriving at
the gated milestone's number passes the step comparison untouched. It cost a
second test rather than a second mechanism.

**What it still does not cover, and why that is `PL-VFD8`.** Both carriers are
objects `wave` binds, and neither exists for a milestone that has a timeline
row but no `## ... vX.Y.Z ...` section yet: `wave` leaves `plan.milestone`
`None` on the `scope` beat, and `plan.step` is whatever row the project stands
on. `ROADMAP.md` has two such rows today - v0.6.0 "the schematic" and v0.7.0 -
so the same wrong offer returns at the next unscoped milestone. Closing it
means carrying the versions the roadmap names ahead of the current one, which
is a `Wave` field rather than a comparison, and is filed rather than taken here.

**Swept.** `subprojects/docket/README.md`'s "The offer a session reads is
reconciled with the plan before it is printed" paragraph said the suggestion is
put beside "`wave`'s current step" and named only the step; it now names both
carriers and says why they are different objects. `.claude/skills/docket/SKILL.md`'s
release mode said the withheld line "names that step"; it now says a step or a
milestone. Checked and still true without editing: `docs/resident-instructions.md`
(its `release.py` reference is `PL-66FP`'s duplicate-cut refusal, untouched
here), `ROADMAP.md`, `docs/worker.md`, `docs/maintainer.md`, `docs/ARCHITECTURE.md`
and `docs/WORKING_NOTES.md`.
