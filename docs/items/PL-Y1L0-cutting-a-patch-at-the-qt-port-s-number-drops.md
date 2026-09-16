---
id: PL-Y1L0
title: Cutting a patch at the Qt port's number drops its section out of wave's unreleased set and moves the beat to v0.5.0, reversing PL-RKWB, and outstanding_roadmap_edits returns an identical list for 0.4.26, 0.4.27 and 0.5.0 so nothing reports it
status: untriaged
added: 2026-09-16
---

**Problem.** Cutting a patch at the Qt port's number drops its section out of wave's unreleased set and moves the beat to v0.5.0, reversing PL-RKWB, and outstanding_roadmap_edits returns an identical list for 0.4.26, 0.4.27 and 0.5.0 so nothing reports it

**Found 2026-09-16**, measured rather than argued, while triaging `PL-SYG4`.

**The measurement.** Against the live store and `ROADMAP.md` at `16f3ce0`:

```
0.4.25: beat=implement  subject='v0.4.26 - the interface moves to Qt'
                        reserved=[0.4.26, 0.5.0, 0.6.0, 0.7.0]
0.4.26: beat=implement  subject='v0.5.0 - the case you can branch'
                        reserved=[0.5.0, 0.6.0, 0.7.0]
0.4.27: beat=implement  subject='v0.5.0 - the case you can branch'
                        reserved=[0.5.0, 0.6.0, 0.7.0]
```

`wave` builds its unreleased set as `section.version > current`, so a cut at or
past the port's number drops the port's own section out of the plan and the beat
anchors on the next milestone. That reverses `PL-RKWB` - the owner's 2026-09-14
decision to put the port ahead of v0.5.0 - until somebody hand-edits
`ROADMAP.md`.

**Nothing reports it.** `outstanding_roadmap_edits`, the only post-cut roadmap
advisory, returns a byte-identical three-statement list for `0.4.26`, `0.4.27`
and `0.5.0` - the missing version-table row, the stale baseline mark, the stale
baseline heading - and never mentions a milestone section whose number the cut
has passed. `wave().problems` is empty at all three. `.claude/skills/docket/SKILL.md`
§ "Mode: ship a release" names the same three edits and no fourth.

**Why it matters.** The renumber `ROADMAP.md` provides for is load-bearing for
the plan rather than cosmetic, and the one apparatus that exists to say what a
release has made stale does not name it. A session that cuts a patch mid-port,
follows the hand-off exactly and pushes has silently reordered the release train;
the next session reads a beat that contradicts a decision of record and has
nothing to tell it why. It is the same class as `PL-VFD8` - an apparatus
answering confidently about a plan arrangement it cannot see - one file over.

**Done when.** `outstanding_roadmap_edits` names the milestone section whose
number a cut has reached or passed, as one more statement the release has made
wrong, so the hand-off says to renumber it; a test in
`subprojects/docket/tests/test_release.py` pins the arrangement above.

**Depends on `PL-KQHN`** only for the wording: if the project decides a patch no
longer takes a reserved number, this fires on the `0.4.27` case alone rather
than on both. The advisory is owed either way.
