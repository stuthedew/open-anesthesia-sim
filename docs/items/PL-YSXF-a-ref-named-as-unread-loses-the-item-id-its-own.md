---
id: PL-YSXF
title: A ref named as unread loses the item id its own branch name carries, which needs no history to read
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
milestone: v0.2.8
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-08-31
closed: 2026-08-31
pr: 124
verify: uv run pytest subprojects/docket/tests -k contributes
---

**Problem.** `branches_in_flight` reads an id two ways - from the branch name
and from the front of its commit subjects - and the two need different
evidence. The name read needs none at all: `claude/pl-k7qx-live` names its
item whatever history the checkout holds. The commit read needs the history
that lets `^base` exclude the default branch's own work.

A ref that cannot be answered goes to `unreadable` before the name loop runs,
so both reads are discarded together. The id the name proved is thrown away
with the ids the walk could not prove.

**Why it matters.** It is the collision the whole read exists to prevent,
arriving through the guard against the opposite error. `in_flight_ids` drops
`unreadable` entirely, so an unread ref means `docket next` offers an item a
live session is holding - and a branch named for its item is the case where
the checkout knew the answer for certain.

Two conditions put a ref there, and `PL-MGNC` added the second, so the
exposure grew rather than staying where `PL-KWC1` left it.

**Where.** `subprojects/docket/src/docket/vcs.py` - the name loop reads
`unlanded`, and `unreadable` refs never reach it.

**Done when.** A ref whose name carries an id contributes that id whether or
not its commits could be read, the report still says its commits went unread,
and a test covers a ref that is in both halves of the answer.

**Relations.** `PL-S1P1` (the refs that went unread never reach `docket next`)
is the same hole from the caller's side: that one carries the gap to the
callers, this one stops widening it in the first place. Both are
`branches_in_flight`; work them together.

**Triaged and admitted to v0.2.8's frozen list, 2026-08-31**, at the project
owner's direction once `PL-S1P1` had closed. P2, `defect`/`infra`,
`parallel-sessions` beside `PL-CPSY`, `PL-MGNC` and `PL-S1P1` - the same band
as the three holes it completes, because the exposure is the same one and is
met by default in a session container. Under the scope test in `ROADMAP.md`'s
"What the freeze closes": the queue's ranking is machinery this release's goal
names, and this is the fourth and last hole in the function the other three
were about.

The `verify:` command keys on `contributes`, the word the Done-when uses for
what an unread ref should still do. Run before it was written down: `-k
contributes` collects 313 tests and deselects all 313 today, so it fails now
and passes with the work. `-k named` was rejected - eight existing tests
already carry that word and all eight pass.

**Done 2026-08-31, by reading the name of a ref whose commits went unread.**
The name loop ran over `unlanded`, which is what is left after both guards have
taken their refs out, so a ref sent to `unreadable` never reached it. It now
runs over the candidates in either half, and such a ref is reported in `branches`
for the id its name proves *and* in `unreadable` for the ids its commits might
have added - one ref in both halves, which is what the report's two fields were
always able to say.

The direction is the argument, and it is the opposite of `PL-MGNC`'s on purpose.
A guard refuses an id *inferred* from a walk the history cannot support, where
being wrong withholds startable work. A branch name proves its id outright, and
what stays open is only whether the branch has landed - the cheaper uncertainty,
because an item whose work landed is closed and never offered anyway, while
dropping the id offers an item a live session is holding. A ref the default
branch already contains never reaches the read at all, which is what bounds it;
`test_a_landed_branch_contributes_nothing_however_its_name_reads` holds that
bound.

Two rendered sentences moved with it, because both had claimed too much: `flight`
now says what a ref's *commits* carry is unknown, and the line `PL-S1P1` put under
every queue answer says any item its commits carry is missing rather than that
work in flight on it is. The name half is no longer missing, so saying it was
would have been the same false completeness in reverse.

`-k contributes` selects five tests, three of which fail with the change to
`vcs.py` reverted; the other two are the negative controls - a ref whose name
carries nothing, and a landed ref - and pass either way, which is what makes them
worth having.
