---
id: PL-01GY
title: The refused-Reset banner's exit says to change the setting the refusal names, and a tissue-flow mismatch names the cardiac output, which since PL-HQF5 repairs nothing because a new output scales every flow by the same factor; the mismatch is now reachable only by a perfusion fraction written past its guard
status: untriaged
added: 2026-10-18
---

**Problem.** The refused-Reset banner's exit says to change the setting the refusal names, and a tissue-flow mismatch names the cardiac output, which since PL-HQF5 repairs nothing because a new output scales every flow by the same factor; the mismatch is now reachable only by a perfusion fraction written past its guard

The rationale comment above `REFUSED_RESET_REPAIR_TEXT` in
`src/anesthesia_sim/app/dashboard_frame.py`, and the `refused_reset_exit`
docstring, still say the named setting's dial rebuilds the record. Change
them with the banner text.
