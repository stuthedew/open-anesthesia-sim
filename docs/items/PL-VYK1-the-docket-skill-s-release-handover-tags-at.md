---
id: PL-VYK1
title: The docket skill's release handover tags at origin/main rather than at the cut's own merge commit, so a re-run of the three commands tags whatever merged next
status: untriaged
added: 2026-09-07
---

**Problem.** The docket skill's release handover tags at origin/main rather than at the cut's own merge commit, so a re-run of the three commands tags whatever merged next

`.claude/skills/docket/SKILL.md`'s release mode hands the project owner three
commands, and requires them filled in "every time, not only the first":

```bash
git fetch origin main
git tag -a v0.3.0 origin/main -m "v0.3.0"
git push origin v0.3.0
```

The middle line names `origin/main`, whose meaning moves. Run at the moment the
release merges it is right; run an hour later, after one more pull request has
merged, it tags a commit that carries the next item's work and no release at
all. `PL-BKDP` guessed this was how a `v0.4.8` tag came to sit on `b03a7d03` -
the merge commit of `#432`, which cut no release - one merge after v0.4.7 was
tagged correctly at `888c1f46`. That guess is unproven and remains one; what is
not a guess is that the command as written permits it, and that the same
skill's own instruction to resolve the merge commit rather than leave a
placeholder is undercut by a reference that resolves differently every time it
is read.

**The fix is to name the commit.** The release cut is a specific merge commit,
known at the moment the handover is written, so the handover should print its
hash rather than a moving reference - the same reasoning the skill already
applies when it forbids an angle-bracket placeholder (`PL-1DN9`). A session
that cannot yet know the hash, because the pull request has not merged, can
print the command with the hash to be substituted *and* say which merge commit
it means, which is the shape that survives being read late.

**Related.** `PL-PNW6` carries what happens next when a version number is
re-used after a withdrawn tag; this item is about the tag landing on the wrong
commit in the first place.
