---
id: PL-WNJG
title: Tag v0.5.17 on the merge commit of PL-HHCD's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: done
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-28
closed: 2026-09-28
pr: 1223
payoff: v0.5.17 carries its annotated tag, so the next cut is not refused and git describe resolves across it
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do: PL-N936 measured the failure, a dry run reporting [new tag] and the real push dying on an unexpected disconnect
---

**Problem.** Tag v0.5.17 on the merge commit of PL-HHCD's cut: the release is cut and only the project owner can push a tag ref from this environment

**Done 2026-09-28.** The project owner pushed `v0.5.17`, and it peels to
`2afd46f7`, the commit that added `docs/releases/v0.5.17.md` (`#1219`).
