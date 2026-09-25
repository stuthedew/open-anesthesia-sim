---
id: PL-397Q
title: subprojects/docket/README.md's release section says the digest's cut read is computed only where a release is being offered, the claim PL-FT3M corrected in cli._cuts's docstring, and names only cmd_release and the check as readers of an interrupted cut, which the digest and status now name too (PL-1BS2)
status: untriaged
feature: release-process
touches: subprojects/docket/README.md, docs/items/PL-N0MH-only-docket-check-names-the-settings-it-ran.md
added: 2026-09-25
---

**Problem.** subprojects/docket/README.md's release section says the digest's cut read is computed only where a release is being offered, the claim PL-FT3M corrected in cli._cuts's docstring, and names only cmd_release and the check as readers of an interrupted cut, which the digest and status now name too (PL-1BS2)

**Found 2026-09-25 in `PL-FT3M` and `PL-1BS2`'s close-out docs sweep.** Two
lines of `subprojects/docket/README.md` § "Releases are mechanical", outside
both items' `touches`:

- "The digest carries the same answer on its `Releasable:` line, computed only
  where a release is actually being offered" is the claim `PL-FT3M` corrected
  in `cli._cuts`'s docstring. The walk is gated on `Readiness.is_worth_cutting`,
  so it also runs where the line says `No release to offer` because the
  roadmap has reserved the number.
- "both halves of the repair read it: `cmd_release` folds those items back in
  ... and `checks._check_release_notes` reports the state" is still true but no
  longer the whole of it: since `PL-1BS2` the digest's `Releasable:` line and
  `status`'s `Unreleased:` line name an interrupted cut too, through
  `cli._interrupted`.

**Not a recurrence of `PL-N0MH`**, which `bin/docket new` recorded it as. That
item is about `next`, `digest`, `status` and `list` not naming the settings
they ran under with `--items`; this one is README prose about the release
path, and shares no file or function with it.
