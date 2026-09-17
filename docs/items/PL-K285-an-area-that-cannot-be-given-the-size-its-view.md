---
id: PL-K285
title: An Area that cannot be given the size its View needs says so rather than collapsing it, which is the second of the three properties docs/interface-provenance.md records Blender not supplying
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: M
blocked-by: PL-1FT6, PL-TH35
classes: safety, anticipated
touches: src/anesthesia_sim/layout/, src/anesthesia_sim/app/, tests/unit
---

**Problem.** An Area that cannot be given the size its View needs says so rather than collapsing it, which is the second of the three properties docs/interface-provenance.md records Blender not supplying

**Why it matters.** The second of the three properties
`docs/interface-provenance.md` records Blender not supplying, and the one with
no precedent to copy. Blender's answer when a region will not fit is
`RGN_FLAG_TOO_SMALL` and collapse to zero extent, which for a 3D tool costs a
keystroke; here `docs/MODEL.md` requires that a required value is never hidden
to make room, and a silent collapse is exactly the failure that division exists
to prevent.

**Done when.** The View contract says whether a declared minimum is a request
or a constraint; a split or a border drag that cannot meet it is refused or
reported rather than satisfied by collapsing; the interface says so where a
conditional surface genuinely cannot fit; and a test drives an Area below the
size its View needs and asserts the stated behaviour rather than a zero-extent
pane.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 8.
