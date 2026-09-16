---
id: PL-VFD8
title: The reserved-version guard cannot see a milestone that has a timeline row but no section yet, so the digest will offer v0.6.0 the moment v0.5.x is behind it
priority: P2
effort: M
status: done
classes: defect
feature: release-roadmap-seam
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_release.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md, ROADMAP.md, docs/items/PL-SYG4-the-digest-s-reserved-verdict-suppresses-the.md
added: 2026-09-14
closed: 2026-09-16
pr: 606
verify: uv run pytest subprojects/docket/tests/test_release.py && grep -q 'def test_a_timeline_row_with_no_section_reserves_its_version' subprojects/docket/tests/test_release.py
---

**Problem.** The reserved-version guard cannot see a milestone that has a timeline row but no section yet, so the digest will offer v0.6.0 the moment v0.5.x is behind it

**Found 2026-09-14 while closing `PL-6T4L`** (the digest offering v0.5.0 while
that milestone had 8 of 22 `Required scope` entries open). That fix taught
`release_offer`'s reserved-version guard to read `plan.milestone` - the
milestone the beat is about - as well as `plan.step`. Both are objects `wave`
binds, and there is a third arrangement in which it binds neither.

**The mechanism, measured rather than argued.** `wave`'s no-gate branch finds
the milestone *section* whose version matches the first milestone row ahead of
the current version, and binds `None` when the roadmap has no such section yet
- which is the normal state of a milestone that has a timeline row and has not
been scoped. The beat is then `scope`, and the only carrier left is the row the
project stands on. Probed against a fixture carrying the live grammar:

```
timeline    1 milestone (0, 5, 1) 'v0.5.1 - the interface moves to Qt'
            4 gate      None      'Gate 2'
            5 milestone (0, 6, 0) 'v0.6.0 - the schematic'      <- no section
version     0.5.1
beat        scope        subject 'v0.6.0 - the schematic'
step        'Gate 2'     version None        <- carries no number at all
milestone   None                              <- no section to bind
OFFER       ReleaseOffer(kind='stands', version='0.6.0', milestone='')
```

So the digest would print `Offer 0.6.0 before taking new work` while the
roadmap gives 0.6.0 to "the schematic", unscoped - `PL-6T4L`'s failure again,
one milestone later. `ROADMAP.md` has two rows in exactly this state today:
v0.6.0 - the schematic, and v0.7.0 - multi-substance and nitrous oxide.

**`plan.next_step` is not the fix.** It happens to carry the number in the
probe above, where the project stands on the gate row - but this timeline puts
a gate row between each milestone and the next, so a project standing on a
patch track has `next_step` on the gate and the number one row further on. A
carrier that works in one of two adjacent arrangements is how this defect has
arrived three times (`PL-D2GW`, `PL-KD98`, `PL-6T4L`).

**Why it matters.** It is the same silent wrong answer `PL-6T4L` records, with
the same consequence: the offer is the only line in the digest that tells a
session to *do* something, and `bin/docket release` takes the version from
whoever runs it, so nothing downstream objects before the tag is permanent.
The difference is only that it fires at the next unscoped milestone rather than
at this one.

**Done when.** The reserved-version guard answers from every version the
roadmap names ahead of the current one - carried on `Wave` where `wave` already
has the timeline rows and the milestone sections in hand, rather than
recomputed - and a test pins the arrangement above: a milestone with a timeline
row and no section, the bump arriving at its version, and the offer withheld
naming it. The existing two carriers keep answering as they do today, so
`PL-6T4L`'s tests stand unchanged.

**Not a widening of the guard's reach.** Every version this would add is one
the roadmap places *ahead* of the current version, which is unreleased by
construction; the release beat returns before the comparison, so the version a
release is actually due at is still offered. Measured on the live roadmap the
day this was filed, the addition changes no answer: from 0.4.24 the bump can
only arrive at 0.5.0, which the beat's milestone already holds.

