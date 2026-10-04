---
id: PL-BLKJ
title: docket's release.notes_by_version reads a notes bullet with its own one-line pattern rather than through notes_bullets, so a bullet inside an HTML comment or a fence is claimed and one opening on an empty marker line is missed; latent
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** docket's release.notes_by_version reads a notes bullet with its own one-line pattern rather than through notes_bullets, so a bullet inside an HTML comment or a fence is claimed and one opening on an empty marker line is missed; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`NOTES_ENTRY_RE` is `^- (PL-id)` over physical lines. Release notes holding a comment around "- PL-CCCC withdrawn from this release" (with a blank line inside) claim `PL-CCCC`; an entry whose marker stands alone, "-" over "  PL-CCCC Title on the next line — #5", is not claimed; a fenced example bullet is. CommonMark § 4.6, § 4.5, § 5.2. Consumers: `checks._check_release_notes`, the notes reads in `cli.py` and `unrecorded_milestones`. `notes_bullets` is the reader the head's fix rule names, and its walker's own gaps are a sibling member. Latent: the 79 notes files hold no comment, fence or bare marker, and this pattern's claims equal `notes_bullets`' ids in all 79.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
