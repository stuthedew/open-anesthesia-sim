---
id: PL-6MW8
title: PL-Z0SM's trigger fired on 2026-09-23 (third merge-skew instance within 30 days, #967 then #970): adopt strict up-to-date status checks on main and revise CLAUDE.md's rule against merging origin/main into an open pull request out of habit
priority: P2
effort: S
status: ready
classes: infra
feature: merge-skew
touches: CLAUDE.md
added: 2026-09-23
payoff: a pull request green on a stale base can no longer merge into a red main
not-delegable: the setting is the project owner's, in main's branch protection, which no session can change
---

**Problem.** PL-Z0SM's trigger fired on 2026-09-23 (third merge-skew instance within 30 days, #967 then #970): adopt strict up-to-date status checks on main and revise CLAUDE.md's rule against merging origin/main into an open pull request out of habit

**The trigger.** `PL-Z0SM` (merge skew) was answered "hold" on 2026-09-23
(project owner, ratified), and the answer named what would change it: "Strict
up-to-date checks are adopted at a third instance within 30 days of the last."
`PL-70VB` is that third instance. #967 and #970 each passed CI on their own
base, and the two together turned `main` red at 17:18 the same day.

**Why it matters.** Each instance fails every open pull request at once. With
several sessions merging within the hour, that now happens more often than a
full `quality.yml` run per open pull request per merge would cost, which is the
break-even `PL-Z0SM` named.

**Done when.** `main`'s protection requires branches to be up to date before
merging, and the `CLAUDE.md` bullet "Do not merge `origin/main` into an open
pull request out of habit" says that a stale base is now refused at merge. It
must no longer argue that bringing the base in wastes a green run. The setting
is the project owner's to change. The `CLAUDE.md` edit follows it in the same
session that confirms the setting is on.