**Why it matters.** The guard exists so a session is never offered a version
the roadmap has already promised to an unfinished milestone - the failure
`PL-6T4L` caught, where the digest would have stamped `milestone: 0.5.0` onto
four items and tagged a branching release with no branching in it. A milestone
that has a timeline row but no section yet is exactly the state every milestone
passes through between being placed and being scoped, so the blind spot is not
an edge case; it is the window in which the next version is most likely to be
reached. `PL-FWJF` is the same structural gap seen from the `wave` side - a
`-` row carrying real intent that the readers skip.

**Done when.** A version named by a timeline row is reserved whether or not a
section for it exists yet, so a digest between v0.5.x and v0.6.0 declines to
offer v0.6.0 and says which row holds it. `tests/unit/` covers a row with no
section.

**`PL-188T` is this defect by a third door** (filed 2026-09-14 by the
pre-port survey, and it says so itself): once `v0.4.25` was cut and the port's
section moved to `v0.4.26`, `wave` binds `step = v0.4.x` and
`milestone = v0.5.0`, so a simulated `release_offer` on a `0.4.26` bump returns
`stands` and a patch cut mid-port is offered the port's own number. Its
`Done when` is this item's verbatim. Close both together.

**It stopped being hypothetical on 2026-09-15, and by a fourth door.** Observed
on `origin/main` at `17403970`, `bin/docket digest`:

```
Releasable: 42 finished item(s) since 0.4.25. Offer 0.5.0 before taking new work.
Plan: 0.4.25, between numbered steps (v0.4.x - the code is the model). Beat:
implement v0.4.26 - the interface moves to Qt - the timeline puts it before
v0.5.0 - the case you can branch, whose gate is clear, 19 of 26 Required scope
ids closed and 7 still open.
```

Two adjacent lines contradicting each other in every session's first read: cut
0.5.0, and the milestone holding 0.5.0 has not been reached.

**This arrangement is outside what the docstring claims is reachable**, which
is worth more than the instance. `ReleaseOffer`'s docstring says the case
neither carrier sees is "an unscoped milestone, which has a timeline row and no
section yet". **v0.5.0 is fully scoped** - goal, Required scope, definition of
done, frozen gate. What put it out of reach was `PL-RKWB` moving the Qt port
*between* the step the project stands on and that milestone on 2026-09-14: both
carriers reach one row, and nothing reaches two. So the blind spot is a
*distance* rather than a *state*, and the docstring's statement of its own
limits is too narrow. Correct that with the fix.

**What made it visible rather than what caused it.** Gate 1's last clearable
entry closed in `#597`, moving the beat from `clear` to `implement`; the
suppression had been firing through the `clear` path. Nothing about `#597`
touched this code.

**Four doors now, and that is the argument against a fifth carrier.**
`PL-KD98` moved the release beat off `step`; `PL-6T4L` added the
`plan.milestone` carrier; `PL-J45M` added the `own_scope` guard; `PL-188T` is
the patch-cut-mid-port door; this is the scoped-milestone-two-rows-ahead door.
Each previous fix added a carrier for whichever arrangement had just bitten. A
fix should say why enumeration terminates, or stop enumerating - ask the
roadmap which unshipped sections and rows reserve a version and check the
suggestion against all of them, which terminates by construction. `PL-WK0N`
was filed for this instance before `PL-VFD8` was found and is dropped into
this item.

**Fixed 2026-09-16, by stopping the enumeration rather than extending it.**
`wave` now carries `reserved`: every version `ROADMAP.md` names ahead of the
current one, read from the release train's milestone rows *and* from the
milestone sections, nearest first, each with the roadmap's own name for what
holds it. `release_offer` checks the suggestion against that list instead of
against `plan.step` and `plan.milestone`. Both of those are still bound and
still used elsewhere; what changed is that the reservation no longer asks
where the project is standing, and a version is reserved by the one property
that survives the plan being rearranged - being *named* ahead of the current
one. There is no fifth arrangement to find, because the question is now about
the file rather than about a position in it.

