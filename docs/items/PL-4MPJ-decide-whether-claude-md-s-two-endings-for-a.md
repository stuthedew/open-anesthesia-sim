---
id: PL-4MPJ
title: Decide whether CLAUDE.md's two endings for a generator - fix it now, or end the reply with a prompt that starts a fresh session on it - extend to a defect in the generator machinery, which now shares the generator's rank but not that obligation
priority: P3
effort: S
status: done
classes: planning
feature: generator-machinery-rank
milestone: v0.4.28
touches: CLAUDE.md
added: 2026-09-19
closed: 2026-09-19
pr: 700
not-delegable: the whole item is a decision only the project owner can take; no command can prove it, and the edit it authorizes is one clause
---

**Problem.** Decide whether CLAUDE.md's two endings for a generator - fix it now, or end the reply with a prompt that starts a fresh session on it - extend to a defect in the generator machinery, which now shares the generator's rank but not that obligation

**Decision needed.** Do `CLAUDE.md`'s two endings for a generator - fix it in
this session, or end the reply with a ready-to-paste prompt that starts a fresh
one - also bind a session that finds a defect in the generator machinery? It
now shares the generator's rank and not that obligation. Recommended answer
below: no.

**Where.** `CLAUDE.md` § "A root cause of more than two items is pulled, not
queued", whose closing clause currently reads *"The two endings above are the
generator's own; only the ranking is inherited."* That sentence is a session's
holding pattern, not a decision.

**Why it matters.** The two endings are the strongest obligation in that
section - a session that finds a generator may not file it and carry on. The
machinery rule (`PL-G5ZH`) gave a machinery defect the generator's *rank*
because the project owner asked for that in those words; it did not give it the
generator's obligation, because they did not ask for that and it changes what
every session must do on a finding. Left unanswered, the asymmetry is a rule
nobody decided.

**Decided: extend them (project owner, 2026-09-19).** Against the
recommendation below, which is kept in full because the bar to reopen a
*specified* decision is a compelling argument rather than ordinary evidence -
so a later session needs to know what was already weighed and rejected.
`CLAUDE.md`'s clause now reads that the two endings bind a machinery defect
too, and the `docket` skill says the same at the point a triage pass would
otherwise band one and move on.

**Recommendation, refused: do not extend them.** Two reasons, and both are about the
evidence rather than the importance. A generator's warrant is a *measured*
cluster - three or more items, named, resolvable, checked - and the obligation
to stop the session is proportionate to that. An `impairs-generators:` claim
has no such count; its evidence is one session's prose. Making a prose claim
able to compel an interruption in every later session is a larger grant than
the rank itself. Second, a machinery defect is usually found *by a session
already inside the machinery*, where `CLAUDE.md`'s fix-now door is open
anyway - so the obligation would mostly fire where it is redundant.

**Against the recommendation**, and recorded so the case is not re-derived: the
suppression argument is genuinely unbounded. A generator is paid again by every
session it stands through; a broken identification path means no generator is
recorded at all, and nothing in the store would say one went unfound. If that
reading wins, the two endings should extend.

**Done when.** The clause in `CLAUDE.md` states a decision rather than a
holding pattern, marked `(project owner, DATE)` if specified or
`(project owner, DATE, ratified)` if taken on this recommendation, naming what
it was chosen over.

**Worked.** The clause carries the plain `(project owner, 2026-09-19)` form,
since the answer was the opposite of the recommendation and so was specified
rather than ratified. Three files say it: `CLAUDE.md` where a session meets it
before looking anything up, `.claude/skills/docket/SKILL.md` where a triage
pass would otherwise file one and carry on, and `docs/WORKING_NOTES.md` where
the thread closes.
