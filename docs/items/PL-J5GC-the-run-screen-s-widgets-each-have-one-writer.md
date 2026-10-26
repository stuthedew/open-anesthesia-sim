---
id: PL-J5GC
title: The run screen's widgets each have one writer since PL-X7D5 and PL-WM5P, but nothing requires values shown together to come from one state, so a label, divisor or verdict can come from a different state than the value beside it: three members filed after PL-WM5P closed
priority: P1
effort: M
status: ready
classes: defect, safety
feature: defect-review-2026-10
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/controller.py, tests/integration/test_simulation_view.py
deferred-from: v0.7.0 - recorded as a generator head by PL-R4Y2's defect review on 2026-10-25; each member's safety finding was filed and placed by its own triage, and this head's work is the structure that stops the next one
added: 2026-10-25
payoff: a value and its divisor, setting or verdict are never shown from two different states
verify: grep -q 'def test_every_value_and_its_qualifiers_on_screen_come_from_one_state' tests/integration/test_simulation_view.py
root-cause-of: PL-6RJ0, PL-3B34, PL-HF4B
generator: live - three members were filed against main after PL-WM5P's fix merged, and its guard compares each widget with itself rather than a group with each other
misread: Which widgets state a run's current state, and that each is restated on every path that changes it
---

**Problem.** The run screen's widgets each have one writer since PL-X7D5 and PL-WM5P, but nothing requires values shown together to come from one state, so a label, divisor or verdict can come from a different state than the value beside it: three members filed after PL-WM5P closed

**Evidence.** Found on 2026-10-25 by asking the generator question of the product defects filed since 2026-10-23. `PL-WM5P` merged at 05:44 UTC on 2026-10-25 (`#1779`), giving every run-state surface one writer. The three members below were filed at 21:59 UTC the same day, each checked against `main` after that merge:

- `PL-6RJ0`: `RunView._write_settings` writes the "1 MAC sevoflurane = 2.0%" line from the current settings, on the halt path too. The readout cards whose ×MAC values it divides are written only in `refresh`, from the last drawn frame. After a halt that follows an agent change, the line names the new agent above the old agent's multiples.
- `PL-3B34`: a dial moved on a halted run is applied and recorded at the halt instant, so the settings readout shows a setting that no step ran under, beside concentrations computed under the previous one.
- `PL-HF4B`: a failed step is rolled back, so the accounting panel reads the restored "Valid" state under a banner that quotes the failed step's totals.

**The mechanism.** `PL-X7D5` and `PL-WM5P` made the rule "each widget has one writer", and their guard checks that a halted screen reads like a drawn one. Both hold here. What fails is a different rule: values shown together must come from one state. A label, a divisor or a verdict written from the current settings, the restored state or the failed step sits beside a value written from the last drawn frame. The guard compares each widget with itself across two screens, so it cannot see two widgets on one screen that disagree.

**Why it matters.** The 1 MAC line is the divisor of every ×MAC number in its row, and the settings readout is the context a learner reads a concentration under. A correct number under the wrong divisor or setting is the presentation failure `CLAUDE.md`'s safety-critical standard names.

**Done when.** Each group of widgets that qualifies one value is written from one state in one call: the readout cards with their 1 MAC line, the settings with the concentrations they produced, and the accounting verdict with the totals it judges. `tests/integration/test_simulation_view.py` has `test_every_value_and_its_qualifiers_on_screen_come_from_one_state`, a guard that fails on a group whose members come from two states. `PL-6RJ0`, `PL-3B34` and `PL-HF4B` close under it, or each says why it stays.

**Generator check.** This item is the head, as three post-close instances of `PL-X7D5`'s fact. Each member records `reenters: PL-X7D5`.
