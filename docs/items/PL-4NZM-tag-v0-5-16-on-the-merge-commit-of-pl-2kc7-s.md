---
id: PL-4NZM
title: Tag v0.5.16 on the merge commit of PL-2KC7's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: done
classes: planning
feature: release-process
milestone: v0.5.17
touches: docs/items/
added: 2026-09-27
closed: 2026-09-27
pr: 1208
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

**Tagged 2026-09-27.** `PL-2KC7`'s `#1200` merged at 20:15:51 UTC as
`553522c6`, and the owner's annotated tag is dated 20:49:58 UTC, 34 minutes
later. `git ls-remote --tags origin` lists the annotated tag object `1705b9bb`
peeling to `553522c6`, the commit that added `docs/releases/v0.5.16.md`, so
the next cut is no longer refused on an untagged predecessor: `bin/docket
release 0.5.17 --dry-run` refuses it only for want of a release-train claim.
With v0.5.15's span no longer the newest, `tools/doc_check.py` now holds
v0.5.15's notes to every closure inside it, and with the tag fetched it passes
with 0 errors, because the cut gave `PL-NC62` (`#1188`) its pointer there.
As at v0.5.15, `main` took one closure between the cut and its merge:
`PL-G8TR` (`#1198`), which `update-armed.yml` merged into the cut's branch
during review. It ships inside the v0.5.16 tag with no bullet in v0.5.16's
notes, and the dry run lists it as finished since v0.5.16, so the next release
describes it and v0.5.16's notes take a pointer to it at that cut. The span's
other pull request after the cut is `#1200` itself, which `PL-2KC7` records.

