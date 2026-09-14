---
id: PL-THPB
title: Tag v0.4.21 on the merge commit of #549: the release is cut and only the project owner can push a tag ref from this environment
status: done
added: 2026-09-13
closed: 2026-09-13
verify: git ls-remote --tags origin v0.4.21 | grep -q 'refs/tags/v0.4.21'
---

**Problem.** Tag v0.4.21 on the merge commit of #549: the release is cut and only the project owner can push a tag ref from this environment

**Why this is an item and not only a line in a reply.** `.claude/rules/instruction-writing.md`
rule 14 requires a request that could outlive the sitting to be captured as
well, and an untagged release is that rule's own worked example: `v0.3.8` sat
untagged for hours because the request lived only in a closing block whose
session was then archived (`PL-H1JD`).

**Nothing in the tree reports the gap.** `tools/doc_check.py`'s baseline-tag
advisory was retired in v0.3.4 - a local checkout cannot tell a release never
tagged from one tagged since it last fetched - so the only thing that catches
this is `bin/docket release` refusing to cut v0.4.22. `git ls-remote --tags
origin` is what answers.

**The commands, to be run once `#549` is merged**, while `origin/main` *is* the
merge commit:

    git fetch origin main
    git tag -a v0.4.21 origin/main -m "v0.4.21"
    git push origin v0.4.21

**Not delegable to a session.** A tag push from this environment reports
`[new tag]` on a dry run and then dies with `send-pack: unexpected disconnect`,
ending on `Everything up-to-date` while the remote has no tag (`PL-N936`).
Branch pushes from the same session work throughout, so this is tag refs
specifically.

**Done when.** `git ls-remote --tags origin` returns `refs/tags/v0.4.21`.

**Done, and verified rather than assumed (2026-09-13).** The project owner
pushed the tag. `git ls-remote --tags origin v0.4.21` returns
`777dbca21c7685785bda3444197f0470dfcb47ca refs/tags/v0.4.21`, and
`git rev-list -n1 v0.4.21` resolves to `6cd1a1da`, which is `#549`'s merge
commit - so the tag exists on the remote and sits where this item asked for it.

**Recovered from an abandoned branch.** This file existed only on
`origin/claude/next-version-release-o2zzaf`, pushed there after `#549` had
already merged, so nothing merged it and nothing else reported it - the
post-merge-push case `bin/docket stranded` names. Its session
(`PL-4KKR: cut v0.4.21`) archived in a failed state mid-push, which is what
makes this an abandoned branch rather than live work someone else holds.
The branch itself is now the project owner's to delete; see the closing block
of the session that recovered this.