**Measured on the live `ROADMAP.md` at `7aa507c`, before and after.** Three
probes, the first unchanged and the other two the two open doors:

```
                        before                       after
0.4.25 -> 0.5.0   reserved 'the case you can    reserved 'the case you can
                           branch'                       branch'        (PL-6T4L)
0.5.1  -> 0.6.0   stands                        reserved 'the schematic' (this)
0.4.25 -> 0.4.26  stands                        reserved 'the interface
                                                          moves to Qt'  (PL-188T)
```

The second is this item's own arrangement and the third is `PL-188T`'s, which
was live on `main`: with Gate 1 open the beat is `clear`, so `PL-FWJF`'s
carrier - which reaches the port only once that gate clears - was not holding
the port's number at all.

**Four carriers are not four tests, which is the reason for the shape.** Each
previous fix added the binding that had just bitten, and each was correct about
its own arrangement; what none of them could say is why there was not another.
Reading the roadmap's own statement of which numbers are spent terminates by
construction, and it costs less code than the two bindings it replaces.

**The exemption that stayed, and why it is not a fifth carrier.** `PL-J45M`'s
case is a *finished* gate-only milestone that `_release_due` cannot classify,
where `wave` falls through to `implement` and withholding the offer would print
"which is unfinished" against work that is done. That is a subtraction of one
version rather than an addition of a binding, it is bounded by the beat's own
milestone, and `PL-J45M` deletes it by fixing the classifier - its `verify:`
greps for the exact `supported = ...` line, which is left spelled as it was so
that check still reads true.

**The docstring's statement of its own limits is corrected, as the brief
asked.** It had claimed the one unreachable case was "an unscoped milestone,
which has a timeline row and no section yet"; the blind spot was a *distance*,
both carriers reaching one row and nothing reaching two. `ReleaseOffer` now
says what is read and where the single exemption is.

**Tests.** Four in `subprojects/docket/tests/test_release.py`, each watched
failing on the pre-fix tree: `test_a_timeline_row_with_no_section_reserves_its_version`
pins this item's arrangement (a milestone placed and not yet scoped, with a
boundary marker between it and the project so the old `step` carrier cannot
reach it); `test_a_version_named_ahead_of_the_current_one_is_reserved` pins
`PL-188T`'s; `test_the_digest_declines_the_number_of_a_milestone_it_says_to_scope`
reads the two contradicting digest lines together; and
`test_the_reserved_set_carries_every_version_the_plan_names_ahead` pins the set
itself, including that a patch track reserves nothing. The 1 000 existing
`docket` tests pass unchanged, `PL-6T4L`'s and `PL-J45M`'s among them.

**Swept.** `subprojects/docket/README.md`'s reconciliation paragraphs named two
carriers and stated the blind spot as a live limit; they now describe the
reserved set and carry the history as history. `.claude/skills/docket/SKILL.md`'s
release mode said the withheld version was given to "a step or a milestone";
it now says a milestone ahead of the current one, placed or scoped or both.
`ROADMAP.md` § "the interface moves to Qt" said the guard does not yet reserve
that number, which this makes false. `PL-SYG4` carries a dated note: its
verdict is unchanged, but the sentence resting on `PL-188T` is spent and there
are now two reserved numbers ahead of the patch track rather than one. Checked
and still true without editing: `ROADMAP.md`'s v0.4.25 baseline record and the
closed `PL-6T4L`, `PL-FWJF` and `PL-WK0N` briefs, which are records of what was
true when they closed; `docs/ARCHITECTURE.md`, `docs/worker.md`,
`docs/maintainer.md`, `docs/WORKING_NOTES.md` and `docs/resident-instructions.md`,
none of which names the guard.
