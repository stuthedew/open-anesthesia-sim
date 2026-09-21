---
id: PL-V065
title: "Cut v0.5.1 from the work finished since v0.5.0: the grooming, sweep and queue-tooling fixes that follow the MVP, with nothing computational moved"
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-21
closed: 2026-09-21
pr: 866
payoff: the finished work since the MVP ships under its own number and stops being re-offered in every session digest, and the release that carries no simulator change says so in the one place a reader checks
verify: grep -q "^version = \"0.5.1\"" pyproject.toml
---

**Problem.** Twelve items have closed since v0.5.0 and are re-offered in every
session digest. They are grooming, gate-staleness and queue-tooling work; none
of them is a milestone, so this is a patch release rather than a capability
boundary.

## The sequencing constraint, measured rather than assumed

The project owner asked for `PL-DG84`'s stale-open-thread advisory (#861) and
`PL-YVP7`'s Required-scope entry 9 (#862) to ship in this version. **The cut
must run after both merge, not before**, because `bin/docket release` stamps
`milestone:` onto items that are `status: done` *in the tree the cut runs on*:

- `PL-YVP7` merged as #862 (`186d8e27`). `status: done` on `main`; the dry run
  picks it up, and the PR number is recoverable from the merge commit.
- `PL-DG84` reads `status: ready` on `main` until #861 merges. Cutting first
  omits it **silently** - the dry run run on `186d8e27` lists 12 items and
  `PL-DG84` is not among them.

Merging #861's branch into the release branch instead was rejected on three
counts: the bullet would cite no pull request, there being no merge commit to
recover one from, which is the defect `PL-W7WL` fixed across 128 bullets; both
branches would carry the same item file under different `milestone:` stamps;
and if the release merged first, the `v0.5.1` tag would sit on a commit that
does not contain the work its own notes cite.

## What this release contains, by tree object

`src/anesthesia_sim/data` (`ab3499fd`), `core` (`ca5a3542`), `app` (`01bc2d90`)
and `tests/reference` (`a1848300`) are **byte-identical at v0.5.0 and at the
cut**. No equation, parameter, constant, numerical method, solver step or
displayed clinical value moves in this release, and #861 does not change that:
it touches `subprojects/docket/` and `docs/WORKING_NOTES.md` only.

## What the cut was shipped as, and what that was chosen over

`#863` (`PL-ZM48`, `PL-X9WZ`) merged after this cut was taken and before it
landed, and `#864`, `#865` and `#867` were open and green at the same moment.
**Ship the cut as taken** (project owner, 2026-09-21, ratified, over holding
this pull request while those merged and re-running `make release
VERSION=0.5.1`, which resumes a cut under the same number and would have picked
the newly-`done` items up).

The argument that decided it is the treadmill rather than the tidiness: while
sibling sessions keep landing pull requests, any regenerated set of notes goes
stale before it can merge - `#867` appeared while the question was being put.
The cost is stated rather than smoothed over: the v0.5.1 tag contains
`PL-ZM48` and `PL-X9WZ` without naming them, and they are cited under v0.5.2.
`PL-4B1G` shows the same shape is already accepted here - the cut of v0.5.0 is
inside the v0.5.0 tag and is cited in v0.5.1's notes, because a cut cannot
stamp itself.

Recorded in `ROADMAP.md`'s v0.5.1 baseline section too, since that is where a
reader meets the gap rather than here.

**Done when.** `pyproject.toml` reads 0.5.1, `docs/releases/` holds the notes,
`ROADMAP.md` has the version-table row with the `current baseline` mark moved
onto it and a baseline section, `make check` is green, and the tag is run by
the project owner.
