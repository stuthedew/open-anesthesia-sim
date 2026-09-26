---
id: PL-84Z4
title: Tag v0.5.12 on the merge commit of PL-5ZLQ's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: done
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-26
closed: 2026-09-26
pr: 1121
payoff: v0.5.12 carries its annotated tag, so the next cut is not refused and git describe resolves across it
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do: PL-N936 measured the failure, a dry run reporting [new tag] and the real push dying on an unexpected disconnect
---

**Problem.** Tag v0.5.12 on the merge commit of PL-5ZLQ's cut: the release is cut and only the project owner can push a tag ref from this environment

**Why it matters.** `PL-5ZLQ` cut v0.5.12 and stopped where the tooling
stops: `bin/docket release` does not tag, and a session cannot push a tag ref
from this environment (`PL-N936`). Until the tag is on origin, `bin/docket
release` refuses the next cut and `git describe` resolves nothing across the
span.

**Done when.** `git ls-remote --tags origin v0.5.12` shows the annotated tag
peeling to the commit that added `docs/releases/v0.5.12.md` on `main`, which
for a squash merge is the cut's own merge. The owner runs, once `PL-5ZLQ`'s
pull request has merged:

```bash
git fetch origin main
git tag -a v0.5.12 "$(git log --first-parent --diff-filter=A --format=%H origin/main -- docs/releases/v0.5.12.md)" -m "v0.5.12"
git push origin v0.5.12
```

Run before the merge, the lookup finds nothing and `git tag` refuses with
`Failed to resolve ''`; run after a later merge, it still tags the cut.

**Tagged 2026-09-26.** `PL-5ZLQ`'s `#1115` merged at 19:21 UTC as `05559059`,
and the owner pushed v0.5.12 at 19:26. `git ls-remote --tags origin` lists the
annotated tag object `297fdfde` peeling to `05559059`, the commit that added
`docs/releases/v0.5.12.md`, so the next cut is no longer refused on an untagged
predecessor. `#1113` and `#1116` merged after the cut was taken and before it
merged, so they sit inside the tag and are described in v0.5.13, on `PL-V065`'s
precedent.
