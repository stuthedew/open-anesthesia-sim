---
id: PL-GTW5
title: docket check's headline open count excludes untriaged items, so 'N open, M untriaged' reads as M of N when it is actually N plus M
status: untriaged
added: 2026-09-05
---

**Problem.** docket check's headline open count excludes untriaged items, so 'N open, M untriaged' reads as M of N when it is actually N plus M

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `bin/docket check`'s first line reads

```
docket: 169 open (0 P0, 8 P1, 99 P2, 62 P3), 0 untriaged, 0 errors, 4 advisories
```

and the session-start digest reads the same way (`164 open - 0 P0, 8 P1,
94 P2, 62 P3` with `6 items untriaged` on a later line). The band breakdown
sums to the headline exactly, because both count only items carrying a
`status:`. An untriaged capture has none, so it is in neither. Measured
2026-09-05: 466 item files, 251 `done` + 46 `dropped` = 297 closed, and
118 `ready` + 38 `needs-decision` + 13 `blocked` = 169 - the headline. The
six untriaged captures at session start were a further six.

**Why it matters.** "169 open, 6 untriaged" reads to any ordinary reader as
*six of the hundred and sixty-nine*, and it means *a hundred and seventy-five,
six of which nobody has triaged*. The error is small in proportion and
systematic in direction: it always understates, and it understates by exactly
the work that has arrived most recently and been examined least. Observed the
same day: closing one untriaged item left the headline unchanged at 169, which
is the shape of the confusion - work left the queue and the number that
describes the queue did not move.

It also affects nothing downstream, which is why this is P3 rather than
higher. `docket next` ranks startable items and untriaged ones are not
startable; `docket gate` counts by class; the triage advisory names the number
separately and prominently. Nothing computes a wrong answer. It is a label
that invites a wrong reading, in the one line every session reads first.

**Approach, and it is a wording change rather than a counting change.** The
current number is the useful one - triaged, placeable work is what a session
can act on - so do not fold untriaged items into it. Say what it is instead:
`169 triaged open, 6 untriaged` or `169 open of 175, 6 untriaged`. Whichever
wording is chosen, the digest's line and `docket check`'s line should agree,
since they are read minutes apart by the same reader.

**Done when.** The headline distinguishes triaged-open from all-open, in both
`bin/docket check` and the session-start digest, with a test pinning the
wording so it cannot drift back.
