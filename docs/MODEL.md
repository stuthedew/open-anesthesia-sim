# Volatile-agent patient uptake and distribution model

## Status

This document specifies the scientific model that the simulator has implemented
since v0.1.0. Its equations and compartment structure have not changed since
then, and every supported agent shares them.

**This document names no current release.** The version table in `ROADMAP.md`
records it. A statement here that needs a version says what has been true
*since* that version.

Release v0.0.2 modelled an ideal breathing circuit's wash-in and washout with no
patient, checked against exact formulas. Its reference tests are unchanged
(§ "Preserved circuit reference tests"). v0.1.0 extends it along this path:

```text
delivered agent
        ↓
breathing circuit
        ↓
alveolar gas ⇄ blood (perfusion-limited, no separate arterial compartment)
        ↓
vessel-rich group / muscle / fat
        ↓
venous blood
        ↓
alveolar gas
```

v0.1.0 is the first sevoflurane model with a patient, the “Sevo works”
milestone.

This is an educational model. It is not a clinical prediction, dosing tool, patient monitor, or medical device.

## Intended use, and the safety class this project holds itself to

The medical-device standards ISO 14971 (risk management) and IEC 62304
(software) judge every hazard and every software safety class against what the
product is intended for. This section states that intended use.

### Intended use

This is a teaching simulator for volatile-agent uptake and distribution. It is
intended for anesthesia clinicians, trainees, and students. It helps them
build intuition about how agent concentration moves between the breathing
circuit, alveolar gas, blood, and the tissue groups, under management that the
learner chooses. In particular, it makes visible the compartments that no
clinical monitor displays: vessel-rich, muscle, fat, and mixed venous.

**It is not intended for use with an identifiable patient's data.** It is meant
to be run on hypothetical or illustrative parameters. It is not intended for
entering, importing, or reproducing an identifiable patient's parameter values,
or for informing the management of a specific patient.

The boundary is drawn at the *data*, not at physical nearness to a patient. A
simulator open on a workstation while a case runs is ordinary teaching and
carries no hazard of its own. A run built from a particular patient's weight,
age, and cardiac output is a prediction about that patient, whatever the
window is labelled. The patient-factor work planned in `ROADMAP.md` will make
such runs possible.

### Software safety classification: Class C, for the whole application

IEC 62304 § 4.3 assigns a software safety class from the severity of the harm
that a software failure could contribute to. **Class A** applies where no
injury or damage to health is possible, **Class B** where injury is possible
but not serious, and **Class C** where death or serious injury is possible.
Annex B.4.3 makes the class depend on severity alone. Where software sits in a
sequence of events leading to a hazardous situation, the probability of its
failure is **set to 1**, not estimated. So "this would rarely be wrong" is not
an argument for a lower class.

This project assigns **Class C to the whole application**, the interface layer
included, for three reasons:

- A lower class saves no work. Class A excuses low-risk software from detailed
  design, unit verification, and integration testing. This project checks all
  its code the same way, so nothing would be excused.
- Class A asserts that *no injury is possible*, and the interface layer cannot
  claim that. The correct number with the wrong units, label, patient context,
  stale state, or model version is still a safety failure. The interface also
  carries several safety features: the distinction between a halted and a
  paused run, the displayed-precision rule, the ISO 5360 agent colours, and
  the extreme-preserving decimation.
- A split would not hold, because code that looks cosmetic carries clinical
  meaning. The chart's frame (`app/chart_frame.py`) decides what a chart line
  claims about a run. The styling file (`app/theme.py`) holds the colours that
  identify each agent.

A split would pay off only where the exempted part is large, genuinely
non-clinical, and costly to verify. None of those holds now.

### This is an engineering bar, not a regulatory status

The class is adopted as an engineering standard, as the accessibility standard
WCAG 2.2 AA is (§ "Color contrast, and the standard this interface is held to").
Nothing here claims conformance to IEC 62304, to a quality management system, or
to any regulatory status. Writing the class down gives a reviewer a stated bar
for the code.

The class does not settle device status. FDA publishes examples of software
functions that are *not* medical devices. They include software intended for
health care professionals as educational tools for medical training. One
worked example is "games that simulate various cardiac arrest scenarios to
train health professionals in advanced cardiopulmonary resuscitation (CPR)
skills" ([FDA, Examples of Software
Functions That Are NOT Medical Devices](https://www.fda.gov/medical-devices/device-software-functions-including-mobile-medical-applications/examples-software-functions-are-not-medical-devices),
and the guidance "Policy for Device Software Functions and Mobile Medical
Applications"). That exclusion depends on intended use, not on which
physiologic parameters the software accepts: the software must not support a
health professional's assessment of a *specific patient*. That is why the
intended-use boundary above is drawn at a specific patient's data.

ISO 14971:2019, the risk-management standard for medical devices, defines
**reasonably foreseeable misuse**, and its clause 5.2 requires documenting that
misuse. Using this simulator outside the intended use above is such misuse. The
hazard table in the next section has a row for it. § "What keeps a real
patient's data out of a run" names the two safeguards against it and the tests
that enforce them.

**Sources for this section.** IEC 62304 and ISO 14971 are published standards
and are not open access. The clause structure, the three class definitions,
and Annex B.4.3's probability rule were read from secondary summaries, not from
the standards' own text. The FDA material was read at the source. A reviewer
revising this section should check the standards directly. The conclusion,
Class C for the whole application, does not depend on their wording, but the
clause numbers cited here do.

## Reasonably foreseeable misuse, and the hazards the presentation carries

For each way a reader could be misled, this section says what prevents it and
which test checks that safeguard. The rest of this document argues forward from
each decision, which finds the mistakes one thought to look for. Working back
from each way to be misled finds the others.

**Every row names the test that enforces it, or says plainly that it has
none.** A check fails when a test named anywhere in this document matches no
existing test, so the right-hand column cannot list tests that are gone. A
reviewer still has to judge whether each test is any good.

| A reader could be misled into | What stops it | Held by |
| --- | --- | --- |
| reading a run as a prediction for a real patient whose data was entered into it | the use statement, which is the disclaimer at the foot of the window, stays in view. The simulated patient is always the built-in reference adult. Cardiac output and ventilation are teaching controls, and a learner can set either one to a value measured in a patient. Only the use statement stops a learner reading that run as a prediction for that patient (§ "What keeps a real patient's data out of a run") | `test_the_educational_disclaimer_says_what_the_tool_is_not`, `test_the_dashboard_carries_the_educational_disclaimer`, `test_the_region_and_the_use_disclaimer_stay_in_the_viewport`, `test_every_run_simulates_the_shipped_reference_adult` |
| reading a correct concentration as belonging to a different agent | agent colour is never the only cue. The agent name is always visible in every top-level window, within the limit stated in § "Minimum displayed outputs" -> "What this list requires once the layout is the reader's". `tools/agent_identity_check.py` checks the ISO 5360 colours in `src/anesthesia_sim/app/theme.py` and the text colour that stays readable on each | `test_agent_dropdown_options_pair_every_color_with_the_agent_name`, `test_every_agent_has_render_objects_in_its_own_identification_color`, `test_the_agent_name_stays_legible_while_the_run_disables_the_selector` |
| reading a run halted by a failure as one the user paused | a halt has its own status words, and the two failure modes have different words. The status word, the transport controls and the banner are set from the run's status alone, never from a compartment value. So a run still shows as stopped, and does not offer Pause, even when its own snapshot refuses a value. A banner written before any frame of the stopped run was drawn says so, instead of claiming that a step was rolled back | `test_refresh_view_reports_a_failed_run_as_stopped_not_paused`, `test_refresh_view_reports_the_supported_run_length_as_stopped_not_failed`, `test_a_halt_is_shown_when_the_snapshot_itself_is_refused`, `test_a_halt_is_stated_from_the_run_status_alone`, `test_a_halt_no_frame_was_drawn_for_is_worded_as_one_rather_than_as_a_failed_step` |
| reading a run that a mark stopped as one the learner paused, while two runs are compared | it reads "Paused — stopped on your mark". While two runs are compared, the branch control hides its own "stopped on your mark", so this status word is the only cue. A failure, or reaching the supported run length, overrides this word. A MAC target's row reads "reached" from its first crossing on. A new branch reads "Paused" at the instant it starts from its parent run, though it carries the parent's halt record, because no step of the branch stopped it | `test_a_halt_on_a_mark_is_told_apart_from_a_pause_during_a_comparison`, `test_a_branch_opened_on_a_mark_crossing_is_not_said_to_be_stopped_by_it`, `test_a_run_a_mark_stopped_is_not_worded_as_the_learner_s_own_pause` |
| reading a run whose Reset the model refused as one still running, or as one that was reset | the model refuses a Reset only when the tissue blood flows no longer add up to the cardiac output, which only a perfusion fraction written past its range check can cause. A refused Reset leaves the run exactly as it was. The interface then halts the run and records the refusal as its failure. If the run had already failed for another reason, that failure stays the reason, and the banner's advice on recovery mentions the refusal. The status word, the run controls and the banner state the halt. The banner says that no setting can repair the refusal, and that closing and reopening the application starts a new run. It names neither the refused Reset nor a dial. The refusal message gives the two flows as they were set, in L/min, the unit every readout shows | `test_a_reset_the_core_refuses_halts_the_run_visibly`, `test_a_reset_the_core_refuses_leaves_the_run_exactly_as_it_was`, `test_a_refused_reset_names_the_way_out_in_the_banner`, `test_a_tissue_flow_mismatch_is_stated_in_litres_per_minute` |
| comparing readouts with a chart that was drawn from different settings | the readouts come from the model's steps, and the chart from the recorded settings of the run. Before each step, the two sets of settings are compared. If a setting reaches the model without being recorded, the run halts on the last step on which the two agree, and a banner says why. The interface never changes a setting that way. Reset then starts a new run from the model's settings. A recorded change after such a write brings the record back into line with the model without halting the run | `test_a_setting_written_onto_the_core_past_the_controller_refuses_the_next_step`, `test_a_setting_written_onto_a_branch_s_core_past_its_controller_refuses_its_next_step`, `test_reset_after_a_setting_written_past_the_controller_runs_at_that_setting`, `test_a_run_whose_core_setting_moved_past_its_controller_halts_on_the_last_recorded_step` |
| reading the agent selector or a slider, used on a run whose values cannot be read, as a control that took effect | if reading the run's values fails while the selector or a slider is in use, the run halts and the halt is stated from the run's record, so the failure cannot pass unseen. The selector goes back to the agent that record names. The banner still names Reset as the way to recover, unless a refused Reset has left its own instructions. The controls stay usable on a halted run, because locking them would show the agent selector as disabled. A slider moved on a run that has already stopped is refused, as the row on values from different steps says | `test_an_agent_change_on_a_halted_run_restates_the_halt`, `test_a_slider_moved_on_a_run_whose_snapshot_refuses_halts_it` |
| reading the value printed beside a dial dragged into a halt as the value the run holds | after writing its banner, the halt sets every dial from the run's record (`SimulationController.record()`), which gives the agent and the four settings in force. The record takes them from the settings the compartments hold, not from any compartment value. So the label beside the dial whose drag caused the halt shows the value that both the dial and the run hold. A run whose values cannot be read draws no new screen that could rewrite the label | `test_a_drag_that_halts_the_run_leaves_its_label_on_the_dial`, `test_a_halt_is_stated_before_its_dials_are_written` |
| reading a value under a label, a 1 MAC divisor or a verdict that describes a different step of the run | each value and what qualifies it come from one step, and values a halt leaves stale are withheld. § "Every value and what qualifies it come from one step" lists the groups and the cases | `test_every_value_and_its_qualifiers_on_screen_come_from_one_state`, `test_a_halt_after_an_agent_change_shows_no_mac_multiple_beside_another_agent_s_1_mac`, `test_the_accounting_panel_reports_the_failure_after_an_accounting_halt`, `test_a_setting_changed_on_a_halted_run_is_not_shown_as_the_setting_its_values_ran_under`, `test_a_setting_refused_at_the_supported_run_length_names_a_branch_only_while_one_can_be_taken`, `test_a_halt_that_no_frame_draws_after_the_run_started_over_says_its_readouts_are_withheld`, `test_a_stopped_run_refuses_every_setting_and_records_nothing` |
| believing a setting above the vaporizer maximum was simulated | such a setting is **rejected, not capped**, so no run continues on a value the user did not choose. The maximum itself is accepted by the circuit and by the record of settings a run is built from. That record carries the maximum beside the dial setting | `test_rejects_delivered_concentration_above_the_vaporizer_maximum`, `test_explicit_delivered_concentration_above_the_agent_max_is_rejected`, `test_accepts_delivered_concentration_exactly_at_the_vaporizer_maximum`, `test_rejects_a_dial_above_the_vaporizer_maximum`, `test_a_run_cannot_open_or_change_under_a_dial_above_the_vaporizer_maximum` |
| reading a displayed value as resolved to its last digit | the number of decimals shown is a recorded choice within a justified range. Only the display rounds. The model keeps the precision that the display discards | `test_the_model_keeps_precision_the_display_throws_away`, `test_concentration_decimals_are_a_choice_within_a_recorded_band` |
| reading a control mark on the timeline as a measurement | the timeline labels its marks "Settings only — not a measurement." | `test_the_interface_says_a_control_mark_is_an_input_not_a_measurement` |
| reading a modelled compartment value as a measured one | the readout section states, beside its values, that they are model outputs and not measurements (`INTERPRETATION_DISCLAIMER_TEXT`; § "The statement that the readouts are model outputs"). The chart's hover names every value it reports as modelled (§ "The chart's hover readout: what the tooltip may show") | `test_the_interface_says_the_readouts_are_model_outputs_not_measurements`, `test_the_readouts_say_they_are_model_outputs_beside_the_values`, `test_the_hover_reports_the_drawn_state_through_the_formatters` |
| reading one compartment's concentration as another's where two traces are drawn on top of each other | the compartment is named in text on every value line. The hover reports every compartment whose drawn point at the pointer's instant is inside the hover radius, each under its own name. It does not pick the nearest trace for the reader (§ "Where more than one trace answers"). This matters because the top of the percent axis is fixed at 3 MAC for every agent (`CHART_AXIS_TOP_MAC`). On that axis, the fat trace moves less than 4 px over its whole first hour. So the slow compartments are drawn within a pixel or two of one another, and no pointer position can pick one out from the others | `test_two_compartments_within_one_hover_radius_answer_under_their_own_names`, `test_a_contended_hover_names_no_run_while_only_one_is_drawn` |
| comparing two compartments of one run in one hover box as one moment when the box took them from different instants | every compartment of one run is reported at the run's drawn instant nearest the pointer in time. So the instant that labels a value depends only on the pointer's position along the time axis, and the pointer's height decides only which traces are in reach (§ "Where more than one trace answers") | `test_every_compartment_of_one_run_answers_at_one_instant`, `test_a_vertical_hand_movement_never_moves_the_instant_a_hover_reports`, `test_a_trace_answers_only_where_its_point_at_the_named_instant_is_in_reach` |
| reading the hover's value as a live readout after the pointer has left the plot | the hover box shows only while the pointer is over the plot (§ "When it answers"). When the pointer leaves the plot, the box closes at once, and no later screen update brings it back. A box left open would change with every screen update. While a run plays, its values would climb with the run, at an instant the reader is not looking at | `test_the_hover_hides_when_the_pointer_leaves_and_a_later_frame_does_not_bring_it_back` |
| reading one run's displayed value, or the record of what was changed on it, as the other's while two are compared | while more than one run is drawn, every place that shows a value, or the record of what was changed, names its run in text. § "Naming the run in a comparison" lists the seven places | `test_the_hover_names_the_run_only_while_more_than_one_is_drawn`, `test_two_runs_within_the_hover_radius_answer_under_their_own_names`, `test_a_small_pointer_movement_never_swaps_which_run_the_hover_answers`, `test_the_wash_in_state_and_off_scale_lines_name_their_run`, `test_a_lone_run_leaves_the_shared_chart_lines_unnamed`, `test_each_run_s_unmarked_changes_line_is_named_while_runs_are_compared`, `test_the_sidebar_panels_name_the_run_they_record`, `test_a_lone_run_leaves_the_sidebar_panel_headings_unnamed`, `test_the_halt_and_refusal_banners_name_their_run`, `test_a_halt_stated_without_a_frame_still_names_the_run_it_stopped`, `test_a_lone_run_leaves_the_notice_banner_unnamed`, `test_hidden_notice_banners_take_no_height`, `test_the_schematic_follows_its_run_through_a_reset_an_agent_change_and_a_comparison`, `test_the_panel_follows_its_run_through_an_agent_change_and_a_comparison` |
| reading a preview of a dragged setting as part of the run that happened | the preview is drawn only while the slider handle is held. It is drawn inside a tinted region that starts at the point the run reached. A label in the plot names the control and the value tried, and says the value is not applied. Each of its curves is one pixel thinner than the run's, and never thinner than 2 px, and the hover never reports from them. The run keeps its setting until the handle is released (§ "A preview of an unapplied setting") | `test_a_held_thumb_previews_the_setting_without_applying_it`, `test_a_preview_is_drawn_only_inside_its_region_with_its_label`, `test_the_hover_never_answers_from_a_preview` |
| reading a cost as a figure the project supplies, or as computed at a price other than the one it used | the project supplies no price. A cost is shown only beside the two numbers it multiplied, the liquid volume and the price per millilitre. Beside them are the bottle price, currency and date that the price came from, and words saying that the price is the reader's (§ "A cost at the reader's price") | `test_no_cost_is_shown_until_the_reader_sets_a_price`, `test_the_cost_is_the_delivered_liquid_times_the_bottle_price_over_the_bottle_volume`, `test_the_displayed_cost_reproduces_gas_man_s_printed_costs`, `test_each_run_is_priced_at_its_own_agent_s_price`, `test_no_cost_is_shown_where_one_cannot_be_trusted` |
| reading a cost computed from a price entered in the wrong form: a price per millilitre typed as the bottle price, a bottle volume typed in litres or as a count of bottles, the price and the volume swapped, or a price in another currency | the price is entered as a bottle price and a bottle volume, and the volume field names its unit, millilitres of liquid. The readout shows the price per millilitre of liquid that the two give. Each of the first two mistakes makes that price 100 to 1000 times the true one. A swap shows only where price and volume differ widely. At Gas Man's default sevoflurane price, a swap changes the cost by only 8 %. The currency is stored and shown as its three-letter ISO 4217 code, never as a bare "$" (§ "A cost at the reader's price") | `test_an_entry_that_is_not_a_plain_positive_price_is_refused_with_its_reason`, `test_a_refused_entry_changes_nothing_and_says_why`, `test_a_price_per_millilitre_is_shown_to_four_figures_in_millilitres_of_liquid`, `test_a_currency_that_is_not_three_capital_letters_is_refused` |
| reading a container's fill height, or its filled area, as the amount of agent it holds | a container's height shows the compartment's tension on the concentration chart's own scale. Every container is drawn at the same width. So no length or area on a container stands for an amount. Each container prints its amount beside its tension. The share bar shows the amounts on one scale and names each share in text (§ "The compartment schematic: what its heights, amounts and share bar assert") | `test_a_container_s_height_is_its_tension_and_not_its_amount`, `test_fat_s_share_grows_through_the_first_hour_while_its_container_stays_nearly_empty`, `test_the_share_bar_is_painted_to_each_share_and_named_in_text`, `test_the_circuit_fills_to_its_closed_form_tension_on_the_chart_s_scale`, `test_a_tension_above_the_chart_s_top_fills_the_container_and_keeps_its_value` |
| reading an amount of agent vapour as millilitres of liquid, or a liquid-equivalent amount as vapour, which misreads it by a factor of about 180 to 210, depending on the agent | no panel prints a bare "mL" beside an agent amount. A vapour amount is written "mL vapour" and a liquid amount "mL of liquid". `DisplayUnit` defines each spelling once, so no panel writes its own (§ "The compartment schematic: what its heights, amounts and share bar assert"). The agent cost panel writes its delivered amount as "mL of liquid" or "L vapour", whichever unit the reader chose, and its caption says what that unit measures | `test_no_agent_amount_is_printed_with_a_bare_millilitre_unit`, `test_the_delivered_agent_is_shown_to_a_tenth_with_its_unit_named`, `test_patient_inputs_reach_the_drawn_liquid_figure_through_the_model`, `test_a_unit_picked_in_one_view_reaches_every_view_and_survives_a_restart` |

<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->
<!-- not-restated: 8 % -->

### Every value and what qualifies it come from one step

Each group of widgets that states one value with what qualifies it is written
from a single step:

- the readout cards, with their heading and 1 MAC line;
- the dials, with the delivered line;
- the accounting verdict, with the totals it judges.

A test checks every group. For each scenario, every member of a group must
describe the step that scenario names. Every other screen element must be
listed with the reason it belongs to no group.

**After a halt that comes before the screen has been redrawn since the run
started over**, by an agent change or a Reset, the screen still shows the run
that was discarded. So each card withholds its percent and its ×MAC number
("—%", "— ×MAC") under the heading and 1 MAC line of the run that replaced it,
and the clock withholds its time ("—"). The accounting panel withholds its
verdict and amounts too. The banner says that the readouts are withheld and that
the chart still shows the run before it started over.

**After a step fails its accounting check**, the model undoes that step, and
the run's own accounting passes again. So the panel shows the rejected step's
check: "Validation failed", with that step's totals. The banner names the panel
as the one exception to "the values shown are the last completed step". If the
screen is not redrawn after the halt, the panel shows the same check from the
run's record.

**A dial moved on a stopped run**, failed or at the supported run length (the
longest run the model allows), is refused before anything is applied, and springs
back to the setting the run holds. No step runs after a stop. So the new setting
would sit beside values it never produced, and the record would claim a change
that never acted on the patient. A run can also fail on the first step after a
setting was accepted. Then none of its values was computed under that setting
either. The banner states the refusal and the way out. The way out is Reset,
which keeps every setting. At the supported run length, it can also be a branch,
a new run from an earlier instant, where each dial starts at what it was set to
then. The banner names the branch only while one can be taken. So it names Reset
alone when the run is compared with another, which locks its branch control, and
on a dashboard with no branch control.

### Naming the run in a comparison

While two or more runs are drawn, each of these places names its run in text:

1. Each run's own readout panel (§ "Minimum displayed outputs").
2. The chart's hover readout. With one run under the pointer, the name is on
   its first line (§ "The hover and the run it belongs to"). With several, it
   is on each value line. Every run inside the hover radius is reported, so a
   small pointer movement cannot swap which run is read (§ "Where more than one
   trace answers").
3. The three advisory lines inside a chart: the wash-in state, the off-scale
   notice, and the count of control changes the chart could not mark. They
   stack one line per run.
4. The headings of the two record panels: the agent-accounting validation in
   the sidebar, and the control-change record in the right column of the
   unconditional region, the part of the window that is always shown. Each of
   the two stacks whole panels, one per run. So the name is in each panel's own
   heading and moves with the panel.
5. The notice banner, between the runs' control rows and their readouts. Both
   runs use this one place, and a banner with nothing to say is hidden and
   takes no room, so its position does not show whose banner it is.
6. The heading over each run's compartment schematic, taken from the name on
   the run's own panel.
7. The heading over each run's agent cost panel, in the same way.

Colour, line width and drawing order cannot do this. The hover box is separate
from the legend. Line width has no text equivalent, and nothing shows which
run is drawn on top. The run names sit in the always-shown region above the
charts. Without these names, a learner could misread a comparison in three ways:

- One run's F_A/F_I could be read as the other's, or its off-scale notice
  attributed to a run whose traces are all inside the axis.
- The control-change record, "What was changed during this run", read as the
  other run's, says that run received an intervention it never got.
- A halt banner read as covering the whole dashboard says both runs are frozen.
  "The values shown are the last completed step" then claims both runs stopped
  at a failed step when one is still going. "The simulation is unchanged and
  still running its previous setting" is false of the run that took the
  setting.

With only one run drawn, the hover, the chart's advisory lines, the sidebar
panel headings and the banner show no run name.

### The statement that the readouts are model outputs

The readout section's heading row carries **"Model outputs — not
measurements."**, beside "Modelled concentrations:" and the agent's name. It
sits beside the values it qualifies and says what they are, as the timeline's
"Settings only — not a measurement." does for control marks. The compartments
this simulator exists to show are the ones no monitor displays. So a reader has
no measured value to check them against, and a polished display invites reading
them as measurements. The statement is not repeated on the chart. A repeated
disclaimer stops being read, and the chart's hover already names every value it
reports as modelled. The requirement behind it is the hazard row for reading a
modelled compartment value as a measured one.

### What keeps a real patient's data out of a run

§ "Intended use" excludes entering an identifiable patient's data, and using a
run to inform the management of a specific patient. Two safeguards stand
against that misuse today:

1. The use statement (`USE_DISCLAIMER_TEXT` in `app/dashboard_frame.py`) sits
   at the foot of the window. It says that the simulator is for teaching and
   is not a clinical prediction, monitoring or dosing tool. In each built-in
   Workspace it stays in view, however the page scrolls.
2. The simulated patient is always the reference adult in
   `data/patients/reference_adult.json`. No control accepts a weight, age, sex,
   height or body composition. Every run keeps that patient's compartment
   volumes and perfusion fractions, whatever the learner sets.

Changing cardiac output and alveolar ventilation is a core teaching feature.
It also lets a learner set either one to a value measured in a real patient.
The run then shows the reference adult at that flow, and it is not a
prediction for that patient. The simulator accepts such a value, so the use
statement is the only safeguard against reading that run as a prediction.

The patient factors planned in `ROADMAP.md` (planned-milestone item 30) will
remove the second safeguard. `test_every_run_simulates_the_shipped_reference_adult`
checks each way a patient could get into a run today, so adding patient factors
will make it fail. The work that adds them must then rewrite this section and
the hazard table's row for this misuse.

**For developers.** `SimulationController.reset()` builds the new run's settings record
before it clears anything. So a refused Reset leaves the run exactly as it was, and the halt
goes through the failed-step path. Before each step, `SimulationController.advance()`
compares `AgentUptakeSystem.settings_key()` with the key saved when the run last recorded
settings. Code in `app/` changes settings only through the controller, which records the
whole settings record at each change. The agent selector and the sliders read the snapshot
only inside handlers guarded by `halt_gate` in `app/halt_gate.py`. A halt resets the
selector from the run's record, because the refused snapshot is the one that would name the
agent. If a halt comes before the screen is redrawn, every withheld value is hidden before
the dials are written, because writing a dial can raise an exception.

## How this document is held to the tree

The hazard table applies one rule to each of its rows: *every row names the test
that enforces it, or says plainly that it has none*. This section applies the
same rule to the whole document, in four clauses.

Without these clauses, a sentence reads exactly as it did when it was true, even
after the test it names is renamed, the field it describes removed, or the number
it states changed. Requirements traceability, linking each requirement to the
tests and risk controls that cover it, is the established practice for software
of this class. IEC 62304 § 5.1.1 requires the software development plan to carry
traceability between system requirements, software requirements, software system
tests and risk control measures. The FDA's *General Principles of Software
Validation* (2002) § 5.2.2 names traceability analysis among the validation
tasks. Gotel and Finkelstein set out the problem in *An analysis of the
requirements traceability problem*, ICRE 1994, pp. 94–101.

**The four clauses bind this document and `README.md`**, the two documents that
a reader of a displayed value trusts. How they apply to the project's other
documents is in this section's note for developers.

1. **A live assertion names what it asserts.** A sentence that states a fact
   about the code or its data, such as that a test enforces a rule, that a field
   exists, that a value is *N*, or that a job runs something, names that thing in
   a form that can be looked up. The forms are a test, path, symbol or field in
   code format, or a `<!-- provenance: -->` marker over a restated number. The
   author owes this, whether or not the checker reads the sentence.
   `tools/doc_check.py` resolves every one of those forms.
2. **An enumerated family is kept complete.** Some headings promise one
   assertion per member: the invariants list, the required-tests subsections,
   the displayed-outputs list, the hazard table, a frozen gate list and a
   marked enumeration. Every member of such a family names its entity or
   carries the declared-none form of clause 3. `check_bound_families` fails a
   member that does neither.
3. **The declared-none form names the item that owes the link.** An absence is
   written ``no test yet (`PL-XXXX`)``, and the parenthesis names an item still
   open in the queue. The words before it belong to the sentence, and the form
   itself is fixed. With a fixed form, a script can tell a forgotten link from a
   declared absence. Each exemption also points forward to the work that owes
   the link. And closing the named item without adding the link fails the
   check.
4. **A dated statement is a record of what was true on its date, and is never
   checked against the code.** A sentence that carries a date, sits under a
   dated heading, or sits inside a released version's section asserts what was
   true at that date. It is not linked, not checked, and **not edited to carry a
   later fact**. A later fact is added with its own date.

**A computed claim names the test that computes it.** This is clause 1 applied
to what the model computes and what the interface displays. For example, a
sentence that says when a compartment first shows a nonzero reading is a claim
about the model's output. It names the test that computes the figure, in code
format, or it carries ``no test yet (`PL-XXXX`)``. The strongest form is a test
that reads the figure from this document and compares it with the model's
output, as `tests/reference/test_mac_awake_washout_figures.py` does. Then the
page cannot drift from the model without a test failing. Naming a test is the
minimum.

`check_bound_families` enforces this rule one section at a time, in each section
listed in its table. Each paragraph there that states a number with a unit must
carry one of these: a test in code format, the declared-none form, a date, or a
published source cited by a DOI, a PubMed id, an ISBN or a journal locator such
as "Anesth Analg 1991;72:316-324". An author and a year alone, such as "Mapleson
1963", does not count, because no pattern can tell it from a phrase such as
"Until 2026". The test or the declared-none form may instead be in the note for
developers below the paragraph. That note covers the paragraphs directly above
it, back to the previous heading or note, and stops at the first paragraph that
passes on its own. A date or a source in the note covers only the note. A
paragraph with none of these passes only if a marker covers each of its numbers
with a unit. A `provenance:` marker covers a value the paragraph
asserts, in that value's unit. A `derived:` marker covers a figure the paragraph
computed, in the unit it writes, and each input it asserts. A `not-restated:`
marker covers nothing, because it says its numbers are not stored values. So a
computed figure cannot pass on a marker written for a figure beside it. A
section joins the table when the change that makes it conform is merged, as
clause 2's families do. The check cannot read a qualitative claim, such as which
value a readout shows beside a halt. Such a claim still falls under clause 1,
and review enforces it.

**Counts.** A count is stated in prose only where a check links it to what it
counts, such as a group heading over its entries or a marker over a data value.
Otherwise the count is dated, the rule is stated without the number, or the
number is read from the tool that prints it. So this document never states the
size of its own families.

**What an assertion that names nothing looks like.** Inside a bound family, it
must use the declared-none form, or the check fails. The same is true of a
paragraph that states a number with a unit, in a section that the check covers
paragraph by paragraph. Elsewhere in a bound document, such an assertion is a
number without a marker or a claim without a code span. There, the
documentation review before a work item closes catches it:
`tools/doc_check.py candidates` prints it when its subject changes. Computed
claims are the exception, and their sections join the check one at a time. A
dated assertion is a record anywhere.

**For developers.** `ROADMAP.md`'s frozen lists are already families under
clause 2, and its prose falls under clause 4. `docs/ARCHITECTURE.md`'s package
map is already a family. Every thread in `docs/WORKING_NOTES.md` is dated, so
only clause 4 governs it. Prose about the project's workflow tooling, called
the apparatus, is not bound. That covers `.claude/`, `CONTRIBUTING.md` and
`docs/resident-instructions.md`, where the counts rule is only advice. In
`tools/doc_check.py`, `check_named_tests`, `check_citations`,
`check_prose_provenance` and `check_make_targets` resolve the forms clause 1
names. A family joins `check_bound_families`'s table only when the change that
annotates its members is merged, so the check never keeps `make check` failing
for work not yet done. `check_gate_counts` applies clause 3 in code: it calls a
frozen count "a dated fact that must never change".

## Purpose

The milestone must demonstrate:

- circuit wash-in and washout;
- ventilation between the breathing circuit and alveolar gas;
- uptake from alveolar gas into blood;
- cardiac-output-dependent delivery to tissues;
- perfusion-limited distribution into vessel-rich, muscle, and fat groups;
- mixed-venous return to the lungs;
- dynamic changes in fresh gas flow, delivered concentration, alveolar ventilation, and cardiac output;
- deterministic numerical behavior; and
- explicit conservation of agent mass.

v0.1.0 modeled sevoflurane only. v0.2.0 added isoflurane and desflurane as
selectable agents, using the same equations unchanged (see § "Status" and
"v0.2.0: isoflurane and desflurane" under § "Parameter provenance").

## Model boundary

The modeled system contains:

1. one ideal, perfectly mixed breathing circuit;
2. one ideal, perfectly mixed alveolar gas compartment;
3. one venous blood pool;
4. one vessel-rich tissue group;
5. one muscle tissue group; and
6. one fat tissue group.

**Perfusion-limited exchange.** Agent moves between blood and alveolar gas,
and between blood and each tissue group, by perfusion-limited exchange. Blood
leaves the lung or the tissue at equilibrium with it, so the barrier between
them never limits how fast agent moves. The rate is then set by the blood
flow, the agent's blood:gas partition coefficient and the difference in
partial pressure, as the uptake equations in § "Governing equations" show. In
diffusion-limited exchange, which this model does not represent, blood leaves
before it has equilibrated, and the barrier limits the rate. The term
describes the exchange between blood and the lung or a tissue, not the blood
itself. Jones and Rowland-Yeo
call the two tissue cases perfusion rate-limited and permeability
rate-limited, and give the first as typical of small lipophilic molecules,
which the volatile agents are (Jones HM, Rowland-Yeo K. Basic concepts in
physiologically based pharmacokinetic modeling in drug discovery and
development. *CPT Pharmacometrics Syst Pharmacol* 2013;2:e63,
doi:10.1038/psp.2013.41). Yasuda et al. assumed perfusion-limited delivery to
the tissues when they fitted sevoflurane and isoflurane kinetics in volunteers
(*Anesth Analg* 1991;72:316-24, p. 319).

Arterial blood is not a separate mixing compartment. The model treats the
lung's exchange with blood as perfusion-limited, so blood leaving the alveolar
capillaries equilibrates instantly with alveolar gas. The model also has no
shunt and only one alveolar compartment, so it has no ventilation-perfusion
mismatch. All arterial blood has therefore passed through that exchange.
Arterial partial pressure, as a fraction, is defined as $`F_a \equiv F_A`$,
with no arterial volume, mixing delay, or value of its own. In patients, the
arterial partial pressure runs below the end-tidal one during administration,
as Carpenter and Eger measured (§ "Desflurane's residual, and why the
parameter file was not changed"). So this identity is a deliberate
simplification of the model, not a property of the agents. It matches the
perfusion-limited mammillary structure of the Gas Man simulator, the source of
this project's sevoflurane and patient parameters. Gas Man computes four
compartments: alveolar gas and the vessel-rich, muscle, and fat groups. It
displays arterial tension without tracking it as a compartment. See:

- Philip JH. Gas Man Version 4.1 Teaches Inhalation Kinetics. Society for
  Technology in Anesthesia. <https://www.stahq.org/files/7913/2743/1066/Abstract_57.pdf>
- Do distribution volumes and clearances relate to tissue volumes and blood
  flows? A computer simulation. BMC Anesthesiology.
  <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1508141/>

This simplification is listed in § "Known limitations."

Inspired gas is not a separate compartment either. The circuit is one ideal,
perfectly mixed volume, with no dead space and no separate inspiratory and
expiratory limbs. So the gas the patient inspires *is* the circuit gas, and
there is no transport delay between the two. The model therefore tracks one gas
concentration between the vaporizer and the alveoli. That concentration is the
**inspired fraction** $`F_I`$, the middle term of the literature's
$`F_D \rightarrow F_I \rightarrow F_A`$ cascade. $`V_C`$ is the circuit's
volume, and $`M_C`$ is the agent it holds, so $`M_C = V_CF_I`$.

This is an assumption of the circuit model, not a property of breathing
systems in general. It makes the displayed $`F_A/F_I`$ ratio the textbook one,
the canonical teaching curve of inhaled-anesthetic uptake (§ "F_A/F_I as a
displayed ratio"). A multi-limb system, such as Lerou and Booij's three-part
model, separates inspired gas from mean circuit gas. There the two would be
distinct states, and this model's single $`F_I`$ would no longer describe both.
Extending the model that way would first require recording that change in this
document.

Symbols and the gas-phase cascade ($`F_D`$, $`F_I`$, $`F_A`$) follow Hendrickx
and De Wolf (pp. 161-162). They attribute the $`F_D - F_I`$ gradient to
rebreathing (p. 169) and the $`F_I - F_A`$ gradient to uptake (p. 171), and
describe the teaching role of the $`F_A/F_I`$ curve (p. 167) (Hendrickx JFA,
De Wolf A. Special aspects of pharmacokinetics of inhalation anesthesia. In:
Schüttler J, Schwilden H, eds. Modern Anesthetics. Handbook of Experimental
Pharmacology 182. Springer, 2008:159-186).

**One symbol to read carefully.** $`F_I`$ is the inspired fraction, and
$`F_i`$ is tissue group $`i`$'s fraction. The two differ only in case. Both
conventions are standard in the literature. Renaming either symbol would make
this model's symbols disagree with every source a reader is likely to come
from. Where both appear in one expression, the tissue index is written out.

The external inputs and outputs are:

- agent entering through fresh gas;
- carrier gas entering through fresh gas;
- an equal volume of mixed circuit gas leaving through the circuit exhaust; and
- no metabolism or other chemical destruction of the agent.

The circuit and patient form a closed recirculating exchange path, apart from
fresh-gas inflow and circuit exhaust.

**That circle is semi-closed.** The exhaust described above runs whenever fresh
gas flows, at exactly the fresh-gas rate. Closed-circuit operation is different.
It uses a fresh gas flow titrated down to the patient's uptake, or a machine mode
that shuts the surplus gas valve outright. Its balance of agent in and out
differs, and these equations do not describe it. The section "Breathing circuit"
explains this limit and estimates its size, and the section "Known limitations"
lists it.

## Conventions

### Time

Simulation time is explicit state and is measured internally in seconds.

Flows entered in liters per minute are converted to liters per second:

$$
\dot V_{\mathrm{s}} = \frac{\dot V_{\mathrm{min}}}{60}
$$

**The setting in liters per minute is the record, and the per-second value is
derived from it.** A run stores each flow as it was set, in liters per minute.
The equations use a per-second value. That value is computed from the stored
setting each time the equations need it, and it is never stored. Multiplying it
by 60 does not always give back the setting, and the tissue flows formed from
cardiac output share that error. So settings rebuilt from per-second values
could describe a run that nobody set up.

Wall-clock time may schedule interface updates, but it must never be used as simulation time.

Every time in this document, in the model's code and in a saved run is in
seconds. The screen shows time in one form only. The clock, every recorded
control stamp and the chart's axis ticks are all durations, and each part
carries its own unit: `45s`, `1m30s`, `1h23m45.6s`, `24h`. A part that is zero
is left out. Tenths of a second appear only where there are some, so a stamp
still identifies the step at which it was taken.

The clock and the stamps use the axis's form because all three are on screen
together. A control mark stamped `5400.0 s` on an axis reading `1h30m` would
make the reader convert by hand between two displayed forms of one quantity.
At the supported 24-hour run length, a clock in seconds would read
`86400.0 s`. That figure shows false precision for a limit that this document
states in hours.

The time span that the chart draws is still written out in words:
`15 minutes` above an axis whose last tick reads `15m`. The reader picks that
phrase from a selector and sees it again in a caption. Neither place is a tick
label, so the phrase does not have to fit in a tick's width. § "The chart's time
base" explains that choice, and § "Displayed precision" sets the precision at
which each form is shown.

#### Simulated time is a count of steps, not a running total

A run takes one step size and keeps it for its whole length. Simulated time
is the number of completed steps multiplied by that step. It is one
multiplication, rounded once. It is never a total accumulated one step at a
time.

The two methods agree within about 35 nanoseconds over a four-hour run at the
app's 0.1 s step. That is far below anything displayed, so multiplying gains
no accuracy. Its advantage is that the product depends only on how far
the run has gone. A running total also depends on the order and number of the
additions that produced it. Ten steps of 0.1 s sum to 0.9999999999999999
and multiply to 1.0.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

A step of a different size from the one a run has already taken is rejected
with an error, and it is not counted. Time is the count multiplied by one step
size, so the count means a time only while every step is the same size. Reset
clears the count and the step size together, so a fresh run may use a
different step.

#### The reproducibility guarantee

**A run depends only on its inputs and on the number of steps taken.** The
screen uses the computer's clock to decide when to update. But how many steps
each update takes is a setting the reader chooses, never something measured
from the clock. The simulation never takes extra steps to catch up after a slow
update, and it reads no clock. So a slow or busy computer reaches a given step
*later in real time*, and every value it computes and every record it stores
is identical. The run is slower, not different.

**An automatic check enforces this.** It stops the build if any part of the
model's code reads the computer's clock, draws an unseeded random number, or
makes an identifier from either. The screen code may still use the clock, as
the paragraph above allows. If the check missed any of these routes, a run
could stop being reproducible while the check still passed.

So two runs with the same starting state, parameters, step size, setting
changes and order of events, taken to the same step, are **exactly identical**
in every stored value. They do not merely agree within a tolerance. At step
*n*, which falls at *n* times the step size in both runs, they hold the same
state. Every comparison of one run with another relies on this. That includes
comparing a branched run with the run it branched from, at every instant they
share. § "What a branch comparison asserts, and what it does not" says what
such a comparison may and may not claim.

**A state computed from a saved run has a guarantee of its own.** The guarantee
above holds because every run uses the same step size, so only one sequence of
calculations reaches step *n*. A saved run stores no samples and no step size.
Its states are computed on request, and more than one sequence of calculations
can reach the same instant. For those states, "The canonical evaluation rule"
under § "Runtime controls" gives the guarantee. That rule is stronger in one
way. Two computations of one saved run at one instant give exactly the same
bits. It is narrower in another. Only values computed the canonical way may be
stored, exported or branched from.

**Playing a run faster does not make it a different run.** The playback rate is
how much simulated time passes per second of real time. A faster rate takes
more *whole steps* per screen update, never a larger step. So a case played at
real time and at three hundred times real time takes the same steps, in the
same order, at the same size, and gives exactly the same results sooner. A
rate that enlarged the step would fall under the first exclusion below. It
would compute a second solution of the same equations, and a displayed value
would depend on how fast the reader was watching. No label could fix that.

The guarantee does not cover four things, and none of them is a defect:

- **A different step size.** Between setting changes, runs at two step sizes
  differ only by computer rounding, because each step solves the equations
  exactly. A test bounds that difference. A setting change takes effect at the
  next step, and steps of different sizes end at different times. So the moment
  a change takes effect moves with the step size, and after any setting change
  the two runs differ by more than rounding.
- **A different model version.** The guarantee applies within one version of
  the equations and one parameter set. That is why both are versioned.
- **A different platform.** Basic arithmetic gives identical results on every
  computer. But each step also uses an exponential function, whose last digit
  can differ between platforms, Python builds and math libraries.
  Reproducibility is claimed for one installation, not across all of them.
- **Elapsed real time.** How long a machine takes to reach step *n* is a
  property of the machine. So is how many steps it has reached when a
  wall-clock minute is up. Neither is a property of the model.

**For developers.** `UptakeEquationSettings` in `core/governing_equations.py` stores each
flow in the unit the user set it in. Converting to a per-second flow and multiplying by 60
does not always return the setting. On a 0.1 L/min grid across the supported 0 to 10 L/min
range, it fails for 7 of the 101 cardiac outputs (1.9, 3.8, 3.9 and 7.6 to 7.9 L/min). A
step of another length than the run's earlier steps raises a `SimulationConfigurationError`,
because `elapsed_s` is the step count times one step length.
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

`tools/import_boundary_check.py` is the check on the model's code. It runs in
`make check` and CI, and it fails the build on a `time`, `datetime`, `random`,
`secrets` or `uuid` import in any module under `src/anesthesia_sim/core/`. Its
`BOUNDARIES` table gives the reason for each entry. The restriction stops at
`core/` because the interface may use the wall clock. Seeding cannot undo two
of those imports. `secrets` draws from `random.SystemRandom`, whose `seed()` is
documented to do nothing and whose `getstate()` raises an error.
`uuid.uuid1()` mixes the current time with the host's hardware address, so a
run would differ between *machines* as well as between runs. The exponential
in a step is one `exp()` call, a library function whose last bit may differ
between platforms. The propagator is also built from a series and a sequence
of squarings, and a compiler may reassociate their summation order.

### Concentrations

Every concentration that the model computes is a dimensionless
partial-pressure-equivalent fraction from 0 through 1. Only one concentration
is set rather than computed: the vaporizer dial. The model stores the dial as the
percent that was dialled, and it derives $`F_D`$ from that percent, as
described below.

The gas-phase symbols follow the inhaled-anesthetic literature:
$`F_D \rightarrow F_I \rightarrow F_A`$. The middle one, $`F_I`$, is the
inspired gas, although the breathing circuit holds it. The circuit keeps the
subscript $`C`$. $`V_C`$ is its volume and $`M_C`$ is the agent in it.
§ "Model boundary" above states the assumption that makes circuit gas and
inspired gas one quantity, and what would break it.

For example, $`F = 0.02`$ represents a 2% gas-phase concentration.
<!-- not-restated: 2 % -->

Two other places quote the same quantity in percent of an atmosphere, and
they cannot do otherwise: a vaporizer dial and a MAC. The conversion between
the two forms is:

$$
\text{percent} = 100F
$$

One module in the model's code does this conversion, in both directions, and
no other code repeats it. The code treats a percent and a fraction as different
kinds of number. It rejects one where the other is wanted, both before the
program runs and wherever a concentration is stored. It also rejects a value
that is already converted, or one that does not say which form it is in. The
conversion is used in only two places. The circuit and the recorded settings
derive $`F_D`$ from the dial's percent where the equations use it, and the
screen converts for display.

**The percent dialled is the record, and $`F_D`$ is derived from it.** The
circuit, the settings that a run records for each stretch, and the record of
control changes all store the vaporizer setting as the percent dialled. A new
run starts the dial at the agent's published percent, without converting it.
Converting a fraction back to a percent does not always return the setting. On
a 0 to 8% dial in 0.01% steps, it fails for 126 of the 801 settings. So a
record kept as a fraction could not give back what a learner dialled.
§ "Time" applies the same rule to the flows. An error message about a setting
gives it in percent, beside the vaporizer maximum, which is also stored in
percent.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

The interface also converts to the second display unit, a multiple of the
running agent's 1 MAC. This unit rescales the percent above by one constant
per agent, and it introduces no new state:

$$
\text{MAC multiple} = \frac{100F}{\mathrm{MAC}_\%}
$$

The section "MAC multiples as a display unit" states what that quotient does
and does not assert. It defines no modeled quantity, and the model's own
calculations never compute it. The stored MAC cannot be zero, and every
display that divides by it accepts only a MAC stored that way. No other lower
limit is set, so a MAC far below any real agent's would still give multiples
too large to read. The shipped MACs are 1.2% to 6.0%.
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- provenance: data/agents/desflurane.json mac_percent = 6 -->

A concentration fraction must always be finite and satisfy:

$$
0 \leq F \leq 1
$$

**The range is checked once, when a concentration is created.** A fraction
must lie from 0 to 1 and a percent from 0 to 100, and both must be finite.
Each rejects a value of the other form, because that is a missed conversion
rather than a concentration out of range. Anything that is not a plain number
is rejected before the range is checked. Minus zero is stored as zero.

Every place that stores a concentration accepts only a checked value and
rejects a plain number. These places include each compartment, the breathing
circuit and its saved state, the settings a run is built from, and the agent's
parameters, which hold its MAC and vaporizer maximum. So a concentration is
checked once, where it is created.

A fraction that a step computes is checked before any compartment stores it,
under that compartment's name. A value outside 0 through 1 halts the run and
names the compartment, instead of being stored or shown. Rounding in the
calculation can carry a computed fraction a little above the largest fraction
it started from. So the delivered concentration and each starting fraction
must be at or below 0.99 of ambient pressure (§ "The numerical envelope"). No
supported setting computes a fraction outside the range.
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

**For developers.** `src/anesthesia_sim/core/concentration.py` is the only
place where the conversion between a fraction and a percent is written. The two
forms are distinct types there, so a type checker rejects a percent where a
fraction is wanted, and the conversion rejects a bare number.
`AgentUptakeSystem.for_agent()` starts the dial at the published percent
without converting it, because multiplying a fraction by 100 does not always
return the percent it came from. The first failure is at 0.23%, and 0.9% comes
back as 0.9000000000000001. Nothing in `core/` computes the MAC multiple. Its
divisor is stored as a `MacPercent`, a `Percent` that rejects zero when it is
built, and every formatter that forms the quotient rejects a divisor that was
not built as a `MacPercent`.

`Fraction` and `Percent` check a value when it is built. Each rejects a value
that is not finite, or that lies outside 0 to 1 for a `Fraction` or 0 to 100
for a `Percent`. Each raises a `TypeError` for anything that is not an `int` or
a `float`, such as a `bool`, a `Decimal` or a string, before the range is
checked. `core/checked_number.py` states these rules once, for the
concentrations and the flows: what counts as a number, that one checked
quantity is never built from another, and that minus zero is stored as zero
(§ "Supported input ranges"). The places that store a concentration are each
compartment's setter, the driving fraction that a compartment's own closed
form takes, `BreathingCircuit` when it is built or set, the
`BreathingCircuitState` that a rollback restores it from, the
`UptakeEquationSettings` that a run is built from, and the `AgentParameters`
that an agent's data file is parsed into. `AgentParameters` stores the agent's
MAC and vaporizer maximum. A computed fraction is checked under the name of the
compartment that will store it, in `AgentUptakeSystem._write_state_vector`.
`core/concentration.py` records the measurements behind the 0.99 input limit.

### Agent amount

Every compartment stores the agent as an equivalent gas volume at one
documented reference temperature and pressure. That condition is **20 °C and
760 mmHg, dry**, where the ideal-gas molar volume is 24.055 L/mol. The
condition defines the *unit*. It is not a claim about where any of the gas
physically is. "Known limitations" records what it costs to carry the whole
model at one condition.

The implementation must use the same reference conditions everywhere. It must
not add gas fractions, dissolved blood concentrations, and tissue
concentrations directly.

Let $`M_x`$ denote the equivalent gas volume of the agent stored in
compartment $`x`$.

The unit used in code is liters of equivalent pure agent gas, unless the
implementation document explicitly selects another consistent unit.

**Nothing the model computes depends on the reference condition.** Every
governing equation works with dimensionless fractions and physical volumes, and
every partition coefficient is a ratio. So the concentration curves, the mass
balance and every displayed concentration do not depend on which condition
the unit names. If the condition changed, no number under § "Governing
equations", "Conservation of agent mass" or "Minimum displayed outputs" would
move. The condition matters only when an amount is converted *out* of the unit,
into moles, mass, or the millilitres of liquid that a vaporizer is filled from.
For that conversion, the two conditions differ by a factor of 1.058,
because the ideal-gas molar volume is 24.055 L/mol at 20 °C and 25.450 L/mol at
37 °C.

**Why 20 °C.** Three grounds support it, and the first can be checked by
arithmetic.

1. **The published vapour-to-liquid constants are 20 °C constants.** The
   consumption literature quotes one composite number per agent: the vapour
   volume obtained from 1 mL of liquid. Biro gives isoflurane 195 mL,
   sevoflurane 184 mL and desflurane 210 mL. That number can instead be
   derived from the primary density measurement and the molar volume above.
   The derivation reproduces all three within 0.7 % at 20 °C. It reproduces
   none of them at 37 °C, where the same derivation runs 5.1–6.3 % high:

   | Agent | Liquid density at 20 °C, g/mL | Molar mass, g/mol | Derived mL vapour per mL liquid, 20 °C | Biro's constant | At 37 °C |
   | --- | --- | --- | --- | --- | --- |
   | Sevoflurane | 1.5203 | 200.05 | 182.8 | 184 | 193.4 |
   | Isoflurane | 1.5019 | 184.49 | 195.8 | 195 | 207.2 |
   | Desflurane | 1.4651 | 168.04 | 209.7 | 210 | 221.9 |

   The densities are those of Laster, Fang and Eger. They were measured in
   four 50-mL volumetric flasks at 20 °C, with a temperature coefficient of
   −0.00250 ± 0.00014 g/mL per °C over 0–25 °C. The molar masses are the
   formula masses, which the ChEMBL chemistry database gives to two decimals.
   So the table shows that the field's constants are 20 °C constants. A model
   that declared 37 °C would either mix two conditions or print consumption
   figures 5.5 % below the published ones. That 5.5 % is $`1 - 1/1.058`$, the
   same for every agent. Put the other way, 1 L of vapour comes from 5.47 mL of
   liquid sevoflurane here, and would come from 5.17 mL at 37 °C.

2. **The amounts a consumption figure converts are fresh gas, and fresh gas is
   at room temperature.** The delivered and exhausted amounts,
   $`M_{\mathrm{delivered}}`$ and $`M_{\mathrm{exhausted}}`$, both add up
   $`\dot V_F`$, the flow at the common gas outlet. That flow is carrier gas
   plus the vapour that the vaporizer added. It is on the machine side of the
   patient, at operating-room temperature, not at 37 °C. A cost or waste figure
   is computed from those two amounts (`ROADMAP.md` "Planned milestones" item
   28). Declaring 20 °C makes them exact. Declaring 37 °C would leave them
   approximate. It would *also* need a room-to-body temperature correction on
   $`\dot V_F`$, which would change the governing equations, not a label.

3. **Gas Man's own constants are 20 °C constants, and its litres carry no
   condition at all.** Gas Man states a condition in one place only, its
   `GASMAN.INI` setting `Volatility=209 Vapor/Liquid volume ratio (20'C)`. It
   never states a condition on the litres of uptake and of delivered agent
   that it displays. This model does the same. It uses the condition only where
   vapour is converted to liquid. Gas Man's five printed constants for vapour
   per volume of liquid settle which condition that is. The 20 °C derivation
   reproduces every one of them, and the 37 °C derivation reproduces none:

   | Agent | Gas Man | Derived, 20 °C | Derived, 37 °C |
   | --- | --- | --- | --- |
   | Halothane | 228 | 227.7 (−0.15 %) | 240.9 (+5.6 %) |
   | Enflurane | 198 | 198.6 (+0.29 %) | 210.1 (+6.1 %) |
   | Isoflurane | 196 | 195.8 (−0.09 %) | 207.2 (+5.7 %) |
   | Sevoflurane | 183 | 182.8 (−0.10 %) | 193.4 (+5.7 %) |
   | Desflurane | 209 | 209.7 (+0.35 %) | 221.9 (+6.2 %) |

   The 20 °C derivation is within 0.35 % on all five, against 5.6–6.2 % at
   37 °C. The table adds halothane and enflurane to the three agents this
   model carries, because Laster, Fang and Eger measured their densities in
   the same experiment. This model takes its partition coefficients, MACs and
   reference patient from Gas Man ("Source hierarchy"), so the amounts here
   follow Gas Man's arithmetic. A different reference condition would make this
   model's litre and Gas Man's litre different quantities, although every
   parameter behind them is shared.

<!-- provenance: data/agents/sevoflurane.json liquid_density.g_ml = 1.5203 -->
<!-- provenance: data/agents/isoflurane.json liquid_density.g_ml = 1.5019 -->
<!-- provenance: data/agents/desflurane.json liquid_density.g_ml = 1.4651 -->
<!-- provenance: data/agents/sevoflurane.json molar_mass_g_mol = 200.05 -->
<!-- provenance: data/agents/isoflurane.json molar_mass_g_mol = 184.49 -->
<!-- provenance: data/agents/desflurane.json molar_mass_g_mol = 168.04 -->
<!-- derived: 182.8 from data/agents/sevoflurane.json liquid_density.g_ml = 1.5203, molar_mass_g_mol = 200.05 -->
<!-- derived: 195.8 from data/agents/isoflurane.json liquid_density.g_ml = 1.5019, molar_mass_g_mol = 184.49 -->
<!-- derived: 209.7 from data/agents/desflurane.json liquid_density.g_ml = 1.4651, molar_mass_g_mol = 168.04 -->

**37 °C was the alternative.** This model's partition coefficients were
measured at 37 °C. The alveolar, venous and tissue compartments are physically
at 37 °C. So 37 °C is the condition at which the *stored* amounts are natively
exact. It was not chosen, for two reasons. The amounts that are converted out
of the unit are the fresh-gas terms, not the stored amounts. And the published
constants that any figure will be compared against are 20 °C constants.
§ "Known limitations" gives what choosing 20 °C costs.

**The conversion's inputs are stored, and one part of the code does the
conversion.** Each agent file stores the liquid's density, with its spread,
the temperature at which it was measured and its source. It stores the
molar mass with its own source. The code derives the millilitres of vapour per
millilitre of liquid from them, as the table above does. It computes the molar
volume from the gas constant, 20 °C and one standard atmosphere, and does not
store it. A density measured at any temperature other than 20 °C is rejected
when the file loads, because no temperature correction is stored. The
conversion is exact for the delivered and exhausted agent and the circuit's
amount, which are at room temperature. It overstates an alveolar, venous or
tissue amount by 5.8 % (§ "Known limitations", under § "One reference
condition, where the model physically has two"). A cost is computed from the
delivered amount, so it is exact.

The published ratios are not stored. A test checks the derived ratios against
Biro's within 1 % and against Gas Man's within 0.5 %. It also prices the
isoflurane delivered in the Gas Man Workbook's Exercises 14-1 and 14-2 with the
derived ratio. The prices must match the book's costs, allowing for rounding
to the cent and for Gas Man's ratio being rounded to a whole
millilitre.

The agent cost display is the only code that uses the conversion. It shows the
delivered agent as liquid and converts nothing else, so no figure it shows
carries the 5.8 % error. It reads the amount and the running agent's ratio from
the same moment of the run, so it cannot pair one agent's vapour with another
agent's ratio. Using desflurane's ratio would misstate sevoflurane by about
13 %. A test fails if any other code uses the conversion. The cost on the same
display multiplies this liquid figure by the reader's price (§ "A cost at the
reader's price").

The sources for this section are listed below, with the route by which each
was read.

- Laster MJ, Fang Z, Eger EI II. *Specific gravities of desflurane, enflurane,
  halothane, isoflurane, and sevoflurane.* Anesth Analg 1994;78(6):1152-3.
  PMID 8198275, doi:10.1213/00000539-199406000-00022. Retrieved from PubMed
  and verified against the abstract on 2026-09-17, and again on 2026-10-26,
  when its densities were stored.
- ChEMBL database, release 34, compounds CHEMBL1200694 (sevoflurane),
  CHEMBL1256 (isoflurane) and CHEMBL1200733 (desflurane), for the molecular
  formulas and the molar masses. Read through a ChEMBL connector (an MCP
  server) on 2026-10-26. It is tier 2 under § "Source hierarchy", because a
  molar mass is computed from the formula and the standard atomic weights, not
  measured on the agent. Each agent file says why no tier-1 source exists for
  it.
- Mohr PJ, Newell DB, Taylor BN, Tiesinga E. *CODATA recommended values of the
  fundamental physical constants: 2022.* Rev Mod Phys 2025;97(2):025002.
  doi:10.1103/RevModPhys.97.025002. Table XXXII gives the gas constant as the
  product of the exact Avogadro and Boltzmann constants. Table XXXIII gives
  the standard atmosphere, 101 325 Pa exactly, and the molar volume of an
  ideal gas at 0 °C, which the tests use to check the 24.055 L/mol above.
  Read at full text from arXiv:2409.03787v1 on 2026-10-26.
- Biro P. *Calculation of volatile anaesthetics consumption from agent
  concentration and fresh gas flow.* Acta Anaesthesiol Scand
  2014;58(8):968-72. PMID 25060161, doi:10.1111/aas.12374. Retrieved from
  PubMed and verified against the abstract on 2026-09-17. The abstract gives
  the four constants but does not state their temperature, so the
  reproduction above is what shows they are 20 °C constants.
- Philip JH. *Workbook for Gas Man*. Appendix C's `GASMAN.INI` listing is the
  source for the `Volatility` setting. Chapter 10's closed-circuit
  liquid-injection section (printed pp. 103-105) is the source for the five
  expansion constants. There the constants convert an *input*, the volume of
  liquid injected, rather than a displayed amount. Both were read from the
  project owner's private reference library on 2026-09-16.
  `docs/references/README.md` § "Philip — *Workbook for Gas Man*" has the
  reading notes. The workbook is Tier 3 under § "Source hierarchy": it
  defines what Gas Man does, and it measures nothing.

**For developers.** Each agent file stores the liquid's density as
`liquid_density`, with its spread and the temperature at which it was
measured, and the molar mass as `molar_mass_g_mol`. Each has its own `sources`
entry, which says why no tier-1 source (§ "Source hierarchy") exists.
`core/liquid_agent.py` derives the millilitres of vapour per millilitre of liquid from them.
`tests/reference/test_published_vapour_to_liquid.py` checks the derived ratios
against Biro's within 1% and against Gas Man's within 0.5%. The display reads
the amount and the ratio from one snapshot, which pairs the ratio with the running agent
(`SimulationSnapshot.agent_vapour_per_liquid`). A unit test fails if any other code under
`src/` calls `liquid_volume_ml`.

## Symbols

The **Code** column names the one place in the model's code that holds each
symbol, written `ClassName.accessor`. A reader who knows these variables
should be able to follow the code without the column, so code that needs the
column to be understood has a defect.

| Symbol | Meaning | Unit | Code |
| --- | --- | --- | --- |
| $`t`$ | Explicit simulation time | s | `SimulationState.elapsed_s` |
| $`\Delta t`$ | Simulation step | s | `SimulationState.simulation_step_s` |
| $`F_D`$ | Delivered fresh-gas agent fraction | dimensionless | `BreathingCircuit.delivered_partial_pressure_fraction` |
| $`F_I`$ | Inspired agent fraction, which is the gas in the breathing circuit (see § "Model boundary") | dimensionless | `BreathingCircuit.inspired_partial_pressure_fraction` |
| $`F_A`$ | Alveolar agent fraction | dimensionless | `AlveolarCompartment.partial_pressure_fraction` |
| $`F_a`$ | Arterial partial-pressure-equivalent fraction, defined as $`F_a \equiv F_A`$ (§ "Model boundary"). It is not an independent state | dimensionless | — no attribute: the code reads `AlveolarCompartment.partial_pressure_fraction` wherever an arterial fraction is required |
| $`F_v`$ | Venous blood partial-pressure-equivalent fraction | dimensionless | `VenousBloodCompartment.partial_pressure_fraction` |
| $`F_i`$ | Tissue group $`i`$ partial-pressure-equivalent fraction | dimensionless | `TissueGroup.partial_pressure_fraction` |
| $`V_C`$ | Mixed breathing-circuit volume | L gas | `BreathingCircuit.circuit_volume_l` |
| $`V_A`$ | Modeled alveolar gas volume | L gas | `AlveolarCompartment.gas_volume_l` |
| $`V_v`$ | Venous blood-pool volume | L blood | `VenousBloodCompartment.volume_l` |
| $`V_i`$ | Volume of tissue group $`i`$ | L tissue | `TissueGroup.volume_l` |
| $`\dot V_F`$ | Fresh gas flow at the common gas outlet: carrier gas plus the vapour the vaporizer added, not the flowmeter setting (see § "Breathing circuit") | L gas/min | `BreathingCircuit.fresh_gas_flow_l_min` |
| $`\dot V_A`$ | Alveolar ventilation | L gas/min | `AlveolarCompartment.alveolar_ventilation_l_min` |
| $`Q`$ | Cardiac output | L blood/min | `PatientCompartments.cardiac_output_l_min` |
| $`Q_i`$ | Blood flow to tissue group $`i`$, formed as $`f_iQ`$ and never stored | L blood/min | `TissueGroup.blood_flow_l_min_at` |
| $`f_i`$ | Fraction of cardiac output reaching tissue group $`i`$, so that $`Q_i = f_iQ`$ | dimensionless | `TissueGroup.perfusion_fraction` |
| $`\mathrm{MAC}_\%`$ | The agent's alveolar concentration at 1 MAC, at age 40. It is used only as a display divisor and appears in no governing equation | percent | `AgentParameters.mac_percent` |
| $`\lambda_{b:g}`$ | Agent blood:gas partition coefficient, stored once per patient in the venous pool | dimensionless | `PatientCompartments.blood_gas_partition_coefficient` |
| $`\lambda_{i:g}`$ | Tissue:gas partition coefficient for group $`i`$, which is the coefficient the agent data files store | dimensionless | `TissueGroup.tissue_gas_partition_coefficient` |
| $`\lambda_{i:b}`$ | Tissue:blood partition coefficient for group $`i`$, derived as $`\lambda_{i:g}/\lambda_{b:g}`$ and never stored | dimensionless | `TissueGroup.tissue_blood_partition_coefficient_for` |
| $`M_C`$ | Agent stored in the breathing circuit | L equivalent gas | `BreathingCircuit.agent_amount_l` |
| $`M_A`$ | Agent stored in alveolar gas | L equivalent gas | `AlveolarCompartment.agent_amount_l` |
| $`M_v`$ | Agent stored in venous blood | L equivalent gas | `VenousBloodCompartment.agent_amount_l` |
| $`M_i`$ | Agent stored in tissue group $`i`$ | L equivalent gas | `TissueGroup.agent_amount_l` |

A symbol may be defined by the model but have no expression of its own in the
implementation. For such a symbol, the Code cell holds an em dash followed by
what the code reads in its place. $`F_a`$ is the only such symbol.

The two tissue coefficients are related by
$`\lambda_{i:g} = \lambda_{i:b}\lambda_{b:g}`$. The agent data files store
$`\lambda_{i:g}`$ and $`\lambda_{b:g}`$, and $`\lambda_{i:b}`$ is derived from
them. This is why § "Tissue compartments" below writes the tissue capacity as
$`V_i\lambda_{i:b}\lambda_{b:g}`$ but computes it as the equivalent single
multiplication $`V_i\lambda_{i:g}`$. Both symbols name their two phases in
order, and so do both identifiers. They do so because the primary literature
has no convention that would let a reader supply a missing phase. Baker and
Farmery's 2011 review gives one quantity three names in a single chapter: the
tissue-gas partition coefficient (p. 569), the tissue-blood partition
coefficient (p. 570) and the blood tissue partition coefficient (Table 2). Its
Eq. (4) settles the quantity as tissue:blood. `docs/references/README.md` has
the full citation.

## Compartment capacities

### Gas compartments

The equivalent agent amount in the breathing circuit is:

$$
M_C = V_C F_I
$$

The equivalent agent amount in the alveolar gas compartment is:

$$
M_A = V_A F_A
$$

Therefore:

$$
F_I = \frac{M_C}{V_C}
$$

and:

$$
F_A = \frac{M_A}{V_A}
$$

### Blood compartments

The blood:gas partition coefficient relates the concentration of agent
dissolved in blood to the gas-phase concentration at equilibrium.

**The patient holds one blood:gas coefficient.** The agent's parameter file
stores it, and the model writes it once, into the venous pool. The lung's
uptake term and every tissue group's tissue:blood coefficient read that one
value, and the tissue groups store none. The pool refuses a second value, and
the patient refuses a replacement pool with a different one. If each group
kept its own copy, the copies could disagree and no check would fire. A pool at
0.1 beside groups at sevoflurane's 0.65 would still conserve agent, and the run
would give uptake curves that look plausible and are wrong.
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->

Arterial blood has no compartment, capacity or amount balance of its own.
Instead, $`F_a \equiv F_A`$ at every instant, for the reasons § "Model
boundary" gives.

The agent amount stored in venous blood is:

$$
M_v = V_v \lambda_{b:g} F_v
$$

Therefore:

$$
F_v = \frac{M_v}{V_v\lambda_{b:g}}
$$

### Tissue compartments

For tissue group $`i`$:

$$
M_i = V_i \lambda_{i:b}\lambda_{b:g}F_i
$$

Therefore:

$$
F_i =
\frac{M_i}
{V_i\lambda_{i:b}\lambda_{b:g}}
$$

The effective tissue capacity is:

$$
C_i =
V_i\lambda_{i:b}\lambda_{b:g}
$$

Written equivalently with the stored tissue:gas coefficient, it is:

$$
C_i =
V_i\lambda_{i:g}
$$

which is the single multiplication that `TissueGroup.capacity_l` computes.

Either way, the same relationship may be written:

$$
M_i = C_iF_i
$$

**For developers.** `PatientCompartments.from_parameters` writes the agent's
blood:gas coefficient once, into the venous pool. The lung's uptake term and
every tissue group's tissue:blood coefficient read it through
`PatientCompartments.blood_gas_partition_coefficient`.

## Tissue groups

Version v0.1.0 contains exactly three perfusion-limited tissue groups:

- vessel-rich group;
- muscle; and
- fat.

Each group has:

- a tissue volume $`V_i`$;
- a fraction of cardiac output $`f_i`$;
- a tissue blood flow $`Q_i = f_iQ`$, which is computed from the patient's
  cardiac output whenever it is needed and is not stored on the group;
- an agent tissue:gas partition coefficient $`\lambda_{i:g}`$, which is the
  coefficient stored for each agent;
- an agent tissue:blood partition coefficient $`\lambda_{i:b}`$, derived
  from the tissue:gas coefficient and the patient's one blood:gas
  coefficient (the group stores no blood:gas coefficient);
- a stored agent amount $`M_i`$; and
- a derived partial-pressure-equivalent fraction $`F_i`$.

Tissue flow is:

$$
Q_i = f_iQ
$$

The flow fractions must satisfy $`f_i > 0`$ and $`\sum_i f_i = 1`$ within a
documented validation tolerance.

Consequently:

$$
\sum_i Q_i = Q
$$

## Governing equations

All flow terms below must be in liters per second. Flows that the user sees
and enters are in liters per minute, so they are converted before they are
used here.

### Breathing circuit

Fresh gas enters at concentration $`F_D`$. A volume of gas equal to the fresh
gas volume leaves through the exhaust, at the current concentration of the
mixed circuit gas, $`F_I`$.

**$`\dot V_F`$ is the flow at the common gas outlet, not the flowmeter
setting.** The balance below uses one $`\dot V_F`$ both for the agent that
arrives and for the gas that leaves, so both must refer to the same stream.
Agent enters at $`\dot V_F F_D`$, which must be the vapour flow that the
vaporizer actually adds. Mixed circuit gas leaves at that same total flow.
$`\dot V_F`$ is therefore the whole gas stream delivered to the circuit, which
is the carrier gas plus that added vapour. The balance is wrong if
$`\dot V_F`$ is read as the carrier gas alone.

A vaporizer adds vapour to the carrier stream. It does not displace part of
that stream. Let $`\dot V_c`$ be the carrier flow, which is what the
flowmeters are set to, and let $`\dot V_v`$ be the added vapour flow. The
delivered fraction is then $`F_D = \dot V_v/(\dot V_c + \dot V_v)`$, and the
two flows are related by:

$$
\dot V_F = \dot V_c + \dot V_v = \frac{\dot V_c}{1-F_D}
$$

The gap between the two flows is small at ordinary dial settings. It is not
small at the top of a desflurane dial. At 2% delivered, the two flows differ
by 2%. The calibrated maximum of the Tec 6 vaporizer is 18%, and this model
uses it as desflurane's dial maximum. At 18% the two flows differ
by 22%. Gas from flowmeters set to 2 L/min then leaves the common gas outlet
at about 2.44 L/min. Suppose a reader takes the interface's fresh-gas-flow
control for a flowmeter setting. That reader is then wrong by the same factor
in the circuit time constant $`V_C/\dot V_F`$, which is the quantity the
wash-in curve is about.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- derived: 22 percent from data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- derived: 2.44 L/min from data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- not-restated: 2 % -->

The interface therefore labels that control "Fresh gas flow", with the gloss
"common gas outlet" on the line below it. The alveolar readout uses the same
two-line form for "end-tidal-equivalent", for the same reason. The unqualified
name is the one on a real flowmeter bank, and the label must not be shortened
back to that name to fit a layout.

**$`V_C`$ is the assembled breathing system, never a manufacturer's apparatus
figure.** The model has one well-mixed gas compartment in front of the
patient, so the corrugated limbs and the Y-piece can only be inside $`V_C`$.
The machine's circuit volume, which supplies $`V_C`$, is therefore the
assembled total of the apparatus plus the patient circuit.

- The *apparatus* is the workstation's internal volume, including its
  absorber and excluding the breathing circuit. Every volume that
  `docs/machine-survey.md` § "(a1) Apparatus gas volume" found is stated that
  way (Shin et al. cite Dräger's instructions for use for theirs).
- The *patient circuit* is the disposable limbs and Y-piece fitted for the
  case.

A profile author who has an apparatus figure therefore adds a patient-circuit
volume to it and stores the sum. That volume is 1.2 L unless the profile
assumes a circuit with a stated volume of its own. It is the internal volume
of the Hudson RCI circuit that Shin et al. added to each machine's figure
(*BMC Anesthesiol* 2017;17(1):10, PMID 28103806; read at full text 2026-10-04
from PubMed Central, PMC5248460).

The stored total leaves out the circuit's reservoir bag, whatever the source of
the figure. Shin et al.'s sums leave out the 3 L bag of their set-up, so a
total built from them already does. Adding the bag would nearly double a
Perseus A500's assembled 3.3 L.

If the apparatus figure is stored alone, $`\tau_C`$ is shortened by the
circuit's share. A Perseus A500's 2.1 L gives 31.5 s at 4.0 L/min, where its
assembled 3.3 L gives 49.5 s, so the first value is 36% short. No automatic
check can catch that error, because both are correctly cited volumes. This rule
applies until the machine and the patient circuit get separate volumes, as
`docs/machine-abstraction.md` plans. The shipped 6.0 L is such a total, and no
source divides it between the two (§ "Parameter provenance").
<!-- derived: 31.5 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- derived: 49.5 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

Ventilation transfers gas between the breathing circuit and the alveolar
compartment.

The circuit amount balance is:

$$
\frac{dM_C}{dt} = \dot V_F(F_D-F_I) - \dot V_A(F_I-F_A)
$$

Because:

$$
M_C = V_CF_I
$$

the concentration equation is:

$$
\frac{dF_I}{dt} = \frac{\dot V_F}{V_C}(F_D-F_I) - \frac{\dot V_A}{V_C}(F_I-F_A)
$$

When alveolar ventilation is zero, this reduces to the v0.0.2 circuit equation:

$$
\frac{dF_I}{dt} = \frac{\dot V_F}{V_C}(F_D-F_I)
$$

For constant input and no patient connection, the exact v0.0.2 solution still
applies:

$$
F_I(t+\Delta t) = F_D+\left[F_I(t)-F_D\right]\exp\left(-\frac{\dot V_F\Delta t}{V_C}\right)
$$

The existing v0.0.2 analytic reference tests must continue to pass unchanged.

**The exhaust is a semi-closed circle's, and it runs whenever fresh gas
runs.** $`\dot V_F`$ appears twice in the balance above and does two
different jobs. It is the rate at which agent arrives, and it is the rate at
which mixed circuit gas leaves. The two jobs share one symbol because the
outflow is not an independent quantity here. The outflow is fixed equal to
the inflow, which is what a circle system does while gas is passing through
its surplus gas valve. Two of this model's own assumptions fix it there.
First, both gas compartments have fixed volumes. Second, the modeled patient
takes up no net volume, since "Alveolar gas" removes agent from a constant
$`V_A`$ without removing gas from it. Every litre admitted therefore has to
leave, and the exhaust is the only way out.

**A real circle spills less than it is given**, by the volume the patient
removes. That volume is the oxygen consumed, the vapour taken up, and any
nitrous oxide. Carbon dioxide is not a fourth term. Carbon dioxide gives back
to the circuit the volume that the blood took from the circuit, and the
absorbent then removes it again, so it nets to nothing here. The gap is an
absolute rate rather than a share of the flow. So it is small where the flow
is large, and it is the whole of the spill where the flow is small. For the
reference adult it is on the order of 0.3 L/min early in a case. About
240 ml/min of that is oxygen, from the $`10M^{3/4}`$ allometry that
"Parameter provenance" takes from page 17 of Lowe and Ernst. That allometry is
Brody's interspecies metabolic relation, not a measurement in an anaesthetised
adult, and it carries that section's caution with it. The rest is the
65 ml/min of sevoflurane vapour that "Alveolar gas" computes at the early
induction gradient, which falls away as uptake does. Against the 4.0 L/min
that this project ships as its opening fresh gas flow, the gap is 6 to 8%.
Against the 0.5 L/min that the supported range also allows, it is half or
more.
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- derived: 6 to 8 percent from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->

**At the bottom of that range the valve shuts**, which is closed-circuit
technique. Fresh gas is titrated down to uptake, with no surplus left to vent.
A machine may also shut the valve as a mode of its own. Meyer et al., who
wrote for the manufacturer of one of the machines this project has surveyed,
state: *"In the automatic controlled mode of the Zeus anesthesia machine, the
surplus gas valve can be closed to prevent any loss of gas volume"* (Meyer
J-U, Kullik G, Wruck N, Kück K, Manigel J. Advanced technologies and devices
for inhalational anesthetic drug dosing. In: Schüttler J, Schwilden H, eds.
*Modern Anesthetics.* Handbook of Experimental Pharmacology vol. 182. Berlin:
Springer; 2008:451–470; read at full text 2026-09-19, with the record and
route in `docs/machine-survey.md` § "Sources").

**Neither is modeled here, and the reason is not the exhaust term.** The
circuit equation is the part that still applies with a shut valve. Gas that
the patient's uptake pulls out of the circuit leaves at $`F_I`$, exactly as
spilled gas does. So $`\dot V_F(F_D-F_I)`$ is the same balance either way, and
$`F_I`$ is not what changes. Two other things change.

- **Where that agent goes.** "Circuit exhaust" counts the whole of
  $`\dot V_FF_I`$ as leaving the system. With the valve shut, that agent is
  carried into the alveolus and kept there. That needs the extra inspired gas
  that "Alveolar gas" writes as
  $`\dot V_A + \sum_k \dot M_{\mathrm{uptake},k}`$, and this model does not
  include that term.
- **What sets the flow.** A closed circuit's fresh gas flow *is* the
  patient's total uptake, so $`\dot V_F`$ stops being a free input and
  becomes an output. This model computes no part of that sum. It does not
  track oxygen, which is the largest of the three streams. Its fixed alveolar
  volume also assumes that the agent it does compute removes no volume at
  all.

So closed-circuit operation is blocked twice over. It is **not** a fourth
member of the three "Known limitations" entries that the fixed alveolar
volume blocks by itself. Lifting that constraint is necessary here but not
sufficient. An oxygen-consuming patient is the other half, and this model has
no such patient.

**Setting the removal rate to zero and leaving the rest alone would be
wrong.** Such a model runs without error and gives a plausible curve. The
circuit settles at $`F_I = F_A + \dot V_FF_D/\dot V_A`$. With the shipped
4.0 L/min fresh gas flow, the reference adult's 4 L/min alveolar ventilation
and a 2% dial, the circuit settles two percentage points above alveolar. In
the steady state, every litre of delivered agent reaches the patient, as in a
closed circuit. But it is not a closed circuit, because nothing ties the fresh
gas flow to uptake. At 4.0 L/min, for the same dial, the vaporizer adds agent
about thirteen times faster than at the 0.3 L/min that this patient's uptake
would set. Closed-circuit operation is a property of the machine, and one
coefficient switched by a condition is the wrong way to model it.
`docs/machine-abstraction.md` reserves a place for it, a `closed_circuit`
removal strategy, recorded there as not implemented.
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- not-restated: 2 % -->

**For developers.** The machine profile's `circuit_volume_l` supplies $`V_C`$, so it holds
the total of the apparatus and the patient circuit. Nothing checks that a stored volume is
that total. `check_provenance` in `tools/doc_check.py` checks only that each stored number
appears in this document. The planned split in `docs/machine-abstraction.md` adds an
`apparatus_volume_l`. Desflurane's 18% is stored as `max_delivered_concentration_percent`.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

### Alveolar gas

Ventilation moves gas between the circuit and the alveolar compartment.

Pulmonary blood flow enters the lungs at the venous concentration $`F_v`$. It
leaves in equilibrium with alveolar gas, at $`F_A`$.

The alveolar amount balance is:

$$
\frac{dM_A}{dt} = \dot V_A(F_I-F_A) - Q\lambda_{b:g}(F_A-F_v)
$$

Because:

$$
M_A = V_AF_A
$$

the alveolar concentration equation is:

$$
\frac{dF_A}{dt} = \frac{\dot V_A(F_I-F_A) - Q\lambda_{b:g}(F_A-F_v)}{V_A}
$$

Alveolar gas has no single time constant. If ventilation acted alone, that is,
at $`Q = 0`$, it would turn the alveolar volume over with:

$$
\tau_A^{\mathrm{vent}} =
\frac{V_A}{\dot V_A}
$$

using compatible time and flow units. For the reference adult, where
$`V_A = 2.5`$ L and $`\dot V_A = 4`$ L/min, this is 37.5 s.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->
<!-- derived: 37.5 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->

That quantity is not the time constant of the coupled system, and the model
does not offer it as a derived output. Two things separate it from what a run
exhibits. First, blood uptake is a second exchange term that
acts on the same compartment. If $`F_I`$ and $`F_v`$ are held fixed, $`F_A`$
relaxes with the time constant $`V_A/(\dot V_A + Q\lambda_{b:g})`$. For the
reference adult on sevoflurane, that is 20.7 s rather than 37.5 s. Second,
$`F_I`$ and $`F_v`$ are not fixed. They are state variables of the same system.
So the alveolar trajectory is a sum of exponentials over all six modeled
compartments, and no single constant describes it. A
$`\tau_A^{\mathrm{vent}}`$ presented as "the alveolar time constant" would be a
plausible number for a rate that the simulation does not exhibit.
<!-- derived: 20.7 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4, default_cardiac_output_l_min = 5 -->
<!-- derived: 20.7 s from data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->

**The coupled system's own time constants.** The model's six concentrations
change together. Any run is the level set by the delivered fraction plus six
exponential terms, each with its own time constant. The delivered fraction
does not affect those time constants. They depend only on the three flows, the
volumes and the partition coefficients. The table gives them at the reference
adult's default flows and at the corner of the supported settings, where fresh
gas flow, alveolar ventilation and cardiac output are all at their maximums of
10, 12 and 10 L/min. The circuit volume is the reference circle system's 6 L in
both.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12, MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

| Flows (L/min): fresh gas, $`\dot V_A`$, $`Q`$ | Agent | $`\tau_1`$ (s) | $`\tau_2`$ (s) | $`\tau_3`$ (s) | $`\tau_4`$ (s) | $`\tau_5`$ (s) | $`\tau_6`$ (s) | Period of the fastest pair (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4, 4, 5 (defaults) | sevoflurane | 15.8 | 15.8 | 63.1 | 365 | 10 300 | 167 000 | 753 |
| | isoflurane | 13.7 | 13.7 | 54.5 | 426 | 11 500 | 187 000 | 466 |
| | desflurane | 16.6 | 16.6 | 66.1 | 264 | 6 020 | 95 500 | 1 540 |
| 10, 12, 10 (corner) | sevoflurane | 6.89 | 6.89 | 27.2 | 161 | 4 890 | 81 300 | 398 |
| | isoflurane | 6.02 | 6.21 | 22.4 | 190 | 5 280 | 89 500 | none |
| | desflurane | 7.17 | 7.17 | 29.1 | 114 | 2 890 | 47 000 | 384 |
<!-- derived: 15.8 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, venous_pool_volume_l = 1.222, default_alveolar_ventilation_l_min = 4, default_cardiac_output_l_min = 5, tissue_groups.vessel_rich.volume_l = 6, tissue_groups.vessel_rich.perfusion_fraction = 0.76, tissue_groups.muscle.volume_l = 33, tissue_groups.muscle.perfusion_fraction = 0.18, tissue_groups.fat.volume_l = 14.5, tissue_groups.fat.perfusion_fraction = 0.06 -->
<!-- derived: 15.8 s from data/machines/reference_circle_system.json circuit_volume_l = 6, default_fresh_gas_flow_l_min = 4 -->
<!-- derived: 15.8 s from data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65, tissue_gas_partition_coefficients.vessel_rich = 1.1, tissue_gas_partition_coefficients.muscle = 2.4, tissue_gas_partition_coefficients.fat = 34 -->
<!-- derived: 13.7 s from data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3, tissue_gas_partition_coefficients.vessel_rich = 2.1, tissue_gas_partition_coefficients.muscle = 4.5, tissue_gas_partition_coefficients.fat = 70 -->
<!-- derived: 16.6 s from data/agents/desflurane.json blood_gas_partition_coefficient = 0.42, tissue_gas_partition_coefficients.vessel_rich = 0.54, tissue_gas_partition_coefficients.muscle = 0.97, tissue_gas_partition_coefficients.fat = 13 -->

Three things follow from the table.

- **The fastest time constant is 13.7 to 16.6 s at the default flows, and 6.02
  to 7.17 s at the corner.** The corner is not where the model is fastest,
  though. A search over all three flows for each agent found the fastest time
  constant anywhere in the supported settings to be 5.83 s. That is isoflurane
  at 10 L/min of fresh gas, 12 L/min of ventilation and 9.32 L/min of cardiac
  output. For sevoflurane and desflurane the fastest is at the corner. No
  change in the model is faster than 5.83 s. § "Supported simulation step"
  compares the step with it.
- **The slowest time constant is the fat group's, at 47 000 s (13 hours) to
  187 000 s (52 hours).** It is about 5 700 to 14 900 times the fastest. Many
  numerical methods would then need steps short against the fastest time
  constant to stay stable, over runs long enough for the slowest to matter.
  The exact method of § "Selected method (as implemented)" has no such limit.
- **In five of the six rows, the two fastest time constants are one
  oscillating pair, so they are equal.** Gas moves both ways between the
  circuit and the alveoli, and blood carries agent from the alveoli through the
  tissues and back. Exchange around such a loop allows an oscillation, but it
  cannot be seen. Its period is 384 to 1 540 s, and over half a period it
  shrinks by a factor of at least $`e^{17}`$, about $`2.5\times10^{7}`$. At
  the corner, isoflurane's two fastest are separate and do not oscillate.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->

A test recomputes every figure in the table from its own independent copy of
the equations. It fails when a change to a parameter file or to the equations
moves any of them, and its message says to re-derive this table. On 2026-11-01
the model's code agreed with those figures to within a relative difference of
3 × 10⁻¹⁵.

The pulmonary uptake rate is:

$$
\dot M_{\mathrm{pulmonary}} = Q\lambda_{b:g}(F_A-F_v)
$$

A positive value represents net uptake from alveolar gas into blood. A negative value represents net return from blood to alveolar gas during washout.

**The alveolar volume is held constant, and that is what excludes nitrous
oxide.** The substitution $`M_A = V_AF_A`$ above treats $`V_A`$ as a constant
and divides through by it. The model's code does exactly that, and keeps the
volume fixed for the whole step. Ventilation carries the same volume in and
out. No term adds inspired gas to replace the agent that blood takes up. That
treatment is correct for the agents this model ships and wrong for nitrous
oxide, as the arithmetic below shows.

Compare the pulmonary uptake rate above with alveolar ventilation at the early
induction gradient, where $`F_v \approx 0`$. Use the reference adult, with
$`Q = 5`$ L/min, $`V_A = 2.5`$ L and $`\dot V_A = 4`$ L/min:
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5, alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->

| Gas | $`\lambda_{b:g}`$ | $`F_A - F_v`$ | $`\dot M_{\mathrm{pulmonary}}`$ | Of $`\dot V_A`$ |
| --- | --- | --- | --- | --- |
| Sevoflurane at 2% | 0.65 | 0.02 | 0.065 L/min | 1.6% |
| Nitrous oxide at 70% | 0.47 | 0.50 | 1.18 L/min | 29% |
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 1.6 percent from data/patients/reference_adult.json default_cardiac_output_l_min = 5, default_alveolar_ventilation_l_min = 4 -->
<!-- derived: 1.6 percent from data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- not-restated: 2 % -->

The last column decides the question. For sevoflurane, uptake removes 1.6% of
each inspired alveolar volume. A fixed volume can ignore that, and this model
does. For nitrous oxide, uptake removes 29%. That removal *is* the
concentration effect. The gas left behind is concentrated by the volume that
departed, and replacement inspired gas is drawn in to fill the deficit. A
fixed-volume compartment represents neither half of the effect.

**Nitrous oxide's $`\lambda_{b:g} = 0.47`$ above is the conventional textbook
figure and is not a stored parameter.** This project ships no nitrous oxide
parameter file at all. The value is used here only to size the comparison.
Adopting it would need an entry of its own that meets the standard set in
"Source hierarchy".

**One constraint, not three omissions.** "Known limitations" lists three
separate absent features: nitrous oxide, simultaneous gases, and concentration
or second-gas effects. They are one feature. The fixed alveolar volume blocks
all three, and lifting that constraint unblocks all three. Two standard
formulations lift it. They are equivalent to first order, and a milestone that
adds several gases could adopt either one. The first lets $`V_A`$ change over time, and the
concentration equation gains a volume term:

$$
\frac{dV_A}{dt} = \dot V_{A,\mathrm{in}} - \dot V_{A,\mathrm{out}} - \sum_k \dot M_{\mathrm{uptake},k}
\qquad
\frac{dF_A}{dt} = \frac{dM_A/dt - F_A\,dV_A/dt}{V_A}
$$

The second keeps $`V_A`$ constant and replaces the volume lost to total uptake
with inspired gas. The effective inspired ventilation then becomes
$`\dot V_A + \sum_k \dot M_{\mathrm{uptake},k}`$. It is the smaller change to
this model, and it is the form the classical treatment uses.

Either way, the second-gas effect follows from the alveolus containing more
than one gas. It needs no machinery of its own. So the work for `ROADMAP.md`'s
planned items 6 and 7 is not the sum of two separate pieces. Item 7 is nearly
free if item 6 is built this way. Item 7 is unreachable if nitrous oxide is
bolted on beside a volatile agent. Item 6 already says to model the patient as
a set of substances instead of bolting nitrous oxide on. The alveolar-volume
coupling is the reason.

**For developers.** With the delivered fraction set to zero, the six equations
become $`d\mathbf{F}/dt = A_6\mathbf{F}`$. $`A_6`$ is the 6×6 block of the
matrix that `build_system_matrix` in `core/governing_equations.py` assembles,
in that module's state order. Each of the six terms is $`e^{\lambda_k t}`$ for
one eigenvalue $`\lambda_k`$ of $`A_6`$, with time constant
$`\tau_k = -1/\operatorname{Re}\lambda_k`$. The search for the fastest time
constant used a grid of 11 fresh gas flows, 13 ventilations and 21 cardiac
outputs for each agent, refined along cardiac output.
`test_modal_time_constants_are_the_pinned_ones` in
`tests/reference/test_coupled_dynamics.py` recomputes every figure in the
table from that module's independent transcription of the equations. On
2026-11-01 the eigenvalues of the matrix that `build_system_matrix` assembles
agreed with those figures to within a relative difference of 3e-15. The
alveolar row of `build_system_matrix` divides each of its terms by
`alveolar_volume_l`, and the equation settings keep that volume fixed for the
whole step.

### Arterial blood

The lung's exchange with blood is perfusion-limited, and the model has no
shunt and one alveolar compartment. So all arterial blood has equilibrated
instantaneously with alveolar gas, and $`F_a \equiv F_A`$ at every instant
(see § "Model boundary"). There is no separate arterial amount balance, capacity, or
time constant. Every equation below that references $`F_a`$ uses the current
alveolar fraction $`F_A`$ directly.

### Tissue uptake and return

For tissue group $`i`$, arterial blood enters at $`F_a`$. Venous blood leaves
in equilibrium with the tissue, at $`F_i`$.

The tissue amount balance is:

$$
\frac{dM_i}{dt} = Q_i\lambda_{b:g}(F_a-F_i)
$$

Substituting the tissue capacity gives:

$$
\frac{dF_i}{dt} = \frac{Q_i}{V_i\lambda_{i:b}}(F_a-F_i)
$$

The tissue time constant is therefore:

$$
\tau_i =
\frac{V_i\lambda_{i:b}}{Q_i}
$$

with compatible time and flow units.

At zero tissue flow:

$$
Q_i = 0
\quad\Longrightarrow\quad
\frac{dM_i}{dt}=0
$$

The tissue amount must remain unchanged.

### Venous blood

Blood leaving the tissue groups enters the venous pool. Venous blood leaves
that pool for the lungs at concentration $`F_v`$.

The venous amount balance is:

$$
\frac{dM_v}{dt} = \lambda_{b:g}\left(\sum_i Q_iF_i-QF_v\right)
$$

Because:

$$
M_v = V_v\lambda_{b:g}F_v
$$

the venous concentration equation is:

$$
\frac{dF_v}{dt} = \frac{\sum_i Q_iF_i-QF_v}{V_v}
$$

The instantaneous flow-weighted concentration entering the venous pool is:

$$
F_{\mathrm{tissue\ return}} = \frac{\sum_i Q_iF_i}{Q}
$$

when $`Q>0`$.

At zero cardiac output, the pulmonary and tissue perfusion transfers are zero,
and the model performs no division by $`Q`$.

## Conservation of agent mass

### External delivery

The cumulative delivered agent amount is:

$$
M_{\mathrm{delivered}}(t) = \int_0^t \dot V_FF_D\,dt
$$

### Circuit exhaust

The cumulative exhausted agent amount is:

$$
M_{\mathrm{exhausted}}(t) = \int_0^t \dot V_FF_I\,dt
$$

This term belongs to the semi-closed circle system. For a machine running with
its surplus gas valve shut, the term is zero. That machine needs a different
model. It is not this model with a coefficient turned down. See
§ "Breathing circuit".

### Stored amount

The total stored amount is:

$$
M_{\mathrm{stored}} = M_C+M_A+M_v+\sum_i M_i
$$

Arterial blood contributes no separate term, because it is not a compartment
and contains no independent amount of agent (see § "Model boundary").

### Mass-balance identity

For an initial stored amount $`M_{\mathrm{initial}}`$:

$$
M_{\mathrm{initial}} + M_{\mathrm{delivered}} = M_{\mathrm{stored}} + M_{\mathrm{exhausted}} + \varepsilon_M
$$

where $`\varepsilon_M`$ is the numerical mass-balance residual.

The identity is a bookkeeping statement over whatever terms the model
includes. It would therefore still hold, unchanged, if
$`M_{\mathrm{exhausted}} \equiv 0`$. What would no longer hold is the
interpretation of that term as agent lost from the system. The section
"Breathing circuit" explains why a shut surplus gas valve is not this model
with its exhaust switched off.

Equivalently:

$$
\varepsilon_M = M_{\mathrm{initial}} + M_{\mathrm{delivered}} - M_{\mathrm{stored}} - M_{\mathrm{exhausted}}
$$

The implementation must report both absolute and relative residuals:

$$
\varepsilon_{\mathrm{absolute}} = |\varepsilon_M|
$$

and:

$$
\varepsilon_{\mathrm{relative}} = \frac{|\varepsilon_M|}{\max(M_{\mathrm{initial}}+M_{\mathrm{delivered}}, M_{\mathrm{scale}})}
$$

Here $`M_{\mathrm{scale}}`$ is a documented small positive reference amount
that prevents division by zero.

**$`M_{\mathrm{initial}}`$ is counted from the system's own parts, which are
set once.** The parts are the circuit, the alveoli, the patient and the
mass-balance check, built together for one agent. Replacing a part of a built
system raises an error. Without that refusal, a replacement part could fail
in two ways:

- A part holding agent that $`M_{\mathrm{initial}}`$ did not count would halt
  the next step on this identity, which would blame the numerics for a swapped
  part.
- An empty part built for another agent would pass the identity, and no check
  would find it.

The refusal applies to the parts themselves. Agent added directly to a part's
stored amount is not refused when it is added. Nor is a tissue group or venous
pool that already holds agent when it is added to the patient. This balance
detects either case at the next step or read.

`tests/unit/test_record_writes.py` walks every class in `core/`. Each field of a
mutable record must either refuse a later write or be checked against a rule,
at the write or by this identity. The test fails on any field that does
neither. A field is exempt only when its entry says why no rule ties it to
another field, or names the open item that will check it.

Two bounds apply, and each one addresses a different question.

**The run-time halt thresholds, as implemented in `core/agent_simulation_validation.py`:**

```text
AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L = 1e-12
AGENT_ACCOUNTING_RELATIVE_TOLERANCE = 1e-9
MINIMUM_RELATIVE_SCALE_L = 1e-15
```

The absolute bound and the minimum scale carry their unit in their names, and
the relative bound has none. A step passes if it meets either bound. The
relative error divides by the starting plus delivered amount, or the minimum
scale if larger, so it never divides by zero before agent is delivered. A step
that fails both bounds stops the run. These thresholds mark where the model
refuses to show a number, not the standard the shipped model is held to.

**The release gate is the relative residual alone.** The reference runs in
`tests/reference/test_multi_agent.py` and
`tests/reference/test_sevo_patient.py` assert it, and they restate it as
`MASS_BALANCE_RELATIVE_GATE`:

```text
MASS_BALANCE_RELATIVE_GATE = 1e-10
```

The gate is relative because the residual is rounding error that accumulates
once per step. The residual therefore scales with how much agent a run has
handled. An absolute bound would measure the delivered concentration and the
run length instead of conservation. The values below were measured on
2026-09-06 with the shipped exact step, over 600 s of wash-in followed by
600 s of washout:

| Agent | Dial | Delivered | $`\varepsilon_{\mathrm{absolute}}`$ | $`\varepsilon_{\mathrm{relative}}`$ |
| --- | --- | --- | --- | --- |
| isoflurane | 4% | 1.60 L | 3.589e-13 L | 2.243e-13 |
| isoflurane | 2% | 0.80 L | 1.794e-13 L | 2.243e-13 |
| desflurane | 4% | 1.60 L | 9.262e-14 L | 5.789e-14 |
| desflurane | 2% | 0.80 L | 4.631e-14 L | 5.789e-14 |

<!-- not-restated: 2 % -->

Halving the dial setting halves the absolute residual exactly. It leaves the
relative residual unchanged to four significant figures.

The gate value comes from the table below. The table gives the worst relative
residual at any step, measured on the same day at two sets of settings. The
first set is the reference runs' own settings. The second set is the corner of
the supported envelope: fresh gas 10 L/min, alveolar ventilation 12 L/min,
cardiac output 10 L/min, and each agent at its calibrated dial maximum.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

| Horizon | Reference settings | Worst envelope corner |
| --- | --- | --- |
| 1200 s, what the reference runs cover | 2.12e-13 | 2.26e-13 |
| 1 h | 2.19e-13 | 1.04e-12 |
| 4 h | 3.75e-12 | 2.88e-12 |
| 8 h | 5.05e-12 | 6.36e-12 |

The gate of 1e-10 leaves about 450x headroom at the horizon that the reference
runs use, and about 16x at 8 h. So neither moving a dial nor lengthening a
case changes what the gate certifies. The gate is an order of magnitude
stricter than the 1e-9 halt threshold. Passing the gate therefore says
strictly more than that the run did not stop. A real conservation defect would
raise the residual by orders of magnitude, not by factors of two.

**The delivered and exhausted totals are kept by a summation that stops
rounding error from building up.** Each total adds one transfer per step.
Ordinary computer addition rounds slightly each time. For a nearly constant
transfer it rounds the same way step after step, so the error grows with the
number of steps. The worst case in the supported settings is desflurane at its
18% vaporizer maximum and 10 L/min of fresh gas, at the shortest step of 1 ms.
That delivers 0.00003 L per step, and 2592 L over the 86.4 million steps of a
24 h run.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

That run was measured four ways on 2026-10-25, each for 24 h. Two
settings of the patient were used. "Default" is the reference adult's alveolar
ventilation of 4 L/min and cardiac output of 5 L/min. "No uptake" sets both to
zero, so that nearly all the delivered agent is exhausted again. Each total's
drift is its relative difference from the true sum of the same transfers,
rounded once. The drift was read every 2,000,000 steps. The residual is
$`\varepsilon_{\mathrm{relative}}`$ as the halt check computes it, and its
worst value was taken over every step.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

| Summation | Patient | Worst drift, delivered | Worst drift, exhausted | Worst residual |
| --- | --- | --- | --- | --- |
| plain | default | 1.0e-9 | 9.1e-14 | 9.77e-10, at 18.96 h |
| plain | no uptake | 1.0e-9 | 1.0e-9 | 1.10e-11 |
| compensated | default | 8.8e-17 | 9.7e-17 | 3.73e-11, at 24 h |
| compensated | no uptake | 2.5e-17 | 9.8e-17 | 4.52e-12 |
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

With plain addition, a correct run came within 2.4% of the halt threshold of
one part in a billion. It would have been halted for agent that it had not
lost. With no uptake, the two totals drifted alike and their errors cancelled
in the residual. With compensated summation, each total stays within the last
digit or two of the exact sum for the whole run. The remaining residual comes
from the model's own step, not the sums. It grows with the run's length and
stays 27 times below the halt threshold at 24 h.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The method is Kahan's compensated summation. Beside each total it keeps the
part that rounding lost on the last addition, and takes it off the next
transfer. The total then stays within about two roundings of the exact sum,
however long the run (Higham, *Accuracy and Stability of Numerical
Algorithms*, 2nd ed., SIAM, 2002, §4.3, equation 4.8). A test checks both
totals against an exact sum at the largest totals the supported settings
reach. Saving and restoring a run carry these correction terms with it, and a
reset clears them.

Clipping a negative stored amount to zero does not repair mass balance. It
must not be used to conceal an unstable update.

**For developers.** Writing a part onto a built system raises a
`SimulationConfigurationError`. The relative error uses
`max(initial + delivered, MINIMUM_RELATIVE_SCALE_L)` as its denominator. With
compensated summation, each total stays within a few units in the last place.
The computed sum of n nonnegative terms is then within $`2u + O(nu^2)`$ of the
exact sum, relative to it, where $`u = 2^{-53}`$ (Higham 2002, §4.3, equation
4.8). At 8.64e7 steps the $`O(nu^2)`$ term is about 1e-24, so the bound does
not grow with the run's length. `tests/unit/test_agent_simulation_validation.py`
checks both totals against an exact sum. `capture_state()` and
`restore_state()` carry the correction terms, and `reset()` clears them. The
measurement script and its logs are kept outside the repository, in the
project's `v0.7.0/pl-xst1/` folder.
<!-- absent: v0.7.0/pl-xst1/ -->

## Numerical method

The model advances in explicit simulation time. Every setting is held constant
over each step (piecewise-constant settings).

The implementation must:

1. derive concentrations from the current stored amounts;
2. evaluate every transfer from one consistent state;
3. carry every internal transfer as an equal and opposite pair, so that no
   compartment can gain what another does not lose;
4. integrate fresh-gas delivery and exhaust by the same method, and over the
   same trajectory, as the compartments whose boundary they cross;
5. advance the cumulative delivery and exhaust amounts;
6. advance explicit simulation time; and
7. calculate the post-step mass-balance residual.

The method in § "Selected method (as implemented)" advances every compartment together in one
step, so no transfer is applied before another, and nothing is held fixed while another value
moves. Requirement 2 is met because every rate is computed from the same state. Requirement 3
is met because each exchange between two compartments removes from one exactly what it adds to
the other, so the total stored amount is unchanged. Requirement 4 is why delivered and
exhausted agent are calculated in the same step.

A step is all-or-nothing. The step writes each compartment in turn, and a check can reject a
value after earlier compartments have been written. A step that cannot be completed must
leave every tracked value exactly as it was before the step. § "Step atomicity" explains why,
and what the run is left with.

**How each limit in this section was chosen.** Each limit below has a reason,
and the subsection named after it gives the measurements.

- **The largest step, 0.1 s.** Each step is exact, so accuracy does not set it. It sets how
  late a dial change reaches the model. For an ordinary dial change, the delay causes about a
  tenth of the error that one standard deviation in a measured partition coefficient causes.
  For an abrupt ventilation change, it causes about twice the error of one standard deviation.
  The screen is redrawn every 0.2 s, so a shorter step would not show. See § "Supported simulation step".
- **The smallest step, 1 ms.** It is the finest step at which the results have
  been tested and shown to match the results at 0.1 s. Nothing finer has been
  checked, so nothing finer is allowed. See § "Supported simulation step".
- **Compartment volumes from 0.01 to 10 000 L, and partition coefficients from
  0.001 to 10 000.** These limits sit far outside any real patient or agent.
  The arithmetic has been checked against a high-precision calculation across
  the whole range. The smallest volume is 0.01 L because at 0.001 L the error at
  the hardest settings grew to 0.049% of the state over 24 hours. See
  § "The numerical envelope".
- **Delivered and stored fractions up to 0.99.** A gas cannot exceed the
  ambient pressure, so no fraction can pass 1. The model stops at 0.99 so that
  rounding near the top cannot carry a fraction above 1. See § "The numerical
  envelope".
- **The accounting check's tolerance, one part in 10⁹.** In the measured
  runs, a correct 24-hour run's error stayed below 4e-11, at least 25 times
  inside the tolerance. A looser tolerance would let a real accounting error pass. See
  § "The numerical envelope".
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_PARTITION_COEFFICIENT = 0.001 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_PARTITION_COEFFICIENT = 10000 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->
<!-- not-restated: 24 hours -->

**For developers.** Each exchange between two compartments appears in the
system matrix as a pair of off-diagonal entries whose contributions to the
total stored amount cancel. `tests/unit/test_governing_equations.py` checks
that cancellation as a property of the matrix.

### Step atomicity

A partially applied step leaves some compartments at the new time and others at the old time.
The model never produced that set of numbers at any instant, yet on screen they cannot be told
apart from numbers it did produce. The project prefers an obvious failure to a
plausible-looking number, so a failed step must be undone.

Before each step, the model saves every value it tracks, and it puts them back if the step
fails (`AgentUptakeSystem.advance()`). The model then holds the last completed step. That is a
real result at a real simulation time, which the interface may display and a reader may reason
about. The error raised (`SimulationNumericalError`) names the failed check and the step size,
so nobody has to infer the cause from the numbers.

The values saved are the eight that change from step to step, plus the starting amount of the
mass-balance check. The eight are the circuit's inspired fraction, the alveolar amount, each
of the three tissue amounts, the venous amount, and the total agent delivered and exhausted so
far. Settings and parameters are not restored. Restoring cardiac output, for example, would
undo a change that the run had accepted. If the circuit volume has changed, a restore puts
back the saved amount of agent rather than the saved fraction, and the volume stays at its
setting.

Undoing the step does not let the run continue. The model reached a state it could not step
from, so the step would fail again and the run must stop anyway. Undoing it decides only what
the screen may *show* while the run is stopped.

Three constants are set to 0.1 s, and each of them states a different thing:
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

```text
MAXIMUM_SIMULATION_STEP_S  = 0.1                   # core/simulation_step.py
SIMULATION_STEP_S          = SimulationStep(0.1)   # app/dashboard_frame.py
SIMULATION_TICK_INTERVAL_S = 0.1                   # app/dashboard_frame.py
```

`MAXIMUM_SIMULATION_STEP_S`, 0.1 s, is the largest step the model supports, and
`MINIMUM_SIMULATION_STEP_S`, 1 ms, is the smallest. Both limits are allowed values. A
`SimulationStep` cannot be built outside that range, and `AgentUptakeSystem.advance()` and
`SimulationState.advance()` accept only a `SimulationStep`. `SIMULATION_STEP_S` is the step
the interface takes, set at the upper limit on purpose. § "Supported simulation step" gives
the timing error this accepts and why the two are equal. The two values are set separately
and are equal only in this configuration, which is why they have separate names.
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

`SIMULATION_TICK_INTERVAL_S` is not a step. It is how often the program updates, in *real*
seconds. It equals the step because real-time playback means one step per update. The
playback speed is the ratio between the two: each update takes
`multiplier × tick interval ÷ step` whole steps. Written that way, "60× real time" is a claim
that a test can check. If the two shared one name, someone could change how often the program
updates, to suit a different computer, without recomputing the speeds. Every speed on screen
would then be false, and nothing would fail.

### Selected method (as implemented)

Each step solves the **whole model at once, exactly**. Every setting is held constant during a
step, so within that step the six modelled fractions follow fixed linear equations,
$`dy/dt = Ay + b`$, where $`A`$ holds the rate constants and $`b`$ the constant inputs. Adding
a ninth state whose value is always 1 folds $`b`$ into $`A`$, giving $`dy/dt = Ay`$. The
seventh and eighth states are described below. The exact solution is

$$
y(t+\Delta t) = \exp(A\,\Delta t)\,y(t)
$$

with no truncation error at any step size.

`core/governing_equations.py` builds $`A`$. Each entry of $`A`$ is one term of one balance
equation in § "Governing equations", in the order this document gives them.
`core/matrix_exponential.py` computes $`\exp(A\Delta t)`$ and contains no physiology. Neither
module needs an outside library. The module's docstring gives the method's source and how its
constants were derived.

Two of the nine states are not fractions. They are the running totals of agent delivered to
the circuit and exhausted from it, at the rates in § "External delivery" and § "Circuit
exhaust": $`\dot M_{\mathrm{delivered}} = \dot V_FF_D`$ and
$`\dot M_{\mathrm{exhausted}} = \dot V_FF_I`$. Delivered agent has a simple formula of its own.
Exhausted agent does not, because it depends on the inspired fraction as that fraction changes.
Solving it in the same step meets requirement 4 of § "Numerical method".

**The only error this method leaves is rounding.** Measured on 2026-09-06 over a 3600 s run at
1 MAC, the agent left unaccounted for at any step was at most 13 picolitres, for desflurane,
and less than one part in a trillion of the agent handled for every agent. Rounding scales
with the largest amount in play, which over an hour at desflurane's dial setting is about
43 L of delivered agent.

That error is a thousand times smaller than the check allows, so no accuracy is lost. In
litres, though, it grows with how much agent the run has handled. So a long run routinely
exceeds the check's fixed limit in litres, `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L` (a
millionth of a microlitre), and is then passed by its limit as a share of the agent alone.
Measured on 2026-09-06, the limit in litres was first exceeded after 3452 s at the reference
settings, and after 538 s at the most extreme sevoflurane settings the model accepts.

So the check (`check_agent_accounting`) accepts an error that passes either limit. The limit
in litres catches a gross error early, while little agent has been delivered. The limit as a
share does the checking after that. The reference runs test against the share limit,
`MASS_BALANCE_RELATIVE_GATE` (§ "Mass-balance identity"). A release test on the error in
litres would rest on a claim that depends on the dial setting and stops being true after
about an hour of simulated time.

**The exact step has two consequences.**

First, **a step cannot drive a fraction negative**. Every transfer rate is zero or positive,
so the exact solution cannot take a compartment below zero. `core/matrix_exponential.py`
computes the solution so that this also holds after rounding. So no step size and no
parameter set can drive a compartment negative.

That argument covers the lower limit only. Without rounding, no fraction exceeds the larger of
the delivered fraction and the largest fraction the run started with. Rounding could still
carry a fraction just above 1 from a state already at 1. No supported setting reaches that
state, because every shipped vaporizer maximum keeps each fraction far below 1. The model
also refuses it as an input: the delivered concentration and every starting fraction are
limited to 0.99 of the ambient pressure. Runs started at 0.99 computed fractions at most 0.0033
percentage points above it (§ "The numerical envelope").
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

Second, **a shorter step does not change the answer**. Every supported step gives the same
result to within rounding, and a test (`test_step_refinement_converges`) checks that. That
test cannot show the answer is *right*, because a wrong transfer rate would also give the same
answer at every step. Nor can the mass-balance check, because every transfer between
compartments adds exactly what it removes. The test in § "Independent-solution test" checks
correctness. It compares all six modelled fractions with a separate, independent solution of
the governing equations.

**For developers.** Exhausted agent is $`\dot V_F\int F_I\,dt`$ along the
coupled solution, which the same step matrix integrates. The worst residuals
measured on 2026-09-06 were 1.0e-12 L for sevoflurane, 2.4e-12 L for
isoflurane and 1.3e-11 L for desflurane, and the relative error was at most
9.2e-13 in every case. Conservation is built into the matrix. The arithmetic is done in
fractions, so the equal-and-opposite pairs cancel only to rounding precision, relative to
the largest quantity in play.

Every off-diagonal entry of $`A`$ is a transfer rate, so it is nonnegative.
That makes $`A`$ a Metzler matrix and $`\exp(A\Delta t)`$ an entrywise
nonnegative matrix, whatever the parameters are. `core/matrix_exponential.py`
shifts the matrix before summing its series, so that this also holds in
floating point.

The capacity guard and the rollback in § "Step atomicity" cover two cases. The
first is a state at the top of the range that a caller passes to `resume_at`
or opens a `RunDefinition` from, because those two routes check a state only
from 0 through 1. The second is a model extension whose matrix is not a pure
transfer system.

#### Supported simulation step

`MAXIMUM_SIMULATION_STEP_S` is the largest step at which a run may be taken, and
`MINIMUM_SIMULATION_STEP_S` is the smallest. A step outside that range is refused when it is
chosen, before anything is calculated. The caller can retry with a step inside the range, and
the run it already has stays intact. The two limits have different reasons. The largest step
is a declared limit on how late a control change may reach the model, and it is argued first
below. The smallest step is set by rounding, and it is argued after.

**Accuracy does not set the ceiling.** The exact step has no truncation error
at any step size, and its propagator keeps every fraction in range at any step
size.

What a longer step still costs is **control resolution**. Settings are held
constant across a step, so the step is the interval over which a change to a
control is invisible to the model. At 0.1 s, a slider move is resolved to a
tenth of a second. At 10 s, a change made and reversed inside one step would
never reach the model at all.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**The physical timescale beside the step.** The fastest process in the model, anywhere in the
supported settings, has a time constant of 5.83 s. That is for isoflurane at the highest fresh
gas flow and ventilation, with a cardiac output of 9.32 L/min. At the default flows it is 13.7
to 16.6 s (§ "Alveolar gas"). The 0.1 s step is about a sixtieth of the fastest. So in one
step, the fastest process closes only about 1.7% of its remaining gap, and a control change
one step late moves the values very little. A chart drawn once per step also misses no process.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**The largest step is a declared limit, because no numerical limit was found.** On 2026-09-06
the step was tried from $`10^{-3}`$ s to $`10^{300}`$ s across the supported settings. The
result differed from an independent solution by about $`10^{-14}`$ to $`2\times10^{-12}`$ of a
fraction, and the difference did not grow with the step. Around $`10^{13}`$ s, a displayed
digit is first wrong by a whole count, and the model raises no error below about
$`10^{18}`$ s. So no caller can reach a numerical limit.

How late a control reaches the model gives no natural limit either. A control change takes
effect at the start of the next step, so it is delayed by up to one whole step. The error that
the delay causes in the modelled values is **exactly proportional to the step**, measured over
three manoeuvres and all three agents. Halving the step halves the error, with no point where
it suddenly drops. So no step size makes control timing invisible, and the largest step can
only be a declared limit whose error is measured and stated.

**The tolerance, in percentage points of one atmosphere.** These figures are absolute
concentrations, not counts of the readout's last digit. How many decimals the readout shows is
a display choice (§ "Displayed precision"), and it must not affect the model. The table gives
the worst error over all three agents at the shipped 0.1 s step, caused by a control change
that lands one step late:
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

| Manoeuvre | Worst displacement | Binding agent |
| --- | --- | --- |
| Case opening: dial off to 1 MAC, reference flows | 6.7×10⁻³ pp | desflurane |
| Unperfused load, then perfusion on and dial off | 5.0×10⁻² pp | desflurane |
| Ventilator start at the envelope corner | 1.4×10⁻¹ pp | desflurane |

These figures are judged against the model's own parameter uncertainty, which
comes before both the step and the display. One standard deviation of a single
measured partition coefficient displaces a displayed compartment by
$`9\times10^{-4}`$ to $`6.8\times10^{-2}`$ pp (Yasuda et al. 1989, with the
measurement in § "Displayed precision"). So at 0.1 s, the timing error of an
ordinary control action is about a tenth of one parameter SD. In that
sense the step is fine enough.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**A test keeps both control-timing tables current.** The largest step,
`MAXIMUM_SIMULATION_STEP_S`, rests on these figures alone. On every run,
`tests/reference/test_control_resolution.py` measures them again from the parameter files. It
runs each manoeuvre on time and one step late, and takes the worst difference over all six
displayed compartments. A change to the equations, a partition coefficient, the reference
adult's volumes, the supported input ranges or the step itself changes the test's result
before it can make this section wrong. The test also fixes the step at which the figures were
measured, because the table and the step are one decision.

**What 0.1 s does not buy.** An abrupt manoeuvre's timing error is not kept within one
parameter SD. At this step, a ventilator start shifts the alveolar reading by up to 0.14 pp,
about twice one parameter SD. The error lasts while the ventilator start's effect settles.
Keeping it within one SD would need a step near 0.05 s.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**The step stays at 0.1 s, and that timing is accepted, for three reasons.**
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

1. Halving the step doubles the computation per simulated second. It also changes how the
   interface updates, because `SIMULATION_TICK_INTERVAL_S` is set from the step and the
   playback speeds come from their ratio.
2. The benefit applies only at 1× playback. Above 1×, controls act only every
   `multiplier × 0.1` s (the control grid below), which is longer than the step, so a reader
   at 60× would see no change.
3. Frames are two grid steps apart even at 1×. So a 0.05 s step would resolve
   control timing to half of what the display can show.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

At the shipped step, then, the timing error of an abrupt ventilation change is about twice one
parameter SD. That is the one case where the step adds more error than the parameters do. The
error is small in absolute terms: 0.14 pp, against a 1 MAC of 6.0% for desflurane. A reader
comparing an abrupt ventilation change with a measurement should know that its *timing* is
accurate to a tenth of a second and no better.
<!-- provenance: data/agents/desflurane.json mac_percent = 6 -->

**The figures above are for one step of delay, and at 1× playback a control change waits only
one step.** The table above is the error that the largest step (`MAXIMUM_SIMULATION_STEP_S`)
allows. Above 1×, control timing is coarser. The program computes a whole update's worth of
steps at once, so simulated time stands still for one real update interval and then jumps by
`multiplier × 0.1` s. A setting changed during playback therefore first acts at the next
update. The simulated instants that a reader can reach are `multiplier × 0.1` s apart:

| Playback rate | Control grid | Frames are | Worst displacement per grid step | Second worst | Margin |
| --- | --- | --- | --- | --- | --- |
| 1× | 0.1 s | 0.2 s | 1.4×10⁻¹ pp | 5.0×10⁻² pp | 2.84× |
| 5× | 0.5 s | 1 s | 7.0×10⁻¹ pp | 2.5×10⁻¹ pp | 2.78× |
| 20× | 2 s | 4 s | 2.5 pp | 9.8×10⁻¹ pp | 2.56× |
| 60× | 6 s | 12 s | 5.8 pp | 2.8 pp | 2.11× |
| 300× | 30 s | 60 s | 1.0×10¹ pp | 1.0×10¹ pp | 1.03× |

<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->
<!-- not-restated: 1 s -->

The first three columns are in simulated seconds. "Worst" is the same
measurement that the table above reports, re-run at each rate over the same
three manoeuvres and all three agents (measured 2026-09-06). "Second worst" is
the next manoeuvre down at that rate. The margin is their ratio, computed from
the measurements rather than from the rounded columns beside it.

**Read the worst column as an upper limit over the three manoeuvres.** At every rate, the
worst is the ventilator start with desflurane, and the second worst is the unperfused load then
dial off. That order was measured and could change, so a test
(`test_the_ventilator_start_binds_the_per_rate_table_at_every_rate`) checks it on every run.
The ventilator start leads by 2.84× at 1× but only 1.03× at 300×, which is 3%. At the coarsest
rate the two are equal to the two significant figures the table shows. A parameter change
that swapped them would leave the limit correct but the name of the worst manoeuvre wrong.

**The two manoeuvres converge because their errors level off at different delays.** The
ventilator start's transient is largely over within 30 s, the delay at 300×. So **its error
levels off instead of growing with the delay**. Scaling its 1× figure up in proportion
overstates the 300× figure about four times. The unperfused load's transient is still under
way at 30 s, so its error still grows almost in proportion to the delay. Neither the figures
nor the margin can be scaled between rates, so use the measured values.

**An ordinary dial change is well below both columns.** It is the case opening, a third
manoeuvre, and it is about 21× milder than the worst column at 1×. The ratio narrows to 19× at
20×, 16× at 60× and about 7× at 300×, where the case opening reaches 1.5 pp. Use this
comparison to judge what a learner's own actions cost. To see how far the worst figure stands
above the other abrupt manoeuvres, use the second-worst column. The tens of percentage points
at 300× come from abrupt manoeuvres.

Three things follow.

- **Nothing arrives late.** Each recorded control change carries the simulated time it was
  made (`ControlChange`, `SimulationState.elapsed_s`). The new setting acts from the next step,
  at every rate. So the control record is exact to the step, and no displayed value is stale
  against it. The rate limits only which instants a reader can *choose*.
- **An exact route exists at every rate: pause, change, resume.** No steps are taken while the
  run is paused. So a setting changed during the pause acts from the step on which the run
  resumes. Use this route to time a manoeuvre, and faster playback to watch one.
- **Controls are already timed twice as finely as the screen shows.** The screen is redrawn
  every two updates. So at every rate, a reader sees the run at half the resolution at which
  they can act on it. Applying control changes between the steps of an update, or updating
  more often, would time controls more finely than the screen can show.

The largest supported step and the shipped step are the same number, and the
interface runs at it.

**To get the state after a set time, use the run's definition, not a long step.** A step longer
than the largest step cannot be built: `SimulationStep(30.0)` raises a
`SimulationConfigurationError`. Accuracy is not the reason. The refusal protects the record of
control changes, so that a stepped run is one the interface could have produced, with each
setting held for whole steps. For the state after 30 s or an hour with unchanged settings,
build a `RunDefinition` from the system's `equation_settings()` and `state_vector()`, with
`opened_at_s` set to the time the system has reached (`SimulationState.elapsed_s` for a run
under way). Then move it with `advance_to` and read `state_at`. `opened_at_s` has no default,
so a run partway through a case cannot be opened at zero by mistake. `state_at` computes one
exact solution over the whole interval (§ "The canonical evaluation rule") in place of 300 or
36 000 steps. `test_state_at_matches_a_stepped_run` in `tests/unit/test_run_definition.py`
checks that both routes agree. The application builds its predictions this way.

**The floor.** `MINIMUM_SIMULATION_STEP_S` is 1 ms. It is the one bound on the
step that is numerical.
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

A finer step costs rounding, which the sweep above shows as "a finer step is slightly worse".
Each step adds its change to the stored amount. The finer the step, the smaller that change is
beside the amount, so the same rounding is a larger share of the change. The table below was
measured on 2026-10-03 over 10 000 steps from 60 s into the default sevoflurane wash-in,
against the same span taken in 0.1 s steps or as one exact step. Each row gives the largest
error, as a share of the change, in any of the alveolar, vessel-rich, muscle and fat fractions:
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

| Step | Worst relative error in the change |
| --- | --- |
| 1 ms | 3.3×10⁻¹² |
| 0.1 ms | 2.4×10⁻¹¹ |
| 10 µs | 7.8×10⁻¹⁰ |
| 1 µs | 7.2×10⁻⁹ |
| 10 ns | 3.8×10⁻⁷ |
| 0.1 ns | 1.0×10⁻⁴ |
| 1 ps | 5.8×10⁻³ |
| 10 fs | 3.2×10⁻¹ |

<!-- not-restated: 1 ms -->

<!-- not-restated: 2.4 -->

No error is raised at any of these steps. At $`10^{-14}`$ s, the change over those steps is a
third wrong, and a single step's change is nearly half wrong, yet each is returned as an
ordinary step. From about $`10^{-16}`$ s down, a step changes nothing, and still returns
normally. The error grows with no sudden jump. So, as with the largest step, no step marks
where results become wrong, and the smallest step is chosen rather than forced.

**Where the floor is declared, and what enforces it.** 1 ms is the finest step
at which the solution has been shown to match the shipped step's solution. It
is the bottom of the step sweep above. A test beside the step-refinement gate
(§ "Step-refinement test") drives the model at that step and pins the constant
there. Apart from the tests of the floor itself, no test runs finer than
0.02304 s. The table is a dated measurement and not a gate, because the steps
below its first row are outside the domain and no test can take them. So
lowering the floor needs a new measurement, starting with that test at the new
floor.
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

**The floor also bounds the run's own arithmetic.** At the floor, the supported
run length is 86 400 000 steps. A float represents every whole count up to
$`2^{53}\approx9.0\times10^{15}`$ exactly. Below about $`9.6\times10^{-12}`$ s,
a day would take more steps than that, and `elapsed_s` would round the count
before multiplying it by the step (§ "Simulated time is a count of steps, not a
running total").
<!-- derived: 86 400 000 steps from core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- derived: 86 400 000 steps from core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- derived: 9.6e-12 s from core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The smallest step also applies to a compartment stepped on its own, and the largest does
not.** In a run, only `AgentUptakeSystem.advance()` steps the compartments, and it takes a
`SimulationStep`, so no step below the limit reaches them that way. But code can step each
compartment directly, and rounding costs it as much as it costs a run. The table below was
measured on 2026-10-19 over 10 000 steps, with each compartment held at a fraction of 0.01 and
stepped toward 0.02. The compartments were a tissue group with a time constant of 480 s, the
venous pool at 7.8 s and the breathing circuit at 60 s:

| Step | Largest error in what the three changed by, as a share of the change |
| --- | --- |
| 0.1 s | 2e-14 |
| 1 ms | 3e-13 |
| 1 µs | 3e-11 |
| 1e-10 s | 3e-5 |
| 1e-14 s | 4% for the pool and the circuit; the tissue did not change at all |

<!-- not-restated: 1 ms -->

<!-- not-restated: 0.1 s -->

So each compartment's own step method (`TissueGroup.advance`, `VenousBloodCompartment.advance`
and `BreathingCircuit.advance_fresh_gas`) rejects a step below the smallest step, with the
same check and message the run uses. A compartment is not held to the run's largest step,
because that limit is how long a run holds its settings, and a compartment stepped alone at
1 s is correct.
<!-- not-restated: 1 s -->

**A compartment stepped on its own has its own largest step: the supported run length.** One
step cannot cover more simulated time than the span over which the model is claimed to
represent a patient (§ "Supported run length"). Without that limit, a breathing circuit stepped
over an absurdly long time would return an infinite or undefined exhaust. At the limit, a step
covers at most about 1.4 million circuit time constants, far inside what a computer can hold.
The tissue groups and the venous pool give a finite result at any step, but they take the same
limit so that one rule says which steps a compartment accepts.
<!-- derived: 1.4e6 time constants from core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- derived: 1.4e6 time constants from core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- derived: 1.4e6 time constants from core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

A playback update is a whole number of the run's own steps, so
`PlaybackRate.steps_per_tick` takes a `SimulationStep`, as the run does. The spacing of points
on a chart is not held to the smallest step. `RunDefinition` applies each column's spacing only
once, so rounding does not build up beyond one spacing per column. A spacing of a tenth of the
smallest step still matches the run to within 5×10⁻¹⁴. A limit on the spacing would reject
short time axes that the program draws correctly.

**The capacity check reports a state the model cannot enter.** When a step drives an amount out
of range, `AgentUptakeSystem.advance()` raises `SimulationNumericalError`. The step is undone in
full, simulation time does not advance, and the run must stop at the last completed step. No
step can drive a fraction below zero (§ "Selected method (as implemented)"). Rounding can still
carry a fraction just above 1 from a state already at 1, which no supported setting reaches.
The check covers that state, and later model changes whose equations are not pure transfers
between compartments. Too coarse a step never triggers it. The two errors mean different
things. `SimulationConfigurationError` says a setting was rejected and the run can still be
trusted. `SimulationNumericalError` says the run in progress cannot be trusted.

The implementation must not depend on:

- wall-clock elapsed time;
- interface frame rate;
- the interface toolkit;
- filesystem state;
- display size; or
- event-loop scheduling.

A run with identical initial state, settings, events, and simulation steps must produce identical results.

**For developers.** Both step limits are declared in `core/simulation_step.py`.
`SimulationStep` raises a `SimulationConfigurationError` when it is built
outside them. Every function that takes a run's step takes a `SimulationStep`,
so the step is checked once, where it is chosen. For callers that `mypy` does
not check, `SimulationState`, `AgentUptakeSystem.advance()` and
`PlaybackRate.steps_per_tick` reject anything else with a `TypeError`.

The fastest process closes about 1.7% of its gap in one step because
$`1 - e^{-0.1/5.83} = 0.0170`$. In the 2026-09-06 sweep, the disagreement was
U-shaped in the step, with a minimum around 1 to 60 s, because rounding
accumulates once per step. The propagator was entrywise nonnegative at every
one of 4374 (settings, step) combinations, so no fraction is rejected for
stepping coarsely. No method on `SimulationState` takes steps in a loop for a
caller, because no caller in `src/` needs one. The run loop takes a whole
number of steps per tick. The loops over `advance` that remain are test
helpers that drive the controller step by step, as the interface does.

`BreathingCircuit.advance` calls `BreathingCircuit.advance_fresh_gas`. Each
compartment checks the smallest step through `require_compartment_step` in
`core/supported_ranges.py`, which calls `require_at_least_the_smallest_step` in
`core/simulation_step.py`. That is the check `require_supported_simulation_step`
makes for the run. A compartment takes a plain `float` rather than a
`SimulationStep`. Without the compartment's own largest step, a breathing
circuit stepped by about 1e308 s would compute the number of time constants
elapsed (the admitted gas divided by the circuit volume) as `inf`.
`BreathingCircuit.advance_fresh_gas` would then return an exhaust of `inf`
during wash-in, and `nan` (zero times `inf`) when the dial was at or below the
circuit's fraction. The 1.4e6 time constants at the limit are about 300 decades
inside the range of a `float`. The tissue groups and the venous pool stay
finite at any step because `exponential_approach` saturates at equilibrium.

### The numerical envelope

Every compartment volume and every partition coefficient in `core/` has a declared *numerical
envelope*. That is the range in which the arithmetic has been checked. A value outside it is
refused when it is created. Two types in `core/numerical_envelope.py` enforce it, and every
compartment, settings record and parameter file read by `core/parameters.py` uses them.

| Input | Envelope | Shipped values | Type |
| --- | --- | --- | --- |
| The breathing circuit's volume, the alveolar gas volume, the venous pool's volume and each tissue group's volume | 0.01 to 10 000 L | 1.222 to 33 L | `CompartmentVolume` |
| The blood:gas and each tissue:gas partition coefficient, and each tissue:blood coefficient formed from them | 0.001 to 10 000 | 0.42 to 70 | `PartitionCoefficient` |
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_PARTITION_COEFFICIENT = 0.001 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_PARTITION_COEFFICIENT = 10000 -->
<!-- provenance: data/patients/reference_adult.json venous_pool_volume_l = 1.222 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->

**The envelope is not a supported range.** § "Supported input ranges" states
where the model is claimed to represent a patient. The envelope states only
where the arithmetic has been checked against a high-precision evaluation, and
how accurate it was found to be. It is set far outside every shipped value, so
no real parameter set comes near it. A value inside it can still describe no
patient: a 10 mL lung is inside the envelope and is not a lung.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

**What it guarantees.** Both ranges are positive and include their ends. So every product or
quotient of two such values is positive, finite and well within a computer's range. A volume
times a coefficient lies between 0.00001 and 10⁸ L.

**The tissue:blood coefficient is checked where it is formed.** It is the tissue:gas coefficient
divided by the blood:gas coefficient. Two coefficients inside the envelope can give a quotient
far outside it, such as 0.001 over 10 000. One function forms the quotient and checks it
(`tissue_blood_partition_coefficient` in `core/numerical_envelope.py`). It is checked again
whenever either of an agent's coefficients changes, and whenever a patient is built or a tissue
group is replaced. A group's tissue:gas coefficient cannot be changed after the group is built.

**Every input to `core/` has a range that includes its ends, and one sweep tests them.** A value
outside it is refused when created. So a calculation added later works within those ranges,
and nobody has to set limits for it. The table lists each input that has a range, and the
function or type that refuses a value outside it.

| Input | Interval | Refused by |
| --- | --- | --- |
| A compartment volume | 0.01 to 10 000 L | `CompartmentVolume` |
| A partition coefficient, including each tissue:blood quotient | 0.001 to 10 000 | `PartitionCoefficient` |
| Fresh gas flow | 0 to 10 L/min | `FreshGasFlow` |
| Alveolar ventilation | 0 to 12 L/min | `AlveolarVentilation` |
| Cardiac output | 0 to 10 L/min | `CardiacOutput` |
| A tissue group's perfusion fraction | above 0, up to 1, the three summing to 1 | `TissueGroup` and `PatientCompartments` |
| The coupled system's step | 0.001 to 0.1 s | `SimulationStep` |
| A compartment's own step | 0.001 s to 86 400 s | `require_compartment_step` |
| A case instant | 0 to 86 400 s | `CaseInstant` |
| A run's step count | 0 up to the steps that fit in 86 400 s | `require_supported_step_count` |
| The columns of one evaluation | 1 to 100 000 | `RunDefinition.evaluate` |
| A partial pressure, as a fraction of one atmosphere | 0 to 1 | `Fraction` |
| The same, as a percent of one atmosphere | 0 to 100 | `Percent` |
| The delivered concentration in the coupled model | 0 to 99% | `UptakeEquationSettings` and `AgentUptakeSystem.set_delivered_concentration_percent` |
| Each fraction the stepped system is built with | 0 to 0.99 | `AgentUptakeSystem` |
| The state a run opens from, each fraction | 0 to 1, and each cumulative amount of agent 0 to 14 400 L | `require_canonical_state` |
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_PARTITION_COEFFICIENT = 0.001 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_PARTITION_COEFFICIENT = 10000 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- provenance: core/tissue.py PERFUSION_FRACTION_UPPER_BOUND = 1 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/run_definition.py MAXIMUM_WINDOW_COLUMNS = 100000 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

**The state a run starts from has a range too.** One check (`require_canonical_state` in
`core/governing_equations.py`) is shared by a `RunDefinition` and the live system's
`resume_at`. It checks the state's length, that its values are finite, that the entry fixed at
1 is 1, and that each of the six fractions is valid. It also refuses a total of agent delivered
or exhausted below zero or above 14 400 L, the fresh gas of a 24-hour case at 10 L/min. Neither
the delivered nor the exhausted fraction can exceed 1, so no case can move more agent than that.
`tests/unit/test_governing_equations.py` sets each fraction and amount to the nearest storable
value past each limit and expects a refusal.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

A tissue group or the venous pool stepped on its own accepts any blood flow that is finite and
not negative, with no upper limit, by design. A run computes that flow from a cardiac output
that has a limit, so a limit here would refuse nothing a run can produce. The sweep steps both
at the largest flow a computer can hold, and each result stays finite and between its start
and its equilibrium.

`tests/unit/test_numerical_envelope_sweep.py` tests both halves of the claim. The first test
runs every calculation at 96 extreme combinations of volumes and coefficients, called corners.
At each corner, each volume is at one of its limits, and the two coefficients are at one of the
six corners of the region allowed by their own limits and the tissue:blood quotient's limits.
Each flow is set to zero, to the smallest positive number a computer can hold and to its
maximum. The test steps the whole model once at the smallest and largest step, steps each
compartment alone at its own limits, and computes a run over 24 hours by both the chart's
method and the canonical one (§ "The canonical evaluation rule"). Each run washes in to the 0.99 limit,
washes out from it, or sits at it.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

Each result of the first test must be finite. Each fraction must lie from 0
through 1, with no allowance. It must also lie at or below the ceiling, and the
agent balance must close, both to within the error bound that
`core/matrix_exponential.py` states for the propagators that produced it. That
bound uses the squarings each propagator actually needed, with a margin of 3,
so a corner that needs few squarings is held to a few roundings. The worst
result measured on 2026-10-26 reached 2.5 times its bound.

The second test creates each input in the table at each end of its range and at the nearest
value a computer can store past it, and requires the simulator's own refusal. The model's
starting state puts every compartment at the edge at once, so the circuit's fraction, checked
directly, is refused first. A compartment that stores an amount is checked to within the
computer's last digit instead.

One refusal inside the ranges is expected. It is an error, never a wrong value. Computed in one
piece over the whole 24 hours, a run at the hardest corners needs more work than the method
allows, so it is refused, as § "What a long interval costs at the corners" below describes.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The coupled model's inputs stop at 0.99 of the ambient pressure.** A gas's partial pressure
cannot exceed the ambient pressure, which § "Assumptions" fixes at one atmosphere, 760 mmHg.
So no compartment can hold agent at a fraction above 1. The fraction check therefore stays
strict, and the inputs stop below 1 instead. A model of hyperbaric or reduced pressure would
keep the limit of 1 at that pressure. `MAXIMUM_INPUT_FRACTION` in `core/supported_ranges.py` is
0.99. A dial above 99% is refused, and the model refuses to start with any compartment above
0.99. It checks this on the amount of agent each compartment holds, because reading a fraction
back from an amount can add a rounding error in the last digit. A venous pool set to 0.99 read
back as 0.9900000000000001, and the check does not refuse it for that.
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

A computed fraction is still checked only from 0 through 1, because rounding may put it just
above 0.99. For the same reason, the check shared by a `RunDefinition` and `resume_at`
(`require_canonical_state`) allows fractions from 0 through 1, since both start from a state
that a run passed through. The chart checks each fraction it computes before drawing it, so a
chart opened from a state at 1 is refused with `SimulationNumericalError` rather than drawn.
The refusal names the compartment, such as the muscle group, because a learner sees it as the
banner that says why the run halted.

The gap between 0.99 and 1 must exceed the largest overshoot that a run started at 0.99
computes. That excess was measured on 2026-10-31 at all 96 corners, each with the 27
combinations of extreme flows, for a wash-in to 0.99, a washout from it and an equilibrium at
it:

| Path | Largest fraction computed from the ceiling | Excess over 0.99 |
| --- | --- | --- |
| One step of the coupled system, at 0.001 s and 0.1 s | 0.9900000000610623 | 6.1e-11 |
| The canonical path, at five instants up to 86 400 s | 0.9900008107237728 | 8.1e-7 |
| The display path, 60 columns across 86 400 s | 0.9900330968959383 | 3.3e-5 |
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The margin of 0.01 is about 300 times the largest excess. The 0.99 limit belongs to the model,
not to one agent's vapour pressure, so a later gas delivered at a high fraction does not need
a new limit. It is far above every shipped vaporizer maximum, the highest being desflurane's
18%, so no shipped run is affected.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

**Why the chart's excess is the largest.** The excess is error in the calculation itself, far
more than rounding in the stored values could cause. It arises at the hardest corner, with
every volume at 0.01 L, blood:gas at 10 000 and tissue:blood at 0.001. There, a 24-hour chart
of 60 columns computes each column over 1464.4 s, the hardest calculation the method allows.
Repeated over 59 columns, its error adds up to the 0.0033 percentage points measured
(2026-10-31). No shipped agent needs a calculation that hard over 24 hours. The 0.99 limit
keeps even this worst case inside the ambient pressure. Pushing a computed fraction back to 1
would hide an error of this size instead of limiting it.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Neither shorter calculations nor a different method would shrink it, so the chart keeps its
method.** Two remedies were measured on 2026-11-01 at that corner over the chart's 1464.4 s
column, against the same high-precision reference, with no fresh gas:

- **Splitting the interval does not help.** Computed in one piece over 1464.4 s, the worst error
  was 6.0×10⁻⁷. Built from pieces of 100 s, 10 s or 1 s, it was 5.9×10⁻⁷, 5.8×10⁻⁷ and
  5.8×10⁻⁷. Each shorter piece is more accurate, but more of them are combined. "What it costs"
  in `core/matrix_exponential.py` predicts this: the error limit grows with the interval times
  the fastest rate, however the interval is divided.
- **A method that does less work cannot do much less here.** Al-Mohy and Higham's method saves
  work when a matrix's largest rate is much smaller than a simple bound on it suggests. Here
  the two are close, so it would save little. It would also give up the step that keeps the
  result nonnegative after rounding, which every compartment's check relies on (Al-Mohy AH,
  Higham NJ. A new scaling and squaring algorithm for the matrix exponential. SIAM J Matrix
  Anal Appl 2009;31(3):970-989. doi:10.1137/09074721X; read from its abstract).
<!-- not-restated: 1 s -->

No run in the application reaches that chart. A stepped run at the hardest corners stops on the
mass-balance check within a few dozen steps, as shown below, so its chart never spans 24 hours.
The excess, 0.0033 percentage points, is also less than half of the smallest change the display
shows, 0.01 percentage points at two decimals.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**How the bounds were measured.** The products and quotients alone would allow far wider
bounds. The bound that applies comes from the accuracy of each step's calculation.
`core/matrix_exponential.py` halves the interval until it is short, then doubles the result
back up. Each doubling, called a squaring, can double the rounding error, so the number of
squarings sets the accuracy ("What it costs" in that module). The fastest rate in the model
sets how many are needed. The criterion is that **at every corner of the envelope, the 0.1 s
step needs no more squarings than the shipped parameters already need over 24 hours.** That
number is 19, for sevoflurane at the widest supported flows. So no step inside the envelope has
a larger error bound than a calculation that a shipped run already makes.
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The corners were measured on 2026-10-25, with every flow at zero or at the top of its supported
range. Over all 2,560 corners, the 0.1 s step needed at most 19 squarings, a factor of
$`2^{13}`$ below the cap of 32. Two independent sweeps, of 24,576 and 32,768 corners that also
divided cardiac output in other ways, found the same maximum.
`tests/unit/test_numerical_envelope.py` fixes both counts.
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->

The table gives the corners that matter, each compared with a calculation to 70 digits. In each
row, the inputs not named are at the shipped values, and every flow is at the top of its
supported range. "Step error" is the worst error, as a share, in any part of one 0.1 s step's
calculation. "After 24 h" is the worst error, as a share, in a wash-in from zero after 864,000
steps of 0.1 s, against the exact state at 24 h.
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

| Corner | Fastest rate (1/s) | Squarings at 0.1 s | Step error | After 24 h |
| --- | --- | --- | --- | --- |
| Shipped sevoflurane | 0.136 | 0 | 6.0e-16 | 9.6e-11 |
| Alveolar gas 0.01 L, blood:gas 10 000, every tissue:blood 1 | 1.67e5 | 19 | 7.5e-11 | 2.5e-5 |
| Alveolar gas 0.01 L, blood:gas 10 000, tissue:blood as shipped | 1.67e5 | 19 | 5.8e-11 | 2.5e-5 |
| Every volume 0.01 L, blood:gas 10 000, every tissue:blood 0.001 | 1.67e5 | 19 | 1.3e-10 | 2.6e-5 |
| One tissue 0.01 L, its tissue:blood 0.001 | 1.27e4 | 15 | 7.3e-12 | 3.1e-6 |
| Circuit 0.01 L | 36.7 | 6 | 1.4e-14 | 3.1e-9 |
| Venous pool 0.01 L | 16.7 | 5 | 8.0e-15 | 2.9e-9 |
| Alveolar gas 0.001 L, blood:gas 10 000, tissue:blood as shipped (below the 0.01 L floor) | 1.67e6 | 22 | 1.7e-9 | 4.9e-4 |
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

Two rows hold the tissue groups at their shipped tissue:blood coefficients
while the blood:gas coefficient is 10 000. That makes each tissue:gas
coefficient larger than 10 000. No parameter file can build those settings,
although a settings record can. The two rows compare the two floors on the
same reading.

The last row is why the smallest volume is 0.01 L and not 0.001 L. At 0.001 L, the hardest
corner's step error was 1.7×10⁻⁹, against 5.8×10⁻¹¹ for the same corner at 0.01 L. Over a
24-hour run, that error grew to 0.049% of the state.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

The bound on the error after 24 h barely depends on the step. A shorter step needs fewer
squarings, so each step's bound is smaller, but there are proportionally more steps. The
measured error does vary with the step. At the alveolar corner it was 1.8×10⁻⁵ at 0.01 s and
3.0×10⁻⁵ at 0.001 s. With every volume at 0.01 L, it fell from 2.6×10⁻⁵ at 0.1 s to 7.0×10⁻⁷
at 0.01 s and 3.2×10⁻⁷ at 0.001 s. The shipped run needs no squarings, so its error grows with
the number of steps: 9.6×10⁻¹¹ at 0.1 s, 9.6×10⁻¹⁰ at 0.01 s and 4.8×10⁻⁹ at 0.001 s (measured
2026-10-25).
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

**What a long interval costs at the corners.** The canonical evaluation computes one step for
each stretch of unchanged settings (§ "The canonical evaluation rule"). At the hardest corner, a
stretch longer than about 1,610 s needs more than 32 squarings, and `matrix_exponential` refuses
it with `SimulationConfigurationError` instead of returning a result. So a run at that corner is
refused once its settings stay unchanged for about 27 minutes. That is an obvious failure,
which this document prefers to a plausible-looking number. The shipped parameters need 19
squarings over the whole 24 hours.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**What a stepped run does at the stiffest corners: the mass-balance check halts it.** After
every step, the check in § "Mass-balance identity" requires the agent delivered, exhausted and
stored to agree within one part in 10⁹ (`AGENT_ACCOUNTING_RELATIVE_TOLERANCE`). At 19
squarings, each step's rounding is about one part in 10¹⁰, so the unaccounted agent exceeds
that tolerance within a few dozen steps. The run then halts with
`AgentSimulationValidationError`, and the step is undone. This was measured on 2026-10-25 for
sevoflurane at the widest supported flows, with every tissue:blood coefficient set to 1:

| Alveolar gas | Blood:gas | The mass-balance check halted the run at |
| --- | --- | --- |
| 0.01 L | 10 000 | 4.3 s |
| 0.01 L | 100 | 499 s |
| 1.0 L | 10 000 | 934 s |
| 0.01 L | 12 | no halt within 1 h |
| 2.5 L | 100 | no halt within 1 h |
| 0.1 L | 1.3 | no halt within 1 h |
<!-- not-restated: 2.5 L -->
<!-- not-restated: 1.3 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

So the "After 24 h" column above measures one step's calculation repeated 864,000 times, which
is not a run that the model completes at the hardest corners. Inside the envelope, a run either
matches the high-precision calculation to the limits in that table, or is refused with an
error. A blood:gas coefficient of 12, as high as any volatile agent's, ran an hour without a
halt even in a 0.01 L lung.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

**The tolerance stays a fixed $`10^{-9}`$, and a test says when to revisit it.** A tolerance
that grew with the number of squarings would end the halts above, but it would also loosen the
check where learners run. No supported setting needs a squaring. On 2026-10-31, each shipped
agent was stepped with fresh gas at 0, 0.5, 1, 4 and 10 L/min, alveolar ventilation at 0, 1, 4
and 12 L/min and cardiac output at 0, 0.5, 2.5, 5 and 10 L/min, at steps of 0.1 s, 0.01 s and
0.001 s. None of the 900 calculations needed a squaring. Over 24 h at the 0.1 s step, a correct
run's worst error was 3.08 parts in 10¹², for sevoflurane at 2% with 4 L/min of fresh gas,
4 L/min of ventilation and 5 L/min of cardiac output. The worst case in § "Mass-balance
identity", desflurane at 18% at the 1 ms step for 24 h, reached 3.73 parts in 10¹¹.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- not-restated: 4 L/min, 5 L/min -->

A tolerance built by adding up the worst-case rounding of every step would be loose where
learners run. Even with no squarings, a run of 24 hours at the 1 ms step would allow 5.8 parts
in 10⁸, 58 times looser than one part in 10⁹, so a real accounting error could pass on a long run
that a learner can reach. A tolerance widened only by what squarings add would equal one part
in 10⁹ wherever none is needed. It suits a profile that needs squarings, and no shipped profile
does, so it was not built.
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

A test (`test_every_shipped_agent_steps_without_squarings_at_any_supported_setting` in
`tests/unit/test_numerical_envelope_sweep.py`) steps each shipped agent with the patient and
machine that the application uses. It sets each flow at either end of its supported range,
uses the smallest and largest step, and requires that no step needs a squaring. A patient
profile with faster rates, such as a small patient, fails it on the day it ships, and its
message says to widen the tolerance only by what the squarings add.

**What would reopen the limits.** The 0.01 L volume limit was set at the adult supported flows.
A patient profile with much smaller volumes would bring much smaller flows with it. A profile
within ten times of that limit would need this measurement repeated at its own flows. So would
an agent with a coefficient within ten times of either coefficient limit.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->

**For developers.** `tissue_blood_partition_coefficient` builds the quotient as
a `PartitionCoefficient`. `AgentParameters` holds both factors, so it checks the
quotient whenever a factor is written. A `TissueGroup` holds only the
tissue:gas coefficient, so `PatientCompartments` checks each group's quotient
when the patient is built and when a group is replaced.
`require_canonical_state` builds each of the six fractions as a `Fraction`, and
the display path builds each fraction it computes as a `Fraction` before it
wraps the state in a `DisplayState`. A dial above 99% is refused both by a
settings record and by the stepped system's dial setter. Every refusal inside
the ranges is an error from `core/exceptions.py`, never a wrong value.

The figures behind the chart's excess are these. On the canonical path, one
propagator across the whole 86 400 s at the stiffest corners needs more than 32
squarings, so it is refused. In the 60-column chart, each column's 1464.4 s
propagator needs 32 squarings, the most that `core/matrix_exponential.py`
performs. Its worst entry differed from a 50-digit reference by 5.65e-7, about
3e11 units in the last place. That is about $`2^{32}`$ times the unit roundoff,
which is 4.8e-7. The chart applies the propagator 59 times, and 59 times
5.65e-7 is 3.3e-5. The same corner's 0.1 s step needs 19 squarings and differs
from the reference by 1.6e-11. Built from propagators over 1464.4 s, 100 s,
10 s or 1 s, the interval needs 32, 28, 25 or 22 squarings for each piece. For
Al-Mohy and Higham's method, the 1-norm of the system matrix is 1.83e5 /s and
its spectral radius is 1.67e5 /s. Scaling the spectral radius times 1464.4 s
down to the degree-13 Padé approximant's threshold of 5.37 still takes 26
squarings.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- not-restated: 1 s -->

The shipped run's 24-hour propagator measured 3.3e-11 in its worst entry, and
the corners' 0.1 s steps measured up to 1.3e-10. At 0.001 L the stiffest corner
needed 22 squarings.
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->

The bound on one step's rounding is about $`3 \cdot 2^{s} \cdot 2^{-52}`$,
where $`s`$ is the number of squarings the step needs and 3 is the margin the
sweep uses. The mass-balance check compares the whole run's residual, so a
rigorous tolerance would sum that bound over every step. Even at $`s = 0`$, the
sum is 5.8e-10 for 24 h at the 0.1 s step, 5.8e-9 at 0.01 s and 5.8e-8 at the
1 ms step. A tolerance widened only by what the squarings add would be about
$`3 (2^{s} - 1) 2^{-52}`$ per step, summed, which is exactly $`10^{-9}`$
wherever $`s = 0`$.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

## Parameter provenance

No scientific parameter may be added without:

- a full source citation;
- the value and unit used;
- the definition used by the source;
- the temperature or reference conditions when relevant;
- any conversion performed;
- the tissue-group mapping;
- a brief justification for selecting that source; and
- the tier of the hierarchy below that the source belongs to and, where the
  source is not a primary measurement, what the primary literature reports
  instead and by how much it differs.

### Source hierarchy: what may be cited as the authority for a value

A citation records where a number was found. It does not, on its own, say
whether anything was measured there. Three tiers are distinguished. Only the
first may be named as the authority for a stored value on its own strength. A
lower tier may be adopted only on a recorded decision, under the rule stated
below the three tiers.

1. **Primary measurement.** A study that measured the quantity, in the
   species, population and conditions the model claims to represent, and
   reports the value, its dispersion, and its reference conditions. Strum and
   Eger's sevoflurane blood:gas determination (0.686 ± 0.047 at 37 °C, n=19)
   and Yasuda, Targ and Eger's human tissue:blood coefficients are examples
   of this tier.
2. **Secondary synthesis.** A review, textbook, monograph or consensus
   document that collects primary measurements without making one. It is a
   good way to find the primary source, and to record the figure the field
   usually quotes, such as the textbook blood:gas coefficient of 1.4 for
   isoflurane. It cannot by itself be the authority for a stored value,
   because the rounding, and the choice between measurements that disagree,
   happened where the reader cannot see. It can be adopted only on the
   recorded decision described below.
3. **Reference implementation.** Another simulator's parameter set: the
   numbers a working program was built to run on. Gas Man is this project's
   reference implementation. It is useful in two ways. It defines the behavior
   of a widely used teaching tool, so this simulator can be compared with it.
   It also supplies a complete, internally consistent set, where the primary
   literature supplies scattered measurements made in different laboratories
   on different cohorts. **It is still not a source of measurements.** A
   parameter set is assembled to make a program behave. Nobody can recover
   from the program which measurement each number descends from, or what was
   adjusted to make the set consistent. **The program's behavior has itself
   been compared with measurements in patients**, and the agreement is
   materially worse during wash-in than during maintenance. § "Known
   limitations" gives the figures and the limits they set.

**A lower tier may be adopted, but never silently.** The ranking above says
which tier a reader may trust without examining it. It does not forbid storing
a tier-2 or tier-3 number, and nearly half of this project's provenance table
is such numbers (§ "Where this project stands", below, gives the counts). What
the ranking forbids is an adoption the reader cannot see. So a stored value
whose authority is not a primary measurement must carry three things, and
every such value carries all three today:

- **The tier, on the entry itself, with the values it covers.** Each source
  entry in the data file records its tier in a `tier` field, and the
  project's checks reject a tier outside the fixed list. The entry's
  `authority_for` field lists the stored values that rest on it.
- **Why no tier-1 source was adopted.** This goes on the entry, or in the
  file's `provenance_gap` where the whole file is in that state.
- **The date and whose decision it was**, where a lower tier is adopted in
  preference to an available primary source rather than for want of one.
  The three blood:gas coefficients are the worked example. Primary
  measurements exist for all three, and the project owner decided on
  2026-09-03 to keep the Gas Man values and label them. Each value's
  difference from its measurement is given later in this section.

That bar is higher than the one a tier-1 citation clears. Only two reasons are
admissible. The work of finding a primary source is not one of them:

1. **No primary measurement of *this quantity, in this population* exists or
   is reachable.** The whole reference patient is in this state. That
   includes the parameters that carry a primary citation beside them. Hudgel
   and Devadatta measured awake functional residual capacity, whereas the
   stored volume describes an anaesthetised lung. Cattermole et al. measured a
   different population. Janssen et al. report a muscle mass, whereas this
   model stores a volume. Each parameter's note says which of these cases
   applies, so the citation serves as a comparison and not as a source.
2. **The value belongs to a set whose internal consistency is part of what is
   being modelled**, and replacing it would mean mixing primary measurements
   from different laboratories and cohorts. This is the argument for tier 3
   given above. The three blood:gas coefficients are the worked example. Eger,
   Strum and Eger, Lerman et al., and Esper et al. 2015 did measure them in
   this population, so the first reason does not cover them. But one
   laboratory's blood:gas figure, placed among Gas Man's tissue values, would
   make the simulated curve a mix of two parameter sets with different
   origins. The same objection applies, later in this document, to dividing a
   Gas Man curve by a MAC taken from Mapleson.

The second reason is the narrower of the two. It applies only where the entry
cites the primary measurements with their values and records how far the
stored value differs, so the reader can see what the choice costs. For the
three blood:gas coefficients the stored values sit 0.9% to 26.3% below the
measured ones. Later in this section, each difference is given, with the date
of the decision and the planned route to measured coefficients for all three,
which would remove this reason for them.

Where a primary measurement *is* available and simply has not been adopted,
the entry says so in those words, and its `adopted` field records that no
primary measurement backs the value. A stored value can name a source and
state its tier while no measurement of that quantity supports it. That is
the ordinary case here, and it is why the `adopted` field exists.

**Full texts held on hand are in `docs/references/`, and holding one changes
nothing about its tier.** They are kept so that a claim can be checked against
the source itself. `docs/references/README.md` gives the full citation for
each text. Baker and Farmery's 2011
*Comprehensive Physiology* review of inert gas transport in blood and tissues
is the closest published statement of what this document specifies. For any
individual number in it, the review is a tier-2 synthesis.

**Republication does not promote a value between tiers.** A peer-reviewed
paper that prints a reference implementation's parameter table is still a
tier-3 citation. Both of this project's tier-3 citations are of that kind, and
neither measured a coefficient. De Wolf et al. 2012 is a Gas Man simulation
study, and its Table 1 is the parameter set it fed to Gas Man. Weber et al. 2021
is a Gas Man simulation study that describes the product's standard 70 kg
patient. The two do not even agree on what that set holds. Weber et al.'s
Table 1 prints Gas Man 4.2's 1 MAC as 2.1% sevoflurane and 1.1% isoflurane. De
Wolf et al. state 2.0% and 1.2%, which are the values stored on De Wolf's
authority. Yet every partition coefficient the two print is the same. Citing
either paper as though the value had been measured is the error this section
guards against.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- not-restated: 70 kg -->

**Where this project stands.** Of the 49 rows in the table of stored values
below, 27 are tier 1, 16 are tier 3, four are tier 2, and two adopt no source
of any tier. **Nine of the twelve partition coefficients are Yasuda, Targ and
Eger's human measurements.** These nine are all of the tissue:gas values,
adopted on 2026-09-13 after the stored values were checked against that
paper's Table 1. The other three, the blood:gas coefficients, are the Gas Man
set as published by De Wolf et al., and remain tier 3. Ten of the eleven
reference-patient parameters in
`src/anesthesia_sim/data/patients/reference_adult.json` come from the Gas Man
default patient. The three `mac_percent` values are the MAC values that De Wolf
et al. state they used in their Gas Man simulations. Two tier-2 sources are
cited beside them but not adopted: Mapleson's 1996 meta-analysis and the
age-related iso-MAC charts built on it. The two rows that adopt no source are
the anesthesia machine values in
`src/anesthesia_sim/data/machines/reference_circle_system.json`: a circuit
volume that departs deliberately from the published Gas Man figure, and a
default fresh gas flow with no published counterpart.

**The thirty-one rows that adopt a source other than Gas Man are of six kinds.**

1. **Nine tissue:gas partition coefficients**, three per agent, adopted from
   Yasuda, Targ and Eger 1989 on 2026-09-13. They are human autopsy
   measurements at 37 °C. § "v0.2.0: isoflurane and desflurane" says how they
   were checked, and why the published figures were *not* substituted for the
   stored ones.
2. **The eleventh reference-patient parameter, `venous_pool_volume_l`**, from
   Davis and Mapleson 1981. It is tier 2, adopted on 2026-09-07 on the
   project owner's decision.
3. **Three vaporizer maxima.** Each is the calibrated maximum of a device
   rather than a physiologic quantity, and each cites a primary source: the
   Dräger Vapor 2000 specification for sevoflurane, and published
   vaporizer-performance measurements for isoflurane (Kelly and Kong 2011)
   and desflurane (Johnston et al. 1994, on the Tec 6).
4. **Six MAC-awake rows**, a fraction and a standard deviation for each agent.
   They are adopted primary measurements: Katoh et al. 1993 for sevoflurane
   and isoflurane, and Chortkoff et al. 1995 for desflurane.
5. **Nine liquid-density rows**, a density, its standard deviation and its
   measurement temperature for each agent. They are Laster, Fang and Eger
   1994's primary measurements at 20 °C, adopted on 2026-10-26.
6. **Three molar masses**, ChEMBL's formula masses, adopted the same day. They
   are tier 2 because a molar mass is computed from the molecular formula and
   the standard atomic weights, not measured on the agent. So no tier-1 source
   exists for one (§ "Agent amount").

**Recompute these counts with `python3 tools/source_tier_counts.py` rather
than by hand.** It counts each `sources` entry's `authority_for` list, per file
and in total, and names the source behind every row.

No check compares these counts with this paragraph, so they can go stale
silently. `check_provenance` confirms that a documented key holds its stated
value, but not which tier its source has. Whoever changes a count must check
that the sentence around it is still true.

Of all the stored values, `mac_percent` is the only one used as a divisor for
a displayed value. It is tier 3, from De Wolf et al.'s Gas Man set. It divides
every value shown in MAC multiples, so its tier affects a displayed clinical
value as well as a starting dial position. § "Delivery-limit and MAC
parameters" states what that costs, and § "Known limitations" records it.

Every `sources` entry in every data file names its tier. Each agent's data file
cites the primary blood:gas measurements beside its tier-3 blood:gas value:
Strum and Eger for sevoflurane, Eger for desflurane, Lerman et al. 1984 for
isoflurane, and Esper et al. 2015 for all three. (Their tissue:gas values are
Yasuda et al.'s, adopted as primary, as listed above.) Each entry records the
measured value, the fact that it was **not adopted**, and how far the stored
number differs from it. Against the older measurements the stored values are
sevoflurane −5.2%, isoflurane −11.0% and desflurane −0.9%. Esper et al. 2015
measured all three agents in 120 surgical patients at 37 °C. Against its means
the stored values are sevoflurane −12.2%, isoflurane −10.3% and desflurane
−26.3%, so desflurane has the widest gap in the project, about 3.8 of Esper's
standard deviations. Esper et al. was read from its abstract only.

The Gas Man study that prints this parameter set notes the gap in its own
footnote: its blood/gas coefficients "differ from them observed by Esper et
al." (Weber et al. 2021, Table 1). § "The early wash-in curve against the
published figures" records what Esper's desflurane value would do in this
model. The decision to keep the Gas Man values and label them, rather than
move to the textbook 1.4 or to Lerman's measured 1.46 for isoflurane, was
taken on 2026-09-03. The route to primary values for all three agents is
`ROADMAP.md`'s planned-milestone item 31.

`src/anesthesia_sim/data/patients/reference_adult.json` still adopts no
primary source for any of its eleven parameters, and it records that in those
words. The file also says something specific about each parameter.

**Five carry a measurement cited beside them and explicitly not adopted.**
Each gives the measured value, its reference conditions, and how far the
stored number sits from it. Hudgel and Devadatta measured FRC by helium
dilution in ten healthy men. Read with Wahba's review of the roughly 20
percent reduction under general anaesthesia, that measurement brackets the
lung gas volume. Cattermole et al.'s 686 subjects in the 50–75 kg band give a
median cardiac output of 5.51 L/min, and the stored value is 9.3 percent below
it. Janssen et al.'s whole-body MRI gives a skeletal-muscle mass. Its apparent
agreement with the stored muscle volume is a coincidence, since those men
averaged about 86 kg rather than 70. Heinonen et al.'s PET measurement of
resting adipose perfusion is about half what the stored fat flow fraction
implies. Frayn and Karpe's review supplies the muscle comparison. It also
shows that the fat gap concerns the absolute flow, not the muscle-to-fat
ratio, which the stored fractions get right.

**Six have no comparison, and the file says why for each**, so that the gap
is not taken for an oversight. Two are not measurements. The reference
weight is a label that no equation uses. The venous pool is a well-mixed volume
that sets the 14.7-second mixed-venous time constant. It is not the
physiologic venous blood volume, which is several times larger. One, the
default alveolar ventilation, is a convention: Gas Man's program default. The
remaining three each combine several tissues into one group: the vessel-rich
volume and flow fraction, and the fat volume. No single measurement exists of
what this model means by each of them.

**None of these comparisons changes or promotes a stored value.** A measurement
cited beside a tier-3 number does not source it, which is the second of the
three rules below. The gap between the stored fat perfusion and the measured
one is the largest of the five. § "Known limitations" records it as well,
because it changes the shape of a displayed curve and not only a number in a
file.

**The lineage is Lowe and Ernst's, not Mapleson's.** The note beneath the
Workbook's Model Parameters table (Appendix B, page 168) reads: "Values for
volume, flow and relative flow are taken from Lowe and Ernst, 1981". The book
is *The Quantitative Practice of Anesthesia: Use of Closed Circuit*, Williams &
Wilkins. The Workbook attributes nothing to Mapleson.

**The table supplies seven of the eleven values, not all eleven.** Page
183's "Patient default options" describes the interface controls and carries
no numbers. Alveolar volume, the three tissue volumes and the three flow
fractions are in the table and equal what is stored. Cardiac output appears
only as the sum of the flow column. Reference weight and alveolar ventilation
are not in the table. **The venous pool's 1.0 L is not in the table at all**:
its `Blood` row reads 5.00 L. Lowe and Ernst is the link that decides whether
this chain ends in a measurement or in another compilation. The paragraphs
below show that Lowe and Ernst is itself a compilation, and that the chain
behind it never reaches a measurement.

**A second Workbook page, read 2026-09-15 from the private corpus, carries
three of those four.** Its Appendix C, "Gas Man System Defaults", pages 171–72,
prints the program's `GASMAN.INI` verbatim. Its `[Volumes]` block gives
`CKT=8.0`, `ALV=2.5`, `VRG=6.0`, `MUS=33.0`, `FAT=14.5` and `VEN=1.0`. `[Ratio]`
gives `76`, `18`, `6`. `[Defaults]` gives `VA=4` and `CO=5`. So alveolar
ventilation is stated as a number, and cardiac output does not rest on a column
sum. The venous pool's 1.0 L is in the document after all. Only `weight_kg` is
in neither appendix. The Workbook's prose states it, together with the 4 L/min
alveolar ventilation, in Chapter 13, page 127. **None of this promotes a value
to a higher tier.** These are one program's defaults written down more than
once, tier 3 each time. The stored venous pool no longer uses Gas Man's value
at all.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

**Lowe and Ernst has been read at the source, and the chain does not end
there.** Pages 55–60 and 82–84 were read on 2026-09-08 from an
interlibrary-loan scan. Two papers that use the book had cited it at pages
57 and 83: Lerou and Booij's system model (*Br J Anaesth* 2001;86:12–28) and
Couto da Silva, Mapleson and Vickers' study of Lowe's method (*Br J Anaesth*
1997;79:103–12). Both were read at full text on 2026-09-06. This repository
does not hold the scan, because it is under publisher copyright and the
repository is public. The scan's own record gives the author as Lowe, Harry
J., so his initials are `HJ`, and the Workbook's `HF` is a misprint.

**Page 56 settles the tier question for the book, in one sentence.** Of
figure 4.1b, the table in which the volumes and flows are printed, it says:
"The figure models a 100-kg patient with normal physiologic organ volumes and
blood flows (9, 19, 20, 26)." The book collects those figures and cites them
onward to four references. Chapter 4's own narrative names three of them:
Mapleson, Smith et al. and Zwart et al. Lowe and Ernst is therefore **tier 2,
a secondary synthesis**. The Workbook's upstream source has an upstream source
of its own, and the only provenance chain the reference patient has still ends
in nobody's measurement.

**Those four references are identified, and three of them are models.**
Chapter 4's reference list is on pages 64–65, which were read on 2026-09-10
from a second interlibrary-loan scan. Each reference was matched to its PubMed
record. PubMed holds no abstract and no PubMed Central text for any of the
three papers, and the fourth is a monograph that PubMed does not index. The
paragraphs below report the reading of each at its source.

- **9.** Mapleson, W.W. An electrical analogue for the uptake and exchange of
  inert gases and other agents. *J Appl Physiol* 18:197, 1963. — PMID 13932730,
  [10.1152/jappl.1963.18.1.197](https://doi.org/10.1152/jappl.1963.18.1.197),
  18:197–204. PubMed titles it "An **electric** analogue for uptake and exchange
  of inert gases and other agents", without the book's *the*.
- **19.** Smith, N.T., Zwart, A., and Beneken, J.W. Interaction between the
  circulatory effects and the uptake and distribution of halothane: Use of a
  multiple model. *Anesthesiology* 37:47, 1972. — PMID 5050101,
  [10.1097/00000542-197207000-00008](https://doi.org/10.1097/00000542-197207000-00008),
  37(1):47–58. PubMed indexes the third author as Beneken **J E**.
- **20.** Zwart, A., Smith, N.T., and Beneken, J.W. Multiple model approach to
  uptake and distribution of halothane: The use of an analog computer. *Comput
  Biomed Res* 5:228, 1972. — PMID 5031801,
  [10.1016/0010-4809(72)90084-5](https://doi.org/10.1016/0010-4809(72)90084-5),
  5(3):228–38. PubMed gives Beneken **J E** again, so `JE` is the reading taken
  here. The grounds are the same as for reading Lowe's initials as `HJ`: two
  independent records against one.
- **26.** *Recommendations of the International Commission on Radiological
  Protection*, p. 151. Report of Committee II on Permissible Dose for Internal
  Radiation. Pergamon Press, Oxford, 1960. — Not indexed by PubMed, which does
  not cover monographs. It could not be reached from this project's build
  machine on 2026-09-10: `www.icrp.org`, `journals.sagepub.com` and `doi.org`
  each returned nothing.

References 9, 19 and 20 are **uptake-and-distribution models**. A model
consumes organ volumes and blood flows. It does not measure them. So none of
the three can be where figure 4.1b's figures were measured. Reference 26 is
the only one of the four that is not an anesthetic model. It is cited to a
single page, and that page ends the chain.

**The chain terminates at tier 2, and never reaches tier 1.** Page 151 of the
ICRP report was read on 2026-09-10. It carries **Table 8, "Organs of standard
man — Mass and effective radius of organs of the adult human body"**,
tabulated for a total body of 70,000 g. A "standard man" is a reference
specification agreed by a committee. The document's own title is *Report of
Committee II*. The table gives no citation, sample count or dispersion for any
row. Table 7, on the facing page 150, is different: each of its tissue rows
carries a count in parentheses. Under the hierarchy at the head of this
section, a consensus document that collects primary measurements without
making one is **tier 2**. So the longest provenance chain behind the reference
patient runs Gas Man (tier 3) → Lowe and Ernst (tier 2) → ICRP Committee II
(tier 2). **Nothing on that chain was measured by anybody this document can
name.**

**Table 8 has no blood flows.** It gives mass and effective radius, and
nothing else. Yet Lowe and Ernst cite all four references together for "organ
volumes *and blood flows*". So the perfusion fractions, which set every time
constant this model computes, cannot come from reference 26 at all. They must
come from reference 9, 19 or 20, and all three of those are models.

**Four of Lowe's rows correspond to Table 8 closely enough to be an
inheritance.** The comparison is at 100 kg, where his kilogram column can be
treated as per cent of body weight: brain 2.1 against 2.1, kidney 0.4 against
0.43, heart 0.4 against 0.43, and muscle 42.6 against 43. Five rows do not
correspond: skin 10.0 against 8.7, adipose 15.0 against 14, blood 7.0 against
7.7, lung 0.8 against 1.4, and bone 12.0 against a skeleton of 10 without
marrow or 14.2 with marrow. **The liver is the outlier that matters: 5.7
against 2.4.**
<!-- not-restated: 2.1, 2.4 -->

**That gap has a candidate explanation, from this project's arithmetic rather
than from the book.** Liver 1,700 g plus gastrointestinal
tract 2,000 g plus spleen 150 g plus pancreas 70 g is 3,920 g. That is **5.60%
of 70 kg against Lowe's 5.7%**. This group of organs is the hepatoportal
compartment. An uptake model lumps it together because the splanchnic bed
drains through the liver. No other grouping of Table 8 comes as close. Neither
document says that this is what happened, and the match is no evidence against
either author.
<!-- not-restated: 70 kg -->

**Why the lumping matters here.**
`tissue_groups.vessel_rich.volume_l` is stored as 6.0 L. Lowe has ten
compartments. The only grouping of them that reproduces both that volume and
the stored 0.76 perfusion fraction is kidney + heart + brain + liver, at 8.6%
of body weight. On ICRP's own rows those four organs are **5.36%, which is 3.75
L at 70 kg**. That is 38% below what is stored. So the stored value rests on a
lumping decision made one link up the chain. **No stored value changes because
of this, and none should.** Lumping the splanchnic bed into the liver
compartment is ordinary modelling. § "Tissue compartments" above already
treats the vessel-rich group as one lumped tissue. And nothing here is sourced
to ICRP.
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.volume_l = 6 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**References 19 and 20 measured nothing either.** Both were read in full text
on 2026-09-10. They share one parameter set. Reference 20's Appendix says its
tables "are the same as used by N. Ty Smith in his article … where he gives the
rationals for our choice". So the provenance lies in reference 19. Reference 19
says that the table this chain would need "lists the **assumed** blood
volumes, tissue volumes, and partition coefficients". "Assumed" is the paper's
own word, and it gives no source for any of these values. Its *flows* are
compiled from "several sources, most of which can be found in a recent review".
That review is the authors' own handbook chapter. The awake cardiac output of
5,800 ml/min is taken from Milnor's chapter in *Medical Physiology*, 12th
edition. The compiled flows did not balance, and the authors made them balance.
Total cardiac output was 3,480 ml/min, against regional flows summing to 3,290
ml/min, and "the discrepancy was compensated for by adjusting the values for
skin and skeletal muscle flows". **A stated assumption is not a source, and an
adjusted sum is not a measurement.** So neither paper can be promoted to a
higher tier, and neither is a candidate for adoption.

**They are not the origin of figure 4.1b either.** Reference 19 models a 75 kg
man in twelve compartments: arterial, brain grey, brain white, heart,
well-perfused organs, poorly-perfused tissue, fat and fatty marrow, splanchnic,
skeletal muscle, skin shunt, vena cava, and lung. Lowe has ten rows for a 100
kg patient, and the numbers do not correspond. The vessel-rich equivalent in
reference 19 is 64.0% of cardiac output, against Lowe's 76%. Its fat is 16.3%
of body mass, against Lowe's 15.0%. **So the perfusion fractions still have no
identified origin.** Reference 26 gives masses and no flows. References 19 and
20 give different flows for different compartments. Reference 9, Mapleson
1963, is the last of the four still unread, and reference 20 names him only as
the source of the model *concept*.

**Reference 9 closes the chain. Most of its volumes are reference 26's, and
references 19 and 20 are its table relumped.** Mapleson 1963 was read on 2026-09-10. His Appendix 1 opens:
"*Tissue volumes and blood supplies.* With the following exceptions the volumes
in Table 1 are those for the 'standard man' of the International Commission on
Radiological Protection (I.C.R.P.) (23)…". His reference 23 is that report at
**page 151**, which is Lowe and Ernst's reference 26. So Lowe and Ernst very
likely took the ICRP citation from Mapleson's own reference list. References
19 and 20 are Mapleson's Table 1, lumped and relabelled. When Table 1 is lumped
as Smith's own footnotes describe, it reproduces all **nine of their nine
rows**, and those nine rows sum to 58.04 litres against Mapleson's own 58.04.

**Mapleson's Table 1 is the most honestly sourced document in this chain, and
it still measures nothing.** Its volumes are ICRP's, except for six that he
names one by one. Grey and white matter come from Pittinger et al. The marrows
and bone cortex come from Ellis. He derived skin nutritive himself from forearm
geometry. The arterial-to-venous blood ratio is "taken to be as in dogs". Lung
parenchyma comes from Cander and Forster. The air in the lungs comes from "the
average of all measurements in Dittmer and Grebe in which the average age was
over 20", which "gives a functional residual capacity of 2.5 liters". His flows
are compiled from about twenty sources, with a note on every row. Some rows
come from animals: adrenals from dogs and fatty marrow from goats. One row is
called an *Estimate*. And one row is neither sourced nor estimated: **"Skin
shunt: Values chosen merely to complete cardiac output"**. That row is 1,290 of
6,480 ml/min, which is **19.9% of the total** and the second-largest flow in
the table.
<!-- not-restated: 2.5 liters -->

This model's whole representation of perfusion comes from one assumption in
that appendix: "it has been thought legitimate to assume that **the blood flow
to any region is a fixed fraction of the total cardiac output** from 20 to 70
years of age."

**Figure 4.1b's flow column cannot be reproduced from any of the four.** On Mapleson's own
rows, kidney + heart + brain + liver is 3,820 of 6,480 ml/min, which is
**59.0%**. Every well-perfused organ together is **63.0%**. Lowe has **76%**,
and Smith and Zwart have 64.0%. Muscle plus skin nutritive is 10.2%, against
Lowe's 13%. Fat plus fatty marrow is 4.0%, against Lowe's 5%. **The perfusion
fractions this model runs on have no identified origin in any reference the
book names for them.** Reference 26 has no flows at all, and the other three do
not match. **This finding covers only the four documents that have been
read.** An origin may still exist: the book prints more than one table, and
Gas Man may lump differently.
<!-- not-restated: 5 % -->

**Three of the stored values also appear in those tables.** They are alveolar
ventilation of 4 l/min, a functional residual capacity of 2.5 l in reference
20's table only, and a skeletal muscle tissue volume of 33 litres. The next
paragraph settles where each one came from. **No stored value changes because
of any of it.**
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

**Two of the three figures in those tables descend from Mapleson, and one is a
coincidence.** The 2.5 L is Mapleson's functional residual capacity. It is a
mean of published human measurements, cited to Dittmer and Grebe's *Handbook
of Respiration*, and not a round number somebody chose. It is still not the
stored value's source. Mapleson's row is FRC plus half the tidal volume,
whereas this model stores an alveolar gas volume. The stored value also reaches
this project through Gas Man, whose upstream source is Lowe and Ernst, and
Lowe and Ernst state no alveolar gas volume at all. The 33 is Mapleson's muscle 30 plus skin
nutritive 3, which is exactly how Smith prints it. It is *not* the stored
33.0, because Lowe's muscle row is 29.8 L at 70 kg and reproduces the stored
value under no grouping. Alveolar ventilation of 4 l/min stays a coincidence,
because Mapleson gives a formula, not a figure.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

Mapleson 1963 is one of the four, but that does not make Mapleson the
*Workbook's* source. The Workbook attributes nothing to Mapleson. Lowe and
Ernst cite him for a table they collected, two links further up the chain.

**The model patient is 100 kg, which is why the material arrives in this
project as fractions.** Page 56 picks that weight so that "the organ weights
can also be read as per cent of total body weight". So Lerou and Booij's Table
6 of fractions is the book's own table divided by 100, not a normalization they
performed. Nothing in the book states a 70 kg parameter set. Cardiac output is
allometric, and this too was read at the source. Page 59 gives the cardiac output for its worked prime dose as
$`2M^{3/4}`$ dl/min, "or 63.25 dl" for the 100 kg patient. That is 0.2 times
body mass to the three-quarter power in L/min. It gives **4.84 L/min at 70
kg**, against the 5.0 stored here, which would need 73.1 kg. The book's own
worked value of 63.25 dl fixes the exponent independently of reading a
superscript off a scan. The stored cardiac output stays a fixed 5.0, and
§ "Known limitations" below gives the reasoning.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**The relation itself is derived, not measured, and pages 17–19 say from
what.** Page 59 states $`2M^{3/4}`$ without citing anything. Chapter 2 builds
the relation in three steps. Neither of its two constants is a cardiac-output measurement:

- **Figure 2.2, page 17** plots oxygen consumption against body weight for
  mammals from 0.03 kg to 8,000 kg. The plot is linear on log–log axes, and the
  slope is given as "approximately 10 kg^(3/4)". The figure is reproduced by
  permission from *Brody, S. Bioenergetics and Growth. Reinhold, New York,
  1945*. It is an interspecies metabolic allometry, not a human study.
- **Page 17** takes the arteriovenous oxygen content difference as "about 5 ml
  of O₂/dl of blood", attributed to Guyton et al. (the chapter's reference 13).
  Guyton et al. are also credited with concluding that kg^(3/4) "is probably a
  better index of cardiac output than any other parameter, including surface
  area". Chapter 2's reference list is outside the pages read, so that
  citation is unresolved.
- **Figure 2.4, page 19** is the arithmetic. kg^(3/4) × 10 gives O₂ use in
  ml/min. O₂ use ÷ 5 gives cardiac output in dl/min, and the figure annotates
  that divisor as "(a–v)DO₂ = 5 ml/dl". The figure also draws the two steps
  combined, kg^(3/4) × 2 → $`\dot{Q}`$ in dl/min, which is page 59's constant.

<!-- not-restated: 2.4 -->

So $`0.2M^{3/4}`$ is Brody's mammalian metabolic allometry divided by an
arteriovenous difference that is assumed constant across mammals. **4.84 L/min
at 70 kg is therefore a derived interspecies extrapolation and must not be
treated as a measured human cardiac output.** This matters in § "Known
limitations" below. That section is the one place where this document sets the
figure beside Cattermole et al.'s measured median, and it says so there.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**Checked against the book itself, the Workbook's attribution survives for
three of the seven values and fails for four.** The vessel-rich pair
reproduces exactly and *uniquely*. Kidney, heart, brain and liver are 8.6% of
body weight at 76% of cardiac output. That is 6.02 L at 70 kg against the
stored 6.0, and 0.76 against the stored 0.76. The book's ten compartments form
1023 non-empty groupings. Across all of them, at a tolerance of half a
percentage point, no other grouping matches both values. The same exhaustive
search returns **zero** groupings for the stored muscle pair (33.0 L at 0.18,
against the book's muscle row at 29.8 L and 0.130). It also returns zero for
the stored fat pair (14.5 L at 0.06, against adipose at 10.5 L and 0.050).
Alveolar volume is the third value that survives, and it survives in a negative
sense. The book states no alveolar gas volume at all. It lumps the circuit and
the patient's FRC into a single ventilatory volume of "about 100 dl". So the
Workbook cannot have taken 2.5 L from it.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.perfusion_fraction = 0.18 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.fat.volume_l = 14.5 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.fat.perfusion_fraction = 0.06 -->
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- not-restated: 0.050 -->

**What survives for the other four is the split rather than the values.** The
book's five non-vessel-rich compartments take 13 + 3 + 2 + 1 + 5 = 24% of
cardiac output. The stored muscle and fat fractions sum to exactly 0.24. Their
volumes do not follow: 83.6% of body weight is 58.5 L at 70 kg, against the
stored 47.5 L. So Gas Man appears to have kept the book's 76/24 flow split. It
appears to have redistributed the 24 across two compartments where the book
has five, over a smaller tissue volume. That arithmetic is this project's, and
it does not prove the Workbook wrong. Gas Man may lump differently, or may
work from a page outside the range supplied. The data file carries the figures
and the detail for each value.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**Nothing is promoted or adopted because of any of it.** All seven values stay
tier 3 and unadopted. Learning where Gas Man's numbers came from is not
evidence that they were measured. For the four that do not reproduce, there is
nothing here to adopt. For the ones that do, adopting would mean naming as the
authority a compilation whose own four sources are unread. What the reading
gains is an attribution checked against the document itself, and a known tier
for the next link in the chain.

**The venous pool has a published counterpart, and it replaced Gas Man's
1.0 L.** Davis and Mapleson's paper (*Br J Anaesth* 1981;53:399–405) was read
at the source on 2026-09-07. It describes a standard man of 70 kg with a total
blood volume of 5189 ml and a cardiac output of 6480 ml/min. Page 400 states
that **for models of inhaled anaesthetics** the two venous pools may be
combined, "in which case it would be marginally more accurate to make the
arterial pool 799 ml (15.4% of the total blood volume) and the combined venous
pool 1222 ml (23.6%)". That combined pool is the same object as $`V_v`$ here:
one well-mixed venous pool that carries tissue return. Their Appendix
derives it from the ICRP (1975) blood distribution rather than measuring it,
so it is tier 2. **It was adopted on 2026-09-07, on the project owner's
decision.** The stored value, `venous_pool_volume_l`, is 1.222 L. It is called
a pool because "venous blood volume" would suggest the physiologic venous
blood volume, which this is not. At the stored 5.0 L/min cardiac output, the
mixed-venous time constant is 14.7 s, against 12.0 s at Gas Man's 1.0 L.
<!-- provenance: data/patients/reference_adult.json venous_pool_volume_l = 1.222 -->
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->
<!-- not-restated: 70 kg -->

**What the larger pool costs.** The 30-minute $`F_A/F_I`$ wash-in distances
from the published cohort means are unchanged to two decimal places (+0.16,
+0.31, +0.79, +0.38 SD). The pool has long since equilibrated by then. So the
published wash-in comparison cannot discriminate between the two values, and
it is no evidence either way. The 5-minute $`F_A/F_{A0}`$ elimination ratios
move **0.11 to 0.13 published SD further from** their cohort means:
sevoflurane +3.67 to +3.79, isoflurane +4.02 to +4.15, and desflurane +1.02 to
+1.13. They move because a larger pool returns more agent to the lungs.
§ "Published wash-in and elimination validation test" already attributes a
shift in the same direction to this model's rebreathing circuit rather than to
tissue return. This shift is a tenth of the gap it adds to.
<!-- not-restated: 0.31 -->

**Gas Man's 1.0 L is not an arterial compartment under a venous name.** Lerou
and Booij's arterial fraction of 0.2 gives 0.98 L at their 4.9 L total,
within 2% of Gas Man's 1.0 L, which suggested that reading. Davis and
Mapleson's own arterial pool for an inhaled-anaesthetic model is 799 ml, which
is 15.4% rather than 20%. So that coincidence does not survive the primary
source. Their venous pool is the closer structural match, and the time
constants nearly agree: 1222/6480 = 11.3 s, against Gas Man's 1.0/5.0 =
12.0 s. That near agreement is a property of the time constant rather than of
the volume. It is not evidence of a shared lineage, because nothing documents
Gas Man as having taken anything from this paper.
<!-- not-restated: 2 % -->

**Gas Man's own default is 1.0 L, and nothing argues for restoring it.**
Appendix C's `GASMAN.INI` listing, on page 172, reads `[Volumes] … VEN=1.0`.
That is a program default, tier 3. Davis and Mapleson's 1222 ml is tier 2 and
is the same object this model has, so the stored venous pool is a considered
replacement for Gas Man's default.
<!-- provenance: data/patients/reference_adult.json venous_pool_volume_l = 1.222 -->

**So, three rules for a `sources` entry.**

- Name the tier. Where the stored value is not a primary measurement, say in
  the note which value the primary literature reports and by how much the two
  differ. Use words that a reader comparing against a textbook can act on.
- Do not let a primary citation stand in for a primary value. Citing a
  measurement *alongside* a tier-3 number does not source that number. A file
  that looks sourced while its number came from somewhere else is worse than
  one that cites nothing, because it stops the reader checking.
- Where no primary source has been adopted, record it as an open gap. "No
  primary source has been adopted for this value" is a legitimate provenance
  state for an educational simulator, and one that can later be fixed. A
  tier-3 citation presented as settled is neither legitimate nor marked for fixing.

Saying that a constant comes from Gas Man, or from a paper that reprints Gas
Man's table, presents a tier-3 source as though it were a measurement.

**The first and third of those rules are part of the data-file format, and
`make check` enforces them.** Each family of data file (agent, patient and
machine) has its own `schema_version`, checked against that family's
supported versions in `src/anesthesia_sim/core/parameters.py`, so a format
change affects only its own family. Version 2 gave every `sources` entry two
required fields and allowed one optional top-level string. Version 3 added a
third required field to each entry. Version 4, for agent files alone, added
`molar_mass_g_mol` and `liquid_density` (§ "Agent amount"). Agent files must
be version 4, and patient and machine files version 3. The fields are a list,
because the checker reads the first table in this section as the provenance
table below:

- `tier`, on each `sources` entry: `primary`, `secondary` or
  `reference-implementation`. It says which of the three tiers above the
  *document* belongs to.
- `adopted`, on each `sources` entry: whether this file names that source as
  the authority for a value it stores.
- `authority_for`, on each `sources` entry since version 3: the dotted key
  paths of the stored values that rest on this source, spelled as the
  provenance table spells them. The list is empty exactly when `adopted` is
  false. The per-row counts under § "Source hierarchy" are computed from it.
- `provenance_gap`, optional and top level: why no primary source has been
  adopted, in a file where none has been.

`tools/doc_check.py`'s `check_source_tiers` enforces these as exact rules:

- Every entry declares a tier from the closed vocabulary, an `adopted` flag
  and an `authority_for` list.
- That list is non-empty exactly when the entry is adopted.
- Each path in the list is a stored value of the same file, and no stored
  value is named by two entries.
- A file with no entry that is both `primary` and `adopted` records a
  non-empty `provenance_gap`.

Each rule is an error that stops the build, not a warning, because none of
them needs judgment to decide. `src/anesthesia_sim/core/parameters.py` also
checks the vocabulary and the `authority_for` rules when it loads a file, so a
bad entry fails as soon as the file is read.

**`tier` and `adopted` are two fields because one field alone would decide
nothing.** Every agent file cites primary measurements that it has explicitly
*not* adopted, and so does the reference patient, which cites five. A check
that read the tier alone would report all four of this project's data files as
primary-sourced, although the reference patient adopts no primary source and
many of the table's rows are tier 3 (§ "Where this project stands" above gives
the counts). That is the failure the second rule above exists to prevent, so
the check reads the adoption and not the citation list. Today each agent file
declares two adopted primary sources, for `mac_awake` and for the vaporizer
maximum. `src/anesthesia_sim/data/patients/reference_adult.json` declares
none and records the gap.

**What the check does not decide is whether a citation labelled `primary`
really is one.** That needs somebody who has read the paper. A tool that
guessed, from the author, the journal or a product name in the title, would
look authoritative and be wrong. The tool checks that a claim was made and is
well-formed, and a reviewer checks that the claim is true. The provenance
table below works the same way: the checker confirms that a documented key
exists and holds the stated value, never that the value is right.

The following table records the values selected for v0.1.0. Each value is
loaded from a versioned data file and validated against its schema, rather
than hardcoded. Full citations, definitions and reference conditions are
recorded as `sources` entries in that file, not duplicated here.

Each row names the file and the exact JSON key path of the value it documents,
so a row traces to one stored value, not to a file that happens to contain a
matching number. `tools/doc_check.py` (run by `make check` and CI) checks the
table against the data files in both directions. Every row must name a key
that the file contains and state the value stored there, and every numeric
parameter in every data file must have exactly one row. A derived row states
the stored value beside the derived one. The tissue:blood coefficients are
computed when a file is loaded, from the tissue:gas and blood:gas values, so
their rows name the stored tissue:gas key and show the division.

Both directions start from a data file, so that check cannot see a constant
that never entered one, such as a field default on a `core/` dataclass.
`test_every_constant_a_core_dataclass_defaults_to_is_a_value_the_provenance_table_selects`
looks for such a constant. It reads every numeric field default on a `core/`
dataclass through `dataclasses.fields()`, including one written as a named
constant, and requires each to appear in this table's Selected-value column.
It skips zero and a field's full scale (1, or 100 for a percent), which carry
no scientific content. It matches values, not names, so it can miss a
constant: a new one equal to a value the table already selects passes, and 6.0
is selected for both the circuit and the vessel-rich tissue.

The table is not the only place these values appear. Some prose restates one:
the reference adult's alveolar volume and ventilation, and each agent's
blood:gas coefficient, vaporizer maximum and MAC. Each such sentence carries a
hidden marker, an HTML comment that names the file and key it restates:

```text
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
```

`doc_check.py` checks both sides of that link: the key against the data file,
and the stated value against the paragraph the marker sits under. So neither
the file nor the sentence can change without the other. Without the markers,
editing a data file would force an update to this table but leave the prose
around it quietly wrong.

Some figures are *derived* from several stored values, and no file holds
them. Such a figure carries a `derived:` marker that names its inputs instead.
One figure may carry several of these markers where its inputs span more than
one file:

```text
<!-- derived: 20.7 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4, default_cardiac_output_l_min = 5 -->
```

When an input changes, the checker reports that the figure must be recomputed
and names the figure. It never recomputes the figure itself. The rounding and
the units are matters of judgment, and a plausible wrong number in this
document is worse than none.

**Rewording a marked sentence is expected to fail the check.** The failure
asks for the marker to be moved or updated with the sentence.

A marker can also name a constant in code, such as the shipped step. It is
written as the module's path under the package, followed by the constant's
name:

```text
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
```

**A figure that equals a stored value must carry a marker.**
`doc_check.py` finds each figure in this document and in `README.md` that
equals a stored value, in that value's unit. The stored values are every
number in a parameter data file, and every public constant in the package
whose name ends in a unit, such as `_S` or `_L_MIN`. A figure that restates
its value carries a `provenance:` or `derived:` marker. A figure that only
coincides with one carries a `not-restated:` marker that lists it:

```text
<!-- not-restated: 2 %, 0.05 -->
```

The check never decides which kind a figure is. `2.5` appears in this document
as an alveolar volume in litres, a tolerance in seconds and a flow in litres
per minute, and `2%` is sevoflurane's MAC in one sentence and a dial setting in
the next. Binding a figure to a key by its value would be confidently wrong
where a reader trusts most. So the writer says which kind it is, and the check
enforces only that somebody did. A marker covers only the values it names, in
their units, so a marker for the 6 L circuit does not clear desflurane's 6%
MAC in the same paragraph. The check reads:
<!-- not-restated: 6 L, 6 % -->

- a unit written as a word, such as "seconds", and a time in milliseconds,
  minutes or hours, which it converts to seconds;
- a unit in lower case, such as "l/min";
- each number in a list joined by slashes, such as "6/33/14.5 L", with the
  list's unit;
- in math, a symbol given a number with `=` or `\approx`, such as
  $`V_A = 2.5`$ L or $`V_A = 2.5\,\mathrm{L}`$, where the number ends the span
  or comes before a comma, a semicolon or `\quad`.
<!-- not-restated: 6 L, 33 L, 14.5 L, 2.5 L -->

It reads no other number in math, because most are exponents and coefficients
that only happen to equal a stored value, and it skips a math span split
across two lines. A marker under a list covers the whole list, because a
marker cannot sit inside a list item. A `not-restated:` marker fails if its
paragraph no longer contains a figure it lists, so the declaration cannot
outlive its sentence. A number that equals no stored value, such as a
flow-sweep point or a worked example, needs no marker.

| Parameter | Selected value | Unit | Source (data file · key path) |
| --- | ---: | --- | --- |
| Blood:gas partition coefficient | 0.65 | dimensionless | `data/agents/sevoflurane.json` · `blood_gas_partition_coefficient` |
| Vessel-rich tissue:blood coefficient | 1.6923 (= 1.1 / 0.65) | dimensionless | `data/agents/sevoflurane.json` · `tissue_gas_partition_coefficients.vessel_rich` |
| Muscle tissue:blood coefficient | 3.6923 (= 2.4 / 0.65) | dimensionless | `data/agents/sevoflurane.json` · `tissue_gas_partition_coefficients.muscle` |
| Fat tissue:blood coefficient | 52.3077 (= 34.0 / 0.65) | dimensionless | `data/agents/sevoflurane.json` · `tissue_gas_partition_coefficients.fat` |
| Blood:gas partition coefficient (isoflurane) | 1.3 | dimensionless | `data/agents/isoflurane.json` · `blood_gas_partition_coefficient` |
| Vessel-rich tissue:blood coefficient (isoflurane) | 1.6154 (= 2.1 / 1.3) | dimensionless | `data/agents/isoflurane.json` · `tissue_gas_partition_coefficients.vessel_rich` |
| Muscle tissue:blood coefficient (isoflurane) | 3.4615 (= 4.5 / 1.3) | dimensionless | `data/agents/isoflurane.json` · `tissue_gas_partition_coefficients.muscle` |
| Fat tissue:blood coefficient (isoflurane) | 53.8462 (= 70.0 / 1.3) | dimensionless | `data/agents/isoflurane.json` · `tissue_gas_partition_coefficients.fat` |
| Blood:gas partition coefficient (desflurane) | 0.42 | dimensionless | `data/agents/desflurane.json` · `blood_gas_partition_coefficient` |
| Vessel-rich tissue:blood coefficient (desflurane) | 1.2857 (= 0.54 / 0.42) | dimensionless | `data/agents/desflurane.json` · `tissue_gas_partition_coefficients.vessel_rich` |
| Muscle tissue:blood coefficient (desflurane) | 2.3095 (= 0.97 / 0.42) | dimensionless | `data/agents/desflurane.json` · `tissue_gas_partition_coefficients.muscle` |
| Fat tissue:blood coefficient (desflurane) | 30.9524 (= 13.0 / 0.42) | dimensionless | `data/agents/desflurane.json` · `tissue_gas_partition_coefficients.fat` |
| Reference patient weight | 70.0 | kg | `data/patients/reference_adult.json` · `weight_kg` |
| Alveolar gas volume | 2.5 | L | `data/patients/reference_adult.json` · `alveolar_gas_volume_l` |
| Venous blood-pool volume | 1.222 | L | `data/patients/reference_adult.json` · `venous_pool_volume_l` |
| Vessel-rich tissue volume | 6.0 | L | `data/patients/reference_adult.json` · `tissue_groups.vessel_rich.volume_l` |
| Muscle tissue volume | 33.0 | L | `data/patients/reference_adult.json` · `tissue_groups.muscle.volume_l` |
| Fat tissue volume | 14.5 | L | `data/patients/reference_adult.json` · `tissue_groups.fat.volume_l` |
| Vessel-rich flow fraction | 0.76 | dimensionless | `data/patients/reference_adult.json` · `tissue_groups.vessel_rich.perfusion_fraction` |
| Muscle flow fraction | 0.18 | dimensionless | `data/patients/reference_adult.json` · `tissue_groups.muscle.perfusion_fraction` |
| Fat flow fraction | 0.06 | dimensionless | `data/patients/reference_adult.json` · `tissue_groups.fat.perfusion_fraction` |
| Default alveolar ventilation | 4.0 | L/min | `data/patients/reference_adult.json` · `default_alveolar_ventilation_l_min` |
| Default cardiac output | 5.0 | L/min | `data/patients/reference_adult.json` · `default_cardiac_output_l_min` |
| Breathing-circuit volume | 6.0 | L | `data/machines/reference_circle_system.json` · `circuit_volume_l` |
| Default fresh gas flow | 4.0 | L/min | `data/machines/reference_circle_system.json` · `default_fresh_gas_flow_l_min` |
| Maximum delivered concentration (sevoflurane) | 8.0 | percent | `data/agents/sevoflurane.json` · `max_delivered_concentration_percent` |
| Maximum delivered concentration (isoflurane) | 5.0 | percent | `data/agents/isoflurane.json` · `max_delivered_concentration_percent` |
| Maximum delivered concentration (desflurane) | 18.0 | percent | `data/agents/desflurane.json` · `max_delivered_concentration_percent` |
| 1 MAC, 40-year-old adult (sevoflurane) | 2.0 | percent | `data/agents/sevoflurane.json` · `mac_percent` |
| 1 MAC, 40-year-old adult (isoflurane) | 1.2 | percent | `data/agents/isoflurane.json` · `mac_percent` |
| 1 MAC, 40-year-old adult (desflurane) | 6.0 | percent | `data/agents/desflurane.json` · `mac_percent` |
| MAC-awake (sevoflurane) | 0.34 | fraction of 1 MAC | `data/agents/sevoflurane.json` · `mac_awake.fraction_of_mac` |
| MAC-awake standard deviation (sevoflurane) | 0.05 | fraction of 1 MAC | `data/agents/sevoflurane.json` · `mac_awake.standard_deviation_fraction_of_mac` |
| MAC-awake (isoflurane) | 0.31 | fraction of 1 MAC | `data/agents/isoflurane.json` · `mac_awake.fraction_of_mac` |
| MAC-awake standard deviation (isoflurane) | 0.05 | fraction of 1 MAC | `data/agents/isoflurane.json` · `mac_awake.standard_deviation_fraction_of_mac` |
| MAC-awake (desflurane) | 0.36 | fraction of 1 MAC | `data/agents/desflurane.json` · `mac_awake.fraction_of_mac` |
| MAC-awake standard deviation (desflurane) | 0.063 | fraction of 1 MAC | `data/agents/desflurane.json` · `mac_awake.standard_deviation_fraction_of_mac` |
| Molar mass (sevoflurane) | 200.05 | g/mol | `data/agents/sevoflurane.json` · `molar_mass_g_mol` |
| Molar mass (isoflurane) | 184.49 | g/mol | `data/agents/isoflurane.json` · `molar_mass_g_mol` |
| Molar mass (desflurane) | 168.04 | g/mol | `data/agents/desflurane.json` · `molar_mass_g_mol` |
| Liquid density at 20 °C (sevoflurane) | 1.5203 | g/mL | `data/agents/sevoflurane.json` · `liquid_density.g_ml` |
| Liquid density at 20 °C (isoflurane) | 1.5019 | g/mL | `data/agents/isoflurane.json` · `liquid_density.g_ml` |
| Liquid density at 20 °C (desflurane) | 1.4651 | g/mL | `data/agents/desflurane.json` · `liquid_density.g_ml` |
| Liquid density standard deviation (sevoflurane) | 0.0008 | g/mL | `data/agents/sevoflurane.json` · `liquid_density.standard_deviation_g_ml` |
| Liquid density standard deviation (isoflurane) | 0.0006 | g/mL | `data/agents/isoflurane.json` · `liquid_density.standard_deviation_g_ml` |
| Liquid density standard deviation (desflurane) | 0.0004 | g/mL | `data/agents/desflurane.json` · `liquid_density.standard_deviation_g_ml` |
| Liquid density measurement temperature (sevoflurane) | 20.0 | °C | `data/agents/sevoflurane.json` · `liquid_density.measured_at_celsius` |
| Liquid density measurement temperature (isoflurane) | 20.0 | °C | `data/agents/isoflurane.json` · `liquid_density.measured_at_celsius` |
| Liquid density measurement temperature (desflurane) | 20.0 | °C | `data/agents/desflurane.json` · `liquid_density.measured_at_celsius` |

The reference patient weight identifies which patient the volumes and flows
describe. No equation in this model uses it. `PatientParameters.weight_kg` is
loaded and range-validated, and nothing else reads it. The compartment volumes
and flows are the source's absolute values for a 70 kg adult. They are not
quantities scaled from a weight, so changing the weight alone would not
rescale them. The litres are Gas Man's form of the data. Lowe and Ernst, the
book that the Workbook names as its source, prints the same material as per
cent of a 100 kg body, with cardiac output an allometric function of mass.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**The vessel-rich flow fraction is 0.76 here and 75.8% in the one reachable
publication of the same parameter set.** The stored value comes from the
Workbook's own page-168 table, which gives the vessel-rich relative flow as
0.76 (read at the source on 2026-09-06). Table 1 of De Wolf et al. 2012, the
paper the twelve partition coefficients come from, prints 75.8, and
75.8 + 18 + 6 = 99.8. The model requires the flow fractions to sum to 1 to
within one part in a million million, so the published set could not be
stored as printed, even if it were preferred. That limit stays, because one
loose enough to admit 99.8% would also admit a transcription error silently.
The difference changes the vessel-rich time constant by 0.26%, below the
resolution of anything a learner reads off the curve. The De Wolf entry in
`reference_adult.json` records the difference in full.
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->

**The two machine rows adopt no source of any tier.** The reference patient
adopts no primary source but does adopt tier-3 ones, so the machine rows' gap
is the wider one. The two values describe the apparatus in front of the patient
rather than the patient. So they live in
`data/machines/reference_circle_system.json`, a third kind of parameter file.

- **Circuit volume, 6.0 L.** The Workbook's own table on page 168 gives 8.0 L.
  De Wolf et al. 2012 give the same 8 L in their Methods, for the simulations that
  used the coefficients in their Table 1. The 6.0 L value came in with the first
  circuit model on 2026-08-22, and no record gives a reason for choosing it. The
  project owner ruled on 2026-09-01 that the exact value is not critical, so 6.0 L
  was kept and not changed to 8.0 L. The smaller volume changes how much of the
  early rise in inspired concentration comes from the machine itself. At the same
  flow, $`\tau_C = V_C/\dot V_F`$ is 90 s here and 120 s at 8.0 L, so the
  apparatus lag is 25% shorter. That lag is the part of the inspired curve that a
  learner is most likely to attribute to uptake. So a run that reproduces a
  published Gas Man trajectory has to set the circuit volume to 8.0 L explicitly,
  and cannot assume that value. Like every `circuit_volume_l`, the 6.0 L is one
  total for the apparatus and the patient circuit together (§ "Breathing circuit").
  No source says how it divides between the two.
  <!-- derived: 90 s from data/machines/reference_circle_system.json circuit_volume_l = 6, default_fresh_gas_flow_l_min = 4 -->
- **Default fresh gas flow, 4.0 L/min.** No published counterpart for this
  value exists in any source this project has reached. The Workbook's
  parameter table gives the circuit row a volume and no flow, and describes
  its interface defaults without numbers. The two Gas Man simulation studies
  read here chose flows for their own purposes (De Wolf et al. used 1 L/min,
  and Weber et al. used 10 L/min for washout). The value is a **teaching
  default, not a clinical recommendation** (project owner, 2026-09-20,
  ratified, over lowering it to match contemporary low-flow practice). It is
  well inside the supported range of flows. It puts the circuit time constant
  at 90 s: long enough for the machine lag to show as a distinct phase of the
  early rise, and short enough to resolve within the first minutes of a
  teaching run. The data file labels this a design rationale, not a
  measurement. **It is also the flow a run starts at when a machine profile
  states none**, because no surveyed machine publishes a startup flow. The
  authority for that fallback is this rationale, not a source. The rationale
  holds for this file's 6.0 L circuit. A smaller circuit gives a shorter lag
  at the same flow, as § "What real workstations hold" below computes.

<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->
<!-- not-restated: 10 L/min -->

**The project holds one measured circle-system volume, and it bounds the
circuit-volume row rather than replacing it.** Targ, Yasuda and Eger measured a
conventional circle system by water filling at **9860 ml** (*Anesth Analg*
1989 Aug;69(2):218–25, PMID 2764290). The same study lies behind the
inert-circuit entry under § "Known limitations". It was read at full text on
2026-09-13 from the private reference corpus. The value is not adopted,
because of what the measured system contained. It
included a latex reservoir bag at the Y-piece **standing in for the patient's
lungs**. So adopting 9.86 L as `circuit_volume_l` would put a lung inside the
circuit, and then model it again as the 2.5 L alveolar compartment.
Subtracting the bag is not possible. The paper states no bag volume, and a
latex bag full of water distends past whatever it holds as a gas reservoir.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->

What the measurement supplies instead is a **bound and an ordering**. A real
conventional circle system's assembled volume, apparatus and patient circuit
together, is at most 9.86 L. That bound leaves both the stored 6.0 L and the
Workbook's 8.0 L admissible. It also puts the three figures in one order, with
only one of them measured. At 4.0 L/min the implied circuit time constants are
90 s, 120 s and 148 s.
<!-- derived: 148 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

**Read the like-for-like comparison, not the bare one.** Targ measured an
assembled system *plus* a lung. This model's corresponding total is
$`V_C + V_A`$ = 6.0 + 2.5 = 8.5 L, which is 13.8% below the measured 9.86 L.
The bare comparison, 6.0 against 9.86, would show 39% below. The study invites
the comparison in the like-for-like form. Its Figures 3 and 5 draw the ideal
wash-in and washout as $`100[1 - e^{-(\dot V/V_S)t}]`$ with $`V_S`$ = 9.86 L.
So its own time constant is total system volume over inflow, the same
$`V/\dot V_F`$ that this document uses. It remains a comparison and not an
adoption. A latex bag is not a lung, and that apparatus had no patient taking
up agent.
<!-- derived: 8.5 L from data/machines/reference_circle_system.json circuit_volume_l = 6.0 -->
<!-- derived: 8.5 L from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->

**What real workstations hold, and why that does not settle this row either.**
`docs/machine-survey.md` surveys the machines in current clinical use for the
variables that affect a number this model computes. The assembled volumes it
collects sit below both figures above. Shin et al. print apparatus volumes of
4.7 L for a Dräger Primus, 2.1 L for a Perseus A500 and 2.0 L for a Zeus IE.
Each includes the absorber and excludes the disposable patient circuit. Adding
the 1.2 L circuit that they computed their totals with gives 5.9, 3.3 and
3.2 L. So at this file's flow, the circuit time constant runs from 89 s on the
oldest of the three machines to about 50 s on the newest. That is a factor of
about 1.8 across machines that a learner would meet in the same department.
The stored 6.0 L lands within 2% of the Primus's assembled 5.9 L. That match
is a coincidence, because the stored value was not taken from the survey. It
predates the survey and was kept under the decision above.
<!-- derived: 89 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->
<!-- not-restated: 2 % -->

**Volume is not the whole of the difference between machines**, as the survey
found. Fukuda et al. moved only the fresh gas inlet, with the machine and the
volume held fixed. The inspired/delivered ratio of both isoflurane and
sevoflurane rose significantly at low flow (*J Anesth* 2006;20(4):268–73).
$`F_I/F_D`$ is what the circuit equation above computes. So a real machine
changed it through a property, the layout of its internal gas paths, that this
model does not represent. A future per-machine circuit volume
(`circuit_volume_l`) will therefore reproduce only part of the difference
between machines, and must not be described as reproducing all of it. The
model will not fold that layout into an effective volume either, because that
would attribute to volume a difference that volume did not cause.
`docs/machine-survey.md` sets out the consequence for modelling several
machines, `docs/machine-abstraction.md` records the decision, and
`ROADMAP.md`'s planned-milestone item 39 states when it is revisited.

**A search for the flow row's source found a recommendation, not a
convention.** `docs/machine-survey.md` § "(a2)" looked for a startup fresh gas
flow published by any machine in current clinical use, and found none. So the
row above still adopts no source. What is missing is a published startup
convention, and such a convention does not appear to exist. What the
literature offers instead is a recommendation about what practice should be.
Kalmar et al. conclude that *"routine clinical practice using what
historically is called 'low flow anaesthesia' (e.g. 2 L/min FGF) should be
abandoned"* in favour of automated minimal-flow delivery (*J Clin Monit
Comput* 2022;36(6):1601–1610, PMID 34978655). The paper was read at full text
on 2026-09-20 from PubMed Central, PMC9637609, where the quoted sentence closes
the abstract. That is the recommendation of a single-centre retrospective
study, not a measurement of what flows are used. But its own comparator is a
fixed 2 L/min group that it calls conventional low flow, and that flow already
sits below this model's 4.0.

**The 4.0 L/min default makes no claim about clinical practice**, because
no source this project holds supports one. Under the safety-critical standard,
a correct number carrying a wrong provenance is still a presentation failure.
A different default would not remove the problem, because an unlabelled
default teaches a norm whatever value it has. Moving to 0.5 L/min would carry
the same absent provenance. It would also put the apparatus lag at
**12 minutes**, longer than the demonstration that the default flow exists to
make.
<!-- derived: 12 minutes from data/machines/reference_circle_system.json circuit_volume_l = 6.0 -->
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->

**Two papers cited alongside Kalmar et al. in the survey do not bear on
practice, and the survey says so.** Candries et al. randomised flows of
0.2 to 6 L/min in 28 patients, as the protocol of a Gas Man validation study.
Hoffmann et al. ran 0.3 to 6 L/min *in vitro* into a test lung, and describe
those settings as reflecting clinical conditions. That range contains 4, 5 and
6 L/min. A study's chosen flow range is not a report of practice. Treating it
as one is the same error that the De Wolf entry guards against for its 1 L/min
elsewhere in this section.

There is no "arterial blood-pool volume" row. Arterial blood is not a
compartment and has no state of its own (see § "Model boundary"). The code derives the
tissue:blood coefficients at load time, as tissue:gas divided by blood:gas, in
the `AgentParameters` properties in `core/parameters.py`. The data file does
not store them a second time. The tissue-blood partition-coefficient tests in
`tests/unit/test_parameters.py` guard this derivation.

**The division is the literature's own operation, and one published table
reproduces its results.** Eger and Saidman state the operation in these words:
"a tissue/blood partition coefficient for a given anesthetic is calculated by
dividing a tissue/gas partition coefficient by the blood/gas partition
coefficient for that anesthetic" (p. 1023). Yasuda, Targ and Eger computed
their own tissue:blood table the same way, as the next subsection records.
Both papers were read in full text from the private reference corpus. Eger and
Saidman's p. 1023 was read on 2026-10-25. The full citation of Eger and Saidman
is in § "Known limitations".

Baker and Farmery's 2011 review publishes the results as well as the
operation. Its Table 2 (p. 572) prints two sets of tissue:blood coefficients
for the vessel-rich, muscle and fat groups. The set that matches is the one in
brackets, which the table's footnote d attributes to Eger and Shafer.
Desflurane has only that set. The table was read in full text from the private
reference corpus on 2026-10-25. In each cell the first figure is this
document's derived row and the second is Baker's bracketed figure:

| | vessel-rich | muscle | fat |
| --- | ---: | ---: | ---: |
| sevoflurane | 1.6923 vs 1.69 | 3.6923 vs 3.69 | 52.3077 vs 52.3 |
| isoflurane | 1.6154 vs 1.62 | 3.4615 vs 3.46 | 53.8462 vs 53.8 |
| desflurane | 1.2857 vs 1.29 | 2.3095 vs 2.31 | 30.9524 vs 30.9 |

<!-- derived: 1.6923 from data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 3.6923 from data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 52.3077 from data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 1.6154 from data/agents/isoflurane.json tissue_gas_partition_coefficients.vessel_rich = 2.1, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 3.4615 from data/agents/isoflurane.json tissue_gas_partition_coefficients.muscle = 4.5, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 53.8462 from data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 1.2857 from data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54, blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 2.3095 from data/agents/desflurane.json tissue_gas_partition_coefficients.muscle = 0.97, blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 30.9524 from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13, blood_gas_partition_coefficient = 0.42 -->

Baker's bracketed blood:gas values are the three that the agent files store:
0.65 for sevoflurane, 1.3 for isoflurane and 0.42 for desflurane. Eight of the
nine tissue:blood figures are the derived value rounded to Baker's printed
precision. Desflurane's fat coefficient is the exception. 30.9524 rounds to
31.0, and Baker prints 30.9. The difference is 0.05, or 0.17%, in the last
printed digit. That is too small to come from a different operation, and Baker
does not say how the figures were rounded.
<!-- not-restated: 0.05 -->
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 30.9524 from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13, blood_gas_partition_coefficient = 0.42 -->

**The agreement checks the transformation, not the coefficients.** It shows
that the stored tissue:gas values, divided by the stored blood:gas values,
give the coefficients as the literature publishes them. That confirms the
operation and its arithmetic. It is not a second measurement. Baker attributes
the bracketed set to Eger and Shafer's 2005 tutorial, which ran its
simulations in Gas Man, according to its abstract. The stored tissue:gas
values are Gas Man's figures for Yasuda, Targ and Eger's measurements, and the
stored blood:gas values are De Wolf et al.'s. In all seven cells where Gas
Man's figure differs from Yasuda's mean, Baker's bracketed figure follows Gas
Man's. Isoflurane fat is the clearest: 53.8 is 70.0 divided by 1.3, where
Yasuda's 64.2 would give 49.4. So the match is one parameter set divided
twice, not two sources agreeing. Eger and Shafer's paper is not held here, so
it is not known which of the two took its figures from the other. A reader
should take the table as evidence that the division is the right
operation, and not as evidence that the coefficients are right. § "Known
limitations" says how far other laboratories' coefficients differ from these.
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->

**Baker's other set is not a check on the division.** Its plain figures are
"Data from Fiserova-Bergerova and Diaz (26)", a 1986 paper. They come with
their own blood:gas values, 0.6 for sevoflurane and 1.4 for isoflurane, and
they differ from the derived rows by far more than rounding. § "Known
limitations" gives the differences. The citations of Baker and Farmery 2011,
Eger and Shafer 2005 and Fiserova-Bergerova and Diaz 1986 were checked in
PubMed on 2026-10-25 (PMIDs 23737195, 16115976 and 3721592). Only Baker and
Farmery was read in full text. `docs/references/README.md` has its full
citation.

**For developers.** `_ReferenceAdultPayload._perfusion_fractions_must_sum_to_one`
and `PatientCompartments.__post_init__` each reject a set of flow fractions
whose sum lies outside `FLOW_FRACTION_TOLERANCE = 1e-12` of 1.0.
`default_fresh_gas_flow_l_min` is optional in a machine profile. A run built
from a profile that omits it starts at `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`
in `core/circuit.py`
(`test_a_profile_omitting_the_default_fresh_gas_flow_falls_back_to_the_teaching_default`).
`test_the_flow_default_matches_the_shipped_machine_file` fails if the constant
and the file's value ever differ.

### v0.2.0: isoflurane and desflurane

Isoflurane and desflurane use the same equations, compartments and reference adult patient as
sevoflurane. Only the partition coefficients differ. All twelve values, one blood:gas and three
tissue:gas coefficients for each agent, come from De Wolf et al. 2012, Table 1, the paper already
cited for sevoflurane. So the three agents' values can be compared directly.

**The nine tissue:gas values in that table come from one study's measurements.** They are the
Gas Man simulation program's figures for the human measurements of Yasuda, Targ and Eger 1989.
Five of the nine differ from the study's means by up to 9%, as the table below shows. Even so,
all three agents' tissue values come from *one study, one laboratory, one technique and one
cohort*, measured side by side in the same specimens. Any systematic error in that technique
therefore affects every agent alike. When values are shown as multiples of MAC to compare
agents, an error that all three share cannot make one agent look different from another. The
three blood:gas values are the Gas Man set, graded tier 3 under § "Source hierarchy". They are
comparable only because they come from one published table.

The shared-source argument covers the partition coefficients only. It does not cover the stored
MAC values, which differ from the primary literature in opposite directions for sevoflurane and
desflurane. § "Delivery-limit and MAC parameters" measures the differences.

**Gas Man's Workbook says the nine tissue:gas coefficients come from Yasuda, Targ and Eger, and
the paper confirms it.** The note under the Workbook's page-168 parameter table reads "Values for
isoflurane, halothane, desflurane and sevoflurane are taken from Yasuda, Targ and Eger". That
note alone could not raise the coefficients' source grade (tier), because a program's statement
about its own sources is not independent evidence (§ "Republication does not promote a value
between tiers"). The note had two further weaknesses. The Workbook's reference 45 is the 1988 ASA
annual-meeting abstract `Anesthesiology 69:A615`, not Yasuda, Targ and Eger's 1989 *Anesthesia &
Analgesia* paper. And the same Workbook paragraph credits sevoflurane's values to Yasuda and,
one sentence later, to "the package insert and Abbott data".

So the 1989 paper itself was read in full on 2026-09-13. Its Table 1 reports tissue:**gas**
coefficients, the quantity that the model stores. They come from 14 autopsy specimens, 6 to 10
per tissue, with a mean age of 65.8 ± 14.4 yr, equilibrated at 37 °C. The table below compares
them with the nine stored values:

| | vessel-rich (Yasuda's brain) | muscle | fat |
| --- | ---: | ---: | ---: |
| sevoflurane | 1.1 vs 1.15 ± 0.07 (−0.71 SD) | 2.4 vs 2.38 ± 1.03 (+0.02 SD) | 34.0 vs 34.0 ± 6.0 (exact) |
| isoflurane | 2.1 vs 2.09 ± 0.10 (+0.10 SD) | 4.5 vs 4.40 ± 1.97 (+0.05 SD) | 70.0 vs 64.2 ± 12.3 (+0.47 SD) |
| desflurane | 0.54 vs 0.54 ± 0.02 (exact) | 0.97 vs 0.94 ± 0.35 (+0.09 SD) | 13.0 vs 12.0 ± 2.0 (+0.50 SD) |

<!-- not-restated: 0.05 -->

<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1 -->
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4 -->
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.vessel_rich = 2.1 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.muscle = 4.5 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.muscle = 0.97 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13 -->

All nine stored values lie within 0.71 SD of the measured mean. Two match it exactly. Two more,
isoflurane vessel-rich and sevoflurane muscle, are the mean rounded to the stored precision. The
other five differ by more than rounding, and the largest gap is isoflurane fat, 9.0% above the
mean. Values from another source could not match this closely by chance, so the comparison
confirms the Workbook's attribution. It also settles the Workbook's contradiction for
sevoflurane: sevoflurane's three stored values match this paper, not a package insert.

Two further points matter for the model:

- **The vessel-rich coefficient is Yasuda's *brain* value.** Table 1 measures
  brain, heart, liver and kidney separately (sevoflurane 1.15, 1.21, 1.25,
  0.78). Any weighted average of the four would land away from the stored
  figure. The compartment that this document calls the vessel-rich group is
  parameterised as brain. A learner reading its trace is reading a brain
  trace.
- **This paper is not a source for the stored blood:gas values.** It measured
  none. Its Table 2 tissue:blood figures are calculated "by dividing the
  tissue/gas partition coefficient by the published values for the blood/gas
  coefficients adjusted for age". So Table 1 ÷ Table 2 recovers the
  age-adjusted blood:gas of the 65.8-year-old cohort. Those recovered values
  are 4.9–9.4% above the three round figures stored here.

**The tier changed and the stored values did not** (project owner,
2026-09-13). These were two separate decisions.

*Adopted.* The nine tissue:gas coefficients trace back to a primary human measurement. So all
three agents now cite Yasuda, Targ and Eger as their source, at tier 1, the grade for a primary
measurement. De Wolf et al. stays the source for the three blood:gas values, which this study did
not measure. Only the recorded source and grade changed. No number did.

*Declined.* Storing Yasuda's published figures instead of Gas Man's for the nine coefficients
would move three displayed time constants. Sevoflurane's vessel-rich time constant would move
+4.5% (coefficient 1.15 instead of 1.1), isoflurane's fat −8.3% (64.2 instead of 70.0), and
desflurane's fat −7.7% (12.0 instead of 13.0). The accuracy gained would be smaller than the error
that lumping brain, heart, liver, kidney and viscera into one vessel-rich compartment already
causes. A lumped compartment cannot use a difference of 0.05 in a brain measurement. So the Gas
Man values are kept.
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13 -->
<!-- not-restated: 0.05 -->

Desflurane is markedly less soluble than sevoflurane, which is itself less soluble than
isoflurane (blood:gas 0.42 < 0.65 < 1.3). With the same equations, lower solubility only makes
the agent equilibrate faster.

<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->

**Desflurane's tissue coefficients were checked against a published measurement and kept.**
Desflurane's elimination at five minutes is the only comparison where the model misses a human
measurement by washing out too fast. That result is most sensitive to the vessel-rich
coefficient, which makes that coefficient the obvious suspect. It is not the cause. The value
that would close the gap is nineteen standard deviations above the human measurement, and it
would invert the measured solubility order of the three agents. § "Desflurane's residual, and
why the parameter file was not changed" gives the reasoning. Read it before changing any of
desflurane's coefficients.

**For developers.** Each agent's partition coefficients are in
`data/agents/*.json`, whose `tier` and `adopted` fields record each value's
source. The three agents share the physiologic parameters in
`data/patients/reference_adult.json`. Storing Yasuda's figures would require
recomputing every pinned reference state under `tests/reference/`, because
those states are this parameter set's solution.
`tests/reference/test_multi_agent.py` checks the stored coefficients and the
simulated alveolar-to-circuit ratios.

### Delivery-limit and MAC parameters

Two per-agent values are stored with each agent but play no part in the model's equations. Each
one limits a control the user sees, or sets its starting value. A value that a clinician could
read or act on is safety-critical whether or not the model uses it, so both are specified here.

`max_delivered_concentration_percent` is the highest concentration that the
agent's real vaporizer can deliver (sevoflurane 8%, isoflurane 5%,
desflurane 18%). It is the upper bound of the delivered-concentration
control, and the core enforces it. `BreathingCircuit` carries the limit for
the agent in use, which `AgentUptakeSystem.for_agent()` sets. The circuit
**must reject** any delivered concentration above that limit, at
construction and at every later change. It must not clamp the value to the
limit instead. A clamp would run, display and chart a dial position that the
caller never requested, and on screen that looks exactly like a position the
caller did request. Zero is always accepted, because zero is the vaporizer
turned off, which is how washout begins. The limit exists so that the
simulator does not offer a dial position that does not exist on the matching
real device. It is a device limit, not a physiologic or safety limit. It says
nothing about whether a given concentration is appropriate for a patient.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: data/agents/isoflurane.json max_delivered_concentration_percent = 5 -->
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

**The maximum describes a vaporizer, although it is stored with the agent.** Each agent's value
is the calibrated dial maximum of the vaporizers that its source names: the Dräger Vapor 2000
and Datex-Ohmeda Sevotec 5 for sevoflurane, the Penlon Sigma Delta and Datex-Ohmeda Isotec 5 for
isoflurane, and the Tec 6 for desflurane. So desflurane's figure says how far a Tec 6 dial turns.
Another desflurane vaporizer, or an injector that delivers into the circle, is not bound by it.

The value is stored under the agent for two reasons:

- The reference breathing system in
  `data/machines/reference_circle_system.json` is not a machine and names no
  vaporizer. A per-machine entry would only repeat the agent file's number.
- The dial's start at 1 MAC relies on rejecting any agent whose own vaporizer cannot deliver
  1 MAC. That check needs the maximum and the MAC in the same file.

**The value moves when a machine profile mounts a vaporizer whose maximum
differs from the agent file's.** It then moves to the per-agent limit on the
machine profile, which `docs/machine-abstraction.md` names `agent_limits`.
Three things move with it at that point:

- The MAC check moves to wherever the machine and the agent are paired.
  Otherwise a machine whose limit is below an agent's MAC would reject the run
  at construction.
- The read in `AgentUptakeSystem.for_agent()` moves.
- The controller's own copy of the limit moves too. The interface draws its
  dial from that copy, so without the move the dial would offer positions that
  the circuit rejects.

Until then, the circuit and the dial read the same number from the same file.

**The three maxima come from two classes of vaporizer, which this model would need to tell apart
only away from sea level.** Sevoflurane's 8% and isoflurane's 5% are the maxima of
variable-bypass dials. Desflurane's 18% is the top of the Tec 6's range, and a Tec 6 is a heated
gas–vapour blender. The model fixes ambient pressure at 760 mmHg (§ "Assumptions"). At that
pressure, the same dial setting on either class gives the same partial pressure. So the model
does not need to know which kind of device a limit came from. The classes would differ only at
reduced ambient pressure, which is not modelled. See § "Known limitations".
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: data/agents/isoflurane.json max_delivered_concentration_percent = 5 -->
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

`mac_percent` is 1 MAC for a 40-year-old adult. It is used for two things,
and both are presentation. First, it sets the starting position of the
delivered-concentration control when a run begins. A new run then starts from
a recognizable clinical anchor rather than an arbitrary number. Second, it is
the divisor of the second display unit ("MAC multiples as a display unit").
`AgentUptakeSystem.for_agent()` applies the first use, so the core, not the
controller, makes the starting dial position agent-specific. Every agent file
**must** declare a `mac_percent` that its own vaporizer can deliver. A
cross-field check in `core/parameters.py` enforces this. The check runs after
every field is populated, so the order in which the fields are declared cannot
defeat it. Even so, `mac_percent` is not carried into the simulation. No
governing equation reads it, and `core/` computes no quantity derived from it.
Specifically, the model does **not**:

- compute MAC-hours or an age-adjusted MAC, or sum MAC fractions across
  agents;
- model an effect-site compartment or any depth-of-anesthesia endpoint; or
- imply that an alveolar concentration equal to `mac_percent` corresponds to
  any particular clinical state in a particular patient.

MAC is a population ED50 for immobility in response to a standardized stimulus. It varies with
age, and other agents, opioids, temperature and patient factors modify it. None of these are
modeled here. Presenting a single-agent alveolar concentration as if it indicated anesthetic
depth would be exactly the plausible but wrong clinical inference that the project's safety
standard forbids. So the display shows a *ratio to* 1 MAC, written `×MAC`, and never a depth.
§ "MAC multiples as a display unit" gives the reasoning.

**Because displayed values are divided by it, the stored MAC carries clinical weight.** If it
only set where the dial started, an error in it would move only a run's starting point. But every
displayed compartment value, and the chart's second axis, is divided by it. The stored values are
single adult MACs with no adjustment for age, which De Wolf et al. state they used in their Gas
Man simulations. They are graded **tier 3** under § "Source hierarchy". They were adopted for two
reasons. They belong to the same parameter set as every partition coefficient in this model. And
the reference adult has no age to which an age-related MAC could be applied.

**The size of the gap, and which comparison it distorts.** Mapleson's
meta-analysis of the published MAC literature gives these values for age 40:
isoflurane 1.17%, sevoflurane 1.80% and desflurane 6.6%. Their 95% confidence
limits are about ±7% (±10% for desflurane). The table compares the stored
values with them.

| Agent | Stored `mac_percent` | Mapleson age-40 | Displayed MAC reads |
| --- | --- | --- | --- |
| Sevoflurane | 2.0% | 1.80% | 10% low |
| Isoflurane | 1.2% | 1.17% | 2.5% low |
| Desflurane | 6.0% | 6.6% | 10% high |
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- provenance: data/agents/desflurane.json mac_percent = 6 -->

The errors run in opposite directions for sevoflurane and desflurane. So a comparison of the two
in MAC multiples differs by about 22% between the stored MACs and Mapleson's. Comparing agents is
what the MAC-multiple display exists for. The 22% is larger than either source's own confidence
limits. It is a limitation of the display, listed in § "Known limitations".

**Why the Mapleson values are not adopted** (project owner, 2026-09-04,
ratified, over adopting Mapleson's age-40 values). There are three reasons:

1. Mapleson 1996 is a meta-analysis. It fits a regression to published studies and measures
   nothing, so § "Source hierarchy" grades it **tier 2**. A lower-tier source, like the stored
   values, may still be adopted by a recorded decision. Reasons 2 and 3 explain why the stored
   values were kept.
2. Every other parameter in this model comes from the Gas Man set. Dividing the model's Gas Man
   concentrations by a Mapleson MAC would make each displayed multiple a ratio between values
   from two different sources. Dividing by the model's own MAC is at least internally consistent.
3. With confidence limits of ±7-10%, no MAC source makes a comparison between agents exact. The
   display shows the MAC it divides by and states the limitation, instead of presenting another
   estimate as settled.

`ROADMAP.md`'s planned-milestone item 31 is the route to primary values for
all three agents.

Each agent's `sources` array carries the citation, the tier, the Mapleson
value that the stored value was not taken from, and the difference between
the two.

**For developers.** `_AgentPayload._mac_percent_must_not_exceed_vaporizer_max()`
in `core/parameters.py` rejects an agent whose own vaporizer cannot deliver
its 1 MAC. The 1-MAC start in `AgentUptakeSystem.for_agent()` depends on that
check. Because `mac_percent` divides every displayed compartment value, a
change to it falls under the safety-critical standard in `CLAUDE.md`.

The project must not tag a release while scientific `TBD` values remain in
this document. None remain as of this revision.

## Required invariants

The implementation must preserve the following invariants:

- all volumes are finite and positive;
- fresh gas flow, alveolar ventilation, cardiac output, and tissue flows are finite and nonnegative;
- partition coefficients are finite and positive;
- tissue flow fractions sum to one within tolerance;
- stored agent amounts remain finite and nonnegative;
- derived partial-pressure-equivalent fractions remain finite and within 0 through 1;
- no compartment creates agent spontaneously;
- internal transfers remove and add equal amounts;
- identical runs produce identical state and run definition, element for
  element, however the steps were grouped in real time;
- simulated time is the number of completed steps times the run's step, and
  a step whose length differs from the step the run has already taken is
  refused, not counted;
- changing a setting does not reset stored state;
- Pause prevents simulation-time advancement;
- Reset clears dynamic state while preserving settings;
- a delivered concentration above the agent's vaporizer maximum is rejected, not clamped;
- a simulation step outside `MINIMUM_SIMULATION_STEP_S` to
  `MAXIMUM_SIMULATION_STEP_S` is refused, not simulated;
- a simulation step that cannot be completed leaves every dynamic value, and
  the simulation time, exactly as the last completed step left them;
- zero fresh gas flow prevents new external delivery;
- zero ventilation prevents circuit-to-patient ventilatory exchange;
- zero cardiac output prevents pulmonary and tissue perfusion;
- zero tissue flow prevents uptake by that tissue; and
- equilibrium produces no net internal transfer.

## Required tests

### Preserved circuit reference tests

The v0.0.2 analytic wash-in and washout tests must remain unchanged and continue to pass.

With no patient ventilation:

$$
F_I(t) = F_D+\left[F_I(0)-F_D\right]e^{-t/\tau_C}
$$

where:

$$
\tau_C =
\frac{V_C}{\dot V_F}
$$

using compatible time and flow units.

Held by `test_circuit_matches_analytic_wash_in` and
`test_wash_in_is_monotonic_and_never_overshoots` in
`tests/reference/test_circuit_wash_in.py`, and for the washout by
`test_zero_delivered_concentration_washes_out_circuit` in
`tests/unit/test_circuit.py`.

### Zero-agent test

If all initial stores are zero and $`F_D=0`$, then every stored amount and
concentration must remain zero.

Held by `test_no_delivered_agent_keeps_every_store_zero` in
`tests/reference/test_sevo_patient.py`.

### Zero-ventilation test

If $`\dot V_A=0`$, the circuit may wash in, but the patient compartments must receive no new agent through ventilation.

Held by `test_zero_ventilation_prevents_patient_delivery` in
`tests/reference/test_sevo_patient.py`.

### Zero-cardiac-output test

If $`Q=0`$, alveolar gas may change through ventilation, but arterial blood, venous blood, and tissue stores must not change through perfusion.

Held by `test_zero_cardiac_output_prevents_patient_uptake` in
`tests/reference/test_sevo_patient.py`.

### Zero-tissue-flow test

For any tissue $`i`$, $`Q_i=0`$ must imply $`\frac{dM_i}{dt}=0`$.

Held by `test_a_zero_tissue_flow_leaves_that_group_alone` in
`tests/unit/test_governing_equations.py`, which checks the coupled system's
matrix, and by `test_zero_flow_preserves_tissue_state` in
`tests/unit/test_tissue.py`.

### Equilibrium test

If all connected compartments have the same partial-pressure-equivalent
fraction, with $`F_I=F_A=F_a=F_v`$ and every tissue group at the same value,
then all internal transfer rates must be zero.

Held by `test_equilibrium_produces_no_net_internal_transfer`, for sevoflurane
in `tests/reference/test_sevo_patient.py` and for isoflurane and desflurane in
`tests/reference/test_multi_agent.py`.

### Directional ventilation test

With otherwise identical conditions, increasing alveolar ventilation must accelerate the approach of $`F_A`$ toward $`F_I`$.

Held by `test_higher_ventilation_closes_the_alveolar_to_inspired_gap_faster`
in `tests/reference/test_sevo_patient.py`. It runs the default sevoflurane
wash-in at 2 and 8 L/min of alveolar ventilation and requires $`F_A/F_I`$ to
be higher at 8 L/min at every whole second of the first minute. The test
compares the ratio because $`F_A`$ alone measures the approach to $`F_I`$
only when $`F_I`$ is the same in both runs, and here it is not. The circle
system rebreathes, and more ventilation carries more agent into the patient,
so $`F_I`$ itself rises more slowly at the higher ventilation.

### Directional solubility test

In controlled synthetic cases, increasing $`\lambda_{b:g}`$ must increase blood capacity and slow the rise of $`F_A/F_I`$.

Held by `test_higher_blood_gas_solubility_slows_alveolar_to_circuit_rise` in
`tests/reference/test_sevo_patient.py`.

### Directional tissue-capacity test

Increasing either $`V_i`$ or $`\lambda_{i:b}`$, with flow held constant, must lengthen the tissue time constant:

$$
\tau_i =
\frac{V_i\lambda_{i:b}}{Q_i}
$$

Held by `test_a_larger_or_more_soluble_tissue_has_a_longer_time_constant` in
`tests/unit/test_tissue.py`.

### Washout test

After loading the compartments, setting $`F_D=0`$ must produce finite,
nonnegative washout without spontaneous increases in total system mass.

Individual tissue concentrations may rise for a time through redistribution.
The test must therefore not require every compartment to decrease
monotonically.

Held by `test_washout_never_increases_total_system_mass` in
`tests/reference/test_sevo_patient.py`.

### Step-refinement test

Reference simulations at supported smaller steps must produce the same
solution, to within floating-point rounding.

At minimum, compare:

```text
dt = 0.1 s
dt = 0.05 s
dt = 0.025 s
```

All three steps are inside the supported domain. The first is
`MAXIMUM_SIMULATION_STEP_S` itself, and the finest is 25 times
`MINIMUM_SIMULATION_STEP_S`.

The gate compares *successive* halvings (0.1 against 0.05, then 0.05 against
0.025) rather than comparing each step against the finest. It also requires
every gap to stay below a stated bound at the level of rounding error. Two
step sizes can show only that a pair of runs agree. Three step sizes show that
the step does not enter the result.
<!-- not-restated: 0.05 -->

**Changing the step size changes the result only by rounding, and the test requires that.** The
model solves its equations exactly over each step, so it reaches the same answer at every
supported step size. The gaps between runs are as small as computer rounding allows, and they do
not shrink as the step shrinks. The test compares the alveolar, vessel-rich and mixed-venous
concentrations after 60 s.

**A second test checks the smallest supported step, 1 ms.** A minute in 1 ms steps must match the
same minute in the application's 0.1 s steps, to within rounding. So the smallest step the model
accepts gives the application's answer. The test expects the smallest step to be 1 ms, so
changing it means measuring the rounding figures below again.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

Passing this test shows only that the 0.1 s step is short enough for the
model's equations to be solved accurately. It does not show that the model
matches a patient. A wrong transfer rate gives the same answer at every step,
so it passes here. § "Independent-solution test" below checks that the
equations are solved correctly, and § "Published wash-in and elimination
validation test" compares the model with measured patients.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

Held by `test_step_refinement_converges`, for the three halvings, and by
`test_the_smallest_supported_step_lands_on_the_ceilings_solution`, for the
minimum step. Both are in `tests/reference/test_sevo_patient.py`.

**For developers.** Each figure is an absolute gap in fraction. The worst gap
between successive halvings is 3.4e-16, in the alveolar fraction (measured
2026-11-01). Euler's method, whose error halves with the step, shows gaps up to
1.8e-6 at these steps (measured 2026-11-03). The test's limit, 1e-14, was set
on 2026-09-06 at about twelve times the worst gap then, 8.1e-16. That
measurement reported four values, and no record names the fourth. The test has
compared the same three since the method became exact.

The test of the smallest step, `MINIMUM_SIMULATION_STEP_S`, allows 3e-14 in
each compared fraction. That is wider than the halvings' limit because its
minute takes 60 000 steps rather than at most 2 400, and rounding builds up
once per step. Measured on 2026-10-03, its worst gap is 2.4e-15, in the
alveolar fraction, so the limit allows about twelve times that gap, the same
margin as the halvings'. The gap does not change smoothly with the step. It
depends on how the calculation happens to round at that step, and steps near
1 ms reach 1.2e-14. On a machine that rounds differently, the margin could be
nearer two and a half times.
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

A method that does not solve the equations exactly fails the 1e-14 limit,
because its result moves with the step. Test such a method by checking that
each halving of the step shrinks every gap by a predicted factor, about two
when its error is proportional to the step.

### Independent-solution test

The coupled six-state solution must be checked against an integration of the
governing equations that shares no solver with the implementation
(`tests/reference/test_coupled_dynamics.py`). The oracle may load the
parameter files and nothing else from the package under test. A comparison
against code derived from the implementation is a tautology, not a
verification. So the test enforces that restriction on its own imports.
`test_exact_step_matches_the_independent_solution_everywhere` holds the
comparison. `test_oracle_imports_no_solver_from_core` and
`test_oracle_bodies_call_no_solver_from_core` hold the restriction.

The comparison covers every shipped agent, and its tolerance is **absolute**:

$$
\max_k \left| F_k^{\mathrm{shipped}} - F_k^{\mathrm{reference}} \right|
\leq
4\times10^{-13}
$$

over every state $`k`$ and every trajectory below.

**Runs at fixed settings out to one hour have a limit of their own.** A test runs each agent at
the reference settings for 60, 600 and 3600 s at the application's 0.1 s step. It compares each
result with the independent solution at that time. The limit is looser than the one above,
because the one-hour run builds up more rounding error than any run below.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**Why the limit is a fixed size.** The model solves its equations exactly over each step. So the
only difference between it and the independently written solution is computer rounding, since
the two agree exactly in exact arithmetic. Rounding builds up with the *number* of steps rather
than with their size, so it is slightly larger at a finer step. A limit that shrank with the step
would therefore claim the reverse of what is true.

**The measurements the limit is set from.** Each of the five runs below was compared with the
independent solution along its whole length, for all three agents. The differences are rounding.
At the application's 0.1 s step, desflurane gives the largest on every run. Even the largest
difference measured is nine orders of magnitude smaller than the worst error of the earlier,
approximate method.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

The oracle runs at an eighth of the step under test. At that step its
truncation error no longer contributes to the residual, as the next paragraph
shows.

**The remaining difference is rounding, because it has no consistent direction.** Running the
independent solution with steps eight times shorter again, 0.0015625 s, moves the largest
differences by at most 11%, some up and some down. If the difference still held error from the
independent solution's own method, it would fall about four thousandfold and never rise. A
difference that moves a few percent either way comes from rounding in the two solutions.

**The limit leaves room for rounding that differs between computers.** It is sized on how much
the model's own rounding can vary. Solving the same runs at 0.1, 0.05 and 0.025 s moves the
answer by more than its difference from the independent solution, and the limit is set above
that spread. It is still nearly nine orders of magnitude below the error of any method that does
not solve the equations exactly. So the test fails as soon as such an error returns.
<!-- not-restated: 0.05 -->

**The runs the limit covers.** The test covers *trajectories*, runs whose settings change over
time, as well as fixed settings. A run of the application is a sequence of settings, each held
until someone moves a slider. A slider move puts an approximate method under the most strain,
because the state is then far from where the new settings will settle it, and the method's error
grows with how fast the state changes. Runs whose settings never change are the smaller part of
what the interface produces. Limited to them, the test that every release must pass would claim
more checking than its evidence supports.

The gate therefore drives five kinds of run:

- *ordinary use*, held for 600 s. It is each agent's own 1 MAC delivered,
  4 L/min fresh gas, and the reference adult's default alveolar ventilation
  and cardiac output. The corner and the two setting-change runs below were
  chosen for where the operator split's error was largest. This one is chosen
  for ordinary clinical settings, so that a claim about what the interface
  displays is not established only at its extremes.
- the *reference point*, held and compared at horizons of 60 s, 600 s and
  3600 s. It is 5% delivered, 4 L/min fresh gas, and the reference adult's
  default alveolar ventilation and cardiac output. The pinned reference states
  below belong to this point.
- the *envelope corner*, held for 600 s. It is each agent's own
  `max_delivered_concentration_percent`, with fresh gas, alveolar ventilation
  and cardiac output all at their supported maxima. Those maxima are 10, 12
  and 10 L/min, which are also the sliders' maxima.
- a *ventilator start*: the same corner, but with alveolar ventilation at zero
  for the first 300 s, then at its maximum. Meanwhile the circuit fills to the
  dial setting while the lungs take up none of it. This is an ordinary
  manoeuvre. The earlier, approximate method exceeded the limit set from runs
  held at the corner.
- an *unperfused load, then dial off*: the corner with cardiac output at zero
  for 600 s, and then perfusion at its maximum with the vaporizer closed for
  300 s. During the first 600 s the circuit and alveoli saturate while every
  blood and tissue compartment stays empty. That sets up the widest spread of
  states the sliders allow. It is also the only trajectory that takes cardiac
  output or the delivered concentration to its minimum. Under the operator
  split it had the largest error of any trajectory, which is why it was added.
  Under the exact step it gives the smallest of the five figures above.

<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- not-restated: 5 % -->

**Trajectories that nobody wrote by hand.** The five runs above change their settings once or
never. A learner moves four sliders again and again, in combinations that nobody listed. So the
test also drives three random runs for each agent. Each is fixed in advance, so that a failure
can be repeated exactly. Each lasts 600 s and moves the controls every 0.1 to 20 s, sometimes to
the very end of a slider's range. So zero ventilation, zero perfusion and zero fresh gas flow are
all reached. These runs must meet the same limit as the five above, and they stay below the worst
of them.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

A second test drives the same runs through the full simulation. It checks that every step runs
without error, that the agent accounting adds up after every step, and that every step is
counted. It also checks that each of the six concentrations stays finite, at or above zero, and
at or below the highest concentration delivered so far. No compartment can hold agent at a higher
concentration than was ever delivered, because each is fed only from the others and from the
vaporizer. A looser upper limit would let a model change drive a compartment to several times the
dial setting.

In every case the largest difference is taken over the whole run, because it
falls at no predictable moment. With the earlier, approximate method it fell
soon after a change: about 85 s into a wash-in at fixed settings, and about
13 s after a setting change. With the present method it falls wherever
rounding peaks, which moves with the step. Measured on 2026-10-25:

- At the shipped 0.1 s step, nine of the fifteen pairs of agent and trajectory
  peak in the last 1.5 s of a 600 s run. Desflurane peaks there on four of the
  five trajectories. Only sevoflurane on the ventilator start peaks inside a
  transient, 6.4 s after ventilation starts.
- At 0.05 s, only four of the fifteen pairs peak in the last 1.5 s, and at 0.025 s five do. The
  ventilator start peaks in the circuit between 236 s and 283 s, while ventilation is off, for
  every agent at 0.025 s and for two of the three at 0.05 s. The worst of all runs is one of
  these, at 236.1 s.
- At every step, the unperfused load peaks during its loading phase, between
  350.8 s and the phase's end at 600 s, long after the circuit and alveoli
  have saturated.

<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

So the gate's runs contain the instants at which the operator split's error
peaked, and that kind of error is what the gate exists to catch. They do not
contain the largest rounding residual, which at the shipped step was still
reaching new highs in the last 1.5 s on nine of the fifteen pairs. The pinned
reference states follow that growth at held settings out to 3600 s.

The corner and the two setting-change trajectories were chosen by measuring
the operator split's error coefficient:

- Varied one at a time at fixed settings, the old method's error rose
  steadily with fresh gas flow and alveolar ventilation, to their slider
  maxima. Against cardiac output it was lowest near 5 L/min and rose toward
  both ends, more toward the top. The equations are linear in the delivered
  fraction, so each agent's worst dial was its vaporizer maximum.
- Across trajectories, the sweep first tried every combination of extreme settings in both
  phases. It then varied each setting around the worst combination. The worst point was always the
  first setting change after the loading phase filled. Repeating the cycle three or six times did
  not raise the peak, so the old method's error did not build up over a run. A third phase between
  the two never raised the error.
- Every axis was monotone toward the corner used, except cardiac output
  during loading. That axis was worst at *zero*, the opposite end from the
  held-settings corner.

<!-- not-restated: 5 L/min -->

With the earlier, approximate method, the unperfused load had the larger
error and the ventilator start the smaller. With the present method the two
have swapped places, and rounding builds up over a run. Three ventilator
starts in a row give desflurane a larger difference than one start. So the
sweep still shows where an approximate method has its largest error, which is
the error the test exists to catch. The sweep does not bound the present
method's rounding, which a longer run raises. The steady rise along each
setting was measured, not proved. A change to the equations could move the
worst case off these runs, so repeat the sweep after such a change.

Within one step, the model never updates a compartment from a value that the
same step has already changed. So it leaves no error that runs in one
direction, and a difference between two compartments is as accurate as either
reading it is taken from.

The reference states are pinned in the test file. A change to the oracle or to
a parameter file must be re-derived and reviewed rather than silently adopted.
The pinned states are the oracle's own solution, not the shipped solver's.
Re-pinning them from the implementation would turn this gate into a
self-comparison. The supported ranges above are restated in the test file and
checked against `core/supported_ranges.py`. So widening the model's declared
domain cannot silently leave this gate measuring only a subset of it.

**For developers.** Each figure here is an absolute residual in fraction,
taken as the maximum over the whole run.

- **Runs held to one hour.**
  `test_the_shipped_step_reaches_the_pinned_reference_horizons` compares each
  run's endpoint with the independent solution, and a separate test ties that
  solution to the pinned reference states. It allows `HELD_RUN_ROUNDING_BOUND`,
  an absolute $`10^{-12}`$, against the $`4\times10^{-13}`$ for the other runs.
  The one-hour run reaches **7.16e-14**, for desflurane in muscle (measured
  2026-09-07, unchanged on 2026-11-02). Step count alone does not explain
  this. The hour takes 36 000 steps, and so does the 900 s unperfused load at
  0.025 s, whose worst residual is smaller. The 600 s figures are at most
  1.34e-14, and the 60 s figures at most 5.69e-16. Dividing the hour into
  different steps moves the shipped solution by up to 2.17e-13, and the limit
  is 4.6 times that spread. `tests/reference/test_coupled_dynamics.py` records
  the full table.
- **Why the limit does not shrink with the step.** The operator split's error
  was $`C\,\Delta t`$, so a bound on $`C`$ bounded the error at every step
  size. The exact step has no such coefficient.
- **The five runs.** Measured on 2026-09-07 at the 0.1 s step, the worst
  residuals are 1.58e-14 for *ordinary use*, 1.54e-14 for the *envelope
  corner*, 1.39e-14 for the *ventilator start*, 1.34e-14 for the *reference
  point* and 8.80e-15 for the *unperfused load, then dial off*. Re-measured on
  2026-10-25, all five were unchanged to every digit that
  `tests/reference/test_coupled_dynamics.py` records. They lie within a factor
  of 1.8 of each other, because rounding does not grow with how far settings
  move. The unperfused load gives the smallest although it runs 900 s, against
  the others' 600 s. Its worst falls while the blood and tissue states are
  still exactly zero. Three desflurane ventilator starts in a row reach
  2.46e-14, against 1.39e-14 for one (2026-10-25). The test repeats all five at 0.05 s and 0.025 s. The
  worst there is **5.89e-14**, for desflurane on a ventilator start at 0.025 s,
  and the next is 5.46e-14, for desflurane on the held envelope corner at the
  same step (measured 2026-10-25). The earlier method's worst over these runs
  was 2.29e-4 at 0.1 s.
- **The margin for other machines.** The earlier method's limit carried a
  margin of 1.22. Its error coefficient came out the same on every machine,
  but rounding does not. A different `exp` implementation or a fused
  multiply-add instruction moves the last bits of both solutions. The spread
  was measured with no independent solution, as one exact calculation divided
  into 0.1, 0.05 and 0.025 s steps. It reaches 1.07e-13. The limit is 3.7 times
  that spread and 6.8 times the worst residual.
- **The random runs.** Each is fixed by a seed and starts empty at a random
  point in the settings envelope. Controls move only on a step boundary. At
  each move, each control changes with probability one half, at least one
  always changes, and one move in five lands exactly on a limit. They meet
  the same 4e-13 limit. Their worst residual is 1.10e-14, for desflurane in
  the vessel-rich fraction (measured 2026-11-01 at the shipped step). A run
  that changes its settings 48 to 64 times takes as many steps as one that
  never does, so it builds up as much rounding and no more.
  `test_randomised_control_trajectories_keep_every_invariant` drives the same
  runs through `SimulationState`. Its concentration check replaces a looser
  upper limit of 1.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- not-restated: 900 s -->
<!-- not-restated: 0.05 -->

### Published wash-in and elimination validation test

Every test above is **verification**. Each one asks whether the
implementation solves the intended equations correctly. It checks this by
comparing the implementation against an analytic solution, an independent
integration of these same equations, a conservation identity, or the
implementation's own behavior at another step size or setting. None of these
tests asks whether the equations describe the phenomenon. A model can be
numerically flawless and physiologically wrong. A suite made only of the tests
above would report the first property as though it had settled the second.

This test is the **validation** half, and the only required test whose expected values
come from published measurements. § "Independent-solution test" above answers a different
question. A pass of one says nothing about the other.

**This section covers two comparisons, in opposite directions.** The first is
$`F_A/F_I`$ at 30 minutes of **wash-in**, which agrees with the published
measurements. The second is $`F_A/F_{A0}`$ at 5 minutes of **elimination**,
which does not agree. Both come from the same volunteers in the same sitting.
§ "The early wash-in curve against the published figures" below extends the
wash-in comparison to the first 25 minutes.

$`F_A/F_I`$ at 30 minutes of wash-in is the classic measured quantity in the
uptake literature. Yasuda et al. published it for all three shipped agents in
two volunteer studies:

| Agent | $`F_A/F_I`$ at 30 min | Cohort | Published $`F_I`$ | Source |
| --- | --- | --- | --- | --- |
| Sevoflurane | 0.850 ± 0.018 | n=7 | 1.0% | Anesth Analg 1991;72:316-24 |
| Isoflurane | 0.733 ± 0.027 | n=7 | 0.6% | Anesth Analg 1991;72:316-24 |
| Desflurane | 0.90 ± 0.01 | n=8 | 2.0% | Anesthesiology 1991;74:489-98 |
| Isoflurane | 0.73 ± 0.03 | n=8 | 0.4% | Anesthesiology 1991;74:489-98 |

<!-- not-restated: 2.0 % -->

- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Liu J, Laster M, Taheri S,
  Peterson NA. *Comparison of kinetics of sevoflurane and isoflurane in
  humans.* Anesth Analg 1991;72(3):316-24. PMID 1994760,
  doi:10.1213/00000539-199103000-00007.
- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Johnson BH, Freire BA,
  Fassoulaki A. *Kinetics of desflurane, isoflurane, and halothane in humans.*
  Anesthesiology 1991;74(3):489-98. PMID 2001028,
  doi:10.1097/00000542-199103000-00017.

Both papers report a second measured quantity on the same subjects, in the
opposite direction. That quantity is $`F_A/F_{A0}`$ after five minutes of
elimination, which begins where the 30-minute administration above ends.
$`F_{A0}`$ follows each paper's own definition: the last alveolar fraction
recorded during that administration. So the two comparisons form one
continuous protocol rather than two separate ones.

| Agent | $`F_A/F_{A0}`$ at 5 min | Cohort | Source |
| --- | --- | --- | --- |
| Sevoflurane | 0.157 ± 0.020 | n=7 | Anesth Analg 1991;72:316-24 |
| Isoflurane | 0.223 ± 0.024 | n=7 | Anesth Analg 1991;72:316-24 |
| Desflurane | 0.14 ± 0.02 | n=8 | Anesthesiology 1991;74:489-98 |
| Isoflurane | 0.22 ± 0.02 | n=8 | Anesthesiology 1991;74:489-98 |

All eight figures in the two tables are mean ± SD. They were read from the two
abstracts and checked against PubMed on 2026-09-06.

Isoflurane is compared against both of its cohorts, in both directions.

**For wash-in**, the model must land inside the published standard deviation
for every row. It must also reproduce the ordering by solubility that the two
studies were run to test. That is, $`F_A/F_I`$ is higher for desflurane than
for sevoflurane, and higher for sevoflurane than for isoflurane. The ordering
is required because each row could pass its own tolerance while the agents sat
in the wrong order. The model meets both requirements. The elimination rows
have a different requirement, described below, because the model does not land
inside their spread.

**The tolerance is the published spread, and the operating point is not
fitted.** The test reads alveolar ventilation and cardiac output from
`reference_adult.json` at run time rather than writing them into the test. The
test fails if those defaults stop being 4.0 and 5.0 L/min. The whole
comparison rests on this assertion, because the agreement is sensitive to both
flows. A change of 1 L/min of alveolar ventilation either way puts all three
agents outside their published spread. A change of 1 L/min of cardiac output
moves every agent by more than one published standard deviation. An operating
point chosen to make the comparison pass would therefore make the result
circular. The operating point is instead the shipped default. It is cited to
the Gas Man workbook under § "Parameter provenance", and it was fixed in
v0.1.0 before any comparison to Yasuda existed.
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

Fresh gas flow is the one setting that the test chooses. It is 10 L/min, so that $`F_I`$ has
settled by 30 minutes instead of still rising. Here $`F_I`$ is the modeled *circuit* fraction,
not the vaporizer dial. A settled $`F_I`$ matches the protocols, which held an inspired
concentration at the airway. This choice does not decide the wash-in result. The test shows
every agent inside its published spread at every fresh gas flow from 1 to 10 L/min. The choice
does decide almost all of the elimination result, so the two comparisons are not equally strong.
The papers published four different $`F_I`$ values, and the test compares all four against one
delivered fraction. That is valid because the governing equations are linear in that fraction.
The test checks this for both ratios across the published range.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

**The elimination comparison does not agree.** At the default settings, and at the same
10 L/min that the wash-in comparison uses, the model has more alveolar agent at five minutes
than every cohort did. These values were measured on 2026-09-07:
<!-- not-restated: 10 L/min -->

| Agent | Cohort | Model | Published | Distance |
| --- | --- | --- | --- | --- |
| Sevoflurane | n=7 | 0.2328 | 0.157 ± 0.020 | +3.79 SD |
| Isoflurane | n=7 | 0.3227 | 0.223 ± 0.024 | +4.15 SD |
| Desflurane | n=8 | 0.1626 | 0.14 ± 0.02 | +1.13 SD |
| Isoflurane | n=8 | 0.3227 | 0.22 ± 0.02 | +5.13 SD |

So the check on these values is a **regression** pin. It holds the model's own ratio fixed, so
that any change to washout fails the test and has to be explained. It claims nothing about
agreement. The test does make three claims about elimination, and the model meets all three.
They are the published ordering by solubility (desflurane leaves fastest, then sevoflurane,
then isoflurane), independence from the delivered fraction, and the sign of the departure.

**Most of that departure comes from the breathing system, not from the tissue
return**, because of how the two ratios are defined. $`F_A/F_I`$ has the inspired fraction in
its denominator, so whatever a breathing system does to $`F_I`$ divides out. That is why the
wash-in comparison is inside the published spread at every supported flow. $`F_A/F_{A0}`$ has
no such term. It is the alveolar fraction divided by its own value five minutes earlier. So
agent that returns to the alveoli *from the circuit* counts exactly as though it had come out
of the patient. This model always rebreathes. Its one circuit (§ "Model boundary")
recirculates gas, apart from the fresh gas that enters and the gas that leaves through the
exhaust. The inspired gas *is* circuit gas. So during an elimination $`F_I`$ settles near
$`\dot V_A/(\dot V_A + \dot V_F)`$ of $`F_A`$, where $`\dot V_F`$ is the fresh gas flow. That
is 0.29 at the highest supported flow, and the measured value at five minutes was 0.30 to 0.32.
The published protocols did not rebreathe. Each study gave the agents through a
non-rebreathing circuit. At exactly 30 minutes, each exchanged it for a fresh inspiratory and
expiratory circuit (*Anesth Analg* page 317, *Anesthesiology* page 490). Neither paper states
the inspired fraction during elimination, so an inspired fraction at or near zero is inferred,
not reported. This model cannot be set to that fraction at any supported flow.

**The open-circuit diagnostic, and why its numbers are not this simulator's.** A test can run
the same five minutes with the rebreathing taken away. After each step of the elimination, it
discards whatever the patient exhaled into the circuit and records it as exhausted agent.
Collecting the whole expirate has the same effect. This keeps $`F_I`$ near zero. With
rebreathing, the same run settles at 0.30 to 0.32. **This condition exists only in the test.
No fresh gas flow, dial position or patient setting of the simulator produces it.** A
non-rebreathing mode was not built, because it would change the model boundary and add one
more mode for the interface to show (project owner, 2026-09-06). Nobody running the
application sees the numbers below, so any restatement of them must carry this warning. They
were measured on 2026-09-07:

| Agent | Cohort | Shipped | Open circuit | Published |
| --- | --- | --- | --- | --- |
| Sevoflurane | n=7 | +3.79 SD | 0.1541, −0.15 SD | 0.157 ± 0.020 |
| Isoflurane | n=7 | +4.15 SD | 0.2388, +0.66 SD | 0.223 ± 0.024 |
| Desflurane | n=8 | +1.13 SD | 0.0935, −2.33 SD | 0.14 ± 0.02 |
| Isoflurane | n=8 | +5.13 SD | 0.2388, +0.94 SD | 0.22 ± 0.02 |

**Three of the four cohorts land inside the published spread once the rebreathing circuit is
removed, and desflurane misses on the other side.** For sevoflurane, and for isoflurane in
both cohorts, the rebreathing circuit accounts for the whole of a gap 3.8 to 5.1 published
standard deviations wide. So this model's vessel-rich return does reproduce a human
elimination once the breathing systems are matched. For desflurane, removing the circuit more
than closes the gap. The model crosses its published mean and settles 2.33 SD below it, so it
washes out *faster* than the volunteers did. With the circuit gone, that residual is a
disagreement about tissue return. § "Desflurane's residual" below lists the explanations that
were ruled out and what remains. The test checks that the shift between the two conditions is
3.5 to 4.2 SD per cohort, so a test fails if the circuit stops explaining the gap. Without the
circuit, the elimination does not measurably depend on fresh gas flow. With it, the
elimination moves by 11.5 to 21.6 SD between 1 and 10 L/min.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

Neither condition validates the elimination a user watches, and no test claims
that it does. The elimination this simulator runs is the rebreathing one. What
is asserted about it is the regression pin above.

**For developers.** The test is `tests/reference/test_published_wash_in_and_elimination.py`.
It checks the five-minute elimination ratio against a stored value to $`1\times10^{-4}`$ absolute,
and its failure message gives the distance from each published mean. No tolerance is wide enough
to hide the disagreement. Neither paper's full text is in PubMed Central. Both are in the
private reference corpus that `docs/references/README.md` describes, and each has an
extraction note in `docs/references/` that gives the pages cited above. The open-circuit
condition is a test-only driver. Its $`F_I`$ is not zero, because exhaled gas refills the circuit
during each step before being discarded. The remaining $`F_I`$ is at most
$`\dot V_A \Delta t / V_C`$ of $`F_A`$ at the start of the step, or 1.1 × 10⁻³ at the shipped
ventilation, step and circuit volume. The test also checks this residual $`F_I`$ and the model's
mass balance across the discards. Across the supported flow range, the open-circuit elimination
changes by 4 × 10⁻⁶ published SD.
<!-- not-restated: 1.1 -->

#### Desflurane's residual, and why the parameter file was not changed

The obvious explanation for that residual is that desflurane's vessel-rich
coefficient is too low. The sensitivity measured under § "Parameter provenance"
shows that the five-minute ratio depends mostly on the vessel-rich tissue:gas
coefficient and barely on the blood:gas coefficient. A tissue group with too
little capacity empties too fast. That explanation fits the arithmetic, but the
measured tissue solubility rules it out, as the next paragraphs show.

**Raising the coefficient does close the gap, and it costs almost nothing in
the wash-in row.** Desflurane's stored vessel-rich tissue:gas coefficient is
0.54, and its blood:gas coefficient is 0.42. Together they imply a
tissue:blood ratio of 1.286. The table below instead solves for the
coefficient that reproduces each cohort's published five-minute ratio. It does
so at the shipped operating point, with the apparatus removed (measured
2026-09-08):

<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54, blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 1.286 from data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54, blood_gas_partition_coefficient = 0.42 -->

| Agent | Tissue:blood demanded | Measured human brain:blood | Distance |
| --- | --- | --- | --- |
| Sevoflurane | 1.74 | 1.70 ± 0.09 | +0.4 SD |
| Isoflurane | 1.45 | 1.57 ± 0.10 | −1.2 SD |
| Desflurane | 2.24 | 1.29 ± 0.05 | +19 SD |

<!-- not-restated: 0.05 -->

At a tissue:blood ratio of 2.24, desflurane's elimination lands on the
published 0.140. Its wash-in row stays inside its published spread, at +0.55
SD. That is not luck. The vessel-rich group's time constant is 2.0 to 2.7
minutes across the three agents, so the group is fully equilibrated after a
30-minute administration. Its capacity is therefore nearly invisible in
$`F_A/F_I`$ and shows up almost entirely in the elimination. So the two
published rows do not conflict with each other, and a single coefficient
satisfies both.

**The measured tissue solubility rules the change out.** The
measured column above comes from Yasuda's study of human tissue. The same
group published it three years before its pair of kinetic studies:

- Yasuda N, Targ AG, Eger EI 2nd. *Solubility of I-653, sevoflurane,
  isoflurane, and halothane in human tissues.* Anesth Analg 1989;69(3):370-3.
  PMID 2774233. Brain:blood, mean ± SD: I-653 (desflurane) 1.29 ± 0.05,
  isoflurane 1.57 ± 0.10, sevoflurane 1.70 ± 0.09, halothane 1.94 ± 0.17.
  Read from the abstract and checked against PubMed on 2026-09-08.

<!-- not-restated: 0.05 -->

Two of the three demanded values agree with that measurement. A demanded value is the
coefficient that an agent would need to match its published elimination. Desflurane's
demanded value is nineteen standard deviations above its own measured value, and above the
value that either other agent demands. Adopting it would make desflurane the *most*
tissue-soluble of the three agents, which would invert the ordering that the source paper was
written to report. The stored Gas Man coefficients match that paper's brain:blood values to
within 3%: 1.692 against 1.70, 1.615 against 1.57, and 1.286 against 1.29. So there is no
better value to move to. A test checks that at any vessel-rich coefficient the published human
tissue data support, desflurane's elimination still misses on the same side.

| Coefficient given | $`F_A/F_{A0}`$ at 5 min | Against 0.14 ± 0.02 |
| --- | --- | --- |
| 1.286, shipped | 0.0935 | −2.33 SD |
| 1.39, its own measured mean + 2 SD | 0.0998 | −2.01 SD |
| 1.70, sevoflurane's, the highest of the three | 0.1167 | −1.17 SD |

**Nine other candidates were measured or struck, and each fails in one of two ways.** Either
it moves sevoflurane and isoflurane as much as desflurane or more, which the published rows
have no room for, or it moves desflurane the wrong way. Rows one to six were measured on
2026-09-08, and the seventh on 2026-09-13, using the published apparatus's real volume from
the methods sections. Rows four to six were computed by a separate calculation of the same
equations, which agrees with the simulator to within 0.8%. The eighth and ninth rows were not
measured. Each is struck because a primary measurement on file rules it out, as described
below the table.

| Candidate | What reaching 0.140 takes | What it costs the other rows |
| --- | --- | --- |
| Blood:gas too low | ×1.63, to 0.687 | 10.9 SD above Eger 1987's measured 0.424 ± 0.024, and the wash-in row falls to −4.35 SD |
| Alveolar ventilation too high | between 2.5 and 3.0 L/min | at 3.0, sevoflurane +2.1 and isoflurane +2.7 SD, and all three wash-in rows at −2.0 SD |
| Cardiac output | out of reach | 3 to 7 L/min moves desflurane only from −2.6 to −2.1 SD |
| Fast capacity this model omits: lung tissue, pulmonary and arterial blood | about 3 L of blood-equivalent | moves all three agents together (below) |
| A non-ideal lung — shunt or ventilation-perfusion dispersion, both excluded by $`F_a \equiv F_A`$ | moves the wrong way | a 20% shunt takes desflurane from −2.29 to −2.66 SD; a log-normal V/Q distribution at log SD 1.0 takes it to −2.91 |
| Circuit-style rebreathing in the published apparatus, at an assumed ratio | $`F_I/F_A`$ = 0.30 | sevoflurane +2.72 SD, isoflurane +3.29 and +4.10 |
| The published apparatus's 50 ml dead space, as a ventilation decrement (below) | more than the wash-in rows allow | at the largest decrement they allow, desflurane is still −1.48 SD and both isoflurane cohorts leave their spread, at +1.69 and +2.17 |
| End-tidal sampling bias, a correction to the *published* value | an upward bias in the ratio, growing as solubility falls | struck: the one human measurement of the alveolar-to-arterial gradient points the other way (below) |
| Circuit-wall absorption, which this model's inert circuit walls leave out | the right direction, as in the sixth row | struck: the one study of a real circle system found desflurane close to the ideal curve at every flow (below) |

<!-- not-restated: 2.1 -->

**The sixth row measured circuit-style rebreathing at an assumed ratio, and
the apparatus turns out not to be that shape at all.** The "Materials and
Methods" section of Yasuda 1991 *Anesthesiology* places about 50 ml of
corrugated Teflon between the tracheal sampling port and the nonrebreathing
valve. The paper states that this tubing protects the end-tidal sample from
contamination with inspired gas. At end-expiration the tubing contains
alveolar gas, and at end-inspiration it contains fresh gas. That makes it a
**series dead space**, not a mixing volume that returns a fraction of every
breath. In a model with one perfectly mixed alveolar compartment, the two are
different mechanisms.

Consider one breath during the elimination, with agent-free fresh gas. Let
$`V_D`$ be the total series dead space, anatomic plus apparatus. Inspiration
first pushes that $`V_D`$ of alveolar gas back into the alveoli. It then
follows with $`V_T - V_D`$ of agent-free gas. So the alveoli receive $`V_T`$
of gas carrying $`V_D F_A`$ of agent, and they expel $`V_T`$ carrying
$`V_T F_A`$. The net change is $`-(V_T - V_D) F_A`$. This is exactly this
model's $`\dot V_A (F_I - F_A)`$ at $`F_I = 0`$, provided that $`\dot V_A`$ is
the true alveolar ventilation $`(V_T - V_D) f`$. **So the published apparatus's
dead space is an alveolar-ventilation decrement of $`V_D f`$ and nothing
else.** The sixth row tested the dead space as a non-zero $`F_I`$. That would
describe this model's circuit, not Yasuda's apparatus.

**Modelled as a ventilation decrement, the dead space fails for the same reason
as the second row. It is the second row's mechanism, at a size taken from the
source.** The model has no respiratory rate, so the table runs the decrement
across the conventional range of rates for a paralysed, normocapnic adult. It
was measured on 2026-09-13. For comparison, with no dead space at all,
desflurane sits at −2.33 SD:

| $`f`$ (/min) | $`\dot V_A`$ (L/min) | Desflurane | Isoflurane n=8 | Worst wash-in row |
| --- | --- | --- | --- | --- |
| 6 | 3.70 | −1.89 SD | +1.59 SD | −0.42 SD |
| 8 | 3.60 | −1.73 SD | +1.82 SD | −0.63 SD |
| 10 | 3.50 | −1.56 SD | +2.05 SD | −0.85 SD |
| 12 | 3.40 | −1.38 SD | +2.30 SD | −1.08 SD |

<!-- not-restated: 0.42 -->

The decrement moves desflurane the right way. It recovers between 0.44 and
0.95 SD of the 2.33 SD gap, which is a quarter to two fifths of it and never
the whole. The cost falls on the isoflurane cohort that was inside its spread
at +0.94 SD. The decrement pushes that cohort out to between +1.59 and +2.30
SD. The wash-in comparison sets its own ceiling. At 11 breaths per minute,
sevoflurane's wash-in row reaches −0.96 SD, and one more breath per minute
takes it outside its spread. So the largest decrement that the comparison
allows at all leaves desflurane 1.48 SD short, with both isoflurane cohorts
outside their spreads. The mechanism is **common-mode**, which means it moves
every cohort together. Desflurane's residual is differential, which means it
affects one agent alone.
`test_no_apparatus_dead_space_reaches_desflurane_s_published_elimination` and
`test_the_apparatus_dead_space_moves_every_cohort_together` assert both
halves, so this finding cannot go out of date without a test failing.

**It is still open whether the comparison should subtract the apparatus dead space.** Yasuda
derived the alveolar fraction of ventilation, $`f_A`$, from mixed expired gas,
$`F_M = f_A F_A + f_D F_I`$. The 1-l mixing chamber that supplies $`F_M`$ sits beyond the
nonrebreathing valve. The re-inspired 50 ml never reaches the chamber, so their $`f_A`$ is
$`(V_T - V_{D,\text{anat}} - V_{D,\text{app}})/V_T`$. That value already excludes the
apparatus dead space, so a comparison run at *their* alveolar ventilation must not subtract it
again. Neither paper reports that ventilation (below). This model runs at a default 4.0 L/min,
which has no primary source.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

**Neither paper publishes a ventilation.** Ventilation was titrated for each subject to
normocapnia, an end-tidal carbon dioxide of 5.5–6.5%. Minute ventilation was measured and used
in the mass balance. Even so, **no $`\dot V_E`$ and no $`f_A`$ is reported in either paper**,
and neither paper has a ventilation table. The *Anesthesiology* paper does give the definition
that the derivation above needs, in its description of the total-body-clearance method. Doses
delivered to the alveoli are computed as $`F_I \dot V_A \times 30`$ min "where
$`\dot V_A = f_A \dot V_E`$". So $`f_A`$ is the alveolar fraction of *total* minute ventilation.

**The nearest published analogue points the seventh row the wrong way.** The
paper reports pulmonary elimination clearances, $`V_1 k_{10}`$, for the eight
volunteers whose data give desflurane's residual. They are desflurane 4.11 ±
0.45, isoflurane 3.94 ± 0.34 and halothane 3.94 ± 0.33 L/min. The
seven-volunteer *Anesth Analg* cohort has 3.58 and 3.62 L/min. This model
runs at 4.0 L/min, so for the cohort in question it already matches the
study's own effective clearance. A dead-space decrement *lowers* alveolar
ventilation, which moves the model **away** from 4.11 rather than toward it.
This argument is independent of the common-mode argument, and it is stronger,
because it is specific to the one cohort that the mechanism would have to help.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- not-restated: 0.34 -->

**These clearances are a consistency check on the operating point and must not
be adopted as the operating point.** They were fitted to the same elimination
curves that this comparison is scored against, so running the model at them
would be circular. The paper itself also shows how precise they are. The same
eight subjects breathed all three agents at once from one cylinder. Their
ventilation was therefore physically identical across those three rows, yet
the fitted values still spread by about 4%.

The fourth row's volumes are round physiologic figures: 1 kg of lung tissue at
a tissue:blood ratio of 1.2, and 1.8 L of pulmonary and arterial blood. They only set how large
the added capacity is. They are not proposed as parameters. The added capacity equals 20.1% of
desflurane's fast pool, 19.7% of sevoflurane's and 23.4% of isoflurane's, about the same share
for all three. But closing the residuals needs +2.41 gas-equivalent litres for desflurane and
−1.32 for isoflurane. The conclusion does not need precise volumes. Any capacity that scales
with blood solubility is the same *fraction* of every agent's fast pool. So adding it moves all
three rows together, and it cannot produce a residual in one agent alone.

**So the cause is not identified. The disagreement's sign and size are
known.** Once the candidates above are ruled out,
what remains must be a mechanism that acts on the least soluble agent alone
and keeps its alveolar fraction high. **One candidate remains, and this
project cannot test it:**

1. *The published value.* Desflurane's recovery, the agent recovered divided
   by the agent taken up, was 105 ± 25% in those eight volunteers. Isoflurane,
   measured in the same sitting, had 102 ± 13%. Desflurane's figure has the
   wider spread of the two, and it is centred above complete recovery.

**End-tidal sampling, the eighth table row, is struck** (project owner,
2026-09-13).

*What it proposed.* The published $`F_A`$ is end-tidal gas from an
anaesthetized volunteer. This model's $`F_A`$ is the fraction in one perfectly
mixed compartment. In a lung with ventilation-perfusion dispersion, a unit
with ventilation-perfusion ratio $`r`$ has
$`P_A/P_{\bar v} = \lambda_{b:g}/(\lambda_{b:g} + r)`$ during an elimination.
So the last units to empty carry the highest partial pressure during washout
and the lowest during wash-in. A washout-to-wash-in ratio would then be biased
upward, by an amount that grows as solubility falls. Take a log-normal
perfusion distribution at log SD 1.0 with a 5% shunt. On that distribution, this
model understates the arterial retention, which it fixes at
$`\lambda_{b:g}/(\lambda_{b:g} + \dot V_A/Q)`$, by 44% for desflurane, 30% for
sevoflurane and 15% for isoflurane. That is the same rank order as the
residuals, which is what made the hypothesis attractive.
<!-- not-restated: 5 % -->

*What the methods sections settled in its favour.* The fifth table row rules
out the reading in which the published value is a **flow-weighted** alveolar
fraction. So the hypothesis rested entirely on the published $`F_A`$ being an
end-tidal sample instead. The "Materials and Methods" section of Yasuda 1991
*Anesthesiology* places that sampling port **at the tracheal tube**. The 50 ml
of Teflon that the seventh row analyses is interposed to protect the sample
from inspired gas. The paper samples mixed expired gas **separately**, from the
1-l mixing chamber, and reports it as $`F_M`$. So the quantity that the fifth
row excludes is $`F_M`$, not $`F_A`$. The fifth row therefore does not rule the
hypothesis out.

*What struck it.* The one primary human measurement of that gradient disagrees with the
hypothesis on both counts. Yasuda's own discussion flags the assumption "that the $`F_A`$
accurately indicates the anesthetic partial pressures in arterial blood". It cites Carpenter RL,
Eger EI II, *Alveolar-to-arterial-to-venous anesthetic partial pressure differences in
humans*, Anesthesiology 1989;70(4):630–5, PMID 2930000. That study sampled arterial blood,
end-tidal gas and inspired gas simultaneously in eight surgical patients.

- **Solubility runs the other way.** Measured $`P_A/P_a`$ is 1.23 ± 0.13 for
  halothane and 1.11 ± 0.09 for isoflurane, P = .009. The authors state the
  rule: the difference "should be greater with anesthetics having higher
  blood solubility". Desflurane is the least soluble agent in the comparison.
  So it should show the *smallest* gradient, where the hypothesis needs the
  largest.
- **The sign reverses through an elimination.** The mechanism is
  contamination of the end-tidal sample by physiologic dead space gas, which
  the authors call "unchanged inspired gas". The fitted relation is
  $`(P_A - P_a) = 0.22 (P_I - P_a) + 0.02`$. The authors interpret its slope
  as the sample being about 20% dead space gas. The bias therefore follows
  $`F_I`$. It is upward during administration, where $`F_{A0}`$ is measured,
  and **downward through an elimination run at $`F_I = 0`$**. Both push the
  published $`F_A/F_{A0}`$ *down*. So the measured 0.140 understates the true
  arterial ratio, and this model's 0.0935 sits further from the true ratio,
  not nearer.

*Two limits of that measurement, neither enough to revive the hypothesis.*

- Carpenter's regression was fitted over positive $`P_I - P_a`$ only, never
  at $`F_I = 0`$. Applying it to an elimination therefore extrapolates the
  mechanism, not the fitted line.
- His patients were 52 ± 16 years old, against Yasuda's 25 ± 5, and
  physiologic dead space depends on age.

For the hypothesis to hold, both limits would have to resolve in its favour,
and the measured solubility ordering would also have to reverse. Yasuda's 50 ml
guard does not settle the question either. It protects against contamination
from the **apparatus**, whereas Carpenter's 20% is physiologic dead space inside
the patient.

*What follows if the bias is real.* If the sampling bias is real and has the
measured sign, the published 0.140 is **low**. Then any reading of this section
that treats the model as washing desflurane out too fast understates the gap
rather than overstating it.

**Circuit-wall absorption, the ninth table row, is struck by the paper behind the circuit
volume.** Targ, Yasuda and Eger measured washin at 0.5–2 L/min and washout at 1–5 L/min in a
real conventional circle system. They compared both against the ideal exponential (*Anesth
Analg* 1989 Aug;69(2):218–25, PMID 2764290). Desflurane's curves lay close to the ideal line at
every flow. They deviated most at the lowest flows and near complete washin, and the comparison
here runs at neither. The authors conclude that absorption of desflurane "by circuit
components or soda lime should not hinder induction of or recovery from anesthesia". So for
**desflurane**, this measurement most nearly supports the model's inert circuit, and it strikes
the candidate.
<!-- not-restated: 5 L/min -->

**The direction does not rule it out, because a store that this model leaves out would move
the comparison toward the published value.** A wall that dissolves agent during a 30-minute
administration gives it back during the washout. That keeps the circuit fraction high, and
with it the inspired fraction, which *slows* the alveolar fall. Desflurane's residual is this
model washing out too **fast**, with the apparatus removed. A wall in the published apparatus
would have raised the published ratio above what an inert apparatus gives, which matches the
residual's sign. The sixth table row shows the same direction for rebreathing, which also
returns agent to the inspired gas. Two other grounds rule the candidate out for desflurane:
the measurement above, and the published apparatus having no circle system (the bullet on
sevoflurane and isoflurane below). This model has no wall term, so a test cannot vary one. The
circuit volume is the model's only store on the circuit side. A test checks that, for every
agent, the five-minute $`F_A/F_{A0}`$ rises at each step as the circuit volume goes from half
to twice its stored value. That direction is what rules the candidate out for sevoflurane and
isoflurane, below.

**The same study finds that a real circuit measurably retards sevoflurane and
isoflurane. That is a limitation of this simulator, but it is not a candidate
here, for three separate reasons, any one of which is sufficient.** The circuit components'
partition coefficients rank halothane > isoflurane > sevoflurane > desflurane at every
equilibration time from 7.5 min to 9 weeks, and the washin and washout curves follow the same
order.

- **§ "Known limitations" already records it.** That section gives the coefficient table and the
  ranking, states that the inert circuit is most nearly true for desflurane and least true for
  halothane, and records the decision not to add a wall term. Counting it here would suggest
  that the residual is partly explained, and it is not.
- **The departure it would be offered to explain is in the elimination rows,
  not the wash-in rows.** Sevoflurane's +3.79 SD and isoflurane's +4.15 SD are
  five-minute $`F_A/F_{A0}`$ figures. The wash-in comparison has no departure
  for anything to explain. Every agent stays inside its published spread at
  every fresh gas flow from 1 to 10 L/min.
- **On the elimination rows the mechanism moves the wrong way, and it is
  absent from the published measurement besides.** Most of that departure is
  already attributed to the breathing system. Removing the rebreathing takes
  sevoflurane to −0.15 SD and isoflurane to +0.66 SD. Wall absorption is a
  *further* store that returns agent to the circuit during the washout. Adding
  it would keep $`F_I`$ high for longer and push both rows further above their
  means, not toward them. The direction rules the candidate out for these two
  agents because the departure it would explain is the model washing out too
  slowly, the opposite of desflurane's residual. They are also the two agents
  for which wall absorption is strongest. The published cohorts also breathed
  from a non-rebreathing apparatus, whose design puts the potent agents'
  inspired fraction at or near zero. So no circle-system wall effect is present
  in the published number at all.

<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

**A mechanism that belongs to this model's circle system cannot explain a
disagreement with a measurement made without one.** Such a mechanism can only
limit what the simulator shows a learner, and "Known limitations" is where such
limits are recorded.

Whatever the explanation is, it has to fit the whole published set and not
desflurane alone. The same eight volunteers gave a halothane ratio of
0.25 ± 0.02. Halothane's blood:gas coefficient is conventionally about 2.4.
That is a textbook figure, not a parameter this project stores. So across a
roughly six-fold range of solubility, the published five-minute ratios span
only 0.14 to 0.25. That spread is narrower than a perfusion-limited model
produces.
<!-- not-restated: 2.4 -->

**Two of the three questions about the published protocol are answered, and the
third cannot be.** The three questions are the breathing system, how end-tidal
gas was sampled (the eighth table row, above), and the alveolar ventilation
during elimination. The published circuit is non-rebreathing, so its design puts
the potent agents' inspired fraction at or near zero. Its 50 ml of series dead
space cannot account for the residual. Ventilation was titrated in each subject
to normocapnia, and neither paper reports a $`\dot V_E`$ or an $`f_A`$. So the
ventilation during elimination is unknown, and the comparison has no published
value to run at.

So one candidate is left, the published value itself, and no measurement available to this
project can settle it. **No candidate is claimed as the cause.** The cause of the residual is
not identified. What is known is its sign, its size, and the nine candidates in the table
above, with what ruled each of them out.

**A band of one standard deviation tests a plausible individual, not the
cohort mean.** A deterministic model compared against a cohort *mean* would
conventionally be judged against the standard error of that mean (SEM),
$`\text{SD}/\sqrt{n}`$. For these cohorts that band is 2.6 to 2.8 times
narrower. This section makes the weaker claim on purpose. It asks only whether
the model is a **plausible individual** drawn from the published cohort.
Desflurane's wash-in sits at +0.79 SD, which is +2.2 SEM. So it passes this
claim and would fail a claim about the mean. A passing wash-in must not be
restated as "reproduces the published mean", because no test here tests that.

**Four caveats limit how strongly a pass may be stated.** The first two apply
to both directions. The last two apply only to the elimination comparison. All
four belong beside any statement of this result, wherever it is restated.

1. *The published subjects were breathing nitrous oxide.* Both protocols ran
   65–70% N₂O at the same time as the potent agents. So the measured curves
   carry a second-gas effect that this model cannot reproduce. "Known
   limitations" excludes nitrous oxide, simultaneous gases, and concentration
   and second-gas effects. "Assumptions" states that carrier gases are assumed
   not to affect kinetics. The comparison is therefore not perfectly matched,
   and the mismatch runs in a direction that is not obviously conservative.
2. *These are Gas Man parameters, derived to reproduce Eger's data.* The
   partition coefficients being tested descend from the same lineage as the
   measurements they are tested against (see § "Parameter provenance"). A pass
   shows that this implementation reproduces the intent of its parameter set.
   It does not show that the parameter set is independently right. That is
   weaker than "validated against a human measurement", and it must not be
   described as more. The intent itself is least reliable in the wash-in
   direction, which is where this comparison looks. Gas Man's own published
   agreement with patients is materially worse during wash-in than during
   maintenance (see § "Known limitations").
3. *The breathing systems differ, and by more than the measurement's own
   spread.* The paragraphs above measure the difference at 3.5 to 4.2
   published standard deviations per cohort. Any statement that this model
   eliminates more slowly than these volunteers did has to carry this caveat,
   because most of that difference comes from a rebreathing circuit rather than from a
   patient.
4. *This model has no metabolism, and it has no counterpart to the fourth
   compartment that human washout needs. Neither omission matters over five
   minutes.* Over five minutes of elimination, metabolism is negligible for all three agents,
   and the papers bound it. They report recovery, the agent recovered during elimination
   divided by the agent taken up. Recovery was 101 ± 7% for sevoflurane and 101 ± 6% for
   isoflurane in the first study, and 105 ± 25% for desflurane and 102 ± 13% for isoflurane in
   the second. Halothane gave 64 ± 9%, so the same method does detect a metabolized agent. The
   papers' elimination curves over several days must not be added to this comparison. Over
   days, the missing metabolism is no longer negligible. Nor is the fat group's blood flow,
   which § "Known limitations" weighs against two human sources that disagree about its
   direction. The measured tail also moves beyond what this model can follow within the 24
   hours for which a run is supported, long before days have passed. Every washout that these
   papers fitted needed a fourth compartment between muscle and fat, which this model lacks. On
   the published mean coefficients, that compartment's term becomes the largest in the measured
   curve about 1.8 to 3.1 hours after the 30-minute administration. It stays the largest until
   about 20.7 to 29.4 hours (the intertissue-diffusion note under § "Known limitations"). At
   five minutes, that term is about one part in twenty of what remains. A comparison over those
   hours would measure an omission rather than a parameter. So the gap over those hours is
   measured beside this comparison and is not part of it. § "The first 24 hours of elimination
   against the published mean curves" records its size and direction hour by hour, and claims
   no agreement.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

<!-- not-restated: 6 % -->

**For developers.**
`test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination` checks the
vessel-rich coefficient claim, and `test_a_larger_circuit_can_only_slow_the_elimination` checks
the circuit-volume direction. Candidate-table rows four to six were measured on an independent,
simple fixed-step (forward-Euler) integration of these equations. With no shunt, it puts
desflurane at −2.29 SD, against the shipped driver's −2.33. The seventh row used the shipped
driver. `data/patients/reference_adult.json` records the 4.0 L/min alveolar ventilation as a
program default. Both Yasuda papers, Carpenter 1989, and Targ 1989 were read at full text on
2026-09-13. Targ 1989 is also cited for the circuit volume and the inert-circuit entry in
§ "Known limitations".
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

#### The early wash-in curve against the published figures

**The first 25 minutes are compared too, point by point** (2026-10-18). The 30-minute ratio
alone barely registers the lung's gas volume or the circuit. Both papers plot the whole
$`F_A/F_I`$ curve during administration as Figure 2, as mean ± SD with each SD drawn on one
side of the marker. Neither paper tabulates it, so the values were read from the page scans.
Read the same way, each 30-minute point lands within 0.006 of the value stated in the text,
which is the size of a reading error here.

The run is `_clamped_wash_in()` in
`tests/reference/test_published_wash_in_and_elimination.py`. **It is a
test-only driver, and no setting of the shipped simulator produces the
condition it creates.** Both papers gave the agents as a square wave from a
non-rebreathing circuit, so the inspired fraction was the cylinder's from the
first breath (*Anesth Analg* p. 317, *Anesthesiology* p. 490). The shipped
circuit instead fills at its own time constant, so its $`F_I`$ lags the dial
for the first minute or more. After every step, the driver sets the circuit
back to the fixed $`F_I`$ and records the agent it adds or removes. That way
the model's conservation check still passes. Everything else is the shipped
model at the shipped operating point.

Measured 2026-10-18, as distance from each point's mean in its SD:

| Cohort | 1 to 3 min | 5 min | 7.5 to 25 min |
| --- | --- | --- | --- |
| Sevoflurane, n=7 | −0.54 to −0.69 SD | −0.22 SD | +0.48 to +0.77 SD |
| Isoflurane, n=7 | −0.70 to −0.83 SD | −0.19 SD | +0.34 to +0.76 SD |
| Isoflurane, n=8 | −0.60 to −0.67 SD | +0.08 SD | +0.32 to +1.06 SD |
| Desflurane, n=8 | +1.79 to +1.82 SD | +1.82 SD | +2.10 SD at 10 min, then +0.94 to +0.28 SD |

<!-- not-restated: 0.34 -->

<!-- not-restated: 0.54, 0.76, 2.10 -->

**Sevoflurane and isoflurane follow the published curves within one SD**.
They run a little slow in the first 3 minutes and a little fast after 7.5
minutes. The one isoflurane point beyond one SD, +1.06 SD at 12.5 minutes, is
within the reading error of the band.

**Desflurane rises faster than its cohort from 1 to 10 minutes**, by 0.034 to
0.042 in $`F_A/F_I`$, and agrees from 12.5 minutes on. The operating point is
an unlikely cause, because the same eight volunteers breathed isoflurane from
the same cylinder and the model follows their isoflurane curve. A ventilation
or lung-volume error would also move every agent the same way, but sevoflurane
and isoflurane sit slightly below their curves early on. So the likely cause
is something only desflurane has, such as its blood:gas or a tissue:gas
coefficient.

**No single stored coefficient closes the gap when it is moved only within its
measured range** (measured 2026-10-18). Each desflurane coefficient was moved alone in the
reference test, with every other value unchanged:

- **Blood:gas is the only coefficient that brings the early points into the
  band, and it does so only at values where the 30-minute comparison fails.**
  The 1-to-10-minute points come within one SD once blood:gas is about 0.55 or
  higher. Esper et al. 2015 measured 0.57 ± 0.04 in surgical patients, and at
  0.57 every early point lies within 0.83 SD. But the 30-minute ratio stays
  within one SD at every fresh gas flow from 1 to 10 L/min only up to about
  0.46. At 0.57 it fails at every flow, from −1.35 SD at 10 L/min to −2.61 SD
  at 1 L/min. Eger's 0.424 ± 0.024 has too narrow a spread to reach the values
  that bring the early points into the band.
- **The vessel-rich and muscle coefficients** cannot close the gap at any
  value within Yasuda et al. 1989's measurements (brain 0.54 ± 0.02, muscle
  0.94 ± 0.35).
- **Esper's values for all three agents** would put the sevoflurane and
  isoflurane points in the first 3 minutes 1.0 to 1.4 SD below their curves.
  So taking Esper's value for desflurane alone would mix two lineages of
  blood:gas coefficients. Taking it for all three would move the two agents
  that agree now.

<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- not-restated: 0.54 -->

Raising desflurane's blood:gas coefficient also closes little of its washout
residual. At 0.57, the open-circuit 5-minute ratio moves from −2.33 SD to
−1.97 SD. No stored value is changed, and the disagreement is recorded as a
known limitation. The five desflurane points and the isoflurane point at
12.5 minutes are checked against a regression band from −1 to +2.5 SD instead
of the agreement band. The band's upper edge sits above the largest distance
measured, +2.10 SD, so the gap cannot grow past +2.5 SD without a test failing.
`ROADMAP.md`'s planned-milestone item 31, a primary-literature coefficient set,
is where this would be weighed again.
<!-- not-restated: 2.10 -->

Caveat 1 above applies here too, and the early curve is where a second-gas
effect would show first. Its size is not measured. The volunteers had breathed
70% nitrous oxide for 30 minutes before the potent agents started, and 65%
throughout. So their nitrous oxide uptake was already small by then, and the
effect is probably small too. This model has no second-gas effect. Three of
the 1-minute SDs are stand-ins. Those error bars are lost among overlapping
marks near the axis, so each cohort's next readable bar is used instead, as
the note says.

**For developers.** `docs/references/yasuda-1991-figure-2-wash-in.md` records how the
figures were read and every value read from them.

#### What the published-data gate can and cannot resolve

**A passing gate shows only that no stored value is wrong by more than the gate
can detect, and for most stored values that is a lot** (measured 2026-10-18).
The published-data gate is the set of checks whose expected value is a published human
measurement rather than this model's own output. It contains the early wash-in points from 1
to 25 minutes, run with F_I held at the airway (§ "The early wash-in curve against the
published figures" above). It also contains the 30-minute wash-in band for each cohort at
every fresh gas flow from 1 to 10 L/min, the sign of the elimination disagreement for each
cohort, and both solubility orderings. The regression pins are not part of the gate. They
include the 5-minute elimination pin above and the late-washout tables. A pin fails on any
change at all, so it catches an accidental edit. It cannot show whether a published value would
have caught a wrong stored value. So no pin may be cited as validation of a stored value.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

To measure what the gate can detect, each stored parameter was multiplied by
a factor, for one agent at a time, with every other value as shipped. The
factor was searched between a tenth and four times the stored value, to the
nearest half a percentage point, until some published-data assertion failed.
A change to the blood:gas coefficient affects every compartment while the
tissue:gas coefficients stay as shipped. So each tissue:blood coefficient
moves inversely, exactly as it would if the stored blood:gas value alone were
wrong. Each cell of the table is the range of change that still passes every
published-data assertion, measured on 2026-10-18:

| Stored parameter | Sevoflurane | Isoflurane | Desflurane |
| --- | --- | --- | --- |
| Blood:gas coefficient | −5% / +5% | −1% / +5% | −1% / +10% |
| Vessel-rich tissue:gas, or vessel-rich volume | −15% / +15% | −4% / +11% | −6% / +55% |
| Muscle tissue:gas, or muscle volume | −44% / +102% | −17% / past +300% | −11% / +105% |
| Fat tissue:gas, or fat volume | past −90% / past +300% | past −90% / past +300% | −84% / past +300% |
| Venous pool volume | past −90% / +86% | −50% / +60% | −83% / past +300% |
| Alveolar gas volume (FRC) | past −90% / +19% | −39% / +21% | −8% / +33% |
| Circuit volume | past −90% / +76% | past −90% / +253% | −85% / +98% |

<!-- not-restated: 5 %, 6 %, 8 % -->

The first row is relative to the stored blood:gas coefficients. These are
0.65 for sevoflurane, 1.3 for isoflurane and 0.42 for desflurane.
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->

"Past" means that the gate still passed at the end of the search, at a tenth
or at four times the stored value. A tissue's volume and its tissue:gas
coefficient give the same edges, because a run depends only on their
product, which is the tissue's capacity. The search found the same edges for
both.

**What a reader may conclude from a pass:**

- **A narrow edge is not a narrow uncertainty.** Most of the tightest edges
  come from the 12.5- and 15-minute points. At those points the shipped model
  already sits at +0.75 to +0.94 SD. A change that raises the late curve by a
  few tenths of an SD then takes it past +1 SD. So isoflurane's −1% edge for
  blood:gas means that the shipped model has used most of the band there. It
  does not mean that the stored coefficient is known to 1%. The reading error
  of the published figure is about 0.3 SD. So an edge set by less movement
  than that is within the reading error.
- **Blood:gas and the vessel-rich group are now resolved on both sides**, to
  between 1% and 15% for sevoflurane and isoflurane. The early points set
  every lower edge, through the 12.5- and 15-minute points. Through the 2-
  and 3-minute points, they also set isoflurane's upper blood:gas edge and
  both agents' upper vessel-rich edges. At its 1 L/min point, the 30-minute
  flow sweep still sets the other upper edges, and most of desflurane's. A
  pass still rules out a structurally wrong model. It does not rule out a
  mis-parameterized one.
- **The gate now detects an alveolar gas volume that is too large.** Making
  the volume a fifth to a third larger slows the first minute enough to take
  it outside one SD for every agent. Doubling the volume moves sevoflurane's
  1-minute F_A/F_I from 0.537 to 0.429, which is −2.85 SD. Making the volume
  smaller still goes unseen for sevoflurane.
- **Desflurane's edges reflect its disagreement with the published data.**
  Its points from 1 to 10 minutes sit at +1.7 to +2.1 SD. They are checked
  only against the regression band, which ends at +2.5 SD. So its lower edge
  for alveolar gas volume, −8%, is the edge of that band rather than a
  published SD.
- **The gate cannot see fat for sevoflurane or isoflurane at all.** That is
  what a 30-minute load and a 5-minute washout should look like. Fat
  solubility and fat volume set the hours-long tail of washout, from which a
  learner judges emergence. Nothing here checks them against a measurement.
  § "The first 24 hours of elimination against the published mean curves"
  compares that tail with the published fits, and it asserts no agreement.
- **Making the circuit smaller goes unseen** for sevoflurane and isoflurane,
  down to a tenth of the stored value. The reason is that the early points
  are run with F_I held at the airway, so they never see the circuit. The
  gate constrains muscle only loosely.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

<!-- not-restated: 2.1, 8 % -->

The two ratios respond to almost separate parts of the parameter set, which
is why the edges fall where they do. The table gives how far each ratio moves
when one coefficient is raised by 10%. The movement is in units of that
ratio's own published standard deviation, and was measured on 2026-09-06:

| Perturbed coefficient | Wash-in | Elimination |
| --- | --- | --- |
| Blood:gas | −0.57 to −0.64 | +0.09 to +0.17 |
| Vessel-rich tissue:gas | −0.02 to −0.06 | +0.45 to +0.55 |
| Muscle tissue:gas | −0.08 to −0.15 | −0.09 to −0.12 |
| Fat tissue:gas | −0.00 | −0.00 |

<!-- not-restated: 0.06 -->

Wash-in at 30 minutes depends mostly on blood:gas and barely on the vessel-rich
group. Elimination at five minutes depends mostly on the vessel-rich group and
barely on blood:gas. This fits the rebreathing explanation above. The circuit
sets *where* the elimination ratio sits against the published mean, as an
offset fixed by the reference settings. Among the model's own parameters,
vessel-rich solubility is the one that the ratio moves with. The model's
departure from the fitted mean curves over the rest of the day is in
§ "The first 24 hours of elimination against the published mean curves".
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Two tests keep the table in step with the code.**
`test_the_published_data_gate_fails_at_a_stated_perturbation` asserts that
the gate fails for every agent at blood:gas ×0.90 and ×1.15, at vessel-rich
tissue:gas ×0.80 and ×1.75, and at alveolar gas volume ×1.50. The test does
not use ×1.10 for blood:gas, because desflurane's edge is ×1.097.
`test_the_published_data_gate_passes_at_a_stated_perturbation` asserts that
the gate still passes for every agent at fat tissue:gas ×0.50 and ×2.00, fat
volume ×2.00, muscle tissue:gas ×1.50 and circuit volume ×0.50. It also
asserts a pass at alveolar gas volume ×0.50 for sevoflurane, at venous pool
volume ×0.50 for sevoflurane and desflurane, and at venous pool volume ×2.00
for desflurane. The agents left out of those rows have an edge at or inside
the factor. Each factor sits well clear of its edge, because a test placed at
an edge would sit 0.01 to 0.03 SD from flipping. The first test fails if the
gate goes blind along a direction that it resolves today. The second fails if
the gate starts to resolve a change that this section says it cannot
resolve, so that the table is measured again rather than left stale. Neither
test widens or narrows `AGREEMENT_TOLERANCE_SD`. The limit is the published
spread, not the band.
<!-- not-restated: 1.10 -->

**For developers.** The regression pins include `PINNED_REFERENCE_STATES` in
`tests/reference/test_coupled_dynamics.py`.

#### The first 24 hours of elimination against the published mean curves
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**This subsection measures the late washout alongside the gate above. It is not
a second gate** (2026-09-27). Caveat 4 keeps the five-minute comparison out of
the papers' multi-day curves, because over those hours a compartment that this model lacks
carries the measured washout. So a comparison there measures an omission rather than a
parameter. This subsection gives the size of that omission, the hour from which it appears and
the direction in which it points. Every check here is one of three kinds. None claims agreement
with a human washout, and none may be restated as one.

1. A regression band around what the test measured. The measurements date from
   2026-09-27, or from 2026-10-03 for the muscle group's variation and the open
   circuit's modes below.
2. The conclusion that such a band supports.
3. A property of the published coefficients.

**What is compared, and under what conditions.** Both papers fit each
volunteer's elimination to a sum of five exponentials,
$`F_A/F_{A0} = \sum_i A_i e^{-t/\tau_i}`$. Each paper publishes the mean and
SD of every coefficient in its Tables 1 and 2 (*Anesth Analg* p. 321,
*Anesthesiology* pp. 494-95). The curve built from the mean coefficients is compared as
published. Its amplitudes sum to 0.912 to 0.937 rather than 1 at discontinuation, because they
are means of per-subject fits. Scaling them to sum to 1 would raise every fitted value by 7 to
10%, and lower every ratio below by 7 to 10%. The model runs the gate's own protocol: the
shipped 30-minute wash-in at the reference settings, then the vaporizer closed for 23.5 hours.
So the run ends at the supported run length of 24 hours. Its fifth minute matches the gate's
pinned five-minute ratios, so the tables continue the gate's comparison rather than starting a
second protocol. The comparison uses the gate's two conditions and no others. *Shipped* is the
rebreathing circuit at 10 L/min, which gives the tail that the chart draws. *Open circuit* is
the test-only condition that discards the circuit's contents after every step, and no setting
of the simulator can produce it. The table times are the papers' own sampling times within the
first day (*Anesth Analg* p. 317), chosen because the fit passes near a measured sample at
each. The run's last minute, 1410 min, is added.
<!-- not-restated: 10 L/min -->
<!-- not-restated: 24 hours -->

**The result, as model over fit.** The cohorts are in the order sevoflurane
and isoflurane from *Anesth Analg*, then desflurane and isoflurane from
*Anesthesiology*.
`test_the_first_24_hours_of_elimination_against_the_published_mean_curves`
checks every entry to within 1%, and every crossing hour below to within
0.1 h. The 1410-minute rows were measured on 2026-10-17, and the rest on
2026-09-27:

| Minutes | Sevoflurane, shipped | Isoflurane, shipped | Desflurane, shipped | Isoflurane (second study), shipped |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 1.20 | 1.33 | 1.11 | 1.42 |
| 30 | 0.61 | 0.71 | 0.75 | 0.88 |
| 60 | 0.81 | 0.87 | 0.93 | 1.08 |
| 120 | 1.01 | 1.07 | 1.11 | 1.33 |
| 240 | 1.20 | 1.26 | 0.88 | 1.52 |
| 400 | 1.02 | 1.07 | 0.55 | 1.23 |
| 600 | 0.74 | 0.78 | 0.56 | 0.86 |
| 800 | 0.67 | 0.68 | 0.80 | 0.74 |
| 1400 | 1.23 | 1.11 | 2.09 | 1.15 |
| 1410 | 1.24 | 1.12 | 2.11 | 1.16 |

| Minutes | Sevoflurane, open circuit | Isoflurane, open circuit | Desflurane, open circuit | Isoflurane (second study), open circuit |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 0.80 | 0.98 | 0.64 | 1.05 |
| 30 | 0.43 | 0.51 | 0.53 | 0.63 |
| 60 | 0.58 | 0.64 | 0.65 | 0.79 |
| 120 | 0.70 | 0.77 | 0.76 | 0.95 |
| 240 | 0.82 | 0.85 | 0.58 | 1.04 |
| 400 | 0.67 | 0.69 | 0.36 | 0.79 |
| 600 | 0.47 | 0.48 | 0.37 | 0.53 |
| 800 | 0.43 | 0.42 | 0.54 | 0.46 |
| 1400 | 0.81 | 0.71 | 1.39 | 0.74 |
| 1410 | 0.82 | 0.72 | 1.41 | 0.75 |

<!-- not-restated: 0.36 -->

<!-- not-restated: 0.65, 0.76, 0.42, 0.54 -->

The next table gives the hours at which the shipped tail crosses the fitted
curve, and how far from the curve the tail sits between crossings:

| Cohort | Below from | Above from | Below from | Above from | Widest below, middle stretch | At 23.5 h |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sevoflurane | 0.13 h | 1.98 h | 6.88 h | 20.65 h | 0.67 at 12.9 h | 1.24 |
| Isoflurane | 0.17 h | 1.62 h | 7.33 h | 21.78 h | 0.68 at 13.5 h | 1.12 |
| Desflurane | 0.10 h | 1.30 h | 3.38 h | 15.30 h | 0.51 at 8.1 h | 2.11 |
| Isoflurane (second study) | 0.22 h | 0.78 h | 8.42 h | 21.05 h | 0.74 at 13.7 h | 1.16 |

In the open circuit, the tail falls below the fitted curve between the second
and the sixth minute. For sevoflurane and the first study's isoflurane, it
stays below the curve for the whole run. Desflurane rises back above the
curve at 19.18 h. The second study's isoflurane sits above the curve between
2.45 and 4.58 h, by 5% at most. Between 8 and 13 hours, the open-circuit
tail is a third to a half of the mean curve in every cohort (0.34 to 0.46).
<!-- not-restated: 5 % -->
<!-- not-restated: 0.34 -->

**Read in stretches.** The shipped tail sits above the fitted curve at five
minutes. That excess is the apparatus term that the gate records. The tail
falls below the curve from 6 to 13 minutes until 0.8 to 2.0 hours. At the
widest, around 15 to 25 minutes, it is 15 to 44% below. It then runs above
the curve until 3.4 hours for desflurane and 6.9 to 8.4 hours for the other
three, by 12 to 52% at the widest. From there it runs *below* the curve until
15.3 hours for desflurane and 20.7 to 21.8 hours for the others. At the
widest it is a third below, near 13 hours, and for desflurane it is a half
below, near 8 hours. It finishes above the curve, by 12 to 24% at 23.5 hours
and by a factor of 2.1 for desflurane. The middle stretch answers the
question that the intertissue-diffusion note asked. In every fitted curve,
the fourth compartment's term is the largest from 1.8 to 3.1 hours until
20.7 to 29.4 hours
(`test_the_fourth_compartment_is_the_largest_term_over_the_recorded_hours`
re-derives those hours from the coefficients). This model has no such term.
Over those hours its tail falls faster than the measured mean. With the
apparatus gone, it does so from the start. In the shipped condition, it does
so only from the seventh hour. Until then the rebreathing circuit and the
muscle group's slow return, described below, hold the tail above the curve.
With the circuit's return taken away, the same hours sit at or below the
curve.
<!-- not-restated: 2.1 -->

The model's muscle group returns agent more slowly than the fitted muscle
term does. That is why the ratio of model to fit peaks in hours 2 to 4. In
the open circuit, this peak is the tail's closest approach to the curve. In
the shipped condition, it is the tail's furthest excess over the curve. A
fitted time constant is an apparent one, read off the whole curve, so the model's terms are
read off its own curve in the same way (2026-10-03). They are the exponential components of the
open-circuit model, which is the five equations of § "Governing equations" with nothing
inspired. The table gives each term as its time constant in minutes and its amplitude in
percent of $`F_{A0}`$, with the cohorts in the same order as the tables above. A test checks
the model's terms to within 0.2%:

| Term | Sevoflurane | Isoflurane | Desflurane | Isoflurane (second study) |
| --- | ---: | ---: | ---: | ---: |
| Muscle, model | 155 min, 2.37% | 161 min, 4.31% | 92.6 min, 2.47% | 161 min, 4.31% |
| Muscle, fitted | 81.7 min, 4.60% | 85.0 min, 7.19% | 48.9 min, 4.86% | 80.0 min, 5.93% |
| Fat, model | 2650 min, 0.060% | 2860 min, 0.12% | 1540 min, 0.063% | 2860 min, 0.12% |
| Fat, fitted | 2230 min, 0.028% | 2310 min, 0.072% | 1350 min, 0.031% | 2110 min, 0.080% |

So the model's muscle term is 1.89 to 2.02 times as slow as the fitted one,
and 0.51 to 0.73 times as large. Its fat term is 1.14 to 1.36 times as slow
and 1.5 to 2.1 times as large. The fitted fat amplitudes in that comparison
have SDs that are 53 to 94% of their means. A group's isolated time constant is its tissue
volume times the tissue:gas coefficient, divided by its blood flow times the blood:gas
coefficient. The reference adult has 33 L of muscle perfused at 0.9 L/min and 14.5 L of fat
perfused at 0.3 L/min. On these values, the isolated constants for sevoflurane, isoflurane and
desflurane are 135, 127 and 84.7 minutes for muscle, and about 2500, 2600 and 1500 minutes for
fat. Each is shorter than the group's apparent constant. The arterial blood that reaches a
group during the washout still carries agent, because the lungs do not exhale all of the agent
in each group's return, and the rest goes round again. So a store empties more slowly than its
own blood flow alone would empty it, and the isolated constant understates how slow the
model's term is.
<!-- derived: 135 minutes from data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33.0, tissue_groups.muscle.perfusion_fraction = 0.18, default_cardiac_output_l_min = 5 -->
<!-- derived: 135 minutes from data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 127 minutes from data/agents/isoflurane.json tissue_gas_partition_coefficients.muscle = 4.5, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 84.7 minutes from data/agents/desflurane.json tissue_gas_partition_coefficients.muscle = 0.97, blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 2500 minutes from data/patients/reference_adult.json tissue_groups.fat.volume_l = 14.5, tissue_groups.fat.perfusion_fraction = 0.06, default_cardiac_output_l_min = 5 -->
<!-- derived: 2500 minutes from data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34.0, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 2600 minutes from data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70.0, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 1500 minutes from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13.0, blood_gas_partition_coefficient = 0.42 -->
<!-- not-restated: 2.1 -->

The claim that the muscle group's slow return places this peak in hours 2 to 4
was tested on 2026-10-03. The group's tissue:gas coefficient was lowered to
0.58 to 0.67 of its stored value, with everything else as stored. This change
makes the group's isolated time constant equal to the fitted one, and its apparent time
constant 1.09 to 1.28 times the fitted one. Over a 30-minute wash-in the group is far from
equilibrium. It takes up agent about as fast as its blood flow brings it, whatever its
capacity. So it contains only 4 to 10% less agent at discontinuation, and the change mainly
alters how fast that store comes back. With the change, in six-hour runs, the open-circuit peak
comes at 0.62 to 1.45 hours instead of 2.17 to 3.92. At four hours the tail is 0.50, 0.62, 0.24
and 0.70 of the fitted curve, instead of 0.82, 0.85, 0.58 and 1.04. The shipped peak comes at
0.65 to 1.97 hours instead of 2.27 to 4.15. The tail lies above the curve until 1.6, 3.7 and
4.5 hours instead of 6.9, 7.3 and 8.4. With the change, desflurane's tail never rises above the
curve.
<!-- not-restated: 0.65 -->

The late excess is due to the model's larger and slower fat term, and it is
still growing when the run ends. The ratio rises between minutes 1400 and 1410
in every cohort and in both conditions. It grows because the fitted curve is
still falling on the fourth compartment's time constant, while the model is
already falling on its fat term's.

**Three limits on how far these results can be read.**

1. *The fitted mean curve is not the measured mean, and where it can be
   checked it runs high.* Five minutes is the one time at which both are
   published. There, the mean coefficients give 0.194, 0.243, 0.147 and 0.228,
   against measured means of 0.157 ± 0.020, 0.223 ± 0.024, 0.14 ± 0.02 and
   0.22 ± 0.02. The fitted values are above the measured ones by
   1.84, 0.83, 0.33 and 0.39 published SD, or by 3.5 to 24%
   (`test_the_fitted_mean_curves_run_above_their_own_measured_five_minute_means`).
   A sum of exponentials built from mean coefficients over-states the mean of
   the subjects' curves wherever a time constant varies between subjects.
   Every one of these time constants does vary, with SDs of 10 to 52% of the
   means. So every ratio above understates the model against the volunteers'
   mean. At the one point where the size of that understatement can be
   measured, it is 3.5 to 24%. For sevoflurane, the open-circuit model sits
   0.15 SD below the measured five-minute mean and 20% below the fitted curve
   at the same instant. The whole of that 20% comes from the fit itself.
   Nothing here corrects for this, because no measured mean exists at the
   later times to correct against. Both papers plot those later means
   (Figures 3 and 4), but on logarithmic axes from which no number was taken.
2. *The term that carries the measured curve over the middle stretch is as
   uncertain between subjects as it is large.* The fourth compartment's
   amplitude is 0.717 ± 0.800, 1.296 ± 1.237, 0.775 ± 0.482 and 1.125 ± 0.669
   (×100). Those SDs are 59 to 112% of the means. So a tail that lies a third
   to a half below the mean curve over those hours is inside the spread of the
   volunteers' own curves. The direction and the mechanism are settled. The
   model has no term there, and in the open circuit the model's tissue return
   alone is a third to a half of the mean. The size is known to about a factor
   of two, and no better.
3. *The published subjects breathed nitrous oxide throughout, and the
   parameters under test descend from the lineage of the data.* These are
   caveats 1 and 2 of the gate, unchanged.

**How much of the gap sevoflurane's missing metabolism could account for:
little, and in the wrong direction over the middle stretch.** This model has no
metabolism (§ "Known limitations"). A human does, and for sevoflurane it is
2 to 5% of the absorbed dose (Kharasch 1995, cited under
§ "Supported run length"). The module has a first-order sink on the
vessel-rich group that is used only in tests. The sink is placed where the
papers' own mammillary model places hepatic elimination: "the second
compartment (vessel-rich group; k20)", *Anesth Analg* p. 318. It runs at that
paper's fitted sevoflurane rate constant, k20 = 0.0094 min⁻¹ (Table 3,
p. 321). The SD of that constant is 0.0171, so the cohort could not tell it
from zero. The sink runs during the
administration as well as the elimination, because a human's metabolism does.
In this model, by the end of the run, the sink removes 7.8% of the 30-minute
uptake in the shipped condition and 7.1% in the open circuit. Both figures are
above Kharasch's range, which is what makes the sink's effect a bound. The sink
lowers the shipped tail by 4.5% at five minutes and by 1.9 to 2.9% from 30
minutes on. It lowers the open tail by 5.0% and then by 1.3 to 1.8%
(`test_sevoflurane_s_missing_metabolism_moves_the_tail_by_a_few_percent`). So
where the shipped model runs above the fitted curve, metabolism could account
for about an eighth of the excess where the excess is widest. That is 2.8 of
the 20.4 points at four hours, and 3.0 of the 24.0 points at 23.5 hours. Where
the shipped model runs below the fitted curve, metabolism widens the gap by the
same few percent. The reason is where the sink looks. Hepatic clearance sees
the arterial partial pressure, which through the tail is the alveolar one, and
it never sees the stores that feed it. The model's own conservation identity is
checked across the removals. The removals are recorded as exhausted agent, so
that § "Mass-balance identity" remains true with the sink in place.
<!-- not-restated: 5 %, 5.0 %, 1.3 -->

**What a learner sees of it: nothing on screen, and the record gains the
number.** The departures above are in $`F_A/F_{A0}`$. At the gate's 1% dial,
$`F_{A0}`$ is 0.805, 0.672 and 0.876% of an atmosphere for sevoflurane,
isoflurane and desflurane. So the shipped alveolar trace falls below the
readouts' 0.01 percentage points (§ "Displayed precision") at 2.8, 4.2 and 1.9
hours. That is before the stretch over which the trace runs below the measured
mean. On the chart's linear axis, which is fixed at 3 MAC, the trace is a few
pixels high well before that. A higher dial scales $`F_{A0}`$ with it, and
keeps the trace above the 0.01 percentage-point limit for longer. A 6%
desflurane dial keeps it there until about the fifth hour, which is inside
desflurane's stretch. So a learner who runs a case long can reach the
shortfall. The intertissue-diffusion note is where a reader of that tail is
sent.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->
<!-- not-restated: 6 % -->

**The result does not bear on § "Supported run length"**, which gives the full reasoning. The
departures measured here come from the missing fourth compartment and from the fat group's own
size, and both are present from the first hour to the last. The limit of 24 hours rests on two
other omissions growing past negligible. So shortening the span would not remove these
departures from the tail. Extending it would add the late excess, which is still growing at the
boundary.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**For developers.** The checks are in
`tests/reference/test_late_washout_against_published_fits.py`. With these numbers, the
intertissue-diffusion note under § "Known limitations" and § "Supported run length" can give a
number as well as a direction. The coefficients were read at the source on 2026-09-27:
*Anesth Analg* p. 321 through the private corpus's text layer, and *Anesthesiology* pp. 494-95
as page images. `test_the_published_coefficients_sum_below_one_at_discontinuation` checks
their sum. The model runs at the shipped 0.1 s step, sampled once a minute.
`test_the_run_ends_at_the_supported_run_length` checks the run's length, and
`test_the_twenty_four_hour_run_opens_from_the_five_minute_gate_s_own_ratio` checks that its
fifth minute matches the gate's ratios to four decimal places. The model's terms are the
exponential modes of its open-circuit system, decomposed from its state at discontinuation.
`test_the_model_s_apparent_muscle_and_fat_terms_against_the_fitted_ones` checks them. The
modes match the stepped open-circuit run to within 0.08% at every minute from the fifth. The
run lies above the modes by the amount that the driver re-breathes within each step before it
empties the circuit. `test_the_muscle_group_s_slow_return_places_the_tail_s_rise_in_hours_2_to_4`
checks the result of lowering the muscle group's coefficient.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

### Mass-balance test

Long wash-in, steady-delivery, and washout simulations must satisfy:

$$
|\varepsilon_M|
\leq
\varepsilon_{\mathrm{absolute,max}}
$$

or:

$$
\varepsilon_{\mathrm{relative}}
\leq
\varepsilon_{\mathrm{relative,max}}
$$

using the release tolerances documented above.

Held by `test_long_wash_in_and_washout_validate_agent_simulation` in
`tests/reference/test_sevo_patient.py`, and for isoflurane and desflurane by
`test_wash_in_and_washout_validates_agent_simulation` in
`tests/reference/test_multi_agent.py`.

### Closed-form agreement test

A run driven through its own controls must give identical results from the
closed form and from the stepped solver. The states derived from the run
definition, at instants that the stepped system passed through, must equal the
states that the system reached by stepping.

The comparison covers every compartment at every instant probed, not only the
endpoints. "Deterministic replay test" gives the reason. The comparison must
also cross at least two setting changes, because a stretch of constant settings
is the easy case. What a run definition has to get right is the boundary
between two of them.
The tolerance is absolute rather than relative. It is stated in fractions of
one atmosphere, because that is what the compartments contain and what a
readout converts. A relative tolerance would tighten without limit on the
near-zero tissue fractions of an induction, and it would say nothing about a
displayed digit.

The required agreement is far tighter than the two-decimal percent set under
§ "Displayed precision", and far looser than floating-point noise. So a real
divergence fails and a rounding difference does not.
`tests/unit/test_run_definition.py` checks `state_at` and `evaluate` against a
run stepped alongside its definition, and records the figures measured. Its
`test_evaluate_matches_a_stepped_run` and `test_state_at_matches_a_stepped_run`
make that comparison on one run that crosses two setting changes.
`tests/unit/test_resume_at.py` and `tests/integration/test_controller.py` apply
the same comparison in two more cases. One is a system started at a keyframe
and stepped from there. The other is a branch compared against its parent.
Each test records its own figure and the headroom left above it.

The comparison against the stepped system carries the claim, because the stepped solver is the
independently written solution of the same equations that the closed form is
checked against.

### Parameter-recovery test

The model must return a stored parameter when it is run through a measurement
procedure whose result that parameter fixes. Each procedure is derived from a
physical law, not from the equations in this document. Lerou and Booij used
this device to check their own system model. They simulated the closed-circuit
helium dilution measurement of alveolar volume (Lerou JG, Booij LH.
Model-based administration of inhalation anaesthesia. 1. Developing a system
model. *Br J Anaesth* 2001;86:12–28, doi:10.1093/bja/86.1.12; PMID 11575385,
retrieved from PubMed and read at the abstract 2026-10-25).

**It catches a class of error that the other verification tests cannot.** The
§ "Independent-solution test" integrates the equations that this document
states. If this document states an equation wrongly, the oracle reproduces the
error and agrees with the code. The § "Mass-balance test" catches an error
only when agent is lost or created. Suppose this document had written the
tissue capacity as $`V_i\lambda_{i:b}`$, leaving out the blood:gas factor, and
formed the tissue's rate to match. Agent would still be conserved, and the
oracle would agree with the code. A tissue volume measured by the Fick
principle would come back divided by $`\lambda_{b:g}`$.

`tests/reference/test_parameter_recovery.py` runs two procedures for each of
the three agents.

- `test_an_alveolar_volume_recovered_by_closed_circuit_dilution_matches_the_stored_value`
  is Lerou and Booij's procedure. The circuit fills while ventilation is
  stopped. The circuit is then closed by setting the fresh gas flow to zero,
  and the lungs are ventilated from it with the cardiac output at zero. With
  no blood flow, the agent behaves as an insoluble tracer, which is the role
  helium plays in the real measurement. Conservation then gives
  $`V_A = V_C(F_1-F_2)/F_2`$, where $`F_1`$ is the circuit's fraction when it
  is closed and $`F_2`$ is the fraction that the circuit and lungs share once
  they have mixed.
- `test_a_tissue_volume_recovered_from_its_washin_matches_the_stored_value`
  integrates each tissue group's uptake through the opening wash-in by the
  Fick principle, $`\dot U_i = Q_i\lambda_{b:g}(F_a-F_i)`$. It divides the
  total by $`\lambda_{i:g}F_i`$ at the end of the run, which is the agent that
  one litre of the tissue holds at its own fraction.

Each recovered value must equal the stored one to within a relative tolerance
at the level of rounding. The test module states each tolerance beside the
residual it measured.

The zero fresh gas flow is not the closed-circuit technique that § "Breathing
circuit" says this model does not represent. That technique needs fresh gas
matched to the patient's uptake. This procedure has no fresh gas and, at zero
cardiac output, no uptake.

Like the other verification tests, these check that the equations are the ones
intended. They cannot show that a stored value is right, because each
procedure recovers whatever value the data files hold.

### Deterministic replay test

Two runs with identical:

- initial state;
- parameters;
- setting changes;
- event ordering; and
- simulation steps

must produce identical snapshots and identical run definitions.

Identical means element for element. Every segment and keyframe of one run's
definition must equal the same segment and keyframe of the other's, and the
snapshot must be the same in every field. Equal endpoints are not enough, and
neither is agreement within a tolerance. Comparing endpoints would pass a pair
of runs that diverged and then came back together. Also, a branched run is
compared against its parent at every instant they share.

The two runs must also be driven differently in real time. One run takes the
same steps one per tick, and the other takes them in ragged bursts. The
interface must also read the two runs between ticks at different rates.
Driving both runs identically tests the model on one trajectory twice. That
is a weaker claim than the one "The reproducibility guarantee" makes, which is
that how the ticks fell cannot affect the run.

The bursts that a **playback rate** produces are one case of this, and they are
tested as one. The test uses the rates that the interface actually offers, not
invented burst sizes. So a rate added to that ladder is covered on the day it
is added.

Held by `test_identical_runs_produce_identical_snapshots`,
`test_a_run_reaches_the_same_definition_however_the_ticks_fell` and
`test_a_run_reaches_the_same_definition_at_every_playback_rate` in
`tests/integration/test_sevo_controller.py`.

### Canonical evaluation test

A run that is queried while it is built must give the same result as the same
run when it is never queried. The results must match element for element,
across the whole state vector, at every instant probed and in every keyframe
stored. This property shows that the canonical result belongs to the run
definition rather than to the caller. A cache, a memoised propagator or a
reused buffer would remove the property while looking like an optimisation.

The test enforces two further properties. First, a branch that opens from one
of its parent's keyframes must reproduce the parent element-wise at every
instant they share. That is what "The canonical evaluation rule" owes
`ROADMAP.md` item 12. Second, the program must reject a value from the display
path where a canonical value is required. That makes the rule a property of
the program rather than of the reader.

The measured separation between the two paths is published under § "The
canonical evaluation rule". The same module holds that separation to bounds,
one for each quantity. So a change to the equations, to the propagator or to
how a window is walked fails there. It does not silently move a figure that
this document prints. The compartment fractions and the cumulative
accumulators have separate bounds because their displays resolve four orders
of magnitude apart. A single bound covering both would have to be the looser
one.

All of these are in `tests/reference/test_canonical_evaluation.py`.
`test_querying_a_run_does_not_change_what_it_answers` and
`test_querying_a_run_does_not_change_the_keyframes_it_stores` hold the first
property. `test_a_fork_opening_from_a_keyframe_reproduces_its_parent` holds
the branch. `test_a_display_value_cannot_open_a_run_definition` holds the
refusal, and `test_the_display_path_stays_within_its_measured_separation`
holds the bounds.

## Runtime controls

The following settings may change during a run without resetting state:

- fresh gas flow;
- delivered agent concentration;
- alveolar ventilation; and
- cardiac output.

A change affects transfers prospectively from the next simulation step.

Changing cardiac output recalculates tissue flows:

$$
Q_i=f_iQ
$$

It does not alter existing blood or tissue stores.

Changing ventilation does not alter existing circuit or alveolar stores.

Changing delivered concentration does not alter existing circuit concentration.

**These four are the model's inputs, and the list contains every model input
and nothing else.** The interface has settings of its own that also change
during a run without resetting state: the playback rate, the chart's time base,
and the choice of which compartment traces are drawn. None of them is a model
input, because none affects the model's state. Identical inputs still produce
identical results, so a case played at sixty times real time is the same run
watched faster. § "Interface boundary" sets the constraints on those settings,
and § "The reproducibility guarantee" rules out treating the playback rate as
an input.

**The playback rate does decide when an input arrives.** A control changed
*during* a run first acts at the next tick, and ticks fall every
`multiplier × 0.1` s of simulated time, where the multiplier is the playback
rate. So the same slider moves made at two different rates are different
inputs, and they produce different runs. At a faster rate, the learner has a
coarser choice of when an input acts. § "Supported simulation step" measures
this.

### Halting on a marked crossing

A run may be **marked** in two ways. A *time bookmark* marks an instant of the
case. A *MAC target* marks a height on one named compartment, stored as a
multiple of the running agent's 1 MAC. § "MAC multiples as a display unit"
states what that multiple asserts on each compartment, and marking a height
does not widen that claim. A mark is a question asked of the case rather than
an input to it. Nothing marked enters a governing equation, opens a segment or
moves a keyframe. A run stepped through its marks computes what an unmarked
run computes, element for element. The only thing a mark changes is when the
run stops.

**The crossing is tested on every simulation step, and the run halts on the
step that crossed.** In this one respect a halt is finer than anything a
learner can reach while the run is playing. § "Supported simulation step"
publishes the grid on which a *control change* lands. That grid is
`multiplier × 0.1` s, so 0.1 s at 1x and 30 simulated seconds at 300x. A halt
is not on that grid. It lands on the crossing step itself, at every playback
rate. So the concentration displayed beside a halt is the reading on the
first step at or past the height the learner marked. It lies
within one simulation step of that height, not up to a whole burst's worth of
simulated time past it. One step's change can still show on screen. It grows
with the gap between a compartment and the gas reaching it, and with the flow
that carries that gas in. With 8% sevoflurane at 10 L/min, a 0.10 ×MAC circuit
target halts showing 0.11 ×MAC. The jump can be larger on other compartments.
Run the same settings for 120 s with alveolar ventilation at 0 L/min, so that
the alveolar reading stays at zero while the circuit fills. Restoring
ventilation to 12 L/min then makes a 0.10 ×MAC alveolar target halt showing
0.12 ×MAC, two display counts past its mark. A halt one or more counts past
its mark is therefore correct. It lies above the mark on a rising crossing and
below it on a falling one, and it is not a
detection fault. If the test ran once per rendered frame instead, the same
bookmark would stop at a different concentration depending on how fast the
case was being played. Nothing on screen would say so. Two branches nominally
taken "at 0.8 ×MAC" would then open from two different states.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->

**A halt leaves the run paused, and resuming is explicit.** The reason is the
grid in the paragraph above. A halt is exact, but a setting changed while the
run plays first acts at the next tick. Without the pause, "halt at 0.8 ×MAC,
then turn the vaporizer off" could turn the vaporizer off up to 30 simulated
seconds after the value being looked at. The displayed value would be right,
and the action taken from it would be wrong. No step is taken while the run is
paused, and a setting changed then applies at once. So the learner gets the
safe order, pause, change, resume, without having to know it. The run's status
reads "Paused — stopped on your mark", so the halt is not mistaken for the
learner's own Pause while two runs are compared and the branch control is
withdrawn.

**A crossing is a transition between two steps, never a comparison at one
step.** The test asks whether the reading was on one side of the height at the
previous step and is on the other side at this step. Suppose the test were
instead "the reading is at or above the height". A run that settled exactly on
a marked height would then pass the test on every later step and could never
be advanced past it. Also, a comparison at a single reading cannot say *which*
step crossed, and saying that is the whole purpose of the halt. The height
counts as reached on arrival and not on departure, in both directions. This
rule also makes a halt resumable. The run is left standing on the crossing
step. So the earlier reading for the next step is the crossing step's own
reading, and the crossing that was just halted on is not crossed again.

**A MAC target halts on every crossing, in either direction.** A target names
a compartment and a height and has no direction. Consider a case taken up
through 0.8 ×MAC and back down through it. It has reached what the learner
marked both times, so it stops both times. A target that halted once and then
had to be set again would make two identical-looking targets in the list behave
differently, according to which one had already halted. Nothing on screen would
distinguish them, and that is the hidden mode this interface is built to avoid.
Resuming a paused run takes one control, and the learner is already looking at
it.

**The state of a mark is one of six outcomes.** Each of the last four has its
own wording, because a reader would otherwise mistake it for one of the
others.

- **Still running**: nothing has happened yet, and the run can still reach the
  mark.
- **Passed**: a time bookmark at or behind the run's own clock. This outcome is
  positional. It is true however the clock came to be there. A step may have
  taken the run past the mark. The run may have been forked at the mark and
  opened standing on it. Or the learner may have marked an instant the case
  had already run past. A passed mark on the trunk is one at which a branch may
  be taken (§ "What this requires of a branch").
- **Reached**: a MAC target that the run has stood on at least once. Either the
  run halted on the target, or the target lies inside a step that the run
  stands on or opened on. This outcome is historical. It is a property of the
  run rather than of the mark, so a reset and a change of agent clear it,
  because each begins a new run.

  Two steps are checked again against the current marks every time the mark
  outcomes are read. The first is the last step of a stopped run, whether it
  paused, halted or reached the supported run length, on a trunk or on a
  branch. A run stopped by a failure is not checked, because a failure is not a
  pause. The second is the step on which a branch opened. A branch stands on
  that step from the start, however far it has run since, so the step counts
  as the branch's own. Suppose a target is added after the step that crossed
  it. The target then shows as reached on a trunk standing on that step and on
  every branch opened there, whichever came first, the target or the branch.
  The run keeps that result after it moves on. A run that went past the step
  before the target was added never stood on it with the target marked. That
  run shows the target as still running, as it shows any height it did not
  stop on.
- **Not reached within the supported run length**: the run has stopped at the
  limit that § "Supported run length" declares, and this mark is still
  outstanding. A height above a compartment's asymptote is never reached. So
  this outcome is a result rather than an interruption. A row that still read
  "still running" would invite a learner to wait for something that cannot
  arrive.
- **Before this branch opened**: a time bookmark earlier than the instant at
  which this branch forked. A branch inherits its trunk's marks, so such a
  bookmark comes across with the rest, and no step of the branch can reach it.
  It is inherited rather than dropped so that a trunk's list and a branch's
  list do not disagree about what the case is marked at
  (`docs/ARCHITECTURE.md` § "What a branch is"). This outcome can be decided
  without running anything. Reporting it as the previous outcome would tell a
  learner that a longer run might reach the mark, which is false. A MAC target
  has no equivalent outcome. A height can be reached from either side, so a
  branch may cross a height that its trunk never crossed.
- **Not reached before the simulation error**: the run stopped on an exception
  that the model could not step past, and this mark is still outstanding.
  Resuming is not offered, because the next step would raise the same
  exception as the last one. So only a reset could reach the mark, and a reset
  is a different run. This outcome is worded differently from the cap outcome
  above, because the cap is what it would be mistaken for. The two stop a run
  for opposite reasons. At the cap, the model has answered the question and
  says that a longer run would not change the result. In a failure, the model
  could not answer at all. Reporting a failure as the cap would turn what this
  run did into a claim about what the model supports. When a run is at the cap
  *and* has failed, the cap is what is reported. Nothing steps after a
  failure, so such a run ran out of supported time first and was failed by a
  setting afterwards.

**The two kinds of mark are reported in two vocabularies, and the clock is
what divides them.** A run's clock only increases, and it never goes below the
instant the run began. So the state of a *time bookmark* is a position: either
ahead of the clock, or at or behind it. No history is needed to decide it. A
*MAC target* names a height, and a compartment may arrive at a height, leave it
and arrive again. So the only thing that can be said of a target is what the
run did. "Passed" and "before this branch opened" therefore apply only to time
bookmarks, and "Reached" applies only to targets. The other three outcomes
apply to both.

**A bookmark is reported as "passed", never as "reached".** Suppose a
bookmark's state were decided only from where the run halted. Then every
instant that the run is at or behind, but never *stopped on*, would read "still
running", which says the run can still reach the mark. Seven cases were found
(2026-09-20) in which no step could make that true. "Reached" would also go
wrong whenever the clock moves backwards. In the reference simulator, a
bookmark is a pause point that fires on the original pass and on every replay
alike (Philip JH, *Workbook for Gas Man®*, Med Man Simulations, chapter 2,
"Using Bookmarks"). So a rewind, or truncating at a mark and running on, leaves
a mark that will stop the learner again, and any earlier claim that it was
reached is no longer true. "Passed" is worked out again from the clock every
time the row is drawn, so it survives a rewind. "Reached" would have to be
withdrawn, and failing to withdraw it is a displayed value going quietly wrong.

### The control-input record

Every change to a control that the model runs under is recorded against the
simulated time at which it took effect. The record is kept with the run and
cleared with it. § "The control-input timeline" and the display rules below say
what the record is for, what it asserts, and why it has its shape.

#### The run is that record, and every state is derived from it

**What is held.** A run is stored as two things. The first is the settings in
force at each moment: the four controls above, together with the patient and
agent parameters that the equations read. The second is one *keyframe* per
change, which is the state at the instant that change took effect. Nothing
else about the run is stored. Flows are stored as they were set, in liters per
minute, for the reason that § "Time" gives. The record lives in
`core/run_definition.py`.

**What is derived.** While every setting is held constant, the equations are
linear and time-invariant. So between two changes, the propagator under
§ "Selected method (as implemented)" is exact over any horizon, not only over
one simulation step. The state at any instant is therefore one propagation from
the keyframe that opens the stretch containing that instant. No value has to
have been recorded for the state to be recoverable. Each keyframe is computed
the same way: one propagation per stretch, composed in order from the start of
the run.

**Two paths, and they differ in composition order rather than in method.** To
return the state at a single instant, the program applies one propagator to the
keyframe that brackets the instant. To draw a window of evenly spaced columns,
it instead reuses one propagator across the columns inside a stretch, chaining
from the first column. That reuse is what makes a frame cheap. Both paths solve
the same equations exactly. They differ only in the order in which the
floating-point operations are composed. This was measured on 2026-09-07 against
a stepped 600 s sevoflurane run with two setting changes, reaching a fraction
of 0.0316. The single-instant path stays within 1.8e-14 of the stepped run, and
the window path within 3.7e-15. Both figures are absolute differences in a
fraction of one atmosphere. Both are about ten orders of magnitude below 1e-4,
the smallest difference that the two-decimal percent readout under
§ "Displayed precision" can show. So neither path can change a displayed digit.
§ "The canonical evaluation rule" below states, as a guarantee, which of the
two paths a stored, exported or branched value may be taken from.

**Why the run is stored as a definition.** A 30-day case at the fixed 0.1 s step,
stored as one sample per step, takes 3.16 GiB. The same case stored as its
settings and their changes takes 1.6 MiB, about two thousand times less. The
second gain is that the time to draw a chart window does not grow with how long
the run has been going.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**What does move the cost is the number of changes inside the window**,
because each stretch in view needs its own propagator. On the same thirty-day
run, a full-span window at 600 columns costs 14.2 ms with two changes in view,
231 ms with sixty, and about 1.1 s with six hundred, on a frame that forms all
its propagators. Once the changes outnumber the columns, sampling 600 instants
is the wrong way to draw the run. What to draw instead is a question for the
interface.

**The number of changes moves the cost of the first frame only.**
`RunDefinition.evaluate_anchored` keeps the propagators that each window uses,
so that the next window can reuse them. All but three cover an interval that
the grid fixes: either the column spacing, which the time base fixes, or a
stretch's offset to its first grid column, which the anchoring fixes. The three
that change are those for the window's two bounds, and the one for the offset
in the stretch where the window opens, whose first grid column is the first one
past the left edge. So a window that follows the run forms two new propagators
every frame. It forms the third only when its left edge has passed a grid
column since the frame before. It also forms those of any stretch newly in
view, and a new column spacing forms them all again.

The cost was measured on 2026-10-04 on a 24-hour run, the longest that
§ "Supported run length" allows, with every setting distinct. The full-span
window at 600 columns has its left edge fixed at the run's opening. With two,
sixty and six hundred changes in view, it costs 13.2 ms, 179 ms and 819 ms on
its first frame, and 6.3 ms, 5.9 ms and 8.3 ms on each frame after.

Only the last window's propagators are kept. Each is about 3.1 KB, and six
hundred take 1.8 MiB, so the store is bounded by one window and does not grow
with the run. A kept propagator is, bit for bit, the matrix that forming it
again would give, because it is looked up by everything it is formed from: the
settings and the interval. Which propagators are kept depends on the window
drawn last, but no drawn value can depend on that. So the store is not a second
record of the run, and `state_at` reads none of it.

**What `drawn_window` costs a frame, at the settings the dashboard draws with**
(measured 2026-10-04). The dashboard redraws every 200 ms
(`RENDER_INTERVAL_S` in `app/dashboard_frame.py`) and shows at most two runs
(`MAX_DISPLAYED_RUNS`). Each run is drawn by one
`SimulationController.drawn_window` call at
`max(150, plot width in pixels + 1)` columns (`chart_columns` in
`app/chart_frame.py`). Each cell gives one run's call without kept propagators,
then with them, as the median of 40 frames, with a 15-minute window following
a 30-minute run at 1x:
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

| Changes in view | 150 columns | 1 069 columns | 2 401 columns |
| --- | --- | --- | --- |
| None | 6.6 ms → 3.9 ms | 12.3 ms → 10.1 ms | 20.3 ms → 18.6 ms |
| Ten | 25.0 ms → 3.5 ms | 28.6 ms → 9.4 ms | 35.5 ms → 18.0 ms |
| Sixty | 135 ms → 3.7 ms | 119 ms → 9.1 ms | 129 ms → 18.8 ms |

Three costs are left. The two propagators for the window's bounds change every
frame, at about 1.4 ms each. The third is formed only on a frame whose left
edge has passed a grid column. Last, each column costs one chained product, at
about 7 µs. So the column count now sets the cost, not the number of changes
in view. At 1x, the third propagator is formed on about one frame in forty at
150 columns, one in four at 1 069 and one in two at 2 401. From 5x up, at
1 069 columns or more, nearly every frame forms it. Playing faster adds little.
In a later measurement, whose times ran about a quarter above the table's, one
run with sixty changes in view cost 13.0 ms at 20x against 12.0 ms at 1x at
1 069 columns, and 23.9 ms against 22.8 ms at 2 401. Two runs at 2 401 columns
therefore take about 40-50 ms of a 200 ms frame. Without kept propagators, two
runs with sixty changes in view at 1 069 columns take about 240 ms, which is
longer than the frame.
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

**This is the only record.** The chart is drawn from the definition, through
`SimulationController.drawn_window` and `RunDefinition.evaluate_anchored`, so
there is no second record that could disagree with it. The stepped system that
advances the run is still checked against the definition by the "Closed-form
agreement test".

**For developers.** Recording one sample per step costs 130.8 bytes per
sample, measured over 20 000 samples of a live run, so the 30-day case is
25 920 000 samples. The definition's size assumes a busy ICU day with 50
setting changes, which over the case gives 1 501 stretches. A one-hour window at 600
columns costs 10.6 ms to draw on a two-hour run and 13.0 ms on a thirty-day
run. Drawing from per-step samples cost 62.6 ms at four hours and 207.7 ms at
twelve.

#### The canonical evaluation rule

**One instant, one answer, whatever route the caller took.** A run's states
are calculated, and the same value can be reached by more than one sequence
of arithmetic. A fixed 0.1 s step allows only one sequence, because every
caller must take that step. A propagator that is exact over any interval lifts
that limit, and with it that protection. The rule below restores the
protection.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

- **Canonical.** The state at an instant is one propagation from the keyframe
  that opens the stretch containing the instant, over the interval between the
  two. Each keyframe is computed the same way: one propagation per stretch,
  composed in recording order from the start of the run. So two evaluations of
  one run definition at one instant perform the identical sequence of
  floating-point operations. Their results are **bit-identical**, not merely
  equal within a tolerance. `RunDefinition.state_at` in
  `core/run_definition.py` is this path.
- **Display.** To draw a window of evenly spaced columns, this path reuses one
  propagator across the columns inside a stretch, chaining from the first
  column. That reuse is what makes the cost of a frame depend on the window
  rather than on the run. The path solves the same equations exactly, but it
  composes the operations in a different order. `RunDefinition.evaluate` is
  this path. So is the chart's `RunDefinition.evaluate_anchored`, which also
  keeps the propagators it used for the next frame. A kept propagator is the
  matrix that forming it again would give. So keeping them changes no drawn
  value, and the canonical path reads none of them.

**What each may be used for.** Every value that is stored, exported, replayed,
compared against another run, or used as the state a branch opens from is taken
from the canonical path. A value from the display path may be drawn, and it may
be used for nothing else. It may not be a keyframe, an exported figure or a
branch's opening state.

**The program enforces this rule.** The display path returns its states
wrapped in `DisplayState`, which is not a state vector, so a display state
cannot be passed where a state vector is expected. `RunDefinition` also
rejects one as an opening state by name, with an error that says which path
the value came from instead of a length mismatch. The wrapper is not a
subclass of the state tuple, because some code that will take a state has not
been written yet. Code without a check of its own rejects only a value whose
shape is not a state's, and a subclass would pass it.

**How far apart the two paths are, measured.** The table gives the worst
absolute difference between the canonical and the display result at the same
instant. It covers the 600-column window that a chart draws, on a sevoflurane
run with four setting changes. It was measured on 2026-09-07 on the run in
`tests/reference/test_canonical_evaluation.py`. That test checks both
quantities against bounds an order of magnitude above the values printed here:

| Span | Six compartment fractions | Two cumulative accumulators |
| --- | --- | --- |
| 1800 s | 1.0e-14, of 0.0301 | 3.1e-12 L, of 2.06 L |
| 24 h | 8.0e-13, of 0.0300 | 3.1e-09 L, of 30.26 L |

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The wider span is the worse case, because its columns are further apart and
each chained propagation covers a longer interval. 24 h is the longest
supported run under § "Supported run length". So the second row is the worst
that a supported run reaches at this column count.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The headroom is wide against every amount on screen, and there is none
against the residual lines, which is why the rule is enforced rather than
trusted.** A fraction is displayed as a two-decimal percent, and the measured
difference between the two paths is about a hundred-millionth of that step.
The agent-accounting panel displays its three amounts to 0.1 L, and the
paths' running totals differ by less than a ten-millionth of that. But the
panel's two residual lines print the power of ten that a residual lies below,
and a residual is formed from those running totals. Their difference between
the paths is as large as an ordinary passing residual, at 30 minutes and over
24 h. So a display value that reached the mass-balance readout would change
the power of ten it prints, and the wrong one would look exactly like an
ordinary passing residual.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**What this requires of a branch.** `ROADMAP.md` item 12 asks that a branched
run reproduce its parent exactly, not merely within a tolerance. This rule
does so under one condition and one property of how a branch is built:

- **A branch opens at a keyframe.** Suppose a branch restarted from the
  canonical state at an instant for which the parent has no keyframe. It would
  then compute in two propagations what the parent computed in one, which
  rounds the same exact solution differently. Opening at a stretch boundary
  reproduces the parent bit for bit, and
  `tests/reference/test_canonical_evaluation.py` checks it. On the run there, a
  restart at 1 234.5 s changed 1 109 of the 1 269 state values in their last
  digits. Such differences depend on where the fork is and how far past it one
  looks, so they are examples, not a bound. The route the program actually
  takes is bounded, and that bound is zero.
- **The branch's run definition opens *at* the fork instant, on the case's own
  axis**, carrying the parent's keyframe. Parent and child then name the same
  case instant. Each forms its propagation interval as that instant minus the
  opening of the segment that holds it. Both start from the identical keyframe
  and use the identical subtraction. So the reproduction follows from how the
  branch is built, not from a caller having performed the right conversion.

Restarting at an instant with no keyframe, which the first condition rules out,
is a defect that a plausible branch implementation would introduce. The second
condition prevents another. If a branch's definition opened at a zero of its
own, every caller would reach a branch instant by *subtracting* the fork
instant from the case's time, instead of naming the branch's own elapsed time.
That subtraction can change the last digit of the result. So a branch would
compute over a slightly different interval from its parent, and give a result
that differs in its last digit. With one time frame, there is no offset for a
caller to name and no conversion to get right.

**A fork at a bookmark cannot satisfy both, and it is the second that gives
way.** At a control event both conditions can be met at one instant, because a
control event is a keyframe. A bookmark's instant usually is not. On a 120 s
run with two control changes, only 3 of the 1 201 instants where a halt could
land are keyframes. Meeting both conditions there would mean *recording* a
keyframe where the run halts. That makes the branch exact against its parent,
but it changes the parent's later results:
48 of 54 values differ from the same case built without the mark. Marking a
run would then change the run, which the project's determinism requirement
(`CLAUDE.md`) forbids.

So every fork keeps the first condition and relaxes the second to this:
**the branch's run definition opens at the keyframe at or before the fork
instant, on the case's own axis**. Meanwhile the branch's clock and its live
uptake system are at the fork. Exact reproduction is untouched, because it
never depended on the definition opening *at* the fork. It depends on parent
and child forming each propagation interval from the *same keyframe* by the
*same subtraction*, and opening where the parent's own stretch opens states
that directly. This was measured on 2026-09-14 on a 3 600 s sevoflurane run
with changes at 300 s and 600 s, forked at a bookmark at 655.3 s. Across nine
state values at six times out to an hour, 0 of 54 differ. The trunk stays
identical, byte for byte, to the same case built without the bookmark.

**A branch taken where a run is paused or stopped runs under the settings the
dials show there, and records the settings the run had on its way there as
where it came from.** The two can differ, because the learner can turn a dial
while the run is paused. Take a sevoflurane run at 2% that is paused at
10 min, after which the learner turns the vaporizer to 3%. The run reached
10 min under a stretch of settings at 2%, and that stretch cannot change. The
3% starts a new stretch at 10 min that has not run yet. Any change made during
the pause goes into that new stretch, so turning the dial again before the
next step replaces the 3%. A change during the pause never adds a second
stretch at the same instant, and it never reaches back into the 2% stretch.
Below, the *reaching stretch* is the stretch that ran up to the instant, the 2%
one here. The *stretch in force* is the stretch that runs from the instant on,
the 3% one here. Where nothing changed at the instant, the two are the same
stretch. The halt record lists the marks a run stopped on. The three ways of
branching, a branch's reset and the halt record all follow one rule:
<!-- not-restated: 2 % -->

- **Its provenance, the record of where it came from, is the reaching
  stretch.** `ResumePoint.segment` is the stretch that the step reaching the
  fork ran under (`RunDefinition.reaching_segment_at`). The branch's run
  definition opens at that stretch's keyframe. A fork at a control event is
  built the same way as a fork at a bookmark, so the construction above serves
  every fork. Except at the case's opening, which the paragraph after this list
  covers, nothing the parent later does at the fork can replace the stretch
  that the branch records as its provenance.
- **It runs under the stretch in force, which is what the dial says.**
  `resumed_at`, `resumed_here` and `resumed_at_mark` all run under the stretch
  in force at the fork (`RunDefinition.segment_at`). So "Branch here" opens
  with the dials as they stand when it is taken. A branch at an instant that
  the trunk has already passed runs under the settings the trunk had as it
  left that instant, including a change made at that instant and no change
  made later. On a run that a mark has halted, a branch taken before the
  learner changes a setting there runs under the old setting. A branch taken
  after that change runs under the new one, as do the branches taken from that
  instant's mark and keyframe entries in the "From" selector. A branch opens at
  what the dial says and does not go back to the previous setting.
- **The branch's timeline opens with the parent's changes at the fork.** The
  branch's run definition records, as a change at the fork, each setting it
  runs under that differs from its provenance. Its control timeline opens with
  a copy of each change the parent recorded at the fork
  (`RunRecord.opened_with`). After the case's opening, those copies are the
  settings that differ between the reaching stretch and the stretch in force,
  so the run definition and the control timeline agree. At the case's opening,
  the copies are the changes the parent made before Start, each shown from the
  value the parent's timeline starts at. Either way, the branch's timeline
  shows the settings it opened under, whatever the trunk later does at the fork
  instant. No later change merges into a copied entry or removes it, and a
  change the learner makes at the fork is recorded after the copies.
- **A reset branch keeps its settings and the entries it opened with.** It
  reopens at the fork on the same provenance. Its timeline opens with the
  entries from its first opening, followed by each setting that differs from
  the one the branch opened under. An opened entry records where the branch
  began, not something done to it since. So when the trunk's Reset asks before
  discarding the branch, an opened entry does not count as work the branch
  would lose (`RunRecord.opened_with`). Every later entry does count. That
  includes a setting that the learner changed and kept through a reset, and a
  dial that the learner set back to the trunk's value from before its change
  at the fork. The branch opened at what the dial said, so setting the dial
  back is the learner's own change.
- **The halt record names the marks as they are.** A run's halt record lists
  the marks crossed by the step it stopped on: the step that halted a trunk, or
  the step that reached a branch's fork. The record is worked out again against
  the current marks whenever it is read, as the mark outcomes are. So a mark
  removed and added back under another label is named by its new label.
- **A crossing is decided by the canonical readings, on the trunk as on every
  branch.** A running trunk also holds its live, stepped readings. The live
  and canonical readings can lie about a hundred-trillionth apart on opposite
  sides of a height. When the trunk halted on its live readings at the exact
  height, a branch opened on the halting step could show the same target as
  still running. Testing the canonical readings at the exact height fails
  differently. A steady compartment's canonical reading
  moves in its last digit from step to step, so a run that settled on a target
  crossed it again and again. A run with no ventilation and a target on the
  circuit at 1.00 ×MAC of a 1 MAC dial halted 965 times in ten minutes
  (2026-11-01). So a target's height is a band, one part in a hundred thousand
  of the height on either side (`bookmarks.HEIGHT_BAND`). A reading inside the
  band is at the height, and the crossing rule above applies to the band. The
  band is about five hundred times finer than a two-decimal readout near 1 MAC
  of sevoflurane.

  A canonical reading costs about 2 ms, where a whole step costs about 60 µs.
  So the live readings screen each step. Where neither of a step's live
  readings lies near an edge of a band, the canonical readings lie on the same
  sides of it, and a step the live readings find crossing nothing is passed. A
  step they find crossing a mark, or one with a live reading within one part in
  a million of the height of an edge (`bookmarks.LIVE_READING_GAP`), is tested
  again from the canonical readings. So the run halts only on a crossing that
  its halt record names. The widest measured gap between the two readings, over
  2 h at the 0.001 s step (2026-11-01), was 1.2 parts per billion. Scaled
  linearly to 24 h, it is 14 parts per billion, about a seventieth of the
  allowance. A marked instant needs no canonical
  reading, because whether a step crosses it depends only on the step's two
  instants.
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

At the case's opening no step has run yet, so the opening stretch is both the
reaching stretch and the stretch in force. A change the trunk makes at the
opening still replaces the opening stretch, even after a branch was taken
there. The branch's provenance then names settings the trunk no longer opens
under. That provenance is still true, because the opening keyframe is a state
that no setting produced, and the branch did run under those settings from
there. Its own timeline still states them, as its copy of the trunk's changes
made before Start.

**Returning to a marked instant the run has already passed is the same fork,
taken late.** Consider a learner paused at three hours who marks the one-hour
point and goes back to it. The run holds no keyframe at that instant and is
not standing on it, so neither of the two earlier ways of forking applies. The
construction above needs neither. The state at any instant the run has
reached is the run's definition evaluated there, and standing on a halt only
ever served to name the fork instant. So
`SimulationController.resumed_at_mark` takes the mark itself and forks at the
step that reached it, using the bookmark fork's construction. Here is what
that reproduces, and what it does not:

- **It reproduces the case's state at the mark, element for element.** The
  branch opens from the canonical state there, inside the parent's own stretch.
  Every later instant is one propagation from the same keyframe that the parent
  propagates from, until the branch's own settings change. Take the run in
  `tests/integration/test_controller.py` that is marked at 60 s after its clock
  reached 180 s. Its branch agrees with its trunk at all 601 instants from the
  mark to a minute past it.
- **It is the branch the halt would have given.** A mark set before the run
  passed it halts the run, and the run is forked at the halt. The same mark set
  after the clock went past it is forked here. The two branches' whole
  provenance is equal: stretch, fork state, step count and the step the fork
  ends. Taken at the same moment, both run under the same settings, including a
  change the trunk made while it stood on the halt. The branch also stays the
  halt's branch for a mark added later. Every run checks which marks were
  crossed by the step it opened on or stands on, against the marks as they are
  whenever its mark outcomes are read. So a mark added inside that step is
  treated the same on the trunk and on the branch, whether it was added before
  the branch or after. Every way of forking checks that step in the same way,
  including a fork at a control event. So `resumed_at` at a keyframe the trunk
  halted on opens on the halt's crossing, as `resumed_here` does.
- **It leaves the trunk the case it was.** Nothing is recorded where the mark
  is. That is what kept the bookmark fork from changing the run it marks.
- **It does not open at the typed instant.** The fork is the end of the step
  that reaches the mark, at the mark or one step past it. For a typed 45.3 s at
  the 0.1 s step the fork is at 45.300000000000004 s, and for a typed 45.35 s
  it is at 45.400000000000006 s. That is the instant a halt would have stopped
  on. The crossing rule itself finds it (`TimeBookmark.steps_to_reach`), not a
  rounding of the typed value. In the first hour, 12 767 of the 36 001 one-decimal
  instants are not a whole number of steps in binary. Rounding would put a mark
  that lies inside a step onto the step before it. The branch treats its mark
  as passed, not as "before this branch opened", even when the fork is one step
  past the mark. That is because the branch opens standing on the step that
  crossed the mark.
- **It does not replay what the trunk did afterwards.** The branch continues
  under the settings the trunk had as it left the mark's instant, until the
  learner changes something. Its own control record holds only a change the
  trunk made at that instant, if there was one. The trunk's later changes stay
  the trunk's. The reference simulator's rewind works differently. It returns
  to time zero, keeps the recorded settings and plays them back as it runs
  (Philip JH, *Workbook for Gas Man®*, Med Man Simulations, appendix E,
  "Replaying Simulations", printed pages 186-87). So it takes the trunk back and
  truncates it at the mark. Returning to a mark here forks instead, so the run
  that happened stays on the axis beside the alternative.
- **Its opening readouts are the canonical state's, not the ones the trunk
  showed when it stood there.** A running case displays its stepped live state,
  which is one propagation per step from the opening. Every branch opens from
  the canonical state. Over three hours of a run measured on 2026-10-12, the
  two agree to 4.9e-14 as a fraction, less than a billionth of the 0.01% that a
  two-decimal percent can show. No reader can see the difference. The same
  holds for a fork at a control event or at a halt.

<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

A mark still ahead of the clock is refused rather than reached. The case holds
no state there yet, and a fork there would be a prediction drawn as if it were
a run. The learner reaches such a mark by running on, and the halt there is
then the fork.

**Branching where a paused run stands is the same fork, with the clock naming
the instant.** The clock always stands on a whole number of steps, and the
construction above reproduces the case at any instant the run has reached. So
`SimulationController.resumed_here` forks wherever the trunk is paused, on a
halt or anywhere else. It forks from the canonical state there, inside the
parent's own stretch, and records nothing on the trunk. The branch opens
standing on the crossing made by the step that ends there. That crossing is
checked again against the marks as they are now, as `resumed_at_mark` checks
it, and is not read from a halt's record, which names only what was marked
when the run stopped. Three kinds of run are refused: a running run, because
where it stands moves with every step; a failed run, because a failure is not a
pause; and a run at the supported run length, because it has no step left for a
branch to take.

**So nothing is left over to bound, and there is nothing to show a learner.**
`ROADMAP.md`'s v0.5.0 definition of done asks this document for "the bound on
any divergence that could not be eliminated". On the canonical path, no such
divergence survives. A branch and its parent agree exactly at every instant
they share, for a fork on a keyframe and for a fork between two keyframes.
`tests/reference/test_canonical_evaluation.py` checks each case over 207
instants, against a restart at the fork, which does not agree.
`tests/integration/test_controller.py` checks the same over 201, 301 and 601
case instants, and over the 240 drawn columns that a trunk and a bookmark
branch share. Two divergences do exist. The display path's, tabulated above,
is refused in code as a source for anything but a drawn value. The restart's
is never taken by any branch this program builds. A bound of zero drawn on
screen would tell a learner there is something to watch where there is
nothing. § "What a branch comparison asserts, and what it does not" says what
a comparison of the two drawn runs may claim, and the zero bound is one of
those claims.

**Relaxing the second condition takes away a second job it was doing.** When a
definition opens at the fork, its `opened_at_s` is where the branch began, so a
chart could clip a branch's drawn range there. Once the definition opens at the
earlier keyframe, that clip would draw the branch back across time it never
lived through, showing the trunk's course under the branch's name. That is the
right numbers in the wrong patient context, a presentation failure that the
safety-critical standard names. So every fork carries the fork instant
explicitly, in `ResumePoint.fork`, and `SimulationController.began_at_s` reads
it: zero on a trunk, the fork instant on a branch. `drawn_window` clips its
lower bound there, with `first_s = max(start_s, self.began_at_s)` in
`app/controller.py`, and `app/bookmarks.py` is given it to decide that a mark
is unreachable. `began_at_s` exists so that no code infers the fork instant
from `run_segments[0].opening.instant_s`, which is where the *definition*
opens, the instant this relaxation moves.

**The relaxation also decides what `reset()` records.** Reset
keeps the settings and restores the state. Consider a branch that is reset
after its learner has dialled something new. It stands at the fork state under
settings its parent never used. Its definition still opens at the parent's
keyframe under the parent's settings. The new setting is recorded
as a *change at the fork*, in the run definition and in the branch's own
control timeline. The keyframe that this change opens is the
fork's own state. So the trace starts where the readouts say the branch is,
and the parent's stretch stays the parent's.

**Deciding that from the settings instead makes it depend on the order of two
reversible acts**, which is why it is recorded rather than written into the
opening. The sequences *dial, dial back, reset* and *dial, reset, dial back*
leave the same branch: the same settings, live state and displayed values.
Suppose the definition's opening were chosen at the moment of the reset. The
second sequence would then get the fork rather than the keyframe, compute in
two propagations where the parent took one, and silently stop reproducing the
parent. On 2026-09-20, 40 of 45 values differed across five probes. When the
dial is recorded as a change instead, the dial-back is collapsed by a rule the
run definition already has: a dial moved and moved back before a step ran
cancels out. The branch is then where it started. After a reset that *kept*
the new setting, the remaining difference is 0.000249 on the same probes. That
is a different management of the case, not rounding, and recording the dial as
a change keeps the two apart.

**What is not relaxed is the one frame.** The definition still opens at a case
instant on the case's own axis, and the clock still continues the parent's.
Nothing converts between frames, so relaxing the second condition does not
bring back the callers' subtraction that can change the last digit. The only
change is that the definition now opens earlier than the fork instant, on the
same axis.

**One simulated-time frame, and every reader is in it.** A branch's *simulated
time* is the case's time, measured from induction. It continues the parent's
rather than restarting at the fork. This one time is what the clock displays
and what stamps every recorded control change. It is also what rules the
chart's axis, what the supported run length is measured against, and what the
run definition's segments and keyframes are stamped in.
`SimulationController.resumed_at()`, `resumed_here()` and `resumed_at_mark()`
all open the branch's definition at the keyframe where the stretch the step
reaching the fork ran under opens, on the case's own axis. `advance()`
and `drawn_window()` pass case time straight through to the definition. Nothing
converts between frames anywhere, because there is only the one frame.

Continuing the case's time is a matter of correctness. Uptake and distribution
are a function of the time since induction. A branch that counted from zero
would therefore place the patient at the wrong point on the uptake curve, on
the clock, the control marks and the axis at once. That is the correct value
shown under the wrong patient context, which the project's safety-critical
standard (`CLAUDE.md`) counts as a failure in its own right. Continuing the
case's time also keeps simulated time to the single multiplication that
§ "Simulated time is a count of steps, not a running total" describes. A
branch's instants, in its run definition and on its clock, are the case's step
count times the step, not the fork instant plus a second total.

**What one frame is worth, measured 2026-09-14.** Two measurements were taken,
on a 120 s sevoflurane run and on the branches taken from it.

The first measurement is the reproduction. A branch was forked at the 60 s
keyframe and advanced 60 s further. It agrees with its parent at all 601 case
instants that the two share. Both are given the same number, the case's own
`steps × step`, and neither does any arithmetic on it. A definition opened at a
zero of its own, and asked for its own `steps × step` instead, differs from the
parent at **354 of those 601**. Both are exact solutions of the same
equations, but only the first is the same sequence of floating-point
operations, which is the sameness `ROADMAP.md` item 12 asks for. A definition
opened at its own zero could match too, but only if every caller subtracted
the fork instant itself, and nothing enforced that. With one frame, the second
result cannot arise.

The second measurement is what a reader sees. Drawn columns sit on absolute
multiples of the spacing (§ "What the chart draws"). So one frame puts a trunk
and a branch on the same column instants, without the display path being told
anything. The measurement used a 13-column 120 s axis, with the fork
deliberately off the grid at 55.3 s. On that axis, **all 8 of the branch's
columns** are instants that the trunk also draws. With the branch anchored to
its own zero, it drew 55.3, 65.3, 75.3 … and shared **2 of 8**. The two traces
then could not be read against each other at matched points.
`tests/integration/test_controller.py` and
`tests/reference/test_canonical_evaluation.py` test both measurements.

**A fork at a bookmark adds exactly one column to that, and it is the fork
itself** (measured 2026-09-20 on a 120 s axis at 150 columns). The fork above
lands on the trunk's own columns because a control event is drawn on every run
that has one. A bookmark's instant is not a control event, so the trunk draws
it only if it happens to fall on the grid. The branch always draws it, because
it is the left end of the branch's own clipped range. Everywhere else, the two
traces can still be read against each other. The value at that one point is
the case's own state there, which both runs contain. So the extra column marks
the instant at which the two stop being the same run, not a disagreement about
that instant.

**The drawn values at the columns they do share are equal to floating-point
composition rather than bit for bit, where a control-event fork's are exact.**
`evaluate_anchored` chains one propagator across consecutive grid columns. It
breaks the chain at a bound or at an event column, so a branch restarts from
its keyframe at its own left bound. For a control-event fork, that instant also
opens a segment on the trunk, and both walks break there. A bookmark fork's
instant does not open a segment on the trunk. So the trunk chains straight
through it while the branch restarts. The result is the same exact solution,
composed in a different order. This was measured on 2026-09-20 on the 3 600 s
case above, forked at the 655.3 s bookmark. Both runs were advanced 1 200 s,
and both were asked for a 601-column axis from zero to 1 800 s. **2 977 of
3 438 shared column elements differ, worst 7.70e-16 as a fraction and
8.17e-14 L on an accumulator**. The first is eleven orders of magnitude below
the 1e-4 to which § "Displayed precision" resolves a fraction. The second is
twelve orders below the 0.1 L to which the agent-accounting panel displays an
amount. A branch forked at the
600 s control event instead differs at none of the columns it shares.

The guarantee above still holds, because it rests on `state_at` and not on
`evaluate`. Asked for those same 382 instants canonically, the two runs agree
exactly, with 0 values differing. `tests/integration/test_controller.py` tests
that pair on the 45.3 s case above. Across the 240 columns that the two runs
share, 0 of 2 160 canonical values differ, while 1 909 of the same 2 160 drawn
values do, and the fork is the one extra column. This is the separation that
§ "The canonical evaluation rule" makes between the two paths. It matters to a
reader of a trace of the difference between two runs. That trace would show a
few units in the last digit here, where two identical runs show zero, and that
is not a disagreement about the case.

**For developers.** These are the measured figures behind the statements
above, in the order the statements appear.

- **Headroom.** A two-decimal percent resolves 1e-4 (§ "Displayed
  precision"). That section records passing residuals below 2.1e-11 L,
  measured on branches played for 30 minutes. The display path's
  accumulator difference at 1800 s is 3.1e-12 L. Over 24 h the worst
  relative residual measured was 3.08e-12, which on amounts of tens of
  litres is of the order of 1e-10 L. The accumulator difference at 24 h is
  3.1e-9 L.
- **A restart off a keyframe.** The restart was probed at the 141 instants
  at or past the fork (2026-09-21). The worst difference was 7.8e-15 as a
  fraction and 1.9e-12 L on an accumulator. An earlier restart on the same
  run differed by up to 5.3e-13 in an accumulator (2026-09-07).
- **The subtraction.** With a fork at 900 s, `(900.0 + 1e-6) - 900.0` is
  9.999999974752427e-07 and not 1e-6. So a child asked for its own `1e-6`
  would land one unit in the last place away.
- **The height band.** The live and canonical readings can lie about 1e-14
  apart.
- **Halting.** A canonical reading is one matrix exponential. The widest gap
  measured between the live and canonical readings was 1.2e-9 of the
  reading. Extrapolated in proportion to 24 h, it is 1.4e-8.
- **Dial order at a reset.** On the 2026-09-20 probes, the worst of the
  differing elements was 1.21e-15.
- **Drawn values of two identical runs.** The worst of the differing drawn
  elements was 2.7e-15.
- **A branch's opening readouts.** Their agreement with the trunk is about
  nine orders of magnitude below the 1e-4 that a two-decimal percent can
  show.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 900 s -->

### Supported input ranges

Each control is supported over a closed interval, endpoints included. A
setting outside the interval is refused rather than simulated:

| Control | Range | Declared and refused by |
| --- | --- | --- |
| Fresh gas flow | 0 to 10 L/min | `FreshGasFlow` in `core/supported_ranges.py`, the type that every fresh gas flow is built as |
| Delivered concentration | 0 to the agent's `max_delivered_concentration_percent` | `BreathingCircuit`, and `UptakeEquationSettings`, which carries the maximum beside the dial. Both refuse through `require_within_vaporizer_maximum` in `core/validation.py` |
| Alveolar ventilation | 0 to 12 L/min | `AlveolarVentilation` in `core/supported_ranges.py`, the type that every alveolar ventilation is built as |
| Cardiac output | 0 to 10 L/min | `CardiacOutput` in `core/supported_ranges.py`, the type that every cardiac output is built as |

<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

Fresh gas flow carries a **second** bound that is not in this table and is
not the model's. That bound is what the anesthesia machine in front of the
patient can actually deliver. The subsection below separates the two claims.

**The ranges belong to the model, so every way of running it refuses alike.**
`core/supported_ranges.py` declares the three flow ranges. A flow outside its range is
refused when the value is first made, before the simulation can store it. A script, a
notebook and a test meet the same refusal as the interface. The ventilation and cardiac
output sliders take their limits from that file. The fresh gas flow slider takes the range
the circuit accepts, which is this range narrowed to what the attached machine can deliver
(§ "The model's envelope and a machine's deliverable range are two claims", below). Each of
the three sliders moves in steps of 0.1 L/min. A run may open, as its patient profile
states, at a ventilation or cardiac output between two steps. Such a run is refused when
the dashboard sets up its controls, as a run that opens with a fresh gas flow between
steps is. Otherwise the slider would sit on a neighbouring step beside a rounded readout,
and both would show a flow that the run does not have. The shipped patient states 4.0 and
5.0 L/min, so nothing displayed changes.
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

**Refused, not clamped**, for the same reason as the vaporizer maximum. A
silently clamped setting would simulate, display and chart a value that the
user did not ask for. A `SimulationConfigurationError` is raised before
anything changes. So the run in progress stays trustworthy, and the interface
reports the refusal beside the control that caused it. § "Supported
simulation step" above draws the same distinction between a refused argument
and a step that broke down.

**Each flow is checked once, when its value is made, not where it is stored or used.** A
flow is kept from one step to the next, and it can enter the simulation five ways: through
an `AgentUptakeSystem` setter, through the setter or the constructor of the compartment
that holds it, through the `UptakeEquationSettings` record, or by assignment straight onto
the compartment's field. A `RunDefinition` is built from that record, and records each
change as a new record. So `core/supported_ranges.py` makes each flow its own `float`
subclass: `FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput`. Only the constructor
of each runs the range check. In the compartments, the settings record, the application's
snapshot and the setters that feed them, every field and argument that holds a flow
requires the type. A plain `float` passed to any of the five ways in is refused with a
`TypeError` that names the type to build, whatever its value. So no way in has to remember
the check. The control timeline stores plain `float` values, and a setting read back from
it is rebuilt as its type. Arithmetic on a flow returns a plain `float`, so a value
calculated from a flow is never taken as checked. `SimulationStep` treats the step the
same way.

**A settings record loaded from a saved file runs the same checks.** Python restores a
pickled or copied frozen dataclass through `__setstate__`, which by default writes each
saved value straight into its field without running `__post_init__`.
`UptakeEquationSettings` and `TissueGroupEquationSettings` instead rebuild the record from
the saved values. So a saved value that the constructor would refuse is refused on load,
at every pickle protocol, with the constructor's own exception. This catches a wrong saved
value. It does not protect against a pickle made to attack, because a pickle can call any
importable function. Nothing in `src/` loads a pickle yet. The other records that a saved
run holds, such as `RunDefinition` and `Keyframe`, do not yet check their values on load.

**A value assigned straight onto a flow field is refused at the assignment.** `mypy`
refuses `circuit.fresh_gas_flow_l_min = 1000.0` in `src/`, and the compartments' own
methods write the field only from a checked flow. A plain `float` can still arrive from
code that `mypy` does not check, such as a notebook, a test or a value typed `Any`. If it
were caught any later, the snapshot that the display reads would already have copied it,
and the readouts shown it. So `BreathingCircuit`, `AlveolarCompartment` and
`PatientCompartments` run the flow's `require_*` check in `__setattr__`. The write is
refused with the same `TypeError`, in the same words, and the field keeps its previous
value. The dataclass constructor, `dataclasses.replace`, a copy and a pickle all write
through `__setattr__`. A copy and a pickle do so because each compartment is a
`slots=True` dataclass, which they restore one field at a time through `__setattr__`. A
`__dict__` would be updated without calling it. So the constructors run no check of their
own. For a flow, the write checks the type. The fresh gas flow's write also checks the
flow against the machine's range, as described below.

**No compartment stores a blood flow, so none can disagree with the cardiac
output.** A tissue group's blood flow is its perfusion fraction times the patient's
cardiac output, $`Q_i = f_iQ`$, and `TissueGroup.blood_flow_l_min_at` is the one place
that multiplies them. The venous pool's flow is the cardiac output itself. Each
compartment's `time_constant_s` and `advance()` are given the flow, as $`Q_i`$ is given to
$`\tau_i = V_i\lambda_{i:b}/Q_i`$. A tissue group is given the blood:gas coefficient too,
for the same reason (§ "Blood compartments"). So every flow follows the cardiac
output through `set_cardiac_output`, a copy, `dataclasses.replace` and a pickle. A copy
made at another output leaves the original's flows unchanged. A new cardiac output written
onto the field of a built patient is refused, and the refusal names `set_cardiac_output`,
so that cardiac output has one way in. Writing the value the field already holds is
accepted.

**A tissue's perfusion fraction is fixed once the group is built.** The
patient checks that its three fractions sum to 1 only when it is built, so a
later change to one fraction would leave flows that no longer sum to the
cardiac output. `TissueGroup` refuses a second write of the field and says to
build a new patient with the new fractions. A tissue group written onto a
built patient is refused unless the fractions, with the replacement in place,
still sum to 1. Copies and pickles write the field once, onto a new object, so
they are accepted. Neither a tissue group nor the patient lets a field be
deleted, because a write after the deletion would bypass both checks.

`UptakeEquationSettings` still refuses tissue flows that do not sum to the cardiac
output. Now only a fraction forced past its check, with `object.__setattr__`, can reach
that refusal. At the next step, `advance()` raises it as a `SimulationNumericalError`, as
it does for every check that fails inside a step. Through `SimulationController`, the same
refusal comes before that step begins, as a `SimulationConfigurationError`. The
controller finds that the simulation's settings no longer match the run's definition, and
builds the settings record to report why before it takes the step. At Reset,
`SimulationController.reset()` refuses before it clears anything, and the interface halts
the run. A setting change that the record refuses is undone, so the compartment, the run's
definition and the timeline keep the previous setting. No setting change repairs such a
fraction. A new cardiac output scales every tissue flow by the same factor, so flows that
did not sum to the old output do not sum to the new one. Putting the fractions back, or
building a new patient, is the only repair.

**The alveolar and tissue agent amounts are checked against the compartment's capacity
when they are written, in the same `__setattr__`.** `set_partial_pressure_fraction` takes
a `Fraction`, so no setter can store an amount greater than the capacity. An assignment
onto the field could. The resulting partial pressure above one atmosphere would be
refused only two layers later, when `SimulationController.snapshot()` built the
`Fraction`. Whether an amount fits the volume that holds it is for the compartment to
check, not for either value alone (`.claude/rules/core-domain.md`). So
`AlveolarCompartment` and `TissueGroup` check it where the amount is stored. They check
the constructor, the setter and a direct assignment alike, in the constructor's own
words, and the field keeps its previous value. The one write that bypasses this check is a
rollback. `restore_state` puts back what the compartment held when the step began. A
rollback that could raise would replace the step's own error. It would also leave later
compartments still holding the failed step (§ "Step atomicity").
Only a write that bypasses the capacity's own check can shrink a capacity below a held
amount, because each value is checked first by its own write. The rollback leaves that
case to the snapshot, whose amount-over-capacity fraction refuses it visibly. No
supported setting makes such a write. The tests reach a refusing snapshot by replacing the
fraction that the snapshot reads.

**Every checked field of the five run records meets its constructor's checks when it is
written.** `BreathingCircuit`, `AlveolarCompartment`, `TissueGroup`,
`VenousBloodCompartment` and `AgentSimulationValidator` check every field in
`__setattr__`, including the constructor's own writes. So no constructor runs a check of
its own, and nothing is written when a value is refused. A relation between two fields is
checked by whichever is written second. These relations are the dial against the
vaporizer's maximum, the fresh gas flow against the machine's range, the machine's range
against the model's envelope, and each compartment's agent amount against its capacity. A
volume or partition coefficient is checked against the last of these. One too small for
the agent the compartment holds is refused, as `set_circuit_volume` refuses a circuit
volume too small for its agent (`require_room_for_the_agent_held`, `core/validation.py`).
The circuit stores its agent as a fraction of its volume. So a circuit volume assigned
directly, bypassing `set_circuit_volume`, cannot overfill the circuit, and is not refused.
Instead the agent amount changes with the volume, and the circuit gains or loses agent
that no flow carried. The next step then halts on the mismatch that the mass-balance check
finds (§ "Mass-balance identity"), and the step is rolled back. The venous pool's rollback
bypasses its check, for the same reason as the alveolar and tissue amounts. The circuit
and the validator roll back through their checks. Those checks cannot refuse a state that
`capture_state()` saved, because nothing those saved values are checked against can have
changed since.

**Built from an `int` or a `float` and nothing else, with no sign at zero.**
`core/checked_number.py` states what every checked type is built from. `FreshGasFlow`,
`AlveolarVentilation`, `CardiacOutput`, `Fraction`, `Percent` and `CaseInstant` all build
through it. They accept an `int` or a `float`, subclasses included, so a NumPy double
passes. A `bool`, a `Decimal` or a string is refused with a `TypeError` that names the
value and its type, before any comparison reads it. So is a value already built as another
checked quantity, such as a `StepCount` or a `CaseInstant` passed to a flow's
constructor, because that value is a swapped argument. Minus zero is stored as zero, so a
readout never shows `-0.0 L/min`. The range check is one chained comparison against both
ends, ends included. A NaN fails both halves, and an infinity fails one. An `int` too
large for a `float` is compared exactly and refused as outside the range, in the
setting's own words. `StepCount` refuses anything that is not an `int` the same way, with
a `TypeError`. The `require_positive_finite` and `require_nonnegative_finite` checks in
`core/validation.py` also refuse a `bool`, a `Decimal` or a string, for each amount, flow
and step they check. `SimulationStep` is built through the first of them. Those two checks
do not refuse a value built as another checked quantity, and they leave minus zero as it
is. They have no supported range to compare an `int` too large for a `float` against. So
they refuse it by name, as outside what a `float` can hold, before `isfinite` reads it.

**The dial's bound is enforced in both records that hold the dial and its maximum, through
one check.** The delivered concentration has the same five ways in as a flow. Its bound
is the maximum of the agent's vaporizer, not a constant of the model, so no type can
carry it. Only a record that holds both the dial and the maximum can check one against
the other. `BreathingCircuit` holds both. `UptakeEquationSettings` carries
`max_delivered_concentration_percent` beside the dial, as a required field with no
default. Each record's constructor refuses a dial above the maximum through
`require_within_vaporizer_maximum` in `core/validation.py`. So both records refuse in the
same words, and the rule is written once. Both accept zero, which is the vaporizer off,
and the maximum itself. `AgentUptakeSystem.equation_settings()` reads the maximum off the
circuit, so each stretch of a run records the limit its dial was set under. The
propagator cache key carries the maximum with the rest of the record, although the
matrix never reads the maximum.

**For developers.** Each flow is built as a type that only its guard produces.
`test_an_opening_ventilation_or_cardiac_output_off_the_slider_grid_is_refused`
in `tests/unit/test_dashboard_frame.py` checks that a run opening between two
slider steps is refused. The step's bounds are checked at the run, not at the
compartment, because a step is an argument to one call. A compartment advanced
alone has no truncation error at any step, so guarding it at
`MAXIMUM_SIMULATION_STEP_S` would refuse an exact calculation (§ "Supported
simulation step").
`test_the_fresh_gas_flow_control_narrows_to_a_declared_machine_range`,
`test_a_declared_range_off_the_display_grid_offers_only_settings_inside_it`
and `test_an_opening_fresh_gas_flow_off_the_slider_grid_is_refused`, in the
same file, check the three cases of the fresh gas flow control below.

No source chose the three flow maxima. They began as the interface
sliders' maxima, before the model declared any range. To change a range, edit its
constant in `core/supported_ranges.py`. The flow types, the checks and the ventilation and
cardiac output sliders all read it from there. The fresh gas flow slider follows through
the circuit's accepted range. `test_envelope_limits_match_the_supported_input_ranges` in
`tests/reference/test_coupled_dynamics.py` then fails on purpose. Re-run that file's
envelope and trajectory sweeps at the new limits. Update its limit constants, and
`EXACT_STEP_ORACLE_TOLERANCE`, the most that the exact step may differ from the
independent solution.
Then re-derive every figure measured at the flow maxima: the fastest time constant in
§ "Alveolar gas" and § "Supported simulation step", the corner sweeps in § "The numerical
envelope" and `tests/unit/test_numerical_envelope.py`, and the figures below.

#### What a setting outside the range costs

**The calculation is exact at any flow, so the limits are not numerical.** A setting
outside the ranges would give a numerically correct answer. Refusing it has another
reason. The ranges are the model's **verification domain**, the ranges over which it has
been checked. § "Independent-solution test" runs its test trajectories across them.
§ "Published wash-in and elimination validation test" compares the model with measured
human data across them. Every figure in this document is measured across them. Outside
them, neither the code nor the *model* has been checked against anything. A cardiac
output of 1000 L/min is not a patient, and these equations were never proposed to
describe one. Solving them exactly for that setting gives a precise answer to a question
that physiology does not ask. Nothing on the display would invite doubt. That is exactly
the case in which an obvious failure must be preferred to a plausible-looking number.

**The limits were chosen.** Nothing in the equations breaks at 10.01 L/min. The limits
mark only the settings that the interface offers and that the checks measure over.
Widening one is a legitimate change, and a safety-critical one. To widen one, first
extend the verification domain. Then re-run the trajectories of
§ "Independent-solution test" over it, and revise this section with the results.

#### The model's envelope and a machine's deliverable range are two claims

The two are different statements about different things:

| Claim | What it says | Declared in | Refused by |
| --- | --- | --- | --- |
| The model's envelope | The range over which the lumped compartment structure, the reference adult's fixed volumes and the constant-coefficient partition model are claimed to represent a patient | `MINIMUM_FRESH_GAS_FLOW_L_MIN` and `MAXIMUM_FRESH_GAS_FLOW_L_MIN` in `core/supported_ranges.py` | `FreshGasFlow`, which runs `require_supported_fresh_gas_flow` when it is built |
| A machine's deliverable range | What that machine's flowmeters, minimum-flow floor and fresh gas delivery can physically set | `deliverable_fresh_gas_flow_range` in that machine's `data/machines/*.json` profile | `BreathingCircuit._require_deliverable_flow` |

**The effective limit on the control is the intersection.** Each side refuses
in its own words, so a reader of a refusal can tell which claim the setting
violated. The model's refusal names the domain over which the model is
claimed. The machine's refusal names the device. It also says, in the same
sentence, that the envelope is *not* what refused the setting.
`test_machine_deliverable_flow_range_is_separate_from_model_envelope`
in `tests/unit/test_supported_ranges.py` checks both directions.

**Keeping the two ranges apart stops a machine from widening what was verified.** Suppose
a machine profile's flowmeter reaches 15 L/min, and its range were merged with the
model's into one pair of limits. That profile would extend the range that every reference
test was run over, without any change to `core/supported_ranges.py`. The result would be
an exact number, produced outside everything that was checked, and shown exactly like one
inside it. Merging fails the other way too. Take a machine with no true off position at
its common gas outlet, and a minimum flow of 0.5 L/min. With one pair of limits, that
machine either could not be represented or would move the model's lower limit for every
other machine. Kept apart, a machine profile can narrow what a run will accept, and can
never widen it.

**A machine whose range does not overlap the model's range at all is refused when the
circuit is built.** It is also refused when its range is reassigned on a built circuit.
So the mismatch is not found one refused setting at a time. Every flow such a machine can
deliver is outside the model's range, and every flow the model supports is outside the
machine's. Each refusal would be correct, but none would say that the pairing itself
cannot be simulated
(`test_a_machine_that_overlaps_the_envelope_nowhere_is_refused_when_built`
in `tests/unit/test_circuit.py`).

**The shipped profile declares no range, and nothing displayed changes.**
`data/machines/reference_circle_system.json` records `deliverable_fresh_gas_flow_range`
as `null`, because no operator's manual or manufacturer specification giving a deliverable
range could be reached for any machine surveyed. `docs/machine-survey.md` § "(b8) Flow
bounds, minimum oxygen flow, and the hypoxic guard" reports the range as unknown for all
eight. It names ISO 80601-2-13:2022 as the governing standard, and says that its text was
not reached, so it makes no claim about its requirements. `null`
means **no claim, not a machine known to be unlimited**. The table above is then the only
limit on the flow. The profile's `provenance_gap` records this reasoning, and
`test_the_shipped_machine_declares_no_deliverable_flow_range_and_says_why` in
`tests/unit/test_parameters.py` checks that the file keeps to it.

**Two machine minimums are not stored.** The field table in `docs/machine-abstraction.md`
also names `minimum_total_flow_l_min` and `minimum_oxygen_flow_l_min`, under the same
survey section. Neither is a field here, because that document's rule is that a field
exists only if something uses it. A minimum total fresh gas flow *is* the lower end of the
deliverable range. Storing one number under two names in a safety-critical data file is
the confusion this subsection removes. A minimum oxygen flow affects nothing this model
calculates, because the model carries one volatile agent in one gas phase and no oxygen.
It may be added when a hypoxic guard needs it, and that is a model extension, not a data
question.

**The fresh gas flow control offers only flows that both the model and the machine accept,
read from the circuit.** `BreathingCircuit.accepted_fresh_gas_flow_range_l_min` states
this range once. Where a machine profile declares no range, it is the model's range. Where
a profile declares one, it is the overlap of the two. The slider is limited to this range,
because a slider offering a flow the attached machine cannot set would invite a refusal
instead of preventing one. The slider moves in steps of 0.1 L/min, the flow's
displayed resolution. An end of the range that falls between two steps is offered as the
step just inside it. A machine with a minimum flow of 0.25 L/min is offered 0.3 L/min,
never the 0.2 L/min it would refuse. A range that contains no step is an error, instead of
a control whose only setting the run refuses. A machine profile
whose opening flow is not one of the offered steps is also refused, when the dashboard sets
up its controls. A slider position is read like a displayed value. A run that opens
between two steps would leave the slider on a neighbouring step beside a rounded readout,
and both would show a flow that the run does not have. Nothing displayed changes while the
shipped profile declares no range.

#### Supported run length

A run is supported up to **24 hours of elapsed simulated time**. The limit is declared as
`MAXIMUM_ELAPSED_SIMULATION_TIME_S` in `core/supported_ranges.py`.
`SimulationState.advance()` refuses the step that would carry a run past it, with a
`SimulationDomainLimitError`, before anything advances. A point past the limit can also be
handed in rather than reached. Then the value handed in is what is wrong, so it is refused
with a `SimulationConfigurationError` before any run holds it. That covers a step count
past the limit, refused where a `SimulationState` pairs the count with its step. It also
covers an instant past the limit, refused where the instant is built as a `CaseInstant`
(below). Such an instant is the opening at which a branch's `RunDefinition` is built, or a
point to which a run is moved. A run that stops at the limit stops on a step count at which
a run may also be built. Only the step from that count is refused. At the shipped 0.1 s
step, the last step lands exactly on 24 hours.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

| Quantity | Limit | Declared and refused by |
| --- | --- | --- |
| Elapsed simulated time | 0 to 24 h (86 400 s) | `core/supported_ranges.py`: `CaseInstant`, the type every instant is built as when a run opens, moves, keyframes, marks or branches at it, and `SimulationState`, which checks a `StepCount` against its step |

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The 24 hours belong to the case, not to each run.** The section below argues this limit
from what the model leaves out, which depends on how long the *patient* has been
anesthetized. So a branch shares the 24 hours its parent was using, counted from the point
where the branch was taken. A branch taken at 23 h has one hour left, not another
twenty-four. No separate check enforces this. Every check on the limit reads the case's
clock, a step count or a case instant, which a branch continues from its parent. So the
arithmetic that limits the original run also limits every branch of it.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Each instant and each step count is a type, checked once where it is built**, as
§ "Supported input ranges" describes for the flows. Every instant at which a run is opened,
moved, keyframed, marked or branched is a `CaseInstant`. A `CaseInstant` is a `float`
subclass, and only its constructor runs `require_supported_case_instant`. It is built only
from an `int` or a `float`, and it stores minus zero as zero, as the flows do. A `bool`, a
`Decimal` or a string is refused with a `TypeError` before any comparison. An `int` too
large for a `float` is refused as past the run length. The places that keep an instant, or
move a run to one, require the type and refuse anything else with a `TypeError`, whatever
its value. These places are a `RunDefinition`'s opening and every point it is advanced to,
each `Keyframe`, a `TimeBookmark` and the `BookmarkCrossing` that a run halts on, and the
instant at which `SimulationController.resumed_at` branches. A value built as another
checked quantity, such as a `StepCount` passed as an instant, is refused as a swapped
argument, both where the instant is kept and by `CaseInstant` itself, with no advice to
rebuild it. Code that only passes an instant on is annotated with the type and checks
nothing again, such as a snapshot, a chart frame and the instants at which a branch is
offered. So a time bookmark past the 24 hours cannot be made at all.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

A completed-step count is a `StepCount`, an `int` subclass. It is checked only for what a
count can be checked for alone: it must be whole and not negative, and a `bool` is refused.
How many steps fit in 24 hours depends on the step. So `SimulationState` checks the count
and the step together against `maximum_step_count`, through `require_supported_step_count`.
That check relates two fields, so the record makes it, at every write to either field, in
`__setattr__`. So a count or a step assigned straight onto a built state meets the
constructor's own refusals, in the constructor's words, and the field keeps its previous
value. `mypy` refuses such an assignment in `src/`. A plain `int` count or a plain `float`
step is refused with a `TypeError`. A count above zero with no step, or a pair past the run
length, is refused with a `SimulationConfigurationError`. A flow written onto its
compartment is treated the same way (§ "Supported input ranges"). The state's uptake system
is written once, when the state is built, because the count says how far that one system
has been advanced. A later write is refused with a `SimulationConfigurationError`.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

`SimulationState.elapsed_s` builds the count times the step as a `CaseInstant`. That
constructor never refuses the product, because the count was chosen on that same product.
An instant that a run is only *asked* about stays a plain `float`, such as the instant
passed to `RunDefinition.state_at` and the ends of a drawn window. The run's own opening
and end bound such an instant, and the run checks that relation. Arithmetic on either type
returns a plain `float` or `int`, so a calculated instant or count is never taken as
checked. The control record's instants, `ControlChange.elapsed_s` and an adjustment's
start and end, are `CaseInstant` too.

**It is the same kind of statement as the four ranges above, and it is
reached rather than set.** A flow is a setting. It is refused when a caller
offers a value outside its interval. A run length is a property of how far the
run has gone. So it is checked as each step is taken, and otherwise only where
a run is built already part-way along it. In every other way the run length is
like the flow ranges. The interval is closed, so a run may complete the step
that lands on 24 hours. Outside the interval the equations still solve
exactly, as "What a setting outside the range costs" says of the flows. What
stops at the boundary is the claim that the solution represents a patient.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**What bounds it is what this model omits.** The first omission is metabolism.
§ "Known limitations" records that this model has none. § "Published
wash-in and elimination validation test" already draws the consequence. That
test compares against five minutes of elimination. It explicitly refuses the
two Yasuda papers' own multi-day curves, because *over days the missing
metabolism is no longer negligible, and neither is the fat group's flow*. The
fat group's flow is the second omission. The two human sources that § "Known
limitations" weighs do not agree about which way the stored flow errs. A
resting depot measurement puts the stored figure at about twice the truth. The
same papers' washout fits put it at or a little below the truth. Either way,
the flow acts directly on the slow tail of washout. A run beyond this boundary
therefore displays a trace whose slow component is increasingly the two
omissions rather than the model.

**Inside the limit, the washout tail already lacks its largest measured term, and the
displayed number does not say so.** Every washout that the two Yasuda papers fitted needed
five compartments. Their authors took the fourth to be fat filled by diffusion from the
well-perfused tissue beside it. This model has no such route. The fourth compartment
carries the largest term in the measured curve over most of the supported span: from about
1.8 to 3.1 hours after a 30-minute administration until about 20.7 to 29.4 hours. The
intertissue-diffusion note under § "Known limitations" has the coefficients and the
arithmetic. All else equal, a tail without that store falls faster than the measured one
from about the third hour of elimination. Measured against the published mean curves over
the whole supported run, the shipped tail does so (§ "The first 24 hours of elimination
against the published mean curves"). It runs about a third below the curves from about the
seventh hour until about the twenty-first. For desflurane it runs below them by half, from
3.4 to 15.3 hours. In the hours before that, it runs a fifth to a half above them, while
the rebreathing circuit and the muscle group's slow return hold it up. At 23.5 hours of
elimination it runs above them again, by 12 to 24%, or by a factor of 2.1 for desflurane.
That is because this model's fat group returns more agent than the fitted fat term. In
that subsection's open-circuit run, which has no rebreathing, the tissue return alone is a
third to a half of the mean curve between hours 8 and 13.
<!-- not-restated: 2.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**That result does not move the 24 hours.** The limit rests on the two omissions above
growing past negligible over the span. The measured departures come from neither of them.
The metabolism bound in the same subsection accounts for about an eighth of the excess
where the tail runs above the curves, and widens the gap where it runs below. The shortfall
comes from the missing fourth compartment, which is as present in the first hour as in the
last. Shortening the span would not remove it. Extending the span would add the late
excess, which is still growing at 24 hours. The limit therefore certifies how closely the
late tail follows a measured washout inside the span only as far as that subsection
measured.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

Sevoflurane is the agent for which the missing metabolism matters most, so it
is the agent that limits this bound. For sevoflurane, 2% to 5% of the absorbed
dose is metabolized, against far less for isoflurane and desflurane.
Its metabolism also begins immediately rather than late. Fluoride and HFIP
appear in plasma within minutes of the start of administration. The same
review finds that metabolism "does not contribute to the termination of
clinical drug effect". That finding is what makes omitting metabolism safe
over a case. It is true while ventilation and perfusion dominate the trace. It
becomes progressively false once the only thing still moving is the slow tail,
to which this model gives no sink. That review's dose-proportionality covers
exposures of 0.35 to 9.5 MAC-hours. So past roughly ten MAC-hours, even the
size of the omission is unmeasured.
<!-- not-restated: 2 %, 5 % -->

- Kharasch ED. *Biotransformation of sevoflurane.* Anesth Analg
  1995;81(6 Suppl):S27-38. PMID 7486145,
  doi:10.1097/00000539-199512001-00005.

**That citation is tier 2, and nothing here is stored from it.** It is a
review. Under § "Source hierarchy", a tier-2 source is the authority for a
stored value only on a recorded decision. No such decision has been taken for
this one. There would also be nothing for it to authorize. The 24 hours is not
computed from 2% to 5%, and no parameter in this model descends from that
paper. What the review supplies is the magnitude and the timing of the
omission that this boundary is argued against. That is exactly what tier 2 is
legitimate for. A cap derived arithmetically from a metabolic rate would need
the primary measurements instead. It would be a different and better limit
than this one, but it is not what is claimed here.
<!-- not-restated: 2 %, 5 % -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Why 24 hours, and not a multiple of the slowest time constant.** At the shipped reference
settings, sevoflurane's fat group has a time constant of about 42 h. A limit set at several
multiples of it would favour exactly the long tail described above, the part of the trace
that is most nearly all omission. The fat time constant sets a minimum for the limit
instead, and that minimum is a fraction of one time constant. The run must last long
enough that the fat compartment is still visibly filling when it stops. 24 hours is about
0.6 of the time constant. By then a single compartment filling exponentially has gone a
little over two fifths of the way to equilibrium, so the fat trace still shows what it
exists to show. A run of a few hours would stop that trace near its start. The minimum
says nothing about how far above it a run may go. The span is also far longer than any
anesthetic this simulator is built to teach.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The 24 hours are not inside the measured exposure range, and do not claim to be.** The
review above measured how sevoflurane's metabolism scales with dose only from 0.35 to
9.5 MAC-hours. The limit bounds elapsed time, not exposure. A MAC-hour is usually counted
at the end-tidal concentration, which in this model is the alveolar fraction. A run whose
alveolar fraction is held near 1 MAC gains about one MAC-hour per hour. So it leaves the
measured range at about 9.5 hours, and reaches about 24 MAC-hours at the limit.
Every agent's dial opens at that agent's 1 MAC. The alveolar fraction stays below the dial
during uptake, so a run left at the dial gains somewhat less. Sevoflurane's vaporizer
delivers at most 8%, four times its 2% MAC. Counted at the dial, a run held there reaches
at most about 96 MAC-hours. So a long run at or above 1 MAC end-tidal leaves the measured
range well before 24 hours. After that, even the size of the omission is unmeasured. The
24 hours rest instead on the argument above, that the omission grows steadily once only
the slow tail is still moving, with no sudden break. They do not rest on the measured
range. Isoflurane and desflurane are metabolized far less than sevoflurane, so for them the
same span omits less.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- derived: 96 MAC-hours from data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

**Reaching it is not a failure, and the interface may not present it as one.** The step is
refused before it begins, so a run stopped here has stopped on a completed step, inside the
supported span, and every displayed value is a real solution of the model.
`SimulationDomainLimitError` is a separate error for this reason, and the interface
(`app/`) checks for it to choose its wording. The run stops, and the reader is told which
limit was reached and why it is set there. Reset starts a new run. Describing a correct
model as a broken one misleads a reader as surely as the reverse. It spends the
interface's one signal for a real fault, and it teaches a reader to discount that signal.
The interface must equally not present the stop as a pause. Start is refused, because a
resumed run's first step would be refused again.

**Whether a run is at the limit is decided from the run, never from the
refusal alone.** A run can come to rest on 24 hours by three routes, and only
one of them refuses a step. The first is a trunk stepping onto the last
supported count. The second is a branch forked on that count, either at a mark
that halted the trunk there or at a dial moved there. The third is a branch
reset onto such a fork. Recorded from the refusal alone, the other two routes
would look like an ordinary pause: Start offered, no limit notice, and a mark
that the run never reached reported as still ahead of a run that cannot step.
So the controller asks the core's own guard, `require_supported_run_length`,
whether the run's next step would be refused. It asks every time the run's
state is read and after every step. It reports the limit with the reason that
the refusal would give. A run stepping onto the count halts on the step that
arrives there, not on the refused step after it. So no run appears to be
running, or paused, while it is at a point where no step is left. The
interface may catch a `SimulationDomainLimitError` on some other path, such as
a setting. That error is recorded as the reason, and it takes precedence over
the derived one.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Volatile sedation in intensive care is out of scope, deliberately.** It runs
for days through an anesthetic-conserving device. That is exactly the regime
in which this model is wrong. Supporting it needs a model extension,
metabolism first, rather than a raise of this number. Raising the number
without that extension would produce the plausible-looking wrong values that
this document exists to prevent.

Widening this limit is a safety-critical change on the same terms as widening
a flow interval. Argue the longer span against what the model omits, extend
the validation that covers it, and revise this section with the result.

**For developers.** The step's check and the state's own check take the last
count from one function, `maximum_step_count`. It returns the largest count
whose simulated time, `elapsed_s`, is no later than 24 hours. `elapsed_s` is
the count times the step, rounded once. The count is decided on that product,
not on 24 hours divided by the step. At some computed steps, that quotient
rounds a whole step either way. It then gives a last step that lands a rounding
error past 24 hours, or one that stops a step short of 24 hours. Deciding on
the product means that a count is accepted exactly when the instant it stands
at is accepted. So a branch is built or refused alike, whether it is taken from
its parent's count or from its parent's instant.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

#### What is not bounded this way

The two gas volumes, of the breathing circuit and of the alveolar compartment, are **fixed
model parameters rather than controls**, and have no supported range. Each is set once,
when `AgentUptakeSystem.for_agent()` builds the system, and nothing changes it afterwards.
The interface has no control for either, and `SimulationController` has no setter for
either. Both have a numerical envelope, 0.01 to 10 000 L, which is a separate claim,
stated in § "The numerical envelope". It says only where the arithmetic has been checked
against a high-precision calculation. It says nothing about which volumes describe a
patient, so it does not contradict the physiological argument below.
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

The two volumes have different sources. The alveolar gas volume is a patient parameter of
2.5 L, read from `data/patients/reference_adult.json`. The provenance table above lists it
with the FRC measurement it is reconciled against. The circuit volume is a *machine*
parameter of 6.0 L, read from `data/machines/reference_circle_system.json`. That is a third
kind of parameter file, beside the agent and patient files, because the breathing system
belongs to neither. The same table lists the circuit volume with what is known of its
origin, which is that no source has been adopted for it.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

**Each parameter file is the only source of its own values, and `core/` keeps no copy of
them.** `AlveolarCompartment` has no default for its gas volume or its ventilation, and
`BreathingCircuit` has none for its volume or its vaporizer maximum. Every shipped run is
built by `AgentUptakeSystem.for_agent()`, which reads the values from the agent, patient
and machine files and passes them on. The fresh gas flow keeps a default,
`TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`, because a machine profile may state no startup
flow, and a run built from such a profile opens at that constant. Its authority is the
teaching-default reason recorded in the flow's provenance row, not a published source.
`test_the_flow_default_matches_the_shipped_machine_file` checks that the constant equals
the file's value. `test_for_agent_builds_the_circuit_at_the_machine_file_s_values` and
`test_for_agent_builds_the_alveoli_at_the_patient_file_s_values` check that a shipped run
gets the file's values. The serious failure would be a change that stopped `for_agent()`
reading a file. Every provenance row in this table would then silently describe a file
that the model no longer uses. So each of the four values is also checked with a file that
states a different value, and that run fails if `for_agent()` stops passing the value on.
For the machine file the tests are
`test_for_agent_builds_the_circuit_at_a_changed_machine_file_volume` (3.3 L) and
`test_a_profile_stating_its_startup_flow_opens_the_run_at_that_flow` (2.0 L/min). For the
patient file the test is `test_for_agent_builds_the_alveoli_at_changed_patient_file_values`
(3.0 L and 5.0 L/min).
<!-- not-restated: 5.0 L/min -->

**Why neither gets a supported range.** A supported range describes an
envelope that a run can be steered *within*. The four controls above each name
an interval because a user can put the model anywhere in it. The verification
gates are what establish that the model represents a patient across that
interval. Neither volume moves. The single shipped value is the whole of each
volume's domain, and every reference measurement in this document is made at
that value. An interval declared around it would assert verification across a
span that nothing has measured. That would be the same overstatement as
widening one of the four intervals without re-running the gates. Fixing the
value and saying so is the stronger claim, not the weaker one.

**What a wrong volume would be wrong for.** The argument is about physiology, as it is for
the four controls, not about numerical error. On 2026-09-06, with sevoflurane at the
shipped 0.1 s simulation step, a 0.005 L alveolar compartment and a 10 000 L circuit both
ran without incident. The agent balance held. So each gives an
arithmetically correct answer to a question that physiology does not ask. A 5 mL alveolus
is not a lung. This model's few compartments, its fixed tissue volumes and its constant
partition coefficients are claimed to represent a patient only near the shipped values.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- not-restated: 10000 L -->

**The 0.005 L alveolar compartment above, every volume below 0.01 L in the
paragraphs that follow, and every circuit volume above 10 000 L can no longer
be built.** Each is outside § "The numerical envelope". The measurements are
kept because they show what the propagator's own refusals do when a matrix
reaches them by another route. `tests/unit/test_matrix_exponential.py` still
drives those refusals, with a matrix built to match.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

**The numerics do eventually object, and that is a backstop rather than a
bound.** The same measurement was continued downward at the shipped 0.1 s step.
An alveolar volume of $`10^{-8}`$ to $`10^{-10}`$ L halts the run through
`AgentSimulationValidationError`. That error comes from the mass-balance
guard, not from any declared domain. From $`10^{-11}`$ L down, the propagator
is refused before any arithmetic. Down to $`10^{-308}`$ L it is refused
because it would need more squarings than `core/matrix_exponential.py`
performs (described below). Below that it is refused because scaling the
matrix down overflows, and then the matrix itself overflows. Both the halt and
the refusal are the required "obvious failure rather than a plausible-looking
number", but they arrive by accident of arithmetic. Neither is a limit that
this document declares, and neither may be treated as one. They sit far below
any volume a caller would pass by mistake, and they say nothing about the
physiological question above. Circuit volume has no such point. It was
advanced up to $`10^{300}`$ L with accounting passing throughout.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**A mass-balance check cannot catch a failure that wipes out every term it compares.**
When this was measured, before the refusals described below, an alveolar volume of
$`10^{-300}`$ L turned the propagator into the zero matrix. `propagate()` then returned all
zeros, and the mass-balance identity compared $`0 + 0 - 0 - 0`$, because every total had
been wiped out together. Zero does balance zero. No volume that can now be built reaches
this, and a test reaches it only with a matrix built for the purpose. Look for the same
weakness wherever a check compares quantities that one failure can affect together.

So `core/matrix_exponential.py` refuses a zero propagator. $`\exp(A\,\Delta t)`$ can be
inverted for every finite $`A`$, because its determinant is
$`e^{\operatorname{tr}(A)\Delta t}`$. So a zero result can only be a floating-point
artifact. The module also refuses the case where scaling the matrix's norm down to the
bound that the series needs overflows. That case would otherwise raise a bare
`OverflowError` at $`10^{-309}`$ L, outside the error types in `core/exceptions.py` that a
caller relies on. Both refusals arrive as `SimulationNumericalError` through
`AgentUptakeSystem.advance()`, and the step is rolled back. A matrix that carries the
constant state cannot produce the zero matrix at all, so the model now stops those volumes
earlier, at the limit on squarings described below. The scaling refusal still fires first
wherever the scaling overflows.

**Measured at every power of ten from $`10^{0}`$ to $`10^{-323}`$ L at the 0.1 s step**, the
propagator is returned at 11 of them, $`10^{0}`$ to $`10^{-10}`$ L, each with the constant
state's row exact. The other 313 are refused before any arithmetic. A single term too
small for any double, such as `exp(-0.5 * 3600)`, is still returned as 0.0, which is
correct. Such a single zero is what distinguishes a decayed entry from a wiped-out matrix.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**A limit on the squarings closes the last failure in this family.** At very small volumes
the propagator can stay finite and nonzero while the constant state's row drifts. No
interval may change that row, which is why its row in $`A`$ is empty. The shift that the
module applies to the matrix before summing its series lets error in, and the squarings
amplify it. After $`s`$ squarings, the worst entry's relative error is
$`c\cdot2^{s}\cdot2^{-52}`$. $`c`$ was between 0.6 and 2.7 at every power of ten measured on
2026-10-03, against a high-precision calculation of the same exponential, from those
needing no squarings to those needing 45. So every state whose own rate the shift swamps
drifts the same way. Two changes close the failure. First, the constant state's row is set
to the identity matrix's row before the squarings, which keep it exact to the last bit. So
`governing_equations.UNIT_STATE`'s guarantee that no step changes the constant state holds
in floating point as well as in the algebra. Second, a propagator that needs more than 32
squarings is refused before any arithmetic, because beyond that the error bound exceeds one
part in a million. The most any supported input needs is 19, at the 24-hour limit and the
widest supported flows. The first change alone is not enough, because with the constant
row exact a wrecked matrix is no longer zero, so only the limit refuses it.
`tests/unit/test_agent_simulation_validation.py` holds the regression test for a case that
the mass-balance check passed with every propagator entry wrong.

**What is left open, stated plainly.** Python code written against `core/` can still build
either volume anywhere in the numerical envelope, 0.01 to 10 000 L, by passing a
`CompartmentVolume`. So a 10 000 L circuit or a 0.01 L alveolar compartment is accepted.
`SimulationController` still takes a `circuit_volume_l` argument when it is built. Such
values are outside the verified domain, and only the numerical envelope limits them. They
cannot be changed during a run, and the interface cannot reach them at all. They are
chosen once, by someone who has gone to the trouble of building the model directly.
`BreathingCircuit.set_circuit_volume` remains for the same reason. It is how the value
reaches the circuit, and it holds the checks for agent conservation and capacity.
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->

**Zero is a supported input on all four, deliberately.** There are three
reasons, and the third is the one that decides it:

- The governing equations stay well posed. A zero flow removes a transfer
  term rather than dividing by one. At $`Q=0`$ the tissue and venous
  derivatives are zero, and the alveolar equation loses its uptake term.
  § "Required tests" above already specifies that behavior in the
  zero-ventilation, zero-cardiac-output, and zero-tissue-flow tests.
- Zero is the endpoint of a continuous axis. Setting a slider's lowest value
  just above zero would place an arbitrary boundary inside the model's own
  valid domain. A reader would have no way to tell that boundary from a
  modeling limit.
- The low end of each flow axis is where the teaching is, and zero is its
  limit. Reducing cardiac output *accelerates* alveolar wash-in, because less
  agent is carried away from the lungs per unit time. This is one of the
  central results in uptake and distribution, and this model reproduces it.
  With sevoflurane at 1 MAC and the reference adult's other defaults,
  $`F_A/F_I`$ at five minutes is 0.41 at 10 L/min, 0.49 at 5 L/min, 0.58 at
  2.5 L/min, 0.70 at 1 L/min, and 0.86 at zero. Refusing the last of those
  would cut the demonstration off one step before its clearest case. The same
  argument applies to alveolar ventilation at zero, which is apnoea.

<!-- not-restated: 10 L/min, 5 L/min -->

**What zero cardiac output does not claim.** It is a statement about agent
transport and nothing else. Uptake stops, so alveolar gas approaches the
inspired gas, and the tissue stores keep whatever they already had. It is not
a model of circulatory arrest, cardiopulmonary bypass, or ECMO. The section
"Known limitations" excludes all three. Nothing about the patient's condition
follows from a run at zero cardiac output. A run at $`Q=0`$ answers
"where does the agent go when perfusion stops", not
"what is happening to this patient".

**These ranges define the verification domain.** § "Independent-solution test" above runs
its test trajectories across everything these ranges allow. Its worst disagreement with
the independent solution comes on a trajectory that holds cardiac output at zero.
Narrowing a range would take that worst case out of reach, and widening one would admit
trajectories that were never measured. Either way, that test must be re-measured
(§ "What a setting outside the range costs" above). Three tests stop a range from changing
unnoticed. `test_envelope_limits_match_the_supported_input_ranges` restates all six flow
limits and fails if the model moves one.
`test_displayed_resolution_and_shipped_step_match_the_interface` does the same for the
displayed resolution and the step at which every figure is quoted.
`test_the_sliders_span_the_supported_input_ranges` fails if the interface stops short of
the declared ranges or goes past them. That test reads the shipped machine profile, which
declares no deliverable range. A profile that declares one narrows the fresh gas flow
slider to the overlap on purpose (§ "The model's envelope and a machine's deliverable range
are two claims").

**The simulation step is bounded too, and separately.** A user does not set it, but every
`advance()` call takes it. Its limits are `MINIMUM_SIMULATION_STEP_S` and
`MAXIMUM_SIMULATION_STEP_S`, not these ranges. § "Supported simulation step" above argues
for both. The step's maximum is a declared limit, in seconds, on how long a change to a
control may go unseen by the model.
These ranges are a claim about where the compartment structure represents a patient.
Neither is calculated from the other. Widening a range means re-running the reference
tests at the new extreme setting, without revisiting the step.

## Reset behavior

Reset must:

- pause the simulation;
- set simulation time to zero by clearing the step count from which that time
  was reached, and release the step that the run was using, so that a fresh
  run may use a different one;
- clear circuit, alveolar, blood, and tissue agent amounts;
- open a fresh run definition at the cleared state, so that no state of the
  discarded run can be derived or drawn;
- clear the recorded control-input timeline, which belongs to the run that
  recorded it;
- reset cumulative delivered and exhausted amounts;
- restore the mass-balance residual to zero;
- clear any recorded failure state, so that a session halted by a failed step
  can be started again from a clean state; and
- preserve the user’s selected settings.

**A branch's Reset returns it to its fork rather than to zero**, because a
branch never held the case's induction (§ "The canonical evaluation rule").
Its clock, its state and its accounting go back to the fork. Its settings are
preserved as a trunk's are. A trunk's fresh run definition opens under those
settings. A branch's opens on the parent's stretch it was taken from, so the
preserved settings are recorded in it as a change at the fork. The
control-input timeline is cleared. It then holds the entries that the branch
first opened with, followed by each preserved setting that differs from the
one the branch opened under. So a reset branch's timeline and its provenance
agree on the settings it runs under (`PL-K5BS`, `PL-ZR49`).

A Reset that the core refuses does none of these things. The fresh run
definition opens on a settings record, which is built from the compartments.
Building that record fails when the tissue flows no longer sum to the cardiac
output. Since `PL-HQF5` and `PL-Z0HN`, the only cause of that is a perfusion
fraction written in a way that bypasses its guard.
`SimulationController.reset()` builds that record before it does anything
listed above. A refused Reset therefore leaves the run exactly as it was,
rather than half cleared. The interface halts the run on the refusal through
the failed-step path (`PL-M4M0`). For other failures, the banner names Reset
as the way to recover. For this refusal it says instead that no setting can
repair it, because a new cardiac output scales every flow by one factor. It
also says that closing and reopening the application starts a new run
(`PL-01GY`). The next step refuses the same record. There,
`AgentUptakeSystem.advance()` reports the refusal as a failed step rather than
as a refused setting, because a run whose record cannot be built is not worth
continuing.

## Agent-change behavior

Changing the running agent must begin a new run. Switching between volatile
agents is not modeled (see § "Known limitations"). So there is no residual
washout to carry across. There is also no state from the old agent that the
new agent's partition coefficients would make meaningful. A change of agent
must therefore do everything Reset does. In addition, it must rebuild every
compartment against the new agent's parameters. It must also take the
delivered concentration from that agent's own 1 MAC, rather than carrying over
the old agent's percentage, because the same percentage is a different
clinical depth for each agent.

Because a change of agent begins a new run, it **destroys one**. Destroying a
run places a requirement on the interface, not only on the controller. The run
definition, the control-input timeline and the simulated time that a run
reached are everything a learner has to look back at. Nothing in this
application saves them, and there is no undo. So:

- the interface must not discard a run that holds anything (any elapsed
  simulated time, or any recorded control change) without first stating that
  the run will be discarded and obtaining the user's confirmation;
- the statement must name what is lost in the terms that the display already
  uses for it, so that the user can check it against the readouts it
  describes;
- declining must leave the run, its definition, its timeline and the control
  that offered the change exactly as they were; and
- a selection that resolves to the agent already running must change nothing,
  since it proposes no new case.

A run that holds nothing (no elapsed time and no recorded control change) is
exempt, because it has nothing to discard. A confirmation that fires when
nothing is at stake also teaches the user to answer it without reading it. By
the time something is at stake, that confirmation would go unread. Pressing
Reset is therefore also the way to make a later change of agent happen without
a confirmation.

**Reset's exemption covers the run whose button was pressed, and no other
run** (project owner, 2026-10-18, ratified, over extending it to every run the
press takes with it, `PL-W5WX`). Pressing a run's Reset is the request to
discard that run. The trunk's Reset also drops every branch drawn beside it,
because a branch cannot outlive the run it was taken from. But the reader did
not press Reset on the branch. So when a drawn branch has run past its fork, or
holds a control change made since it opened, the trunk's Reset states what
that branch holds and asks before it discards anything, as the list above
requires. A change that sets a dial back to the trunk's value before the fork
counts, because the branch opened at what the dial said. The
trunk's Reset also asks about a branch whose state cannot be read, because
what that branch holds is not known to be nothing. A branch that holds
neither is dropped without a question. Four tests in
`tests/integration/test_simulation_view.py` enforce this rule:
`test_resetting_the_trunk_asks_before_dropping_a_branch_that_holds_work`,
`test_resetting_the_trunk_asks_before_dropping_a_branch_set_back_to_the_earlier_flow`,
`test_declining_the_trunks_reset_leaves_every_run_as_it_was` and
`test_confirming_the_trunks_reset_starts_the_case_over_without_the_branch`.

**Every run holds while a question is open, and carries on as it was when
the question closes** (project owner, 2026-10-31, ratified, over letting the
runs go on stepping, `PL-TPBH`). The trunk's Reset question, the question
asked before a new agent starts a new case, and the Workspace strip's
questions are all window-modal. While one is open, the reader cannot press
Pause on any run. Before this rule, a reader who spent ten seconds on a
question at 300× came back to a case 50 simulated minutes further on. Now no
run takes a step while a question is open. When it closes, a running run runs
again at the same playback rate, and a paused run stays paused. The hold only
skips ticks of the step timer and changes nothing in the run. So a run's
trajectory is the same as if the reader had answered at once, as
§ "The reproducibility guarantee" requires. The bookmark editor is not modal,
so it holds nothing. `test_the_run_does_not_advance_while_a_reset_question_is_open`
enforces this rule for the trunk's Reset question, and two tests beside it
enforce it for the new-case and Workspace questions.

## What a branch comparison asserts, and what it does not

**Two curves, one difference, an obvious conclusion. The conclusion is the
part that this model does not supply.** The sections above establish that a
difference between two runs is *real*. Together,
§ "The reproducibility guarantee" and § "The canonical evaluation rule" rule
out rounding, evaluation order, playback rate and the machine as sources of
the difference. Neither
section says what the difference is *about*. A comparison is the most
persuasive thing that this simulator draws. It persuades whether or not its
limits reach the reader. That is why the limits are stated here, rather than
left for the reader to infer from the machinery that produced the comparison.

### What is compared, and what the two runs share

**Two managements of one case.** A comparison shows a **trunk** and one
**branch** of it. The two are the same run, continued in two ways from an
instant that the first run passed through. The structure is
described in `docs/ARCHITECTURE.md` § "What a branch is, and what it
shares with its parent".

**Two, and never N.** The display shows at most two runs. While two are shown,
a further fork is refused rather than replacing the one on screen
(`test_a_second_fork_is_refused_while_two_runs_are_shown`). No branch is ever
compared with another branch. Each branch is compared with the trunk it was
taken from. `ROADMAP.md` § "Explicitly out of scope for v0.5.0" declares both
limits. So a comparison asserts something about **two** control timelines over
one case. Nothing on screen has surveyed a range of managements or ranked one,
because only two were ever run. A reader must not generalise from a facility
capped at two runs as though it had no cap.

**What the two runs share. The code enforces each one by construction, not by
a reader's agreement to leave it alone:**

- **The patient.** Both runs use one reference adult
  (`src/anesthesia_sim/data/patients/reference_adult.json`). The patient is
  carried into the branch at the fork rather than chosen again
  (`test_a_branch_is_the_agent_and_patient_its_parent_was`,
  `test_a_case_s_branches_carry_the_trunk_s_agent_and_patient_at_the_fork`).
- **The agent.** The agent is carried into the branch the same way. It is then
  locked on both sides for as long as the comparison is shown. A branch's
  `set_agent` refuses outright
  (`test_a_branch_cannot_change_its_agent_out_from_under_the_case`). The
  trunk's selector is locked while two runs are shown
  (`test_the_trunks_selector_is_locked_while_two_runs_are_shown`). Changing
  agent begins a new run (§ "Agent-change behavior"). So an agent that could
  change under a comparison would end one of its two runs rather than vary it.
- **The equations, the parameter set and the model version.** § "The
  reproducibility guarantee" does not cover runs on a different model version
  or a different platform. A comparison stays within one model version and one
  platform by construction, because both runs are runs of the same program.
- **The circuit volume.** It is a build-time parameter with no live setter
  (`test_the_circuit_volume_is_a_build_time_parameter_with_no_live_setter`).
  It is applied to a branch before any state is.
- **The step.** A branch carries the trunk's own step through its
  `ResumePoint`. A fork at an instant that is not a whole number of steps is
  refused rather than approximated
  (`test_a_branch_steps_to_where_its_parent_stepped`). § "The reproducibility
  guarantee" does not cover two runs at different steps. Carrying the step is
  what keeps that exclusion from applying to a comparison.
- **Every control value up to the fork.** The branch's settings are replayed
  from the trunk's own recorded control timeline. They are then checked
  against the settings that the trunk's stretch of the run carries, rather
  than trusted
  (`test_a_branch_inherits_its_parent_s_settings_at_the_fork`).
- **The bookmarks.** Both runs are marked at the same questions
  (`test_a_branch_opens_carrying_the_marks_of_the_case_it_continues`).
- **The time frame.** Both runs are stamped in case time, measured from
  induction. The chart's columns are anchored to the case's zero rather than
  to either run's own opening. So the two traces are compared at matched
  instants
  (`test_a_branch_is_drawn_on_the_same_columns_as_the_run_it_forked_from`). A
  fork taken at a bookmark adds exactly one column, which is the fork itself
  (`test_a_bookmark_branch_draws_one_column_its_parent_does_not_and_it_is_the_fork`).

**What differs is the control timeline after the fork, and nothing else.** A
branch opens with a timeline of its own, which holds none of the trunk's
earlier changes. The only entries it opens with are copies of the trunk's
changes at the fork
(`test_a_branch_opens_with_only_the_change_it_runs_under_in_its_timeline`). A
reset branch keeps them, and can record the learner's settings after them, as
§ "Reset behavior" says. Each entry states a setting in force from the fork
on, so the sentence below is still true. Forking leaves the trunk untouched
(`test_forking_leaves_the_trunk_untouched`). So everything that either run
records after the fork is what its learner did to it. **A difference between
the two runs at an instant past the fork is therefore caused by the settings
that differ after the fork, on either side, and by nothing else in the
model.** That is what the mechanism provides, and it is worth stating
positively as well as negatively. Building the case twice instead would leave
the two runs differing by everything that was not reproduced identically. A
learner reading that comparison could not see which differences they had
caused.

### The shared history is identical by construction, not by measurement

**Construction, not reproduction.** A branch's run definition carries the
parent's own keyframe. It forms each propagation interval as the instant minus
the opening of the segment that holds the instant. Parent and child use the
identical keyframe and the identical subtraction, so they perform the same
sequence of floating-point operations at every instant they share. § "What
this requires of a branch" states the rule and its two conditions, and says
which of them a fork at a bookmark relaxes. The tests exist to catch that
construction breaking, not to establish the property.
`test_a_fork_opening_from_a_keyframe_reproduces_its_parent` and
`test_a_fork_opening_between_two_keyframes_reproduces_its_parent` test the two
fork shapes. `test_a_branch_reproduces_its_parent_at_every_instant_they_share`
and `test_a_bookmark_branch_and_its_parent_agree_at_every_column_they_share`
test them through the controller, at case instants and at drawn columns.
`test_a_fork_opening_at_the_instant_it_was_taken_does_not_reproduce_its_parent`
tests the restart that would *not* reproduce. No branch that this program
builds ever takes that route.

**So there is no residual to state: it is zero.** A branch and its parent
agree element for element, not within a tolerance, at every instant they
share. This is true at a fork on a keyframe and at a fork between two
keyframes (§ "What this requires of a branch"). Nothing is left over for a
reader to allow for, and for the same reason nothing is shown to them.

**What that does not guarantee is anything after the fork.** Identity before
the fork is a statement about arithmetic, and it sets no bound on anything
after the fork. How far the two runs diverge, in which direction, how quickly,
and whether they converge again are properties of the settings and of the
model. No property of the construction limits any of them. "Identical up to
the branch point" is a warrant that what comes after is not an artifact of the
fork, and it is a warrant for nothing else.

**And it is a statement about the canonical path, which is not the path the
chart draws.** Where the fork was taken at a control event, the drawn values
of the two runs agree exactly at every column they share. Where it was taken
at a bookmark, they agree only to within floating-point composition. The worst
difference is 2.7e-15 over the 240 shared columns that the test above checks.
§ "The canonical evaluation rule" tabulates this and places it orders of
magnitude below what § "Displayed precision" resolves, so no displayed digit
moves. A **difference** trace between the two drawn traces would *not* show
zero, and that is one reason this interface draws none. Such a trace would
show a few units in the last place where two identical runs should show zero.
A reader who saw it would take it for a disagreement about the case, not for
the composition order that it is.

### Neither run is a prediction for a patient

**This model has one patient, and no variability around it.** The parameters
are those of one reference adult. No equation here takes a covariate that
distinguishes one patient from another. No weight, age, sex or
body-composition term enters any of the equations, and nothing scales a
volume, a flow or a coefficient from such a term (§ "Known limitations"). Two
branches are two trajectories of *one* modelled patient under two managements.
They are not two patients, not two samples from a population, and not a range.

**So a difference between the branches is a property of the model rather than
an expected clinical difference.** It carries no interval, no spread and no
distribution, because the model contains nothing that could supply one. It
does not say how much two patients managed those two ways would differ from
each other. It does not say how far a real patient would depart from either
curve. Nor does it say how likely either management is to reach a given state
by a given time. It says what these equations do under these two control
timelines. That statement applies inside the envelope that § "Supported input
ranges" and § "Supported run length" declare, and to the fidelity that
§ "Published wash-in and elimination validation test" establishes.

**A branch that differs in cardiac output is still not a second patient.**
This is the case most likely to be misread. Cardiac output is a live control,
and it is also the quantity by which a clinician most readily tells one
patient from another. Dialling it changes this patient's circulation. Its
effect on uptake is a real property of these equations, and a legitimate thing
to put on either side of a fork. What it does not do is describe a
*different* patient. A patient who differs in cardiac output differs in
compartment volumes too, and this model keeps those volumes fixed. So moving
one half of the coupled pair shifts every tissue time constant
$`V_i \lambda_{i:b} / Q_i`$ in a direction the intact pair need not take.
§ "Known limitations" measures that artifact where it arises from weight
scaling, and the same arithmetic governs it here.

**The reading to refuse, stated concretely: "low flow woke this patient twelve
minutes sooner."** Three separate things are wrong with it, and only the first
is about variability.

- **"this patient"**: there is one modelled patient and no population around
  it, so nothing on screen is about a patient at all.
- **"woke"**: this model has no effect-site compartment and defines
  $`F_a \equiv F_A`$ (§ "Model boundary"). So it has no measure of
  responsiveness in which two runs could differ. The nearest thing the chart
  shows is the vessel-rich trace read against the MAC-awake band. That band is
  one standard deviation either side of a published population mean, and it
  is explicitly not a prediction for the patient on the screen (§ "MAC-awake
  as a chart reference"). The interface displays no time-to-wake-up figure of
  any kind, by decision rather than by omission.
- **"twelve minutes"**: a duration read between two curves inherits every
  limitation of the model that drew them. § "Known limitations" is long
  enough that a minutes-precise emergence difference is not among the things
  this model is claimed to get right.

**What a comparison is for is the mechanism**: which way a curve moves when
one thing changes, why it moves that way, and roughly how fast, in a model
whose structure makes the reason legible. That is the educational claim these
two runs support, and it is the only one.

### What the interface may assert about a comparison

The interface may mark where the branch was taken
(`BRANCH_POINT_LEGEND_LABEL` in `src/anesthesia_sim/app/dashboard_frame.py`).
It may name the run that each displayed value and each record of an input
belongs to (§ "Reasonably foreseeable misuse, and the hazards the presentation
carries", the row on reading one run's value as the other's). And it may carry
the two standing statements beside the readouts:
`INTERPRETATION_DISCLAIMER_TEXT` and `USE_DISCLAIMER_TEXT`.

**It must not draw the conclusion for the reader.** That rules out a
difference trace between two runs, a score or ranking of one management
against the other, a time-to-wake-up figure, and a sentence stating what the
comparison shows. Each of these is the conclusion that this section says the
model does not support. A qualifier beside it does not repair that, because
the number would be acted on and the qualifier would not. § "MAC-awake as a
chart reference" already makes this argument about a wake-up readout. Audited
2026-09-21 against `src/anesthesia_sim/app/dashboard_frame.py`,
`src/anesthesia_sim/app/chart_frame.py` and
`src/anesthesia_sim/app/qt_chart.py`: the interface draws none of them.

**Where the line falls, since two shipped surfaces sit close to it and neither
crosses.** First, a bookmark halts a run on the step that crosses a marked
instant or height. The clock then shows where that run actually stopped
(§ "Halting on a marked crossing"). Two runs halted at one marked height
therefore show two instants. Each is an instant that its run *reached*, not a
figure predicted for an endpoint that the run has not reached. Second, each
run's control-change record states that run's own inputs. It is the record of
what its learner did, not a statement about the difference between the two
runs. That is why the record is headed for the run it belongs to rather than
for the comparison.

## Interface boundary

The interface may:

- display values;
- convert fractions to percent;
- collect user settings;
- issue Start, Pause, and Reset commands;
- choose how many simulation steps each tick of its own loop takes, so that a
  run can be played faster than real time, subject to the constraint below;
- halt a run and record why when the core raises, and report a value the
  core refused;
- render the run's states across a window of its axis, evaluated from its
  definition;
- choose how wide a window of the run the chart draws, and how that window is
  ruled, subject to the constraint below;
- choose the instants a plotted trace is evaluated at, subject to the
  constraint below;
- draw a subset of the compartment traces, at the reader's request, subject
  to the constraint below;
- draw a published clinical constant as a chart reference, at a height the
  chart's own axis gives meaning to, subject to the constraint below;
- form the ratio of two modelled fractions where this document names it as a
  displayed quantity, subject to the constraint below;
- declare where one user adjustment of a control begins, so that the run's
  record of its own inputs can be read as the acts that produced it,
  subject to the constraint below; and
- display mass-balance status.

**What a drawn window is.** A chart draws from a `DrawnWindow`
(`app/run_series.py`). It contains the states at the instants that one frame
plots. `SimulationController.drawn_window` evaluates them from the run's
definition, and nothing is stored behind them. Each state is bound to the
substance that the run is of. It carries that substance's six compartment
values, as fractions of one atmosphere, under the stable identifiers that
`RecordedQuantity` names. A trace addresses one of them as a `RecordedSeries`,
which is a substance-and-quantity pair. Today a run is of one substance, the
agent it is a run of. Changing agent starts a new run rather than adding to
this one, so a window describes one substance.

A window is keyed by substance rather than by six named fields, because a
compartment fraction asserts nothing without the substance it is a fraction
of. Six flat names can describe exactly one substance. A second substance
would then have to arrive either as six more names or as values pooled with
the first substance's values. Pooled values are the correct-number-wrong-label
failure that this document forbids elsewhere. The chart is addressed the same
way: one trace is bound to one substance-and-quantity pair. So a trace can
draw only what it names. A frame that asks for a substance the run is not of
fails, rather than drawing whichever substance the run does contain. The
wash-in quotient below is formed from one substance's own two fractions, for
the same reason.

**What a snapshot is, and why it is not keyed the same way.** A frame is
rendered from an instantaneous state, `app/controller.py`'s
`SimulationSnapshot`. The snapshot carries the six compartment values as flat
named fields rather than as the per-substance mapping above. That asymmetry
is a decision, not unfinished work (`PL-TCD1`, 2026-09-13). A snapshot is one
instant's transient state for the running agent. Unlike the run definition, it
is never stored, never compared against a later run, and never read back. So
giving it a second substance later adds a field rather than invalidating
anything already written. That is the test that `ROADMAP.md` § "Designed for
forking" applies: "whether retrofitting invalidates recorded runs or merely
adds a field". That section places per-compartment agent amounts in the
snapshot on the declined side of the test. `ROADMAP.md` Phase 1 generalizes
the patient to N simultaneously present substances, and the mapping arrives
with it.

What the asymmetry may not do is let one frame describe the run in two
vocabularies. The six fields travel with the `agent_id` and
`agent_display_name` they belong to. This is for the same reason that
`agent_mac_percent` travels beside the concentrations it scales. The
interface also names the substance on the readout row itself, rather than
leaving a reader to carry it over from the agent selector. So a compartment
number and the trace beside it name the same substance on the face of the
display.

**What the chart draws.** A plotted trace need not draw the run at every
instant the run passed through. A run advances by one step every 0.1 s, well
beyond what a chart can resolve. But every point that the trace does draw must
be a state the run actually reached, at the instant it is drawn at. The
interface must not interpolate, smooth, average, or otherwise synthesize a
plotted value. The instant that the numeric readouts were formatted from must
always be drawn, so that the end of a trace and the readouts beside it cannot
disagree.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

The chart meets this by **evaluating the run's definition rather than reading
samples back from a store**. `core/run_definition.py` returns the state at any
instant in closed form. So the columns that a frame draws are chosen for the
axis being drawn and computed for it. No recorded series lies behind the trace
that could disagree with it. Two rules decide where the columns fall. Both are
properties that this document requires, not optimisations:

- **The columns sit on a grid anchored to the case's zero**, at absolute
  multiples of the spacing that the selected time base and the plot width
  imply. There is one column per pixel boundary of the widest plot the frame
  is drawn on, and never fewer than 150 (`chart_columns` in
  `app/chart_frame.py`, `PL-GS3R`). The spacing is the span divided by those
  columns, rounded down onto whole hundredths of a second, and onto tenths
  wherever that adds at most a tenth more columns (`grid_spacing_s` in
  `app/chart_time_base.py`, `PL-T5NJ`). Every drawn instant is then a whole
  number of hundredths, so the chart's hover can print exactly the instant
  whose state it prints. Rounding down keeps each chord within a pixel of
  time. The one exception is a spacing below a hundredth of a second, which
  needs a one-minute axis more than 6000 px wide. A plot can become wider than
  the width its frame was sampled for, by a window resize or by a reader
  dragging an Area border. The plot is then redrawn on the next render tick, whether the run is
  running or paused (`resample_owed`, `PL-9LNF`). A window that follows the
  run therefore keeps every column it had and gains at most one, so a steady
  trace is not redrawn on every frame. A grid anchored to the viewport would
  instead move on every scroll and resize, and rewrite the whole chart on
  every frame. The anchor is the case's zero rather than each run's own
  opening. That choice puts a branch's columns on the same instants as the
  trunk's, so the two can be read against each other at matched points. A
  per-run anchor put a branch forked at 55.3 s on 55.3, 65.3, 75.3 … while
  the trunk drew 0, 10, 20 ….
- **Every control event inside the window is a column of its own.** Between
  events the trajectory is a sum of exponentials with bounded curvature and
  no hidden transients. So every sharp feature in a run is at an event
  boundary. A grid that stepped over one would draw a straight line through
  the single instant that a reader is looking for. Each such column is read
  from the keyframe that the run definition already stores at that instant,
  so it is exact rather than propagated.

**So the drawn chart reproduces every control change**, to the last digit
the readouts display, while the stored record need not. There is no stored
record (project owner, 2026-09-05, recorded here when the sample store was
deleted). At the instant the dial moves, the interpolation error scales as
O(h) rather than O(h²). That is the signature of a kink, since the derivative
of the circuit fraction is discontinuous at a control change. Placing a
column on each event is the whole of the answer to it.

**Between events the guarantee is a pixel of time, not a number of percentage
points** (`PL-GS3R`, decided 2026-09-14). Take two drawn instants no more than
a pixel apart, both exact. A monotone run and the straight segment the plot
rules between them cross every level inside the same pixel. So the drawn line
is within one pixel of time of the run everywhere, and on the run at every
drawn instant. The numeric departure between drawn instants is deliberately
not the guarantee. Where the trace is steep, one pixel of time is many
percentage points of value. No display shows a value between drawn instants:
the hover returns a value only at a point the plot draws (§ "The chart's
hover readout"). The pixel is a logical pixel of the plot, which is the
resolution at which the axis is ruled and labelled.

That guarantee was the response to a measurement. From `PL-2FM6` until
`PL-GS3R`, the rule was a fixed budget of 150 columns at every width. Across
the twelve-hour base, that rule ruled a 290 s chord, and it drew the steep
early wash-in below the run. For sevoflurane 2% to 4% at the fastest supported
settings (FGF 10 L/min, V_A 12 L/min, Q 10 L/min), the line fell below the run
by 0.53 pp on the alveolar trace (0.26 MAC) and 0.89 pp on the circuit trace.
For a desflurane overpressure induction, 0% to 12% then 6% at 600 s, it fell
below by 3.8 pp on the alveolar trace (0.64 MAC) and 5.5 pp on the circuit.
A numeric bound could be held instead: 0.01 pp, the readout's resolution,
everywhere on every trace. On that desflurane case it would need a 2 s chord,
which is 21 601 columns across twelve hours. No hardware this project has
measured can draw that many inside its frame budget. And the whole of that
error lies within 1 800 s of a dial change. Beyond that, the 290 s chord
itself is within 0.0024 pp. These values were measured on 2026-09-14 against
the closed-form state every 0.1 s, the step the run advances by, over five
twelve-hour runs built in closed form.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- not-restated: 2 %, 6 % -->

The table below gives what the one-pixel rule leaves between drawn instants,
measured on a 1 000 px plot. The chord is the rung's span divided by 1 000:

| Time base | Chord | Sevoflurane 2% to 4%, worst trace | Desflurane 0% to 12% to 6%, worst trace | Desflurane, alveolar |
| --- | ---: | ---: | ---: | ---: |
| 15 min | 0.9 s | 0.0004 pp | 0.0025 pp | 0.0025 pp |
| 1 h | 3.6 s | 0.0052 pp | 0.032 pp | 0.032 pp |
| 4 h | 14.4 s | 0.048 pp (circuit) | 0.28 pp (circuit) | 0.21 pp |
| 12 h | 43.2 s | 0.21 pp (circuit) | 1.21 pp (circuit) | 0.26 pp |

<!-- provenance: app/chart_time_base.py SELECTABLE_TIME_BASE_FLOOR_S = 900 -->

<!-- not-restated: 2 %, 6 % -->

Those are the mid-chord departures of a straight segment from a curve that
passes through both of its ends. Each is a vertical gap at an instant that no
display shows, and, by the argument above, less than one pixel horizontally.
The departures grow with the chord, so a narrower plot draws a larger one and
a wider plot a smaller one. They are the bound a reader should have in mind
for a trace's *shape* inside a single pixel column, never for a value.

**The one case the pixel argument does not cover is an extremum between two
dial changes.** The alveoli and the venous blood keep filling for a moment
after the vaporizer is turned down. So a trace can turn inside one interval
and rise above both drawn values, where the line falls short of it. This was
measured over five runs. Two were the sevoflurane cases at the fastest
settings, 2% to 4% and 4% to 0%. Two were the desflurane case, at the fastest
settings and at slow settings (FGF 0.5 L/min, V_A 2 L/min, Q 2 L/min). The
fifth was the reference adult at 1 to 2 MAC. The worst such gap at any rung
is 0.0028 pp, on the mixed venous trace at the desflurane dial-down on the
twelve-hour base. That is less than a third of the readout's resolution.
`tests/unit/test_run_definition.py` checks that the gap in that case stays
below half of it.
<!-- not-restated: 2 % -->

Pegging that residual to the displayed resolution is deliberate. It does not
cross the line drawn under § "Supported simulation step". That section
forbids traffic in the other direction: the readout's decimal count must not
feed back into the model. That is why the step tolerance and the supported
ranges are stated in absolute percentage points. The statement here is about
the *chart*, expressed in the units a reader actually reads it in. Nor is the
peg arbitrary. The two-decimal readout is itself derived from model fidelity
under § "Displayed precision": one published SD of a partition coefficient
displaces a compartment by 8.7e-4 to 6.8e-2 percentage points.

The pixel-column framing is the one Jugel, Jerzak, Hackenbroich and Markl
prove from the other side, for recorded data. They prove that a line chart is
fixed by at most four values per pixel column (M4: A Visualization-Oriented
Time Series Data Aggregation, *Proceedings of the VLDB Endowment*
2014;7(10):797-808). Their selection method itself is not used. Nothing is
selected from a store. The run is evaluated at the column instants, and a
control event is always a column, whatever the pixel width. A selection of
recorded extremes could not guarantee that (`PL-4RBD`). The Flet chart could
not afford one column per pixel (`PL-YSZN`). It kept a fixed 150-column budget
through its own series module until `PL-25KS` ported the dashboard, and that
module was removed along with the Flet chart.

The drawn columns are display-path values, taken under § "The canonical
evaluation rule" below. They may be drawn and used for nothing else. The
program enforces that rule rather than only describing it.

**Which compartment traces are drawn is the reader's to choose, and the
choice may not change anything else.** A reader cannot compare two
compartments while four other lines cross them, so the interface may draw a
subset of the six. Three conditions bound this choice. First, the selection
is presentation only. It affects no model state and changes nothing in the
run definition, and identical inputs still produce identical results. Second,
every compartment's concentration stays in the numeric readouts whatever is
drawn. A chart showing two curves is therefore a chosen view of six modelled
compartments, not a model with two. Third, the display must state, for every
compartment, whether its trace is currently drawn. A legend entry for a line
that is not on the plot makes a claim about the run that the run does not
support. That is the same defect as an unlabelled reference, arriving from
the other direction.

A **reference** is not a trace, and it is deliberately exempt from the rule
above. It draws no state of the run, because it is a published constant
rather than a modeled quantity. A labelling requirement bounds the exemption
instead. A reference must state the value and the divisor it was drawn from.
It must name the compartment that it is to be read against. It must also be
visually distinguishable in kind from a compartment trace, by mark type
rather than by colour alone. A reader who has no reason to think otherwise
takes an unlabelled horizontal line for a modeled quantity. That is the
confusion between modeled and measured values that this document forbids
elsewhere, arriving through the chart.
See § "MAC-awake as a chart reference".

A **displayed ratio** of two modelled fractions is a trace, and it is *not*
exempt from the rule above. Every point it draws is still computed from one
evaluated state of the run, at the instant at which it is drawn. Nothing
about it may be interpolated, smoothed or averaged. A ratio also needs a
**stated domain**. A quotient of two modelled states can be undefined (a zero
denominator) or outside what the plot claims to show. In neither case does
the interface have a number that it may substitute. So five rules apply. The
domain is documented here and enforced in one place in code. A drawn instant
outside the domain contributes no point, rather than a clamped, extrapolated
or defaulted one. The trace breaks where the domain does, rather than joining
across the instants it skipped, because a join would draw values the run
never produced. The display states which two quantities the ratio is of, in
the terms this document uses for them. Where the trace is absent, the display
says which boundary it stopped at, because otherwise an absent trace looks
like a run that stopped. See § "F_A/F_I as a displayed ratio", the only such
quantity today.

A **control mark** is a third kind of chart series. It is exempt from the
trace rule for yet another reason: it draws no value at all. It marks a
simulated time on the horizontal axis and asserts nothing about the vertical
one. A labelling requirement of its own bounds the exemption. A control mark
must be visually distinguishable in kind from both a trace and a reference,
by something other than colour. The display must identify it as a record of
a user input, not of anything measured or modelled. It must also come with a
statement of which control moved and to what setting. A bare mark says only
that something unspecified happened. That invites the reader to supply their
own explanation for the change in the curves beside it.
See § "The control-input timeline".

Declaring where an adjustment begins is a statement about the *input
device*, not about the model. It changes no simulation state and records no
value. It must not alter what is recorded or what the model computes. The
declaration exists because a slider reports continuously while it is dragged.
The interface is therefore the only party that can tell one turn of a control
from two.

**How wide a window the chart draws is the reader's to choose, and the choice
may not change the run.** A case runs for hours, but the moment a learner is
most likely to be watching lasts minutes, so no single window serves both.
Three conditions bound the choice. First, it is a view control. It affects no
model state, alters nothing in the run definition, and leaves identical
inputs producing identical results. So it sits outside "Runtime controls"
with the other interface settings. Second, the width in force must be a fixed
property of the selection, not of how long the run has been going. A window
that grew with the run would rescale every trace's slope while the underlying
rates did not change. Third, a mode that claims to show the whole run must
show all of it at every length. A window narrower than the case, labelled as
the whole case, is a false statement about what the reader is looking at.
See § "The chart's time base", which carries the widths, the ruling and the
labelling that this paragraph requires.

**A playback rate is a number of steps, never a step size, and it has to be
on screen.** The two compartments that make uptake and distribution worth
teaching cannot be watched in real time. At the reference settings,
sevoflurane's muscle group has a time constant of about 135 min, and fat has
one of about 42 h. So the interface may play a run faster by taking more
steps per tick. Three conditions bound this, and they are of different kinds.

The first condition is arithmetic. The step size is fixed, and the rate is
realised *only* as the number of those steps that a tick takes. A rate that
does not land on a whole number of steps is refused rather than rounded,
because the alternatives would be a step of a different size, or a run
advancing at a rate other than the one displayed. This rule keeps a faster playback inside
"The reproducibility guarantee" rather than making it a second numerical
solution. Identical inputs still produce identical run definitions. Two
learners comparing the same case at different speeds are comparing the same
arithmetic. A count of more than 1 000 steps per tick is refused too
(`PL-T6P0`). A tick takes all of its steps before the interface can respond,
so a count with no bound would freeze the application with no error. The
bound is set by time: one step measured about 53 microseconds on 2026-10-26,
so 1 000 steps take about half of the 0.1 s tick. The tick is one step long,
so the fastest offered rate takes 300 steps per tick at any step.
<!-- provenance: app/playback.py MAXIMUM_STEPS_PER_TICK = 1000 -->
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**What the rate label is a statement about, and what was measured**
(`PL-SQJ1`). The label states the *setting*: the multiple of real time that
the loop is asked for. `app/playback.py` derives the steps per tick from that
setting, so the label cannot drift from the loop, by construction. The
simulated clock is exact at every rate, because simulated time is a count of
steps taken. Whether the wall clock keeps up depends on the host.
`RunView.step_tick` takes its burst on a `PreciseTimer` interval and takes no
extra steps to make up for a missed tick. A tick that the event loop could
not service is therefore lost. The **delivered rate** is the set rate times
the fraction of ticks that fired. It was measured on 2026-09-27 with the real
dashboard on the offscreen platform and both timers running. Every rung from
1× to 300× delivered 99.0 to 99.9% of its setting over 8 to 30 s. The tick
period stayed at 100 ms to within 4 ms. The 73 to 91% measured once came from
the Flet loop and went away with that toolkit. The label is therefore left as
it is, and nothing on screen names a delivered rate (project owner,
2026-09-27, ratified, over qualifying the label as "up to 300×", which trades
a precise claim that is true for a vague one, and over building the
disclosure now). A host that holds the loop past one interval delivers less
than the label says, and nothing on screen says so. `PL-2NYN` is the guard
that would show the delivered rate beside the set one when fewer than 95% of
ticks fire over a 50-tick window. A delivered rate below 99% measured on the
owner's own machine reopens the decision.
<!-- not-restated: 100 ms -->

The second condition is control resolution, and it limits what the sentence
above may be taken to mean. Those two learners are comparing the same
arithmetic. They are comparing the same *case* only if neither of them
touches a control. A tick advances its whole burst without interruption, so a
setting changed while the run plays first acts at a tick boundary. The
boundaries are `multiplier × 0.1` s of simulated time apart. The same slider
moves made at two rates therefore land at two different simulated instants
and produce two different runs. The runs differ because the inputs differed,
not because the arithmetic did. § "Supported simulation step" carries the grid for each rate, what one
step of it costs a displayed compartment, and the pause-change-resume route
that is exact at every rate.

The third condition is human factors, and it is why the rate is a required
displayed output rather than a preference. A rate is a **mode**. A clock
advancing at sixty times real time, beside numbers that look like a live
case, is easy to misread at a glance. So the rate must be shown wherever
simulated time is shown, at every rate, including real time. If the label
were absent at 1x, the label's *presence* would become the signal. A reader
would have to be taught that convention, rather than being able to read it
off the screen. The rate must not imply anything about the model. It is a
statement about how fast the interface is playing recorded steps, never about
the patient. It is also not a second reading of the clock it sits beside.

The interface must not:

- calculate uptake;
- calculate partitioning;
- calculate tissue flow;
- calculate mixed-venous return;
- integrate equations;
- correct negative stores;
- calculate mass balance;
- modify core state directly;
- continue a run past a step the core could not complete;
- take extra simulation steps to make up wall-clock time a slow tick lost,
  or otherwise let elapsed real time decide how many steps a run takes;
- change the simulation step size in response to a playback control, or
  advance a run at a rate other than the one it is displaying;
- let a view control change what a run recorded, or present a chart window
  narrower than the run as though it showed the whole of it;
- present a run halted by a failure as though it were paused;
- discard a run that holds recorded state without stating what will be lost
  and obtaining confirmation, as "Agent-change behavior" requires; or
- display a concentration at a finer resolution than "Displayed precision"
  justifies, or render a value the model does not resolve as though it were
  a value the model asserts; or
- predict when the simulated patient would wake, or display a
  time-to-awakening figure of any kind. The MAC-awake reference is a
  labelled population band precisely because a per-patient prediction is a
  claim this model does not support. A disclaimer beside such a number would
  not undo that claim, because the number would be acted on and the
  disclaimer would not.

The controller exposes immutable snapshots, and immutable windows onto the
recorded run, rather than mutable compartment objects.

## Minimum displayed outputs

The interface must show the following outputs. Each entry names the test that
enforces it, which makes the entries a bound family under
§ "How this document is held to the tree", clause 2. The test names say that
the value reaches the *display*, and that is the link that matters here. A
required output can go on travelling in `SimulationSnapshot` long after the
widget that draws it has gone. Three of these entries have no snapshot field at
all. The playback rate and the chart's time base are view settings, and
$`F_A/F_I`$ is derived at the point of drawing.

- simulated time (`test_refresh_view_formats_every_concentration_metric`,
  `test_the_clock_panel_reads_in_the_chart_axis_form_past_an_hour`);
- the playback rate that is set, as a multiple of real time. It is drawn
  wherever simulated time is drawn, and at every rate, including real time
  (`test_the_playback_rate_is_drawn_under_the_clock_it_governs`). It is the
  setting, not a reading of whether the clock is moving: a paused, reset or
  halted run still shows the rate it plays at, and the status word in the
  transport row says whether the run is running. See § "Interface boundary"
  for what the rate is a statement about, and what it is not;
- how much simulated time the chart is showing, and whether that width was
  chosen or fits the whole run so far
  (`test_the_axis_caption_states_the_span_the_chart_is_showing`,
  `test_the_caption_says_when_the_span_was_chosen_by_the_run_rather_than_the_reader`).
  See § "The chart's time base";
- run state, with running, paused, and halted-by-failure distinguishable from
  one another (`test_refresh_view_reflects_running_state`,
  `test_the_transport_is_enabled_by_state_in_all_four_states`);
- why a run halted, whenever one has
  (`test_refresh_view_reports_a_failed_run_as_stopped_not_paused`,
  `test_refresh_view_reports_the_supported_run_length_as_stopped_not_failed`);
- which agent is running
  (`test_the_readout_row_names_the_substance_its_numbers_belong_to`);
- the delivered concentration of that agent
  (`test_refresh_view_formats_every_concentration_metric`,
  `test_refresh_view_updates_delivered_concentration_label_for_current_agent`);
- circuit or inspired concentration
  (`test_refresh_view_formats_every_concentration_metric`,
  `test_the_alveolar_readout_is_labelled_end_tidal_equivalent`);
- alveolar or end-tidal-equivalent concentration
  (`test_the_alveolar_readout_is_labelled_end_tidal_equivalent`);
- mixed-venous concentration
  (`test_refresh_view_formats_every_concentration_metric`);
- vessel-rich concentration
  (`test_refresh_view_formats_every_concentration_metric`);
- muscle concentration
  (`test_refresh_view_formats_every_concentration_metric`);
- fat concentration (`test_refresh_view_formats_every_concentration_metric`,
  `test_a_real_run_displays_a_filling_compartment_as_below_resolution`);
- cumulative delivered amount
  (`test_the_accounting_panel_prints_amounts_at_one_decimal_of_a_litre`);
- cumulative exhausted amount
  (`test_the_accounting_panel_prints_amounts_at_one_decimal_of_a_litre`);
- total stored amount
  (`test_the_accounting_panel_prints_amounts_at_one_decimal_of_a_litre`);
- mass-balance residual or status
  (`test_refresh_view_reports_valid_agent_accounting`,
  `test_refresh_view_reports_failed_agent_accounting`); and
- every concentration above, and the delivered concentration, also shown as a
  multiple of the running agent's 1 MAC, with that agent's 1 MAC in percent
  stated on the display (`test_every_compartment_is_readable_in_mac_multiples`,
  `test_the_dial_is_readable_in_the_unit_its_compartments_are`,
  `test_the_display_names_the_mac_the_readouts_were_divided_by`). See
  § "MAC multiples as a display unit" for what the multiple asserts, and for
  why both units are shown rather than one being selected; and
- the running agent's population MAC-awake on the chart, drawn as a band. The
  band is labelled with the fraction and the divisor it was drawn from, and
  with the trace it is to be read against. The agent's nominal 1 MAC is drawn
  alongside it as a visually distinct line
  (`test_the_band_states_the_fraction_and_the_divisor_it_was_drawn_from`,
  `test_the_interface_says_which_trace_the_band_is_read_against`,
  `test_no_trace_dash_is_as_wide_as_the_one_mac_reference_line`). See
  § "MAC-awake as a chart reference" for what the band asserts and what it does
  not. That section also explains why no time-to-wake-up figure is displayed
  anywhere in the interface; and
- every setting changed during the current run. Each is listed with the
  simulated time it took effect, the control it changed and the values it moved
  between, and each is marked on the chart at that time
  (`test_the_list_states_what_was_changed_and_to_what`,
  `test_a_recorded_change_is_marked_on_the_chart_at_its_own_time`). See
  § "The control-input timeline"; and
- $`F_A/F_I`$ over the run, on a dimensionless axis of its own. The plot is
  labelled as a ratio against the modelled inspired concentration, not against
  the vaporizer dial. The plot carries the control marks above, is ruled at the
  equilibrium that the curve approaches, and states where the ratio is not
  defined
  (`test_the_wash_in_axis_is_ruled_at_quarters_and_the_window_is_the_chart_s`,
  `test_the_wash_in_plot_says_what_its_denominator_is`,
  `test_the_wash_in_trace_draws_nothing_before_agent_reaches_the_circuit`). See
  § "F_A/F_I as a displayed ratio" for the domain it is drawn over, and for
  what the curve does and does not assert.

The six compartment concentrations above are requirements on the **numeric
readouts**, not on the chart. The reader may show and hide the chart's
compartment traces (see § "Interface boundary"). A required value must not
leave the display when the curve that draws it does. Four of the chart entries
in this list are the MAC-awake band, the 1 MAC line, the control marks, and
$`F_A/F_I`$. They are requirements on the chart itself, and the reader cannot
hide them. The time base is the one chart entry above that the reader does
choose. For the time base, this list requires that the width in force is
stated. It never requires that any particular width is in force.

### What this list requires once the layout is the reader's

This list was written for one fixed layout. Since v0.6.0, `ROADMAP.md`
planned-milestone item 34 has let the reader add, resize and remove the
interface's areas. The two meet at the paragraph above. Hiding a compartment
trace is safe *because* the value stays in the numeric readouts. So a layout
that can remove the readouts removes the guarantee that the sentence rests on.
Every show/hide affordance that this document permits then becomes unsafe at
once. The failure is silent. The chart behaves exactly as documented while the
display no longer meets this list.

So the list divides into three parts. The division follows what a reader
could misread a value without. It does not follow how the interface happens to
be arranged today.

**Unconditional - the values that no workspace may remove and nothing may
cover.** The set is stated as a *test*, not as a list. The test is this: a
value is unconditional when a reader could misread the run's other displayed
numbers without it. Applying that test gives two tiers.

**Invariant, whatever is being simulated.** This tier is simulated time, the
rate at which it is advancing, run state, why a run halted (when one has), and
what is being administered. Once more than one top-level window can exist, the
tier also includes the name of the run that the window is showing. See
§ "What a second top-level window owes" below. That section is where the last
value comes from. It also explains why this tier and the next are allocated to
windows differently. None of these values depends on the substance or the
model. A concentration with no time, no run state and no named drug is the
correct number under the wrong patient. This document treats that as a display
failure, not as a missing convenience.

**Instantiated per modelled substance, and the current instance is not the
rule** (project owner, 2026-09-16). For the inhaled-agent model that this
document specifies, the test selects the delivered concentration and the six
compartment concentrations. Each is shown in both units, with that agent's 1
MAC in percent stated. **That instance applies only while an inhaled agent is
what the run models.** A run that administers no volatile agent owes no
vaporizer dial, no circuit concentration and no MAC multiple, because it has no
such quantity to misread. Examples are the intravenous models of `ROADMAP.md`
planned-milestone item 13, or any later substance. Such a run owes its own
instance of the same test instead. That instance is named where the substance's
model is specified.

Writing today's instance as the permanent list is a specific error. This
document has already made that error once, and it guards against it here. The
error is to record a rule that is true of the model currently implemented as if
it were a rule about the application. The test above is what generalises. The
seven concentrations are what the test currently returns.

**Reachable rather than simultaneously visible.** This tier is the agent
accounting: cumulative delivered, cumulative exhausted, total stored, and the
mass-balance residual with its absolute error. These values state whether the
*model* is conserving mass. A reader does not titrate against them. Their
absence from a particular workspace makes no clinical reading wrong, so a
layout may leave them out. They must stay reachable in every layout, and they
must not be removable from the application.

**What "reachable" means** (`PL-50PZ`, project owner, 2026-09-27, ratified,
over leaving the word undefined). A View kind is reachable in a Workspace when
a reader can bring it on screen from that Workspace through the interface
alone, in a bounded number of steps, without a drag or a file edit. Two parts
of the build make that true for every Workspace at once. First, every Area's
header carries a View chooser. Its menu lists every View kind that the build
registers, whatever the Workspace names, and choosing one shows it in that Area
(`app/area_layout.py`). Second, the dashboard's page grows to give a chosen
View the size it needs. So the choice shows the View itself, and never only the
notice that the Area is too small for it (`PL-K285`). The registry,
`app/view_registry.py`, marks the accounting View `required_reachable`. A build
that does not register that View fails when the module is imported. A layout
always contains at least one Area, so there is always a chooser to use. None of
the shipped Workspaces names the accounting View, so the chooser is its route
in the shipped set. `tests/integration/test_view_chooser.py` checks that route
from every Area of each shipped Workspace. Each Area that names the accounting
View builds a View of its own (`PL-TH35`). So when two Areas name it, both show
the five amounts.

**Conditional. These bind a surface only when that surface is shown.** A
concentration chart carries the MAC-awake band, the 1 MAC line and the control
marks. It also states how much simulated time it is showing, and whether that
width was chosen or fits the run. An $`F_A/F_I`$ plot carries its equilibrium
rule and states where the ratio is not defined. A reference exists so that a
*trace* is not read without its clinical anchor. Where no trace is drawn, there
is nothing to anchor, and nothing is lost when the surface is absent. What must
never happen is a surface shown without its references. That is what these
entries have always been about.

**The control-input timeline splits the same way.** The record itself is
unconditional. The record is every setting changed during the run, with the
simulated time it took effect, the control it changed and the values it moved
between. Its **marks on the chart** are conditional on a chart being shown. The
list carries the facts, and the marks carry the reading against the curve. That
reading exists only where a curve does.

**Where the unconditional set lives in the build.** `app/unconditional_set.py`
states the two tiers and the control-input record as data, with the inhaled
instance as `INHALED_AGENT`. Each run's values sit in one region across the top
of the dashboard, outside the Areas that `app/area_layout.py` lays out. Since
`PL-W9P6` (2026-10-18), the setting sections sit in a plain column between the
region and the Areas, so they are not in an Area either. The dashboard refuses
to place a run whose region lacks a declared value. So a value moved into an
Area fails at once, rather than becoming something the reader's own Area
operations can close (`PL-NWTM`, laid out to `PL-J8K2`).

**Where the educational-use disclaimer lives** (`PL-JSY5`, 2026-10-18). The use
disclaimer, `USE_DISCLAIMER_TEXT`, is a standing statement rather than one of
this list's values, so `app/unconditional_set.py` does not declare it. Its home
is the line across the foot of the window, outside the layout container. The
project owner ratified that placement on 2026-10-11, together with the band
across the top (`PL-J8K2`, Q1). No split, join, close or Workspace switch
affects the line, so it is present in every Workspace a learner builds
(`test_the_dashboard_carries_the_educational_disclaimer`). Once more than one
top-level window can exist, each window carries the line in its own frame,
beside its invariant tier. This is because a window read alone needs the
statement of what the tool is for as much as it needs the run's time and agent.

*Always in view* (`PL-NNML`, 2026-10-20). The line sits at the foot of the
window, below the part of the dashboard that scrolls. The unconditional region
sits at the top, above that part. Only the Workspace tabs, the Areas and the
case's controls scroll between them. So neither the window's height nor any
scrolling takes the line out of view. Neither takes the region out of view
either, nor the interpretation statement, `INTERPRETATION_DISCLAIMER_TEXT`, on
the region's readout heading row. That includes the scroll to the concentration
chart that happens when a branch is taken (`PL-562Z`). This is what the colour
section below means by "always". Before this change, the whole page scrolled.
Measured offscreen at 1366 px wide on 2026-10-20, the page was 1087 px tall in
the Default Workspace and 1505 px in Induction and Maintenance. So in a 700 or
900 px window, the line was below the visible part, and scrolling down to it
moved the region off the top.
`test_the_region_and_the_use_disclaimer_stay_in_the_viewport` checks both at
700, 900 and 1100 px in each shipped Workspace.

**The rule all three rest on is about occlusion, not about window types.** No
value this list requires may be covered while the application still believes it
is showing that value. This one sentence applies to a panel drawn over the
dashboard. It applies to a second top-level window dragged over another
window's invariant region, or over the main window's per-substance readouts. It
applies to any later floating mechanism. It covers all three without being
argued again for each. It is a property of the display rather than of a window type, which is why it
is stated once, here.

**What "the application believes" is bounded by what it can observe, and the
boundary is stated rather than implied** (2026-09-16). The rule applies to the
application's *own* windows and panels, which it creates, positions and can
query. It makes no claim about a window that belongs to another application, or
to the operating system, drawn on top of one of ours. That is not a loophole
being reserved. It is the limit of what any application can enforce. Saying so
stops a later reader from taking the sentence above as a guarantee against
every way a value can be hidden. What the toolkit itself can report is narrower
than it first appears, and this was measured rather than assumed (PySide6
6.11.2 / Qt 6.11.2, 2026-09-16). `QWidget.isVisible()` is documented to stay
true for a widget "obscured by other windows on the screen". So it reports the
application's own show/hide bookkeeping, and never occlusion.
`QWindow.visibility()` reports which of Hidden, Windowed, Minimized, Maximized
or FullScreen a window occupies. That catches a minimized or hidden window and
nothing else. The one signal close to occlusion, `QWindow.isExposed()`, is
documented only as something that *might* change when a window is "made totally
obscured by another window". The platform plugins also disagree about it. The
macOS plugin drives it from `NSWindow.occlusionState`, while the Windows plugin
deliberately keeps it true under occlusion for compatibility. So it is not a
signal that a safety rule may rest on, and this document does not rest one on
it. What the application must do is the half it can achieve. It must never go
on *asserting* that it is showing a value when it can see that the value's own
window is minimized or hidden.

**Guaranteed structurally, not by validating a saved layout.** Each top-level
window's unconditional region sits outside *that window's* area system. So no
split, join, close or workspace switch affects it, and no saved layout has to
be checked against this list to be safe. Closing a window is also one of those
operations, and it is the one operation that the area system does not own. The
main window cannot be closed while any other window is open. That is what keeps
the per-substance tier from being closed out from under a reader. Validating
each workspace and refusing the ones that fail is the fallback for anything
that cannot live in that region. Validation warns after the fact, where the
structure prevents the failure. That makes validation the weaker of the two,
which is why it is the fallback. Blender is the model for the *structure*, a
region outside the area system, and explicitly not for its persistence.
Blender's Topbar and Status Bar sit outside the area system as this region
does, but neither is unconditionally present. *Focus Mode* (View -> Area ->
Focus Mode, Ctrl-Alt-Spacebar) hides the Topbar, the Status Bar and the
editor's secondary regions together, for maximum screen space (Blender Manual,
"Interface -> Window System -> Areas", read at the source 2026-09-16). That is
the right trade for a 3D application and the wrong one here. Blender has no
class of value whose absence is a safety failure, and this application does. So
take the structure and refuse the escape hatch. Say so wherever a reader would
otherwise assume that the whole precedent was copied.

**What a second top-level window owes, and it is not the whole set** (project
owner, 2026-09-16, ratified - a recommendation put to them and agreed, chosen
over the two live readings `PL-W54S` had written, and reopenable on ordinary
evidence per `CLAUDE.md`; the occlusion rule above is not, being the safety
floor rather than the arrangement). The guarantee above is stated against the
area system's own operations. It stops at the frame of the window that carries
the region. `ROADMAP.md` item 34 includes break-out as its second half, which
is wanted but not yet scheduled (project owner, 2026-09-26). Break-out takes an
area into its own top-level window, which is itself a full window with its own
areas. The region that v0.6.0 builds has to be the right shape for break-out on
the first attempt. `PL-WLWY` wrote three candidate readings of what such a
window owes, and closed without choosing between them. The answer is a fourth
reading. It splits the obligation the way this section has already split the
list, because **the two tiers are unconditional for different reasons and those
reasons travel differently**:

- **Every top-level window the application owns carries the invariant tier
  together with the name of the run that window is showing.** The invariant
  tier is simulated time, the rate at which it is advancing, run state, why a
  run halted (when one has), and what is being administered. The tier and the
  name sit in a region outside *that* window's area system. The tier's own
  justification above is that "a concentration with no time, no run state and
  no named drug is the correct number under the wrong patient". That is a
  property of any surface that displays a concentration, not of the display
  taken as a whole. So the tier follows the concentration into whatever window
  the concentration goes to. It is five values and a name. That is small enough
  for a window holding one chart to carry it without the squeeze that
  § "Diverged, and each divergence has a specific cause" of
  `docs/interface-provenance.md` refuses.
- **The per-substance tier lives once, in the main window**, which **cannot be
  closed while any other top-level window is open**. Closing the main window
  closes the others. This tier's justification is the other one: a reader could
  misread the run's *other* displayed numbers without it. That is a statement
  about the display taken as a whole, not about any one surface.
- **The accounting tier is unchanged**, because it is already an obligation on
  the application rather than on any layout or window.

**Why the other two readings were refused**, recorded so that they are not
proposed again. *Every window carries the whole region* is not merely the
stricter option. A broken-out window is typically small, such as one chart on a
second screen. Forcing seven concentrations in two units into it has one of two
results. Either they dominate the window, which defeats break-out, or they are
squeezed, which is the failure the never-hidden divergence exists to refuse.
*The main window carries everything and a broken-out window names only its run*
leaves a window drawing compartment traces with no time, no rate, no run state
and no agent. It also rests the guarantee on a window that the reader may not
be able to see. `PL-WLWY` used that same property to rule out the reading that
the contract applies to the application rather than to the window. A guarantee
that rests on where the window manager has put things is the same guarantee in
both cases.

**This is the display side of an evidenced failure mode, not a house
preference.** It is established that correct data read in the wrong context is
a distinct class of clinical-information-system error. Ash, Berg and Coiera
describe the "silent errors" that such systems foster rather than prevent (*J
Am Med Inform Assoc* 2004;11(2):104-112, doi:10.1197/jamia.M1471). Magrabi and
colleagues classified 42,616 reported incidents. Their classification makes
information *output* a category in its own right, at 20% of computer-related
problems (*J Am Med Inform Assoc* 2010;17(6):663-670,
doi:10.1136/jamia.2009.002444). The closest measured analogue of the rule above
is the wrong-patient order. Restoring one piece of patient context to the
display banner, a photograph, was associated with lower wrong-patient order
entry across 2,558,746 orders (adjusted OR 0.57, 95% CI 0.52-0.61; Salmasian et
al., *JAMA Netw Open* 2020;3(11):e2019652,
doi:10.1001/jamanetworkopen.2020.19652). That is the invariant tier's argument
in a different clinical setting: context carried in the frame of the view,
rather than assumed from elsewhere on the screen. Two things are deliberately
*not* claimed here, because they were checked and not found. The first is that
duplicating a live readout across windows is itself a named hazard. The one
randomised trial of concurrently open records found no difference in
wrong-patient errors (Adelman et al., *JAMA* 2019;321(18):1780-1787,
doi:10.1001/jama.2019.3698). The second is that tiling is a published
preference over overlapping windows. The only controlled comparison does not
support that claim. The tiling argument rests on this project's own occlusion
reasoning, as item 34 already records.

**A stepping stone, and recorded as one** (project owner, 2026-09-15). This is
deliberately the rigid version, with a fixed unconditional region and a
conditional remainder. It was chosen to be correct while the layout apparatus
is built, not to be the apparatus's final shape: "ultimately, will be able to
resize everything however ... I'm ok with starting with a relatively more rigid
structure as a stepping stone". So the particular split of this list is
expected to be revisited as that apparatus matures. What must survive any
revision is the occlusion rule above. That rule is the safety requirement,
while the split is only the arrangement.

**While two runs are shown, every readout names the run it describes, and all
six compartments keep theirs** (`PL-1XPX`). This list is a requirement on the
numeric readouts, and it does not become a smaller one in compare mode. The
rule in the paragraph above says that a required value must not leave the
display with the curve that draws it. That rule applies to the chart's
two-compartment cap (`ROADMAP.md` v0.5.0, `PL-HLD5`) exactly as it applies to a
reader hiding a trace. The cap is a colour-capacity limit on the chart, not a
reduction of what the display owes. So while two runs are compared, the chart
may draw two compartments and the readouts still carry six, for both runs. The
readouts are what keep the other four on the display.

**The run is named in text, not carried by colour or by position.** Colour is
spent on the compartment, and it cannot take a second meaning on either side of
a mode change. "The six compartment traces" measures the worst
trace-against-trace pair at 1.01:1 against a 3:1 requirement. That is why
`PL-HLD5` put the run on line width rather than colour. Text has no equivalent
of line width. Position alone fails the reader who has looked away and back,
which is the stale-context failure that this requirement exists for. A
concentration that does not say which management produced it is the correct
number under the wrong patient context.

**A run's name renders its identity, not its place** (`PL-7Z84`). Each run that
the session places is given a number, counting from 1, and the name is "Run"
followed by that number. A run keeps its number for as long as it holds its
place on screen. For the trunk, that is from when the dashboard opens. For a
branch, it is from its fork until it is dropped. The run's own Reset and a
change of agent both keep the number, because both start a new run definition
in the same place, after any confirmation that § "Agent-change behavior" asks
for. No number is given out twice in a session. So a branch taken after a
dropped one is "Run 3", never a second "Run 2". A reused name would let a
Workspace pinned to the dropped run find a run of that name, and show its
values as the dropped run's values. `src/anesthesia_sim/layout/run_identity.py`
defines the identity, and `dashboard_frame.run_label` is the one place where it
is rendered.

A view shows the name of its run whenever a reader could mistake its values for
another run's values. That applies in three cases: while another run is drawn
anywhere in the application, while the view is pinned to a run, and always in a
window broken out of the main one
(§ "What a second top-level window owes, and it is not the whole set"). The
old test was the number of runs on the dashboard. That test fails for a run
shown alone in a pinned Area or in a window of its own. Break-out windows are not built, so the dashboard is the
only window in which a run is drawn. In this version, therefore, the names are
shown when two runs are compared, and a pinned Workspace shows its run's name
in the header of every Area (`PL-2KXB`).

**A Workspace pins a run by its identity, and an absent pin is stated**
(`PL-WV9K` Q6). The pin is saved with the Workspace as two values: the run's
number, and the random token of the session that placed the run. A run with
the same number in a later session is therefore a different run. When a pinned
run is not open, the Workspace's Areas show a named "run not present" state. They
never show another run in its place, and the simulation is left untouched.
`Workspace.shown_runs` decides which runs a Workspace's Views show. The tab
strip (`PL-2KXB`) is where a reader sets a pin and sees the absent state.

**Both runs are shown, rather than the selected one with the selection stated.**
Showing only the selected run would make the readout block a mode. A stale
selection in that mode would have no visual sign at all. The block looks the
same whichever run is selected, so a reader who has forgotten the selection
takes one management's number for the other's. Stating the selection only
warns after the fact, whereas showing both runs prevents the error. Pairing the
two values under one compartment label keeps this from doubling the block's
height. The second run's value and its second unit sit under the first run's
value in the same panel. Each value has its run's name on the line above it.
So the block keeps one row of seven panels, and it grows by those name lines
rather than by a second row (`PL-F2YS`). This preserves the one-row
comparative reading for which this document requires the resolution to be
uniform: a reader sees the circuit lead the alveoli, and the alveoli lead the
tissues. The two values are stacked rather than placed side by side because
stacking keeps each panel at its one-run width. That width keeps the row seven
panels across at 1366 px. Placed side by side, the values would make each
panel roughly twice as wide. Each run's delivered concentration sits on that
run's own line, beside its name and its transport controls. The values that
the two runs share are stated once, on the heading line above the paired
block: the substance, the agent's 1 MAC, and the version and model. They are
the same for both runs for two reasons. A second run must use the first run's
agent, and a branch's MAC is checked against its trunk's MAC when the branch
is opened (`PL-QLZ5`). `PL-3355` still applies. A readout panel reserves the
width of the widest value it can show, so a value is never wrapped away from
its unit at any width at which the row is laid out.

**No difference readout is required, and none may be added without a stated
sign convention.** The arithmetic difference of two alveolar fractions is not
a quantity with a conventional clinical reading. Clinicians reason about depth
in MAC multiples and in time-to-target. Displaying such a difference would
imply a standard meaning that it does not have, and "Displayed precision"
refuses that on grounds of interpretability. The chart already shows the
comparison continuously, on the axis the reader is looking at.

Arterial concentration is deliberately **not** in this list. In this model,
arterial blood holds no independent state: $`F_a \equiv F_A`$ (see § "Model
boundary"). A separate arterial readout would
therefore display the alveolar number a second time under a different name.
That would present a definitional identity as though it were an independently
modeled quantity. Earlier revisions of this document required an arterial
readout. That requirement dates from before the arterial simplification was
made explicit. It is withdrawn, rather than satisfied by a duplicate label.

Showing which agent is running is a required output, not a convenience. A
correct concentration attributed to the wrong agent is a presentation failure.
The same number also means a different clinical depth for each agent: 2% is
about 1 MAC of sevoflurane but roughly a third of a MAC of desflurane.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- derived: a third of a MAC of desflurane from data/agents/desflurane.json mac_percent = 6 -->

The agent selector and the header reinforce that written name with the
agent-identification color specified by ISO 5360:2016 Table 2 ("Dimensions and
colours of agent-specific bottle collars and connectors"): yellow for
sevoflurane, purple for isoflurane, and blue for desflurane. Footnote b of that
table is the reason the color appears here at all: "if a colour is used on a
vaporizer, bottle, or package label to facilitate correct identification, it
is important that only the colour for the appropriate anaesthetic agent be
used". Displaying a color therefore obligates the application to display the
correct one. Color is a redundant cue, never the only identifier. The agent
name stays visible, and each foreground and background pair must meet WCAG 2.2
AA contrast. The cited standard references, the screen-color approximations
and the accessible foregrounds are kept together in `app/theme.py`, so that the
mapping can be audited as one unit.

The displayed fills are two approximations away from the standard's own value.
They must not be read as an exact reproduction. Table 2 footnote c states that
"Munsell colour is the original" and that the other color systems it lists
"show the nearest available colour sample". The Pantone reference is therefore
already ISO's approximation, and the sRGB `fill` approximates the Pantone in
turn. Converting each Munsell original to sRGB independently (via Illuminant C,
chromatically adapted to D65) gives the deviation of each displayed fill from
the standard's original value:

| Agent | ISO Munsell original | Munsell as sRGB | Displayed fill | ΔE00 |
| --- | --- | --- | --- | --- |
| Sevoflurane | 6.25Y 8.5/12 | `#F2D600` | `#FEDB00` | 2.1 |
| Isoflurane | 7.5P 4/12 | `#8D4192` | `#981D97` | 5.7 |
| Desflurane | 10B 4/10 | `#0069A0` | `#00629B` | 2.6 |

<!-- not-restated: 2.1 -->

The sevoflurane and desflurane originals fall outside the sRGB gamut. No
display can reproduce them exactly, so some deviation is unavoidable rather
than a choice. The Scope of ISO 5360 excludes desflurane's *dimensions*, and
Table 2 records "N.S." for its collar angle. Its *colour* is specified in that
same row, and that colour is what this application uses.

A known limitation of the standard is reproduced here deliberately. A user
with a color vision deficiency cannot distinguish isoflurane's purple from
desflurane's blue. For normal color vision the two differ by only 1.09 in
luminance, so hue alone separates them. Simulating the three dichromacies
removes the hue without supplying the luminance: 1.48 for protanopia, 1.06 for
deuteranopia, and 1.11 for tritanopia. These values were measured by
`tools/contrast_check.py` with the Brettel 1997 projection recorded under § "The
six compartment traces" below. They are pinned by
`tests/unit/test_contrast_check.py`, so this paragraph cannot go stale behind a
color edit. Choosing more separable colors would break the correspondence to
real vaporizers, so it is the worse option. The mitigation is that the agent
name is always rendered alongside the color. `tests/unit/` asserts this for
both the dropdown options and the header badge. Color must never be the only
thing distinguishing two agents in this interface.

Distinguishing a halted run from a paused one is required for the same
reason. Both stop the numbers advancing, and under § "Step atomicity" both
leave state that the reader can trust. But a paused run will continue when
the reader asks, and a halted run cannot. A halted run displayed as "Paused"
therefore offers a Start control that will fail on its first tick. It also
presents a stopped trajectory as one still in progress. That is the
mode-confusion failure that this specification's interface rules exist to
prevent. A display that is merely frozen, with no change of state at all, is
worse still.

The phrase “end-tidal-equivalent” must not imply that airway sampling dynamics, dead space, or capnography are modeled.

**The alert colour deliberately does not follow the medical alarm-colour
convention** (project owner, 2026-09-14). The agent colours above are adopted
*because* a standard obligates them. This is the opposite decision, about a
different colour. The two are recorded together so that the difference is
visible rather than inferred.

IEC 60601-1-8 governs *visual alarm signals*, which are indicators that encode
priority by colour together with a flash rate. This interface has none. Every
use of `WARNING` in `app/theme.py` is bold coloured text. Those uses are the
run-status word, a transient notice line, the agent-accounting status word,
the permanent educational disclaimer, and the case-discard dialog. There is no
indicator lamp, no filled banner, no flashing element and no priority tier. So
there is nothing to which the convention could apply.

The disclaimer is what settles the question, and it points away from adopting
the convention rather than toward it. `WARNING` is the colour of a line that is
on screen *always*. A monitor's alarm colours carry meaning precisely because
they are absent until something is wrong. A permanent element painted in a
high- or medium-priority alarm colour would teach the opposite of the
convention it borrowed. The divergence is also chosen for its own sake. A
teaching tool that looks unmistakably unlike a monitor cannot be mistaken for
one, and this project's disclaimers already take that view.

*"Always" names where the line lives, not that it is in view on every screen
today* (`PL-JSY5`, 2026-10-18). Where the line lives, and the one gap in that,
are stated in § "Minimum displayed outputs" -> "What this list requires once
the layout is the reader's". The argument above needs only that the line is
a permanent statement rather than a conditional one, and that is true at every
window size.

The interface applies the same economy of signals one level down. The
supported-run-length boundary is `MUTED`, not `WARNING`, for two reasons.
Colouring a correct model's declared boundary as a fault would teach a reader
to distrust a number that is sound. It would also spend the one signal that
this interface has.

Two things apply regardless, and neither is in question. First, any colour
chosen must still clear the contrast target that `tools/contrast_check.py`
enforces. Second, the ISO 5360 agent colours are untouched. They identify an
agent and carry no urgency. That is why Table 2 footnote b obligates them and
nothing obligates this colour. **The decision binds the Qt port as much as the
current interface**. The port decides the palette afresh, and it is the moment
at which an indicator-shaped surface could first appear. The port must not
arrive carrying a monitor's priority palette.

*The priority-to-colour mapping itself is deliberately not recorded here.* It
could not be established from a primary source, and the secondary sources
disagree. Three independent reports give the low-priority colour as cyan, as
blue, and as "green or blue". Writing down a value that is wrong at least twice
over would be worse than recording none. The decision above does not depend on
the mapping.

### MAC multiples as a display unit

Every compartment is displayed twice. One display is a percent of one
atmosphere, and the other is a multiple of the running agent's 1 MAC. Both are
shown at once: on every compartment, on the delivered-agent control, and on
the chart. The chart carries a percent axis on the left and a MAC axis on the
right. Each axis states its own unit in its title, `% of 1 atm` and `×MAC`.
Until PL-6580, both units were stated in a caption above the plot instead.
The percent unit is `% of 1 atm` and not `vol %`. A volumes percent is a
gas-phase volume fraction. The circuit and alveolar compartments have one. The
mixed-venous, vessel-rich, muscle and fat compartments do not. They hold a
partial pressure instead, which convention quotes as a percentage of an
atmosphere. An axis that titled all six as a volume fraction would claim, for
four of them, a quantity they do not have.

**Why the second unit exists.** A percent axis silently changes meaning when
the agent changes. 2% is 1 MAC of sevoflurane and about a third of a MAC of
desflurane. So two runs plotted in percent are two different clinical
situations drawn at the same height. A learner who compares a desflurane
wash-in to a sevoflurane one in percent is comparing nothing. MAC multiples
are the unit that keeps its meaning when the agent changes, and they are the
unit clinicians reason in.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- derived: a third of a MAC of desflurane from data/agents/desflurane.json mac_percent = 6 -->

**What a MAC multiple on a compartment asserts.** This is the whole difficulty
of the unit, and the difficulty is not the arithmetic. MAC is defined for the
*alveolar* (end-tidal) concentration at one atmosphere in a nominal
40-year-old. It is the population ED50 for immobility in response to a
standardized surgical stimulus. So:

- On the **alveolar** compartment, a MAC multiple has its conventional
  meaning. It is subject to every limitation of the divisor recorded below.
- On the **circuit, mixed-venous, vessel-rich, muscle and fat** compartments,
  it means only *this compartment's partial pressure equals N times the
  alveolar partial pressure that would be 1 MAC*. It is a ratio of partial
  pressures. It is **not** a statement that the patient is at N MAC of
  anesthetic depth. The two read identically on a label unless the label says
  which one it means.

The display never presents the ratio as a depth, and the notation is what
tells the reader so. The unit is written `×MAC` on every readout and on the
chart's right-hand axis, for the reason given below. Until PL-6580, the
distinction was also stated in prose beside the chart, in the terms above.
That paragraph was removed with the rest of the panel's explanatory text. The
reader of this display is an anesthesia provider. For that reader, what MAC is
defined against is fundamental knowledge, not something to be taught at the
top of a chart. A dozen lines of text between the reader and the plot cost
more than they gave. This section is now the only full statement of the
convention, which is why it is stated here at length.

Three further limitations apply to every compartment, including the alveolar
one, and none of them is modeled here. First, MAC falls about 6% per decade of
age (Mapleson 1996, cited in each agent's `sources`), and this model's
reference adult has no age parameter. Second, the MAC multiples of
co-administered agents are additive, and this model runs one agent at a time.
Third, opioids, temperature and patient factors modify MAC, and none of them
is represented.
<!-- not-restated: 6 % -->

**The unit is written `×MAC`, not `MAC`.** "0.80 MAC" is read as a depth.
"0.80 ×MAC" is read as what the number is. The multiplication sign does safety
work rather than typographic work, and that is why the readouts carry it. The
chart's right-hand axis is titled `×MAC` for the same reason and in the same
words. Its ticks show bare numbers, such as `0.5` and `1.0`. So the title is
the only thing on the plot that says what they are. The title also labels six
traces at once, and five of them are not the compartment that MAC is defined
for. One unit is written as one token everywhere it appears.

**The divisor is displayed.** A MAC multiple has exactly one free parameter.
`CLAUDE.md` requires a clinically meaningful displayed value to be traceable
to the transformation that produced it. The interface therefore states the
running agent's 1 MAC in percent beside the chart, as "1 MAC sevoflurane =
2.0%". A reader who disagrees with the divisor can then see that they
disagree. They can also convert back to the percent that the model actually
computes.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->

**Nothing in `core/` computes a MAC multiple.** The transformation lives in
`app/formatting.py` and takes the divisor as an argument. The divisor reaches
it through `SimulationSnapshot.agent_mac_percent`. That field sits beside the
concentrations the divisor scales and the agent it belongs to. So a frame
cannot pair one agent's compartment with another agent's MAC. The chart's
plotted points remain in percent. The MAC axis relabels that same coordinate
rather than carrying a second series, so the two axes cannot come to disagree
about where a trace is. Both units are always shown rather than selected,
because a unit selector would make the axis unit a mode, and a chart read under the
wrong assumed unit is a misreading that no disclaimer catches.

**The chart's vertical range is denominated in MAC, and fixed.** For every
agent, the axis runs from 0 to **3 ×MAC** of the running agent, with a rule
every half MAC. The axis is therefore one ruler: the same case drawn under two
agents is drawn at the same height. That is the property the second unit
exists to give, and the axis previously took it away. Until PL-CC23, the top
of the axis was the agent's vaporizer dial maximum. That was 3.00 ×MAC of
desflurane, 4.00 of sevoflurane and 4.17 of isoflurane. So a learner who
compared a desflurane wash-in to a sevoflurane one was comparing shapes
silently rescaled by 1.39×. The horizontal rules were also a fixed 2 percent
apart. That is every 0.33 ×MAC under desflurane and every 1.67 ×MAC under
isoflurane.
<!-- derived: 3.00 from data/agents/desflurane.json max_delivered_concentration_percent = 18, mac_percent = 6 -->
<!-- derived: 4.00 from data/agents/sevoflurane.json max_delivered_concentration_percent = 8, mac_percent = 2 -->
<!-- derived: 4.17 from data/agents/isoflurane.json max_delivered_concentration_percent = 5, mac_percent = 1.2 -->
<!-- derived: 1.39 from data/agents/isoflurane.json max_delivered_concentration_percent = 5, mac_percent = 1.2 -->
<!-- derived: 1.39 from data/agents/desflurane.json max_delivered_concentration_percent = 18, mac_percent = 6 -->
<!-- derived: 0.33 from data/agents/desflurane.json mac_percent = 6 -->
<!-- derived: 1.67 from data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**Why 3, and why fixed.** Three is exactly desflurane's dial maximum divided
by its 1 MAC. So the shared ceiling is anchored to a real device limit rather
than to a preference. The agent whose vaporizer is most limited also gets no
dead band above its reachable range. The ceiling puts the 1 MAC line at a
third of the plot height. That is inside the plot rather than on its frame,
which a ceiling of 2 could not do. The ceiling also keeps on the plot the 2-3×
MAC range that overpressure induction works in. The axis is fixed rather than
fitted for the reason that "Why the axis is fixed rather than fitted" gives
for the wash-in plot below. An axis that grew to fit an excursion would redraw
a rising curve at a smaller height partway through a lesson. A reader would
attribute that change of shape to the model. The axis is fixed across the
session, not only within a run, so two consecutive runs are comparable too.

**A trace above the ceiling is named, not left to look like a plateau.** A
fixed ceiling can be exceeded, where a ceiling at the dial maximum could not.
The setting that exceeds it is in common use, not an edge case. Sevoflurane's
8% dial setting is 4.00 ×MAC and is a common inhalational-induction setting. A
clipped trace draws as a horizontal line at the top of the frame, and a
horizontal line is what a plateau looks like. So a reader would conclude that
the concentration stopped rising at 3 ×MAC when the model says it did not.
That is a wrong clinical reading of a correct model. The chart therefore names
the compartments that are above the ceiling. It also says that the readouts,
which are not clipped, keep showing their values. The comparison is made
against the displayed resolution rather than against zero, so a trace sitting
exactly at the ceiling is not reported. This matters because isoflurane's
ceiling is 3 × 1.2, which in binary floating point is 3.5999999999999996.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- derived: 4.00 from data/agents/sevoflurane.json max_delivered_concentration_percent = 8, mac_percent = 2 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**What the divisor is worth.** `mac_percent` is a tier-3 value, and this
section is where that matters most. The value is now the divisor of every MAC
number on the display, not only the vaporizer's starting position.
"Delivery-limit and MAC parameters" carries its provenance and the size of the
gap against the primary literature. That includes the consequence for the
cross-agent comparison that this unit exists to support.

### The chart's time base

**What it is.** The time base is how much simulated time the chart shows at
once. The reader either picks a width from a fixed ladder or leaves the
default, which fits the whole run so far. In both cases the horizontal axis is
simulated time. The time base decides only how much of that time is on the
plot and how finely the span is ruled. The code for this section is
`app/chart_time_base.py`. That module is arithmetic over simulated time. It
reads no simulation state and imports no toolkit. So the widths and the rule
this section reasons about can be read, cited and tested without loading the
interface. The section above governs the vertical axis, and this one governs
the horizontal axis.

**Why a case needs one.** The compartments this model exists to teach are
slow, but the moment a learner is most likely to be watching is not. At the
reference settings, muscle's time constant for sevoflurane is about 135 min
and fat's is about 42 h, while induction lasts minutes. A five-minute window
hides everything slower than the vessel-rich group. A twelve-hour window puts
a five-minute induction in the leftmost 0.7% of the plot. The playback rate is
what makes a long case watchable in one sitting, and the time base is what
makes it readable. They are separate controls because they address separate
questions: how fast the run advances, and how much of it is in view.

**A time base is a view control and reaches no model state.** Choosing a time
base changes which part of the run is drawn, and at what column spacing, and
nothing else. No step is resized. Nothing in the run definition is added,
discarded or altered, and the run is not re-stepped. The time base therefore
leaves "The reproducibility guarantee" untouched. The same case watched at
fifteen minutes and at twelve hours is the same run, keyframe for keyframe.
Every point drawn at any width is still a state that the run reached at the
simulated instant where the point sits on the time axis. It is evaluated from the run definition
under the constraint that "Interface boundary" places on a plotted trace. So a
wider window is a coarser *grid* of exact states. It is never a resampling, an
interpolation or a stored image zoomed into.

**Why a fixed ladder rather than a free zoom.** The selected width is the
width of the window at every point of every run. So seconds per pixel is a
property of the reader's choice, not of how long the run has been going. A
trace's slope on the plot is then a fixed multiple of its rate. The slope
stays comparable between two moments of one run and between two runs. A
window that grew continuously with the run would rescale every slope while the
underlying rates stayed the same. That would be a misleading visual encoding
of rate of rise, which is the one quantity that uptake and distribution are
taught by. The fixed vertical range rests on the same argument. Discrete steps
also make one step a meaningful change rather than a nudge, because each rung
is at least half again as wide as the one below it.

**The ruling derives from the width.** Each rung carries the interval at
which its gridlines and labels fall. Every rung is ruled into four to six
intervals. That range looks like a grid, rather than like a bare axis or a
hatch pattern. A single fixed interval cannot do that across the whole ladder.
The 60 s interval that this replaced would rule a twelve-hour axis into 720
lines, which would look like a solid block. Ticks stand at multiples of the
interval measured from the case's zero, not from the window's left edge. So a
gridline stays at the same simulated time as the window slides underneath it.
That is true for every run on the axis, because a branch is on the same clock
as the trunk it came from.

**Fitting always fits.** Fitting is the default mode. Past the widest declared
rung, the ladder continues by doubling, rather than stopping at the widest
rung and showing only part of the case. Suppose a mode named for showing the
whole run silently showed the most recent twelve hours of a fourteen-hour run.
It would then claim something false about what the reader is looking at. That
is why the honesty of the name is a requirement on the mode, not a property of
how far the ladder reaches. The ladder also carries rungs below the narrowest
width that the selector offers. Fitting can reach those rungs, but the reader
cannot choose them. Fitting has to work at ten seconds as well as at ten
hours, and choosing a span with nothing in it gives a view nobody wants.

**Every axis label carries its own unit, and the width in force is stated.** A
tick reads `0`, `45s`, `3m`, `1m30s` or `1h30m`, rather than a bare number
under a unit given in a caption. The axis spans anything from a minute to half
a day. So a bare `12` would mean twelve minutes on one time base and twelve
hours on another, while looking identical on both. A reader who missed the
caption would have nothing in the label to correct them. Beside the plot, the
chart names the width in words. It also says whether the reader chose that
width or it is the whole run so far, because those are different claims about
what is on screen. The time base is a mode in exactly the sense that the
playback rate is one, and it is displayed for the same reason. When a reader
cannot see the span, they supply their own assumption for it.

**Each chart holds its own time base** (project owner, 2026-10-19,
ratified, over one shared window saved per Workspace; `PL-L59K`). The
concentration chart and the F_A/F_I plot each carry a time-base control. A
choice made in one control sets that chart alone. So one chart can show the
first fifteen minutes of a case while another fits the whole run. `ROADMAP.md`
§ "v0.6.0 - the layout is the reader's", Required scope entry 11, asks for
this. Two charts at different widths no longer share a time axis, so each
chart states its own width beside its plot. Every advisory that depends on the
window is based on that chart's own window and shown on that chart. These
advisories are the notice naming traces above the axis, the count of control
changes the chart could not mark, and the count of F_A/F_I stretches it could
not draw. A notice naming a clipped trace that the chart in front of the
reader does not draw would be false for that chart. Charts at the same width
are drawn from one frame, so they show the same instants. A chart saves its
width with its other settings. The shipped Induction Workspace saves its
concentration chart on the 15-minute width, which follows the run. So the
current values stay on the plot after the first fifteen minutes. Switching to
the Induction tab loads that state, so its chart opens on that width
(`PL-2KXB`).

### MAC-awake as a chart reference

The compartment chart carries two horizontal clinical references. A **band**
marks the running agent's population MAC-awake, and a **line** marks its
nominal 1 MAC. Neither is a modeled quantity. Both are published constants,
drawn at a height that the chart's own percent axis gives meaning to. `core/`
computes neither of them. No governing equation reads MAC-awake, just as none
reads `mac_percent`.

**Why two rather than one.** Chortkoff et al. state that "along with
pharmacokinetics, the ratio of the awakening concentration to the
anesthetizing concentration (MAC-awake/MAC) determines time to awakening".
When both references are drawn, that ratio becomes the visible gap between
them. The chart then shows the *decrement required for arousal*, not only the
endpoint. That is what lets a reader compare a twenty-minute case and a
three-hour case side by side. It is the lesson of context-sensitive emergence,
stated as geometry.

**The mark type carries the distinction, not the colour.** The two references
differ in epistemic status, and their marks say so. MAC-awake is a measured
population value with real spread, so it is drawn as a band. 1 MAC is a
definitional anchor, not a distribution of the same kind, so it is drawn as a
line. The difference between a band and a line survives greyscale and every
colour-vision deficiency. § "Color contrast" below requires that of any
encoding that carries meaning. It is also a stronger separation than any pair
of colours. Both references are drawn in the interface's own ink and label
colours rather than in a seventh and eighth hue. That way, neither is mistaken
for another compartment.

**The band's geometry, and why it is two strokes rather than a thicker mark.**
The band is drawn as a stroke on each of its two boundaries, with a light fill
between them. Both strokes sit on the published values, so the drawn extent
equals the data extent exactly. Nothing pads the band outward. A band drawn
thicker than one standard deviation would assert a wider population spread
than the sources support. That would be a claim about the evidence, not a
styling choice. So a minimum drawn height is specifically excluded, whatever
it would do for legibility.

The second stroke is necessary because no axis range can provide the
separation. On the fixed `CHART_AXIS_TOP_MAC` range, the band spans 3.33% of
the plot height for sevoflurane and 4.20% for desflurane. No ceiling that this
chart can take changes that. At 2 MAC the band is unambiguous, but the 1 MAC
anchor sits at mid-plot. That leaves no room above it for the overpressure
induction that the chart has to be able to show. At 4 MAC the band is back to
the 2.50% it had on the dial-maximum axis that this one replaced. Suppose a
mark is stroked on its upper edge only, over an unstroked fill. It then has the
geometry of a line with a shadow beneath it, however wide the fill is. That
geometry is what made this band look like a line. It would have collapsed the
band-versus-line distinction above into no distinction at all. Two strokes
with a gap between them have the geometry of an interval. They remain an
interval at any thickness the axis leaves. So what a reader sees between the
two rules is the population spread, not a decoration around a threshold.

<!-- derived: 3.33 percent from data/agents/sevoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- derived: 4.20 percent from data/agents/desflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.063 -->

**What the band asserts.** MAC-awake is the concentration at which half of a
population responds to verbal command. That is a *different endpoint* from
MAC, which is immobility in response to a standardized surgical incision. The
label says which endpoint the band shows. The band extends one standard
deviation either side of the published mean. It therefore spans roughly the
middle two thirds of a population, not its full range.

**What the band does not assert, and what the interface therefore never
shows.** The band is not a prediction for the patient on the screen. The
interface displays no time-to-wake-up figure of any kind. A readout of the
form "time to wake-up: 14 min" would be taken as a per-patient prediction,
which this model does not support. No surrounding disclaimer undoes that,
because the number would be acted on and the disclaimer would not. A band is
the strongest claim that the evidence supports, which is why the reference
takes that form.

**Which trace the band is read against, and why that is the load-bearing
part.** The band must be read against the **vessel-rich** trace. This model
has no effect-site compartment and defines $`F_a \equiv F_A`$ (see § "Model
boundary"). So the alveolar trace is the fastest curve on the chart, and the
furthest from where responsiveness actually returns. One measurement shows
the size of the gap. It ran sevoflurane for 3 hours at the opening dial of
2.0%, which is the stored 1 MAC, and the default fresh gas flow of 4 L/min.
That brought the alveolar fraction only to 1.69%, or 0.84 MAC. The vaporizer
was then turned off and the fresh gas flow raised to 10 L/min. The alveolar
trace crosses the band's centre at 2.86 min, and the vessel-rich trace crosses
it at 6.55 min, 2.29 times later. These figures were measured on 2026-10-26
with `AgentUptakeSystem.for_agent("sevoflurane")` at 0.1 s steps (`PL-39KH`).
They were measured again on 2026-10-31, with each crossing time interpolated
between the two steps on either side of it (`PL-PTDZ`). That second run
corrected one figure below, from 7.31 to 7.30 min.
`tests/reference/test_mac_awake_washout_figures.py` reads this protocol and
its figures from this section, runs the protocol, and holds each figure to the
places printed. So a parameter change that moves a figure fails the test, and
so does an edit here that changes the protocol or a figure on its own.
<!-- not-restated: 10 L/min -->
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->

<!-- derived: 2.86 min from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->

The primary literature makes this a question of *which number is correct*,
not only of how a number is read. Katoh et al. determined sevoflurane and
isoflurane MAC-awake by two methods, a slow, equilibrated washout and a fast
one. The two methods disagree. Slow washout gave 0.34 and 0.31 of MAC for
sevoflurane and isoflurane respectively, against 0.22 for both by fast
washout. The paper attributes the difference to end-tidal-to-arterial and
arterial-to-cerebral anesthetic differences. That is precisely what this model
represents as the alveolar-to-vessel-rich difference. The paper also
estimates the brain concentration at awakening. That estimate is not a
measurement, because cerebral concentration cannot be sampled in these
patients. The abstract says the brain concentrations were "calculated with
end-tidal anesthetic concentrations", and the title calls them "predicted".
So they come from Katoh's own model of brain uptake (`PL-YDRT`). That model
treats the brain as one well-mixed compartment perfused by arterial blood. Its
equation 1 (p. 1013) is:
<!-- provenance: data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34 -->
<!-- provenance: data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31 -->

$$
\frac{dP_{Brain}}{dt} = \frac{CBF \cdot \lambda_{B/G} \cdot (P_{Art} - P_{Brain})}{V_{Brain} \cdot \lambda_{T/G}}
$$

This is the perfusion-limited form that § "Tissue uptake and return" uses for
each tissue group. Katoh's compartment is the brain alone, though, while this
model's vessel-rich group pools the brain with the heart, liver, kidney and
viscera. Every patient was given the same rules for the flow and the volume.
Cerebral blood flow $`CBF`$ is 14.3% of a cardiac output set by a cardiac
index of 3.5 L/min/m², so it scales with body surface area. Brain volume
$`V_{Brain}`$ is 21 mL/kg, so it scales with body weight. The brain's time
constant therefore varied a little from patient to patient. The coefficients
were the same for everyone. The blood:gas coefficient $`\lambda_{B/G}`$ is
0.63 for sevoflurane and 1.36 for isoflurane, and the brain:gas coefficient
$`\lambda_{T/G}`$ is 1.15 and 2.09.
The arterial partial pressure was not measured. Katoh's equation 2 sets it
equal to the end-tidal value. Equation 3 (p. 1016) corrects the end-tidal
value for 20% dead-space gas, as $`P_{Art} = (P_{ET} - 0.2\,P_I)/0.8`$. The
two give different answers. During fast washout, the calculated cerebral
concentration at first eye opening was 0.30 of MAC for sevoflurane and 0.26
for isoflurane under equation 2 (Table 1, p. 1014). Under equation 3 it was
0.34 and 0.30 (Table 3, p. 1016). The abstract quotes the equation 3 figures,
"nearly equal to MAC-Awake obtained by slow alveolar washout". Neither set
differs significantly from the slow-washout values. The stored values are
therefore the slow-washout ones, and the trace they belong against is the
vessel-rich one. That rests on a modelled estimate agreeing with an
equilibrated measurement, which is weaker evidence than a direct measurement
of the brain would be.

<!-- not-restated: 0.34 -->

**Three ways of misreading the band run in the same direction, and it is the
consequential one.** Concentration falls during emergence. So a trace crosses
a higher reference sooner, and a faster-falling trace crosses any reference
sooner. Three distinct reading errors therefore all shorten the apparent time
to awakening. The first is reading the band against the alveolar trace instead
of the vessel-rich one. The second is drawing the slow-washout value against a
fast-washout alveolar trace, where 0.22 would be the matching figure. The
third is the denominator mistake described below. A learner who takes away
any of these errors concludes that emergence is faster than this model says.
That learner carries into practice the belief that a patient is more awake
than they are. That is why this document specifies the reference, rather than
leaving it to the chart.

**The band's height has a fourth source of error, and its direction differs
by agent** (`PL-GCGX`). The band is the stored fraction times the stored
`mac_percent`, which is the Gas Man flat adult MAC. The traces are absolute
partial pressures and do not depend on that divisor. So wherever the divisor
departs from the literature, the band moves against the traces by the same
proportion. § "Delivery-limit and MAC parameters" compares the stored MAC with
Mapleson's age-40 values. Against them, the stored MAC is 11.1% high for
sevoflurane, 2.6% high for isoflurane and 9.1% low for desflurane. Mapleson's 95%
confidence limits are about ±7%, and ±10% for desflurane. Only sevoflurane's
gap is larger than its limits. So the sevoflurane band probably sits too high,
by about 11% if Mapleson is right, and a band drawn too high teaches an earlier
wake-up. On the measurement above, the vessel-rich trace crosses sevoflurane's
drawn band centre of 0.68% at 6.55 min. It crosses 0.612%, the same fraction of
Mapleson's 1.80%, at 7.30 min. The isoflurane and desflurane gaps are inside
the limits, so Mapleson does not show either band to be off. For desflurane a
direct measurement points the same way. The drawn centre of 2.16% agrees with
Song et al.'s measured 2.17%, as the paragraph below says. All three figures
are gaps from Mapleson's MAC, not from the MAC each source used.
<!-- derived: 0.68 percent from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->
<!-- derived: 2.16 percent from data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36, mac_percent = 6 -->

Katoh's own denominator is each patient's age-adjusted MAC, from two linear
equations on p. 1013. For isoflurane it is 1.43 − 0.0061 × age (yr) percent,
and for sevoflurane 2.56 − 0.0156 × age (yr) percent. The paper cites four MAC
studies for them and does not say how the equations were derived from those
studies. At age 40 the equations give 1.94% for sevoflurane and 1.19% for
isoflurane. At that age the stored MAC is 3.3% above Katoh's for sevoflurane
and 1.2% above it for isoflurane. The band is the stored fraction times the
stored MAC, so it sits above Katoh's own age-40 awakening concentration by
the same proportions. The drawn centres are 0.68% sevoflurane and 0.372%
isoflurane, where Katoh's fractions times Katoh's age-40 MAC give 0.658% and
0.368%. Both differences are much less than the 0.05 of MAC standard
deviation of Katoh's fractions. Katoh's slow-washout patients themselves woke
at a mean end-tidal 0.63 ± 0.11% sevoflurane and 0.36 ± 0.08% isoflurane
(Table 1, p. 1014). Those figures are lower than the band mostly because the
patients were older, with mean ages of 45.9 and 45.1 years. So they are not a
like-for-like check of a band drawn for age 40. The age-40 comparison points
the same way as the Mapleson one: the band sits slightly high, so it teaches a
slightly early wake-up (`PL-P319`).
<!-- not-restated: 0.36 -->
<!-- provenance: data/agents/sevoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- provenance: data/agents/isoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- derived: 3.3% from data/agents/sevoflurane.json mac_percent = 2 -->
<!-- derived: 1.2% from data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- derived: 0.68 percent from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->
<!-- derived: 0.372 percent from data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31, mac_percent = 1.2 -->

**The value is stored as a fraction of MAC, never as a percent of one
atmosphere, and that is a safety decision rather than a schema preference.**
Each source expresses MAC-awake as a ratio to MAC. Katoh does so explicitly,
"as a ratio to age-adjusted MAC". A published *percent*, by contrast, is
anchored to whichever MAC its own population was measured against. Desflurane
is the worked example. Chortkoff's MAC-awake of 2.60% is 36% of a MAC of about
7.25%, which is Rampil's 18-30 year figure. This project stores Rampil's 31-65
year figure of 6.0% instead. Dividing the absolute percent by the stored MAC
would give 0.433 rather than the published 0.36. That is 20% high, so the band
would be drawn 20% too high and crossed too soon. Storing the fraction removes
the trap outright. It also stays correct if `mac_percent` is ever changed or
made age-aware.

<!-- derived: 0.433 from data/agents/desflurane.json mac_percent = 6, mac_awake.fraction_of_mac = 0.36 -->

A fraction with no stated denominator is the correct number in the wrong
context. So each agent's `mac_awake.mac_reference_basis` records the MAC that
its fraction was derived against. The interface states the divisor that the
fraction is multiplied by. Applying the fraction to this project's own
`mac_percent` keeps the band and the axis consistent by construction. For
desflurane, it also gives an independent cross-check. 0.36 of the stored 6.0%
is 2.16%. Song et al. measured 2.17% in the non-jaundiced control arm of a
population that the 31-65 year divisor describes.

<!-- derived: 2.16 percent from data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36, mac_percent = 6 -->

**The 1 MAC line is the nominal value, not the dialled one.** A fixed
reference stays comparable across runs. That is what lets a reader compare two
cases of different length side by side. A line that tracked the concentration
the learner happened to dial would only restate where the trace already
starts. The line is the flat adult `mac_percent`. It is labelled as a
reference adult value, not as a patient-specific one. The reason is that this
model has no age parameter, while Katoh expressed MAC-awake as a ratio to
age-adjusted MAC.

One consequence is expected and is not a rendering fault. At a 1 MAC dial, no
patient trace reaches the 1 MAC line, however long the case runs. Muscle and
fat keep taking up agent for many hours, so the blood returning to the lungs
stays below the alveolar gas. That keeps the alveolar fraction below the
inspired fraction, and rebreathing keeps the inspired fraction below the dial
(`PL-39KH`). The measurement above shows the size: after 3 hours at 1 MAC the
alveolar and vessel-rich traces stood at 0.84 MAC. That is true of the
patient, and it is worth teaching.

**What the references inherit, and one methodological limitation.** The
fractions are tier 1, from primary measurements in humans. `mac_percent` is
tier 3. So the *absolute height* of both references inherits every limitation
that "Delivery-limit and MAC parameters" records for the divisor. The
interface displays that divisor, so a reader who disagrees with it can see
that they do. Separately, the three fractions were not determined by one
method. Katoh's slow-washout arm is *descending*. Chortkoff and Song both
determined desflurane MAC-awake by *ascending* stepwise equilibration. All
three are equilibrated determinations rather than fast-washout ones, which is
why all three belong against the vessel-rich trace. But ascending and
descending determinations are not interchangeable, and no descending-washout
desflurane MAC-awake was found. The three fractions (0.31 isoflurane, 0.34
sevoflurane, 0.36 desflurane) sit in a narrow range, so each agent carries its
own value rather than one fraction covering all three.
<!-- provenance: data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31 -->
<!-- provenance: data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34 -->

<!-- provenance: data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36 -->

### The control-input timeline

**What it is.** The timeline is a record of the settings that a run was
given. It is kept with the run and cleared with it. Each entry is one change
that the model actually ran under. The entry gives the simulated time at which
the change took effect, the user adjustment it belongs to, and the control. It
also gives the values before and after, and the unit that both values are in.

**Why the model needs one at all.** A curve without its inputs is not a
result that anybody can check. The exercises that this simulator exists to
support all take the form "change one thing and look at what happened".
Examples are overpressuring and then dialling back, dropping the flow, and
halving the cardiac output. A learner who cannot see where they dialled back cannot read
their own experiment. The stronger requirement is reconstruction. The recorded
timeline, re-applied to a fresh run at the recorded times, must reproduce the
run that it describes. Reconstruction is what makes a recorded run a result
rather than a picture of one, and the design decisions below exist to provide
it.

**Recorded values are the model's, not the interface's.** Each value is read
back from the compartment that holds it, after the core has accepted it. It is
stored in the unit that the core uses. So the delivered dial is stored as the
percent of one atmosphere it was set to, which is the percent the core is set
with (`PL-NJPB`). It is displayed through `format_percent`, the formatter
that every other concentration on the page goes through. That formatter takes
the model's fraction, so the recorded percent is converted to a fraction on its
way in and back to a percent for display. A record
of what was *asked for*, rather than of what took effect, would diverge from
the run the first time the two differed. The core rejects an out-of-range
setting rather than clamping it precisely so that the two cannot differ
silently.

**A refused setting is not recorded**, because it never took effect. The
recording happens after the core's setter returns. So this rule follows from
the structure of the code, rather than from a check that someone could forget.

**Only what the model saw is recorded.** A setting equal to the one already
in place is not a change. Nor is a setting that is replaced before the next
simulation step. Only the value in place when a step runs is integrated. So a
control moved twice between two steps is one change, from the first value to
the last. A control moved and moved back within one step is no change at all.
Recording the intermediate values would describe a run that did not happen.
Without this collapse, the timeline would record the input device rather than
the simulation.

**What a displayed adjustment is, and why it is not the same object.** A
slider reports its value continuously while it is dragged. So one turn of one
control arrives at the model as a series of settings. The run really was
computed under each of them, and all of them are one act by the person. The
record keeps every setting, because reconstruction needs them. The display
groups them into adjustments, because a reader needs to see the act. The
grouping is exact rather than inferred. The interface declares where an
adjustment begins, at the moment a drag starts, and every change carries the
number it was assigned. Nothing infers a gesture from the spacing of the
entries, and nothing may. A playback multiplier changes how much simulated
time one drag spans, so any threshold would group correctly at one rate and
wrongly at another. A change that arrives with no adjustment declared becomes
an adjustment of its own. Examples are a keyboard press on a slider and a
programmatic call. Treating such a change as its own adjustment is the honest
reading of a discrete input.

A displayed adjustment states the interval it spans. It also states how many
settings the model was stepped under during that interval. The count is
displayed rather than hidden because an adjustment made over eight settings is
not the same run as one made in a single step, even where the endpoints match.

**What it asserts, and what it does not.** A timeline entry asserts that the
named control moved between the stated values over the stated simulated
interval. It says nothing about the patient. It is a record of an *input*,
never of a measurement or of a modelled quantity. That is why the chart's
marks are labelled as inputs, and why the list beside them says so
explicitly. Otherwise a vertical rule on a chart of patient concentrations invites
the reader to see an event in the curves.

**Stability of the recorded identifiers.** Each control is recorded under a
fixed string chosen from the domain: `fresh_gas_flow`, `delivered`,
`alveolar_ventilation` and `cardiac_output`. The string is not taken from the
name of the accessor that applies the setting. An identifier taken from the
code would make the vocabulary of every already-recorded run obsolete the next
time the code was renamed. A fifth string, `circuit_volume`, was recorded here
until the circuit volume was established as a fixed model parameter rather
than a control (§ "What is not bounded this way"). Retiring it cost no
already-recorded timeline, because a timeline is held in memory and cleared
with its run rather than persisted.

**Bounds are displayed, not silent.** The chart carries a fixed number of
marks, and the list carries a fixed number of lines. So a run may record more
adjustments than either can show. The display counts what it does not show. A
chart that quietly stops annotating, or a list that quietly ends, states that
nothing else happened. Each chart counts its own unmarked changes and says so
on itself, because each chart has a window of its own
(§ "The chart's time base").

**The record itself carries no ceiling, and that is a decision rather than
an omission.** The two bounds above limit only what is *shown*. Dropping the
oldest entries would remove the beginning of a case. That is the part a
learner returns to, since "where did I dial back?" is the question this record
exists to answer. Dropping them would also bound nothing, because the run
definition of § "The run is that record, and every state is derived from it"
above holds one stretch and one keyframe per accepted change, and that
definition is not bounded either. Capping only the display record would give up the reconstruction claim
above, while the larger structure kept growing.

What makes that affordable is that the record grows with the time spent
*changing settings*, not with the length of the run. Only the value in place
when a step runs is recorded. So a drag adds at most one entry per simulation
step, however fast the slider reports. That rate is a property of the tick
rather than of simulated time, so it is the same at every playback multiplier.
Measured on 2026-09-14 under `PL-1PSX`, continuous dragging gave ten entries
per real second at 1×, 5×, 20×, 60× and 300× alike. A drag made while the run
is paused gave one entry. The grouping behind the display costs 0.9 ms per
frame at a thousand entries and 8.8 ms at ten thousand, against a 200 ms
frame. It is recomputed only when the record changes. It would cost half a
frame at a hundred thousand entries. Reaching that many takes about three
hours of unbroken dragging, and at that point the record is smaller than
9 MB.
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

### F_A/F_I as a displayed ratio

**What it is.** It is a second plot under the compartment chart, on the same
time window. It draws $`F_A/F_I`$, the modelled alveolar fraction divided by
the modelled inspired fraction, on a dimensionless axis fixed from 0 to 1. It
is a *displayed* quantity. `core/` computes it nowhere, no governing equation
reads it, and it is no part of the run's definition. `app/wash_in.py` is the
code in which this section ends, in the same way that `app/formatting.py` is
the code in which "Displayed precision" ends. `app/wash_in.py` holds the
arithmetic and the domain, and nothing else. `tests/unit/test_wash_in.py` pins
both.

**Why the interface owes it.** The uptake literature is taught from this
curve, and every wash-in figure a reader has seen is drawn as this curve. It
is also the quantity on which this model has been compared against human
measurement. The section "Published wash-in and elimination validation test"
checks $`F_A/F_I`$ at 30 minutes for all three shipped agents. So the trace
and the validation are the same number.
`test_the_displayed_ratio_is_the_quantity_this_file_validates` asserts this,
rather than leaving it to inspection. Six absolute concentrations cannot be
laid beside a published figure, but this ratio can.

**The denominator is the modelled inspired concentration, not the vaporizer
dial.** The inspired fraction here is the breathing circuit's own. That is an
assumption of this circuit model rather than a general fact (see § "Model
boundary"). The distinction from the dial is not pedantic. The circuit
approaches the delivered concentration only over its own time constant. So
early in a run the two differ substantially, and dividing by the dial would
understate the ratio for as long as the difference lasted. The interface
states which one it uses at the point of display.

**The curve is the textbook wash-in curve only while the inspired
concentration is held constant.** If the vaporizer or the fresh gas flow moves
mid-run, $`F_A/F_I`$ remains a well-defined ratio of two modelled states. But
it stops being a wash-in fraction of anything a reader can name. A rise across
such a change is the setting moving, not uptake slowing. The control marks of
"The control-input timeline" are drawn on this plot as well as on the
compartment chart above it. Both sets of marks are drawn in the same pass over
the same adjustments. So the plot that could be misread is the plot that
carries the annotation.

**The plotted domain, and why it has two boundaries.** A drawn column
contributes a point only where both of these conditions are true:

1. $`F_I \geq 10^{-4}`$, one displayed unit of concentration. $`F_I`$ is
   exactly zero before any agent reaches the circuit. That is true at the
   start of every run, and throughout a run whose vaporizer is never opened.
   There the quotient is $`0/0`$. This lower limit is derived from
   `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` rather than chosen beside it. So
   the ratio is never formed from a denominator that the interface itself
   renders as `0.00%`.
2. $`F_A/F_I \leq 1`$. The condition $`F_A \leq F_I`$ is exactly the uptake
   regime. Alveolar gas gives up agent to blood, so the alveolar fraction
   stays below the inspired one and reaches it only at equilibrium. Above 1,
   the tissues are returning agent faster than it is being delivered. That is
   elimination, not wash-in. Equilibrium is drawn on the chart as a labelled
   reference line.

   The comparison allows `WASH_IN_ROUNDING_ALLOWANCE`, 1e-6, above 1 for
   rounding (`PL-N559`). At zero cardiac output the exact solution has
   $`F_A`$ rise to $`F_I`$ and stop. The stepped run instead settles onto a
   floating-point fixed point within about 1e-13 of that, and in some runs
   the fixed point has $`F_A`$ above $`F_I`$. Isoflurane at a fresh gas flow of
   10 L/min settles
   at 1 + 2.2e-14, which the plot once captioned as the patient returning
   agent. Once a run reaches its fixed point, every later step returns the
   same state, so the overshoot does not grow with run length. On 2026-10-26
   it was the same at 96 h as at 1 h.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

   The value comes from a clinical requirement rather than from the rounding
   (project owner, 2026-10-26, ratified, over 1e-9 sized from the rounding
   and over deriving the value in code). A whole run of the longest supported
   length, held at a quotient of 1 + 1e-6, must lose less than 1% of the
   agent in the fast pool: alveolar gas, venous blood and the vessel-rich
   group. Agent then leaves at alveolar ventilation times $`F_I`$ times
   1e-6, and the concentration cancels against the pool. The worst case is
   desflurane at an alveolar ventilation of 12 L/min, which loses about 0.3%
   in 24 h.
   `test_the_rounding_allowance_hides_no_clinical_change_over_a_whole_run`
   checks this for every shipped agent from the run-length limit, the
   ventilation limit and the data files, so extending any of them fails it.
   The allowance is also about 10 million times the largest overshoot
   measured, 9.6e-14.
   `test_a_zero_cardiac_output_steady_state_is_not_read_as_elimination`
   checks the fixed point against the closed form for each shipped agent.
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

Outside either boundary nothing is drawn. The value is not clamped to the
axis, not interpolated across, and not replaced by a default. A ratio pinned
to 1.0 would draw a completed wash-in that the run never reached. A line
joining the wash-in on either side of a washout would draw values that the run
never produced. So the trace is a set of segments rather than one polyline,
and it breaks where the domain does.

**One point past the boundary, so the ending is legible.** Each stretch is
extended at each end by its *crossing* column. The crossing column is the
neighbouring drawn column that has a ratio but sits outside the domain.
Without it, the curve stops at the last column at or below equilibrium. That
column can sit a whole column spacing's rise below the equilibrium line that
the curve stopped short of. A trace that halts in clear space short of a
boundary looks exactly like one that the frame cut off. This trace is still
climbing steeply when it stops. With the crossing column drawn, the trace
meets the equilibrium reference and ends on it. It carries a point marker that
says the series ended rather than ran out of view. The stretches are
classified over the columns that each frame draws, rather than maintained as
the run goes. So a boundary can fall only on an instant that the chart
actually plots (`app/chart_frame.py`, PL-2FM6).

That extension is bounded by a stated ceiling, not by a property of the
model. A run stepped at 0.1 s crosses equilibrium by only a hair. This was
measured across every shipped agent and every supported alveolar ventilation
and cardiac output, at the maximum fresh gas flow. The first stepped state
above equilibrium reaches 1.00235. But the ratio is not continuous in general.
`BreathingCircuit.set_circuit_volume` conserves the agent in the circuit while
it changes the volume that the agent is divided by. So a circuit volume
doubled between two steps halves $`F_I`$ and doubles the ratio. No interface
control does that today. A rule that holds only because a slider is absent is
not one to build on. So a crossing column above the ceiling is not drawn at
all, and the stretch ends where it would have ended without it. The stretch is
not clamped onto the ceiling and not interpolated onto it.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**The crossing column is drawn, but its number is not printed as wash-in.**
Its quotient is above 1, so it is elimination rather than a wash-in fraction.
The chart's hover at that column says "Past equilibrium: not a wash-in
fraction" under the wash-in label instead of printing the quotient
(`WASH_IN_HOVER_PAST_EQUILIBRIUM_TEXT` in `app/chart_frame.py`, `PL-YH6Z`).
Printed there, a value such as 1.03 would teach a wash-in past completion, at
the dot a reader is most likely to point at.

**A blank stretch says which boundary it is.** "No agent has reached the
circuit yet" and "the patient is returning agent" are opposite situations. A
reader shown only an absent trace cannot tell which of the two applies. The
line beside the plot names the case. Where the trace is drawing, that line
also gives the value at which the trace's right-hand end sits. One evaluation
of one rule produces both, so the sentence and the curve cannot disagree.

**Why the axis is fixed rather than fitted, and why it does not stop at 1.**
0 to 1 is the scale of every published wash-in figure, and matching those
figures is the point of drawing this curve at all. So the ruling and the
labels stop at 1. The axis itself extends a little above 1. That headroom is
required for legibility, and it is not a margin. If the axis topped out at
equilibrium, the trace's ending would land on the frame. There, a line that
stopped and a line that the plot cut off look exactly alike. The top of the
frame is deliberately unlabelled. So the readable scale remains 0 to 1, and
the space above it is not taken as a range the ratio can reach. An axis that
instead grew to fit the elimination excursion would redraw the wash-in curve
at a smaller height partway through a lesson. A reader would attribute that
change of shape to the model rather than to the axis. Such an axis would also
have no stable height to grow to. During elimination the circuit is fed by
agent-free fresh gas and by rebreathed alveolar gas. So the ratio settles near
$`1 + \dot V_{\mathrm{FGF}} / \dot V_A`$, which the supported input ranges do
not bound. This was measured on sevoflurane, by closing the vaporizer at
10 L/min after a 30-minute wash-in. The ratio was 3.47 at the reference
adult's 4.0 L/min of alveolar ventilation, 1.83 at 12.0, 5.93 at 2.0 and 20.11
at 0.5. The predictions were 3.50, 1.83, 6.00 and 21.00. Values above 1 are
excluded because they are not wash-in fractions. That they are also unbounded
is why no fitted axis would help.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4.0 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

**Displayed precision.** The ratio is shown to two decimals. This figure is
deliberately *not* derived from the concentration resolution. The quotient's
own resolution depends on its denominator. So a run early in wash-in knows the
ratio far less finely than a run at equilibrium, and a single derived figure
would over-claim at one end. The figure is set instead by what the quantity is
compared against. Yasuda et al. report 0.850, 0.733 and 0.90, with standard
deviations of 0.018, 0.027 and 0.01. So a third decimal would be finer than
the published spread. See
§ "Published wash-in and elimination validation test".

**What it does not assert.** The ratio is a modelled ratio, not a
measurement. It carries the alveolar compartment's own limitation: this model
has no airway sampling delay and no dead space. And it is not a depth of
anesthesia, a time to any endpoint, or a prediction for an individual patient.

### Color contrast, and the standard this interface is held to

**The target is WCAG 2.2 Level AA.** In two places this project deliberately
holds itself to a higher bar, and it explicitly defers a set of criteria. WCAG
2.2 is the current W3C Recommendation (published 2023-10-05). WCAG 3.0 is a
Working Draft whose scoring model replaces pass/fail entirely, and this
interface is not designed against it. Conforming to 2.2 AA also satisfies the
2.1 AA that EN 301 549 and the 2024 ADA Title II rule reference, and the 2.0
AA that Section 508 references. None of those instruments applies to this
project, though. AA is chosen because it is the right engineering bar for a
teaching tool, not because the project is obliged to comply.
<!-- not-restated: 2.1 -->

Two criteria carry most of the weight:

- **SC 1.4.3, Contrast (Minimum)**, requires 4.5:1 for text. Every readout,
  every label naming a readout, and every agent name over its identification
  color is held to this minimum. The project claims the large-text exception
  (18pt, or 14pt bold) nowhere. The interface's default text size is 14px, so
  bold status text is judged at 4.5:1 like everything else. The larger readout
  values are held to the same 4.5:1.

  **Text is measured against the surface it is actually drawn on, and there are
  two such surfaces.** The run-status word, the halted-run notice and the
  educational-use disclaimer sit in the top-level column, so the page
  background shows through behind them. The readouts, their labels, the axis
  description and the accounting lines sit inside panels. The page background
  is the darker of the two. So wherever a color appears on both, the page
  background is the stricter test and the one that counts. Assuming that the
  panel was the surface is what hid the shortfall that `PL-X0RG` fixed. The
  label color measured 4.28:1 on the panel and 3.98:1 on the page, and only the
  second is what a reader of the run-status word actually sees.
- **SC 1.4.11, Non-text Contrast**, requires 3:1 for graphical objects. Here
  that means each chart trace against the panel it is drawn on, and each agent
  swatch treated as a shape. It also means the active track of each parameter
  slider, which is how a control shows where its value sits in its range.

<!-- not-restated: 4.5 -->

**A color that carries meaning both as text and as a graphic needs two values,
not one.** The two minima differ by half again, so a single constant that
serves both roles fails one of them. This interface has one such case. It is
recorded here because the constant's name does not make the roles obvious.
`ACCENT` is the graphical one, used for the sliders' active track.
`ACCENT_TEXT` is the same hue darkened until it is legible as text. It carries
the affirmative status words "Running" and "Valid", whose counterpart is the
warning color. Telling a running run from a halted run is safety-critical for
the reason given above. So the word that announces the state is held to the
text minimum on the surface it is actually drawn on. The color is also never
the only cue. The words themselves differ, so a reader who cannot tell the
colors apart still reads the state.

Held **above** AA in two places:

- **Color is never the sole channel.** SC 1.4.1 (Level A) requires this, but
  the reason here is stronger than the criterion. ISO 5360 Table 2 footnote b
  makes displaying a color an obligation to display the *correct* one. So a
  second cue is what keeps a mis-seen color from becoming a mis-identified
  agent. The agent name always accompanies the color. The chart's traces
  require a non-color channel for the reason given in the next bullet.
- **Chart traces are held to pairwise separation, which WCAG does not cover.**
  SC 1.4.11 asks only for 3:1 against the *background*. It says nothing about
  how far apart two adjacent series must be, yet reading one compartment
  against another is the whole lesson of this chart. **Confirmed against the
  source on 2026-09-07** (`PL-JX0Z`). The project owner supplied the
  Understanding document after the egress proxy refused five routes to it.
  Its line-graph example (Figure 38) is explicit: *"The lines should have 3:1
  contrast against their background, but as there is little overlap with other
  lines they do not need to contrast with each other or the graduated lines."*
  Its "Graphical Objects" section makes each line in a graph a graphical object
  in its own right. It also allows the Gestalt "law of continuity" to ignore
  **minor** overlaps between them. Note the condition that both carve-outs
  depend on: an absence of overlap. This chart does not meet it. Six traces
  start together, converge toward equilibrium and cross through wash-in and
  washout. So this chart does not qualify for the exemption that would excuse
  pairwise separation. That makes the bar below a supported exceedance rather
  than an arbitrary strictness. It is also why `tools/contrast_check.py`
  reports the pairwise matrix without failing on it, while it enforces the
  3:1 minimum against the panel that the criterion does require.

  This bar cannot be met by luminance differences. Contrast ratios compose
  along a bounded axis, since black to white is 21:1. Sort $`n`$ traces by
  luminance, and the smallest adjacent gap is largest when the gaps are equal.
  So no arrangement of six traces gives every pair more than
  $`21^{1/5}\approx1.84`$. The requirement in the next bullet tightens this
  further, to 1.48. Both values are less than SC 1.4.11's 3:1. So a redundant
  non-color channel (line style or marker) is a **requirement** for this chart
  rather than an embellishment, and no palette choice can remove it. The next
  section describes how that requirement is met.
- **Each chart trace clears 3:1 against the panel, both as displayed and under
  simulated dichromacy.** SC 1.4.11 is defined on the color the display emits,
  so this is the project's bar rather than the criterion's. The reason for it
  is the criterion's *purpose*: that a graphical object be findable against its
  background. Measuring one observer does not serve that purpose. This is not a
  hypothetical strictness. The muscle trace passed at 3.19:1 as displayed and
  failed at 2.98:1 when simulated for deuteranopia. No normal-vision check
  could have seen that shortfall.

**Deferred, and named so that the deferral is visible** rather than silently
unlisted: SC 2.4.11 (Focus Not Obscured), 2.5.8 (Target Size), 1.4.10 (Reflow)
and 1.4.12 (Text Spacing). Each needs a settled interface before it can be
assessed. What the rendering backend can deliver for keyboard and
screen-reader support is an open question rather than a commitment.

**Exempt from SC 1.4.11, and recorded as such rather than left unasked**: the
gridline grey, `GRIDLINE`, in all four things it draws. These are the plot's
ruling, the axis lines, the rule between sections of the chart column and the
sliders' unfilled groove (project owner, 2026-09-27, ratified, over darkening
the grey to 3:1; `PL-HKTB`). The grey measures 1.31:1 on the panel. The
criterion applies only to a graphical object *required to understand the
content*. The Understanding document's line-graph example does count a chart's
"background lines for the values" as graphical objects, and it asks 3:1 of
them. But in that example the rulings are how a value is perceived at all.
The document states what lifts the requirement under its
"Required for understanding" heading. There, the requirement does not apply
when "a graphic with text embedded or overlaid conveys the same information,
such as labels and values on a chart". This chart has three such carriers of the same
information. Every ruling stands at a tick that the axis labels as text at
5.00:1. The readouts state every compartment's current value. The hover states
the exact value at any drawn point. So the chart passes the criterion's own
test: assume the area is invisible, and ask whether the graphic is still
understood. The section rule sits over a bold heading or a titled panel that
already marks the boundary. The groove is the edge of a control whose handle
and filled track already identify it. The criterion's own paragraph on
boundaries excuses these cases in terms. Darkening was refused because of the
chart's hierarchy, not because of the criterion. A ruling at 3:1 would be 87%
as dark as the lightest trace (3.43:1). It would collapse the visual ordering
in which a ruling sits below a reference line, which sits below a trace. The
line widths of 1 / 1.5 / 2-3 px also carry that ordering. The record is the
`EXEMPT` table in `tools/contrast_check.py`. It has one entry per use, which
gives the criterion's grounds and cites the drawing code by symbol.
`make check` counts the uses into the contrast report line. It refuses an
exempt name that the palette does not hold. It also refuses a colour that is
both required and exempt on one surface, so nothing is held to the criterion
and excused from it at the same time. An exemption is not a shortfall. A
shortfall is a pair that should meet a minimum and does not. The bar for
entering the exemption table is the criterion's own carve-out, never a failing
ratio.

**The ratios are computed, not asserted.** `tools/contrast_check.py` runs in
`make check`. It reads the color constants out of `app/theme.py`, which has
contained every one of them since `PL-2CS8`.
`check_colors_live_in_the_theme` requires them to stay there. The tool holds
each declared requirement to its declared minimum. It uses WCAG 2.2's own
definitions of relative luminance and contrast ratio. Its requirement table
names the colors, the criterion, and the reason they are held to that number.
The judgment of *which* colors matter stays in that table, and the tool only
evaluates it. Most entries are one foreground against one background. Some
elements have an edge that either of two channels can carry. Such an element
declares both channels and is held to the better of them. Each agent
identification badge is that case: a fill outlined in the agent's own text
color. The badge is perceivable by whichever of the two clears the minimum, so
measuring one channel at a time misreports it. Requirements that do not meet
their minimum today are listed in the table, each against the item that closes
it. A listed shortfall that starts passing is reported as an error, so a fix
cannot leave its excuse behind. A colour that the criterion does not apply to
is recorded in the same file's exemption table, not as a requirement or a
shortfall. The paragraph above records the gridline grey that way.

**A declared colour reaches the screen by one of three mechanisms.** Most of
this interface is drawn by a stylesheet composed from `app/theme.py`'s
constants. Those constants are what `tools/contrast_check.py` reads. Every one
of those stylesheets is composed in `app/stylesheets.py` (`PL-Y4YX`). Some
widgets cannot be drawn that way. An entry's fill, a spin box's stepper, a
list's rows and its scroll bar, a check box's indicator and a dialog's own
surface are painted from Qt palette roles. Styling them with a stylesheet
instead costs the native stepper and the check box's tick. For those widgets,
`qt_widgets.declare_interface_colours` declares the same theme colours as
palette roles. PANEL and INK become `Base` and `Text`, MUTED becomes
`PlaceholderText`, and PRIMARY and PANEL become `Highlight` and
`HighlightedText`. So the pairs on screen are pairs that the requirement table
already measures. The function writes only the `Active` and `Inactive` colour
groups. A disabled colour stays the platform's, with the single declared
exception recorded above.

The third mechanism writes the same role set on the `QApplication` itself,
through `qt_widgets.declare_application_colours`. It is the fallback that the
other two cannot provide. Qt's application palette follows the **host
appearance**. So on a machine set to Dark, everything that this interface did
not name arrived with a dark theme's surfaces, around a light window. That
included what no per-widget declaration can reach, because a stylesheet makes
every widget beneath it resolve its colours from the application palette, not
from the styled ancestor. **This interface declares its light theme there rather
than following the host** (project owner, 2026-09-20, ratified - chosen over
leaving the host appearance alone, and over growing a second palette for dark
appearance). The reason is the requirement table. All 24 requirements are
measured on PANEL and BACKGROUND. So are the dichromacy minimums that the six
compartment traces were re-picked against. An interface that rendered any
other surface would be measuring surfaces that are not on screen. The cost is
recorded rather than hidden. A reader whose machine is set to Dark gets a
light-appearing window. Supporting dark appearance properly means re-measuring
every requirement here against a second pair of surfaces. It also means
re-picking all six traces under four vision models. That is interface work,
not a setting.

**It is a palette and not a colour-scheme hint.** Qt 6.8's
`styleHints().setColorScheme` documents itself as a hint. Its documentation
says that "overriding the color scheme is not supported on all platforms". It
was observed being ignored outright on 2026-09-20, when it still reported
`Unknown` after being set. So nothing here rests on it. A palette is
authoritative at any depth. The test `tests/integration/test_dark_appearance.py`
supplies a dark host palette. Measured against that palette, the page's scroll
bar goes from 94.3% of its pixels darker than mid-grey to none.

Two things still follow the host. Both do so by the rule, not by omission. A
**disabled** widget draws from the `Disabled` colour group, which all three
mechanisms leave to the platform. Declaring a disabled colour is a decision
under `.claude/rules/ui-color.md`, and this interface has exactly one, measured
above. The splitter handles used to be disabled, so they kept the host's dark
surface. Since `PL-W9P6` (2026-10-18) they are enabled. The border between two
Areas now shows the page's `BACKGROUND` under a dark host too.
`test_the_border_between_two_areas_shows_the_page_rather_than_the_host` checks
this (`PL-05M4`).
A **tooltip** draws from `ToolTipBase` and `ToolTipText`, which are outside the
declared role set. This interface uses no tooltip today.

All of this is visible rather than asserted.
`tests/integration/test_dark_appearance.py` renders the dashboard and both
dialogs under the palette that a dark host supplies. It fails on any content
widget that resolves to that palette. That is what caught six controls that
had declared nothing (`PL-RKRY`, `PL-7W9N`, `PL-0NVN`). It also checks the
chrome and the untouched `Disabled` group against the same host. Which
controls this test covers is not left to a remembered list of widget kinds.
`tests/integration/test_simulation_view.py` builds the whole dashboard under a
foreground colour that this interface never uses. It fails on any control that
paints its own content and resolves to that colour. So a control added later
must declare a colour, rather than depend on somebody noticing it. The test
names what it exempts, each against the reason it draws no text.
`tools/contrast_check.py` counts those kinds into its report line. A
requirement exists only where somebody wrote a colour down. So a control that
writes none would otherwise be absent from both sides of that line's count,
and the line would treat it as covered (`PL-4L49`).

### The six compartment traces: what separates them

Six curves share one plot. Taking a value off the wrong curve is a misreading
of a clinical quantity, not an aesthetic complaint. The curves are separated by
**line style**, with color as a second cue and never the first. This section
records why that order is forced, and which standard the colors must meet
instead.

**Line style is the separating channel.**

| Compartment | Line style | Dash pattern (px) | Width (px) |
| --- | --- | --- | --- |
| Circuit | solid | — | 3 |
| Alveolar | long dash | 10 on, 4 off | 3 |
| Mixed venous | short dash | 4 on, 3 off | 2 |
| Vessel-rich | even dash | 6 on, 6 off | 2 |
| Muscle | dotted | 2 on, 3 off | 2 |
| Fat | dash-dot | 12 on, 4 off, 2 on, 4 off | 2 |

All six styles differ. The legend entry beside each checkbox names its style in
words, so a reader can learn each trace's style without consulting the plot.
Circuit and vessel-rich were both solid until `PL-GVXP`. For that one pair, the
redundant channel was redundant in name only.

**Which style goes on which compartment is decided by the colors.** The two
traces that are hardest to separate by color get the two marks that are easiest
to separate by shape. The next pair gets the next easiest marks, and so on
outward. The closest pairs in the matrix below are vessel-rich against fat, and
mixed venous against fat. In the first pair, an even dash is set against an
alternating dash-dot. In the second, a short uniform dash is set against that
same dash-dot. In each pair, the two marks differ in mark length, gap length
and rhythm at once. The one pair of marks in the set that a reader could
genuinely confuse is the 2 px dots against the 4 px short dash. That pair is
spent on mixed venous against muscle, which has the widest separation of any
pair among these six.

**Color is a second cue, and the arithmetic says it cannot be the first.**
Every trace clears the 3:1 contrast that SC 1.4.11 requires against the panel.
It does so as displayed and as simulated for each dichromacy:

| Trace | sRGB | Normal | Protanopia | Deuteranopia | Tritanopia |
| --- | --- | --- | --- | --- | --- |
| Circuit | `#176B87` | 6.02 | 5.67 | 6.21 | 6.02 |
| Alveolar | `#159789` | 3.61 | 3.23 | 3.84 | 3.63 |
| Mixed venous | `#7C3AED` | 5.70 | 5.96 | 4.68 | 5.55 |
| Vessel-rich | `#DC2626` | 4.83 | 7.18 | 4.14 | 4.84 |
| Muscle | `#D17206` | 3.43 | 3.96 | 3.22 | 3.46 |
| Fat | `#64748B` | 4.76 | 4.74 | 4.76 | 4.77 |

Compared trace against trace, the contrast is a different picture. The design
rests on this table:

| Pair | Normal | Protanopia | Deuteranopia | Tritanopia | Worst |
| --- | --- | --- | --- | --- | --- |
| Vessel-rich / Fat | 1.01 | 1.51 | 1.15 | 1.02 | **1.01** |
| Mixed venous / Fat | 1.20 | 1.26 | 1.02 | 1.16 | **1.02** |
| Alveolar / Muscle | 1.05 | 1.23 | 1.19 | 1.05 | **1.05** |
| Circuit / Mixed venous | 1.06 | 1.05 | 1.33 | 1.08 | **1.05** |
| Alveolar / Vessel-rich | 1.34 | 2.22 | 1.08 | 1.33 | **1.08** |
| Mixed venous / Vessel-rich | 1.18 | 1.20 | 1.13 | 1.15 | **1.13** |
| Circuit / Fat | 1.26 | 1.19 | 1.31 | 1.26 | **1.19** |
| Muscle / Fat | 1.39 | 1.20 | 1.48 | 1.38 | **1.20** |
| Alveolar / Mixed venous | 1.58 | 1.84 | 1.22 | 1.53 | **1.22** |
| Alveolar / Fat | 1.32 | 1.47 | 1.24 | 1.31 | **1.24** |
| Circuit / Vessel-rich | 1.25 | 1.27 | 1.50 | 1.24 | **1.24** |
| Vessel-rich / Muscle | 1.41 | 1.81 | 1.28 | 1.40 | **1.28** |
| Circuit / Muscle | 1.75 | 1.43 | 1.93 | 1.74 | **1.43** |
| Mixed venous / Muscle | 1.66 | 1.50 | 1.45 | 1.61 | **1.45** |
| Circuit / Alveolar | 1.67 | 1.75 | 1.62 | 1.66 | **1.62** |

**Re-picking the palette does not fix this, and the search was run rather than
assumed.** The ceiling above is $`21^{1/5}\approx1.84`$. Requiring 3:1 against
a white panel caps every trace's luminance at 0.30. That shortens the axis and
brings the ceiling down to **1.48**. A search over lightness, with each hue and
saturation held fixed, reaches **1.28** as the best worst-pair contrast across
the four vision models. It gets there only by driving four of the six traces to
near-black. That loses the hue identity that makes a trace nameable, and it
buys a number still less than half of 3:1. So the colors here are chosen to
name their compartment and to clear the 3:1 minimum against the panel. The
line style does the separating. `.claude/rules/ui-color.md` records this as a
standing judgment, so that the search is not re-run every time a color is
touched.

**Two colors were re-picked to meet the 3:1 minimum, not to improve
separation.** The alveolar trace was `#18A999`, at 2.93:1 as displayed and
2.61:1 simulated for protanopia. The muscle trace was `#D97706`, at 3.19:1 as
displayed and 2.98:1 simulated for deuteranopia. Each new color keeps the old
hue and saturation exactly. It is darkened to the lightest shade that clears
3.2:1 in all four models. That target is 3:1 plus two tenths, so the shipped
value is not itself a boundary case. The alveolar trace also draws the
$`F_A/F_I`$ wash-in plot. That plot carries a single line and never had a
separation problem. It inherited the shortfall from the shared constant, and
the same change fixes it.

**What changes when two runs share the axis, and what does not.** Nothing about
a compartment's appearance changes. Each compartment keeps the line style and
the colour that the table above gives it. The reason is that colour already
means "compartment" here. A channel that means something else on either side
of a mode change is a misread of a clinical value waiting to happen. What is added is the **run, on
line width, at two levels**. The arithmetic above allows this only under a cap.
With six compartments, the width column above is already spent across 2 px and
3 px. So **at most two compartments are drawn while two runs are shown**
(`PL-HLD5`, `PL-8PSW`). Two compartments times two runs is four curves. The cap
limits how much the chart's colours can carry. It never reduces what the
display must show. § "Minimum displayed outputs" keeps all six readouts on
screen for both runs, and it names this cap when it says so.

**The first run is the wider, and the second keeps the single-run width.** This
is forced rather than chosen. A branch reproduces its parent element-wise up to
the fork (planned-milestone item 12). So before the branch point, the two
curves do not merely run close together. They coincide exactly, and whichever
curve is drawn thicker hides the other completely over that stretch. The
narrower curve therefore has to be the one drawn last, on top. Widening one
curve, rather than narrowing the other, also keeps every trace at or above the
2 px width that the table above gives it. A 1 px antialiased line renders
lighter than its declared colour. That would push it back below the 3:1
minimum against the panel, which this section treats as an error rather than a
tracked shortfall. A reader compares the two width levels *locally*, between
the two curves of one compartment, which are adjacent by construction. The
reader does not have to decode them across the plot.

**Two marks that are not traces, and how they are separated.** A control change
and a branch point are both vertical lines. Both annotate an instant rather
than showing any part of the run. Both are drawn in the control mark's colour.
They are separated by the dash pattern: the control mark is finely dashed and
the branch point is solid. The legend also names both in words. Neither mark
depends on a hue. That is deliberate, because a reader must not confuse this
pair. A fork is where two runs stop being the same run. Reading a fork as a
setting change would attribute a divergence to the wrong cause.

**The dichromacy simulation.** The simulation uses Brettel, Viénot and Mollon's
projection onto the reduced stimulus surface that each dichromacy leaves. That
surface is defined by the neutral axis and by the monochromatic stimuli that a
dichromat and a normal trichromat see as the same hue.[^brettel1997] The
simulation uses the two-half-plane form rather than the single-matrix
simplification of Viénot, Brettel and Mollon (1999). That simplification is
not accurate for tritanopia, and all three dichromacies are reported
here.[^vienot1999] The coefficients are the precomputed sRGB-space forms
published by libDaltonLens. libDaltonLens derives them from Brettel's
construction over the Smith and Pokorny (1975) cone fundamentals.[^daltonlens]

There are three limits on how far these numbers may be read. First, the
simulation renders, for a normal observer, an approximation of a dichromat's
*appearance*. It is not a measurement of dichromatic perception. It also
models the three dichromacies rather than the far commoner anomalous
trichromacies, so it does not represent the milder losses of anomalous
trichromacy. Second, WCAG's
relative-luminance formula is then applied to that simulated output. The
formula was not defined for that use, because SC 1.4.11 is defined on the
color the display emits. Third, the whole calculation is about luminance. So
it says nothing about the hue difference that a reader with normal color
vision actually uses. The numbers are good for the comparative claim that this
section uses them for: that no arrangement of these six colors separates them,
whichever observer is assumed.

`tools/contrast_check.py` computes every figure in this section. `make check`
runs it, and `tests/unit/test_contrast_check.py` pins the figures. Run it with
`--matrix` to print the pairwise table above.

[^brettel1997]: Brettel H, Viénot F, Mollon JD. Computerized simulation of
    color appearance for dichromats. J Opt Soc Am A. 1997;14(10):2647-2655.
    doi:10.1364/JOSAA.14.002647

[^vienot1999]: Viénot F, Brettel H, Mollon JD. Digital video colourmaps for
    checking the legibility of displays by dichromats. Color Res Appl.
    1999;24(4):243-252.
    doi:10.1002/(SICI)1520-6378(199908)24:4<243::AID-COL5>3.0.CO;2-3

[^daltonlens]: libDaltonLens, public domain, https://github.com/DaltonLens/libDaltonLens
    — coefficients and derivation, the latter written out at
    https://daltonlens.org/understanding-cvd-simulation/

### Displayed precision

#### What the concentration readouts show

Every modeled concentration and relative partial pressure, in all six
compartments, is displayed to **0.01 percentage points**, which is two decimals
of a percent. The delivered-agent setting uses the same resolution, in the
readout beside its slider and in the label shown while the slider is dragged, so
the setting a reader dials and the values it produces are read at one scale. A
positive value that would round to `0.00%` is displayed as `<0.01%`, so `0.00%`
means only that no agent has arrived, as before a run starts.

Each displayed digit is accurate as a statement about this model with these
parameters. No displayed value may be read as accurate to its last digit as a
prediction about a patient ("Known limitations").

**For developers.** `test_format_percent_uses_the_documented_display_resolution`
enforces the resolution, and
`test_format_percent_marks_a_value_below_the_resolution` enforces the `<0.01%`
form.

#### Why the readouts show two decimals

**The equation solver does not limit the resolution** (measured 2026-09-06). The
simulator's results differ from an independently computed solution by at most
$`1.6\times10^{-12}`$ percentage points anywhere in the reference test's runs,
and by $`5.2\times10^{-12}`$ over an hour with the settings held constant. That
is about one two-billionth of the last displayed digit, so **a third decimal
would not be numerical noise.** What decides the count is **model fidelity**,
meaning what the parameters can support, and it is bounded from the other side
by **legibility**.

**Two questions must be kept apart.** The first is *how finely two moments
within one run can be told apart*. Within a run the parameters are fixed and the
simulation is deterministic, so the answer is about nine decimal places finer
than the readout shows. The second is *how finely this model resolves a
concentration in a patient*. Its answer is much coarser, and it is the question
that a clinician reading a percent sign is asking.

**The upper limit: one measured standard deviation of a partition coefficient is
worth about one to seven counts of the last displayed digit.** One count is 0.01
percentage points. Perturbing a single stored coefficient by one published SD,
and re-running at 1 MAC with the reference adult's flows, displaces a displayed
compartment by these amounts, which have no test yet (`PL-19W8`):

| Coefficient perturbed by one SD | Displacement, worst over 3600 s |
| --- | --- |
| Fat tissue:gas | 8.7×10⁻⁴ to 6.7×10⁻³ pp |
| Blood:gas | 1.5×10⁻² to 5.4×10⁻² pp |
| Vessel-rich tissue:gas | 1.3×10⁻² to 5.0×10⁻² pp |
| Muscle tissue:gas | 1.3×10⁻² to 6.8×10⁻² pp |

<!-- not-restated: 1.3 -->

Each range runs over the three agents that the simulator offers, and desflurane
always gives the largest displacement. The SDs are the measured ones that
"Parameter provenance" records. The tissue SDs are those of Yasuda, Targ and
Eger's human tissue coefficients, 3.9% of the mean for desflurane, 5.3% for
sevoflurane and 6.4% for isoflurane. For desflurane's blood:gas coefficient the
SD is Eger's $`0.424 \pm 0.024`$, which is 5.7%. Which agent gives the largest
displacement has no test yet (`PL-19W8`). The three tissue SDs are the source's
brain:blood ones, and fat's are larger. Which SD each row perturbed is being
checked, with no test yet (`PL-TDX0`).

So the last digit of a two-decimal readout lies between about a seventh of one
parameter SD and seven times it. A third decimal would put the last digit at one
seventieth to seven tenths of one SD. It would assert resolution in a quantity
whose measured spread is one to two orders of magnitude wider, in the readouts
where a reader is least able to notice. That is false precision, and it stops
the count at two.

A digit finer than one SD is still honest, because an SD moves the whole
trajectory. It moves where the curve sits, not how finely two points on it can
be told apart, so a reader comparing 09:14 with 09:16 of one run is not limited
by it. What the SD forbids is digits *far* finer than itself, because a reader
cannot tell which of the two questions a printed digit answers.

**The lower limit: one decimal hides the slow compartments' wash-in, which is
the reason for displaying them.** At 0.1 percentage points the sevoflurane and
isoflurane fat fractions read `0.0%` for the whole hour (0.032% and 0.015% at
3600 s). Desflurane's fat fraction stays at `0.0%` for its first 19.3 minutes
and reaches 0.2%. Muscle reads `0.0%` for its first 2.9 minutes with desflurane,
8.5 minutes with sevoflurane and 14.8 minutes with isoflurane. At two decimals,
at 1 MAC with default flows, the same compartments first show a nonzero value at
57, 125 and 190 seconds (muscle) and 237, 781 and 1477 seconds (fat), for
desflurane, sevoflurane and isoflurane in that order. These times have no test
yet (`PL-19W8`).

This lower limit is the project owner's teaching judgment, not a property of the
model. The solver and the parameters both support one decimal comfortably. What
rules one decimal out is that a simulator built to show uptake and distribution
would show a flat zero where the uptake is happening. A future change to one
decimal has to answer that objection.

**So the band is one to two decimals, and two is the chosen count.** The count
inside the band is a presentation decision, which the owner may revise without
re-deriving anything in the model. Moving the readout to one decimal would
change what a reader sees and which settings a slider can reach, and nothing in
the model's equations.

**Why not the 0.1 percentage points that agent monitors show.** Agent monitors
display end-tidal and inspired concentrations to a tenth of a percentage point,
and that would suit the circuit and alveolar readouts. This simulator also
displays compartments that no monitor shows, and at that resolution fat and
muscle read `0.0%` for the times given under the lower limit above. A resolution
of 0.01 percentage points is the coarsest that keeps every displayed compartment
legible. That it is also close to what the parameters support is a coincidence,
because the two are measured independently. The times this paragraph relies on
have no test yet (`PL-19W8`).

**Why not significant figures.** A significant-figures rule gives the smallest
values the most decimal places, and the small values are where this model
supports the least. The parameters' measured SDs, 3.9% to 6.4% of the mean, are
*relative*, so they apply undiminished to a compartment holding a thousandth of
a percent. Three significant figures on the fat fraction would imply a relative
resolution of 0.1% on a number whose parameters are known to about 5%, which
over-claims by a factor of fifty. The solver is not the limit here. With the
exact method that the simulator uses, the compartments that hold little agent
carry at most $`2\times10^{-4}`$ relative error anywhere in the first ten
seconds of a run, and $`8\times10^{-11}`$ at ten seconds itself. This paragraph
uses the brain:blood SDs noted above, so it is being corrected, and its figures
have no test yet (`PL-TDX0`).
<!-- not-restated: 5 % -->

**Why a value below the resolution is marked rather than shown as zero.** Even
at two decimals, muscle and fat start below the last digit, for the times given
under the lower limit above. Showing `0.00%` over those intervals would state
that the compartment holds no agent, which the model does not say. The model
says that the compartment is filling, below what the display resolves, and
`<0.01%` states exactly that. The display marks what it cannot carry rather than
adding a decimal that the model cannot support.

A negative value is never shown in the below-resolution form. The model cannot
hold a negative concentration, minus zero included (§ "Concentrations"), so a
negative value that reaches the display means that something upstream is wrong.
The display refuses it rather than showing it as a plausible small positive
reading.

**For developers.** Nothing in `core/` reads the decimal count.
`MAXIMUM_SIMULATION_STEP_S` is a tolerance in seconds, the supported input
ranges are intervals in L/min, and "Supported simulation step" and "Supported
input ranges" derive both without reference to the readout. No `Fraction` can
hold a negative value, and the formatter is the code that refuses one.

#### The MAC multiple's resolution

**The MAC resolution is derived from the percent resolution.** A MAC multiple is
a percent divided by the agent's MAC in percent (`mac_percent`), so the percent
resolution already fixes how finely the quotient is known. The rule is to take
**the finest power of ten that is nowhere finer than the percent resolution
converted into MAC.** Converted, 0.01 percentage points is 0.005 MAC for
sevoflurane, 0.0083 for isoflurane and 0.0017 for desflurane. Isoflurane sets
the limit, at 0.0083 MAC, and **0.01 MAC** is the finest power of ten at or
above it. `test_the_mac_resolution_is_derived_from_the_percent_resolution`
repeats this arithmetic for every shipped agent, so adding an agent or changing
the percent resolution fails there rather than silently over-claiming.

The smallest change the MAC readout can show is therefore 0.02 percentage points
of sevoflurane, 0.012 of isoflurane and 0.06 of desflurane, never less than the
percent readout's. The two readouts round separately, so the MAC value can
occasionally change while the percent stays the same. The three per-agent
figures have no test yet (`PL-19W8`).
<!-- not-restated: 0.06 -->

A positive MAC multiple below the resolution reads `<0.01 ×MAC`, and this
matters more on the MAC line than on the percent line. A compartment clears
0.01 MAC later than it clears 0.01 percentage points, so `0.00 ×MAC` beneath a
percent line that already shows the compartment filling would make the two
readouts contradict each other.

**For developers.**
`test_format_mac_multiple_marks_a_value_below_the_resolution` enforces that
form. The MAC resolution is derived rather than stored beside the percent
resolution so that re-measuring one number never means re-deriving two.

#### What the model keeps that the display rounds

**The resolution is a property of the display alone.** The model computes and
keeps every value at full precision, including every value the chart is drawn
from, and a slider's value reaches the model without rounding. The rounding
happens exactly once, in the readout, which is the only place between a slider
and a pixel where resolution is lost. With the exact method that the simulator
uses, the model keeps about nine orders of magnitude more than the display
shows.

**For developers.** Everything upstream of the formatter carries full binary64
precision: the compartment states, every integration step, the mixed-venous and
tissue transfers, and every state of the `DrawnWindow` that the chart is drawn
from. Nothing in `core/` rounds, and the snapshot fields that the interface
reads are raw fractions. `test_the_model_keeps_precision_the_display_throws_away`
enforces this. Two runs whose delivered concentrations differ by an amount four
orders of magnitude smaller than the display resolution must reach states that
differ, and must still look identical on the display.

#### Comparing two readouts

**Solver error does not make the gap between two readouts less accurate than
either reading.** Within one time step, the model updates every compartment
from the values it had at the start of that step. Rounding does make the gap
less accurate. Each reading is rounded to its last displayed digit, so a gap
taken from two readings can differ from the true gap by up to one count of that
digit.

The six compartment readouts and the clock sit in one row of seven panels, where
seven fit, so that the readouts can be read *in order*: the circuit leads the
alveoli, and the alveoli lead the tissues. § "The readout row's width condition"
below says what happens when seven panels do not fit. Solver error could mislead
that reading only by reversing which of two compartments is shown as higher. A
measurement compared every pair of the six readouts at every time step, in every
run that § "Independent-solution test" describes and for all three agents, which
is 1 485 000 pair comparisons. The simulator's readings **never** disagreed with
those of the independent solution about which compartment is higher, even where
the gap was tiny (measured 2026-10-17).

That is a measurement on one platform, not a guarantee. Rounding to a fixed
number of decimals never reverses the order of two values. So the display can
show two compartments in the wrong order only where the simulator and the
independent solution put them in opposite order. That needs a true gap smaller
than the two compartments' solver errors added together. The largest difference
between the two solutions in any pair's gap, over every run, is
$`1.1\times10^{-12}`$ as a fraction, not a percent, and true gaps that small do
occur while two compartments cross. A reversal is arithmetically possible
there, though none was observed.

The interface therefore adds no warning or marker when readouts are compared. A
reader who compares them in order, as the row is designed for, can rely on the
order shown. The interface shows no gap between two readouts. A gap that a
reader works out by subtracting two readings carries the rounding of both,
described at the start of this subsection, and the solver limit in the
paragraph above.

**For developers.** Two tests enforce the ordering claim. Each covers one half of
the path from the model to the readout and can fail on its own.
`test_exact_step_matches_the_independent_solution_everywhere` bounds the
solver's error against the independent solution.
`test_format_percent_preserves_order` in `tests/unit/test_formatting.py` checks
that the shipped formatter never shows a higher fraction as a lower percent. It
covers the "<0.01%" reading below the display resolution and both sides of every
value at which the last displayed digit changes. Together the two tests mean that
no reversal can occur at a true gap above $`1.0\times10^{-7}`$ counts, which is
twice the first test's tolerance.
`test_displayed_ordering_reverses_only_at_a_crossing` is the measurement of every
run quoted above, and it reads each value through the shipped `format_percent`.
It allows a reversal where the true gap is below that same threshold, instead of
asserting that none occurs, because a reversal is possible at a crossing. It
cannot fail unless one of the other two tests fails, so it records the
measurement and adds no evidence of its own.

#### One resolution for all six readouts

**The resolution is the same in every compartment, for two reasons.**

- **The six readouts are read comparatively.** Different decimal counts across
  them would put digits of different place value in the same position, and a
  value scanned rather than read would then be misjudged by a factor of ten.
  That is a property of the reading task, whatever the solver does.
- **Parameter uncertainty is absolute in its effect across the row.** The
  one-SD displacements tabulated above run from $`8.7\times10^{-4}`$ to
  $`6.8\times10^{-2}`$ percentage points across all six compartments and all
  four coefficients. That is a spread of less than two orders of magnitude, on a
  row whose *values* span four. A single absolute resolution, set by the
  compartments where the displacement is largest, expresses that spread directly
  and is conservative where the displacement is smaller.

#### The readout row's width condition

**The row has a width condition, and both reasons above rest on it.** The row's
column count follows its width, and every panel takes exactly one column. So the
seven panels sit **side by side wherever seven panels' reserved widths fit the
row, four per line where seven do not, two where four do not, and one below
that**. These four arrangements are the rungs of the row's ladder. Each column
reserves the widest value it can show, measured in the font the interface draws
with. The clock's column reserves its widest elapsed time, and each
compartment's column its widest percent and MAC multiple, so the clock's width
costs no other column. The widths at which the row steps down depend on the font
and the display scale. With the font that the tests draw with, measured on
2026-10-18, the row is seven across from 1005 logical pixels, four from 591 and
two from 310. Those figures illustrate the rule and do not specify it. The
ladder is derived from what the interface draws with, so it states no pixel
width that a different font or display scale would make wrong.

The change of arrangement affects the two reasons unequally, and withdraws
neither.

- **Reading the row in order becomes harder.** Below the seven-across width the
  six readouts are on two or more lines, and the comparison that the row invites
  becomes a scan across the lines instead of a single glance. The measurement
  behind the ordering claim is untouched, because it compares displayed values,
  not their positions. What narrows is the claim that the arrangement invites
  the comparison, not the claim that the ordering is faithful.
- **The uniform resolution still applies at every width.** The grid aligns
  the values within a column at every rung, so a reader scanning two panels
  compares them against a common position, whether they are side by side or
  stacked.

**The window opens maximized, so the row opens at the widest rung the screen
affords.** Maximized, the readout region gets the screen's available width less
the window's own frame. A 1366 px laptop screen, one of the commonest widths,
opens on seven across, as the paragraph after next measures. A 1280 px screen
gives the region about 1234 px (measured 2026-09-27, with the tests' font).
Whether it still opens on seven, now that the control-change record shares the
region as described below, has no test yet (`PL-LKX7`).

Maximized is not full screen. The title bar and window controls stay, and on
macOS the window is zoomed. Maximized is also the default window state of the
reference design that the interface follows (`docs/interface-provenance.md`
§ "Adopted"). A reader who un-maximizes gets the window's normal size back,
which is a fixed fraction of the screen's available area, centred. At that size
the row steps down the ladder above wherever its width requires. A screen too
narrow for seven across even when maximized opens on a lower rung, because
maximizing changes the row's width, never the rule that picks the rung.

**The row's width follows the window, never an Area.** The readouts sit in a
region above the layout container that the Areas replace (§ "Minimum displayed
outputs" -> "What this list requires once the layout is the reader's"). So a
split, a join, a border drag or a Workspace switch never changes the width that
the row is laid out at. Only two things change it: the window's width, and how
the region divides that width. The region holds the runs' rows in a left column
and the control-change record in a right column, which take 0.82 and 0.18 of the
width. The left column never narrows below its own minimum width. At every rung,
each panel is laid out at its full reserved width, so no value is wrapped away
from its unit.
<!-- not-restated: 0.18 -->

**A 1366 px window opens on seven columns, with one run or two** (measured
2026-10-18). With the tests' font, a 1366 px window gives the region 1320 px.
The record column takes 235 px and the readout column 1073 px, which is 68 px
more than the 1005 px that seven across needs. Two runs share that one row, so
the outcome above for a 1366 px screen also applies in compare mode. At 235 px
the longest control-change lines no longer fit on one line, so the record wraps
them, but only after the time and after the arrow, which keeps every value
beside its unit.

**For developers.** `readout_columns` in `src/anesthesia_sim/app/dashboard_frame.py`
sets the row's column count from its width, and the ladder is
`READOUT_ROW_LADDER`. The pixel widths above are measured on the offscreen font
that the test suite renders with. `src/anesthesia_sim/app/main.py` shows the
window with `showMaximized()` over a normal geometry of `WINDOW_SCREEN_FRACTION`
of the screen's available area. The readouts are in
`SimulationView.unconditional_region`, and `wrapping_between_parts` wraps the
control-change record.
The region's two shares are those of the chart panel's Area and the sidebar's
Area in the layout that the dashboard first opened on, which made the record as
wide as the sidebar beneath it. The Workspaces that now ship divide the width
differently, and the region keeps its own shares.
`test_every_readout_reserves_a_qualifier_line_and_an_equal_column` enforces the
column count and the one-column span.
`test_the_readout_row_reflows_where_its_panels_stop_fitting` reads the step-down
widths from the row rather than asserting them.
`test_no_unconditional_value_sits_inside_the_layout_container` keeps the row
outside the Areas.
`test_two_runs_share_one_readout_block_whose_values_name_their_runs` and
`test_a_1366_px_window_opens_one_run_s_readout_row_on_seven_columns` enforce the
1366 px outcome in compare mode.

#### Time, flows and the chart

**Simulated time is displayed to 0.1 s, which is exactly one simulation step
(`SIMULATION_STEP_S`).** Every recorded control change is stamped at that same
resolution, so the timeline and the clock never show one time in two different
forms. The chart's time-axis labels are durations that carry their own units,
and they are no finer than the whole second, because every tick the axis can
place falls on a whole second. The axis labels a span that a reader scans, not
an instant that they read off. A tenth of a second on every label would spend
width on a digit that is zero at every tick spacing the axis offers. "The
chart's time base" gives the label form and the reason it differs from the
clock's.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**The chart is read for shape, so its resolution is coarser than the
readouts'.** It plots the same percentages on a shared linear axis that runs
from 0 to 3 ×MAC of the agent in use, and a second axis on the right shows the
same position in MAC multiples. Its resolution is set by pixels rather than by
decimals. Every number the chart offers, in the readout row and in the hover
readout that § "The chart's hover readout: what the tooltip may show" derives
below, is shown at the resolutions above. The MAC axis is labelled on round MAC
values, in half-MAC steps, which the fixed 3 ×MAC range gives for every agent,
so a gridline that a reader learns under one agent means the same thing under
the next. § "The chart's vertical range is denominated in MAC, and fixed" above
explains the range. The chart's horizontal extent is the selected time base, so
the reader chooses the seconds per pixel, as "The chart's time base" explains.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**Fresh gas flow, alveolar ventilation and cardiac output are displayed to
0.1 L/min**, the resolution of the controls that set them. A slider and the
readout beside it show one quantity, so each slider moves in steps of the
display resolution: 0.1 L/min for the three flows, and 0.01 percentage points
for the delivered dial. The value applied to the model is exactly the value
printed beside the control. If a control could apply a value that its own label
rounds away, a reader could not tell which value is the setting in force.

**For developers.** The sliders are integer-valued.
`test_fresh_gas_flow_slider_forwards_value_to_controller`,
`test_alveolar_ventilation_slider_forwards_value_to_controller` and
`test_cardiac_output_slider_forwards_value_to_controller` read the flows'
resolution from each control's label, and
`test_the_slider_steps_at_the_display_resolution` enforces the slider steps.
Because `CONCENTRATION_DISPLAY_DECIMALS` and `FLOW_DISPLAY_DECIMALS` set those
steps, they also decide which settings can reach the model. `app/wash_in.py`
derives `WASH_IN_DENOMINATOR_FLOOR_FRACTION`, the smallest inspired fraction an
F_A/F_I ratio may be formed from (§ "F_A/F_I as a displayed ratio"), from the
concentration resolution, so one more decimal of concentration moves that floor
down tenfold. A change to either count is therefore a change to the model's
reachable inputs, and is derived in this section first.

#### The agent-accounting panel

**The panel's three amounts are displayed to 0.1 L, and its two residual lines
as the power of ten each lies below, because they answer different questions**
(decided 2026-09-15). The amounts are read against each other, delivered against
exhausted plus stored, and against a reader's sense of scale. The residual lines
are a numerical check. They have to make a residual of order 10⁻¹² L visible
against amounts of order 1 to 100 L, which no fixed decimal count can do.

**The amounts take one uniform resolution, on the same argument as the
readouts.** Perturbing one stored coefficient by one published SD moves the
exhausted total by 0.016 to 0.042 L at 3600 s, and by 0.18 to 0.23 L at the 24 h
supported limit. By agent, the shifts are sevoflurane 0.024 and 0.19 L,
isoflurane 0.016 and 0.18 L, and desflurane 0.042 and 0.23 L, and the blood:gas
coefficient dominates throughout. These shifts were measured at 1 MAC with the
reference adult's flows, and have no test yet (`PL-19W8`). One count of 0.1 L
therefore lies between a quarter of an SD and six SDs across the whole supported
span, which is inside the band the readouts' derivation admits. A count of
0.01 L would fall to a fiftieth of an SD by 24 h. Delivered agent carries no
parameter uncertainty, because it is the dial times the flow times the time, and
it takes the same resolution so that the three amounts read at one scale.
<!-- not-restated: 0.18 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 0.01 L -->

The panel labels the unit as litres of equivalent pure agent gas, the unit this
document uses, because a bare "L" beside an anaesthetic agent invites a reader
to take it as litres of liquid.

**A residual line shows only the power of ten that the residual is less than**,
such as `<1e-13 L`, which means less than 10⁻¹³ L. A residual that passes its
check is the rounding left over from summing the initial, delivered, exhausted
and stored amounts. Its digits and its sign are set by the order in which the
arithmetic ran, not by anything modelled. So a correct change to the code that
alters only the last binary digits of that arithmetic changes those digits and
that sign. The `<` means the same as it does on the amounts. Neither line shows
a sign, so both lines read alike. The sign means something only in a check that
fails. Then the run halts, and the failure notice prints the signed values to
six figures. A residual of exactly zero reads `0 L`.

**For developers.** The power of ten is computed from the float's exact value.
The residual's form rests on a measurement taken on 2026-10-03. A change to the
propagator's arithmetic that left each run's own path bit-identical was replayed
on an 81-run protocol: three agents, three dial pairs, three cardiac outputs and
three fresh gas flows, each run forked at minute 30 with the dial set back and
its branch played for 30 minutes, on the v0.5.21 tag and on v0.5.22. A branch's
residual moved by up to 5.9 times between the two trees. Of 2,511 branch
samples, the two trees' residuals read differently at four significant digits on
1,975, at two on 634, at one on 154, and at the power of ten on 22, which are
the samples where the two residuals fall on either side of a power of ten. Every
residual was below 2.1 × 10⁻¹¹ L, every check passed in both trees, and a run's
own path read identically in every form. `format_agent_residual` defines the
form. `test_format_agent_residual_prints_the_power_of_ten_it_lies_below`,
`test_format_agent_residual_drops_the_sign_the_rounding_chose`,
`test_format_agent_residual_bound_is_strict_and_tight_at_every_power_of_ten` and
`test_format_agent_residual_reads_zero_as_zero` pin it.
`test_format_agent_residual_prints_no_digit_a_last_bit_change_redraws` uses the
pair `5.601e-14 L` and `5.609e-14 L`, which the two trees printed for one
sample. `AGENT_AMOUNT_DISPLAY_PRECISION` stores the amounts' count,
`format_agent_volume` defines their form, and `test_agent_amounts_precision`
pins both.
<!-- not-restated: 2.1 -->

#### Agent amounts in millilitres, and the cost

**An agent amount's precision is derived for the amount in one unit, and does
not carry over to another unit.** The derivation above is for litres of vapour.
The agent cost View shows the delivered total in millilitres of liquid, and the
compartment schematic shows each compartment's amount in millilitres of vapour,
so each of those needs its own precision. The bound is one-sided. It limits only
how fine a count may be. A count coarser than the derivation loses detail but
claims nothing false. A finer one claims a resolution that the parameters or the
conversion do not support, so it is refused rather than quietly reduced to the
bound. An amount in a unit that has no derivation is refused, rather than shown
at a default.

| Amount | Unit | Decimals | Resolution | Derived from |
| --- | --- | --- | --- | --- |
| A run total: delivered, exhausted or stored | Litres of vapour | 1 | 0.1 L | One SD of a partition coefficient, above |
| The delivered total | Millilitres of liquid | 1 | 0.1 mL | One SD of the measured liquid density |
| The exhausted total | Millilitres of liquid | 0 | 1 mL | The litre's resolution, converted |
| The stored total | Millilitres of liquid | Refused | - | The conversion reads a store 5.8% high |
| One compartment's amount | Millilitres of vapour | Two significant figures, none finer than 0.01 mL | 1% to 10% of the amount | One SD of a partition coefficient, as a share of the amount, below |
| One compartment's share of the agent held | Percent of the stored total | 0 | 1 percentage point | One SD of a partition coefficient, below |

**The exhausted total in millilitres of liquid is shown in whole millilitres.**
The exhausted total carries the partition coefficients' uncertainty, so it must
not claim a finer resolution in millilitres of liquid than in litres of vapour.
Otherwise a reader who switches the unit would see the model resolve a
difference in one unit that it does not resolve in the other. One step of the
litre display, 0.1 L of vapour, is 0.55 mL of sevoflurane liquid, 0.51 mL of
isoflurane and 0.48 mL of desflurane at the 20 °C reference of § "Agent amount",
and the smallest power of ten at or above all three is 1 mL. The partition
coefficients give the same answer. At 24 h, the one-SD shifts derived above for
the litre display, 0.19 L of sevoflurane vapour, 0.18 L of isoflurane and 0.23 L
of desflurane, are 1.04, 0.92 and 1.10 mL of liquid. So one step of 1 mL is
about one SD, and a step of 0.1 mL would be a tenth of one.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The delivered total in millilitres of liquid is shown to a tenth.** The
delivered agent is the dial times the flow times the time, so no partition
coefficient makes it uncertain. The delivered and exhausted totals are both gas
at room temperature, so their conversion to liquid at the 20 °C reference is
exact. That leaves one uncertainty in the delivered figure in liquid. It comes
from the measured liquid density, whose SD is 0.0008, 0.0006 and 0.0004 g/mL
for sevoflurane, isoflurane and desflurane. One SD moves the figure by 0.1 mL
only once it holds about 190 mL of sevoflurane, 250 mL of isoflurane or 366 mL
of desflurane. Above those volumes the last digit is finer than one SD of the
density. At 2% sevoflurane and 2 L/min, 190 mL takes about 14.5 h, and at the
dial's maximum of 8% and 10 L/min it takes 43 min. At Gas Man's Exercise 14-1,
39.4 mL of isoflurane, one SD is 0.016 mL. So 0.1 mL lies inside the band that
the density spans across the supported settings, as 0.1 L does for the
partition coefficients. The tenth also lets a reader multiply the delivered
figure by the price per millilitre beside it and get the cost, as § "A cost at
the reader's price" asks. The delivered total in litres stays at 0.1 L, coarser
than the delivered amount supports, which the one-sided bound allows.
<!-- provenance: data/agents/sevoflurane.json liquid_density.standard_deviation_g_ml = 0.0008 -->
<!-- provenance: data/agents/isoflurane.json liquid_density.standard_deviation_g_ml = 0.0006 -->
<!-- provenance: data/agents/desflurane.json liquid_density.standard_deviation_g_ml = 0.0004 -->
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- not-restated: 2 % -->

**A cost is shown to three significant figures, and a price per millilitre to
four.** A cost is the delivered agent in liquid times the reader's price per
millilitre (§ "A cost at the reader's price"). The price is the reader's own
figure, so it carries no modelled uncertainty, and the cost's only modelled
uncertainty is the liquid figure's, which comes from the measured density alone.
The largest relative SD of a stored density is sevoflurane's, 0.0008 / 1.5203,
or 0.053 %. That SD is relative, so the cost's precision is a count of
significant figures, not of decimals. A count of n figures has a smallest
relative step of 1 in (10^n - 1), at a value such as 999. At three figures that
is 0.10 %, coarser than one SD of the density, which the one-sided bound allows.
At four it would be 0.010 %, finer than one SD. A cost is never shown finer than
**a hundredth** of its currency, which is the smallest unit of most currencies.
For example, 0.68 reads `USD 0.68`, not `USD 0.680`. A positive cost below a
hundredth reads `USD <0.01`, and a run that has delivered nothing reads `USD 0`.
Four figures is the fewest at which the price's rounding moves the product of
the figures shown by at most half of the cost's smallest step. Half a step at
four figures is at most 0.5 in 1000, against 0.5 in 999 for the cost. The liquid
volume's 0.1 mL is then the only rounded figure in the reader's multiplication
that is coarse enough to matter, and the readout says so (§ "A cost at the
reader's price").
<!-- provenance: data/agents/sevoflurane.json liquid_density.standard_deviation_g_ml = 0.0008 -->
<!-- provenance: data/agents/sevoflurane.json liquid_density.g_ml = 1.5203 -->

**The stored total has no liquid precision, and is refused in liquid.** A store
converted to liquid reads 5.8% high (§ "Known limitations"). That error grows
with the amount. At 17 mL of liquid it is already a whole count of 1 mL, and in
a long run it is several. No count of decimals can make a figure with a known
bias of several counts read correctly, so the stored total keeps litres of
vapour, as the accounting panel shows it.

**For developers.** `app/formatting.py` keys each precision by the amount and
the unit, in `AGENT_AMOUNT_DISPLAY_PRECISION`. Each entry is an
`AgentAmountPrecision`, which holds the amount, the unit and the count shown. It
reads the finest count from the derivation for that amount and unit, so no
caller can pass a looser bound, and it refuses a finer count when it is built. A
precision that a reader could set would be built the same way.
`test_the_exhausted_total_in_millilitres_of_liquid_claims_no_more_than_in_litres`
repeats the litre-to-millilitre conversion for every shipped agent from the
stored molar mass and density.
`test_the_delivered_total_in_millilitres_of_liquid_is_shown_to_a_tenth` computes
the three volumes from the stored densities.
`test_the_cost_s_and_the_price_s_precisions_follow_from_the_density_and_the_cost`
computes both counts from the stored densities.
`test_a_unit_with_no_derived_precision_is_refused` enforces the refusal of the
stored total in liquid.

Concentration, flow, MAC multiples and the F_A/F_I ratio are each shown in one
unit, so each keeps one count. If a reader is ever given a choice of unit for
one of them, its count moves into a table of the same shape.

#### A compartment's amount and share on the schematic

**A compartment's amount needs a precision of its own.** At the totals' 0.1 L,
venous blood reads below resolution for a whole hour at 1 MAC with every agent
the simulator offers, and so do the alveoli with sevoflurane and isoflurane.
Desflurane's alveoli read 0.1 L from about two minutes. These figures have no
test yet (`PL-19W8`).

**A compartment's amount is shown to two significant figures, because its
uncertainty is a share of the amount rather than a fixed volume** (measured
2026-11-01). The totals' derivation was repeated on each compartment's amount in
millilitres of vapour. Each of the four stored coefficients was perturbed by one
published SD, one at a time, at 1 MAC with the reference adult's flows, and the
amounts were read every second for the first 20 minutes, and at 60 min, 180 min
and 24 h. The shift runs from almost nothing, in the circuit in the first
seconds, to 216 mL, in desflurane's fat at 24 h, because the amounts themselves
span as many orders of magnitude. So no single count of decimals lies inside the
band that the readouts' derivation admits. One count of 1 mL is a two-hundredth
of one SD in desflurane's fat at 24 h, the kind of false precision that stopped
the run totals at 0.1 L. One count of 10 mL is still a twenty-second of an SD
there. It would also print sevoflurane's and isoflurane's venous blood as
"<10 mL" for almost the whole first hour, which is the flat reading that the
readouts' lower limit refuses. That blood holds about 0.18 mL at 1 min, 6.6 mL
of sevoflurane at 10 min, and 9.7 to 10.0 mL at 60 min.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 10 mL, 10.0 mL -->

Relative to the amount, the shift is narrow. In venous blood and the three
tissue groups it is 1.4% to 12% of the amount. In the circuit and the alveoli it
is below 3%, because the dial sets them and a coefficient barely moves them. Two
significant figures put the last digit at 1% to 10% of the amount. As measured,
one count lies between a tenth of one SD, in desflurane's venous blood at 79 s
when it holds 0.99 mL, and many SDs in the circuit. These figures have no test
yet (`PL-19W8`). The one-sided bound allows the coarse end. The fine end is
finer than the readouts' seventh of an SD, but only in the first two minutes,
while venous blood fills. Three significant figures would put one count at a
hundredth of an SD. That is the same order as the readouts' third decimal, which
was refused at a seventieth of an SD, and as the totals' second decimal, which
was refused at a fiftieth. One significant figure would print fat's amount in
steps of 1000 mL by 24 h. So two is the finest count the parameters support, and
it is the count chosen.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The readouts' uniform resolution does not carry over to the schematic's amounts,
because neither of its two reasons applies to them. The parameters' uncertainty
in an amount is relative, as above, not absolute. And the amounts are not a row
read as one set. They are labels on separate containers, each followed by its
unit, and the schematic compares them on one scale, in the share bar.

A positive amount that would round to 0.00 mL reads `<0.01 mL vapour`, and
exactly zero reads `0 mL vapour`
(`test_a_compartment_s_amount_is_shown_to_two_figures_and_no_finer_than_0_01_ml`).
A limit finer than 0.01 mL would print four or more decimals for a moment's
worth of agent. The 0.01 mL limit is a provisional choice made for legibility.
It can only make an amount coarser than the two-figure rule would show it, which
the one-sided bound allows.

**A compartment's share is shown in whole percent.** A positive share below 0.5%
reads `<1%`, so a compartment that holds agent never reads as holding none. A
share of 99.5% or more that is not the whole reads `>99%`, so no compartment
reads as holding all of the agent while another holds some. In a desflurane run,
the circuit holds more than 99.5% of the agent for about its first second. One
SD of a coefficient moves a compartment's share by at most
1.2 percentage points, in isoflurane's muscle at 24 h. This figure has no test
yet (`PL-19W8`). So one count of 1 percentage point lies between 0.8 SD and more
than a hundred SDs, and a count of 0.1 would fall to a twelfth of one SD.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**For developers.** `app/formatting.py` is where this section is put into code.
It holds the resolution as a single constant, and derives from it the formatter,
the below-resolution marker, the MAC decimal count and the MAC axis placement.
It imports no toolkit, so the functions this section reasons about can be read,
cited and tested without loading the interface. `tests/unit/test_formatting.py`
pins the constant and every string the formatter produces.
`tests/unit/test_dashboard_frame.py` tests the end-to-end path: a real
controller, a real step, and the string on the panel. `app/dashboard_frame.py`
reads the constant to set the delivered dial's slider position, so the value the
slider applies and the readout beside it cannot drift apart.
`tests/reference/test_coupled_dynamics.py` restates the same constant and checks
it against `app/formatting.py`, because the ordering claim above is a property
of the rounded values. Adding a decimal would change what that claim proves
without changing anything the test reads, so a change to the resolution is a
change to this section.

### The chart's hover readout: what the tooltip may show

When a pointer is held over a trace, a small floating readout appears. This
section derives the readout's contents in the same way that
§ "Displayed precision" above derives the contents of the numeric readouts,
and for the same reason. What a hover reports is a clinically meaningful displayed value.
So what it may show is a claim about the model, not a formatting convention.

**It needs a derivation of its own because it is read detached from everything
that qualifies it.** The six numeric readouts sit under a heading that names
the agent and calls the values modelled. They sit beside a legend that names
each compartment. They are on a panel whose alveolar entry carries the
`end-tidal-equivalent` gloss that this document requires above. A floating box
carries none of that context. It appears over the plot, and it can cover the
heading that it would otherwise be read under. It is the one place in this
interface where a number is presented with nothing around it. So the box has
to supply for itself every qualifier that the readout row gets from its
surroundings.

**And it is the display a reader has most deliberately stopped to consult.** A
reader glances at a value in the readout row while a run plays. A value under
a cursor is one that somebody went looking for. That makes the hover readout
the display most likely to be written down. It is also the display where being
mistaken for a measurement costs most.

#### What it shows

The box has three lines. The first gives the run context, the second says what
the value is, and the third gives the value.

```
Modelled sevoflurane · 20m8s
Alveolar (end-tidal-equivalent)
1.43%   0.71 ×MAC
```

**The order carries the safety argument. It is not a matter of typography.**
The qualifiers come before the number. So a reader reaches `1.43%` only after
passing "modelled" and the compartment the value belongs to, rather than
meeting them afterwards. `.claude/rules/expert-review.md` states the general
form: prefer an interface that prevents an error to one that warns after it. A
hedge placed below the number it hedges is a warning, because the number has
already been read.

Each line, and the reason it must be there:

1. **Run context: the modelled marker, the agent, the run where more than one
   is drawn, and the instant.** The marker appears on every hover, not only on
   the compartments that have a measured twin. The reason is that the box is
   detached from the heading that would otherwise carry the marker. The agent
   is there because the same percentage means different things under different
   agents. For example, 1.43% is 0.71 MAC of sevoflurane and 0.24 MAC of
   desflurane. A floating box cannot rely on the header being visible behind
   it. The instant is given in the compound form of `format_elapsed`, to the
   hundredth of a second that the chart's columns are laid on. So the printed
   instant is the instant of the state printed beside it, not a rounding of
   it (`PL-T5NJ`). The clock, every control stamp and the time axis use the
   same form.
2. **What the value is: the compartment, with its gloss where the readout row
   has one.** The two glossed compartments are
   `Alveolar (end-tidal-equivalent)` and `Circuit (inspired)`. The other four
   carry no gloss, because the readout row gives them none. Those two glosses
   exist for the two compartments that a clinician would most readily set
   beside a monitor reading. § "Minimum displayed outputs" made that decision,
   and the box reuses it rather than taking it again.
3. **The value, in both units the chart carries.** The value is given as a
   percent and as a MAC multiple, the same pair that the readout panel shows.
   The reason is that the chart itself has two axes, and a single number could
   be read against either one.

**Every number in the box is produced by `app/formatting.py`, never by the
chart library.** The box uses only `format_percent`, `format_mac_multiple` and
`format_elapsed`. The rest of this section exists to justify this rule, and the
rule is not a style preference. A charting library formats a coordinate, and
formatting a coordinate is different from formatting a clinical value. Every
default this project has met formats the coordinate.

The MAC multiple is computed against the snapshot's own `mac_percent`, exactly
as the MAC axis and the readout row compute theirs. A hover that reported a MAC
multiple computed from any other divisor would be the traceability failure that
`CLAUDE.md` forbids. It would arrive through the one display that looks least
like a calculation.

#### The hover and the run it belongs to

**While more than one run is drawn, the first line names the run. While only
one run is drawn, it does not** (project owner, 2026-09-17, ratified, over
giving the run a fourth line of its own and over holding the curve's line width
and the legend to be sufficient).

```
Modelled sevoflurane · Run 2 · 20m8s
Alveolar (end-tidal-equivalent)
1.43%   0.71 ×MAC
```

**The hover is a displayed concentration, so § "Minimum displayed outputs"
already decides the principle**: "The run is named in text, not carried by
colour or by position… Text has no width analogue… A concentration that does
not say which management produced it is the correct number under the wrong
patient context." That paragraph was written about the numeric readouts. Every
reason it gives applies to the hover with more force, not less. The readouts
sit in a labelled block beside the run's own panel. The hover box floats over
the plot with nothing around it. That is the same argument that the start of
this section makes for why the modelled marker travels with the value.

**The argument that the pointer is already over one curve is false, and this
was measured.** At the time, `nearest_trace_point` kept the single globally
nearest drawn point across *every* run on the frame. (`PL-JVHL` retired that
rule, as described below.) Wherever two runs' curves for one compartment run
close together, the pointer is within reach of both runs. The measurement was
made on 2026-09-17 on a branched sevoflurane case. It used the reference adult,
with the trunk held at 1 MAC and the branch forked at 10 min. The axis covered
60 minutes and was 900 px wide and 360 px tall, so the scale was 4.00 s/px and
0.0167 %/px. The table gives the share of the shared axis on which both runs'
points for one compartment sit inside the 12 px hover radius:

| Branch's management at the fork | Alveolar | Fat |
| --- | ---: | ---: |
| doubled to 2 MAC | 1.6% | 100% |
| raised to 1.25 MAC | 8.5% | 100% |
| vaporizer turned off | 1.6% | 100% |

The fat figure is 100% in every case, even against the widest difference in
management that the interface permits. The reason is that the percent axis is
fixed at 3 MAC for every agent (`CHART_AXIS_TOP_MAC`), and the slow
compartments sit near zero on it. Through a case's first hour, fat stays within
about 1% of the axis height. Those slow compartments are the ones this chart
exists to teach. The problem is consequential, not cosmetic. Of the hovers that
could report either run, 83.3–95.3% (alveolar) and 43.8–81.4% (fat) would print
*different* text. On the emergence case, the fat hover at 3492 s shows either
`0.03%   0.02 ×MAC` or `0.01%   <0.01 ×MAC`, depending on which run it
reported. That is a threefold difference in stored agent, between a run still
carrying agent and a run 48 minutes into emergence.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**The run goes on line 1 rather than on a fourth line.** This section already
calls line 1 the *run context*, so naming the run completes that line. It does
not change the three-line form that the rest of this section derives. While two
runs are compared, the run name is also the only token on that line that tells
them apart. `assemble_chart_frame` refuses a frame whose runs differ in agent,
because the runs share one MAC axis and one set of clinical references. So the
agent is the same across the runs being compared. Without the run name, the
line would spend its distinguishing slot on a constant. The one argument for a
fourth line is that a reader scans a separate line but may miss a token in the
middle of a line. That matters because the run under a resting pointer can
change. The answer is that the value on line 3 changes at the same moment, so
the reader has two cues rather than none.

**The run name is conditional, and that is not a hidden mode.** A single run
has nothing to be told apart from. A name on the only run drawn would imply a
comparison that is not on screen. The condition is the same one that the width
channel already uses: `run_trace_style` widens nothing until a second run
exists. The condition is also visible on its face. A second run brings a second
legend entry, a second readout panel and a second set of curves with it. A
reader cannot be in the two-run state without seeing the two runs.

**Naming the run made the choice between runs *visible*. It did not make the
hover report the curve the reader aimed at.** In the measurement above, moving
the pointer by 2 px changed which run the hover reported on 75.4–99.9% of the
fat axis. That is a question of targeting, not of the readout, and the next
subsection describes how it was settled (`PL-JVHL`).

#### Where more than one trace answers

**Every run whose drawn point is inside the hover radius is reported, and the
box carries one value line per run** (project owner, 2026-09-19, ratified, over
breaking near-ties toward the trunk and over leaving the targeting alone until
the axis compression is fixed).

```
Modelled sevoflurane
Alveolar (end-tidal-equivalent)
Run 1 · 20m8s   1.43%   0.71 ×MAC
Run 2 · 20m8s   1.45%   0.73 ×MAC
```

**The rule is "stop choosing". It is that because the two targeting rules that
would have chosen better were measured, and they change nothing.** The rules
were scored on the branched sevoflurane case above, with the reader showing
alveolar and fat. That is the pair that `COMPARED_COMPARTMENT_CAP` admits on a
two-run frame. The metric is narrower than the 75.4–99.9% figure above and
cannot be compared with it. It takes the hovers where both runs are inside the
radius *before and after* a 2 px move, and gives the share of them whose
reported run changed. The earlier figure counts axis columns. This one counts
hovers that could have gone either way.

| Targeting rule | fat, 2 MAC | fat, 1.25 MAC | fat, vaporizer off |
| --- | ---: | ---: | ---: |
| the single globally nearest drawn point | 9.2% | 9.0% | 9.2% |
| nearest curve measured along its length | 9.2% | 9.0% | 9.2% |
| the pointer inside a run's own band, 2 px or 4 px | 9.2% | 9.0% | 9.2% |
| distance, near-ties broken toward the trunk | 0.0% | 0.0% | 0.0% |
| every run inside the radius answers | 0.0% | 0.0% | 0.0% |

The results are identical to the digit, for two reasons. Both reasons are facts
about this chart, not about any implementation. First, the trace is drawn at
about one sample per 4 s against a 12 px radius. So the pointer's distance to
the polyline and its distance to the nearest vertex differ by a fraction of a
pixel. Here, "nearest along its length" gives the same number as
"nearest drawn point", however real the distinction is on a sparse, steep
curve. Second, both runs' fat points are inside the radius over 94.5–98.0% of
the hoverable area. So "inside a run's own band" has to break the tie by the
rule it was meant to replace, exactly where the defect lives.

**Breaking near-ties toward the trunk also reaches 0.0%, and it was refused
because of what it costs.** A tie window does not remove the boundary. It adds
a second boundary, where the pointer crosses out of the window. On the alveolar
trace of the 1.25 MAC case, the tie window raises the share of contended axis
columns that flip from 58.5% to 98.4%. It also makes the branch's value
unreachable wherever the curves lie inside the window, which is most of the fat
trace. A displayed value that a reader cannot reach is worse than one that is
hard to aim at.

**Distance settles nothing, including which compartment is reported** (project
owner, 2026-09-20, ratified, over recording the measurement and leaving the
flip to the axis fix). Before this decision, the nearest drawn point picked the
trace, on the reasoning that a reader aims at a curve. `PL-0RZ0` measured what
the same compression does to that reasoning. Two or more compartments sit
inside the radius over 15.2–45.7% of the two-run chart's hoverable area, and
over 37.0% of the single-run chart's. Across the contended pointer pairs 2 px
apart, the aimed-at compartment changed on 6.6–13.6% of pairs. On 99.9% of
those, the hover printed a different number, by a median of 17.1–17.9× for
muscle against fat.

| Chart | Compartments | Two or more in reach | 2 px flips the compartment |
| --- | --- | ---: | ---: |
| one run | all six | 37.0% | 12.7% |
| two runs, vaporizer off | muscle + fat | 45.7% | 7.5% |
| two runs, 1.25 MAC | muscle + fat | 19.1% | 9.2% |
| two runs, 1.25 MAC | mixed venous + vessel rich | 29.4% | 6.6% |
| two runs, 2 MAC | alveolar + fat | 0.5% | 13.6% |

**There is no aim to respect at that separation**, which is why the reasoning
above did not survive its own measurement. At a flip, the two winning points
are a median 0.9 px apart, and 100% of them are within 2 px. The box hangs from
the aimed-at point, and the two points are this close, so the box does not
move. Only the compartment's name and the
numbers change, and the reader has already read past the name. `PL-QYBW` states
this second consequence in its own terms: at 0.2–1.4 px, no targeting rule can
let a reader aim at one trace rather than another. A rule that picked one would
be picking arbitrarily, not honouring an aim.

**No value became unreachable under the old rule, and recording that is part of
the case.** This section refuses the near-tie tie-break partly because it made
a value unreachable. Measured across the same cases, every compartment was
reported somewhere on 98% or more of the axis columns where it is drawn. The
worst was muscle, at 2.0% on the single-run chart. The defect was that the
reader got the wrong trace, never that a trace could not be reached.
<!-- not-restated: 2.0 % -->

So every run and every compartment whose drawn point is inside the radius is
reported. Nothing is left for a hand movement too small to aim with to decide.
That is what takes the flip rate to zero on both axes.

**The box keeps the form it had wherever one compartment is reported.** That is
54.3–99.5% of hovers across the measured cases, and 63.0% on the single-run
chart. The form is the agent, then the compartment, then one value line per
run. Where the readings span several compartments, one heading cannot stand for
them all, so the compartment heading is dropped. Each value line then opens
with its own compartment, with the gloss that `docs/MODEL.md` requires wherever
a compartment is named. The run follows, while more than one run is drawn:

```
Modelled sevoflurane
Muscle · Run 1 · 20m   0.19%   0.10 ×MAC
Muscle · Run 2 · 20m   0.09%   0.04 ×MAC
Fat · Run 1 · 20m   0.01%   0.01 ×MAC
Fat · Run 2 · 20m   0.01%  <0.01 ×MAC
```

The lines are ordered by compartment first, following the trace table, and then
by run. Both orders are the frame's own drawing order, so the box is read in
the same direction as the legend beside it. The box carries one value line on
21–93% of hovers. It never carries more than four on the two-run chart, or more
than three on the single-run chart. That small number of lines is what made it
affordable to stop choosing here.

**The pointer names the instant, and the radius decides only what is in reach**
(`PL-1K9G`, 2026-09-22). Each run is reported at its drawn instant nearest the
pointer in time, and a tie goes to the earlier instant. Each of the run's
compartments is reported at that instant if its point there is inside the
radius. So every compartment of one run is reported at one instant. Moving the
pointer up or down the percent axis can change what is in reach, but never the
instant that a value is labelled with.

Before that change, each trace kept its own drawn point nearest the pointer,
measured in both dimensions. So on a sloped trace, the pointer's height chose
the column. This was measured on the branched case above. It was also measured
on a two-hour single run, both on its fitted 2-hour axis and on the 12-hour
axis, where a dial change draws a near-vertical step. The scan covered every
pixel of height at four sub-pixel phases per column. Before any number was
kept, the scan's selection was checked against the shipped function:

| Chart | Boxes holding 2+ of one run's readings that mixed instants | Spread, median / max | A vertical 2 px move changed the instant / the printed value |
| --- | ---: | ---: | ---: |
| one run, 60 min | 70.1% | 16 s / 72 s | 44.9% / 35.1% |
| two runs, mixed venous + vessel-rich | 88.3–94.7% | 12–16 s / 32–52 s | 50.6–62.8% / 36.9–52.8% |
| two runs, muscle + fat | 13.0–16.8% | 4 s / 4 s | 3.0–5.4% / 0.3–0.8% |
| one run, 12 h axis | 84.5% | 288 s / 912 s | 37.3% / 33.3% |

<!-- not-restated: 13.0 -->

The premise that made the problem look cosmetic was that two adjacent columns
usually print the same value. That premise holds for fat, and mostly for
muscle, which is the pair on which the problem was first observed. It fails for
the other four compartments. On the 60-minute axis, 44.0–93.3% of adjacent
columns of the circuit, alveolar, mixed venous and vessel-rich traces print
different values. The figure is 3.3–16.0% for muscle and 0.7–1.3% for fat. Nor
was the spread one grid column, as this section used to say. A sloped trace's
nearest point can lie as far to the side as the radius reaches, which is
fifteen minutes on the 12-hour axis. `PL-1K9G` holds the whole scan.

**The radius is measured at the named instant, not to the nearest of the
trace's points.** The alternative was to keep the old reach and report the
point at the named instant. That would also have made the instant depend on the
pointer's time alone, and it would have kept every value that the old rule
reported. But where this rule reports nothing, the alternative would have
reported a point a median 13.5 px and up to 42.5 px from the pointer on the
60-minute axis, and up to 146 px on the 12-hour axis. The dot and the box would
then hang on a value the reader is nowhere near. So every value the box reports
is at the instant the pointer names *and* within reach of the pointer. The cost
is aim beside a steep segment. There, a pointer level with a point several
columns along no longer reports that point. Of the area over which each trace
was reported, 84–100% is kept on the 60-minute and 2-hour axes, and 45–54% for
the four fast compartments on the 12-hour axis. Nothing is reported that the
old rule did not report, and no drawn instant becomes unreachable.

The wash-in plot reports values by the same rule, and it treats a run's
stretches as one set of drawn instants. It draws one trace per run, so no box
there mixed instants. But the same vertical movement moved its one instant on
23.9–44.4% of movements.

**The instant is stated on each line rather than once for the box.** Every
compartment of one run shares the instant, but two runs need not. Each run also
draws the columns that its own control events fall on, and a branch draws no
columns before its fork. So the instants nearest one pointer can differ between
runs. Where both runs are drawn, they can differ by up to one grid column. That
is 4 s on the 60-minute axis and 48 s on the 12-hour one, and `format_elapsed`
shows both. A single instant above a column of values would assert a
simultaneity that the readings do not have. This is the same rule that makes
the modelled marker travel with the value rather than sit in a heading: a
qualifier belongs to the number it qualifies.

**The lines are ordered by run, not by distance**, and so is the box's own
position, which hangs from the point of the first run reported. Ordering by
distance would put this defect back into the layout. The numbers would swap
places under a hand movement too small to aim with, which is what the rule
exists to stop. Run order is the order of the legend and of the readout panels,
so the box is read in the same direction as everything beside it.

**A dot is drawn on every point that is reported**, not one dot for the box. A
single dot would mark one run's curve while the text reported several runs.
That is the attribution failure that § "The hover and the run it belongs to"
closes, arriving through the marker instead of through the words.

**When one run is reported, the box uses the three-line form, unchanged.** Two
runs drawn with only one inside the radius is the ordinary case, because the
reader has aimed successfully. That case gets the form that the rest of this
section derives, still naming the run because two are drawn. The box gaining
and losing a line as the pointer moves is not a hidden mode. It is a display of
what is in reach. A run leaves the radius because the reader moved
deliberately, and the box shows this by losing that run's line. That event is
visible, whereas the silent swap it replaces was not.

**The root cause is the axis, and the axis stays** (project owner, 2026-09-23,
ratified, over a reader-selected logarithmic scale, `PL-QYBW`). The slow
compartments are compressed near zero because the percent axis is fixed at
3 MAC for every agent (`CHART_AXIS_TOP_MAC`). That compression puts two runs' fat
points 0.2–1.4 px apart and makes them contend almost everywhere. Only fat
stays compressed for long. At a 1 MAC dial on the three shipped agents, muscle
spans 25–48 px of the 360 px plot at one hour, and fat spans 1.5–3.7 px. Fat's
trace near zero is its true partial pressure, and partial pressure is what
drives effect. So the chart keeps one linear axis for all six compartments, and
the rule above resolves the contention without a change of scale. What the
trace cannot show is how much agent fat holds: a fifth of the stored agent at
one hour, and a third at three. That is a question of amount, and
planned-milestone item 27's schematic is the view that shows it. A logarithmic
scale was the alternative weighed. Fixed from 0.001 to 3 MAC, it would put the
two runs' fat 23–75 px apart, but it has three costs. It draws below the
0.01-point resolution of § "Displayed precision". It is a display mode on a
chart of clinical values. And it would arrive ahead of the v0.6.0 View contract
that decides where a View's own settings live. Its strongest use, the washout
tail, is a candidate for item 36's catalogue of views rather than a mode on
this chart.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

`chart_frame.format_compared_trace_hover` and
`chart_frame.format_compared_wash_in_hover` produce both forms above. Like
every other number here, they go through `app/formatting.py`, using
`format_percent`, `format_mac_multiple` and `format_elapsed`.
`nearest_trace_point` and `nearest_wash_in_point` collect the traces within
reach at the instant that the pointer names. `tests/unit/test_chart_frame.py`
holds both worked examples above verbatim. Beside them it holds the measured
fat and muscle cases from which the run rule and the compartment rule were
decided, and the geometry from which the instant rule was decided
(`test_every_compartment_of_one_run_answers_at_one_instant`).

#### Resolution: the readouts' derivation applies unchanged

The hover prints two decimals of a percent and two decimals of a MAC multiple,
with the below-resolution forms `<0.01%` and `<0.01 ×MAC`.
§ "Displayed precision" derives both. Nothing in that derivation depends on
where the number appears. The ceiling is one measured standard deviation of a
partition coefficient, which displaces a trajectory rather than a display. The floor is
a teaching judgment about what a reader can learn from the slow compartments.

**The one argument for a finer hover readout is answered here on its own
terms, rather than inherited from the readouts.** That section separates two questions
that a printed digit could be answering. The first is how finely two moments
*within one run* can be told apart. That is about nine decimal places finer
than the readout shows. The second is how finely this model resolves a
concentration *in a patient*, which is much coarser. A hover is closer to the
first question than the readout row is. It reports one trace at one instant,
which is the shape of a within-run comparison, and the within-run question
would justify a third decimal.

The hover does not get a third decimal, for the same reason that settles the
readouts: a reader cannot tell which of the two questions a printed digit is
answering. The hover makes that confusion worse rather than better. It is the
display most likely to be transcribed. It appears over a chart whose whole
subject is a patient. And it is read without the row of five other
compartments, which make it obvious that a within-run comparison is what is on
offer. So the display most exposed to the patient reading is the last one
that should carry a digit that only the within-run reading supports.

**The below-resolution form is required here, not optional.** At 1 MAC
sevoflurane, fat stays below 0.01% for the first thirteen minutes, and muscle
stays below it for the first two. Those minutes are the slow-compartment
wash-in that the chart exists to show. `<0.01%` says what is known. A hover
that printed a number there would claim a resolution the model does not have.
It would do so on the compartment where a reader is least able to notice.

#### What a chart library prints instead, measured

The default matters for two reasons. It is what ships if nothing overrides it.
And both toolkits this project has used default to formatting the coordinate.
`flet_charts.LineChartDataPoint` defaults to a `LineChartDataPointTooltip`
whose `text` this application never writes into. `pyqtgraph.ScatterPlotItem`
defaults `tip`, which is the formatter for the hoverable-points route, to
`'x: {x:.3g}\ny: {y:.3g}\ndata={data}'.format`.

These values were measured on 2026-09-14. The case was the reference adult,
with sevoflurane delivered at 0.02 (1 MAC) and the shipped column budget over
a one-hour axis. `.3g` was applied to the drawn y as `ScatterPlotItem` would
apply it, and `format_percent` was applied to the same value. The table shows
four instants of the first hour:

| Instant | Compartment | `.3g` on the drawn y | This readout |
| --- | --- | ---: | ---: |
| 48.3 s | Alveolar | `0.262` | `0.26%` |
| 48.3 s | Muscle | `0.000656` | `<0.01%` |
| 48.3 s | Fat | `3.52e-05` | `<0.01%` |
| 289.9 s | Fat | `0.00116` | `<0.01%` |
| 1208.1 s | Fat | `0.00888` | `0.01%` |
| 3600.0 s | Alveolar | `1.54` | `1.54%` |

The default has three separate defects, and the third is the one that would
go unnoticed:

- **Resolution.** `3.52e-05` carries five decimal places beyond the resolution
  that this document derives. It does so on the compartment where the readout
  row deliberately refuses to print a number at all. A reader comparing the
  hover with the panel would find the two disagreeing about whether the value
  is known.
- **Units.** `.3g` prints no unit. The chart carries a percent axis and a MAC
  axis. So a bare `1.54` could belong to either of two scales, which differ by
  a factor of about two for sevoflurane. `3.52e-05` is worse, because it reads
  equally well as a fraction of an atmosphere, which is a hundredfold out.
- **A varying number of decimals.** Three significant figures give two
  decimals at `1.54`, three at `0.262` and six at `0.000656`. The readout row
  is fixed at two decimals. The whole of § "Displayed precision" is the
  argument for a *uniform* resolution. A display whose precision changes with
  the size of the value it shows claims that the model resolves small values
  more finely than large ones. That is the opposite of the truth.

#### Which series answer a hover, and which do not

The six compartment traces respond to a hover, in the form above. The wash-in
trace responds in its own units, because $`F_A/F_I`$ is dimensionless and has
neither a percent nor a MAC reading:

```
Modelled sevoflurane · 20m8s
Wash-in F_A/F_I (alveolar / modelled circuit)
0.71
```

`format_wash_in_ratio` produces the number. The parenthesis is the caption that
`app/wash_in.py` already carries, for the reason stated there: $`F_I`$ is the
modelled circuit rather than the vaporizer dial. The caption uses a solidus
rather than a division sign, because every non-ASCII character that reaches a
reader must have been rendered and seen first (`tools/glyph_check.py`), and the
division sign has not been.

**The clinical references and the control marks do not respond to a hover,
and the reason is interaction rather than content.** The 1 MAC line spans the
plot horizontally, and the MAC-awake band is a horizontal region. The control
marks are vertical and full height. All three cross every trace. Making them
hoverable would therefore put an annotation under the pointer whenever a
reader aims at a trace that passes behind one. And the annotations are exactly
where a reader is most likely to want a reading, since a trace crossing 1 MAC
is the event that the reference is drawn for. What they would report is also
already on screen. The divisor is stated beside the chart, and the input
timeline lists each control change with its old and new value.

#### When it answers

The hover responds whenever the pointer is over the plot, whether the run is
playing or paused.

**This reverses a restriction that came from the toolkit rather than from the
affordance.** `PL-KP7H` withdrew the hover while a run plays. The reason was
that Flet's control-tree diff descends into every point's tooltip object on
every frame, and the tooltips were half the cost of a saturated frame. A hover
that responds only while paused is a hidden mode. A reader who tries it during
a run gets nothing, concludes that the chart is not interactive, and never
finds the hover again.

Qt has no such cost to avoid, by either route the readout could be built on. A
crosshair is driven by the scene's own `sigMouseMoved`, rate-limited through a
`SignalProxy`. Hoverable points carry a `tip` callable that is evaluated when
the pointer arrives, rather than a tooltip object stored for each point. Both
routes cost work per pointer event, and neither cost depends on how many
points are drawn. Nothing has to be withdrawn, so there is no mode to announce
and no caption to write. The affordance is discoverable because it is present.

**The hover is not a default, though, and that has to be checked rather than
assumed.** `ScatterPlotItem` ships with `hoverable` set to `False`, and a
plotted line carries no hover of its own at all. So a port that says nothing
about the hover loses it outright rather than inheriting it. The Qt build owes
the hover under the parity rule "Every capability the Flet build has, the Qt
build has".

At high playback speed, the reported value moves as the run does. That is
correct, not a defect to design around. Every other readout in the interface
moves too, and a reader who wants to study a value pauses, as they would in
any case. What is not acceptable is the affordance being absent while the
reader looks for it.

**The hover responds only to a pointer that is actually there.** Leaving the
plot takes the box down at once, along with any pointer move still waiting to
be handled. So a value that moves with the run is always one that the reader
is pointing at. If the box stayed up at the last point the pointer crossed, it
would recompute its value every frame. While a run played, it would climb with
the run like a live readout of the state being watched, for an instant that
nobody is looking at (`PL-LTKL`).

**Built on pyqtgraph, over the drawn points within a pixel radius**
(`PL-G59B`, 2026-09-14). The radius stopped choosing between runs with
`PL-JVHL` (2026-09-19) and between compartments with `PL-0RZ0` (2026-09-20).
The pointer's height stopped choosing the instant with `PL-1K9G`
(2026-09-22). `app/chart_frame.py` holds the derivation above as code.
`format_trace_hover` and `format_wash_in_hover` produce the three-line form,
and `format_compared_trace_hover` and `format_compared_wash_in_hover` produce
the compared one. `nearest_trace_point` responds only for a compartment that
the reader has left shown. It also responds only within a pixel radius of the
point that the plot draws at the instant the pointer names. `app/qt_chart.py`
shows the readout wherever the pointer is, running or paused. Every instant
that the readout prints is stated at the step by which the run advances,
`HOVER_INSTANT_RESOLUTION_S`. A drawn column sits wherever the anchored grid
puts it, and the state reported is the state at exactly that instant. But
printing the instant to four decimals would claim a resolution that no other
display on the screen has. `tests/unit/test_chart_frame.py` holds both worked
examples above verbatim, and `tests/integration/test_qt_chart.py` tests the
rendered readout against a real run.

### A preview of an unapplied setting

While a learner holds a slider's thumb, the chart draws the trajectory that the
run would take if the value under the thumb were applied where the run stands
now (`PL-5B1N`). This section says what that drawing is, how it is computed and
what it may imply.

**A preview is a third kind of value.** It is not a modelled state of the run,
because the run has not passed through it. It is not a measurement either. It
is a prediction, conditional on a setting that the learner has not applied and
may never apply. A preview drawn with the run's weight and no label would read
as a run that happened. So everything below exists to keep it from reading
that way.

**How it is computed.** `SimulationController.preview_window` opens a second
run definition at the run's reach. It starts from the run's canonical state
there (§ "The canonical evaluation rule"), under the settings that applying the
value would give. Those settings are built the way a branch builds its own: a
trial run is rebuilt from the settings in force, checked to hold every value
the run holds, and given the value through its own setter
(`SimulationController.preview_settings`). So the value is checked by the core
setter that would apply it, and a cardiac output moves every tissue flow
exactly as applying it would. It is the same model and version as the run, it
is deterministic, and nothing of the run is written. At the run's own setting
the preview coincides with what the run then draws, to within floating-point
composition error. The preview is evaluated on the run's own grid. It ends at
the axis's right edge, or at the end of the supported run length if that comes
first. While the run plays, it is evaluated again on every frame from the run's
new reach.

**Four cues mark it, and none of them is colour.**

1. **Position.** The preview lies wholly to the right of the run's reach,
   inside a tinted region. The region's left edge is a stroke at the reach,
   where the run stands now. The run that the preview belongs to never enters
   the region.
2. **A label in the plot**, such as "Preview: Fresh gas flow 6.0 L/min, not
   applied". It names the control and the value tried in the slider's own
   words, and it names the run while runs are compared. It is drawn inside
   the region, so a screenshot taken during a drag carries it.
3. **Width.** Each preview curve is one pixel thinner than a lone run's curve
   of the same compartment, and never thinner than 2 px, below which an
   antialiased line renders under 3:1 against the panel
   (§ "The six compartment traces: what separates them"). The two 3 px traces
   preview at 2 px. The four 2 px traces preview at 2 px, so for them the other
   three cues carry the distinction. In compare mode the first run is drawn one
   step wider, but its preview keeps the lone-run width. Otherwise the preview
   would be wider than the other run's real curve of the same compartment, and
   the width cue would point the wrong way.
4. **Binding to the drag.** The preview exists only while the thumb is held.
   It appears when the thumb is pressed, and the frame drawn at the release no
   longer has it. Nothing decays or lingers.

**The curves keep each compartment's colour and dash pattern, deliberately.**
Those two channels are what tell the six compartments apart, and inside the
preview they have to do the same work. Dash pattern cannot carry "predicted"
instead: the muscle trace is already dotted, and a solid run with a dotted
preview would flatten the five dashed traces into one style. Reduced opacity
cannot carry it either. Blended over the panel at 0.85 opacity, the alveolar
and muscle traces fall to 2.93 and 2.83 against it, under SC 1.4.11's 3:1, and
at 0.75 four of the six do. The region's fill is decoration, on the same ground
as the MAC-awake band's: its edge and the label carry the information
(`theme.PREVIEW_REGION_FILL_OPACITY`).

**What a drag does to the run.** A pointer drag applies its value when the thumb
is released, and the control-input timeline records one change there. Until
then the run keeps the setting in force, and the value printed beside the
slider is that setting. The value is applied before the preview ends, so the
frame drawn at the release shows the run under its new setting. A key press, a wheel step or a click on the groove is
one discrete input, so it applies at once and draws no preview.

**The window keeps its width during a preview.** It slides so that the run's
reach sits at mid-plot: half the window shows the run that happened, and half
shows the prediction (`chart_time_base.preview_window`). Early in a run the
window stops at zero, and the reach sits left of the middle. Widening the axis
to make room would rescale every slope, which § "The chart's time base"
refuses. The window returns to following the run at the release.

**What a preview does not do.** The hover never answers from it, so no value on
a preview curve is ever printed as a reading. A preview that goes above the
top of the concentration axis is cut off there, as a run's trace is. The
off-scale notice then names each clipped prediction with its highest
predicted value in view, because the readouts give only the run's values
(`dashboard_frame.PREVIEW_OFF_SCALE_NOTICE_TEMPLATE`). A predicted F_A/F_I
stretch that stops ends in a dot, by the same rule as the run's. A stopped run, failed or at the
supported run length, refuses every setting and draws no preview. Both plots
draw it: the F_A/F_I plot shows the predicted ratio, so the two plots never
show two different futures. Each compared run has its own controls, so only
the run whose thumb is held previews, and the window centres on that run's
reach. A compared run further along may then be drawn inside the region; the
label names the run the preview belongs to.

### A cost at the reader's price

This section specifies what a stored agent price carries, and what a readout
that shows a cost must show beside it (`PL-VJZK`). `app/preferences.py`
stores a price (`PL-93B3`). The agent cost View shows the cost, and its form
sets the price (`PL-1P15`, `app/agent_cost.py`).

**A price is neither modelled nor measured.** This document separates
modelled values from measured ones, and every value the interface shows today
is modelled. A price is a third kind of value: a number the reader supplies.
A cost multiplies a modelled amount by that number. A wrong price therefore
makes a correct amount lead to a wrong conclusion. So the readout must show
which part of a cost is the model's and which part is the reader's. That is
why the safety standard in `CLAUDE.md` applies to a cost, although money is
not a clinical quantity.

**The project ships no price.** A shipped price goes stale, and it differs
from one institution to the next. The reference implementation shows both
problems. Gas Man's parameter file prices isoflurane at $20.47 for a 100 mL
bottle (Philip JH, *Workbook for Gas Man*, Appendix C, printed p. 171). The
book calls its defaults "USA bottle volume and bottle cost as of March 5, 2008"
(printed p. 105). Chapter 14 gives $78.00 per 100 mL bottle "on March 5, 2008"
(printed p. 141). Chapter 14's first exercise prints its costs beside the
price they used, "a bottle cost of US$20.47 per 100 ml" (printed p. 134). The
costs of both isoflurane exercises are reproduced at that price
(`tests/reference/test_published_vapour_to_liquid.py`). Without the price
beside them, a reader could not tell which of the two prices produced those
costs. So, until the reader sets a price, the readout says that no price is
set, and it shows no cost.

**What a stored price carries.** The store holds at most one price for each
agent. Each price records five things:

- the agent it prices;
- the price of one bottle, in the price's currency;
- the volume of that bottle, in millilitres of liquid agent;
- the currency, as its three-letter ISO 4217 code, such as `USD` or `EUR`;
  and
- the date on which the price applied, as an ISO 8601 calendar date, such as
  `2008-03-05`. The reader gives it, and the entry offers the day of entry
  for the reader to change. A price goes stale from the day it was quoted,
  not from the day it was typed in, so the date records the quote.

Every stored price is the reader's own, because the project ships none. So
the record has no field that says who set the price. If a release ever ships
a default price, the record gains that field. The readout must then mark a
default price as one the project supplied, with its date.

**The price is taken per bottle, and the price per millilitre is derived**
(decided by `PL-VJZK` on 2026-10-26, over asking for a price per millilitre).
An institution buys agent by the bottle, and its pharmacy quotes a price per
bottle. Gas Man's Set Cost command takes "the bottle volume and bottle cost"
in the same way (printed p. 15). A field that asked for a price per
millilitre would make the reader divide first. A bottle price typed into such
a field would multiply every cost by the bottle's volume in millilitres. That
volume is 100 to 250 for the volatile agents in Gas Man's defaults (printed
pp. 171-172). Taking the bottle price and the bottle volume removes that
mistake. The per-bottle form still allows three mistakes of its own. A price
per millilitre typed as the bottle price gives a cost 100 to 250 times too
low. A bottle volume typed in litres, such as 0.25, or as 1 for one bottle,
gives a cost 100 to 1000 times too high. Swapping the price and the volume
inverts the price per millilitre. So the field for the bottle volume names its
unit, millilitres of liquid. The readout also shows the price per millilitre
that the two figures give. Each of the first two mistakes makes that price 100
to 1000 times the true one. A swap shows only where the two numbers differ
widely. At Gas Man's sevoflurane default of 240.34 for a 250 mL bottle
(printed p. 172), a swap changes the cost by 8 %, and nothing on screen would
show it. One function derives the price per millilitre from the two
stored figures. The store never holds it, so it cannot disagree with them.
The store refuses no positive finite bottle volume, whatever its size,
because no source gives the sizes in which the agents are sold (`PL-93B3`,
2026-11-01). A volume typed in litres or as a count of bottles is caught on
screen instead: it makes the price per millilitre, which the readout shows
beside every cost, 100 to 1000 times the true one.

<!-- not-restated: 8 % -->

**Why a currency code, and why that form of date.** The sign "$" names the
United States, Canadian and Australian dollars, among others. So a cost in "$"
does not say which currency it is in. Gas Man shows the problem: its parameter
file labels each bottle cost "Bottle cost in $US" (printed p. 171), while its
menu says the cost is typed "in the local currency" (printed p. 15). An
ISO 4217 code names exactly one currency. A date written 03/05/2008 means
March or May depending on the reader's country, and the ISO 8601 form
2008-03-05 does not. Both standards are cited here by their numbers,
ISO 4217:2015 and ISO 8601-1:2019, and neither was read for this section.

**What the store refuses.** It refuses a bottle price or a bottle volume that
is not a positive finite number. A price of zero is refused too, because it is
far more likely to be an empty field than an agent given away. It refuses a
currency that is not three capital letters, and a date that is not a real
calendar date. It refuses each of these when the reader enters it, and again
when it reads the preferences file. A refused entry leaves the stored price
as it was, so the readout goes on showing the cost at that earlier price, with
that price beside it. A price refused when the preferences file is read is not
used, and it is never replaced by a default. The readout then says that no
valid price is set for the agent.
The store does not also check the three letters against the codes that
ISO 4217 assigns (`PL-93B3`, 2026-11-01). That list changes several times a
year, so the check would need a dated copy of it with its own provenance, and
a copy that fell out of date would refuse a real currency. Any three letters
remove the ambiguity of "$", and a mistyped code is shown beside every cost and
price, where the reader sees it.

**What a cost readout shows.** A cost is never shown alone. Beside it, the
readout shows these six things:

1. the delivered agent in millilitres of liquid equivalent, labelled as
   delivered and as liquid. This is the modelled figure that the cost
   multiplies. It stays on screen, so that a number the reader supplied is
   never the only carrier of a modelled quantity. This holds even where the
   reader has chosen to show the View's amounts in litres of vapour
   (`ROADMAP.md`, v0.7.0 entry 8);
2. the price per millilitre of liquid that it multiplied by, so that a reader
   can check the product by eye;
3. the bottle price and the bottle volume that the price per millilitre came
   from;
4. the currency's code, on the cost and on each price;
5. the date on which the price applied; and
6. words saying that the cost is at the reader's price. Words are required,
   not only a colour or a style, so that the statement reaches every reader.

A bare "mL" does not say enough. The schematic labels its amounts in
millilitres of vapour (`ROADMAP.md`, v0.7.0 entry 1), and Gas Man prices
"Cost/mL vapor" (printed p. 174). One millilitre of liquid isoflurane gives
about 196 mL of vapour, so a volume or a price read as vapour is wrong by that
factor. For Gas Man's Exercise 14-1 at 60 min, the readout could read
"39.4 mL of liquid x USD 0.2047 per mL of liquid = USD 8.07, at your
price of USD 20.47 per 100 mL bottle, as of 2008-03-05". The wording and the
layout are placeholders, and the six facts are the requirement. The book
prints $8.06, because Gas Man rounds isoflurane's vapour-to-liquid ratio to
196 (§ "Agent amount").

**How the cost is computed.** The cost is the delivered agent's liquid
equivalent times the price per millilitre. The delivered agent is the basis,
because it is what left the bottle (`ROADMAP.md`, planned-milestone item 28,
and `PL-H4N8`). § "Agent amount" converts the delivered agent to liquid
exactly. The price is the one stored for the agent whose amount is priced.
The cost depends only on the delivered amount, the agent's vapour-to-liquid
ratio and the stored price. The date is shown and never used in the
arithmetic, and nothing reads the clock to compute a cost. The cost is
computed from the unrounded liquid volume and price per millilitre, and it is
rounded only for display. So the product of the two figures shown beside it
can differ from the cost. The difference is at most half a unit of the
volume's last shown digit times the price per millilitre, plus the volume
times half a unit of the price's last shown digit. Desflurane at USD 115.13
per 240 mL bottle, run at 6 % and 1 L/min for 60 min, costs USD 8.23. Shown as
17.2 mL and USD 0.4797 per mL, the two figures multiply to USD 8.25.

<!-- not-restated: 6 % -->

**When no cost is shown.** The readout shows no cost, and says why, in each
of these cases:

- no price is set for the agent;
- the stored price was refused;
- the price per millilitre is not a positive finite number, or the cost is
  not finite, which entries such as a bottle price of 1e308 for a 0.5 mL
  bottle can cause; or
- the delivered amount cannot be converted to liquid (§ "Agent amount").

It never shows a cost of zero in place of one of these cases. It never shows
a cost left over from an earlier instant, another agent or an earlier price.
A change to the price redraws the cost at once, whether or not the run is
advancing. The cost and the facts shown beside it are read from one price
record, so they cannot come from two different prices. When two runs
are compared, each run's cost uses the price of its own agent. A cost is
never added to, or subtracted from, a cost in another currency.

**Displayed precision.** How many decimals a cost can justify depends on the
price, so it is not a count of decimals (`PL-0S0V`). § "Displayed precision"
derives two precisions, in its paragraph on a cost and a price per millilitre: the cost
is shown to three significant figures and never finer than a hundredth, and
the price per millilitre to four significant figures. The product of the
figures shown can still differ from the cost by more than one unit of its
last digit, because the liquid volume is shown to 0.1 mL. So the readout
always says that the figures beside the cost are rounded, and that the cost
is computed before rounding (`PL-1P15`).

**What the form takes.** The reader types the bottle price and the bottle
volume as digits with at most one decimal point. A sign, an exponent, a
thousands separator or a decimal comma is refused rather than guessed at,
because "1,250" could mean 1250 or 1.25. A refused entry changes nothing, and
the form says why. The date field writes the date as ISO 8601 does, and starts
at the day of entry.

**Tests.** The two rows in the hazard table (§ "Reasonably foreseeable misuse,
and the hazards the presentation carries") name the tests that enforce this
section. `test_the_displayed_cost_reproduces_gas_man_s_printed_costs` runs both
of Gas Man's isoflurane exercises from the patient inputs to the drawn cost,
at the book's price, and checks the four printed costs.

### The compartment schematic: what its heights, amounts and share bar assert

The compartment schematic draws the circuit, the alveoli, venous blood, the
vessel-rich group, muscle and fat as containers, in the readout row's order
(`PL-RNYV`). This subsection says what each mark on it asserts,
before any of it is drawn (`PL-2881`, 2026-11-01). It also governs every
other View that shows an agent amount: the schematic's share bar (`PL-S79P`)
and the agent cost View (`PL-B396`). Gas Man's Picture draws the same
containers to show where the tension is. This schematic adds the amounts and
the share bar to show where the agent is, which the readouts and the chart do
not show. `ROADMAP.md` § "v0.7.0 - the schematic" records that design and
what it was chosen over.

**A container's fill height is the compartment's modelled tension, and it is
not an amount.** Every container of one run fills against one scale. That
scale is the concentration chart's percent axis, from zero at the bottom to
`chart_axis_top_percent` at the top, which is 3 MAC of the running agent for
every agent (`CHART_AXIS_TOP_MAC`). So a height on the schematic and a height
on the chart are the same tension, and a learner who moves between the two
Views reads one ruler. The schematic reads the top from that function and
does not choose a second one. A container that holds more agent can stand
lower than one that holds less. With sevoflurane at a 1 MAC dial, fat stands
at 0.03% atm at 60 min, under 1% of its container's height, while it holds a
fifth of the stored agent (`ROADMAP.md` § "v0.7.0 - the schematic").
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

Every container is drawn at one width, so its filled area is not an amount
either. Drawn to scale, fat's container would take about 500 px of a View
600 px wide, and four of the others between 1 and 7 px each, which is why
`ROADMAP.md` records that drawing to scale was refused. A tension above the
top of the scale fills its container to the top and is marked as off the
scale, as the chart names a clipped trace in its off-scale notice. The
container's label still prints the tension, so no value is lost. A
sevoflurane dial at its 8% maximum puts the circuit at 4 MAC, so this case is
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
reachable.

**A container's amount is the compartment's modelled agent, and its label says
it is vapour.** The amount is $`M_x`$ of § "Agent amount": the equivalent
volume of pure agent vapour at 20 °C and 760 mmHg, dry, shown in millilitres.
It is a statement about the model's store, not about gas in the body. The
agent in blood and fat is dissolved, and the reference condition names the
unit, not where any of the gas is. Each amount is read from the snapshot's
record for its compartment (`PL-KFTM`), which reads that compartment's
`agent_amount_l` in `core/`. The schematic does not compute an amount of its
own. Its precision is derived in § "Displayed precision".

**How the interface names the unit of an agent amount, once for every View.**
Two units count agent in millilitres, and they differ by a factor of about
180 to 210, by agent. At the reference condition, 1 mL of liquid gives about
183 mL of sevoflurane vapour and about 210 mL of desflurane vapour
(§ "Agent amount"). So no View prints a bare "mL" beside an
agent amount. A vapour amount is written "mL vapour", as in "38 mL vapour". A
liquid amount is written "mL of liquid", as in "4.2 mL of liquid". The model
holds no liquid, so this figure is worked out: it is the volume of liquid
agent that would give that much vapour, which is what a vaporizer uses up.
The spelling was "mL liquid equiv." until the project owner found it awkward
on 2026-11-01. The caption under the figure says that the vaporizer used
this liquid. `DisplayUnit` in `app/display_units.py` holds each spelling,
from the first View that prints it, so every View reads it there and none
writes its own. The schematic added "mL vapour" (`PL-RNYV`). The wording is a
placeholder while the interface is being built. The rule is not: every
spelling of an agent amount's unit names vapour or liquid. The accounting
View's litres keep their caption, "Litres of equivalent pure agent gas", which
names the vapour in other words.

**What the share bar shows.** The schematic has one bar, divided into six
segments in the containers' order. Each segment's length is that
compartment's amount as a share of all the agent the run holds, circuit
included:

```math
s_x = \frac{M_x}{\sum_y M_y}
```

The sum runs over the six compartments, and it is the snapshot's
`stored_agent_l`. So the six shares fill the whole bar. Each segment is named
in text, never by colour alone. A share printed in text is shown in whole
percent, derived in § "Displayed precision". When a run starts, it holds no
agent, so no share exists. The bar is then drawn empty and prints no share,
rather than dividing by zero or showing six zeros as if they were shares. The
bar is used instead of the containers' areas because a position along a
common scale is judged more accurately than an area (Cleveland WS, McGill R,
"Graphical perception: theory, experimentation, and application to the
development of graphical methods", *J Am Stat Assoc* 1984;79(387):531-554,
https://doi.org/10.1080/01621459.1984.10478080). Only the first segment
starts at the bar's baseline. Each of the others is judged by its length,
which their ranking still places above area.

**How the containers are joined.** The containers stand in one row, in the
readout row's order. A line joins the circuit to the alveoli, which is
ventilation. A line above the row carries arterial blood from the alveoli to
each tissue group, and a line below it carries each tissue group's venous
blood to the venous container, which a line joins back to the alveoli. So the
three tissue groups are drawn in parallel, as § "Assumptions" perfuses them.
A row of containers joined one to the next would draw agent passing from the
vessel-rich group through muscle into fat, which is the intertissue route this
model omits (`PL-RNYV`). Each schematic shows its run's current instant, and
the line over it states that instant as the readouts' clock prints it. Two
compared runs can stand at different times, as a branch taken at an earlier
mark does, so a difference between two schematics may be elapsed time rather
than the change the branch made. The run writes its schematic where it writes
its readouts, from the same snapshot, and withholds the schematic's values
where it withholds the readouts', after a Reset or an agent change that no
frame has been drawn since. While runs are compared, the same line names the
run, as the hazard table's row on reading one run's value as the other's
requires.

**Why no container is drawn for arterial blood.** This model gives arterial
blood no volume, capacity or amount of its own, because
$`F_a \equiv F_A`$ at every instant (§ "Blood compartments"). Gas Man's
Picture draws an arterial container. Here it would show agent that the model
does not hold, and its segment on the share bar would be a share of nothing.
Arterial tension equals alveolar tension, which the alveolar container
already shows.

**What the schematic does not assert.** Every height, amount and share on it
is a model output, so the schematic carries the interpretation statement,
"Model outputs — not measurements.", once, in its own heading, as the readout
section does. No amount is a prediction about a patient to its last digit,
for the reason § "Displayed precision" gives for the readouts.

## Assumptions

This model assumes:

- every modeled compartment is perfectly mixed;
- each tissue group's exchange with blood is perfusion-limited, and the group
  exchanges agent only with the blood flowing through it. No agent passes directly from one tissue group to
  another, which is the intertissue diffusion that "Known limitations" lists
  as omitted;
- partition coefficients are constant;
- tissue volumes and flow fractions are constant;
- outgoing pulmonary blood equilibrates with alveolar gas;
- the alveolar gas volume is constant. Uptake removes agent from the
  compartment without removing volume from it, and no inspired flow replaces
  the gas taken up. This assumption excludes nitrous oxide, simultaneous
  gases, and the concentration and second-gas effects. "Alveolar gas" gives
  the size of the error and what lifting the assumption would take;
- inspired gas is circuit gas. One modeled gas concentration, $`F_I`$, lies
  between the vaporizer and the alveoli, because there is one perfectly mixed
  circuit with no dead space and no separate limbs (see § "Model boundary");
- the breathing system is a semi-closed circle whose surplus gas valve is
  open. Exhaust outflow equals fresh-gas inflow at every instant, so one fresh
  gas flow, $`\dot V_F`$, is both the delivery rate and the removal rate (see
  § "Breathing circuit");
- inspired gas reaches the alveoli undiluted by water vapour, because the
  modeled alveoli hold no water. Real alveolar gas is saturated at body
  temperature. This is what "dry" means in the reference condition that "Agent
  amount" states. "Known limitations" gives its size, 47/760, and what
  correcting it would cost;
- tissue venous blood equilibrates with its tissue group;
- carrier gases do not affect agent kinetics;
- temperature is constant. Every stored gas volume is at the one reference
  condition that "Agent amount" states: 20 °C and 760 mmHg, dry. No equation
  converts between ambient and body conditions. "Known limitations" sizes
  what that costs;
- ambient pressure is constant at one atmosphere, 760 mmHg. Every
  concentration in this model is a fraction of that pressure, so the model is
  specified at sea level and nowhere else (see the note below this list);
- there is no metabolism;
- there is no chemical degradation;
- there is no anesthetic reaction with circuit materials;
- there is no vaporizer or machine delivery delay beyond the modeled circuit;
- settings remain constant within each numerical step; and
- the selected reference patient does not change physiologically during a run.

**At one atmosphere, a fraction and a partial pressure are interchangeable.**
They differ only by a factor of the ambient pressure, so with that pressure
fixed at 760 mmHg, $`F_A = 0.02`$ is 15.2 mmHg. The model relies on this in
three places. "Concentrations" stores every modeled concentration as a fraction
with no unit, the interface displays each one as a percent of one atmosphere,
and $`\mathrm{MAC}_\%`$ divides one sea-level percent by another.

**The delivered-concentration control depends on it most.** The control is a
vaporizer dial setting, not a modeled gas concentration. A dial position means
a partial pressure, the quantity that produces the anesthetic effect, only once
the ambient pressure is known. At 760 mmHg it means the same partial pressure
whichever class of vaporizer the dial belongs to, so no equation, stored value
or displayed number here is wrong at sea level. Away from 760 mmHg the two
classes diverge in opposite directions, which limits where the model applies.
§ "Known limitations" below describes it.

**For developers.** The control is `app/control_record.py`'s
`ControlInput.DELIVERED`, and its recorded changes carry the unit *percent of
1 atm*. The model has no device-class parameter, which is not a defect at sea
level. A model that adds ambient pressure will need one.

## Known limitations

This model does not model:

- a separate arterial blood-mixing compartment. The lung's exchange with blood
  is perfusion-limited, and the model omits shunt and ventilation-perfusion
  mismatch (both below). So arterial blood carries the alveolar partial
  pressure at every instant, as in the Gas Man reference simulator's
  mammillary structure (see § "Model boundary");
- lung tissue and pulmonary blood. No compartment represents either, and
  together they are a store worth about a fifth of every agent's fast pool
  (sized below);
- a vessel-poor tissue group. Bone, cartilage, ligament, tendon and the other
  tissues with little or no blood flow have no compartment, and none of the
  three tissue groups stands for them (the reason is below);
- halothane, enflurane, ether, or xenon. The modeled agents are sevoflurane,
  isoflurane and desflurane (see § "Parameter provenance");
- nitrous oxide;
- simultaneous gases;
- concentration or second-gas effects;
- absorption of agent by the breathing circuit's own plastics and rubber,
  whose size depends strongly on the agent (measured below);
- vaporizer interlocks;
- switching between volatile agents;
- direct anesthetic injection;
- automated end-tidal control;
- closed-circuit operation, or any machine mode that shuts the surplus gas
  valve. In this model, gas leaves through the exhaust whenever fresh gas flows
  in, and a closed circuit would need a different balance of agent in and out
  (§ "Breathing circuit" gives the reasoning and sizes the gap);
- dead space;
- airway sampling delay;
- multiple alveolar units;
- shunt;
- ventilation-perfusion mismatch;
- diffusion-limited exchange, in the lung or in a tissue group (§ "Model
  boundary" defines it);
- intertissue diffusion, which is agent passing directly from a lean tissue
  into fat lying against it. It is a route between two tissues, separate from
  the blood-to-tissue diffusion limitation above (measured below);
- uncertainty in the tissue:gas partition coefficients. Each is carried as
  an exact value. The stored values are Gas Man's, which differ by up to 9%
  from the means of the one laboratory they come from. Other laboratories
  report values for the same tissue that differ by up to 150% (below, with the
  tissues each difference applies to);
- metabolism;
- compound A or other degradation products;
- renal or hepatic dysfunction;
- cardiopulmonary bypass;
- ECMO;
- hypothermia;
- alveolar humidification. Real alveolar gas is saturated with water vapour
  at 47 mmHg, and the modeled alveolus holds none, so no inspired fraction is
  diluted when it reaches the alveolus (sized below, with what correcting it
  would cost);
- the difference between ambient and body conditions. Every gas volume is
  carried at the single reference condition that "Agent amount" fixes, and no
  ambient-to-body correction is applied anywhere (sized below);
- altitude, or any ambient pressure other than the 760 mmHg fixed under
  § "Assumptions" (what that excludes is below);
- age-dependent MAC;
- individual variation in awakening concentration. The chart's MAC-awake band
  is a population value at one standard deviation, never a threshold for the
  simulated patient (see § "MAC-awake as a chart reference");
- anesthetic potency;
- BIS, eBIS, or hypnosis;
- nociceptive response;
- hemodynamic response;
- IV anesthetics;
- effect-site models;
- clinical alarms;
- dosing recommendations; or
- patient-specific clinical predictions.

**Three of those bullets are one constraint, not three omissions.** Nitrous
oxide, simultaneous gases, and concentration or second-gas effects are all
blocked by the fixed alveolar volume that "Alveolar gas" and "Assumptions"
declare. Adding nitrous oxide without lifting that constraint would give an
$`F_A`$ curve that looks plausible but is wrong by tens of percent through
induction. "Alveolar gas" gives the arithmetic, and the two standard
formulations that lift the constraint.

**Lung tissue and pulmonary blood are an omitted store worth about a fifth of
the fast pool.** On round physiologic figures, 1 kg of lung tissue with a
tissue:blood ratio of 1.2, and 1.8 L of pulmonary and arterial blood, the store
is worth 20.1% of desflurane's fast pool, 19.7% of sevoflurane's and 23.4% of
isoflurane's.

The store takes up agent in the first minutes of wash-in, but it equilibrates
fully within about thirty minutes. So it barely changes $`F_A/F_I`$ at 30
minutes, the value compared with the published wash-in data. It acts mainly
early in an elimination, and only a run with the rebreathing circuit removed
showed it. "Desflurane's residual, and why the parameter file was not changed"
weighs these figures against the other explanations of desflurane's
five-minute washout disagreement, described below.

**The vessel-poor group is left out because it takes up almost no agent, and
Eger's own model leaves it out for that reason.** Eger grouped the body's
tissues into four groups by their capacity and their blood flow: vessel-rich,
muscle, fat and vessel-poor. His later five-compartment model keeps the first
three. It deletes the vessel-poor group "because its contribution to uptake is
considered insignificant", and adds a lung compartment and an
intertissue-diffusion compartment instead (Carpenter et al. 1986, as Hendrickx
and De Wolf report it on p. 163). Eger and Saidman give the physiological
reason. The group is "made up of ligaments, tendons, cartilage, bone, and
other avascular tissues", and it "does not contribute to uptake because of its
minimal or absent perfusion" (p. 1023). Gas Man, the reference simulator, also
has exactly three tissue groups (the Workbook's Model Parameters table,
p. 168).

So the three groups here are Eger's five-compartment model without its lung
and intertissue-diffusion compartments, which the list above names as
omissions. The three groups hold 6.0, 33.0 and 14.5 L, which is 53.5 L in a
70 kg reference patient. That total is the sum of three compartments, not a
body composition. The rest of the body, including the vessel-poor tissues, is
not a store that this model fills or empties.
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.volume_l = 6 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.fat.volume_l = 14.5 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->
<!-- derived: 53.5 L from data/patients/reference_adult.json tissue_groups.vessel_rich.volume_l = 6, tissue_groups.muscle.volume_l = 33, tissue_groups.fat.volume_l = 14.5 -->

Nothing in this project measures what the omission costs. The case that it is
small rests on perfusion: a tissue that receives almost no blood receives
almost no agent over any case this simulator teaches. Hendrickx and De Wolf's
p. 163 and Eger and Saidman's p. 1023 were read in full text. Carpenter et
al.'s full text has not been read, which is why the deletion is cited through
Hendrickx and De Wolf. The intertissue-diffusion note below gives the full
citation of all four sources.

**The circuit's own walls absorb agent, and the model's circuit is inert.**
The modeled circuit is an ideal, well-mixed volume whose walls hold no agent.
Agent enters with fresh gas and leaves with the exhaust. Targ, Yasuda and Eger
measured what a real circuit holds (*Anesth Analg* 1989 Aug;69(2):218–25, PMID
2764290), in the companion to the tissue paper that this project's
coefficients come from. Their Table 1 gives plastic/gas and rubber/gas
partition coefficients after 6–9 weeks' equilibration:

| component | desflurane | sevoflurane | isoflurane | halothane |
| --- | ---: | ---: | ---: | ---: |
| Y-piece (polypropylene) | 6.67 | 7.68 | 10.6 | 19.1 |
| circuit tube (polyethylene) | 16.2 | 31.2 | 57.9 | 128 |
| reservoir bag (latex) | 19.3 | 29.1 | 48.9 | 190 |
| bellows (black rubber) | 10.4 | 22.6 | 42.9 | 199 |
| endotracheal tube (PVC) | 34.7 | 68.5 | 114 | 233 |
| mask pad (PVC) | 51.7 | 104 | 170 | 323 |

The ranking held at every equilibration time from 7.5 min to 9 weeks. So
**the inert circuit is most nearly true for desflurane and least for
halothane**, and the size of this omission depends on which agent is loaded.
The same study measured washin and washout in a real circuit at 0.5–5 L/min
inflow, against the ideal exponential. Desflurane's curves "closely
approximated the maximal possible theoretical rates", while the more soluble
agents lagged.
<!-- not-restated: 5 L/min -->

The authors conclude that for desflurane this absorption "should not hinder
induction of or recovery from anesthesia". The coefficients above
**overstate** the effect during a case, because equilibration is nowhere near
complete in the hours an anesthetic lasts, as the paper says. What the model
cannot show is the early lag that a real circuit adds for sevoflurane and
isoflurane. Absorption by the circuit walls is not planned. It would be a
second gas store with its own time constant, and no teaching objective in
`ROADMAP.md` asks for one.

**Desflurane's five-minute washout disagrees with the published human
measurement, and no parameter value that the human measurements support closes
the gap.** As a diagnostic, the model was run with the rebreathing circuit
removed. It then reproduces the published $`F_A/F_{A0}`$ at five minutes for
sevoflurane and for both isoflurane cohorts, but washes desflurane out 2.33
published standard deviations too *fast*. This is the one comparison in this
project against a human measurement that fails in the direction that
overstates recovery. A learner who took desflurane's early washout as a
physiologic prediction would expect a faster fall than Yasuda's volunteers
showed. "Desflurane's residual, and why the parameter file was not changed"
gives what was ruled out: the tissue and blood solubilities, the operating
point, the fast capacity this model omits, a non-ideal lung, and both readings
of the published apparatus (circuit-style rebreathing, and the 50 ml of series
dead space that its methods section describes). End-tidal sampling bias was
ruled out by a human measurement of the end-tidal gradient, which runs the
other way with solubility and reverses sign through an elimination. The one
hypothesis left is the published value itself, which this project cannot test,
so the disagreement is left uncorrected.

**Dead space is left out, and the effect of a series dead space is known
exactly.** The model ventilates the alveolar compartment continuously and has
no separate breaths, so it represents neither anatomic nor apparatus dead
space. A *series* dead space is exactly equivalent to a reduction in alveolar
ventilation. Over one breath, the dead-space volume re-enters the alveoli at
$`F_A`$ and leaves at $`F_A`$, which nets to nothing. So a dead space $`V_D`$
at respiratory rate $`f`$ acts as an alveolar ventilation of
$`\dot V_A - V_D f`$ ("Desflurane's residual, and why the parameter file was
not changed" gives the derivation). The alveolar ventilation control is
therefore already the dead-space control, provided the value entered is a true
alveolar ventilation. The interface names the control "Alveolar ventilation"
for that reason, and a minute ventilation entered there overstates gas
exchange by the whole of the dead space. What this model cannot represent is
**parallel** inhomogeneity: unequal ventilation-perfusion ratios across
alveolar units. The bullets on multiple alveolar units, shunt and
ventilation-perfusion mismatch name it, and no single ventilation figure
reproduces it.

**Cardiac output and the three perfusion fractions are held fixed under
anesthesia, and a real anesthetic moves them.** Cardiac output, $`Q`$, is a
user control, and nothing else changes it. The three perfusion fractions,
$`\text{perfusion fraction}_i`$, are constant for the whole of a run and are
not a control at all. A volatile anesthetic is itself a cardiovascular
depressant, so the model holds fixed the quantities its own subject acts on.
Each tissue's time constant is $`\tau_i = V_i\lambda_{i:b}/Q_i`$: its volume
times its tissue:blood partition coefficient, over its blood flow. So a flow
that fell under anesthesia would *lengthen* every tissue's equilibration for
as long as the agent was given, against the intuition that more agent means
faster equilibration.

**It is not modeled because the human volunteer data do not describe a
relationship this model could represent.** Three studies measured healthy
volunteers who were anesthetized without surgery, each against their own awake
baseline:

- Weiskopf RB, Cahalan MK, Eger EI 2nd, Yasuda N, Rampil IJ, Ionescu P,
  Lockhart SH, Johnson BH, Freire B, Kelley S. *Cardiovascular actions of
  desflurane in normocarbic volunteers.* Anesth Analg 1991;73(2):143-56.
  PMID 1854029. Desflurane alone at 0.83, 1.24 and 1.66 MAC, in 12 men.
  **Cardiac index did not change**, although stroke volume index fell and
  filling pressure rose at every concentration. This is myocardial depression
  with cardiac output maintained.
- Cahalan MK, Weiskopf RB, Eger EI 2nd, Yasuda N, Ionescu P, Rampil IJ,
  Lockhart SH, Freire B, Peterson NA. *Hemodynamic effects of
  desflurane/nitrous oxide anesthesia in volunteers.* Anesth Analg
  1991;73(2):157-64. PMID 1854030, doi:10.1213/00000539-199108000-00008. The
  **same** volunteers, in the same crossover, with 60% nitrous oxide carrying
  0.5 MAC of the total. Cardiac index now fell dose-dependently.
- Malan TP Jr, DiNardo JA, Isner RJ, Frink EJ Jr, Goldberg M, Fenster PE,
  Brown EA, Depa R, Hammond LC, Mata H. *Cardiovascular effects of sevoflurane
  compared with those of isoflurane in volunteers.* Anesthesiology
  1995;83(5):918-28. PMID 7486177, doi:10.1097/00000542-199511000-00004.
  With sevoflurane, cardiac index fell at 1.0 and 1.5 MAC and **returned to
  baseline at 2.0 MAC** as systemic vascular resistance fell. Isoflurane
  behaved similarly. With both agents the depression diminished with
  prolonged administration, and with spontaneous rather than controlled
  ventilation.

<!-- not-restated: 0.5 MAC -->

Together these studies show that the *sign* of the cardiac-output change
depends on the carrier gas, that the dose-response **changes direction**, and
that the effect changes with time at a fixed dose and with the mode of
ventilation. This model has no second gas, no ventilation mode, no surgical
stimulus and no pharmacodynamic layer, so it could represent none of those
dependencies. It could represent only a $`Q(\text{dose})`$ that moves one way
with dose and does not change with time, which the studies above do not show.
Teaching one would be worse than holding the flow fixed and saying so. The
case for modeling regional flow is weaker still. The measurements this project
could find of how anesthesia redistributes flow between the vessel-rich,
muscle and fat groups are largely from animals. The note below on the fat
group's perfusion gives what the human record supports, even at rest.

**What a learner gets instead is the control.** Cardiac output is on the
interface, so a learner can move it and watch: a higher output carries more
agent away from the lung, stores more of it and slows the rise of $`F_A`$.
The model's own tests check the same directions. What is absent is the
*automatic* coupling from the agent to the flow, which the reader has to
supply.

`ROADMAP.md`'s planned-milestone item 35 carries that coupling as a possible
future option that a user would turn on, with a run's default behaviour
unchanged. The evidence above favours an option, because an option can state
its own uncertainty where a model's default behaviour cannot.

**The stored MAC that the MAC-multiple display divides by limits that
display.** Each agent's stored MAC is tier 3 under § "Source hierarchy", and
"Delivery-limit and MAC parameters" measures the gap. Against Mapleson's
age-40 meta-analytic values, the stored sevoflurane MAC is 10% low and the
stored desflurane MAC is 10% high. The choice of MAC source alone therefore
shifts a sevoflurane-versus-desflurane comparison in MAC multiples by about
22%. The shift is consistent within an agent and changes no curve's shape or
timing. It rescales one agent's MAC axis against another's. The gap is larger
than either source's own confidence limits, so by the primary literature two
agents at "1 MAC" are not equipotent to that precision. The interface displays
the divisor for this reason. Moving all parameters to primary sources is
`ROADMAP.md`'s planned-milestone item 31.

**Two omissions limit the supported run length, and a third limits the late
washout within it.** The first two are metabolism, in the list above, and the
fat group's flow, in the note below. Both are negligible over a case and not
over days, so a run is supported to 24 hours, and the simulator will not step
past that limit. A longer run would increasingly display what this model
leaves out. "Supported run length" argues for the number and gives the measured
extent of sevoflurane's metabolism. Within those 24 hours:
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

- the fat flow makes the fat trace's loading uncertain by up to about a factor
  of two, in a direction that the note below leaves unsettled. The PET
  measurement, on which the stored flow runs about twice too high, counts
  against the 24 hours;
- the third omission, the fourth compartment of the intertissue-diffusion
  note, carries the largest term in the measured washout from about hour 2-3
  of elimination to about hour 21-29. All else equal, the modelled tail
  therefore falls faster than the measurement from about the third hour. That
  note gives where the shipped tail falls below the published mean curves, and
  by how much.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

Neither the fat flow nor the missing compartment moves the 24 hours by itself,
and nor does the measured gap. § "Supported run length" gives the reason that
leaves the number where it is.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The fat group's flow is twice a resting depot measurement, and is where
human washout fits put it. The two human sources disagree about which way the
fat trace errs.** The fat flow fraction is tier 3 under § "Source hierarchy",
like every other parameter in the reference patient. Heinonen et al. measured
resting subcutaneous adipose perfusion in the thigh of six healthy young women
by positron emission tomography (PET). Their figure is close to half what the
stored fraction implies. The two Yasuda 1991 papers this model is validated
against each fit a five-compartment mammillary model to each volunteer's data,
and read the slowest compartment as fat. Both estimate its blood flow as that
compartment's tissue/blood partition coefficient times its fitted rate
constant (*Anesth Analg* p. 319). For sevoflurane and isoflurane they found
2.4 ± 0.6 and 2.2 ± 0.5 mL per 100 mL of tissue per minute (Table 5, p. 322).
For desflurane and isoflurane they found 2.1 ± 0.4 and 2.2 ± 0.2 (Table 5,
p. 496). These are mean ± SD, at the fat:blood coefficients of Yasuda, Targ
and Eger 1989.
<!-- not-restated: 2.4, 2.1 -->

The stored fraction implies 2.07 mL per 100 mL per minute: 0.06 of the
5.0 L/min default cardiac output, flowing into 14.5 L. Flow per unit of tissue
is the partition coefficient over the time constant, so the comparison needs
no fitted volume. This model's stored fat solubilities (fat:gas over
blood:gas) are 52 for sevoflurane, 54 for isoflurane and 31 for desflurane. At
those values, the fitted fat-group time constants of 2,120, 2,130, 1,340 and
2,090 minutes (Table 4 of each paper) give 2.5, 2.5, 2.3 and 2.6. Read as
evidence about the fat group's flow, the PET measurement puts the stored
figure at about twice the truth, and the washout fits put it at or a little
below the truth.
<!-- derived: 2.07 from data/patients/reference_adult.json tissue_groups.fat.perfusion_fraction = 0.06, default_cardiac_output_l_min = 5.0, tissue_groups.fat.volume_l = 14.5 -->
<!-- derived: 52 for sevoflurane from data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34.0, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 54 for isoflurane from data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70.0, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 31 for desflurane from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13.0, blood_gas_partition_coefficient = 0.42 -->

Neither settles it, for different reasons. The PET figure is one depot in one
small cohort, awake and at rest, set against a whole-body lumped compartment,
and the depots within such a compartment really do differ (Frayn and Karpe).
The fitted compartment is fat only by the authors' assignment (see the
cautions below). Its volume is a third to two fifths of the fat this model
stores, and the analysis "only accounts for about 25 L of the body volume"
(*Anesth Analg* p. 323). The same paper's flow estimates ran too small for the
vessel-rich group and too large for muscle, compared with known values
(p. 323). The volunteers breathed nitrous oxide throughout. The terminal time
constant was fitted over days on which they had left the hospital and exceeded
basal activity between samples (p. 319).

Both sources support this much. The fat group's time constant is long
compared with any simulated case, whichever flow is right, so the fat
compartment stays far from equilibrium and no displayed curve reaches a wrong
endpoint. What moves with the flow is how much agent fat has taken up by the
end of a case. That amount sets the slow tail of washout, and it moves by up
to about a factor of two. A learner who reads the fat trace as a physiologic
prediction should treat its fat loading as uncertain by about that much, in
an unsettled direction. The PET measurement is not adopted.

**Fat fills here only through its own blood supply, and human washout finds a
second, faster fat-like store that this model does not have.** Every tissue
group exchanges agent only with the blood flowing through it (§ "Tissue uptake
and return"). Gas Man omits the direct route from lean tissue to fat too:
"Inter-tissue diffusion may occur between fat and muscle; this effect has been
ignored in the Gas Man model" (Workbook, Appendix B, p. 170). Carpenter et al.
needed a fifth compartment to fit human washout in 27 of 36 data sets, with a
time constant that "lies between the time constants predicted for muscle and
fat". Both Yasuda papers found five compartments in every washout they
fitted. "Following the suggestion of Carpenter et al.", both interpreted the
fourth as "a layer of fat that receives anesthetic from adjacent vessel-rich
organs by intertissue diffusion" (*Anesth Analg* p. 320, *Anesthesiology*
p. 493). The first paper computes that compartment's volume on the assumption
that it is fat (p. 319). The table gives their mammillary time constants and
estimated volumes (Tables 4 and 5 of each paper, mean ± SD), beside this
model's fat group at the default cardiac output:

| Cohort | Fourth compartment: time constant (min) | Fourth compartment: volume (L) | Fat group: time constant (min) | Fat group: volume (L) | This model's fat group: time constant (min) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sevoflurane, Anesth Analg 1991;72:316-24 | 377 ± 123 | 2.5 ± 0.6 | 2,120 ± 690 | 4.1 ± 3.0 | 2,528 |
| Isoflurane, Anesth Analg 1991;72:316-24 | 383 ± 119 | 3.0 ± 0.7 | 2,130 ± 680 | 5.1 ± 4.1 | 2,603 |
| Isoflurane, Anesthesiology 1991;74:489-98 | 435 ± 131 | 5 ± 2 | 2,090 ± 230 | 6 ± 3 | 2,603 |
| Desflurane, Anesthesiology 1991;74:489-98 | 273 ± 88 | 6 ± 3 | 1,340 ± 230 | 5 ± 3 | 1,496 |

**So the fat trace is the fitted fat group, and the fourth compartment is what
is missing.** This model's fat time constant is a little longer than the
fitted fat group's in all four cohorts: within one standard deviation in
three, and 2.2 standard deviations above it in the fourth. It is 5.5 to 6.8
times the fourth compartment's time constant. The muscle group equilibrates in
85 to 135 minutes, so nothing in this model has a time constant on the fourth
compartment's scale. Leaving that compartment out biases three things. Each
bias is worked out from the compartment structure above, not from running the
simulator:

- **Fat holds too little agent.** Suppose the fourth compartment is fat at
  this model's stored fat solubility, and fill it and the fat group from a
  constant arterial partial pressure. Over any case from half an hour to four
  hours, the fourth compartment then takes up 0.9 to 2.2 times as much agent
  as this model's whole fat group. Within the studies' own fits, it takes up
  2.6 to 5.6 times as much as the fitted fat group. The two ranges differ
  because the fitted volumes are too small, as the note on the fat group's
  flow says. So the size is known to an order of magnitude only: the missing
  store is as large as the modelled fat group's uptake, or larger.
- **The fat trace shows only the slowly filling fat.** On the fitted time
  constants, the partial pressure in fat lying against well-perfused tissue,
  as a fraction of arterial, is four to six and a half times the trace's
  throughout a case of that length. After an hour, that fat is at 13 to 20% of
  arterial, against the trace's 2.3 to 3.9%. It still stays below the lean
  tissue feeding it, because agent moves down that gradient into the fat.
- **The late washout loses its largest measured term.** On the coefficients of
  the published mean washout curves (Tables 1 and 2 of each paper), after a
  30-minute administration the fourth compartment's term becomes the largest
  in the measured washout at 1.8 to 3.1 hours. It stays the largest until 20.7
  to 29.4 hours, inside the 24 hours that a run is supported for (§ "Supported
  run length"). Without that store the modelled tail should fall faster, and
  it does. Against the mean curves themselves (§ "The first 24 hours of
  elimination against the published mean curves"), the shipped tail runs below
  them from about the seventh hour until about the twenty-first, and a third
  below at the widest, near hour 13. For desflurane it is below from 3.4 to
  15.3 hours, by about half at the widest point, near 8 hours. The shipped tail
  is above the curves before and after that span. With the rebreathing circuit
  taken away, the model's tissue return alone is a third to a half of the mean
  curve between hours 8 and 13. With the circuit in place, as shipped, the gap
  starts later than the third hour, because the rebreathing circuit and the
  muscle group's slow return hold the tail above the curve until the seventh
  hour. The size is known to about a factor of two, which is the fourth
  compartment's own between-subject spread.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Eger and Saidman's review draws the same compartment, and names a fourth
bias.** Their Table 3 (p. 1024) gives intertissue diffusion a group of its
own, "a subset of the FG" [fat group]. That group is 2.9 L, where the fat
group is 14.5 L. Its time constants are 230, 412 and 396 minutes for
desflurane, sevoflurane and isoflurane, against bulk fat's 1,226, 2,198 and
2,114. The review cites those figures from the Yasuda fits, and each lies
within one standard deviation of the matching fitted compartment in the table
above. The fourth bias is in the lean tissues that feed the store. Part of the
intestine, liver, kidney and heart, and part of the muscle and skin, "are
slower to reach equilibrium because anesthetic is continuously lost to
adjacent fat". And 50 minutes into desflurane, "[w]ere it not for losses by
intertissue diffusion, the desflurane partial pressure in the MG [muscle
group] would reach 74% of the partial pressure delivered to it from the lungs"
(p. 1025). On that reading, this model's muscle trace runs ahead of the tissue
it represents. Yasuda et al. suggest that the route may also enlarge the
apparent delivery to muscle from the vessel-rich organs beside it (*Anesth
Analg* p. 323). That acts the other way, and nothing here says which effect
wins. The brain is spared. The review draws it apart from the rest of the
vessel-rich group "for reasons related to intertissue diffusion" (p. 1022).
This model has no effect-site compartment and parameterises its vessel-rich
group as brain (§ "v0.2.0: isoflurane and desflurane"). So the trace that a
learner takes to be the brain is the one this bias spares. A route added later
that drew its loss from that group would slow it, contrary to the review.
<!-- not-restated: 14.5 L -->

**Eger and Saidman put the effect on late recovery, not on emergence.** Agent
stored this way "returns to the circulation to delay recovery in normal-weight
and obese patients, particularly with more soluble anesthetics. However, the
increased anesthetic in fat occurs at a lower partial pressure and thus might
not influence emergence materially" (p. 1032). That matches the direction
above: what the model misses is the tail, not the early fall. The review's
emphasis is obesity, which this model's one reference adult does not
represent.

**Two cautions keep this a limitation rather than a missing parameter.** The
first is that the route and its size rest on different evidence. The route has
been measured outside Eger's group. In two dogs after 80 minutes of halothane,
perirenal fat sampled against the kidney held 20 and 35 times the
concentration of fat sampled far from it. Its tension was "comparable to the
arterial tension instead of to the very low tension to be expected if the fat
had received halothane only from its own blood supply" (Allott et al.,
p. 289). Eger and Saidman cite that as the direct demonstration (their ref 8),
though they call their own group's washout fits "the most convincing
evidence" (p. 1025). The size has not been measured that way. Their
"approximately 30% of the anesthetic taken up" and their time constants of 200
to 400 minutes (p. 1025) cite Carpenter et al. and the two Yasuda papers.
Eger is an author of every one of those papers, so the figures restate the
fits rather than confirm them. Allott et al.'s own case for lean tissue losing
agent to fat "depends almost entirely on the improved fit to femoral venous
tensions" (p. 290). And a fit establishes a time constant, not which tissue
holds it. The Yasuda authors write that intertissue diffusion is what "we
believe provides the explanation for the fourth compartment" (*Anesth Analg*
p. 323). Hendrickx and De Wolf quote Hull as saying that assigning a tissue to
a fitted compartment is "ill-founded because parameters of the fit to the
uptake data contain no information that might support such assumptions". They
add that compartment parameters relate to cardiac output and demographics in
no straightforward way, and conclude that correlating them with tissue volumes
and blood flows "should be done with care, if at all" (*Modern Anesthetics*,
pp. 165–66).

The second caution is that the fat-perfusion note above leaves the direction
of the fat group's own error unsettled. On its PET reading, the fat group
already holds too much agent, which acts against this omission. On its washout
reading, the fat group holds about what the fitted fat group would. Nothing
here measures whether the two cancel, and neither may be read as correcting
the other.

**Nothing in `ROADMAP.md` plans a fourth tissue compartment, and the one paper
here that approximated the route warns against the shortcut.** Allott et al.
fitted their dogs' data by giving fat more of the cardiac output, or by giving
lean tissue a higher solubility (Table I, p. 281). They warn that such mimicry
is "bound to fail to varying degrees in other circumstances". In recovery,
"metabolism will still remove halothane from the circulation … whereas extra
fat perfusion will eventually return halothane to the circulation". And with a
low fat/lean partition coefficient "the tension gradients for diffusion will be
less". Each circumstance might be matched by a distortion of its own, but "the
only general solution is to build a more elaborate model which incorporates
direct representations of metabolism (which would be straightforward) and
intercompartment diffusion (which would be more complex)" (p. 290).

The time constants in the table's last column, the ratios and the crossing
times were computed on 2026-09-26 from the published means above and this
model's parameters as stored then. None of the sources below is the authority
for a stored value:

- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Liu J, Laster M, Taheri S,
  Peterson NA. *Comparison of kinetics of sevoflurane and isoflurane in
  humans.* Anesth Analg 1991;72(3):316-24. PMID 1994760,
  doi:10.1213/00000539-199103000-00007. **Full text**, from the private
  reference corpus: the compartment assumptions on p. 319, the interpretation
  on p. 320, Tables 1, 2 and 4 on p. 321, Table 5 on p. 322, and the volume
  and muscle remarks on p. 323. Seven volunteers, with 30 minutes'
  administration and six to seven days' elimination.
- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Johnson BH, Freire BA,
  Fassoulaki A. *Kinetics of desflurane, isoflurane, and halothane in humans.*
  Anesthesiology 1991;74(3):489-98. PMID 2001028,
  doi:10.1097/00000542-199103000-00017. **Full text**, a scan with no text
  layer, read as page images from the private reference corpus: the
  interpretation on p. 493, Table 1 on p. 494, Table 2 on p. 495, Tables 4 and
  5 on p. 496. Eight volunteers, with 30 minutes' administration and five to
  seven days' elimination.
- Carpenter RL, Eger EI 2nd, Johnson BH, Unadkat JD, Sheiner LB.
  *Pharmacokinetics of inhaled anesthetics in humans: measurements during and
  after the simultaneous administration of enflurane, halothane, isoflurane,
  methoxyflurane, and nitrous oxide.* Anesth Analg 1986;65(6):575-82. PMID
  3706798; PubMed records no DOI. **Abstract read**, through PubMed: nine
  patients, 2 hours' administration. The abstract does not name intertissue
  diffusion. The Yasuda papers credit that reading to this paper, whose full
  text has not been read.
- Eger EI 2nd, Saidman LJ. *Illustrations of inhaled anesthetic uptake,
  including intertissue diffusion to and from fat.* Anesth Analg
  2005;100(4):1020-33. PMID 15781517, doi:10.1213/01.ANE.0000146961.70058.A1.
  **Full text**, from the private reference corpus: the brain drawn apart on
  p. 1022, Table 3 on p. 1024, the lean-tissue losses, the evidence and the
  30% share on p. 1025, and recovery on p. 1032. PubMed classifies it as a
  review, so it is tier 2 under § "Source hierarchy". Its figures need more
  caution than most reviews' do, because the paper says they "illustrate
  concepts but are not necessarily precise (quantitative) reflections of the
  kinetics" (p. 1020).
- Allott PR, Steward A, Mapleson WW. *Pharmacokinetics of halothane in the
  dog: comparison of theory and measurement in individuals.* Br J Anaesth
  1976;48(4):279-95. PMID 1275995, doi:10.1093/bja/48.4.279. **Full text**,
  from the private reference corpus: the design on p. 279, Table I on p. 281,
  and the discussion on pp. 289-90. Seven dogs were given 1% halothane for
  80 minutes. The perirenal-fat samples are from two further dogs of another
  series (p. 289). The paper is Eger and Saidman's ref 8, and it has no author
  in common with their refs 3-7.
- Perl W, Rackow H, Salanitre E, Wolf GL, Epstein RM. *Intertissue diffusion
  effect for inert fat-soluble gases.* J Appl Physiol 1965;20(4):621-7. PMID
  5838712, doi:10.1152/jappl.1965.20.4.621. The Workbook lists it as reference
  32 and prints the year as 1964. It is also Eger and Saidman's ref 9, which
  they credit with suggesting the effect "40 yr ago" (p. 1025). Allott et al.
  credit a 1963 chapter of Perl's with first suggesting it "on theoretical
  grounds" (p. 289). PubMed returns "[Abstract not available]". Neither text
  has been read, so nothing is taken from either.
- Philip JH. *Workbook for Gas Man®*, Appendix B, pp. 169-70, and Hendrickx
  JFA, De Wolf A, *Special aspects of pharmacokinetics of inhalation
  anesthesia*, Handb Exp Pharmacol 2008;(182):159-86, PMID 18175091,
  doi:10.1007/978-3-540-74806-9_8, pp. 163 and 165-66. Both were read from the
  private reference corpus. Both are tier 3, and `docs/references/README.md`
  carries their entries.

**The tissue:gas coefficients rest on one laboratory's means, and other
laboratories disagree with them by up to 150% in some tissues.** The stored
values are Gas Man's. They differ from Yasuda, Targ and Eger's means in seven
of the nine cells, by up to 9% in isoflurane's fat coefficient, 70.0 against
64.2 (§ "Parameter provenance" has the table). Hendrickx and De Wolf state the
general case: "Tissue solubilities vary up to 150% between authors (Yasuda et
al. 1989), and the tissue homogenates used to determine these coefficients may
not represent in vivo conditions" (p. 165). The 150% is not spread evenly
across the tissues this model uses. Yasuda, Targ and Eger, whose measurements
the stored values rest on, compare their values with two other laboratories on
p. 373. Fiserova-Bergerova et al.'s values for sevoflurane, isoflurane and
halothane were similar to theirs for brain and for fat, except halothane's fat
coefficient, which was 65% greater. They were 115% to 150% greater for kidney
and 10% to 30% less for muscle. Those values are Fiserova-Bergerova, Tichy and
Di Carlo 1984, Yasuda's ref 8. Lowe's isoflurane values were 50% to 75%
greater. The authors could not explain the differences.
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->

A third published set agrees less well. Baker and Farmery's 2011 review
prints tissue:blood coefficients from Fiserova-Bergerova and Diaz 1986 beside
the set that matches this model (Table 2, p. 572). On the tissue:blood scale,
that set puts sevoflurane's fat coefficient at 71.7, 37% above this model's
52.3, and isoflurane's muscle coefficient at 1.71, 51% below this model's
3.46. Its vessel-rich figures are 28% above this model's for both agents. The
set's own blood:gas values, 0.6 for sevoflurane and 1.4 for isoflurane, move
these gaps in opposite directions for the two agents, so the tissue:gas scale
that this model stores gives the fairer comparison. On that scale the set's
sevoflurane fat coefficient is 26% above this model's and its isoflurane
muscle coefficient 47% below. Its vessel-rich coefficient is 18% above for
sevoflurane and 38% above for isoflurane. The set may not be a measurement.
According to its PubMed abstract, the 1986 paper measured coefficients only
for water-soluble solvents such as acetone and the alcohols. It then fitted
equations that predict any substance's tissue coefficients from its blood:gas
and fat:gas values. Baker does not say which of the anesthetic figures were
measured and which predicted. The set has no desflurane values.
<!-- not-restated: 18 % -->

So for sevoflurane and isoflurane, Yasuda's brain and fat values, which this
model's vessel-rich and fat groups store as Gas Man's figures, were reproduced
by one other laboratory, in 1984. The 1986 set does not reproduce them, and it
may be a prediction rather than a measurement. Yasuda, Targ and Eger make no
such comparison for desflurane. The 150% is the kidney, which this model does
not parameterise on its own (§ "Parameter provenance" records that the
vessel-rich group is Yasuda's brain value). Muscle is where the model's
coefficient is least certain, on two counts. The other laboratories disagree
with it in both directions: Fiserova-Bergerova's two sets put muscle lower,
and Lowe's isoflurane values were higher by a margin that Yasuda does not
break down by tissue. And Yasuda's own muscle measurements spread the most.
Their standard deviation is 43% of the mean for sevoflurane (2.38 ± 1.03),
45% for isoflurane (4.40 ± 1.97) and 37% for desflurane (0.94 ± 0.35),
against 17% to 19% for fat. Eger and Saidman's Table 1 makes the same point
from the literature as a whole. Their best figure for sevoflurane muscle is
1.7, with 1.1 to 2.4 as the range across the studies they cite (p. 1022),
where the agent file stores 2.4. A muscle group's time constant is
proportional to its tissue:gas coefficient, so 1.7 in place of 2.4 would
shorten the sevoflurane muscle time constant by 29%. That is how much a
coefficient's provenance can move the intermediate part of every wash-in and
washout curve this simulator draws.
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4 -->
<!-- derived: 29% from data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4 -->
<!-- not-restated: 1.1 -->

Every stored coefficient lies within one standard deviation of its cited
measurement. A learner should read the muscle and fat traces as one
well-measured parameter set, not the only set the literature supports.
Yasuda, Targ and Eger's p. 373, Eger and Saidman's Table 1, Baker and
Farmery's Table 2 and Hendrickx and De Wolf's p. 165 were read in full text.
Fiserova-Bergerova and Diaz 1986 was read as its PubMed abstract only (PMID
3721592), and the 1984 paper not at all. The Yasuda, Targ and Eger citation is
in § "Parameter provenance".

**Cardiac output does not scale with the patient, and the reference weight is
a label, not an input.** The default cardiac output is a stored 5.0 L/min. No
equation reads the patient's weight, so editing the weight changes nothing
this model computes. Two published figures sit either side of the stored
value, **and they are not evidence of the same kind.** The first is Lowe and
Ernst's cardiac-output relation, the upstream source that the Gas Man Workbook
names, read at the source. It gives $`0.2M^{3/4}`$ for a body mass $`M`$ in
kg, which is 4.84 L/min at 70 kg. It is **derived, not measured**: Brody's
1945 interspecies oxygen-consumption allometry divided by an arteriovenous
oxygen content difference that is assumed constant across mammals
(§ "Parameter provenance" gives the derivation). The second is Cattermole et
al.'s **measured** median of 5.51 L/min, from 686 subjects in the 50–75 kg
band that this patient sits in.
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

The fixed value is kept for a structural reason. A time constant is
$`V_i \lambda_{i:b} / Q_i`$, and this model stores compartment volumes as
fixed litres. So scaling only the flow would make every time constant
proportional to $`M^{-3/4}`$: a heavier patient would equilibrate *faster* and
a lighter one more slowly. That is an artifact of scaling one half of a
coupled pair. At the shipped sevoflurane coefficients, a 20 kg child under a
weight-scaled cardiac output alone would equilibrate about 2.6 times more
slowly than the reference adult, which is the opposite of the direction in
which paediatric inhalational uptake runs. (Salanitre and Rackow's
*Anesthesiology* 1969;30(4):388–94 study of pulmonary exchange in infants and
children is the classic reference for that direction. Its PubMed record was
retrieved, but its text has not been read, so no figure is taken from it.)
Half of the scaling is therefore worse than none of it. Adopting the relation
for the one patient that exists would have lengthened every time constant by
3.32% and changed nothing else.

**So this model describes one 70 kg adult.** It is not a paediatric, obese,
or otherwise weight-varying model, and no field in the interface makes it one.
A run is that adult's run, whatever value the reference weight shows.
Weight-varying physiology is `ROADMAP.md`'s planned-milestone item 30, as a
package. Compartment volumes, alveolar volume, alveolar ventilation, the
perfusion fractions and MAC by age should move together, or none of them
should move.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**One reference condition, where the model physically has two.** "Agent
amount" fixes the amount unit at 20 °C and 760 mmHg, dry. Nothing here
converts between conditions, so a litre in the circuit and a litre in the
alveoli are added as equals, though as volumes of gas they are not the same
quantity of agent. The circuit volume $`V_C`$ is at ambient temperature, and
the fresh gas flow $`\dot V_F`$ is a flow at the common gas outlet. So the
circuit, delivered and exhausted amounts, $`M_C`$, $`M_{\mathrm{delivered}}`$
and $`M_{\mathrm{exhausted}}`$, are at the stated condition and are exact
there. The alveolar gas volume $`V_A`$ is at body temperature, and the
partition coefficients that build the venous and tissue amounts $`M_v`$ and
$`M_i`$ were measured at 37 °C. So the alveolar, venous and tissue stores are
natively 37 °C quantities carried under a 20 °C label. The two conditions meet
in the ventilation term, which moves $`\dot V_A`$ litres out of the circuit and
the same $`\dot V_A`$ litres into the alveoli. In the alveoli, warming ambient
gas to body temperature would expand it by the molar-volume ratio.

**The size is 5.8 %, and it applies to the stores, not to conservation.**
Every term is exact in the model's own arithmetic, and the mass balance closes
to within $`10^{-13}`$ L, a ten-millionth of a microlitre, whatever condition
the unit names. So no agent goes missing, and the question is what the litres
*mean*. Read as amounts of substance, the alveolar, venous and tissue stores
hold 5.5 % fewer moles than their 20 °C label implies, so the label overstates
them by 5.8 %. The ratio behind both figures is 25.450/24.055, the molar
volumes in litres at 37 °C and at 20 °C. The fresh-gas terms are unaffected.

**It is invisible in everything the simulator shows today.** A
partial-pressure fraction has no unit and carries no condition. So $`F_A`$,
$`F_A/F_I`$, the MAC multiple and every trace on the chart are untouched by it.
It would matter only where an amount is converted out of the litre unit, as
the liquid-equivalent consumption figure planned under § "Planned milestones"
item 28 will be. The code for that conversion exists, and nothing on screen
shows its result yet. It converts a delivered or exhausted amount exactly and
a stored amount 5.8 % high. There it biases the split between stored and
exhausted agent, but not the delivered total, which is the figure that means
cost. Removing this limitation would need a gas-phase model that carries
explicit conditions per compartment, which is well outside the current
milestone.

**The modeled alveoli are dry, and real ones are saturated at 47 mmHg.** This
is the third gas-phase condition, beside temperature and pressure. "Agent
amount" states the reference condition as 20 °C and 760 mmHg, *dry*. Alveolar
gas is fully saturated at body temperature, so of the 760 mmHg available,
47 mmHg is water and 713 mmHg is left to everything else. In a patient, agent
leaves the circuit dry, and is warmed and humidified on reaching the alveoli.
A dry inspired fraction $`F_I`$ therefore occupies $`F_I \times 713`$ mmHg
rather than $`F_I \times 760`$. That is a dilution of 47/760, or 6.2 % of an
atmosphere, before any uptake has occurred. Equivalently, the undiluted figure
is 6.6 % above the humidified one, which is 47/713. The alveolar equation
carries $`\dot V_A(F_I - F_A)`$ with no such factor, so $`F_I`$ arrives
undiluted.

**The 47 mmHg is computed.** The saturation pressure of water at 37.0 °C is
47.12 mmHg on the IAPWS-95 formulation (Wagner W, Pruß A. *The IAPWS
Formulation 1995 for the Thermodynamic Properties of Ordinary Water Substance
for General and Scientific Use.* J Phys Chem Ref Data 2002;31(2):387–535,
doi:10.1063/1.1461829). The formulation's saturation equation reproduces both
the triple-point pressure and the normal boiling point to better than one
part in a million. The conventional 47 of the alveolar gas equation is that
value rounded, and the two agree to 0.3 %. This project stores no such value,
because no equation here reads it.

**Applying the factor would break the validation, as a measurement shows.**
The governing equations are linear in $`F_I`$, the property that "Published
wash-in and elimination validation test" also rests on. So applying the factor
to the inspired term multiplies every computed $`F_A/F_I`$ by exactly 713/760.
$`F_A/F_I`$ is the one quantity this model is validated against, and the
validation does not survive the factor. At the shipped defaults, the modeled
$`F_A/F_I`$ for each of the four published wash-in cohorts lies within one
standard deviation of the published mean. With the factor, all four fall
outside it:

| Cohort | Modeled $`F_A/F_I`$ | Now | With the factor | Then |
| --- | --- | --- | --- | --- |
| Sevoflurane, Anesth Analg 1991;72:316-24 | 0.8528 | +0.16 SD | 0.7999 | −2.78 SD |
| Isoflurane, Anesth Analg 1991;72:316-24 | 0.7414 | +0.31 SD | 0.6954 | −1.39 SD |
| Desflurane, Anesthesiology 1991;74:489-98 | 0.9079 | +0.79 SD | 0.8516 | −4.84 SD |
| Isoflurane, Anesthesiology 1991;74:489-98 | 0.7414 | +0.38 SD | 0.6954 | −1.15 SD |

<!-- not-restated: 0.31 -->

These figures were measured on 2026-09-19, at the parameters stored then,
against the published means and standard deviations.

**Humidification is real, and the factor fails because it would count it
twice.** In those studies, $`F_A/F_I`$ is a ratio of two analyser readings
taken from real airways. So whatever humidification does to alveolar agent is
already inside the measured 0.850, and a model that reproduces that number has
already absorbed it. The stored coefficients raise the same problem. They are
tissue:gas and blood:gas ratios equilibrated at 37 °C, and how much water the
gas phase held in those determinations is recorded nowhere that this project
has read. Applied to $`F_I`$ alone, against coefficients whose own gas-phase
basis is unknown here, a factor could not be shown to move the model toward
the real behaviour rather than away from it. A proper correction puts the
coefficients and the inspired term on the same gas-phase basis together. That
needs the same per-compartment gas-phase model that the note above names,
which is well outside the current milestone. Do not "fix" the omission by
inserting 713/760.

**Dry alveoli change no displayed value, but they limit what the simulator can
be asked.** They do not affect the displayed percent or the MAC multiple,
because $`F_A`$ here is anchored to a measured end-tidal quantity, not to a
computed dry-gas fraction. The rows above are end-tidal measurements, and MAC
is defined on the end-tidal concentration too ("MAC multiples as a display
unit"). So a model fitted to the first and divided by the second compares like
with like, whatever water the sampled gas held. There is no water anywhere in
this model, so nothing here distinguishes a dry circuit from a humidified one.
No question about airway humidification has an answer in it, whether it
concerns an HME, a heated humidifier or the difference between them.

**Ambient pressure is not modelled, and away from one atmosphere the
delivered-concentration dial stops meaning one partial pressure.**
§ "Assumptions" above fixes ambient pressure at 760 mmHg, so this model is
specified for sea level. Take a user in Denver (about 630 mmHg) or Mexico City
(about 585 mmHg) who sets 6% desflurane in this simulator and 6% on the
corresponding real device. That user is not delivering the same anesthetic,
and nothing else in the simulator says so. The delivered-concentration control
is a vaporizer dial, and this project's three agents are drawn from two
classes of vaporizer that respond to falling ambient pressure in opposite
directions.
<!-- not-restated: 6 % -->

**The real devices for sevoflurane and isoflurane are variable-bypass
vaporizers.** This class includes the Dräger Vapor 2000, Sevotec 5, Isotec 5
and Penlon Sigma Delta. Fresh gas is split between a bypass channel and a
vaporizing chamber. The gas leaving the chamber is saturated at the agent's
saturated vapour pressure, which temperature sets and ambient pressure does
not. The dial sets the splitting ratio. So as ambient pressure falls, the
output rises in volumes percent while the delivered *partial pressure* is
approximately preserved, and the dial needs no altitude correction. Boumphrey
and Marshall give the approximation as
$`\%_1 = \%_\mathrm{cal} \times P_\mathrm{cal} / P_1`$. Their worked example
is isoflurane dialled to 2% at 101.3 kPa, which delivers 4.05% at 50 kPa.
That is 2.026 kPa of isoflurane either way.
<!-- not-restated: 2 % -->

**The real devices for desflurane are gas–vapour blenders.** This class
includes the Tec 6 and Tec 6 Plus. Desflurane needs it because it boils at
22.8 °C. The sump is kept at about 39 °C, which fixes desflurane's vapour
pressure at about 1460 mmHg, a pressure chosen to clear the vaporizer's own
internal resistances. Pure vapour is injected into the fresh gas stream. A
differential pressure transducer keeps the vapour circuit at the fresh-gas
circuit's pressure, so the two flows stay in the fixed *ratio* that the dial
sets. Andrews and Johnston describe it: "The pressure in the vapor circuit is
electronically regulated to equal the pressure in the fresh gas circuit…
vaporizer output is constant because the amount of flow through each circuit
is proportional". Output is therefore a constant volumes percent, and the
delivered partial pressure falls with ambient pressure. Datex-Ohmeda states
the consequence for the operator directly: "Decreased atmospheric pressure,
with altitude, does not significantly affect the concentration of agent
delivered (V/V), but decreases the partial pressure of the agent in the ratio
of the atmospheric pressure to the calibrated pressure of 760 mm Hg. To
compensate for the reduction of vapor pressure output at altitude, the rotary
valve must be advanced to maintain the required agent partial pressure."

**The MAC that the display divides by is a sea-level percent for the same
reason.** 1 MAC is a partial pressure, which convention quotes as a percentage
of one atmosphere. So at reduced ambient pressure, the percentage needed to
reach it rises while the partial pressure does not. James and White proposed
MAPP, minimum alveolar *partial pressure*, in place of MAC on exactly this
ground. So the unit described under § "MAC multiples as a display unit" is a
sea-level unit too.

**No altitude correction factor is stored, and the $`1/P`$ form above must
not become one.** $`\%_\mathrm{cal} \times P_\mathrm{cal} / P_1`$ is the
dilute-vapour limit of the flow-splitting physics. The fuller form is
$`F \approx k\,\mathrm{SVP}/(P - \mathrm{SVP})`$, where SVP is the saturated
vapour pressure, and it reduces to $`k\,\mathrm{SVP}/P`$ only where
$`\mathrm{SVP} \ll P`$. Isoflurane's saturated vapour pressure is about
240 mmHg at 20 °C, which is not small against 760. Carrying the denominator
through gives a delivered partial pressure that *overshoots* rather than holds
steady: on that arithmetic alone, about 16% high at 585 mmHg, where the
$`1/P`$ form predicts a flat line. The direction of each class's response is
not in doubt, and neither is the contrast between the two. The size of the
variable-bypass compensation is approximate, so no number is stored for it. An implementation of ambient pressure should
derive the variable-bypass case from each agent's saturated vapour pressure
rather than from the $`1/P`$ shortcut, and would owe each agent's SVP a source
of its own. None is stored today.

**Sources for the notes above.** None of them is the authority for a stored
value:

- Weiskopf RB, Sampson D, Moore MA. The desflurane (Tec 6) vaporizer: design,
  design considerations and performance evaluation. *Br J Anaesth*
  1994;72:474–479. Primary, and the authority for every figure attributed to
  it here: the 22.8 °C boiling point, the 39 °C sump, the 1460 mmHg that the
  sump fixes and why that pressure was chosen, and the ±15% relative (or
  ±0.5% absolute) output accuracy. Read in full text. It states the 1460 mmHg
  twice, once for the sump and once for the regulator that reduces it to the
  fresh-gas pressure. It says nothing about ambient pressure or altitude, so
  it is not the source for that behaviour.
- Andrews JJ, Johnston RV. The new Tec6 desflurane vaporizer. *Anesth Analg*
  1993;76:1338–1341. Primary. It is the source of the flow-ratio mechanism
  quoted above, which appears in the abstract.
- James MF, White JF. Anesthetic considerations at moderate altitude. *Anesth
  Analg* 1984;63:1097–1105. Primary. It is the source of the case for
  reasoning in partial pressures rather than percentages at altitude, and of
  the MAPP proposal. It predates desflurane, so it covers the variable-bypass
  class only.
- Datex-Ohmeda. *Tec 6 Plus Vaporizer* specification sheet AN3307-A/1100,
  © 2000 Datex-Ohmeda Division, Instrumentarium Corp. A manufacturer
  statement, quoted above. It also gives the 1–18% concentration range that
  this model stores as desflurane's delivery range. Read in full.
  **Owner-attested**: see the note below.
- Boumphrey S, Marshall N. Understanding vaporizers. *Contin Educ Anaesth
  Crit Care Pain* 2011;11:199–203. **Tier 2** under § "Source hierarchy". It
  is a secondary synthesis, taken here for the shape of the explanation and
  the worked example, and never as the authority for a number. Its "Altitude"
  section describes both classes side by side. Read in full.
  **Owner-attested**: see the note below.

<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

**Two of those five are owner-attested: they were read from the project
owner's copies, and no other reader can check them.** They are the
Datex-Ohmeda specification sheet and the Boumphrey and Marshall article. Any
reader can reach the three journal articles above through their DOI or PMID.
`docs/references/` cannot hold copies of these two, because the repository is
public (`docs/references/README.md` § "Redistribution"). So three things rest
on that reading alone: the passage quoted from Datex-Ohmeda, the 1–18% range
beside it, and the worked example attributed to Boumphrey and Marshall.
Nothing stored depends on any of them. A reader who wants to verify one has to
reach the document itself.
<!-- not-restated: 18 % -->

**Gas Man's own agreement with patients depends on the phase of the case, and
wash-in is its worst phase.** This model's parameter set and its compartment
structure both descend from Gas Man, which § "Source hierarchy" ranks tier 3.
Its value there is that it fixes the behaviour of a widely used teaching tool
for this implementation to be compared against. A prospective in-patient study
measured how closely that behaviour tracks real end-expired sevoflurane.
Twenty-eight ASA I–II adults undergoing gynecologic or urologic surgery were
maintained on sevoflurane in O₂/air, fourteen on a Dräger Zeus and fourteen on
a Getinge FLOW-i. Fresh gas flow was re-randomised every fifteen minutes over
0.2 to 6 L/min, and the vaporizer setting was left to the anesthesiologist.
Each case was then re-run in Gas Man with that patient's weight and the same
flows, vaporizer settings and minute ventilation. Cardiac output was left at
the Gas Man default, Brody's formula, which is the 1945 interspecies relation
that the cardiac-output note above declines to adopt. Over the whole hour, Gas
Man tracked both workstations to within 10% on two measures of measured
against predicted: the median signed percentage error and the median absolute
percentage error. It drifted by −0.96%/h [−1.14, −0.88] on the FLOW-i and
−0.57%/h [−0.85, −0.16] on the Zeus. Split into the study's two phases, that
agreement does not hold:

| Workstation | Phase | Median performance error | Median absolute performance error |
| --- | --- | --- | --- |
| FLOW-i (n = 14) | wash-in, 0–15 min | 18% [1, 51] | 21% [8, 51] |
| FLOW-i (n = 14) | maintenance, 15–60 min | 0% [−7, 5] | 6% [2, 10] |
| Zeus (n = 14) | wash-in, 0–15 min | 7% [−6, 28] | 13% [6, 32] |
| Zeus (n = 14) | maintenance, 15–60 min | −1% [−5, 5] | 5% [2, 9] |

<!-- not-restated: 15 min -->

<!-- not-restated: 18 %, 6 %, 5 % -->

The brackets are the published interquartile ranges, and they carry more of
the finding than the medians do. A quarter of FLOW-i patients were tracked
worse than 51% through the first fifteen minutes, against worse than 10% over
the last forty-five. The two metrics are Varvel's. This project has not read
Varvel, so the metrics are taken as the study states them. The authors
conclude that Gas Man predicts end-expired sevoflurane "with better relative
performance for simulating maintenance than wash-in". They state that
conclusion for the wash-in and maintenance periods *combined*, not for the
wash-in alone.

**What the study bounds here is what Gas Man's lineage is worth.** The study
measures Gas Man, not this implementation, and nothing in this project has
been compared against a Gas Man trajectory. The comparisons under § "Required
tests" are against published human data, and no figure in the table above is
a tolerance that anything here must meet. Caveat 2 under § "Published wash-in
and elimination validation test" says that passing shows this implementation
reproducing its parameter set's *intent*, not that the set is independently
right. The study measures what that intent is worth in patients, and it is
worth least in the phase that the simulator displays most: the first minutes
of the $`F_A/F_I`$ rise, which is the canonical teaching curve of
inhaled-anesthetic uptake (see § "Model boundary"). So "agrees with Gas Man"
may not be read as "agrees with a patient" anywhere in a case, and least of
all in the first fifteen minutes. § "The early wash-in curve against the
published figures" compares this model's own first minutes with the published
human curves, and finds desflurane rising faster than its cohort.

**Nor is the gap necessarily the patient model's.** The two workstations ran
the same protocol, the same simulator and the same cardiac-output default,
and differ in how they deliver agent into the circle. Their wash-in median
absolute errors differ by a factor of about 1.6, which is suggestive and no
more. The fourteen patients on each workstation are different patients, so
the contrast is between groups, and the interquartile ranges behind it,
[8, 51] against [6, 32], overlap across most of their length. The study does
not decompose the error. The phase split may also come partly from the metric:
a percentage error is at its most sensitive when the denominator is small and
rising, which is the wash-in's own condition. With the Methods unread, how
much either effect accounts for is unknown. The direction is the one this
project's own circuit predicts. The apparatus lag $`\tau_C = V_C/\dot V_F`$ is
"the part of the inspired curve a learner is most likely to attribute to
uptake" (see § "Parameter provenance"). `docs/machine-survey.md` reaches the
same conclusion from the machine side: one perfectly mixed circuit is least
like a real workstation exactly where Gas Man's published agreement with
patients is weakest.

- Candries E, De Wolf AM, Hendrickx JFA. Prospective validation of Gas Man
  simulations of sevoflurane in O2/air over a wide fresh gas flow range. *J Clin
  Monit Comput* 2022;36(6):1881–1890. PMID 35318567;
  [DOI 10.1007/s10877-022-00842-0](https://doi.org/10.1007/s10877-022-00842-0).
  **Abstract read**, through the PubMed record, and every figure above is
  stated there. PubMed returns no PMC identifier for the paper, so there is no
  PubMed Central full text, and `docs/machine-survey.md` records that the
  project owner's private reference corpus did not hold it either. Its
  Methods, its Varvel definitions and its per-patient data are therefore
  unread. It is the authority for nothing stored in this project.

**For developers.** The inert circuit is `BreathingCircuit`. The directional
gates in `tests/reference/test_sevo_patient.py` assert that a higher cardiac
output slows the rise of $`F_A`$. The MAC-multiple display divides by each
agent's tier-3 `mac_percent`, and the Datex-Ohmeda 1–18% range is desflurane's
`max_delivered_concentration_percent`. `reference_adult.json` carries both
fat-flow comparisons. Its Heinonen et al. note gives both figures and the
volume-to-mass conversion between them, and its Frayn and Karpe entry records
that fat depots differ. The default cardiac output is
`default_cardiac_output_l_min`, and no equation reads `weight_kg`. The
reference-condition gap leaves the release gate's relative residual untouched.
`core/liquid_agent.py` is where an amount leaves the unit. It converts a
delivered or exhausted amount exactly and reads a store 5.8 % high, and its
docstring says so. The humidification table was measured through
`_wash_in_ratio` in `tests/reference/test_published_wash_in_and_elimination.py`,
against the published means and standard deviations that the module itself
holds.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->


## Release gate

A release is complete only when:

- all parameter values and sources are present;
- no scientific `TBD` markers remain;
- v0.0.2 circuit reference tests still pass;
- unit, integration, invariant, and independent reference tests pass;
- the published wash-in validation passes for every agent and cohort. The
  elimination comparison in the same test module is not part of this gate. It
  only checks that results have not changed from earlier versions, and makes
  no claim of agreement;
- mass balance closes within the documented tolerance;
- supported step sizes pass convergence and nonnegativity tests;
- deterministic replay passes;
- live setting changes preserve stored state;
- the interface contains the educational and non-clinical warning;
- Ruff formatting and linting pass;
- strict mypy passes;
- pytest passes;
- GitHub Actions passes; and
- this document describes the behavior actually present in the tagged release
