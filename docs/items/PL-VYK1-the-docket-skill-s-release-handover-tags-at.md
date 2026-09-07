---
id: PL-VYK1
title: The docket skill's release handover tags at origin/main rather than at the cut's own merge commit, so a re-run of the three commands tags whatever merged next
priority: P2
effort: S
status: ready
classes: defect, docs
feature: release-process
touches: .claude/skills/docket/SKILL.md
added: 2026-09-07
verify: python3 tools/doc_check.py check && grep -q 'git tag -a' .claude/skills/docket/SKILL.md && ! grep -q 'git tag -a v0.3.0 origin/main' .claude/skills/docket/SKILL.md
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

**Why it matters.** A release tag is the one artifact nothing downstream
contradicts. `make check` reads no tags, `bin/docket release` inspects only
whether the *previous* version is tagged, and `PL-6YYR` records that a tag
naming a version no release cut is currently detected by nothing at all. So a
handover that permits the wrong commit produces a wrong answer no check will
ever return, and `git describe --contains` then places commits inside a release
whose notes describe none of them - an answer that is wrong rather than absent,
and effectively permanent once the history moves on.

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

**Done when.** The release mode's tag block names the cut's own merge commit
rather than `origin/main`, so the three commands tag the same commit whenever
they are run rather than whatever merged most recently. Where the session
writing the handover cannot yet know the hash, because the pull request has not
merged, the block says which merge commit is meant beside the placeholder it
prints, so a reader coming to it late can still resolve it correctly.
