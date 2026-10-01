---
id: PL-HC8P
title: Name the three inference shapes in .claude/rules/apparatus-standard.md so a session adding a reader of a fact to the apparatus asks whether the project already records it before writing one more reader (project owner, 2026-10-01)
priority: P2
effort: S
status: done
classes: docs
touches: .claude/rules/apparatus-standard.md
added: 2026-10-01
closed: 2026-10-01
pr: 1270
payoff: a session writing apparatus code meets the three inference shapes and the record-or-read test before it adds the next reader, instead of triage finding the item it caused
verify: grep -q "## Read the fact from its record" .claude/rules/apparatus-standard.md
---

**Problem.** Name the three inference shapes in .claude/rules/apparatus-standard.md so a session adding a reader of a fact to the apparatus asks whether the project already records it before writing one more reader (project owner, 2026-10-01)

**Why it matters.** The project's own map of the workflow lane found one
mechanism under 47% of it on 2026-09-12 - the apparatus infers a fact it could
have recorded (`PL-6ZQY`) - and `docs/WORKING_NOTES.md` § "All six of
PL-6ZQY's clusters now have a head" split it on 2026-09-19 into two shapes
wanting opposite fixes: *infers a fact nobody recorded* (write the record) and
*re-derives a fact already recorded* (read the existing record). `CLAUDE.md`
§ "Prefer deterministic tooling" holds the third, a hard check scripting the
judgment half (`PL-GPJ7`). Triage asks the question of every workflow capture
after the fact (`misread:`, `bin/docket generators --misread`), and the
generator register names each head by the fact its readers misread. No rule
asks it at the moment a session is about to write a new reader of a fact into
the apparatus, which is the moment the next member is created. On 2026-10-01
the project owner, reading an outside analysis of the generator fixes that
reached the same theme, asked that it be treated as a known failure mode and
avoided going forward. A survey the same day found 20 sites still inferring
(11 of shape A, 6 of B, 3 of C), 9 already named by open items, 4 deliberate
and documented in `subprojects/docket/README.md`, and 7 unfiled, now
`feature: recorded-not-inferred`.

**Done when.** `.claude/rules/apparatus-standard.md` carries a section naming
the three shapes, the test that separates the first two (does a document or
module already state the fact with a grammar?), and the fix each wants, so it
loads with any apparatus file opened. The section is path-scoped, not
resident, so `CLAUDE.md`'s "names what it replaces" rule for the resident set
does not apply; nothing was cut, and the section says why it is not a check:
whether a reader infers or reads a record is judgment, which `CLAUDE.md`
refuses to script.

**Generator check.** The fact misread is not one fact but the class of them;
this item adds no reader and records no fact, so it is not an instance of any
head. It is the write-time half of the question `triage.md` asks at capture
time, filed as the owner's request rather than as a defect.
