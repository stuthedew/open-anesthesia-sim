---
id: PL-2YSL
title: "Cut v0.4.23: the release where standing decisions were re-taken by counting, and the counts moved them"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-14
closed: 2026-09-14
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.23"' pyproject.toml && test -f docs/releases/v0.4.23.md
---

**Problem.** Cut v0.4.23: the release where standing decisions were re-taken by counting, and the counts moved them

**Fourteen finished items since v0.4.21**, offered and approved by the project
owner on 2026-09-14. `v0.4.22` was confirmed tagged on the remote
(`8cf9be3` -> `82f00d3`) before the cut, so `bin/docket release`'s
refusal-on-untagged-predecessor did not apply, and `list_sessions` showed no
live session carrying a cut.

**Why it matters.** A release cut is repository work that no other item names,
so `CLAUDE.md`'s housekeeping rule requires it filed before it is done: every
in-flight guard this project has matches a `PL-` id, and an unfiled cut is
invisible to all of them - which is how two sessions cut `v0.3.7` (`PL-66FP`).
The cut also carries the half nothing generates. `bin/docket release` writes
the bump and the notes; `ROADMAP.md`'s version-table row, the `current
baseline` mark and the baseline section are prose saying what the release was
*for*, and a release shipped without them leaves the project's own account of
itself one release behind.

**A patch, and the version policy is why.** `ROADMAP.md` § "Versioning
decision" chooses the number for the capability boundary a release crosses,
and this crosses none: nothing a learner can do changed. `bin/docket wave`
puts the project between numbered steps on `v0.4.x - the code is the model`,
with Gate 1 the next beat, so `0.4.23` is the patch-track successor rather
than a milestone claiming a name it has not earned.

**Done when.** `pyproject.toml` and `uv.lock` carry `0.4.23`,
`docs/releases/v0.4.23.md` exists, `ROADMAP.md` has the version-table row, the
moved `current baseline` mark and the baseline section, `make check` is green,
and the tag is handed to the project owner as three runnable commands - the
one step this environment cannot perform (`PL-N936`).
