---
id: PL-G5MQ
title: Tag v0.5.14 on the merge commit of PL-47SP's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: done
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-27
closed: 2026-09-27
pr: 1159
payoff: v0.5.14 carries its annotated tag, so the next cut is not refused and git describe resolves across it
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do: PL-N936 measured the failure, a dry run reporting [new tag] and the real push dying on an unexpected disconnect
---

**Problem.** Tag v0.5.14 on the merge commit of PL-47SP's cut: the release is cut and only the project owner can push a tag ref from this environment

**Why it matters.** `PL-47SP` cut v0.5.14 and stopped where the tooling
stops: `bin/docket release` does not tag, and a session cannot push a tag ref
from this environment (`PL-N936`). Until the tag is on origin, `bin/docket
release` refuses the next cut and `git describe` resolves nothing across the
span. Once it is, v0.5.13's span is no longer the newest, and
`tools/doc_check.py` holds v0.5.13's notes to every closure inside it; the cut
found none of the 17 items v0.5.14 ships merged inside that span, so no pointer
is owed.

**Done when.** `git ls-remote --tags origin v0.5.14` shows the annotated tag
peeling to the commit that added `docs/releases/v0.5.14.md` on `main`, which
for a squash merge is the cut's own merge. The owner runs, once `PL-47SP`'s
pull request has merged:

```bash
git fetch origin main
git tag -a v0.5.14 "$(git log --first-parent --diff-filter=A --format=%H origin/main -- docs/releases/v0.5.14.md)" -m "v0.5.14"
git push origin v0.5.14
```

Run before the merge, the lookup finds nothing and `git tag` refuses with
`Failed to resolve ''`; run after a later merge, it still tags the cut.

**Tagged 2026-09-27.** `PL-47SP`'s `#1156` merged at 03:22:46 UTC as
`863dede8`, and the owner's annotated tag is dated nine seconds later. `git ls-remote
--tags origin` lists the annotated tag object `82d1749e` peeling to
`863dede8`, the commit that added `docs/releases/v0.5.14.md`, so the next cut
is no longer refused on an untagged predecessor. With v0.5.13's span no longer
the newest, `tools/doc_check.py` now holds v0.5.13's notes to every closure
inside it, and `python3 tools/doc_check.py check` passes with the tag fetched.
`main` took nothing between the cut and `#1156`'s merge, so every closure
inside v0.5.14's own span is described in v0.5.14 and it needs no pointer of
its own; the span's four pull requests that no item records, `#1144`,
`#1145`, `#1146` and `#1149`, are captures, brief corrections and a drop that
close nothing.
