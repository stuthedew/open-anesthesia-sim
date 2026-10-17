---
id: PL-8TPV
title: bin/docket arm still says to arm a pull request after the owner switches its auto-merge off to let another one merge first, so its session can re-arm it against the owner's choice
status: untriaged
feature: arm-follows-owner
touches: subprojects/docket/src/docket/arming.py
added: 2026-10-17
---

**Problem.** bin/docket arm still says to arm a pull request after the owner switches its auto-merge off to let another one merge first, so its session can re-arm it against the owner's choice

**What happened, 2026-10-17.** Between 05:53 and 06:34 UTC, auto-merge was
switched off ten times on five pull requests: #1475, #1478, #1480, #1481 and
#1483. The owner switched them off so that other pull requests would merge
first. They said so in `PL-8ZTQ`'s thread at 06:52 UTC: "I switched them off to
prioritize other PR".

A session could not tell that the owner had made those switches:

- GitHub attributes every call to the owner's account, whether the owner or a
  session made it. So the pull request's timeline shows the owner's name on
  every arm and every disarm.
- `bin/docket arm` still printed `arm` for #1478 after the second switch. It
  decides from the branch's paths and the open claims, and it does not look at
  the pull request's auto-merge setting.
- The GitHub notice that a session receives when auto-merge is switched off
  tells it to turn auto-merge back on if the pull request should still merge.

So a session that follows its rules turns auto-merge back on, or merges the
pull request itself once CI passes. That night, #1483's session recorded the
plan "auto-merge flipped off again; merge when CI passes". `PL-8ZTQ`'s thread
spent a helper agent reading other sessions' transcripts to find out who had
switched #1478 off, until the owner said.

**What a fix has to achieve.** When the owner switches auto-merge off, the
session that owns the pull request leaves it off. The session still arms a
pull request that `bin/docket arm` clears and that nobody has switched off. To
do that, a fix needs to know who last changed the setting, and GitHub does not
record that in a form a session can read. One route is for each session to
record its own arms and disarms, and to treat any other change as the owner's.
That is the case that `.claude/rules/apparatus-standard.md` calls "Nobody
records the fact". The session that builds this chooses the route.

**Related.** `PL-XTBF` has the same cause in the other direction. There,
`bin/docket arm` tells a session to switch off auto-merge that the owner
switched on after reading the pull request. Both items carry the feature
`arm-follows-owner`. Only two items share the cause, so it is not a generator.
