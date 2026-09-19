---
id: PL-CM40
title: No single command prints the refreshed picture a closing block needs - main's tip, whether this branch is contained in it, flight and stranded - so the rule has to name three
priority: P3
effort: S
status: needs-decision
classes: infra
touches: subprojects/docket/src/docket/cli.py, .claude/rules/instruction-writing.md
feature: refresh-before-reporting
added: 2026-09-19
---

**Problem.** No single command prints the refreshed picture a closing block needs - main's tip, whether this branch is contained in it, flight and stranded - so the rule has to name three

**Why it matters.** `.claude/rules/instruction-writing.md` rule 14 now names
three commands because no one command answers the question. Every resident
word is paid in every request of every session, so a rule that exists only to
sequence commands is a candidate for the disposition `CLAUDE.md` ranks first -
put the decidable part in code and delete the prose.

**Decision needed.** Whether this is one new command or a flag on an existing
one, and what it prints. The four facts a closing block actually needs are:
the default branch's tip after a fetch, whether this branch is contained in it
(so a merged-and-squashed branch is named as such rather than looking ahead),
`flight`, and `stranded`. `bin/docket branch` already fetches and already
reasons about the branch's relation to the base, so it may be the right home
rather than a fifth command.

**Blocked on `PL-QSGX` in practice**, since a combined command that calls a
non-fetching `flight` inherits the same staleness.

**Done when.** One command answers it, rule 14 names that command instead of
three, and the resident character total goes down rather than up.
