---
id: PL-LRP2
title: Tag v0.5.9 on the merge commit of PL-R498's cut: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: done
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-24
closed: 2026-09-24
payoff: v0.5.9 carries its annotated tag, so the next cut is not refused and git describe resolves across it
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do: PL-N936 measured the failure, a dry run reporting [new tag] and the real push dying on an unexpected disconnect
recurrences: 2026-09-24 PL-08D4
---

**Problem.** Tag v0.5.9 on the merge commit of PL-R498's cut: the release is cut and only the project owner can push a tag ref from this environment

**`PL-R498` cut v0.5.9 and stopped where the tooling stops.** `bin/docket
release` deliberately does not tag: the bump and the notes are reviewed first,
and the tag then goes on the merge commit rather than on any branch commit.

**Which commit.** Two commits on `main` lead with `PL-R498: cut v0.5.9`. `#978`
merged with only `PL-R498`'s capture and its first start claim, and its subject
reads "PL-R498: cut v0.5.9 from the 27 items finished since v0.5.8" - it is not
the cut, and the tag must never go on it (`PL-H14W`). The cut's own merge leads
with "PL-R498: cut v0.5.9, the release where", which the second command below
resolves. If it resolves nothing, `git tag` fails on an empty ref rather than
tagging the wrong commit.

```bash
git fetch origin main
git tag -a v0.5.9 "$(git log origin/main -1 --format=%H --grep='^PL-R498: cut v0.5.9, the release where')" -m "v0.5.9"
git push origin v0.5.9
```

**Why it matters.** `bin/docket release` refuses to cut the next release while
the previous one is untagged, because a release cut without a tag leaves a
permanent gap that `git describe --contains` resolves nothing across. Nothing
in the tree reports it either, so `git ls-remote --tags origin v0.5.9` is the
only answer.

**Done when.** `git ls-remote --tags origin v0.5.9` resolves, on the merge
commit of the pull request that carries `PL-R498`'s cut.

**Done 2026-09-24.** The project owner pushed the tag. `git ls-remote --tags
origin` shows `refs/tags/v0.5.9` as an annotated tag object (`6da21496`)
peeling to `6c8307e0`, "PL-R498: cut v0.5.9, the release where ...", which is
the cut's own merge and not `8428844c`. Closed in `PL-NLXK`'s cut of v0.5.10,
which the tag let through the untagged-predecessor refusal.
