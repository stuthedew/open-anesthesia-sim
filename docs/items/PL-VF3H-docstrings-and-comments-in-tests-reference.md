---
id: PL-VF3H
title: Docstrings and comments in tests/reference/, tools/doc_check.py and src/ repeat nine statements that docs/MODEL.md corrected on 2026-11-21
priority: P2
effort: S
status: ready
classes: defect
feature: model-spec-accuracy
touches: src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/app/dashboard_frame.py, tools/doc_check.py
deferred-from: v0.7.0 - captured after the freeze by the check of docs/MODEL.md against the code; it changes no displayed value, and it is not safety or science
added: 2026-11-21
payoff: four docstrings and comments in the model code, the dashboard and the document checker say what the code beside them does
---

**Problem.** Docstrings and comments in tests/reference/, tools/doc_check.py and src/ repeat nine statements that docs/MODEL.md corrected on 2026-11-21

**Why it matters.** A developer reads a docstring before the document. Each of these states something that the code beside it, or `docs/MODEL.md`, contradicts.

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. `PL-RMNP` corrected each statement in `docs/MODEL.md`. The copies below stayed, because a change under `tests/reference/` waits for the project owner's read and the others are in `src/` and `tools/`.

[superseded 2026-11-21: entries 1 to 5, the five under `tests/reference/`, moved to `PL-MYK0` (the same statements in three published-data tests), which waits on `PL-SZ6G` (a run's time as a whole number of seconds). Entries 6 to 9 keep their numbers.]

6. `src/anesthesia_sim/core/governing_equations.py`, module docstring and `build_system_matrix`: the entries are written "in the order" `docs/MODEL.md` gives the equations. The code writes the venous balance before the tissue balances, and the delivery and exhaust rows belong to § "Conservation of agent mass".
7. `src/anesthesia_sim/app/dashboard_frame.py`, the comment above `USE_DISCLAIMER_TEXT`: each statement appears "on the readout section's heading row". The use disclaimer is drawn at the foot of the window.
8. `tools/doc_check.py`, docstring of `check_source_tiers`: a tier-only reading "passes all four of this project's data files". Five parameter files carry `sources`.
9. `tools/doc_check.py`, docstring of `check_untied_restatements`: it names `docs/MODEL.md` and `README.md` and leaves out `docs/INTERFACE.md`, which `PROVENANCE_DOCUMENTS` includes.

**Done when.** Each of entries 6 to 9 agrees with the code beside it and with `docs/MODEL.md`.

**Generator check.** Filed by `PL-RMNP` (the check of `docs/MODEL.md` against the code), a sweep that the owner asked for. The fact it misreads is whether a `docs/MODEL.md` sentence about what the model computes matches what it computes, which the head `PL-B6YV` (a document sentence about what the model computes, checked against the code) already states. It is counted under the sweep and is not a new head.
