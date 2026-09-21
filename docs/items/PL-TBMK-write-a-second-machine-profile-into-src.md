---
id: PL-TBMK
title: Write a second machine profile into src/anesthesia_sim/data/machines/, so there is something to select between and PL-WZVZ's comparison has a second column
priority: P3
effort: M
status: blocked
classes: feature, anticipated
feature: machine-profile-framework
touches: src/anesthesia_sim/data/machines, docs/machine-survey.md, tests/unit
blocked-by: PL-QW19, PL-2FZ9
added: 2026-09-21
payoff: gives PL-WZVZ's comparison table a second column, which is the condition its Done when names and which no scheduled item delivers
---

**Problem.** Write a second machine profile into src/anesthesia_sim/data/machines/, so there is something to select between and PL-WZVZ's comparison has a second column

**Why it matters.** `src/anesthesia_sim/data/machines/` holds exactly one
profile, `reference_circle_system.json`. Every clause of `PL-WZVZ`'s
`Done when.` that names a *second* machine — "selecting between machines shows
the parameters that differ", "a comparison of two runs on different machines" —
is unreachable until this exists, and nothing schedules it: planned-milestone
item 40 ships a second profile *loadable and refused where inadmissible* with no
profile of its own, and planned-milestone item 1 keeps the interlock baseline.

**Filed so the condition is in a field rather than in prose** (`PL-0H5D`). Until
today `PL-WZVZ` recorded only its display-surface blockers, so closing those in
v0.6.0 would have reported it promotable — at `P1`, `safety`-classed, and
unbuildable. That false-ready already happened once on this item (`PL-8G48`,
2026-09-20).

**What blocks it.** `PL-QW19` first: `default_fresh_gas_flow_l_min` is a
required field no manufacturer publishes, so a real profile must invent an
unsourced number or cannot be written at all — and an invented number in a
machine profile is exactly what `CLAUDE.md`'s source-hierarchy rule refuses.
Then `PL-2FZ9`, without which a second profile is not reachable by a run: the
runtime ignores an extra file in that directory entirely.

**`feature`-classed, with `anticipated`.** The deliverable is a set of sourced
parameter values with provenance, held to `docs/MODEL.md` § "Source hierarchy".
`anticipated` because nothing displays a machine today, so nothing is wrong yet.

**Done when.** A second profile exists under
`src/anesthesia_sim/data/machines/`, every value in it traceable to a source
`docs/machine-survey.md` records at its stated tier, unknowns stored as unknown
rather than invented, and a run can be driven on it.
