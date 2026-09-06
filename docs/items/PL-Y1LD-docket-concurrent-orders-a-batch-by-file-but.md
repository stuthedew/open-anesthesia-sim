---
id: PL-Y1LD
title: docket concurrent orders a batch by file, but the lane mechanism separates only two sessions, so the third and fourth simultaneous session have no command that picks for them
status: untriaged
added: 2026-09-06
---

**Problem.** docket concurrent orders a batch by file, but the lane mechanism separates only two sessions, so the third and fourth simultaneous session have no command that picks for them

**Why it matters.**

**Where.**

**Done when.**

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

**Not urgent, and it does not meet the compounding-friction bar.** Nothing
gives a wrong answer silently, nothing is being routed around, and the manual
pass took one session a few minutes. It is worth doing when four-way work
becomes routine rather than a one-off.
