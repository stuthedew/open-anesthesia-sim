---
id: PL-PNW6
title: A release cut at a version number some withdrawn tag once named leaves every warm checkout pointing v<version> at the old commit, and the handover's own 'git fetch origin main' is the command that leaves it stale silently
status: untriaged
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
