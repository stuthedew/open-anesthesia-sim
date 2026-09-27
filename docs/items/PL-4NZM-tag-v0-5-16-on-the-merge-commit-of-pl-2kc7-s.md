---
id: PL-4NZM
title: Tag v0.5.16 on the merge commit of PL-2KC7's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: ready
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-27
payoff: v0.5.16 carries its annotated tag, so the next cut is not refused and git describe resolves across it
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do: PL-N936 measured the failure, a dry run reporting [new tag] and the real push dying on an unexpected disconnect
---

**Problem.** Tag v0.5.16 on the merge commit of PL-2KC7's cut: the release is cut and only the project owner can push a tag ref from this environment

**Why it matters.** `PL-2KC7` cut v0.5.16 and stopped where the tooling
stops: `bin/docket release` does not tag, and a session cannot push a tag ref
from this environment (`PL-N936`). Until the tag is on origin, `bin/docket
release` refuses the next cut and `git describe` resolves nothing across the
span. Once it is, v0.5.15's span is no longer the newest, and
`tools/doc_check.py` holds v0.5.15's notes to every closure inside it: the one
such closure is `PL-NC62` (`#1188`), which merged during v0.5.15's review, and
the cut added its pointer to v0.5.15's notes, so none is owed.

**Done when.** `git ls-remote --tags origin v0.5.16` shows the annotated tag
peeling to the commit that added `docs/releases/v0.5.16.md` on `main`, which
for a squash merge is the cut's own merge. The owner runs, once `PL-2KC7`'s
pull request has merged:

```bash
git fetch origin main
git tag -a v0.5.16 "$(git log --first-parent --diff-filter=A --format=%H origin/main -- docs/releases/v0.5.16.md)" -m "v0.5.16"
git push origin v0.5.16
```

Run before the merge, the lookup finds nothing and `git tag` refuses with
`Failed to resolve ''`; run after a later merge, it still tags the cut.
