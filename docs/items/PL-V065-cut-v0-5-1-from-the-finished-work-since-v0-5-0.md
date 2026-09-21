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

**Done when.** `pyproject.toml` reads 0.5.1, `docs/releases/` holds the notes,
`ROADMAP.md` has the version-table row with the `current baseline` mark moved
onto it and a baseline section, `make check` is green, and the tag is run by
the project owner.
