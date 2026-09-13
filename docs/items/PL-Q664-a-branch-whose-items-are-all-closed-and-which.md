---
id: PL-Q664
title: A branch whose items are all closed and which has no open pull request is indistinguishable from live work in docket flight, so finished work can stall unseen
status: untriaged
added: 2026-09-13
---

**Problem.** `bin/docket flight` reports an item as in flight from a commit
subject alone, and says so plainly: "A live session and a branch nobody will
merge look the same here; the age is what separates them." Age is a weak
separator on a project where a session turns around in under an hour. There is
a stronger one available and unused: whether every item the branch touches is
already `done` or `dropped`, and whether the branch has an open pull request.
Both are decidable - the first from the branch's own item files, the second
from one API call `tools/pr_title_check.py` already makes and already degrades
to a silent skip when it cannot look.

**Worked instance.** `claude/hopeful-allen-tetrje` carried `PL-NB35` and
`PL-VV16` at `status: done, closed: 2026-09-13`, ten item files existing
nowhere else, a clean merge into `main`, and no pull request. Every session's
digest read "in flight ... do not start these again", so the queue was telling
sessions to leave alone work that nobody was doing. It surfaced only because
the project owner asked whether the feature had been built, three hours later.

**Why it matters.** This is the failure `flight` exists to prevent, arriving
through the one state it cannot see. Finished-and-unopened is the worst case of
it: the work is complete, the evidence is on a branch, and the signal that
would recover it points the other way.

**Sketch.** A third line in `flight`'s output, or a new `docket unopened`:
branches whose closed-item set is non-empty, whose open items are none, and for
which no open pull request exists. Wording matters - the check can say "nothing
here is being worked", never "safe to merge".
