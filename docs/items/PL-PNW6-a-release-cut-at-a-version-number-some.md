---
id: PL-PNW6
title: A release cut at a version number some withdrawn tag once named leaves every warm checkout pointing v<version> at the old commit, and the handover's own 'git fetch origin main' is the command that leaves it stale silently
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: release-process
touches: .claude/skills/docket/SKILL.md, subprojects/docket/src/docket/release.py
added: 2026-09-07
---

**Problem.** A release cut at a version number some withdrawn tag once named leaves every warm checkout pointing v<version> at the old commit, and the handover's own 'git fetch origin main' is the command that leaves it stale silently

**Measured 2026-09-07**, in a scratch pair of repositories, tagging `v0.4.8` at
commit A, cloning, then deleting that tag on the origin and re-tagging at
commit B:

| In the warm clone | Exit | Result |
| --- | --- | --- |
| `git fetch origin main` | 0 | tag never attempted; still at A, nothing printed |
| `git fetch --tags origin` | 1 | `! [rejected] v0.4.8 -> v0.4.8 (would clobber existing tag)`; still at A |
| `git fetch --tags --force origin` | 0 | `t [tag update]`; now at B, `refs/remotes/*` untouched |

The first row is the problem, and it is the row that matters because it is the
command the skill's own release handover tells the owner to run. It exits zero
and says nothing, so a warm checkout keeps `v0.4.8` on a commit that carried no
release, indefinitely, with nothing indicating it.

**This is not the same condition as `PL-LT77`.** That one is a tag deleted on
origin and never replaced, where the local copy is the only one and `doc_check`
reports it in wording that reads as a claim about the repository. This is a tag
deleted and then *re-created at a different commit*, where origin and the warm
checkout both hold `v0.4.8` and disagree about what it means. `doc_check` is
silent here - the ROADMAP row exists and the version matches - so nothing
reports it at all, which makes it the quieter of the two.

**Blast radius is small and pointed at the one reader who cannot escalate.** A
container that clones fresh is correct by construction, so remote sessions
self-heal; what persists is the project owner's own machine, and `git describe`,
`git log v0.4.8..`, and any release-span question asked there answer from the
wrong commit.

**Why it matters.** The failure is silent in the one direction that matters.
The fetch the handover itself prescribes exits zero and prints nothing, so
nothing distinguishes a checkout holding the right tag from one holding the
withdrawn one, and there is no moment at which the reader is told to look.
Every release-span question then answers from the wrong commit while reporting
no fault - `git describe --contains`, `git log v<version>..`, and
`bin/docket release`'s own refusal to cut while the previous release is
untagged, which reads a tag it believes it can trust. `doc_check` is silent
here by construction, because the ROADMAP row exists and the version matches,
so unlike `PL-LT77` there is no red check to prompt a diagnosis at all.

**Shape of a fix, not yet chosen.** Either the release handover carries
`git fetch --tags --force origin` whenever the number being cut is one a tag
has previously named - which the cutting session can decide, since it is the
one that knows the number was re-used - or `bin/docket release` records that a
number was re-used so the handover is generated rather than remembered. Note
that `--prune-tags` is not available here: `.claude/hooks/no-prune-guard.sh`
refuses it, correctly, because a stale `origin/<branch>` ref can be the only
surviving copy of a stranded item (`PL-HKF4`).

**Concrete instance.** v0.4.8, cut 2026-09-07 under `PL-BKDP`, is exactly this
case: the number was previously tagged on `b03a7d03` and withdrawn.

**The sharper failure, measured 2026-09-07 after the above.** A warm checkout
does not merely read the old commit - it cannot make the new tag at all. While
the number is withdrawn on origin, no fetch of any kind clears the local copy:
`--tags --force` has nothing to overwrite it with, because origin holds no
`v0.4.8` to force. So the stale tag survives every safe fetch, and the tag
command the release handover prints then fails outright:

```
$ git tag -a v0.4.8 "$COMMIT" -m "v0.4.8"
fatal: tag 'v0.4.8' already exists
```

That is the good case, in the sense that it is loud and stops. The bad case is
the reader who reaches for `-f` to get past it, because `git tag -f -a` will
happily re-point the local tag and the subsequent `git push origin v0.4.8`
succeeds - leaving the release correctly tagged on origin and the *reason* it
failed unexamined, which is the same warm checkout that will misreport
`git describe` for every earlier tag it also holds stale.

**So the handover for a re-used number owes an explicit local delete**, before
the tag and after the fetch:

```bash
git tag -d v0.4.8          # clears the withdrawn tag if this checkout holds it
```

Verified as a whole sequence: delete, resolve the commit by its subject, confirm,
tag, push - which put the tag on the intended commit from a checkout that had
been holding the withdrawn one.

**Done when.** Cutting a release at a version number some tag has previously
named produces a handover that clears the withdrawn tag locally before it
tags - so the owner never meets `fatal: tag 'v0.4.8' already exists`, and never
reaches for `-f` to get past it - and a warm checkout that follows the handover
ends with `v<version>` on the commit the release was actually cut at. Which of
the two shapes above delivers that is the decision this item is waiting on:
put the extra commands in the handover the cutting session writes, since that
session is the one that knows the number was re-used, or have
`bin/docket release` record the re-use so the handover is generated rather
than remembered.

**Decision needed.** Where the extra tag commands come from when a version
number is re-used: (1) the cutting session writes them into the handover it
already produces, since it is the session that knows the number was previously
tagged - no new mechanism, but it depends on a session noticing; or (2)
`bin/docket release` records the re-use and generates the handover, which makes
it deterministic at the cost of teaching the release tool about tag history it
does not read today. Answer this and the item is `ready`; a `verify:` command
cannot be written before it, because the two shapes put the change in different
files.
