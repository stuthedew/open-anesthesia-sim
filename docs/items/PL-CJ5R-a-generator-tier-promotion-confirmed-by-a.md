---
id: PL-CJ5R
title: A generator-tier promotion confirmed by a reader arrives too late to rank anything twice now: root-cause-of only moves a queue position, so writing it onto an item already being implemented is a no-op, and PL-GYRX was dropped for the same reason
priority: P2
effort: S
status: done
classes: defect, infra
feature: recurrence-signal
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md, docs/WORKING_NOTES.md
added: 2026-09-21
closed: 2026-09-21
payoff: a reader asked to confirm a generator promotion can act on the answer, because the cluster is only named while the item still has a queue position to move
verify: uv run pytest subprojects/docket/tests/test_plan.py subprojects/docket/tests/test_cli.py subprojects/docket/tests/test_checks.py -q && grep -q 'def test_an_item_in_flight_is_not_offered_for_promotion' subprojects/docket/tests/test_plan.py
---

**Problem.** A generator-tier promotion confirmed by a reader arrives too late to rank anything twice now: root-cause-of only moves a queue position, so writing it onto an item already being implemented is a no-op, and PL-GYRX was dropped for the same reason

**Where this came from.** The project owner ratified the promotion of
`PL-W7WL` (the release cut writes notes before `record` backfills `pr:`) to the
generator tier on 2026-09-21, on a session's recommendation, over declining it.
Reading the store before writing the field showed the write would do nothing.

**The claim itself is sound, and that is not the problem.** `PL-66X4`,
`PL-2M5T` and `PL-3HMQ` are three re-filings of one mechanism — all three
`dropped` as duplicates of `PL-W7WL`, which is the evidence that it causes
them — and `root_cause_faults` requires only that the named ids be distinct,
known to the store, and three or more. It would validate.

**It would also rank nothing.** `plan.py` builds its generator map from
`startable` items alone: `{item.identifier: item.root_cause_of for item in
startable if is_generator(item, known)}`. A `done` item is not startable, so
the tier never reaches it. `PL-W7WL` is being implemented right now on
`claude/friendly-mccarthy-ylyzxc` — unpushed, and past its metadata into
`release.py` and the cli imports — so the field would be written onto an item
about to close, and its close-out rewrites `status`, `closed` and `pr` in the
same front matter that the write would touch.

**Why it matters: this is the second instance, which is what makes it a
mechanism rather than an accident.** `PL-GYRX` was dropped 2026-09-19 with exactly this reasoning
about the sibling field: "a closed item is never ranked, and
`impairs-generators:` only changes a queue position. Backfilling the field onto
merged work would record a claim nothing acts on." Two fields, two entrances to
one tier, the same hole in both: the confirmation a human reader owes arrives
after the window in which the promotion could have moved anything.

**What is not lost.** `PL-X5JR`'s `recurrences:` field is already on `PL-W7WL`
on `main` — `recurrences: 2026-09-13 PL-66X4, 2026-09-14 PL-2M5T, 2026-09-20
PL-3HMQ` — and `bin/docket show` prints it with "That is the generator
threshold." So the auditable fact survives and the next reader gets the same
prompt. Only the queue-position bump was unavailable, and only because the item
was already being worked.

**Recommended.** Surface the promotion candidate at the moment `bin/docket
next` is about to *offer* the item, where a reader can act on it and the item
is by definition still startable — the shape `verify_required_from`'s advisory
already uses — rather than leaving it to whoever happens to read `docket show`.
Not a promotion by the heuristic, which `PL-X5JR` refuses and this does not
reopen: the reader still decides, but is asked at the only moment their answer
can change a ranking.

**Done when.** A recurrence cluster at or above the generator floor is reported
where it can still rank the item, and a test pins that an item already closed
or in flight is not offered for promotion.

**What was built, and where the recommendation above was already half true.**
Surfacing at `bin/docket next` had landed with `PL-X5JR`: `_say_recurring`
prints the cluster beside `_say_promotable` on both the ranked and the empty
answer, and the session-start digest carries the same line. So the moment was
already right and the *population* was wrong - `plan.recurring` filtered on
`CLOSED_STATUSES` alone, which named a candidate whose promotion `recommend`
would never read. It now takes the in-flight ids the ranking already excludes
on, and both call sites pass them.

**`untriaged` and `blocked` were deliberately kept, though `_startable`
excludes them too.** The rule is the narrowest that removes the hazard, which
is the window having *closed* rather than not yet opened. A claim written onto
an untriaged item ranks the moment triage seats it and is what a triage pass
most wants before choosing a band; one on a blocked item ranks when its
blocker clears. Dropping them would have traded this defect for the same
defect pointing the other way. Measured before deciding: 4 items in the store
sit at or above the floor, 2 of them open and named, and neither is untriaged
or blocked - so the carve-out costs nothing today and the suppression is what
had to be argued for.

**A third surface said so out loud, and the filter made it false.**
`_record_recurrence` printed "`bin/docket next` now names it as a
generator-tier promotion candidate" on the filing that crossed the floor - a
prediction about another command, and wrong from the moment the matched item
was on a branch. It states the floor instead, with the condition carried, and
does not buy an accurate sentence with a git call: `docket new` reads no refs,
and the capture path is the one `CLAUDE.md` keeps cheap because it runs when
usage is nearly spent. `docket show` was left alone deliberately - its "That
is the generator threshold" is a fact about the count, and it prints the
`IN FLIGHT` mark two lines above.

**What it cannot catch, stated rather than implied.** An unpushed branch is in
no ref, so `flight` cannot see it - which is the state `PL-W7WL` was actually
in when this was found. The filter catches every pushed in-flight branch and
no unpushed one; `FlightReport.unreadable` and `_say_unread` already carry
that gap beside the answer, per the apparatus floor.
