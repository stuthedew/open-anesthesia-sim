---
id: PL-SWP3
title: PL-3CBS's landed-work advisory is keyed on verify: and scoped to ready/needs-decision, so an item captured and worked in the same commit is structurally invisible to it: #635 left PL-0J9K and PL-MMVF untriaged with their code on main
status: untriaged
feature: queue-hygiene
added: 2026-09-17
---

**Problem.** PL-3CBS's landed-work advisory is keyed on verify: and scoped to ready/needs-decision, so an item captured and worked in the same commit is structurally invisible to it: #635 left PL-0J9K and PL-MMVF untriaged with their code on main

**What was found.** `PL-3CBS` (done, v0.2.8) built the advisory that reports an
open item whose work has already landed. It is keyed on `verify:` — "the item's
own statement of what would prove it done" — and scoped to `ready` and
`needs-decision` items carrying one. That key was chosen on a measurement and
the measurement was right: the obvious alternative, an item id at the head of a
merged commit subject, was 85% false positives (eleven of thirteen such ids on
`main` were capture or triage commits).

**The blind spot is the shape the key cannot reach.** An item captured *and*
worked in the same commit never passes through `ready`, so it never acquires a
`verify:` command, so it can never be a candidate. Both of the check's scoping
clauses exclude it, independently.

**The instance, verified 2026-09-17 against `origin/main`.** `#635` (`ff4be61`,
"PL-XD3C, PL-MMVF, PL-0J9K: make digest's git calls measurable, then cut them by
half") *added* six item files and landed 385 lines of
`subprojects/docket/src/docket/vcs.py` in one commit. `git cat-file --batch`
(`PL-0J9K`'s ask) is at `vcs.py:313` and `GitRunner`'s memo (`PL-MMVF`'s ask) is
at `vcs.py:174`. Both item files still read `status: untriaged` on `main`.

**What it cost, rather than what it could cost.** Both items appeared in
`bin/docket triage`'s untriaged list and in this session's own review of it, and
were recommended to the project owner as live work on a four-item branch. The
correction came from reading `vcs.py`, not from any check. A session had already
been started on that branch when the error was caught.

**Why the capture-and-work shape is common here rather than exotic.**
`CLAUDE.md` asks a session that diagnoses a cluster to file it in one call
(`docket new --feature ...`) and permits fixing what its three-test door admits
in the same branch. A commit that files five items and implements two is
therefore the encouraged shape, not an aberration — which is what makes this
worth a check rather than a one-off correction.

**Do not re-propose the commit-subject signal.** `PL-SRCP` was dropped as a
duplicate of `PL-3CBS` partly for proposing it, and the 85% figure is why. A
candidate key worth measuring instead: an *open* item whose file was **added**
by a commit that also changed a non-`docs/items/` path, which is decidable from
one `git log --diff-filter=A` and does not depend on the subject line at all.
Count its false-positive rate before building it — `CLAUDE.md`'s "name the
number that would change your mind, then go and count it" applies, and the
number here is what fraction of captured-and-worked commits actually finished
the item versus merely started on it.

**Not a defect in `PL-3CBS`.** Its check is sound within its scope and its key
was chosen correctly on evidence. This is the residual it did not cover.

**Where.** `subprojects/docket/src/docket/checks.py`, beside the advisory
`PL-3CBS` added.
