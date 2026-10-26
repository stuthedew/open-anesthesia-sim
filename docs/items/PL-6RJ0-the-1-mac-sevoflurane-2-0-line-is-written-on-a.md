---
id: PL-6RJ0
title: The "1 MAC sevoflurane = 2.0%" line is written on a different path from the readout cards whose ×MAC values it divides: a halt after an agent change writes the new agent's 1 MAC above cards still holding the old agent's multiples, and a raise from setting_readouts would leave the old 1 MAC above freshly written cards
priority: P1
effort: S
status: done
classes: defect, ux, safety
feature: replay-findings
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py
added: 2026-10-25
closed: 2026-10-26
pr: 1840
payoff: the 1 MAC line always states the divisor of the ×MAC numbers beside it, including while a halt is shown
verify: grep -q 'def test_a_halt_after_an_agent_change_shows_no_mac_multiple_beside_another_agent_s_1_mac' tests/integration/test_simulation_view.py
reenters: PL-X7D5
---

**Problem.** `RunView._write_settings` writes `_one_mac_text` (`app/run_view.py`). It runs from `_write_statement`, and so from `present_halt` as well. The readout cards are written only in `refresh`. After an agent change whose first frame fails, the heading reads "1 MAC desflurane = 6.0%". The cards beside it still show the last frame's sevoflurane values, divided by 2.0%. Separately, `_write_settings` calls `setting_readouts` before it writes the line. A raise there would leave the previous agent's 1 MAC above cards that `refresh` has just rewritten. No shipped agent triggers that raise today.

**Why it matters.** The 1 MAC line exists to state the divisor of every ×MAC number in the row. While the halt is shown, it states the wrong one. The halt banner says the readouts are the last frame's. It does not say that the 1 MAC line has moved on to another agent. Writing the line in `refresh`, from the snapshot that `readouts()` divides by, fixes both paths. This is a stale label on a clinical value, reachable only once another fault has halted the run.

**Done when.** The 1 MAC line is written from the same snapshot as the readout cards it divides, in `refresh`, so after a halt that follows an agent change, or a raise from `setting_readouts`, the line and the cards name the same agent. `tests/integration/test_simulation_view.py` has `test_the_one_mac_line_and_the_cards_name_the_same_agent_after_a_halt`.

**Found by.** `PL-TBQS` reviewer replay on #1585, findings r03 F1 and r06 F2, plus `PL-ZWXD`'s fourth #1585 entry. Checked against main on 2026-10-25 by reading `refresh`, `_write_statement`, `present_halt` and `_write_settings`, and `test_a_halt_after_an_agent_change_names_one_agent` (`tests/integration/test_simulation_view.py`), which does not check the 1 MAC line against the cards.

**Route revised 2026-10-26, after the blind review.** The first fix wrote the 1 MAC line in `refresh`, with the cards. Both blind review passes found that this moved the mismatch rather than removing it. On the same halt, the delivered line and the substance heading are written from the record and name the new agent, so the line then contradicted the delivered ×MAC beside it. And a halt on a run's first frame left the line blank, although it is an unconditional value. So the line is now written by `_write_statement` on both paths, from the record, and before the dials, so a raise from `setting_readouts` cannot leave the old agent's 1 MAC on screen. When a halt follows an agent change, so that the cards were divided by another agent's MAC, `present_halt` replaces each card's ×MAC number with "— ×MAC" (`WITHHELD_MAC_MULTIPLE_TEXT`) until the next frame. Every ×MAC number on screen is then divided by the 1 MAC that the line states. The test is now `test_a_halt_after_an_agent_change_shows_no_mac_multiple_beside_another_agent_s_1_mac`, with `test_a_halt_on_the_first_frame_still_states_the_1_mac_line` beside it.
