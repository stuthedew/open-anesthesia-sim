---
id: PL-JTXX
title: PL-0SCG is status ready but waits on GitHub Support ticket 4733783, so docket next can hand a live legal-exposure item to a session that cannot act on it
status: untriaged
added: 2026-09-12
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
