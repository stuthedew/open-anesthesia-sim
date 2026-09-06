---
id: PL-Y1LD
title: docket concurrent orders a batch by file, but the lane mechanism separates only two sessions, so the third and fourth simultaneous session have no command that picks for them
priority: P3
effort: M
status: needs-decision
classes: session-cost, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-06
---

**Problem.** docket concurrent orders a batch by file, but the lane mechanism separates only two sessions, so the third and fourth simultaneous session have no command that picks for them

**Observed 2026-09-06**, handing out four gate items to four simultaneous
sessions. `docket.toml`'s own comment says "Two lanes and no more, because two
sessions can hold a repository between them and four cannot", and that is
right about lanes - but the project owner ran four anyway, and the apparatus
had no answer for sessions three and four.

What exists: `bin/docket next <lane>` picks for two sessions, and `bin/docket
concurrent` prints a file-disjoint batch. What is missing is the join between
them. `concurrent` returned a 29-item batch, but choosing four from it that
were each startable, on the gate, worth doing, and pairwise disjoint was done
by hand - reading `touches` for ten candidates and cross-checking them in a
scratch script. That is the work `next` does for one session and no command
does for four.

**The shape a fix probably takes**, though this is a design round rather than
a decided approach: `bin/docket concurrent --pick <n>` returning the best `n`
mutually disjoint startable items in rank order, which is `next`'s ranking
applied to `concurrent`'s graph. That is one command, reuses both halves, and
is the deterministic-tooling answer to a judgment a session currently re-makes
at full context every time.

**Where.** `subprojects/docket/src/docket/cli.py` - `cmd_concurrent` and the
ranking `cmd_next` applies, which are the two halves that would be joined.

**Done when.** Either one command returns the best `n` mutually disjoint
startable items in rank order, so a session handing out work to three or four
sessions runs a command rather than a scratch script, or the project records
that four-way work is rare enough to keep doing by hand and why.

**Why it matters, and why it is not urgent: it does not meet the
compounding-friction bar.** Nothing
gives a wrong answer silently, nothing is being routed around, and the manual
pass took one session a few minutes. It is worth doing when four-way work
becomes routine rather than a one-off.

**Decision needed.** Is the join between `next`'s ranking and `concurrent`'s
graph worth building - `bin/docket concurrent --pick <n>`, returning the best
`n` mutually disjoint startable items in rank order - or is four-way work rare
enough to keep doing by hand? Nothing gives a wrong answer today and the manual
pass took one session a few minutes, so this is a question about how routine
three- and four-way sessions become.
