---
id: PL-27H0
title: docs/MODEL.md still specifies a per-step recorded sample store and a display operation that selects which recorded samples a trace draws, both of which PL-2FM6 deleted
status: untriaged
added: 2026-09-14
---

**Problem.** docs/MODEL.md still specifies a per-step recorded sample store and a display operation that selects which recorded samples a trace draws, both of which PL-2FM6 deleted

**Found 2026-09-14, re-briefing `PL-RD3B` against the tree `PL-2FM6` left.**
`PL-5328` found the same cause in an item's brief; this is the same cause in
the authoritative model specification, which is the more consequential of the
two. `CLAUDE.md` treats stale documentation here as a safety issue rather than
tidiness.

**What the document says.** Two places, both in § "What the display layer may
do" and the paragraphs under it:

- the permitted-operations list opens with "select which recorded samples a
  plotted trace draws, subject to the constraint below";
- "**What a recorded sample is.** The recorded history is one sample per
  simulation step, and each sample is a simulated time together with one entry
  *per substance* ..."

**What the tree holds.** Measured on `9744d39`:

| The document's claim | The code |
| --- | --- |
| a recorded history of one sample per simulation step | absent; `core/run_definition.py`'s `RunDefinition` is "A run, as the settings it was computed under and the states they imply" - `advance_to` and `record_change` are "the whole of what a run *is*" |
| a trace selects among recorded samples | `app/controller.py`'s `DrawnWindow` is "the states one frame draws, evaluated from the run's definition ... nothing else exists behind them" |

`DrawnWindow`'s own docstring states the replacement outright: "It replaces
`HistoryWindow`, and the difference is what `PL-2FM6` is: a window over
*recorded samples* asked which of them to draw and cost what the window
spanned, where this one is the answer itself."

**What is still true, and must not be lost in the edit.** The *keying*
argument in the same paragraphs survives intact and is load-bearing: a
compartment fraction asserts nothing without the substance it is a fraction
of, one trace binds to one substance-and-quantity pair, and a frame asking for
a substance the run is not of fails rather than drawing whichever it holds.
That reasoning is about `RecordedSeries` and `DrawnWindow` and applies
unchanged. Only the claim that a *store of per-step samples* sits behind them
is stale.

**Why it matters.** A reader of `docs/MODEL.md` is told the chart selects among
recorded samples, when the chart is drawn from states evaluated in closed form
from the run's definition. That is the difference `PL-P1Z3` wrote § "The
canonical evaluation rule" to make auditable, so the specification now
understates the guarantee it also states elsewhere - and a reader reconciling
the two has no way to tell which is current.

**Not fixed here.** Outside `PL-5328`'s `touches`, and an edit to the
authoritative model specification wants its own doc-sweep and
`tools/doc_check.py candidates` pass rather than riding a queue-hygiene commit.
