---
id: PL-N936
title: "A session cannot push a tag: the real push is dropped while git push --dry-run reports success, so every release tag goes to the project owner"
priority: P3
effort: S
status: done
classes: docs
feature: dev-tooling
milestone: v0.4.5
touches: .claude/skills/docket/SKILL.md
added: 2026-09-06
closed: 2026-09-06
pr: 381
verify: python3 tools/doc_check.py check && grep -qF 'Do not try to push the tag yourself first' .claude/skills/docket/SKILL.md
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

**Confirmed the same day, and the confirmation removes the one alternative
reading.** v0.4.3 is now tagged on the remote, so the obvious objection is that
the push landed late and the two `ls-remote` checks were simply early. It did
not. The tag objects differ:

| | object | tagger |
| --- | --- | --- |
| pushed by this session | `7675d1d` | never landed |
| on the remote | `fba19c2` | Stuart Feichtinger, 2026-09-06 |

Both point at the same commit, `bfd59c4`, which is why the outcome is right;
but the object that exists is the project owner's, created after this session
reported the failure, and the one this session built is still only local. An
annotated tag records its tagger and timestamp, so two people tagging the same
commit produce different objects - which is what makes this checkable at all
rather than a matter of timing.

So the finding is not "the push is slow" or "the check was early". A session's
tag push is dropped, and the tag that appears afterwards is somebody else's.

**Closed at triage, 2026-09-06, because the work had already landed.** `a575f8d`
("PL-N936: record that a session cannot push a tag, and that the dry run says
otherwise", #375, on `origin/main`) both created this file and made the
`SKILL.md` edit, and the session left the status at `untriaged`. Checked against
the four clauses of **Done when.**: the release mode now says the push will fail
before a session tries, that `--dry-run` reports `[new tag]` anyway, that the
tag is the owner's to run, and its three-command block tags `origin/main`
directly rather than carrying a `<merge commit>` placeholder. Nothing is
outstanding, so triaging it back into the open queue would have offered finished
work to the next session.

**`pr:` will name the triage pull request, not #375.** `bin/docket record` reads
what a commit *closed*, and `a575f8d` closed nothing — it left the status at
`untriaged`, which is the whole defect here — so it declines the number and says
so ("`a575f8d` closed no item, so #375 is owed to nothing"). The closure lands
in the triage pass instead, and that is the pull request the field will record.
The work's own provenance is the paragraph above: `a575f8d`, #375.

**The `verify:` command is a reconstruction, and says so.** It was written at
close rather than before the work, so it was never watched failing in the
ordinary way. It was run both ways instead: it passes on the merged tree, and
its `grep` half exits 1 against `a575f8d^`, the tree immediately before the
edit. That is weaker evidence than a command run first — it proves the command
discriminates, not that anyone let it.
