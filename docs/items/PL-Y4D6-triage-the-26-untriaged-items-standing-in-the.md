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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it.

> **Ten from the 2026-09-17 triage of the twenty-six untriaged captures** (`PL-Y4D6`). They are disposed of on two different grounds.

> Two findings against items 24 and 28 arrived with it, and they are **not** here. They are `PL-H4N8` (cost is the delivered amount, not the exhausted one) and `PL-QBX0` (item 24's gate misses the ISO 5360 colours and the contrast-checked palette). Their hazards are anticipated in the same way. But the fix for each is a sentence in the planned-milestone entry itself. So neither is blocked on anything, and neither takes the carve-out. They are on the frozen list above, added under the unconditional exception. `tools/doc_check.py` requires that, and it says so explicitly: deferring is not a third option for these two classes.

> *Nine on this subsection's own refilling-queue ground.* All nine were captured on 2026-09-16 or 2026-09-17. All are apparatus or documentation findings, and none completes an entry already on the frozen list. They are `PL-4RHP` (this subsection's own entry count is outside `check_gate_counts`' reach), `PL-B396` (whether item 28 is scoped at all, which is a milestone decision rather than gate work), `PL-KF0T` and `PL-YD6X` (planned-milestone items 33 and 24 describe closed work as open), `PL-KSCW` (`stranded` sees a missing item file and not a missing *section* of one), `PL-LBW5` (a `verify:` command naming a path its own `touches` omits), `PL-M21Q` (a `needs-decision` item carries the question and not the recommendation), `PL-SY1J` (`bin/docket show` named the later of two branches carrying one item) and `PL-XD3C` (`digest`'s cost grows with the item edits that unmerged refs carry, and nothing prunes them).

> **The compounding-friction test was applied to two of the nine, and neither passes it.** `PL-SY1J` comes closest: it hands a session a confident verdict that names the wrong carrier. `PL-XD3C` is the one whose cost grows. The test is arithmetic. Name what each remaining entry pays, and multiply. Neither cost is paid per remaining entry. What remains of this gate is the milestone's own work. An in-flight verdict that names one carrier costs the sessions that collide. `digest`'s growth costs every session equally, whether this gate is open or shut. No saving per entry can be named, so both wait. That is what "work that is merely valuable makes no remaining entry cheaper" says to do.
