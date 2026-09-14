---
id: PL-YNYK
title: PL-6194's no-check decision rested on the prediction that a redundant-parenthesis check would fire once and never again, and the count falsifies it: the population in tests/ regenerated from 6 to 15 over the 11 days the item sat open, while src/ fell 40 to 35
priority: P3
effort: S
status: needs-decision
classes: defect
feature: dev-tooling
touches: tools, .github, tests/unit
added: 2026-09-14
---


**Problem.** PL-6194's no-check decision rested on the prediction that a redundant-parenthesis check would fire once and never again, and the count falsifies it: the population in tests/ regenerated from 6 to 15 over the 11 days the item sat open, while src/ fell 40 to 35

**The count does not reproduce today, and that is the first thing to settle.**
Measured 2026-09-14 on `main` using `PL-6194`'s own pattern - the one its
`verify:` field greps with, `^ +[a-z_]+=[(][a-zA-Z_][a-zA-Z0-9_.]*[)],?$` - the
population is **0 in `src/`, 0 in `tests/`, and 0 across `tools/` and
`subprojects/`**. `PL-6194` closed the same day this item was filed, so the
zero is the state immediately after its sweep rather than evidence against the
item: what this item asserts is a *regrowth rate*, and a reading taken the day
of the sweep cannot measure one.

**Why it matters.** `PL-6194` declined to add a check on a prediction - that a
redundant-parenthesis check would fire once and never again - and a standing
decision resting on a prediction is worth re-taking when the prediction can be
tested. `CLAUDE.md` makes the same point from the other end: a check that fires
every run without changing a decision is a defect in the check, so the cost of
being wrong runs in both directions and only a count settles it. Note also that
`ruff` selects no rule for this shape - `PL-6194` recorded that
`ruff check --isolated --select ALL --preview` does not flag a keyword
argument's parenthesised value - so there is no free option here.

**Decision needed.** Whether `PL-6194`'s no-check decision stands, given that
its prediction is now testable and the population is currently zero.

The number that decides it is the regrowth rate, which nobody has: re-run the
pattern above on a date far enough past `PL-6194`'s sweep for new code to have
landed, and count what has reappeared. The three answers:

- **Stands.** The population stays at or near zero - the prediction held, and
  this item closes `dropped` with the count.
- **Add the check.** The population regrows at a rate that makes a hand sweep
  recurrent work, which is `CLAUDE.md`'s own test for moving work out of the
  model and into a script.
- **Re-measure later.** Too soon to tell, which is where the project is today.

Do not answer this from the figures in the title. They were taken with a pattern
this item does not state, and they do not reproduce under the one `PL-6194` used.
