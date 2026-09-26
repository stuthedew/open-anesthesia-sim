---
id: PL-397Q
title: subprojects/docket/README.md's release section says the digest's cut read is computed only where a release is being offered, the claim PL-FT3M corrected in cli._cuts's docstring, and names only cmd_release and the check as readers of an interrupted cut, which the digest and status now name too (PL-1BS2)
priority: P3
effort: S
status: done
classes: docs
feature: release-process
touches: subprojects/docket/README.md
added: 2026-09-25
closed: 2026-09-26
payoff: the docket README stops telling a reader that the cut walk runs only under a release offer and that only release and check report an interrupted cut, both now contradicted by the digest and status
verify: grep -qF 'is_worth_cutting' subprojects/docket/README.md && grep -qF '_interrupted' subprojects/docket/README.md
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

**Reproduced 2026-09-26** on `78b1a02b`: both sentences stand in § "Releases
are mechanical". `cmd_digest` passes `_cuts(...) if ready.is_worth_cutting`,
and it and `cmd_status` both pass `interrupted=_interrupted(...)`. The README
names neither `is_worth_cutting` nor `_interrupted`. `PL-N0MH`'s file needs
nothing more from this item, since its `recurrences:` already reads `withdrawn
2026-09-25 PL-397Q`, so `touches` is narrowed to the README. `PL-KCK8` is in
the same file and feature, but its fix goes in the `resource:` section and
concerns a different mechanism, so the two are not one edit. One sitting can
take both.

**Why it matters.** This section is the reference for how the release path
guards itself. It tells a reader that the cut walk runs only under a release
offer, but the walk also runs between milestones, where the line says `No
release to offer`. It also says only `release` and `check` see an interrupted
cut, but the digest and `status` now say why their count is short.

**Done when.** § "Releases are mechanical" says the digest's cut read runs
wherever `Readiness.is_worth_cutting` holds, not only where a release is
offered. The interrupted-cut paragraph also names the digest's `Releasable:`
line and `status`'s `Unreleased:` line as readers, through `cli._interrupted`.

**Generator check.** A one-off, which the close-out docs sweep caught as
designed. The fact misread is the link between a document sentence and the
tree fact it restates (`PL-4FBP`, `PL-G424`, both closed 2026-09-19), but
neither head's route claims this kind. `PL-4FBP` leaves a claim outside a
bound family to the close-out sweep "by decision rather than by oversight".
`PL-G424` leaves prose drift that is not a citation to judgment and the
capture rule, on purpose. `doc_check` decides whether a cited path exists,
never whether the sentence around it is still true.

**Worked.** Both sentences still stood on `17c9f3ed` when picked up, and
`cmd_digest` and `cmd_status` still read as the brief says. The cut-read
sentence now names `Readiness.is_worth_cutting` and the `No release to offer`
case in `cli._cuts`'s own words, with `PL-FT3M`. The interrupted-cut paragraph
now names the digest's `Releasable:` line and `status`'s `Unreleased:` line as
readers through `cli._interrupted`, and says what they print instead of an
offer (the version and the command that finishes it, `render._interrupted_cut`)
and why (`PL-1BS2`). Nothing else the brief did not specify.
