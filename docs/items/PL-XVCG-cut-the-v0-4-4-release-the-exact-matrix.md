---
id: PL-XVCG
title: 'Cut the v0.4.4 release: the exact matrix exponential and its re-derivations'
priority: P2
effort: S
status: done
classes: planning, docs
feature: planning-cadence
milestone: v0.4.5
added: 2026-09-06
closed: 2026-09-06
pr: 379
not-delegable: proving a release cut means cutting the release. No command can run beforehand - `make release` refuses while the previous version is untagged, and the version-table row, baseline mark and release prose it stops short of are judged by a reader rather than by a check
---

**Problem.** Cut the v0.4.4 release: the exact matrix exponential and its re-derivations

**Why it matters.**

**Where.**

**Done when.**

**Done 2026-09-06.** Thirteen items since 0.4.3. `make release VERSION=0.4.4`
bumped `pyproject.toml`, relocked `uv.lock` and wrote `docs/releases/v0.4.4.md`;
the ROADMAP version-table row, the moved `current baseline` mark, the new
baseline section and the `### v0.4.4` release narrative are the hand half.

The version is a patch and stays one: `ROADMAP.md`'s `v0.4.x` row already
settles that the exact step crosses no capability boundary. What it does cross,
and what the prose leads on, is that a displayed number moves in its last digit
- the first release since v0.4.0 where that is true, and the first to touch
`src/` in four.

The `v0.4.x` track is **not** finished by this release. `PL-GS5X`, `PL-3TLK`
and `PL-X9KD` are done; the `core-domain-language` naming items (`PL-H46J`,
`PL-212V`, `PL-9SH6`, `PL-VZL0`, `PL-FZ6T`, `PL-X2XX`) remain, so the row keeps
its place in the plan.
