---
id: PL-TP5M
title: PL-ZBRB's advisory names blocked-by to work around a checker that did not read it, and PL-KBD0's check now does
priority: P3
effort: S
status: done
classes: infra
feature: planning-cadence
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-13
closed: 2026-10-03
verify: grep -qF 'one repair then satisfies both checks' subprojects/docket/src/docket/checks.py
---

**Problem.** PL-ZBRB's advisory names blocked-by to work around a checker that did not read it, and PL-KBD0's check now does

**Why it matters.** `PL-ZBRB`'s advisory reports an undeclared prose
prerequisite, and its message names both `status: blocked` and `blocked-by`
because, at the time, nothing read the second field - `plan.py` filtered on
status alone and `concurrency.py` was the only consumer of the edge. Its own
docstring says so. `PL-KBD0` closed that gap: `_ready_with_an_open_blocker` now
errors on a `ready` item declaring an open blocker, so a reader who acts on
`PL-ZBRB` and stops one field early is caught by a check rather than by a
sentence.

The message is therefore doing work a checker now does, and a reader who
follows it can be told the same thing twice in one run - once as an advisory
about the prose, once as an error about the field.

**Not urgent, and deliberately not folded into `PL-KBD0`.** Narrowing an
advisory's wording is a judgment about what a reader needs to be told, not a
consequence of the check landing, and `PL-KBD0` was already deciding one
question about how far a check should reach.

**Where.** `subprojects/docket/src/docket/checks.py`, `PL-ZBRB`'s advisory
message and its docstring's note about naming both fields.

**Decision needed.** Whether the advisory should now name only `blocked-by` -
leaving the status contradiction to the check that reads it - or keep naming
both because the two fire in different situations and a reader meeting the
advisory may not be about to trip the error. Check what the two messages
actually read like together on one item before deciding; it may be that they
compose fine and the honest answer is to change nothing but the docstring's
note.

**Done when.** The two messages have been read side by side on one item that
trips both - which is the step the answer rests on and which nobody has taken -
and `PL-ZBRB`'s advisory and its docstring say what is true after `PL-KBD0`:
either naming only `blocked-by`, or keeping both with the reason they still
fire in different situations, or changing nothing but the docstring's stale
note that no checker reads the field.

## Decided 2026-10-03 - keep both fields in the message; the two stale docstring notes are the whole edit

**The side-by-side read the brief asked for**, taken on 2026-10-03 on a scratch
copy of the store with `bin/docket check --items`, three items added: one
declaring an open blocker under `status: ready` and narrating a second,
undeclared one; one declaring only; one narrating only. On the item that trips
both, the run prints (the id and path shortened):

    error     sits at `ready` while PL-024 is still open; `ready` says the
              work can be started now, so set `status: blocked`, or drop the
              edge if it no longer holds
    advisory  names PL-029 as a prerequisite in prose and does not list it in
              `blocked-by` - "**Blocked on `PL-029`**, whose work this one
              builds on.". Declare the edge and set `status: blocked`, which is
              the half `docket next` reads, or reword the sentence if it is not
              a prerequisite - or, if it records a wait that no longer holds,
              open its passage with `[superseded YYYY-MM-DD]`

They compose. Each names its own edge (`PL-024` declared, `PL-029` narrated)
and its own repair, and the two cannot fire on one edge: the error needs the
edge declared and the advisory needs it undeclared. "Told the same thing twice"
is two edges each told once. On a single edge they fire in sequence, and that
sequence is why the message keeps both fields: a reader who follows an advisory
naming only `blocked-by` lands on the error at the next run. `PL-KBD0` built
that error as the backstop for the reader who stops one field early, not as the
instruction, so the advisory names the whole repair and one edit satisfies both
checks. The message's clause "which is the half `docket next` reads" is still
true - `plan._startable` filters on `status` alone and never opens `blocked_by`,
read 2026-10-03 - so nothing in the message is false. Neither check fires on the
real store today: 0 errors and 0 advisories of these two kinds, the scratch
items aside.

**Recommendation:** keep the message as it is, and rewrite the two docstring
notes that stopped being true when `PL-KBD0` landed on 2026-09-13:

- `_undeclared_prerequisites`: "Three items are in that state today; `PL-KBD0`
  is whether the checker should hold the two fields together" - it does, and
  the message names both because one repair then satisfies both checks.
- `_ready_with_an_open_blocker`: "`PL-ZBRB`'s message has to name both fields
  to work around it, which is a message doing a checker's job" - it names both
  so that one repair satisfies both checks; this error is the backstop for the
  half-repair, not the reason the message is worded as it is.

**Decided 2026-10-03** by the design-round session as an obvious call, over
narrowing the message to `blocked-by` (a second round trip for every reader who
follows it, caught by an error instead of told in a sentence) and over changing
nothing (two docstrings stating as open a question answered three weeks ago).
Made in this round rather than handed to a build thread: two sentences, no
behavior, no test, in the one file the item declares.
