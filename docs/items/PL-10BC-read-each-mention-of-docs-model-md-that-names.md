---
id: PL-10BC
title: Read each mention of docs/MODEL.md that names no section, and re-point the ones that mean a requirement PL-CTXZ moved to docs/INTERFACE.md (640 mentions of the path remain in src/ and tests/ on 2026-11-11, with and without a section)
status: untriaged
feature: model-md-structure
added: 2026-11-11
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
