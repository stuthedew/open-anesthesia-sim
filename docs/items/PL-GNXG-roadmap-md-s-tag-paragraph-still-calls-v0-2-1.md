---
id: PL-GNXG
title: ROADMAP.md's tag paragraph still calls v0.2.1 and v0.2.2 untagged, but both were tagged
status: dropped
closed: 2026-08-31
reason: every statement it names has since been corrected by hand on main - the tag list carries v0.2.1, v0.2.2 and v0.2.7, and the count reads two - and the check that would stop them going stale again is PL-M5FK, which PL-34B4 already widened to cover this paragraph as well as the list above it. Recovered from the branch it was stranded on and recorded as dropped rather than deleted, so the same finding is not raised a third time.
feature: dev-tooling
touches: ROADMAP.md, docs/items/PL-J3ZK-tag-releases-so-a-commit-can-be-mapped-to.md
added: 2026-08-30
---

**Problem.** `ROADMAP.md` lines 51 and 55-57 are false against the repository's
tags. Three statements, all checked against `git ls-remote --tags origin`:

- Line 51 lists v0.0.1, v0.0.2, v0.2.3, v0.2.4, v0.2.5 and v0.2.6 as carrying
  annotated tags. Nine annotated tags exist: those six plus v0.2.1, v0.2.2 and
  v0.2.7.
- Line 55 says "Four versions are untagged". Two are: v0.1.0 and v0.2.0.
- Lines 55-57 say v0.2.1 (`bc5f823`) and v0.2.2 (`3099980`) "are settled and
  only await the two commands". Both were tagged on 2026-08-29 at exactly those
  commits - `v0.2.1` -> `bc5f823`, `v0.2.2` -> `3099980`, both annotated, both
  on `origin`.

**Why it matters.** This is the same defect `PL-M5FK` (ROADMAP.md's tag list
goes stale on every release and no check reads it) records, found one release
earlier and one paragraph wider: the staleness is not confined to the sentence
that lists tag names. The branch `claude/triage-untriaged-items-c87bq1` carries
a hand fix that adds v0.2.7 to line 51 and leaves both other statements false,
which is the evidence that a hand fix is not reliable here. A section whose
subject is which releases are traceable, and which is itself wrong about it, is
the wrong way round.

**Where.** `ROADMAP.md` lines 51-64. `PL-J3ZK` (tag releases so a commit can be
mapped to the version it shipped in) is `needs-decision` and is the item those
lines cite; its retrospective half is now half-resolved by the owner's tagging,
so its open question has narrowed to v0.1.0 and v0.2.0 alone.

**Approach.** Correct all three statements in one edit, and narrow `PL-J3ZK`'s
open decision to the two versions that are still untagged. Scope the prose so
that what remains is judgment rather than a list a future release invalidates:
the names of tagged versions belong to `PL-M5FK`'s check, not to prose.

**Related.** `PL-M5FK` (ROADMAP.md's tag list goes stale on every release and
no check reads it) is the check that would have caught all three lines.
`PL-8HJ2` (make release fails mid-way on the ROADMAP table it does not write)
is the third mention of the same seam.

**Done when.** No statement in `ROADMAP.md`'s tag section disagrees with
`git tag`, and `PL-J3ZK` names only v0.1.0 and v0.2.0 as open.
