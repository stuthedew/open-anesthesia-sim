---
id: PL-27H0
title: docs/MODEL.md still specifies a per-step recorded sample store and a display operation that selects which recorded samples a trace draws, both of which PL-2FM6 deleted
priority: P1
effort: M
status: done
classes: safety, docs
feature: model-spec-accuracy
milestone: v0.4.26
touches: docs/MODEL.md
added: 2026-09-14
closed: 2026-09-14
pr: 582
verify: python3 tools/doc_check.py check && ! grep -qF 'Every point drawn at any width is still a recorded sample' docs/MODEL.md && ! grep -qF 'SimulationHistorySample' docs/MODEL.md
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

**Verified 2026-09-14 against `fb60a00`, and the sweep is wider than the two
places the brief above names.** `grep -rn
'RunHistory\|HistoryWindow\|SimulationHistorySample' src/` returns two hits and
neither is a store: `app/controller.py:234` names `HistoryWindow` only to say
`DrawnWindow` replaced it, and `app/formatting.py:24` names the deleted class by
mistake (`PL-4K9V`, the same sentence in the source docstring).
`core/run_definition.py:1` opens "A run held as the settings it was computed
under, rather than as samples of itself", and `core/simulation.py:20` records
that the simulation no longer keeps "samples at all (`PL-2FM6`)". So the store
is gone from the tree and `docs/MODEL.md` carries 19 occurrences of "recorded
sample" or "recorded history".

**The passages that rest on it**, by line, measured on `fb60a00`:

- `docs/MODEL.md:3560-3562` — § "Closed-form agreement test" defines itself as
  "the states derived from the run definition, at the instants the run recorded,
  must equal the recorded samples". There is no second record to equal. The
  tests that cite the section have already been re-pointed: `tests/unit/
  test_resume_at.py:185-196` compares the definition against a system stepped by
  `advance()`, not against a sample store.
- `docs/MODEL.md:3740-3744` — "**Both records are live in this release.** The
  recorded history remains, and the chart is still drawn from it ... Retiring the
  recorded half is a separate change". It landed; `PL-2FM6` is closed.
- `docs/MODEL.md:4356`, `:4359`, `:4372`, `:4397` — § "Interface boundary": the
  interface may "render the run's recorded history" and "select which recorded
  samples a plotted trace draws", followed by "**What a recorded sample is.**"
  and by the snapshot asymmetry argued against a recorded history that "is never
  stored, never compared against a later run".
- `docs/MODEL.md:4488`, `:4499-4500` — a reference "draws no recorded sample";
  a displayed ratio is a trace because "every point it draws is still computed
  from one recorded sample".
- `docs/MODEL.md:4998-5001` — "Every point drawn at any width is still a
  recorded sample, selected under the constraint 'Interface boundary' places on
  a plotted trace, so a wider window is a coarser *selection* of real samples
  and never a resampling".
- `docs/MODEL.md:5841` — "every `SimulationHistorySample` the chart is drawn
  from".
- `docs/MODEL.md:4478`, `:4537` — "changes no recorded sample" and "alters no
  recorded sample" as clauses bounding two view controls. These are vacuous
  rather than false, and are the cheapest part of the sweep.

**Why this is classed `safety` and not `docs` alone.** The two claims at
`:4998-5001` and `:4499-4500` are about the provenance of every point a learner
sees on the chart, not about an internal mechanism. `docs/MODEL.md` says a drawn
point is a recorded sample — a state the model actually stepped through — and
that a wider window is a coarser selection of real samples.
`app/chart_series.py:447-449` says the opposite and says it deliberately:
"**Every drawn point is a state of the run at the instant it is drawn at**,
evaluated from the run definition rather than selected from recorded samples
(`PL-2FM6`). Nothing between two drawn points is interpolated by this code."
`CLAUDE.md`'s safety-critical standard names provenance explicitly — "the
correct number with the wrong units, label, patient context, stale state, model
name/version, or provenance is still a safety failure" — and requires displayed
values to be "traceable to the exact model/version, inputs, units, and
transformations that produced them". A reviewer auditing a plotted point against
this specification is sent to a store that does not exist, and the numbers are
right the whole time, which is what makes it hard to notice. The § "Closed-form
agreement test" instance is the same failure one level up: the specification
states a verification guarantee in terms of an artifact that is gone.

**Done when.** `docs/MODEL.md` describes one record. Every passage listed above
states what the tree does — that a drawn point is the run's state at the instant
it is drawn at, evaluated in closed form from the run definition — and no
passage asserts a per-step store, a selection among stored samples, or a second
record to be held against the first. § "Closed-form agreement test" states what
it compares today. `SimulationHistorySample`, `RunHistory` and `HistoryWindow`
appear nowhere in the file. The keying argument under § "Interface boundary" —
that a compartment fraction asserts nothing without its substance, that one
trace binds to one substance-and-quantity pair, and that a frame asking for a
substance the run is not of fails — survives word for word against
`RecordedSeries` and `DrawnWindow`, and `python3 tools/doc_check.py check`
reports 0 errors.
