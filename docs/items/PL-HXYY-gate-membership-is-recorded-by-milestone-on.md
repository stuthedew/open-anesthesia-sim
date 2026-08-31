---
id: PL-HXYY
title: Gate membership is recorded by milestone: on some open entries and not others
status: untriaged
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

**Done when.** `milestone:` has one documented meaning, an item at a status
that cannot have shipped cannot carry it (or the field is split in two), and
`docket check` enforces whichever answer is chosen.

**Note.** Found 2026-08-31 while reassessing the v0.2.8 gate. Not fixed there:
which meaning is right is a decision, and the wrong one silently rewrites the
provenance of every closed item.
