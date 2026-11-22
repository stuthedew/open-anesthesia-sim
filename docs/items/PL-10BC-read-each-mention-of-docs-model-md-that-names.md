---
id: PL-10BC
title: Read each mention of docs/MODEL.md that names no section, and re-point the ones that mean a requirement PL-CTXZ moved to docs/INTERFACE.md (640 mentions of the path remain in src/ and tests/ on 2026-11-11, with and without a section)
priority: P2
effort: M
status: ready
classes: defect, docs
feature: model-md-structure
touches: src/anesthesia_sim/app, src/anesthesia_sim/core/run_definition.py, tests, tools/contrast_check.py, docs/ARCHITECTURE.md, docs/machine-abstraction.md
deferred-from: v0.7.0 - a new problem: these mentions became wrong when #2109 (6446f927, 2026-11-13, PL-CTXZ) moved the interface sections out of docs/MODEL.md after the freeze, and PL-CTXZ is closed, so there is no open entry to pair it with
added: 2026-11-11
payoff: A contributor who follows a docstring to the specification it names finds the interface requirement it means, instead of a document that no longer states it.
---

**Problem.** Read each mention of docs/MODEL.md that names no section, and re-point the ones that mean a requirement PL-CTXZ moved to docs/INTERFACE.md (640 mentions of the path remain in src/ and tests/ on 2026-11-11, with and without a section)

**Found 2026-11-14**, in a review of the night's merges: these mentions name `docs/MODEL.md` for text that is now only in `docs/INTERFACE.md`. `git blame` dates each before #2109, so the move missed them. The document check does not see them, because it reads no `#` comment, no possessive form such as "`docs/MODEL.md`'s unconditional set", and no bare § whose document is named on the line before.

1. `docs/machine-abstraction.md:50`: § "Runtime controls" moved; § "Parameter provenance" did not.
2. `src/anesthesia_sim/app/formatting.py:461` (a comment): § "F_A/F_I as a displayed ratio".
3. `src/anesthesia_sim/app/preferences.py:151-153`: § "A cost at the reader's price".
4. `tests/unit/test_agent_cost.py:360-362` and `:456-458`: § "A cost at the reader's price".
5. `tests/integration/test_controller.py:3549-3552`: § "Halting on a marked crossing".
6. "`docs/MODEL.md`'s unconditional set" at `src/anesthesia_sim/app/unconditional_set.py:1`, `tests/unit/test_unconditional_set.py:1` and `docs/ARCHITECTURE.md:119`. `docs/MODEL.md` no longer mentions the set; it is in `docs/INTERFACE.md` § "Minimum displayed outputs".
7. The per-substance tier at `src/anesthesia_sim/app/run_view.py:521` and `src/anesthesia_sim/app/unconditional_set.py:214`, in the same section.
8. `tests/unit/test_chart_frame.py:1399`: "`docs/MODEL.md`'s measured table" is `docs/INTERFACE.md` § "What a chart library prints instead, measured".
9. `tests/reference/test_coupled_dynamics.py:1895`, an assertion message: "re-derive the measured figures in docs/MODEL.md". The figures are cited only in `docs/INTERFACE.md`.

The line numbers are from `e278a80`.

**Checked 2026-11-21**, by `PL-5FMC` (the check of `docs/INTERFACE.md` against the code), at `2452b9b4e`. These mentions of `docs/MODEL.md` mean a requirement that is now in `docs/INTERFACE.md`: the module docstring and two more places in `app/unconditional_set.py`; `required_reachable` and `required_kinds` in `app/view_registry.py`; `app/area_layout.py`; three places in `app/preferences.py` (§ "A cost at the reader's price"); `tests/unit/test_agent_cost.py`; `app/theme.py`; `tools/contrast_check.py`; `app/stylesheets.py`; the comment above `COMPARTMENT_TRACES` in `app/chart_frame.py`; and `DisplayState` in `core/run_definition.py`.

**Checked again 2026-11-22**, at `d4e8200c`. The fault is still there. `grep -n 'MODEL.md' src/anesthesia_sim/app/unconditional_set.py` still prints the module docstring's "`docs/MODEL.md`'s unconditional set", and `grep -c -i 'unconditional set' docs/MODEL.md` prints 0. The comment above the F_A/F_I axis limits in `app/formatting.py` still names `docs/MODEL.md` for the section on F_A/F_I as a displayed ratio, which is now a heading of `docs/INTERFACE.md` only. `src/` and `tests/` hold 610 mentions of `docs/MODEL.md` in 111 files, and 443 of those lines carry no section mark.

**Why it matters.** `docs/MODEL.md` and `docs/INTERFACE.md` are the two specifications a contributor reads before changing the code. A docstring that sends them to `docs/MODEL.md` for an interface requirement sends them to a document that no longer states it. They may then conclude that the requirement is gone, and remove a value that every Workspace must keep on screen, or change how a cost is priced, without seeing the rule that forbids it. The document check cannot catch these mentions, because it does not read `#` comments, possessive forms, or a § whose document is named on the line before.

**Done when.** Every mention of `docs/MODEL.md` in `src/`, `tests/`, `tools/contrast_check.py`, `docs/ARCHITECTURE.md` and `docs/machine-abstraction.md` that means a requirement now stated in `docs/INTERFACE.md` names `docs/INTERFACE.md` instead, with the section that states it. Each mention that still means `docs/MODEL.md` is left as it is.

**Generator check.** The misread fact is which document holds a section after `PL-CTXZ` (moving the interface sections out of `docs/MODEL.md`) moved it. No head's `misread:` line states it. The same fact was misread by `PL-CVTG` (done: items whose `touches` named the old document) and by `PL-GC7Z` (open: a comment citing a `docs/MODEL.md` note with no section mark). The mechanism the three share is that a citation written as a comment, a possessive or a bare § is invisible to the document check, so a move of a section strands it silently. That is a candidate generator, because `PL-48MX` and `PL-SY7G` (the later stages of splitting the two documents) will move more sections. It is reported to the coordinator rather than recorded here, since no open item yet holds the fix to the check.
