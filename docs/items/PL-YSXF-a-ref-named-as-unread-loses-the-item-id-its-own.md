---
id: PL-YSXF
title: A ref named as unread loses the item id its own branch name carries, which needs no history to read
status: untriaged
added: 2026-08-31
---

**Problem.** A ref named as unread loses the item id its own branch name carries, which needs no history to read

**Why it matters.**

**Where.**

**Done when.**

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
