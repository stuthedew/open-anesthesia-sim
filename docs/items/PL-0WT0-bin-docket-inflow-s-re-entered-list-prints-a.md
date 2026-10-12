---
id: PL-0WT0
title: bin/docket inflow's re-entered list prints a head its successor already answers exactly as it prints one nobody has: on 2026-10-12 eight of its ten lines named a successor head among their re-entries, visible only to a reader who knows which filings carry root-cause-of, so each run re-asks settled questions; name the successor where a re-entering filing is a head
priority: P2
effort: S
status: done
classes: defect
feature: generator-heads
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-12
closed: 2026-10-12
pr: 1459
payoff: bin/docket inflow lists apart the closed heads a successor head already answers, naming it, so a session reading the list asks only the questions still open
verify: grep -q 'def test_a_line_a_successor_head_answers_names_it' subprojects/docket/tests/test_inflow.py
---

**Problem.** bin/docket inflow's re-entered list prints a head its successor already answers exactly as it prints one nobody has: on 2026-10-12 eight of its ten lines named a successor head among their re-entries, visible only to a reader who knows which filings carry root-cause-of, so each run re-asks settled questions; name the successor where a re-entering filing is a head

**Reproduced 2026-10-12 at 19:20 UTC.** Over `bin/docket inflow`'s ten lines,
`model.is_generator` holds for one filing among the re-entries of eight:
`PL-4Q9B` (`PL-MT3R`), `PL-9HD1` (`PL-HXJY`), `PL-GHHW` (`PL-927J`),
`PL-J6HP` and `PL-WD5Z` (both `PL-8QMD`), `PL-KGYT` (`PL-5DZ8`), `PL-TZ7T`
(`PL-0HLS`) and `PL-WFFX` (`PL-979D`). The other two, `PL-0HPV` and
`PL-61FT`, have none. All ten print under one heading, "a generator whose fix
did not hold".

**Why it matters.** The list is where `CLAUDE.md` § "What this project is"
expects a generator still producing to be found, and `PL-4097` settled that a
successor head is recorded by its own `reenters:` naming the head whose fix did
not hold. The list reads that record to count the line and then drops the half
that answers it, so the heading is false for eight of ten lines and every run
puts eight settled questions beside the two open ones. A reader either re-derives
which filings are heads, or skims the list and misses the two that need an
answer.

**Done when.** A line whose closed item is named in the `reenters:` of an item
`model.is_generator` accepts prints that head as its successor, with its status,
under a heading of its own; the heading "a generator whose fix did not hold"
carries only the lines with no successor; and the README's account of the list
says so.

**Generator check.** One-off. The fact misread is which later head succeeds a
closed one; `PL-4097` misread it too (its own generator check says so), and no
head's `misread:` states it, but two items are below the three a generator
needs. The list was built by `PL-WXKD` reading `reenters:` as a count, and the
successor shape it now has to read was settled the day this was filed.
