---
id: PL-674D
title: '`docket release` bumps pyproject.toml but leaves uv.lock stale, breaking make check'
priority: P2
effort: S
status: needs-decision
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/release.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-08-25
---

**Problem.** `docket release` writes the new version into `pyproject.toml`
and stops. `uv.lock` records the project's own version too, so the very next
command a release runs - `make check`, whose first step is `uv sync
--locked` - fails with "The lockfile at `uv.lock` needs to be updated, but
`--locked` was provided". Hit while cutting v0.2.3; fixed there by running
`uv lock`, which produced a one-line diff.

**Why it matters.** The failure lands between "the release is written" and
"the release is verified", which is the worst place for it: the tree is
half-updated, `make check` is red, and the reason has nothing to do with the
release's content. A session that has not seen it before will read a red
`make check` as its own doing. Small, but it recurs at every release, which
is exactly the kind of thing `CLAUDE.md` says to move into code.

**Where.** `subprojects/docket/src/docket/release.py` (`bump_version`).

**Decision needed.** `docket` is standard-library-only and deliberately
package-manager-agnostic, so it cannot shell out to `uv` without acquiring a
dependency on the project's toolchain - and this repository is the only known
consumer. Three options: teach `bump_version` to rewrite a lockfile's project
version when one sits beside `version_file` (self-contained, but `docket`
starts knowing about lockfile formats); have `release` print a
toolchain-specific follow-up command from config (honest, still manual); or
leave the tool alone and record the step in the skill's release mode
(cheapest, and keeps the tool general). The last is the default unless the
first is wanted.

**Done when.** Cutting a release leaves `make check` passing without a manual
step, or the manual step is documented where the release workflow is read.
