---
id: PL-SWFM
title: ROADMAP.md's version table lists v0.2.3 twice and marks two rows 'current baseline'; the prose section still reads 'Current baseline: v0.2.3' after v0.2.4 shipped
priority: P3
effort: S
status: done
classes: docs
touches: ROADMAP.md
added: 2026-08-25
closed: 2026-08-25
commit: 6e19632
---

**Problem.** ROADMAP.md's version table lists v0.2.3 twice and marks two rows 'current baseline'; the prose section still reads 'Current baseline: v0.2.3' after v0.2.4 shipped

**Why it matters.** This is the remainder of PL-Z4GF's original scope — that
item's README-heading half is done (commit `d40ff83`), but its ROADMAP.md
half was never touched. `ROADMAP.md` is this project's own authoritative
version map; a duplicated row and a stale baseline heading in that file are
exactly the kind of small wrongness `PL-Z4GF` was filed to prevent, and
readers trust the rest of a provenance-anchored document less once they
notice one part of it disagrees with itself.

**Where.** `ROADMAP.md` § "Versioning decision" (the table, around the
duplicated v0.2.3 rows) and the "## Current baseline" heading and section
that follows it.

**Done when.** One row per release in the version table, exactly one marked
as the current baseline, and the baseline section heading naming that
release.

**Gate.** Frozen into v0.3.0's Gate 0 debt list (project owner, 2026-08-25):
this is the same problem PL-Z4GF's original scope named before that gate
froze, continuing under a new id rather than a new finding, per "The gate is
a snapshot, not a moving target" in ROADMAP.md.
