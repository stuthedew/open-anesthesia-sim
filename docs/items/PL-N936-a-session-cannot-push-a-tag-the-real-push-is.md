---
id: PL-N936
title: "A session cannot push a tag: the real push is dropped while git push --dry-run reports success, so every release tag goes to the project owner"
status: untriaged
feature: dev-tooling
touches: .claude/skills/docket/SKILL.md
added: 2026-09-06
---

**Problem.** Pushing a tag from a container session fails, and the way it fails
is worse than the failure. Observed 2026-09-06 cutting v0.4.3, twice:

```
$ git push --dry-run origin v0.4.3
To https://github.com/stuthedew/open-anesthesia-sim
 * [new tag]         v0.4.3 -> v0.4.3          <- accepted

$ git push origin v0.4.3
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
Everything up-to-date                          <- and the tag is not there
```

`git ls-remote --tags origin` confirms the tag never landed. Branch pushes from
the same session, to the same remote, over the same proxy, worked repeatedly
before and after - including the commit the tag was to point at - so this is
specific to tag refs rather than to the network or to credentials in general.
The proxy reports healthy while it happens: `recentRelayFailures: []` from
`$HTTPS_PROXY/__agentproxy/status`.

**Why it matters, and why the dry run is the worst part.** The last line is
`Everything up-to-date`, which reads as success to anyone skimming, and the
`--dry-run` that a careful session runs *first* to check whether it may push
reports `[new tag]`. So the obvious way to test the capability returns a false
green, and the obvious way to read the failure returns a false success. A
session that trusted either would report a release tagged when it is not - and
an untagged release is the one repository state `bin/docket release` refuses to
cut across, so the cost lands on whoever cuts next rather than on whoever
caused it.

Nothing catches it either. `tools/doc_check.py`'s release-tag check reported
`0 errors` on the merged v0.4.3 tree with no v0.4.3 tag anywhere, which is
correct behaviour rather than a bug - v0.4.2's row in `ROADMAP.md` records
that the baseline-tag advisory was removed in v0.3.4 precisely because a local
checkout cannot tell a release never tagged from one tagged since it last
fetched - but it does mean the gap
is invisible from inside the tree.

**This is the third operation in the same family.** `PL-TFWR` and `PL-XQRK`
record that a session cannot delete a remote branch, because the proxy drops
the deletion ref, so every branch cleanup ends on the project owner's desk.
Tagging is the same shape: an operation a session will reasonably attempt, that
fails in a way that does not look like a failure, and whose only remedy is to
hand the exact commands over.

**Where.** `.claude/skills/docket/SKILL.md`, Mode: ship a release - which
already says "Never ask the owner to 'tag vX.Y.Z'. Paste the commands, filled
in", and is therefore already right about *who* tags. What it does not say is
that the session must not try first, or that `--dry-run` will encourage it to.

**Done when.** A session reading the release mode knows before it tries that
the tag push will fail, that `--dry-run` will say otherwise, and that the
commands go to the owner - and the three-command block it hands over resolves
the merge commit itself rather than carrying a placeholder to fill in.

**Found while cutting v0.4.3 (`PL-Y0W6`), 2026-09-06.** The release is merged
as `bfd59c4` and was still untagged when this was written.
