---
id: PL-XR8K
title: "Tag v0.4.22 on the merge commit of #554: the release is cut and only the project owner can push a tag ref from this environment"
priority: P2
effort: S
status: done
classes: planning
feature: release-process
touches: docs/items/
added: 2026-09-14
closed: 2026-09-14
not-delegable: Proving this means pushing a tag ref to the remote, which no session in this environment can do - `PL-N936` measured the failure and found it convincing rather than obvious. There is nothing to run before the work, because the work is the project owner's.
verify: git ls-remote --tags origin v0.4.22 | grep -q 'refs/tags/v0.4.22'
---

**Problem.** Tag v0.4.22 on the merge commit of #554: the release is cut and only the project owner can push a tag ref from this environment

**Why this is an item and not only a line in a reply.**
`.claude/rules/instruction-writing.md` rule 14 requires a request that could
outlive the sitting to be captured as well, and an untagged release is that
rule's own worked example: `v0.3.8` sat untagged for hours because the session
holding the request was archived and its closing block went with it
(`PL-H1JD`). `PL-THPB` is the same item one release earlier.

**Why a session cannot do it.** `git push` of a tag ref from this environment
fails, and fails convincingly: `--dry-run` reports `[new tag]`, the real push
dies with `send-pack: unexpected disconnect` and ends on `Everything
up-to-date`, and `git ls-remote --tags` then shows nothing. Branch pushes from
the same session work throughout, so it is tag refs specifically (`PL-N936`).

**What it blocks if it is not done.** `bin/docket release` refuses to cut the
next release while the previous one is untagged, and it is right to: a release
cut without a tag leaves a permanent gap that `git describe --contains`
resolves nothing across, and the gap cannot be repaired with confidence once
the history has moved on. Nothing in the tree reports the omission either - the
baseline-tag advisory was removed in v0.3.4 because a local checkout cannot
tell a release never tagged from one tagged since it last fetched - so
`git ls-remote --tags origin` is the only thing that answers.

**It also unblocks `PL-2M5T`**, which needs the release tagged before
`bin/docket release` will look at v0.4.22 again.

**Done when** `git ls-remote --tags origin` shows `refs/tags/v0.4.22` on the
merge commit of #554.

**Why it matters.** The tag is what ties a span of commits to the release they
went out in, and that mapping is not recoverable afterwards. Every later
release is blocked behind it by a deliberate refusal, so an untagged release
stops the release train rather than merely leaving a gap in it.

**Done 2026-09-14.** `git ls-remote --tags origin` shows
`8cf9be39a2d8f0be7c205fbe5a45d46728ba2778 refs/tags/v0.4.22`, dereferencing to
`82f00d3a80bbee5eac25635e0901398e17f8f967`, which is `#554`'s merge commit — so
the tag exists on the remote and sits where this item asked for it. The project
owner pushed it, as the item said only they could.

**It was closed because CI said so, which is the point of the `verify:` line.**
`quality.yml` run #1884 on `82f00d3a` failed `make docket` with "PL-XR8K is open
but its `verify:` command already passes", and that error was the only thing red
on `main`. The item's own evidence command is what noticed the tag had landed;
no session watched for it. A `verify:` line that names something only the work
creates turns "did the owner do the thing yet" into a check that fails loudly
the moment the answer changes, rather than a request that decays in a closing
block (`PL-H1JD`).
