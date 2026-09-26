---
id: PL-KCK8
title: subprojects/docket/README.md's resource: section says only what a claim on release-train holds, not that a done item carrying it ships in no release, which PL-KRS6 made true
status: untriaged
feature: release-process
added: 2026-09-26
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

**Done when.** The README's `resource:` section says that a `done` item
carrying `release-train` belongs to no release's count or notes, and points at
`release.unreleased` for why.
