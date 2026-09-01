---
id: PL-HXYY
title: Gate membership is recorded by milestone: on some open entries and not others
priority: P3
effort: S
status: needs-decision
classes: defect, infra
feature: dev-tooling
touches: docs/items/PL-1CYR-nothing-re-checks-the-branch-against-main.md, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/check.py, subprojects/docket/README.md
added: 2026-08-31
---

**Problem.** `PL-1CYR` carries `milestone: v0.2.8` in its front matter while
still `ready`; `PL-NSN9`, an entry on the same frozen list and equally open,
carries no `milestone:` field. Both are entries by the only test that decides
membership — `bin/docket wave` parses the ids out of `ROADMAP.md`'s gate
subsection — so the field is carrying membership information for one of them
and nothing for the other.

**Why it matters.** It is ambiguous which the field means: "this shipped in
v0.2.8", which `docket release` stamps at release time, or "this is scoped to
v0.2.8", which is what a frozen entry is. Read the first way, `PL-1CYR` claims
to have shipped in a release that has not been cut. Read the second way, every
other open entry is missing it. Nothing checks either reading, and `PL-DL1X`
is about the release path stamping this exact field too early — so a
hand-stamped `milestone:` on an open item is the same wrong state that item's
failure mode produces, arrived at by hand.

**Where.** `docs/items/PL-1CYR-*.md`; the `milestone:` handling in
`subprojects/docket/src/docket/cli.py` (`cmd_release`) and whatever in
`check.py` would enforce the rule; `subprojects/docket/README.md` for what the
field means.

**Decision needed.** Does `milestone:` mean "shipped in this release", which
is what `docket release` stamps, or "scoped to this release", which is what a
frozen entry is? The two cannot share one field: the first must be absent
until a release is cut, the second must be present on every entry from the
moment the list is frozen. Pick one meaning and give the other its own field,
or drop the second use and let `ROADMAP.md`'s gate subsection remain the only
record of membership — which is what `bin/docket wave` already reads.

**Done when.** `milestone:` has one documented meaning, an item at a status
that cannot have shipped cannot carry it (or the field is split in two), and
`docket check` enforces whichever answer is chosen.

**Note.** Found 2026-08-31 while reassessing the v0.2.8 gate. Not fixed there:
which meaning is right is a decision, and the wrong one silently rewrites the
provenance of every closed item.

**Measured 2026-09-01, while closing `PL-DL1X`.** The ambiguity has a
consequence the note above does not name: `release.unreleased` selects `done`
items with **no** `milestone`, so a hand-stamped one is invisible to the
release that actually ships it. `bin/docket release 0.2.8 --dry-run` lists 46
items and omits all ten that carry `milestone: v0.2.8` in front matter -
`PL-1CYR`, `PL-5QKT`, `PL-921W`, `PL-DVPZ`, `PL-H8MQ`, `PL-J295`, `PL-JWXF`,
`PL-KWC1`, `PL-QS72`, `PL-YSXF`. Every one of them is gate work, so the notes
for "the workflow works" would omit most of the workflow work, and a tag makes
that permanent.

That moves the item off "which reading is tidier" and onto a defect with a
deadline: it has to be settled before v0.2.8 is cut, not before the field is
documented.
