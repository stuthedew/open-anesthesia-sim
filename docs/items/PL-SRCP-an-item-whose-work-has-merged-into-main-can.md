---
id: PL-SRCP
title: An item whose work has merged into main can stay open in the queue, and docket next then offers already-landed work
status: untriaged
added: 2026-08-30
---

**Problem.** Closing an item out is a manual edit in a separate commit from the
work, so a session that lands its change and then ends leaves the item at
`status: ready`. Nothing notices. `docket next` keeps ranking it, `docket wave`
keeps counting it as an open gate entry, and the digest keeps reporting a queue
larger than it is.

**Found 2026-08-30.** PR 92 merged `PL-1TPM` (mark a suggestion the current
step has not reached) and `PL-0RS6` (rank in-scope work above out-of-scope
work) into `main`. Both item files still read `status: ready` afterwards. Both
`verify:` commands passed on the merged tree, and `PL-1TPM` was a frozen
v0.2.8 gate entry, so the gate read 18 open when it was 17 and `docket next`
offered `PL-1TPM` as the second-best thing to do — work a session would have
started and found already written. Closed out by hand in the session that found
it.

**Why it matters.** The failure is silent and it points the wrong way: every
other queue defect makes work invisible, and this one makes finished work
*visible*, which is worse, because a session acts on it. It also corrupts the
two numbers the owner steers by — the gate's open count and the digest's item
count — and it corrupts them in the direction of "there is more left than there
is", which is the direction nobody double-checks.

**Where.** `subprojects/docket/src/docket/vcs.py` already knows how to ask git
questions; `subprojects/docket/src/docket/check.py` is where an advisory would
be raised. This is the mirror of `PL-64LS` (detect items stranded on an unmerged
branch), which asks the same question in the other direction, so the two are
worth designing together and may share one git pass.

**First step — decide what the evidence is.** Commit subjects carry the item id
by convention (`CLAUDE.md`'s "Name the work after the item"), so
`git log <default-branch> --format=%s` yields the ids whose work has landed, and
any of those still at `status: ready`/`in-progress` is the finding. That is
decidable and cheap. It is also only a convention: an item worked without its id
in a subject stays undetected, which is the same honest limitation
`docket concurrent` and the milestone marking already document, and it belongs
in `subprojects/docket/README.md` next to them.

The alternative — running each open item's `verify:` command and flagging the
ones that pass — is not it: `verify:` for a coverage item passes on a tree where
nothing has been done, and running the suite per item costs minutes.

**Done when.** An item whose id appears in a merged commit subject on the
default branch while its status is still open is reported where a session will
see it before it starts work, the detection is derived from git rather than from
running tests, and what the check cannot see is recorded in
`subprojects/docket/README.md`.
