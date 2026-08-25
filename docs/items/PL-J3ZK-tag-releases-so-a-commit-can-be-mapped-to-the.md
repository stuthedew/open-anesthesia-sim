---
id: PL-J3ZK
title: Tag releases so a commit can be mapped to the version it shipped in
priority: P2
effort: S
status: ready
classes: infra, session-cost
feature: dev-tooling
touches: subprojects/docket/src/docket/release.py, .claude/skills/docket/SKILL.md
added: 2026-08-25
---

**Problem.** Only `v0.0.1` and `v0.0.2` are tagged. Versions since then were
bumped in `pyproject.toml` and shipped without a tag, so `git describe
--contains` resolves nothing for any commit after `v0.0.2`, and there is no
way to ask which release a given change went out in.

**Why it matters.** It cost real accuracy once already. Backfilling the
`milestone` field on historical items should have been a git query - find the
first tag containing each item's commit - and instead had to fall back to
stamping all of them `v0.2.2`, which is true but coarse: work that actually
shipped in 0.1.0 or 0.2.0 is now recorded as having shipped in 0.2.2. For a
project whose standard is that a displayed value be traceable to the exact
version that produced it, an unreliable version history is a provenance gap,
not a tidiness one.

**Where.** `subprojects/docket/src/docket/release.py` (the release command
already prints the tag to create, but nothing enforces it),
`.claude/skills/docket/SKILL.md`.

**First step.** Decide whether `docket release` should create the tag itself
or keep printing the instruction. Creating it is a write to shared history
from a tool that otherwise only edits files, which argues for keeping the
instruction and adding a check that the previous version was tagged before a
new one is cut.

**Done when.** Cutting a release either creates the tag or refuses while the
previous version is untagged, and the existing untagged versions have been
tagged retrospectively at the commits that shipped them.

**Context.** Found while inverting the milestone model so that a release
records what shipped rather than planning what will. The backfill is recorded
in the commit that introduced it.
