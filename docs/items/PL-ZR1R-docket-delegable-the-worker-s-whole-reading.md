---
id: PL-ZR1R
title: `docket delegable` - the worker's whole reading list in one command
priority: P2
effort: S
status: done
classes: infra, session-cost
feature: delegation
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
added: 2026-08-25
closed: 2026-08-25
commit: c7728e2
---

**Problem.** PL-G3TG makes `docket list` mark delegable items, but reading them
out means `docket list | grep delegable`, and the marked line does not carry
the `verify:` command the worker needs. There is no single command that answers
"what may I work, and what proves each one done".

**Why it matters.** It is the difference between the owner running a worker
whenever spare capacity appears and needing a session in the loop to assemble
the batch first. The point of the delegation tier is that the middle of the
pipeline needs nobody; a batch that has to be hand-assembled puts a session
back into it.

**Where.** `subprojects/docket/src/docket/cli.py` (a new `cmd_delegable`) and
`render.py` for the format.

**First step.** A dedicated command rather than a `--delegable` flag on `next`.
`next` answers "what should *I* do now": it ranks, limits to three, and
explains its reasoning. A worker wants the opposite — every delegable item,
best-first, no prose, each with its `verify:` command printed beside it so the
batch can be worked without opening the files first. Different question,
different command; overloading `next` would make both answers worse.

Exclude what is in flight, as `next` does: a worker must not take an item
already on someone's branch. Print the count, so an empty result reads as
"nothing to do" rather than as a broken command.

**Note on why this was deferred, and un-deferred.** PL-G3TG deliberately left
it out "until the pilot shows the queue is big enough to need one". That was
the wrong criterion. The driver is not queue size but whether the owner can
start a worker run without a session assembling the batch, and they have asked
to be able to.

**Done when.** `docket delegable` prints every delegable, not-in-flight item
with its `verify:` command, and a worker pointed at `docs/worker.md` needs no
other command to know what to work.
