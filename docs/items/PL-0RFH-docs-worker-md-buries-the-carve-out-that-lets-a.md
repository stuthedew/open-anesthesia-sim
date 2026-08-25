---
id: PL-0RFH
title: `docs/worker.md` buries the carve-out that lets a worker decide anything at all
status: ready
priority: P2
effort: S
classes: docs, session-cost
feature: worker-instructions
touches: docs/worker.md
added: 2026-08-25
---

**Problem.** `docs/worker.md` states the no-improvising rule at length and
puts the carve-out — that a worker fixes its own work in progress, inside the
item's `touches`, without asking — in one paragraph beneath it, phrased as an
exception. Read quickly, the file says "never decide anything".

**Why it matters.** It cost a good item. Working PL-LHHG, the worker found
that a 60-second step is rejected by the controller before the commissioned
guard is reached, and proposed narrowing its own test to the 0.1-second step
used elsewhere in the same file. That is squarely on the permitted side of the
line: it was changing code it had written for that item, inside `touches`, not
the brief, the command, the tooling or the implementation. It was told not to
improvise and restarted the item anyway.

No harm resulted — it reached the same test on the second pass — but the
failure mode is real and it runs the opposite way from the one the rule was
written against. A worker that blocks on every judgment call delivers nothing
and returns every decision to the owner, which is the cost the delegation tier
exists to remove. Over-blocking is quieter than improvising and therefore
likelier to persist.

**Where.** `docs/worker.md`, the **When something errors** section.

**First step.** State the permitted side first and positively — the worker is
expected to make ordinary implementation decisions inside `touches`: names,
fixtures, structure, which parameters a test uses — before listing what it may
not touch. Give the PL-LHHG case as the worked example of a decision it should
have made without asking, since an example of permitted judgment is exactly
what the section lacks.

**Done when.** `docs/worker.md` says plainly what a worker decides for itself,
and a reader of the errors section cannot come away thinking every choice is a
block.
