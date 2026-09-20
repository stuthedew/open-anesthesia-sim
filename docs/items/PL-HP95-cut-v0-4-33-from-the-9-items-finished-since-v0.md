---
id: PL-HP95
title: Cut v0.4.33 from the 9 items finished since v0.4.32: the release that puts the two bookmark collections in front of a learner
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 760
payoff: clears the release the session-start digest re-raises in every session, and unblocks the next cut, which docket refuses while a release is untagged
verify: grep -q '^version = "0.4.33"' pyproject.toml
---

**Problem.** Cut v0.4.33 from the 9 items finished since v0.4.32: the release that puts the two bookmark collections in front of a learner

The nine are `PL-LPLD` (the two bookmark collections), `PL-NM7X` (the
fresh-gas-flow default recorded as a teaching default), `PL-FG9D` (the
anesthesia-machine abstraction design), `PL-XJ37` (naming the fork control as
v0.5.0 scope), `PL-205P` (the `verify:` that read the remote and reddened
`main`), `PL-66Z5` and `PL-QNQJ` (the superseded branch refs and the paragraph
one of them carried), `PL-JFQ3` (promoting the nine blocked items whose
blockers had closed) and `PL-V3GD` (the `v0.4.32` cut itself). All nine are
merged on `origin/main`; `v0.4.32` is cut and tagged, so nothing is outstanding
from the previous release.

**`0.4.33` is the number, and the mechanical guess of `0.5.0` is refused by the
roadmap rather than by preference.** `ROADMAP.md` gives `0.5.0` to "the case
you can branch", whose gate still has `PL-WZVZ` and `PL-8PS6` open and whose
`Required scope` is unbuilt, so cutting `0.5.0` here would ship that milestone
under its own name with most of it missing. The patch is also right on its own
terms, on the `v0.4.25` precedent: the collections exist and are listed, but a
learner cannot yet run to a mark and stop, because the halt is `PL-CTD7` and is
not built. So no capability boundary is crossed, and every number above this
one is spent.

**The cut also clears one `pr:` backfill.** `PL-LPLD` is marked `done` on the
base and records no `pr`; `#758` is recoverable from its merge commit.
`bin/docket record` bare writes it and any other the base can supply; let it
ride the release commit rather than composing one for it.

**Procedure**, from the `docket` skill's release mode, in order:

1. `make release VERSION=0.4.33` - never `bin/docket release` alone, which
   leaves `uv.lock` stale and fails the next `uv sync --locked`.
2. `bin/docket record` for the `pr:` backfill above.
3. The edits `bin/docket release` prints as outstanding: a `ROADMAP.md`
   version-table row, the `current baseline` mark moved onto it, and a baseline
   section saying what the release was for.
4. `make check`, which is what proves those edits landed.
5. Commit, push, open the pull request; the tag is the project owner's to run
   after the merge.
