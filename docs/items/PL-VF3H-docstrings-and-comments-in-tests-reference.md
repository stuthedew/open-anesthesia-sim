---
id: PL-VF3H
title: Docstrings and comments in tests/reference/, tools/doc_check.py and src/ repeat nine statements that docs/MODEL.md corrected on 2026-11-21
status: untriaged
feature: model-spec-accuracy
added: 2026-11-21
---

**Problem.** Docstrings and comments in tests/reference/, tools/doc_check.py and src/ repeat nine statements that docs/MODEL.md corrected on 2026-11-21

**Found by.** `PL-RMNP`, the check of `docs/MODEL.md` against the code, on 2026-11-21. `PL-RMNP` corrected each statement in `docs/MODEL.md`. The copies below stayed, because a change under `tests/reference/` waits for the project owner's read and the others are in `src/` and `tools/`.

1. `tests/reference/test_late_washout_against_published_fits.py`, module docstring: the amplitudes sum to "0.912-0.937". The largest sum is 0.93645, sevoflurane's, so the range is 0.912 to 0.936. The docstring and the failure message of `test_the_published_coefficients_sum_below_one_at_discontinuation` repeat 0.937.
2. The same module docstring: "Between 8 and 13 hours" the open-circuit tail is a third to a half of the mean curve. That range, 0.34 to 0.46, is each cohort's lowest point. Over hours 8 to 13 the ratio runs from 0.34 to 0.66. The lowest point comes near hour 8 for desflurane and near hour 13 for the others.
3. `tests/reference/test_published_wash_in_and_elimination.py`, docstring of `test_early_wash_in_matches_published_human_measurement`: desflurane runs "0.034 to 0.042" above its published curve from 1 to 10 minutes. The 7.5-minute point is 0.032 above, so the range is 0.032 to 0.042.
4. The same file, two comments. "The numeric value is in the methods text and is not held here (`PL-ZDWL`)": `docs/MODEL.md` says that neither paper reports a ventilation, and the closed item `PL-ZDWL` found the same. "x1.10 is not used, because desflurane passes it": desflurane fails the gate at ×1.10, and `docs/MODEL.md` gives the right reason, that ×1.10 is too close to desflurane's edge at ×1.097.
5. `tests/reference/test_canonical_evaluation.py`, module docstring: the accumulators show "to six decimals of a litre", and the two bounds differ because "their headroom differs by four orders". `app/formatting.py` shows the three amounts to 0.1 L (`_RUN_TOTAL_LITRE_DECIMALS = 1`). What differs by about four orders is the measured difference, 8.0e-13 of an atmosphere against 3.1e-9 L.
6. `src/anesthesia_sim/core/governing_equations.py`, module docstring and `build_system_matrix`: the entries are written "in the order" `docs/MODEL.md` gives the equations. The code writes the venous balance before the tissue balances, and the delivery and exhaust rows belong to § "Conservation of agent mass".
7. `src/anesthesia_sim/app/dashboard_frame.py`, the comment above `USE_DISCLAIMER_TEXT`: each statement appears "on the readout section's heading row". The use disclaimer is drawn at the foot of the window.
8. `tools/doc_check.py`, docstring of `check_source_tiers`: a tier-only reading "passes all four of this project's data files". Five parameter files carry `sources`.
9. `tools/doc_check.py`, docstring of `check_untied_restatements`: it names `docs/MODEL.md` and `README.md` and leaves out `docs/INTERFACE.md`, which `PROVENANCE_DOCUMENTS` includes.

**Done when.** Each of the nine agrees with the code beside it and with `docs/MODEL.md`.
