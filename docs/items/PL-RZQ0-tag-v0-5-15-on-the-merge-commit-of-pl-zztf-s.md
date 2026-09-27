---
id: PL-RZQ0
title: Tag v0.5.15 on the merge commit of PL-ZZTF's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: done
classes: planning
feature: release-process
milestone: v0.5.16
touches: docs/items/
added: 2026-09-27
closed: 2026-09-27
pr: 1192
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

**Tagged 2026-09-27.** `PL-ZZTF`'s `#1190` merged at 18:03:24 UTC as
`16cb66a4`, and the owner's annotated tag is dated 18:26:35 UTC, 23 minutes
later. `git ls-remote --tags origin` lists the annotated tag object `61cb877b`
peeling to `16cb66a4`, the commit that added `docs/releases/v0.5.15.md`, so
the next cut is no longer refused on an untagged predecessor: `bin/docket
release 0.5.16 --dry-run` refuses it only for want of a release-train claim.
With v0.5.14's span no longer the newest, `tools/doc_check.py` now holds
v0.5.14's notes to every closure inside it, and `python3 tools/doc_check.py
check` passes with the tag fetched. Unlike v0.5.14, `main` took one closure
between the cut and its merge: `PL-NC62` (`#1188`), which `update-armed.yml`
merged into the cut's branch during review. It ships inside the v0.5.15 tag
with no bullet in v0.5.15's notes, and it is the one item the dry run lists
as finished since v0.5.15, so the next release describes it and v0.5.15's
notes take a pointer to it at that cut, as `ROADMAP.md`'s current baseline
section already says by name. The span's other pull request after the cut is
`#1190` itself, which `PL-ZZTF` records.
