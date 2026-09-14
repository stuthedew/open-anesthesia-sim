---
id: PL-MHYG
title: "Cut v0.4.22: the release where what this project says about itself was checked against what is true"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.23
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-14
closed: 2026-09-14
pr: 554
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.22"' pyproject.toml && test -f docs/releases/v0.4.22.md
---

**Problem.** Cut v0.4.22: the release where what this project says about itself was checked against what is true

**Fifteen finished items since v0.4.21**, offered and approved by the project
owner on 2026-09-14. `v0.4.21` was confirmed tagged on the remote before the
cut, so `bin/docket release`'s refusal-on-untagged-predecessor did not apply.

**A patch, and the version policy is why.** § "Versioning decision" chooses the
number for the capability boundary a release crosses, and this crosses none:
nothing a learner can do changed, and nothing a reader of the simulator sees
changed. That is measured rather than asserted - `src/anesthesia_sim/app/`,
`tests/reference/` and `.github/` resolve to the same tree objects as at
`v0.4.21` (`7586231`, `e519afd`, `5aa42db`), and the whole of `src/` differs in
two files, neither of which moves a number: a docstring on
`core/alveolar.py` and one `sources` entry plus a rewritten `provenance_gap` on
`data/machines/reference_circle_system.json`.

**What the release is about**, in one line each, is in `ROADMAP.md`'s
`v0.4.22` version-table row under § "Versioning decision" - it was the current
baseline when this item closed, and `v0.4.23` has since taken that heading: the
specification stopped saying a measurement had
not been sought (`PL-QBKQ`, `PL-XWCY`, `PL-DJYF`); what a number says when
nothing around it qualifies it (`PL-YLKR`, `PL-DNHM`, `PL-3M3K`); and nine
apparatus items, one of which recommended destroying work (`PL-8M8H`).

**One session was waiting on the same decision and could not be told.**
`session_01LVX9BVkhKGUjMgTe2bkwwL` - the `PL-GLBF, PL-J7C5, PL-PGZK, PL-8M8H,
PL-028F` gate batch - was running with "awaiting merge + v0.4.22 cut decision"
as its state when this cut began. It is a separate container, so `SendMessage`
could not reach it; `ListAgents` reports no peer on this machine. What guards
the collision is `bin/docket release`'s own refusal on an unmerged ref carrying
a cut, which is why this branch was pushed as soon as the cut existed rather
than at the end. `PL-66FP` is the precedent - two sessions cut v0.3.7
independently and the second was discarded at the merge.

**Why it matters.** A release cut that is not recorded as an item is invisible
to every in-flight guard this project has, all of which match a `PL-` id, and
the cut is the one piece of repository work most likely to be started twice -
the session-start digest offers it to every session at once. Filing it first is
`CLAUDE.md`'s housekeeping rule, and the collision above is the reason that rule
exists.

**Done when** `pyproject.toml` reads `0.4.22`, `uv.lock` agrees,
`docs/releases/v0.4.22.md` exists with the fifteen items stamped,
`ROADMAP.md` carries the version-table row and the baseline section, and
`make check` is green. The tag is not part of this item: only the project owner
can push a tag ref from this environment, so it is filed separately.
