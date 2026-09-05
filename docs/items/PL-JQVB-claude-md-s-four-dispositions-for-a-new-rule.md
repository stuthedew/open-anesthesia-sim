---
id: PL-JQVB
title: CLAUDE.md's four dispositions for a new rule list no carrier for a paste-able brief or an agent definition, and a skill's resident cost is invisible to measure_resident
priority: P3
effort: S
status: needs-decision
classes: session-cost, docs
touches: CLAUDE.md, tools/doc_check.py
added: 2026-09-05
---
**Problem.** `CLAUDE.md`'s four dispositions for a new rule — a check, a
skill, a path-scoped rule, or resident — name no carrier for two things this
repository already uses: a paste-able brief handed to a fresh session, and an
agent definition. Separately, `check_resident_instructions` measures `CLAUDE.md`
and `.claude/rules/`, so a rule moved into a skill leaves the measured set
entirely and reads as a pure reduction when it is a relocation.

**Why it matters.** The dispositions are the routing rule every behaviour
change passes through, and `CLAUDE.md` says a rule landing in none of the four
"has been lost". A carrier in live use that the list does not name forces a
session either to file the rule under a disposition that does not fit or to
leave it resident by default — and resident-by-default is the outcome the list
exists to prevent. The measurement gap compounds it: the cheapest way to make
the growth advisory go quiet is the one move it cannot see.

**Where.** `CLAUDE.md`, the four dispositions under the behaviour-change rule;
`tools/doc_check.py`, `check_resident_instructions` and what it reads.

**Decision needed.** Two questions, separable. Whether the disposition list gains
entries for a brief and an agent definition, or whether those are deliberately
not carriers for a *rule* and the list is right as it stands. And whether
skills enter the measured set — which changes what the number means, from "text
every session loads" to "text a session may be made to load", rather than
merely widening its scope.

**Done when.** Both questions have a recorded answer, and either `CLAUDE.md`
and the measurement reflect it or `docs/resident-instructions.md` records why
they do not.
