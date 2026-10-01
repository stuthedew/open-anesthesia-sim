---
id: PL-1XZD
title: CLAUDE.md's retirement sentence reads 'nobody acts on it' as the test for fluff, so an advisory whose decision is still taken somewhere it never reaches is retired instead of routed; name the decision and where it is taken before retiring (project owner, 2026-10-01, ratified)
priority: P2
effort: S
status: done
classes: docs
touches: CLAUDE.md, docs/resident-instructions.md, docs/WORKING_NOTES.md
added: 2026-10-01
closed: 2026-10-01
pr: 1270
payoff: an advisory whose decision is still taken somewhere is routed to that moment instead of deleted, and only fluff is retired
verify: grep -q "Nobody reading it is the symptom, not the test" CLAUDE.md
---

**Problem.** CLAUDE.md's retirement sentence reads 'nobody acts on it' as the test for fluff, so an advisory whose decision is still taken somewhere it never reaches is retired instead of routed; name the decision and where it is taken before retiring (project owner, 2026-10-01, ratified)

**Why it matters.** `CLAUDE.md` § "Prefer deterministic tooling over repeated
model work" ends its retirement bullet with "an advisory nobody acts on is a
candidate for retirement rather than promotion". Read alone, "nobody acts on
it" is the test, and it conflates two cases that want opposite fixes: no
decision exists that the signal could change, which is fluff and goes; or a
decision exists and the signal reaches nobody at the moment it is taken, which
is the routing question `CLAUDE.md` asks of every rule and never of a check.
The project practises the second reading - `PL-G6J5` retired the slow-command
advisory on a count, and `.claude/rules/expert-review.md` lists a check
retirement among the things not tightened without naming and measuring the
suppressed side - but the resident sentence does not point at it, and a
session reading the sentence alone retires on silence. The owner raised it on
2026-10-01 against a reply that had used exactly that proxy ("nothing would
read it") to decide against a record. The same two-step is alarm
rationalization's: ANSI/ISA-18.2 removes an alarm with no defined operator
response and treats one whose response is not being taken as a presentation
problem, never grounds for removal.

**Done when.** The clause reads: an advisory nobody acts on is retired only
after naming the decision it was built to change and where that decision is
taken; if that decision is still taken somewhere, route the advisory to that
moment first, and retire it only if it still changes nothing there; if no such
decision exists, it is fluff and goes; nobody reading it is the symptom, not
the test. `docs/resident-instructions.md` carries the entry naming the clause
it replaces and the character cost (project owner, 2026-10-01, ratified, over
an item of its own, which would have left the naive sentence resident until
it ranked).

**Generator check.** No fact is misread by a reader here; this corrects what a
resident rule says about retiring one. A one-off, the owner's request.
