---
id: PL-BLKJ
title: docket's release.notes_by_version reads a notes bullet with its own one-line pattern rather than through notes_bullets, so a bullet inside an HTML comment or a fence is claimed and one opening on an empty marker line is missed; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/release.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: the items a release is recorded as shipping are the bullets its notes page shows, so a commented-out or fenced bullet claims nothing
verify: grep -qF '"notes by version, ' tests/unit/test_doc_check.py
---

**Problem.** docket's release.notes_by_version reads a notes bullet with its own one-line pattern rather than through notes_bullets, so a bullet inside an HTML comment or a fence is claimed and one opening on an empty marker line is missed; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`NOTES_ENTRY_RE` is `^- (PL-id)` over physical lines. Release notes holding a comment around "- PL-CCCC withdrawn from this release" (with a blank line inside) claim `PL-CCCC`; an entry whose marker stands alone, "-" over "  PL-CCCC Title on the next line — #5", is not claimed; a fenced example bullet is. CommonMark § 4.6, § 4.5, § 5.2. Consumers: `checks._check_release_notes`, the notes reads in `cli.py` and `unrecorded_milestones`. `notes_bullets` is the reader the head's fix rule names, and its walker's own gaps are a sibling member. Latent: the 79 notes files hold no comment, fence or bare marker, and this pattern's claims equal `notes_bullets`' ids in all 79.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `NOTES_ENTRY_RE` over a notes file holding "- PL-CCCC withdrawn" inside an HTML comment that also holds a blank line claims `PL-CCCC`.

**Why it matters.** `notes_by_version` is what `checks._check_release_notes`, the notes reads in `cli.py` and `unrecorded_milestones` take for the items a release shipped, so a commented-out or fenced bullet is claimed as released, and an entry opening on its own marker line is not, where `notes_bullets` - the reader every other notes check uses - says otherwise.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** `notes_by_version` reads its ids through `notes_bullets`, so the two agree on every notes file; a `notes by version, ...` case in `CONTINUED_STATEMENTS` pins it.
