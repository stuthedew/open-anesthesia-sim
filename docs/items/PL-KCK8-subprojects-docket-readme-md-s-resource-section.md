---
id: PL-KCK8
title: subprojects/docket/README.md's resource: section says only what a claim on release-train holds, not that a done item carrying it ships in no release, which PL-KRS6 made true
priority: P3
effort: S
status: done
classes: docs
feature: release-process
touches: subprojects/docket/README.md
added: 2026-09-26
closed: 2026-09-26
pr: 1061
payoff: a reader who learns resource: from the README knows the release item ships in no release, instead of expecting it in the next release's count and notes
verify: grep -qF 'PL-KRS6' subprojects/docket/README.md
---

**Problem.** subprojects/docket/README.md's resource: section says only what a claim on release-train holds, not that a done item carrying it ships in no release, which PL-KRS6 made true

**Why it matters.** The section headed "`resource:` names a shared thing the
item's claim also holds" is the item format's reference for the field, and it
now describes one of the field's two effects. Since `PL-KRS6`,
`release.unreleased` leaves out a `done` item whose `resource` is
`release-train`, so the item a release is cut under counts toward no release
and no notes name it. A reader who learns the field from the README expects
that item to ship in the next release, which is the convention `PL-KRS6`
reversed. Nothing there is false today, so this is a gap rather than a wrong
statement.

**Where.** `subprojects/docket/README.md`, under the heading "`resource:` names
a shared thing the item's claim also holds". Found 2026-09-26 while closing
`PL-KRS6`, whose `touches` do not reach the README. The rule and its reason are
in `release.unreleased`'s docstring and in
`.claude/skills/docket/modes/release.md`, the paragraph headed "Close the
release item after the cut, never before it".

**Reproduced 2026-09-26** on `78b1a02b`: the `resource:` section says what a
claim on the train holds and says nothing about `release.unreleased`, which
keeps only items whose `resource` is not `RELEASE_TRAIN`. The `milestone:`
section just below
describes `release.unreleased` as selecting "finished work with **no**
milestone", and it leaves out this exception too. The README does not cite
`PL-KRS6` anywhere. `PL-397Q` is in the same file and feature, but its fix
goes in § "Releases are mechanical" and concerns a different mechanism, so the
two are not one edit. One sitting can take both.

**Done when.** The README's `resource:` section says that a `done` item
carrying `release-train` belongs to no release's count or notes, and points at
`release.unreleased` for why, citing `PL-KRS6`.

**Generator check.** A one-off, which the close-out docs sweep caught as
designed. The fact misread is the link between a document sentence and the
tree fact it restates (`PL-4FBP`, `PL-G424`, both closed 2026-09-19), but
neither head's route claims this kind. `PL-4FBP` leaves a claim outside a
bound family to the close-out sweep "by decision rather than by oversight".
`PL-G424` leaves prose drift that is not a citation to judgment and the
capture rule, on purpose. `doc_check` decides whether a cited path exists,
never whether the sentence around it is still true.

**Worked.** Still a gap on `17c9f3ed` when picked up: the `resource:` section
said nothing of `release.unreleased`, and the README cited `PL-KRS6` nowhere.
A paragraph after the section's first now says a `done` item carrying
`release-train` belongs to no release's count or notes, points at
`release.unreleased`'s docstring for why, and cites `PL-KRS6`. One edit the
Done-when did not name: the `milestone:` section's "selects finished work with
**no** milestone" gained "(and no `resource: release-train`, above)", since the
brief's reproduction names that sentence as leaving out the same exception and
it is in the one file this item declares.
