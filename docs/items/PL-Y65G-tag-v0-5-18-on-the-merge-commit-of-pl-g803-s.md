---
id: PL-Y65G
title: Tag v0.5.18 on the merge commit of PL-G803's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: done
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-30
closed: 2026-09-30
pr: 1244
payoff: v0.5.18 carries its annotated tag, so the next cut is not refused and git describe resolves across it
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do: PL-N936 measured the failure, a dry run reporting [new tag] and the real push dying on an unexpected disconnect
---

**Problem.** Tag v0.5.18 on the merge commit of PL-G803's cut: the release is cut and only the project owner can push a tag ref from this environment

**Why it matters.** `bin/docket release` refuses to cut the next release while
v0.5.18 is untagged, and `git describe --contains` resolves nothing across an
untagged span.

**Done when.** `git ls-remote --tags origin v0.5.18` lists the tag, peeling to
the commit that added `docs/releases/v0.5.18.md` on `main`. After the cut
merges, the owner runs:

```bash
git fetch origin main
[ -z "$(git tag -l v0.5.18)" ] || git ls-remote --exit-code origin refs/tags/v0.5.18 >/dev/null || [ $? -ne 2 ] || git tag -d v0.5.18
git tag -a v0.5.18 "$(git log --first-parent --diff-filter=A --format=%H origin/main -- docs/releases/v0.5.18.md)" -m "v0.5.18"
git push origin v0.5.18
```

**Done 2026-09-30.** The project owner pushed `v0.5.18`, and it peels to
`9ace0a34`, the commit that added `docs/releases/v0.5.18.md` (`#1236`).
