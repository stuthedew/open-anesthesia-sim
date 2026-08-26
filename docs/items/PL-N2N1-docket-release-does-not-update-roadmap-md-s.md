---
id: PL-N2N1
title: docket release does not update ROADMAP.md's version table or baseline heading, which has now drifted twice
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/release.py, subprojects/docket/README.md
added: 2026-08-26
---

**Problem.** `docket release` bumps `pyproject.toml` and writes
`docs/releases/vX.Y.Z.md`, but does not touch `ROADMAP.md` — which this
project's own header calls "the authoritative version and milestone map". So
every release leaves that file naming the previous one, until someone notices.

**Why it matters.** It has drifted twice, and the second time was one release
after the first was fixed:

- PL-Z4GF and PL-SWFM cleaned up a table that had reached two `v0.2.3` rows,
  two rows marked "current baseline", and a prose heading naming v0.2.3 after
  v0.2.4 had shipped.
- One release later, v0.2.5 shipped with no table row at all and v0.2.4 still
  marked the current baseline — found while editing the file for something
  else, not by any check.

A version map that disagrees with `pyproject.toml` is the kind of small
wrongness `CLAUDE.md` treats as a provenance problem rather than tidiness:
every release note, gate record and milestone claim in the project is anchored
to it. Two occurrences in two releases makes it recurring rather than
incidental, which is the bar under "Prefer deterministic tooling over repeated
model work".

**Note on the structural half, already done.** PL-SWFM restructured the
section so the recurrence is cheap to repair — one table row and one heading,
rather than the eighty lines of accreted per-release narrative it used to be.
That worked: this second drift took one edit to fix. What it does not do is
stop the drift happening, which needs either the command or a check.

**Where.** `subprojects/docket/src/docket/release.py` writes the version bump
and the release notes; `subprojects/docket/README.md` documents what a release
does.

**Decision needed.** Whether `docket release` should *write* `ROADMAP.md` or
`docket check` should merely *refuse* when it disagrees. Writing prose into a
hand-maintained document is a real hazard — the milestone description column
is editorial, and a generated row would either be thin or would overwrite
something considered. Refusing is cheaper, cannot corrupt the file, and fits
the existing split where `doc_check.py` decides what the tree can decide and
leaves judgment alone; the cost is that the owner still writes the row by
hand, just never forgets to. Recommend the check.

The narrow decidable version: the table contains exactly one row per released
version, matching the tags and `pyproject.toml`; exactly one row is marked
current baseline; and the "Current baseline:" heading names that same version.
All three are answerable from files on disk without parsing the editorial
column.

**Done when.** A release cannot land with `ROADMAP.md` naming a different
current version than `pyproject.toml`, either because the command maintains
those fields or because a check fails until a person does — with the choice
and its reasoning recorded in `subprojects/docket/README.md`.
