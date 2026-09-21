---
id: PL-XF5V
title: No command reports how much of a generator's cluster is still open: all 12 recorded heads are closed while 60 distinct members are not, and answering 'are the generators dealt with' took a script over the whole store
priority: P2
effort: M
status: done
classes: feature, infra
feature: convergence-visibility
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_cli.py
added: 2026-09-20
closed: 2026-09-21
pr: 829
payoff: 'are the generators dealt with' is answered by a command reporting each cluster's drain, instead of a script written over the whole store
verify: grep -q 'def test_a_generator_head_reports_how_much_of_its_cluster_is_open' subprojects/docket/tests/test_cli.py
---

**Problem.** No command reports how much of a generator's cluster is still open: all 12 recorded heads are closed while 60 distinct members are not, and answering 'are the generators dealt with' took a script over the whole store

**Measured 2026-09-20, against the whole store.** Every `root-cause-of:` head
this project carries is closed, and most of what each one named is not:

| Head | Feature | Members | Still open |
| --- | --- | ---: | ---: |
| `PL-4FBP` | generator-heads | 24 | 21 |
| `PL-G424` | generator-heads | 21 | 19 |
| `PL-BHVM` | parallel-sessions | 8 | 6 |
| `PL-4Q9B` | generator-heads | 10 | 6 |
| `PL-6TP8` | generator-heads | 12 | 4 |
| `PL-G21K` | verify-false-reject | 7 | 3 |
| `PL-L4YG` | dev-tooling | 5 | 1 |
| `PL-2T03`, `PL-6T44`, `PL-HWW1`, `PL-TZ7T` | — | 14 | 0 |

**60 distinct open members**, 17.6% of the 341 open items, and four heads whose
clusters are genuinely drained. Nothing in `bin/docket` prints either fact.

**Why it matters.** The project owner's recurring question is "is that dealt
with?", and `CLAUDE.md` answers it for a feature with `bin/docket feature
<name>`. A generator has no equivalent. `docket show` on a *member* prints the head
with its status and cluster size (`PL-C97K`); on a *head* it printed nothing at
all about the cluster, so only one half of the edge was loaded and the count
over it existed nowhere. A session asked the question today reads item files until
it can answer, which is the read `CLAUDE.md` builds deterministic tooling to
replace: "printing the few lines a decision needs, instead of loading the
documents that hold them, is the same win as answering the question outright."

**The answer is also actively misleading without it.** Every head reads
`done`, so the surface a session sees says the generator work is finished. What
finished is the *cause* — a convention adopted, a check built — and each head's
brief is explicit that its members are repairs still owed. `format_generators`
already reasons about this: its docstring says a head at `done` "asks the
opposite question — whether this member still reproduces at all." Nobody has
asked that question of the 60, and nothing counts how many are left to ask it
of.

**This is not `impairs-generators:`, and that was checked rather than assumed.**
Nothing broke. `format_generators` renders what it was built to render and
`generator_check.py`'s stated scope is candidate clusters, not drain. This is a
report that does not exist, which is an enhancement to propose — the same
reading `PL-FH61` records for its own case.

**Its sibling is `PL-S0MB`.** That item is the identical failure on the other
surface: a catch-all `feature:` name can never report completion, so
`dev-tooling` (174 items) and `queue-hygiene` (29) cannot answer "yes, that is
dealt with" either. One problem, two surfaces; whichever is worked first should
read the other.

**A count is not the same as a work list, and this is why the report is worth
building rather than the sweep being run blind.** `.claude/rules/citation-drift.md`
— the rule `PL-G424` itself installed — decides that drift in a `done` or
`dropped` brief is *not a finding*, and that repairing a live one "rides the
current item's commit under the current item's id" rather than needing an item
of its own. Applied to that head's own members, the rule dissolves an unknown
number of them: `PL-RFSL` is the first instance recorded, filed because
`PL-38PN`'s remaining deliverable is refused by the closed-brief clause. So the
60 are an upper bound on outstanding work, not an estimate of it, and no
surface says which of the three dispositions each one takes. A report that
prints the cluster and its drain is what makes that sweep decidable in one pass
instead of sixty reads.

**Done when.** A session can ask how much of a generator's cluster is still
open and get the answer from a command rather than from a script — including
that four of the twelve are drained — and a test pins the count against a
store whose head is closed and whose members are not.

**Approved as the next workflow-lane item** (project owner, 2026-09-21,
ratified), over leaving it to rank on its `P2` band. The question it exists to
answer - "are the generators and their clusters dealt with?" - was asked again
on 2026-09-21 and answered a second time by a throwaway script over the whole
store: 12 heads, all closed; 99 distinct members, 60 still open; unchanged from
the 2026-09-20 figures in the table above, which is itself a fact no command can
report. Two derivations of the same number, two days apart, is the recurrence
`CLAUDE.md`'s deterministic-tooling rule is written for.

One addition the second derivation argues for: report the **drain trend**, not
only the present split. "Unchanged in a day" is the fact that made the answer
useful, and it needs the previous count, which nothing stores. The cheapest
honest form is to print each cluster's open count against the count at the
head's close date, both derivable from the store's `closed:` dates - not a new
stored field.

**Closed 2026-09-21.** `bin/docket generators` reports every cluster against how
much of it is still open, `docket show` on a head carries the same line, and a
member's id resolves to the head above it. `plan.clusters` builds the clusters
on `is_generator`'s own test, so a cluster this counts is exactly a claim the
checker accepts and `recommend` ranks.

**Two figures in the title and the problem line are wrong, and the table beneath
them is right.** There are **eleven** sound heads, not twelve: the table
enumerates eleven, and the twelfth is `PL-LSR0`, which ranks on the generator
tier by `impairs-generators:` and names no members to drain. The report prints
that item on a line of its own rather than in the count, so the discrepancy
cannot be re-derived a third time. The open-member figure was 60 at filing and
reads 58 today, which is the drain the trend below exists to show.

**The trend is three buckets rather than one number, and the reason is the
store's granularity.** `closed:` is a date and not a timestamp, so a member
closed on its head's own date cannot be ordered against it — **32 of the 99
member closures are that case**, a third of the edges. A single "open when the
head closed" figure would have had to pick a reading and print it as fact, which
`.claude/rules/apparatus-standard.md`'s floor refuses. So what closed *after*
the head is drain, what closed *on its date* is named beside the drain, and what
closed *before* is named only where it would otherwise stop the line's numbers
reconciling. The project owner asked for the count at the head's close date;
that figure is `open + closed since`, and the same-date bucket is what the dates
alone cannot assign to either side.

**`PL-S0MB` is still its sibling** and is untouched by this: a catch-all
`feature:` name cannot report completion, which is the same failure on the
feature surface rather than the generator one.
