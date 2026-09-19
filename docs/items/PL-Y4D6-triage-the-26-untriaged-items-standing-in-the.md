---
id: PL-Y4D6
title: Triage the 26 untriaged items standing in the queue on 2026-09-17
priority: P3
effort: M
status: done
classes: planning
milestone: v0.4.28
touches: docs/items
added: 2026-09-17
closed: 2026-09-17
pr: 663
not-delegable: the deliverable is a judgment per item - what each is worth, how big it is and what it belongs with - recorded in twenty-six item files; `bin/docket check` proves the answers are well-formed and can prove nothing about whether they are right
---

**Problem.** Triage the 26 untriaged items standing in the queue on 2026-09-17

**Why it matters.** Twenty-six untriaged items is a second queue behind the queue:
`bin/docket next` ranks on `priority`, so an untriaged capture is invisible to
every session that asks what to work on, however urgent it is. Four of the
twenty-six turned out to be work that had already landed on `main` or questions
already answered, so the queue was also overstating what is left.

**Done when** each of the twenty-six items standing untriaged at 2026-09-17
03:55Z carries a priority, an effort and a status, with `classes`, `touches` and `feature` filled where they apply; the
full brief where the status is past `untriaged`; a `verify:` command that has been
run and seen to fail where the status is `ready`, or a `not-delegable:` reason
where no command can prove it; and `bin/docket check` reports 0 errors.

**Three captures that arrived while the pass ran are deliberately not in it.**
`PL-7TYC` and `PL-TKFD` were filed by `#655` and `PL-XZD0` by `#657`, all after
this pass read the store. `PL-7TYC` is being worked by another session right now
(`session_01KstW6HaDazX1VTrM1Uizj2`, titled for it), so triaging it here would be
a second resolution of a file somebody holds. They are the next pass's, and the
store reports them.
