---
id: PL-X9T3
title: Run the Qt spike on the project owner's own machine and record frame cost, input latency and how it looks, which is the half no session here can measure
priority: P2
effort: S
status: blocked
classes: perf, ux
feature: teachable-case
blocked-by: PL-55DH
touches: docs/WORKING_NOTES.md
not-delegable: the measurement has to run on the project owner's own hardware. `PL-2QMK` records why no session here can do it - the web container has no GPU and Flet's renderer cannot even load - and the whole point of this item is the number this container is structurally unable to produce.
verify: python3 tools/doc_check.py check && grep -q 'PL-X9T3' docs/WORKING_NOTES.md
added: 2026-09-08
---

**Problem.** Run the Qt spike on the project owner's own machine and record frame cost, input latency and how it looks, which is the half no session here can measure

**The half no session here can do.** `PL-QXSB`'s Qt measurement is the
Python-side frame only: 0.51 ms to hand six traces and twelve readouts their new
values. Painting was unmeasurable — no GPU, a software rasteriser, an offscreen
platform plugin — and forcing a repaint gave 18-28 ms *including for an
unchanged frame*, which is an artifact rather than a figure.

**Why it matters.** It is the load-bearing half of `PL-QXSB`'s evidence. The
Python-side number already favours Qt by forty-fold, but the term it leaves out
is the one a reader actually experiences, and a decision to rewrite the
interface on half a measurement would be exactly the "recommend first, research
afterwards" `CLAUDE.md` names. It is also the item most likely to *stop* the
port cheaply, which is worth as much as the one that starts it.

**What to record**, on the owner's machine, at 1x and 300x:

1. **Frame cost** — the same three-stage split `PL-YSZN` used on Flet, so the
   numbers are comparable rather than merely favourable.
2. **Input latency** — how long a callback that is ready to run waits. That is
   what "laggy" named, and Flet's is 20-30 ms p90 after `PL-KP7H` and `PL-R2YM`.
3. **How it looks.** Whether six traces are distinguishable, whether the type
   is legible at the sizes the dashboard uses, and whether a drag feels
   immediate. No measurement substitutes for looking at it.

**Done when** the three are written into `docs/WORKING_NOTES.md` beside
`PL-QXSB`'s own measurements, so the decision reads one comparison rather than
two.
