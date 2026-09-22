---
id: PL-NJ9M
title: bin/docket delegable cannot tell a brief that determines the fix from one that leaves the choice open, so a hand-off meant to need no reading still does
priority: P2
effort: M
status: done
classes: infra
feature: delegation
touches: subprojects/docket, docs/worker.md
added: 2026-09-08
closed: 2026-09-22
pr: 895
verify: uv run pytest subprojects/docket/tests/test_cli.py -q && grep -rq 'def test_delegable_sends_the_worker_to_the_instructions' subprojects/docket/tests/ && grep -q 'reads as unclear and is not' docs/worker.md
---

**Problem.** bin/docket delegable cannot tell a brief that determines the fix from one that leaves the choice open, so a hand-off meant to need no reading still does

**What was observed.** Reviewing the 86 items `bin/docket delegable` currently
offers, for a hand-off to an external (non-Claude) worker on 2026-09-08:
`PL-YNCW` (`docket new --touches` before the title swallows it) is offered, and
its brief ends "Options worth weighing at triage: `nargs="+"` with repeated
use, a comma-separated single value, or leaving the parser alone and fixing
only the error message", with a `**Done when.**` permissive enough to accept
any of the three. Nothing in the front matter distinguishes that from
`PL-38PN` (stale source line citations), whose brief names the wrong line
numbers *and* the right ones, leaving nothing to choose.

**Why it matters.** `delegable` exists so a session can hand work off without
reading the queue - the command says so, and `docs/worker.md` tells the worker
to stop and write `**Blocked.**` when a brief is unclear. Both behave
correctly here and the round trip still happens: the item is dispatched, read,
blocked and returned, which is the cost the command was built to remove. The
failure is not silent, so this is friction rather than a wrong answer, and it
falls hardest on a worker that cannot ask - a session in another vendor's
harness, which is the case that motivated the review.

**Not decided: which end to fix.** Either triage resolves the options before an
item may read as delegable (a `**Decision needed.**` heading already exists for
questions the owner owns, and this is a smaller kind), or `delegable` prints
the caution beside the item rather than withholding it. The second is cheaper
and admits that "the brief still has a choice in it" is a judgment no check can
make from front matter alone - unless the shape of a resolved brief is made
decidable, which is the third option and the largest. Related: `PL-S2L4` (the
delegable list offers items `docs/worker.md` forbids a worker to touch) is the
other half of "the list cannot be handed over as printed".
**Done when.** A decision is recorded among the three the brief names - triage
resolves the open options before an item may read as delegable; `delegable`
prints the caution beside the item rather than withholding it; or the shape of a
resolved brief is made decidable - and the chosen one is built, with a test
pinning it. `PL-S2L4` (the delegable list offered items `docs/worker.md` forbids
a worker to touch) closed already and is the precedent worth reading first: it
is the same failure - the printed list cannot be handed over as-is - answered
once, and how it chose to report what it could not offer is the shape this
decision should either follow or deliberately depart from.

**Decision needed.** Which end is fixed: triage resolves a brief's open options before it may read as delegable, `delegable` prints the caution beside the item, or the shape of a resolved brief is made decidable?

**Measured 2026-09-22 on `main`, and it refutes all three options.** Each of
them assumes the defect has a population. It does not:

- `bin/docket delegable` offers **154** open items, up from the 86 reviewed on
  2026-09-08.
- **Zero of the 154 leave the fix open.** Four carry a `**Decision needed.**`
  section - `PL-9LXK` (nothing checks a prose claim about tier or adoption
  counts), `PL-DHJ7` (the live ROADMAP sections' unchecked subset counts),
  `PL-N32Y` (v0.1.0's wrong `Required scope` line) and `PL-SYG4` (the digest's
  reserved verdict) - and all four record the answer inside the brief:
  `**Project owner's decision, 2026-09-13.**`, `**Decided 2026-09-19 by
  PL-4FBP's ratified convention**`, the same, and `**Question 2 is answered
  (project owner, 2026-09-17, ratified).**`
- A scan of the 154 for this item's own observed shape - "Options worth
  weighing at triage", "Not decided", "either ... or leaving", "unresolved" -
  returns three hits, all narrative rather than open choices.
- `PL-YNCW` (`docket new --touches` before the title swallows it), the single
  observed instance, closed in v0.4.21.

**A convention closed the gap, not a mechanism.** The store leaves the question
standing and writes the answer underneath it, dated and naming who decided -
which is why 158 `done` items and 23 `dropped` ones still carry the heading. It
is the record of what was weighed, not a live question. Each option falls to
that: **option 3** would have to read prose to tell an answered section from an
open one, which is the judgment half `CLAUDE.md` forbids scripting; **option 1**
has nothing to resolve, no offered brief leaving a choice open; **option 2**
would print a caution beside 154 items where zero need it, a signal firing every
run without changing a decision.

**The cost this item was filed on is still live, by a route the brief did not
predict.** The answer sits *below* the question - 26 lines in `PL-9LXK`, 23 in
`PL-DHJ7`, 16 in `PL-N32Y`, 46 in `PL-SYG4`, which puts the sentence "Left at
`needs-decision` rather than triaged to `ready`" in between - under a heading a
worker has no rule to look for, while `docs/worker.md` § "When a brief is
unclear" opens "**Stop. Do not guess.**" and calls itself the most important
instruction in the file. A worker blocking there is obeying its instructions,
and the round trip happens anyway.

**Recommended: none of the three; put the rule where the reader is.** Built on
this branch so the recommendation can be read rather than imagined, and held
behind this decision rather than opened as a pull request, because it is not one
of the three options the brief named:

1. `docs/worker.md` § "When a brief is unclear" gains two paragraphs: a decision
   section on an item the worker was *given* is a record rather than a question,
   the three forms the answer takes, and read to the end of the brief before
   blocking on one. The escape stays - the convention is practice, not a
   guarantee - so a brief that really is unresolved still blocks.
2. `subprojects/docket/tests/test_cli.py` pins the listing footer that is the
   only path from `bin/docket delegable` to those instructions, and was
   untested.

**Why `delegable` itself is left alone.** Front matter cannot tell an answered
decision section from an open one, and an item that is genuinely open is already
withheld twice: `Item.delegability` returns at `status != "ready"` before
`model_guidance` returns "open design decision" for `needs-decision`. A third
read of the same fact would withhold the four answered items above, whose briefs
determine their fix completely.

**Decided 2026-09-22 (project owner, ratified)**, over all three options the
brief named - triage resolving a brief's open options before it may read as
delegable, `delegable` printing the caution beside the item, and making the
shape of a resolved brief decidable. None is built. The population measured
zero, and the round trip the item was filed on is removed in `docs/worker.md`
instead.

**What would reopen this.** The count, not the argument. A brief that reaches
`bin/docket delegable` leaving its fix genuinely open - no answer recorded
below the question, and the worker blocks correctly - is the instance this
decision says does not currently exist. One is ordinary evidence, since the
decision is ratified rather than specified: say so and put it back. The two
items filed alongside are what keep the count from drifting silently - `PL-RWJD`
(the answer-under-the-question convention is written down nowhere a triaging
session reads) and `PL-X4RX` (a brief's prose contradicting its own status field
goes unchecked), grouped as `feature: answered-decision-record`.
