---
id: PL-JTXX
title: PL-0SCG is status ready but waits on GitHub Support ticket 4733783, so docket next can hand a live legal-exposure item to a session that cannot act on it
status: dropped
added: 2026-09-12
closed: 2026-09-12
reason: refuted by its own subject: GitHub Support's 2026-09-12 reply on ticket 4733783 turned PL-0SCG's remaining work into a bounded one-command check against a named pull-request range, so status: ready is correct and a session picking it up learns the answer rather than finding a dead end
---

**Problem.** PL-0SCG is status ready but waits on GitHub Support ticket 4733783, so docket next can hand a live legal-exposure item to a session that cannot act on it

**Verified 2026-09-12.** `PL-0SCG` reads `priority: P2`, `status: ready`,
`classes: docs, infra`, and its title records that GitHub Support ticket
4733783 is open because pre-rewrite blobs - publisher-copyright PDFs - may
still be reachable through `refs/pull/*/head` after the copyright purge.

`ready` is a commitment that the work can be started and proved. This work
cannot: it waits on a third party this project does not control, and no
session can close it. So `bin/docket next` can offer a live legal-exposure
item to a session whose only honest move is to hand it straight back.

The `docket` skill already separates these two cases - a question this project
can answer is `needs-decision`, and something only an outside event resolves is
not debt a session can clear. This is the second shape.

**Dropped 2026-09-12, the same day it was filed**, by the session that filed it.
The argument was sound against the state it was written in: while support ticket
4733783 was an open-ended wait, `PL-0SCG` was unstartable and `bin/docket next`
could hand a legal-exposure item to a session with no move available.

Support's reply ended that state. The remaining work is now a bounded check any
session can run in one command against a named range:

```text
git ls-remote origin 'refs/pull/*/head' | sed -E 's#.*refs/pull/([0-9]+)/head#\1#' \
  | awk '$1>=297 && $1<=386' | wc -l
```

It read 90 on 2026-09-12 and reads 0 once GitHub completes the purge, at which
point `PL-0SCG` is done. So `ready` is right and there is nothing here to work.
Kept rather than deleted so the reasoning is findable if the status is
questioned again - the answer is that it depends on the ticket's state, which
changed.

