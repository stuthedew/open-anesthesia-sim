---
id: PL-8GQW
title: Tag v0.4.30 on the merge commit of #730: the release is cut and only the project owner can push a tag ref from this environment
priority: P2
effort: S
status: ready
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-19
verify: git ls-remote --tags origin v0.4.30 | grep -q 'refs/tags/v0.4.30'
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do - PL-N936 measured the failure and found it convincing rather than obvious: git push --dry-run reports [new tag], the real push dies with send-pack: unexpected disconnect, and git ls-remote --tags then shows nothing. There is nothing to run before the work, because the work is the project owner's.
---

**Problem.** Tag v0.4.30 on the merge commit of #730: the release is cut and only the project owner can push a tag ref from this environment

**`PL-SW0D` cut v0.4.30 and stopped where the tooling stops.** `bin/docket
release` deliberately does not tag: the bump and the notes are reviewed first,
and the tag then goes on the merge commit rather than on any branch commit.

**Why it matters.** `bin/docket release` refuses to cut the next release while
the previous one is untagged, because a release cut without a tag leaves a
permanent gap that `git describe --contains` resolves nothing across, and the
gap cannot be repaired with confidence once the history has moved on. So this
blocks every later release rather than only annoying this one. Nothing in the
tree reports it either: the baseline-tag advisory was removed in v0.3.4 because
a local checkout cannot tell a release never tagged from one tagged since it
last fetched, so `git ls-remote --tags origin` is the only answer.

**Done when.** `git ls-remote --tags origin v0.4.30` resolves, on the merge
commit of #730.
