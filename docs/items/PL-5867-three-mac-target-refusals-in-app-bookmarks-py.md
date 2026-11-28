---
id: PL-5867
title: Three MAC target refusals in app/bookmarks.py name a compartment by its code value, such as 'vessel_rich', and one quotes a repr; they reach the mark editor's notice verbatim through refused_setting_notice
priority: P3
effort: S
status: done
classes: defect
feature: replay-findings
touches: src/anesthesia_sim/app/bookmarks.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
closed: 2026-11-27
pr: 2342
filed-pr: 2291
payoff: a user whose mark is refused reads the compartment by its on-screen name, not a code value
tests: tests/unit/test_bookmarks.py::test_removing_a_target_that_is_not_there_names_its_compartment_as_the_legend_does, tests/unit/test_bookmarks.py::test_a_target_on_a_quantity_that_is_not_a_compartment_lists_the_compartments_by_name, tests/unit/test_bookmarks.py::test_a_reading_without_a_target_s_compartment_names_it_as_the_legend_does, tests/unit/test_run_series.py::test_every_compartment_has_one_on_screen_name_in_the_order_the_interface_lists_them, tests/unit/test_chart_frame.py::test_each_trace_is_named_as_the_one_record_of_compartment_names_names_it
---

**Problem.** Three MAC target refusals in app/bookmarks.py name a compartment by its code value, such as 'vessel_rich', and one quotes a repr; they reach the mark editor's notice verbatim through refused_setting_notice

**Found 2026-11-23** while closing `PL-8QFW` (the refused-setting banner named a setting by its field in the code). The mark editor shows a refused mark through `refused_setting_notice` (`SimulationView._apply_to_every_run`, `_remove_mark` and the add path), word for word. Three messages in `app/bookmarks.py` name a compartment by `RecordedQuantity.value`, which is a code value such as `vessel_rich` or `mixed_venous`: `MacTarget.__post_init__` ("given 'vessel_rich', which is not one of ..."), `BookmarkSet.without_mac_target` ("no MAC target stands at 0.8 ×MAC on the vessel_rich compartment, so there is none to remove") and `_require_readings` ("the before reading names no vessel_rich compartment"). The removal refusal is reached only when the Remove rows disagree with the run's marks, which the dashboard halts on first (`_marks_now`), so a user should rarely or never see it.

**Why it matters.** It is the same fault as `PL-8QFW` in a second notice: a user reads a code name where the screen labels the compartment in words.

**Done when.** Each refusal that can reach the mark editor names the compartment as the chart's legend names it, read from the one place that label is held, and a test pins the notice the editor shows. The approved-wording list records any changed string.

**Generator check.** An instance of the fault `PL-8QFW` fixed in the banner, found while closing it, in a second notice that `PL-8QFW` did not reach. One-off: no head states the fact, and the label home exists.

**Reproduced 2026-11-23.** `src/anesthesia_sim/app/bookmarks.py` on `main` builds all three messages from `target.quantity.value`.

**Done 2026-11-27.** `run_series.COMPARTMENT_NAMES` is now the one record of each compartment's on-screen name, and `chart_frame.COMPARTMENT_TRACES` reads its labels from it. The legend, the hover and the mark editor's list show the same names as before. `app/bookmarks.py` cannot read `chart_frame`, which imports `controller`, which imports `bookmarks`, so the record sits in `run_series`, which both already import. The three refusals now name the compartment from it: "no MAC target stands at 0.80 ×MAC on Vessel-rich, so there is none to remove", "the before reading holds no value for Mixed venous, ...", and a target on a quantity that is not a compartment lists the six by name and quotes no repr.

The wording follows NUREG-0700 Rev. 3 (O'Hara, Brookhaven National Laboratory for the U.S. Nuclear Regulatory Commission, July 2020; full text from https://www.osti.gov/servlets/purl/1644018, read 2026-11-27). Guideline 1.3.3-4, p. 1-39: "Labels should be worded consistently, so that the same item is given the same label whenever it appears." Guideline 2.7.1-3, p. 2-85: "System messages should use familiar terminology." The compartment's label is used as a name, as the legend writes it, so a user can match the message to the chart.

The repeated-target refusal can reach the mark editor too, and it printed the Python repr of the target's key. Both blind review passes of this pull request found it, so `PL-5HM5`, which recorded it, is fixed in the same pull request. Every refusal here now names a target as "0.80 ×MAC on Vessel-rich", with the height at the marks list's two decimals, from one function, `_stated_height`.

The readout panels hold a second copy of the names, and one differs ("Vessel-rich group"). `PL-GRC6` records it, because which name the compartment carries everywhere is a wording choice of its own.

Documents checked: `docs/INTERFACE.md` (no passage quotes these refusals; unchanged), `docs/ARCHITECTURE.md` (`run_series.py`'s entry does not list its tables; unchanged), `README.md`, `docs/MODEL.md`, `docs/VERIFICATION.md` and `docs/PARAMETERS.md` (none names these messages; unchanged).
