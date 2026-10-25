# Volatile-agent patient uptake and distribution model

## Status

This document specifies the scientific model implemented starting in v0.1.0.
That model has stayed in force, unchanged, ever since. Its governing equations
and compartment structure have not changed, and every agent this model
supports shares them. For that reason, the title does not name a version.

**It deliberately names no current released baseline.** The version table in
`ROADMAP.md` is where the current baseline is recorded. A second copy here
would go stale at every release, and nothing would read wrong until someone
checked the version. That is exactly what happened: this sentence named v0.2.3
for thirteen releases after v0.2.3 (`PL-C1KK`). Nothing in this document
should restate the current version. A statement that needs a version should
instead say what has been true *since* a version, because that cannot go
stale.

The preceding milestone, v0.0.2, delivered an ideal breathing-circuit wash-in
and washout model without a patient, and validated it analytically. Its
reference tests are preserved unchanged
(see § "Preserved circuit reference tests" below). Version v0.1.0 extends that
model along this path:

```text
delivered agent
        ↓
breathing circuit
        ↓
alveolar gas ⇄ blood (flow-limited, no separate arterial compartment)
        ↓
vessel-rich group / muscle / fat
        ↓
venous blood
        ↓
alveolar gas
```

Version v0.1.0 is the first sevoflurane model with a patient. It is the
“Sevo works” milestone.

This is an educational model. It is not a clinical prediction, dosing tool, patient monitor, or medical device.

## Intended use, and the safety class this project holds itself to

The sentence above says what this is *not*. Both ISO 14971 and IEC 62304 begin
from what a thing **is**. Intended use is what every later judgment about
hazard and class is made against. So this document states the intended use
here, rather than leaving it to be inferred from the absence of a disclaimer
(queue item `PL-BLHV`, 2026-09-13).

### Intended use

This is a teaching simulator for volatile-agent uptake and distribution. It is
intended for anesthesia clinicians, trainees, and students. It helps them
build intuition about how agent concentration moves between the breathing
circuit, alveolar gas, blood, and the tissue groups, under management that the
learner chooses. In particular, it makes visible the compartments that no
clinical monitor displays: vessel-rich, muscle, fat, and mixed venous.

**It is not intended for use with an identifiable patient's data.** The
simulator is intended to be run on hypothetical or illustrative parameters. It
is not intended for entering, importing, or reproducing the parameter values of
an identifiable patient. It is also not intended to inform the management of a
specific patient.

The boundary is deliberately drawn at the *data* rather than at physical
proximity to a patient. The distinction is not pedantic. A simulator open on a
workstation while a case runs is ordinary teaching, and it carries no hazard
of its own. A run built from a particular patient's weight, age, and cardiac
output is a prediction about that patient, whatever the window is labelled. A
boundary drawn at proximity would forbid the first case and permit the second,
which is backwards. The patient-covariate work planned in `ROADMAP.md` makes
the second case possible. So the boundary is recorded before that work, rather
than after it.

### Software safety classification: Class C, for the whole application

IEC 62304 § 4.3 assigns a software safety class from the severity of the harm
that a software failure could contribute to. **Class A** applies where no
injury or damage to health is possible. **Class B** applies where injury is
possible but not serious. **Class C** applies where death or serious injury is
possible. Annex B.4.3 is what makes the assignment depend on severity alone.
Where software sits in a sequence of events leading to a hazardous situation,
the probability of the software failing is **set to 1** rather than
estimated. So "this would rarely be wrong" is not an argument for a lower
class.

This project assigns **Class C uniformly, across the whole application**. It
does not place the interface layer in a lower class. The reasons are these:

- A lower class buys nothing here. Class A exists to *exempt* low-risk software
  from detailed design, unit verification, and integration testing. This
  project applies one quality gate to the whole tree, so the exemption would
  have nothing to exempt. Declaring Class C costs nothing. Declaring Class A
  for part of the tree would be a claim to defend.
- Class A asserts that *no injury is possible*, and the interface layer cannot
  make that claim. `CLAUDE.md` states that presentation correctness is itself
  a safety matter. The correct number with the wrong units, label, patient
  context, stale state, or model version is still a safety failure. The
  interface is also where several safety features live: the distinction
  between a halted and a paused run, the displayed-precision rule, the
  ISO 5360 agent colours, and the extreme-preserving decimation.
- The boundary does not stay in one place. `app/chart_frame.py` looks like
  chrome, but it decides what a trace asserts about a run. `app/theme.py`
  looks like styling, but it carries agent identification. A class boundary
  drawn through these files would put the line in a different place from the
  one this project already maintains.

A split would pay off only where the exempted surface is large and genuinely
non-clinical, and where its verification burden is actually felt. That is a
condition to watch for, not a reason to build a split now.

### This is an engineering bar, not a regulatory status

The class above is adopted in the same way that this project adopts
WCAG 2.2 AA. The section
"Color contrast, and the standard this interface is held to" in this document
describes that standard as "chosen as the right engineering bar for a teaching
tool, not as a compliance obligation". Nothing
here claims conformance to IEC 62304, to a quality management system, or to
any regulatory status. No such claim should be read into it. Writing the class
down is strictly more useful than leaving it implicit, because the written
class records the bar that a reviewer can hold the code to.

Device status is a separate question, and the class does not settle it. FDA
publishes examples of software functions that are *not* medical devices. They
include software intended for health care professionals as educational tools
for medical training. One worked example is "games that simulate various
cardiac arrest scenarios to train health professionals in advanced
cardiopulmonary resuscitation (CPR) skills" ([FDA, Examples of Software
Functions That Are NOT Medical Devices](https://www.fda.gov/medical-devices/device-software-functions-including-mobile-medical-applications/examples-software-functions-are-not-medical-devices),
and the guidance "Policy for Device Software Functions and Mobile Medical
Applications"). That exclusion depends on intended use, not on which
physiologic parameters the software accepts. Specifically, it depends on the
software not facilitating a health professional's assessment of a *specific
patient*. That is why the intended-use statement above is load-bearing rather
than decorative, and why its boundary is drawn where it is.

ISO 14971:2019 is the other half of the frame. The 2007 edition mentioned
**reasonably foreseeable misuse** only in passing. The 2019 edition made it a
defined term, and its clause 5.2 makes documenting that misuse an explicit
requirement. Use of this simulator against the intended use above falls
exactly into that category. That is why such use is recorded as a stated
boundary with mitigations, rather than met with a stronger disclaimer.

**On the sources for this section.** IEC 62304 and ISO 14971 are published
standards and are not open access. The clause structure, the three class
definitions, and Annex B.4.3's probability rule stated above were read from
secondary summaries, not from the standards' own text. That fact is recorded
here rather than left implied. The FDA material was read at the source. A
reviewer revising this section should check the standards directly. The
conclusion (Class C, uniform) does not depend on their wording, but the clause
numbers cited here do.

## Reasonably foreseeable misuse, and the hazards the presentation carries

Every other safety argument in this document runs in one direction: here is a
decision, and here is why it is sound. This section runs the other way. For
each hazard, it says how a reader could be misled, what stops it, and which
test checks that safeguard (queue item `PL-FDBK`, 2026-09-13).

The direction matters because the two directions find different defects.
Arguing forward finds the mistakes you thought to look for. Asking what has
*not* been excluded is what found `PL-VYXP` (a mass-balance baseline anchored
to an implicit zero) and `PL-B32L` (I/O exceptions escaping this model's
documented error hierarchy). Neither defect had surfaced across roughly two
hundred queue items, because a queue records the decisions taken, not the
harms that have not yet been ruled out.

ISO 14971:2019 makes this a requirement rather than a nicety. It made
**reasonably foreseeable misuse** a defined term, and in clause 5.2 it made
documenting that misuse explicit. Use of this simulator against the intended
use above is in that category. So it appears here as a table row with a
mechanism and a mitigation, rather than as a stronger disclaimer.

**Every row names the test that enforces it, or says plainly that it has
none.** `tools/doc_check.py` fails when a test named anywhere in this document
does not resolve to a test that exists. So the right-hand column cannot decay
into decoration. The check cannot judge whether the test is any good. That
remains a question for a reviewer.

| A reader could be misled into | What stops it | Held by |
| --- | --- | --- |
| reading a correct concentration as belonging to a different agent | agent colour is a redundant cue, never the sole identifier. The agent name is always visible: the invariant tier that every top-level window shows carries it, subject to the observability limit stated there (§ "Minimum displayed outputs" -> "What this list requires once the layout is the reader's"). `tools/agent_identity_check.py` audits the ISO 5360 colours and their accessible foregrounds in `src/anesthesia_sim/app/theme.py` as one unit | `test_agent_dropdown_options_pair_every_color_with_the_agent_name`, `test_every_agent_has_render_objects_in_its_own_identification_color`, `test_the_agent_name_stays_legible_while_the_run_disables_the_selector` |
| reading a run halted by a failure as one the user paused | a halt gets its own status words rather than falling back to "Paused", and the two failure modes are also distinguished from each other. The status word, the transport and the banner are stated from the run's status alone. None of these three facts is built from a compartment value. So a run whose own snapshot refuses a value still shows as stopped, not as running with Pause offered. A banner written before any frame of the stopped run has been drawn says so, instead of claiming that a step was rolled back (`PL-7DJK`) | `test_refresh_view_reports_a_failed_run_as_stopped_not_paused`, `test_refresh_view_reports_the_supported_run_length_as_stopped_not_failed`, `test_a_halt_is_shown_when_the_snapshot_itself_is_refused`, `test_a_halt_is_stated_from_the_run_status_alone`, `test_a_halt_no_frame_was_drawn_for_is_worded_as_one_rather_than_as_a_failed_step` |
| reading a run whose Reset the core refused as one still running, or as one that was reset | `SimulationController.reset()` builds the settings record that the fresh run definition opens on before it clears anything. So a refusal leaves the run exactly as it was, not half cleared. The refusal is a set of tissue flows that no longer sum to the cardiac output. Since `PL-HQF5` and `PL-Z0HN`, only a perfusion fraction set by bypassing its guard can cause it. The interface then halts the run through the failed-step path. The refusal is recorded as the failure. On a run that had already failed for something else, that earlier failure stays the reason, and the banner's way out states the refusal. The status word, the transport and the banner state the halt. The banner's way out says that no setting can repair the refusal, and that closing and reopening the application starts a new run. It does not name the Reset that was just refused, or a dial that cannot repair it (`PL-01GY`). The refusal names the two flows in L/min, the unit every readout shows, as they were set (`PL-M4M0`) | `test_a_reset_the_core_refuses_halts_the_run_visibly`, `test_a_reset_the_core_refuses_leaves_the_run_exactly_as_it_was`, `test_a_refused_reset_names_the_way_out_in_the_banner`, `test_a_tissue_flow_mismatch_is_stated_in_litres_per_minute` |
| comparing readouts with a chart that was drawn from different settings | the readouts come from the steps and the chart comes from the run definition. So before each step, `SimulationController.advance()` compares `AgentUptakeSystem.settings_key()` with the key it noted when the definition last recorded settings. A setting written onto the core without going through the controller halts the run on the last step on which both agree, with a banner saying why. Nothing in `app/` writes a setting that way. Reset then starts a new run from the settings the core holds at that point. A setting changed through the controller afterwards records the whole settings record. So that change brings the definition back into line rather than halting the run (`PL-XRN8`) | `test_a_setting_written_onto_the_core_past_the_controller_refuses_the_next_step`, `test_a_setting_written_onto_a_branch_s_core_past_its_controller_refuses_its_next_step`, `test_reset_after_a_setting_written_past_the_controller_runs_at_that_setting`, `test_a_run_whose_core_setting_moved_past_its_controller_halts_on_the_last_recorded_step` |
| reading the agent selector or a slider, used on a run whose snapshot refuses, as a control that took effect | the selector and the sliders read the snapshot through `RunView._snapshot_for_a_control`. On a refusal, that method halts the run and states the halt from the run's status, rather than letting the raised exception escape the slot unseen. It puts the selector back to the agent that the controller names, because the snapshot that would name it is what refused. Reset remains the way out that the banner names, unless a refused Reset has left its own way out in place. The controls stay live on a halted run rather than locked (project owner, 2026-10-12, ratified, over locking them, which would render the agent selector disabled) (`PL-V2HC`) | `test_an_agent_change_on_a_halted_run_restates_the_halt`, `test_a_slider_moved_on_a_run_whose_snapshot_refuses_halts_it` |
| reading the value printed beside a dial dragged into a halt as the value the run holds | after writing its banner, the halt writes every dial from `SimulationController.record()`. That record gives the agent and the four settings in force. It is read from the settings the compartments hold and from no compartment value. So the label beside a dial dragged into the halt shows the value that the dial and the run hold, not the value before the drag. Only a frame would have rewritten the label, and a run whose snapshot refuses draws no frame (`PL-85LJ`) | `test_a_drag_that_halts_the_run_leaves_its_label_on_the_dial`, `test_a_halt_is_stated_before_its_dials_are_written` |
| believing a setting above the vaporizer maximum was simulated | such a setting is **rejected, not clamped**, so no run proceeds on a value the user did not choose. The boundary value itself is accepted. The circuit accepts it, and so does the settings record a run is built from, which carries the maximum beside the dial (`PL-BBMG`) | `test_rejects_delivered_concentration_above_the_vaporizer_maximum`, `test_explicit_delivered_concentration_above_the_agent_max_is_rejected`, `test_accepts_delivered_concentration_exactly_at_the_vaporizer_maximum`, `test_rejects_a_dial_above_the_vaporizer_maximum`, `test_a_run_cannot_open_or_change_under_a_dial_above_the_vaporizer_maximum` |
| reading a displayed value as resolved to its last digit | displayed precision is a recorded choice within a justified band. The model keeps the precision that the display discards, rather than rounding its own state | `test_the_model_keeps_precision_the_display_throws_away`, `test_concentration_decimals_are_a_choice_within_a_recorded_band` |
| reading a control mark on the timeline as a measurement | the timeline labels its marks "Settings only — not a measurement." | `test_the_interface_says_a_control_mark_is_an_input_not_a_measurement` |
| reading a modelled compartment value as a measured one | the readout section states, beside its values, that they are model outputs and not measurements (`INTERPRETATION_DISCLAIMER_TEXT`, `PL-2K1R`). The chart's hover names every value it reports as modelled (§ "The chart's hover readout: what the tooltip may show") | `test_the_interface_says_the_readouts_are_model_outputs_not_measurements`, `test_the_readouts_say_they_are_model_outputs_beside_the_values`, `test_the_hover_reports_the_drawn_state_through_the_formatters` |
| reading one compartment's concentration as another's where two traces are drawn on top of each other | the compartment is named in text on every value line. Every compartment whose drawn point, at the instant the pointer names, is inside the hover radius is reported under its own name. The hover does not choose the nearest trace for the reader (§ "Where more than one trace answers"). This matters because the percent axis is fixed at 3 MAC for every agent (`CHART_AXIS_TOP_MAC`). On that axis, fat's whole first hour spans less than 4 px. So the slow compartments are drawn within a pixel or two of one another, and no aim can separate them (`PL-0RZ0`, `PL-QYBW`) | `test_two_compartments_within_one_hover_radius_answer_under_their_own_names`, `test_a_contended_hover_names_no_run_while_only_one_is_drawn` |
| comparing two compartments of one run in one hover box as one moment when the box took them from different instants | every compartment of one run is reported at the run's drawn instant nearest the pointer in time. So the instant that labels a value depends only on the pointer's position along the time axis. The pointer's height decides only what is in reach. Before this, each trace's own nearest point had been taken in both dimensions. That labelled 70.1% of the single-run chart's multi-reading boxes with two instants, up to fifteen minutes apart on the 12-hour axis (§ "Where more than one trace answers", `PL-1K9G`) | `test_every_compartment_of_one_run_answers_at_one_instant`, `test_a_vertical_hand_movement_never_moves_the_instant_a_hover_reports`, `test_a_trace_answers_only_where_its_point_at_the_named_instant_is_in_reach` |
| reading the hover's value as a live readout after the pointer has left the plot | the box responds only while the pointer is over the plot (§ "When it answers"). Leaving the plot takes the box down at once, along with any pointer move still waiting for a response, so no later frame responds for a pointer that has gone. If the box were left up, it would update again on every frame. While a run plays, it would climb with the run, for an instant the reader is not looking at (`PL-LTKL`) | `test_the_hover_hides_when_the_pointer_leaves_and_a_later_frame_does_not_bring_it_back` |
| reading one run's displayed value, or the record of what was changed on it, as the other's while two are compared | the run is named in text wherever a value is shown. First, it is named on each run's own readout panel (§ "Minimum displayed outputs"). Second, while more than one run is drawn, it is named in the chart's hover readout: on its first line where one run answers (§ "The hover and the run it belongs to"), and on each value line where several do. Every run inside the hover radius is reported, so no hand movement can swap which run is read (§ "Where more than one trace answers"). This is needed because the hover floats free of the legend, and line width has no textual equivalent. Third, it is named on the three advisories that sit in a chart rather than on either run's panel: the wash-in state line, the off-scale notice and the count of control changes the chart could not mark (`PL-L59K`). These stack one line per run, so they are named for the same reason as the hover. Stacking order is declared nowhere on screen, and the run names sit in the unconditional region above the charts. Without names, the branch's F_A/F_I would be readable as the trunk's, and its off-scale notice could be attributed to a run whose traces are all inside the axis (`PL-25DD`). Fourth, it is named in the headings of the two record panels: the agent-accounting validation in the sidebar, and the control-change record in the right column of the unconditional region. Each of these stacks whole panels rather than lines, one per run. So the name goes in each panel's own heading, where it travels with the panel rather than with its position in the column. This matters because "What was changed during this run" over a list of settings, read as the other run's, says the trunk received an intervention it never got (`PL-C3GS`). Fifth, it is named on the notice banner. The runs share one place for this banner, between their transport rows and their readouts. The banner qualifies the values rather than showing one. "The values shown are the last completed step", read as applying to the whole dashboard, says both runs' readouts are frozen at a failed step when one is still going. "The simulation is unchanged and still running its previous setting" is false of the run that took the setting. Stacking order does not separate these banners at all, because a banner with nothing to say is hidden and takes no room. With one run halted, its banner appears in the same place whichever run it belongs to, and the words are identical (`PL-TSZM`, `PL-T91K`) | `test_the_hover_names_the_run_only_while_more_than_one_is_drawn`, `test_two_runs_within_the_hover_radius_answer_under_their_own_names`, `test_a_small_pointer_movement_never_swaps_which_run_the_hover_answers`, `test_the_wash_in_state_and_off_scale_lines_name_their_run`, `test_a_lone_run_leaves_the_shared_chart_lines_unnamed`, `test_each_run_s_unmarked_changes_line_is_named_while_runs_are_compared`, `test_the_sidebar_panels_name_the_run_they_record`, `test_a_lone_run_leaves_the_sidebar_panel_headings_unnamed`, `test_the_halt_and_refusal_banners_name_their_run`, `test_a_halt_stated_without_a_frame_still_names_the_run_it_stopped`, `test_a_lone_run_leaves_the_notice_banner_unnamed`, `test_hidden_notice_banners_take_no_height` |

<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

### The row that was only partly mitigated until the Qt port

The last row deserves a close reading, because its mitigation was incomplete
from 2026-09-13 until the dashboard moved to Qt, and this section said so
rather than implying otherwise.

Three statements existed, and they did not cover the same surface. `README.md`
states that "Every value on screen is a model output, never a measurement".
But a learner running the application never opens `README.md`. The
control-input timeline carries "Settings only — not a measurement.", which is
exact but covers only the timeline's marks. The interface's own standing
notice is an **educational-use** disclaimer. It tells a reader what the tool
is *for*, not how to read a number on it. Nothing told a reader that the
compartment readouts and the chart traces are modelled predictions rather than
measurements. That distinction is exactly the one this project's value depends
on. The compartments that the project exists to display are the ones no
monitor shows, so a reader has no measured counterpart to check them against.
The polish of the display also invites the opposite reading, that the values
are measurements.

The project owner agreed on 2026-09-13 that the interface should carry an
interpretation statement separate from the use disclaimer. The statement
landed with the dashboard port (`PL-2K1R`, on `PL-25KS`). Its wording follows
the timeline's pattern. It is short, it sits beside the thing it qualifies,
and it says what the value *is* rather than what the user must not do:
**"Model outputs — not measurements."** It appears once, on the heading row of
the readout section, beside "Modelled concentrations: {agent}". It is not
repeated on the chart, for two reasons. A disclaimer that is repeated stops
being read. And the chart's own hover text already names every value it
reports as modelled. The wording is the port's choice, and the owner may
revise it. The requirement is the hazard table's row above.

## How this document is held to the tree

The hazard table above applies a rule to its own rows: *every row names the
test that holds it, or says plainly that it has none*. This section applies
the same rule to the whole document. The four clauses below generalise that
rule. They were adopted on 2026-09-19 (`PL-4FBP`, project owner, ratified)
over two alternatives: refusing the convention, and marking free prose one
sentence at a time.

The clauses exist because, without them, a sentence's link to the tree lives
only in the reader's head. A sentence reads exactly as it did when it was
true, even after the test it names has been renamed away, the field it
describes has been removed, or the number it states has drifted. That is the
silent-wrong-answer shape that `CLAUDE.md` requires to be caught in code
rather than remembered. A review on 2026-09-19 checked 38 of this document's
own required invariants and required tests against the suite. Two of them were
only partly enforced, and no check had surfaced either one. The practice is
the established one for software of this class. IEC 62304 § 5.1.1 requires
the software development plan to carry traceability between system
requirements, software requirements, software system tests and risk control
measures. The FDA's *General Principles of Software Validation* (2002) § 5.2.2
names traceability analysis among the validation tasks. The problem itself is
set out by Gotel and Finkelstein, *An analysis of the requirements
traceability problem*, ICRE 1994, pp. 94–101.

**Bound: this document and `README.md`**. These are the two documents held to
the specialist standard, and the two that a reader of a displayed value
trusts. `ROADMAP.md`'s frozen lists are already families under clause 2, and
its prose falls under clause 4. `docs/ARCHITECTURE.md`'s package map is
already a family. Every thread in `docs/WORKING_NOTES.md` is dated, so clause
4 governs it and nothing else does. Apparatus prose is not bound. That covers
`.claude/`, `CONTRIBUTING.md` and `docs/resident-instructions.md`. In those
files, the counts rule below is advice rather than a requirement.

1. **A live assertion names what it asserts.** Some sentences assert a fact
   about the tree. Examples are that a test enforces an invariant, that a
   field exists, that a value is *N*, or that a job runs something. Such a
   sentence names the entity in a form that the tree resolves. That form is a
   code-spanned test, path, symbol or field, or a `<!-- provenance: -->`
   marker over a restated number. This is an obligation on the author, and it
   does not depend on what the checker can reach. `check_named_tests`,
   `check_citations`, `check_prose_provenance` and `check_make_targets` in
   `tools/doc_check.py` already resolve every one of those forms.
2. **An enumerated family is held complete.** Some headings promise one
   assertion per member. Examples are the invariants list, the required-tests
   subsections, the displayed-outputs list, the hazard table, a frozen gate
   list and a marked enumeration. In such a family, every member names its
   entity or carries the declared-none form of clause 3.
   `check_bound_families` fails a member that does neither. A family joins
   that check's table when its annotation pass lands. So the check never keeps
   `make check` red for work that is not yet done.
3. **The declared-none form names the item that owes the link.** An absence is
   written ``no test yet (`PL-XXXX`)``. The leading words belong to the
   sentence, and the parenthesis is fixed. The parenthesis names an item that
   is still open in the queue. Three things follow. A script can tell a
   forgotten link from a declared absence. An exemption becomes a forward
   reference to work rather than a permanent hole. And closing the named item
   without adding the link fails the check.
4. **A dated statement is a record, held to its date and never to the tree.** A
   sentence may carry a date, sit under a dated heading, or sit inside a
   shipped release's section. Such a sentence asserts what was true at that
   date. It is not linked, not checked, and **not edited to carry a later
   fact**. A later fact is appended with its own date. `check_gate_counts`
   draws the same line from the checker's side. It calls a frozen count
   "a dated fact that must never change", and this clause makes that the
   author's rule as well.

**Counts, which both halves meet.** A count in prose is stated only where a
check ties it to what it counts, or else the count is dated. Two examples of
a checked count are a group heading over its entries and a marker over a data
value. Otherwise the rule is stated without the number, or the number is
read from the tool that prints it. This extends the project owner's
2026-09-13 decision on data-file rows (`PL-9LXK`) beyond those rows. It is
also why this document states the sizes of its own families nowhere.

**What an assertion that names nothing looks like.** Inside a bound family, it
uses the declared-none form, or the check fails. Outside a bound family but in
a bound document, it is a number without a marker or a claim without a code
span. Such an assertion is left to the close-out sweep by decision, not by
oversight, and `tools/doc_check.py candidates` prints it when its subject
changes. Anywhere, an assertion that is dated is a record.

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

Only sevoflurane was modeled in v0.1.0. Isoflurane and desflurane were added
in v0.2.0 as additional selectable agents. They use this same section's
equations unchanged (see § "Status" and "v0.2.0: isoflurane and desflurane"
under § "Parameter provenance").

## Model boundary

The modeled system contains:

1. one ideal, perfectly mixed breathing circuit;
2. one ideal, perfectly mixed alveolar gas compartment;
3. one venous blood pool;
4. one vessel-rich tissue group;
5. one muscle tissue group; and
6. one fat tissue group.

Arterial blood is not a separate mixing compartment. Pulmonary exchange is
modeled as flow-limited. Blood leaving the lungs is assumed to equilibrate
instantaneously with alveolar gas. The arterial partial-pressure-equivalent
fraction is therefore defined as $`F_a \equiv F_A`$, with no arterial volume,
mixing delay, or independent state. This matches the flow-limited mammillary
structure of the Gas Man reference simulator, from which this project's
sevoflurane and patient parameters are drawn. Gas Man's computational model is
a four-compartment system: alveolar gas plus the vessel-rich, muscle, and fat
groups. In that system, arterial tension is displayed but not tracked as an
independent compartment. See:

- Philip JH. Gas Man Version 4.1 Teaches Inhalation Kinetics. Society for
  Technology in Anesthesia. <https://www.stahq.org/files/7913/2743/1066/Abstract_57.pdf>
- Do distribution volumes and clearances relate to tissue volumes and blood
  flows? A computer simulation. BMC Anesthesiology.
  <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1508141/>

This is a deliberate simplification. It is documented here rather than left as
an unfilled parameter. See § "Known limitations."

Inspired gas is likewise not a separate compartment. The circuit is one ideal,
perfectly mixed volume with no dead space and no separate inspiratory and
expiratory limbs. So the gas the patient inspires *is* the circuit gas. There
is no second state to carry and no transport delay between the two. The model
therefore keeps one gas-phase state between the vaporizer and the alveoli. It
names that state for the clinical quantity rather than for its container: the
**inspired fraction** $`F_I`$, the middle term of the literature's
$`F_D \rightarrow F_I \rightarrow F_A`$ cascade. The container keeps its own
name. $`V_C`$ is the circuit's volume, and $`M_C`$ is the agent stored in it.
So $`M_C = V_CF_I`$ says what it is: a volume of apparatus holding gas at the
inspired fraction.

This is an assumption of the circuit model, not a property of breathing
systems in general. It is what makes the displayed $`F_A/F_I`$ ratio the
textbook one, the canonical teaching curve of inhaled-anesthetic uptake. See
§ "F_A/F_I as a displayed ratio". A multi-limb system, such as Lerou and
Booij's three-part model, separates inspired gas from mean circuit gas. In
such a system the two would be distinct states, and this model's single
$`F_I`$ would no longer describe both. That departure would have to be
recorded here before the model was extended that way.

The naming is Hendrickx and De Wolf's, which is the field's naming. They set
out the gas-phase cascade and the symbols $`F_D`$, $`F_I`$ and $`F_A`$ on
pp. 161-162. They attribute the $`F_D - F_I`$ gradient to rebreathing on
p. 169, and the $`F_I - F_A`$ gradient to uptake on p. 171. They describe the
didactic role of the $`F_A/F_I`$ curve on p. 167 (Hendrickx JFA, De Wolf A.
Special aspects of pharmacokinetics of inhalation anesthesia. In: Schüttler J,
Schwilden H, eds. Modern Anesthetics. Handbook of Experimental
Pharmacology 182. Springer, 2008:159-186). The project owner supplied this source, and it
is recorded at that depth. The pages above are what the citation is being used
for, and no page beyond them is relied on here.

**One symbol to read carefully.** $`F_I`$ is the inspired fraction, and
$`F_i`$ is tissue group $`i`$'s fraction. The two differ only in case. The
collision comes from the literature, not from this document, because both
conventions are standard. It is kept rather than worked around, because
renaming either symbol would leave this model's symbols disagreeing with every
source a reader arrives from. Where both appear in one expression, the tissue
index is written out.

The external inputs and outputs are:

- agent entering through fresh gas;
- carrier gas entering through fresh gas;
- an equal volume of mixed circuit gas leaving through the circuit exhaust; and
- no metabolism or other chemical destruction of the agent.

The circuit and patient form a closed recirculating exchange path except for fresh-gas inflow and circuit exhaust.

**That circle is semi-closed, and this document says so rather than leaving
it to be inferred.** The exhaust above is unconditional. It runs whenever
fresh gas runs, at exactly the fresh-gas rate. Closed-circuit operation is a
different conservation statement and is outside what these equations
describe. Closed-circuit operation means a fresh gas flow titrated down to the
patient's uptake, or a machine mode that shuts the surplus gas valve outright.
The section "Breathing circuit" argues and sizes that boundary, and the
section "Known limitations" lists it.

## Conventions

### Time

Simulation time is explicit state and is measured internally in seconds.

Flows entered in liters per minute are converted to liters per second:

$$
\dot V_{\mathrm{s}} = \frac{\dot V_{\mathrm{min}}}{60}
$$

**The liters per minute is the record, and the per-second value is derived
from it.** A run stores each flow as it was set, in liters per minute. The
governing equations read a per-second value. That value is computed from the
stored setting at the point where the equations read it, and it is not stored
beside the setting. The conversion does not run backwards. Multiplying a
per-second flow by 60 does not return the setting for 7 of the 101 cardiac
outputs on a 0.1 L/min grid across the supported 0 to 10 L/min range
(1.9, 3.8, 3.9 and 7.6 to 7.9 L/min). The tissue flows formed from cardiac
output inherit the difference. So settings rebuilt from a per-second record would
describe a run that nobody set up. `UptakeEquationSettings` in
`core/governing_equations.py` stores the flows this way, and `PL-SM5V` records
the measurement.
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

Wall-clock time may schedule interface updates, but it must never be used as simulation time.

Seconds are the unit wherever this document, the core and the run definition
state a time. The interface shows that one quantity in **one** form, and it
adds no second unit when it does so. The clock, every recorded control stamp
and the chart's axis ticks all appear as compound durations. Every component
of a duration carries its own unit: `45s`, `1m30s`, `1h23m45.6s`, `24h`. A
component that is zero is dropped. A tenth of a second is shown only where
there is one, so a stamp still identifies the step at which it was taken.

The clock and the stamps showed seconds until `PL-Q4M4` and `PL-CZFY`. They
were moved onto the axis's form because the two forms were on screen together.
A reader looking for a control mark stamped `5400.0 s` on an axis reading
`1h30m` had to convert by hand between two displayed forms of one quantity. At
the supported 24-hour run length, the clock's top reading was `86400.0 s`.
That is false precision on a boundary that this document states in hours
(`PL-Q4M4`, `PL-CZFY`).

The width of time that the chart is drawing is the one thing still spelled out
in words: `15 minutes` above an axis whose last tick reads `15m`. That is a
difference of register, not a second form. It is a phrase that a reader
chooses from a selector and sees again in a caption. It is not a tick
competing for width. "The chart's time base" is where that choice is decided,
and "Displayed precision" sets the precision at which each form is shown.

#### Simulated time is a count of steps, not a running total

A run takes one step size and keeps it for its whole length. Simulated time
is the number of completed steps multiplied by that step. It is one
multiplication, rounded once. It is never a total accumulated one step at a
time.

The two methods agree to about 35 ns over a four-hour run at the shipped 0.1 s
step. That is far below anything displayed, so the multiplication does not buy
accuracy. What it buys is path-independence. The product depends only on how
far the run has gone. A running total depends on the order and number of the
additions that produced it. Ten steps of 0.1 s sum to 0.9999999999999999 and
multiply to 1.0.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

A step that differs from the one a run has already taken is rejected by
raising a `SimulationConfigurationError`, and it is not added to the count.
The product needs a single step to multiply by. A count of steps means a time
only while every step in it is the same size. A run stepped at two cadences
would leave `elapsed_s` no step to multiply by. Reset clears the count and the
step together, so a fresh run may take a different step.

#### The reproducibility guarantee

**A run is a function of its inputs and of the number of steps taken, and of
nothing else.** The interface schedules its ticks with the wall clock. But the
number of steps that a tick takes is a setting the reader chooses. It is never
a measurement that the loop makes. No tick takes extra steps to make up
simulated time that a slow tick lost, and the run loop reads no clock. Suppose
a machine wakes the loop late, drops a frame, or runs the whole session
slowly. Its run therefore reaches a given step *later in real time*, and the run is
identical in every state, keyframe and control stamp. It runs slower. It does
not run differently.

**This is measured, not asserted.** `tools/import_boundary_check.py` runs in
`make check` and CI. It fails the build on a `time`, `datetime`, `random`,
`secrets` or `uuid` import in any module under `src/anesthesia_sim/core/`. The
reason for each entry is recorded beside it in the check's `BOUNDARIES` table.
The restriction stops at `core/` because the paragraph above allows the
interface its wall clock. The check closes every route by which a compartment
could get a clock of its own: the clock directly, an unseeded generator, or an
identifier made from either. Any of those routes would leave this section
looking verified while it was false (`PL-J833`, `PL-ZK9R`).

Two of those imports are worth naming, because seeding cannot undo their
effect. `secrets` draws from `random.SystemRandom`. Its `seed()` is a
documented stub, and its `getstate()` raises an error. `uuid.uuid1()` mixes
the current time with the host's hardware address. That makes a run differ
between *machines* as well as between runs.

So, given the same initial state, parameters, step size, setting changes and
event ordering, two runs taken to the same step count produce **element-wise
identical** run definitions and snapshots. They are identical, not merely in
agreement within a tolerance. They have the same segments, the same keyframes,
and the same state at step *n*, which is at simulated time *n* times the step
in both runs. Any comparison of one run against another relies on this
property. That includes comparing a branched run against the run it branched
from, at every instant they share.
§ "What a branch comparison asserts, and what it does not" says what a
comparison built on this property may and may not claim. That section limits
the drawing, and this paragraph limits the arithmetic behind it.

**What carries this for a state that is derived rather than stepped to.** The
paragraph above is a claim about the stepped system. It relies on every caller
taking the same step width. With the step fixed, only one sequence of
arithmetic reaches step *n*. A run held as its definition records no samples
and fixes no width. A state is computed when it is asked for, and more than
one sequence of arithmetic can reach the same instant. "The canonical
evaluation rule" under § "Runtime controls" is what carries the guarantee
there. That rule is stronger than this paragraph in one respect and narrower
in another. Two evaluations of one run definition at one instant are
bit-identical, not merely reproducible across runs. And only values from the
canonical path may be stored, exported or branched from. The two guarantees
divide the work. The step count covers the stepped system that the snapshot is
read from. The canonical rule covers every state derived from the run
definition.

**Playing a run faster does not make it a different run.** The interface
offers a playback rate, which is how much simulated time advances per second
of real time. The rate is implemented as the number of *whole steps* that a
tick takes, never as a larger step. So the same case played at real time and
at three hundred times real time is the same steps, in the same order, at the
same size. The result is an element-wise identical run definition and
snapshot, reached at different real times. A rate that resized the step
instead would fall under the first of the four exclusions immediately below.
It would be a second numerical solution of the same equations, not the same
run watched faster. It would also make a displayed value depend on how fast
the reader happened to be watching. That is a determinism failure that no
label repairs.

The guarantee does not cover four things, and none of them is a defect:

- **A different step size.** Two runs at different steps are two roundings of
  the same solution, not two solutions. The step is exact, so what separates
  them is floating-point accumulation. "Step-refinement test" is what bounds
  that difference.
- **A different model version.** The guarantee applies within one version of
  the equations and one parameter set. That is why both are versioned.
- **A different platform.** Addition, multiplication and division are
  correctly rounded, so they give identical results everywhere. But the step's
  propagator is built from one `exp()` call. That call is a library function
  whose last bit may differ between platforms, interpreters and math
  libraries. The propagator is also built from a series and a sequence of
  squarings, and a compiler may reassociate their summation order.
  Reproducibility is claimed for one build, not across all of them.
- **Elapsed real time.** How long a machine takes to reach step *n* is a
  property of the machine. So is how many steps it has reached when a
  wall-clock minute is up. Both are deliberately not properties of the model.

### Concentrations

Every concentration that the model computes is a dimensionless
partial-pressure-equivalent fraction from 0 through 1. Only one concentration
is set rather than computed: the vaporizer dial. The model stores the dial as the
percent that was dialled, and it derives $`F_D`$ from that percent, as
described below.

The gas-phase cascade is named as the inhaled-anesthetic literature names it,
$`F_D \rightarrow F_I \rightarrow F_A`$. So the middle gas-phase state is
$`F_I`$ (inspired). It is not a symbol named after the breathing circuit that
holds the gas. The container keeps the apparatus subscript: $`V_C`$ is its
volume and $`M_C`$ is the agent in it. So a capital $`C`$ names the rig, and
$`F_I`$ names the gas. § "Model boundary" above states the assumption that
makes the two one quantity, and it states what would break that assumption.

For example, $`F = 0.02`$ represents a 2% gas-phase concentration.
<!-- not-restated: 2 % -->

Two other places quote the same quantity in percent of an atmosphere, and
they cannot do otherwise: a vaporizer dial and a MAC. The conversion between
the two forms is:

$$
\text{percent} = 100F
$$

`src/anesthesia_sim/core/concentration.py` is the only place where that
arithmetic is written, in both directions. The two forms are distinct types
there, so a type checker rejects a percent where a fraction is wanted. Since
`PL-4R3W`, the code also rejects that mix-up at run time wherever a
concentration is stored (see below). Since `PL-SWD1`, the conversion itself
rejects a value that is already in the form it returns, rather than
converting it again. Since `PL-1DP1`, the conversion also rejects a value that
was never built as the form it takes, a bare number included, because such a
value carries no form to convert it by. The conversion is used in two places
and no others. The circuit and the recorded settings derive $`F_D`$ from the
dial's percent where the governing equations use it. The interface converts
for display. Before `PL-WVSK`, the factor was written out twelve times across
six modules, and seven of those copies were on the path to a displayed value.
This section also said then that the interface alone converted. `core/` had
contradicted that statement ever since the agent data files began carrying a
MAC.

**The percent dialled is the record, and $`F_D`$ is derived from it.** The
circuit, the settings that a run records for each stretch, and the control
timeline all store the vaporizer setting as the percent that was dialled.
`AgentUptakeSystem.for_agent()` opens the dial at the published percent from
the agent data file, without converting it. The conversion does not run
backwards. Multiplying a fraction by 100 does not always return the percent
it came from. It fails for 126 of the 801 settings that a 0 to 8% dial makes
at 0.01% steps. The first failure is at 0.23%, and 0.9% comes back as
0.9000000000000001. So a record kept as a fraction could not give back what a
learner dialled. § "Time" states the same rule for the flows, and `PL-NJPB`
records the measurement. A rejected setting is quoted back in the percent it
was set in, beside the vaporizer maximum. That maximum is stored in the same
unit, so the message gives both values in percent.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

The interface also converts to the second display unit, a multiple of the
running agent's 1 MAC. This unit rescales the percent above by one constant
per agent, and it introduces no new state:

$$
\text{MAC multiple} = \frac{100F}{\mathrm{MAC}_\%}
$$

The section "MAC multiples as a display unit" states what that quotient does
and does not assert. The quotient is not the definition of a modeled
quantity, and nothing in `core/` computes it.
The divisor is stored as a `MacPercent` (`core/concentration.py`). That type
is a `Percent` that rejects zero when it is built. So the quotient is never
formed against a zero MAC. Every formatter that forms the quotient rejects a
divisor that was not built as a `MacPercent` (`PL-F9TC`). The type sets no
lower bound other than zero. A MAC far below any real agent's MAC would still
give multiples too large to read. The shipped MACs are 1.2% to 6.0%.
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- provenance: data/agents/desflurane.json mac_percent = 6 -->

A concentration fraction must always be finite and satisfy:

$$
0 \leq F \leq 1
$$

**The range is enforced by the type, where a value is built** (`PL-4R3W`).
`Fraction` and `Percent` in `core/concentration.py` check a value when it is
built. Each rejects a value that is not finite, or that lies outside 0 to 1
for a `Fraction` or 0 to 100 for a `Percent`. Each rejects a value of the
other type, because that is a missed conversion rather than a concentration
out of range. Each raises a `TypeError`, before the range is checked, for
anything that is not an `int` or a `float`, such as a `bool`, a `Decimal` or a
string. Each raises the same error for a value that was built as any other
checked quantity, such as a step, a flow, an instant or a count. Each stores
minus zero as zero. `core/checked_number.py` states these rules once, for the
concentrations and for the flows: what counts as a number, that one checked
quantity is never built from another, and that minus zero is stored as zero
(`PL-LLMN`, `PL-979Z`; § "Supported input ranges"). Every place that stores a
concentration takes the type. These
places are each compartment's setter, the driving fraction that a
compartment's own closed form takes, `BreathingCircuit` when it is built or
set, the `BreathingCircuitState` that a rollback restores it from, the
`UptakeEquationSettings` that a run is built from, and the `AgentParameters`
that an agent's data file is parsed into. `AgentParameters` stores the agent's
MAC and vaporizer maximum. Each of those places rejects a value that was not
built as the type, a bare number included. So a concentration is checked
once, where it is built, rather than again at each way in. A fraction that a
step computes is built as a fraction before any compartment stores it. It is
built under the name of the compartment that will store it
(`AgentUptakeSystem._write_state_vector`). So a computed value outside the
range halts the run and names that compartment, instead of being stored or
shown. The one limit comes from the type itself. A circuit built without an
agent defaults its vaporizer maximum to 100%. At that dial setting, a
computed fraction can round past 1, and the type rejects it there. No
supported setting computes a fraction outside the range, and
`core/concentration.py` records the measurement.

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

**Nothing the model computes depends on the condition, and one kind of
operation will.** Every governing equation moves dimensionless fractions and
physical volumes, and every partition coefficient is a ratio. So the
trajectories, the mass-balance identity and every displayed concentration do
not depend on which condition the unit names. If the condition changed, no
number under § "Governing equations", "Conservation of agent mass" or
"Minimum displayed outputs" would move. Only one kind of operation uses the
condition: a conversion *out* of the unit, into moles, mass, or the
millilitres of liquid that a vaporizer is filled from. For that conversion,
the two candidate conditions differ by a factor of 1.058. The reason is that
the ideal-gas molar volume is 24.055 L/mol at 20 °C and 25.450 L/mol at 37 °C.

**Why 20 °C, and what it was chosen over** (project owner, 2026-09-17,
ratified, over 37 °C, the condition at which the stored amounts are natively
exact, `PL-S6WW`). The choice rests on three grounds. The first can be
checked, rather than resting on convention.

1. **The published vapour-to-liquid constants are 20 °C constants.** The
   consumption literature quotes one composite number per agent: the vapour
   volume obtained from 1 mL of liquid. Biro gives isoflurane 195 mL,
   sevoflurane 184 mL and desflurane 210 mL. That number can instead be
   derived from the primary density measurement and the molar volume above.
   The derivation reproduces all three within 0.7 % at 20 °C. It reproduces
   none of them at 37 °C, where the same derivation runs 5.1–6.3 % high:

   | Agent | Liquid density at 20 °C, g/mL | Molar mass, g/mol | Derived mL vapour per mL liquid, 20 °C | Biro's constant | At 37 °C |
   | --- | --- | --- | --- | --- | --- |
   | Sevoflurane | 1.5203 | 200.055 | 182.8 | 184 | 193.4 |
   | Isoflurane | 1.5019 | 184.492 | 195.8 | 195 | 207.2 |
   | Desflurane | 1.4651 | 168.038 | 209.7 | 210 | 221.9 |

   The densities are those of Laster, Fang and Eger. They were measured in
   four 50-mL volumetric flasks at 20 °C, with a temperature coefficient of
   −0.00250 ± 0.00014 g/mL per °C over 0–25 °C. The molar masses are exact
   from the formula. So the field's constants are referenced at 20 °C as a
   matter of arithmetic rather than of convention. A model that declared
   37 °C would either mix two conditions or print consumption figures 5.5 %
   below the numbers a reader can look up. That 5.5 % is $`1 - 1/1.058`$, the
   same factor for every agent. Inverted for display, 1 L of vapour is
   5.47 mL of liquid sevoflurane here, and it would be 5.17 mL on a 37 °C
   reference.

2. **The terms a consumption figure converts are fresh gas, and fresh gas is
   at ambient temperature.** $`M_{\mathrm{delivered}}`$ and
   $`M_{\mathrm{exhausted}}`$ both integrate $`\dot V_F`$, the flow at the
   common gas outlet. That flow is carrier gas plus the vapour that the
   vaporizer added. It is on the machine side of the patient, at
   operating-room temperature rather than at 37 °C. A cost or waste figure is
   computed from those two amounts ("Planned milestones" item 28). Declaring
   20 °C makes them exact. Declaring 37 °C would leave them as the
   approximated terms. It would *also* call for an ambient-to-body correction
   on $`\dot V_F`$ that no equation here carries. That correction would be a
   change to the governing equations rather than to a label.

3. **The reference implementation's own constants are 20 °C constants, and
   its litres carry no condition at all.** Gas Man states a condition in one
   place only. That place is the `GASMAN.INI` parameter written `Volatility=209
   Vapor/Liquid volume ratio (20'C)`. Gas Man never states a condition on the
   litres of uptake and of delivered agent that it displays. This model has
   the same structure: the condition is used at the vapour-to-liquid boundary
   and nowhere else. Gas Man's five printed expansion constants settle which
   condition that is. The 20 °C derivation reproduces every one of them, and
   the 37 °C derivation reproduces none:

   | Agent | Gas Man | Derived, 20 °C | Derived, 37 °C |
   | --- | --- | --- | --- |
   | Halothane | 228 | 227.7 (−0.15 %) | 240.9 (+5.6 %) |
   | Enflurane | 198 | 198.6 (+0.29 %) | 210.1 (+6.1 %) |
   | Isoflurane | 196 | 195.8 (−0.09 %) | 207.2 (+5.7 %) |
   | Sevoflurane | 183 | 182.8 (−0.11 %) | 193.4 (+5.7 %) |
   | Desflurane | 209 | 209.7 (+0.35 %) | 221.9 (+6.2 %) |

   The 20 °C derivation is within 0.35 % on all five, against 5.6–6.2 % at
   37 °C. This table is two agents wider than the set this model carries. The
   two extra agents are the two whose densities Laster, Fang and Eger measured
   in the same experiment. This project's partition coefficients, MAC divisors
   and reference patient are the Gas Man set ("Source hierarchy"). So the
   trajectories that these amounts come out of are that program's arithmetic.
   Adopting a different reference for the same volumes would make this model's
   litre and Gas Man's litre different quantities, even though every parameter
   feeding these volumes is shared with Gas Man.

**37 °C was the alternative, and it is not a poor one.** This model's
partition coefficients were measured at 37 °C. The alveolar, venous and
tissue compartments are physically at 37 °C. So 37 °C is the condition at
which the *stored* amounts are natively exact. It was not chosen, for two
reasons. The amounts that leave the unit are the fresh-gas terms rather than
the stores. And the published constants that any figure will be compared
against are 20 °C constants. What choosing 20 °C costs is recorded under
§ "Known limitations".

The sources for this section are listed below, with the route by which each
was read.

- Laster MJ, Fang Z, Eger EI II. *Specific gravities of desflurane, enflurane,
  halothane, isoflurane, and sevoflurane.* Anesth Analg 1994;78(6):1152-3.
  PMID 8198275, doi:10.1213/00000539-199406000-00022. Retrieved from PubMed
  and verified against the abstract on 2026-09-17.
- Biro P. *Calculation of volatile anaesthetics consumption from agent
  concentration and fresh gas flow.* Acta Anaesthesiol Scand
  2014;58(8):968-72. PMID 25060161, doi:10.1111/aas.12374. Retrieved from
  PubMed and verified against the abstract on 2026-09-17. The abstract gives
  the four constants but does not itself state their temperature. That is why
  the reproduction above is the evidence, and not the citation.
- Philip JH. *Workbook for Gas Man*. Appendix C's `GASMAN.INI` listing is the
  source for the `Volatility` parameter. Chapter 10's closed-circuit
  liquid-injection section (printed pp. 103-105) is the source for the five
  expansion constants. In that section the constants are the unit of an
  *input*, the volume injected, rather than of a readout. Both were read from
  the private reference corpus on 2026-09-16 and recorded in `PL-S6WW` and
  `PL-B396`. `docs/references/README.md` § "Philip — *Workbook for Gas Man*"
  has the extraction note. The workbook is Tier 3 under § "Source hierarchy":
  it fixes what the reference implementation does, and it measures nothing.

## Symbols

The **Code** column names the one expression in `core/` that denotes each
symbol, written `ClassName.accessor`. The column maps this specification onto
the implementation. It is not a key for reading the implementation. A reader
who knows these variables should be able to follow `core/` without it. If a
reader needs this column to get through the code, that is a defect in the
code, not a use for the table.

| Symbol | Meaning | Unit | Code |
| --- | --- | --- | --- |
| $`t`$ | Explicit simulation time | s | `SimulationState.elapsed_s` |
| $`\Delta t`$ | Simulation step | s | `SimulationState.simulation_step_s` |
| $`F_D`$ | Delivered fresh-gas agent fraction | dimensionless | `BreathingCircuit.delivered_partial_pressure_fraction` |
| $`F_I`$ | Inspired agent fraction, which is the gas in the breathing circuit (see § "Model boundary") | dimensionless | `BreathingCircuit.inspired_partial_pressure_fraction` |
| $`F_A`$ | Alveolar agent fraction | dimensionless | `AlveolarCompartment.partial_pressure_fraction` |
| $`F_a`$ | Arterial partial-pressure-equivalent fraction. Arterial blood is flow-limited, so $`F_a \equiv F_A`$, and $`F_a`$ is not an independent state | dimensionless | — no attribute: the code reads `AlveolarCompartment.partial_pressure_fraction` wherever an arterial fraction is required |
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
| $`\lambda_{b:g}`$ | Agent blood:gas partition coefficient | dimensionless | `AgentParameters.blood_gas_partition_coefficient` |
| $`\lambda_{i:g}`$ | Tissue:gas partition coefficient for group $`i`$, which is the coefficient the agent data files store | dimensionless | `TissueGroup.tissue_gas_partition_coefficient` |
| $`\lambda_{i:b}`$ | Tissue:blood partition coefficient for group $`i`$, derived as $`\lambda_{i:g}/\lambda_{b:g}`$ | dimensionless | `TissueGroup.tissue_blood_partition_coefficient` |
| $`M_C`$ | Agent stored in the breathing circuit | L equivalent gas | `BreathingCircuit.agent_amount_l` |
| $`M_A`$ | Agent stored in alveolar gas | L equivalent gas | `AlveolarCompartment.agent_amount_l` |
| $`M_v`$ | Agent stored in venous blood | L equivalent gas | `VenousBloodCompartment.agent_amount_l` |
| $`M_i`$ | Agent stored in tissue group $`i`$ | L equivalent gas | `TissueGroup.agent_amount_l` |

Two conventions govern the Code column. First, some parameters are copied
into more than one compartment. For such a parameter, the cell names its
definition in `core/parameters.py` rather than one of the copies. For example,
$`\lambda_{b:g}`$ is an agent parameter, and `VenousBloodCompartment` and
every `TissueGroup` keep a copy of it. Second, a symbol may be defined by the
model but have no expression of its own in the implementation. For such a
symbol, the cell is an em dash and says what the code reads in its place.
$`F_a`$ is the only such symbol.

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

Arterial blood is flow-limited (see § "Model boundary"). It has no capacity
or amount balance of its own. Instead, $`F_a \equiv F_A`$ at every instant.

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
The coefficient the data files store is the tissue:gas one.

Either way, the same relationship may be written:

$$
M_i = C_iF_i
$$

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
- an agent tissue:blood partition coefficient $`\lambda_{i:b}`$, which is
  derived from the tissue:gas coefficient;
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
vaporizer actually adds. Mixed circuit gas leaves at that same total
volumetric rate. $`\dot V_F`$ is therefore the whole gas stream delivered to
the circuit, which is the carrier gas plus that added vapour. The balance
does not close if $`\dot V_F`$ is read as the carrier gas alone. This
paragraph settles what the symbol means. It changes no equation.

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
accepts that value as desflurane's `max_delivered_concentration_percent`. At
18% the two flows differ by 22%. Gas from flowmeters set to 2 L/min then
leaves the common gas outlet at about 2.44 L/min. Suppose a reader takes the
interface's fresh-gas-flow control for a flowmeter setting. That reader is
then wrong by the same factor in the circuit time constant $`V_C/\dot V_F`$,
which is the quantity the wash-in curve is about. The interface therefore
labels that control "Fresh gas flow", with the gloss "common gas outlet" on
the line below it. The alveolar readout uses the same two-line form for
"end-tidal-equivalent", for the same reason. The unqualified name is the one
on a real flowmeter bank, and the label must not be shortened back to that
name to fit a layout (`PL-71CF`).
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- derived: 22 percent from data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- derived: 2.44 L/min from data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- not-restated: 2 % -->

**$`V_C`$ is the assembled breathing system, never a manufacturer's apparatus
figure.** The model has one well-mixed gas compartment in front of the
patient, so the corrugated limbs and the Y-piece can only be inside $`V_C`$.
The machine profile's `circuit_volume_l`, which supplies $`V_C`$, is therefore the
assembled total of the apparatus plus the patient circuit (`PL-TBMX`). The
*apparatus* is the workstation's internal volume, including its absorber and
excluding the breathing circuit. Every volume that `docs/machine-survey.md`
§ "(a1) Apparatus gas volume" found is stated that way (Shin et al. cite
Dräger's instructions for use for theirs). The *patient circuit* is the
disposable limbs and Y-piece fitted for the case. A profile author who has an
apparatus figure therefore adds a patient-circuit volume before storing it.
That volume is 1.2 L, the internal volume of the Hudson RCI circuit that Shin
et al. added to each machine's figure. The exception is a profile that
assumes a circuit whose own volume is stated (*BMC Anesthesiol*
2017;17(1):10, PMID 28103806; read at full text 2026-10-04 from PubMed
Central, PMC5248460). Shin et al.'s sums leave out the circuit's 3 L
reservoir bag, so a total built from them leaves it out too (project owner,
2026-10-04, ratified, over counting the bag in the total or leaving the point
open). If the apparatus figure is stored alone, $`\tau_C`$ is shortened by the
circuit's share. A Perseus A500's 2.1 L gives 31.5 s at 4.0 L/min, where its
assembled 3.3 L gives 49.5 s, so the first value is 36% short. No check can
catch that error. Both are correctly cited volumes, and
`tools/doc_check.py`'s `check_provenance` asks only that a stored number has a
row in this document. This rule applies until the split described in
`docs/machine-abstraction.md` gives the machine an `apparatus_volume_l` and
gives the run its patient circuit. The shipped 6.0 L is such a total, and no
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
Springer; 2008:451–470; read at full text 2026-09-19 from the project owner's
private reference corpus, with `docs/machine-survey.md` § "Sources" holding
the bibliographic record, the route and the depth).

**Neither is modeled here, and the reason is not the exhaust term.** The
circuit equation is the part that still applies with a shut valve. Gas that
the patient's uptake pulls out of the circuit leaves at $`F_I`$, exactly as
spilled gas does. So $`\dot V_F(F_D-F_I)`$ is the same balance either way, and
$`F_I`$ is not what changes. Two other things change.

- **Where that agent goes.** "Circuit exhaust" counts the whole of
  $`\dot V_FF_I`$ as leaving the system. With the valve shut, that agent is
  carried into the alveolus and retained instead. That requires the inspired
  make-up term that "Alveolar gas" writes as
  $`\dot V_A + \sum_k \dot M_{\mathrm{uptake},k}`$, and this model does not
  include that term.
- **What sets the flow.** A closed circuit's fresh gas flow *is* the
  patient's total uptake, so $`\dot V_F`$ stops being a free input and
  becomes an output. This model computes no part of that sum. It does not
  track oxygen, which is the largest of the three streams. Its fixed alveolar
  volume also declares that the agent it does compute removes no volume at
  all.

So closed-circuit operation is blocked twice over. It is **not** a fourth
member of the three "Known limitations" entries that the fixed alveolar
volume blocks by itself. Lifting that constraint is necessary here but not
sufficient. An oxygen-consuming patient is the other half, and this model has
no such patient.

**This is recorded to warn against an implementation that sets the removal
rate to zero and leaves the rest alone.** Such an implementation integrates,
and it produces a plausible trajectory. The circuit settles at
$`F_I = F_A + \dot V_FF_D/\dot V_A`$. Take the shipped 4.0 L/min fresh gas
flow, the reference adult's 4 L/min alveolar ventilation and a 2% dial. The
circuit then settles two percentage points above alveolar. In the steady
state, every litre of delivered agent reaches the patient, which is what a
closed circuit does. But the result is not a closed circuit, because the
fresh gas still arrives at a flow that nobody has tied to uptake. At
4.0 L/min, for the same dial, the vaporizer adds agent about thirteen times
faster than it would at the 0.3 L/min that this patient's uptake would set.
A conditional coefficient is the wrong shape for this machine property.
`docs/machine-abstraction.md` names the slot that such a mode would occupy: a
`closed_circuit` removal strategy, recorded there as not implemented.
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- not-restated: 2 % -->

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

That quantity is not the time constant of the coupled system. It is recorded
here as a limitation of any description of alveolar kinetics by a single
mechanism. It is not exposed as a derived output, because two things separate
it from what a run exhibits. First, blood uptake is a second exchange term that
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

The pulmonary uptake rate is:

$$
\dot M_{\mathrm{pulmonary}} = Q\lambda_{b:g}(F_A-F_v)
$$

A positive value represents net uptake from alveolar gas into blood. A negative value represents net return from blood to alveolar gas during washout.

**The alveolar volume is held constant, and that is what excludes nitrous
oxide** (`PL-L2F2`). The substitution $`M_A = V_AF_A`$ above treats $`V_A`$ as
a constant and divides through by it. `core/governing_equations.py` implements
exactly that. The alveolar row of `build_system_matrix` divides each of its
terms by `alveolar_volume_l`, and the equation settings keep that volume fixed
for the whole step. Ventilation carries the same volume in and out. No term
adds inspired gas to replace the agent that blood takes up. For the agents this
model ships, that treatment is correct rather than merely convenient. For
nitrous oxide it is not. The difference is arithmetic rather than a matter of
degree.

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
"Source hierarchy". Do not read anything in this section as a nitrous oxide
parameter set.

**One constraint, not three omissions.** "Known limitations" lists three
separate absent features: nitrous oxide, simultaneous gases, and concentration
or second-gas effects. They are one feature. The fixed alveolar volume blocks
all three, and lifting that constraint unblocks all three. Two standard
formulations lift it. They are equivalent to first order, and a milestone that
scopes multi-gas support could adopt either one. The first makes $`V_A`$ a
state variable, and the concentration equation gains a volume term:

$$
\frac{dV_A}{dt} = \dot V_{A,\mathrm{in}} - \dot V_{A,\mathrm{out}} - \sum_k \dot M_{\mathrm{uptake},k}
\qquad
\frac{dF_A}{dt} = \frac{dM_A/dt - F_A\,dV_A/dt}{V_A}
$$

The second keeps $`V_A`$ constant and replaces the volume lost to total uptake
with inspired gas. The effective inspired ventilation then becomes
$`\dot V_A + \sum_k \dot M_{\mathrm{uptake},k}`$. The second formulation is the
less invasive change here, and it is the form the classical treatment uses.

Either way, the second-gas effect follows from the alveolus containing more
than one gas. It needs no machinery of its own. That is why `ROADMAP.md`'s
planned items 6 and 7 are not additive over these equations. Item 7 is nearly
free if item 6 is built this way. Item 7 is unreachable if nitrous oxide is
bolted on beside a volatile agent. Item 6 already instructs that the patient be
modeled as a set of substances rather than as the bolt-on. The
alveolar-volume coupling is the mechanism behind that instruction. The roadmap
states the instruction as a conclusion without giving the reason.

### Arterial blood

Arterial blood is flow-limited. Blood leaving the lungs equilibrates
instantaneously with alveolar gas, so $`F_a \equiv F_A`$ at every instant (see
§ "Model boundary"). There is no separate arterial amount balance, capacity, or
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

Arterial blood contributes no separate term, because it is flow-limited and
contains no independent amount of agent (see § "Model boundary").

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

Two bounds apply, and each one addresses a different question.

**The run-time halt thresholds, as implemented in `core/agent_simulation_validation.py`:**

```text
AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L = 1e-12
AGENT_ACCOUNTING_RELATIVE_TOLERANCE = 1e-9
MINIMUM_RELATIVE_SCALE_L = 1e-15
```

These names are spelled exactly as the module spells them, so each one
resolves to the constant that it quotes. The absolute bound and the minimum
scale carry their unit in the name. The relative bound is dimensionless. A
step passes if either tolerance is satisfied. The relative error uses
`max(initial + delivered, MINIMUM_RELATIVE_SCALE_L)` as its denominator. This
avoids division by zero when no agent has yet been delivered. A step that
exceeds both tolerances stops the run. These thresholds mark the point past
which the model refuses to show a number. They are not the standard that the
shipped model is held to.

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

Clipping a negative stored amount to zero does not repair mass balance. It
must not be used to conceal an unstable update.

## Numerical method

The model is advanced in explicit simulation time, with the settings held
constant over each step (piecewise-constant settings).

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

Requirements 2 and 3 are properties of the system matrix, not of a sequence of
operations. The method in "Selected method (as implemented)" advances the
whole system in one step. So there is no order in which transfers are applied,
and nothing is held fixed while another value moves. Requirement 2 is
satisfied because every rate reads the same state vector. Requirement 3 is
satisfied because each internal exchange appears as a pair of off-diagonal
entries whose contributions to the total stored amount cancel. That
cancellation is a structural property of the matrix, and
`tests/unit/test_governing_equations.py` checks it as such. It is not an
invariant maintained by applying paired deltas. Requirement 4 is why delivered
and exhausted agent are also states of that system.

A step is all-or-nothing. The step writes each compartment in turn, and a
guard can reject a value after earlier compartments have already been
written. So a step that cannot be completed must leave every dynamic value
exactly as it was before the step. § "Step atomicity" below explains why, and
what state a caller is left with.

### Step atomicity

A partially applied step is not a solution of the model at any time. It leaves
some compartments at $`t+\Delta t`$ and others at $`t`$. No instant of the
model ever produced that set of numbers. In the interface, it cannot be told
apart from numbers that the model did produce. The project prefers an obvious
failure to a plausible-looking number, so a failed step must be undone, not
annotated.

`AgentUptakeSystem.advance()` captures every dynamic value before the step
and restores it on any failure. Afterwards, the model holds the last completed
step. That is a real solution at a real simulation time, which the interface
may display and a reader may reason about. A reader would otherwise have to
infer the diagnosis from those numbers. Instead, the message of the raised
`SimulationNumericalError` carries it: the message names the invariant that
failed and the step size at which it failed.

The dynamic values are the eight that carry the trajectory, plus the
accounting period's initial amount. The eight are the circuit's inspired
fraction, the alveolar amount, each of the three tissue amounts, the venous
amount, and the cumulative delivered and exhausted amounts. Settings and
parameters are deliberately not captured. A rollback that restored cardiac
output would undo a change that the run had accepted. Each compartment
captures its own values. So if a dynamic field is added later without a
matching capture, the result is a local omission. It is not a partial restore
that looks complete.

Rolling back does not make the run resumable. The model reached a state that
it could not step from, so the same step would fail again. The caller must
stop either way. What the rollback decides is what the caller may *show*
while it is stopped.

Three constants are set to 0.1 s, and each of them states a different kind of
thing:
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

```text
MAXIMUM_SIMULATION_STEP_S  = 0.1                   # core/simulation_step.py
SIMULATION_STEP_S          = SimulationStep(0.1)   # app/dashboard_frame.py
SIMULATION_TICK_INTERVAL_S = 0.1                   # app/dashboard_frame.py
```

`MAXIMUM_SIMULATION_STEP_S` is the top of the model's supported domain, and
`MINIMUM_SIMULATION_STEP_S`, 1 ms, is the bottom. Both endpoints are included,
so any step from 1 ms to 0.1 s is supported. A `SimulationStep` cannot be
built outside that range. Both `AgentUptakeSystem.advance()` and
`SimulationState.advance()` accept only a `SimulationStep`.
`SIMULATION_STEP_S` is the step that the interface takes, and it is set at
that upper limit deliberately. § "Supported simulation step" below states what
the bound tolerates and explains why the two values are equal. Neither value
is derived from the other. Their equality is a fact about this configuration,
not an identity, and that is why they have separate names.
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

`SIMULATION_TICK_INTERVAL_S` is not a step at all. It is how often the run
loop wakes, in *real* seconds. It equals the step only because, here,
real-time playback means a tick that takes one step. The two have separate
names because the playback rate is the ratio between them: a tick takes
`multiplier × tick interval ÷ step` whole steps. Writing that out makes
"60× real time" a claim that a test can check, rather than a label beside a
loop. Without it, someone could re-tune the wakeup for a different host
without re-deriving the rates. Every rate on screen would then be false, and
nothing would fail.

### Selected method (as implemented)

Each simulation step is advanced by **one exact propagation of the whole
coupled system**. Every setting is held constant during a step. So within that
step, the six modelled fractions obey a linear, time-invariant system
$`dy/dt = Ay + b`$. The constant $`b`$ is carried against a ninth state whose
value is always 1, which turns the system into $`dy/dt = Ay`$, and

$$
y(t+\Delta t) = \exp(A\,\Delta t)\,y(t)
$$

is then its exact solution, with no truncation error at any step size.

`core/governing_equations.py` assembles $`A`$. Every entry of $`A`$ is one
term of one balance equation in § "Governing equations" above, written in the
order in which this document states them. `core/matrix_exponential.py`
computes $`\exp(A\Delta t)`$ and contains no physiology. Neither module adds a
dependency. The exponential uses scaling and squaring with a truncated Taylor
series, in about sixty lines of arithmetic on plain lists. Its module
docstring gives the method's provenance and the derivation of its constants.

Two of the nine states are not fractions. They accumulate the agent that
crosses the system boundary, at the rates given in "External delivery" and
"Circuit exhaust": $`\dot M_{\mathrm{delivered}} = \dot V_FF_D`$ and
$`\dot M_{\mathrm{exhausted}} = \dot V_FF_I`$. Delivered agent has a closed
form of its own. Exhausted agent does not, because it is
$`\dot V_F\int F_I\,dt`$ along a coupled trajectory. Carried as a state, it is
integrated by the same propagator over the same trajectory. That is what
requirement 4 of § "Numerical method" above asks for.

**The residual that this method leaves is rounding, and in absolute terms it
is larger than the split's residual was.** Measured on 2026-09-06 over a
3600 s run at 1 MAC, the worst residual at any step is 1.0e-12 L for
sevoflurane, 2.4e-12 L for isoflurane and 1.3e-11 L for desflurane. The
relative error is at most 9.2e-13 in every case. The split kept the absolute
residual at about 2e-15 L because it moved agent between compartments as
amounts, so its equal-and-opposite pairs cancelled to the last bit. Here,
conservation is a property of the matrix, and the arithmetic is done in
fractions. So the pairs cancel only to floating-point precision *relative
to the largest quantity in play*. Over an hour at desflurane's dial setting,
that quantity is about 43 L of delivered agent. That is where the four orders
of magnitude come from.

None of this is a loss of accuracy. The relative residual is three orders of
magnitude less than the check's own relative tolerance. The absolute figures
scale with how much agent the run has handled, not with any error in the run.
It does mean that `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L` (1e-12 L) is now
routinely exceeded on a long run, and that the relative branch alone is doing
the check. Measured on 2026-09-06, the absolute tolerance was first exceeded
at t = 3452 s at the reference runs' own settings. It was first exceeded at
t = 538 s at the sevoflurane corner of the envelope.

That result decides the shape of the guard (`PL-4GN8`). The disjunction in
`check_agent_accounting` is right. The absolute branch catches a gross error
early in a run, when little agent has been delivered and the relative
denominator is small. The relative branch does the check from then on. What
was wrong was the *release gate*. The reference runs asserted the absolute
residual. So what they certified depended on the dial setting they happened to
use, and it was simply false past about an hour of simulated time. They now
assert `MASS_BALANCE_RELATIVE_GATE`, above.

**What this replaces, and why the decision changed.** Until v0.4.x, each step
was the exact analytic solution of five *pairwise* exchanges, applied in
sequence. The five were: fresh gas into the circuit; circuit and alveoli
against each other; each tissue against a held arterial fraction; venous blood
against the flow-weighted tissue outflow; and the net patient uptake applied
back to alveolar gas. Each exchange was solved exactly while the other flows
were held constant. That made the sequence a first-order (Lie/Godunov)
operator split. Its error was $`O(\Delta t)`$ against the true simultaneous
solution, even though every sub-step was itself exact.

**The split was kept once, on accuracy, and that decision was right on its own
terms** (project owner, 2026-08-30). Both methods were measured against the
same from-scratch RK4 oracle at 5% delivered, over 60 s and 3600 s. The
exponential's worst disagreement across all six states was
$`1.3\times10^{-16}`$ to $`4.8\times10^{-14}`$. The split's was
$`5.2\times10^{-6}`$ to $`1.7\times10^{-5}`$. But the split's error was
bounded rather than unknown. So an exact step would have bought a tighter
number, not the correction of a wrong one, and no work planned at that date
needed it. Queue item PL-6GS0 holds those measurements. They were produced by
the v0.2.0 architecture review's verification harness, which was retired
under PL-STNV.
<!-- not-restated: 5 % -->

**It was superseded on 2026-09-03** (project owner), for a reason that the
original decision did not weigh. The reason was not accuracy but whether the
code can be read as the model. `ROADMAP.md` planned-milestone item 29 sets
this bar: a reviewer who knows the standard variables and equations should be
able to follow `core/` and recognize them without a lookup table. The split
could not meet that bar. Three of its five sequential sub-steps belonged to
the splitting scheme rather than to the physiology. The alveolar balance's two
terms were computed in different sub-steps, with a third sub-step between
them. And the split never formed the pulmonary uptake rate specified under
§ "Alveolar gas" above. Assembling the system matrix, by contrast, *is*
transcribing the governing equations. The alveolar balance is one row, and its
two terms are two entries in that row. Accuracy was not the motivation, and it
was not a cost either.

**Two consequences worth stating rather than leaving to be inferred.**

First, **the fractions cannot leave their physical range**. Every off-diagonal
entry of $`A`$ is a transfer rate, so it is nonnegative. That makes $`A`$ a
Metzler matrix and $`\exp(A\Delta t)`$ an entrywise nonnegative matrix.
`core/matrix_exponential.py` shifts the matrix before summing its series, so
that this property holds in floating point and not only in exact arithmetic.
A step therefore cannot drive a compartment negative at any step size. This
follows from the construction, not from the shipped parameters. So no patient
file or agent can trigger the compartment capacity guard through the model.
The guard and the rollback remain as protection for a model extension
whose matrix is not a pure transfer system.

Second, **refining the step no longer changes the answer**. Under the split,
halving $`\Delta t`$ halved the error. The step-refinement gate
(`test_step_refinement_converges`) asserted that each successive halving moved
the solution less than the one before. Every supported step now lands on the
same solution to within floating-point rounding. So that gate now asserts the
stronger property instead: that the step size does not affect the answer. The
gate cannot tell whether the answer is *right*, because a wrong transfer rate
is equally independent of the step. The mass-balance gate cannot tell either,
because every internal transfer is an equal-and-opposite pair.
§ "Independent-solution test" below is the gate that checks correctness. It
compares all six states against a from-scratch integration of the equations
above.

#### Supported simulation step

`MAXIMUM_SIMULATION_STEP_S` is the largest step at which a run may be taken,
and `MINIMUM_SIMULATION_STEP_S` is the smallest. Both are declared in
`core/simulation_step.py`. A step outside the two cannot be built.
`SimulationStep` rejects it with a `SimulationConfigurationError` when it is
constructed. So nothing is miscalculated, and a caller can retry with a step
inside the range while the run it already has stays intact. Every function
that takes a run's step takes a `SimulationStep`. So the step is checked once,
where it is chosen, rather than at each entry point that a fix had covered
(`PL-0GJC`). Some callers are not checked by `mypy`. For those callers,
`SimulationState`, `AgentUptakeSystem.advance()` and
`PlaybackRate.steps_per_tick` reject anything else with a `TypeError`. The two
bounds are different kinds of statement. The ceiling is a declared tolerance on
control timing, and it is argued first below. The floor, meaning the smallest
step, is numerical, and it is argued after the ceiling.

**What the ceiling now means, and what it no longer rests on.** Until v0.4.x
the ceiling was an *applicability domain*. The method was first order, so its
error grew with the step. 0.1 s was the largest step at which every claim that
"Displayed precision" makes about the last displayed digit was still true. That
derivation is void. The exact step has no truncation error at any step size.
Its propagator keeps every fraction in range at any step size. So accuracy no
longer sets a largest step.
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->

What a longer step still costs is **control resolution**. Settings are held
constant across a step. So the step is the interval over which a change to a
control is invisible to the model. At 0.1 s, a slider move is resolved to a
tenth of a second. At 10 s, a change made and reversed inside one step never
happened at all.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**Re-derived 2026-09-06 (`PL-X9KD`), and the honest result is that this is a
declared tolerance rather than a derived limit.** The search for a limit was
run first, and it found none. The step was swept from $`10^{-3}`$ s to
$`10^{300}`$ s across the settings envelope. Over that sweep, the disagreement
with an independent solution stays between about $`10^{-14}`$ and
$`2\times10^{-12}`$ in fraction. The disagreement does not grow with the step.
Instead it is U-shaped in the step, with a minimum around 1 to 60 s. The reason
is that the only error mechanism left is rounding. Rounding accumulates once
per *step*, so a finer step is slightly worse. The propagator was entrywise
nonnegative exactly at every one of 4374 (settings, step) combinations tested.
So no fraction that a step computes is rejected for stepping coarsely.
`advance()` raises nothing until about $`10^{18}`$ s. The first step at which a
displayed digit is wrong by a whole count is around $`10^{13}`$ s. There is no
numerical ceiling that a caller can reach.

Control resolution does not supply a threshold either, and this point decides
the shape of the constant. A control change takes effect at the next step
boundary. So the change is displaced later by up to one whole step, and that
displacement is **exactly proportional to the step**. This was measured over
three manoeuvres and all three agents. Halving the step halves the
displacement, and there is no knee anywhere. So no step size is the one at
which control timing becomes invisible. The constant can honestly be only a
declared tolerance. What it owes a reader is the measurement of what it
tolerates.

**The tolerance, in percentage points of one atmosphere.** These figures are
absolute concentrations. They are deliberately not counts of the readout's
last digit. The readout's decimal count is a presentation decision
(§ "Displayed precision"), and it must not feed back into the model. The table
gives the worst displacement over all three agents at the shipped 0.1 s step,
caused by a control change that lands one step late:
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

| Manoeuvre | Worst displacement | Binding agent |
| --- | --- | --- |
| Case opening: dial off to 1 MAC, reference flows | 6.7×10⁻³ pp | desflurane |
| Unperfused load, then perfusion on and dial off | 5.0×10⁻² pp | desflurane |
| Ventilator start at the envelope corner | 1.4×10⁻¹ pp | desflurane |

The criterion these figures are judged against is the model's own parameter
uncertainty. That uncertainty is upstream of both the step and the display. One standard
deviation of a single measured partition coefficient displaces a displayed
compartment by $`9\times10^{-4}`$ to $`6.8\times10^{-2}`$ pp (Yasuda et al.
1989, with the measurement in § "Displayed precision"). So at 0.1 s, an
ordinary control action is timed to about a tenth of one parameter SD. That is
the sense in which the step is fine enough.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**A test enforces both control-resolution tables**, and that is not a
formality. Since `PL-X9KD` retired the accuracy derivation, these figures are
the whole content of `MAXIMUM_SIMULATION_STEP_S`. Until `PL-ZVS7`, they were
asserted by prose here and in `core/uptake_system.py`, and by nothing else.
`tests/reference/test_control_resolution.py` re-measures every one of them from
the parameter files on each run. It drives each manoeuvre twice, once on time
and once one grid step late. It takes the worst difference over all six
displayed compartments. Suppose something changes the governing equations, a
partition coefficient, the reference adult's volumes, the supported input
envelope, or the step itself. That change moves the test's result before it
can change what this section tells a reader. The same test pins the step at
which the figures were measured, because the table and the constant are one
decision.

**What 0.1 s does not buy, stated rather than left to be discovered.** An
abrupt manoeuvre is not kept within that criterion. At this step, a ventilator
start displaces the alveolar reading by up to $`1.4\times10^{-1}`$ pp, which is
about twice one parameter SD. The displacement lasts for the duration of the
transient that the ventilator start causes. Keeping it within one SD would need
a step near 0.05 s.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**Put to the project owner as a trade-off rather than a correction, and
decided on 2026-09-06: the step stays at 0.1 s and that timing is accepted**
(`PL-NBCJ`). Three things decided it. First, halving the step doubles the
propagations per simulated second. It also changes the interface's tick
structure, because `SIMULATION_TICK_INTERVAL_S` is assigned from the step and
the playback rates are derived from their ratio. Second, the benefit is
confined to 1× playback. Above 1×, the control grid described below is
`multiplier × 0.1` s wide and dominates the step outright. So a reader at 60×
would see no change at all. Third, frames are two grid steps apart even at 1×.
So a 0.05 s step would resolve control timing to half of what the display can
show.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

So the following is accepted, and it is stated here rather than left for a
reader to infer from a value. At the shipped step, an abrupt ventilation change
is timed to about twice one parameter SD. That is the one case where the step
contributes more error than the parameters do. The error is small in absolute
terms: 1.4×10⁻¹ pp against a 1 MAC of 6.0% for desflurane. It is disclosed
rather than removed. A reader comparing an abrupt ventilation change against a
measurement should know that its *timing* is resolved to a tenth of a second
and no better.
<!-- provenance: data/agents/desflurane.json mac_percent = 6 -->

**Everything above is per step of delay, and the interface waits one step for a
control change only at 1× playback.** In other words, the table above is the
tolerance that this constant declares. It is not the resolution that the
application offers. The run loop advances a whole tick's worth of steps with
nothing between them. So simulated time stays still for one real tick interval
and then jumps by `multiplier × 0.1` s. A setting changed while the run is
playing therefore first acts at a tick boundary. The simulated instants that a
reader can reach are that far apart:

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
measurement that the table above reports. It was re-run at each rate over the
same three manoeuvres and all three agents (2026-09-06, `PL-NBWP`). The
"second worst" column is the next manoeuvre down at that rate. The margin is
their ratio. It is computed from the measurements rather than from the rounded
columns beside it (2026-09-13, `PL-WT07`).

**Read the worst column as a bound over the three manoeuvres rather than as a
property of one of them.** At every rate, the worst is the ventilator start
with desflurane. The second worst is the unperfused load then dial off. That
ordering is a measured fact and not a structural one. So it is re-checked on
every run by
`test_the_ventilator_start_binds_the_per_rate_table_at_every_rate`. The margin
column shows why it matters to state the bound this way round. The lead is
2.84× at 1× and 1.03× at 300×, which is three per cent. So at the coarsest
grid, the two manoeuvres are the same number to the two significant figures
that this table publishes. A parameter revision that reversed them would leave
the bound intact but make the attribution wrong. This phrasing is built to
survive that failure.

**They converge because they saturate at different rates.** The ventilator
start's transient has largely run its course by the time a 30 s grid step has
passed. So **its displacement saturates rather than scaling with the delay**.
If its 1× figure is extrapolated linearly, the 300× figure is over-stated by
about four times. The unperfused load's transient is still going at 30 s. So
its displacement is still nearly linear in the delay and keeps growing. Use
the measured values. Neither the figures nor the margin can be extrapolated.

**An ordinary dial change sits well below both, and is a third manoeuvre rather
than the runner-up.** The case opening is about 21× milder than the bound at
1×. The ratio narrows to 19× at 20×, 16× at 60× and about 7× at 300×, where the
case opening reaches 1.5 pp. That is the comparison to use when sizing what a
learner's own actions cost. It is not the comparison that says how much room
the bound has. The tens of percentage points at 300× belong to abrupt
manoeuvres, and the nearest of those is the second-worst column above.

Three things follow, and the third is why the behaviour was left alone.

- **Nothing arrives late.** A recorded `ControlChange` carries
  `SimulationState.elapsed_s` at the moment of the call. The new setting acts
  over the step that begins there, at every rate. So the control timeline is
  exact to the step, and no displayed value is stale against it. The rate
  coarsens only which instants a reader can *choose*.
- **An exact route exists at every rate: pause, change, resume.** The run loop
  takes no steps while the run is paused. So a setting changed during the
  pause acts from the step on which the run resumes. This route is for timing
  a manoeuvre. The rate ladder is for watching one.
- **The grid is already finer than the display, by exactly two.** Frames are
  one render interval apart, which is two tick intervals. So at every rate, a
  reader sees the run at half the resolution at which they can act on it. The
  grid could be tightened by servicing control events inside the burst, or by
  waking the loop more often. Either way would resolve control timing that the
  display cannot show. What was wrong here was the documentation, and the
  documentation is what has been fixed.

The largest supported step and the shipped step are the same number, and the
interface runs at it.

**The floor.** `MINIMUM_SIMULATION_STEP_S` is 1 ms. It is the one bound on the
step that is numerical (`PL-YZ17`, 2026-10-03). Before that change, any
positive step at or below the ceiling was accepted. So the bottom of the domain
sat wherever the arithmetic happened to fail, not where anybody had looked. The
arithmetic failed at about $`4.8\times10^{-304}`$ s. At that step, the 86 400 s
run length divided by the step overflows. `SimulationState` then raised a bare
`OverflowError` from outside the simulator's own exceptions.
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

What a finer step costs is rounding. The sweep above already shows the start
of this cost in "a finer step is slightly worse". Each step adds the amount it
changed to what was already stored. The finer the step, the smaller that
change is beside the stored amount it is added to. So the same rounding is a
larger share of the change. The table below was measured over 10 000 steps
from 60 s into the default sevoflurane wash-in. It was compared against the
same span taken in 0.1 s steps or as one exact step. Each row gives the largest
relative error in the amount by which any of the alveolar, vessel-rich, muscle
and fat fractions changed:
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

Nothing raises at any of these steps. At $`10^{-14}`$ s, the change that those
steps compute is a third wrong, and a single step's change is nearly half
wrong. Each is still returned as an ordinary step. From about $`10^{-16}`$ s
down, a step changes nothing at all, and it still returns normally. The growth
has no knee. So, as with the ceiling, no step is the one at which the result
becomes wrong, and the floor is declared rather than derived.

**Where it is declared, and what enforces it.** 1 ms is the finest step at
which the solution has been shown to be the shipped one. It is the bottom of
the sweep that `PL-X9KD` took. A test beside the step-refinement gate
(§ "Step-refinement test") drives the model at that step and pins the constant
there. Nothing runs finer. Apart from the tests of the floor itself, the finest
step any test takes is 0.02304 s. The table is a dated measurement rather than
a gate, because the steps below its first row are outside the domain and no
test can take them. So lowering the floor is a new measurement rather than an
edit, and it starts with that test at the new floor.
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

**It also bounds the run's own arithmetic, which nothing did before.** At the
floor, the supported run length is 86 400 000 steps. A float represents every
whole count up to $`2^{53}\approx9.0\times10^{15}`$ exactly. Below about
$`9.6\times10^{-12}`$ s, a day is more steps than that. Then `elapsed_s` would
round the count before multiplying it by the step (§ "Simulated time is a count
of steps, not a running total").
<!-- derived: 86 400 000 steps from core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- derived: 86 400 000 steps from core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- derived: 9.6e-12 s from core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The floor also applies to a compartment stepped on its own, and the ceiling
does not** (`PL-WP52`, 2026-10-19). Only `AgentUptakeSystem.advance()` steps a
compartment at a run's step, and it takes a `SimulationStep`. So no step below
the floor can get to a compartment through a run. But each compartment is
public, and rounding costs a compartment stepped alone the same as it costs
the run. The table below was measured over 10 000 steps. Each compartment was
held at a fraction of 0.01 and stepped toward 0.02. The compartments were a
tissue group with a time constant of 480 s, the venous pool at 7.8 s and the
breathing circuit at 60 s:

| Step | Largest error in what the three changed by, as a share of the change |
| --- | --- |
| 0.1 s | 2e-14 |
| 1 ms | 3e-13 |
| 1 µs | 3e-11 |
| 1e-10 s | 3e-5 |
| 1e-14 s | 4% for the pool and the circuit; the tissue did not change at all |

<!-- not-restated: 1 ms -->

<!-- not-restated: 0.1 s -->

So `TissueGroup.advance`, `VenousBloodCompartment.advance` and
`BreathingCircuit.advance_fresh_gas` each reject a step below the floor.
`BreathingCircuit.advance` calls `BreathingCircuit.advance_fresh_gas`. Each of
the three makes the check through `require_at_least_the_smallest_step` in
`core/simulation_step.py`. That is the same check, in the same words, that
`require_supported_simulation_step` makes for the run. A compartment still
takes a plain `float` rather than a `SimulationStep`. The reason is that the
ceiling is how long the run holds its settings, and a compartment stepped
alone at 1 s is correct.
<!-- not-restated: 1 s -->

A playback tick counts in the run's own step. So
`PlaybackRate.steps_per_tick` takes a `SimulationStep`, as the run does.
The chart's grid is deliberately not subject to the floor. `RunDefinition`
chains a column spacing at most once per column. So the rounding cannot
accumulate beyond what the columns asked for. A grid at a tenth of the floor
still lands on the run's own state to within 5e-14. Putting a floor under the
grid would reject narrow axes that the controller draws correctly today
(project owner, 2026-10-03, ratified, over flooring the grid's spacing as the
run's step is floored, `PL-6QYJ`).

The floor's value is the measurement above (project owner, 2026-10-03,
ratified, over refusing only a step whose run length overflows, and over a
floor at the 9.6e-12 s where a day's step count stops being exact,
`PL-YZ17`). It was the session's recommendation rather than the owner's own
specification, so ordinary evidence can reopen it.
<!-- derived: 9.6e-12 s from core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The measurements the old bound rested on are kept as history.** They
describe a method this project shipped for eleven releases, and a reader
comparing versions needs them. Take the worst trajectory that the four sliders
can produce, across all three agents. On it, the operator split's first-order
coefficient $`C`$ was at most $`2.29\times10^{-3}\ \mathrm{s^{-1}}`$. The
method's error was $`C\,\Delta t`$. So every figure that "Displayed precision"
quoted was that error at exactly $`\Delta t = 0.1\ \mathrm{s}`$, and doubling
the step doubled all of them. The method's compartment capacity guard first
fired at 12 s for isoflurane, 25 s for sevoflurane and 50 s for desflurane.
Those steps are two orders of magnitude above the bound, and they depend on
the agent by a factor of four. That is why the guard was never the domain
check. None of these figures describes what ships.
<!-- not-restated: 0.1 s -->

**The capacity guard remains, and it now reports a state the model cannot
enter.** Where a step drives an amount out of range,
`AgentUptakeSystem.advance()` reports `SimulationNumericalError`. The step is
rolled back in full, and simulation time does not advance. The caller must
stop the run, and the run stops at the last completed step rather than at a
partially applied one. Under the exact step, no parameter set triggers the
guard, because the system matrix is Metzler and its propagator is therefore
entrywise nonnegative (see § "Selected method (as implemented)"). The guard is cover for
a model extension whose matrix is not a pure transfer system. It is not cover
for a caller stepping too coarsely. The two failures are kept deliberately
distinct. `SimulationConfigurationError` says that the setting was rejected
and the run is still trustworthy. `SimulationNumericalError` says that a run
in progress is not trustworthy.

The implementation must not depend on:

- wall-clock elapsed time;
- interface frame rate;
- the interface toolkit;
- filesystem state;
- display size; or
- event-loop scheduling.

A run with identical initial state, settings, events, and simulation steps must produce identical results.

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
   of this tier. Both are already cited in this project's agent files.
2. **Secondary synthesis.** A review, textbook, monograph or consensus
   document that collects primary measurements without making one. It is
   legitimate for finding the primary source. It is also legitimate for
   recording what the field conventionally quotes. That is a real fact about
   what the reader expects, and it is the reason isoflurane's textbook 1.4 is
   worth naming. It is not the authority for a stored value on its own
   strength, because the rounding, and the choice between measurements that
   disagree, happened somewhere the reader cannot see. It can be adopted only
   on the recorded decision described below.
3. **Reference implementation.** Another simulator's parameter set: the
   numbers that some working program was built to run on. Gas Man is this
   project's reference implementation, which is why this document names it
   throughout. The tier is genuinely useful, and it is not a euphemism for
   worthless. It fixes the behavior of a widely taught teaching tool as
   something this implementation can be compared against. It also supplies a
   complete, internally consistent set, where the primary literature supplies
   scattered measurements made in different laboratories on different
   cohorts. **It is still not a source.** A parameter set is assembled to make
   a program behave. The program does not let anyone recover which
   measurement each individual number descends from, or what was adjusted to
   make the set cohere. **And the behavior it fixes has itself been measured
   against patients**, with an agreement materially worse during wash-in than
   during maintenance. § "Known limitations" carries the figures and says
   what they bound.

**A lower tier may be adopted, but never silently.** The ranking above says
which tier a reader may trust without examining it. It does not say that a
tier-2 or tier-3 number may never be stored. This project's provenance table
is mostly made of such numbers, and it says so a few paragraphs down. What the
ranking forbids is an adoption the reader cannot see. So a stored value whose
authority is not a primary measurement must carry three things, and every such
value carries all three today:

- **The tier, on the entry itself, with the values it covers.** The `tier`
  field in the data file records the tier, and `make check` checks it against
  the closed vocabulary. The entry's `authority_for` names the stored values
  that the entry is the authority for. Neither is a claim in prose that a
  reader has to reconstruct.
- **Why no tier-1 source was adopted.** This goes on the entry, or in the
  file's `provenance_gap` where the whole file is in that state.
- **The date and whose decision it was**, where a lower tier is adopted in
  preference to an available primary source rather than for want of one.
  `venous_pool_volume_l` is the worked example. Davis and Mapleson 1981 is
  tier 2, and it was adopted on the project owner's decision of 2026-09-07.
  It replaced a round 1.0 L that none of the sources then cited for it
  contained. When the Workbook's Appendix C was read on 2026-09-15, its
  defaults listing turned out to hold that 1.0 L, as `VEN=1.0`. That changes
  the history, not the stored value. The file's Workbook entry records it.

That is a higher bar than a tier-1 citation clears, not a lower one. It is
deliberately not a licence to prefer the convenient number. Two reasons are
admissible, and the fact that finding a primary source takes work is not one
of them:

1. **No primary measurement of *this quantity, in this population* exists or
   is reachable.** The whole reference patient is in this state. That
   includes the parameters that carry a primary citation beside them. Hudgel
   and Devadatta measured awake functional residual capacity, where the
   stored volume is an anaesthetised lung. Cattermole et al. measured a
   different population. Janssen et al. report a muscle mass, where this
   model stores a volume. Each note says which of these cases it is, and that
   is what makes the citation a comparison rather than a source.
2. **The value belongs to a set whose internal consistency is part of what is
   being modelled**, and replacing it would mean mixing the reachable
   primaries across laboratories and cohorts. This is tier 3's own argument
   above: a reference implementation supplies a complete, internally
   consistent set where the primary literature supplies scattered measurements
   made in different laboratories on different cohorts. The twelve partition
   coefficients are the worked example. Eger, Strum and Eger, Lerman et al.,
   and Esper et al. 2015 did measure these quantities in this population, so
   the first reason does not cover them. But a single laboratory's blood:gas
   figure dropped into a Gas Man tissue set makes the trajectory a hybrid of
   two parameter lineages. That is the same objection this document makes
   below against dividing a Gas Man trajectory by a Mapleson MAC, applied one
   level down.

The second reason is the narrower of the two, and it is not a way around the
first. It is available only where the entry cites the primaries with the
measured value and records the difference from the stored one. That keeps the
cost of the choice visible to the reader rather than argued away. Against the
measured blood:gas coefficients the differences are desflurane −0.9%,
sevoflurane −5.2% and isoflurane −11.0%, and the decision itself is dated
2026-09-03 (`PL-D6LX`). Against Esper et al. 2015, the largest of those
measurements and the most recent, the stored values are lower again:
desflurane −26.3%, sevoflurane −12.2% and isoflurane −10.3% (`PL-SWY5`).
`ROADMAP.md`'s planned-milestone item 31 is the route to a primary coefficient
set, which would retire this reason for these twelve.

Where a primary measurement *is* available and simply has not been adopted,
the entry says so in those words, and the value **carries no adopted
primary**. That is a statement about the `adopted` field rather than about the
citation. A stored value can name a source and declare its tier while no
measurement of that quantity supports it. That is the ordinary case here, and
it is the reason the field exists.

**Full texts held on hand are in `docs/references/`, and holding one changes
nothing about its tier.** The directory exists so that a session checking a
claim can read the source instead of recalling it. `docs/references/README.md`
gives the full citation for each text. Baker and Farmery's 2011
*Comprehensive Physiology* review of inert gas transport in blood and tissues
is the closest published statement of what this document specifies. For any
individual number in it, the review is a tier-2 synthesis.

**Republication does not promote a value between tiers.** A peer-reviewed
paper that prints a reference implementation's parameter table is a tier-3
citation wearing a journal's name. Both of this project's tier-3 citations are
of exactly that kind, and neither measured a coefficient. De Wolf et al. 2012
is a Gas Man simulation study, and its Table 1 is the parameter set it fed to
Gas Man. Weber et al. 2021 is a Gas Man simulation study that describes the
product's standard 70 kg patient. The two do not even agree on what that set
holds. Weber et al.'s Table 1 prints Gas Man 4.2's 1 MAC as 2.1% sevoflurane
and 1.1% isoflurane. De Wolf et al. state 2.0% and 1.2%, which are the values
stored on De Wolf's authority. Yet every partition coefficient the two print
is the same (`PL-0SG0`). Each agent file's De Wolf note carries the figures,
read on 2026-10-12 from PMC's XML record of PMC7943506. Citing either paper as
though the value had been measured is the specific failure this section exists
to prevent.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- not-restated: 70 kg -->

**Where this project stands, stated rather than implied.** Of the 37 rows in
the provenance table below, 16 are tier 3, one is tier 2, 18 are tier 1, and
two adopt no source of any tier. **Nine of the twelve partition coefficients,
which are every tissue:gas value, are Yasuda, Targ and Eger's human
measurements.** They were adopted on 2026-09-13 (`PL-FN5F`) after the stored
values were checked against that paper's Table 1. The other three, the
blood:gas coefficients, are the Gas Man set as published by De Wolf et al.,
and they remain tier 3. Ten of the eleven physiologic parameters in
`src/anesthesia_sim/data/patients/reference_adult.json` are the Gas Man default
patient. The three `mac_percent` values are the MAC values that De Wolf et al.
state they used in their Gas Man simulations. Two tier-2 sources are cited
alongside them but not adopted: Mapleson's 1996 meta-analysis and the
age-related iso-MAC charts built on it. The two unadopted rows are the machine
parameters in `src/anesthesia_sim/data/machines/reference_circle_system.json`.
One is a circuit volume that departs deliberately from the published Gas Man
figure. The other is a default fresh gas flow with no published counterpart at
all.

That count moved on 2026-09-13, and the *values* did not. Nine rows crossed
from tier 3 to tier 1 because the project read the paper Gas Man had always
named and found the stored numbers in it. Nothing was recalculated. That
distinction is the whole point of separating `tier` from `adopted`: what
changed was the record of where a number came from.

**The nineteen exceptions are of four kinds**, and naming them is the point of
the counts above. The largest group is the nine tissue:gas partition
coefficients, three per agent, adopted from Yasuda, Targ and Eger 1989 on
2026-09-13. They are human autopsy measurements at 37 °C. The paragraph below
the table on Gas Man's attribution says how they were checked, and why the
published figures were *not* substituted for the stored ones. The eleventh
reference-patient parameter, `venous_pool_volume_l`, is Davis and Mapleson
1981. It is tier 2, adopted on 2026-09-07 on the project owner's decision
(`PL-8ZJQ`), and it is the only tier-2 source adopted anywhere in this
project. The three vaporizer maxima are each the calibrated maximum of a
device rather than a physiologic quantity. Each cites a primary source for it:
the Dräger Vapor 2000 specification for sevoflurane, and published
vaporizer-performance measurements for isoflurane (Kelly and Kong 2011) and
desflurane (Johnston et al. 1994, on the Tec 6). Finally, the six MAC-awake
rows, a fraction and a standard deviation for each agent, are adopted primary
measurements: Katoh et al. 1993 for sevoflurane and isoflurane, and Chortkoff
et al. 1995 for desflurane.

**Recompute these with `python3 tools/source_tier_counts.py`. Do not adjust
them as rows arrive.** The command prints the counts from each `sources`
entry's `authority_for`, file by file and in total, and it names the source
behind every row.

The pair of counts that stood here until 2026-09-13 was 29 rows, with 26 of
them tier 3. That pair was true when it was written. It survived two changes
that made neither count true. The six MAC-awake rows were added, and `PL-8ZJQ` moved
`venous_pool_volume_l` off tier 3 (`PL-7KDC`). Nothing computed reads these
counts, which is why they could go stale silently. `check_provenance` decides
whether a documented key holds the stated value, never what tier its source
carries. Until 2026-09-30 nothing recorded which source a row rested on at
all. Only each entry's note said so, in prose, so no command could have
computed these counts. `PL-9LXK` added the record and the command.

The command prints the counts but never checks this paragraph. That was the
project owner's decision of 2026-09-13. Whether a changed count still fits the
sentence around it remains the author's responsibility.

`mac_percent` is the one of these values that a reader now divides by. It is
the divisor of the second display unit, so its tier governs a displayed
clinical value rather than only a starting dial position. "Delivery-limit and
MAC parameters" states what that costs, and "Known limitations" records it.

Every `sources` entry in every data file names its tier. The three agent files
cite the primary measurements alongside their tier-3 values. They cite Strum
and Eger for sevoflurane, Eger for desflurane, Lerman et al. 1984 for
isoflurane, Esper et al. 2015 for all three, and Yasuda et al. for tissue
solubility. Each entry records the measured value, the fact that it was **not
adopted**, and how much the stored number differs from it. Against the older
blood:gas measurements the stored values are sevoflurane −5.2%, isoflurane
−11.0% and desflurane −0.9%, so isoflurane is the widest gap. Esper et al.
2015 measured all three agents in 120 surgical patients at 37 °C, and against
its means the stored values are sevoflurane −12.2%, isoflurane −10.3% and
desflurane −26.3%. That makes desflurane the widest gap in the project, at
about 3.8 of Esper's SDs. The paper was read from its abstract only
(`PL-SWY5`). The Gas Man study that prints this parameter set says so in its
own footnote: its blood/gas coefficients
"differ from them observed by Esper et al." (Weber et al. 2021, Table 1).
§ "The early wash-in curve against the published figures" records what
Esper's desflurane value would do in this model. The decision to keep the Gas
Man value and label it, rather than move to the textbook 1.4 or to Lerman's
measured 1.46, was taken on 2026-09-03. The
route to primary values for all three agents is `ROADMAP.md`'s
planned-milestone item 31.

`src/anesthesia_sim/data/patients/reference_adult.json` still adopts no
primary source for any of its eleven parameters, and it records that in those
words. What changed on 2026-09-06 is that the file now says something specific
about each parameter rather than only about the set.

**Five carry a measurement cited alongside and explicitly not adopted**, in
the form the agent files use. That form gives the measured value, its
reference conditions, and how far the stored number sits from it. Hudgel and
Devadatta measured FRC by helium dilution in ten healthy men. Read with
Wahba's review of the roughly 20 percent reduction under general anaesthesia,
that measurement brackets the lung gas volume. Cattermole et al.'s 686
subjects in the 50–75 kg band give a median cardiac output of 5.51 L/min, and
the stored value is 9.3 percent below it. Janssen et al.'s whole-body MRI
gives a skeletal-muscle mass. Its apparent agreement with the stored muscle
volume is a coincidence, since that cohort of men averaged about 86 kg rather
than 70. Heinonen et al.'s PET measurement of resting adipose perfusion is
about half what the stored fat flow fraction implies. Frayn and Karpe's review
supplies the muscle comparison. It also supplies the reason the fat gap is a
question about the absolute level rather than the muscle-to-fat ratio, which
the stored fractions get right.

**Six have no comparison, and the file says why for each**, so that the
silence is not taken for an oversight. Two are not measurements at all. The
reference weight is a label that no equation reads. The venous pool is a
well-stirred mixing volume that sets a 12-second time constant. It is not the
physiologic venous blood volume, which is several times larger. One is a
derived convention. The remaining three are lumped-compartment aggregates: the
vessel-rich volume and flow fraction, and the fat volume. No single
measurement exists of the quantity this model means by any of them.

**No stored value changed, and none of this promotes anything.** A measurement
cited beside a tier-3 number does not source it. That is the second of the
three rules below, and these entries are written to be interpreted under that
rule. The gap between the stored fat perfusion and the measured one is the
largest of the five. It is recorded in "Known limitations" as well, because it
acts on the shape of a displayed curve rather than only on a number in a file.

**The lineage is Lowe and Ernst's, not Mapleson's, and this is now confirmed
from the source rather than inferred.** Until 2026-09-06 this file named
Mapleson's 1963, 1964 and 1973 papers as its primary lineage. It did so on the
strength of their titles, and nobody had opened them. `PL-6Q8N` removed that
framing. Later the same day the project owner supplied the Workbook's front
matter and appendices. Its Model Parameters table (Appendix B, page 168)
settles the question. The note beneath the table reads, in these words,
"Values for volume, flow and relative flow are taken from Lowe and Ernst,
1981". The book is *The Quantitative Practice of Anesthesia: Use of Closed
Circuit*, Williams & Wilkins. The Workbook attributes nothing to Mapleson.

That reading also corrected this file about its own contents. **The table
supplies seven of the eleven values, not all eleven.** The citation had been
pointing at the wrong section: page 183's "Patient default options", which
describes the interface controls and carries no numbers. Alveolar volume, the
three tissue volumes and the three flow fractions are in the table and equal
what is stored. Cardiac output is there only as the sum of the flow column.
Reference weight and alveolar ventilation are interface defaults for which the
supplied chapters state no number. **The venous pool's 1.0 L is not in the
table at all**: its `Blood` row reads 5.00 L. `PL-3YZW` carries that gap.
`PL-7HDS` carried the reading of Lowe and Ernst, which is the link that decides
whether this chain ends in a measurement or in another compilation. It ends in
neither, and the next four paragraphs report that reading.

**A second Workbook page, read 2026-09-15, carries three of those four.** The
whole Workbook reached the private corpus that day. Its Appendix C, "Gas Man
System Defaults", pages 171–72, prints the program's `GASMAN.INI` verbatim. Its
`[Volumes]` block gives `CKT=8.0`, `ALV=2.5`, `VRG=6.0`, `MUS=33.0`, `FAT=14.5`
and `VEN=1.0`. `[Ratio]` gives `76`, `18`, `6`. `[Defaults]` gives `VA=4` and
`CO=5`. So alveolar ventilation is stated as a number rather than described,
and cardiac output no longer rests on a column sum. The venous pool's 1.0 L is
in the document after all. Only `weight_kg` is in neither appendix. **Nothing
is promoted by any of it.** These are one program's defaults written down
twice, tier 3 both times, and the venous pool has since moved off Gas Man
entirely. What the page corrects is the record, below, of which page the
numbers were read from.

**Lowe and Ernst has now been read at the source, and the chain does not end
there.** On 2026-09-08 the project owner supplied pages 55–60 and 82–84 as an
interlibrary-loan scan. Two earlier readings at one remove had narrowed the
pages to 57 and 83. They were Lerou and Booij's system model (*Br J Anaesth*
2001;86:12–28) and Couto da Silva, Mapleson and Vickers' study of Lowe's method
(*Br J Anaesth* 1997;79:103–12). Both were supplied on 2026-09-06 and read here
at full text. This repository does not hold the scan, because it is
publisher-copyright material and the repository is public. The author's
initials are `HJ`, because the scan's own record prints the author as Lowe,
Harry J. The Workbook's `HF` is therefore a misprint. Interlibrary loan is a
third route. It is neither the one `.claude/rules/citing-sources.md` describes
nor the personal access by which the Workbook arrived, and `PL-XJ5P` still
carries that gap.

**Page 56 settles the tier question for the book, in one sentence.** Of
figure 4.1b, the table in which the volumes and flows are printed, it says:
"The figure models a 100-kg patient with normal physiologic organ volumes and
blood flows (9, 19, 20, 26)." The book collects those figures and cites them
onward to four references. Chapter 4's own narrative names three of them:
Mapleson, Smith et al. and Zwart et al. Lowe and Ernst is therefore **tier 2,
a secondary synthesis**. The Workbook's upstream source has an upstream source
of its own, and the only provenance chain the reference patient has still ends
in nobody's measurement. The answer could have gone the other way. The
hierarchy above admits a lower tier on a recorded decision, and a book that
had *measured* these volumes would have been adoptable without one.

**Those four references are now identified, and three of them are models.**
Chapter 4's reference list is on pages 64–65, which were supplied on
2026-09-10 as a second interlibrary-loan scan (`PL-8SDL`). Each reference was
checked against its PubMed record, and none was read beyond that record.
PubMed holds no abstract and no PubMed Central text for any of the three
papers, and the fourth is a monograph that PubMed does not index.

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
  not cover monographs. It is also unreachable from here: `www.icrp.org`,
  `journals.sagepub.com` and `doi.org` each returned nothing through the egress
  proxy on 2026-09-10.

References 9, 19 and 20 are **uptake-and-distribution models**, and that is
what this chain needed to know. A model consumes organ volumes and blood flows.
It does not measure them. So none of the three can be the place that figure
4.1b's figures came from. Reference 26 is the only one of the four that is not
an anesthetic model. It is cited to a single page, and that page is the one
that ends the chain.

**The chain terminates at tier 2, and never reaches tier 1.** Page 151 of the
ICRP report was supplied by the project owner on 2026-09-10 and read here
(`PL-LT51`). It carries **Table 8, "Organs of standard man — Mass and effective
radius of organs of the adult human body"**, tabulated for a total body of
70,000 g. A "standard man" is a reference specification agreed by a committee.
The document's own title is *Report of Committee II*. The table gives no
citation, sample count or dispersion for any row. Table 7, on the facing page
150, is different: each of its tissue rows carries a count in parentheses.
Under § "Source hierarchy" above, a consensus document that collects primary
measurements without making one is **tier 2**. So the longest provenance chain
behind the reference patient runs Gas Man (tier 3) → Lowe and Ernst (tier 2) →
ICRP Committee II (tier 2). **Nothing on that chain was measured by anybody
this file can name.**

**Table 8 has no blood flows**, and that is the more useful half of the
finding. It gives mass and effective radius, and nothing else. Yet Lowe and
Ernst cite all four references together for "organ volumes *and blood flows*".
So the perfusion fractions cannot come from reference 26 at all. The perfusion
fractions are the half that sets every time constant this model computes. They
must come from reference 9, 19 or 20, and all three of those are models.
Reading those three is now the more valuable request, not the less valuable
one.

**Four of Lowe's rows correspond to Table 8 closely enough to be an
inheritance.** The comparison is at 100 kg, where his kilogram column can be
treated as per cent of body weight: brain 2.1 against 2.1, kidney 0.4 against
0.43, heart 0.4 against 0.43, and muscle 42.6 against 43. Five rows do not
correspond: skin 10.0 against 8.7, adipose 15.0 against 14, blood 7.0 against
7.7, lung 0.8 against 1.4, and bone 12.0 against a skeleton of 10 without
marrow or 14.2 with marrow. **The liver is the outlier that matters: 5.7
against 2.4.**
<!-- not-restated: 2.1, 2.4 -->

**That gap has a candidate explanation, and it comes from this file's
arithmetic rather than from the book.** Liver 1,700 g plus gastrointestinal
tract 2,000 g plus spleen 150 g plus pancreas 70 g is 3,920 g. That is **5.60%
of 70 kg against Lowe's 5.7%**. This group of organs is the hepatoportal
compartment. An uptake model lumps it together because the splanchnic bed
drains through the liver. No other grouping of Table 8 comes as close. Neither
document says that this is what happened, and the match is no evidence against
either author.
<!-- not-restated: 70 kg -->

**Why it is recorded rather than left out.**
`tissue_groups.vessel_rich.volume_l` is stored as 6.0 L. Lowe has ten
compartments. The only grouping of them that reproduces both that volume and
the stored 0.76 perfusion fraction is kidney + heart + brain + liver, at 8.6%
of body weight. On ICRP's own rows those four organs are **5.36%, which is 3.75
L at 70 kg**. That is 38% below what is stored. So the stored value rests on a
lumping decision made one link up the chain, and that decision is now visible
where before it was not. **No stored value changes because of this, and none
should.** Lumping the splanchnic bed into the liver compartment is ordinary
modelling. § "Tissue compartments" above already treats the vessel-rich group
as one lumped tissue. And nothing here is sourced to ICRP.
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.volume_l = 6 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**References 19 and 20 have been read too, and they measured nothing either.**
Both were supplied by the project owner on 2026-09-10 and read in full text
(`PL-LT51`). They share one parameter set. Reference 20's Appendix says its
tables "are the same as used by N. Ty Smith in his article … where he gives the
rationals for our choice". So the provenance lies in reference 19. Of the table
this chain would need, reference 19 says that it "lists the **assumed** blood
volumes, tissue volumes, and partition coefficients". "Assumed" is the paper's
own word, and it gives no source for any of these values. Its *flows* are
compiled from "several sources, most of which can be found in a recent review".
That review is the authors' own handbook chapter. The awake cardiac output of
5,800 ml/min is taken from Milnor's chapter in *Medical Physiology*, 12th
edition. The compiled flows did not balance, and the authors made them balance.
Total cardiac output was 3,480 ml/min, against regional flows summing to 3,290
ml/min, and "the discrepancy was compensated for by adjusting the values for
skin and skeletal muscle flows". **A stated assumption is not a source, and an
adjusted sum is not a measurement.** So neither paper can be promoted, and
neither is a candidate for adoption.

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

**Reference 9 closes the chain, and it makes two of the four references one
document.** Mapleson 1963 was supplied and read on 2026-09-10 (`PL-LT51`). His
Appendix 1 opens: "*Tissue volumes and blood supplies.* With the following
exceptions the volumes in Table 1 are those for the 'standard man' of the
International Commission on Radiological Protection (I.C.R.P.) (23)…". His
reference 23 is that report at **page 151**, which is Lowe and Ernst's
reference 26. So Lowe and Ernst very likely took the ICRP citation from
Mapleson's own reference list. References 19 and 20 are Mapleson's Table 1,
lumped and relabelled. Lumped as Smith's own footnotes describe, Table 1
reproduces their table in **nine rows of nine**, and those nine rows sum to
58.04 litres against Mapleson's own 58.04.

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

**Then there is the negative finding, which is the one that matters.** Figure
4.1b's flow column cannot be reproduced from any of the four. On Mapleson's own
rows, kidney + heart + brain + liver is 3,820 of 6,480 ml/min, which is
**59.0%**. Every well-perfused organ together is **63.0%**. Lowe has **76%**,
and Smith and Zwart have 64.0%. Muscle plus skin nutritive is 10.2%, against
Lowe's 13%. Fat plus fatty marrow is 4.0%, against Lowe's 5%. **The perfusion
fractions this model runs on have no identified origin in any reference the
book names for them.** Reference 26 has no flows at all, and the other three do
not match. That is now established rather than outstanding. **It is a
statement about four documents that have been read, not about the world.** It
does not follow that no origin exists. The book prints more than one table, and
Gas Man may lump differently.
<!-- not-restated: 5 % -->

**Two of the three coincidences above are lineage after all, and one is not**
(`PL-ZD67`). The 2.5 L is Mapleson's functional residual capacity. It is a mean
of published human measurements, cited to Dittmer and Grebe's *Handbook of
Respiration*, and not a round number somebody chose. It is still not this
file's source. Mapleson's row is FRC plus half the tidal volume, whereas this
file stores an alveolar gas volume. The value also arrives here through Gas
Man, whose upstream source is Lowe and Ernst, and they lump the quantity away.
The 33 is Mapleson's muscle 30 plus skin nutritive 3, which is exactly how
Smith prints it. It is *not* this file's 33.0, because Lowe's muscle row is
29.8 L at 70 kg and reproduces the stored value under no grouping. Alveolar
ventilation of 4 l/min stays a coincidence, because Mapleson gives a formula,
not a figure.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

**Three of this file's stored values also appear in those tables.** The
paragraph after next settles where each one came from, rather than leaving it
as a resemblance. The three are alveolar ventilation of 4 l/min, a functional
residual capacity of 2.5 l in reference 20's table only, and a skeletal muscle
tissue volume of 33 litres. **No stored value changes because of any of it.**
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

Mapleson 1963 turns out to be one of the four, but that does not rehabilitate
the lineage that was removed. The removed claim was that Mapleson's papers were
the *Workbook's* primary source, on the strength of their titles. The Workbook
attributes nothing to Mapleson. This is a different document, which cites him
for a table it collected, two links further up the chain.

**The model patient is 100 kg, which is why the material arrives in this
project as fractions.** Page 56 picks that weight so that "the organ weights
can also be read as per cent of total body weight". So Lerou and Booij's Table
6 of fractions is the book's own table divided by 100, not a normalization they
performed. Nothing in the book states a 70 kg parameter set. Cardiac output is
allometric, and that too has now been read at the source rather than taken
from a report. Page 59 gives the cardiac output for its worked prime dose as
$`2M^{3/4}`$ dl/min, "or 63.25 dl" for the 100 kg patient. That is 0.2 times
body mass to the three-quarter power in L/min. It gives **4.84 L/min at 70
kg**, against the 5.0 stored here, which would need 73.1 kg. The book's own
worked value of 63.25 dl fixes the exponent independently of reading a
superscript off a scan. `PL-YKSM` decided on 2026-09-08 that the fixed 5.0
stays. § "Known limitations" below carries the reasoning.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**The relation itself is derived, not measured, and pages 17–19 say from
what.** Page 59 states $`2M^{3/4}`$ without citing anything, and until
2026-09-10 the trail stopped there. Chapter 2 builds the relation in three
steps. Neither of its two constants is a cardiac-output measurement:

- **Figure 2.2, page 17** plots oxygen consumption against body weight for
  mammals from 0.03 kg to 8,000 kg. The plot is linear on log–log axes, and the
  slope is given as "approximately 10 kg^(3/4)". The figure is reproduced by
  permission from *Brody, S. Bioenergetics and Growth. Reinhold, New York,
  1945*. It is an interspecies metabolic allometry, not a human study.
- **Page 17** takes the arteriovenous oxygen content difference as "about 5 ml
  of O₂/dl of blood", attributed to Guyton et al. (the chapter's reference 13).
  Guyton et al. are also credited with concluding that kg^(3/4) "is probably a
  better index of cardiac output than any other parameter, including surface
  area". Chapter 2's reference list is outside the pages supplied, so that
  citation is unresolved. `PL-LT51` carries it.
- **Figure 2.4, page 19** is the arithmetic. kg^(3/4) × 10 gives O₂ use in
  ml/min. O₂ use ÷ 5 gives cardiac output in dl/min, and the figure annotates
  that divisor as "(a–v)DO₂ = 5 ml/dl". The figure also draws the composed edge
  directly, kg^(3/4) × 2 → $`\dot{Q}`$ in dl/min, which is page 59's constant.

<!-- not-restated: 2.4 -->

So $`0.2M^{3/4}`$ is Brody's mammalian metabolic allometry divided by an
arteriovenous difference that is assumed constant across mammals. **4.84 L/min
at 70 kg is therefore a derived interspecies extrapolation and must not be
treated as a measured human cardiac output.** § "Known limitations" below is
where that matters, because it is the one place this document sets the figure
beside Cattermole et al.'s measured median. That section says so (`PL-DZQT`).
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
authority a compilation whose own four sources are unread. The reading gains
two things. The attribution has been checked against the document rather than
against a report of it. And the tier of the next link is now a known question
instead of an assumption.

**The venous pool now has a published counterpart, and it is not the stored
1.0 L.** Davis and Mapleson's paper (*Br J Anaesth* 1981;53:399–405) was
supplied by the project owner and read at the source on 2026-09-07. It
describes a standard man of 70 kg with a total blood volume of 5189 ml and a
cardiac output of 6480 ml/min. Page 400 states that **for models of inhaled
anaesthetics** the two venous pools may be combined, "in which case it would be
marginally more accurate to make the arterial pool 799 ml (15.4% of the total
blood volume) and the combined venous pool 1222 ml (23.6%)". That combined pool
is the same object as $`V_v`$ here: one well-stirred venous pool that carries
tissue return. Their Appendix derives it from the ICRP (1975) blood
distribution rather than measuring it, and that is what keeps it at tier 2.
**It was adopted on 2026-09-07, on the project owner's decision** (`PL-8ZJQ`).
It is the first value in this file to carry a source other than the Gas Man
Workbook. `venous_pool_volume_l` is 1.222 L. The key was renamed from
`venous_blood_volume_l` in the same edit (`PL-BD94`), because the old name
suggests the physiologic venous blood volume, which this is not. At the stored
5.0 L/min cardiac output, the mixed-venous time constant moves from 12.0 s to
14.7 s.
<!-- provenance: data/patients/reference_adult.json venous_pool_volume_l = 1.222 -->
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->
<!-- not-restated: 70 kg -->

**What that costs, measured rather than argued.** The 30-minute $`F_A/F_I`$
wash-in distances are unchanged to two decimal places (+0.16, +0.31, +0.79,
+0.38 SD). The pool has long since equilibrated by then. So the published
wash-in comparison cannot discriminate between the two values, and it is no
evidence either way. The 5-minute $`F_A/F_{A0}`$ elimination ratios move
**0.11 to 0.13 published SD further from** their cohort means: sevoflurane
+3.67 to +3.79, isoflurane +4.02 to +4.15, and desflurane +1.02 to +1.13. They
move because a larger pool returns more agent to the lungs. § "Published
wash-in and elimination validation test" already attributes a shift in the
same direction to this model's rebreathing circuit rather than to tissue
return. This shift is a tenth of the gap it adds to. The nine oracle reference
states were re-derived and re-pinned in the same change.
<!-- not-restated: 0.31 -->

**It also settles the arterial question, and against the arterial reading.**
The suspicion was that the stored 1.0 L might be an arterial compartment under
a venous name. The basis was Lerou and Booij's arterial fraction of 0.2, which
gives 0.98 L at their 4.9 L total, within 2% of what is stored. Davis and
Mapleson's own arterial pool for an inhaled-anaesthetic model is 799 ml, which
is 15.4% rather than 20%. So that coincidence does not survive the primary
source. Their venous pool is the closer structural match, and the time
constants nearly agree: 1222/6480 = 11.3 s, against the 1.0/5.0 = 12.0 s that
this file used until 2026-09-07. That near agreement is a property of the time
constant rather than of the volume. It was not evidence of a shared lineage,
because nothing documents Gas Man as having taken anything from this paper.
<!-- not-restated: 2 % -->

**Where 1.0 L came from is answerable, and the answer changed on 2026-09-15.**
The value entered the repository on 2026-08-22 in `875ba08`, "Build v0.1.0 sevo
patient simulation", the tenth commit. It was written into the data file with
the rest of the reference patient. It carried the citation "Gas Man Workbook
and Laboratory Manual. Default Options: Patient Defaults", whose note read "The
default 70 kg patient uses alveolar volume 2.5 L, venous volume 1.0 L, alveolar
ventilation 4 L/min, cardiac output 5 L/min, tissue volumes 6/33/14.5 L, and
flow percentages 76/18/6". `PL-XTMB` read that section at the source. It is
Appendix E, page 183, and it describes the interface controls without giving
any number. The table that does give numbers, Appendix B page 168, has a
`Blood` row of 5.00 L and nothing at 1.0. On that evidence, this section said
until 2026-09-15 that none of the four sources ever cited for the value
contained it.
<!-- not-restated: 70 kg, 2.5 L, 4 L/min, 5 L/min, 6 L, 33 L, 14.5 L -->

**It is in the Workbook, one appendix further on.** Appendix C's `GASMAN.INI`
listing, on page 172, reads `[Volumes] … VEN=1.0`. The v0.1.0 note's sentence
matches that listing's three blocks item for item. It has the volumes. It has
the flow fractions as the *percentages* `76`/`18`/`6` that the INI writes,
rather than the table's 0.76/0.18/0.06. And it has `VA=4` with `CO=5` from
`[Defaults]`. So the original citation was **mis-sectioned rather than
borrowed**. It named Appendix E, but the numbers were read off Appendix C, and
every value in that sentence, including 1.0 L, is on that page. `PL-XTMB` and
`PL-3YZW` quote Appendix B and Appendix E and never Appendix C. Whether that
page was among those supplied on 2026-09-06 and went unread is not recorded.
<!-- not-restated: 0.76, 0.18, 0.06 -->

**None of this promotes the value or argues for restoring it.** `VEN=1.0` is a
program default, tier 3. Davis and Mapleson's 1222 ml is tier 2 and is the same
object this model has. It was adopted on 2026-09-07 and that decision still
applies. Two things change. The stored venous pool is a considered replacement
for Gas Man's own default, not the correction of a value with no known source.
And the one round number in this file with no counterpart anywhere is now
`weight_kg`, which no equation reads.

**So, three rules for a `sources` entry.**

- Name the tier. Where the stored value is not a primary measurement, say in
  the note which value the primary literature reports and by how much the two
  differ. Use words that a reader comparing against a textbook can act on.
- Do not let a primary citation stand in for a primary value. Citing a
  measurement *alongside* a tier-3 number does not source that number. A file
  that looks sourced while its number came from somewhere else is worse than
  one that cites nothing, because it stops the reader checking.
- Where no primary source has been adopted, record that as an open gap rather
  than as a settled citation. "No primary source has been adopted for this
  value" is a legitimate provenance state for an educational simulator, and
  one that can later be fixed. A tier-3 citation presented as settled is
  neither.

This applies to what a session *says* as well as to what it writes down.
Suppose a session answers "where does this constant come from?" with Gas Man,
or with a paper that reports Gas Man's table. That answer states a tier-3
provenance as though it were a measurement. It is the same error, made in
conversation instead of in a file.

**The first and third of those rules are now part of the schema, and
`make check` enforces them.** Data files moved to `schema_version` 2 on
2026-09-07 (`PL-1JDD`). All four files moved at once, because that change
applied to every family of them. Since `PL-HNWX`, each family has had its own
version. Agent, patient and machine files are each checked against their own
supported window of versions in `src/anesthesia_sim/core/parameters.py`. So a
later schema change moves only the family it applies to. At version 2, every
`sources` entry gained two new required fields, and a data file may carry one
new optional top-level string. Version 3 (2026-09-30, `PL-9LXK`) again applied
to every family, and it added a third required field to each entry. Today
every window accepts version 3 alone. The fields are written as a list rather
than a table. The reason is that the provenance table below is located by
being the first table in this section, and a second table above it would be
read in its place:

- `tier`, on each `sources` entry: `primary`, `secondary` or
  `reference-implementation`. It says which of the three tiers above the
  *document* belongs to.
- `adopted`, on each `sources` entry: whether this file names that source as
  the authority for a value it stores.
- `authority_for`, on each `sources` entry since version 3: the dotted key
  paths of the stored values for which this source is the authority. The paths
  are spelled as the provenance table spells them. The list is empty exactly
  when `adopted` is false. It records which source each stored value rests on.
  Before version 3, only a note's prose said so, and the per-row counts under
  § "Source hierarchy" had nothing to be computed from.
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

Each rule fails the build rather than raising an advisory, because none of
them needs any context to decide. `src/anesthesia_sim/core/parameters.py`
validates the vocabulary and the `authority_for` rules when it loads a file.
So a bad entry fails when the file is read, rather than when the checker next
runs.

**`tier` and `adopted` are two fields because one field alone would decide
nothing.** Every agent file cites primary measurements that it has explicitly
*not* adopted. So does the reference patient, which cites five. A check that
read the tier alone would therefore report all four of this project's data
files as primary-sourced. Yet on that same day, this document records that
most of the provenance table's rows are tier 3. That count is
stated once, under § "Source hierarchy", and is deliberately not repeated
here. The count changes whenever a row is added or a source is adopted, and
keeping two copies of it is how the previous pair came to be wrong
(`PL-7KDC`). A tier-only report would be the exact failure that the second
rule above exists to prevent. So the check has to read the adoption rather
than the citation list. As things stand, the three agent files each declare
two adopted primary sources, for `mac_awake` and for the vaporizer maximum.
`src/anesthesia_sim/data/patients/reference_adult.json` declares none and
carries the gap.

**What the check does not decide is whether a citation labelled `primary`
really is one.** That needs somebody who has read the paper. A tool that
guessed at it, by author, by journal or by a keyword denylist on a product
name, would look authoritative and be wrong. The tool checks that a claim was
made and is well-formed. A reviewer checks that the claim is true. The
provenance table below already works on the same split. The checker decides
that a documented key exists and has the stated value, never that the value is
right.

The following table records the values selected for v0.1.0. Each value is
loaded from a versioned data file and validated against its schema, rather
than hardcoded. Full citations, definitions and reference conditions are
recorded as `sources` entries in that file, not duplicated here.

Each row names the file and, beside it, the exact JSON key path that the row
documents. So a row is traceable to one stored value, rather than to a file
that happens to contain a matching number. `tools/doc_check.py` (run by
`make check` and CI) checks the table against the data files in both
directions. Every row must name a key that the file contains and state the
value stored there. Every numeric parameter in every data file must have
exactly one row. A derived row states the stored value beside the derived one.
The tissue:blood coefficients are computed at load time from the tissue:gas
and blood:gas values, so their rows name the stored tissue:gas key and show
the division.

Both directions start from a data file. So a constant that never entered a
data file is invisible to that check. The circuit volume was invisible in that
way while it sat as a `BreathingCircuit` field default with no row here
(`PL-4YY1`).
`test_every_constant_a_core_dataclass_defaults_to_is_a_value_the_provenance_table_selects`
screens for the next such constant (`PL-65HT`). It reads every numeric field
default on a `core/` dataclass through `dataclasses.fields()`, so it also
reads a default spelled as a named constant. It requires each default to
appear in this table's Selected-value column. Zero, and the whole of the
field's own scale (1, or 100 for a percent), carry no science and are not
screened. The test is a screen and not a proof, because it matches values
rather than names. A new constant equal to one the table already selects
passes. And 6.0 is selected for the circuit and the vessel-rich tissue alike.

The table is not the only place these values appear. Some prose restates one
of them: the reference adult's alveolar volume and ventilation, and each
agent's blood:gas coefficient, vaporizer maximum and MAC. Where it does, the
sentence carries a marker that names the file and the key it restates. The
marker is written as an HTML comment, so it is invisible in the rendered
document:

```text
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
```

`doc_check.py` enforces both halves of that link. It checks the key against
the data file, and it checks the stated value against the paragraph that the
marker sits under. So neither the file nor the sentence can change without the
other. That is the failure the markers exist to prevent. Before the markers,
editing a data file updated this table, because the checker forces that, but
it left the surrounding prose quietly wrong.

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

**Rewording a marked sentence is expected to fail the check.** The failure is
the marker asking to be moved or updated with the sentence. It is not a false
alarm.

A marker can also name a constant in code, such as the shipped step. It is
written as the module's path under the package, followed by the constant's
name:

```text
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
```

**A figure that equals a stored value must carry a marker** (`PL-JS6P`).
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
as an alveolar volume in litres, as a tolerance in seconds and as a flow in
litres per minute. `2%` is sevoflurane's MAC in one sentence and a dial
setting in the next. Binding each figure to a key by its value would be
confidently wrong in the places a reader trusts most. So the writer says which
kind it is, and the check enforces only that somebody did. A marker ties a
figure only to a value that the marker names, in that value's unit. So a
marker for the 6 L circuit does not clear desflurane's 6% MAC in the same
paragraph. The check recognizes a unit written as a word, such as "seconds".
It also recognizes a time in milliseconds, minutes or hours, which it converts
to seconds. It recognizes a unit spelled in lower case, such as "l/min". In a
list joined by slashes, such as "6/33/14.5 L", it reads each number with the
list's unit. In math, it reads a symbol given a number with `=` or `\approx`,
such as $`V_A = 2.5`$ L or $`V_A = 2.5\,\mathrm{L}`$, where the number ends
the span or comes before a comma, a semicolon or `\quad`. It reads no other
number in math, because most numbers in an equation are exponents and
coefficients that only happen to equal a stored value. It also does not read a
math span that is split across two lines. A marker under a list covers the
whole list, because a marker cannot be placed
inside a list item. A `not-restated:` marker fails if it lists a figure that
its paragraph no longer contains. So the declaration cannot outlive its
sentence. A number that equals no stored value, such as a flow-sweep point or
a worked example, needs no marker.
<!-- not-restated: 6 L, 6 %, 33 L, 14.5 L, 2.5 L -->

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

The reference patient weight identifies which patient the volumes and flows
describe. No equation in this model uses it. `PatientParameters.weight_kg` is
loaded and range-validated, and nothing else reads it. The compartment volumes
and flows are the source's absolute values for a 70 kg adult. They are not
quantities scaled from a weight, so changing the weight alone would not
rescale them. The litres are Gas Man's form of the data rather than the form
used by Gas Man's upstream source. Lowe and Ernst, the book that the Workbook
names, prints the same material as per cent of a 100 kg body, with cardiac
output an allometric function of mass (`PL-YKSM`).
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**The vessel-rich flow fraction is 0.76 here and 75.8% in the one reachable
publication of the same parameter set**, and the difference is recorded rather
than reconciled away. The stored value comes from the Workbook's own page-168
table, which gives the vessel-rich relative flow as 0.76 (read at the source
on 2026-09-06). Table 1 of De Wolf et al. 2012 prints 75.8. That is the same
paper the twelve partition coefficients come from, and 75.8 + 18 + 6 = 99.8.
`_ReferenceAdultPayload._perfusion_fractions_must_sum_to_one` and
`PatientCompartments.__post_init__` each reject a set whose sum lies outside
`FLOW_FRACTION_TOLERANCE = 1e-12` of 1.0. So the published triple could not be
stored as printed, even if it were preferred. That tolerance stays where it
is, because a tolerance wide enough to admit 99.8% would also admit a
transcription error silently. The difference changes the vessel-rich time
constant by 0.26%, which is below the resolution of anything a learner reads
off the curve. The finding is the provenance, not the arithmetic. The De Wolf
entry in `reference_adult.json` records it in full (`PL-0NQ1`).
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->

**The two machine rows adopt no source at all, which is a stronger statement
than the reference patient's gap and is meant to be.** The two values describe
the apparatus in front of the patient rather than the patient. So they live in
`data/machines/reference_circle_system.json`, a third kind of parameter file.
`PL-4YY1` added that file. It moved both values out of field defaults in
`core/circuit.py`, where no provenance row could cover them, and it changed
neither value.

- **Circuit volume, 6.0 L.** The Workbook's own page-168 table publishes 8.0 L.
  The Methods of De Wolf et al. 2012 print the same 8 L for the simulations to
  which their Table 1 supplied the coefficients. This project keeps 6.0
  deliberately. The project owner ruled on 2026-09-01 that which value is used
  is not critical. The departure changes the machine's own share of the early
  rise. $`\tau_C = V_C/\dot V_F`$ is 90 s here, against 120 s at 8.0 L and the
  same flow, which makes the apparatus lag 25% shorter. That lag is the part
  of the inspired curve that a learner is most likely to attribute to uptake.
  So a run that reproduces a published Gas Man trajectory has to set 8.0 L
  rather than assume it. Like every `circuit_volume_l`, the 6.0 L is an
  assembled total of apparatus plus patient circuit (§ "Breathing circuit").
  No source apportions it between the two.
  <!-- derived: 90 s from data/machines/reference_circle_system.json circuit_volume_l = 6, default_fresh_gas_flow_l_min = 4 -->
- **Default fresh gas flow, 4.0 L/min.** No published counterpart for this
  value exists in any source this project has reached. The Workbook's
  parameter table gives the circuit row a volume and no flow. Its interface
  defaults are described without numbers. The two Gas Man simulation studies
  read here chose flows for their own purposes (De Wolf et al. used 1 L/min,
  and Weber et al. used 10 L/min for washout). The value is a **teaching
  default, not a clinical recommendation** (project owner, 2026-09-20,
  ratified, over lowering it to match contemporary low-flow practice). It is a
  flow well inside the supported interval. It was chosen because it puts the
  circuit time constant at 90 s. That is long enough for the machine lag to
  show as a distinct phase of the early rise, and short enough to resolve
  within the first minutes of a teaching run. This choice is a design
  rationale, and the data file labels it as one rather than as a measurement.
  **It is also the flow a run starts at when a machine profile states none**
  (`PL-QW19`). `default_fresh_gas_flow_l_min` is optional in a profile,
  because no surveyed machine publishes a startup flow. A run built from a
  profile that omits it starts at `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`
  in `core/circuit.py`
  (`test_a_profile_omitting_the_default_fresh_gas_flow_falls_back_to_the_teaching_default`).
  The authority for that fallback is this rationale and not a source.
  `test_the_flow_default_matches_the_shipped_machine_file` fails if the
  constant and the file's value ever differ. The rationale is stated for this
  file's 6.0 L circuit. At a smaller assembled volume, the same flow gives a
  shorter lag, as § "What real workstations hold" below computes.

<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->
<!-- not-restated: 10 L/min -->

**The project now holds one measured circle-system volume, and it sets a bound
on the first row rather than replacing it** (`PL-QBKQ`). Targ, Yasuda and Eger
measured a conventional circle system by water filling at **9860 ml**
(*Anesth Analg* 1989 Aug;69(2):218–25, PMID 2764290). It is the same study
that lies behind the inert-circuit entry under § "Known limitations". It was
read at full text on 2026-09-13 from the private reference corpus. The value
is not adopted, and the reason is what the measured system contained. It
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

**What real workstations hold, and why that does not settle this row either**
(`PL-4DCG`). `docs/machine-survey.md` surveys the machines in current clinical
use for the variables that affect a number this model computes. The assembled
volumes it collects sit below both figures above. Shin et al. print apparatus
volumes of 4.7 L for a Dräger Primus, 2.1 L for a Perseus A500 and 2.0 L for a
Zeus IE. Each includes the absorber and excludes the disposable patient
circuit. Adding the 1.2 L circuit that they computed their totals with gives
5.9, 3.3 and 3.2 L. So at this file's flow, the circuit time constant runs
from 89 s on the oldest of the three machines to about 50 s on the newest.
That is a factor of about 1.8 across machines that a learner would meet in the
same department. The stored 6.0 L lands within 2% of the Primus's assembled
5.9 L. That match is a coincidence rather than a sourcing. The stored value
predates the survey and was kept on the ruling above.
<!-- derived: 89 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->
<!-- not-restated: 2 % -->

**And volume is not the whole of the difference**, which is the survey's
finding rather than this document's. Fukuda et al. moved only the fresh gas
inlet, with the machine and the volume held fixed. The inspired/delivered
ratio of both isoflurane and sevoflurane rose significantly at low flow
(*J Anesth* 2006;20(4):268–73). $`F_I/F_D`$ is what the circuit equation above
computes. So a real machine changed it through a property that this model has
no place to put. The survey carries the consequence for the planned machine
abstraction. What it means here is that a future per-machine
`circuit_volume_l` reproduces part of an inter-machine difference, and must
not be described as reproducing all of it. `docs/machine-abstraction.md` is
where that consequence was decided (`PL-FG9D`). Internal topology is not
represented. Folding it into an effective volume is refused, because that
would attribute to volume a difference that volume did not cause.
`ROADMAP.md`'s planned-milestone item 39 states the condition under which the
decision not to represent internal topology is revisited.

**The flow row's gap has since been searched, and what came back is a
recommendation rather than a convention** (`PL-NM7X`). `docs/machine-survey.md`
§ "(a2)" looked for a startup fresh gas flow published by any machine in
current clinical use, and found none. So the row above still adopts no source.
The gap is now narrower than "not sought". What is missing is a published
startup convention, and such a convention does not appear to exist. What the
literature carries instead is normative. Kalmar et al. conclude that
*"routine clinical practice using what historically is called 'low flow
anaesthesia' (e.g. 2 L/min FGF) should be abandoned"* in favour of automated
minimal-flow delivery (*J Clin Monit Comput* 2022;36(6):1601–1610, PMID
34978655). The paper was read at full text on 2026-09-20 from PubMed Central,
PMC9637609, where the quoted sentence closes the abstract. That is the
recommendation of a single-centre retrospective study, not a measurement of
what flows are used. But its own comparator is a fixed 2 L/min group that it
calls conventional low flow, and that flow already sits below this model's
4.0.

**Until 2026-09-20 this section called 4.0 L/min "a routine mid-range clinical
flow", and that sentence is withdrawn rather than re-sourced.** It was a claim
about clinical practice that no source this project holds supports. Under the
safety-critical standard, a correct number carrying a wrong provenance is
still a presentation failure. **The number did not change**, because an
unlabelled default teaches a norm whatever value it has. Moving to 0.5 L/min
would relocate the problem rather than remove it, and would carry the same
absent provenance. It would also put the apparatus lag at **12 minutes**,
longer than the demonstration that the default flow exists to make. What was
wrong was the sentence.
<!-- derived: 12 minutes from data/machines/reference_circle_system.json circuit_volume_l = 6.0 -->
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->

**Two papers cited alongside Kalmar et al. in the survey do not bear on
practice, and the survey now says so.** Candries et al. randomised flows of
0.2 to 6 L/min in 28 patients, as the protocol of a Gas Man validation study.
Hoffmann et al. ran 0.3 to 6 L/min *in vitro* into a test lung, and describe
those settings as reflecting clinical conditions. That range contains 4, 5 and
6 L/min. A study's chosen flow range is not a report of practice. Treating it
as one is the same error that the De Wolf entry guards against for its 1 L/min
elsewhere in this section.

There is no "arterial blood-pool volume" row. Arterial blood is flow-limited
and has no state of its own (see § "Model boundary"). The code derives the
tissue:blood coefficients at load time, as tissue:gas divided by blood:gas, in
the `AgentParameters` properties in `core/parameters.py`. The data file does
not store them a second time. The tissue-blood partition-coefficient tests in
`tests/unit/test_parameters.py` guard this derivation.

**The division is the literature's own operation, and one published table
reproduces its results** (`PL-H536`). Eger and Saidman state the operation in
these words: "a tissue/blood partition coefficient for a given anesthetic is
calculated by dividing a tissue/gas partition coefficient by the blood/gas
partition coefficient for that anesthetic" (p. 1023). Yasuda, Targ and Eger
computed their own tissue:blood table the same way, as the next subsection
records. Both papers were read in full text from the private reference corpus,
and Eger and Saidman's p. 1023 was read for this paragraph on 2026-10-25. The
full citation of Eger and Saidman is in § "Known limitations".

Baker and Farmery's 2011 review publishes the results as well as the
operation. Its Table 2 (p. 572) prints two sets of tissue:blood coefficients
for the vessel-rich, muscle and fat groups. The set that matches is the one in
brackets, which the table's footnote d attributes to Eger and Shafer.
Desflurane has only that set. The table was read in full text from the private
reference corpus on 2026-10-25 (`PL-VPF8`). Every figure matched the ones the
session that filed `PL-H536` had recorded from an earlier copy on 2026-09-03.
In each cell the first figure is this document's derived row and the second is
Baker's bracketed figure:

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
values are Yasuda, Targ and Eger's measurements as Gas Man rounded them, and
the stored blood:gas values are De Wolf et al.'s. Eger is an author in both
lines, so the two are not independent in origin. If Eger and Shafer took their
coefficients from Gas Man, the match is one parameter set divided twice. Their
paper is not held here, so where its coefficients came from has not been read.
A reader should take the table as evidence that the division is the right
operation, and not as evidence that the coefficients are right. § "Known
limitations" says how far other laboratories' coefficients differ from these.

**Baker's other set is not a check on the division.** Its plain figures are
"Data from Fiserova-Bergerova and Diaz (26)", a 1986 paper. They come with
their own blood:gas values, 0.6 for sevoflurane and 1.4 for isoflurane, and
they differ from the derived rows by far more than rounding. § "Known
limitations" gives the differences. The citations of Baker and Farmery 2011,
Eger and Shafer 2005 and Fiserova-Bergerova and Diaz 1986 were checked in
PubMed on 2026-10-25 (PMIDs 23737195, 16115976 and 3721592). Only Baker and
Farmery was read in full text. `docs/references/README.md` has its full
citation.

### v0.2.0: isoflurane and desflurane

Isoflurane and desflurane use the same governing equations and compartment
structure as sevoflurane. They also use the same physiologic parameters, from
`data/patients/reference_adult.json`. Only the partition coefficients in each
agent's own `data/agents/*.json` file differ. All twelve values came to this
project through one table: De Wolf et al. 2012, Table 1, which is the paper
already cited for sevoflurane. The three data files are therefore directly
comparable, rather than assembled from unrelated sources.

**Since 2026-09-13 that comparability rests on something better than a shared
publisher.** The nine tissue:gas values in that table are the human
measurements of Yasuda, Targ and Eger 1989. They were checked against the
paper and adopted (`PL-FN5F`). So the three agents are comparable because
their tissue coefficients come from *one study, one laboratory, one technique
and one cohort*. The values were measured side by side in the same specimens.
That is the strongest form of the property that a MAC-normalized axis needs,
not a weaker one. Whatever the systematic error of that technique is, every
agent carries it identically. The three blood:gas values are still the Gas
Man set, and they are still tier 3, so the shared-error argument applies to
them only in its original, weaker form.

Both halves of that argument are about the *coefficients*, which are the
subject of this paragraph. The argument does **not** extend to the three
`mac_percent` divisors. Their deviations from the primary literature run in
opposite directions between sevoflurane and desflurane.
"Delivery-limit and MAC parameters" measures that separately. Each agent file
records the primary measurement alongside its stored number and states the
difference.

**Gas Man says those coefficients are Yasuda's, and that claim is recorded
without being acted on.** The note under the Workbook's own page-168 parameter
table reads "Values for isoflurane, halothane, desflurane and sevoflurane are
taken from Yasuda, Targ and Eger". If that claim were true, the twelve
coefficients would descend from a human tissue-solubility measurement rather
than being a simulator's choices. Four things stop the claim from moving the
tier, and the first is enough on its own:

- A program's statement about its own provenance is the program talking about
  itself. This is the same rule as
  § "Republication does not promote a value between tiers" above, applied one
  link further back.
- The Workbook names a different document from the one that the agent files
  cite. Its reference 45 is the abstract `Anesthesiology 69:A615`, from the
  1988 ASA annual-meeting supplement. It is not Yasuda, Targ and Eger's 1989
  *Anesthesia & Analgesia* paper. What the abstract reports is unknown here.
- The same paragraph contradicts itself for sevoflurane. It credits
  sevoflurane's values to Yasuda and, one sentence later, to
  "the package insert and Abbott data".
- The arithmetic is close but not exact. Multiplying Yasuda's measured
  brain:blood by each file's stored blood:gas reproduces the stored
  vessel-rich tissue:gas exactly for sevoflurane and desflurane (1.1050 → 1.1;
  0.5418 → 0.54). For isoflurane it gives 2.0410 against a stored 2.1, a miss
  of 2.9%. That miss is less than half the measurement's own standard
  deviation. The arithmetic is close enough to suggest the route, but never
  enough to name it.

<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.vessel_rich = 2.1 -->

**The check has since been run, and the claim is confirmed.** The project
owner supplied the full text of Yasuda, Targ and Eger later the same day. It
was read at full text on 2026-09-13 and is in the private reference corpus.
Its Table 1 reports tissue:**gas** coefficients, which is the quantity that
the agent files store. The coefficients come from 14 autopsy specimens, 6 to
10 per tissue, with a mean age of 65.8 ± 14.4 yr, equilibrated at 37 °C. The
table below compares them with the nine stored values:

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

All nine stored values lie within 0.71 SD of the measured mean, and three of
them reproduce it to the stored precision. A parameter set assembled from
somewhere else could not match that closely by coincidence. So the Workbook's
attribution is confirmed by the arithmetic, not by the Workbook's own say-so.
The Workbook's self-contradiction is resolved in Yasuda's favour.
Sevoflurane's three stored values match this paper, not a package insert.

Two things follow that are not about provenance:

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

**The tier moved and the values did not.** The project owner decided this on
2026-09-13 and took it as two separate questions (`PL-FN5F`).

*Adopted.* The nine tissue:gas coefficients descend from a primary human
measurement. So Yasuda, Targ and Eger is now the adopted authority for them in
all three agent files, and they are tier 1. De Wolf et al. stays the adopted
authority for the three blood:gas values alone, which this study did not
measure. No number changed with the adoption. What changed is the record of
where the numbers came from. Separating `tier` from `adopted` exists to carry
that record.

*Declined.* Storing Yasuda's published figures in place of Gas Man's rounding
of them would move three displayed time constants. Sevoflurane vessel-rich
would move +4.5% at 1.15 against 1.1, isoflurane fat −8.3% at 64.2 against
70.0, and desflurane fat −7.7% at 12.0 against 13.0. The change would also
require recomputing every pinned reference state under `tests/reference/`,
because those states are this parameter set's solution. The accuracy it would
buy is also within the error that the model's own lumping already carries. The
vessel-rich group is one compartment standing for brain, heart, liver, kidney
and viscera. So a difference of 0.05 on a brain measurement is not one that
this structure can use. `PL-D6LX`'s original decision to keep the Gas Man
values therefore still applies, now for a better-evidenced reason than it had
(`PL-ZP7Z`, `PL-B9K7`, `PL-FN5F`).
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13 -->
<!-- not-restated: 0.05 -->

Desflurane is markedly less soluble than sevoflurane, which is itself less
soluble than isoflurane (blood:gas 0.42 < 0.65 < 1.3). This does not change
any equation. Lower solubility only means faster equilibration through the
same closed-form solutions. `tests/reference/test_multi_agent.py` checks this
directly by comparing simulated alveolar/circuit ratios, rather than only
comparing the static coefficient values.

<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->

**Desflurane's tissue coefficients have been questioned against a published
measurement and kept.** Its five-minute elimination is the one comparison in
this repository that misses a human measurement in the direction of washing
out too fast. The sensitivity of that ratio makes the vessel-rich coefficient
the obvious suspect. The coefficient is not the cause. The reasoning is in
"Desflurane's residual, and why the parameter file was not changed", not here,
so that it sits beside the comparison that raised it. Read that section before
changing any coefficient in `data/agents/desflurane.json`. The value that the
disagreement demands is nineteen standard deviations above the human
measurement. That value would also invert the measured solubility ordering of
the three shipped agents.

### Delivery-limit and MAC parameters

Two per-agent parameters are stored in the agent data files but play no part
in the governing equations. Each one exists to limit a control that the user
sees, or to set its starting value. Both are recorded here because a value
that a clinician could read or act on is safety-critical, whether or not the
model integrates it.

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

**It is a device-capability default stored under the agent on purpose, and
where it is stored is not a claim about the agent** (`PL-JQY1`). Each agent
file's value is the calibrated dial maximum of the vaporizers that the file's
adopted source names. These are the Dräger Vapor 2000 and Datex-Ohmeda
Sevotec 5 for sevoflurane, the Penlon Sigma Delta and Datex-Ohmeda Isotec 5
for isoflurane, and the Tec 6 for desflurane. Each file's note calls the value
a device-capability limit rather than a scientific model parameter. So
desflurane's figure says how far a Tec 6 dial turns. It does not say that
desflurane cannot be delivered above that figure. Another desflurane
vaporizer, or an injector that delivers into the circle, is not bound by
anything about the agent.

The value stays under the agent for two reasons. First, the reference
breathing system in `data/machines/reference_circle_system.json` is not a
machine and names no vaporizer. A per-machine entry would today only repeat
the agent file's number and add nothing to it. Second,
`_AgentPayload._mac_percent_must_not_exceed_vaporizer_max()` in
`core/parameters.py` rejects an agent whose own vaporizer cannot deliver its
1 MAC. The 1-MAC start in `AgentUptakeSystem.for_agent()` depends on that
check. The check can be written only where the maximum and `mac_percent` are
in the same file.

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

**The three maxima come from two different classes of vaporizer, and that
distinction matters nowhere in this model except away from sea level.**
Sevoflurane's 8% and isoflurane's 5% are the maxima of variable-bypass dials.
Desflurane's 18% is the upper end of the Tec 6's range, and a Tec 6 is a
heated gas–vapour blender rather than a variable-bypass vaporizer. This list
is the one place in the document where both classes appear together, although
it does not name them. At the 760 mmHg fixed under § "Assumptions", a dial
position on either class gives the same partial pressure. So nothing in the
core has to know which kind of device a given limit came from. The two classes
behave differently only at reduced ambient pressure, which is not modelled.
See § "Known limitations".
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

MAC is a population ED50 for immobility in response to a standardized
stimulus. It varies with age, and it is modified by other agents, opioids,
temperature and patient factors, none of which are modeled here. Presenting a
single-agent alveolar concentration as if it indexed anesthetic depth would
be exactly the kind of plausible-but-wrong clinical inference that
`CLAUDE.md` forbids. That is why the displayed unit is a *ratio to* 1 MAC,
written `×MAC`, and never a depth. The display section named above gives the
reasoning for that distinction. The rest of this section says how much the
three stored numbers are worth.

**The provenance tier now carries clinical weight, and it did not before.**
While `mac_percent` only chose where the dial started, an error in it moved
the starting point of a run and nothing else. It is now the divisor of every
displayed compartment value and of the chart's second axis. In that role it
is a clinically meaningful transformation under `CLAUDE.md`'s safety-critical
standard. The stored values are **tier 3**. They are the flat adult MACs that
De Wolf et al. state they used in their Gas Man simulations. They were adopted
for two reasons. They belong to the same parameter set as every partition
coefficient in this model. And the reference adult has no age parameter to
which an age-related MAC could be applied.

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

The errors run in opposite directions for sevoflurane and desflurane. So a
comparison of sevoflurane with desflurane in MAC multiples differs by about
22% between the two MAC sources. This comparison is exactly the one that the
second display unit exists to make honest. The difference is larger than either
source's own confidence limits. It is a real limitation of the display, and
it is recorded in "Known limitations" rather than left implicit.

**Why the Mapleson values are nonetheless not adopted here** (project owner,
2026-09-04, on the recommendation below). There are three reasons, and the
first is this document's own rule. Mapleson 1996 is a meta-analysis. It fits
a regression to a literature survey and measures nothing, which makes it
**tier 2** under § "Source hierarchy". That does not forbid adopting it
outright, because a lower tier may be adopted on a recorded decision. It does
mean that adopting it would need such a decision, and the two reasons below
are why this decision went the other way. Second, every other parameter in
this model comes from the Gas Man set. A Mapleson divisor applied to a Gas Man
trajectory would make each displayed multiple a ratio between two different
parameter lineages. Dividing this model's output by this model's own MAC is
at least internally consistent. Third, confidence limits of ±7-10% mean that
no MAC source makes a cross-agent comparison exact. So the honest response is
to display the divisor and disclose the limitation, which the interface and
this section do. That is more honest than substituting a different
non-primary number and presenting it as settled. The route to primary values for all three
agents is `ROADMAP.md`'s planned-milestone item 31.

**This is a decision taken, not a default left standing.** The question was
put to the project owner when the second display unit was built. The gap had
been measured and the alternative costed, and the stored values were kept on
2026-09-04. Revisiting the decision is therefore a change to a recorded
decision, not a correction of an oversight. A later revision has to answer
the case above, and item 31 is where that answer belongs. The reason is that
moving `mac_percent` alone would leave one parameter on a different lineage
from the twelve coefficients beside it.

Each agent's `sources` array carries the citation, the tier, the Mapleson
value that the stored value was not taken from, and the difference between
the two.

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

### Zero-agent test

If all initial stores are zero and $`F_D=0`$, then every stored amount and
concentration must remain zero.

### Zero-ventilation test

If $`\dot V_A=0`$, the circuit may wash in, but the patient compartments must receive no new agent through ventilation.

### Zero-cardiac-output test

If $`Q=0`$, alveolar gas may change through ventilation, but arterial blood, venous blood, and tissue stores must not change through perfusion.

### Zero-tissue-flow test

For any tissue $`i`$, $`Q_i=0`$ must imply $`\frac{dM_i}{dt}=0`$.

### Equilibrium test

If all connected compartments have the same partial-pressure-equivalent
fraction, with $`F_I=F_A=F_a=F_v`$ and every tissue group at the same value,
then all internal transfer rates must be zero.

### Directional ventilation test

With otherwise identical conditions, increasing alveolar ventilation must accelerate the approach of $`F_A`$ toward $`F_I`$.

### Directional solubility test

In controlled synthetic cases, increasing $`\lambda_{b:g}`$ must increase blood capacity and slow the rise of $`F_A/F_I`$.

### Directional tissue-capacity test

Increasing either $`V_i`$ or $`\lambda_{i:b}`$, with flow held constant, must lengthen the tissue time constant:

$$
\tau_i =
\frac{V_i\lambda_{i:b}}{Q_i}
$$

### Washout test

After loading the compartments, setting $`F_D=0`$ must produce finite,
nonnegative washout without spontaneous increases in total system mass.

Individual tissue concentrations may rise for a time through redistribution.
The test must therefore not require every compartment to decrease
monotonically.

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

**What the third step size asserts changed with the exact step, and the
claim is now stronger.** Under the operator split, the gate required each gap
to be *smaller* than the last. The split had a first-order error that halved
with the step and converged to a limit that none of the three steps reached.
Every supported step now lands on that limit. The gaps therefore sit at the
smallest size that floating-point rounding allows, and they no longer shrink.
Requiring them to shrink would fail correct arithmetic. The gate requires
instead that the gaps stay at that rounding level. Measured on 2026-09-06, the
worst successive-halving gap across the four reported values is 8.1e-16. A
first-order method would show 1.4e-11 at these steps.

**A second test beside the gate drives the bottom of the supported domain**,
`MINIMUM_SIMULATION_STEP_S` (`PL-YZ17`). A minute simulated in 1 ms steps
must land within 3e-14 of the same minute simulated in 0.1 s steps, in each
compared fraction. This bound is wider than the bound for the halvings
because that minute takes 60 000 steps rather than at most 2 400, and the
residual is rounding error that accumulates once per step. Measured on 2026-10-03, the
worst gap is 2.4e-15, in the alveolar fraction. The bound allows about twelve
times that gap, which is the same margin the halvings have. The gap does not
vary smoothly with the step. It depends on how the propagator happens to
round at that particular step, and steps near 1 ms reach 1.2e-14. Against a
machine that rounds differently, the margin is therefore nearer two and a half
times. This test enforces the claim that the minimum step makes: the
solution at the declared minimum step is the shipped solution. The test also
pins the minimum step at 1 ms. Moving the minimum therefore means re-taking
these figures, not just editing a constant.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

The release comparison tolerance is 5e-3 relative or 1e-8 absolute, and
meeting either one is enough. It applies to the alveolar, vessel-rich and
mixed-venous fractions after 60 s of the default sevoflurane wash-in. Under
the operator split, comparing 0.1 s directly with 0.025 s exceeded the
tolerance in the mixed-venous fraction alone. That compartment has barely
begun to fill at 60 s, so the split's gap of 1.4e-6 in fraction between those
two steps was 0.55% of the mixed-venous fraction. Under the exact step, the two runs land about
4e-17 apart there (measured 2026-10-03).
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

This gate tests self-consistency across the supported steps, not
correctness. A wrong transfer rate is exactly as independent of the step as a
right one, so it passes here. The § "Independent-solution test" below is the
test that asks whether the solution is the right one at all.

### Independent-solution test

The coupled six-state solution must be checked against an integration of the
governing equations that shares no solver with the implementation
(`tests/reference/test_coupled_dynamics.py`). The oracle may load the
parameter files and nothing else from the package under test. A comparison
against code derived from the implementation is a tautology, not a
verification. So the test enforces that restriction on its own imports.

The comparison covers every shipped agent, and its tolerance is **absolute**:

$$
\max_k \left| F_k^{\mathrm{shipped}} - F_k^{\mathrm{reference}} \right|
\leq
4\times10^{-13}
$$

over every state $`k`$, every horizon and every trajectory below.

**Why absolute, where the split's bound was a coefficient.** The split's error
was $`C\,\Delta t`$, so a bound on $`C`$ bounded the error at every step size.
The exact step has no such coefficient. It is the solution of these equations
over the interval. What the comparison measures is the accumulated
floating-point difference between two independently written solutions, which
agree exactly in exact arithmetic. That residual grows with the *number* of
steps rather than with their size. So it is slightly worse at a finer step,
which is the opposite of the split. A per-step coefficient would therefore
state the reverse of what is true.

**Derived from the exact step's own error, not inherited.** The residual was
re-measured on 2026-09-07 across all three agents, the horizons above and
every trajectory below. The maximum was taken over the whole trajectory rather
than at the endpoints. At the shipped 0.1 s step, the five trajectories give
1.58e-14, 1.54e-14, 1.39e-14, 1.34e-14 and 8.80e-15. These lie within a factor
of 1.8 of one another. That is because the measurement is of accumulated
rounding, and every trajectory takes the same number of steps. The gate also
drives the same trajectories at 0.05 s and 0.025 s. That gives the worst figure
anywhere: **5.89e-14**, for desflurane on a *ventilator start* at the finest
step. The operator split's worst over the same domain was 2.29e-4 at this
step. Against it, the exact step is nine orders of magnitude closer to the
independent solution.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**Until 2026-09-07 this bound was 5e-12 and measured the wrong thing.** The
oracle ran at half the shipped step. At that step the oracle is converged at
held settings but not through a transient. So on the trajectories that set the bound, 86% to
99.8% of what the gate reported was the oracle's own RK4 truncation rather
than the shipped step's error. The bound therefore sat about 320 times above
the residual it was watching. A regression that made the exact step a hundred
times worse would have passed it. The oracle now runs at an eighth of the step
under test. At that step, refining the oracle further stops changing the
answer.

**The residual is rounding, not truncation, and that is checked rather than
asserted, by the absence of a direction.** Refining the oracle a further
eightfold, to 0.0015625 s, moves the five figures above by at most 11%. It also
moves them both ways. RK4 is fourth order. So a residual that still carried
the oracle's truncation would fall by a factor of about four thousand and
would never rise. A residual that reshuffles by a few percent in either
direction is the difference of two independently accumulated rounding paths.

The margin is deliberately wider than the 1.22 that the splitting bound
carried. A systematic coefficient reproduces between machines, but accumulated
rounding does not. A different `exp` implementation or a contracted
multiply-add moves the last bits of both solutions. So the margin is sized on
how much accumulated rounding can vary, not on the residual. The identical
trajectories were solved at 0.1, 0.05 and 0.025 s with no oracle involved. This is the same exact propagator, differently subdivided, so every
difference is the shipped side's own accumulation. The answer moves by up to
1.07e-13, which is larger than the residual itself. The bound clears that
spread by 3.7 times and the worst residual by 6.8 times. It remains nearly
nine orders of magnitude below the error of any method that is not exact. So
the gate fails the moment method error returns, and catching that is the only
thing the gate is there for.
<!-- not-restated: 0.05 -->

**The domain the bound covers.** The domain is *trajectories*, not operating
points. A run of the application is a sequence of settings, each held until
someone moves a slider. Moving a slider puts the split under the most strain,
because the state is then far from the equilibrium of the settings now in
force. A gate that holds one operating point for every run measures the split
only where the run never turns. That is the smaller half of what the interface
produces.

The gate therefore drives four kinds of run:

- the *reference point*, held and compared at horizons of 60 s, 600 s and
  3600 s. It is 5% delivered, 4 L/min fresh gas, and the reference adult's
  default alveolar ventilation and cardiac output. The pinned reference states
  below belong to this point.
- the *envelope corner*, held for 600 s. It is each agent's own
  `max_delivered_concentration_percent`, with fresh gas, alveolar ventilation
  and cardiac output all at their supported maxima. Those maxima are 10, 12
  and 10 L/min, which are also the sliders' maxima.
- a *ventilator start*: the same corner, but with alveolar ventilation at zero
  for the first 300 s, and then ventilation at its maximum. During the first
  300 s the circuit saturates at the dial setting against lungs that can take
  none of it. This is an ordinary manoeuvre, and it alone exceeds the previous
  bound.
- an *unperfused load, then dial off*: the corner with cardiac output at zero
  for 600 s, and then perfusion at its maximum with the vaporizer closed.
  During the first 600 s the circuit and alveoli saturate while every blood
  and tissue compartment stays empty. This is the worst trajectory the four
  sliders can reach.

<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- not-restated: 5 % -->

In every case the maximum is taken over the whole trajectory rather than at
an endpoint, because the worst disagreement is always inside a transient. At
held settings it is inside the wash-in transient, at about 85 s. Across a
setting change it is inside the transient that the change itself starts,
about 13 s later.

Both the corner and the worst trajectory are maxima by measurement rather
than by assumption. Across held settings, each axis was swept separately.
Fresh gas flow and alveolar ventilation raise the coefficient monotonically up
to their slider maxima. Cardiac output has an interior *minimum* near 5 L/min
and rises toward both ends, and the upper end is the larger. The governing
equations are linear in the delivered fraction, so each agent's worst dial is
its vaporizer maximum. Across trajectories, the corners of both phases were
swept first, and then each axis around the winner. The worst point is always
the first transition after the loading phase saturates. Repeating the cycle
three or six times does not raise the peak at all. So the coefficient is
bounded rather than accumulating over a run. A third phase inserted between
the two never beat the pair. Every axis is monotone toward the corner used,
except cardiac output during loading. That axis is worst at *zero*, which is
the opposite end from the held-settings corner. The monotonicity is measured,
not proved. So a change to the governing equations could move the maximum off
these trajectories. It is worth re-running the sweep rather than trusting it.
<!-- not-restated: 5 L/min -->

**The split's own coefficients are kept as history.** They are kept because
they describe what this project shipped for eleven releases, and because any
later work on step size starts from them rather than re-deriving them. The worst coefficient measured over
the whole reachable domain was
$`C_{\max} = 2.29\times10^{-3}\ \mathrm{s^{-1}}`$, on the
*unperfused load, then dial off* trajectory with desflurane:

| Run | Worst coefficient |
| --- | --- |
| Reference point, worst of the three agents | $`3.1\times10^{-4}\ \mathrm{s^{-1}}`$ |
| Envelope corner, sevoflurane | $`7.0\times10^{-4}\ \mathrm{s^{-1}}`$ |
| Envelope corner, isoflurane | $`7.4\times10^{-4}\ \mathrm{s^{-1}}`$ |
| Envelope corner, desflurane | $`1.21\times10^{-3}\ \mathrm{s^{-1}}`$ |
| Ventilator start, sevoflurane | $`1.03\times10^{-3}\ \mathrm{s^{-1}}`$ |
| Ventilator start, isoflurane | $`1.11\times10^{-3}\ \mathrm{s^{-1}}`$ |
| Ventilator start, desflurane | $`1.52\times10^{-3}\ \mathrm{s^{-1}}`$ |
| Unperfused load then dial off, sevoflurane | $`1.34\times10^{-3}\ \mathrm{s^{-1}}`$ |
| Unperfused load then dial off, isoflurane | $`1.40\times10^{-3}\ \mathrm{s^{-1}}`$ |
| Unperfused load then dial off, desflurane | $`2.29\times10^{-3}\ \mathrm{s^{-1}}`$ |

Two lessons from that gate survive it, and both are why the trajectories above
are still driven. Domain variation is what made each of its bounds wrong,
twice over, one dimension at a time. The bound was first set at
$`5\times10^{-4}\ \mathrm{s^{-1}}`$ from the reference point alone. It was
exceeded by a factor of about 2.4 at settings that three sliders could reach.
It was then reset at $`1.5\times10^{-3}\ \mathrm{s^{-1}}`$ from the envelope,
but measured only on runs that held one operating point. It was exceeded by a
ventilator start at that same corner, which is a manoeuvre a user performs.
Neither gate ever failed, because nothing it drove ever went where the error
was. A release gate narrower than the reachable input domain is a verification
claim broader than its evidence, whatever the method under it.
<!-- not-restated: 2.4 -->

**One safety disclosure this section used to carry is now withdrawn.** The
split applied its transfers in order. So each compartment was driven across
the interval by an upstream value that the same step had already moved. The
resulting bias had opposite signs at the two ends of the transfer chain. The
circuit read below the independent solution and the tissues read above it. So
a *difference* between two readouts carried the sum of two displacements. That
difference was the least accurate thing the interface displayed, at up to 1.8
times the error in either reading it was taken from. That was true of the
split and is not true of the exact step. The exact step drives no compartment
from an already-moved value and leaves no bias with a sign. A gradient between
two compartments is now no less accurate than either reading it is taken from.
The withdrawn claim is recorded here rather than deleted because it was also
published in § "Displayed precision" below. A reader comparing versions needs
to know which way it went.

The reference states are pinned in the test file. A change to the oracle or to
a parameter file must be re-derived and reviewed rather than silently adopted.
The pinned states are the oracle's own solution, not the shipped solver's.
Re-pinning them from the implementation would turn this gate into a
self-comparison. The supported ranges above are restated in the test file and
checked against `core/supported_ranges.py`. So widening the model's declared
domain cannot silently leave this gate measuring only a subset of it.

### Published wash-in and elimination validation test

Every test above is **verification**. Each one asks whether the
implementation solves the intended equations correctly. It checks this by
comparing the implementation against an analytic solution, an independent
integration of these same equations, a conservation identity, or the
implementation's own behavior at another step size or setting. None of these
tests asks whether the equations describe the phenomenon. A model can be
numerically flawless and physiologically wrong. A suite made only of the tests
above would report the first property as though it had settled the second.

This test is the **validation** half. It is the only required test whose
expected values come from outside this repository
(`tests/reference/test_published_wash_in_and_elimination.py`). The distinction
matters to a reader of the two sections. § "Independent-solution test" above
and this section answer different questions, and treating them as one
over-reads both.

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

Isoflurane is compared against both cohorts rather than one, in both
directions.

**For wash-in**, the model must land inside the published standard deviation
for every row. It must also reproduce the ordering by solubility that the two
studies were run to test. That is, $`F_A/F_I`$ is higher for desflurane than
for sevoflurane, and higher for sevoflurane than for isoflurane. The ordering
is required because three tolerances that happen to overlap do not make a
model. The model meets both requirements. The requirement for the elimination
rows is different, because the model does not land inside their spread. The
paragraphs below describe that requirement.

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

Fresh gas flow is the one setting the test chooses. The test sets it to
10 L/min so that $`F_I`$ is settled rather than still rising at 30 minutes.
Here $`F_I`$ is the modeled *circuit* fraction, not the vaporizer dial. A
settled $`F_I`$ matches protocols that held an inspired concentration at the
airway. The test shows that this choice does not carry the wash-in result.
Every agent stays inside its published spread at every fresh gas flow from 1
to 10 L/min. The choice does carry almost all of the elimination result. That
dependence is the reason the two comparisons are not equally strong, and the
next paragraphs cover it. One delivered fraction serves four different published
$`F_I`$ values because the governing equations are linear in that fraction.
The test asserts this linearity across the published range, for both ratios
separately, rather than assuming it.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

**The elimination comparison does not agree, and the model states the
disagreement rather than a tolerance around it.** At the shipped defaults, and
at the same 10 L/min that the wash-in comparison uses, the model has more
alveolar agent at five minutes than every cohort did. This was measured on
2026-09-06 and re-measured on 2026-09-07. The re-measurement followed
`PL-8ZJQ` raising `venous_pool_volume_l` to 1.222 L, which moved the rows 0.11
to 0.13 SD further above their means:
<!-- not-restated: 10 L/min, 1.222 L -->

| Agent | Cohort | Model | Published | Distance |
| --- | --- | --- | --- | --- |
| Sevoflurane | n=7 | 0.2328 | 0.157 ± 0.020 | +3.79 SD |
| Isoflurane | n=7 | 0.3227 | 0.223 ± 0.024 | +4.15 SD |
| Desflurane | n=8 | 0.1626 | 0.14 ± 0.02 | +1.13 SD |
| Isoflurane | n=8 | 0.3227 | 0.22 ± 0.02 | +5.13 SD |

So the assertion on these values is a **regression** pin. It pins the model's
own measured ratio to $`1\times10^{-4}`$ absolute. It claims nothing about
agreement. It exists so that any change to washout fails the test and has to
be explained. Its failure message still states the distance from each
published mean. Until `PL-RXW0`, the pin was one published SD wide, which is a
band of 6% to 12% relative. The test does make three claims about
elimination, and the model meets all three. They are the published ordering by
solubility (desflurane leaves fastest, then sevoflurane, then isoflurane),
independence from the delivered fraction, and the sign of the departure.
<!-- not-restated: 6 % -->

**Most of that departure is the breathing system, not the tissue return**,
and the difference is a property of the two ratios rather than of the model's
physiology. $`F_A/F_I`$ has the inspired fraction in its denominator. So
whatever a breathing system does to $`F_I`$ divides out of the ratio. That is
why the wash-in comparison is inside the published spread at every supported
flow. $`F_A/F_{A0}`$ has no such term. It is the alveolar fraction divided by
its own value five minutes earlier. So agent that returns to the alveoli *from
the circuit* is counted exactly as though it had come back out of the patient.
This model always rebreathes. "Model boundary" gives it one circuit, which is
a closed recirculating path except for fresh-gas inflow and exhaust, and
inspired gas *is* circuit gas. So during an elimination $`F_I`$ settles near
$`\dot V_A/(\dot V_A + \dot V_F)`$ of $`F_A`$. That fraction is 0.29 at the
highest supported flow, and it was measured at 0.30 to 0.32 at five minutes.
The published protocols did not rebreathe. This is an inference and is
recorded as one. Neither abstract states the breathing system. But both report
mixed expired concentrations and agent recovered against agent taken up.
Neither quantity can be obtained without collecting the whole expirate rather
than returning it to the subject. Their elimination therefore ran at an
inspired fraction at or near zero. This model cannot be set to that fraction
at any supported flow. Confirming the inference against the methods sections
needs full texts that are not in PubMed Central and are not held in
`docs/references/`.

**The open-circuit diagnostic, and why its numbers are not this simulator's.**
`tests/reference/test_published_wash_in_and_elimination.py` can run the same
five minutes with the rebreathing taken away. After each step of the
elimination, it discards whatever the patient exhaled into the circuit and
records it as exhausted agent. That is what collecting the whole expirate
does. This keeps $`F_I`$ at zero to within one step of refilling. The
remaining $`F_I`$ is at most $`\dot V_A \Delta t / V_C`$ of $`F_A`$ at the
start of the step, or 1.1 × 10⁻³ at the shipped ventilation, step and circuit
volume. The same run settles at 0.30 to 0.32 with rebreathing. **It is a
test-only driver. No fresh gas flow, dial position or patient setting of the
shipped simulator produces the condition it creates.** `PL-W21J` weighed a
supported non-rebreathing mode against the driver. The project owner chose the
driver on 2026-09-06, because a mode would change the model boundary rather
than a fixture, and it would add one more thing that the interface would have
to make visible. Nobody running the application sees the numbers below. A restatement
of them that drops this warning says something about the shipped model that is
not true of it. The numbers were measured on 2026-09-07:
<!-- not-restated: 1.1 -->

| Agent | Cohort | Shipped | Open circuit | Published |
| --- | --- | --- | --- | --- |
| Sevoflurane | n=7 | +3.79 SD | 0.1541, −0.15 SD | 0.157 ± 0.020 |
| Isoflurane | n=7 | +4.15 SD | 0.2388, +0.66 SD | 0.223 ± 0.024 |
| Desflurane | n=8 | +1.13 SD | 0.0935, −2.33 SD | 0.14 ± 0.02 |
| Isoflurane | n=8 | +5.13 SD | 0.2388, +0.94 SD | 0.22 ± 0.02 |

**Three of the four cohorts land inside the published spread once the
apparatus is gone, and desflurane misses on the other side.** For sevoflurane,
and for isoflurane in both cohorts, the rebreathing circuit accounts for the
whole of a gap 3.8 to 5.1 published standard deviations wide. So this model's
vessel-rich return does reproduce a human elimination once the breathing
systems are matched. No comparison in this repository could say that before.
For desflurane, the circuit over-accounts for the gap. The model crosses its
published mean and settles 2.33 SD below it. It washes out *faster* than the
volunteers did rather than more slowly. That residual is a disagreement about
tissue return, with the circuit no longer available to explain it.
§ "Desflurane's residual" below says what the residual is not, and what is
left of it. The test asserts the movement itself, 3.5 to 4.2 SD per cohort,
rather than recording it. So the attribution in the paragraph above cannot go
stale in silence. The test also asserts the driver's residual $`F_I`$, the
model's own conservation identity across the discards, and the flow
independence that the diagnostic gives. Across the whole supported flow range,
the open-circuit elimination moves by 4 × 10⁻⁶ published SD. The shipped
elimination moves by 11.5 to 21.6 SD between 1 and 10 L/min.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

Neither condition validates the elimination a user watches, and no test claims
that it does. The elimination this simulator runs is the rebreathing one. What
is asserted about it is the regression pin above.

#### Desflurane's residual, and why the parameter file was not changed

The obvious explanation for that residual is that desflurane's vessel-rich
coefficient is too low. The sensitivity measured under § "Parameter provenance"
shows that the five-minute ratio mostly measures the vessel-rich tissue:gas
coefficient and barely measures the blood:gas coefficient. A tissue group with
too little capacity empties too fast. That explanation is arithmetically right
and physically wrong, and this section records the difference.

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

**What rules the change out is the tissue measurement, not this model.** The
measured column above comes from Yasuda's study of human tissue. The same
group published it three years before its pair of kinetic studies:

- Yasuda N, Targ AG, Eger EI 2nd. *Solubility of I-653, sevoflurane,
  isoflurane, and halothane in human tissues.* Anesth Analg 1989;69(3):370-3.
  PMID 2774233. Brain:blood, mean ± SD: I-653 (desflurane) 1.29 ± 0.05,
  isoflurane 1.57 ± 0.10, sevoflurane 1.70 ± 0.09, halothane 1.94 ± 0.17.
  Read from the abstract and checked against PubMed on 2026-09-08.

<!-- not-restated: 0.05 -->

Two of the three demanded values agree with that measurement. Desflurane's
demanded value is nineteen standard deviations above its own measured value.
It is also above what either other agent demands. Adopting it would make
desflurane the *most* tissue-soluble of the three agents. That would invert
the ordering that the source paper was written to report. The stored Gas Man
coefficients match that paper's brain:blood values to within 3%: 1.692
against 1.70, 1.615 against 1.57, and 1.286 against 1.29. So this is not a
case of a reference implementation that has drifted from the primary
literature, and there is no better value to move to.
`test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
asserts the contrapositive. Given any vessel-rich coefficient that the
published human tissue data support, desflurane's elimination still misses on
the same side.

| Coefficient given | $`F_A/F_{A0}`$ at 5 min | Against 0.14 ± 0.02 |
| --- | --- | --- |
| 1.286, shipped | 0.0935 | −2.33 SD |
| 1.39, its own measured mean + 2 SD | 0.0998 | −2.01 SD |
| 1.70, sevoflurane's, the highest of the three | 0.1167 | −1.17 SD |

**Nine other candidates were tested or struck, and each fails the same way.**
Either it moves sevoflurane and isoflurane as much as desflurane or more,
which the published rows have no room for, or it moves desflurane the wrong
way. Rows one to six were measured on 2026-09-08. Rows four to six were
measured on an independent forward-Euler integration of these equations. That
integration reproduces the shipped driver to within 0.8%. Its own zero-shunt
baseline for desflurane is −2.29 SD rather than −2.33. The seventh row was
measured on 2026-09-13 on the shipped driver, after the methods sections
supplied the apparatus's real volume (`PL-RFLN`). The paragraphs below it
explain why it is a row of its own rather than a correction to the sixth. The
eighth and ninth rows were not measured here at all. A primary measurement
that the project has on file rules out each of them outright. A block below
gives, for each, what it proposed and what ruled it out.

| Candidate | What reaching 0.140 takes | What it costs the other rows |
| --- | --- | --- |
| Blood:gas too low | ×1.63, to 0.687 | 10.9 SD above Eger 1987's measured 0.424 ± 0.024, and the wash-in row falls to −4.35 SD |
| Alveolar ventilation too high | between 2.5 and 3.0 L/min | at 3.0, sevoflurane +2.1 and isoflurane +2.7 SD, and all three wash-in rows at −2.0 SD |
| Cardiac output | out of reach | 3 to 7 L/min moves desflurane only from −2.6 to −2.1 SD |
| Fast capacity this model omits — lung tissue, pulmonary and arterial blood | about 3 L of blood-equivalent | worth 20.1% of desflurane's fast pool against 19.7% of sevoflurane's and 23.4% of isoflurane's: flat, where desflurane needs +2.41 gas-equivalent litres and isoflurane −1.32 |
| A non-ideal lung — shunt or ventilation-perfusion dispersion, both excluded by $`F_a \equiv F_A`$ | moves the wrong way | a 20% shunt takes desflurane from −2.29 to −2.66 SD; a log-normal V/Q distribution at log SD 1.0 takes it to −2.91 |
| Circuit-style rebreathing in the published apparatus, at an assumed ratio | $`F_I/F_A`$ = 0.30 | sevoflurane +2.72 SD, isoflurane +3.29 and +4.10 |
| The published apparatus's own dead space, sourced — 50 ml re-inspired each breath, which in this model is a ventilation decrement rather than an $`F_I`$ | more than the wash-in rows will bear | at the largest admissible decrement desflurane is still −1.48 SD while both isoflurane cohorts leave their spread, at +1.69 and +2.17 |
| End-tidal sampling bias in a lung with ventilation-perfusion dispersion — a correction to the *published* value rather than to this model | a bias upward at both ends, growing as solubility falls | the one human measurement of that gradient has it larger for *more* soluble agents and negative through an elimination, so it moves the published value down and deepens the residual — struck below |
| Circuit-wall absorption — this model's circle system has inert walls, and a real one's plastic and rubber dissolve agent | nothing it can supply: walls that absorb during administration give the agent back through the washout, holding $`F_I`$ up | the one study to measure a real circle system found desflurane's washin and washout lay close to the ideal exponential at every flow, so the inert wall is the assumption it most nearly supports for this agent — struck below |

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

**Run correctly, it fails the way the second row fails. That is no
coincidence, because it *is* the second row, at a sourced magnitude.** The
model has no respiratory rate, so the table runs the decrement across the
conventional range of rates for a paralysed, normocapnic adult. It was
measured on 2026-09-13. For comparison, with no dead space at all, desflurane
sits at −2.33 SD:

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

**Whether any decrement is owed at all is undetermined. That is the question
still open, not the one the table above answered.** Yasuda derived the
alveolar fraction of ventilation from $`F_M = f_A F_A + f_D F_I`$. The 1-l
mixing chamber that supplies $`F_M`$ sits beyond the nonrebreathing valve.
So the 50 ml that is re-inspired never reaches the chamber, and their derived
$`f_A`$ is
$`(V_T - V_{D,\text{anat}} - V_{D,\text{app}})/V_T`$. That value already
nets the apparatus out. A comparison run at *their* alveolar ventilation must
therefore not subtract it again. This model runs at 4.0 L/min.
`data/patients/reference_adult.json` records that value as a program default
with no primary source behind it, and it is neither quantity.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

**Both papers have since been read at full text, and the study publishes no
ventilation at all** (`PL-ZDWL`, supplied by the project owner and read
2026-09-13). Ventilation was titrated for each subject to normocapnia, an
end-tidal carbon dioxide of 5.5–6.5%, rather than set to a fixed figure.
Minute ventilation was measured and used in the mass balance. Even so, **no
$`\dot V_E`$ and no $`f_A`$ is reported in either paper**, and neither paper
has a ventilation table. The *Anesthesiology* paper does settle one thing, in
its description of the total-body-clearance method. It gives the definition
that the derivation above needs. Doses delivered to the alveoli are computed
as $`F_I \dot V_A \times 30`$ min "where
$`\dot V_A = f_A \dot V_E`$". So $`f_A`$ is the alveolar fraction of *total*
minute ventilation.

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
a tissue:blood ratio of 1.2, and 1.8 L of pulmonary and arterial blood. They
were used to size the term and are not proposed as parameters. None of them is
a stored value, and none should be treated as one. What the row establishes
does not depend on their precision. Any capacity that scales with blood
solubility is worth the same *fraction* of every agent's fast pool. Adding it
therefore moves all three rows together, and it cannot produce a residual in
one of them.

**So the cause is not identified. This is a recorded disagreement, and what is
recorded is its sign and its size.** Once the candidates above are ruled out,
what remains must be a mechanism that acts on the least soluble agent alone
and keeps its alveolar fraction high. **One candidate remains, and this
project cannot test it:**

1. *The published value.* Desflurane's recovery, the agent recovered divided
   by the agent taken up, was 105 ± 25% in those eight volunteers. Isoflurane,
   measured in the same sitting, had 102 ± 13%. Desflurane's figure has the
   wider spread of the two, and it is centred above complete recovery.

**End-tidal sampling was the second candidate, and it is struck** (project
owner, 2026-09-13). It is recorded here rather than deleted because it was the
leading explanation for a week. A reader who meets the eighth table row
deserves to know why it was struck.

*What it proposed.* The published $`F_A`$ is end-tidal gas from an
anaesthetized volunteer. This model's $`F_A`$ is the fraction in one perfectly
mixed compartment. In a lung with ventilation-perfusion dispersion, a unit
with ventilation-perfusion ratio $`r`$ sits at
$`P_A/P_{\bar v} = \lambda_{b:g}/(\lambda_{b:g} + r)`$ through an elimination.
So the last units to empty carry the highest partial pressure during washout
and the lowest during wash-in. A ratio of the two would then be biased upward
at both ends, by an amount that grows as solubility falls. Consider a
log-normal perfusion distribution at log SD 1.0 with a 5% shunt. On that
distribution, the arterial retention that this model fixes at
$`\lambda_{b:g}/(\lambda_{b:g} + \dot V_A/Q)`$ is understated by 44% for
desflurane, 30% for sevoflurane and 15% for isoflurane. That is the same rank
order as the residuals, which is what made the hypothesis attractive.
<!-- not-restated: 5 % -->

*What the methods sections settled, and it was in its favour.* The fifth table
row rules out the reading in which the published value is a **flow-weighted**
alveolar fraction. So the hypothesis rested entirely on the published $`F_A`$
being an end-tidal sample instead. The "Materials and Methods" section of
Yasuda 1991 *Anesthesiology* places that sampling port **at the tracheal
tube**. The 50 ml of Teflon that the seventh row analyses is interposed to
protect the sample from inspired gas. The paper samples mixed expired gas
**separately**, from the 1-l mixing chamber, and reports it as $`F_M`$. So the
quantity that the fifth row excludes is $`F_M`$, not $`F_A`$, and the obstacle
was removed.

*What struck it.* The one primary human measurement of that gradient
disagrees with the hypothesis on both counts. Yasuda's own discussion flags the
assumption "that the $`F_A`$ accurately indicates the anesthetic partial
pressures in arterial blood". It cites Carpenter RL, Eger EI II,
*Alveolar-to-arterial-to-venous anesthetic partial pressure differences in
humans*, Anesthesiology 1989;70(4):630–5, PMID 2930000. That study sampled
arterial blood, end-tidal gas and inspired gas simultaneously in eight surgical
patients (supplied by the project owner and read 2026-09-13).

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

*Two things that would reopen it, neither sufficient to keep it open.* First,
Carpenter's regression was fitted over positive $`P_I - P_a`$ only, never at
$`F_I = 0`$. Applying it to an elimination therefore extrapolates the
mechanism, not the fitted line. Second, his patients were 52 ± 16 years old,
against Yasuda's 25 ± 5, and physiologic dead space depends on age. Both
points would have to resolve in the hypothesis's favour. The measured
solubility ordering would also have to reverse, and no argument here proposes
that. Yasuda's 50 ml guard does not settle the question either. It protects
against contamination from the **apparatus**, whereas Carpenter's 20% is
physiologic dead space inside the patient.

*One consequence worth stating plainly.* If the sampling bias is real and has
the measured sign, the published 0.140 is **low**. So every interpretation of
this section that treats the model as washing desflurane out too fast is
conservative rather than optimistic.

**Circuit-wall absorption was never on this list, and the paper behind the
circuit volume decides it** (`PL-XWCY`). Targ, Yasuda and Eger measured washin
at 0.5–2 L/min and washout at 1–5 L/min in a real conventional circle system.
They compared both against the ideal exponential (*Anesth Analg* 1989
Aug;69(2):218–25, PMID 2764290, read at full text 2026-09-13). The same study
is behind the circuit volume's provenance and the inert-circuit entry under
§ "Known limitations". Desflurane's curves lay close to the ideal line at every
flow. They deviated most at the lowest flows and near complete washin, and
none of those conditions is this model's operating point. The authors conclude
that absorption of desflurane "by circuit components or soda lime should not
hinder induction of or recovery from anesthesia". So for **desflurane**, the
model's inert circuit is the assumption that this measurement most nearly
supports. The candidate is struck on evidence rather than on argument.
<!-- not-restated: 5 L/min -->

**The direction rules it out independently, and that half needed no
measurement.** A wall that dissolves agent during a 30-minute administration
gives the agent back during the washout. That keeps the circuit fraction high,
and therefore the inspired fraction too, which *slows* the alveolar fall.
Desflurane's residual is this model washing out too **fast**. A mechanism that
can only slow a washout cannot produce that residual. So no amount of wall
absorption would have helped, whatever the measurement had said. This model
has no wall term, so a test cannot vary one. The circuit volume is the one
circuit-side store it has, and
`test_a_larger_circuit_can_only_slow_the_elimination` pins the direction on
it (`PL-P1P6`). For every agent, the five-minute $`F_A/F_{A0}`$ rises at each
step from half to twice the stored circuit volume.

**The same study finds that a real circuit measurably retards sevoflurane and
isoflurane. That is a limitation of this simulator, but it is not a candidate
here, for three separate reasons, any one of which is sufficient.** The
finding is real. The partition coefficients of the circuit components rank
halothane > isoflurane > sevoflurane > desflurane at every equilibration time
from 7.5 min to 9 weeks. The washin and washout curves follow the same order.
But the finding does not bear on the residual.

- **It is already recorded, in the right place.** "Known limitations" contains
  the coefficient table and the ranking. It also states that the inert circuit
  is most nearly true for desflurane and least true for halothane, and it
  records the decision not to add a wall term (`PL-LS3H`). Repeating it here
  would suggest to a reader of this section that the residual is partly
  explained, which is the opposite of the truth.
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
  means, not toward them. This is the same directional argument that strikes
  the candidate for desflurane, applied to the two agents for which wall
  absorption is strongest. The published cohorts also breathed from a
  non-rebreathing apparatus, in which the potent agents' inspired fraction is
  zero by construction. So no circle-system wall effect is present in the
  published number at all.

<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

The general form of that last point is worth keeping. **A mechanism that
belongs to this model's circle system cannot explain a disagreement with a
measurement made without one.** Such a mechanism can only be a statement about
what the simulator shows a learner, and "Known limitations" is the place for
that kind of statement.

Whatever the explanation is, it has to fit the whole published set and not
desflurane alone. The same eight volunteers gave a halothane ratio of
0.25 ± 0.02. Halothane's blood:gas coefficient is conventionally about 2.4.
That is a textbook figure, not a parameter this project stores. So across a
roughly six-fold range of solubility, the published five-minute ratios span
only 0.14 to 0.25. That spread is narrower than a perfusion-limited model
produces.
<!-- not-restated: 2.4 -->

**What is still missing, now that the methods sections have been read.** This
section used to name three things that would settle the question. They were
the breathing system, how end-tidal gas was sampled, and the alveolar
ventilation measured during elimination. Two of them are answered, and one was
outstanding. The breathing system and the end-tidal sampling are recorded
above, and they settled the apparatus question. The published circuit is
non-rebreathing, and the potent agents' inspired fraction in it is zero by
construction. Its 50 ml of series dead space cannot account for the residual.
The third has now been looked up, and the answer is negative. `PL-ZDWL` read
both papers in full text on 2026-09-13, and **neither publishes a ventilation
at all**, as the paragraphs above record. Ventilation was titrated in each
subject to normocapnia rather than set to a figure, and neither paper reports
a $`\dot V_E`$ or an $`f_A`$. So there is no published value at which to run
the comparison, and that avenue is closed rather than outstanding.

So one candidate is left, and this project cannot test it. That candidate is
the published value itself, and no measurement available here will settle it.
The end-tidal-weighted bias that was listed beside it was struck on the same
day (`PL-03ZG`, dropped for that reason). Circuit-wall absorption was struck
with it, as recorded above. **Neither the remaining candidate nor any struck
one is a claim this specification makes.** The cause of the residual is not
identified. What this section records is its sign, its size, and the nine
candidates in the table above, with what ruled each of them out.

**Which question a band of one standard deviation addresses.** This matters
because this section now makes the one-SD claim in two places. A deterministic model compared against a
cohort *mean* would conventionally be judged against the standard error of
that mean, $`\text{SD}/\sqrt{n}`$. For these cohorts that band is 2.6 to 2.8
times narrower. The claim made here is deliberately the weaker one. It says
that the model is a **plausible individual** drawn from the published cohort,
not that it reproduces the cohort's mean. The distinction matters in practice.
Desflurane's wash-in sits at +0.79 SD, which is +2.2 SEM. So the same run that
passes the claim this document makes would fail the claim it does not make. A
reader who restates a passing wash-in as "reproduces the published mean" has
claimed something that no test here has tested.

**Four caveats limit how strongly a pass may be stated.** The first two apply
to both directions. The last two apply only to the elimination comparison. All
four belong beside any statement of this result, wherever it is restated. The
root README used to carry such a statement, and the README no longer exists
(`PL-WB5K`). So the obligation passes to whatever `PL-N092` writes in its
place.

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
4. *This model has no metabolism, and it has nothing on the scale of the
   fourth compartment that human washout needs. Five minutes is within what
   both omissions allow.* Over five minutes of elimination, metabolism is
   negligible for all three shipped agents, and the papers bound it
   themselves. They report recovery, which is the agent recovered during
   elimination divided by the agent taken up. Recovery was 101 ± 7% for
   sevoflurane and 101 ± 6% for isoflurane in the first study. It was
   105 ± 25% for desflurane and 102 ± 13% for isoflurane in the second.
   Halothane gave 64 ± 9%, which is the same method detecting a metabolized
   agent. Both papers also report elimination curves over several days, and
   those must not be added to this comparison. Over days the missing
   metabolism is no longer negligible. Neither is the fat group's flow, which
   acts on the slow tail of washout either way (`PL-HBH2`). § "Known
   limitations" weighs that flow against two human sources that disagree about
   its direction. The flow is about twice a resting depot measurement, and at
   or a little below what the same papers' washout fits imply. The measured
   tail leaves what this model can follow long before days, though, and within
   the 24 hours for which a run is supported (`PL-YD2V`). Every washout these
   papers fitted needed a fourth compartment between muscle and fat, and this
   model has no counterpart for it. On the published mean coefficients, that
   compartment's term becomes the largest in the measured curve at about 1.8
   to 3.1 hours after the 30-minute administration. It stays the largest until
   about 20.7 to 29.4 hours (the intertissue-diffusion note under § "Known
   limitations"). At five minutes that term is about one part in twenty of
   what remains. From about the third hour it is the largest term there is. A
   comparison carried into those hours would measure an omission rather than a
   parameter. So the gap over those hours is measured beside this gate rather
   than gated by it. § "The first 24 hours of elimination against the
   published mean curves" records its size and direction hour by hour
   (`PL-KK1Q`), and asserts no agreement.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

<!-- not-restated: 6 % -->

#### The early wash-in curve against the published figures

**The first 25 minutes are compared too, point by point** (`PL-R0NL`,
2026-10-18). Until then the 30-minute ratio was the only wash-in comparison,
and that ratio barely registers the lung's gas volume or the circuit. Both
papers plot the whole $`F_A/F_I`$ curve during administration as Figure 2.
They plot it as mean ± SD, with each SD drawn on one side of the marker.
Neither paper tabulates it. So the values were read from the page scans, and
`docs/references/yasuda-1991-figure-2-wash-in.md` records the method and every
value read. When the 30-minute points are read the same way, each lands within
0.006 of the value stated in the text. That is the size of a reading error
here.

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

**No single stored coefficient, moved within what was measured, closes the
gap** (`PL-CM1B`, measured 2026-10-18). Each desflurane coefficient was moved
alone through the reference test's own harness, with every other value left as
shipped:

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
residual (`PL-RFLN`). At 0.57 the open-circuit 5-minute ratio moves from
−2.33 SD to −1.97 SD. So the two findings do not share this cause in any
useful sense. Nothing stored changes, and the disagreement is a known
limitation. The five desflurane points and the isoflurane point at 12.5
minutes are checked against a regression band from −1 to +2.5 SD instead of
the agreement band. That way the gap cannot grow without being noticed. A
primary-literature coefficient set, `ROADMAP.md`'s planned-milestone item 31,
is where this would be weighed again.

Caveat 1 above applies here too, and the early curve is where a second-gas
effect would show first. Its size is not measured. The volunteers had breathed
70% nitrous oxide for 30 minutes before the potent agents started, and 65%
throughout. So their nitrous oxide uptake was already small by then, and the
effect is probably small too. This model has no second-gas effect. Three of
the 1-minute SDs are stand-ins. Those error bars are lost among overlapping
marks near the axis, so each cohort's next readable bar is used instead, as
the note says.

#### What the published-data gate can and cannot resolve

**A green gate shows only that no stored value is wrong by more than the gate
can detect, and for most stored values that is a lot** (`PL-9YHR`,
2026-10-17, and re-measured for `PL-R0NL` on 2026-10-18). The published-data
gate is the set of assertions whose expected value is a published human
measurement rather than this model's own output. The gate contains the early
wash-in points from 1 to 25 minutes, which are run with F_I held at the
airway. It also contains the 30-minute wash-in band for each cohort at every
fresh gas flow from 1 to 10 L/min, the sign of the elimination disagreement
for each cohort, and both solubility orderings.
§ "The early wash-in curve against the published figures" above describes
the early points. The regression pins are not part of the gate. The pins
include the 5-minute elimination pin above, `PINNED_REFERENCE_STATES` in
`tests/reference/test_coupled_dynamics.py` and the late-washout tables. A
pin fails on any change at all. It detects an accidental edit. It says
nothing about whether a published value would have caught a wrong one. So no
pin may be cited as validation of a stored value.
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
product, which is the tissue's capacity. This was measured, not assumed. The
search found the same edges for both. Before the early points joined the
gate, the same search on 2026-10-17 put blood:gas at −14% / +5% for
sevoflurane, −11% / +12% for isoflurane and −3% / +10% for desflurane. It
put the vessel-rich group at −22% to −46% below and +24% to +55% above.
`PL-9YHR` records that table.
<!-- not-restated: 5 % -->

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
  published SD (`PL-CM1B`).
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

Wash-in at 30 minutes is a blood:gas measurement that barely sees the
vessel-rich group. Elimination at five minutes is a vessel-rich measurement
that barely sees blood:gas. This does not compete with the rebreathing
explanation above. The circuit sets *where* the elimination ratio sits
against the published mean, as an offset fixed by the operating point. Among
the model's own parameters, vessel-rich solubility is the one that the ratio
moves with. This section is also the only place that records the size and
sign of this model's departure from a *measured* human washout. Its departure
from the fitted mean curves over the rest of the day is in
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

#### The first 24 hours of elimination against the published mean curves
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**A measurement recorded beside the gate above, not a second gate** (`PL-KK1Q`,
2026-09-27). Caveat 4 refuses to carry the five-minute comparison into the
papers' multi-day curves. The reason is that over those hours the measured
washout is carried by a compartment that this model does not have. So a
comparison there measures an omission rather than a parameter. That refusal
still applies. This
subsection adds the size of the omission, the hour from which it appears and
the direction in which it points. With these, the intertissue-diffusion note
under § "Known limitations" and § "Supported run length" can give a number
where before they could give only a direction. Every assertion in
`tests/reference/test_late_washout_against_published_fits.py` is one of three
kinds. It may be a regression band around what the test measured, on
2026-09-27, or on 2026-10-03 for the muscle group's variation and the open
circuit's modes below. It may be the reading that such a band supports. Or
it may be a property of the published coefficients. None asserts agreement
with a human washout, and none may be restated as one.

**What is compared, and under what conditions.** Both papers fit each
volunteer's elimination to a sum of five exponentials,
$`F_A/F_{A0} = \sum_i A_i e^{-t/\tau_i}`$. Each paper publishes the mean and
SD of every coefficient in its Tables 1 and 2. These were read at the source
on 2026-09-27: *Anesth Analg* p. 321 through the private corpus's text layer,
and *Anesthesiology* pp. 494-95 as page images. The curve built from the mean
coefficients is compared as published, un-normalised. Its amplitudes sum to
0.912 to 0.937 rather than 1 at discontinuation, because they are means of
per-subject fits. Normalising them would raise every fitted value by 7 to
10%, and lower every ratio below by 7 to 10%
(`test_the_published_coefficients_sum_below_one_at_discontinuation`). The
model runs the gate's own protocol. That protocol is the shipped 30-minute
wash-in at the reference operating point, followed by closing the vaporizer.
The model runs it at the shipped 0.1 s step, sampled once a minute. The
elimination lasts 23.5 hours, so the 30 minutes of wash-in and the
elimination together end at the supported run length of 24 hours
(`test_the_run_ends_at_the_supported_run_length`). Until 2026-10-17 the
elimination lasted 24 hours, and the run went 30 minutes past that length
(`PL-RXW0`). The run's fifth minute must match the gate's pinned five-minute
ratios to four decimal places
(`test_the_twenty_four_hour_run_opens_from_the_five_minute_gate_s_own_ratio`).
So the tables continue the gate's comparison rather than starting a second
protocol. There are two conditions, exactly the gate's two. The first is
*shipped*, the rebreathing circuit at 10 L/min, which gives the tail that the
chart draws. The second is *open circuit*, the test-only driver that discards
the circuit's contents after every step. No setting of the shipped simulator
can produce the open circuit. The stated times are the papers' own sampling
times within the first day (*Anesth Analg* p. 317), where the fit passes near
a measured sample rather than interpolating. To these times is added
1410 min, the run's last minute.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
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
term does. That is what puts the peak of model over fit in hours 2 to 4. In
the open circuit, this peak is the tail's closest approach to the curve. In
the shipped condition, it is the tail's furthest excess over the curve. A
fitted time constant is an apparent one, read off the whole curve. So the
model's terms are read off its curve in the same way. They are the modes of
its open-circuit system, decomposed from its state at discontinuation
(`PL-921Y`, 2026-10-03). The open-circuit system is the five equations of
§ "Governing equations" with nothing inspired. The table gives each term as
its time constant in minutes and its amplitude in percent of $`F_{A0}`$, with
the cohorts in the same order as the tables above.
`test_the_model_s_apparent_muscle_and_fat_terms_against_the_fitted_ones`
checks the model's terms to within 0.2%:

| Term | Sevoflurane | Isoflurane | Desflurane | Isoflurane (second study) |
| --- | ---: | ---: | ---: | ---: |
| Muscle, model | 155 min, 2.37% | 161 min, 4.31% | 92.6 min, 2.47% | 161 min, 4.31% |
| Muscle, fitted | 81.7 min, 4.60% | 85.0 min, 7.19% | 48.9 min, 4.86% | 80.0 min, 5.93% |
| Fat, model | 2650 min, 0.060% | 2860 min, 0.12% | 1540 min, 0.063% | 2860 min, 0.12% |
| Fat, fitted | 2230 min, 0.028% | 2310 min, 0.072% | 1350 min, 0.031% | 2110 min, 0.080% |

So the model's muscle term is 1.89 to 2.02 times as slow as the fitted one,
and 0.51 to 0.73 times as large. Its fat term is 1.14 to 1.36 times as slow
and 1.5 to 2.1 times as large. The fitted fat amplitudes in that comparison
have SDs that are 53 to 94% of their means. The modes match the
stepped open-circuit run to within 0.08% at every minute from the fifth. The
run lies above the modes by the amount that the driver re-breathes within
each step before it empties the circuit. Each group's isolated time constant
is shorter than its apparent one. The isolated time constant is the tissue
volume times the tissue:gas coefficient, divided by the tissue blood flow
times the blood:gas coefficient. The reference adult has 33 L of muscle
perfused at 0.9 L/min and 14.5 L of fat perfused at 0.3 L/min. On these
values the isolated constants are 135, 127 and 84.7 minutes for muscle, and
about 2500, 2600 and 1500 minutes for fat. The arterial blood that reaches a
group during the washout is not free of agent. The lungs do not exhale all
of the agent in every group's return, and what they do not exhale goes round
again. So a store empties more slowly than its own blood flow alone would
empty it. Before `PL-921Y`, this subsection set the isolated muscle constant
against the fitted constant. Compared that way, the isolated muscle constant
reads 1.5 to 1.7 times as slow, which understates the difference.
<!-- derived: 135 minutes from data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33.0, tissue_groups.muscle.perfusion_fraction = 0.18, default_cardiac_output_l_min = 5 -->
<!-- derived: 135 minutes from data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 127 minutes from data/agents/isoflurane.json tissue_gas_partition_coefficients.muscle = 4.5, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 84.7 minutes from data/agents/desflurane.json tissue_gas_partition_coefficients.muscle = 0.97, blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 2500 minutes from data/patients/reference_adult.json tissue_groups.fat.volume_l = 14.5, tissue_groups.fat.perfusion_fraction = 0.06, default_cardiac_output_l_min = 5 -->
<!-- derived: 2500 minutes from data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34.0, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 2600 minutes from data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70.0, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 1500 minutes from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13.0, blood_gas_partition_coefficient = 0.42 -->
<!-- not-restated: 2.1 -->

The claim that the muscle group's slow return places this peak in hours 2
to 4 was tested by lowering the group's tissue:gas coefficient to 0.58 to
0.67 of its stored value, with everything else as
stored (`PL-95NW`, 2026-10-03). This change makes the group's isolated time
constant equal to the fitted one. It makes the group's apparent time constant
1.09 to 1.28 times the fitted one, which is most of the way to it. Over a
30-minute wash-in the group is far from equilibrium. It takes up agent about
as fast as its blood flow brings it, whatever its capacity. So it contains
only 4 to 10% less agent at discontinuation, and what the change moves is how
fast that store comes back. With the change, in six-hour runs, the
open-circuit peak comes at 0.62 to 1.45 hours rather than 2.17 to 3.92. At
four hours the tail is 0.50, 0.62, 0.24 and 0.70 of the fitted curve, rather
than 0.82, 0.85, 0.58 and 1.04. The shipped peak comes at 0.65 to 1.97 hours
rather than 2.27 to 4.15. The stretch above the curve ends at 1.6, 3.7 and
4.5 hours rather than 6.9, 7.3 and 8.4, and for desflurane it never opens
(`test_the_muscle_group_s_slow_return_places_the_tail_s_rise_in_hours_2_to_4`).
<!-- not-restated: 0.65 -->

The late excess is due to the model's larger and slower fat term, and it is
still growing when the run ends. The ratio rises between minutes 1400 and 1410
in every cohort and in both conditions. It grows because the fitted curve is
still falling on the fourth compartment's time constant, while the model is
already falling on its fat term's.

**Three things bound how sharply any of that may be read.**

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

**Whether the result bears on § "Supported run length": it does not, and the
reasoning is recorded there** so that the number is argued in one place. In
short, the departures measured here come from the missing fourth compartment
and from the fat group's own size. Both are present from the first hour to the
last. The limit of 24 hours is argued against two other omissions growing past
negligible, and these departures are not those two omissions. So shortening
the span would not remove these departures from the tail. Extending the span
would add the late excess, which is still growing at the boundary.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

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
run stepped alongside its definition, and records the figures measured.
`tests/unit/test_resume_at.py` and `tests/integration/test_controller.py` apply
the same comparison in two more cases. One is a system started at a keyframe
and stepped from there. The other is a branch compared against its parent.
Each test records its own figure and the headroom left above it.

Until PL-2FM6, the run also kept one recorded sample per step, and the chart
drew from those samples. This test was what showed that the two records
described one run. The record of samples is gone. The comparison against the
stepped system now carries the claim, because the stepped solver is the
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
during a run without resetting state. They are the playback rate, the chart's
time base, and the choice of which compartment traces are drawn. None of them
appears in the list, because none of them affects model state. No step is
resized. No segment or keyframe of the run definition is added, discarded or
altered. Identical inputs still produce identical results.
"Interface boundary" is where those settings are bounded. The distinction is
worth stating rather than leaving the reader to infer it from the document
in which a control is described. A reader who took the playback rate for a
model input would treat a case played at sixty times real time as a different
run, rather than as the same run watched faster.
"The reproducibility guarantee" exists to rule out that reading.

**"Identical inputs" matters in that paragraph, because the playback rate
decides when an input arrives.** The rate is not a model input,
and it changes nothing about a step. That much is exactly as stated. But the
rate does decide the grid of simulated instants at which a control changed
*during* a run can first act. That grid is `multiplier × 0.1` s wide. So the
same slider moves made at two different rates are not the same inputs, and
they do not produce the same run. Nothing here is stale or resized. The reader
simply has a coarser choice of when an input acts. § "Supported simulation
step" measures this, and `PL-NBWP` is where the claim above was found to be
overstated.

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
rate. So the concentration displayed beside a halt is the height the learner
marked. It is not a value up to a whole burst's worth of simulated time past
that height. If the test ran once per rendered frame instead, the same
bookmark would stop at a different concentration depending on how fast the
case was being played. Nothing on screen would say so. Two branches nominally
taken "at 0.8 ×MAC" would then open from two different states.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**A halt leaves the run paused, and resuming is explicit.** This follows from
the paragraph above rather than being a separate choice. A halt is exact, but
the learner's next action would not be. A setting changed while the run plays
first acts at a tick boundary. Without the pause, "halt at 0.8 ×MAC, then
turn the vaporizer off" would turn the vaporizer off up to 30 simulated
seconds after the value being looked at. The displayed value would be right,
and the action taken from it would be wrong. No step is taken while the run is
paused, and the setters apply unconditionally. So a halt that pauses makes the
pause-change-resume route automatic. A learner does not have to know to use
it.

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

**A MAC target halts on every crossing, in either direction** (project owner,
2026-09-20). A target names a compartment and a height and has no crossing
direction. Consider a case taken up through 0.8 ×MAC and back down through it.
It has reached what the learner marked both times, so it stops both times. The
alternative was to halt once and then require the target to be re-armed. That
was considered and refused. Two targets that look identical in the list would
then behave differently according to which one had already fired. Nothing on
screen would distinguish them, and that is the hidden mode this interface is
built to avoid. Resuming a paused run takes one control, and the learner is
already looking at it.

**The state of a mark is reported as one of six outcomes, not two.** The
distinctions are required rather than stylistic, because each of the last four
outcomes would be mistaken for one of the others.

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
  Two steps are checked again every time the standings are read, against the
  marks as they are at that moment (`PL-1ZQ4`; project owner, 2026-10-17,
  ratified, over keeping MAC targets historical everywhere). The first is the
  step on which a stopped run's clock ends. The run may be paused, halted, or
  at the supported run length, on a trunk or on a branch. A run that stopped
  after a failure does not count, because a failure is not a pause. The second
  is the step on which a branch opened. A branch opens *standing on* that step,
  however far it has run since. That step is where the branch is, rather than
  something its trunk did. So suppose a target is added after the step that
  crossed it. The target then reads reached on the trunk standing on that step
  and on every branch opened there, whichever came first, the target or the
  branch. A run that leaves the step it stood on keeps what that step crossed,
  so the target still reads reached once the run moves on. A run that went
  past the step before the target was added never stood on it with the target
  marked. That run reads the target as still running, as it reads any height
  it did not stop on.
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
what divides them** (project owner, 2026-09-20, ratified, over reusing
"reached" for both kinds). A run's clock only increases, and it never goes
below the instant the run began. So the state of a *time bookmark* is a
position: either ahead of the clock, or at or behind it. No history is needed
to decide it. A *MAC target* names a height, and no clock orders heights. A
compartment may arrive at a height, leave it and arrive again. So the only
thing that can be said of a target is what the run did. Therefore "passed" and
"before this branch opened" apply to time bookmarks and never to targets.
"Reached" applies to targets and never to bookmarks. The remaining three
outcomes apply to both.

**Reporting a passed bookmark as "reached" was measured to be wrong in seven
ways, and it is refused** (`PL-3K9B`, measured 2026-09-20). Suppose a bookmark
is decided from the set of halts alone. Then every instant that the run is at
or behind, but never *stopped on*, would read "still running". That says the
run can still reach the mark. In none of the seven cases could any step make
that true. Four cases involve a branch opening on or at a mark. One involves a
mark added behind a running trunk. One involves a mark removed and re-added.
One involves a branch reset. The word is "passed" rather than "reached"
because the two claims separate as soon as a clock moves backwards. In the
reference simulator, a bookmark is a pause point that fires on the original
pass and on every replay alike (Philip JH, *Workbook for Gas Man®*, Med Man
Simulations, chapter 2, "Using Bookmarks"). So a rewind, or truncating at a
mark and running on, leaves a mark that will stop the learner again. Any
historical claim about that mark has meanwhile been revoked. A positional word
is read again from the clock every time the row is drawn, so it survives a
rewind. A historical word would have to be withdrawn, and failing to withdraw
it is a displayed value going quietly wrong.

### The control-input record

Every change to a runtime control that the model actually runs under is
recorded against the simulated time at which it took effect. The record is kept
with the run and cleared with it. § "The control-input timeline" below says
what the record is for, what it does and does not assert, and why it has the
shape it has. That section sits with the display rules that the rest of the
interface section carries.

#### The run is that record, and every state is derived from it

**What is held.** A run is stored as two things. The first is the settings in
force at each moment: the four controls above, together with the patient and
agent parameters that the equations read. The second is one *keyframe* per
change, which is the state at the instant that change took effect. Nothing else
about the run is stored. The chart's drawing path, described below, keeps
propagators from one frame to the next, but those are operators formed from
these settings, not states. The flows among those settings are stored as they
were set, in liters per minute, for the reason that § "Time" gives.
`core/run_definition.py` is where this lives.

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
fraction of one atmosphere. Both are eleven orders of magnitude below 1e-4,
the smallest difference that the two-decimal percent readout under
§ "Displayed precision" can show. So neither path can change a displayed digit.
§ "The canonical evaluation rule" below states, as a guarantee, which of the
two paths a stored, exported or branched value may be taken from.

**What this is for, measured rather than argued.** Until PL-2FM6, the run
recorded one sample per step. That cost 130.8 bytes per sample, measured over
20 000 samples of a live run. A 30-day case at the fixed 0.1 s step is
25 920 000 samples, or 3.16 GiB. The same case stored as a definition is
1.6 MiB, about two thousand times smaller. That figure assumes a busy ICU day
with 50 setting changes, which over the case gives 1 501 stretches. The second
gain is that the cost of drawing a window no longer depends on how long the run
has been going. A one-hour window at 600 columns costs 10.6 ms on a two-hour
run and 13.0 ms on a thirty-day run. The recorded path cost 62.6 ms at four
hours and 207.7 ms at twelve.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**Where the cost does still move is the number of changes inside the window**,
because each stretch in view needs its own propagator. As measured on the same
thirty-day run, a full-span window at 600 columns cost 14.2 ms with two
changes in view, 231 ms with sixty, and about 1.1 s with six hundred. That
cost was paid on every frame until PL-CNCF. In that regime the columns are
sparser than the changes, and sampling 600 instants is the wrong way to draw
the run in any case. What to draw instead is a question for the interface, not
for the model.

**It now moves on the first frame only.** `RunDefinition.evaluate_anchored`
keeps the propagators that each window uses, so that the next window can use
them. All but three of them cover an interval that the grid fixes. One such
interval is the column spacing, which the time base fixes. The other is each
stretch's offset to its first grid column, which the anchoring fixes. The three
that change are the propagators for the window's two bounds, and the one for
the offset in the stretch where the window opens. That stretch's first grid
column is the first one past the left edge. So a window that follows the run
forms new propagators for its two bounds. It forms the third one on a frame
whose left edge has passed a grid column since the frame before. It also forms
those of any stretch newly in view. A new column spacing forms them all once
more. This was re-measured on 2026-10-04 on a 24-hour run, the longest that
§ "Supported run length" allows, with every setting distinct. The full-span
window at 600 columns has its left edge at the run's opening, which never
moves. On its first frame it costs 13.2 ms, 179 ms and 819 ms with two, sixty
and six hundred changes in view, as it did before. On each frame after that it
costs 6.3 ms, 5.9 ms and 8.3 ms. Only the last window's propagators are kept.
Each is about 3.1 KB, and six hundred of them take 1.8 MiB. So what is kept is
bounded by one window and does not grow with the run. A kept propagator is, bit
for bit, the matrix that forming it again would give. That holds because it is
looked up only by the settings and the interval it was formed from, and those
are everything it is formed from. Which propagators are kept depends on the
window drawn last, but no drawn value can depend on it. So the store is not a
second record of the run, and `state_at` reads none of it.

**What `drawn_window` costs a frame, at the settings the dashboard draws with**
(PL-CNCF, measured 2026-10-04). The dashboard draws every 200 ms
(`RENDER_INTERVAL_S` in `app/dashboard_frame.py`). It draws at most two runs
(`MAX_DISPLAYED_RUNS`). Each run is drawn through one
`SimulationController.drawn_window` call at
`max(150, plot width in pixels + 1)` columns (`chart_columns` in
`app/chart_frame.py`). The table gives the cost of one run's call, before and
after the propagators were kept. The call follows a 15-minute window on a
30-minute run at 1x, and each value is the median of 40 frames:
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

| Changes in view | 150 columns | 1 069 columns | 2 401 columns |
| --- | --- | --- | --- |
| None | 6.6 ms, now 3.9 ms | 12.3 ms, now 10.1 ms | 20.3 ms, now 18.6 ms |
| Ten | 25.0 ms, now 3.5 ms | 28.6 ms, now 9.4 ms | 35.5 ms, now 18.0 ms |
| Sixty | 135 ms, now 3.7 ms | 119 ms, now 9.1 ms | 129 ms, now 18.8 ms |

Three costs are left. The propagators for the two bounds change every frame,
and each takes about 1.4 ms. The third propagator is formed on a frame whose
left edge has passed a grid column. Last, there is one chained product per
column, at about 7 us each. So the column count, not the number of changes in
view, now sets the cost. At 1x, the third propagator is formed on about one
following frame in forty at 150 columns, one in four at 1 069 and one in two at
2 401. From 5x up, the left edge passes a column on nearly every frame at 1 069
columns or more, so nearly every frame forms it. This was re-measured in a
later process whose times ran about a quarter above the table's. With sixty
changes in view at 1 069 columns, one run's call cost 13.0 ms at 20x against
12.0 ms at 1x. At 2 401 columns it cost 23.9 ms against 22.8 ms. Two runs at 2 401
columns therefore take about 40-50 ms of a 200 ms frame. Before the propagators
were kept, sixty changes in view on two runs at 1 069 columns took about
240 ms. That is longer than the frame they were drawn in.
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

**This is the only record.** Until PL-2FM6, a recorded history was kept beside
the definition, and the chart was drawn from that history. The
"Closed-form agreement test" checked that the two agreed. PL-2FM6 deleted the
history. The chart is now drawn from the definition, through
`SimulationController.drawn_window` and `RunDefinition.evaluate_anchored`.
There is no second record in which a divergence could appear. The stepped
system that advances the run still exists, and the agreement test checks the
definition against it.

#### The canonical evaluation rule

**One instant, one answer, whatever route the caller took.** A run's states are
derived rather than recorded, and a derived value can be reached by more than
one sequence of arithmetic. The fixed 0.1 s step used to rule that out, because
it left every caller only the same step width to take. A propagator that is
exact over any horizon removes that limit, and with it that protection. The
rule below replaces the protection.
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

**The program enforces this rule, not the paragraph above.** The display path
returns its states wrapped in `DisplayState`, which is not a state vector. So a
display state cannot be passed where a state vector is expected.
`RunDefinition` also refuses one as an opening state by name. Its error says
which path the value came from, rather than failing on a length mismatch. The
wrapper is deliberately not a subclass of the state tuple. The places that
consume a state and must apply this rule include some that have not been
written yet. A place that does not think to check anything refuses only a value
that is structurally not a state, so a subclass of the state tuple would pass
it.

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

**The headroom differs by four orders between those two columns, which is why
the rule is enforced rather than trusted.** A fraction is displayed as a
two-decimal percent, so "Displayed precision" resolves 1e-4. The measured
difference is eight orders below that. If the fractions were all that a run
held, that margin would make the separation between the two paths academic. The
accumulators are displayed as six decimals of a litre, which resolves 1e-6 L.
The measured difference is less than three orders below that. Three orders is
ample, but it is not fourteen. A display value that reached the mass-balance
readout would be wrong in a place a reader could eventually see. It would also
look exactly like the right answer.
<!-- not-restated: 6 L -->

**What this requires of a branch.** `ROADMAP.md` item 12 asks that a branched
run reproduce its parent element-wise, not merely within a tolerance. This rule
supplies that under one condition and one property of how a branch is built.
Both were measured rather than assumed:

- **A branch opens at a keyframe.** Suppose a branch restarted from the
  canonical state at an instant for which the parent has no keyframe. That
  would replace one propagation over an interval with two propagations over its
  halves, which is a different rounding of the same exact solution. Opening at
  a stretch boundary reproduces the parent bit for bit. The restart was
  measured twice, both times on the run in
  `tests/reference/test_canonical_evaluation.py`, which now checks the second
  measurement. The first found up to 5.3e-13 in an accumulator (2026-09-07).
  The second forked at 1 234.5 s and probed the 141 instants at or past the
  fork. It found 1 109 of the 1 269 state elements differing, worst 7.8e-15 as
  a fraction and 1.9e-12 L on an accumulator (2026-09-21, `PL-Z3W6`). The size
  of the difference depends on where the fork is taken and how far past it a
  reader looks. So these are instances of the divergence, not a bound on it.
  What is bounded is the route the program actually takes, and that bound is
  zero.
- **The branch's run definition opens *at* the fork instant, on the case's own
  axis**, carrying the parent's keyframe. Parent and child then name the same
  case instant. Each forms its propagation interval as that instant minus the
  opening of the segment that holds it. Both start from the identical keyframe
  and use the identical subtraction. So the reproduction follows from how the
  branch is built, not from a caller having performed the right conversion.

Restarting at an instant with no keyframe, which the first condition rules out,
is a defect that a plausible branch implementation would introduce. The second
condition removes a second defect. Until 2026-09-14 (`PL-ZMRT`, project owner),
a branch's definition opened at a zero of its own. The rule here then required
every caller to reach a branch instant by *subtracting* the fork instant from
the case's time, rather than by naming the branch's own elapsed time. That
distinction mattered, because the subtraction does not always round-trip. With
a fork at 900 s, `(900.0 + 1e-6) - 900.0` is 9.999999974752427e-07 and not
1e-6. So a child asked for its own `1e-6` propagated over a different interval
from its parent, and landed one unit in the last place away. The measurement is
still arithmetically true, but it no longer describes a hazard this program can
express. With one time frame, there is no offset for a caller to name and no
conversion to get right.
<!-- not-restated: 900 s -->

**A fork at a bookmark cannot satisfy both, and it is the second that gives
way** (`PL-B8MK`, decided and built 2026-09-20). The two conditions above
coincide for every fork the program takes today. Those forks are taken *at*
control events, and a control event is a keyframe. So "opens at a keyframe" and
"opens at the fork instant" name one instant, and nothing distinguishes them. A
bookmark's instant is not in general a keyframe. On a 120 s run with two
control changes, only 3 of the 1 201 instants where a halt could land are
keyframes. Meeting both conditions there would mean *recording* a keyframe
where the run halts. This project measured that route and refused it. It makes
the branch exact against its parent, but it displaces the parent's own later
results: 48 of 54 elements differ from the same case built without the mark.
Marking a run would then change the run, which `CLAUDE.md`'s determinism
requirement refuses outright.

So a bookmark fork keeps the first condition and relaxes the second to this:
**the branch's run definition opens at the keyframe at or before the fork
instant, on the case's own axis**. Meanwhile the branch's clock and its live
uptake system are at the fork. The element-wise guarantee is untouched, because
it never depended on the definition opening *at* the fork. It depends on parent
and child forming each propagation interval from the *same keyframe* by the
*same subtraction*. Opening at the keyframe where the parent's own segment
opens states that property directly. It does not rely on the special case in
which the two instants coincide. This was measured on 2026-09-14 on a 3 600 s
sevoflurane run with changes at 300 s and 600 s, forked at a bookmark of
655.3 s. Across the nine state entries at six probes out to an hour, 0 of 54
elements differ. The trunk stays byte-identical to the same case built without
the bookmark.

**Returning to a marked instant the run has already passed is that fork taken
late** (`PL-W4XQ`, 2026-10-12). Consider a learner paused at three hours who
marks the one-hour point and goes back to it. The learner is asking for a fork
at an instant for which the run holds no keyframe, and on which the run is not
standing. So neither of the two earlier ways of forking applies. The
construction above needs neither. The state at an instant the run has reached
is the run's definition evaluated there. Standing on a halt only ever named the
fork. So `SimulationController.resumed_at_mark` takes the mark itself and forks
at the step that reached it, using the bookmark fork's construction. Here is
what that reproduces, and what it does not:

- **It reproduces the case's state at the mark, element for element.** The
  branch opens from the canonical state there, inside the parent's own stretch.
  Every later instant is one propagation from the same keyframe that the parent
  propagates from, until the branch's own settings change. Take the run in
  `tests/integration/test_controller.py`, marked at 60 s after its clock
  reached 180 s. The branch agrees with its trunk at all 601 instants from the
  mark to a minute past it.
- **It is the branch the halt would have given.** A mark set before the run
  passed it halts the run, and the run is forked at the halt. The same mark set
  after the clock went past it is forked here. The two branches' whole
  provenance compares equal: stretch, fork state, step count, the step the fork
  ends, and crossing. It also stays that branch for a mark added later. Every
  run asks the step it opened on, or stands on, which marks it crossed. It asks
  against the marks as they are whenever its standings are read. So a mark
  added inside that step is treated the same on the trunk and on the branch,
  whether it was added before the branch or after (`PL-1ZQ4`). Each way of
  forking asks that step in the same way, including a fork at a control event.
  So `resumed_at` at a keyframe the trunk halted on opens on the halt's
  crossing, as `resumed_here` does.
- **It leaves the trunk the case it was.** Nothing is recorded where the mark
  is. That is what kept the bookmark fork from changing the run it marks.
- **It does not open at the typed instant.** The fork is the end of the step
  that reaches the mark, at the mark or one step past it. For a typed 45.3 s at
  the 0.1 s step the fork is at 45.300000000000004 s, and for a typed 45.35 s
  it is at 45.4 s. That is the instant a halt would have stopped on. It is
  found by the crossing rule itself (`TimeBookmark.steps_to_reach`), not by
  rounding the typed value. In the first hour, 12 767 of the 36 001 one-decimal
  instants are not a whole number of steps in binary. Rounding would put a mark
  that lies inside a step onto the step before it. The branch treats its mark
  as passed, not as "before this branch opened", even when the fork is one step
  past the mark, because it opens standing on the step that crossed the mark.
- **It does not replay what the trunk did afterwards.** The branch continues
  under the settings in force at the mark, with a control record of its own
  that starts empty, until the learner changes something. The trunk's later
  changes stay the trunk's. This is how it differs from the reference
  simulator's rewind. That rewind returns to time zero, keeps the recorded
  settings and plays them back as it runs (Philip JH, *Workbook for Gas Man®*,
  Med Man Simulations, appendix E, "Replaying Simulations", printed pages
  186-87, as read and quoted in `PL-W4XQ`). That simulator takes the trunk back
  and truncates it at the mark. Returning to a mark here forks instead (project
  owner, 2026-10-12, ratified, over truncating the run at the mark after a
  confirm, `PL-ZW0J`). The run that happened stays on the axis beside the
  alternative.
- **Its opening readouts are the canonical state's, not the ones the trunk
  showed when it stood there.** A running case displays its stepped live state,
  which is one propagation per step from the opening. Every branch opens from
  the canonical state. Over three hours of the run in the item's measurement
  (2026-10-12), the two agree to 4.9e-14 as a fraction. That is ten orders
  below the 1e-4 that a two-decimal percent can show, so no reader can see the
  difference. The same holds for a fork at a control event or at a halt.

<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

A mark still ahead of the clock is refused rather than reached. The case holds
no state there yet, and a fork there would be a prediction drawn as if it were
a run. The learner reaches such a mark by running on, and the halt there is
then the fork.

**Branching where a paused run stands is the same fork, with the clock naming
the instant** (`PL-Y2SL`, 2026-10-12). The clock always stands on a whole
number of steps. The construction above reproduces the case at any instant the
run has reached. So `SimulationController.resumed_here` forks wherever the
trunk is paused, on a halt or anywhere else. It forks from the canonical state
there, inside the parent's own stretch, and records nothing on the trunk. The
branch opens standing on the crossing made by the step that ends there. That
crossing is asked again of the marks as they are now, as `resumed_at_mark` asks
it. It is not read from a halt's record, which names only what was marked when
the run stopped (`PL-2N43`). Three kinds of run are refused. A running run is
refused, because where it stands moves with every step. A failed run is
refused, because a failure is not a pause. A run at the supported run length is
refused, because it has no step left for a branch to take.

**So nothing is left over to bound, and there is nothing to show a learner**
(`PL-Z3W6`, 2026-09-21). `ROADMAP.md`'s v0.5.0 definition of done asks this
document for "the bound on any divergence that could not be eliminated". On the
canonical path, no such divergence survives. A branch and its parent agree
element for element at every instant they share. That holds for a fork on a
keyframe and for a fork between two keyframes.
`tests/reference/test_canonical_evaluation.py` checks each shape over 207
instants, against a restart at the fork, which does not agree.
`tests/integration/test_controller.py` checks the same over 201, 301 and 601
case instants. It also checks the 240 drawn columns that a trunk and a bookmark
branch share. The two divergences that do exist are named rather than left as a
residue. One is the display path's divergence, tabulated above and refused in
code as a source for anything but a drawn value. The other is the restart's,
which no branch this program builds ever takes. A bound of zero drawn on screen
would tell a learner there is something to watch where there is nothing. That
would be a false signal, not a safeguard.
§ "What a branch comparison asserts, and what it does not" says what the
comparison these two runs are drawn for may and may not claim. This zero is one
clause of that.

**What the relaxation costs is a second job the second condition was doing
silently.** When the definition opens at the fork, `opened_at_s` *is* where the
branch began. `drawn_window` clips its lower bound there, with
`first_s = max(start_s, self._run_definition.opened_at_s)` in
`app/controller.py`. The comment on that line reads
"a branch opens at its fork". Once the definition opens at the earlier
keyframe, that stops being true. The clip would then let a branch be drawn back
across an interval it never lived through, showing the trunk's trajectory under
the branch's identity. That is a presentation failure of the kind the
safety-critical standard names: the right numbers in the wrong patient context.
It is not a cosmetic failure. So a bookmark fork carries the fork instant
explicitly, and the clip is read from it. `ResumePoint.fork` carries it, and
`SimulationController.began_at_s` reads it. `began_at_s` is zero on a trunk and
the fork instant on a branch. It is also what `app/bookmarks.py` is given to
decide that a mark is unreachable. `began_at_s` exists to stop code from
inferring the number from `run_segments[0].opening.instant_s` instead. That
value is where the *definition* opens, which is the instant this relaxation
moves.

**One thing more follows from the relaxation, and it is `reset()`'s.** Reset
keeps the settings and restores the state. Consider a branch that is reset
after its learner has dialled something new. It stands at the fork state under
settings its parent never used. Its definition still opens at the parent's
keyframe under the parent's settings. What the learner has dialled is recorded
as a *change at the fork*. The keyframe that this change opens is the fork's
own state. So the trace starts where the readouts say the branch is standing,
and the parent's stretch stays the parent's.

**Deciding that from the settings instead makes it depend on the order of two
reversible acts**, which is why it is recorded rather than written into the
opening. The two sequences *dial, dial back, reset* and *dial, reset, dial
back* leave one branch: the same settings, the same live state and the same
displayed values. Suppose the definition's opening were chosen at the moment of
the reset. The second sequence would then get the fork rather than the
keyframe. It would restart from two propagations where the parent took one, and
it would silently stop reproducing the parent. Measured on 2026-09-20, 40 of 45
elements differed across five probes, worst 1.21e-15. When the dial is recorded
as a change instead, the dial-back is collapsed by a rule the run definition
already has: a dial moved and moved back before a step ran is collapsed. The
branch is then where it started. After a reset that *kept* the new setting, the
remaining difference is 2.49e-04 on the same probes. That is a second
management rather than a rounding, and this arrangement preserves that
distinction.

**What is not relaxed is the one frame.** The definition still opens at a case
instant on the case's own axis. The clock still continues the parent's. Nothing
converts between frames. So the hazard that `PL-ZMRT` removed, a subtraction on
the caller's side that does not round-trip, does not come back this way. The
only change is that the definition's opening no longer equals the fork instant.
It is earlier than the fork instant, on the same axis.

**One simulated-time frame, and every reader is in it.** A branch's *simulated
time* is the case's time, measured from induction. It continues the parent's
rather than restarting at the fork. This one time is what the clock displays
and what stamps every recorded control change. It is also what rules the
chart's axis, what the supported run length is measured against, and what the
run definition's segments and keyframes are stamped in.
`SimulationController.resumed_at()` opens the branch's definition at the fork
instant. `resumed_here()` and `resumed_at_mark()` open it at the keyframe at or
before the fork instant. All three do so on the case's own axis. `advance()`
and `drawn_window()` pass case time straight through to the definition. Nothing
converts between frames anywhere, because there is only the one frame.

Continuing the case's time is not a presentation preference. Uptake and
distribution are a function of the time since induction. A branch that counted
from zero would therefore place the patient at the wrong point on the uptake
curve, on the clock, the control marks and the axis at once. That is the
correct value shown under the wrong patient context, which `CLAUDE.md`'s
safety-critical standard counts as a failure in its own right. Continuing the
case's time also keeps simulated time to the single multiplication that
§ "Simulated time is a count of steps, not a running total" describes. A
branch's instants are the case's step count times the step. They are not the
fork instant plus a second total. Since `PL-ZMRT` this applies to the run
definition's instants as well as to the clock's. Before `PL-ZMRT` it applied
only to the clock.

**What one frame is worth, measured 2026-09-14.** Two measurements were taken,
on a 120 s sevoflurane run and on the branches taken from it.

The first measurement is the reproduction. A branch was forked at the 60 s
keyframe and advanced 60 s further. It agrees with its parent at all 601 case
instants that the two share. Both are handed the same float, the case's own
`steps × step`, and neither performs any arithmetic on it. A definition opened
at a zero of its own, and asked for its own `steps × step` instead, differs
from the parent at **354 of those 601**. Both are exact solutions of the same
equations. Only the first is the same sequence of floating-point operations,
which is the kind of sameness `ROADMAP.md` item 12 asks for. The old
arrangement could reach the first result too, but only through a subtraction
made by the caller, which the arrangement could not enforce. The current
arrangement cannot express the second result at all.

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
itself** (`PL-B8MK`, measured 2026-09-20 on a 120 s axis at 150 columns). The
fork above lands on the trunk's own columns because a control event is drawn
on every run that has one. A bookmark's instant is not a control event, so the
trunk draws it only if it happens to fall on the grid. The branch always draws
it, because it is the left end of the branch's own clipped range. Everywhere
else, the two traces can still be read against each other. The value at that
one vertex is the case's own state there, which both runs contain. So the
extra column marks the instant at which the two stop being the same run. It
does not mark a disagreement about that instant.

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
8.17e-14 L on an accumulator**. These are eleven and seven orders of magnitude
below the 1e-4 and 1e-6 of § "Displayed precision". A branch forked at the
600 s control event instead differs at none of the columns it shares.

The guarantee above is unaffected, because it rests on `state_at` and not on
`evaluate`. Asked for those same 382 instants canonically, the two runs agree
element for element, with 0 differing. `tests/integration/test_controller.py`
tests that pair on the 45.3 s case above. Across the 240 columns that the two
runs share, 0 of 2 160 canonical elements differ. Of the same 2 160 drawn
elements, 1 909 do differ, worst 2.7e-15, and the fork is the one extra
column. § "The canonical
evaluation rule" is what separates the two paths. This difference is an
instance of that separation rather than an exception to it.
It is recorded here for one reason. A difference trace between two runs would
show a few units in the last place here, where two identical runs should show
zero. A reader who met that without this paragraph would take it for a
disagreement about the case.

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

**The ranges are the model's, not the interface's** (PL-0MLQ). Until v0.2.10
the three flow ranges were declared only as slider limits in
`app/simulation_view.py`, and nothing enforced them.
`AgentUptakeSystem.set_cardiac_output(1000.0)` was accepted and simulated. So
were a fresh gas flow of 500 L/min and an alveolar ventilation of 200 L/min.
The compartment setters checked only that the value was nonnegative and
finite. The sliders were the only thing keeping a run inside the domain that
the verification gates cover. Every other caller of `core/`, such as a
headless run, a notebook or a test, could leave that domain.
`core/supported_ranges.py` now declares the three intervals. It builds each
flow as a type that only its guard produces. So a value outside its range is
refused where the flow is built, before any compartment or settings record can
store it (`PL-0YYV`, below). `app/` never restates the ranges. Its ventilation
and cardiac output sliders import the constants. Its fresh gas flow slider
reads the circuit's accepted range, which is this envelope narrowed by the
range of the mounted machine (§ "The
model's envelope and a machine's deliverable range are two claims", below).
Each of the three sliders steps at 0.1 L/min. A run may open with a
ventilation or cardiac output, as the patient profile states it, that is not
one of those steps. Such a run is refused when the dashboard builds its
controls, as a run with an off-grid opening fresh gas flow is (`PL-96SQ`).
Otherwise the slider would sit on a neighbouring step beside a rounded
readout, and both would show a flow that the run does not have.
`test_an_opening_ventilation_or_cardiac_output_off_the_slider_grid_is_refused`
in `tests/unit/test_dashboard_frame.py` tests this. The shipped patient states
4.0 and 5.0 L/min, so nothing displayed changes.
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

**Refused, not clamped**, for the same reason as the vaporizer maximum. A
silently clamped setting would simulate, display and chart a value that the
user did not ask for. A `SimulationConfigurationError` is raised before
anything changes. So the run in progress stays trustworthy, and the interface
reports the refusal beside the control that caused it. § "Supported
simulation step" above draws the same distinction between a refused argument
and a step that broke down.

**Enforced where a flow is built, not where it is stored or used** (`PL-0YYV`,
closing `PL-HSFV`). This is the opposite of where the step's two bounds sit,
and the reason for it does not apply to the step. A step is an argument to one
call. A compartment advanced alone has no truncation error at any step. So
guarding a compartment at `MAXIMUM_SIMULATION_STEP_S` would refuse an exact
calculation. § "Supported simulation step" argues why the minimum step binds
the run rather than the compartment. A flow, by contrast, is persistent state,
and there are five ways in. The first is an `AgentUptakeSystem` setter. The
second is the setter of the compartment that the flow belongs to. The third is
that compartment's constructor. The fourth is the `UptakeEquationSettings`
record. A `RunDefinition` is built from that record, and records each change
as a new one. The fifth is an assignment straight onto the compartment's
field. `mypy` refuses that assignment in `src/`, but nothing refused it
elsewhere until `PL-LBQY`, below. Until `PL-0YYV` the compartment checked the
first three ways in, and the fourth checked only sign and finiteness. So a
record rebuilt with `dataclasses.replace` to a cardiac output of 1000 L/min,
a hundred times the supported maximum, opened a run. The run returned finite,
plausible fractions (`PL-HSFV`, measured 2026-10-04). Each flow is now a
`float` subclass in `core/supported_ranges.py`: `FreshGasFlow`,
`AlveolarVentilation` and `CardiacOutput`. The constructor of each is the only
thing that runs its guard. In the compartments, the settings record, the application's snapshot and the
setters that feed them, every field and signature that holds a flow takes the
type. The control timeline is annotated `float`, and a setting reopened from it
is built back into its type.
The check is made once, where the value is built, and no way in has to
remember it. A bare `float` handed to any of the five ways in is refused with
a `TypeError` that names the type to build, whatever its value. Arithmetic on
a flow returns a plain `float`, so a derived quantity is never mistaken for a
checked one. This is the shape that `SimulationStep` gives the step. It is
also the first slice of `PL-51B7`, which carries the shape to the remaining
checked quantities.

**An assignment straight onto the field meets the same refusal, at the write**
(`PL-LBQY`; project owner, 2026-10-04, ratified, over frozen compartments, at
45 test rewrites and an `object.__setattr__` on every per-step write, and over
accepting the window, which leaves the Reset path open). `mypy` refuses
`circuit.fresh_gas_flow_l_min = 1000.0` in `src/`. The compartments' own
methods write the field from a checked flow. So a bare `float` reaches the
field only from a caller that `mypy` does not read, such as a notebook, a test
or a value typed `Any`. Until `PL-LBQY`, a bare `float` written that way was caught only
when the next step rebuilt the settings record. By then the snapshot had
copied the value and the readouts had shown it. A paused run showed it for as
long as the run stayed paused. `BreathingCircuit`, `AlveolarCompartment` and
`PatientCompartments` now run the flow's `require_*` in `__setattr__`. So a
write to the flow field is refused with the same `TypeError`, in the same
words, and the field keeps the value it had. The dataclass constructor,
`dataclasses.replace`, a copy and a pickle all write through `__setattr__`. A
copy and a pickle do so because each compartment is a `slots=True` dataclass.
A copy or a pickle restores such a dataclass's state one field at a time
through `__setattr__`, where a `__dict__` would be updated without calling it.
So the constructors run no check of their own. For a flow, the write checks
the type. The fresh gas flow's write also checks the flow against the
machine's range. The circuit's write has done that since `PL-19Y0`, as
described below.

**No compartment stores a blood flow, so none can disagree with the cardiac
output** (`PL-HQF5`). A tissue group's blood flow is its perfusion fraction
times the patient's cardiac output, $`Q_i = f_iQ`$.
`TissueGroup.blood_flow_l_min_at` is the one place where that product is
formed. The venous pool's flow is the cardiac output itself. Each
compartment's `time_constant_s` and `advance()` take the flow as an argument,
as $`\tau_i = V_i\lambda_{i:b}/Q_i`$ does. Until `PL-HQF5` each compartment
stored a flow of its own. Three kinds of write could put that stored flow out
of step with the output. The first was a compartment's own `set_blood_flow`.
The second was a change to a tissue's perfusion fraction. The third was a
change to the output of a copy that shared the original's compartments
(`PL-Z0T3`). Now `set_cardiac_output`, a copy, `dataclasses.replace` and a
pickle move every flow with the output. A copy made at another output leaves
the original's flows unchanged. A new output written straight to the field of
a built patient is still refused, and the refusal names `set_cardiac_output`
(`PL-KFNP`). That refusal once kept the stored flows matched to the output. It
is kept now so that a cardiac output has one way in. Writing the value that
the field already holds is accepted.

**A tissue's perfusion fraction is fixed once the group is built**
(`PL-Z0HN`). The patient checks that its three fractions sum to 1 only when
it is built, so a later change to one fraction would leave flows that no
longer sum to the cardiac output. `TissueGroup` refuses a second write of the
field and says to build a new patient with the new fractions. A tissue group
written onto a built patient is refused unless the fractions, with the
replacement in place, still sum to 1. Copies and pickles write the field once,
onto a new object, so they are accepted. Neither a tissue group nor the patient
lets a field be deleted, because a write after the deletion would bypass both
checks.

`UptakeEquationSettings` still refuses tissue flows that do not sum to the
cardiac output. Only a fraction written past its guard, with
`object.__setattr__`, can now reach that refusal. At the next step, `advance()`
raises it as a `SimulationNumericalError`, as it does for every check that
fails inside a step. Through `SimulationController`, the same refusal comes
before that step begins, as a `SimulationConfigurationError`. The controller
sees that the core's settings no longer match its run definition, and builds
the record to say why before it takes the step (`PL-XRN8`). At Reset,
`SimulationController.reset()` refuses before it clears anything, and the
interface halts the run (`PL-M4M0`). A setting change that the record refuses
is written back, so its compartment, the run's definition and the timeline
keep the previous setting (`PL-VCP4`). No setting
change repairs such a fraction. A new cardiac output scales every tissue flow
by the same factor, so flows that did not sum to the old output do not sum to
the new one. Putting the fractions back, or building a new patient, is the
only repair.

**The alveolar and tissue agent amounts meet the compartment's capacity at
the write, in the same `__setattr__`** (`PL-544D`).
`set_partial_pressure_fraction` takes a `Fraction`, so no setter could store
an amount greater than the capacity. The field itself could store one, though.
`alveoli.agent_amount_l = alveoli.gas_volume_l * 1.0000001` was accepted. The
quotient read from it, a partial pressure above one atmosphere, was refused
only when `SimulationController.snapshot()` built the `Fraction` two layers
later. `PL-7DJK` made that refusal a visible halt. The relation between an
amount and the volume that contains it is for the compartment to check, not
for any one quantity (`.claude/rules/core-domain.md`). So
`AlveolarCompartment` and `TissueGroup` check it where the amount is stored.
They check it for the constructor, the setter and an assignment made past them
alike, in the constructor's own words, and the field keeps the value it had. A
rollback is the one write made past the guard. `restore_state` puts back what
the compartment held when the step began. A rollback that could itself raise
would replace the step's own error. It would also leave the compartments
restored after it still holding the failed step (§ "Step atomicity"). So
suppose a capacity moved under a held amount in the meantime. Since `PL-19Y0`
only a write past the capacity's own guard can cause that. The rollback leaves
that case to the quotient that the snapshot builds from the restored state,
which refuses it visibly (`PL-7DJK`). Until `PL-19Y0` the constructor wrote
the amount before `__post_init__` had refused a bad volume. So the amount's
guard required the volume to be a number, and left a capacity that was not
positive to that later refusal. Now each field is checked by its own write
first, and that stand-in check is gone. No supported setting makes this write.
The hole was the reproduction's own route to a refusing snapshot. The tests
now reach that snapshot by replacing the quotient that the snapshot reads.

**Every checked field of the five run records meets its constructor's checks
at the write** (`PL-19Y0`, on the mechanism `PL-LBQY` gave the flows). Until
`PL-19Y0`, an assignment past the constructor and the setters met only two
checks: the flows' type and the alveolar and tissue amounts' capacity. So on a
sevoflurane run, each of the following was stored, for the snapshot to copy
and the readouts to show: a dial of `Percent(50.0)` against its 8% vaporizer,
a bare-`float` dial, a zero circuit volume, an inspired fraction of 1.5, a
perfusion fraction of 7, a negative tissue volume and a venous amount greater
than its capacity. `BreathingCircuit`, `AlveolarCompartment`, `TissueGroup`,
`VenousBloodCompartment` and `AgentSimulationValidator` now check every field
in `__setattr__`, including the constructor's writes. So none of their
constructors runs a check of its own, and nothing is written when a value is
refused. A relation between two fields is checked by whichever of the two is
written second. The relations checked this way are the dial against the
vaporizer's maximum, the fresh gas flow against the machine's range, the
machine's range against the model's envelope, and each compartment's agent
amount against its capacity. Before the third relation was checked, a range
reassigned on a built circuit to 20 to 30 L/min had left
`accepted_fresh_gas_flow_range_l_min` inverted at 20 to 10 (`PL-HJ7L`). A
volume or partition coefficient now meets the last relation too. A value too
small for the agent that the compartment holds is refused, as
`set_circuit_volume` refuses a circuit volume too small for its agent
(`require_room_for_the_agent_held`, `core/validation.py`). The circuit stores
its agent as a fraction of its volume. So a circuit volume written past
`set_circuit_volume` cannot overfill the circuit, and it is not refused at the
write. Instead the agent moves with the volume, and the circuit gains or loses
agent that no flow carried. The next step then halts on the difference that
the accounting identity finds (§ "Mass-balance identity"), and the step is
rolled back. The venous pool rolls back past its guard, for the same reason
as the alveolar and tissue amounts. The circuit and the validator roll back
through their guards. Those guards cannot refuse a state that
`capture_state()` produced, because nothing that their captured values are
checked against can have moved since.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

**Built from an `int` or a `float` and nothing else, with no sign at zero**
(`PL-LLMN`). Until `PL-LLMN` each guard asked `math.isfinite` and then made
the two comparisons, so it admitted whatever those admit. `True` was a flow of
1 L/min. A `Decimal` was converted and stored. A string was refused in the
words of `isfinite` rather than the simulator's. And `-0.0`, which is inside
every interval, was stored with its sign and displayed as `-0.0 L/min`.
`core/checked_number.py` now states what every checked type is built from.
`FreshGasFlow`, `AlveolarVentilation`, `CardiacOutput`, `Fraction`, `Percent`
and, since `PL-7N8P`, `CaseInstant` all build through it. They accept an
`int` or a `float`, subclasses included, so a NumPy double passes. A `bool`, a
`Decimal` or a string is refused with a `TypeError` that names the value and
its type, before any comparison reads it. Since `PL-979Z` the same applies to
a value already built as another checked quantity, such as a `StepCount` or a
`CaseInstant` handed to a flow's constructor. That value is a swapped
argument, not a number to check against a second range. Minus zero is stored
as the zero it is. The range check is the chained closed-interval comparison
alone, with no `isfinite` before it. A NaN fails both halves, and an infinity
fails one. An `int` too long for a `float` is compared exactly and refused
against the range, in the setting's own words, where `isfinite` raised
`OverflowError`. `StepCount` refuses what is not an `int` the same way, as a
`TypeError`. Until `PL-7N8P`, `CaseInstant` kept its own guard. That guard
built an instant of 1 s from `True` and stored a `Decimal`. It also let an
`int` past the float range escape as `OverflowError` instead of refusing it
against the run length. Until `PL-3800`, the `require_positive_finite` and
`require_nonnegative_finite` guards in `core/validation.py` had the same
holes, for every volume, coefficient, amount and step they guard.
`SimulationStep` had them too, through the first of those guards. Those two
guards have no supported range to refuse an `int` past the float range
against. So they refuse it by name, as outside the range a `float` holds,
before `isfinite` reads the value. What they admit is unchanged. The words in
which they refuse a sign, a NaN or an infinity are unchanged too.
<!-- not-restated: 1 s -->

**The dial's bound is enforced in both records that hold the pair, through one
guard** (`PL-BBMG`). The delivered concentration has the same four ways in as
a flow. Its bound is not a constant of the model but the maximum of the
agent's vaporizer, so no type can carry it. A dial is checked against a
maximum, and only a record that holds both can make the check.
`BreathingCircuit` always held both and refused a dial above the maximum.
`UptakeEquationSettings` held the dial alone and bounded it at 100%. So a
record rebuilt with `dataclasses.replace` to 20% sevoflurane, against the
agent's 8% maximum, opened a run. It was recorded as a change to a run, and it
returned an alveolar fraction of 0.033306 at 60 s (measured 2026-10-04). The
record now carries `max_delivered_concentration_percent` beside the dial. The
field is required and has no default. The record's constructor refuses a dial
above it through `require_within_vaporizer_maximum` in `core/validation.py`,
the same function that the circuit calls. So both records refuse in one
sentence, and the relation is written once.
`AgentUptakeSystem.equation_settings()` reads the maximum off the circuit. So
each stretch of a run records the limit that its dial was set under. The
propagator cache key carries the maximum with the rest of the record, although
the matrix never reads the maximum. Both records accept zero, which is the
vaporizer off, and the maximum itself. Both refuse the first percent past the
maximum.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

#### What a setting outside the range costs

**The argument for these limits changed with the exact step, but the ranges
did not.** Until v0.4.x, these limits were justified numerically. The operator
split was first order, and its coefficient $`C`$ grew roughly in proportion to
the flows. A setting outside the ranges therefore produced a displayed number
that was not merely unverified but *wrong*, by a known multiple of the last
displayed digit. The exact step removes that argument entirely. It solves the
equations exactly at any flow, so an out-of-range setting now yields a number
that is numerically right.

**What justifies refusing such a setting is therefore the reason that always
applied as well.** This section states that reason on its own, now that it is
the only one. These ranges define the **verification domain**. They are the
ranges over which "Independent-solution test" drives its trajectories. They
are the ranges over which "Published wash-in and elimination validation test"
compares the model against measured human data. Every figure in this document
is measured across them. Outside them, the implementation has not been checked
against anything. More seriously, neither has the *model*. A cardiac output of
1000 L/min is not a patient, and these equations were never proposed as a
description of one. Solving them exactly for that setting produces a precise
answer to a question that physiology does not ask. For exactly that case, the
required behavior is to prefer an obvious failure to a plausible-looking
number. That requirement does not depend on the arithmetic being imprecise.

The numerical figures below are kept as history. They describe the method
that shipped through v0.4.2. They were measured on desflurane over the
*unperfused load, then dial off* trajectory of § "Independent-solution test"
above. They used the shipped 0.1 s step and were compared against the
0.01-percentage-point displayed resolution.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

| Setting | $`C`$ (s⁻¹) | Multiple of the bound | Last displayed digit uncertain by |
| --- | --- | --- | --- |
| The documented maxima | $`2.29\times10^{-3}`$ | 1.0 | 2.3 counts |
| Alveolar ventilation 200 L/min | $`3.37\times10^{-3}`$ | 1.5 | 3.4 counts |
| Fresh gas flow 500 L/min | $`5.82\times10^{-3}`$ | 2.5 | 5.8 counts |
| All three flows at twice their maxima | $`4.57\times10^{-3}`$ | 2.0 | 4.6 counts |
| All three at ten times their maxima | $`2.28\times10^{-2}`$ | 10.0 | 23 counts |
| Cardiac output 1000 L/min | $`9.12\times10^{-2}`$ | 40 | 91 counts |

The last row is the setting that PL-0MLQ found the simulator accepting. Under
the split, ninety-one counts meant an alveolar readout that was wrong in its
*first* decimal, while it presented itself as a settled two-decimal value.
Under the exact step, that readout is right to the last digit. It is a precise
concentration for a patient whose cardiac output is twenty times any human's.
That is the worse of the two failures, not the better one, because nothing
about the display invites doubt.

Note what the table also showed: the error did *not* explode at the boundary.
Nothing broke at 10.01 L/min. The exact endpoints of the interval are a
decision, not a discovered cliff. They mark the settings envelope that the
interface offers and that the verification measures over. That is still true,
and it is now the whole of the story rather than half of it. The endpoints are
where verification stops, and nothing else marks them. Widening one is a
legitimate change and a safety-critical one. To widen one, first extend the
verification domain. Then re-run the trajectories of "Independent-solution
test" over it, and revise this section with the results.

**Re-derivation still owed.** This subsection has been re-grounded rather than
re-measured. The argument above is complete. The table, however, is history.
The displayed-resolution claims that the table refers to have not yet been
re-derived for the exact step. Queue item `PL-X9KD` covers that work, together
with "Displayed precision" and the supported step bound.

#### The model's envelope and a machine's deliverable range are two claims

Until `PL-8PS6`, one pair of constants stood for both claims. They are
different statements about different things:

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

**The hazard is a machine widening the envelope, and it is why this is a
split rather than a tidying.** Suppose a profile's flowmeter reaches 15 L/min,
and its range is merged into one pair of constants. That profile would extend
the domain that every reference gate was driven over, without a single
statement in `core/supported_ranges.py` changing. The result would be an
arithmetically exact number, produced outside everything that was verified,
and presented on screen exactly like one inside it. The converse fails the
same way from the other end. Take a machine with no true off position at its
common gas outlet, and a minimum flow of 0.5 L/min. Under one constant, that
machine would either be unrepresentable or would move the model's lower limit
for every other machine. Separating the two claims means that a machine
profile can narrow what a run will accept, and can never widen it.

**A machine that overlaps the envelope nowhere is refused when the circuit is
built.** It is also refused when its range is reassigned on a built circuit,
by the check made when the range is written (`PL-19Y0`). The mismatch is
therefore not discovered one refused setting at a time. Every flow such a
profile can deliver is outside the envelope, and every flow the model supports
is outside the profile's range. Each individual refusal would be correct, but
none of them would say that the pair is what cannot be simulated
(`test_a_machine_that_overlaps_the_envelope_nowhere_is_refused_when_built`
in `tests/unit/test_circuit.py`).

**The shipped profile declares no range, and nothing displayed changes.**
`data/machines/reference_circle_system.json` records
`deliverable_fresh_gas_flow_range` as `null`. The reason is that no operator's
manual or manufacturer specification giving a deliverable range was reachable
for any machine surveyed. `docs/machine-survey.md` § "(b8) Flow bounds, minimum
oxygen flow, and the hypoxic guard" reports the range as unknown for all
eight. It names ISO 80601-2-13:2022 as the governing standard. It also states
that the standard's text was not reached, and that no claim about its
requirements is made. A `null` is an **absence of claim and not a machine
known to be unlimited**. The table above is then the only bound on the flow.
That is precisely the behavior that shipped before the field existed. The
profile's `provenance_gap` carries that reasoning, and
`test_the_shipped_machine_declares_no_deliverable_flow_range_and_says_why` in
`tests/unit/test_parameters.py` checks that the file keeps to it.

**What is not stored beside it.** `docs/machine-abstraction.md`'s field table
also names `minimum_total_flow_l_min` and `minimum_oxygen_flow_l_min` under
the same survey section. Neither is a field here, because that document's own
rule is that a field exists only if something consumes it. A minimum total fresh gas
flow *is* the lower end of the deliverable range. Storing two names for one
number in a safety-critical data file is the conflation that this subsection
exists to remove. A minimum oxygen flow affects nothing that this model
computes. The model carries one volatile agent in a single gas phase, and no
oxygen at all. A minimum oxygen flow becomes admissible on the day a hypoxic
guard needs it. That is a model extension rather than a data question.

**The fresh gas flow control offers the intersection, read from the
circuit.** `BreathingCircuit.accepted_fresh_gas_flow_range_l_min` states the
intersection once. Where a profile declares no range, it is the envelope.
Where a profile declares one, it is the overlap of the two claims. The
interface's control is bounded by this range rather than by the envelope alone.
The reason is that a slider offering a flow that the mounted machine cannot set
would invite a refusal instead of preventing one (`PL-7CRY`). The slider steps at the
flow's displayed resolution, 0.1 L/min. An end of the range that falls between
two steps is therefore offered as the step just inside it. A machine with a
minimum flow of 0.25 L/min is offered 0.3 L/min, never the 0.2 L/min it would
refuse. A range that contains no step at all is an error, rather than a
control whose only setting the run refuses. A machine profile whose opening
flow is not one of the offered steps is refused as well, when the dashboard
builds its controls (`PL-1KQ9`). A slider position is a printed value
(`PL-25KS`, decision D4). A run that opens between two steps would leave the
slider on a neighbouring step beside a rounded readout. Both would then show a
flow that differs from the flow the run actually has.
`test_the_fresh_gas_flow_control_narrows_to_a_declared_machine_range`,
`test_a_declared_range_off_the_display_grid_offers_only_settings_inside_it`
and `test_an_opening_fresh_gas_flow_off_the_slider_grid_is_refused`
in `tests/unit/test_dashboard_frame.py` check all three cases. Nothing
displayed changes while the shipped profile declares no range.

#### Supported run length

A run is supported up to **24 hours of elapsed simulated time**. The limit is
declared as `MAXIMUM_ELAPSED_SIMULATION_TIME_S` in `core/supported_ranges.py`.
`SimulationState.advance()` refuses the step that would carry a run past the
limit. It raises `SimulationDomainLimitError` before anything advances. A point
past the limit can also be handed in rather than reached. Such a point is
refused with `SimulationConfigurationError` before any run holds it, because
in that case the value handed in is what is wrong (`PL-BMY5`, `PL-73ZN`). This
covers two cases. The first is a step count beyond the limit, refused where a
`SimulationState` pairs the count with its step. The second is an instant
beyond the limit, refused where the instant is built as a `CaseInstant`
(`PL-CN5S`, below). Such an instant is either the opening at which a branch's
`RunDefinition` is built, or a reach to which a run is moved. A run that
stops at the limit stops on a step count at which a run may also be built.
Only the step from that count is refused. The step's guard and the state's own
check both take that count from one derivation, `maximum_step_count`. It is the
largest count whose simulated time is no later than 24 hours. The simulated
time is the count times the step, rounded once, which is `elapsed_s`. At the
shipped 0.1 s step, the last step lands exactly on 24 hours. The count is
decided on that product, not on the quotient of 24 hours by the step. At some
computed steps, the quotient rounds a whole step either way. It gives either a
last step that lands a float past 24 hours, or one that stops a step short of
landing on 24 hours. Deciding on the product means that a count is accepted
exactly when the instant it stands at is accepted. A branch is then built or
refused alike, whether it is taken from its parent's count or from its parent's
instant (`PL-8H2R`).
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

| Quantity | Limit | Declared and refused by |
| --- | --- | --- |
| Elapsed simulated time | 0 to 24 h (86 400 s) | `core/supported_ranges.py`: `CaseInstant`, the type every instant is built as when a run opens, moves, keyframes, marks or branches at it, and `SimulationState`, which checks a `StepCount` against its step |

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**It is the case's 24 hours and not each run's, which matters once a case can
be branched.** The section below argues this limit against what the model
omits. Those omissions are properties of how long the *patient* has been
anesthetized. So a branch spends the same 24 hours that its parent was
spending, starting from the point where the branch was taken. A fork at 23 h
leaves one hour, not another twenty-four. Nothing enforces this separately.
Every guard on the limit reads the case's axis, which is a step count or a case
instant, and a branch continues its parent's axis. So the arithmetic that
bounds a trunk also bounds every branch of it (`PL-J2TD`).
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The instant and the count are types, each checked once where it is built**
(`PL-CN5S`, the second slice of `PL-51B7`, in the shape that § "Supported
input ranges" gives the flows). Every instant at which a run is opened, moved,
keyframed, marked or branched is a `CaseInstant`. A `CaseInstant` is a `float`
subclass, and its constructor is the only thing that runs
`require_supported_case_instant`. Since `PL-7N8P`, a `CaseInstant` is built
from an `int` or a `float` and nothing else, and it stores minus zero as zero,
as § "Supported input ranges" says of the flows. A `bool`, a `Decimal` or a
string is refused with a `TypeError` before any comparison. An `int` beyond the
float range is refused by the check against the run length. Some places keep
an instant or move a run to one. In those places the type is required, and
anything else is refused with a `TypeError`, whatever its value. These places
are a `RunDefinition`'s opening and every reach it is advanced to, each
`Keyframe`, a `TimeBookmark` and the `BookmarkCrossing` that a run halts on,
and the instant at which `SimulationController.resumed_at` branches. A value
built as another checked quantity, such as a `StepCount` handed in as an
instant, is refused as the swapped argument that it is, with no advice to
rebuild it. It is refused where the instant is kept, and also, since
`PL-979Z`, by `CaseInstant` itself. Code that only carries an instant onward
is annotated with the type and checks nothing again. Examples are a snapshot,
a chart frame and the instants at which a fork is offered. So a time bookmark
past the span cannot be made at all. Until `PL-CN5S`, such a bookmark could be
built in code, though not from the bookmark dialog, whose entry already stopped
at 86 400 s. From the moment it was added, that bookmark was treated as not
reached within the supported run length. A completed-step count is a
`StepCount`, an `int` subclass. It is checked only for what a count can be
checked for on its own: it must be whole and nonnegative, and a `bool` is
refused. The reason is that how many steps fit depends on the step.
`SimulationState` checks the pair against `maximum_step_count` through
`require_supported_step_count`. That check is a relation between two fields,
so it belongs to the record. The record checks the pair at every write to
either field, in `__setattr__`. So a count or a step assigned straight onto a
built state meets the constructor's own refusals, in the constructor's words,
and the field keeps the value it had. `mypy` refuses such an assignment in
`src/`, and nothing refused it elsewhere until `PL-8W1W`. A bare `int` count or
a bare `float` step is refused with a `TypeError`. A count past zero with no
step, or a pair past the run length, is refused with a
`SimulationConfigurationError`. This matches what § "Supported input ranges"
says of a flow written onto its compartment (`PL-LBQY`).
`SimulationState.elapsed_s` builds its product as a `CaseInstant`. That
constructor never refuses the product, because the count being multiplied is
decided on that same product (`PL-8H2R`). An instant that a run is only
*asked* about stays a plain `float`. Examples are the instant passed to
`RunDefinition.state_at` and the bounds of a drawn window. The run's own
opening and reach bound such an instant, and that relation is the run's to
check. Arithmetic on either type returns a plain `float` or `int`, so a
derived instant or count is never treated as checked. The control record's
instants are `ControlChange.elapsed_s` and an adjustment's start and end. They
are still annotated `float`, though each is taken from a `CaseInstant`
(`PL-RCYZ`).

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
the flow acts directly on the slow tail of washout (`PL-HBH2`). A run beyond
this boundary therefore displays a trace whose slow component is increasingly
the two omissions rather than the model.

**Inside the boundary the tail is already missing its largest measured term,
and the number does not say otherwise** (`PL-YD2V`). Every washout that the two
Yasuda papers fitted needed five compartments. Their authors read the fourth
compartment as fat filled by diffusion from the well-perfused tissue lying
against it. This model has no counterpart for that route. The fourth
compartment carries the largest term in the measured curve over most of the
span for which a run is supported. It does so from about 1.8 to 3.1 hours after
a 30-minute administration until about 20.7 to 29.4 hours. The
intertissue-diffusion note under § "Known limitations" has the coefficients and
the arithmetic. All else equal, a tail without that store falls faster than
the measured one from about the third hour of elimination. Measured against the
published mean curves over the whole supported run, the shipped tail does so
(§ "The first 24 hours of elimination against the published mean curves",
`PL-KK1Q`). It runs below the curves by about a third from about the seventh
hour until about the twenty-first. For desflurane it runs below them from 3.4
to 15.3 hours, and by half. Over the hours before that, it runs above them by
a fifth to a half, while the rebreathing circuit and the muscle group's slow
return keep it up. At 23.5 hours of elimination it runs above them again, by
12 to 24%, or by a factor of 2.1 for desflurane. That is because this model's
fat group returns more than the fitted fat term. With the apparatus taken away,
the tissue return alone is a third to a half of the mean curve between hours 8
and 13. **That result does not move the 24 hours** (project owner, 2026-09-27,
ratified, over shortening or extending the span on the measured departures).
The number is argued against the two omissions above growing past negligible
over the span. The measured departures are neither of those omissions. The
metabolism bound in the same subsection accounts for about an eighth of the
excess where the tail runs above the curves. Where the tail runs below, that
bound widens the gap. The shortfall is the missing fourth compartment, which
is as present in the first hour as in the last. Shortening the span would not
take the tail out of it. Extending the span would add the late excess, which is
still growing at the boundary. So the number is kept. What it certifies about
how close the late tail runs to a measured washout inside the span is exactly
what that subsection measured, and nothing more.
<!-- not-restated: 2.1 -->
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

**Why 24 hours, and not a multiple of the slowest time constant.** The fat
group's time constant is about 42 h. A cap argued as several multiples of it
would select for precisely the regime described above. That regime is the part
of the trace that is most nearly all omission. The fat time constant bounds
this number from *below* rather than above. With a span shorter than about one
time constant, the fat trace stops showing what it exists to show. 24 hours is
about 0.6 of it, so the fat compartment is still visibly loading. The span
clears every anesthetic this simulator is built to teach by a wide margin. It
also sits inside the regime that the source above calls clinically negligible
for metabolism. It is also near the outer edge of the exposure range over
which that omission has been measured at all.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**This replaces a memory limit that was never a modelling one.** The figure
used before this section existed was 30 days. It was set on 2026-08-25 to size
a concentration history that no longer exists, and it was enforced nowhere at
all. A run could reach day 45 and go on displaying two-decimal concentrations.
A run length is a question about the supported domain, not about resources.
That is why the number moved by more than an order of magnitude when the
question was asked properly (`PL-Y5WR`).

**Reaching it is not a failure, and the interface may not present it as one.**
The step is refused before it begins. So a run stopped here has stopped on a
completed step, at a simulated time inside the supported span, and every
displayed value is a real solution of the model. `SimulationDomainLimitError`
is a distinct exception type for exactly this reason, and `app/` checks for it
to choose its wording. The run stops, and the reader is told which limit was
reached and why it is where it is. Reset starts a new run. Describing a correct
model as a broken one misleads a reader as surely as the reverse. It spends the
interface's one signal for a real fault, and it teaches a reader to discount
that signal. The interface must equally not present the stop as a pause. Start
is refused, because a resumed run's first step would be refused again.

**Whether a run is at the limit is decided from the run, never from the
refusal alone** (`PL-5291`). A run can come to rest on 24 hours by three
routes, and only one of them refuses a step. The first is a trunk stepping onto
the last supported count. The second is a branch forked on that count, either
at a mark that halted the trunk there or at a dial moved there. The third is a
branch reset onto such a fork. While a stop was recorded only when a step was
refused, the other two routes looked like an ordinary pause. Start was offered,
no limit notice appeared, and a mark that the run never reached was reported as
still ahead of a run that could not step. So the controller asks the core's own
guard, `require_supported_run_length`, whether the run's next step would be
refused. It asks every time the run's state is read and after every step. It
reports the limit with the reason that the refusal would give. A run stepping
onto the count halts on the step that arrives there, not on the refused step
after it. So no run appears to be running, or paused, while it is at a point
where no step is left. The interface may catch a `SimulationDomainLimitError`
on some other path, such as a setting. That error is recorded as the reason,
and it takes precedence over the derived one.
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

#### What is not bounded this way

The two gas volumes, that of the breathing circuit and that of the alveolar
compartment, are **fixed model parameters rather than controls**, and they
carry no declared interval. Each is set once, when
`AgentUptakeSystem.for_agent()` builds the system, and nothing changes it
afterwards. The interface offers no control for either volume, and since
v0.4.x `SimulationController` exposes no setter for either.
`core/validation.py` checks that both are positive and finite. It does not
check them against a measured domain.

The two volumes do not have the same provenance, and the difference is worth
stating rather than smoothing over. The alveolar gas volume is a patient
parameter of 2.5 L. It is read from `data/patients/reference_adult.json`, and
the provenance table above carries it together with the FRC measurement that
it is reconciled against. The circuit volume is a *machine* parameter of
6.0 L. Since `PL-4YY1` it is read from
`data/machines/reference_circle_system.json`. That file is a third kind of
parameter file, beside the agent and patient files, because the breathing
system belongs to neither the agent nor the patient. The same table carries
the circuit volume with what is known about where it came from, which is that
no source is adopted for it. Until `PL-4YY1` the volume was the field default
`circuit_volume_l: float = 6.0` on `BreathingCircuit` and had no row here at
all. So the only tool that checks this document against the data files could
not see it. `check_provenance` walks data files in both directions, and a
constant that never entered a data file is invisible to it.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

**Each parameter file is the single authority for its own values, and `core/`
holds no copy of them.** Since `PL-M85T`, `AlveolarCompartment` has no default
for its gas volume or its ventilation, and `BreathingCircuit` has none for its
volume or its vaporizer maximum. Before that change, the first three defaulted
to 2.5 L, 4.0 L/min and 6.0 L. Those defaults were copies of the files' values,
and only a test kept them equal to the files. The vaporizer maximum defaulted
to 100%, which no agent's vaporizer delivers. Every shipped path goes through
`AgentUptakeSystem.for_agent()`, which reads the values from the agent, patient
and machine files and passes them on. The fresh gas flow keeps a default,
named `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`, because a run can reach it
another way. Since `PL-QW19` a machine profile may state no startup flow, and
a run built from such a profile opens at the named constant. The constant's
authority is the teaching-default rationale recorded with the flow's
provenance row, not any source.
`test_the_flow_default_matches_the_shipped_machine_file` checks that the
constant equals the file's value.
`test_for_agent_builds_the_circuit_at_the_machine_file_s_values`
and `test_for_agent_builds_the_alveoli_at_the_patient_file_s_values` each
assert that the shipped path arrives at the file's values. The failure with
real consequences would be a change that stopped `for_agent()` reading a file.
Every provenance row in this table would then silently become a claim about a
file that the model no longer consults. So each of the four values is also
checked by a run built from a file that states a different value. That run
fails when `for_agent()` stops passing the value on. For the machine file the
tests are `test_for_agent_builds_the_circuit_at_a_changed_machine_file_volume`
(3.3 L) and `test_a_profile_stating_its_startup_flow_opens_the_run_at_that_flow`
(2.0 L/min). For the patient file the test is
`test_for_agent_builds_the_alveoli_at_changed_patient_file_values` (3.0 L and
5.0 L/min). Each of the four was confirmed by breaking it in turn and seeing
its test fail (`PL-H8QP`).
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6.0, default_fresh_gas_flow_l_min = 4.0 -->
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

**What a wrong volume would be wrong for.** The argument is physiological
applicability, exactly as it is for the four controls. It is not numerical
error. This was measured on 2026-09-06 with sevoflurane at the shipped 0.1 s
step. A 0.005 L alveolar compartment and a 10 000 L circuit both advance
without incident, and agent accounting passes. So each yields an
arithmetically correct answer to a question that physiology does not ask. A
5 mL alveolus is not a lung. This model's lumped structure, its fixed tissue
volumes and its constant partition coefficients are claimed to represent a
patient only near the shipped values. Until v0.4.x this section stated the
opposite justification, which was that a small alveolar volume inflated the
operator split's error. That argument was retired with the split.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

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

**Below that the mass-balance guard stopped firing, and what refuses now is
upstream of it** (`PL-3PRZ`). At $`10^{-300}`$ L the run advanced and returned
an alveolar fraction of exactly 0.0, with accounting passing. The guard was not
weak. The propagator had been driven to the zero matrix, so `propagate()`
returned the zero state vector. The identity was then handed
$`0 + 0 - 0 - 0`$ on totals that had all been annihilated together. Zero does
balance zero. Every term of the check had been destroyed before the check ran.
That is the pattern to look for wherever a residual is formed from quantities
that the same failure can affect.

`core/matrix_exponential.py` now refuses a zero propagator. The reason is that
$`\exp(A\,\Delta t)`$ is nonsingular for every finite $`A`$, because its
determinant is $`e^{\operatorname{tr}(A)\Delta t}`$. So the zero matrix is the
exponential of nothing and can only be a floating-point artifact. The module
also refuses the case where scaling the matrix norm down to the series bound
overflows. That case reached `ceil(log2(inf))` and raised a bare
`OverflowError` at $`10^{-309}`$ L. A bare `OverflowError` is outside the
hierarchy in `core/exceptions.py` that a caller relies on. Both refusals now
arrive as `SimulationNumericalError` through `AgentUptakeSystem.advance()`,
with the step rolled back. Since `PL-2MD9` the model no longer reaches the
first refusal. A matrix that carries the constant state cannot produce the
zero matrix at all, and those volumes now stop earlier, at the cap on the
squarings described below. The second refusal still fires first wherever the
scaling overflows.

**Measured across every decade from $`10^{0}`$ to $`10^{-323}`$ L when that
refusal landed**, before and after the change, the counts were these. Before,
120 decades advanced with the constant state row exact, and the same 120
advanced after. Before, 77 had been refused as non-finite, and 194 were
refused after. The difference is made up exactly by the 116 that had returned
a zero propagator silently and the one that had raised `OverflowError`.
Nothing that had advanced was refused. Since `PL-2MD9`, the same sweep at the
0.1 s step returns a propagator at 11 decades, $`10^{0}`$ to $`10^{-10}`$ L,
each with the constant state row exact. It refuses the other 313 before any
arithmetic. Of the 119 decades that returned a propagator before and are
refused now, the mass-balance guard had halted the run at 117. At one more,
the run had stopped on a fraction outside zero to one. The last,
$`10^{-18}`$ L, advanced with every value wrong (described below). A single
mode decaying below the smallest subnormal is still propagated as 0.0, which
is correct. `exp(-0.5 * 3600)` is a real number that no double can hold. A
single zero entry of this kind is what separates a decayed entry from an
annihilated matrix.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**The last failure in this family is closed by a cap on the squarings**
(`PL-2MD9`). Between $`10^{-8}`$ and $`10^{-19}`$ L the propagator stayed
finite and nonzero, but the constant state row drifted. No interval may move
that row, and its row in $`A`$ is empty for exactly that reason. It drifted to
1.0000610 at $`10^{-12}`$ L, then 2.718, then $`2.28\times10^{+222}`$ at
$`10^{-19}`$ L. The shift lets the error in, and the squarings amplify it. The
constant was not the only state affected. This was measured on 2026-10-03
against a high-precision evaluation of the same exponential. The worst
entry's relative error after $`s`$ squarings is $`c\cdot2^{s}\cdot2^{-52}`$,
with $`c`$ between 0.6 and 2.7 at every decade measured, from decades that
need no squarings to decades that need 45. So every state whose own rate the shift swamps drifts
the same way. Two changes close the failure. First, the constant state's row
is written as the identity's row before the squarings, and the squarings keep
it exact to the last bit. So `governing_equations.UNIT_STATE`'s guarantee that
no step perturbs the constant state is now true in floating point as well as
in the algebra. Second, a propagator that needs more than 32 squarings is
refused before any arithmetic, because past that point the error bound
exceeds one part in a million. The most that any supported input needs is 19,
at the 24-hour horizon and the widest supported flows. The first change alone
would have been worse than nothing. It let 114 decades between $`10^{-25}`$
and $`10^{-306}`$ L that had been refused advance again, with every entry but
the constant's destroyed. That happened because the zero-propagator refusal
above relied on the constant row being annihilated with the rest.

**That band was not covered the way this section used to say.** The section
said that the mass-balance guard caught the drift from $`10^{-9}`$ L down. At
$`10^{-18}`$ L it did not. The run advanced three steps with every entry of
the propagator wrong by about 100%. It showed 6.4e-32 L delivered where the
vaporizer had delivered 0.0004 L, and the accounting check passed.
It passed because the same failure had reached every term of the identity,
which is the pattern from `PL-3PRZ` again. The cap refuses this case, and
`tests/unit/test_agent_simulation_validation.py` contains the regression test.

**What is left open, stated plainly.** A caller writing Python against
`core/` can still construct `BreathingCircuit(circuit_volume_l=10_000.0)` or
`AlveolarCompartment(gas_volume_l=1e-6)`. `SimulationController` still takes a
`circuit_volume_l` argument at construction. Those values are outside the
verified domain, and nothing refuses them. They are a different exposure from
the one the four controls had before `PL-0MLQ`. They are not a live setting
that a run can be steered with, and they cannot be reached from the interface
at all. They are a value chosen once, by a caller who has gone to the trouble
of building the model directly. `BreathingCircuit.set_circuit_volume` remains
for the same reason. It is how the parameter gets to the circuit, and it is
where the agent conservation and capacity guards live (`PL-006`).

**Zero is a supported input on all four, deliberately** (PL-629Z). There are
three reasons, and the third is the one that decides it:

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

**These ranges define the verification domain.** § "Independent-solution test"
above drives its trajectories over what these ranges can produce. Its worst
disagreement with the independent solution occurs on a trajectory that holds
cardiac output at zero. Narrowing a range would take that worst case out of
the reachable domain, and widening one would admit trajectories that were
never measured. Either way, the gate must be re-measured. The exact step has
removed the numerical argument for the ranges, so this is now what the ranges
are *for*. See § "What a setting outside the range costs" above. Three checks
stop a range from changing without anyone noticing.
`test_envelope_limits_match_the_supported_input_ranges` restates all six flow
limits and fails if the model moves one.
`test_displayed_resolution_and_shipped_step_match_the_interface` does the
same for the resolution and the step that every figure is quoted at.
`test_the_sliders_span_the_supported_input_ranges` fails if the interface
stops short of the declared domain or extends past it. That test reads the
shipped machine profile, which declares no deliverable range. A profile that
declares one narrows the fresh gas flow slider to the overlap on purpose
(§ "The model's envelope and a machine's deliverable range are two claims").

**The simulation step is bounded too, and separately.** It is not a control
that a user sets, but it is an input to every `advance()` call. What a caller
may pass is bounded by `MINIMUM_SIMULATION_STEP_S` and
`MAXIMUM_SIMULATION_STEP_S`, not by these ranges.
§ "Supported simulation step" above argues for both bounds.

**The two bounds are now independent, and were not before** (`PL-X9KD`). While
the operator split shipped, the coefficient that the step bound inverted was
measured over the trajectories that *these* ranges produce. So widening a
range meant re-deriving both bounds. That chain is now cut. The step's ceiling
is a declared control-resolution tolerance in seconds. These intervals are a
claim about where the compartment structure represents a patient. Neither is
computed from the other. Widening a range means re-running the reference gates
at the new corner. It does not mean revisiting the step.

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
not press Reset on the branch. So when a drawn branch holds elapsed simulated
time or a recorded control change, the trunk's Reset states what that branch
holds and asks before it discards anything, as the list above requires. The
trunk's Reset also asks about a branch whose state cannot be read, because
what that branch holds is not known to be nothing. A branch that holds
neither is dropped without a question. Three tests in
`tests/integration/test_simulation_view.py` enforce this rule:
`test_resetting_the_trunk_asks_before_dropping_a_branch_that_holds_work`,
`test_declining_the_trunks_reset_leaves_every_run_as_it_was` and
`test_confirming_the_trunks_reset_starts_the_case_over_without_the_branch`.

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
branch opens with an empty timeline of its own
(`test_a_branch_opens_with_its_own_empty_control_timeline`). Forking leaves
the trunk untouched (`test_forking_leaves_the_trunk_untouched`). So everything
that either run records after the fork is what its learner did to it. **A
difference between the two runs at an instant past the fork is therefore
caused by the settings that differ after the fork, on either side, and by
nothing else in the model.** That is what the mechanism provides. It is worth
stating positively as well as negatively. Building the case twice instead
would leave the two runs differing by everything that was not reproduced
identically. A learner reading that comparison could not see which
differences they had caused.

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
  `app/chart_frame.py`, `PL-GS3R`). A plot can become wider than the width its
  frame was sampled for, by a window resize or by a reader dragging an Area
  border. The plot is then redrawn on the next render tick, whether the run is
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
arithmetic.

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
- the rate at which simulated time is advancing, as a multiple of real time. It
  is drawn wherever simulated time is drawn, and at every rate, including real
  time (`test_the_playback_rate_is_drawn_under_the_clock_it_governs`). See
  § "Interface boundary" for what the rate is a statement about, and what it is
  not;
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
arterial blood is flow-limited and holds no independent state:
$`F_a \equiv F_A`$ (see § "Model boundary"). A separate arterial readout would
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
the size of the gap. It used a 3-hour 1 MAC sevoflurane case with the
vaporizer turned off at 10 L/min. The alveolar trace crosses the band's centre
at 2.83 min, and the vessel-rich trace crosses it at 6.51 min, 2.30 times
later.
<!-- not-restated: 10 L/min -->

<!-- derived: 2.83 min from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->

The primary literature makes this a question of *which number is correct*,
not only of how a number is read. Katoh et al. determined sevoflurane and
isoflurane MAC-awake by two methods, a slow, equilibrated washout and a fast
one. The two methods disagree. Slow washout gave 0.34 and 0.31 of MAC for
sevoflurane and isoflurane respectively, against 0.22 for both by fast
washout. The paper attributes the difference to end-tidal-to-arterial and
arterial-to-cerebral anesthetic differences. That is precisely what this model
represents as the alveolar-to-vessel-rich difference. The paper also measures
the brain concentration directly rather than leaving it to inference. During
fast washout, the cerebral concentration at first eye opening was 0.34 of MAC
for sevoflurane and 0.30 for isoflurane,
"nearly equal to MAC-Awake obtained by slow alveolar washout". The stored
values are therefore the slow-washout ones, and the trace they belong against
is the vessel-rich one.

<!-- provenance: data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34 -->
<!-- provenance: data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31 -->

**Every way of getting this wrong runs in the same direction, and it is the
consequential one.** Concentration falls during emergence. So a trace crosses
a higher reference sooner, and a faster-falling trace crosses any reference
sooner. Three distinct errors therefore all shorten the apparent time to
awakening. The first is reading the band against the alveolar trace instead
of the vessel-rich one. The second is drawing the slow-washout value against a
fast-washout alveolar trace, where 0.22 would be the matching figure. The
third is the denominator mistake described below. A learner who takes away
any of these errors concludes that emergence is faster than this model says.
That learner carries into practice the belief that a patient is more awake
than they are. That is why this document specifies the reference, rather than
leaving it to the chart.

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

One consequence is expected and is not a rendering fault. On a short case, the
vessel-rich trace never reaches the 1 MAC line, because it never equilibrated.
That is true of the patient, and it is worth teaching.

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
stored in the unit that the core uses. So the delivered dial is stored as a
fraction of one atmosphere. It is displayed as a percent, like every other
concentration on the page, and it is converted once, at the display. A record
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

Every modeled concentration and relative partial pressure is displayed at a
fixed resolution of **0.01 percentage points**, which is two decimals of a
percent. The resolution is the same across all six compartments. The
delivered-agent setting uses the same resolution, both in the readout beside
its slider and in the slider's own drag label. So the value a reader dials and
the values it produces are read at one scale. A positive value that would round
to `0.00%` is displayed as `<0.01%` rather than as zero.

This is a recorded decision (PL-040), not a formatting convention, because
displayed precision is a claim about what the model can support. Earlier
revisions displayed three decimals. They were reduced to two while the operator
split shipped, on the ground that the third decimal and part of the second were
smaller than the solver's own error.

**That ground is gone, and the decision is re-derived here rather than
inherited** (`PL-X9KD`, 2026-09-06). `PL-GS5X` replaced the split with an exact
propagator, so the solver no longer limits anything a reader can see. Measured
against the independent solution, the shipped step's own residual is at most
$`1.6\times10^{-12}`$ percentage points anywhere in the reference gate's
trajectories, and $`5.2\times10^{-12}`$ over a held hour. That is about one
two-billionth of the last displayed digit. **A third decimal would no longer be
numerical noise.** Every figure that the previous version of this section
quoted in counts of the last digit described a method that has been retired.

So the constraint that decides the resolution had to be found again, and it is
not the one that decided it before. It is **model fidelity**, meaning what the
parameters can support. It is bounded from the other side by **legibility**.

**The old section ran two questions together, and the distinction between them
now carries the whole derivation.** The first question is *how finely can two
moments within one run be told apart*. Its answer is now about nine decimal
places finer than the readout shows. Within a run the parameters are fixed and
the simulation is deterministic. Nothing in the arithmetic comes within nine
orders of magnitude of the last displayed digit. The second question is *how
finely does this model resolve a concentration in a patient*. Its answer is
very much coarser, and it is the question that a clinician reading a percent
sign is actually asking. The old section answered the first question and
presented the answer as if it were the answer to the second. It could do that
because the solver error happened to be close to the readout's resolution, and
it can no longer do that.

**The upper limit: one measured standard deviation of a partition coefficient
is worth about one to seven counts of the last displayed digit.** Perturbing a
single stored coefficient by one published SD, and re-running at 1 MAC with the
reference adult's flows, displaces a displayed compartment by these amounts:

| Coefficient perturbed by one SD | Displacement, worst over 3600 s |
| --- | --- |
| Fat tissue:gas | 8.7×10⁻⁴ to 6.7×10⁻³ pp |
| Blood:gas | 1.5×10⁻² to 5.4×10⁻² pp |
| Vessel-rich tissue:gas | 1.3×10⁻² to 5.0×10⁻² pp |
| Muscle tissue:gas | 1.3×10⁻² to 6.8×10⁻² pp |

<!-- not-restated: 1.3 -->

Each range runs over the three shipped agents, and desflurane always gives the
largest displacement. The SDs are the measured ones that
"Parameter provenance" already records. They are the SDs of Yasuda, Targ and
Eger's human tissue coefficients, which are 3.9% of the mean for desflurane,
5.3% for sevoflurane and 6.4% for isoflurane. For desflurane's blood:gas coefficient
the value is Eger's $`0.424 \pm 0.024`$, an SD of 5.7%.

Against that, the last digit of a two-decimal readout lies between about a
seventh of one parameter SD and seven times it. A third decimal would put the
last digit at one seventieth to seven tenths of one SD. It would then assert
resolution in a quantity whose own measured spread is one to two orders of
magnitude wider. It would do so in the readouts where a reader is least able to
notice. That is false precision in the sense that `CLAUDE.md` forbids, and it
is what stops the count at two.

**Parameter uncertainty governs the upper limit but still does not govern the
within-run reading, and both halves matter.** A partition coefficient's SD
displaces a whole trajectory. It moves where the curve sits, not how finely two
points on it can be distinguished. So a reader comparing 09:14 against 09:16 of
one run is not limited by the SD. That is why the readout may honestly carry a
digit finer than the SD, which is the seventh-of-an-SD end of the range above.
What the SD does forbid is carrying digits *far* finer than it. A reader cannot
tell which of the two questions a printed digit is answering. So the interface
must not invite the second reading while it supports only the first. "Known
limitations" is where the consequence is made good: no displayed value may be
read as accurate to its last digit as a prediction about a patient. A displayed
value is accurate to its last digit as a statement about this model with these
parameters.

**The lower limit: one decimal is legible enough to be tempting, and it erases
the teaching.** At 0.1 percentage points the sevoflurane and isoflurane fat
fractions read `0.0%` for the whole hour (0.032% and 0.015% at 3600 s).
Desflurane's fat fraction stays at `0.0%` for its first 19.3 minutes and
reaches 0.2%. Muscle reads `0.0%` for its first 2.9 minutes with desflurane,
8.5 minutes with sevoflurane and 14.8 minutes with isoflurane. At two decimals
the same compartments show a nonzero value at 57, 125 and 190 seconds (muscle)
and 236, 780 and 1474 seconds (fat). What one decimal erases is the
slow-compartment wash-in, which is the reason for displaying those
compartments at all.

**That lower limit is a teaching judgment, and it is the project owner's
rather than the model's** (decided 2026-09-03, `PL-88GQ`). The accuracy
argument does not apply to it. One decimal is comfortably supported by both
the solver and the parameters, so nothing numerical rules it out. What rules it
out is that a simulator built to show uptake and distribution would show a flat
zero where the uptake is happening. It is stated here as a pedagogical
objection so that a future revisit knows exactly what it has to beat. It is
also stated that way so that the revisit does not mistake it for a model
constraint that the revisit cannot change.

**So the band is one to two decimals, and two is the chosen count.** The band
is what the error budget licenses. The count inside it is a presentation
decision, which the owner may revise without re-deriving anything in `core/`.
Nothing in the model is computed from the count. `MAXIMUM_SIMULATION_STEP_S` is
a tolerance in seconds, and the supported input ranges are intervals in L/min.
"Supported simulation step" and "Supported input ranges" derive both without
reference to how many decimals the readout shows. Moving the readout to one
decimal would change what a reader sees and nothing else. That independence is
new. Until `PL-X9KD` both were justified through this count. So by the
reasoning as it was written then, a purely presentational change would have
licensed a step ten times longer and wider input intervals.

**The MAC resolution is derived from this one, not chosen beside it.** A MAC
multiple is a percent divided by the agent's own `mac_percent`. So the
resolution above already fixes how finely the quotient is known. Stating a
second resolution independently would mean re-deriving two numbers whenever
this one is re-measured. The rule is one line: **the finest power of ten that
is nowhere finer than the percent resolution converted into MAC.** That
conversion is agent-specific. Converted, 0.01 percentage points is 0.005 MAC
for sevoflurane, 0.0083 for isoflurane and 0.0017 for desflurane. So the
binding agent is isoflurane at 0.0083 MAC, and **0.01 MAC** is the finest power
of ten at or above it.

One count of the MAC line is therefore 0.02 percentage points of sevoflurane,
0.012 of isoflurane and 0.06 of desflurane. That is coarser than the percent
readout beside it for every agent. This property keeps the two units from
contradicting each other. A reader must never be able to watch the MAC digit
move while the percent digit stays still. That would assert that the model
resolved something it does not. The unit conversion does not preserve
information across agents. That is why the MAC resolution is uniform in MAC
rather than being the percent resolution restated. A per-agent MAC resolution
would put different magnitudes at the same glyph position. That is the failure
that "Why the resolution is uniform rather than per-compartment" rejects below,
arriving across agents instead of across compartments.
<!-- not-restated: 0.06 -->

The below-resolution form applies to the MAC line for the same reason it
applies to the percent line, and it matters more there, not less. A
compartment clears 0.01 MAC later than it clears 0.01 percentage points. So
`0.00 ×MAC` beneath a percent line that already shows the compartment filling
would make the two readouts contradict each other. `<0.01 ×MAC` states what is
known. `tests/unit/test_formatting.py` re-runs the derivation against every
shipped agent. So adding an agent or changing the percent resolution fails
there rather than silently over-claiming.

**The resolution is a property of the display alone.** Everything upstream of
the formatter carries full binary64 precision. That includes the compartment
states, every integration step, the mixed-venous and tissue transfers, and
every state of the `DrawnWindow` that the chart is drawn from. Nothing in
`core/` rounds. The snapshot fields that the interface reads are raw
fractions, and a slider's value reaches the model unquantized. The rounding
happens exactly once, in the readout. So the two decimals are a statement about
what is worth *showing*, never about what the model computes or stores.
`test_the_model_keeps_precision_the_display_throws_away` enforces this. Two runs
whose delivered concentrations differ by an amount four orders of magnitude
smaller than the display resolution must reach states that differ. They must still look
identical on the display.

That test is worth more now than when it was written, not less. While the
solver error was close to the readout's resolution, "the model keeps more
precision than the display shows" was a small claim. Under the exact step the
gap is nine orders of magnitude. The rounding in the readout is now the only
place where resolution is lost anywhere between a slider and a pixel.

**What the last digit does not cover, and what it still does.**
~~The error is a systematic sequencing bias rather than noise, and its sign is
opposite at the two ends of the transfer chain. A *difference* between two of
the six readouts therefore carries the sum of two displacements, up to 1.8
times the error in either reading alone, worst measured at 0.030 percentage
points, so the numeric gap between two readouts is the least certain thing on
the display.~~ **Withdrawn 2026-09-06 (`PL-GS5X`).** That bias was a property
of the operator split's sub-step ordering. The exact step drives no compartment
from an upstream value that has already moved. So there is no displacement
with a sign, and a gap between two readouts is no less accurate than either of
the readings it is taken from. § "Independent-solution test" above records the
withdrawal in full.

The comparison that the interface actually invites is therefore no longer at
risk from the solver, and that is a measurement rather than an assurance. The
six readouts are placed in one row, where seven panels fit it, to be read
*ordinally*: the circuit leads the alveoli, and the alveoli lead the tissues.
§ "The row has a width condition, and both arguments above rest on it" below
states what happens when seven panels do not fit. An ordinal reading is
corrupted only if the error can invert which of two compartments is displayed
as higher. The measurement covered every trajectory in "Independent-solution
test" and all three agents. It compared every pair of the six readouts at every
step, which is 1 485 000 pair comparisons. The shipped and reference solutions
**never** disagree about the displayed ordering, anywhere, at any gap. Since
`PL-0M7K` the readings compared are those of the shipped `format_percent`, and
the count is still zero (re-measured 2026-10-17). Under the split the two
solutions disagreed on the worst reachable trajectory. They disagreed for 0.2 s
of a 900 s run with sevoflurane and 1.7 s with desflurane, at gaps up to 1.73
counts of the last displayed digit.
<!-- not-restated: 0.2 s, 900 s -->

That is a measurement on one platform rather than a guarantee. The arithmetic
behind it explains why the gate keeps a threshold rather than asserting zero.
Rounding to a fixed number of decimals is monotone, so it can never produce an
ordering opposite to the raw one. An inversion therefore needs the two
solutions to be genuinely reordered. That needs a true gap smaller than the sum
of the two displacements. The widest pairwise differential measured anywhere is
$`1.1\times10^{-12}`$ in fraction. True gaps that small do occur while two
compartments cross. So an inversion is arithmetically reachable there, even
though none was observed.

That is why the interface marks nothing here. A reader who compares the
readouts the way the row is designed to be compared cannot be misled by solver
error. A reader who subtracts two of them is doing arithmetic that the
interface does not perform, and the paragraph above is the disclosure for that
reader. Two tests enforce the claim, and each can fail on its own half of the
path from the model to the readout.
`test_exact_step_matches_the_independent_solution_everywhere` bounds the
solver's error. `test_format_percent_preserves_order` in
`tests/unit/test_formatting.py` checks that the shipped formatter never shows a
higher fraction as a lower percent (`PL-0M7K`). It checks this across the
formatter's "<0.01%" reading below the resolution, and on both sides of every
display-count boundary. Together the two tests mean that no inversion can occur
at a true gap above twice the tolerance. Twice the tolerance is
$`1.0\times10^{-7}`$ counts, against the 3.0 counts that the split's bound
allowed. `test_displayed_ordering_reverses_only_at_a_crossing` is the
trajectory measurement quoted above. It enforces that same threshold, but it
cannot fail unless one of the two tests fails. So it is the measurement and not
the evidence.

**Why the resolution is uniform rather than per-compartment.** The six
readouts sit together and are read comparatively. They sit in one row where
seven panels fit the window, and in a grid below that width. The reason for
showing them together is that a reader can see the circuit lead the alveoli,
and the alveoli lead the tissues. Different decimal counts across those tiles
would put different magnitudes at the same glyph position. A value scanned
rather than read would then be misjudged by a factor of ten. That is a
property of the reading task, and it is true whatever the solver does.

A second argument used to be offered beside it. It said that the split's error
was itself bounded in absolute percentage points, and stayed within a factor of
four across the four fast compartments. So one absolute resolution expressed
that error directly. That argument is withdrawn with the split. The
replacement is that **parameter uncertainty is also absolute in its effect
across the row**. The one-SD displacements tabulated above run from
$`8.7\times10^{-4}`$ to $`6.8\times10^{-2}`$ percentage points across all six
compartments and all four coefficients. That is a spread of less than two
orders of magnitude, on a row whose *values* span four. A single absolute
resolution is the direct expression of that spread. It is set by the
compartments where the displacement is largest, and it is conservative in the
ones where the displacement is smaller.

**The row has a width condition, and both arguments above rest on it.** The
interface is responsive. Until now this section stated the one-row arrangement
without qualification, which a reader is entitled to take as a commitment.
`readout_columns` in `src/anesthesia_sim/app/dashboard_frame.py` sets the
row's column count from its width, and every panel spans exactly one column.
`test_every_readout_reserves_a_qualifier_line_and_an_equal_column` enforces
both. So the seven panels sit **side by side wherever seven panels' reserved
widths fit the row, four per line where seven do not, two where four do not,
and one below that** (`READOUT_ROW_LADDER`). The reservation is the widest
value each column can show, measured in the rendering font (`PL-3355`). The
clock's column reserves its widest elapsed form. Each compartment's column
reserves its widest percent and MAC multiple, so the clock's width costs no
other column. The widths at which the row steps down belong to the font and
the display scale rather than to this document. On the offscreen font that the
test suite renders with, measured on 2026-10-18, the row is seven across from
1005 logical pixels, four from 591 and two from 310.
`test_the_readout_row_reflows_where_its_panels_stop_fitting` reads those widths
from the row rather than asserting them. Those figures are an example of the
rule, not a specification of it. The Flet build recorded 1200, 992 and 768 as
a rendered measurement at Flet's sizes (`PL-8M05`). The port derives the same
ladder from what it draws with. So it asserts no pixel figure that a font or a
HiDPI scale would falsify.

The two arguments are not affected equally, and neither is withdrawn.

- **The ordinal reading is the one that weakens.** Below the seven-across
  width the six readouts are on two or more lines. The comparison that the row
  invites stops being a single glance and becomes a scan across the lines. The
  *measurement* behind the claim is untouched. It compares displayed values,
  not their positions, and the 1 485 000 pair comparisons say nothing about
  layout. So what narrows is the claim that the arrangement invites the
  comparison, not the claim that the ordering is faithful.
- **The uniform resolution still applies at every width**, and the reflow does
  not weaken its argument. That argument is that differing decimal counts would
  put different magnitudes at the same glyph position. The grid aligns value
  glyphs within a column at every rung. So a reader scanning two panels
  compares them against a common position, whether they are side by side or
  stacked. The argument never rested on the six being in a single line.

**In practice the row opens at the widest rung the screen affords, because
the window opens maximized.** `src/anesthesia_sim/app/main.py` shows the
window with `showMaximized()` over a normal geometry of
`WINDOW_SCREEN_FRACTION` of the screen's available area, centred (`PL-005`,
with the Qt port). So the row gets the screen's available width less the
window's own chrome, rather than eight tenths of it. That is what pays for
seven across on a 1366 px laptop, one of the commonest screen widths there is.
At the fraction, on the offscreen font above, the row on that screen fell 21
logical pixels short of the seven-across width. A 1093 px window carried a
1047 px row, while the row's 1068 px wanted a window of about 1114 px. So that
machine opened on four columns while a slightly wider one opened on seven. The
conditional arrangement was then the ordinary case rather than the resized
one. Maximized, the same screen offers the row about 1320 px, and a 1280 px
screen offers it about 1234 px, so both open on seven. These figures are again
an example of the rule on one font rather than a specification of it (project
owner, 2026-09-27, ratified, over raising the fraction to 0.85, which clears
1366 px at one font and leaves a 1280 px screen on four columns; `PL-Z4K6`).
Maximized is not full screen. The title bar and window controls stay, and on
macOS it is the zoomed window. So `PL-005`'s refusal of a full-screen start
does not apply to it. Maximized is also the reference's own default window
state (`docs/interface-provenance.md` § "Adopted"). A reader who un-maximizes
gets the fraction back and meets the ladder above as before. A screen too
narrow for seven across at its full width still opens below the widest rung.
The maximized window changes which rung a screen affords, never the rule that
decides it. Until the Qt port the window opened full screen, and the widest
breakpoint was the only one a reader met without resizing.

**The row sits in the unconditional region, so its rung follows that region
and never an Area** (`PL-JSY5`, 2026-10-18). The readouts are in
`SimulationView.unconditional_region`, above the layout container that the
Areas replace (§ "Minimum displayed outputs" -> "What this list requires once
the layout is the reader's";
`test_no_unconditional_value_sits_inside_the_layout_container`). So a split, a
join, a border drag or a Workspace switch never changes the width that the row
is laid out at. Two things do change it: the window's width, and how the region
divides that width. Since `PL-J8K2`, the region holds the runs' rows in a left
column and the control-change record in a right column. Since `PL-F2YS` the
two columns take 0.82 and 0.18 of the width. Those were the shares of the chart
panel's Area and the sidebar's Area in the layout that the dashboard opened on.
So the record was as wide as the sidebar beneath it, as `PL-J8K2` Q3 ratified.
Since `PL-2KXB` the dashboard opens on the shipped Workspaces, whose Areas
divide the width differently. The region keeps its own shares, because a
Workspace switch must not change the width that the row is laid out at. The
left column never narrows below its own minimum width. At whatever width that
leaves, the reservation rule above (`PL-3355`) still applies. Every rung lays
each panel out at its full reserved width, so no value is wrapped away from its
unit.
<!-- not-restated: 0.18 -->

**Measured 2026-10-18: a 1366 px window opens on seven again, with one run or
two.** On the offscreen font, a 1366 px window gives the region 1320 px. The
record column takes 235 px and the readout column 1073 px. That is 68 px more
than the 1005 px that seven across needs. Two runs share that one row
(`test_two_runs_share_one_readout_block_whose_values_name_their_runs`). So the
outcome recorded above for a 1366 px screen also applies in compare mode
(`test_a_1366_px_window_opens_one_run_s_readout_row_on_seven_columns`,
`PL-F2YS`). Before `PL-F2YS` the record took a 3:1 share, and the readout
column was 3 px short of seven at one point in the build of v0.6.0. At 235 px
the longest control-change lines no longer fit on one line. So the record
wraps them, but only after the time and after the arrow, which keeps every
value beside its unit (`wrapping_between_parts`).

**Why not a significant-figures rule.** A significant-figures rule gives the
smallest values the most decimal places, and the small values are exactly
where this model supports the least. The evidence for that is no longer the
solver. Under the exact step the sparsely filled compartments carry at most
$`2\times10^{-4}`$ relative error anywhere in the first ten seconds of a run,
and $`8\times10^{-11}`$ at ten seconds itself. The evidence is the parameters.
Their measured SDs are 3.9% to 6.4% of the mean and are *relative*, so they
apply undiminished to a compartment holding a thousandth of a percent. Three
significant figures on the fat fraction would imply a relative resolution of
0.1% on a number whose parameters are known to about 5%. That over-claims by a
factor of fifty, and it does so most severely in the readouts where a reader is
least able to notice.
<!-- not-restated: 5 % -->

**Why not the 0.1 percentage points clinical monitors report.** Agent
monitors display end-tidal and inspired concentrations to a tenth of a
percentage point. The circuit and alveolar readouts alone would be well
matched to that. This simulator, though, displays compartments that no monitor
shows, and the lower-limit argument above is the answer. At monitor resolution
the sevoflurane and isoflurane fat fractions read `0.0%` for an entire hour,
and muscle reads `0.0%` for its first 2.9 to 14.8 minutes. Rounding to
clinical convention would erase the slow-compartment wash-in, which is the
reason for displaying those compartments at all. A resolution of 0.01
percentage points is the coarsest that keeps every displayed compartment
legible. It is also close to what the parameters support. That closeness is a
coincidence worth naming, not a second constraint meeting the first, since the
two are measured entirely independently.

**Why a below-resolution value is marked rather than shown as zero.** Even
at 0.01 percentage points the slow compartments start below the last digit.
At 1 MAC with default flows, muscle first rounds to a nonzero value at 57 s
(desflurane), 125 s (sevoflurane), and 190 s (isoflurane). Fat first does so at
237 s, 780 s, and 1474 s respectively. Displaying `0.00%` across those
intervals would state that the compartment holds no agent, which the model
does not say. The model says that the compartment is filling, below what the
display resolves. `<0.01%` states exactly that. It also keeps `0.00%` meaning
the one thing it should: nothing has arrived yet, as before a run starts. This
is the distinction between a value the model asserts and a value the display
cannot carry. The interface must preserve that distinction rather than add a
decimal that the model cannot support.

A negative fraction is deliberately excluded from the below-resolution form.
No `Fraction` can hold a negative value, and since `PL-LLMN`
(§ "Concentrations") that includes minus zero. So a negative value that
reaches the formatter means that something upstream is wrong. The formatter
refuses it rather than absorbing it into a plausible small positive reading.
Until `PL-4R3W`, the formatter rendered a negative value with its sign, as the
anomaly it is. Refusing it is the stronger form of the same rule.

**How this section changed when the solver did, stated so a reader comparing
versions is not misled.** Through v0.4.2, this section carried a paragraph
headed "Why parameter uncertainty does not govern this". That paragraph made
two claims. First, the per-step solver error set the decimal count. Second,
parameter uncertainty displaces a whole trajectory rather than limiting the
resolution within a run, so it was disclosed in "Parameter provenance" instead
of being encoded in a decimal count. The second claim is still true, and it is
kept above. The first is not, because there is no longer a per-step solver
error large enough for any readout to express. So the roles have swapped.
Parameter uncertainty now sets the upper bound on the decimal count. The
distinction between a displaced trajectory and the resolution within a run now
explains why that bound is loose enough to permit a digit finer than one SD,
rather than forbidding it.

Two things did *not* change, and neither depended on the solver. One is the
resolution that ships. The other is the reason a reader may not treat that
resolution as a claim about a patient. Nothing in this document has ever
permitted that second reading. "Known limitations" is where the rule is
stated: no displayed value may be read as accurate to its last digit as a
prediction about a patient. A displayed value is accurate to its last digit as
a statement about this model with these parameters.

**Precision elsewhere in the interface, and why it differs.** Simulated time
is displayed to 0.1 s, which is exactly `SIMULATION_STEP_S`. The display
resolves one step and no finer. Every recorded control change is stamped at
that same resolution, so the timeline and the clock never show one time in two
different forms. The chart's own time axis is labelled differently, and
deliberately. Each label is a compound duration that carries its own units. It
is no finer than the whole second on which every tick of the ladder falls. The
axis labels a span that a reader scans, not an instant that they read off. A
tenth of a second on every label would spend width on a digit that is zero at
every width the ladder offers. "The chart's time base" gives the form and the
reason it differs from the clock's. Fresh gas flow, alveolar ventilation and
cardiac output are displayed to 0.1 L/min. This matches the resolution of the
flow controls that set them. A slider and the readout beside it show one
quantity. So the Qt sliders are integer-valued, with steps at the display
resolution: 0.1 L/min for the three flows, and 0.01 percentage points for the
delivered dial. The value applied to the model is exactly the value printed
beside the control (`PL-25KS`). If a control could apply a value that its own
label rounds away, a reader could not tell which value is the setting in
force.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**The agent-accounting panel's three amounts are displayed to 0.1 L, and its
two residual lines as the power of ten each lies below, because they answer
different questions** (`PL-TG60`, 2026-09-15; the residuals' form project
owner, 2026-10-03, ratified, over one significant digit, over the nearest
decade and over keeping the sign, `PL-3PJZ`). The residual lines are a
numerical diagnostic. Their job is to make a residual of order 10⁻¹² L visible
against amounts of order 1 to 100 L. No fixed decimal count can do that.

**The decade is the only digit a passing residual has.** A passing residual is
the rounding left over from summing the initial, delivered, exhausted and stored
amounts. So its mantissa and its sign are set by the order in which the
arithmetic ran, not by anything modelled. A correct change in the last bits
redraws them. `PL-2MD9`'s change to the propagator is the measurement.
`PL-KXW1` records an 81-run protocol: three agents, three dial pairs, three
cardiac outputs and three fresh gas flows. Each run is forked at minute 30
with the dial set back, and its branch is played for 30 minutes. The protocol
was replayed on the v0.5.21 tag and on v0.5.22. A branch's residual moved by up
to 5.9 times between the two trees. There were 2,511 branch samples. The two
trees' residuals read differently at four significant digits on 1,975 of them,
at two on 634, at one on 154, and at the decade on 22. Those 22 are the
samples where the two trees' residuals fall on either side of a power of ten.
Every residual was below 2.1 × 10⁻¹¹ L, and every check passed in both trees.
A run's own path, which `PL-2MD9` left bit-identical, read identically in
every form. So each line prints `<1e-13 L`. This is the smallest power of ten
that the magnitude lies strictly below, computed from the float's exact value.
Here `<` means what it means on the amounts. The sign is dropped along with the
mantissa, so both lines read alike. The sign means something only in a check that fails.
Then the run halts, and the failure notice prints the signed values to six
figures. Exactly zero reads `0 L`. `format_agent_residual` defines the form,
and `tests/unit/test_formatting.py` pins it. The test includes the pair of
strings `5.601e-14 L` and `5.609e-14 L`, which the two trees printed for one
sample.
<!-- not-restated: 2.1 -->

The amounts
are read against each other, delivered against exhausted plus stored. They are
also read against a reader's sense of scale. So they take one uniform
resolution, on the same argument as the readouts above. The readouts'
derivation perturbs one stored coefficient by one published SD. Doing the same
here moves the exhaust total by 0.016 to 0.042 L at 3600 s, and by 0.18 to
0.23 L at the 24 h supported limit. By agent, the shifts are sevoflurane 0.024
and 0.19 L, isoflurane 0.016 and 0.18 L, and desflurane 0.042 and 0.23 L. The
blood:gas coefficient dominates throughout. These shifts were measured at
1 MAC with the reference adult's flows. One count of 0.1 L therefore lies
between a quarter of an SD and six SDs across the whole supported span. That is
inside the band the readouts' derivation admits. A count of 0.01 L, by
contrast, falls to a fiftieth of an SD by 24 h. Until `PL-TG60`, the panel
printed six decimals. They asserted a millilitre of a quantity that the
parameters place only to within a decilitre. This section justified the six
decimals by saying that the amounts made the residual visible. That
justification did not hold. A residual twelve orders of magnitude below the
last printed digit is visible only on the lines that print its order of
magnitude. Delivered agent carries no parameter uncertainty, because it is the
dial times the flow times the time. It takes the same resolution so that the
three amounts read at one scale. The panel states the unit as this document
states it, litres of equivalent pure agent gas, because a bare "L" beside an
anaesthetic agent invites a reader to take it as litres of liquid.
`AGENT_VOLUME_DISPLAY_DECIMALS` stores the count, `format_agent_volume`
defines the form, and `test_agent_amounts_precision` pins both. Precision in
this interface is set by what each number is for, and the rule above governs
the clinical readouts.
<!-- not-restated: 0.18 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The chart plots the same percentages on a shared linear axis that runs from 0
to 3 ×MAC of the running agent. A second axis on the right shows the identical
coordinate in MAC multiples. The chart's resolution is set by pixels rather
than by decimals, and it is coarser than the numeric readouts throughout. A
trace is where a reader reads a *shape*. Every number the chart offers is
rendered at the resolution above, not at the axis's resolution. Those numbers
are the readout row, and the hover readout that § "The chart's hover readout: what the
tooltip may show" derives below. The MAC axis is labelled on round
MAC values rather than on round percentages. It uses half-MAC steps, which the
fixed 3 ×MAC range gives for every agent. So a gridline that a reader learns
under one agent means the same thing under the next. § "The chart's
vertical range is denominated in MAC, and fixed" above explains why the range
is what it is. The chart's horizontal extent is the selected time base rather
than a fixed span, so the reader chooses the seconds per pixel. "The chart's
time base" explains how a width is chosen and how it is ruled.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

`app/formatting.py` is where this section is put into code. It holds the
resolution as a single constant. From that constant it derives the formatter,
the below-resolution marker, the MAC decimal count and the MAC axis placement.
It imports no toolkit, so the functions this section reasons about can be read,
cited and tested without loading the interface.
`tests/unit/test_formatting.py` pins the constant and every string the
formatter produces. `tests/unit/test_dashboard_frame.py` tests the end-to-end
path: a real controller, a real step, and the string on the panel.
`app/dashboard_frame.py` reads the constant to set the delivered dial's slider
position. That is why the value the slider applies and the readout beside it
cannot drift apart.

`tests/reference/test_coupled_dynamics.py` restates the same constant and
checks it against `app/formatting.py`. It does so because the ordering claim
above is a property of the rounded values. Adding a decimal would change what
that claim proves without changing anything the test reads. A change to the
resolution is a change to this section.

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
   it. The instant is given in the compound form of `format_elapsed`. The
   clock, every control stamp and the time axis use the same form.
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

## Assumptions

Version v0.1.0 assumes:

- every modeled compartment is perfectly mixed;
- each tissue group is perfusion limited, and exchanges agent only with the
  blood flowing through it. No agent passes directly from one tissue group to
  another. That direct route is the intertissue diffusion that "Known
  limitations" records as omitted;
- partition coefficients are constant;
- tissue volumes and flow fractions are constant;
- outgoing pulmonary blood equilibrates with alveolar gas;
- the alveolar gas volume is constant. Uptake removes agent from the
  compartment without removing volume from it, and no inspired flow replaces
  the gas that left. This is the assumption that excludes nitrous oxide,
  simultaneous gases, and the concentration and second-gas effects. "Alveolar
  gas" measures what the assumption costs and what lifting it would take;
- inspired gas is circuit gas. One gas-phase state, $`F_I`$, lies between the
  vaporizer and the alveoli, because there is one perfectly mixed circuit with
  no dead space and no separate limbs (see § "Model boundary");
- the breathing system is a semi-closed circle whose surplus gas valve is
  passing gas. An equal exhaust outflow matches the fresh-gas inflow at every
  instant. This is what lets one $`\dot V_F`$ be both the delivery rate and
  the removal rate (see § "Breathing circuit");
- inspired gas reaches the alveoli undiluted by water vapour. Real alveolar
  gas is saturated at body temperature, and nothing here represents that, so
  the circuit's dry gas enters the alveolar compartment unchanged. This is the
  third gas-phase condition, beside the temperature and pressure bullets
  below. The reference condition names it ("dry"), but the model does not
  examine it anywhere. "Known limitations" sizes it at 47/760 and measures
  what correcting it would cost;
- tissue venous blood equilibrates with its tissue group;
- carrier gases do not affect agent kinetics;
- temperature is constant. Every gas volume the model stores is carried at
  the one reference condition that "Agent amount" states: 20 °C and
  760 mmHg, dry. No equation here converts between ambient and body
  conditions. "Known limitations" sizes what that costs;
- ambient pressure is constant, and it is one atmosphere, 760 mmHg. Every
  concentration in this model is a fraction of that pressure, so the model is
  specified at sea level and nowhere else. The note below this list says what
  that gains and what it costs;
- there is no metabolism;
- there is no chemical degradation;
- there is no anesthetic reaction with circuit materials;
- there is no vaporizer or machine delivery delay beyond the modeled circuit;
- settings remain constant within each numerical step; and
- the selected reference patient does not change physiologically during a run.

**What one atmosphere buys, and why nothing in the model is wrong today.** A
gas-phase fraction and a partial pressure differ only by a factor of the
ambient pressure. Fixing that pressure at 760 mmHg therefore makes the two
interchangeable. $`F_A = 0.02`$ is 15.2 mmHg, and no statement in this
document has to say which of the two it means. The rest of the specification
is built on that identity. On its strength, "Concentrations" stores every
state as a dimensionless fraction, the interface displays each one as a
percent of one atmosphere, and $`\mathrm{MAC}_\%`$ divides one sea-level
percent by another.

**The delivered-concentration control is where that assumption does the most
work.** The control is a vaporizer dial rather than a modeled gas state. It is
`app/control_record.py`'s `ControlInput.DELIVERED`, and its recorded changes
carry the unit *fraction of 1 atm*. A dial position means a partial pressure,
the quantity that produces the anesthetic effect, only once the ambient
pressure is known. At 760 mmHg it means the *same* partial pressure whichever
class of vaporizer the dial belongs to. That is why this model needs no
device-class parameter, and why no equation, stored value or displayed number
here is wrong. Away from 760 mmHg the two classes diverge, and they diverge in
opposite directions. That is a limit on where this model applies rather than
a defect in it, and § "Known limitations" below records it. A later reader
should not "fix" this.

## Known limitations

This model does not model:

- a separate arterial blood-mixing compartment. Arterial blood is
  flow-limited and equals alveolar gas at every instant, which matches the Gas
  Man reference simulator's mammillary structure (see § "Model boundary");
- lung tissue and pulmonary blood. No compartment represents either, and
  together they are a store worth about a fifth of every agent's fast pool
  (the note below this list sizes it);
- a vessel-poor tissue group. Bone, cartilage, ligament, tendon and the other
  tissues with little or no blood flow have no compartment, and none of the
  three tissue groups stands for them. The note below this list gives the
  reason, which is the one the field gives;
- halothane, enflurane, ether, or xenon (isoflurane and desflurane were added
  in v0.2.0; see § "Parameter provenance");
- nitrous oxide;
- simultaneous gases;
- concentration or second-gas effects;
- absorption of agent by the breathing circuit's own plastics and rubber. The
  note below this list measures it, and the size of the effect depends
  strongly on the agent;
- vaporizer interlocks;
- switching between volatile agents;
- direct anesthetic injection;
- automated end-tidal control;
- closed-circuit operation, or any machine mode that shuts the surplus gas
  valve. In this model the exhaust runs whenever fresh gas runs. A closed
  circuit is a different conservation statement, not this one with the
  exhaust turned down ("Breathing circuit" argues this and sizes the gap);
- dead space;
- airway sampling delay;
- multiple alveolar units;
- shunt;
- ventilation-perfusion mismatch;
- diffusion limitation;
- intertissue diffusion, which is agent passing directly from a lean tissue
  into fat lying against it. This is a route between two tissues, not the
  blood-to-tissue limitation above. The note below this list measures what it
  leaves out of the fat compartment;
- uncertainty in the tissue:gas partition coefficients. Each is one
  laboratory's mean, carried as an exact value. Other laboratories report
  values for the same tissue that differ by up to 150%, and the note below this
  list says which tissues that reaches;
- metabolism;
- compound A or other degradation products;
- renal or hepatic dysfunction;
- cardiopulmonary bypass;
- ECMO;
- hypothermia;
- alveolar humidification. Real alveolar gas is saturated with water vapour
  at 47 mmHg, and the modeled alveolus holds none, so no inspired fraction is
  diluted when it reaches the alveolus. The note below this list sizes it,
  and measures what correcting it would cost;
- the difference between ambient and body conditions. Every gas volume is
  carried at the single reference condition that "Agent amount" fixes, and no
  ambient-to-body correction is applied anywhere (the note below this list
  sizes it);
- altitude, or any ambient pressure other than the 760 mmHg fixed under
  § "Assumptions". The notes below this list say what that excludes;
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

**Three of those bullets are one constraint, not three omissions**
(`PL-L2F2`). Nitrous oxide, simultaneous gases, and concentration or
second-gas effects look like three independent features to be added, and they
are not. All three are blocked by the fixed alveolar volume that
"Alveolar gas" and "Assumptions" declare, and lifting that constraint unblocks
all three at once. The distinction is worth stating because the shortcut it
rules out looks reasonable. A session scoping nitrous oxide from this list
alone would plan it as a second agent object beside the volatile agent, and
would meet the coupling late. It would then be tempted into a partial fix
whose $`F_A`$ curve is plausible but wrong by tens of percent through
induction. "Alveolar gas" carries the arithmetic that separates the two
cases, and the two standard formulations that lift the constraint.

**Lung tissue and pulmonary blood are an omitted store worth about a fifth of
the fast pool.** The gas-exchange boundary here is the alveolar gas
compartment. Arterial blood is taken to carry that compartment's partial
pressure unchanged. Nothing represents the lung's own tissue, or the pulmonary
blood in transit through it. The store was sized on round physiologic figures
while working on `PL-73G7`: 1 kg of lung tissue at a tissue:blood ratio of
1.2, and 1.8 L of pulmonary and arterial blood. On those figures the store is
worth 20.1% of desflurane's fast pool, 19.7% of sevoflurane's and 23.4% of
isoflurane's.

The store is invisible in the wash-in direction, which is why nothing before
the open-circuit diagnostic surfaced it. It equilibrates fully within about
thirty minutes, so it does not appear in $`F_A/F_I`$ at all. It acts only
early in an elimination. The figures stay where they were measured.
"Desflurane's residual, and why the parameter file was not changed" weighs
them against the other candidate explanations of one specific disagreement,
and a second copy here would be a second thing to keep true. This list carries
the magnitude, because a reader sizing what the model leaves out should not
have to find it inside an argument about one agent.

**The vessel-poor group is left out because it takes up almost no agent, and
Eger's own model leaves it out for that reason** (`PL-NX4H`). Eger grouped the
body's tissues into four groups by their capacity and their blood flow:
vessel-rich, muscle, fat and vessel-poor. His later five-compartment model
keeps the first three. It deletes the vessel-poor group "because its
contribution to uptake is considered insignificant", and adds a lung
compartment and an intertissue-diffusion compartment instead. That is
Carpenter et al. 1986, as Hendrickx and De Wolf report it on p. 163. Eger and
Saidman's review gives the physiological reason. The group is "made up of
ligaments, tendons, cartilage, bone, and other avascular tissues", and it
"does not contribute to uptake because of its minimal or absent perfusion"
(p. 1023). Gas Man, the reference implementation, also carries exactly three
tissue groups, in the Workbook's Model Parameters table on p. 168.

So the three groups here are Eger's five-compartment model without its lung
and intertissue-diffusion compartments, and the bullets on lung tissue and on
intertissue diffusion record those two omissions. The three groups hold 6.0,
33.0 and 14.5 L, which is 53.5 L in a 70 kg reference patient. Read that total
as the sum of three compartments, not as a statement of body composition. The
rest of the body, the vessel-poor tissues among it, is not a store that this
model fills or empties.
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.volume_l = 6 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.fat.volume_l = 14.5 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->
<!-- derived: 53.5 L from data/patients/reference_adult.json tissue_groups.vessel_rich.volume_l = 6, tissue_groups.muscle.volume_l = 33, tissue_groups.fat.volume_l = 14.5 -->

Nothing in this project measures what the omission costs. The case that it is
small is the perfusion argument above: a tissue that receives almost no blood
receives almost no agent over the length of any case this simulator teaches.
Hendrickx and De Wolf's p. 163 and Eger and Saidman's p. 1023 were read in
full text from the private reference corpus on 2026-10-25. Carpenter et al.'s
full text has not been read here, so the deletion is attributed to them only as
Hendrickx and De Wolf report it. The intertissue-diffusion note below gives the
full citation of all four sources.

**The circuit's own walls absorb agent, and the model's circuit is inert.**
`BreathingCircuit` solves an ideal, well-mixed volume whose walls do nothing.
Agent enters with fresh gas and leaves with the exhaust. Targ, Yasuda and Eger
measured what a real circuit does (*Anesth Analg* 1989 Aug;69(2):218–25, PMID
2764290). Their study is the companion of the tissue paper that this
project's coefficients come from. Their Table 1 gives plastic/gas and
rubber/gas partition coefficients after 6–9 weeks' equilibration, in the
order desflurane, sevoflurane, isoflurane, halothane:

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
halothane**. The size of this omission depends on which agent is loaded. That
is unusual on this list, and it is why the dependence is stated rather than
left implied. The same study measured washin and washout in a real circuit at
0.5–5 L/min inflow, and compared them with the ideal exponential. It found
that desflurane's curves "closely approximated the maximal possible
theoretical rates", while the more soluble agents lagged.
<!-- not-restated: 5 L/min -->

A reader should take two things from that, and no more. First, the authors'
own conclusion is that this absorption "should not hinder induction of or
recovery from anesthesia" for desflurane, so the simplification is defensible
rather than a defect. Second, the coefficients above **overstate** the effect
during a case. Equilibration is nowhere near complete in the hours an
anesthetic lasts, and the paper says so directly. What the model cannot show
is the early lag that a real circuit adds for sevoflurane and isoflurane,
relative to the curve drawn here (`PL-LS3H`). Adding a wall term is not
planned. It would be a second gas store with its own time constant, and no
teaching objective in `ROADMAP.md` asks for one.

**Desflurane's five-minute washout disagrees with the published human
measurement, and no admissible parameter closes it.** As a diagnostic, the
model was run with the rebreathing circuit removed. It then reproduces the
published $`F_A/F_{A0}`$ at five minutes for sevoflurane and for both
isoflurane cohorts. It washes desflurane out 2.33 published standard
deviations too *fast*. This is the one place in this repository where a
comparison against a human measurement fails in the direction that overstates
recovery. A learner who took desflurane's early washout as a physiologic
prediction would expect a faster fall than Yasuda's volunteers showed.
"Desflurane's residual, and why the parameter file was not changed" carries
what was ruled out. The candidates ruled out were the tissue and blood
solubilities, the operating point, the fast capacity this model omits, a
non-ideal lung, and both readings of the published apparatus (circuit-style rebreathing, and the
50 ml of series dead space that its methods section actually describes).
End-tidal sampling bias was also ruled out, on the evidence of a human
measurement of the end-tidal gradient. That gradient runs the other way with
solubility and reverses sign through an elimination. One hypothesis is left,
and this project cannot test it: the published value itself. The disagreement
is recorded rather than corrected, because every value that would close it is
outside what the human measurements support.

**Dead space is an omission with a known exchange rate, which is unusual on
this list.** The model ventilates the alveolar compartment continuously and
has no tidal structure, so it represents neither anatomic nor apparatus dead
space. But a *series* dead space is exactly equivalent to a reduction in
alveolar ventilation. Over one breath, the dead-space volume re-enters the
alveoli at $`F_A`$ and leaves at $`F_A`$, which nets to nothing. So a dead
space $`V_D`$ at rate $`f`$ is worth $`\dot V_A - V_D f`$ and nothing else.
"Desflurane's residual, and why the parameter file was not changed" carries
the derivation and the measurement that used it. This has two consequences
for a reader. First, the alveolar ventilation control already *is* the
dead-space control, provided the value entered is a true alveolar ventilation
rather than a minute ventilation. The interface names the control
"Alveolar ventilation" for that reason. A user who enters a minute ventilation
there has overstated gas exchange by the whole of the dead space. Second,
what this model cannot represent is not dead space but **parallel**
inhomogeneity. That means unequal ventilation-perfusion ratios across
alveolar units, which the next three bullets name and which no single
ventilation figure reproduces.

**Cardiac output and the three perfusion fractions are held fixed under
anesthesia, and a real anesthetic moves them.** $`Q`$ and each
$`\text{perfusion fraction}_i`$ are constant for the whole of a run. $`Q`$ is
a user control, and nothing else can change it. The three fractions are not a
control at all. A volatile anesthetic is itself a cardiovascular depressant.
So the model holds fixed exactly the quantities that its own subject matter
acts on, and the consequence falls on the curve a learner is reading. The
tissue time constants are $`\tau_i = V_i\lambda_{i:b}/Q_i`$, so a flow that
fell under anesthesia would *lengthen* every tissue's equilibration for as
long as the agent was being given. That direction runs against the intuition
that more agent means faster equilibration. That is why it is stated here
rather than left to the "hemodynamic response" bullet above.

**It is not modeled because the human volunteer data do not describe a
function this model could carry.** Three studies measured healthy volunteers
who were anesthetized without surgery, each against their own awake baseline:

- Weiskopf RB, Cahalan MK, Eger EI 2nd, Yasuda N, Rampil IJ, Ionescu P,
  Lockhart SH, Johnson BH, Freire B, Kelley S. *Cardiovascular actions of
  desflurane in normocarbic volunteers.* Anesth Analg 1991;73(2):143-56.
  PMID 1854029. The study gave desflurane alone at 0.83, 1.24 and 1.66 MAC to
  12 men. **Cardiac index did not change**, although stroke volume index fell
  and filling pressure rose at every concentration. This is myocardial
  depression with cardiac output maintained.
- Cahalan MK, Weiskopf RB, Eger EI 2nd, Yasuda N, Ionescu P, Rampil IJ,
  Lockhart SH, Freire B, Peterson NA. *Hemodynamic effects of
  desflurane/nitrous oxide anesthesia in volunteers.* Anesth Analg
  1991;73(2):157-64. PMID 1854030, doi:10.1213/00000539-199108000-00008. The
  study used the **same** volunteers, in the same crossover, with 60% nitrous
  oxide carrying 0.5 MAC of the total. Cardiac index now fell
  dose-dependently.
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

Read together, these studies show three things. The *sign* of the
cardiac-output change depends on the carrier gas. The dose-response is **not
monotonic**. And the effect changes with time at a fixed dose, and with the
mode of ventilation. This model has no second gas, no ventilation mode, no
surgical stimulus and no pharmacodynamic layer of any kind, so it could carry
none of those dependencies. It could only carry a monotonic, time-invariant
$`Q(\text{dose})`$, and the literature above does not show that relationship.
Teaching one would be worse than holding the flow fixed and saying so. The
case for modeling regional flow is weaker still. The measurements this
project could find of how anesthesia redistributes flow between the
vessel-rich, muscle and fat groups are largely from animals. The note below
on the fat group's perfusion gives what the human record supports, even at
rest.

**What a learner gets instead is the control.** Cardiac output is on the
interface, so a learner can reach the lesson by moving it and watching. The
lesson is that a higher output carries more agent away from the lung, stores
more of it and slows the rise of $`F_A`$. Moving the control is also how the
model's own directional gates assert this
(`tests/reference/test_sevo_patient.py`). What is absent is the *automatic*
coupling from the agent to the flow, and a reader should supply that
themselves.

**This is the model's current position, not a closed question.**
`ROADMAP.md`'s planned-milestone item 35 carries the coupling as a possible
future feature. It carries it as an *option* that a user would turn on, not as
a change to what a run does by default. The evidence above argues for that
choice, since an overlay may state its own uncertainty where a model's default
behaviour cannot. `PL-8GV5` records how this was decided. The measurements
here are a session's, and the direction is the project owner's (2026-09-13).

**The MAC divisor is a limitation of the display, and a named one.** The
second display unit divides by a tier-3 `mac_percent`, and "Delivery-limit
and MAC parameters" measures the gap. Against Mapleson's age-40
meta-analytic values, the stored sevoflurane MAC is 10% low and the stored
desflurane MAC is 10% high. A sevoflurane-versus-desflurane comparison in MAC
multiples is therefore displaced by about 22% purely by the choice of MAC
source. The direction is consistent within an agent and does not change any
curve's shape or timing. It rescales one agent's MAC axis against another's.
But the gap is larger than either source's own confidence limits. A reader
comparing two agents at "1 MAC" is comparing two doses that the primary
literature would not call equipotent to that precision. The interface
displays the divisor for exactly this reason. Moving all parameters to
primary sources is `ROADMAP.md`'s planned-milestone item 31.

**Two omissions bound the supported run length, and a third bounds the tail
inside it** (`PL-YD2V`). The first two are metabolism, in the list above, and
the fat group's flow, in the note below. Both are negligible over a case, and
neither is negligible over days. That is why a run is supported to 24 hours,
and why the step past that limit is refused rather than taken. "Supported run
length" argues for the number and gives the measured extent of sevoflurane's
metabolism. A longer run is not merely unvalidated. It increasingly displays
what this model leaves out. The fat flow counts against the number on its
depot reading, the reading on which the stored figure runs about twice too
high. On the washout reading the stored figure is at or a little below the
truth, and the note leaves the direction unsettled. So inside the span, the
fat flow's effect on the tail is an uncertainty of up to about a factor of two
in the fat trace's loading, rather than a bias one way. The
intertissue-diffusion note after it describes the third omission. Human
washout needs a fourth compartment that this model lacks. That compartment
carries the largest term in the measured curve from about hour 2-3 of
elimination to about hour 21-29. So inside the supported span, the tail is
already missing its largest measured component. All else equal, the tail
falls faster than the measurement from about the third hour. Neither omission
moves the 24 hours by itself, and the measured gap does not either.
§ "The first 24 hours of elimination against the published mean
curves" puts the shipped tail below the published mean curves from about the
seventh hour to the twenty-first, by about a third at the widest point. For
desflurane the tail is below them from 3.4 to 15.3 hours, by about half at the
widest point, near 8 hours. The shipped tail is above the curves before and
after that span. § "Supported run length" records why that leaves
the number where it is (`PL-KK1Q`).
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The fat group's flow is twice a resting depot measurement, and is where
human washout fits put it. The two human sources do not agree about which way
the fat trace errs** (`PL-HBH2`). The fat flow fraction is tier 3, like every
other parameter in the reference patient, and `reference_adult.json` carries
both comparisons. Heinonen et al. used positron emission tomography to
measure resting subcutaneous adipose perfusion in the thigh of six healthy
young women. Their measurement is close to half what the stored fraction
implies. The file's note gives both figures and the volume-to-mass conversion
between them. This model is validated against two Yasuda 1991 papers. Both
fit a five-compartment mammillary model to each volunteer's data and read the
slowest compartment as fat. Both estimate its blood flow as that
compartment's tissue/blood partition coefficient times its fitted rate
constant (*Anesth Analg* p. 319). For sevoflurane and isoflurane they found
2.4 ± 0.6 and 2.2 ± 0.5 mL per 100 mL of tissue per minute (Table 5, p. 322).
For desflurane and isoflurane they found 2.1 ± 0.4 and 2.2 ± 0.2 (Table 5,
p. 496). These figures are mean ± SD, at the fat:blood coefficients of
Yasuda, Targ and Eger 1989. The stored fraction implies 2.07, which is 0.06 of
the 5.0 L/min default cardiac output flowing into 14.5 L. The comparison
rests on no fitted volume, because flow per unit of tissue is the partition
coefficient over the time constant. This model's own stored fat solubilities
(fat:gas over blood:gas) are 52 for sevoflurane, 54 for isoflurane and 31 for
desflurane. At those values, the fitted fat-group time constants of
2,120, 2,130, 1,340 and 2,090 minutes (Table 4 of each paper) give
2.5, 2.5, 2.3 and 2.6. The intertissue-diffusion note below tabulates the same
fact from the other side. This model's fat time constant is within one
standard deviation of the fitted fat group's in three cohorts, and a little
longer than it in all four. Read as evidence about the fat group's flow, the
PET measurement puts the stored figure at about twice the truth. The washout
fits put it at or a little below the truth.
<!-- derived: 2.07 from data/patients/reference_adult.json tissue_groups.fat.perfusion_fraction = 0.06, default_cardiac_output_l_min = 5.0, tissue_groups.fat.volume_l = 14.5 -->
<!-- derived: 52 for sevoflurane from data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34.0, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 54 for isoflurane from data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70.0, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 31 for desflurane from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13.0, blood_gas_partition_coefficient = 0.42 -->
<!-- not-restated: 2.4, 2.1 -->

Neither settles it, and for different reasons. The PET figure is one depot in
one small cohort, awake and at rest. It is set against a whole-body lumped
compartment, and the differences between depots within such a compartment are
real (the Frayn and Karpe entry in the same file). The fitted compartment is an
assignment rather than an anatomy. As the caution below says, what a fit
establishes is a time constant. The fitted compartment's volume is a third to
two fifths of the fat this model stores. The analysis "only accounts for about 25 L of the
body volume" (*Anesth Analg* p. 323). The same paper's flow estimates ran too
small for the vessel-rich group and too large for muscle, compared with known
values (p. 323). The volunteers breathed nitrous oxide throughout. The terminal
time constant was fitted over days on which they had left the hospital and
exceeded basal activity between samples (p. 319). Both sources support this
much. The fat group's time constant is long compared with any simulated case,
whichever flow is right. So the fat compartment stays far from equilibrium, and
no displayed curve reaches a wrong endpoint. What moves with the flow is how
much agent fat has taken up by the end of a case. That amount sets the slow
tail of washout, and it moves by up to something close to a factor of two. A
learner may read the fat trace as a physiologic prediction rather than as this
parameter set's behaviour. That learner should treat its fat loading as
uncertain by about that much, with the direction unsettled. It should not be
read as an over-estimate, which is what this paragraph said while it weighed
the PET measurement alone. The measurement is not adopted, nothing was changed,
and the gap is recorded instead.

**Fat fills here only through its own blood supply, and human washout finds a
second, faster fat-like store that this model does not have** (`PL-WMCJ`).
Every tissue group exchanges agent with the blood flowing through it and with
nothing else (§ "Tissue uptake and return"). So no agent passes directly from a
lean tissue into fat lying against it. Gas Man omits that route too and says
so: "Inter-tissue diffusion may occur between fat and muscle; this effect has
been ignored in the Gas Man model" (Workbook, Appendix B, p. 170). Carpenter et
al. needed a fifth compartment to fit human washout in 27 of 36 data sets. The
time constant of that compartment "lies between the time constants predicted
for muscle and fat". This model is validated against two Yasuda papers. Both
found five compartments in every washout they fitted. And, "following the
suggestion of Carpenter et al.", both interpreted the fourth as "a layer of fat
that receives anesthetic from adjacent vessel-rich organs by intertissue
diffusion" (*Anesth Analg* p. 320, *Anesthesiology* p. 493). The first paper
computes the volume of that compartment on the assumption that it is fat
(p. 319). The table below gives their mammillary time constants and estimated
volumes (Tables 4 and 5 of each paper), as mean ± SD. It sets them beside this
model's fat group at the default cardiac output:

| Cohort | Fourth compartment: time constant (min) | Fourth compartment: volume (L) | Fat group: time constant (min) | Fat group: volume (L) | This model's fat group: time constant (min) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sevoflurane, Anesth Analg 1991;72:316-24 | 377 ± 123 | 2.5 ± 0.6 | 2,120 ± 690 | 4.1 ± 3.0 | 2,528 |
| Isoflurane, Anesth Analg 1991;72:316-24 | 383 ± 119 | 3.0 ± 0.7 | 2,130 ± 680 | 5.1 ± 4.1 | 2,603 |
| Isoflurane, Anesthesiology 1991;74:489-98 | 435 ± 131 | 5 ± 2 | 2,090 ± 230 | 6 ± 3 | 2,603 |
| Desflurane, Anesthesiology 1991;74:489-98 | 273 ± 88 | 6 ± 3 | 1,340 ± 230 | 5 ± 3 | 1,496 |

**So the fat trace is the fitted fat group, and the fourth compartment is what
is missing.** This model's $`\tau_i = V_i\lambda_{i:b}/Q_i`$ for fat is within
one standard deviation of the fitted fat group's time constant in three
cohorts. In the fourth cohort it is 2.2 standard deviations above it. It is 5.5
to 6.8 times the fourth compartment's time constant. Nothing in this model has
a time constant on that compartment's scale, because the muscle group
equilibrates in 85 to 135 minutes. So whatever the compartment is, it has no
counterpart in this model. Leaving it out biases three things. Each bias is
derived from that structure rather than from a run:

- **Fat holds too little agent.** Suppose the fourth compartment is fat at
  this model's stored fat solubility. Fill it and the fat group from a constant
  arterial partial pressure. Then it takes up 0.9 to 2.2 times as much agent as
  this model's whole fat group over any case from half an hour to four hours.
  Within the studies' own fits, it takes up 2.6 to 5.6 times as much as the
  fitted fat group. The two ranges differ because the fitted volumes are too
  small. The analysis "only accounts for about 25 L of the body volume"
  (*Anesth Analg* p. 323). So the size is an order of magnitude and no more.
  The missing store is as large as the modelled fat group's uptake or larger.
  It is not a small correction to it.
- **The fat trace draws the slow fat alone.** On the fitted time constants,
  fat lying against well-perfused tissue is four to six and a half times higher
  than the trace, as a fraction of the arterial partial pressure. That holds
  throughout a case of that length. After an hour, that fat is at 13 to 20% of
  arterial, against the trace's 2.3 to 3.9%. It still stays below the lean
  tissue feeding it, because agent moves down that gradient into the fat.
- **The late washout loses its largest measured term.** The published mean
  hybrid coefficients are in Tables 1 and 2 of each paper. On them, after a
  30-minute administration, the fourth compartment's term becomes the largest
  in the measured washout at 1.8 to 3.1 hours. It stays the largest until 20.7
  to 29.4 hours. That is inside the 24 hours that a run is supported for
  (§ "Supported run length"). All else equal, leaving the store out makes the
  modelled tail fall faster, and it does. The shipped tail was measured against
  the mean curves themselves (§ "The first 24 hours of elimination against the
  published mean curves", `PL-KK1Q`). It runs below them from about the seventh
  hour until about the twenty-first. At the widest, near hour 13, it is a third
  below. For desflurane it is below from 3.4 to 15.3 hours, and by half. With
  the apparatus taken away, the model's tissue return alone is a third to a
  half of the mean curve between hours 8 and 13. In the shipped condition the
  gap starts later than the third hour. The reason is that the rebreathing
  circuit and the muscle group's slow return hold the tail above the curve
  until the seventh hour (`PL-95NW`). The size is known to about a factor of
  two, which is the fourth compartment's own between-subject spread.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Eger and Saidman's review draws the same compartment, and names a fourth
bias** (`PL-FBY3`). Their Table 3 (p. 1024) gives intertissue diffusion a group
of its own, "a subset of the FG". That group is 2.9 L, where the fat group is
14.5 L. Its time constants are 230, 412 and 396 minutes for desflurane,
sevoflurane and isoflurane, against bulk fat's 1,226, 2,198 and 2,114. Those
figures are the Yasuda fits, cited as such. Each lies within one standard
deviation of the matching fitted compartment in every cohort above. So they
restate the table rather than add to it. The fourth bias is in the lean tissues
that feed the store. Part of the intestine, liver, kidney and heart, and part
of the muscle and skin, "are slower to reach equilibrium because anesthetic is
continuously lost to adjacent fat". And 50 minutes into desflurane, "[w]ere it
not for losses by intertissue diffusion, the desflurane partial pressure in the
MG would reach 74% of the partial pressure delivered to it from the lungs"
(p. 1025). On that reading, this model's muscle trace runs ahead of the tissue
it represents. Yasuda et al. suggest that the route may also enlarge the
apparent delivery to muscle from the vessel-rich organs beside it (*Anesth
Analg* p. 323). That acts the other way, and nothing here says which effect
wins. The brain is spared. The review draws it apart from the rest of the
vessel-rich group "for reasons related to intertissue diffusion" (p. 1022).
This model has no effect-site compartment and parameterises its vessel-rich
group as brain (§ "v0.2.0: isoflurane and desflurane"). So the vessel-rich
trace is the one a learner takes to be the brain, and it is the one this bias
spares. A route added later that drew its loss from that group would slow it,
contrary to the review.
<!-- not-restated: 14.5 L -->

**Eger and Saidman put the effect on late recovery rather than on emergence**,
in the review whose title names the route. Agent stored this way "returns to
the circulation to delay recovery in normal-weight and obese patients,
particularly with more soluble anesthetics. However, the increased anesthetic in
fat occurs at a lower partial pressure and thus might not influence emergence
materially" (p. 1032). That is the direction described above: what the model
misses is the tail, not the early fall. The review's emphasis is obesity, which
this model's one reference adult does not represent.

**Two cautions keep this a limitation rather than a missing parameter.** The
first is that the route and its size rest on different evidence. The route has
been measured outside Eger's group. In two dogs after 80 minutes of halothane,
perirenal fat sampled against the kidney held 20 and 35 times the
concentration of fat sampled far from it. Its tension was "comparable to the
arterial tension instead of to the very low tension to be expected if the fat
had received halothane only from its own blood supply" (Allott et al.,
p. 289). Eger and Saidman cite that as the direct demonstration (their ref 8).
Even so, they call their own group's washout fits "the most convincing
evidence" (p. 1025). The size has not been measured that way. Their
"approximately 30% of the anesthetic taken up" and their time constants of 200
to 400 minutes (p. 1025) cite Carpenter et al. and the two Yasuda papers. Eger
is an author of every one of those papers, so the figures restate the fits
rather than confirm them. Allott et al.'s own case for lean tissue losing agent
to fat "depends almost entirely on the improved fit to femoral venous tensions"
(p. 290). And what a fit establishes is a time constant, not an anatomy. The
Yasuda authors write that intertissue diffusion is what "we believe provides
the explanation for the fourth compartment" (*Anesth Analg* p. 323). Hendrickx
and De Wolf quote Hull as saying that assigning a tissue to a fitted
compartment is "ill-founded because parameters of the fit to the uptake data
contain no information that might support such assumptions". They add that
compartment parameters related to cardiac output and demographics in no
straightforward way. So, they conclude, correlating them with tissue volumes and
blood flows "should be done with care, if at all" (*Modern Anesthetics*, pp. 165–66). The
second caution concerns the fat-perfusion note above, which leaves the
direction of the fat group's own error unsettled. On its PET reading, the fat
group already holds too much agent, which acts the other way from this
omission. On its washout reading, the fat group holds about what the fitted fat
group would. Nothing here measures whether the two cancel, and neither may be
read as correcting the other.

**Nothing in `ROADMAP.md` plans a fourth tissue compartment, and the one paper
here that approximated the route warns against the shortcut.** Allott et al.
matched their dogs by giving fat more of the cardiac output, or by giving lean
tissue a higher solubility (Table I, p. 281). They warn that such mimicry is
"bound to fail to varying degrees in other circumstances". In recovery,
"metabolism will still remove halothane from the circulation … whereas extra
fat perfusion will eventually return halothane to the circulation". And with a
low fat/lean partition coefficient "the tension gradients for diffusion will be
less". Each circumstance might be matched by a distortion of its own, but "the
only general solution is to build a more elaborate model which incorporates
direct representations of metabolism (which would be straightforward) and
intercompartment diffusion (which would be more complex)" (p. 290).

The time constants in the last column, the ratios and the crossing times were
computed on 2026-09-26 from the published means above and this model's stored
parameters. The sources follow, and none of them is the authority for a stored
value:

- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Liu J, Laster M, Taheri S,
  Peterson NA. *Comparison of kinetics of sevoflurane and isoflurane in
  humans.* Anesth Analg 1991;72(3):316-24. PMID 1994760,
  doi:10.1213/00000539-199103000-00007. **Full text**, read from the private
  reference corpus 2026-09-26: the compartment assumptions on p. 319, the
  interpretation on p. 320, Tables 1, 2 and 4 on p. 321, Table 5 on p. 322,
  and the volume and muscle remarks on p. 323. It studied seven volunteers,
  with 30 minutes' administration and six to seven days' elimination.
- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Johnson BH, Freire BA,
  Fassoulaki A. *Kinetics of desflurane, isoflurane, and halothane in humans.*
  Anesthesiology 1991;74(3):489-98. PMID 2001028,
  doi:10.1097/00000542-199103000-00017. **Full text**, a scan with no text
  layer, read as page images from the private reference corpus 2026-09-26: the
  interpretation on p. 493, Table 1 on p. 494, Table 2 on p. 495, Tables 4 and
  5 on p. 496. It studied eight volunteers, with 30 minutes' administration and
  five to seven days' elimination.
- Carpenter RL, Eger EI 2nd, Johnson BH, Unadkat JD, Sheiner LB.
  *Pharmacokinetics of inhaled anesthetics in humans: measurements during and
  after the simultaneous administration of enflurane, halothane, isoflurane,
  methoxyflurane, and nitrous oxide.* Anesth Analg 1986;65(6):575-82. PMID
  3706798; PubMed records no DOI. **Abstract read**, through PubMed
  2026-09-26: nine patients, 2 hours' administration. The abstract does not
  name intertissue diffusion. The Yasuda papers credit that reading to this
  paper, whose full text has not been read here.
- Eger EI 2nd, Saidman LJ. *Illustrations of inhaled anesthetic uptake,
  including intertissue diffusion to and from fat.* Anesth Analg
  2005;100(4):1020-33. PMID 15781517, doi:10.1213/01.ANE.0000146961.70058.A1.
  **Full text**, read from the private reference corpus 2026-09-27: the brain
  drawn apart on p. 1022, Table 3 on p. 1024, the lean-tissue losses, the
  evidence and the 30% share on p. 1025, and recovery on p. 1032. It is
  a review, which is how PubMed classifies it. It is ranked tier 3 because its
  figures "illustrate concepts but are not necessarily precise (quantitative)
  reflections of the kinetics" (p. 1020).
- Allott PR, Steward A, Mapleson WW. *Pharmacokinetics of halothane in the
  dog: comparison of theory and measurement in individuals.* Br J Anaesth
  1976;48(4):279-95. PMID 1275995, doi:10.1093/bja/48.4.279. **Full text**,
  read from the private reference corpus 2026-09-27: the design on p. 279,
  Table I on p. 281, and the discussion on pp. 289-90. Seven dogs were given 1%
  halothane for 80 minutes. The perirenal-fat samples are from two further dogs
  of another series (p. 289). The paper is Eger and Saidman's ref 8, and it has
  no author in common with their refs 3-7.
- Perl W, Rackow H, Salanitre E, Wolf GL, Epstein RM. *Intertissue diffusion
  effect for inert fat-soluble gases.* J Appl Physiol 1965;20(4):621-7. PMID
  5838712, doi:10.1152/jappl.1965.20.4.621. The Workbook lists it as reference 32
  and prints the year as 1964. It is also Eger and Saidman's ref 9, which
  they credit with suggesting the effect "40 yr ago" (p. 1025). Allott et al.
  credit a 1963 chapter of Perl's with first suggesting it "on theoretical
  grounds" (p. 289). PubMed returns "[Abstract not available]". Neither text
  has been read, so nothing is taken from either.
- Philip JH. *Workbook for Gas Man®*, Appendix B, pp. 169-70, and Hendrickx
  JFA, De Wolf A, *Special aspects of pharmacokinetics of inhalation
  anesthesia*, Handb Exp Pharmacol 2008;(182):159-86, PMID 18175091,
  doi:10.1007/978-3-540-74806-9_8, pp. 163 and 165-66. Both were read from the
  private reference corpus on 2026-09-26, and Hendrickx and De Wolf's
  pp. 165-66 were read again on 2026-09-27. Both are tier 3, and
  `docs/references/README.md` carries their entries.

**The tissue:gas coefficients are one laboratory's means, and other
laboratories disagree with them by up to 150% in some tissues** (`PL-H536`).
Hendrickx and De Wolf state the general case: "Tissue solubilities vary up to
150% between authors (Yasuda et al. 1989), and the tissue homogenates used to
determine these coefficients may not represent in vivo conditions" (p. 165).
The 150% is not spread evenly across the tissues this model uses. Yasuda, Targ
and Eger, whose measurements the agent files store, compare their own values
with two other laboratories on p. 373. Fiserova-Bergerova et al.'s values for
sevoflurane, isoflurane and halothane were similar to theirs for brain and for
fat, except halothane's fat coefficient, which was 65% greater. They were 115%
to 150% greater for kidney and 10% to 30% less for muscle. Those values are
Fiserova-Bergerova, Tichy and Di Carlo 1984, Yasuda's ref 8. Lowe's isoflurane
values were 50% to 75% greater. The authors could not explain the
differences.

A third published set agrees less well (`PL-VPF8`). Baker and Farmery's 2011
review prints tissue:blood coefficients from Fiserova-Bergerova and Diaz 1986
beside the set that matches this model (Table 2, p. 572). On the tissue:blood
scale, that set puts sevoflurane's fat coefficient at 71.7, 37% above this
model's 52.3. It puts isoflurane's muscle coefficient at 1.71, 51% below this
model's 3.46. Its vessel-rich figures are 28% above this model's for both
agents. Part of each gap is the set's own blood:gas values, 0.6 for
sevoflurane and 1.4 for isoflurane. The set may not be a measurement.
According to its PubMed abstract, the 1986 paper measured coefficients only
for water-soluble solvents such as acetone and the alcohols. It then fitted
equations that predict any substance's tissue coefficients from its blood:gas
and fat:gas values. Baker does not say which of the anesthetic figures were
measured and which predicted. The set has no desflurane values.

So for sevoflurane and isoflurane, the brain and fat values that this model's
vessel-rich and fat groups use were reproduced by one other laboratory, in
1984. The 1986 set does not reproduce them, and it may be a prediction rather
than a measurement. Yasuda, Targ and Eger make no such comparison for
desflurane. The 150% is the kidney, which this
model does not parameterise on its own (§ "Parameter provenance" records that
the vessel-rich group is Yasuda's brain value). Muscle is where the model's
coefficient is least certain, on two counts. Both other sets put muscle
lower, and Yasuda's own muscle measurements spread the most. Their
standard deviation is 43% of the mean for sevoflurane (2.38 ± 1.03), 45% for
isoflurane (4.40 ± 1.97) and 37% for desflurane (0.94 ± 0.35), against 17% to
19% for fat. Eger and Saidman's Table 1 makes the same point from the
literature as a whole. Their best figure for sevoflurane muscle is 1.7, with
1.1 to 2.4 as the range across the studies they cite (p. 1022), where the
agent file stores 2.4. A muscle group's time constant is proportional to its
tissue:gas coefficient. So taking 1.7 in place of 2.4 would shorten the
sevoflurane muscle time constant by 29%. That is the size of change a
coefficient's provenance can make to the intermediate part of every wash-in
and washout curve this simulator draws.
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4 -->
<!-- derived: 29% from data/agents/sevoflurane.json tissue_gas_partition_coefficients.muscle = 2.4 -->
<!-- not-restated: 1.1 -->

This is a limit on what the model can claim rather than a defect to fix. No
coefficient here is wrong against its cited measurement. A learner should read
the muscle and fat traces as one well-measured parameter set, and not as the
only set the literature supports. Yasuda, Targ and Eger's p. 373, Eger and
Saidman's Table 1 and Baker and Farmery's Table 2 were read in full text from
the private reference corpus on 2026-10-25, and Hendrickx and De Wolf's p. 165
on the same day. Fiserova-Bergerova and Diaz 1986 was read as its PubMed
abstract only (PMID 3721592), and the 1984 paper not at all. The Yasuda, Targ
and Eger citation is in § "Parameter provenance".

**Cardiac output does not scale with the patient, and the reference weight is
a label rather than an input.** `default_cardiac_output_l_min` is a stored
5.0 L/min. No equation reads `weight_kg`, so editing the weight changes nothing
this model computes. Two published figures sit either side of the stored value,
**and they are not evidence of the same kind.** The first is Lowe and Ernst's
own cardiac-output relation. It is the upstream source that the Gas Man
Workbook names, and it has now been read at the source. It gives
$`0.2M^{3/4}`$, which is 4.84 L/min at 70 kg. It is **derived rather than
measured**. It is Brody's 1945 interspecies oxygen-consumption allometry
divided by an arteriovenous oxygen content difference that is assumed constant
across mammals. The section § "Parameter provenance" above carries the
derivation step by step. The second figure comes from Cattermole et al. Their
686 subjects in the 50–75 kg band give a **measured** median of 5.51 L/min, in
the weight band this file's patient sits in. So the stored 5.0 is not bracketed
by two comparable observations. One side is a human measurement and the other
is an interspecies extrapolation. A reader who weighed them equally would be
weighing them wrongly. **The fixed value is kept, on the project owner's
decision of 2026-09-08** (`PL-YKSM`). The reason is structural rather than a
preference between those two numbers. The asymmetry is still worth stating,
because the number being declined is the weaker of the two.
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

A time constant is $`V_i \lambda_{i:b} / Q_i`$, and this model stores
compartment volumes as fixed litres. So scaling only the flow would make
$`\tau \propto M^{-3/4}`$. A heavier patient would then equilibrate *faster*
and a lighter one more slowly. That is an artifact of scaling one half of a
coupled pair, not a physiologic prediction. Measured at the shipped
sevoflurane coefficients, a 20 kg child under a weight-scaled cardiac output
alone would equilibrate about 2.6 times more slowly than the reference adult.
That is the opposite of the direction in which paediatric inhalational uptake
runs. (Salanitre and Rackow's *Anesthesiology* 1969;30(4):388–94 study of
pulmonary exchange in infants and children is the classic reference for that
direction. Its PubMed record was retrieved here, but its text has not been
read, so no figure is taken from it.) Doing half of the scaling is therefore
worse than doing none of it. Adopting the relation on the one patient that
exists would have lengthened every time constant by 3.32% and changed nothing
else.

**What follows from that is narrower than "the weight is unused".** This model
describes one 70 kg adult. It is not a paediatric, obese, or otherwise
weight-varying model, and no field in the interface makes it one. A run is that
adult's run, whatever value the reference weight shows. Weight-varying
physiology is `ROADMAP.md`'s planned-milestone item 30, and it is a package.
Compartment volumes, alveolar volume, alveolar ventilation, the perfusion
fractions and MAC by age should move together, or none of them should move.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**One reference condition, where the model physically has two.** "Agent
amount" fixes the amount unit at 20 °C and 760 mmHg, dry. Nothing here
converts between conditions, so a litre in the circuit and a litre in the
alveoli are added as equals. As volumes of gas they are not the same quantity
of agent. $`V_C`$ is a circuit volume at ambient temperature, and $`\dot V_F`$
is a flow at the common gas outlet. So $`M_C`$, $`M_{\mathrm{delivered}}`$ and
$`M_{\mathrm{exhausted}}`$ are at the stated condition and are exact there.
$`V_A`$ is an alveolar gas volume at body temperature. The partition
coefficients that build $`M_v`$ and $`M_i`$ were measured at 37 °C. So those
three are natively 37 °C quantities carried under a 20 °C label. The two
conditions meet in the ventilation term. That term moves $`\dot V_A`$ litres
out of the circuit and the same $`\dot V_A`$ litres into the alveoli. In the
alveoli, warming ambient gas to body temperature would expand it by the
molar-volume ratio.

**The size of it is 5.8 %, and it applies to the stores rather than to
conservation.** Every term is exact in the model's own arithmetic. The
mass-balance identity closes to 1e-13 L whatever condition the unit names. So
this is a statement about what the litres *mean*, not about agent going
missing. Read as amounts of substance, the alveolar, venous and tissue stores
hold 5.8 % fewer moles than their 20 °C label implies. The ratio behind
that figure is 25.450/24.055. The fresh-gas terms are unaffected.

**It is invisible in everything the simulator shows today, which is why it has
cost nothing so far.** A partial-pressure fraction is dimensionless and
carries no condition. So $`F_A`$, $`F_A/F_I`$, the MAC multiple and every
trace on the chart are untouched by it, and so is the release gate's relative
residual. It affects a reader only where an amount leaves the unit. That is the
liquid-equivalent consumption figure planned under § "Planned milestones"
item 28. There it biases the split between stored and exhausted agent, not the
delivered total, and the delivered total is the figure that means cost.
Removing this limitation would need a gas-phase model that carries explicit
conditions per compartment. That is well outside the current milestone. It is
recorded here so that a reader sizing the model does not have to reconstruct
it.

**The modeled alveoli are dry, and real ones are saturated at 47 mmHg.** This
is the third gas-phase condition, and the only one the document fixed without
examining it. "Agent amount" states the reference condition as 20 °C and
760 mmHg, *dry*. The note above works through the temperature half. This note
covers the water that the word *dry* excludes. Alveolar gas is fully saturated
at body temperature. So of the 760 mmHg available, 47 mmHg is water and
713 mmHg is left to everything else. Agent leaving the circuit is dry. It is
warmed and humidified on reaching the alveoli. A dry inspired fraction $`F_I`$
therefore occupies $`F_I \times 713`$ mmHg rather than $`F_I \times 760`$.
That is a dilution of 47/760, or 6.2 % of an atmosphere, before any uptake has
occurred. Equivalently, the undiluted figure is 6.6 % above the humidified
one, which is 47/713. The alveolar equation carries $`\dot V_A(F_I - F_A)`$
with no such factor, so $`F_I`$ arrives undiluted.

**The 47 mmHg is computed rather than quoted.** The saturation pressure of
water at 37.0 °C is 47.12 mmHg on the IAPWS-95 formulation (Wagner W,
Pruß A. *The IAPWS Formulation 1995 for the Thermodynamic Properties of
Ordinary Water Substance for General and Scientific Use.* J Phys Chem Ref Data
2002;31(2):387–535, doi:10.1063/1.1461829). The formulation's saturation
equation reproduces both the triple-point pressure and the normal boiling point
to better than one part in a million. The conventional 47 of the alveolar gas
equation is that value rounded, and the two agree to 0.3 %. It was computed on
2026-09-19. Nothing in the tree stores it, because no equation here reads it.

**Why the factor is not applied, measured rather than argued.** The governing
equations are linear in $`F_I`$. The section "Published wash-in and
elimination validation test" rests on the same property. So introducing the
factor on the inspired term multiplies every computed $`F_A/F_I`$ by 713/760
exactly. $`F_A/F_I`$ is the one quantity this model is validated against, and
the validation does not survive the factor. At the shipped defaults, the four
published wash-in cohorts sit comfortably inside their spread. With the factor,
three of the four fall outside it:

| Cohort | Modeled $`F_A/F_I`$ | Now | With the factor | Then |
| --- | --- | --- | --- | --- |
| Sevoflurane, Anesth Analg 1991;72:316-24 | 0.8528 | +0.16 SD | 0.7999 | −2.78 SD |
| Isoflurane, Anesth Analg 1991;72:316-24 | 0.7414 | +0.31 SD | 0.6954 | −1.39 SD |
| Desflurane, Anesthesiology 1991;74:489-98 | 0.9079 | +0.79 SD | 0.8516 | −4.84 SD |
| Isoflurane, Anesthesiology 1991;74:489-98 | 0.7414 | +0.38 SD | 0.6954 | −1.15 SD |

<!-- not-restated: 0.31 -->

This was measured on 2026-09-19 through `_wash_in_ratio` in
`tests/reference/test_published_wash_in_and_elimination.py`, against the
published means and standard deviations that the module itself holds.

**What fails there is double counting, not the physics.** In those studies,
$`F_A/F_I`$ is a ratio of two analyser readings taken from real airways. So
whatever humidification does to alveolar agent is already inside the measured
0.850, and a model that reproduces that number has already absorbed it. The
same is true one level down. The stored coefficients are tissue:gas and
blood:gas ratios equilibrated at 37 °C. How much water the gas phase held in
those determinations is recorded nowhere that this project has read. Suppose a
factor were applied to $`F_I`$ alone, against coefficients whose own gas-phase
basis is unknown here. Nobody could show that the factor moves the model
toward the phenomenon rather than away from it. To correct this properly, the
coefficients and the inspired term must be re-referenced together. That is
the same per-compartment gas-phase model that the note above names, and it is
well outside the current milestone. A later reader should not "fix" it by
inserting 713/760.

**What it costs a reader, and what it does not.** Modelling the alveoli as dry
does not affect the displayed percent or the MAC multiple. One
reason covers both: $`F_A`$ here is anchored to a measured end-tidal quantity
rather than to a computed dry-gas fraction. The rows above are end-tidal
measurements. MAC is defined on the end-tidal concentration too ("MAC
multiples as a display unit"). So a model fitted to the first and divided by
the second compares like with like, whatever water the sampled gas held. What
the omission does cost is mechanistic, and it sets a limit on what the
simulator can be asked. There is no water anywhere in this model. So nothing
here distinguishes a dry circuit from a humidified one. No question about
airway humidification has an answer in it, whether it concerns an HME, a
heated humidifier or the difference between them.

**Ambient pressure is not modelled, and away from one atmosphere the
delivered-concentration dial stops meaning one partial pressure.**
§ "Assumptions" above fixes ambient pressure at 760 mmHg and says what that
identity gains. This section states what it costs: this model is specified
for sea level. Take a user in Denver (about 630 mmHg) or Mexico City (about
585 mmHg) who sets 6% desflurane in this simulator and 6% on the
corresponding real device. That user is not delivering the same anesthetic,
and nothing else in the simulator says so. The reason is that the
delivered-concentration control is a vaporizer dial. This project's three
agents are drawn from two classes of vaporizer, and the two classes respond to
falling ambient pressure in opposite directions.
<!-- not-restated: 6 % -->

**Variable bypass — sevoflurane and isoflurane here.** This class includes
the Dräger Vapor 2000, Sevotec 5, Isotec 5 and Penlon Sigma Delta. Fresh gas
is split between a bypass channel and a vaporizing chamber. The gas leaving
the chamber is saturated at the agent's saturated vapour pressure, which is
set by temperature and not by ambient pressure. The dial sets the splitting
ratio. So as ambient pressure falls, the output rises in volumes percent while
the delivered *partial pressure* is approximately preserved, and the dial
needs no altitude correction. Boumphrey and Marshall give the approximation as
$`\%_1 = \%_\mathrm{cal} \times P_\mathrm{cal} / P_1`$. Their worked example
is isoflurane dialled to 2% at 101.3 kPa, which delivers 4.05% at 50 kPa.
That is 2.026 kPa of isoflurane either way.
<!-- not-restated: 2 % -->

**Gas–vapour blender — desflurane here.** This class includes the Tec 6 and
Tec 6 Plus. Desflurane needs this class at all because it boils at 22.8 °C.
The sump is kept at about 39 °C, which fixes desflurane's vapour pressure at
about 1460 mmHg. That temperature was chosen so that the resulting pressure
would clear the vaporizer's own internal resistances. Pure vapour is injected
into the fresh gas stream. A differential pressure transducer keeps the vapour
circuit at the fresh-gas circuit's pressure, so the two flows stay in the
fixed *ratio* that the dial sets. Andrews and Johnston describe it: "The
pressure in the vapor circuit is electronically regulated to equal the
pressure in the fresh gas circuit… vaporizer output is constant because the
amount of flow through each circuit is proportional". Output is therefore a
constant volumes percent, and the delivered partial pressure falls with
ambient pressure. Datex-Ohmeda states the consequence for the operator
directly: "Decreased atmospheric pressure, with altitude, does not
significantly affect the concentration of agent delivered (V/V), but
decreases the partial pressure of the agent in the ratio of the atmospheric
pressure to the calibrated pressure of 760 mm Hg. To compensate for the
reduction of vapor pressure output at altitude, the rotary valve must be
advanced to maintain the required agent partial pressure."

**The MAC divisor is a sea-level percent for the same reason.** 1 MAC is a
partial pressure, which convention quotes as a percentage of one atmosphere.
So at reduced ambient pressure, the percentage needed to reach it rises while
the partial pressure does not. James and White proposed MAPP, minimum alveolar
*partial pressure*, in place of MAC on exactly this ground. This is a further
sense in which the unit described under § "MAC multiples as a display unit"
is a sea-level unit rather than a universal one.

**No correction factor is stored, and the $`1/P`$ form above must not become
one.** $`\%_\mathrm{cal} \times P_\mathrm{cal} / P_1`$ is the dilute-vapour
limit of the flow-splitting physics. The fuller form is
$`F \approx k\,\mathrm{SVP}/(P - \mathrm{SVP})`$, which reduces to
$`k\,\mathrm{SVP}/P`$ only where $`\mathrm{SVP} \ll P`$. Isoflurane's
saturated vapour pressure is about 240 mmHg at 20 °C, which is not small
against 760. Carrying the denominator through gives a delivered partial
pressure that *overshoots* rather than holds steady. On that arithmetic alone
it is about 16% high at 585 mmHg, against the flat line that the $`1/P`$ form
predicts. The direction of each class's response is not in doubt, and neither
is the contrast between the two. The magnitude of the variable-bypass
compensation is approximate. That is why this section says *approximately*
preserved, and why no number is stored anywhere for it. An implementation of
ambient pressure should derive the variable-bypass case from the agent's
saturated vapour pressure rather than from the $`1/P`$ shortcut. It would owe
each agent's SVP a source of its own, and none is stored today.

**Sources for the notes above** follow. None of them is the authority for any
stored value, because there is no stored value for them to support:

- Weiskopf RB, Sampson D, Moore MA. The desflurane (Tec 6) vaporizer: design,
  design considerations and performance evaluation. *Br J Anaesth*
  1994;72:474–479. Primary, and the authority for every figure attributed to
  it here: the 22.8 °C boiling point, the 39 °C sump, the 1460 mmHg that the
  sump fixes and why that pressure was chosen, and the ±15% relative (or
  ±0.5% absolute) output accuracy. The project owner supplied it. It was read
  at the source on 2026-09-06 and re-read against the full text on
  2026-09-08. The full text states the 1460 mmHg twice, once for the sump and
  once for the regulator that reduces it to the fresh-gas pressure. The paper
  says nothing about ambient pressure or altitude, so it is not the source for
  that behaviour.
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
  `max_delivered_concentration_percent` carries for desflurane. The project
  owner supplied it, and it was read in full on 2026-09-06.
  **Owner-attested**: see the note below.
- Boumphrey S, Marshall N. Understanding vaporizers. *Contin Educ Anaesth
  Crit Care Pain* 2011;11:199–203. **Tier 2** under § "Source hierarchy". It
  is a secondary synthesis, taken here for the shape of the explanation and
  the worked example, and never as the authority for a number. Its "Altitude"
  section describes both classes side by side. The project owner supplied it,
  and it was read in full on 2026-09-06. **Owner-attested**: see the note
  below.

<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

**Two of those five are owner-attested rather than checkable, and this note
says which.** `docs/references/` cannot hold them. The repository is public,
so a file placed there is redistributed rather than read privately.
`docs/references/README.md` § "Redistribution" is the rule that follows from
this. Two publisher-copyright full texts were removed on 2026-09-06 for
exactly that reason (`PL-SHG5`). Any reader can reach the three journal
articles above through their DOI or PMID, and the Weiskopf figures were
re-read against the full text on 2026-09-08. The Datex-Ohmeda specification
sheet and the Boumphrey and Marshall article cannot be checked that way. Both
were read in a working session from copies that the project owner supplied,
and nothing in this repository can re-open either. So three things rest on
that reading alone: the passage quoted from Datex-Ohmeda, the 1–18% range
beside it, and the worked example attributed to Boumphrey and Marshall.
Nothing stored depends on any of them. A reader who wants to verify one has to
reach the document itself.
<!-- not-restated: 18 % -->

**Gas Man's own agreement with patients is phase-dependent, and wash-in is its
worst phase.** Both this model's parameter set and its compartment structure
descend from Gas Man. That lineage is ranked tier 3 under
§ "Source hierarchy". Its worth there rests on fixing the behavior of a widely
taught teaching tool as something that this implementation can be compared
against. A prospective in-patient study has since measured how closely that behavior
tracks real end-expired sevoflurane. The result depends on the point in the
case at which the question is asked. Twenty-eight ASA I–II adults undergoing
gynecologic or urologic surgery were maintained on sevoflurane in O₂/air.
Fourteen were on a Dräger Zeus and fourteen on a Getinge FLOW-i. Fresh gas
flow was re-randomised every fifteen minutes over 0.2 to 6 L/min, and the
vaporizer setting was left to the anesthesiologist. Each case was then re-run
in Gas Man on that patient's weight and the same flows, vaporizer settings and
minute ventilation. Cardiac output was left at the Gas Man default, Brody's
formula. That is the same 1945 interspecies relation that the cardiac-output
note above records this model as carrying. Over the whole hour, Gas Man
tracked both workstations to within 10% on two measures of measured against
predicted: the median signed percentage error and the median absolute
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
Varvel at source, so the metrics are taken as the study states them. The authors' own
conclusion is that Gas Man predicts end-expired sevoflurane "with better
relative performance for simulating maintenance than wash-in". Their stated
warrant is the wash-in and maintenance periods *combined*, rather than the
wash-in alone.

**What that bounds here, and what it does not.** The study is not a
measurement of this implementation. Nothing in this project has ever been
compared against a Gas Man trajectory. The comparisons under
§ "Required tests" are against published human data, and no figure in the
table above is a tolerance that anything here must meet. What the study bounds
is what the lineage is worth. Caveat 2 under
§ "Published wash-in and elimination validation test" says that passing shows
this implementation reproducing its parameter set's *intent*. Passing does not
show that the set is independently right. The study measures how much that
intent is worth in patients. It is worth least in the phase that the
simulator displays most: the first minutes of the $`F_A/F_I`$ rise, which is
the canonical teaching curve of inhaled-anesthetic uptake
(see § "Model boundary"). So "agrees with Gas Man" may not be read as
"agrees with a patient" anywhere in a case, and least of all in the first
fifteen minutes. Since 2026-10-18, this model's own first minutes have been
compared with the published human curves, in
§ "The early wash-in curve against the published figures". That comparison
measures this implementation, which the study above does not. It finds
desflurane rising faster than its cohort.

**Nor is the gap necessarily the patient model's.** The two workstations ran
the same protocol, the same simulator and the same cardiac-output default.
They differ in how they deliver agent into the circle. Their wash-in median
absolute errors differ by a factor of about 1.6. That is suggestive and no
more. The fourteen patients on each workstation are different patients, so
the contrast is between groups rather than within one group. The
interquartile ranges behind it, [8, 51] against [6, 32], overlap across most
of their length. The study does not decompose the error, and this document
does not claim that it can be decomposed. Nor is the phase split itself free
of the metric. A percentage error is at its most sensitive when the
denominator is small and rising, which is the wash-in's own condition. The
Methods are unread here, so how much either effect accounts for is
unestablished. The direction is nonetheless the one that this project's own
circuit already predicts. The apparatus lag $`\tau_C = V_C/\dot V_F`$ is "the
part of the inspired curve a learner is most likely to attribute to uptake"
(see § "Parameter provenance"). `docs/machine-survey.md` arrives at the same
conclusion from the machine side. One perfectly mixed circuit is least like a
real workstation exactly where Gas Man's published agreement with patients is
weakest.

- Candries E, De Wolf AM, Hendrickx JFA. Prospective validation of Gas Man
  simulations of sevoflurane in O2/air over a wide fresh gas flow range. *J Clin
  Monit Comput* 2022;36(6):1881–1890. PMID 35318567;
  [DOI 10.1007/s10877-022-00842-0](https://doi.org/10.1007/s10877-022-00842-0).
  **Abstract read**, through the PubMed record on 2026-09-19 and re-read there
  on 2026-09-20. The abstract is where every figure above is stated. PubMed
  returns no PMC identifier for the paper, so there is no PubMed Central full
  text. `docs/machine-survey.md` records that a check of the project owner's
  private reference corpus on 2026-09-20 did not find it either. Its Methods,
  its Varvel definitions and its per-patient data are therefore unread here.
  That is why this note quotes the study's phase split and does not restate
  its metrics' definitions. It is the authority for nothing stored in this
  project.


## Release gate

**Every release passes this gate. It does not belong to one version.** The gate
was first written for v0.1.0, and the line that introduces the criteria kept
that version for four releases while new entries were added to the gate. The
most recent entry is the published wash-in validation, which arrived in the
v0.3.0 window. Several criteria also name agents and cohorts that did not exist
until v0.2.0. A heading that names a version is a second statement that someone
has to keep true. `PL-C1KK`, one section over, records that failure. The
criteria below were already written for any release, so the line that
introduces them is what changed (`PL-8PZ1`).

A release is complete only when:

- all parameter values and sources are present;
- no scientific `TBD` markers remain;
- v0.0.2 circuit reference tests still pass;
- unit, integration, invariant, and independent reference tests pass;
- the published wash-in validation passes for every agent and cohort (the
  elimination comparison in the same module is a regression pin, not a claim
  of agreement, and is deliberately not a release gate);
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
