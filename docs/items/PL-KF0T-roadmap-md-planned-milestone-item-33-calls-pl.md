---
id: PL-KF0T
title: ROADMAP.md planned-milestone item 33 calls PL-2CS8, PL-NGF7 and PL-B9PY open debt that 'reach the gate on their own class', and all three are done
priority: P2
effort: S
status: done
classes: docs, defect
feature: gate-list-integrity
touches: ROADMAP.md
added: 2026-09-16
closed: 2026-09-20
verify: python3 tools/doc_check.py check && ! grep -qF 'All three are debt and reach the gate on' ROADMAP.md
---

**Problem.** ROADMAP.md planned-milestone item 33 calls PL-2CS8, PL-NGF7 and PL-B9PY open debt that 'reach the gate on their own class', and all three are done

**Found while closing `PL-D1RT`** (the stale `v0.5.x — the interface pass`
citations), reading item 33's entry end to end.

Item 33's paragraph "*The structural half is not part of this item, and lands
ahead of v0.5.0*" describes three items in the present tense as work still
owed:

> `PL-2CS8` consolidates the display constants item 24 names as its own
> prerequisite … `PL-NGF7` decides whether an explicit theme object replaces
> the Material defaults … and `PL-B9PY` is the decomposition … **All three are
> debt and reach the gate on their own class.**

All three are closed. `bin/docket show` on 2026-09-16 returns `done` for each,
and `docs/WORKING_NOTES.md` § "Shelved, then resumed: UI structure/form
mockups" already records their dispositions correctly - `PL-2CS8` (consolidate
the scattered display constants) closed in `v0.4.11`, `PL-B9PY` (decompose
`SimulationView`) landed 2026-09-14, and `PL-NGF7` (`contrast_check.py` can see
no disabled-state colour) is dissolved by the Qt port. So the two documents
disagree, and the roadmap is the one a session reads to find out what is
coming.

**Why it matters.** The sentence tells a session scoping the interface pass
that three prerequisites are still outstanding and will be counted at a debt
gate. That is a wrong answer to "can this be scoped yet" in the conservative
direction, which is the direction that goes unchallenged.

**`tools/doc_check.py` cannot catch it**: the ids all resolve and the paths all
exist; what is stale is the tense and the gate claim around them, which is the
judgment half the checker deliberately does not attempt.

**Done when** item 33's structural-half paragraph says the three landed, and
carries no claim that they are debt still to reach a gate.
