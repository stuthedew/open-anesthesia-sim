---
id: PL-R852
title: Replies give clock times in UTC, the zone the tools print, where the project owner reads US Central (Madison, Wisconsin), so every deadline - the compaction clock time among them - is converted by hand
priority: P2
effort: S
status: done
classes: docs
touches: .claude/rules/instruction-writing.md, docs/resident-instructions.md
added: 2026-09-27
closed: 2026-09-27
pr: 1218
payoff: every clock time a reply gives is one the project owner reads as given, the compaction deadline included, with no sum to do first
verify: grep -qF 'America/Chicago' .claude/rules/instruction-writing.md && grep -qF "rule 15's clock times" .claude/rules/instruction-writing.md
---

**Problem.** Replies give clock times in UTC, the zone the tools print, where
the project owner reads US Central (Madison, Wisconsin), so every deadline -
the compaction clock time among them - is converted by hand. `bin/docket`'s
digest prints "at 23:19 UTC", the container's `date` and GitHub's timestamps
are UTC, and a reply repeats what it read: the `/compact` deadline
`CLAUDE.md` asks a session to name reached the owner as "23:42 UTC" on
2026-09-27, which is 6:42 PM CDT. They asked for every time in Central,
"whatever Madison Wisconsin is" (project owner, 2026-09-27).

**Why it matters.** The compaction deadline is the one a reply asks the
owner to act by, and past it the summary re-reads the whole history
uncached; a deadline that has to be converted first is easy to misread by the
hour, and by two once daylight saving ends on 2026-11-01 and the offset
moves from five hours to six.

**Done when.** `.claude/rules/instruction-writing.md` gives every reply's
clock times in `America/Chicago`, labelled CDT or CST, with the command that
converts a UTC time, and `docs/resident-instructions.md` records the carrier
test and why nothing was cut.
