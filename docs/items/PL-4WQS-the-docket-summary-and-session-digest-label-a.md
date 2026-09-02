---
id: PL-4WQS
title: The docket summary and session digest label a count 'open' that excludes untriaged items, understating the queue by exactly the number beside it
status: untriaged
added: 2026-09-02
---

**Problem.** `render.py:600` prints `docket: {len(report.open_items)} open
(...), N untriaged`. `checks.py:119` defines `open_items` as `item.is_open and
not item.is_untriaged`, so the number labelled "open" is the *triaged* open
count and the untriaged count beside it is disjoint from it, not a subset.

Measured 2026-09-02 in this checkout: 88 items on disk are neither `done` nor
`dropped`; `bin/docket check` reported `87 open (0 P0, 10 P1, 45 P2, 32 P3), 1
untriaged`. The session-start digest reads from the same property and said `79
open` on a tree holding 87.

**Why it matters.** Small in size and awkward in placement: it is the first
line of the first command a session runs, and the two numbers invite the
reading "87 open, of which 1 is untriaged" when the truth is "88 open, of which
1 is untriaged". The error is exactly the size of the second number, so it is
largest after a capture-heavy session - the moment the queue's real depth most
needs stating.

The property's definition is right and should not change: `plan.py` needs the
set that is a candidate for work, and an untriaged item is a candidate for a
decision instead. What is wrong is one word in one rendered line, which is why
this is `S` rather than a refactor.

**Where.** `subprojects/docket/src/docket/render.py:600` (the summary line) and
whatever the session-start digest renders from - it shows the same number, so
both wordings move together or neither should. `checks.py:119` is read, not
changed.

**Approach.** Either label the count for what it is - `87 triaged` - or print
the true total and make the second number a subset, `88 open (1 untriaged)`.
The second is preferred: "how much is open" is the question the line is being
asked at session start, and a subset relationship is what a reader assumes from
the comma anyway.

The band breakdown stays as it is either way: it sums to the triaged count
because untriaged items carry no band, and that is correct rather than a second
instance of this bug.

**Found.** 2026-09-02, while confirming that a triage pass had moved all eight
untriaged items into bands - the total did not rise when a ninth item was
captured afterwards, which is what exposed the definition.

**Done when.** No rendered line labels a count "open" that omits untriaged
items, the session-start digest agrees with `bin/docket check` on the number,
and a test pins the wording against a store holding at least one untriaged
item.
