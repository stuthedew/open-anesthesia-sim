---
paths:
  - "/src/anesthesia_sim/app/**"
---

# No simulation calculation in a UI callback

Where a callback under `app/` touches the model, it does one of two things.
It reads a snapshot from `core/`, through the controller, and draws it; or it
forwards what the reader set to a controller setter. It computes no model
quantity: no concentration, MAC multiple, flow, volume, time constant or
rate, and no third value made from two the snapshot already holds. If a
number would need `docs/MODEL.md` to explain it, `core/` computes it and the
interface reads it.

**Why.** A value computed in a slot has no test of its own, no provenance and
no model version, and it reads whatever the widgets hold at the moment they
fire. `CLAUDE.md`'s safety-critical standard requires every displayed
clinical value to be traceable to the model, the inputs, the units and the
transformations that produced it, and a callback records none of those.

**Where the line sits.** `docs/ARCHITECTURE.md` § "Layering" draws it: `app/`
never performs a physiological or unit calculation itself. A presentation
transformation is allowed, and it lives in a module of its own that loads no
toolkit, so that it is tested: `app/formatting.py` turns a fraction into the
percent and the multiple of 1 MAC a reader sees, at the precision
`docs/MODEL.md` § "Displayed precision" derives.

**What is checked, and what this rule carries.** `tools/import_boundary_check.py`
keeps the toolkit out of `core/` and keeps `core/` from importing `app/`, so
the dependency runs one way. Nothing checks what a callback computes, because
whether an expression is a simulation calculation is a judgment, and this rule
is that half. The sentence was a bullet in `CLAUDE.md` § "Architecture and
development discipline" from 2026-08-22 until `PL-ZYHX` moved it here (project
owner, 2026-10-03, ratified, over leaving it resident): a callback is written
only with a file under `app/` open, so the rule loads at that moment and at no
other. `docs/resident-instructions.md` § "What was routed out" is the record.
