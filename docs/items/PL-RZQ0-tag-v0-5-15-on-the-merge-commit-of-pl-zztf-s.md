---
id: PL-RZQ0
title: Tag v0.5.15 on the merge commit of PL-ZZTF's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: ready
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-27
payoff: v0.5.15 carries its annotated tag, so the next cut is not refused and git describe resolves across it
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do: PL-N936 measured the failure, a dry run reporting [new tag] and the real push dying on an unexpected disconnect
---

**Problem.** Tag v0.5.15 on the merge commit of PL-ZZTF's cut: the release is cut and only the project owner can push a tag ref from this environment

**Why it matters.** `PL-ZZTF` cut v0.5.15 and stopped where the tooling
stops: `bin/docket release` does not tag, and a session cannot push a tag ref
from this environment (`PL-N936`). Until the tag is on origin, `bin/docket
release` refuses the next cut and `git describe` resolves nothing across the
span. Once it is, v0.5.14's span is no longer the newest, and
`tools/doc_check.py` holds v0.5.14's notes to every closure inside it; the cut
found none of the 26 items v0.5.15 ships merged inside that span, so no pointer
is owed.

**Done when.** `git ls-remote --tags origin v0.5.15` shows the annotated tag
peeling to the commit that added `docs/releases/v0.5.15.md` on `main`, which
for a squash merge is the cut's own merge. The owner runs, once `PL-ZZTF`'s
pull request has merged:

```bash
git fetch origin main
git tag -a v0.5.15 "$(git log --first-parent --diff-filter=A --format=%H origin/main -- docs/releases/v0.5.15.md)" -m "v0.5.15"
git push origin v0.5.15
```

Run before the merge, the lookup finds nothing and `git tag` refuses with
`Failed to resolve ''`; run after a later merge, it still tags the cut.
