---
id: PL-Z4GF
title: README's Current status heading still says v0.2.3 while the shipped version is v0.2.4
priority: P2
effort: S
status: ready
classes: defect, docs
touches: README.md, ROADMAP.md
added: 2026-08-25
---
**Problem.** `README.md`'s "Current status" heading reads v0.2.3 while the
shipped version is v0.2.4. `ROADMAP.md` has the same drift and worse: its
version table carries two separate `v0.2.3` rows split by a blank line, one of
them marked "Completed / current baseline" alongside a `v0.2.4` row also marked
"current baseline", and the "## Current baseline: v0.2.3" section heading below
it names the wrong release.

**Why it matters.** These two files are the authoritative version map and the
first thing a reader meets. A reader cannot tell which release they are looking
at, and the duplicated table row makes the release history itself ambiguous -
which is the record every provenance claim in this project is anchored to.

**Where.** `README.md` § "Current status"; `ROADMAP.md` § "Versioning decision"
(the table, around the duplicated v0.2.3 rows) and the "## Current baseline"
heading and section that follows it.

**Done when.** One row per release in the version table, exactly one marked as
the current baseline, the baseline section heading naming that release, and
`README.md` agreeing with both. Worth checking at the same time whether
`docket release` can assert this rather than leaving it to be noticed
(PL-674D is already open on that command).
