---
id: PL-B73C
title: Decide whether docket flight and the digest should name unlanded refs carrying no item id at all
status: untriaged
added: 2026-09-04
---

**Problem.** `branches_in_flight` walks every unlanded ref, looks for an id in
the branch name and at the front of each commit subject, and silently drops the
ref when it finds neither. `FlightReport` has `branches` and `unreadable`; there
is no third field for *read successfully, and attributable to nothing*. So the
report is complete about what it could read and silent about work it read
perfectly well and could not name — which is the literal reading of `PL-CP74`'s
title, and the half that item deliberately did not build.

**Why it matters.** `PL-CP74` closed the writing side: `tools/branch_id_check.py`
refuses a branch of one's own that carries no id, and `CLAUDE.md` plus the
`docket` skill say to file housekeeping before doing it. Both act on the session
creating the branch. Neither helps a session looking at a branch somebody else
left, which is what `flight` is for.

**Why it was declined rather than built.** The digest is resent on every turn of
every session, and `CLAUDE.md`'s own test is that a check firing every run
without changing a decision is a defect in the check. Today the repository has
exactly one such ref — `origin/Review_articles`, `PL-JX2T` — and naming it would
put a line nobody acts on into every session for as long as the branch exists.
That is the advisory-nobody-reads failure arriving by construction rather than by
drift.

So the design question is not whether the information exists but what suppresses
it: age, like the abandoned-branch qualifier `flight` already carries; a
push-date floor; naming it in `flight` (asked deliberately) but never in the
digest (resent unasked); or an allow-list of refs a person has already decided
about, which is `PL-JX2T`'s output. The last is the most promising and the most
machinery.

**Where.** `subprojects/docket/src/docket/vcs.py` (`FlightReport`,
`branches_in_flight`), and whatever renders `flight` and `digest`.

**Done when.** Either the report names unattributed unlanded refs with a
suppression rule that keeps the digest quiet in the steady state, or this item
records the decision not to and why, so it is not rediscovered.
