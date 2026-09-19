---
id: PL-Z0C7
title: Cut v0.4.31 from the 10 items finished since v0.4.30: the release that completes model-capability-routing
priority: P2
effort: S
status: ready
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-19
verify: grep -q '^version = "0.4.31"' pyproject.toml && test -f docs/releases/v0.4.31.md && grep -q '^## Current baseline: v0.4.31' ROADMAP.md
---

**Problem.** Cut v0.4.31 from the 10 items finished since v0.4.30: the release that completes model-capability-routing

**Ten items have closed since v0.4.30**, and they complete the
`model-capability-routing` feature - the split that lets `bin/docket next`
say which model a given item warrants, and lets `docs/maintainer.md` name
the model on each side of it rather than saying "the strongest available"
and leaving a reader nothing to resolve.

`bin/docket release --dry-run` lists them: PL-13PB, PL-4MVC, PL-5MT4,
PL-8GQW, PL-9FNV, PL-BSYZ, PL-MN0F, PL-SW0D, PL-V8QG, PL-Z27P.

**Why it matters.** Two reasons, and the second is the one with a deadline
attached to it. A release is how this project marks a capability boundary,
and `model-capability-routing` closing is one - the split is usable from
this release rather than half-built. And `bin/docket release` refuses to cut
a release while the previous one is untagged, so each cut has to be carried
through to its tag before the next is possible; v0.4.30 is tagged
(`fe32c6f`, the merge commit of #730), so nothing blocks this one.

**Scope.** `make release VERSION=0.4.31`, never `bin/docket release` alone -
the tool writes the version into `pyproject.toml` and stops, while `uv.lock`
records the project's own version too, so the next `make check` fails on `uv
sync --locked` with the tree half-updated and the reason unrelated to the
release. `make release` runs both.

Then the half nothing generates: `ROADMAP.md` needs its version-table row,
the `current baseline` mark moved onto it, and a baseline section saying what
the release was *for*. `bin/docket release` names each statement its bump has
made stale, with line numbers. Run `make check` after those edits, not before.

**The tag is the project owner's and is not attemptable from a session.**
`git push` of a tag ref fails from this environment in a way that looks like
success - `--dry-run` reports `[new tag]`, the real push dies with
`send-pack: unexpected disconnect`, and `git ls-remote --tags` then shows
nothing (`PL-N936`). So the close-out ends by pasting the three commands
filled in, and saying the tag is outstanding until `git ls-remote --tags
origin` shows it.

**Done when** `pyproject.toml` reads 0.4.31, `docs/releases/v0.4.31.md`
exists, and `ROADMAP.md`'s current-baseline heading names v0.4.31.
