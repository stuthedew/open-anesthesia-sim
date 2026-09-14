---
id: PL-6TQH
title: "Tag v0.4.23 on the merge commit of #559: the release is cut and only the project owner can push a tag ref from this environment"
priority: P2
effort: S
status: ready
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-14
verify: git ls-remote --tags origin v0.4.23 | grep -q 'refs/tags/v0.4.23'
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do - `PL-N936` measured the failure and found it convincing rather than obvious: `git push --dry-run` reports `[new tag]`, the real push dies with `send-pack: unexpected disconnect`, and `git ls-remote --tags` then shows nothing. There is nothing to run before the work, because the work is the project owner's.
---

**Problem.** Tag v0.4.23 on the merge commit of #559: the release is cut and only the project owner can push a tag ref from this environment

**Why it matters.** `bin/docket release` refuses to cut the next release while
the previous one is untagged, because a release cut without a tag leaves a
permanent gap - `git describe --contains` resolves nothing across its span -
and the gap cannot be repaired with confidence once the history has moved on.
So an untagged `v0.4.23` blocks `v0.4.24` and every release after it.

**Nothing in the tree reports the gap.** `tools/doc_check.py`'s baseline-tag
advisory was removed in `v0.3.4` because a local checkout cannot tell a release
never tagged from one tagged since it last fetched, so `git ls-remote --tags
origin` is the only thing that answers. `v0.3.8` sat untagged for hours on
exactly this shape, and was caught only because a second session happened to
raise it (`PL-H1JD`) - which is why this is an item rather than a line in a
reply that disappears when its session is archived.

**Done when.** `git ls-remote --tags origin v0.4.23` resolves. The commands,
to be run once #559 is merged and `origin/main` is the merge commit:

```bash
git fetch origin main
git tag -a v0.4.23 origin/main -m "v0.4.23"
git push origin v0.4.23
```
