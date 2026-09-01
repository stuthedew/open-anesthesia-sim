---
id: PL-S1P1
title: The in-flight ids reach docket next without the refs that went unread
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
milestone: v0.2.8
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
added: 2026-08-31
closed: 2026-08-31
pr: 123
verify: uv run pytest subprojects/docket/tests -k unread
---

**Problem.** `branches_in_flight` returns a `FlightReport` that names both what
is in flight and the refs whose merge-base with the default branch could not
be read - history a truncated clone does not hold. `in_flight_ids` drops the
second half, because a `set[str]` cannot carry it, and that set is what
`docket next`, `list`, `status`, `concurrent`, `delegable` and the session
digest all read. Only `docket flight` prints the gap.

**Why it matters.** It is the shape of failure this package guards against
everywhere else: `PullRequestHistory.declined` and `StrandedReport.declined`
both exist so a check that could not run is reported as such rather than as a
clean result. Here the same partial answer is presented as a complete one - a
session is told nothing is in flight when the truth is that one ref could not
be read - and the collision it prevents is discovered at push time.

The exposure is bounded: a ref must be fetched *and* truncated below its
merge-base for this to fire, which the container measured on 2026-08-31 was
not (all four refs resolved). It is a correctness-of-reporting hole rather
than an observed failure.

**Where.** `subprojects/docket/src/docket/vcs.py` - `in_flight_ids`; the
digest line in `render.format_digest`; `subprojects/docket/README.md`.

**Done when.** A session whose checkout could not read a ref is told so where
it reads the queue, not only when it runs `docket flight`, and a test covers
the digest saying it.

**Triaged 2026-08-31.** P3, `defect`/`infra`, `parallel-sessions` beside
`PL-CPSY` (a squash-merged branch whose ref survives reports its items in
flight forever) and `PL-KWC1` (read in-flight ids from the commits).

P3 rather than P2, and the split from `PL-CPSY` is deliberate. Both are holes
in the same function's answer, but `PL-CPSY` fires on a condition this project
meets today - squash-merge has been the merge strategy since 2026-08-30 - while
this one needs a ref that is fetched *and* truncated below its merge-base, which
the container measured on 2026-08-31 did not have. It is a
correctness-of-reporting hole with no observed instance, which is what the
lower band is for. It should not be worked ahead of `PL-CPSY`; they collide on
`vcs.py` anyway, so one session or a serialized pair.

The `verify:` command keys on `unread`, matching the word the Problem uses for
the dropped half of the `FlightReport`; nothing in `test_vcs.py` selects on it
today.

Not admitted to v0.2.8's frozen list: it completes no entry. `PL-KWC1` is an
entry and is `done`; this is `in_flight_ids` discarding a field `PL-KWC1` did
not add and does not depend on.

**Admitted to v0.2.8's frozen list, 2026-08-31, reversing the paragraph
above,** under the scope test now recorded in `ROADMAP.md`'s "What the freeze
closes": the queue's ranking is machinery the release's goal names, and this
is a third hole in the function `PL-CPSY` and `PL-KWC1` already cover.

**The "no observed instance" claim above is wrong, and the P3 band rests on
it.** A `--depth 1` clone of this repository with every branch tip fetched —
which is what the session-start hook produces, and therefore the normal state
of a container — was measured on 2026-08-31 with `bin/docket flight` reporting
two refs whose history it could not read. `in_flight_ids` drops exactly that
half, so `docket next` in a fresh container answers as though the refs had
been read and found clean. The precondition the paragraph above calls
unmet is met by default. Reband when the item is picked up.

**Rebanded P2 on being picked up, 2026-08-31,** as the paragraph above
required. The condition is met by default rather than not at all: this
container held one unread ref (`origin/Review_articles`) at the moment the work
started, `bin/docket flight` named it, and `bin/docket next` said nothing. That
puts it beside `PL-CPSY` and `PL-MGNC`, the other two holes in the same
function, rather than a band below them.

**Done 2026-08-31, by fixing the type rather than adding a line of output.**
`in_flight_ids` is gone. `FlightReport` grew an `ids` property, and every
caller that ranks or marks - `next`, `list`, `status`, `concurrent`,
`delegable` and the session digest - now takes the report and reads the ids off
it, so the unread refs travel with the answer instead of being dropped at the
boundary. A caller that wants to ignore them has to do so in writing, which is
what stops the next one re-opening the hole. `render.format_unread` owns the
one sentence all six print, so there is a single wording and a single place to
change it.

Found and fixed on the way: `_flight` resolved its root with `find_root()`
while every other command resolves it from the store, so `docket next --items
<elsewhere>` answered about in-flight work in whatever repository the command
happened to be run in. It is the wrong-project error `_load`'s docstring
already guards against, and it is also what made an end-to-end test possible -
`test_the_queue_commands_say_when_a_ref_went_unread` in `test_cli.py` runs all
six commands against `_shallow_pair`, the real truncated checkout `PL-MGNC`
built, and asserts each one says it.

**What this does not do.** `PL-YSXF` (a ref named as unread loses the id its
own branch name carries, which needs no history to read) is untouched: this
carried the gap to the callers, that one narrows the gap itself. Neither needs
the other's lines, and `branches_in_flight` is still the cheapest place to
spend the next pass.
