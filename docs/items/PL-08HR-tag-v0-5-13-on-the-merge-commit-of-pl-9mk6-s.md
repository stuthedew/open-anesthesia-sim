---
id: PL-08HR
title: Tag v0.5.13 on the merge commit of PL-9MK6's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: done
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-26
closed: 2026-09-26
pr: 1143
payoff: v0.5.13 carries its annotated tag, so the next cut is not refused and git describe resolves across it
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do: PL-N936 measured the failure, a dry run reporting [new tag] and the real push dying on an unexpected disconnect
---

**Problem.** Tag v0.5.13 on the merge commit of PL-9MK6's cut: the release is cut and only the project owner can push a tag ref from this environment

**Why it matters.** `PL-9MK6` cut v0.5.13 and stopped where the tooling
stops: `bin/docket release` does not tag, and a session cannot push a tag ref
from this environment (`PL-N936`). Until the tag is on origin, `bin/docket
release` refuses the next cut and `git describe` resolves nothing across the
span. And once it is, v0.5.12's span is no longer the newest, so
`tools/doc_check.py` holds v0.5.12's notes to the pointer for `#1113` and
`#1116` that the cut wrote.

**Done when.** `git ls-remote --tags origin v0.5.13` shows the annotated tag
peeling to the commit that added `docs/releases/v0.5.13.md` on `main`, which
for a squash merge is the cut's own merge. The owner runs, once `PL-9MK6`'s
pull request has merged:

```bash
git fetch origin main
git tag -a v0.5.13 "$(git log --first-parent --diff-filter=A --format=%H origin/main -- docs/releases/v0.5.13.md)" -m "v0.5.13"
git push origin v0.5.13
```

Run before the merge, the lookup finds nothing and `git tag` refuses with
`Failed to resolve ''`; run after a later merge, it still tags the cut.

**Tagged 2026-09-26.** `PL-9MK6`'s `#1141` merged at 23:54 UTC as `c7fcd6f2`,
and the owner tagged and pushed v0.5.13 at 23:55. `git ls-remote --tags origin`
lists the annotated tag object `6abf31b4` peeling to `c7fcd6f2`, the commit that
added `docs/releases/v0.5.13.md`, so the next cut is no longer refused on an
untagged predecessor. With v0.5.12's span no longer the newest,
`tools/doc_check.py` now holds v0.5.12's notes to the pointer the cut wrote for
`#1113` and `#1116`, and `python3 tools/doc_check.py check` passes with the tag
fetched. Nothing merged between the re-cut at 18 items and `#1141`'s merge, so
every closure inside v0.5.13's own span is described in v0.5.13 and it needs no
pointer of its own; the span's four pull requests that no item records, `#1120`,
`#1124`, `#1128` and `#1130`, are captures and design rounds that close nothing.
