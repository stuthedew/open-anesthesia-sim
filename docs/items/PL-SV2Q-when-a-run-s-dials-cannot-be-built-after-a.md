---
id: PL-SV2Q
title: When a run's dials cannot be built after a Reset or an agent change, the dial row and the delivered line keep the discarded run's setting: 'Delivered 8.00% (4.00 ×MAC)' beside '1 MAC desflurane = 6.0%'
priority: P1
effort: S
status: done
classes: safety, defect
feature: every-view-in-run-state-tests
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/run_presentation.py, tests/integration
added: 2026-11-11
closed: 2026-11-14
pr: 2125
payoff: the delivered concentration on screen is always the current run's, never a discarded run's setting under another agent's name
verify: grep -rq 'def test_a_halt_whose_dials_cannot_be_built_shows_no_earlier_setting' tests/
---

**Problem.** When a run's dials cannot be built after a Reset or an agent change, the dial row and the delivered line keep the discarded run's setting: 'Delivered 8.00% (4.00 ×MAC)' beside '1 MAC desflurane = 6.0%'

**Found by** the lifecycle review of `PL-RF2S`'s first pull request, on 2026-11-11. The fault is on `main` as well: the old halt wrote the same screen.

**Scenario, reproduced.** Sevoflurane at 8.00%, run to 10 minutes and paused. Every frame fails, and `setting_readouts` raises `ValueError("this control can offer no setting")`. The learner picks desflurane and confirms the new case, so the run holds desflurane at 6.0%. The panel then shows:

```
heading: Modelled concentrations: Desflurane
1 MAC: 1 MAC desflurane = 6.0%
delivered line: Delivered 8.00% (4.00 ×MAC)
cards: ('Simulated time', '—', ...), ('Circuit', '—%', '— ×MAC'), ...
dials: ('Delivered sevoflurane', '8.00%', '4.00 ×MAC', 800)
```

The 8.00% is the discarded run's setting, and 4.00 ×MAC was divided by sevoflurane's MAC. The delivered concentration is one of the values that must always be on screen (`UnconditionalValue.DELIVERED_CONCENTRATION`).

**Reach.** No shipped profile causes it. It needs a control that can offer no accepted setting (`PL-7CRY`), which only an injected refusal or a malformed machine profile produces. The repository's own scenario `_a_halt_after_an_agent_change_whose_dials_cannot_be_written` in `tests/integration/test_simulation_view.py` reaches the same state and leaves its settings group unchecked (`"settings": None`).

**Cause.** `RunView.show_presentation` writes neither the dials nor the delivered line when the presentation's dials are `NotBuilt`, so both keep what the last write left. `RunValues` and `withheld_values` in `app/run_presentation.py` cover the four compartment values and not the dials or the delivered line, so neither has a withheld form.

**Suggested fix.** Give the dials and the delivered line a withheld form, and write it whenever the dials cannot be built. `PL-RF2S`'s second pull request draws every View from one value, and is the natural place.

**Done when** a halt whose dials cannot be built shows no setting of any earlier run on the dial row or the delivered line, and the scenario above is a test that fails first.

**Why it matters.** The delivered concentration is one of the values that must always be on screen. Here it shows the discarded sevoflurane run's 8.00% and a MAC multiple divided by sevoflurane's MAC, beside a desflurane heading, so a learner reads another agent's setting as the current one.

**Generator check.** An instance of the fact that `PL-RF2S` states, and `PL-RF2S` is still open: a value from an earlier run stays wherever a write path does not reach. Here the path is a halt whose dials cannot be built. `PL-RF2S` is in flight on another branch, so adding this item to its `root-cause-of:` is left to that branch.
