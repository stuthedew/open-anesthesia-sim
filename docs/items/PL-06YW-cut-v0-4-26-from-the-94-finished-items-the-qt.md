---
id: PL-06YW
title: Cut v0.4.26 from the 94 finished items: the Qt port release, whose Required scope is 28 of 28 closed and whose section takes the number
priority: P2
effort: S
status: ready
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-17
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.26"' pyproject.toml && test -f docs/releases/v0.4.26.md && grep -q '^## Completed: v0.4.26 - the interface moves to Qt' ROADMAP.md
---

**Problem.** Cut v0.4.26 from the 94 finished items: the Qt port release, whose Required scope is 28 of 28 closed and whose section takes the number

**Asked for by the project owner, 2026-09-17.** Ninety-four finished items sit
unshipped since `v0.4.25` (`bin/docket release --dry-run`).

**Why this number and not the mechanical one.** `bin/docket wave` puts the beat
at "release v0.4.26 - the interface moves to Qt", and the port's own Required
scope is **28 of 28 closed**. The mechanical bump is `0.5.0`, which
`ROADMAP.md` has given to the next milestone: cutting that would ship "the case
you can branch" under its own name with sixteen items of it unbuilt. Gate 1
stands at 167 of 170 cleared with **nothing left that it can clear** - its three
open entries (`PL-WZVZ`, `PL-Z34C`, `PL-8PS6`) are blocked on work outside the
gate - so the cadence's no-interim-release rule does not bind. `v0.4.25` is
tagged on `origin` at `6f2532d`, so the refusal-on-untagged-predecessor does not
bind either.

**The definition of done, checked rather than assumed.** Every clause in
§ "v0.4.26 - the interface moves to Qt" -> "Definition of done" has a closed
item behind it: parity and the two re-pointed theme checks (`PL-BXB2`,
`PL-V53R`, `PL-NGF7`), the headless rendering test (`PL-YCWZ`, `PL-2QMK`),
`PL-GS3R`'s re-measured worst drawn departure, `docs/ARCHITECTURE.md`
(`PL-9KP5`), and the spike deletion with the last Flet import (`PL-7SVX`). The
last is confirmed against the tree rather than the item: no `spikes/` directory
exists and no module under `src/` names Flet - the only surviving mentions are
two `pyproject.toml` comments recording that the boundary check now permits it
nowhere.

**What the cut carries in `ROADMAP.md`, and the one edit nothing reports.**
`bin/docket release` names three stale statements - the missing version-table
row, the baseline mark and the baseline heading. It does not name the fourth,
because `outstanding_roadmap_edits` returns an identical three-statement list
for every version: the milestone section whose number the cut reaches. That is
`PL-Y1L0`'s finding, and here the section it applies to is the port's own, which
must be promoted to `## Completed:` by hand. The `verify:` command pins that
heading for exactly that reason.

**Why it matters.** The port is the largest rewrite this project has run - 28
Required-scope ids, `app/` re-expressed on PySide6 and pyqtgraph - and its own
definition of done is *parity against the Flet build*. A tag is what makes that
claim checkable afterwards: "every capability `v0.4.25` had" is immutable and
diffable, where "whatever `origin/main` was that day" is not. Three of the 94
are `P1` `safety` (`PL-GS3R`'s drawn departure, `PL-YVHK`'s hover readout,
`PL-2K1R`'s interpretation disclaimer), and leaving them untagged across the
project's largest span means `git describe --contains` resolves nothing over the
release that carried them. The cut is also what the next beat stands on: Gate 2
freezes when v0.5.0 ships, and v0.5.0's implementation is the beat after this
one.

**Done when.** `pyproject.toml` and `uv.lock` read `0.4.26`,
`docs/releases/v0.4.26.md` exists, the version table carries the row, the
"Current baseline" section stands on `v0.4.26`, the port's section reads
`## Completed: v0.4.26 - the interface moves to Qt`, its timeline row records
the ship, `make check` is green, and `v0.4.26` is tagged on the merge commit on
`origin/main`.
