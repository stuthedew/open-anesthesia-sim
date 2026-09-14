---
id: PL-VFD8
title: The reserved-version guard cannot see a milestone that has a timeline row but no section yet, so the digest will offer v0.6.0 the moment v0.5.x is behind it
status: untriaged
feature: release-roadmap-seam
added: 2026-09-14
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
