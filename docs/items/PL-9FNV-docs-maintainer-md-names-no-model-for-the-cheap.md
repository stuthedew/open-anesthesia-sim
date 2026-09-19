---
id: PL-9FNV
title: docs/maintainer.md names no model for the cheap end of the split either, so a session reading 'delegable' has nothing to resolve it against and the safe default is to keep running the strongest model
priority: P2
effort: S
status: done
classes: docs, defect
feature: model-capability-routing
milestone: v0.4.31
touches: docs/maintainer.md
added: 2026-09-19
closed: 2026-09-19
pr: 733
verify: grep -q 'means Claude Sonnet 5' docs/maintainer.md
---

**Problem.** docs/maintainer.md names no model for the cheap end of the split either, so a session reading 'delegable' has nothing to resolve it against and the safe default is to keep running the strongest model

**Why it matters.** `PL-13PB` is the same defect at the strong end, and the
two are one paragraph: § "Match model capability to the work" is where
`CLAUDE.md` routes the whole model question, and it named no model at either
end. An unresolvable flag has one default behaviour — assume whatever the
session is already running satisfies it — and at the cheap end that default
costs the saving the flag exists to offer, every session, silently.

Raised by the project owner on 2026-09-19, who asked for a cheaper-model
recommendation on clear-cut items and specified the asymmetry it must have:
*"I'd rather err on the side of default opus if any question and miss items
that could have been safe with a lower model than try to catch every lower
model opportunity and find out later I should have actually used opus."*

**One named tier, not a choice between two.** The request named Sonnet *or*
Haiku. Naming both would put the per-item judgment back at the moment of
reading, which is what the asymmetry above exists to remove, so the section
names one. That substitution is this session's reading of their stated
preference rather than their own words, and is recorded as such — it is the
line to correct first if the reading is wrong.

**Three facts decide Sonnet over Haiku**, all of them checkable rather than
preferences: Haiku 4.5 is a generation behind the Claude 5 family; its context
window is 200K against 1M, leaving roughly 50K of headroom against
`CLAUDE.md`'s 150,000-token handoff budget; and it does not take the effort
parameter, so this file's own instruction to open apparatus sessions at `high`
cannot be honoured on it. Sonnet 5 also already captures 75% of the largest
saving available at first-party rates ($2/$10 per 1M against Opus 5's $5/$25
and Haiku 4.5's $1/$5).

**A dated instance, not a rule.** Per `.claude/rules/expert-review.md`,
whichever model is named will stop being the right one, so the section states
the date and names what falsifies it — a new model release.

**Done when.** § "Match model capability to the work" resolves both flags
`bin/docket next` prints, with dates, and says plainly that `delegable` is an
offer a reader may always decline.
