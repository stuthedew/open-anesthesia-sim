---
id: PL-WT9L
title: Tag v0.5.19 on the merge commit of PL-84MH's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: done
classes: planning
feature: release-process
milestone: v0.5.20
touches: docs/items/
added: 2026-09-30
closed: 2026-09-30
pr: 1248
payoff: v0.5.19 carries its annotated tag, so the next cut is not refused and git describe resolves across it
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do: PL-N936 measured the failure, a dry run reporting [new tag] and the real push dying on an unexpected disconnect
---

**Problem.** Tag v0.5.19 on the merge commit of PL-84MH's cut: the release is cut and only the project owner can push a tag ref from this environment

**Generator check.** Bookkeeping: the owner's step after every cut, because
`PL-N936` measured that no session in this environment can push a tag ref -
`PL-08D4`'s recurring design, not a defect firing. `PL-2FY6` asks whether a
workflow should tag the cut on merge and retire this step.

**Done 2026-09-30.** The project owner pushed the annotated tag after `#1246`
merged. `git ls-remote --tags origin` lists `refs/tags/v0.5.19` (`5f8771a`),
peeling to `f52adae`, the v0.5.19 cut's own merge commit.
