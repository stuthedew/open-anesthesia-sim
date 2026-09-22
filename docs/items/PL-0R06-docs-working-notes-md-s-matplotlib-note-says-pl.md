---
id: PL-0R06
title: docs/WORKING_NOTES.md's matplotlib note says PL-KP7H and PL-YLKR would both be rebuilt against a WebAgg canvas, but PL-YLKR closed as design-only on 2026-09-14 and its build is PL-YVHK
priority: P3
effort: S
status: ready
classes: docs
feature: queue-hygiene
touches: docs/WORKING_NOTES.md
added: 2026-09-14
verify: ! grep -qF 'would both be rebuilt against it' docs/WORKING_NOTES.md && python3 tools/doc_check.py check
---

**Problem.** docs/WORKING_NOTES.md's matplotlib note says PL-KP7H and PL-YLKR would both be rebuilt against a WebAgg canvas, but PL-YLKR closed as design-only on 2026-09-14 and its build is PL-YVHK

**Where.** `docs/WORKING_NOTES.md:1287-1289`, in the thread "Measured and
answered: a server-rendered chart is not the way out - PL-YDKJ, PL-2FM6,
PL-2QMK, PL-YSZN (2026-09-08)", under "**Two costs the item does not list.**":

> - **It gives back `PL-KP7H`.** The paused-only hover is Flet controls
>   answering a hover. matplotlib's WebAgg canvas has its own event model, so
>   `PL-KP7H` and `PL-YLKR` would both be rebuilt against it.

**Verified 2026-09-14 against `fb60a00`.** Both named items are closed, and
neither is a thing a WebAgg canvas could make anyone rebuild.

- `PL-KP7H` (drop the per-point default tooltip, which halved a saturated
  frame) is `status: done`, `closed: 2026-09-08`, `milestone: v0.4.11`,
  `pr: 475`.
- `PL-YLKR` (design what a chart tooltip says) is `status: done`,
  `closed: 2026-09-14`, `milestone: v0.4.22`, and its `touches` is
  `docs/MODEL.md, ROADMAP.md, docs/items` with
  `verify: python3 tools/doc_check.py check && grep -qF 'what the tooltip may
  show' docs/MODEL.md`. It shipped a derivation in the specification and no
  code, so there is nothing of it to rebuild against any canvas; what it
  produced transfers to whatever draws the chart.
- The build was split out as `PL-YVHK` (`added: 2026-09-14`, `status: blocked`,
  `blocked-by: PL-G59B`), whose title is "Implement the chart hover readout on
  pyqtgraph". So the live work is already aimed at a third toolkit, not at Flet
  and not at WebAgg.

**Why it matters.** The bullet is one of the two costs the thread weighs against
option 3, and the thread's conclusion — "**Recommendation: option 1**" — is a
recorded decision a later session is meant to be able to re-read and trust. As
written it prices the cost against two closed items, one of which never had an
implementation, which makes the cost look larger and more concrete than it is.
A session revisiting the matplotlib question would either re-derive the cost
from scratch or take a wrong figure into the argument, and a decision record
that has to be re-checked before it can be used is not doing the job the thread
exists for.

**Done when.** `docs/WORKING_NOTES.md:1287-1289` names the work a WebAgg canvas
would actually cost — the hover implementation `PL-YVHK` carries, which is
`blocked-by: PL-G59B` and built on pyqtgraph — rather than `PL-KP7H` and
`PL-YLKR`, and says that `PL-YLKR` was design-only so its derivation transfers
to any canvas rather than being rebuilt against one. The recommendation and the
measurements above it are unchanged. `python3 tools/doc_check.py check` reports
0 errors.

**Out of scope, deliberately.** The wider question of whether the whole
matplotlib thread is still live now that `v0.4.25` moves the chart to pyqtgraph
ahead of `v0.5.0` is not this item. This is a two-line correction to a gloss;
re-opening the recommendation is a decision, and belongs to whoever scopes the
port's chart work.

**Re-scoped 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
Append a dated note naming `PL-YVHK` rather than rewriting the 2026-09-08
costing. The costing is correct as the arithmetic of its own date; what changed
is what the two items turned out to be, which is a later fact and takes a later
date.
