---
id: PL-5V5F
title: Fresh gas flow and alveolar ventilation are both 4.0 L/min in the shipped defaults and in test_dashboard_frame's _snapshot fixture, so swapping the two settings in dashboard_frame.setting_readouts passes the whole unit tier and building settings()'s ventilation from the fresh gas flow passes every test
priority: P2
effort: S
status: ready
classes: test
feature: tests-detect-wrong-values
touches: tests/unit/test_dashboard_frame.py, tests/integration/test_controller.py
added: 2026-10-17
payoff: a readout that shows the fresh gas flow under the ventilation label, or the reverse, fails a test instead of passing on two equal 4.0 L/min values
verify: grep -q 'def test_the_snapshot_fixture_settings_are_all_distinct' tests/unit/test_dashboard_frame.py
---

**Problem.** Fresh gas flow and alveolar ventilation are both 4.0 L/min in the shipped defaults and in test_dashboard_frame's _snapshot fixture, so swapping the two settings in dashboard_frame.setting_readouts passes the whole unit tier and building settings()'s ventilation from the fresh gas flow passes every test

**Severity: medium.** A swap would show a mislabelled displayed setting, and
the unit tier cannot fail on it. Audit finding ORC-1 (unit tier), confirmed by
the adversarial verifier.

**Evidence.** `default_fresh_gas_flow_l_min` is 4.0 in
`src/anesthesia_sim/data/machines/reference_circle_system.json`, and
`default_alveolar_ventilation_l_min` is 4.0 in
`src/anesthesia_sim/data/patients/reference_adult.json`. In
`tests/unit/test_dashboard_frame.py`, `_snapshot` hard-codes
`FreshGasFlow(4.0)` and `AlveolarVentilation(4.0)`, and its signature has no
parameter to override either. Both readout assertions, in
`test_refresh_view_formats_every_concentration_metric` and
`test_slider_drag_labels_match_the_readouts_beside_them`, expect "4.0 L/min"
for both settings.

- Probe P2 swapped the two values in the flows dict inside
  `setting_readouts` (`src/anesthesia_sim/app/dashboard_frame.py`). mypy
  reported success. `test_dashboard_frame.py`, `test_control_timeline.py` and
  `test_chart_frame.py` all passed, as did all 1876 simulator unit tests.
  Exactly 6 Qt tests in `tests/integration/test_simulation_view.py` failed:
  slider forwarding for both flows, a dragged slider, two halt tests and two
  run views.
- Probe P7 built `controller.settings()`'s `alveolar_ventilation_l_min` from
  `circuit.fresh_gas_flow_l_min`. All 1876 unit tests and all 482 integration
  tests passed. Only mypy refused it, with an `arg-type` error.

`test_settings_are_read_of_a_run_whose_snapshot_refuses` in
`tests/integration/test_controller.py` sets the fresh gas flow to 4.0, the
same as the ventilation default, and compares `settings()` with the snapshot.
`test_a_drag_that_halts_the_run_leaves_its_label_on_the_dial` in
`test_simulation_view.py` drags it to 4.0 as well. These are the only tests
that call `controller.settings()`. `RunSettings` has no run-time type check,
so only mypy tells the two fields apart.

A second instance is likely but was not probed. `_snapshot` also sets
`delivered_concentration_percent=Percent(8.0)`, equal to sevoflurane's 8.0%
vaporizer maximum. A swap of the dial and the maximum in `setting_readouts`
would probably pass the unit tier too.

**Why it matters.** A readout that shows ventilation's number under the
fresh-gas-flow label, or the reverse, is a mislabelled displayed setting.
`settings()` writes the dials on the halt path (`RunView.present_halt`), where
only mypy stands between the two values. A future route typed as plain
`float`, such as a control-timeline label or an export, would have no
protection at all.

**Where.** `tests/unit/test_dashboard_frame.py` (`_snapshot` and the two
tests above); `tests/integration/test_controller.py`;
`src/anesthesia_sim/app/dashboard_frame.py` (`setting_readouts`);
`src/anesthesia_sim/app/controller.py` (`settings`).

**Recommended fix.** Give `_snapshot` settings that all differ from each other,
for example a fresh gas flow of 3.0, ventilation 5.5, cardiac output 6.5 and a
dial other than the 8.0 maximum. Update the literal readouts to match. In
`test_settings_are_read_of_a_run_whose_snapshot_refuses`, set the fresh gas
flow to 6.0 and assert `settings().alveolar_ventilation_l_min == 4.0` and
`settings().fresh_gas_flow_l_min == 6.0` as literals. Optionally, have the
fixture assert that its settings are distinct, so the problem cannot come back
unnoticed.

**Done when.** Probes P2 and P7 each fail a unit or integration test, and the
fixture's dial differs from its vaporizer maximum.

**Related.** `PL-HWNG` (ready) is the same class, a fixture value equal to a
default, in `_two_change_run`. It is not extended here because its done-when
is about that helper and the ceiling measured on it. `PL-H8QP` (done) was the
earlier case of this class for the core defaults.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.
