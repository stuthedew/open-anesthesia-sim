---
id: PL-1M5B
title: PL-W3DD's Where claims chart_downsampling.py consumes the sample accessors, but that module is generic over SampleT and imports nothing from controller.py
priority: P3
effort: S
status: done
classes: docs
milestone: v0.4.0
touches: docs/items/PL-W3DD-key-simulationhistorysample-by-substance-rather.md
added: 2026-09-03
closed: 2026-09-05
pr: 343
verify: python3 tools/doc_check.py check && grep -q 'is \*not\* affected' docs/items/PL-W3DD-key-simulationhistorysample-by-substance-rather.md
---

**Problem.** `PL-W3DD`'s "Where" section names
`src/anesthesia_sim/app/chart_downsampling.py` among the call sites that consume
`SimulationHistorySample` through its named accessors, and would therefore need
changing when the record is re-keyed by substance.

It does not. `chart_downsampling.py` is generic over a `SampleT` type variable
and returns *indices into a caller-supplied sequence*; its own module docstring
states that it "performs no unit conversion, no interpolation, and no invention
of values", and it imports nothing from `app/controller.py`. Re-keying the
record cannot reach it.

**Why it matters.** Small, but it inflates an `M` item's stated surface with a
module that is deliberately decoupled, and the decoupling is a design property
worth not obscuring: the reason `chart_downsampling.py` is generic is so that a
change to what a sample *holds* cannot reach the logic deciding which samples
are *drawn*. A brief that lists it as a consumer says the opposite.

**Where.** `docs/items/PL-W3DD-*.md` § "Where";
`src/anesthesia_sim/app/chart_downsampling.py` (module docstring and the
`SampleT` signature).

**Amended 2026-09-03, after `PL-WB0X` merged (#263).** There is now a module
that genuinely does consume the sample through its accessors -
`app/chart_series.py:76-96`, six free functions each returning one field - and
`PL-W3DD`'s note names it. That is the module the "Where" was reaching for
before it existed. `chart_downsampling.py` remains generic over `SampleT` and
remains wrongly listed, so this item still stands; it is now a one-word swap
rather than a deletion.

**Done when.** `PL-W3DD`'s "Where" no longer names `chart_downsampling.py`, or
names it explicitly as unaffected and says why.

**Closed 2026-09-05 on the second branch, alongside `PL-W3DD` itself.** The
"Where" now says the module is not affected and gives the reason - generic
over `SampleT`, returns indices into a caller-supplied sequence, imports
nothing from `app/controller.py` - which is worth more than the deletion: a
reader who wonders why a downsampling module is absent from a re-keying item
finds the answer instead of re-deriving it.

The `verify:` command was rewritten as this item was started, because it had
been written for the *deletion* branch only and would have failed the branch
this item's own "Done when" allows. It now greps for the sentence that states
the exemption, which is absent from `origin/main` and present after the work -
the same specification, pointed at the outcome that was actually taken.

**Found.** Session auditing which open items the v0.4.1 `core/` pass would
invalidate, 2026-09-03.
