---
id: PL-4F6P
title: A `**Worked.**` note said "nothing the brief did not specify" for a test that reached into a private class
priority: P2
effort: S
status: done
classes: defect, docs, session-cost
feature: worker-instructions
milestone: v0.2.5
touches: docs/worker.md, docs/items/PL-5BTB-cover-the-parameter-validators-four-rejection.md
added: 2026-08-25
closed: 2026-08-25
commit: 6e19632
---

**Problem.** PL-5BTB's tests reach into `parameters_module._AgentPayload` and
`._ReferenceAdultPayload`, private classes, to exercise the four validator
rejection paths. That is a reasonable call — the guards are private validators
and the public loader may not reach all four — but it is a decision the brief
did not make. The item's `**Worked.**` note reads "Nothing the brief did not
specify."

**Why it matters.** The `**Worked.**` note is the reviewer's map to the parts
of a diff that a passing check cannot vouch for. If it under-reports, the map
is wrong exactly where it is needed, and the reviewer's saved effort is
returned as a false sense of coverage. This one was caught by reading the
diff; the next may not be.

The likely cause is that `docs/worker.md` describes the note as listing
"judgment calls", which reads as *choices between stated alternatives* rather
than *anything the brief left open*. Coupling a test to a private symbol does
not feel like a judgment call when there was no obvious alternative.

**Where.** `docs/worker.md`, **The `**Worked.**` note**. Related to PL-0RFH,
which is about the same file under-describing what a worker decides.

**First step.** Give examples of what belongs in the note rather than a
category name: a private or internal symbol used, a fixture or helper
introduced, a parameter value chosen, a structure the brief left open. "If a
reviewer would be surprised to find it in the diff, it goes in the note."

**Done when.** `docs/worker.md` describes the note by example, and the
private-class coupling in PL-5BTB is either recorded in its item or judged
fine and left alone deliberately.
