---
id: PL-H1GH
title: "Cut the v0.4.7 release: the supported run length, the tolerance gate, and traces you can tell apart"
priority: P2
effort: S
status: done
classes: planning
feature: release-process
touches: ROADMAP.md, pyproject.toml, uv.lock, docs/releases, docs/items/
added: 2026-09-07
closed: 2026-09-07
pr: 425
verify: grep -q '^version = "0.4.7"' pyproject.toml && test -f docs/releases/v0.4.7.md && grep -qF '## Current baseline: v0.4.7' ROADMAP.md && grep -qF '| v0.4.7 | Completed / current baseline |' ROADMAP.md
---

**Problem.** Ten items finished since v0.4.6 with no release carrying them, and
`ROADMAP.md`'s `v0.4.x` row says patches are cut as work accumulates. The cut
itself takes a commit of its own, so it is filed rather than done unfiled
(`CLAUDE.md`, housekeeping nobody filed).

**Why now rather than earlier.** This was offered twice and declined once on
its own merits. When it was first raised the only releasable item was
`PL-5VR1`, the item that cut v0.4.6 — a release whose whole content is the
bookkeeping of the previous release crosses no boundary and is not worth a
number. What changed is that nine more merged, three of them safety- or
science-classed, and the reason given for holding (four sessions still in
flight) was spent when all four of their pull requests landed.

**What it carries.** `PL-Y5WR` (the supported run length and its halt),
`PL-ZVS7` (the control-resolution tolerance gate), `PL-GVXP` (chart traces
separated by line style, held to 3:1 in four vision models), `PL-3YZW`,
`PL-8ZJQ` and `PL-BD94` (the venous pool's first source and its rename),
`PL-KX9N` (shallow-clone provenance in `docket record`), `PL-QPJZ`
(`bin/docket trend`), `PL-LYX2` (the 2026-09-06 triage pass) and `PL-5VR1`
(the v0.4.6 cut).

**One thing this cut did that the procedure does not name.** The first
`make release` produced notes in which five of the ten items carried no pull
request number, because they had merged without one being recorded and the
notes are generated from the store. Rather than hand-edit generated notes, the
cut was reverted in the working tree, `bin/docket record` was run to write all
five, and the release was cut again. That is the skill's own rule — let the
`record` write ride a commit you are already making — applied to the one commit
in the project that is always available to it. Recorded here because the next
cut will meet the same condition whenever items merge faster than commits are
made against `main`.

**Done when.** `make release VERSION=0.4.7` has run, `ROADMAP.md` carries the
version-table row and the moved baseline, `make check` passes, and the tag is
outstanding with the owner.

**Closed 2026-09-07.** Cut with `make release VERSION=0.4.7`; version-table row
and `## Current baseline: v0.4.7` written; every item in the notes carries its
pull-request number. The tag is the project owner's to push and is outstanding
until they confirm it.
