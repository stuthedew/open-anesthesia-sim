---
id: PL-1YT5
title: CLAUDE.md's auto-pull-request clause is recorded as specified when it was ratified, so it reads as a rule the owner authored and a later session would hold it to the compelling-argument bar instead of ordinary evidence
priority: P3
effort: S
status: done
classes: docs
milestone: v0.4.29
touches: CLAUDE.md
added: 2026-09-19
closed: 2026-09-19
pr: 702
verify: grep -q 'project owner, 2026-09-19, ratified, over treating the switch' CLAUDE.md
---

**Problem.** CLAUDE.md's auto-pull-request clause is recorded as specified when it was ratified, so it reads as a rule the owner authored and a later session would hold it to the compelling-argument bar instead of ordinary evidence

**Where.** `CLAUDE.md` § "Commit and push as you go; the pull request arrives
with the work", the clause added in `#700` reading *"A session-level
auto-pull-request switch set off is that same case and not a third ... (project
owner, 2026-09-19)"*.

**Why it matters.** The plain form means the project owner stated the rule in
their own words. They did not: the session inferred it from a one-word answer
covering two questions, put the case, and the owner confirmed it on a read -
which is `CLAUDE.md`'s definition of *ratified*. The two forms are not
cosmetic. A ratified decision reopens on ordinary evidence, a specified one
only on a compelling argument, so the wrong word here raises the bar against
a rule nobody authored. `CLAUDE.md` states the hazard exactly: *"the reply that
put the case is gone and the record is the only carrier - and without it a
later session cannot tell a design they authored from one they nodded at."*

**Not a defect in the two neighbouring records**, which were checked in the
same pass and are right as they stand. The generator-machinery rank was asked
for in the owner's own words; the two-endings extension was decided *against*
the session's recommendation, which is specifying rather than ratifying. Only
this clause came from the session's own proposal.

**Done when.** The clause carries `(project owner, 2026-09-19, ratified)` and
names in one clause what it was chosen over, per `CLAUDE.md`'s own rule for
the form.
