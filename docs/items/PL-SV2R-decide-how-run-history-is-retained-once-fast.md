---
id: PL-SV2R
title: Decide how run history is retained once fast-forward makes runs days or weeks long
status: dropped
closed: 2026-09-04
reason: Duplicate of PL-011 (bound the controller's concentration history), written in the same session without reading it first. PL-011 already holds the retention question, the owner's 30-day cap from 2026-08-25, and the link to the scenario-branching work; this item's measurements, sizing and prior art have been folded into it, and the correctness constraints with them. Nothing is lost by closing this one.
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/chart_downsampling.py
added: 2026-09-04
---

**Problem.** The project owner wants a fast simulation speed, reaching
simulated days and potentially weeks (2026-09-04). `SimulationController`
appends one `SimulationHistorySample` per step and never truncates, and
`core.uptake_system.MAXIMUM_SIMULATION_STEP_S` is 0.1 s with `advance()`
*raising* above it — so the step count is a hard function of simulated time
and cannot be reduced by taking coarser steps. The operator split's
applicability domain sets it, which makes this a modelling constraint rather
than a tuning knob.

Measured 2026-09-04: `advance()` costs 19 us per step, and one
`SimulationHistorySample` (frozen, slotted, seven floats) is about 264 bytes
including its float objects.

| Simulated | Steps | History RAM | Fast-forward compute |
| ---: | ---: | ---: | ---: |
| 1 hour | 36 000 | 0.01 GB | 1 s |
| 1 day | 864 000 | 0.23 GB | 16 s |
| 1 week | 6 048 000 | 1.60 GB | 115 s |

**So compute is not the obstacle and memory is.** Two minutes of single-core
work buys a week of simulated time, which is a usable interaction. 1.6 GB of
retained history for it is not, and it is spent on samples nothing will ever
draw: the chart shows at most a few hundred points of a bounded window.

**Why it matters.** It decides whether fast-forward is a feature or a crash,
and it is cheaper to decide before the feature is built than to retrofit. It
is also a correctness question and not only a capacity one: whatever is
discarded is discarded permanently, so the consolidation rule decides what a
learner can still see about the part of the run that has scrolled away. A
rule that drops a transient makes the record show a run the simulation did
not produce, which is the failure `chart_downsampling.py` already exists to
prevent at draw time.

**Prior art.** This is a solved problem with an established shape:
**multi-resolution retention**. Keep recent data at full resolution and older
data progressively consolidated, with the consolidation preserving extremes
rather than averaging them away.

- **RRDtool** has done exactly this since 1999: round-robin archives at
  several resolutions, each with a consolidation function (min, max, average,
  last), giving fixed total storage regardless of run length.
  <https://oss.oetiker.ch/rrdtool/> — *cited from general knowledge; verify
  the archive and consolidation semantics against the documentation before
  relying on the detail.*
- **OM3**, "An Ordered Multi-level Min-Max Representation for Interactive
  Progressive Visualization of Time Series", Proc. ACM Management of Data
  (SIGMOD) 2023, is the current academic form of the same idea.
- **M4** (Jugel et al., PVLDB 7(10):797-808, 2014) is the matching *read*
  rule and the one already implemented here: one bucket per pixel column,
  keeping min, max, first and last, with a proof that the rendering matches
  plotting every point.

The fit is good: `select_envelope_indices` already performs min/max envelope
consolidation and already anchors its buckets to absolute sample index
(PL-Q197), which is the same anchoring a tiered store needs. The read side is
largely built.

**Open questions for the design round.**

1. What full-resolution window is kept — the visible window, or a fixed
   recent span such as an hour?
2. What are the tiers, and does the consolidated record keep min and max per
   bucket (so a transient survives) or a single value?
3. Is consolidated history distinguishable from recorded history where it is
   displayed? A drawn point that is a bucket extreme rather than a recorded
   sample is a different claim, and `chart_downsampling.py`'s guarantee that
   "a drawn point is always a recorded sample" would no longer hold
   unqualified.
4. Does anything besides the chart read history — export, agent accounting,
   a future scrub control (PL-DR1Z)? Each constrains what may be discarded.
5. Does fast-forward yield to the event loop? 19 us a step means a naive
   tight loop holds the asyncio loop for as long as the fast-forward runs,
   which would reproduce PL-Q197's dead-input symptom from a different cause.

**Depends on.** `PL-0VM7` (snapshot copies the whole history every frame)
should land first: it establishes the windowed read interface a tiered store
plugs into, so this becomes additive rather than a rewrite.

**Done when.** The retention design is recorded with its reasoning, the
consolidation rule is stated in terms of what a learner can still see, and
the milestone is scoped in `ROADMAP.md` with items.
