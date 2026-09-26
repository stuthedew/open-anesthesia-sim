---
id: PL-CM40
title: No single command prints the refreshed picture a closing block needs - main's tip, whether this branch is contained in it, flight and stranded - so the rule has to name three
priority: P3
effort: S
status: needs-decision
classes: infra
feature: refresh-before-reporting
touches: subprojects/docket/src/docket/cli.py, .claude/rules/instruction-writing.md
deferred-from: v0.6.0 - filed 2026-09-19 as blocked and never on the frozen list; a closing-block convenience, not safety or science, and its decision opened only when PL-QSGX closed on 2026-09-26
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

[superseded 2026-09-26] **Blocked on `PL-QSGX`, and the decision waits rather than only the build**
(declared 2026-09-20 by `PL-LDHD`; `PL-QSGX` closed with `PL-XBV4` on 2026-09-26, so the target has stopped moving and the decision below is open: every read command now fetches once and prints which moment its refs are from, which is one of the four facts this command was to gather). A combined command that calls a
non-fetching `flight` inherits the same staleness, so the obvious reading is
that only the implementation waits. It is the `Decision needed.` above that
waits: whether this is a new command or a flag on `bin/docket branch`, and
what it prints, turns on how much the combined command has left to do - and
`PL-QSGX` landing removes one of the four facts from its job. Deciding first
would be deciding against a moving target, which is why this is `blocked`
rather than `needs-decision`.

**Done when.** One command answers it, rule 14 names that command instead of
three, and the resident character total goes down rather than up.
