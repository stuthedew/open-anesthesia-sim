# Volatile-agent patient uptake and distribution model

## Status

This document specifies the scientific model implemented starting in v0.1.0
and in force unchanged ever since: the governing equations and compartment
structure have not changed, and are shared by every agent this model supports.
The title is version-generic for that reason.

**It deliberately names no current released baseline.** `ROADMAP.md`'s version
table is where that lives, and a second copy here goes stale at every release
without anything reading wrong until someone checks the version — which is
exactly what happened, this sentence having named v0.2.3 for thirteen releases
after v0.2.3 (`PL-C1KK`). Nothing in this document should restate the current
version; a statement that needs one should say what has been true *since* a
version instead, which cannot go stale.

The preceding milestone, v0.0.2, delivered an analytically validated ideal
breathing-circuit wash-in and washout model without a patient; its reference
tests are preserved unchanged (see "Preserved circuit reference tests" below).
Version v0.1.0 extends that model through:

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

Version v0.1.0 is the first patient sevoflurane model—the “Sevo works” milestone.

This is an educational model. It is not a clinical prediction, dosing tool, patient monitor, or medical device.

## Intended use, and the safety class this project holds itself to

The sentence above says what this is *not*. Both ISO 14971 and IEC 62304 begin
from what a thing **is**, because intended use is what every later judgment
about hazard and class is made against, so it is stated here rather than left
to be inferred from the absence of a disclaimer (queue item `PL-BLHV`,
2026-09-13).

### Intended use

This is a teaching simulator for volatile-agent uptake and distribution. It is
intended for anesthesia clinicians, trainees, and students, to build intuition
about how agent concentration moves between the breathing circuit, alveolar
gas, blood, and the tissue groups under management the learner chooses — and
in particular to make visible the compartments no clinical monitor displays:
vessel-rich, muscle, fat, and mixed venous.

**It is not intended for use with an identifiable patient's data.** The
simulator is intended to be run on hypothetical or illustrative parameters. It
is not intended for entering, importing, or reproducing the parameter values of
an identifiable patient, and not intended to inform the management of a specific
patient.

The boundary is deliberately drawn at the *data* rather than at physical
proximity to a patient, and the distinction is not pedantic. A simulator open on
a workstation while a case runs is ordinary teaching and carries no hazard of its
own; a run built from a particular patient's weight, age, and cardiac output is a
prediction about that patient whatever the window is labelled. Proximity would
forbid the first and permit the second, which is backwards. `ROADMAP.md`'s
planned patient-covariate work makes the second reachable, so the boundary is
recorded before that work rather than after it.

### Software safety classification: Class C, for the whole application

IEC 62304 § 4.3 assigns a software safety class from the severity of what a
software failure could contribute to: **Class A** where no injury or damage to
health is possible, **Class B** where injury is possible but not serious, and
**Class C** where death or serious injury is possible. Annex B.4.3 is what makes
the assignment turn on severity alone: where software sits in a sequence leading
to a hazardous situation, the probability of the software failing is **set to 1**
rather than estimated, so "this would rarely be wrong" is not an argument for a
lower class.

This project assigns **Class C uniformly, across the whole application**, and
does not segment the interface layer into a lower class. The reasoning:

- A lower class buys nothing here. Class A exists to *exempt* low-risk software
  from detailed design, unit verification, and integration testing. This project
  applies one quality gate to the whole tree, so there is nothing for the
  exemption to exempt, and declaring Class C costs nothing while declaring
  Class A for part of the tree would be a claim to defend.
- Class A asserts that *no injury is possible*, which the interface layer cannot
  assert. `CLAUDE.md` holds that presentation correctness is itself safety — the
  correct number with the wrong units, label, patient context, stale state, or
  model version is still a safety failure — and the interface is where the
  halted-versus-paused distinction, the displayed-precision rule, the ISO 5360
  agent colours, and the extreme-preserving decimation live.
- The boundary does not sit still. `app/chart_frame.py` looks like chrome and
  decides what a trace asserts about a run; `app/theme.py` looks like styling and
  carries agent identification. Drawing a class boundary through that would put
  the line in a different place from the one this project already maintains.

A split would pay only where the exempted surface is large, genuinely
non-clinical, and its verification burden actually felt. That is a condition to
watch for rather than a reason to build one now.

### This is an engineering bar, not a regulatory status

The class above is adopted the same way this project adopts WCAG 2.2 AA, which
"Color contrast, and the standard this interface is held to" in this document
describes as "chosen as the right engineering bar for a teaching tool, not as a
compliance obligation". Nothing here claims conformance to IEC 62304, a quality
management system, or any regulatory status, and no such claim should be read
into it. Writing the class down is strictly more useful than leaving it
implicit: it records the bar a reviewer can hold the code to.

Device status is a separate question and is not what the class answers. FDA's
published examples of software functions that are *not* medical devices include
software intended for health care professionals as educational tools for medical
training — with "games that simulate various cardiac arrest scenarios to train
health professionals in advanced cardiopulmonary resuscitation (CPR) skills"
given as a worked example ([FDA, Examples of Software Functions That Are NOT
Medical Devices](https://www.fda.gov/medical-devices/device-software-functions-including-mobile-medical-applications/examples-software-functions-are-not-medical-devices),
and the guidance "Policy for Device Software Functions and Mobile Medical
Applications"). That exclusion turns on intended use rather than on which
physiologic parameters the software accepts, and specifically on the software not
facilitating a health professional's assessment of a *specific patient* — which
is why the intended-use statement above is load-bearing rather than decorative,
and why its boundary is drawn where it is.

ISO 14971:2019 is the other half of the frame. It promoted **reasonably
foreseeable misuse** from a passing reference in the 2007 edition to a defined
term, and clause 5.2 makes documenting it an explicit requirement. Use of this
simulator against the intended use above is exactly that category, which is why
it is recorded as a stated boundary with mitigations rather than met with a
stronger disclaimer.

**On the sources for this section.** IEC 62304 and ISO 14971 are published
standards and are not open access; the clause structure, the three class
definitions, and Annex B.4.3's probability rule stated above were read from
secondary summaries rather than from the standards' own text, and that is
recorded here rather than implied. The FDA material was read at the source. A
reviewer revising this section should check the standards directly; the
conclusion (Class C, uniform) does not depend on the wording, but the clause
numbers cited here do.

## Reasonably foreseeable misuse, and the hazards the presentation carries

Every other safety argument in this document runs one way: here is a decision,
here is why it is sound. This section runs the other way — here is how a reader
could be misled, here is what stops it, here is the test holding the stop
(queue item `PL-FDBK`, 2026-09-13).

The direction matters because the two find different defects. Arguing forward
finds the mistakes you thought to look for; asking what has *not* been excluded
is what found `PL-VYXP` (a mass-balance baseline anchored to an implicit zero)
and `PL-B32L` (I/O exceptions escaping this model's documented error hierarchy),
neither of which had surfaced across roughly two hundred queue items, because a
queue records decisions taken rather than harms not yet ruled out.

ISO 14971:2019 makes this a requirement rather than a nicety: it promoted
**reasonably foreseeable misuse** to a defined term and, in clause 5.2, made
documenting it explicit. Use of this simulator against the intended use above is
that category, so it appears here as a row with a mechanism and a mitigation
rather than as a stronger disclaimer.

**Every row names the test that holds it, or says plainly that it has none.**
`tools/doc_check.py` fails when a test named anywhere in this document does not
resolve to a test that exists, so the right-hand column cannot rot into
decoration. What the check cannot judge is whether the test is any good; that
stays a reviewer's question.

| A reader could be misled into | What stops it | Held by |
| --- | --- | --- |
| reading a correct concentration as belonging to a different agent | agent colour is a redundant cue, never the sole identifier: the agent name is always visible - carried by the invariant tier every top-level window shows, subject to the observability limit stated there (§ "Minimum displayed outputs" -> "What this list requires once the layout is the reader's") - and the ISO 5360 colours and their accessible foregrounds are audited as one unit in `src/anesthesia_sim/app/theme.py` by `tools/agent_identity_check.py` | `test_agent_dropdown_options_pair_every_color_with_the_agent_name`, `test_every_agent_has_render_objects_in_its_own_identification_color`, `test_the_agent_name_stays_legible_while_the_run_disables_the_selector` |
| reading a run halted by a failure as one the user paused | a halt gets its own status words rather than falling back to "Paused", and the two failure modes are distinguished from each other as well | `test_refresh_view_reports_a_failed_run_as_stopped_not_paused`, `test_refresh_view_reports_the_supported_run_length_as_stopped_not_failed` |
| believing a setting above the vaporizer maximum was simulated | such a setting is **rejected, not clamped**, so no run proceeds on a value the user did not choose; the boundary itself is accepted | `test_rejects_delivered_concentration_above_the_vaporizer_maximum`, `test_explicit_delivered_concentration_above_the_agent_max_is_rejected`, `test_accepts_delivered_concentration_exactly_at_the_vaporizer_maximum` |
| reading a displayed value as resolved to its last digit | displayed precision is a recorded choice within a justified band, and the model retains precision the display discards rather than rounding its own state | `test_the_model_keeps_precision_the_display_throws_away`, `test_concentration_decimals_are_a_choice_within_a_recorded_band` |
| reading a control mark on the timeline as a measurement | the timeline labels its marks "Settings only — not a measurement." | `test_the_interface_says_a_control_mark_is_an_input_not_a_measurement` |
| reading a modelled compartment value as a measured one | the readout section states beside its values that they are model outputs and not measurements (`INTERPRETATION_DISCLAIMER_TEXT`, `PL-2K1R`), and the chart's hover names every value it reports as modelled (§ "The chart's hover readout: what the tooltip may show") | `test_the_interface_says_the_readouts_are_model_outputs_not_measurements`, `test_the_readouts_say_they_are_model_outputs_beside_the_values`, `test_the_hover_reports_the_drawn_state_through_the_formatters` |
| reading one run's concentration as the other's while two are compared | the run is named in text wherever a value is shown: on each run's own readout panel (§ "Minimum displayed outputs") and, while more than one run is drawn, on the first line of the chart's hover readout (§ "The hover and the run it belongs to"), because the hover floats free of the legend and line width has no textual analogue | `test_the_hover_names_the_run_only_while_more_than_one_is_drawn`, `test_two_runs_within_the_hover_radius_answer_under_their_own_names` |

### The row that was only partly mitigated until the Qt port

The last row is the one worth reading closely, because its mitigation was
incomplete from 2026-09-13 until the dashboard moved to Qt, and this section
said so rather than implying otherwise.

Three statements existed and they did not cover the same surface. `README.md`
states that "Every value on screen is a model output, never a measurement" — but
a learner running the application never opens it. The control-input timeline
carries "Settings only — not a measurement.", which is exact and covers the
marks only. And the interface's own standing notice is an **educational-use**
disclaimer, which tells a reader what the tool is *for* rather than how to read
a number on it. Nothing told a reader that the compartment readouts and the
chart traces are modelled predictions rather than measurements — precisely the
distinction this project's value depends on, since the compartments it exists
to display are the ones no monitor shows, so there is no measured counterpart a
reader could check them against, and the polish of the display argues the
other way.

The project owner agreed the interface should carry an interpretation
statement distinct from the use disclaimer (2026-09-13), and it landed with the
dashboard port (`PL-2K1R`, on `PL-25KS`). The wording follows the timeline's
pattern — short, beside the thing it qualifies, saying what the value *is*
rather than what the user must not do: **"Model outputs — not measurements."**
It stands once, on the readout section's heading row beside "Modelled
concentrations: {agent}", rather than being repeated on the chart, because a
disclaimer that is repeated is one that stops being read and the chart's own
hover already names every value it reports as modelled. The wording is the
port's choice and the owner may revise it; the requirement is the row above.
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

Only sevoflurane was modeled in v0.1.0. Isoflurane and desflurane were
added in v0.2.0 as additional selectable agents, using this same section's
equations unchanged (see "Status" and "v0.2.0: isoflurane and desflurane"
under "Parameter provenance").

## Model boundary

The modeled system contains:

1. one ideal, perfectly mixed breathing circuit;
2. one ideal, perfectly mixed alveolar gas compartment;
3. one venous blood pool;
4. one vessel-rich tissue group;
5. one muscle tissue group; and
6. one fat tissue group.

Arterial blood is not a separate mixing compartment. Pulmonary exchange is
modeled as flow-limited: blood leaving the lungs is assumed to equilibrate
instantaneously with alveolar gas, so the arterial partial-pressure-equivalent
fraction is defined as $`F_a \equiv F_A`$, with no arterial volume, mixing
delay, or independent state. This matches the flow-limited mammillary
structure used by the Gas Man reference simulator that this project's
sevoflurane and patient parameters are drawn from — Gas Man's computational
model is a four-compartment system (alveolar gas plus vessel-rich, muscle,
and fat groups) in which arterial tension is displayed but not tracked as an
independent compartment. See:

- Philip JH. Gas Man Version 4.1 Teaches Inhalation Kinetics. Society for
  Technology in Anesthesia. <https://www.stahq.org/files/7913/2743/1066/Abstract_57.pdf>
- Do distribution volumes and clearances relate to tissue volumes and blood
  flows? A computer simulation. BMC Anesthesiology.
  <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1508141/>

This is a deliberate simplification, documented here rather than left as an
unfilled parameter. See "Known limitations."

Inspired gas is likewise not a separate compartment. The circuit is one ideal,
perfectly mixed volume with no dead space and no separate inspiratory and
expiratory limbs, so the gas the patient inspires *is* the circuit gas: there
is no second state to carry and no transport delay between them. The model
therefore holds one gas-phase state between the vaporizer and the alveoli, and
names it for the clinical quantity rather than for its container — the
**inspired fraction** $`F_I`$, the middle term of the literature's
$`F_D \rightarrow F_I \rightarrow F_A`$ cascade. The container keeps its own
name: $`V_C`$ is the circuit's volume and $`M_C`$ the agent stored in it, so
$`M_C = V_CF_I`$ reads as what it is, a volume of apparatus holding gas at the
inspired fraction.

This is an assumption of the circuit model rather than a property of breathing
systems in general, and it is what makes the displayed $`F_A/F_I`$ ratio the
textbook one — the canonical teaching curve of inhaled-anesthetic uptake — see
"F_A/F_I as a displayed ratio". A multi-limb system such as Lerou and Booij's
three-part model separates inspired gas from mean circuit gas; there the two
would be distinct states, this model's single $`F_I`$ would no longer describe
both, and the departure would have to be recorded here before the model was
extended that way.

The naming is Hendrickx and De Wolf's, which is the field's: the gas-phase
cascade and the symbols $`F_D`$, $`F_I`$ and $`F_A`$ are set out on pp. 161-162,
the $`F_D - F_I`$ gradient attributed to rebreathing on p. 169 and $`F_I - F_A`$
to uptake on p. 171, and the didactic role of the $`F_A/F_I`$ curve on p. 167
(Hendrickx JFA, De Wolf A. Special aspects of pharmacokinetics of inhalation
anesthesia. In: Schuttler J, Schwilden H, eds. Modern Anesthetics. Handbook of
Experimental Pharmacology 182. Springer, 2008:159-186). Supplied by the project
owner and recorded at that depth; the pages above are what the citation is
being used for, and no page beyond them is relied on here.

**One symbol to read carefully.** $`F_I`$ is the inspired fraction and $`F_i`$
is tissue group $`i`$'s; they differ only in case. The collision is the
literature's rather than this document's — both conventions are standard — and
it is kept rather than worked around because renaming either would leave this
model's symbols disagreeing with every source a reader arrives from. Where both
appear in one expression the tissue index is written out.

The external inputs and outputs are:

- agent entering through fresh gas;
- carrier gas entering through fresh gas;
- an equal volume of mixed circuit gas leaving through the circuit exhaust; and
- no metabolism or other chemical destruction of the agent.

The circuit and patient form a closed recirculating exchange path except for fresh-gas inflow and circuit exhaust.

## Conventions

### Time

Simulation time is explicit state and is measured internally in seconds.

Flows entered in liters per minute are converted to liters per second:

$$
\dot V_{\mathrm{s}} = \frac{\dot V_{\mathrm{min}}}{60}
$$

Wall-clock time may schedule interface updates, but it must never be used as simulation time.

Seconds are the unit everywhere this document, the core, and the run
definition state a time. The interface renders that one quantity in **one**
form and introduces no second unit doing so: the clock, every recorded control
stamp and the chart's axis ticks all read as compound durations whose every
component carries its own unit — `45s`, `1m30s`, `1h23m45.6s`, `24h`. A
component that is zero is dropped, and a tenth is shown only where there is
one, so a stamp still resolves the step it was taken at.

The clock and the stamps read in seconds until `PL-Q4M4` and `PL-CZFY`. They
were moved onto the axis's form because the two were on screen together: a reader locating a
control mark stamped `5400.0 s` on an axis reading `1h30m` was converting
between two displayed forms of one quantity by hand, and at the supported
24-hour run length the clock's top reading was `86400.0 s`, which is false
precision on a boundary this document states in hours (`PL-Q4M4`, `PL-CZFY`).

The width the chart is drawing is the one thing still spelled out in words —
`15 minutes` above an axis whose last tick reads `15m`. That is register
rather than a second form: it is a phrase a reader chooses from a selector and
reads back in a caption, not a tick competing for width. "The chart's time
base" is where that is decided and "Displayed precision" is what each form is
resolved to.

#### Simulated time is a count of steps, not a running total

A run takes one step size and keeps it for its whole length. Simulated time
is the number of completed steps times that step — one multiplication,
rounded once — and never a total accumulated a step at a time.

The two agree to about 35 ns over a four-hour run at the shipped 0.1 s step,
far below anything displayed, so what the product buys is not accuracy. It
is path-independence: the product is a function of how far the run has gone,
while a running total is a function of the order and number of the additions
that reached it. Ten steps of 0.1 s sum to 0.9999999999999999 and multiply
to 1.0.

A step differing from the one a run has already taken is refused as a
`SimulationConfigurationError` rather than added to the count. The product
needs a single step to multiply by: a count of steps means a time only while
every step in it is the same size, and a run stepped at two cadences would
leave `elapsed_s` no step to multiply by. Reset clears the count and the step
together, so a fresh run may take a different one.

#### The reproducibility guarantee

**A run is a function of its inputs and of the number of steps taken, and of
nothing else.** The interface schedules its ticks with the wall clock, but
how many steps a tick takes is a setting the reader chooses and never a
measurement the loop makes: no tick takes extra steps to make up simulated
time a slow tick lost, and the run loop reads no clock. A machine
that wakes the loop late, drops a frame, or runs the whole session slowly
therefore produces a run that reaches a given step *later in real time* and
is identical in every state, keyframe and control stamp. It runs slower; it
does not run differently.

**This is measured, not asserted.** `tools/import_boundary_check.py` runs in
`make check` and CI and fails the build on a `time`, `datetime`, `random`,
`secrets` or `uuid` import in any module under `src/anesthesia_sim/core/`,
with the reason recorded beside each entry in its `BOUNDARIES` table. The
confinement stops at `core/` because this paragraph permits the interface its
wall clock; what the check closes is every route by which a compartment could
acquire one for itself — the clock directly, an unseeded generator, or an
identifier minted from either — and so leave this section reading as verified
while being false (`PL-J833`, `PL-ZK9R`).

Two of those are worth naming, because they cannot be recovered from by
seeding. `secrets` draws from `random.SystemRandom`, whose `seed()` is a
documented stub and whose `getstate()` raises; and `uuid.uuid1()` mixes the
current time with the host's hardware address, which makes a run differ
between *machines* as well as between runs.

So, given the same initial state, parameters, step size, setting changes and
event ordering, two runs taken to the same step count produce **element-wise
identical** run definitions and snapshots — identical, not agreeing within a
tolerance: the same segments, the same keyframes, and the same state at step
*n*, which is at simulated time *n* times the step in both. This is the
property a comparison of one run against another rests on, including the
comparison of a branched run against the run it branched from at every
instant they share.

**What carries this for a state that is derived rather than stepped to.** The
paragraph above is a claim about the stepped system, and it rests on every
caller taking the same width: with the step fixed, there is only one sequence
of arithmetic that reaches step *n*. A run held as its definition records no
samples and fixes no width — a state is computed when it is asked for, and the
same instant can be reached by more than one sequence. "The canonical
evaluation rule" under "Runtime controls" is what carries the guarantee there.
It is stronger than this paragraph in one respect and narrower in another: two
evaluations of one run definition at one instant are bit-identical rather than
merely reproducible across runs, and only values from the canonical path may be
stored, exported or branched from. The two halves share the work: the step
count carries the stepped system the snapshot is read from, and the canonical
rule carries every state derived from the run definition.

**Playing a run faster does not make it a different run.** The interface
offers a playback rate — how much simulated time advances per second of real
time — and it is implemented as the number of *whole steps* a tick takes,
never as a larger step. The same case played at real time and at three
hundred times real time is therefore the same steps, in the same order, at
the same size: an element-wise identical run definition and snapshot, reached
at different real times. A rate that resized the step instead would fall under
the first of the four exclusions immediately below — it would be a second
numerical solution of the same equations rather than the same run watched
faster — and
it would make a displayed value a function of how fast the reader happened
to be watching, which is a determinism failure no label repairs.

Four things it does not cover, none of them a defect:

- **A different step size.** Two runs at different steps are two roundings of
  the same solution rather than two solutions: the step is exact, so what
  separates them is floating-point accumulation, and "Step-refinement test" is
  what bounds it.
- **A different model version.** The guarantee holds within one version of
  the equations and one parameter set, which is why both are versioned.
- **A different platform.** Addition, multiplication and division are
  correctly rounded and so identical everywhere, but the step's propagator is
  built from one `exp()` call — a library function whose last bit may differ
  between platforms, interpreters and math libraries — and from a series and a
  sequence of squarings whose summation order a compiler may reassociate.
  Reproducibility is claimed for one build, not across all of them.
- **Elapsed real time.** How long a machine takes to reach step *n*, and how
  many steps it has reached when a wall-clock minute is up, are properties
  of the machine and deliberately not of the model.

### Concentrations

All model concentrations are stored internally as dimensionless partial-pressure-equivalent fractions from 0 through 1.

The gas-phase cascade is named as the inhaled-anesthetic literature names it,
$`F_D \rightarrow F_I \rightarrow F_A`$, which means that
the middle gas-phase state is $`F_I`$ (inspired) — not a symbol named after
the breathing circuit that holds it. The container keeps the apparatus subscript — $`V_C`$ for its volume
and $`M_C`$ for the agent in it — so a capital $`C`$ names the rig and $`F_I`$
names the gas. "Model boundary" above carries the assumption that makes the
two one quantity, and what would break it.

For example, $`F = 0.02`$ represents a 2% gas-phase concentration.

Two other places quote the same quantity in percent of an atmosphere and
cannot do otherwise: a vaporizer dial and a MAC. The conversion between the
two forms is:

$$
\text{percent} = 100F
$$

`src/anesthesia_sim/core/concentration.py` is the only place that arithmetic
is written, in both directions, and the two forms are distinct types there so
that a type checker refuses a percent where a fraction is wanted. It is used
in three places and no others: the agent data files' published percents become
fractions when `AgentUptakeSystem.for_agent()` builds a circuit; a refused
vaporizer setting is quoted back in percent, the unit the dial is read in; and
the interface converts for display. Before `PL-WVSK` the factor was written
out twelve times across six modules, seven of them on the path to a displayed
value, and this section said the interface alone converted — which `core/` had
contradicted since the agent data files began carrying a MAC.

The interface also converts to the second display unit, a multiple of the
running agent's 1 MAC. It is a rescaling of the percent above by one
per-agent constant and introduces no new state:

$$
\text{MAC multiple} = \frac{100F}{\mathrm{MAC}_\%}
$$

What that quotient does and does not assert is "MAC multiples as a display
unit"; it is not the definition of a modeled quantity and nothing in `core/`
computes it.

A concentration fraction must always be finite and satisfy:

$$
0 \leq F \leq 1
$$

### Agent amount

Every compartment stores the agent as an equivalent gas volume at one documented reference temperature and pressure.

The implementation must use the same reference conditions everywhere. It must not add gas fractions, dissolved blood concentrations, and tissue concentrations directly.

Let $`M_x`$ denote the equivalent gas volume of the agent stored in
compartment $`x`$.

The unit used in code is liters of equivalent pure agent gas unless the implementation document explicitly selects another consistent unit.

## Symbols

The **Code** column names the one expression in `core/` that denotes each
symbol, written `ClassName.accessor`. It maps this specification onto the
implementation; it is not a key for reading it. `core/` is meant to be
followable by a reader who knows these variables, so needing this column to
get through the code is a defect in the code rather than a use for the table.

| Symbol | Meaning | Unit | Code |
| --- | --- | --- | --- |
| $`t`$ | Explicit simulation time | s | `SimulationState.elapsed_s` |
| $`\Delta t`$ | Simulation step | s | `SimulationState.simulation_step_s` |
| $`F_D`$ | Delivered fresh-gas agent fraction | dimensionless | `BreathingCircuit.delivered_partial_pressure_fraction` |
| $`F_I`$ | Inspired agent fraction, which is the gas in the breathing circuit (see "Model boundary") | dimensionless | `BreathingCircuit.inspired_partial_pressure_fraction` |
| $`F_A`$ | Alveolar agent fraction | dimensionless | `AlveolarCompartment.partial_pressure_fraction` |
| $`F_a`$ | Arterial partial-pressure-equivalent fraction (flow-limited: $`F_a \equiv F_A`$; not an independent state) | dimensionless | — no attribute: the code reads `AlveolarCompartment.partial_pressure_fraction` wherever an arterial fraction is required |
| $`F_v`$ | Venous blood partial-pressure-equivalent fraction | dimensionless | `VenousBloodCompartment.partial_pressure_fraction` |
| $`F_i`$ | Tissue group $`i`$ partial-pressure-equivalent fraction | dimensionless | `TissueGroup.partial_pressure_fraction` |
| $`V_C`$ | Mixed breathing-circuit volume | L gas | `BreathingCircuit.circuit_volume_l` |
| $`V_A`$ | Modeled alveolar gas volume | L gas | `AlveolarCompartment.gas_volume_l` |
| $`V_v`$ | Venous blood-pool volume | L blood | `VenousBloodCompartment.volume_l` |
| $`V_i`$ | Volume of tissue group $`i`$ | L tissue | `TissueGroup.volume_l` |
| $`\dot V_F`$ | Fresh gas flow at the common gas outlet: carrier gas plus the vapour the vaporizer added, not the flowmeter setting (see "Breathing circuit") | L gas/min | `BreathingCircuit.fresh_gas_flow_l_min` |
| $`\dot V_A`$ | Alveolar ventilation | L gas/min | `AlveolarCompartment.alveolar_ventilation_l_min` |
| $`Q`$ | Cardiac output | L blood/min | `PatientCompartments.cardiac_output_l_min` |
| $`Q_i`$ | Blood flow to tissue group $`i`$ | L blood/min | `TissueGroup.blood_flow_l_min` |
| $`f_i`$ | Fraction of cardiac output reaching tissue group $`i`$, so that $`Q_i = f_iQ`$ | dimensionless | `TissueGroup.perfusion_fraction` |
| $`\mathrm{MAC}_\%`$ | Agent's 1 MAC, age-40 alveolar (display divisor only; not in any governing equation) | percent | `AgentParameters.mac_percent` |
| $`\lambda_{b:g}`$ | Agent blood:gas partition coefficient | dimensionless | `AgentParameters.blood_gas_partition_coefficient` |
| $`\lambda_{i:g}`$ | Tissue:gas partition coefficient for group $`i`$, which is the coefficient the agent data files store | dimensionless | `TissueGroup.tissue_gas_partition_coefficient` |
| $`\lambda_{i:b}`$ | Tissue:blood partition coefficient for group $`i`$, derived as $`\lambda_{i:g}/\lambda_{b:g}`$ | dimensionless | `TissueGroup.tissue_blood_partition_coefficient` |
| $`M_C`$ | Agent stored in the breathing circuit | L equivalent gas | `BreathingCircuit.agent_amount_l` |
| $`M_A`$ | Agent stored in alveolar gas | L equivalent gas | `AlveolarCompartment.agent_amount_l` |
| $`M_v`$ | Agent stored in venous blood | L equivalent gas | `VenousBloodCompartment.agent_amount_l` |
| $`M_i`$ | Agent stored in tissue group $`i`$ | L equivalent gas | `TissueGroup.agent_amount_l` |

Two conventions govern the Code column. Where a parameter is copied into more
than one compartment, the cell names its definition in `core/parameters.py`
rather than one of the copies — $`\lambda_{b:g}`$ is an agent parameter that
`VenousBloodCompartment` and every `TissueGroup` hold a copy of. Where the
model defines a symbol the implementation does not materialize, the cell is an
em dash and says what the code reads in its place; $`F_a`$ is the only such
symbol.

The two tissue coefficients are related by
$`\lambda_{i:g} = \lambda_{i:b}\lambda_{b:g}`$. The agent data files store
$`\lambda_{i:g}`$ and $`\lambda_{b:g}`$; $`\lambda_{i:b}`$ is derived from
them, which is why the tissue capacity in "Tissue compartments" below is
written $`V_i\lambda_{i:b}\lambda_{b:g}`$ and computed as the equivalent
single multiplication $`V_i\lambda_{i:g}`$. Both symbols name their two
phases in order, as do both identifiers, because the primary literature does
not hold a convention that would let a reader supply the missing phase:
Baker and Farmery's 2011 review names one quantity the tissue-gas partition
coefficient (p. 569), the tissue-blood partition coefficient (p. 570) and the
blood tissue partition coefficient (Table 2) in a single chapter, and its Eq.
(4) settles the quantity as tissue:blood. `docs/references/README.md` carries
the citation.

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

The blood:gas partition coefficient relates dissolved blood concentration to an equilibrium gas-phase concentration.

Arterial blood is flow-limited (see "Model boundary") and has no capacity or amount balance of its own: $`F_a \equiv F_A`$ at every instant.

Venous blood stores:

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

Equivalently, in the stored tissue:gas coefficient:

$$
C_i =
V_i\lambda_{i:g}
$$

which is the single multiplication `TissueGroup.capacity_l` computes, the
stored coefficient being the tissue:gas one.

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
- a tissue blood flow $`Q_i`$;
- an agent tissue:gas partition coefficient $`\lambda_{i:g}`$, which is the
  coefficient stored per agent;
- an agent tissue:blood partition coefficient $`\lambda_{i:b}`$, derived from
  that one;
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

All flow terms below must use liters per second after conversion from user-facing liters per minute.

### Breathing circuit

Fresh gas enters at concentration $`F_D`$. An equal fresh-gas volume leaves through the exhaust at the current mixed-circuit concentration $`F_I`$.

**$`\dot V_F`$ is the flow at the common gas outlet, not the flowmeter
setting.** The balance below carries one $`\dot V_F`$ for both the agent
arriving and the gas leaving, so the two have to name the same stream: agent
enters at $`\dot V_F F_D`$, which must be the vapour flow the vaporizer
actually adds, and mixed circuit gas leaves at that same total volumetric
rate. $`\dot V_F`$ is therefore the whole gas stream delivered to the
circuit — carrier gas plus that added vapour — and the balance does not close
under a carrier-only reading. This settles what the symbol means; it changes
no equation.

A vaporizer adds vapour to the carrier stream rather than displacing part of
it. So with carrier flow $`\dot V_c`$, which is what the flowmeters are set
to, and added vapour flow $`\dot V_v`$, the delivered fraction is
$`F_D = \dot V_v/(\dot V_c + \dot V_v)`$ and the two flows are related by:

$$
\dot V_F = \dot V_c + \dot V_v = \frac{\dot V_c}{1-F_D}
$$

The gap that opens between them is small at ordinary dial settings and is not
small at the top of a desflurane dial. At 2% delivered the two flows differ by
2%; at the 18% calibrated maximum of the Tec 6 vaporizer, which this model
accepts as desflurane's `max_delivered_concentration_percent`, they differ by
22% — flowmeters set to 2 L/min leave the common gas outlet at about
2.44 L/min. A reader who takes the interface's fresh-gas-flow control for a
flowmeter setting is wrong by that factor in the circuit time constant
$`V_C/\dot V_F`$, which is the quantity the wash-in curve is about. The
interface therefore names that control "Fresh gas flow" over the gloss
"common gas outlet", in the same two-line form the alveolar readout uses for
"end-tidal-equivalent" and for the same reason: the unqualified name is the
one on a real flowmeter bank, and it must not be shortened back to it to fit
a layout (`PL-71CF`).
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- derived: 22 percent from data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- derived: 2.44 L/min from data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

Ventilation transfers gas between the breathing circuit and alveolar compartment.

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

For constant input and no patient connection, the exact v0.0.2 solution remains:

$$
F_I(t+\Delta t) = F_D+\left[F_I(t)-F_D\right]\exp\left(-\frac{\dot V_F\Delta t}{V_C}\right)
$$

The existing v0.0.2 analytic reference tests must continue to pass unchanged.

### Alveolar gas

Ventilation moves gas between the circuit and alveolar compartment.

Pulmonary blood flow enters the lungs at venous concentration $`F_v`$ and leaves in equilibrium with alveolar gas at $`F_A`$.

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

Alveolar gas has no single time constant. Ventilation acting alone — that is, at $`Q = 0`$ — would turn the alveolar volume over with:

$$
\tau_A^{\mathrm{vent}} =
\frac{V_A}{\dot V_A}
$$

using compatible time and flow units, which is 37.5 s for the reference adult, where $`V_A = 2.5`$ L and $`\dot V_A = 4`$ L/min.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->
<!-- derived: 37.5 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->

That quantity is not the time constant of the coupled system, and it is recorded here — as a limitation of any single-mechanism description of alveolar kinetics — rather than exposed as a derived output, because two things separate it from what a run exhibits. First, blood uptake is a second exchange term acting on the same compartment: holding $`F_I`$ and $`F_v`$ fixed, $`F_A`$ relaxes with $`V_A/(\dot V_A + Q\lambda_{b:g})`$, which is 20.7 s for the reference adult on sevoflurane rather than 37.5 s. Second, $`F_I`$ and $`F_v`$ are not fixed — they are state variables of the same system — so the alveolar trajectory is a sum of exponentials over all six modeled compartments and no single constant describes it. A $`\tau_A^{\mathrm{vent}}`$ presented as "the alveolar time constant" would be a plausible number for a rate the simulation does not exhibit.
<!-- derived: 20.7 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4, default_cardiac_output_l_min = 5 -->
<!-- derived: 20.7 s from data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->

The pulmonary uptake rate is:

$$
\dot M_{\mathrm{pulmonary}} = Q\lambda_{b:g}(F_A-F_v)
$$

A positive value represents net uptake from alveolar gas into blood. A negative value represents net return from blood to alveolar gas during washout.

**The alveolar volume is held constant, and that is what excludes nitrous
oxide** (`PL-L2F2`). The substitution $`M_A = V_AF_A`$ above treats $`V_A`$ as
a constant and divides through by it, and `core/alveolar.py` implements
exactly that: `apply_blood_uptake` subtracts the transferred volume from the
compartment's agent amount and leaves its gas volume untouched, with nothing
augmenting inspired flow to replace what left. For the agents this model ships
that is correct rather than merely convenient. For nitrous oxide it is not,
and the difference is arithmetic rather than a matter of degree.

Compare the pulmonary uptake rate above against alveolar ventilation at the
early induction gradient, where $`F_v \approx 0`$, for the reference adult at
$`Q = 5`$ L/min, $`V_A = 2.5`$ L and $`\dot V_A = 4`$ L/min:
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5, alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->

| Gas | $`\lambda_{b:g}`$ | $`F_A - F_v`$ | $`\dot M_{\mathrm{pulmonary}}`$ | Of $`\dot V_A`$ |
| --- | --- | --- | --- | --- |
| Sevoflurane at 2% | 0.65 | 0.02 | 0.065 L/min | 1.6% |
| Nitrous oxide at 70% | 0.47 | 0.50 | 1.18 L/min | 29% |
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 1.6 percent from data/patients/reference_adult.json default_cardiac_output_l_min = 5, default_alveolar_ventilation_l_min = 4 -->
<!-- derived: 1.6 percent from data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->

The last column is the one that decides it. Uptake removes 1.6% of each
inspired alveolar volume for sevoflurane, which a fixed volume can ignore and
does. It removes 29% for nitrous oxide — and that removal *is* the
concentration effect: the gas left behind is concentrated by the volume that
departed, and replacement inspired gas is drawn in to fill the deficit. A
fixed-volume compartment represents neither half of it.

**Nitrous oxide's $`\lambda_{b:g} = 0.47`$ above is the conventional textbook
figure and is not a stored parameter.** This project ships no nitrous oxide
parameter file at all; the value is used here only to size the comparison,
and adopting it would need its own entry to the standard "Source hierarchy"
sets. Nothing in this section should be read as a nitrous oxide parameter set.

**One constraint, not three omissions.** "Known limitations" lists nitrous
oxide, simultaneous gases, and concentration or second-gas effects as three
separate absent features. They are one feature: all three are blocked by the
fixed alveolar volume, and lifting it reaches all three. Two standard
formulations do so, equivalent to first order, either of which a milestone
scoping multi-gas support could adopt. The first lets $`V_A`$ be state, with
the concentration equation picking up a volume term:

$$
\frac{dV_A}{dt} = \dot V_{A,\mathrm{in}} - \dot V_{A,\mathrm{out}} - \sum_k \dot M_{\mathrm{uptake},k}
\qquad
\frac{dF_A}{dt} = \frac{dM_A/dt - F_A\,dV_A/dt}{V_A}
$$

The second holds $`V_A`$ constant and replaces the volume lost to total uptake
with inspired gas, so the effective inspired ventilation becomes
$`\dot V_A + \sum_k \dot M_{\mathrm{uptake},k}`$. That one is the less invasive
here and is how the classical treatment writes it.

Either way, the second-gas effect follows from the alveolus holding more than
one gas rather than from machinery of its own. That is what makes
`ROADMAP.md`'s planned items 6 and 7 non-additive over these equations: item 7
is nearly free if item 6 is built this way, and unreachable if nitrous oxide is
bolted on beside a volatile. Item 6 already instructs that the patient be
modeled as a set of substances rather than as the bolt-on; the alveolar-volume
coupling is the mechanism behind that instruction, which the roadmap states as
a conclusion without the reason.

### Arterial blood

Arterial blood is flow-limited: blood leaving the lungs equilibrates instantaneously with alveolar gas, so $`F_a \equiv F_A`$ at every instant (see "Model boundary"). There is no separate arterial amount balance, capacity, or time constant. Every equation below that references $`F_a`$ uses the current alveolar fraction $`F_A`$ directly.

### Tissue uptake and return

For tissue group $`i`$, arterial blood enters at $`F_a`$ and venous blood leaves in equilibrium with the tissue at $`F_i`$.

The tissue amount balance is:

$$
\frac{dM_i}{dt} = Q_i\lambda_{b:g}(F_a-F_i)
$$

Substituting tissue capacity gives:

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

Blood leaving the tissue groups enters the venous pool. Venous blood leaves that pool for the lungs at $`F_v`$.

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

At zero cardiac output, pulmonary and tissue perfusion transfers are zero and no division by $`Q`$ is performed.

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

### Stored amount

The total stored amount is:

$$
M_{\mathrm{stored}} = M_C+M_A+M_v+\sum_i M_i
$$

Arterial blood contributes no separate term because it is flow-limited and holds no independent amount (see "Model boundary").

### Mass-balance identity

For an initial stored amount $`M_{\mathrm{initial}}`$:

$$
M_{\mathrm{initial}} + M_{\mathrm{delivered}} = M_{\mathrm{stored}} + M_{\mathrm{exhausted}} + \varepsilon_M
$$

where $`\varepsilon_M`$ is the numerical mass-balance residual.

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

Here $`M_{\mathrm{scale}}`$ is a documented small positive reference amount that prevents division by zero.

Two bounds apply, and they answer different questions.

**The run-time halt thresholds, as implemented in `core/agent_simulation_validation.py`:**

```text
AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L = 1e-12
AGENT_ACCOUNTING_RELATIVE_TOLERANCE = 1e-9
MINIMUM_RELATIVE_SCALE_L = 1e-15
```

These are the identifiers as the module spells them, so each resolves to the constant it quotes; the absolute bound and the scale floor carry their unit in the name, and the relative bound is dimensionless. A step passes if either tolerance is satisfied. The relative error uses `max(initial + delivered, MINIMUM_RELATIVE_SCALE_L)` as its denominator to avoid division by zero when no agent has yet been delivered. Exceeding both stops the run: this is the point past which the model refuses to show a number, not the standard the shipped model is held to.

**The release gate is the relative residual alone**, asserted by the reference runs in `tests/reference/test_multi_agent.py` and `tests/reference/test_sevo_patient.py`, which restate it as `MASS_BALANCE_RELATIVE_GATE`:

```text
MASS_BALANCE_RELATIVE_GATE = 1e-10
```

It is relative because the residual is rounding accumulated once per step, so it scales with how much agent a run has handled. An absolute bound measures the delivered concentration and the run length instead of conservation. Measured 2026-09-06 on the shipped exact step, over 600 s wash-in plus 600 s washout:

| Agent | Dial | Delivered | $`\varepsilon_{\mathrm{absolute}}`$ | $`\varepsilon_{\mathrm{relative}}`$ |
| --- | --- | --- | --- | --- |
| isoflurane | 4% | 1.60 L | 3.589e-13 L | 2.243e-13 |
| isoflurane | 2% | 0.80 L | 1.794e-13 L | 2.243e-13 |
| desflurane | 4% | 1.60 L | 9.262e-14 L | 5.789e-14 |
| desflurane | 2% | 0.80 L | 4.631e-14 L | 5.789e-14 |

Halving the dial halves the absolute residual exactly and leaves the relative one unchanged to four significant figures.

Where the value comes from — worst relative residual at any step, measured the same day at the reference runs' own settings and at the corner of the supported envelope (fresh gas 10 L/min, alveolar ventilation 12 L/min, cardiac output 10 L/min, each agent at its calibrated dial maximum):

| Horizon | Reference settings | Worst envelope corner |
| --- | --- | --- |
| 1200 s, what the reference runs cover | 2.12e-13 | 2.26e-13 |
| 1 h | 2.19e-13 | 1.04e-12 |
| 4 h | 3.75e-12 | 2.88e-12 |
| 8 h | 5.05e-12 | 6.36e-12 |

1e-10 leaves about 450x headroom at the horizon those runs use and about 16x at 8 h, so neither moving a dial nor lengthening a case changes what the gate certifies. It stays an order of magnitude inside the 1e-9 halt threshold, so passing the gate says strictly more than that the run did not stop, and a real conservation defect is orders of magnitude rather than factors of two.

Clipping a negative store to zero does not repair mass balance and must not be used to conceal an unstable update.

## Numerical method

The model is advanced using explicit simulation time and piecewise-constant settings over each step.

The implementation must:

1. derive concentrations from the current stored amounts;
2. evaluate every transfer from one consistent state;
3. carry every internal transfer as an equal and opposite pair, so that no
   compartment can gain what another does not lose;
4. integrate fresh-gas delivery and exhaust by the same method, and over the
   same trajectory, as the compartments they cross the boundary of;
5. advance the cumulative delivery and exhaust amounts;
6. advance explicit simulation time; and
7. calculate the post-step mass-balance residual.

Requirements 2 and 3 are properties of the system matrix rather than of a
sequence of operations. "Selected method (as implemented)" advances the whole
system in one step, so there is no order in which transfers are applied and
nothing to hold fixed while another moves: requirement 2 is satisfied because
every rate reads the same state vector, and requirement 3 because each
internal exchange appears as a pair of off-diagonal entries whose contribution
to the total stored amount cancels — a structural property of the matrix,
checked as such in `tests/unit/test_governing_equations.py`, rather than an
invariant maintained by applying paired deltas. Requirement 4 is why delivered
and exhausted agent are states of that system too.

A step is all-or-nothing. It writes each compartment in turn, and a guard can
reject a value after earlier compartments have already been written; so a step
that cannot be completed must leave every dynamic value exactly as it was
before the step. "Step atomicity" below says why, and what a caller is left
holding.

### Step atomicity

A partially applied step is not a solution of the model at any time. It holds
some compartments at $`t+\Delta t`$ and others at $`t`$ — a set of numbers no
instant of the model ever produced, and indistinguishable in the interface
from numbers it did. Preferring an obvious failure to a plausible-looking
number therefore requires undoing the step, not annotating it.

`AgentUptakeSystem.advance()` captures every dynamic value before the step
and restores it on any failure. What the model holds afterwards is the last
completed step: a real solution, at a real simulation time, which the
interface may display and a reader may reason about. The diagnosis that would
otherwise have to be inferred from those numbers is carried in the raised
`SimulationNumericalError` message instead, which names the invariant that
failed and the step size it failed at.

The dynamic values are the eight the trajectory is carried in — the circuit's
inspired fraction, the alveolar amount, each of the three tissue amounts, the
venous amount, and the cumulative delivered and exhausted amounts — plus the
accounting period's initial amount. Settings and
parameters are deliberately not captured: a rollback that restored cardiac
output would undo a change the run had accepted. Each compartment captures
its own, so a dynamic field added later without a matching capture is a local
omission rather than a partial restore that looks complete.

Rolling back does not make the run resumable. The model reached a state it
could not step from, so the same step would fail again; the caller must stop
either way. What the rollback settles is what the caller may *show* while
stopped.

Three constants sit at 0.1 s, and they are three different kinds of
statement:

```text
MAXIMUM_SIMULATION_STEP_S  = 0.1   # core/uptake_system.py
SIMULATION_STEP_S          = 0.1   # app/dashboard_frame.py
SIMULATION_TICK_INTERVAL_S = 0.1   # app/dashboard_frame.py
```

`MAXIMUM_SIMULATION_STEP_S` is the model's supported domain, closed at its
endpoint: any positive step at or below it is supported, and both
`AgentUptakeSystem.advance()` and `SimulationState.advance()` refuse a larger
one. `SIMULATION_STEP_S` is the step the interface takes, which sits at that
ceiling deliberately; "Supported simulation step" below states what the bound
tolerates and says why those two coincide. Neither is derived from the other,
and the coincidence is a fact about this configuration rather than an
identity — which is why they are named apart.

`SIMULATION_TICK_INTERVAL_S` is not a step at all: it is how often the run
loop wakes, in *real* seconds. It equals the step only because a tick that
takes one step is what real-time playback means here, and the two are named
apart because the playback rate is the ratio between them — a tick takes
`multiplier × tick interval ÷ step` whole steps. Spelling that out is what
makes "60× real time" a claim a test can check rather than a label beside a
loop; re-tuning the wakeup for a host without re-deriving the rates would
otherwise falsify every rate on screen and fail nowhere.

### Selected method (as implemented)

Each simulation step is advanced by **one exact propagation of the whole
coupled system**. Every setting is held constant across a step, so within that
step the six modelled fractions obey a linear, time-invariant system
$`dy/dt = Ay + b`$; carrying the constant $`b`$ against a ninth state whose
value is always 1 makes it $`dy/dt = Ay`$, and

$$
y(t+\Delta t) = \exp(A\,\Delta t)\,y(t)
$$

is then its exact solution, with no truncation error at any step size.

`core/governing_equations.py` assembles $`A`$: every entry is one term of one
balance equation in "Governing equations" above, written in the order this
document states them. `core/matrix_exponential.py` computes
$`\exp(A\Delta t)`$ and carries no physiology. Neither adds a dependency —
the exponential is scaling and squaring with a truncated Taylor series, about
sixty lines of arithmetic on plain lists, and its module docstring carries the
method's provenance and the derivation of its two constants.

Two of the nine states are not fractions. They accumulate the agent crossing
the system boundary, at the rates "External delivery" and "Circuit exhaust"
give: $`\dot M_{\mathrm{delivered}} = \dot V_FF_D`$ and
$`\dot M_{\mathrm{exhausted}} = \dot V_FF_I`$. Delivered agent has a closed
form of its own, but exhausted agent is $`\dot V_F\int F_I\,dt`$ along a
coupled trajectory and does not; carried as a state it is integrated by the
same propagator over the same trajectory, which is what requirement 4 of
"Numerical method" above asks for.

**The residual this leaves is rounding, and it is larger in absolute terms
than the split's was.** Measured 2026-09-06 over a 3600 s run at 1 MAC, the
worst residual at any step is 1.0e-12 L for sevoflurane, 2.4e-12 L for
isoflurane and 1.3e-11 L for desflurane, against a relative error of at most
9.2e-13 in every case. The split held about 2e-15 L absolute, because it moved
agent between compartments as amounts and its equal-and-opposite pairs
cancelled to the last bit. Here conservation is a property of the matrix and
the arithmetic is done in fractions, so the pairs cancel only to floating-point
precision *relative to the largest quantity in play* — and over an hour at
desflurane's dial that quantity is about 43 L of delivered agent, which is
where the four orders of magnitude come from.

Nothing about that is a loss of accuracy: the relative residual is three orders
inside the check's own relative tolerance, and the absolute figures scale with
how much agent the run has handled rather than with any error in it. What it
does mean is that `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L` (1e-12 L) is now
routinely exceeded on a long run and the relative branch alone is carrying the
check — first exceeded at t = 3452 s at the reference runs' own settings and at
t = 538 s at the sevoflurane corner of the envelope, measured 2026-09-06.

That settles the shape of the guard (`PL-4GN8`). The disjunction in
`check_agent_accounting` is right: the absolute branch is the one that catches a
gross error early in a run, when little has been delivered and the relative
denominator is small, and the relative branch carries the check from then on.
What was wrong was the *release gate* — the reference runs asserted the absolute
residual, so what they certified moved with the dial they happened to use and
was simply false past about an hour of simulated time. They now assert
`MASS_BALANCE_RELATIVE_GATE`, above.

**What this replaces, and why the decision changed.** Until v0.4.x each step
was the exact analytic solution of five *pairwise* exchanges, composed in
sequence: fresh gas into the circuit; circuit and alveoli against each other;
each tissue against a held arterial fraction; venous blood against the
flow-weighted tissue outflow; and the net patient uptake applied back to
alveolar gas. Solving each exactly while holding the other flows constant made
the composition a first-order (Lie/Godunov) operator split, whose error was
$`O(\Delta t)`$ against the true simultaneous solution even though every
sub-step was itself exact.

**The split was kept once, on accuracy, and that decision was right on its own
terms** (project owner, 2026-08-30). Measured against the same from-scratch RK4
oracle at 5% delivered over 60 s and 3600 s, the exponential's worst
disagreement across all six states was $`1.3\times10^{-16}`$ to
$`4.8\times10^{-14}`$ against $`5.2\times10^{-6}`$ to $`1.7\times10^{-5}`$
for the split — but the split's error was bounded rather than unknown, so what
an exact step bought was a tighter number rather than the correction of a wrong
one, and no work planned at that date wanted it. Those measurements are carried
in queue item PL-6GS0 and were produced by the v0.2.0 architecture review's
verification harness, retired under PL-STNV.

**It was superseded on 2026-09-03** (project owner) on a ground the original
did not weigh: not accuracy, but whether the code can be read as the model.
`ROADMAP.md` planned-milestone item 29 sets the bar that a reviewer who knows
the standard variables and equations should follow `core/` and recognize them
without a lookup table, and the split could not reach it. Three of its five
composed sub-steps were objects of the splitting scheme rather than of the
physiology; the alveolar balance's two terms were computed in different
sub-steps separated by a third; and the pulmonary uptake rate specified under
"Alveolar gas" above was never formed at all. Assembling the system matrix, by
contrast, *is* transcribing the governing equations — the alveolar balance is
one row and its two terms are two entries of it. Accuracy was not the
motivation and was not a cost either.

**Two consequences worth stating rather than leaving to be inferred.**

First, **the fractions cannot leave their physical range**. Every off-diagonal
entry of $`A`$ is a transfer rate and so is nonnegative, which makes $`A`$ a
Metzler matrix and $`\exp(A\Delta t)`$ an entrywise nonnegative one;
`core/matrix_exponential.py` shifts before summing its series so that this
holds in floating point and not only in exact arithmetic. A step therefore
cannot drive a compartment negative at any step size. That is a property of the
construction rather than of the shipped parameters, so no patient file or agent
can reach the compartment capacity guard through the model. The guard and the
rollback remain as cover for a model extension whose matrix is not a pure
transfer system.

Second, **refining the step no longer changes the answer**. Under the split,
halving $`\Delta t`$ halved the error, and the step-refinement gate
(`test_step_refinement_converges`) asserted that successive halvings moved the
solution less each time. Every supported step now lands on the same solution to
within floating-point rounding, so that gate asserts the stronger property
instead: that the step does not enter the answer. What it cannot answer is
whether the answer is *right* — a wrong transfer rate is equally step-independent
— and neither can the mass-balance gate, since every internal transfer is an
equal-and-opposite pair. "Independent-solution test" below is the gate that
answers it, by comparing all six states against a from-scratch integration of
the equations above.

#### Supported simulation step

`MAXIMUM_SIMULATION_STEP_S` is the largest step `AgentUptakeSystem.advance()`
and `SimulationState.advance()` accept; a longer one is refused as a
`SimulationConfigurationError` before anything is calculated, so nothing is
miscalculated and a caller can retry inside the range with the run it already
has intact.

**What the bound now means, and what it no longer rests on.** Until v0.4.x it
was an *applicability domain*: the method was first order, so its error grew
with the step, and 0.1 s was the largest step at which every claim "Displayed
precision" makes about the last displayed digit still held. That derivation is
void. The exact step has no truncation error at any step size and its
propagator keeps every fraction in range at any step size, so there is no
accuracy-derived domain left to be outside of.

What a longer step still costs is **control resolution**. Settings are held
constant across a step, so the step is the interval over which a change to a
control is invisible to the model: at 0.1 s a slider move is resolved to a
tenth of a second, and at 10 s a change made and reversed inside one step never
happened at all.

**Re-derived 2026-09-06 (`PL-X9KD`), and the honest result is that this is a
declared tolerance rather than a derived limit.** The search for a limit was
run first and came back empty. Sweeping the step from $`10^{-3}`$ s to
$`10^{300}`$ s across the settings envelope, the disagreement with an
independent solution stays between about $`10^{-14}`$ and $`2\times10^{-12}`$
in fraction, and it does not grow with the step — it is U-shaped in it, with a
minimum around 1 to 60 s, because the only error mechanism left is rounding and
rounding accumulates once per *step*, so a finer step is slightly worse. The
propagator was entrywise nonnegative exactly at every one of 4374 (settings,
step) combinations tested, so no compartment guard can be reached by stepping
coarsely; `advance()` raises nothing until about $`10^{18}`$ s, and the first
step at which a displayed digit is wrong by a whole count is around
$`10^{13}`$ s. There is no numerical ceiling a caller can reach.

Control resolution does not supply a threshold either, and this is the point
that decides the shape of the constant. A control change takes effect at the
next step boundary, so it is displaced later by up to one whole step, and that
displacement is **exactly proportional to the step** — measured over three
manoeuvres and all three agents, halving the step halves it, with no knee
anywhere. No step size is therefore the one at which control timing becomes
invisible. What the constant can honestly be is a declared tolerance, and what
it owes a reader is the measurement of what it tolerates.

**The tolerance, in percentage points of one atmosphere.** These are absolute
concentrations, deliberately not counts of the readout: the readout's decimal
count is a presentation decision (§ "Displayed precision") and must not reach
back into the model. Worst displacement over all three agents at the shipped
0.1 s step, from a control change landing one step late:

| Manoeuvre | Worst displacement | Binding agent |
| --- | --- | --- |
| Case opening: dial off to 1 MAC, reference flows | 6.7×10⁻³ pp | desflurane |
| Unperfused load, then perfusion on and dial off | 5.0×10⁻² pp | desflurane |
| Ventilator start at the envelope corner | 1.4×10⁻¹ pp | desflurane |

The criterion these are read against is the model's own parameter uncertainty,
which is upstream of both the step and the display: one standard deviation of a
single measured partition coefficient displaces a displayed compartment by
$`9\times10^{-4}`$ to $`6.8\times10^{-2}`$ pp (Yasuda et al. 1989; § "Displayed
precision" carries the measurement). So at 0.1 s an ordinary control action is
timed to about a tenth of one parameter SD, which is the sense in which the
step is fine enough.

**Both tables in this section are held by a test**, which is not a formality:
since `PL-X9KD` retired the accuracy derivation these figures are the whole
content of `MAXIMUM_SIMULATION_STEP_S`, and until `PL-ZVS7` they were asserted
by prose here and in `core/uptake_system.py` and by nothing else.
`tests/reference/test_control_resolution.py` re-measures every one of them from
the parameter files at each run, driving each manoeuvre twice — on time and one
grid step late — and taking the worst difference over all six displayed
compartments. So a change to the governing equations, to a partition
coefficient, to the reference adult's volumes, to the supported input envelope,
or to the step itself moves the test before it can move what this section tells
a reader. The same test pins the step the figures were measured at, because the
table and the constant are one decision.

**What 0.1 s does not buy, stated rather than left to be discovered.** An
abrupt manoeuvre is not held inside that criterion. A ventilator start at this
step displaces the alveolar reading by up to $`1.4\times10^{-1}`$ pp — about
twice one parameter SD — for the duration of the transient it starts. Holding
that inside one SD would need a step near 0.05 s.

**Put to the project owner as a trade-off rather than a correction, and
decided on 2026-09-06: the step stays at 0.1 s and that timing is accepted**
(`PL-NBCJ`). Three things decided it. Halving the step doubles the
propagations per simulated second and changes the interface's tick structure,
since `SIMULATION_TICK_INTERVAL_S` is assigned from the step and the playback
rates are derived from their ratio. The benefit is confined to 1× playback:
above it the control grid below is `multiplier × 0.1` s wide and dominates the
step outright, so a reader at 60× would see no change at all. And frames are
two grid steps apart even at 1×, so a 0.05 s step would resolve control timing
to half of what the display can show.

What is therefore accepted, and stated here rather than left for a reader to
infer from a value: at the shipped step an abrupt ventilation change is timed
to about twice one parameter SD, which is the one case where the step
contributes more error than the parameters do. It is small in absolute terms —
1.4×10⁻¹ pp against a 6.0% 1 MAC for desflurane — and it is disclosed rather
than removed. A reader comparing an abrupt ventilation change against a
measurement should know that its *timing* is resolved to a tenth of a second
and no better.

**Everything above is per step of delay, and the interface waits one step for a
control change only at 1× playback.** Which is to say: the table above is the
tolerance this constant declares, and it is not the resolution the application
offers. The run loop advances a whole tick's worth of steps with nothing
between them, so simulated time stands still for one real tick interval and
then jumps by `multiplier × 0.1` s. A setting changed while the run is playing
therefore first acts at a tick boundary, and the reachable simulated instants
are that far apart:

| Playback rate | Control grid | Frames are | Worst displacement per grid step | Second worst | Margin |
| --- | --- | --- | --- | --- | --- |
| 1× | 0.1 s | 0.2 s | 1.4×10⁻¹ pp | 5.0×10⁻² pp | 2.84× |
| 5× | 0.5 s | 1 s | 7.0×10⁻¹ pp | 2.5×10⁻¹ pp | 2.78× |
| 20× | 2 s | 4 s | 2.5 pp | 9.8×10⁻¹ pp | 2.56× |
| 60× | 6 s | 12 s | 5.8 pp | 2.8 pp | 2.11× |
| 300× | 30 s | 60 s | 1.0×10¹ pp | 1.0×10¹ pp | 1.03× |

The first three columns are in simulated seconds. "Worst" is the same
measurement the table above reports, re-run at each rate over the same three
manoeuvres and all three agents (2026-09-06, `PL-NBWP`); "second worst" is the
next manoeuvre down at that rate, and the margin is their ratio, computed from
the measurements rather than from the rounded columns beside it (2026-09-13,
`PL-WT07`).

**Read the worst column as a bound over the three manoeuvres rather than as a
property of one of them.** At every rate the worst is the ventilator start with
desflurane and the second worst is the unperfused load then dial off. That is a
measured fact and not a structural one, so it is re-checked on every run by
`test_the_ventilator_start_binds_the_per_rate_table_at_every_rate` — and the
margin column is why saying it that way round matters. The lead is 2.84× at 1×
and 1.03× at 300×, three per cent, so at the coarsest grid the two manoeuvres
are the same number to the two significant figures this table publishes. A
parameter revision that reversed them would leave the bound intact and make the
attribution wrong, which is the failure this phrasing is built to survive.

**They converge because they saturate at different rates.** The ventilator
start's transient has largely run by the time a 30 s grid step has passed, so
**its displacement saturates rather than scaling with the delay** — take its 1×
figure and extrapolate linearly and 300× is over-stated by about four times.
The unperfused load's transient is still going at 30 s, so its displacement is
still nearly linear in the delay and keeps growing. The measured values are the
ones to use; neither the figures nor the margin extrapolates.

**An ordinary dial change sits well below both, and is a third manoeuvre rather
than the runner-up.** The case opening is about 21× milder than the bound at
1×, narrowing to 19× at 20×, 16× at 60× and about 7× at 300×, where it reaches
1.5 pp. That is the comparison to reach for when sizing what a learner's own
actions cost. It is not the comparison that says how much room the bound has:
the tens of percentage points at 300× belong to abrupt manoeuvres, and the
nearest of those is the second-worst column above.

Three things follow, and the third is why the behaviour was left alone.

- **Nothing arrives late.** A recorded `ControlChange` carries
  `SimulationState.elapsed_s` at the moment of the call, and the new setting
  acts over the step beginning there, at every rate. So the control timeline is
  exact to the step and no displayed value is stale against it. What the rate
  coarsens is only which instants a reader can *choose*.
- **An exact route exists at every rate: pause, change, resume.** The run loop
  takes no steps while the run is paused, so a setting changed then acts from
  the step the run resumes on. Timing a manoeuvre is what this is for; the rate
  ladder is for watching one.
- **The grid is already finer than the display, by exactly two.** Frames are
  one render interval apart, which is two tick intervals, so at every rate a
  reader sees the run at half the resolution they can act on it at. Tightening
  the grid — by servicing control events inside the burst, or by waking the loop
  more often — would resolve control timing that the display cannot show. What
  was wrong here was the documentation, and it is what has been fixed.

The supported step and the shipped step are the same number, and the interface
runs at it.

**The measurements the old bound rested on are kept as history**, because they
describe a method this project shipped for eleven releases and a reader
comparing versions needs them. On the worst trajectory the four sliders can
reach, across all three agents, the operator split's first-order coefficient
$`C`$ was at most $`2.29\times10^{-3}\ \mathrm{s^{-1}}`$; its error was
$`C\,\Delta t`$, so every figure "Displayed precision" quoted was that error
at exactly $`\Delta t = 0.1\ \mathrm{s}`$ and doubling the step doubled all
of them. Its compartment capacity guard first fired at 12 s for isoflurane,
25 s for sevoflurane and 50 s for desflurane, two orders of magnitude above
the bound and agent-dependent by a factor of four, which is why the guard was
never the domain check. None of these figures describes what ships.

**The capacity guard remains, and now reports something the model cannot
reach.** Where a step drives an amount out of range,
`AgentUptakeSystem.advance()` reports `SimulationNumericalError`: the step is
rolled back in full, simulation time does not advance, and the caller must stop
the run — from a state that is the last completed step rather than a partially
applied one. Under the exact step no parameter set reaches it, because the
system matrix is Metzler and its propagator therefore entrywise nonnegative
(see "Selected method (as implemented)"); the guard is cover for a model
extension whose matrix is not a pure transfer system, not for a caller stepping
too coarsely. The two failures stay deliberately distinct:
`SimulationConfigurationError` says the setting was refused and the run is
still trustworthy, `SimulationNumericalError` says a run in progress is not.

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
- which tier of the hierarchy below that source sits in, and — where the
  source is not a primary measurement — what the primary literature reports
  instead and by how much it differs.

### Source hierarchy: what may be cited as the authority for a value

A citation records where a number was found. It does not, on its own, say
whether anything was measured there. Three tiers are distinguished. Only the
first may be named as the authority for a stored value on its own strength; a
lower tier may be adopted only on a recorded decision, under the rule stated
below the three.

1. **Primary measurement.** A study that measured the quantity, in the
   species, population and conditions the model claims to represent, and
   reports the value, its dispersion, and its reference conditions. Strum and
   Eger's sevoflurane blood:gas determination (0.686 ± 0.047 at 37 °C, n=19)
   and Yasuda, Targ and Eger's human tissue:blood coefficients are the shape
   of this tier. Both are already cited in this project's agent files.
2. **Secondary synthesis.** A review, textbook, monograph or consensus
   document that collects primary measurements without making one. Legitimate
   for finding the primary source, and for recording what the field
   conventionally quotes — which is a real fact about the reader's
   expectations, and the reason isoflurane's textbook 1.4 is worth naming.
   Not the authority for a stored value on its own strength: the rounding and
   the selection between disagreeing measurements happened somewhere the
   reader cannot see. Adoptable only on the recorded decision below.
3. **Reference implementation.** Another simulator's parameter set — the
   numbers some working program was built to run on. Gas Man is this
   project's reference implementation, and that is why it is named throughout
   this document. The tier is genuinely useful, and is not a euphemism for
   worthless: it fixes the behavior of a widely taught teaching tool as
   something this implementation can be compared against, and it supplies a
   complete, internally consistent set where the primary literature supplies
   scattered measurements made in different laboratories on different
   cohorts. **It is still not a source.** A parameter set is assembled to make
   a program behave; which measurement any individual number descends from,
   and what was adjusted to make the set cohere, are not recoverable from the
   program.

**A lower tier may be adopted, but never silently.** The ranking above says
which tier a reader may trust unexamined. It does not say that a tier-2 or
tier-3 number may never be stored, because this project's provenance table is
mostly made of them and says so a few paragraphs down. What it forbids is an
adoption the reader cannot see. So a stored value whose authority is not a
primary measurement owes three things, and carries all three today:

- **The tier, on the entry itself.** The `tier` field in the data file,
  checked by `make check` against the closed vocabulary — not a claim in prose
  that a reader has to reconstruct.
- **Why no tier-1 source was adopted.** On the entry, or in the file's
  `provenance_gap` where the whole file is in that state.
- **The date and whose decision it was**, where a lower tier is adopted in
  preference to an available primary source rather than for want of one.
  `venous_pool_volume_l` is the worked example: Davis and Mapleson 1981 is
  tier 2, adopted on the project owner's decision of 2026-09-07, replacing a
  round number no source ever contained.

That is a higher bar than a tier-1 citation clears, not a lower one, and it is
deliberately not a licence to prefer the convenient number. Two reasons are
admissible, and finding a primary source being work is not one of them:

1. **No primary measurement of *this quantity, in this population* exists or
   is reachable.** The reference patient is wholly in this state, including
   the parameters that carry a primary citation beside them: Hudgel and
   Devadatta measured awake functional residual capacity where the stored
   volume is an anaesthetised lung, Cattermole et al. measured a different
   population, and Janssen et al. report a muscle mass where this model holds
   a volume. Each note says which of those it is, and that is what makes the
   citation a comparison rather than a source.
2. **The value belongs to a set whose internal consistency is part of what is
   being modelled**, and the reachable primaries would have to be mixed across
   laboratories and cohorts to replace it. This is tier 3's own argument
   above: a reference implementation supplies a complete, internally
   consistent set where the primary literature supplies scattered measurements
   made in different laboratories on different cohorts. The twelve partition
   coefficients are the worked example. Eger, Strum and Eger, and Lerman et
   al. did measure these quantities in this population, so the first reason
   does not cover them — but a single laboratory's blood:gas figure dropped
   into a Gas Man tissue set makes the trajectory a hybrid of two parameter
   lineages — the same objection this document makes below against dividing a
   Gas Man trajectory by a Mapleson MAC, applied one level down.

The second reason is the narrower of the two and is not a way around the
first. It is available only where the primaries are cited on the entry with
the measured value and the difference from the stored one recorded, so that
the cost of the choice is visible to the reader rather than argued away:
desflurane −0.9%, sevoflurane −5.2%, isoflurane −11.0% against the measured
blood:gas coefficients, and the decision itself dated to 2026-09-03
(`PL-D6LX`). `ROADMAP.md`'s planned-milestone item 31 is the route to a
primary coefficient set, which would retire this reason for these twelve.

Where a primary measurement *is* available and simply has not been adopted,
the entry says so in those words and the value **carries no adopted primary**.
That is a statement about the `adopted` field rather than about the citation:
a stored value can name a source and declare its tier while no measurement of
that quantity stands behind it, which is the ordinary case here and the reason
the field exists.

**Full texts held on hand are in `docs/references/`, and holding one changes
nothing about its tier.** The directory exists so that a session checking a
claim can read the source instead of recalling it; `docs/references/README.md`
carries the full citation for each. Baker and Farmery's 2011 *Comprehensive
Physiology* review of inert gas transport in blood and tissues is the closest
published statement of what this document specifies, and it is a tier-2
synthesis for any individual number in it.

**Republication does not promote a value between tiers.** A peer-reviewed
paper that prints a reference implementation's parameter table is a tier-3
citation wearing a journal's name. Both of this project's tier-3 citations are
of exactly that kind, and neither measured a coefficient: De Wolf et al. 2012
is a Gas Man simulation study whose Table 1 is the parameter set it fed to Gas
Man, and Meybohm et al. 2021 is a Gas Man simulation study describing the
product's standard 70 kg patient. Citing either as though the value had been
measured is the specific failure this section exists to prevent.

**Where this project stands, stated rather than implied.** Of the 37 rows in
the provenance table below, 16 are tier 3, one is tier 2, 18 are tier 1, and
two adopt no source of any tier. **Nine of the twelve partition coefficients —
every tissue:gas value — are Yasuda, Targ and Eger's human measurements**,
adopted 2026-09-13 (`PL-FN5F`) after the stored values were checked against that
paper's Table 1; the other three, the blood:gas coefficients, are the Gas Man
set as published by De Wolf et al. and remain tier 3. Ten of the eleven
physiologic parameters in
`src/anesthesia_sim/data/patients/reference_adult.json` are the Gas Man default
patient; and the three `mac_percent` values are the MAC values De Wolf et al.
state they used in their Gas Man simulations, with two tier-2 sources cited
alongside but not adopted — Mapleson's 1996 meta-analysis and the age-related
iso-MAC charts built on it. The two unadopted rows are the machine parameters
in `src/anesthesia_sim/data/machines/reference_circle_system.json`: a circuit
volume that departs deliberately from the published Gas Man figure, and a
default fresh gas flow with no published counterpart at all.

That count moved on 2026-09-13 and the *values* did not. Nine rows crossed from
tier 3 to tier 1 because the project read the paper Gas Man had always named and
found the stored numbers in it, not because anything was recalculated. The
distinction is the whole point of separating `tier` from `adopted`: what
changed was the record of where a number came from.

**The nineteen exceptions are of four kinds**, and naming them is the point of
the counts above. The largest is the nine tissue:gas partition coefficients,
three per agent, adopted from Yasuda, Targ and Eger 1989 on 2026-09-13 — human
autopsy measurements at 37 °C, and the paragraph below the table on Gas Man's
attribution carries how they were checked and why the published figures were
*not* substituted for the stored ones. The eleventh reference-patient parameter, `venous_pool_volume_l`,
is Davis and Mapleson 1981 — tier 2, adopted 2026-09-07 on the project owner's
decision (`PL-8ZJQ`), and the only tier-2 source adopted anywhere in this
project. The three vaporizer maxima are each the calibrated maximum
of a device rather than a physiologic quantity, and each cites a primary source
for it: the Dräger Vapor 2000 specification for sevoflurane, and published
vaporizer-performance measurements for isoflurane (Kelly and Kong 2011) and
desflurane (Johnston et al. 1994, on the Tec 6). And the six MAC-awake rows, a
fraction and a standard deviation for each agent, are adopted primary
measurements: Katoh et al. 1993 for sevoflurane and isoflurane, Chortkoff et al.
1995 for desflurane.

**Recompute these against the table; do not adjust them as rows arrive.** The
pair that stood here until 2026-09-13 — 29 rows, 26 tier 3 — was written when
both were true and survived two changes that made neither: the six MAC-awake
rows were added, and `PL-8ZJQ` moved `venous_pool_volume_l` off tier 3
(`PL-7KDC`). Nothing computed reads them, which is why they could go stale
silently: `check_provenance` decides that a documented key holds the stated
value, never what tier its source carries. `PL-9LXK` is the mechanized answer
to that class.

`mac_percent` is the one of these that a reader now divides by: it is the
divisor of the second display unit, so its tier governs a displayed clinical
value rather than only a starting dial position. "Delivery-limit and MAC
parameters" states what that costs, and "Known limitations" records it.

Every `sources` entry in every data file names its tier. The three agent files
cite the primary measurements alongside their tier-3 values — Strum and Eger
for sevoflurane, Eger for desflurane, Lerman et al. 1984 for isoflurane,
Yasuda et al. for tissue solubility — and each records the measured value, that
it was **not adopted**, and by how much the stored number differs: sevoflurane
−5.2%, isoflurane −11.0%, desflurane −0.9% against the measured blood:gas
coefficients. Isoflurane is the widest gap in the project; the decision to keep
the Gas Man value and label it, rather than move to the textbook 1.4 or to
Lerman's measured 1.46, was taken on 2026-09-03 and the route to primary values
for all three agents is `ROADMAP.md`'s planned-milestone item 31.

`src/anesthesia_sim/data/patients/reference_adult.json` still adopts no
primary source for any of its eleven parameters, and records that in those
words. What changed on 2026-09-06 is that the file now says something specific
about each one rather than only about the set.

**Five carry a measurement cited alongside and explicitly not adopted**, in
the form the agent files use — the measured value, its reference conditions,
and how far the stored number sits from it. Hudgel and Devadatta's helium-
dilution FRC in ten healthy men, read with Wahba's review of the roughly 20
percent reduction under general anaesthesia, brackets the lung gas volume;
Cattermole et al.'s 686 subjects in the 50–75 kg band give a cardiac output
median of 5.51 L/min against a stored value 9.3 percent below it; Janssen et
al.'s whole-body MRI gives a skeletal-muscle mass whose apparent agreement
with the stored muscle volume is a coincidence, since that cohort of men
averaged about 86 kg rather than 70; Heinonen et al.'s PET measurement of
resting adipose perfusion is about half what the stored fat flow fraction
implies; and Frayn and Karpe's review supplies the muscle comparison and the
reason the fat gap is a question about the absolute level rather than the
muscle-to-fat ratio, which the stored fractions get right.

**Six have no comparison, and the file says why for each** rather than leaving
the silence to be read as an oversight. Two are not measurements at all: the
reference weight is a label no equation reads, and the venous pool is a
well-stirred mixing volume setting a 12-second time constant, not the
physiologic venous blood volume, which is several times larger. One is a
derived convention. The remaining three are lumped-compartment aggregates —
the vessel-rich volume and flow fraction, and the fat volume — for which no
single measurement of the quantity this model means exists.

**No stored value changed, and none of this promotes anything.** A measurement
cited beside a tier-3 number does not source it; that is the second of the
three rules below, and these entries are written to be read under it. The gap
between the stored fat perfusion and the measured one is the largest of the
five and is recorded in "Known limitations" as well, because it acts on the
shape of a displayed curve rather than only on a number in a file.

**The lineage is Lowe and Ernst's, not Mapleson's, and that is now read at the
source rather than inferred.** Until 2026-09-06 this file named Mapleson's
1963, 1964 and 1973 papers as its primary lineage, on the strength of their
titles and never having been opened. `PL-6Q8N` removed that framing. Later the
same day the project owner supplied the Workbook's front matter and appendices,
and its Model Parameters table (Appendix B, page 168) settles the question: the
note beneath it reads, in these words, "Values for volume, flow and relative
flow are taken from Lowe and Ernst, 1981" — *The Quantitative Practice of
Anesthesia: Use of Closed Circuit*, Williams & Wilkins. The Workbook attributes
nothing to Mapleson.

That reading also corrected this file about its own contents. **The table
supplies seven of the eleven values, not all eleven**, and the citation had
been pointing at the wrong section — page 183's "Patient default options", which
describes the interface controls and carries no numbers. Alveolar volume, the
three tissue volumes and the three flow fractions are in the table and equal to
what is stored; cardiac output is there only as the sum of the flow column.
Reference weight and alveolar ventilation are interface defaults the supplied
chapters state no number for, and **the venous pool's 1.0 L is not in the table
at all** — its `Blood` row reads 5.00 L. `PL-3YZW` carries that gap and
`PL-7HDS` carried reading Lowe and Ernst, the link that decides whether this
chain ends in a measurement or in another compilation. It ends in neither, and
the reading is the next four paragraphs.

**A second Workbook page, read 2026-09-15, carries three of those four.** The
whole Workbook reached the private corpus that day, and Appendix C, "Gas Man
System Defaults", pages 171–72, prints the program's `GASMAN.INI` verbatim. Its
`[Volumes]` block gives `CKT=8.0`, `ALV=2.5`, `VRG=6.0`, `MUS=33.0`, `FAT=14.5`
and `VEN=1.0`; `[Ratio]` gives `76`, `18`, `6`; `[Defaults]` gives `VA=4` and
`CO=5`. So alveolar ventilation is stated as a number rather than described,
cardiac output no longer rests on a column sum, and the venous pool's 1.0 L is
in the document after all — only `weight_kg` is in neither appendix. **Nothing
is promoted by any of it.** These are one program's defaults written down twice,
tier 3 both times, and the venous pool has since moved off Gas Man entirely.
What it corrects is the record of which page the numbers were read from, below.

**Lowe and Ernst has now been read at the source, and the chain does not end
there.** On 2026-09-08 the project owner supplied pages 55–60 and 82–84 as an
interlibrary-loan scan — the pages having been narrowed to 57 and 83 by two
earlier readings at one remove, Lerou and Booij's system model (*Br J Anaesth*
2001;86:12–28) and Couto da Silva, Mapleson and Vickers' study of Lowe's method
(*Br J Anaesth* 1997;79:103–12), both supplied on 2026-09-06 and read here at
full text. This repository does not hold the scan: it is publisher-copyright
material and the repository is public. The initial is `HJ` — the scan's own
record prints the author as Lowe, Harry J. — so the Workbook's `HF` is a
misprint. Interlibrary loan is a third route, neither the one
`.claude/rules/citing-sources.md` describes nor the personal access the
Workbook arrived by, and `PL-XJ5P` still carries that gap.

**Page 56 answers the tier question against the book, in one sentence.** Of
figure 4.1b, the table the volumes and flows are printed in, it says: "The
figure models a 100-kg patient with normal physiologic organ volumes and blood
flows (9, 19, 20, 26)." The book collects those figures and cites them onward
to four references, of which chapter 4's own narrative names three — Mapleson,
Smith et al. and Zwart et al. Lowe and
Ernst is therefore **tier 2, a secondary synthesis**: the Workbook's upstream
has an upstream, and the only provenance chain the reference patient has still
ends in nobody's measurement. It could have gone the other way — the hierarchy
above admits a lower tier on a recorded decision, and a book that had
*measured* these volumes would have been adoptable without one.

**Those four references are now identified, and three of them are models.**
Chapter 4's reference list is on pages 64–65, supplied on 2026-09-10 as a
second interlibrary-loan scan (`PL-8SDL`). Each was checked against its PubMed
record, and none was read beyond that record — PubMed holds no abstract and no
PubMed Central text for any of the three papers, and the fourth is a monograph
it does not index.

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
  5(3):228–38. Beneken **J E** again, so `JE` is the reading taken here, on the
  same grounds as `HJ` for Lowe — two independent records against one.
- **26.** *Recommendations of the International Commission on Radiological
  Protection*, p. 151. Report of Committee II on Permissible Dose for Internal
  Radiation. Pergamon Press, Oxford, 1960. — not indexed by PubMed, which does
  not cover monographs, and unreachable from here: `www.icrp.org`,
  `journals.sagepub.com` and `doi.org` each returned nothing through the egress
  proxy on 2026-09-10.

References 9, 19 and 20 are **uptake-and-distribution models**, which is what
this chain needed to know: a model consumes organ volumes and blood flows, it
does not measure them, so none of the three can be where figure 4.1b's figures
came from. Reference 26 is the only one of the four that is not an anesthetic
model, and it is cited to a single page — which is the page that ends the
chain.

**The chain terminates at tier 2, and reaches tier 1 nowhere.** Page 151 of the
ICRP report was supplied by the project owner on 2026-09-10 and read here
(`PL-LT51`). It carries **Table 8, "Organs of standard man — Mass and effective
radius of organs of the adult human body"**, tabulated for a total body of
70,000 g. A "standard man" is a reference specification agreed by a committee,
the document's own title being *Report of Committee II*, and the table gives no
per-row citation, sample count or dispersion — unlike Table 7 on the facing
page 150, whose tissue rows each carry a parenthesised count. Under "Source
hierarchy" above, a consensus document that collects primary measurements
without making one is **tier 2**. So the reference patient's longest provenance
chain runs Gas Man (tier 3) → Lowe and Ernst (tier 2) → ICRP Committee II
(tier 2), and **nothing on it was measured by anybody this file can name.**

**Table 8 has no blood flows**, and that is the more useful half of the
finding. It gives mass and effective radius, nothing else, while Lowe and Ernst
cite all four references together for "organ volumes *and blood flows*". So the
perfusion fractions — the half that sets every time constant this model
computes — cannot descend from reference 26 at all. They descend from 9, 19 or
20, all three of which are models, and reading those three is now the more
valuable ask rather than the less.

**Four of Lowe's rows correspond to Table 8 closely enough to be an
inheritance**, at 100 kg where his kilogram column reads as per cent of body
weight: brain 2.1 against 2.1, kidney 0.4 against 0.43, heart 0.4 against 0.43,
muscle 42.6 against 43. Five do not — skin 10.0 against 8.7, adipose 15.0
against 14, blood 7.0 against 7.7, lung 0.8 against 1.4, bone 12.0 against a
skeleton of 10 without marrow or 14.2 with — and **the liver is the outlier
that matters: 5.7 against 2.4.**

**That gap has a candidate, and it is this file's arithmetic rather than the
book's.** Liver 1,700 g plus gastrointestinal tract 2,000 plus spleen 150 plus
pancreas 70 is 3,920 g, **5.60% of 70 kg against Lowe's 5.7%** — the
hepatoportal compartment an uptake model lumps because the splanchnic bed
drains through the liver. No other grouping of Table 8 comes as close. Neither
document says so, and it convicts nobody.

**Why it is recorded rather than left out.**
`tissue_groups.vessel_rich.volume_l` is stored as 6.0 L, and the only grouping
of Lowe's ten compartments reproducing both that volume and the stored 0.76
perfusion fraction is kidney + heart + brain + liver at 8.6% of body weight. On
ICRP's own rows those four organs are **5.36%, which is 3.75 L at 70 kg** — 38%
below what is stored. The stored value therefore rests on a lumping decision
taken one link up the chain, and that decision is now visible where it was not.
**No stored value moves on this and none should**: lumping the splanchnic bed
into the liver compartment is ordinary modelling, "Tissue compartments" above
already treats the vessel-rich group as one lumped tissue, and nothing here is
sourced to ICRP.

**References 19 and 20 are read too, and they measured nothing either.** Both
were supplied by the project owner on 2026-09-10 and read at full text
(`PL-LT51`). They share one parameter set: reference 20's Appendix says its
tables "are the same as used by N. Ty Smith in his article … where he gives the
rationals for our choice", so reference 19 is where the provenance is. And
reference 19 says, of the table this chain would need, that it "lists the
**assumed** blood volumes, tissue volumes, and partition coefficients" — its
own word, with no source given for any of them. Its *flows* are compiled from
"several sources, most of which can be found in a recent review", the review
being the authors' own handbook chapter, with the awake cardiac output of 5,800
ml/min taken from Milnor's chapter in *Medical Physiology*, 12th edition. The
compilation did not balance and was made to: total cardiac output 3,480 ml/min
against regional flows summing to 3,290, and "the discrepancy was compensated
for by adjusting the values for skin and skeletal muscle flows". **A stated
assumption is not a source and an adjusted sum is not a measurement**, so
neither paper is promotable and neither is a candidate for adoption.

**They are not the origin of figure 4.1b either.** Reference 19 models a 75 kg
man in twelve compartments — arterial, brain grey, brain white, heart,
well-perfused organs, poorly-perfused tissue, fat and fatty marrow, splanchnic,
skeletal muscle, skin shunt, vena cava, lung — against Lowe's ten rows for a
100 kg patient, and the numbers do not correspond: its vessel-rich equivalent
is 64.0% of cardiac output against Lowe's 76%, and its fat is 16.3% of body
mass against Lowe's 15.0%. **So the perfusion fractions still have no
identified origin.** Reference 26 gives masses and no flows; 19 and 20 give
different flows for different compartments; reference 9, Mapleson 1963, is the
last of the four unread, and reference 20 names him only as the source of the
model *concept*.

**Reference 9 closes the chain, and it makes two of the four references one
document.** Mapleson 1963 was supplied and read on 2026-09-10 (`PL-LT51`). His
Appendix 1 opens: "*Tissue volumes and blood supplies.* With the following
exceptions the volumes in Table 1 are those for the 'standard man' of the
International Commission on Radiological Protection (I.C.R.P.) (23)…" — and his
reference 23 is that report at **page 151**, which is Lowe and Ernst's
reference 26. So Lowe and Ernst very likely took the ICRP citation from
Mapleson's own list, and references 19 and 20 are Mapleson's Table 1 lumped and
relabelled: under Smith's own lumping footnotes it reproduces in **nine rows of
nine**, the nine summing to 58.04 litres against Mapleson's own 58.04.

**Mapleson's Table 1 is the most honestly sourced document in this chain, and
it still measures nothing.** Its volumes are ICRP's with six exceptions he names
one by one — grey and white matter from Pittinger et al., the marrows and bone
cortex from Ellis, skin nutritive derived by him from forearm geometry, the
arterial-to-venous blood ratio "taken to be as in dogs", lung parenchyma from
Cander and Forster, and the air in the lungs from "the average of all
measurements in Dittmer and Grebe in which the average age was over 20", which
"gives a functional residual capacity of 2.5 liters". Its flows are compiled
from about twenty sources with a note on every row; some rows are animal
(adrenals from dogs, fatty marrow from goats), one is called an *Estimate*, and
one is neither: **"Skin shunt: Values chosen merely to complete cardiac
output"** — 1,290 of 6,480 ml/min, **19.9% of the total** and the second-largest
flow in the table.

One assumption in that appendix is where this model's whole representation of
perfusion comes from: "it has been thought legitimate to assume that **the
blood flow to any region is a fixed fraction of the total cardiac output** from
20 to 70 years of age."

**And the negative finding, which is the one that matters.** Figure 4.1b's flow
column reproduces from none of the four. On Mapleson's own rows, kidney + heart
+ brain + liver is 3,820 of 6,480 ml/min — **59.0%** — and every well-perfused
organ together is **63.0%**, against Lowe's **76%** and Smith and Zwart's 64.0%;
muscle plus skin nutritive is 10.2% against Lowe's 13%, and fat plus fatty
marrow 4.0% against Lowe's 5%. **The perfusion fractions this model runs on
have no identified origin in any reference the book names for them.** Reference
26 has no flows at all, and the other three do not match. That is established
now rather than outstanding — **and it is a statement about four documents that
have been read, not about the world.** It does not follow that no origin
exists: the book prints more than one table and Gas Man may lump differently.

**Two of the three coincidences above are lineage after all, and one is not**
(`PL-ZD67`). The 2.5 L is Mapleson's functional residual capacity, a mean of
published human measurements cited to Dittmer and Grebe's *Handbook of
Respiration* — not a round number somebody chose. It is still not this file's
source: Mapleson's row is FRC plus half the tidal volume where this file stores
an alveolar gas volume, and the value reaches here through Gas Man, whose
upstream is Lowe and Ernst, who lump the quantity away. The 33 is Mapleson's
muscle 30 plus skin nutritive 3, which is exactly how Smith prints it — and it
is *not* this file's 33.0, since Lowe's muscle row is 29.8 L at 70 kg and
reproduces the stored value under no grouping. Alveolar ventilation 4 l/min
stays a coincidence: Mapleson gives a formula, not a figure.

**Three of this file's stored values also appear in those tables**, and where
each came from is settled in the paragraph after next rather than left as a
resemblance: alveolar ventilation 4 l/min, functional residual capacity 2.5 l
in reference 20's table only, and a skeletal muscle tissue volume of 33 litres.
**No stored value moves on any of it.**

That Mapleson 1963 turns out to be one of the four is not a rehabilitation of
that lineage. The removed claim was that Mapleson's papers were the *Workbook's*
primary source, on the strength of their titles; the Workbook attributes nothing
to Mapleson, and this is a different document citing him for a table it
collected, two links further up.

**The model patient is 100 kg, which is why the material reaches this project
as fractions.** Page 56 picks that weight so that "the organ weights can also
be read as per cent of total body weight", so Lerou and Booij's Table 6 of
fractions is the book's own table divided by 100 rather than a normalization
they performed, and nothing in the book states a 70 kg parameter set. Cardiac
output is allometric, and that too is now read rather than reported: page 59
gives the cardiac output for its worked prime dose as $`2M^{3/4}`$ dl/min, "or
63.25 dl" for the 100 kg patient —
0.2 times body mass to the three-quarter power in L/min, **4.84 L/min at
70 kg** against the 5.0 stored here, which would need 73.1 kg. The book's own
worked 63.25 dl is what fixes the exponent independently of reading a
superscript off a scan. `PL-YKSM` decided on 2026-09-08 that the fixed 5.0
stays; "Known limitations" below carries the reasoning.

**And the relation itself is derived, not measured — pages 17–19 say from
what.** Page 59 states $`2M^{3/4}`$ without citing anything, and until
2026-09-10 that was where the trail stopped. Chapter 2 builds it in three
steps, and neither of the two constants is a cardiac-output measurement:

- **Figure 2.2, page 17** plots oxygen consumption against body weight for
  mammals from 0.03 kg to 8,000 kg, log–log linear, slope given as
  "approximately 10 kg^(3/4)". It is reproduced by permission from *Brody, S.
  Bioenergetics and Growth. Reinhold, New York, 1945* — an interspecies
  metabolic allometry, not a human study.
- **Page 17** takes the arteriovenous oxygen content difference as "about 5 ml
  of O₂/dl of blood", attributed to Guyton et al. (the chapter's reference 13),
  who are also credited with concluding that kg^(3/4) "is probably a better
  index of cardiac output than any other parameter, including surface area".
  Chapter 2's reference list is outside the pages supplied, so that citation is
  unresolved; `PL-LT51` carries it.
- **Figure 2.4, page 19** is the arithmetic. kg^(3/4) × 10 gives O₂ use in
  ml/min; O₂ use ÷ 5, the divisor annotated "(a–v)DO₂ = 5 ml/dl", gives cardiac
  output in dl/min. The figure also draws the composed edge directly —
  kg^(3/4) × 2 → $`\dot{Q}`$ in dl/min — which is page 59's constant.

So $`0.2M^{3/4}`$ is Brody's mammalian metabolic allometry divided by an
arteriovenous difference assumed constant across mammals. **4.84 L/min at 70 kg
is therefore a derived interspecies extrapolation and must not be read as a
measured human cardiac output.** "Known limitations" below is where that
matters — it is the one place this document sets the figure beside Cattermole
et al.'s measured median — and it says so there (`PL-DZQT`).

**Checked against the book itself, the Workbook's attribution holds for three
of the seven values and fails for four.** The vessel-rich pair reproduces
exactly and *uniquely*: kidney, heart, brain and liver are 8.6% of body weight
at 76% of cardiac output, which is 6.02 L at 70 kg against the stored 6.0 and
0.76 against the stored 0.76 — and across all 1023 non-empty groupings of the
book's ten compartments, at a tolerance of half a percentage point, no other
grouping matches both. The same exhaustive search returns **zero** groupings
for the stored muscle pair (33.0 L at 0.18, against the book's muscle row at
29.8 L and 0.130) and zero for the stored fat pair (14.5 L at 0.06, against
adipose at 10.5 L and 0.050). Alveolar volume is the third that holds, and it
holds negatively: the book states no alveolar gas volume at all, lumping the
circuit and the patient's FRC into a single ventilatory volume of "about
100 dl", so the Workbook cannot have taken 2.5 L from it.

**What survives for the other four is the split rather than the values.** The
book's five non-vessel-rich compartments take 13 + 3 + 2 + 1 + 5 = 24% of
cardiac output, and the stored muscle and fat fractions sum to exactly 0.24;
their volumes do not follow, 83.6% of body weight being 58.5 L at 70 kg against
the stored 47.5 L. So Gas Man appears to have kept the book's 76/24 flow split
and redistributed the 24 across two compartments where the book has five, over
a smaller tissue volume. That arithmetic is this project's and it convicts the
Workbook of nothing — Gas Man may lump differently, or work from a page outside
the range supplied. The data file carries the figures and the per-value detail.

**Nothing is promoted or adopted by any of it.** All seven stay tier 3 and
unadopted: reading where Gas Man's numbers came from is not evidence that they
were measured. For the four that do not reproduce there is nothing here to
adopt, and for the ones that do, adopting would mean naming as the authority a
compilation whose own four sources are unread. What the reading buys is that
the attribution has been checked against the document rather than against a
report of it, and that the tier of the next link is now a known question
instead of an assumption.

**The venous pool now has a published counterpart, and it is not the stored
1.0 L.** Davis and Mapleson (*Br J Anaesth* 1981;53:399–405), supplied by the
project owner and read at the source 2026-09-07, quantify a standard man of
70 kg with a total blood volume of 5189 ml and a cardiac output of 6480 ml/min.
Page 400 states that **for models of inhaled anaesthetics** the two venous pools
may be combined, "in which case it would be marginally more accurate to make the
arterial pool 799 ml (15.4% of the total blood volume) and the combined venous
pool 1222 ml (23.6%)". That combined pool is the same object as $`V_v`$ here:
one well-stirred venous pool carrying tissue return. Their Appendix derives it
from ICRP (1975) blood distribution rather than measuring it, which is what
keeps it tier 2. **It was adopted on 2026-09-07, on the project owner's decision** (`PL-8ZJQ`),
and is the first value in this file to carry a source other than the Gas Man
Workbook. `venous_pool_volume_l` is 1.222 L, and the key was renamed from
`venous_blood_volume_l` in the same edit (`PL-BD94`) because the old name reads
as the physiologic venous blood volume, which this is not. At the stored
5.0 L/min cardiac output the mixed-venous time constant moves from 12.0 s to
14.7 s.

**What that costs, measured rather than argued.** The 30-minute $`F_A/F_I`$
wash-in distances are unchanged to two decimal places (+0.16, +0.31, +0.79,
+0.38 SD): the pool is long equilibrated by then, so the published wash-in
comparison cannot discriminate between the two values and is no evidence either
way. The 5-minute $`F_A/F_{A0}`$ elimination ratios move **0.11 to 0.13
published SD further from** their cohort means — sevoflurane +3.67 to +3.79,
isoflurane +4.02 to +4.15, desflurane +1.02 to +1.13 — because a larger pool
returns more agent to the lungs. That is the same direction § "Published
wash-in validation test" already attributes to this model's rebreathing circuit
rather than to tissue return, and it is a tenth of the gap it adds to. The nine
oracle reference states were re-derived and re-pinned in the same change.

**It also answers the arterial question, against the arterial reading.** The
suspicion was that the stored 1.0 L might be an arterial compartment under a
venous name, on Lerou and Booij's arterial fraction of 0.2 — 0.98 L at their
4.9 L total, within 2% of what is stored. Davis and Mapleson's own arterial pool
for an inhaled-anaesthetic model is 799 ml, 15.4% rather than 20%, so that
coincidence does not survive the primary source. Their venous pool is the closer
structural match, and the time constants nearly agree: 1222/6480 = 11.3 s
against the 1.0/5.0 = 12.0 s this file held until 2026-09-07. That near
agreement is a property of the time constant rather than of the volume, and it
was not evidence of a shared lineage — nothing documents Gas Man as having taken
anything from this paper.

**Where 1.0 L came from is answerable, and the answer changed on 2026-09-15.**
The value entered the repository on 2026-08-22 in `875ba08`, "Build v0.1.0 sevo
patient simulation", the tenth commit — written into the data file alongside the
rest of the reference patient and carrying the citation "Gas Man Workbook and
Laboratory Manual. Default Options: Patient Defaults", whose note read "The
default 70 kg patient uses alveolar volume 2.5 L, venous volume 1.0 L, alveolar
ventilation 4 L/min, cardiac output 5 L/min, tissue volumes 6/33/14.5 L, and
flow percentages 76/18/6". `PL-XTMB` read that section at the source: it is
Appendix E, page 183, and it describes the interface controls without carrying a
number. The table that does carry numbers, Appendix B page 168, has a `Blood`
row of 5.00 L and nothing at 1.0. On that evidence this section said, until
2026-09-15, that none of the four sources ever cited for the value contained it.

**It is in the Workbook, one appendix further on.** Appendix C's `GASMAN.INI`
listing, page 172, reads `[Volumes] … VEN=1.0`, and the v0.1.0 note's sentence
is that listing's three blocks item for item — the volumes, the flow fractions
as the *percentages* `76`/`18`/`6` the INI writes rather than the table's
0.76/0.18/0.06, and `VA=4` with `CO=5` from `[Defaults]`. So the original
citation was **mis-sectioned rather than borrowed**: it named Appendix E, the
numbers were read off Appendix C, and every value in that sentence including
1.0 L is on that page. `PL-XTMB` and `PL-3YZW` quote Appendix B and Appendix E
and never Appendix C; whether that page was among those supplied on 2026-09-06
and went unread is not recorded.

**None of which promotes the value or argues for restoring it.** `VEN=1.0` is a
program default, tier 3, and Davis and Mapleson's 1222 ml — tier 2, and the same
object this model has — was adopted on 2026-09-07 and stands. What changes is
that the stored venous pool is a considered replacement for Gas Man's own
default rather than the correction of an orphan, and that the one round number
in this file with no counterpart anywhere is now `weight_kg`, which no equation
reads.

**So, three rules for a `sources` entry.**

- Name the tier. Where the stored value is not a primary measurement, say
  which value the primary literature reports and by how much the two differ,
  in the note, in words a reader comparing against a textbook can act on.
- Do not let a primary citation stand in for a primary value. Citing a
  measurement *alongside* a tier-3 number does not source it; a file that
  looks sourced while the number in it came from somewhere else is worse than
  one that cites nothing, because it stops the reader checking.
- Where no primary source has been adopted, record that as an open gap rather
  than as a settled citation. "No primary source has been adopted for this
  value" is a legitimate provenance state for an educational simulator, and a
  recoverable one. A tier-3 citation presented as settled is neither.

This applies to what a session *says* as well as to what it writes down.
Answering "where does this constant come from?" with Gas Man, or with a paper
that reports Gas Man's table, states a tier-3 provenance as though it were a
measurement, and is the same error made in conversation instead of in a file.

**The first and third of those rules are now schema, and `make check` decides
them.** Data files moved to `schema_version` 2 on 2026-09-07 (`PL-1JDD`).
Every `sources` entry carries two new required fields, and a data file may
carry one new optional top-level string. They are written as a list rather
than a table because the provenance table below is found as the first table in
this section, and a second one above it would be read in its place:

- `tier`, on each `sources` entry: `primary`, `secondary` or
  `reference-implementation` — which of the three tiers above the *document*
  is.
- `adopted`, on each `sources` entry: whether this file names that source as
  the authority for a value it stores.
- `provenance_gap`, optional and top level: why no primary source has been
  adopted, where none has been.

`tools/doc_check.py`'s `check_source_tiers` holds two exact rules: every entry
declares a tier from the closed vocabulary and an `adopted` flag, and a file
with no entry that is both `primary` and `adopted` records a non-empty
`provenance_gap`. Both fail the build rather than raising an advisory, because
neither needs any context to decide. `src/anesthesia_sim/core/parameters.py`
validates the same vocabulary at load, so a bad tier fails when the file is
read rather than when the checker next runs.

**`tier` and `adopted` are two fields because one would decide nothing.** Every
agent file cites primary measurements it has explicitly *not* adopted, and so
does the reference patient — it cites five. A check reading the tier alone
would therefore report all four of this project's data files as
primary-sourced, on the same day this document records that most of the
provenance table's rows are tier 3. That count is stated once, under "Source
hierarchy", and deliberately not repeated here: it moves whenever a row is added
or a source is adopted, and two copies of it is how the previous pair came to be
wrong (`PL-7KDC`). That is the second rule above, arriving as the exact failure it
exists to prevent, so the check has to read the adoption rather than the
citation list. As it stands, the three agent files each declare two adopted
primary sources — `mac_awake` and the vaporizer maximum — and
`src/anesthesia_sim/data/patients/reference_adult.json` declares none and
carries the gap.

**What the check does not decide is whether a citation labelled `primary`
really is one.** That needs somebody who has read the paper, and a tool
guessing at it — by author, by journal, by a keyword denylist on a product
name — would be authoritative and wrong. The tool checks that a claim was made
and is well-formed; a reviewer checks that it is true. It is the same split the
provenance table below already runs on: the checker decides that a documented
key exists and holds the stated value, never that the value is right.

The following table records the values selected for v0.1.0. Each value is
loaded and schema-validated from a versioned data file rather than
hardcoded; full citations, definitions, and reference conditions are
recorded as `sources` entries in that file, not duplicated here.

Each row names the exact JSON key path it documents alongside the file, so a
row is traceable to one stored value rather than to a file that happens to
contain a matching number. `tools/doc_check.py` (run by `make check` and CI)
holds the table to the data files in both directions: every row must name a
key the file holds and state the value it holds, and every numeric parameter
in every data file must have exactly one row. A derived row states the stored
value alongside the derived one — the tissue:blood coefficients are computed
at load time from the tissue:gas and blood:gas values, so their rows name the
stored tissue:gas key and show the division.

The table is not the only place these values appear. Where the prose restates
one — the reference adult's alveolar volume and ventilation, each agent's
blood:gas coefficient, vaporizer maximum and MAC — the sentence carries a
marker naming the file and key it restates, written as an HTML comment so it
is invisible in the rendered document:

```text
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
```

`doc_check.py` holds both halves of that: the key against the data file, and
the stated value against the paragraph the marker sits under. So neither the
file nor the sentence can move without the other, which is the failure the
markers exist for — before them, editing a data file updated this table, which
the checker forces, and left the surrounding prose quietly wrong.

A figure *derived* from several stored values — no file holds it — carries a
`derived:` marker naming its inputs instead, and one figure may carry several
where its inputs span more than one file:

```text
<!-- derived: 20.7 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4, default_cardiac_output_l_min = 5 -->
```

When an input moves, the checker reports that the figure must be recomputed
and names it. It never recomputes the figure: the rounding and the units are
judgment, and a plausible wrong number in this document is worse than none.

**Rewording a marked sentence is expected to fail the check.** That is the
marker asking to be moved or updated with the sentence, not a false alarm. A
number a data file does not hold — a solver tolerance, a flow-sweep point, a
worked example — carries no marker and is not checked here, which is why the
markers are explicit rather than a scan for numerals: `2.5` appears in this
document as an alveolar volume in litres, a tolerance in seconds and a flow in
litres per minute, and binding all three to one key would be confidently wrong
in the places a reader trusts most.

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
describe; no equation in this model consumes it (`PatientParameters.weight_kg`
is loaded and range-validated, and read by nothing else). Compartment volumes
and flows are the source's absolute values for a 70 kg adult, not quantities
scaled from a weight, so changing the weight alone would not rescale them. The
litres are Gas Man's form rather than its upstream's: Lowe and Ernst, the book
the Workbook names, prints the same material as per cent of a 100 kg body with
cardiac output an allometric function of mass (`PL-YKSM`).

**The vessel-rich flow fraction is 0.76 here and 75.8% in the one reachable
publication of the same parameter set**, and the difference is recorded rather
than reconciled away. The Workbook's own page-168 table gives the vessel-rich
relative flow as 0.76, read at the source 2026-09-06, and that is where the
stored value comes from. De Wolf et al. 2012's Table 1 — the same paper the
twelve partition coefficients come from — prints 75.8, and 75.8 + 18 + 6 =
99.8. `_ReferenceAdultPayload._perfusion_fractions_must_sum_to_one` and
`PatientCompartments.__post_init__` each reject a set summing outside
`FLOW_FRACTION_TOLERANCE = 1e-12` of 1.0, so the published triple could not be
stored as printed even if it were preferred, and that tolerance stays where it
is: one wide enough to admit 99.8% would admit a transcription error silently.
The consequence of the difference is 0.26% on the vessel-rich time constant,
which is inside anything a learner reads off the curve; the provenance is the
finding, not the arithmetic. `reference_adult.json`'s De Wolf entry carries it
in full (`PL-0NQ1`).

**The two machine rows adopt no source at all, which is a stronger statement
than the reference patient's gap and is meant to be.** They are the apparatus
in front of the patient rather than the patient, so they live in
`data/machines/reference_circle_system.json` — a third kind of parameter file,
added by `PL-4YY1`, which moved both out of `core/circuit.py` field defaults
where no provenance row could reach them and changed neither value.

- **Circuit volume, 6.0 L.** The Workbook's own page-168 table publishes 8.0 L,
  and De Wolf et al. 2012's Methods print the same 8 L for the simulations
  their Table 1 supplied the coefficients to. This project keeps 6.0
  deliberately, on the project owner's ruling of 2026-09-01 that which value is
  used is not critical. What the departure changes is the machine's own share
  of the early rise: $`\tau_C = V_C/\dot V_F`$ is 90 s here against 120 s at
  8.0 L and the same flow, a 25% shorter apparatus lag. That lag is the part of
  the inspired curve a learner is most likely to attribute to uptake, so a run
  reproducing a published Gas Man trajectory has to set 8.0 L rather than
  assume it.
  <!-- derived: 90 s from data/machines/reference_circle_system.json circuit_volume_l = 6, default_fresh_gas_flow_l_min = 4 -->
- **Default fresh gas flow, 4.0 L/min.** No published counterpart exists for
  this one anywhere this project has reached. The Workbook's parameter table
  gives the circuit row a volume and no flow, its interface defaults are
  described without numbers, and the two Gas Man simulation studies read here
  chose flows for their own purposes (De Wolf et al. 1 L/min; Meybohm et al.
  10 L/min for washout). It is a project convention: a routine mid-range
  clinical flow, well inside the supported interval, that puts the circuit time
  constant at 90 s — long enough for the machine lag to read as a distinct
  phase of the early rise, short enough to resolve within the first minutes of
  a teaching run. That is a design rationale, and the data file labels it as
  one rather than as a measurement.

**One measured circle-system volume is now held, and it bounds the first row
rather than replacing it** (`PL-QBKQ`). Targ, Yasuda and Eger measured a
conventional circle system by water filling at **9860 ml** (*Anesth Analg*
1989 Aug;69(2):218–25, PMID 2764290 — the same study behind the inert-circuit
entry under "Known limitations"; read at full text 2026-09-13 from the private
reference corpus). It is not adopted, and the reason is what it contained: the
system it measured included a latex reservoir bag at the Y-piece **standing in
for the patient's lungs**, so adopting 9.86 L as `circuit_volume_l` would put a
lung inside the circuit and then model it again as the 2.5 L alveolar
compartment. Subtracting the bag is not available — the paper states no bag
volume, and a latex bag full of water distends past whatever it holds as a gas
reservoir.

What the measurement supplies instead is a **bound and an ordering**: a real
conventional circle system's apparatus volume is at most 9.86 L, which leaves
both the stored 6.0 L and the Workbook's 8.0 L admissible and puts the three
figures in one order with only one of them measured. At 4.0 L/min the implied
apparatus lags are 90 s, 120 s and 148 s.
<!-- derived: 148 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->

**Read the like-for-like comparison, not the bare one.** Targ measured
apparatus *plus* lung; this model's corresponding total is
$`V_C + V_A`$ = 6.0 + 2.5 = 8.5 L, which is 13.8% below the measured 9.86 L
where the bare 6.0 against 9.86 reads as 39% below. The study invites the
comparison in that form: its Figures 3 and 5 draw the ideal wash-in and
washout as $`100[1 - e^{-(\dot V/V_S)t}]`$ with $`V_S`$ = 9.86 L, so its own
time constant is total system volume over inflow — the same $`V/\dot V_F`$
this document uses. It remains a comparison and not an adoption: a latex bag
is not a lung, and that apparatus had no patient taking up agent.
<!-- derived: 8.5 L from data/machines/reference_circle_system.json circuit_volume_l = 6.0 -->
<!-- derived: 8.5 L from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->

There is no "arterial blood-pool volume" row: arterial blood is flow-limited
and holds no independent state (see "Model boundary"). Tissue:blood
coefficients are derived at load time (`AgentParameters` properties in
`core/parameters.py`) as tissue:gas divided by blood:gas, not stored
redundantly in the data file. The tissue-blood partition-coefficient tests
in `tests/unit/test_parameters.py` guard this derivation.

### v0.2.0: isoflurane and desflurane

Isoflurane and desflurane use the same governing equations, compartment
structure, and `data/patients/reference_adult.json` physiologic parameters
as sevoflurane — only each agent's own `data/agents/*.json` partition
coefficients differ. All twelve values reached this project through one table
(De Wolf et al. 2012, Table 1 — the paper already cited for sevoflurane), so the
three data files are directly comparable rather than assembled from unrelated
sources.

**Since 2026-09-13 that comparability rests on something better than a shared
publisher.** The nine tissue:gas values in that table are Yasuda, Targ and Eger
1989's human measurements, checked against the paper and adopted (`PL-FN5F`), so
the three agents are comparable because their tissue coefficients come from *one
study, one laboratory, one technique and one cohort* — measured side by side in
the same specimens. That is the strongest form of the property a MAC-normalized
axis needs, not a weaker one: whatever the systematic error of that technique,
every agent carries it identically. The three blood:gas values remain the Gas
Man set and remain tier 3, so the shared-error argument covers them in its
original, weaker form.

Both halves of that argument are about the *coefficients*, which is what this
paragraph is about. It does **not** extend
to the three `mac_percent` divisors, whose deviations from the primary
literature run in opposite directions between sevoflurane and desflurane;
"Delivery-limit and MAC parameters" measures that separately. Each agent file records the primary
measurement alongside its stored number and states the difference.

**Gas Man says those coefficients are Yasuda's, and that claim is recorded
without being acted on.** The note under the Workbook's own page-168 parameter
table reads "Values for isoflurane, halothane, desflurane and sevoflurane are
taken from Yasuda, Targ and Eger" — which, if it held, would make the twelve
coefficients descendants of a human tissue-solubility measurement rather than a
simulator's choices. Four things stop it from moving the tier, and the first is
sufficient alone:

- A program's statement about its own provenance is the program talking. That
  is the same rule as "Republication does not promote a value between tiers"
  above, applied one link further back.
- The Workbook names a different document from the one the agent files cite:
  its reference 45 is the abstract `Anesthesiology 69:A615`, from the 1988 ASA
  annual-meeting supplement, not Yasuda, Targ and Eger's 1989 *Anesthesia &
  Analgesia* paper. What the abstract reports is unknown here.
- The same paragraph contradicts itself for sevoflurane, crediting it to Yasuda
  and, one sentence later, to "the package insert and Abbott data".
- The arithmetic is close and not exact. Yasuda's measured brain:blood times
  each file's stored blood:gas reproduces sevoflurane's and desflurane's stored
  vessel-rich tissue:gas exactly (1.1050 → 1.1; 0.5418 → 0.54) and misses
  isoflurane's (2.0410 against a stored 2.1) by 2.9%, which is inside half the
  measurement's own standard deviation. Close enough to suggest the route,
  never enough to name it.

**The check has since been run, and the claim holds.** The project owner
supplied Yasuda, Targ and Eger's full text later the same day; it was read at
full text on 2026-09-13 and is in the private reference corpus. Its Table 1
reports tissue:**gas** coefficients — the quantity the agent files store — from
14 autopsy specimens, 6 to 10 per tissue, mean age 65.8 ± 14.4 yr, equilibrated
at 37 °C. Against the nine stored values:

| | vessel-rich (Yasuda's brain) | muscle | fat |
| --- | ---: | ---: | ---: |
| sevoflurane | 1.1 vs 1.15 ± 0.07 (−0.71 SD) | 2.4 vs 2.38 ± 1.03 (+0.02 SD) | 34.0 vs 34.0 ± 6.0 (exact) |
| isoflurane | 2.1 vs 2.09 ± 0.10 (+0.10 SD) | 4.5 vs 4.40 ± 1.97 (+0.05 SD) | 70.0 vs 64.2 ± 12.3 (+0.47 SD) |
| desflurane | 0.54 vs 0.54 ± 0.02 (exact) | 0.97 vs 0.94 ± 0.35 (+0.09 SD) | 13.0 vs 12.0 ± 2.0 (+0.50 SD) |

All nine sit within 0.71 SD of the measured mean and three reproduce it to the
stored precision, which is not a coincidence available to a parameter set
assembled from somewhere else. So the Workbook's attribution is confirmed on the
arithmetic rather than on its own say-so, and its self-contradiction resolves in
Yasuda's favour: sevoflurane's three stored values match this paper, not a
package insert.

Two things follow that are not about provenance:

- **The vessel-rich coefficient is Yasuda's *brain* value.** Table 1 measures
  brain, heart, liver and kidney separately (sevoflurane 1.15, 1.21, 1.25,
  0.78), and any weighted average of the four would land away from the stored
  figure. The compartment this document calls the vessel-rich group is
  parameterised as brain, and a learner reading its trace is reading a brain
  trace.
- **This paper is not a source for the stored blood:gas values.** It measured
  none. Its Table 2 tissue:blood figures are calculated "by dividing the
  tissue/gas partition coefficient by the published values for the blood/gas
  coefficients adjusted for age", so Table 1 ÷ Table 2 recovers a 65.8-year-old
  cohort's age-adjusted blood:gas, 4.9–9.4% above the three round figures stored
  here.

**The tier moved and the values did not** — the project owner's decision of
2026-09-13, taken as two separate questions (`PL-FN5F`).

*Adopted.* The nine tissue:gas coefficients descend from a primary human
measurement, so Yasuda, Targ and Eger is now the adopted authority for them in
all three agent files and they are tier 1. De Wolf et al. stays adopted for the
three blood:gas values alone, which this study did not measure. Nothing
numerical changed with the adoption; what changed is the record of where the
numbers came from, which is what separating `tier` from `adopted` exists to
carry.

*Declined.* Storing Yasuda's published figures in place of Gas Man's rounding of
them would move three displayed time constants — sevoflurane vessel-rich +4.5%
at 1.15 against 1.1, isoflurane fat −8.3% at 64.2 against 70.0, desflurane fat
−7.7% at 12.0 against 13.0 — and would require recomputing every pinned
reference state under `tests/reference/`, which are this parameter set's
solution. The accuracy it would buy is also inside the error the model's own
lumping already carries: the vessel-rich group is one compartment standing for
brain, heart, liver, kidney and viscera, so 0.05 on a brain measurement is not a
difference this structure can use. `PL-D6LX`'s original decision to keep the Gas
Man values therefore stands, now for a better-evidenced reason than it had
(`PL-ZP7Z`, `PL-B9K7`, `PL-FN5F`).

Desflurane is markedly less soluble than sevoflurane, which is itself less
soluble than isoflurane (blood:gas 0.42 < 0.65 < 1.3). This does not change
any equation: lower solubility only means faster equilibration through the
same closed-form solutions, which `tests/reference/test_multi_agent.py`
checks directly by comparing simulated alveolar/circuit ratios rather than
only comparing the static coefficient values.

<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->

**Desflurane's tissue coefficients have been questioned against a published
measurement and kept.** Its five-minute elimination is the one comparison in
this repository that misses a human measurement in the direction of washing
out too fast, and the sensitivity of that ratio makes the vessel-rich
coefficient the obvious suspect. It is not the cause, and the reasoning is in
"Desflurane's residual, and why the parameter file was not changed" rather
than here so that it sits beside the comparison that raised it. Read that
before changing any coefficient in `data/agents/desflurane.json`: the value
the disagreement demands is nineteen standard deviations above the human
measurement and would invert the measured solubility ordering of the three
shipped agents.

### Delivery-limit and MAC parameters

Two per-agent parameters are carried in the agent data files but take no
part in the governing equations. Both exist to constrain or initialize a
user-facing control, and both are recorded here because a value a clinician
could read or act on is safety-critical whether or not the model integrates
it.

`max_delivered_concentration_percent` is the maximum concentration the
agent's real vaporizer can deliver (sevoflurane 8%, isoflurane 5%,
desflurane 18%). It is the upper bound of the delivered-concentration
control, and it is enforced in the core: `BreathingCircuit` carries the
limit for the agent in use (set by `AgentUptakeSystem.for_agent()`) and
**must reject** any delivered concentration above it, at construction and
at every later change, rather than clamping to it. A clamp would run,
display, and chart a dial position the caller never requested, which is
indistinguishable on screen from one they did. Zero is always accepted: it
is the vaporizer turned off, which is how washout begins. Its purpose is to
keep the simulator from offering a dial position that does not exist on the
corresponding real device. It is a device limit, not a physiologic or
safety limit: it says nothing about whether a given concentration is
appropriate for a patient.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: data/agents/isoflurane.json max_delivered_concentration_percent = 5 -->
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

**The three maxima come from two different classes of vaporizer, and that
distinction matters nowhere in this model except away from sea level.**
Sevoflurane's 8% and isoflurane's 5% are variable-bypass dials; desflurane's
18% is the upper end of the Tec 6's range, and a Tec 6 is a heated gas–vapour
blender rather than a variable bypass. This is the one place in the document
where both classes are present, implicitly, in the same list. At the 760 mmHg
fixed under "Assumptions" a dial position on either class means the same
partial pressure, so nothing in the core has to know which device a given
limit came from; the two classes come apart only under reduced ambient
pressure, which is not modelled — see "Known limitations".

`mac_percent` is 1 MAC for a 40-year-old adult. It is used for two things,
both of them presentation: choosing the starting position of the
delivered-concentration control when a run begins, so that a new run starts
from a recognizable clinical anchor rather than an arbitrary number; and
serving as the divisor of the second display unit ("MAC multiples as a
display unit"). `AgentUptakeSystem.for_agent()` applies the first, so the
starting dial position is agent-specific in the core rather than in the
controller, and every agent file **must** declare a `mac_percent` its own
vaporizer can deliver — a cross-field check in `core/parameters.py` enforces
that, and runs after every field is populated so it cannot be defeated by
field declaration order. It is still not carried into the simulation:
no governing equation reads it, and `core/` computes no quantity derived
from it. Specifically, the model does **not**:

- compute MAC-hours or an age-adjusted MAC, or sum MAC fractions across
  agents;
- model an effect-site compartment or any depth-of-anesthesia endpoint; or
- imply that an alveolar concentration equal to `mac_percent` corresponds to
  any particular clinical state in a particular patient.

MAC is a population ED50 for immobility to a standardized stimulus, varying
with age and modified by other agents, opioids, temperature, and patient
factors none of which are modeled here. Presenting a single-agent alveolar
concentration as though it indexed anesthetic depth would be exactly the
kind of plausible-but-wrong clinical inference `CLAUDE.md` forbids, which is
why the displayed unit is a *ratio to* 1 MAC, written `×MAC`, and never a
depth. The reasoning for that distinction is in the display section named
above; what follows here is what the three stored numbers are worth.

**The provenance tier is load-bearing now, and it was not before.** While
`mac_percent` only chose where the dial opened, an error in it moved the
starting point of a run and nothing else. As the divisor of every displayed
compartment value and of the chart's second axis it is a clinically
meaningful transformation under `CLAUDE.md`'s safety-critical standard. The
stored values are **tier 3**: the flat adult MACs De Wolf et al. state they
used in their Gas Man simulations, adopted because they are the same
parameter set as every partition coefficient in this model and because the
reference adult has no age parameter to apply an age-related MAC to.

**The size of the gap, and which comparison it distorts.** Mapleson's
meta-analysis of the published MAC literature gives, for age 40, isoflurane
1.17%, sevoflurane 1.80% and desflurane 6.6%, with 95% confidence limits of
about ±7% (±10% for desflurane). Against those:

| Agent | Stored `mac_percent` | Mapleson age-40 | Displayed MAC reads |
| --- | --- | --- | --- |
| Sevoflurane | 2.0% | 1.80% | 10% low |
| Isoflurane | 1.2% | 1.17% | 2.5% low |
| Desflurane | 6.0% | 6.6% | 10% high |
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- provenance: data/agents/desflurane.json mac_percent = 6 -->

The errors run in opposite directions for sevoflurane and desflurane, so a
sevoflurane-versus-desflurane comparison in MAC multiples — the exact
comparison the second display unit exists to make honest — differs by about
22% between the two MAC sources. That is larger than either source's own
confidence limits and is a real limitation of the display, recorded in
"Known limitations" rather than left implicit.

**Why the Mapleson values are nonetheless not adopted here** (project owner,
2026-09-04, on the recommendation below). Three reasons,
and the first is this document's own rule. Mapleson 1996 is a meta-analysis:
it regresses a literature survey and measures nothing, which is **tier 2**
under "Source hierarchy". That does not forbid adopting it outright — a lower
tier may be adopted on a recorded decision — but it does mean adopting it
would take one, and the two reasons below are why this decision went the other
way. Second, every other parameter in this model is the Gas Man set, so a
Mapleson divisor over a Gas Man trajectory would make each displayed multiple
a ratio between two different parameter lineages; dividing this model's
output by this model's own MAC is at least internally consistent. Third,
±7-10% confidence limits mean no MAC source makes a cross-agent comparison
exact, so the honest response is to display the divisor and disclose the
limitation — which the interface and this section do — rather than to
substitute a different non-primary number and present it as settled. The
route to primary values for all three agents is `ROADMAP.md`'s
planned-milestone item 31.

**This is a decision taken, not a default left standing.** It was put to the
project owner when the second display unit was built, with the gap measured
and the alternative costed, and the stored values were kept on 2026-09-04.
Revisiting it is therefore a change to a recorded decision rather than a
correction of an oversight: the case above is what a later revision has to
answer, and item 31 is where the answer belongs, because moving `mac_percent`
alone would leave one parameter on a different lineage from the twelve
coefficients beside it.

Each agent's `sources` array carries the citation, the tier, the Mapleson
value it was not taken from, and the difference.

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
  a step differing from the one a run has already taken is refused, not
  counted;
- changing a setting does not reset stored state;
- Pause prevents simulation-time advancement;
- Reset clears dynamic state while preserving settings;
- a delivered concentration above the agent's vaporizer maximum is rejected, not clamped;
- a simulation step above `MAXIMUM_SIMULATION_STEP_S` is refused, not simulated;
- a simulation step that cannot be completed leaves every dynamic value, and
  simulation time, exactly as the last completed step left them;
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
fraction — $`F_I=F_A=F_a=F_v`$ and every tissue group at the same value —
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

Individual tissue concentrations may temporarily rise through redistribution, so the test must not incorrectly require every compartment to decrease monotonically.

### Step-refinement test

Reference simulations at supported smaller steps must produce the same
solution, to within floating-point rounding.

At minimum, compare:

```text
dt = 0.1 s
dt = 0.05 s
dt = 0.025 s
```

All three are inside the supported domain: the first is
`MAXIMUM_SIMULATION_STEP_S` itself, and refinement only moves inward from
there.

The gate compares *successive* halvings — 0.1 against 0.05, then 0.05
against 0.025 — rather than each step against the finest, and additionally
requires every gap to sit below a stated rounding-level bound. Two step sizes
can only show that a pair of runs agree; three show that the step does not
enter the answer.

**What the third point asserts changed with the exact step, and it is now a
stronger claim.** Under the operator split it required each gap to be *smaller*
than the last — a first-order error halving with the step, converging to a
limit that none of the three steps reached. Every supported step now lands on
that limit, so the gaps sit at the floating-point floor and no longer shrink;
requiring them to would fail correct arithmetic. What is required instead is
that they stay at that floor. Measured 2026-09-06, the worst successive-halving
gap across the four reported values is 8.1e-16, against the 1.4e-11 a
first-order method would show at these steps.

The release comparison tolerance is 5e-3 relative or 1e-8 absolute, either
satisfying, on the alveolar, vessel-rich and mixed-venous fractions after
60 s of the default sevoflurane wash-in. Comparing 0.1 s straight to 0.025 s
would exceed it in mixed venous alone — that compartment has barely begun to
fill at 60 s, so a difference of 1.4e-6 in fraction, a seventh of a count of
the last displayed digit, is 0.55% of it.

This gate is self-consistency across the supported steps, not correctness: a
wrong transfer rate is exactly as step-independent as a right one and passes
here. "Independent-solution test" below is what asks whether the solution is
the right one at all.

### Independent-solution test

The coupled six-state solution must be checked against an integration of the
governing equations that shares no solver with the implementation
(`tests/reference/test_coupled_dynamics.py`). The oracle may load the
parameter files and nothing else from the package under test; a comparison
against code derived from the implementation is a tautology, not a
verification, so the test enforces that restriction on its own imports.

The comparison covers every shipped agent, and its tolerance is **absolute**:

$$
\max_k \left| F_k^{\mathrm{shipped}} - F_k^{\mathrm{reference}} \right|
\leq
4\times10^{-13}
$$

over every state $`k`$, every horizon and every trajectory below.

**Why absolute, where the split's bound was a coefficient.** The split's error
was $`C\,\Delta t`$, so bounding $`C`$ bounded the error at every step size.
The exact step has no such coefficient: it is the solution of these equations
over the interval, and what the comparison measures is the accumulated
floating-point difference between two independently written solutions that
agree exactly in exact arithmetic. That residual grows with the *number* of
steps rather than with their size, so it is slightly worse at a finer step —
the opposite of the split — and a per-step coefficient would state the reverse
of what is true.

**Derived from the exact step's own error, not inherited.** Re-measured
2026-09-07 across all three agents, the horizons above and every trajectory
below, taking the maximum over the whole trajectory rather than at endpoints.
At the shipped 0.1 s step the five trajectories give 1.58e-14, 1.54e-14,
1.39e-14, 1.34e-14 and 8.80e-15 — within a factor of 1.8 of one another,
because what is being measured is accumulated rounding and every trajectory
takes the same number of steps. Driving the same trajectories at 0.05 s and
0.025 s, which the gate also does, gives the worst figure anywhere: **5.89e-14**,
desflurane on a *ventilator start* at the finest step. Against the operator
split, whose worst over the same domain was 2.29e-4 at this step, the exact
step is nine orders of magnitude closer to the independent solution.

**Until 2026-09-07 this bound was 5e-12 and measured the wrong thing.** The
oracle ran at half the shipped step, which is converged at held settings but
not through a transient, so 86% to 99.8% of what the gate reported on the
trajectories that set it was the oracle's own RK4 truncation rather than the
shipped step's error. The bound therefore sat about 320 times above the
residual it was watching, and a regression making the exact step a hundred
times worse would have passed it. The oracle now runs at an eighth of the step
under test, which is where refining it stops changing the answer.

**The residual is rounding, not truncation, and that is checked rather than
asserted — by the absence of a direction.** Refining the oracle a further
eightfold, to 0.0015625 s, moves the five figures above by at most 11% and
moves them both ways. RK4 is fourth order, so a residual still carrying the
oracle's truncation would fall by about four thousand and never rise; one that
reshuffles by a few percent in either direction is two independently
accumulated rounding paths being differenced.

The margin is wider than the 1.22 the splitting bound carried, deliberately: a
systematic coefficient reproduces between machines and accumulated rounding
does not, since a different `exp` implementation or a contracted multiply-add
moves the last bits of both solutions. The margin is sized on that, not on the
residual: solving the identical trajectories at 0.1, 0.05 and 0.025 s with no
oracle involved — the same exact propagator, differently subdivided, so every
difference is the shipped side's own accumulation — moves the answer by up to
1.07e-13, which is larger than the residual itself. The bound clears that
spread by 3.7 times and the worst residual by 6.8. It remains nearly nine
orders below the error of any method that is not exact, so the gate fails the
moment method error returns — which is the only thing it is there to catch.

**The domain the bound covers.** The domain is *trajectories*, not operating
points. A run of the application is a sequence of settings held until someone
moves a slider, and moving one is when the split is under the most strain:
the state is then far from the equilibrium of the settings now in force. A
gate that holds one operating point for every run measures the split only
where it never turns, which is the smaller half of what the interface
produces.

The gate therefore drives four kinds of run:

- the *reference point* — 5% delivered, 4 L/min fresh gas, and the reference
  adult's default alveolar ventilation and cardiac output — held, and
  compared at horizons of 60 s, 600 s and 3600 s. This is the point the
  pinned reference states below belong to.
- the *envelope corner* — each agent's own
  `max_delivered_concentration_percent` with fresh gas, alveolar ventilation
  and cardiac output all at their supported maxima (10, 12 and 10 L/min,
  which are also the sliders') — held for 600 s.
- a *ventilator start*: the same corner but with alveolar ventilation at zero
  for the first 300 s, so the circuit saturates at the dial setting against
  lungs that can take none of it, and then ventilation to its maximum. This
  is an ordinary manoeuvre, and it alone exceeds the previous bound.
- an *unperfused load, then dial off*: the corner with cardiac output at zero
  for 600 s, so circuit and alveoli saturate while every blood and tissue
  compartment stays empty, and then perfusion to its maximum with the
  vaporizer closed. This is the worst trajectory the four sliders can reach.

In every case the maximum is taken over the whole trajectory rather than at
an endpoint, because the worst disagreement is always inside a transient — at
held settings the wash-in one, at about 85 s; across a setting change the one
the change itself starts, about 13 s later.

Both the corner and the worst trajectory are maxima by measurement rather
than by assumption. Across held settings, sweeping each axis separately:
fresh gas flow and alveolar ventilation raise the coefficient monotonically
to their slider maxima; cardiac output has an interior *minimum* near 5 L/min
and rises toward both ends, the upper end being the larger; and the governing
equations are linear in the delivered fraction, so each agent's worst dial is
its vaporizer maximum. Across trajectories, sweeping the corners of both
phases and then each axis around the winner: the worst is always the first
transition after the loading phase saturates, and repeating the cycle three
or six times does not raise the peak at all, so the coefficient is bounded
rather than accumulating over a run; a third phase inserted between the two
never beat the pair; and every axis is monotone toward the corner used except
cardiac output during loading, which is worst at *zero* — the opposite end
from the held-settings corner. That monotonicity is measured, not proved, so
a change to the governing equations could move the maximum off these
trajectories, and the sweep is worth re-running rather than trusted.

**The split's own coefficients are kept as history**, because they describe
what this project shipped for eleven releases and because any later work on
step size starts from them rather than re-deriving them. The worst measured
over the whole reachable domain was
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
twice over, one dimension at a time: set at
$`5\times10^{-4}\ \mathrm{s^{-1}}`$ from the reference point alone it was
exceeded by a factor of about 2.4 at settings three sliders could reach, and
reset at $`1.5\times10^{-3}\ \mathrm{s^{-1}}`$ from the envelope but measured
only on runs holding one operating point, it was exceeded by a ventilator start
at that same corner — a manoeuvre a user performs. Neither gate ever failed,
because nothing it drove ever went where the error was. A release gate narrower
than the reachable input domain is a verification claim broader than its
evidence, whatever the method under it.

**One safety disclosure this section used to carry is now withdrawn.** The
split applied its transfers in order, so each compartment was driven across the
interval by an upstream value the same step had already moved, and the
resulting bias had opposite signs at the two ends of the transfer chain: the
circuit read below the independent solution and the tissues above it, so a
*difference* between two readouts carried the sum of two displacements and was
the least accurate thing the interface displayed — up to 1.8 times the error in
either reading it was taken from. That was true of the split and is not true of
the exact step, which drives no compartment from an already-moved value and
leaves no bias with a sign. A gradient between two compartments is now no less
accurate than either reading it is taken from. The withdrawn claim is recorded
here rather than deleted because it was published in "Displayed precision"
below as well, and a reader comparing versions needs to know which way it went.

The reference states are pinned in the test file: a change to the oracle or to
a parameter file must be re-derived and reviewed rather than silently adopted.
They are the oracle's own solution, not the shipped solver's, and re-pinning
them from the implementation would convert this gate into a self-comparison.
The supported ranges above are restated in the test file and checked against
`core/supported_ranges.py`, so widening the model's declared domain cannot
silently leave this gate measuring a subset of it.

### Published wash-in and elimination validation test

Every test above is **verification**: it asks whether the implementation
solves the intended equations correctly, and answers it by comparing the
implementation against an analytic solution, an independent integration of
these same equations, a conservation identity, or its own behavior at another
step size or setting. None of them asks whether the equations describe the
phenomenon. A model can be numerically flawless and physiologically wrong,
and a suite made only of the tests above would report the first as though it
had settled the second.

This test is the **validation** half, and it is the only required test whose
expected values come from outside this repository
(`tests/reference/test_published_wash_in_and_elimination.py`). The distinction
matters to a reader of the two sections: "Independent-solution test" above and
this one answer different questions, and conflating them over-reads both.

**This section covers two comparisons, in opposite directions.** They are
$`F_A/F_I`$ at 30 minutes of **wash-in**, which agrees with the published
measurements, and $`F_A/F_{A0}`$ at 5 minutes of **elimination**, which does
not. Both come from the same volunteers in the same sitting.

$`F_A/F_I`$ at 30 minutes of wash-in is the classic measured quantity in the
uptake literature, and Yasuda et al. published it for all three shipped
agents in two volunteer studies:

| Agent | $`F_A/F_I`$ at 30 min | Cohort | Published $`F_I`$ | Source |
| --- | --- | --- | --- | --- |
| Sevoflurane | 0.850 ± 0.018 | n=7 | 1.0% | Anesth Analg 1991;72:316-24 |
| Isoflurane | 0.733 ± 0.027 | n=7 | 0.6% | Anesth Analg 1991;72:316-24 |
| Desflurane | 0.90 ± 0.01 | n=8 | 2.0% | Anesthesiology 1991;74:489-98 |
| Isoflurane | 0.73 ± 0.03 | n=8 | 0.4% | Anesthesiology 1991;74:489-98 |

- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Liu J, Laster M, Taheri S,
  Peterson NA. *Comparison of kinetics of sevoflurane and isoflurane in
  humans.* Anesth Analg 1991;72(3):316-24. PMID 1994760,
  doi:10.1213/00000539-199103000-00007.
- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Johnson BH, Freire BA,
  Fassoulaki A. *Kinetics of desflurane, isoflurane, and halothane in humans.*
  Anesthesiology 1991;74(3):489-98. PMID 2001028,
  doi:10.1097/00000542-199103000-00017.

Both papers report a second measured quantity on the same subjects, in the
opposite direction: $`F_A/F_{A0}`$ after five minutes of elimination,
beginning where the 30-minute administration above ends. $`F_{A0}`$ is each
paper's own definition — the last alveolar fraction recorded during that
administration — so the two comparisons are one continuous protocol rather
than two.

| Agent | $`F_A/F_{A0}`$ at 5 min | Cohort | Source |
| --- | --- | --- | --- |
| Sevoflurane | 0.157 ± 0.020 | n=7 | Anesth Analg 1991;72:316-24 |
| Isoflurane | 0.223 ± 0.024 | n=7 | Anesth Analg 1991;72:316-24 |
| Desflurane | 0.14 ± 0.02 | n=8 | Anesthesiology 1991;74:489-98 |
| Isoflurane | 0.22 ± 0.02 | n=8 | Anesthesiology 1991;74:489-98 |

All eight figures in the two tables are mean ± SD, read from the two
abstracts and checked against PubMed on 2026-09-06.

Isoflurane is compared against both cohorts rather than one, in both
directions.

**For wash-in**, the model must land inside the published standard deviation
for every row, and must also reproduce the ordering by solubility the two
studies were run to test — $`F_A/F_I`$ higher for desflurane than sevoflurane
than isoflurane — because three tolerances that happen to overlap are not a
model. It does both. What is required of the elimination rows is different,
because the model does not land inside their spread; that is below.

**The tolerance is the published spread, and the operating point is not
fitted.** Alveolar ventilation and cardiac output are read from
`reference_adult.json` at run time rather than written into the test, and the
test fails if those defaults stop being 4.0 and 5.0 L/min. This is the
assertion the whole comparison rests on: the agreement is sensitive to both
flows — 1 L/min of alveolar ventilation either way puts all three agents
outside their published spread, and 1 L/min of cardiac output moves every
agent by more than one published standard deviation — so an operating point
chosen to make the comparison pass would make the result circular. It is
instead the shipped default, cited to the Gas Man workbook under "Parameter
provenance", and fixed in v0.1.0 before any comparison to Yasuda existed.

Fresh gas flow is the one setting the test chooses, at 10 L/min, so that
$`F_I`$ — the modeled *circuit* fraction, not the vaporizer dial — is settled
rather than still rising at 30 minutes, matching protocols that held an
inspired concentration at the airway. The test shows that choice is not
carrying the wash-in result: every agent stays inside its published spread at
every fresh gas flow from 1 to 10 L/min. It carries the elimination result
almost entirely, which is the subject of the next paragraphs and the reason
the two comparisons are not equally strong. One delivered fraction serves
four different published $`F_I`$ values because the governing equations are
linear in it, which the test asserts across the published range — for both
ratios separately — rather than assumes.

**The elimination comparison does not agree, and the model states the
disagreement rather than a tolerance around it.** At the shipped defaults and
the same 10 L/min the wash-in comparison uses, the model holds more alveolar
agent at five minutes than every cohort did (measured 2026-09-06 and
re-measured 2026-09-07, the rows having moved 0.11 to 0.13 SD further above
their means when `PL-8ZJQ` raised `venous_pool_volume_l` to 1.222 L):

| Agent | Cohort | Model | Published | Distance |
| --- | --- | --- | --- | --- |
| Sevoflurane | n=7 | 0.2328 | 0.157 ± 0.020 | +3.79 SD |
| Isoflurane | n=7 | 0.3227 | 0.223 ± 0.024 | +4.15 SD |
| Desflurane | n=8 | 0.1626 | 0.14 ± 0.02 | +1.13 SD |
| Isoflurane | n=8 | 0.3227 | 0.22 ± 0.02 | +5.13 SD |

So the assertion on these values is a **regression** band — the published
standard deviation applied around the model's own measured ratio — which
claims nothing about agreement and exists so that a change moving washout by
more than one published SD fails and has to be explained. The claims the test
does make about elimination, and that hold, are the published ordering by
solubility (desflurane leaves fastest, then sevoflurane, then isoflurane),
independence from the delivered fraction, and the sign of the departure.

**Most of that departure is the breathing system, not the tissue return**,
and the difference is a property of the two ratios rather than of the model's
physiology. $`F_A/F_I`$ carries the inspired fraction in its denominator, so
whatever a breathing system does to $`F_I`$ divides out of it — which is why
the wash-in comparison is inside the published spread at every supported
flow. $`F_A/F_{A0}`$ has no such term: it is the alveolar fraction against its
own value five minutes earlier, so agent returning to the alveoli *from the
circuit* is counted exactly as though it had come back out of the patient.
This model always rebreathes — "Model boundary" gives it one circuit that is
a closed recirculating path except for fresh-gas inflow and exhaust, and
inspired gas *is* circuit gas — so through an elimination $`F_I`$ settles near
$`\dot V_A/(\dot V_A + \dot V_F)`$ of $`F_A`$, which is 0.29 at the highest
supported flow and measured at 0.30 to 0.32 at five minutes. The published
protocols did not, which is an inference and is recorded as one: neither
abstract states the breathing system, but both report mixed expired
concentrations and agent recovered against agent taken up, and neither
quantity can be had without collecting the whole expirate rather than
returning it to the subject. Their elimination therefore ran at an inspired
fraction at or near zero, which this model cannot be set to at any supported
flow; confirming it against the methods sections needs full texts that are
not in PubMed Central and are not held in `docs/references/`.

**The open-circuit diagnostic, and why its numbers are not this simulator's.**
`tests/reference/test_published_wash_in_and_elimination.py` can run the same five minutes with
the rebreathing taken away: after each step of the elimination it discards
whatever the patient exhaled into the circuit and records it as exhausted
agent, which is what collecting the whole expirate does. That holds $`F_I`$ at
zero to within one step of refilling — at most $`\dot V_A \Delta t / V_C`$ of
$`F_A`$, or 1.1 × 10⁻³ at the shipped ventilation, step and circuit volume,
against the 0.30 to 0.32 the same run settles at with rebreathing. **It is a
test-only driver, and no fresh gas flow, dial position or patient setting of
the shipped simulator reaches the condition it creates.** `PL-W21J` weighed a
supported non-rebreathing mode against the driver and the project owner chose
the driver on 2026-09-06, because a mode changes the model boundary rather
than a fixture and adds one more thing the interface would have to make
visible. Nobody running the application sees the numbers below, and a
restatement of them that drops this sentence has said something about the
shipped model that is not true of it (measured 2026-09-07):

| Agent | Cohort | Shipped | Open circuit | Published |
| --- | --- | --- | --- | --- |
| Sevoflurane | n=7 | +3.79 SD | 0.1541, −0.15 SD | 0.157 ± 0.020 |
| Isoflurane | n=7 | +4.15 SD | 0.2388, +0.66 SD | 0.223 ± 0.024 |
| Desflurane | n=8 | +1.13 SD | 0.0935, −2.33 SD | 0.14 ± 0.02 |
| Isoflurane | n=8 | +5.13 SD | 0.2388, +0.94 SD | 0.22 ± 0.02 |

**Three of the four cohorts land inside the published spread once the
apparatus is gone, and desflurane misses on the other side.** For sevoflurane
and for isoflurane in both cohorts the rebreathing circuit accounts for the
whole of a gap 3.8 to 5.1 published standard deviations wide — so this model's
vessel-rich return does reproduce a human elimination once the breathing
systems are matched, which no comparison in this repository could say before.
For desflurane it over-accounts: the model crosses its published mean and
settles 2.33 SD below it, washing out *faster* than the volunteers did rather
than more slowly. That residual is a disagreement about tissue return with the
circuit no longer available to explain it; what it is not, and what is left of
it, is "Desflurane's residual" below.
The movement itself — 3.5 to 4.2 SD per cohort — is asserted rather than
recorded, so the attribution in the paragraph above cannot go stale in
silence, as are the driver's residual $`F_I`$, the model's own conservation
identity across the discards, and the flow independence the diagnostic buys:
across the whole supported flow range the open-circuit elimination moves by
4 × 10⁻⁶ published SD, against the 11.5 to 21.6 SD the shipped one moves
between 1 and 10 L/min.

Neither condition validates the elimination a user watches, and no test claims
that it does. The elimination this simulator runs is the rebreathing one, and
what is asserted about it is the regression band above.

#### Desflurane's residual, and why the parameter file was not changed

The obvious reading of that residual is that desflurane's vessel-rich
coefficient is too low. The sensitivity measured under "Parameter provenance"
makes the five-minute ratio a vessel-rich tissue:gas measurement and barely a
blood:gas one, and a tissue group with too little capacity is a tissue group
that empties too fast. The reading is arithmetically right and physically
wrong, and the difference is what this section records.

**Raising the coefficient does close the gap, and it costs almost nothing in
the wash-in row.** Desflurane's stored vessel-rich tissue:gas coefficient is
0.54 against a blood:gas of 0.42, an implied tissue:blood of 1.286. Solving
instead for the coefficient that reproduces each cohort's published
five-minute ratio, at the shipped operating point and with the apparatus
removed (measured 2026-09-08):

<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54, blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 1.286 from data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54, blood_gas_partition_coefficient = 0.42 -->

| Agent | Tissue:blood demanded | Measured human brain:blood | Distance |
| --- | --- | --- | --- |
| Sevoflurane | 1.74 | 1.70 ± 0.09 | +0.4 SD |
| Isoflurane | 1.45 | 1.57 ± 0.10 | −1.2 SD |
| Desflurane | 2.24 | 1.29 ± 0.05 | +19 SD |

At 2.24 desflurane's elimination lands on the published 0.140 and its wash-in
row stays inside its published spread at +0.55 SD. That is not luck: the
vessel-rich group is fully equilibrated after a 30-minute administration — its
time constant is 2.0 to 2.7 minutes across the three agents — so its capacity
is nearly invisible in $`F_A/F_I`$ and shows up almost entirely in the
elimination. The two published rows are therefore not in conflict with each
other, and a single coefficient satisfies both.

**What rules the change out is the tissue measurement rather than this
model.** The measured column above is Yasuda's human tissue study, the same
group's, three years before the kinetic pair:

- Yasuda N, Targ AG, Eger EI 2nd. *Solubility of I-653, sevoflurane,
  isoflurane, and halothane in human tissues.* Anesth Analg 1989;69(3):370-3.
  PMID 2774233. Brain:blood, mean ± SD: I-653 (desflurane) 1.29 ± 0.05,
  isoflurane 1.57 ± 0.10, sevoflurane 1.70 ± 0.09, halothane 1.94 ± 0.17.
  Read from the abstract and checked against PubMed on 2026-09-08.

Two of the three demanded values land on that measurement. Desflurane's is
nineteen standard deviations above its own, and above what either other agent
demands: adopting it would make desflurane the *most* tissue-soluble of the
three, inverting the ordering the source paper was written to report. The
stored Gas Man coefficients are that paper's brain:blood values to within 3%
— 1.692 against 1.70, 1.615 against 1.57, 1.286 against 1.29 — so this is not
a case of a reference implementation having wandered from the primary
literature, and there is no better value to move to.
`test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
asserts the contrapositive: given a vessel-rich coefficient the published
human tissue data will bear, desflurane's elimination still misses on the same
side.

| Coefficient given | $`F_A/F_{A0}`$ at 5 min | Against 0.14 ± 0.02 |
| --- | --- | --- |
| 1.286, shipped | 0.0935 | −2.33 SD |
| 1.39, its own measured mean + 2 SD | 0.0998 | −2.01 SD |
| 1.70, sevoflurane's, the highest of the three | 0.1167 | −1.17 SD |

**Nine other candidates were tested or struck, and each fails the same way**: it moves
sevoflurane and isoflurane as much as desflurane or more, and the published
rows have no room for that, or it moves desflurane the wrong way. Rows one to
six were measured 2026-09-08, rows four to six on an independent forward-Euler
integration of these equations, which reproduces the shipped driver to within
0.8% and whose own zero-shunt baseline for desflurane is −2.29 SD rather than
−2.33. The seventh was measured 2026-09-13 on the shipped driver, after the
methods sections supplied the apparatus's real volume (`PL-RFLN`); the
paragraphs below it are why it is a row of its own rather than a correction to
the sixth. The eighth and ninth were not measured here at all — each is struck
by a held primary measurement that answers it outright, and each has a block
below giving what it proposed and what killed it.

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

**The sixth row measured circuit-style rebreathing at an assumed ratio, and
the apparatus turns out not to be that shape at all.** Yasuda 1991
*Anesthesiology* § "Materials and Methods" puts about 50 ml of corrugated
Teflon between the tracheal sampling port and the nonrebreathing valve, stated
there to protect the end-tidal sample from contamination with inspired gas.
That volume holds alveolar gas at end-expiration and fresh gas at
end-inspiration, which makes it a **series dead space** rather than a mixing
volume returning a fraction of every breath — and in a model with one
perfectly mixed alveolar compartment the two are not the same mechanism.

Take one breath of the elimination, with the fresh gas agent-free, and let
$`V_D`$ be the total series dead space, anatomic plus apparatus. Inspiration
pushes that $`V_D`$ of alveolar gas back into the alveoli and follows it with
$`V_T - V_D`$ of agent-free gas, so the alveoli receive $`V_T`$ of gas
carrying $`V_D F_A`$ of agent and expel $`V_T`$ carrying $`V_T F_A`$. The net
is $`-(V_T - V_D) F_A`$, which is exactly this model's
$`\dot V_A (F_I - F_A)`$ at $`F_I = 0`$ provided $`\dot V_A`$ is the true
alveolar ventilation $`(V_T - V_D) f`$. **So the published apparatus's dead
space is an alveolar-ventilation decrement of $`V_D f`$ and nothing else.**
Applying it as a non-zero $`F_I`$, which is what the sixth row tested, would
describe this model's circuit rather than Yasuda's apparatus.

**Run correctly, it fails the way the second row fails, which is not a
coincidence — it *is* the second row, at a sourced magnitude.** The model
carries no respiratory rate, so the decrement is run across the conventional
range for a paralysed, normocapnic adult. Measured 2026-09-13, against the
−2.33 SD desflurane sits at with no dead space at all:

| $`f`$ (/min) | $`\dot V_A`$ (L/min) | Desflurane | Isoflurane n=8 | Worst wash-in row |
| --- | --- | --- | --- | --- |
| 6 | 3.70 | −1.89 SD | +1.59 SD | −0.42 SD |
| 8 | 3.60 | −1.73 SD | +1.82 SD | −0.63 SD |
| 10 | 3.50 | −1.56 SD | +2.05 SD | −0.85 SD |
| 12 | 3.40 | −1.38 SD | +2.30 SD | −1.08 SD |

It moves desflurane the right way and carries between 0.44 and 0.95 SD of the
2.33 — a quarter to two fifths, never the whole — and it buys that by pushing
the isoflurane cohort that was inside its spread at +0.94 SD out to between
+1.59 and +2.30. The wash-in comparison sets its own ceiling: at 11 breaths
per minute sevoflurane's wash-in row reaches −0.96 SD and one breath more
takes it outside, so the largest decrement the comparison admits at all leaves
desflurane 1.48 SD short with both isoflurane cohorts outside their spreads.
The mechanism is **common-mode**, and desflurane's residual is differential.
`test_no_apparatus_dead_space_reaches_desflurane_s_published_elimination` and
`test_the_apparatus_dead_space_moves_every_cohort_together` assert both halves,
so this cannot go stale in silence.

**Whether any decrement is owed at all is undetermined, and that is the live
question rather than this one.** Yasuda derived the alveolar fraction of
ventilation from $`F_M = f_A F_A + f_D F_I`$, and the 1-l mixing chamber
supplying $`F_M`$ sits beyond the nonrebreathing valve — so the 50 ml that is
re-inspired never reaches it, and their derived $`f_A`$ is
$`(V_T - V_{D,\text{anat}} - V_{D,\text{app}})/V_T`$, already netting the
apparatus out. A comparison run at *their* alveolar ventilation must therefore
not subtract it again. This model runs at 4.0 L/min, which
`data/patients/reference_adult.json` records as a program default with no
primary source behind it, and which is neither quantity.

**Both papers have since been read at full text, and the study publishes no
ventilation at all** (`PL-ZDWL`, supplied by the project owner and read
2026-09-13). Ventilation was titrated per subject to normocapnia — end-tidal
carbon dioxide of 5.5–6.5% — rather than set to a figure, and while minute
ventilation was measured and used in the mass balance, **no $`\dot V_E`$ and no
$`f_A`$ is reported in either paper**, and neither carries a ventilation table.
What the *Anesthesiology* paper does settle, at its total-body-clearance
method, is the definition the derivation above needs: doses delivered to the
alveoli are computed as $`F_I \dot V_A \times 30`$ min "where
$`\dot V_A = f_A \dot V_E`$", so $`f_A`$ is the alveolar fraction of *total*
minute ventilation.

**The nearest published analogue points the seventh row the wrong way.** The
paper reports pulmonary elimination clearances $`V_1 k_{10}`$ for the eight
volunteers desflurane's residual belongs to: desflurane 4.11 ± 0.45, isoflurane
3.94 ± 0.34 and halothane 3.94 ± 0.33 L/min, against 3.58 and 3.62 L/min in the
seven-volunteer *Anesth Analg* cohort. This model runs at 4.0 L/min, so for the
cohort in question it is already at the study's own effective clearance — and a
dead-space decrement *lowers* alveolar ventilation, moving it **away** from
4.11 rather than toward it. That is independent of the common-mode argument and
stronger, because it is specific to the one cohort the mechanism would have to
help.

**These clearances are a consistency check on the operating point and must not
be adopted as one.** They are fitted to the very elimination curves this
comparison is scored against, so running the model at them would be circular.
Their precision is also readable from the paper itself: the same eight subjects
breathed all three agents simultaneously from one cylinder, so their ventilation
was physically identical across those three rows, and the fitted values still
spread about 4%.

The fourth row's volumes are round physiologic figures — 1 kg of lung tissue
at a tissue:blood ratio of 1.2, and 1.8 L of pulmonary and arterial blood —
used to size the term and not proposed as parameters; none of them is a stored
value and none should be read as one. What it establishes does not depend on
their precision: any capacity that scales with blood solubility is worth the
same *fraction* of every agent's fast pool, so adding it moves all three rows
together and cannot produce a residual in one of them.

**So the cause is not identified. This is a recorded disagreement, and the
sign and the size are what is recorded.** What survives the eliminations above
is a mechanism acting on the least soluble agent alone, in the direction of
holding its alveolar fraction up. **One candidate remains, and this project
cannot test it:**

1. *The published value.* Desflurane's recovery — agent recovered over agent
   taken up — was 105 ± 25% in those eight volunteers, against 102 ± 13% for
   isoflurane measured in the same sitting: the wider spread of the two, and
   centred above complete recovery.

**End-tidal sampling was the second candidate, and it is struck** (project
owner, 2026-09-13). It is recorded here rather than deleted, because it was the
leading explanation for a week and a reader meeting the eighth table row is
owed why.

*What it proposed.* The published $`F_A`$ is end-tidal gas from an
anaesthetized volunteer; this model's is one perfectly mixed compartment. In a
dispersed lung a unit with ventilation-perfusion ratio $`r`$ sits at
$`P_A/P_{\bar v} = \lambda_{b:g}/(\lambda_{b:g} + r)`$ through an elimination,
so the last units to empty carry the highest partial pressure during washout
and the lowest during wash-in, and a ratio of the two would be biased upward at
both ends by an amount growing as solubility falls. On a log-normal perfusion
distribution at log SD 1.0 with a 5% shunt the arterial retention this model
fixes at $`\lambda_{b:g}/(\lambda_{b:g} + \dot V_A/Q)`$ is understated by 44%
for desflurane, 30% for sevoflurane and 15% for isoflurane — the rank order the
residuals have, which is what made it attractive.

*What the methods sections settled, and it was in its favour.* The fifth table
row rules out the **flow-weighted** alveolar reading, so the hypothesis rested
entirely on the published $`F_A`$ being an end-tidal sample instead. Yasuda
1991 *Anesthesiology* § "Materials and Methods" sites that port **at the
tracheal tube**, with the 50 ml of Teflon the seventh row analyses interposed
to protect it from inspired gas, and samples mixed expired gas **separately**
from the 1-l mixing chamber, reporting it as $`F_M`$. So the reading the fifth
row excludes is $`F_M`$, not $`F_A`$, and the obstacle was removed.

*What struck it.* The one primary human measurement of that gradient
disagrees on both counts. Yasuda's own discussion flags the assumption "that
the $`F_A`$ accurately indicates the anesthetic partial pressures in arterial
blood" and cites Carpenter RL, Eger EI II, *Alveolar-to-arterial-to-venous
anesthetic partial pressure differences in humans*, Anesthesiology
1989;70(4):630–5, PMID 2930000 — eight surgical patients with simultaneous
arterial, end-tidal and inspired sampling (supplied by the project owner and
read 2026-09-13).

- **Solubility runs the other way.** Measured $`P_A/P_a`$ is 1.23 ± 0.13 for
  halothane against 1.11 ± 0.09 for isoflurane, P = .009, and its authors state
  the rule: the difference "should be greater with anesthetics having higher
  blood solubility". Desflurane is the least soluble agent in the comparison,
  so it should show the *smallest* gradient where the hypothesis needs the
  largest.
- **The sign reverses through an elimination.** The mechanism is contamination
  of the end-tidal sample by physiologic dead space gas — "unchanged inspired
  gas" — at $`(P_A - P_a) = 0.22 (P_I - P_a) + 0.02`$, a slope its authors read
  as the sample being about 20% dead space gas. The bias therefore follows
  $`F_I`$: upward during administration, where $`F_{A0}`$ is measured, and
  **downward through an elimination run at $`F_I = 0`$**. Both push the
  published $`F_A/F_{A0}`$ *down*, so the measured 0.140 understates the true
  arterial ratio and this model's 0.0935 sits further from it, not nearer.

*Two things that would reopen it, neither sufficient to hold it open.*
Carpenter's regression was fitted over positive $`P_I - P_a`$ only and never at
$`F_I = 0`$, so applying it to an elimination extrapolates the mechanism rather
than the fitted line; and his patients were 52 ± 16 years old against Yasuda's
25 ± 5, with physiologic dead space being age-dependent. Both would have to
resolve in the hypothesis's favour *and* reverse the measured solubility
ordering, which no argument here proposes. Yasuda's 50 ml guard does not
answer it either: that protects against contamination from the **apparatus**,
where Carpenter's 20% is physiologic dead space inside the patient.

*One consequence worth stating plainly.* If the sampling bias is real and
signed as measured, the published 0.140 is **low** — so every reading of this
section that treats the model as washing desflurane out too fast is
conservative rather than optimistic.

**Circuit-wall absorption was never on this list, and the paper behind the
circuit volume decides it** (`PL-XWCY`). Targ, Yasuda and Eger measured washin
at 0.5–2 L/min and washout at 1–5 L/min in a real conventional circle system
against the ideal exponential (*Anesth Analg* 1989 Aug;69(2):218–25, PMID
2764290; read at full text 2026-09-13, and the same study behind the circuit
volume's provenance and the inert-circuit entry under "Known limitations").
Desflurane's curves lay close to the ideal line at every flow — deviating most
at the lowest flows and near complete washin, none of them this model's
operating point — and the authors conclude that absorption of it "by circuit
components or soda lime should not hinder induction of or recovery from
anesthesia". For **desflurane**, then, the model's inert circuit is the
assumption this measurement most nearly supports, and the candidate is struck
on evidence rather than on argument.

**The direction rules it out independently, and that half needed no
measurement.** A wall that dissolves agent through a 30-minute administration
gives it back through the washout, holding the circuit's — and therefore the
inspired — fraction up and *slowing* the alveolar fall. Desflurane's residual
is this model washing out too **fast**. A mechanism that can only slow a
washout cannot produce it, so no magnitude of wall absorption would have
helped whatever the measurement had said.

**The same study finds that a real circuit measurably retards sevoflurane and
isoflurane. That is a limitation of this simulator, and it is not a candidate
here — three separate reasons, any one sufficient.** The finding is real: the
component partition coefficients rank halothane > isoflurane > sevoflurane >
desflurane at every equilibration time from 7.5 min to 9 weeks, and the washin
and washout curves follow that order. But it does not bear on the residual.

- **It is already recorded, in the right place.** "Known limitations" carries
  the coefficient table, the ranking, and the statement that the inert circuit
  is most nearly true for desflurane and least for halothane, together with
  the decision not to add a wall term (`PL-LS3H`). What a reader of this
  section would take from repeating it here is that the residual is partly
  explained, which is the opposite of true.
- **The departure it would be offered against is in the elimination rows, not
  the wash-in rows.** Sevoflurane's +3.79 SD and isoflurane's +4.15 SD are
  five-minute $`F_A/F_{A0}`$ figures. The wash-in comparison has no departure
  for anything to explain: every agent stays inside its published spread at
  every fresh gas flow from 1 to 10 L/min.
- **On the elimination rows the mechanism moves the wrong way, and it is
  absent from the published measurement besides.** Most of that departure is
  already attributed to the breathing system: removing the rebreathing takes
  sevoflurane to −0.15 SD and isoflurane to +0.66 SD. Wall absorption is a
  *further* agent store returning agent to the circuit through the washout, so
  adding it would hold $`F_I`$ up longer and push both rows further above
  their means, not toward them — the same directional argument that strikes it
  for desflurane, pointed at the two agents it is strongest for. And the
  published cohorts breathed a non-rebreathing apparatus with the potent
  agents' inspired fraction zero by construction, so no circle-system wall
  effect is present in the published number at all.

The general form of that last point is worth keeping: **a mechanism belonging
to this model's circle system cannot explain a disagreement with a measurement
made without one.** It can only be a statement about what the simulator shows
a learner, which is what "Known limitations" is for.

Whatever the explanation is, it has to fit the whole published set and not
desflurane alone. The same eight volunteers gave halothane 0.25 ± 0.02, so
across a solubility range of roughly six-fold — halothane's blood:gas is
conventionally about 2.4, a textbook figure and not a parameter this project
stores — the published five-minute ratios span only 0.14 to 0.25, which is a
narrower spread than a perfusion-limited model produces.

**What is still missing, now that the methods sections have been read.** The
three things this section used to name as what would settle it — the breathing
system, how end-tidal gas was sampled, and the alveolar ventilation measured
through the elimination — are two answered and one outstanding. The breathing
system and the end-tidal sampling are recorded above, and they closed the
apparatus question: the published circuit is non-rebreathing with the potent
agents' inspired fraction zero by construction, and its 50 ml of series dead
space cannot carry the residual. The third has been read out and is answered
in the negative: `PL-ZDWL` read both papers at full text on 2026-09-13 and
**neither publishes a ventilation at all**, as the paragraphs above record —
it was titrated per subject to normocapnia rather than set to a figure, and no
$`\dot V_E`$ and no $`f_A`$ is reported. So there is no published value to run
the comparison at, and that avenue is closed rather than outstanding.

So what is left is one candidate, and this project cannot test it: the
published value itself, which no measurement available here will settle. The
end-tidal-weighted bias that stood beside it was struck on the same day
(`PL-03ZG`, dropped for that reason), and circuit-wall absorption was struck
with it above. **Neither the remaining candidate nor any struck one is a claim
this specification makes** — the residual's cause is not identified, and what
is recorded here is its sign, its size, and the nine candidates in the table
above with what ruled each of them out.

**Which question a band of one standard deviation answers**, since this
section now makes the claim in two places. A deterministic model compared
against a cohort *mean* would conventionally be judged against the standard
error of that mean, $`\text{SD}/\sqrt{n}`$, a band 2.6 to 2.8 times narrower
for these cohorts. The claim made here is the weaker one, deliberately: that
the model is a **plausible individual** drawn from the published cohort, not
that it reproduces the cohort's mean. The distinction is not academic —
desflurane's wash-in sits at +0.79 SD, which is +2.2 SEM, so the same run
that passes the claim this document makes would fail the claim it does not
make. A reader restating a passing wash-in as "reproduces the published mean"
has said something no test here has tested.

**Four caveats bound how strongly a pass may be stated.** The first two apply
to both directions; the last two are the elimination comparison's own. All
belong beside any statement of this result, wherever it is restated - the root
README used to carry one and no longer exists (`PL-WB5K`), so the obligation
transfers to whatever `PL-N092` writes in its place.

1. *The published subjects were breathing nitrous oxide.* Both protocols ran
   65–70% N₂O concurrently, so the measured curves carry a second-gas effect
   this model cannot reproduce — "Known limitations" excludes nitrous oxide,
   simultaneous gases, and concentration and second-gas effects, and
   "Assumptions" states that carrier gases are assumed not to affect
   kinetics. The comparison is therefore not perfectly matched, in a
   direction that is not obviously conservative.
2. *These are Gas Man parameters, derived to reproduce Eger's data.* The
   partition coefficients under test descend from the same lineage as the
   measurements being tested against (see "Parameter provenance"). Passing
   shows that this implementation reproduces its parameter set's intent, not
   that the parameter set is independently right. It is weaker than
   "validated against a human measurement" and must not be described as more.
3. *The breathing systems differ, and by more than the measurement's own
   spread.* The paragraphs above measure it, at 3.5 to 4.2 published standard
   deviations per cohort. Any statement that this model eliminates more slowly
   than these volunteers did has to carry it, because most of that difference
   is a rebreathing circuit rather than a patient.
4. *This model has no metabolism, which is why five minutes is the limit.*
   Over five minutes of elimination metabolism is negligible for all three
   shipped agents, and the papers bound it themselves: recovery — agent
   recovered during elimination over agent taken up — was 101 ± 7% for
   sevoflurane and 101 ± 6% for isoflurane in the first study, and 105 ± 25%
   for desflurane and 102 ± 13% for isoflurane in the second, against 64 ± 9%
   for halothane, which is the same method detecting a metabolized agent.
   Both papers also report multi-day elimination curves, and those must not
   be added to this comparison: over days the missing metabolism is no longer
   negligible, and neither is the fat group's flow, which "Known limitations"
   records as about twice the reachable resting measurement and therefore
   acting directly on the slow tail of washout.

**How sharp a gate this is, measured rather than assumed.** The discriminating
power was re-measured on 2026-09-06 with the elimination point included, by
perturbing each agent's blood:gas partition coefficient until some assertion
in the module failed. The perturbation rebuilds the system from a modified
parameter set so that every compartment sees the same coefficient, with
tissue:gas coefficients held shipped — so tissue:blood moves inversely,
exactly as it would if the blood:gas measurement alone were wrong:

| Agent | $`\lambda_{b:g}`$ | Reference point alone | With the flow sweep | With elimination |
| --- | --- | --- | --- | --- |
| Sevoflurane | 0.65 | −14% / +21% | −14% / +6% | −14% / +6% |
| Isoflurane | 1.3 | −11% / +24% | −11% / +12% | −11% / +12% |
| Desflurane | 0.42 | −3% / +30% | −3% / +10% | −3% / +10% |
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->

The first two columns reproduce the 2026-09-02 measurement to within a
percentage point everywhere — isoflurane's edges move by one and desflurane's
lower edge by one — which is the resolution of the search rather than a change
in the model.

This is a coarse gate. At the reference point alone a solubility error of a
fifth survives for two of the three agents — wider than the spread between
published human measurements of the same coefficient — so a pass excludes a
structurally wrong model rather than a mis-parameterized one. The flow sweep
roughly halves the tolerated upward error and is therefore part of the gate
rather than decoration. Desflurane is the tightest row and is tight in one
direction only, because it already sits at +0.79 SD with little room above
the mean; a change that moves it out of the band is a disagreement to
explain, not a tolerance to widen.

**The elimination point adds nothing to that table**, and blood:gas is the
wrong parameter to judge it on. The two ratios respond to almost disjoint
parts of the parameter set, measured the same day as movement per +10% in one
coefficient, in each ratio's own published standard deviation:

| Perturbed coefficient | Wash-in | Elimination |
| --- | --- | --- |
| Blood:gas | −0.57 to −0.64 | +0.09 to +0.17 |
| Vessel-rich tissue:gas | −0.02 to −0.06 | +0.45 to +0.55 |
| Muscle tissue:gas | −0.08 to −0.15 | −0.09 to −0.12 |
| Fat tissue:gas | −0.00 | −0.00 |

Wash-in at 30 minutes is a blood:gas measurement that barely sees the
vessel-rich group; elimination at five minutes is a vessel-rich measurement
that barely sees blood:gas. That does not compete with the rebreathing
explanation above: the circuit sets *where* the elimination ratio sits against
the published mean, as an offset fixed by the operating point, while among the
model's own parameters it is vessel-rich solubility the ratio moves with. Neither sees fat, which is what a 30-minute load
followed by a 5-minute washout should look like, and is a further reason
neither may be read as covering the slow tail. Repeating the perturbation
search on the vessel-rich coefficient gives what the second direction is
worth:

| Agent | Wash-in and its flow sweep | With elimination |
| --- | --- | --- |
| Sevoflurane | at least −90% / +25% | −16% / +19% |
| Isoflurane | at least −90% / +50% | −13% / +16% |
| Desflurane | at least −90% / +57% | −20% / +24% |

The lower edges in the middle column are the search bound rather than a
measurement: the wash-in comparison and its flow sweep were still passing at
a tenth of the shipped vessel-rich tissue:gas coefficient. Downward, that
parameter was essentially unconstrained by anything in this repository until
an elimination was compared; the elimination point closes it to about a fifth
either way. That, rather than the blood:gas column, is what the second
direction buys — together with being the only place the size and sign of this
model's departure from a measured human washout is written down.

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

A run driven through its own controls must be answered identically by the
closed form and by the stepped solver: the states derived from the run
definition, at instants the stepped system passed through, must equal the
states that system reached by stepping.

The comparison is over every compartment at every instant probed rather than
endpoints, for the reason "Deterministic replay test" gives, and it must cross
at least two setting changes, because a stretch of constant settings is the
easy case — what a run definition has to get right is the boundary between two
of them.
The tolerance is absolute rather than relative and is stated in fractions of
one atmosphere, since that is what the compartments hold and what a readout
converts: a relative tolerance would tighten without limit on the near-zero
tissue fractions of an induction and say nothing about a displayed digit.

The agreement required is far below the two-decimal percent under "Displayed
precision" and far above floating-point noise, so a real divergence fails and
a rounding difference does not. `tests/unit/test_run_definition.py` holds
`state_at` and `evaluate` against a run stepped alongside its definition and
records the figures measured; `tests/unit/test_resume_at.py` and
`tests/integration/test_controller.py` apply the same comparison to a system
stood at a keyframe and stepped from there, and to a branch against its
parent, each recording its own figure and the headroom left above it.

Until PL-2FM6 the run also kept one recorded sample per step and the chart
drew from it, and this test was what said the two records described one run.
The recorded half is gone; the comparison against the stepped system is what
carries the claim, because the stepped solver is the independently written
solution of the same equations that the closed form is checked against.

### Deterministic replay test

Two runs with identical:

- initial state;
- parameters;
- setting changes;
- event ordering; and
- simulation steps

must produce identical snapshots and identical run definitions.

Identical means element for element — every segment and keyframe of one run's
definition equal to the same segment and keyframe of the other's, and the
snapshot the same in every field — not merely equal endpoints and not
agreement within a tolerance. Comparing endpoints would pass a pair of runs
that diverged and returned, and the comparison a branched run makes against
its parent is at every instant they share.

The two runs must also be driven differently in real time: the same steps
taken one per tick in one run and in ragged bursts in the other, with the
interface reading the run between ticks at different rates. Driving both
identically holds the model to one trajectory twice, which is a weaker claim
than the one "The reproducibility guarantee" makes — that how the ticks fell
cannot reach the run.

The bursts a **playback rate** produces are a case of this and are tested as
one, against the rates the interface actually offers rather than against
invented burst sizes, so that a rate added to that ladder is covered on the
day it is added.

### Canonical evaluation test

A run queried as it is built must answer identically to the same run never
queried: element for element, across the whole state vector, at every instant
probed and in every keyframe stored. That is what says the canonical answer
belongs to the run definition rather than to the caller, and it is the property a
cache, a memoised propagator or a reused buffer would take away while looking
like an optimisation.

Two further things are held with it. A branch opening from one of its parent's
keyframes must reproduce the parent element-wise at every instant they share,
which is what "The canonical evaluation rule" owes `ROADMAP.md` item 12. And a
value from the display path must be refused where a canonical one is required,
which is what makes that rule a property of the program rather than of the
reader.

The measured separation between the two paths is published under "The
canonical evaluation rule" and held to per-quantity bounds by the same module,
so a change to the equations, to the propagator or to how a window is walked
fails there rather than silently moving a figure this document prints. The
bounds are separate for the compartment fractions and for the cumulative
accumulators because their displays resolve four orders apart, and a single
bound covering both would have to be the looser one.

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

**These four are the model's inputs, and the list is exhaustive of those
alone.** The interface carries settings of its own that also change during a
run without resetting state — the playback rate, the chart's time base, and
which compartment traces are drawn — and none of them appears here, because
none of them reaches model state: no step is resized, no segment or keyframe
of the run definition is added, discarded or altered, and identical inputs
still produce identical results. "Interface boundary" is where they are
bounded. The distinction is
worth stating rather than leaving to be inferred from which document a control
is described in: a reader who took the playback rate for a model input would
read a case played at sixty times real time as a different run rather than as
the same run watched faster, which is the reading "The reproducibility
guarantee" exists to rule out.

**"Identical inputs" is doing work in that paragraph, and the playback rate
is what decides when an input arrives.** The rate is not a model input and
changes nothing about a step — that much is exactly as stated. What it does
decide is the grid of simulated instants at which a control changed *during*
a run can first act, which is `multiplier × 0.1` s wide, so the same slider
moves performed at two rates are not the same inputs and do not produce the
same run. Nothing here is stale or resized; the reader simply has a coarser
choice of when. § "Supported simulation step" measures it, and `PL-NBWP` is
where the claim above was found overstated.

### The control-input record

Every change to a runtime control that the model actually runs under is
recorded against the simulated time it took effect, held with the run, and
cleared with it. What that record is for, what it does and does not assert,
and why it is shaped the way it is are under "The control-input timeline"
below, with the display rules the rest of the interface section carries.

#### The run is that record, and every state is derived from it

**What is held.** A run is the settings in force at each moment — the four
controls above, together with the patient and agent parameters the equations
read — plus one *keyframe* per change: the state at the instant that change
took effect. Nothing else is stored. `core/run_definition.py` is where this lives.

**What is derived.** The equations are linear and time-invariant while every
setting is held constant, so between two changes the propagator under
"Selected method (as implemented)" is exact over any horizon, not only over a
simulation step. The state at any instant is therefore one propagation from
the keyframe that opens the stretch containing it, and no value has to have
been recorded for it to be recoverable. A keyframe is itself computed that
way, one propagation per stretch, composed in order from the start of the run.

**Two paths, and they differ in composition order rather than in method.**
Answering a single instant applies one propagator to the keyframe that
brackets it. Drawing a window of evenly spaced columns instead reuses one
propagator across the columns inside a stretch, chaining from the first, which
is what makes a frame cheap. Both solve the same equations exactly; what
separates them is the order the floating-point operations are composed in.
Measured 2026-09-07 against a stepped 600 s sevoflurane run with two setting
changes, reaching a fraction of 0.0316: the single-instant path sits within
1.8e-14 of the stepped run and the window path within 3.7e-15, as absolute
differences in a fraction of one atmosphere. Both are eleven orders below the
1e-4 that the two-decimal percent readout under "Displayed precision" can
show, so neither can move a displayed digit. Which of the two a stored,
exported or branched value may be taken from is stated as a guarantee under
"The canonical evaluation rule" below.

**What this is for, measured rather than argued.** Recording one sample per
step, as the run did until PL-2FM6, cost 130.8 bytes per sample, measured
over 20 000 samples of a live run; a 30-day case at the fixed 0.1 s step is
25 920 000 samples, or 3.16 GiB.
The same case held as a definition — a busy ICU day at 50 setting changes, so
1 501 stretches — is 1.6 MiB, a factor of about two thousand. The second gain is
that answering a window stops depending on how long the run has been going: a
one-hour window at 600 columns costs 10.6 ms on a two-hour run and 13.0 ms on
a thirty-day one, against the 62.6 ms at four hours and 207.7 ms at twelve
that the recorded path cost.

**Where the cost does still move is the number of changes inside the window**,
because each stretch in view needs its own propagator. Measured on the same
thirty-day run, a full-span window at 600 columns costs 14.2 ms with two
changes in view, 231 ms with sixty, and about 1.1 s with six hundred. That is
the regime where the columns are sparser than the changes, in which sampling
600 instants is the wrong way to draw the run in any case; what to draw
instead is an interface question rather than a model one.

**This is the only record.** Until PL-2FM6 a recorded history remained
beside the definition and the chart was drawn from it, with "Closed-form
agreement test" holding the two to each other; that change deleted the
history, so the chart is drawn from the definition —
`SimulationController.drawn_window`, through `RunDefinition.evaluate_anchored`
— and there is no second record for a divergence to appear in. The stepped
system the run is advanced through remains, and the agreement test holds the
definition to it.

#### The canonical evaluation rule

**One instant, one answer, whatever route the caller took.** A run's states are
derived rather than recorded, and a derived value can be reached by more than
one sequence of arithmetic. The fixed 0.1 s step used to make that impossible
by leaving every caller the same width to take; a propagator exact over any
horizon takes that away. This is the rule that replaces it.

- **Canonical.** The state at an instant is one propagation from the keyframe
  opening the stretch that contains it, over the interval between the two.
  Each keyframe is itself computed that way, one propagation per stretch,
  composed in recording order from the start of the run. Two evaluations of
  one run definition at one instant therefore perform the identical sequence of
  floating-point operations, and are **bit-identical** rather than equal to
  within a tolerance. `RunDefinition.state_at` in `core/run_definition.py` is this path.
- **Display.** Drawing a window of evenly spaced columns reuses one propagator
  across the columns inside a stretch, chaining from the first, which is what
  makes a frame cost the window rather than the run. It solves the same
  equations exactly and composes the operations in a different order.
  `RunDefinition.evaluate` is this path.

**What each may be used for.** Every value that is stored, exported, replayed,
compared against another run, or taken as the state a branch opens from is
taken canonically. A value from the display path may be drawn, and may be
nothing else: not a keyframe, not an exported figure, not a branch's opening
state.

**The program enforces this; the paragraph above does not.** The display path
returns its states wrapped in `DisplayState`, which is not a state vector, so
it cannot be passed where one is expected — and `RunDefinition` refuses one as an
opening state by name, saying which path the value came from rather than
failing on a length. The wrapper is deliberately not a subclass of the state
tuple: the sinks this has to hold at include ones that have not been written
yet, and only a value that is structurally not a state is refused by a sink
that thought to check nothing.

**How far apart the two paths are, measured.** Worst absolute difference
between the canonical and the display answer at the same instant, over the
600-column window a chart draws, on a sevoflurane run with four setting
changes, measured 2026-09-07 on the run in
`tests/reference/test_canonical_evaluation.py`, which holds both quantities to
bounds an order above what is printed here:

| Span | Six compartment fractions | Two cumulative accumulators |
| --- | --- | --- |
| 1800 s | 1.0e-14, of 0.0301 | 3.1e-12 L, of 2.06 L |
| 24 h | 8.0e-13, of 0.0300 | 3.1e-09 L, of 30.26 L |

The wider span is the worse case, because its columns are further apart and
each chained propagation covers more ground; 24 h is the longest supported run
under "Supported run length", so the second row is the worst a supported run
reaches at this column count.

**The headroom differs by four orders between those two columns, which is why
the rule is enforced rather than trusted.** A fraction is displayed as a
two-decimal percent, so "Displayed precision" resolves 1e-4 and the
measurement sits eight orders below it — a margin that would make the
separation academic if the fractions were all a run held. The accumulators are
displayed as six decimals of a litre, resolving 1e-6 L, and the measurement
sits under three orders below that. Three orders is ample and it is not
fourteen; a display value that reached the mass-balance readout would be
wrong in a place a reader could eventually see, and it would look exactly like
the right answer.

**What this requires of a branch.** `ROADMAP.md` item 12 asks a branched run
to reproduce its parent element-wise rather than within a tolerance, and this
rule supplies that under one condition and one property of how a branch is
built, both measured rather than assumed:

- **A branch opens at a keyframe.** Restarting from the canonical state at an
  instant the parent has no keyframe for replaces one propagation over an
  interval with two over its halves, which is a different rounding of the same
  exact solution: measured at up to 5.3e-13 in an accumulator. Opening at a
  stretch boundary reproduces the parent bit for bit.
- **The branch's run definition opens *at* the fork instant, on the case's own
  axis**, carrying the parent's keyframe. Parent and child then name the same
  case instant, and each forms its propagation interval as that instant minus
  the opening of the segment holding it — from the identical keyframe, by the
  identical subtraction. The reproduction follows from construction rather
  than from a caller having performed the right conversion.

The first is a defect a plausible branch implementation would introduce. The
second is what removes a second one: until 2026-09-14 (`PL-ZMRT`, project
owner) a branch's definition opened at a zero of its own, and the rule here
required every caller to reach it by *subtracting* the fork instant from the
case's time rather than by naming the branch's own elapsed time. That
distinction was load-bearing, because the subtraction does not always
round-trip — with a fork at 900 s, `(900.0 + 1e-6) - 900.0` is
9.999999974752427e-07 and not 1e-6, so a child asked for its own `1e-6`
propagated over a different interval from its parent and landed one unit in
the last place away. The measurement is still arithmetically true and it no
longer describes a hazard this program can express: with one frame there is no
offset for a caller to name and no conversion to get right.

**One simulated-time frame, and every reader is in it.** A branch's *simulated
time* — what the clock displays, what stamps every recorded control change,
what rules the chart's axis, what the supported run length is measured
against, and what its run definition's segments and keyframes are stamped in —
is the case's, measured from induction, and continues the parent's rather than
restarting at the fork. `SimulationController.resumed_at()` opens the branch's
definition at the fork instant; `advance()` and `drawn_window()` pass case time
straight through to it. Nothing converts between frames anywhere, because there
is only the one.

Continuing the case's time is not a presentation preference. Uptake and
distribution is a function of time since induction, so a branch counting from
zero would place the patient at the wrong point on the uptake curve on the
clock, the control marks and the axis at once — the correct value under the
wrong patient context, which `CLAUDE.md`'s safety-critical standard counts as a
failure in its own right. It also keeps simulated time one multiplication under
"Simulated time is a count of steps, not a running total": a branch's instants
are the case's step count times the step, not the fork instant plus a second
total. Since `PL-ZMRT` that holds of the run definition's instants as well as
of the clock's, where before it held only of the clock.

**What one frame is worth, measured 2026-09-14.** Two measurements, on a 120 s
sevoflurane run and the branches taken from it.

The first is the reproduction. A branch forked at the 60 s keyframe and
advanced 60 s further agrees with its parent at all 601 case instants the two
share, because both are handed the same float — the case's own `steps × step` —
and neither performs any arithmetic on it. A definition opened at a zero of its
own and asked for its own `steps × step` instead differs from the parent at
**354 of those 601**. Both are exact solutions of the same equations; only the
first is the same sequence of floating-point operations, which is the kind of
sameness `ROADMAP.md` item 12 asks for. The old arrangement could reach the
first answer too, but only through a caller-side subtraction it could not
enforce; this one cannot express the second.

The second is what a reader sees. Drawn columns sit on absolute multiples of
the spacing (§ "What the chart draws"), so one frame puts a trunk and a branch
on the same column instants without the display path being told anything. On a
13-column 120 s axis with the fork deliberately off the grid at 55.3 s, **all 8
of the branch's columns** are instants the trunk also draws; with the branch
anchored to its own zero it drew 55.3, 65.3, 75.3 … and shared **2 of 8**, so
the two traces could not be read against each other at matched points.
`tests/integration/test_controller.py` and
`tests/reference/test_canonical_evaluation.py` hold both.

### Supported input ranges

Each control is supported over a closed interval, endpoints included, and a
setting outside it is refused rather than simulated:

| Control | Range | Declared and refused by |
| --- | --- | --- |
| Fresh gas flow | 0 to 10 L/min | `core/supported_ranges.py` |
| Delivered concentration | 0 to the agent's `max_delivered_concentration_percent` | `BreathingCircuit` |
| Alveolar ventilation | 0 to 12 L/min | `core/supported_ranges.py` |
| Cardiac output | 0 to 10 L/min | `core/supported_ranges.py` |

**The ranges are the model's, not the interface's** (PL-0MLQ). Until v0.2.10
the first three were declared only as slider limits in
`app/simulation_view.py` and enforced nowhere:
`AgentUptakeSystem.set_cardiac_output(1000.0)` was accepted and simulated,
as were a fresh gas flow of 500 L/min and an alveolar ventilation of
200 L/min, because the compartment setters checked only that the value was
nonnegative and finite. The sliders were the sole thing keeping a run inside
the domain the verification gates cover, so every other caller of `core/` —
a headless run, a notebook, a test — could leave it. `core/supported_ranges.py`
declares the three intervals now, each compartment refuses a value outside
its own, and every `AgentUptakeSystem` setter forwards to that compartment;
`app/` imports the same constants for its sliders rather than restating them.

**Refused, not clamped**, for the reason the vaporizer maximum is: a silently
clamped setting would simulate, display, and chart a value the user did not
ask for. A `SimulationConfigurationError` is raised before anything changes,
so the run in progress stays trustworthy and the interface reports the
refusal beside the control that caused it — the same distinction "Supported
simulation step" above draws between a refused argument and a step that
broke down.

**Enforced on the compartment, not on the coupled system**, which is the
opposite of where `MAXIMUM_SIMULATION_STEP_S` sits, and for a reason the two
cases do not share. A step is an argument to one call, and a compartment
advanced alone is exact at any step, so guarding a compartment there would
refuse an exact calculation. A flow is persistent state, reachable through
`AgentUptakeSystem`, through the compartment it belongs to, and through that
compartment's constructor; the compartment is the only point all three pass
through.

#### What a setting outside the range costs

**The argument here changed with the exact step, and the ranges did not.**
Until v0.4.x these limits were justified numerically: the operator split was
first order, its coefficient $`C`$ grew with the flows roughly in proportion,
and a setting outside the ranges therefore produced a displayed number that was
not merely unverified but *wrong*, by a known multiple of the last displayed
digit. The exact step removes that argument entirely — it solves the equations
exactly at any flow, so an out-of-range setting now yields a number that is
numerically right.

**What justifies refusing one is therefore what it always also was**, stated
here now that it stands alone. These ranges define the **verification domain**:
they are what "Independent-solution test" drives its trajectories over, what
"Published wash-in and elimination validation test" compares against measured human data, and
what every figure in this document is measured across. Outside them the
implementation has not been checked against anything — and, more seriously,
neither has the *model*. A cardiac output of 1000 L/min is not a patient, and
these equations were never proposed as a description of one; solving them
exactly for it produces a precise answer to a question physiology does not ask.
Preferring an obvious failure to a plausible-looking number is the required
behavior for exactly that case, and it does not depend on the arithmetic being
imprecise.

The numerical figures below are kept as history. They were measured on
desflurane over the *unperfused load, then dial off* trajectory of
"Independent-solution test" above, at the shipped 0.1 s step against the
0.01-percentage-point displayed resolution, and they describe the method that
shipped through v0.4.2:

| Setting | $`C`$ (s⁻¹) | Multiple of the bound | Last displayed digit uncertain by |
| --- | --- | --- | --- |
| The documented maxima | $`2.29\times10^{-3}`$ | 1.0 | 2.3 counts |
| Alveolar ventilation 200 L/min | $`3.37\times10^{-3}`$ | 1.5 | 3.4 counts |
| Fresh gas flow 500 L/min | $`5.82\times10^{-3}`$ | 2.5 | 5.8 counts |
| All three flows at twice their maxima | $`4.57\times10^{-3}`$ | 2.0 | 4.6 counts |
| All three at ten times their maxima | $`2.28\times10^{-2}`$ | 10.0 | 23 counts |
| Cardiac output 1000 L/min | $`9.12\times10^{-2}`$ | 40 | 91 counts |

The last row is the setting PL-0MLQ found accepted. Under the split, ninety-one
counts was an alveolar readout wrong in its *first* decimal while presenting
itself as a settled two-decimal value. Under the exact step that readout is
right to the last digit, and is a precise concentration for a patient with a
cardiac output twenty times any human's — which is the worse of the two
failures, not the better one, because nothing about the display invites doubt.

Note what the table also showed: the error did *not* explode at the boundary.
Nothing broke at 10.01 L/min, and the interval's exact endpoints are a decision
— the settings envelope the interface offers and the verification measures
over — rather than a discovered cliff. That is still true, and it is now the
whole of the story rather than half of it: the endpoints are where verification
stops, and nothing else marks them. Widening one is a legitimate change and a
safety-critical one — extend the verification domain first, re-run the
trajectories of "Independent-solution test" over it, and revise this section
with them.

**Re-derivation still owed.** This subsection has been re-grounded rather than
re-measured: the argument above is complete, but the table is history and the
displayed-resolution claims it refers to have not yet been re-derived for the
exact step. That is queue item `PL-X9KD`, together with "Displayed precision"
and the supported step bound.

#### Supported run length

A run is supported up to **24 hours of elapsed simulated time**, declared as
`MAXIMUM_ELAPSED_SIMULATION_TIME_S` in `core/supported_ranges.py`. The step
that would carry a run past it is refused by `SimulationState.advance()`,
which raises `SimulationDomainLimitError` before anything advances.

| Quantity | Limit | Declared and refused by |
| --- | --- | --- |
| Elapsed simulated time | 0 to 24 h (86 400 s) | `core/supported_ranges.py`, enforced on `SimulationState` |

**It is the case's 24 hours and not each run's, which matters once a case can
be branched.** The limit is what this model's omissions are argued against
below, and those are properties of how long the *patient* has been anesthetized
— so a branch spends the same envelope its parent was spending, from where it
was taken. A fork at 23 h leaves one hour, not another twenty-four. Nothing
enforces this separately: the guard reads a step count, and a branch continues
its parent's, so the arithmetic that bounds a trunk bounds every branch of it
(`PL-J2TD`).

**It is the same kind of statement as the four ranges above, and it is
reached rather than set.** A flow is a setting, refused when a caller offers
one outside its interval; a run length is a property of how far the run has
gone, so it can only be checked as each step is taken. Everything else about
it is the same: the interval is closed, so a run may complete the step that
lands on 24 hours; and outside it the equations still solve exactly, as
"What a setting outside the range costs" says of the flows. What stops at the
boundary is the claim that the solution stands for a patient.

**What bounds it is what this model omits.** Metabolism, first of all. "Known
limitations" records that this model has none, and "Published wash-in
validation test" already draws the consequence: it compares against five
minutes of elimination and explicitly refuses the two Yasuda papers' own
multi-day curves, because *over days the missing metabolism is no longer
negligible, and neither is the fat group's flow* — which the same section
records as about twice the reachable resting measurement, acting directly on
the slow tail of washout. A run beyond this boundary is therefore displaying
a trace whose slow component is increasingly the two omissions rather than
the model.

Sevoflurane is the binding agent: 2% to 5% of the absorbed dose is
metabolized, against far less for isoflurane and desflurane, and metabolism
begins immediately rather than late — fluoride and HFIP appear in plasma
within minutes of the start of administration. What makes omitting it safe
over a case is the same review's finding that metabolism "does not contribute
to the termination of clinical drug effect": true while ventilation and
perfusion dominate the trace, and progressively false once the only thing
still moving is the slow tail this model gives no sink to. That review's
dose-proportionality covers exposures of 0.35 to 9.5 MAC-hours, so past
roughly ten MAC-hours even the size of the omission is unmeasured.

- Kharasch ED. *Biotransformation of sevoflurane.* Anesth Analg
  1995;81(6 Suppl):S27-38. PMID 7486145,
  doi:10.1097/00000539-199512001-00005.

**That citation is tier 2, and nothing here is stored from it.** It is a
review, and under "Source hierarchy" a tier-2 source is the authority for a
stored value only on a recorded decision; none has been taken for this one, and
there would be nothing for it to authorize — 24 hours is not computed from 2% to
5%, and no parameter in this model descends from that paper. What it supplies is the
magnitude and the timing of the omission this boundary is argued against,
which is exactly what tier 2 is legitimate for. A cap derived arithmetically
from a metabolic rate would need the primary measurements instead, and would
be a different and better limit than this one; it is not what is claimed
here.

**Why 24 hours, and not a multiple of the slowest time constant.** The fat
group's time constant is about 42 h, and a cap argued as several multiples of
it would select for precisely the regime described above — the part of the
trace that is most nearly all omission. The fat time constant bounds this
number from *below* rather than above: shorter than about one of them and the
fat trace stops showing what it exists to show. 24 hours is about 0.6 of it,
so the fat compartment is still visibly loading; it clears every anesthetic
this simulator is built to teach by a wide margin; and it sits inside the
regime the source above calls clinically negligible for metabolism, near the
outer edge of the exposure range over which that omission has been measured
at all.

**This replaces a memory limit that was never a modelling one.** The figure
carried before this section existed was 30 days, set on 2026-08-25 to size a
concentration history that no longer exists, and enforced nowhere at all: a
run could reach day 45 and go on displaying two-decimal concentrations. The
question a run length answers is a supported-domain question and not a
resource one, which is why the number moved by more than an order of
magnitude when it was asked properly (`PL-Y5WR`).

**Reaching it is not a failure, and the interface may not present it as one.**
The step is refused before it begins, so a run stopped here stands on a
completed step at a simulated time inside the supported span, and every
displayed value is a real solution of the model. `SimulationDomainLimitError`
is a distinct exception type for exactly this reason, and `app/` reads it to
choose its wording: the run stops, the reader is told which limit was reached
and why it is where it is, and reset starts a new run. Describing a correct
model as a broken one misleads a reader as surely as the reverse — it spends
the interface's one signal for a real fault, and teaches a reader to discount
it. What the interface must equally not do is present the stop as a pause:
Start is refused, because a resumed run's first step would be refused again.

**Volatile sedation in intensive care is out of scope, deliberately.** It runs
for days through an anesthetic-conserving device, and is exactly the regime
this model is wrong in. Reaching it is a model extension — metabolism first —
rather than a raise of this number, and raising the number without it would
produce the plausible-looking wrong values this document exists to prevent.

Widening this limit is a safety-critical change on the same terms as widening
a flow interval: argue the longer span against what the model omits, extend
the validation that covers it, and revise this section with the result.

#### What is not bounded this way

The two gas volumes — the breathing circuit's and the alveolar
compartment's — are **fixed model parameters rather than controls**, and
they carry no declared interval. Each is set once, when
`AgentUptakeSystem.for_agent()` builds the system, and nothing moves it
afterwards: the interface offers no control for either, and since v0.4.x
`SimulationController` exposes no setter for either. Both are validated as
positive and finite, by `core/validation.py`, rather than against a measured
domain.

The two do not have the same provenance, and the difference is worth stating
rather than smoothing over. The alveolar gas volume is a patient parameter,
2.5 L, read from `data/patients/reference_adult.json` and carried in the
provenance table above with the FRC measurement it is reconciled against.
The circuit volume is a *machine* parameter, 6.0 L, read since `PL-4YY1` from
`data/machines/reference_circle_system.json` — a third kind of parameter file
beside the agent and the patient, because the breathing system belongs to
neither — and carried in the same table with what is known about where it came
from, which is that no source is adopted for it. Until that item it was the
field default `circuit_volume_l: float = 6.0` on `BreathingCircuit` and had no
row here at all, so the only tool that checks this document against the data
files could not see it: `check_provenance` walks data files in both
directions, and a constant that never entered one is invisible to it.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->

**Each parameter file is the single authority for its own values, and the
`core/` field defaults that restate them are held to it by test.**
`AlveolarCompartment` and `BreathingCircuit` both still carry their two
figures as dataclass field defaults — `gas_volume_l: float = 2.5` and
`alveolar_ventilation_l_min: float = 4.0` on the first,
`circuit_volume_l: float = 6.0` and `fresh_gas_flow_l_min: float = 4.0` on the
second. They are kept so that a unit test of one compartment's physics need
not load package data, and they are reached by nothing else: every shipped
path goes through `AgentUptakeSystem.for_agent()`, which reads all four from
the two files and passes them explicitly. What makes that safe to keep is that
neither restatement may drift.
`test_the_bare_circuit_defaults_match_the_shipped_machine_file` (`PL-4YY1`)
and `test_the_bare_alveolar_defaults_match_the_shipped_patient_file`
(`PL-DJYF`) each assert the literals against the file, and
`test_for_agent_builds_the_circuit_at_the_machine_file_s_values` and
`test_for_agent_builds_the_alveoli_at_the_patient_file_s_values` each assert
that the shipped path reads the file rather than falling through to them. The
second half of each pair is the one that catches the consequential failure:
because the defaults currently equal the files' values, a change that stopped
`for_agent()` reading a file would move no number, and every provenance row in
this table would silently become a claim about a file the model no longer
consults.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6.0, default_fresh_gas_flow_l_min = 4.0 -->

**Why neither gets a supported range.** A supported range describes an
envelope a run can be steered *within*: the four controls above each name an
interval because a user can put the model anywhere in it, and the
verification gates are what establish that the model represents a patient
across it. Neither volume moves. The single shipped value is the whole of
each one's domain, every reference measurement in this document is made at
it, and an interval declared around it would assert verification across a
span nothing has measured — the same overstatement that widening one of the
four intervals without re-running the gates would be. Fixing the value and
saying so is the stronger claim, not the weaker one.

**What a wrong volume would be wrong for.** The argument is physiological
applicability, exactly as it is for the four controls — not numerical error.
Measured 2026-09-06 on sevoflurane at the shipped 0.1 s step: a 0.005 L
alveolar compartment and a 10 000 L circuit both advance without incident and
with agent accounting passing, so each yields an arithmetically correct answer
to a question physiology does not ask. A 5 mL alveolus is not a lung, and this
model's lumped structure, its fixed tissue volumes and its constant partition
coefficients are claimed to represent a patient only near the values shipped.
This section stated the opposite justification until v0.4.x — that a small
alveolar volume inflated the operator split's error — and that argument
retired with the split.

**The numerics do eventually object, and that is a backstop rather than a
bound.** The same measurement, continued downward: an alveolar volume of
$`10^{-9}`$ L and below halts the run through `AgentSimulationValidationError`,
the mass-balance guard rather than any declared domain, which is the required
"obvious failure rather than a plausible-looking number" arriving by accident
of arithmetic. It is not a limit this document declares and it must not be read
as one — it sits six orders of magnitude below any volume a caller would pass
by mistake, and it says nothing about the physiological question above.
Circuit volume has no such point: it was advanced up to $`10^{300}`$ L with
accounting passing throughout.

**Below that the mass-balance guard stopped firing, and what refuses now is
upstream of it** (`PL-3PRZ`). At $`10^{-300}`$ L the run advanced and returned
an alveolar fraction of exactly 0.0 with accounting passing. The guard was not
weak: the propagator had been driven to the zero matrix, so `propagate()`
returned the zero state vector, and the identity was handed
$`0 + 0 - 0 - 0`$ on totals that had all been annihilated together. Zero does
balance zero. Every term of the check had been destroyed before the check ran,
which is the shape to look for wherever a residual is formed from quantities
the same failure can reach.

`core/matrix_exponential.py` now refuses a zero propagator, because
$`\exp(A\,\Delta t)`$ is nonsingular for every finite $`A`$ — its determinant
is $`e^{\operatorname{tr}(A)\Delta t}`$ — so the zero matrix is the
exponential of nothing and can only be a floating-point artifact. It also
refuses the case where scaling the matrix norm down to the series bound
overflows, which reached `ceil(log2(inf))` and raised a bare `OverflowError`
at $`10^{-309}`$ L, outside the hierarchy in `core/exceptions.py` that a
caller keys on. Both arrive as `SimulationNumericalError` through
`AgentUptakeSystem.advance()`, with the step rolled back.

**Measured across every decade from $`10^{0}`$ to $`10^{-323}`$ L**, before
and after: 120 advance with the constant state row exact, and the same 120
advance now; 77 were already refused as non-finite and 194 are refused now;
the 116 that returned a zero propagator silently, and the one that raised
`OverflowError`, make up the difference exactly. Nothing that advanced before
is refused now. A single mode decaying below the smallest subnormal is still
propagated as 0.0, which is correct — `exp(-0.5 * 3600)` is a real number no
double can hold — and is what separates a decayed entry from an annihilated
matrix.

**One failure in this family is still open.** Between $`10^{-8}`$ and
$`10^{-19}`$ L the propagator stays finite and nonzero, and the constant state
row — which no interval may move, and whose row in $`A`$ is empty for exactly
that reason — drifts: 1.0000610 at $`10^{-12}`$ L, then 2.718, then
$`2.28\times10^{+222}`$ at $`10^{-19}`$ L. The shift is what admits it, and
the squarings amplify it by $`2^{j}`$. The mass-balance guard catches this
band today, at $`10^{-9}`$ L and below, so no value reaches a display; it is
tracked as its own item rather than fixed here, because the remedy is a change
to the numerical method rather than a guard on its result.

**What is left open, stated plainly.** A caller writing Python against
`core/` can still construct `BreathingCircuit(circuit_volume_l=10_000.0)` or
`AlveolarCompartment(gas_volume_l=1e-6)`, and `SimulationController` still
takes a `circuit_volume_l` argument at construction. Those are outside the
verified domain and nothing refuses them. They are a different exposure from
the one the four controls had before `PL-0MLQ`: not a live setting a run can
be steered with, and not reachable from the interface at all, but a value
chosen once by a caller who has gone to the trouble of building the model
directly. `BreathingCircuit.set_circuit_volume` remains for the same reason
— it is how the parameter reaches the circuit, and it is where the agent
conservation and capacity guards live (`PL-006`).

**Zero is a supported input on all four, deliberately** (PL-629Z). Three
reasons, and the third is the one that decides it:

- The governing equations stay well posed. A zero flow removes a transfer
  term rather than dividing by one: at $`Q=0`$ the tissue and venous
  derivatives are zero and the alveolar equation loses its uptake term, and
  "Required tests" above already specifies that behavior in the
  zero-ventilation, zero-cardiac-output, and zero-tissue-flow tests.
- Zero is the endpoint of a continuous axis. Flooring a slider just above it
  would place an arbitrary boundary inside the model's own valid domain, and
  a reader would have no way to tell that boundary from a modeling limit.
- The low end of each flow axis is where the teaching is, and zero is its
  limit. Reducing cardiac output *accelerates* alveolar wash-in, because less
  agent is carried away from the lungs per unit time — one of the central
  results in uptake and distribution, and one this model reproduces. With
  sevoflurane at 1 MAC and the reference adult's other defaults, $`F_A/F_I`$
  at five minutes is 0.41 at 10 L/min, 0.49 at 5 L/min, 0.58 at 2.5 L/min,
  0.70 at 1 L/min, and 0.86 at zero. Refusing the last of those would
  truncate the demonstration one step before its clearest case. The same
  argument holds for alveolar ventilation at zero, which is apnoea.

**What zero cardiac output does not claim.** It is a statement about agent
transport and nothing else: uptake stops, so alveolar gas approaches inspired
and the tissue stores hold whatever they already had. It is not a model of
circulatory arrest, cardiopulmonary bypass, or ECMO — "Known limitations"
excludes all three — and nothing about the patient's condition follows from
it. A run at $`Q=0`$ answers "where does the agent go when perfusion stops",
not "what is happening to this patient".

**These ranges define the verification domain.** "Independent-solution test"
above drives its trajectories over what these ranges can produce, and its worst
disagreement with the independent solution is reached on one that holds cardiac
output at zero. Narrowing a range would take that worst case out of the
reachable domain, and widening one would admit trajectories never measured;
either way the gate must be re-measured. This is what the ranges are *for* now
that the exact step has removed the numerical argument for them — see "What a
setting outside the range costs" above. Three checks keep that from happening silently:
`test_envelope_limits_match_the_supported_input_ranges` restates all six flow
limits and fails if the model moves one,
`test_displayed_resolution_and_shipped_step_match_the_interface` does the
same for the resolution and step every figure is quoted at, and
`test_the_sliders_span_the_supported_input_ranges` fails if the interface
stops short of the declared domain or reaches past it.

**The simulation step is bounded too, and separately.** It is not a control a
user sets, but it is an input to every `advance()` call, and what a caller
may pass is bounded by `MAXIMUM_SIMULATION_STEP_S` rather than by these
ranges; "Supported simulation step" above derives it.

**The two bounds are now independent, and were not before** (`PL-X9KD`). While
the operator split shipped, the coefficient the step bound inverted was
measured over the trajectories *these* ranges produce, so widening a range
meant re-deriving both. That chain is cut. The step bound is a declared
control-resolution tolerance in seconds, these intervals are a claim about
where the compartment structure represents a patient, and neither is computed
from the other. Widening a range means re-running the reference gates at the
new corner; it does not mean revisiting the step.

## Reset behavior

Reset must:

- pause the simulation;
- set simulation time to zero, by clearing the step count it was reached
  from, and release the step the run was taking so a fresh run may take a
  different one;
- clear circuit, alveolar, blood, and tissue agent amounts;
- open a fresh run definition at the cleared state, so no state of the run
  being discarded can be derived or drawn;
- clear the recorded control-input timeline, which belongs to the run that
  recorded it;
- reset cumulative delivered and exhausted amounts;
- restore the mass-balance residual to zero;
- clear any recorded failure state, so a session halted by a failed step
  becomes startable again from a clean state; and
- preserve the user’s selected settings.

## Agent-change behavior

Changing the running agent must begin a new run. Switching between volatile
agents is not modeled (see "Known limitations"), so there is no residual
washout to carry across and no state from the old agent that the new one's
partition coefficients would make meaningful. A change of agent must
therefore do everything Reset does, and in addition rebuild every compartment
against the new agent's parameters and take the delivered concentration from
that agent's own 1 MAC rather than carrying the old agent's percentage — the
same number is a different clinical depth for each agent.

Because it begins a new run it **destroys one**, and that is a requirement on
the interface rather than only on the controller. The run definition, the
control-input timeline and the simulated time a run reached are the whole of
what a learner has to look back at, nothing in this application persists
them, and there is no undo. So:

- the interface must not discard a run holding anything — any elapsed
  simulated time, or any recorded control change — without first stating that
  it will be discarded and obtaining the user's confirmation;
- the statement must name what is lost in the terms the display already uses
  for it, so that it can be checked against the readouts it describes;
- declining must leave the run, its definition, its timeline and the control
  that offered the change exactly as they were; and
- a selection that resolves to the agent already running must change nothing,
  since it proposes no new case.

A run that holds nothing — no elapsed time and no recorded control change —
is exempt: there is nothing to discard, and
a confirmation that fires where nothing is at stake is answered without being
read by the time one is. Reset is therefore also the way to make a change of
agent free.

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

**What a drawn window is.** What a chart draws from is a `DrawnWindow`
(`app/run_series.py`): the states at the instants one frame plots, evaluated
from the run's definition by `SimulationController.drawn_window`, with nothing
stored behind them. Each state is bound to the substance the run is of and
carries that substance's six compartment values, as fractions of one
atmosphere, under the stable identifiers `RecordedQuantity` names; a trace
addresses one of them as a `RecordedSeries`, a substance-and-quantity pair. A
run is of one substance today, the agent it is a run of; changing agent
starts a new run rather than adding to this one, so a window describes one
substance.

It is keyed by substance rather than by six named fields because a
compartment fraction asserts nothing without the substance it is a fraction
of. A naming of the six flatly can describe exactly one substance, so a
second would have to arrive either as six more names or as values pooled
with the first's, and pooled values are the correct-number-wrong-label
failure this document forbids elsewhere. The chart is addressed the same
way — one trace is bound to one substance-and-quantity pair — so a trace can
draw only what it names, and a frame asking for a substance the run is not
of fails rather than drawing whichever substance it does hold. The wash-in
quotient below is formed from one substance's own two fractions, for the
same reason.

**What a snapshot is, and why it is not keyed the same way.** The
instantaneous state a frame is rendered from — `app/controller.py`'s
`SimulationSnapshot` — carries the six compartment values as flat named
fields rather than as the per-substance mapping above. That asymmetry is
decided rather than unfinished (`PL-TCD1`, 2026-09-13). A snapshot is one
instant's transient state for the running agent: unlike the run definition
it is never stored, never compared against a later run, and never read back,
so giving it a second substance later adds a field rather than invalidating
anything already written. That is the test `ROADMAP.md` § "Designed for
forking" applies — "whether retrofitting invalidates recorded runs or merely
adds a field" — and it names per-compartment agent amounts in the snapshot on
the declined side of it. `ROADMAP.md` Phase 1 generalizes the patient to N
simultaneously present substances, and the mapping arrives with it.

What the asymmetry may not do is let one frame describe the run in two
vocabularies. The six fields travel with the `agent_id` and
`agent_display_name` they belong to, for the same reason `agent_mac_percent`
travels beside the concentrations it scales, and the interface names the
substance on the readout row itself rather than leaving a reader to carry it
over from the agent selector — so a compartment number and the trace beside it
name the same substance on the face of the display.

**What the chart draws.** A plotted trace need not draw the run at every
instant it passed through — a run advances by one step every 0.1 s, well
beyond what a chart can resolve — but every point it does draw must be a
state the run actually reached, at the instant it is drawn at. The interface
must not interpolate, smooth, average, or otherwise synthesize a plotted
value, and the instant the numeric readouts were formatted from must always
be drawn, so that the end of a trace and the readouts beside it cannot
disagree.

The chart meets this by **evaluating the run's definition rather than reading
samples back from a store**. `core/run_definition.py` answers the state at any
instant in closed form, so the columns a frame draws are chosen for the
axis being drawn and computed for it, and there is no recorded series
behind the trace that could disagree with it. Where the columns fall is
decided by two rules, and both are properties this document requires rather
than optimisations:

- **The columns sit on a grid anchored to the case's zero**, at absolute
  multiples of the spacing the selected time base and the width of the plot
  imply: one column per pixel boundary of the plot the frame is drawn on, and
  never fewer than 150 (`chart_columns` in `app/chart_frame.py`, `PL-GS3R`).
  A window following the run therefore keeps every column it had
  and gains at most one, so a steady trace is not redrawn on every frame. A
  grid anchored to the viewport instead would move on every scroll and resize,
  and rewrite the whole chart on every frame. The anchor is the case's zero
  rather than each run's own opening, which is what puts a branch's columns on
  the same instants as the trunk's and lets the two be read against each other
  at matched points; a per-run anchor put a branch forked at 55.3 s on 55.3,
  65.3, 75.3 … while the trunk drew 0, 10, 20 ….
- **Every control event inside the window is a column of its own.** Between
  events the trajectory is a sum of exponentials with bounded curvature and
  no hidden transients, so every sharp feature in a run is at an event
  boundary; a grid that stepped over one would draw a straight line through
  the single instant a reader is looking for. Each such column is read from
  the keyframe the run definition already holds at that instant, so it is exact
  rather than propagated.

**So the drawn chart reproduces every control change**, to the last digit
the readouts display, while the stored record need not — there is no stored
record (project owner, 2026-09-05, recorded here when the sample store was
deleted). The interpolation error at the instant the dial moves scales as
O(h) rather than O(h²) — the signature of a kink, since the derivative of the
circuit fraction is discontinuous at a control change — and placing a column
on each event is the whole of the answer to it.

**Between events the guarantee is a pixel of time, not a number of percentage
points** (`PL-GS3R`, decided 2026-09-14). Between two drawn instants no more
than a pixel apart, both exact, a monotone run and the straight segment the
plot rules between them cross every level inside the same pixel: the drawn
line is within one pixel of time of the run everywhere, and on it at every
drawn instant. The numeric departure between drawn instants is deliberately
not the guarantee. Where the trace is steep, one pixel of time is many
percentage points of value, and no display reads a value between drawn
instants — the hover answers only at a point the plot draws (§ "The chart's
hover readout"). The pixel is a logical pixel of the plot, which is the
resolution the axis is ruled and labelled at.

That guarantee was the answer to a measurement. A fixed budget of 150 columns
at every width — the rule from `PL-2FM6` until `PL-GS3R` — ruled a 290 s chord
across the twelve-hour base and drew the steep early wash-in below the run: by
0.53 pp on the alveolar trace (0.26 MAC) and 0.89 pp on the circuit trace for
sevoflurane 2% to 4% at the fastest supported settings (FGF 10 L/min, V_A
12 L/min, Q 10 L/min), and by 3.8 pp on the alveolar trace (0.64 MAC) and
5.5 pp on the circuit for a desflurane overpressure induction, 0% to 12% then
6% at 600 s. Holding a numeric bound instead — 0.01 pp, the readout's
resolution, everywhere on every trace — needs a 2 s chord on that desflurane
case, 21 601 columns across twelve hours, which no hardware this project has
measured can draw inside its frame budget; and the whole of that error sits
within 1 800 s of a dial change, beyond which the 290 s chord itself is within
0.0024 pp. Measured 2026-09-14 against the closed-form state every 0.1 s, the
step the run advances by, over five twelve-hour runs built in closed form.

What the one-pixel rule leaves between drawn instants, measured on a 1 000 px
plot, where the chord is the rung's span over 1 000:

| Time base | Chord | Sevoflurane 2% to 4%, worst trace | Desflurane 0% to 12% to 6%, worst trace | Desflurane, alveolar |
| --- | ---: | ---: | ---: | ---: |
| 15 min | 0.9 s | 0.0004 pp | 0.0025 pp | 0.0025 pp |
| 1 h | 3.6 s | 0.0052 pp | 0.032 pp | 0.032 pp |
| 4 h | 14.4 s | 0.048 pp (circuit) | 0.28 pp (circuit) | 0.21 pp |
| 12 h | 43.2 s | 0.21 pp (circuit) | 1.21 pp (circuit) | 0.26 pp |

Those are the mid-chord departures of a straight segment from a curve that
passes through both of its ends: a vertical gap at an instant no display
reads, and under one pixel horizontally by the argument above. They grow with
the chord, so a narrower plot draws a larger one and a wider plot a smaller,
and they are the bound a reader should have in mind for a trace's *shape*
inside a single pixel column, never for a value.

**The one case the pixel argument does not reach is an extremum between two
dial changes.** The alveoli and the venous blood keep filling for a moment
after the vaporizer is turned down, so a trace can turn inside one interval
and rise above both drawn values, where the line falls short of it. Measured
over five runs — the two sevoflurane cases at the fastest settings, 2% to 4%
and 4% to 0%; the desflurane case at the fastest and at slow settings (FGF
0.5 L/min, V_A 2 L/min, Q 2 L/min); and the reference adult at 1 to 2 MAC —
the worst such gap at any rung is 0.0028 pp, on the mixed venous trace at the
desflurane dial-down on the twelve-hour base: under a third of the readout's
resolution. `tests/unit/test_run_definition.py` holds that case under half of
it.

Pegging that residual to the displayed resolution is deliberate, and it does
not cross the line drawn under "Supported simulation step". That section
forbids traffic in the other direction — the readout's decimal count must not
reach back into the model, which is why the step tolerance and the supported
ranges are stated in absolute percentage points. This is a statement about
the *chart*, expressed in the units a reader actually reads it in. Nor is the
peg arbitrary: the two-decimal readout is itself derived from model fidelity
under "Displayed precision", one published SD of a partition coefficient
displacing a compartment by 8.7e-4 to 6.8e-2 percentage points.

The pixel-column framing is the one Jugel, Jerzak, Hackenbroich and Markl
prove from the other side, for recorded data: that a line chart is fixed by
at most four values per pixel column (M4: A Visualization-Oriented Time
Series Data Aggregation, *Proceedings of the VLDB Endowment* 2014;7(10):797-808).
Their selection itself is not used. Nothing is selected from a store, the run
is evaluated at the column instants, and a control event is a column whatever
the pixel width, which is what a selection of recorded extremes could not
guarantee (`PL-4RBD`). The Flet chart, which could not afford a column per
pixel (`PL-YSZN`), kept a fixed 150-column budget through its own series
module until `PL-25KS` ported the dashboard and that module left with it.

The drawn columns are display-path values, taken under "The canonical
evaluation rule" below: they may be drawn and nothing else, and the program
enforces that rather than describing it.

**Which compartment traces are drawn is the reader's to choose, and the
choice may not change anything else.** Two compartments cannot be compared
against four other lines crossing them, so the interface may draw a subset of
the six. Three things bound it. The selection is presentation only: it reaches
no model state, changes nothing in the run definition, and leaves identical
inputs producing identical results. Every compartment's concentration stays
in the numeric readouts whatever is drawn, so a chart showing two curves is a
chosen view of six modelled compartments rather than a model with two. And the
display must state, for every compartment, whether its trace is currently
drawn — a legend entry for a line that is not on the plot is a claim about the
run the run does not support, which is the defect an unlabelled reference
would be arriving from the other direction.

A **reference** is not a trace and is deliberately exempt from the rule
above: it draws no state of the run, because it is a published constant
rather than a modeled quantity. That exemption is bounded by a labelling
requirement in its place. A reference must state the value and the divisor
it was drawn from, must name the compartment it is to be read against, and
must be visually distinguishable in kind from a compartment trace — by mark
type rather than by colour alone. An unlabelled horizontal line is a modeled
quantity to a reader who has no reason to think otherwise, which is the
modeled-versus-measured confusion this document forbids elsewhere arriving
through the chart. See "MAC-awake as a chart reference".

A **displayed ratio** of two modelled fractions is a trace and is *not*
exempt from the rule above: every point it draws is still computed from one
evaluated state of the run, at the instant it is drawn at, and nothing about
it may be interpolated, smoothed or averaged. What it needs in addition is a
**stated domain**, because a quotient of two modelled states can be undefined
(a zero denominator) or outside what the plot claims to show, and neither case
has a number the interface may substitute. So: the domain is documented here
and enforced in one place in code; a drawn instant outside it contributes no
point, rather than a clamped, extrapolated or defaulted one; the trace breaks
where the domain does, rather than joining across the instants it skipped,
which would draw values the run never produced; the display states which two
quantities the ratio is of, in the terms this document uses for them; and where
the trace
is absent the display says which boundary it stopped at, since an absent
trace otherwise reads as a run that stopped. See "F_A/F_I as a displayed
ratio", the only such quantity today.

A **control mark** is a third kind of chart series, and is exempt from the
trace rule for a different reason again: it draws no value at all. It marks
a simulated time on the horizontal axis and asserts nothing about the
vertical one. It is bounded by its own labelling requirement in place of
the exemption: a control mark must be visually distinguishable in kind from
both a trace and a reference by something other than colour, must be
identified on the display as a record of a user input rather than of
anything measured or modelled, and must be accompanied by a statement of
which control moved and to what — a bare mark says an unspecified something
happened, which invites the reader to supply their own explanation for the
change in the curves beside it. See "The control-input timeline".

Declaring where an adjustment begins is a statement about the *input
device* and not about the model: it changes no simulation state, records no
value, and must not alter what is recorded or what the model computes. It
exists because a slider reports continuously while dragged, so the
interface is the only party that can distinguish one turn of a control from
two.

**How wide a window the chart draws is the reader's to choose, and the choice
may not change the run.** A case runs for hours and the moment a learner is
most likely to be watching is minutes long, so no single window serves both.
Three things bound the choice. It is a view control: it reaches no model
state, alters nothing in the run definition, and leaves identical inputs
producing identical results, so it sits outside "Runtime controls" with the
other interface settings. The width in force must be a fixed property of the
selection rather than of how long the run has been going, since a window that
grew with the run would rescale every trace's slope while the underlying
rates did not. And a mode that claims to show the whole run must show the
whole of it at every length — a window narrower than the case, labelled as
the whole of it, is a false statement about what the reader is looking at.
See "The chart's time base", which carries the widths, the ruling and the
labelling this paragraph requires.

**A playback rate is a number of steps, never a step size, and it has to be
on screen.** The two compartments that make uptake and distribution worth
teaching cannot be watched in real time — sevoflurane's muscle group has a
time constant of about 135 min at the reference settings and fat about 42 h
— so the interface may play a run faster by taking more steps per tick. Three
things bound it, and they are of different kinds.

The first is arithmetic. The step size is fixed, and the rate is realised
*only* as how many of those steps a tick takes; a rate that does not land on
a whole number of steps is refused rather than rounded, because the
alternatives are a step of a different size or a run advancing at a rate
other than the one displayed. This is what keeps a faster playback inside
"The reproducibility guarantee" rather than making it a second numerical
solution: identical inputs still produce identical run definitions, and
two learners comparing the same case at different speeds are comparing the
same arithmetic.

The second is control resolution, and it is the one that limits what the
sentence above may be taken to mean. Those two learners are comparing the
same arithmetic, and they are comparing the same *case* only if neither of
them touches a control: a tick advances its whole burst uninterrupted, so a
setting changed while the run plays first acts at a tick boundary, and the
boundaries are `multiplier × 0.1` s of simulated time apart. The same slider
moves made at two rates therefore land at two different simulated instants
and produce two different runs — not because the arithmetic differed, but
because the inputs did. § "Supported simulation step" carries the grid per
rate, what one step of it costs a displayed compartment, and the
pause-change-resume route that is exact at every rate.

The third is human factors, and it is why the rate is a required displayed
output rather than a preference. A rate is a **mode**, and a clock advancing
at sixty times real time beside numbers that look like a live case is
misreadable at a glance. So the rate must be shown wherever simulated time
is shown, and at every rate including real time — an absent label at 1x
would make the label's *presence* the signal, which is a convention a reader
has to have been taught rather than one they can read. What the rate must
not do is imply anything about the model: it is a statement about how fast
the interface is playing recorded steps, never about the patient, and it is
not a second reading of the clock it sits beside.

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
- discard a run holding recorded state without stating what will be lost and
  obtaining confirmation, as "Agent-change behavior" requires; or
- display a concentration at a finer resolution than "Displayed precision"
  justifies, or render a value the model does not resolve as though it were
  a value the model asserts; or
- predict when the simulated patient would wake, or display a
  time-to-awakening figure of any kind. The MAC-awake reference is a
  labelled population band precisely because a per-patient prediction is a
  claim this model does not support, and a disclaimer beside such a number
  would not undo it: the number would be acted on and the disclaimer would
  not.

The controller exposes immutable snapshots, and immutable windows onto the
recorded run, rather than mutable compartment objects.

## Minimum displayed outputs

The interface must show:

- simulated time;
- the rate simulated time is advancing at, as a multiple of real time, drawn
  wherever simulated time is drawn and at every rate including real time. See
  "Interface boundary" for what the rate is and is not a statement about;
- how much simulated time the chart is showing, and whether that width was
  chosen or fits the whole run so far. See "The chart's time base";
- run state, with running, paused, and halted-by-failure distinguishable
  from one another;
- why a run halted, whenever one has;
- which agent is running;
- delivered concentration of that agent;
- circuit or inspired concentration;
- alveolar or end-tidal-equivalent concentration;
- mixed-venous concentration;
- vessel-rich concentration;
- muscle concentration;
- fat concentration;
- cumulative delivered amount;
- cumulative exhausted amount;
- total stored amount;
- mass-balance residual or status; and
- every concentration above, and the delivered concentration, additionally as
  a multiple of the running agent's 1 MAC, with that agent's 1 MAC in percent
  stated on the display. See "MAC multiples as a display unit" for what the
  multiple asserts and for why both units are shown rather than selected; and
- the running agent's population MAC-awake on the chart, as a band labelled
  with the fraction and the divisor it was drawn from and with the trace it is
  to be read against, alongside that agent's nominal 1 MAC as a visually
  distinct line. See "MAC-awake as a chart reference" for what the band
  asserts, what it does not, and why no time-to-wake-up figure is displayed
  anywhere in the interface; and
- every setting changed during the current run, each with the simulated time
  it took effect, the control it changed and the values it moved between, and
  marked on the chart at that time. See "The control-input timeline"; and
- $`F_A/F_I`$ over the run, on a dimensionless axis of its own, labelled as a
  ratio against the modelled inspired concentration rather than against the
  vaporizer dial, carrying the control marks above, ruled at the equilibrium
  the curve approaches, and stating where it is not defined. See "F_A/F_I as a displayed ratio" for the domain it is drawn over
  and for what the curve does and does not assert.

The six compartment concentrations above are requirements on the **numeric
readouts**, not on the chart. The chart's compartment traces are the reader's
to show and hide (see "Interface boundary"), and a required value must not
leave the display with the curve that draws it. The chart entries in this list
— the MAC-awake band, the 1 MAC line, the control marks, and $`F_A/F_I`$ — are
requirements on the chart itself and are not selectable. The time base is the
one chart entry above that the reader does choose, and what this list requires
of it is that the width in force is stated, never that any particular width is
in force.

### What this list requires once the layout is the reader's

This list is written against one fixed layout, and `ROADMAP.md`
planned-milestone item 34 makes the interface's areas the reader's to add,
resize and remove. The two meet at the paragraph above: hiding a compartment
trace is safe *because* the value stays in the numeric readouts, so a layout
that can remove the readouts removes the floor that sentence stands on, and
every show/hide affordance this document permits becomes unsafe at once. The
failure is silent - the chart behaves exactly as documented while the display
no longer meets this list.

So the list divides in three, by what a reader can misread a value without
rather than by how the interface happens to be arranged today.

**Unconditional - the values that no workspace may remove and nothing may
cover.** The set is stated as a *test*, not as a list, and the test is: a value
is unconditional when a reader could misread the run's other displayed numbers
without it. Applying that test gives two tiers.

**Invariant, whatever is being simulated.** Simulated time; the rate it is
advancing at; run state; why a run halted, when one has; what is being
administered; and, once more than one top-level window can exist, the name of
the run the window is showing - see "What a second top-level window owes"
below, which is where that last one comes from and why this tier and the next
are allocated to windows differently. None of these depends on the substance or the model: a
concentration with no time, no run state and no named drug is the correct
number under the wrong patient, which this document treats as a display failure
rather than a missing convenience.

**Instantiated per modelled substance, and the current instance is not the
rule** (project owner, 2026-09-16). For the inhaled-agent model this document
specifies, the test selects the delivered concentration and the six compartment
concentrations, in both units, with that agent's 1 MAC in percent stated. **That
instance holds only while an inhaled agent is what the run models.** A run that
administers no volatile agent - the intravenous models of `ROADMAP.md`
planned-milestone item 13, or any later substance - owes no vaporizer dial, no
circuit concentration and no MAC multiple, because there is no such quantity to
misread. It owes its own instance of the same test instead, named where that
substance's model is specified.

Writing today's instance as the permanent list is a specific error this document
has already made once and is guarding against here: a rule that is true of the
model currently implemented, recorded as a rule about the application. The test
above is what generalises; the seven concentrations are what it currently
returns.

**Reachable rather than simultaneously visible.** The agent accounting -
cumulative delivered, cumulative exhausted, total stored, and the mass-balance
residual with its absolute error. These state whether the *model* is conserving
mass. They are not values a reader titrates against, and no clinical reading is
made wrong by their absence from a particular workspace, so a layout may leave
them out. They must stay reachable in every layout, and must not be removable
from the application.

**Conditional. These bind a surface only when that surface is shown.** A
concentration chart carries the MAC-awake band, the 1 MAC line, the control
marks, and the statement of how much simulated time it is showing and whether
that width was chosen or fits the run. An $`F_A/F_I`$ plot carries its
equilibrium rule and states where it is not defined. A reference exists so that
a *trace* is not read without its clinical anchor, so where no trace is drawn
there is nothing to anchor and nothing is lost by the surface's absence. What
must never happen is the surface without its references, which is what these
entries have always been about.

**The control-input timeline splits the same way.** The record itself - every
setting changed during the run, with the simulated time it took effect, the
control it changed and the values it moved between - is unconditional. Its
**marks on the chart** are conditional on a chart being shown: the list carries
the facts, the marks carry the reading against the curve, and that reading
exists only where a curve does.

**The rule all three rest on is about occlusion, not about window types.** No
value this list requires may be covered while the application still believes it
is showing it. That one sentence binds a panel drawn over the dashboard, a
second top-level window dragged over another window's invariant region or over
the main window's per-substance readouts, and any later floating mechanism,
without being re-argued for each. It is a property of the display rather than
of a window type, which is why it is stated once and here.

**What "the application believes" is bounded by what it can observe, and the
boundary is stated rather than implied** (2026-09-16). The rule binds the
application's *own* windows and panels - which it creates, positions and can
interrogate - and it makes no claim about a window belonging to another
application, or to the operating system, drawn on top of one of ours. That is
not a loophole being reserved; it is the limit of what any application can
enforce, and saying so is what stops a later reader taking the sentence above
for a guarantee against every way a value can be hidden. The toolkit's own
answer is narrower than it first appears and was measured rather than assumed
(PySide6 6.11.2 / Qt 6.11.2, 2026-09-16): `QWidget.isVisible()` is documented
to stay true for a widget "obscured by other windows on the screen", so it
reports the application's own show/hide bookkeeping and never occlusion;
`QWindow.visibility()` reports which of Hidden, Windowed, Minimized, Maximized
or FullScreen a window occupies, which catches a minimized or hidden window and
nothing else. The one occlusion-adjacent signal, `QWindow.isExposed()`, is
documented only as something that *might* change when a window is "made totally
obscured by another window", and the platform plugins disagree about it: the
macOS plugin drives it from `NSWindow.occlusionState` while the Windows plugin
deliberately keeps it true under occlusion for compatibility. So it is not a
signal a safety rule may rest on, and this document does not rest one on it.
What the application must do is the reachable half: never go on *asserting*
that it is showing a value whose own window it can see is minimized or hidden.

**Guaranteed structurally, not by validating a saved layout.** Each top-level
window's unconditional region sits outside *that window's* area system, so no
split, join, close or workspace switch reaches it and no saved layout has to be
checked against this list to be safe. Closing a window is on that list too, and
is the one operation the area system does not own: the main window is refused
closure while any other is open, which is what keeps the per-substance tier from
being closed out from under a reader. Validating each workspace and refusing the ones that fail is
the fallback for anything that cannot live in that region; it warns after the
fact where the structure prevents, which is the weaker of the two and is why it
is the fallback. Blender is the model for the *structure* - a region outside
the area system - and explicitly not for its persistence. Its Topbar and Status
Bar sit outside the area system as this region does, but neither is
unconditionally present: *Focus Mode* (View -> Area -> Focus Mode,
Ctrl-Alt-Spacebar) hides the Topbar, the Status Bar and the editor's secondary
regions together, for maximum screen space (Blender Manual, "Interface ->
Window System -> Areas", read at the source 2026-09-16). That is the right
trade for a 3D application and the wrong one here, because Blender has no class
of value whose absence is a safety failure and this application does. Take the
structure; refuse the escape hatch, and say so where a reader would otherwise
assume the whole precedent was copied.

**What a second top-level window owes, and it is not the whole set** (project
owner, 2026-09-16, ratified - a recommendation put to them and agreed, chosen
over the two live readings `PL-W54S` had written, and reopenable on ordinary
evidence per `CLAUDE.md`; the occlusion rule above is not, being the safety
floor rather than the arrangement). The guarantee above is stated against
the area system's own operations and stops at the frame of the window carrying
the region. `ROADMAP.md` item 34 builds break-out - an area taken into its own
top-level window, itself a full window with its own areas - in v0.7.0, and the
region v0.6.0 builds has to be the right shape for it on the first attempt.
`PL-WLWY` wrote three candidate readings of what such a window owes and closed
without choosing between them. The answer is a fourth, and it splits the
obligation the way this section has already split the list, because **the two
tiers are unconditional for different reasons and those reasons travel
differently**:

- **Every top-level window the application owns carries the invariant tier** -
  simulated time, the rate it is advancing at, run state, why a run halted when
  one has, and what is being administered - **together with the name of the run
  that window is showing**, in a region outside *that* window's area system.
  The tier's own justification above is that "a concentration with no time, no
  run state and no named drug is the correct number under the wrong patient",
  and that is a property of any surface displaying a concentration rather than
  of the display taken as a whole. So it follows the concentration into
  whatever window the concentration goes. It is five values and a name, small
  enough that a window holding one chart carries it without the squeeze
  § "Diverged, and each divergence has a specific cause" of
  `docs/interface-provenance.md` refuses.
- **The per-substance tier lives once, in the main window**, which **cannot be
  closed while any other top-level window is open**; closing it closes them.
  Its justification is the other one - a reader could misread the run's *other*
  displayed numbers without it - which is a statement about the display taken as
  a whole rather than about any one surface.
- **The accounting tier is unchanged**, being already an obligation on the
  application rather than on any layout or window.

**Why the other two readings were refused**, recorded so they are not
re-proposed. *Every window carries the whole region* is not merely the stricter
option: a broken-out window is typically small - one chart on a second screen -
and forcing seven concentrations in two units into it either dominates the
window, which defeats break-out, or is squeezed, which is the failure the
never-hidden divergence exists to refuse. *The main window carries everything
and a broken-out window names only its run* leaves a window drawing compartment
traces with no time, no rate, no run state and no agent, and rests the guarantee
on a window the reader may not be able to see - which is the property `PL-WLWY`
used to rule out the reading that the contract binds the application rather than
the window. A guarantee resting on where the window manager has put things is
the same guarantee in both cases.

**This is the display side of an evidenced failure mode, not a house
preference.** That correct data read in the wrong context is a distinct class of
clinical-information-system error is established: Ash, Berg and Coiera describe
the "silent errors" such systems foster rather than prevent (*J Am Med Inform
Assoc* 2004;11(2):104-112, doi:10.1197/jamia.M1471), and Magrabi and colleagues'
classification of 42,616 reported incidents makes information *output* a
category in its own right at 20% of computer-related problems (*J Am Med Inform
Assoc* 2010;17(6):663-670, doi:10.1136/jamia.2009.002444). The closest measured
analogue of the rule above is the wrong-patient order: restoring one piece of
patient context to the display banner - a photograph - was associated with lower
wrong-patient order entry across 2,558,746 orders (adjusted OR 0.57, 95% CI
0.52-0.61; Salmasian et al., *JAMA Netw Open* 2020;3(11):e2019652,
doi:10.1001/jamanetworkopen.2020.19652), which is the invariant tier's argument
in a different clinical setting: context carried in the frame of the view rather
than assumed from elsewhere on the screen. Two things are deliberately *not*
claimed here, having been checked and not found: that duplicating a live
readout across windows is itself a named hazard - the one randomised trial of
concurrently open records found no difference in wrong-patient errors (Adelman
et al., *JAMA* 2019;321(18):1780-1787, doi:10.1001/jama.2019.3698) - and that
tiling is a published preference over overlapping windows, which the only
controlled comparison does not support. The tiling argument stands on this
project's own occlusion reasoning, as item 34 already records.

**A stepping stone, and recorded as one** (project owner, 2026-09-15). This is
deliberately the rigid version - a fixed unconditional region and a conditional
remainder - chosen to be correct while the layout apparatus is built rather
than to be its final shape: "ultimately, will be able to resize everything
however ... I'm ok with starting with a relatively more rigid structure as a
stepping stone". So the particular split of this list is expected to be
revisited as that apparatus matures. What must survive any revision is the
occlusion rule above, which is the safety floor rather than the arrangement.

**While two runs are shown, every readout names the run it describes, and all
six compartments keep theirs** (`PL-1XPX`). This list is a requirement on the
numeric readouts and does not become a smaller one in compare mode. The rule in
the paragraph above — that a required value must not leave the display with the
curve that draws it — binds the chart's two-compartment cap (`ROADMAP.md`
v0.5.0, `PL-HLD5`) exactly as it binds a reader hiding a trace: the cap is a
colour-capacity limit on the chart, not a reduction of what the display owes.
So while two runs are compared the chart may draw two compartments and the
readouts still carry six, for both runs, and the readouts are what keep the
other four on the display.

**The run is named in text, not carried by colour or by position.** Colour is
spent on the compartment and cannot take a second meaning either side of a mode
change — "The six compartment traces" measures the worst trace-against-trace
pair at 1.01:1 against a 3:1 requirement, which is why `PL-HLD5` put the run on
line width rather than colour. Text has no width analogue, and position alone
fails the reader who has looked away and back, which is the stale-context
failure this requirement exists for. A concentration that does not say which
management produced it is the correct number under the wrong patient context.

**Both runs are shown, rather than the selected one with the selection stated.**
Showing one would make the readout block a mode, and a stale selection there has
no visual signature at all: the block looks identical whichever run is selected,
so a reader who has forgotten reads one management's number as the other's.
Stating the selection warns after the fact where showing both prevents. Pairing
the two values under one compartment label is what keeps that from doubling the
block's height: it grows in width instead, which preserves the one-row
comparative reading this document requires the resolution to be uniform for —
a reader seeing the circuit lead the alveoli lead the tissues. What that costs
is width at narrow windows, which `PL-3355` bounds: a readout panel reserves
the width of the widest value it can show, so a value is never wrapped away
from its unit at any width the row is laid out at.

**No difference readout is required, and none may be added without a stated
sign convention.** The arithmetic difference of two alveolar fractions is not a
quantity with a conventional clinical reading — depth is reasoned about in MAC
multiples and in time-to-target — so displaying one implies a standard meaning
it does not have, which "Displayed precision" refuses on interpretability
grounds. The chart already carries the comparison continuously, in the axis the
reader is looking at.

Arterial concentration is deliberately **not** in this list. Arterial blood is
flow-limited in this model and holds no independent state: $`F_a \equiv F_A`$
(see "Model boundary"). A separate arterial readout would therefore display
the alveolar number a second time under a different name, which would present
a definitional identity as though it were an independently modeled quantity.
Earlier revisions of this document required an arterial readout; that
requirement predates the arterial simplification being made explicit and is
withdrawn rather than being satisfied by a duplicate label.

Showing which agent is running is a required output, not a convenience: a
correct concentration attributed to the wrong agent is a presentation
failure, and the same number means a different clinical depth for each agent
(2% is about 1 MAC of sevoflurane but roughly a third of a MAC of
desflurane).
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- derived: a third of a MAC of desflurane from data/agents/desflurane.json mac_percent = 6 -->

The agent selector and header reinforce that written name with the
agent-identification color specified by ISO 5360:2016 Table 2 ("Dimensions and
colours of agent-specific bottle collars and connectors"): yellow for
sevoflurane, purple for isoflurane, and blue for desflurane. That table's
footnote b is the reason the color appears here at all — "if a colour is used
on a vaporizer, bottle, or package label to facilitate correct identification,
it is important that only the colour for the appropriate anaesthetic agent be
used" — so displaying a color obligates displaying the correct one. Color is a
redundant cue, never the sole identifier; the agent name remains visible and
the foreground/background pairs must meet WCAG 2.2 AA contrast. The cited
standard references, screen-color approximations, and accessible foregrounds
live together in `app/theme.py` so the mapping can be audited as one unit.

The displayed fills are two approximations removed from the standard's own
value, and this must not be read as an exact reproduction. Table 2 footnote c
states that "Munsell colour is the original" and that the other color systems
it lists "show the nearest available colour sample"; the Pantone reference is
therefore already ISO's approximation, and the sRGB `fill` approximates the
Pantone in turn. Converting each Munsell original to sRGB independently (via
Illuminant C, chromatically adapted to D65) gives the deviation of each
displayed fill from the standard's original value:

| Agent | ISO Munsell original | Munsell as sRGB | Displayed fill | ΔE00 |
| --- | --- | --- | --- | --- |
| Sevoflurane | 6.25Y 8.5/12 | `#F2D600` | `#FEDB00` | 2.1 |
| Isoflurane | 7.5P 4/12 | `#8D4192` | `#981D97` | 5.7 |
| Desflurane | 10B 4/10 | `#0069A0` | `#00629B` | 2.6 |

The sevoflurane and desflurane originals fall outside the sRGB gamut, so no
display can reproduce them exactly and some deviation is unavoidable rather
than a choice. Desflurane's *dimensions* are excluded from ISO 5360 by its
Scope, and Table 2 records "N.S." for its collar angle; its *colour* is
specified in that same row and is what this application uses.

A known limitation of the standard, reproduced here deliberately: isoflurane's
purple and desflurane's blue are not distinguishable by a user with a color
vision deficiency. They differ by only 1.09 in luminance for normal color
vision — they are separated by hue alone — and simulating the three
dichromacies removes the hue without supplying the luminance: 1.48 for
protanopia, 1.06 for deuteranopia, 1.11 for tritanopia. Measured by
`tools/contrast_check.py` with the Brettel 1997 projection recorded under "The
six compartment traces" below, and pinned by `tests/unit/test_contrast_check.py`
so this paragraph cannot go stale behind a color edit. Choosing more separable colors would break the correspondence to real
vaporizers and is therefore the worse option; the mitigation is that the agent
name is always rendered alongside the color, which `tests/unit/` asserts for
both the dropdown options and the header badge. Color must never be the only
thing distinguishing two agents in this interface.

Distinguishing a halted run from a paused one is required for the same
reason. Both stop the numbers advancing, and under "Step atomicity" both
leave state the reader can trust — but a pause is a run that will continue
when the reader asks, and a halt is a run that cannot. A halted run displayed
as "Paused" therefore offers a Start control that will fail on its first
tick, and presents a stopped trajectory as one still in progress: the
mode-confusion failure this specification's interface rules exist to prevent.
A display that is merely frozen, with no state change at all, is worse still.

The phrase “end-tidal-equivalent” must not imply that airway sampling dynamics, dead space, or capnography are modeled.

**The alert colour deliberately does not follow the medical alarm-colour
convention** (project owner, 2026-09-14). The agent colours above are adopted
*because* a standard obligates them; this is the opposite decision about a
different colour, and the two are recorded together so the difference is
visible rather than inferred.

IEC 60601-1-8 governs *visual alarm signals* — indicators encoding priority by
colour together with a flash rate. This interface has none. Every use of
`WARNING` in `app/theme.py` is bold coloured text: the run-status word, a
transient notice line, the agent-accounting status word, the permanent
educational disclaimer, and the case-discard dialog. There is no indicator
lamp, no filled banner, no flashing element and no priority tier, so there is
nothing for the convention to bind.

The disclaimer is what settles it, and it points away from adoption rather than
toward it. `WARNING` is the colour of a line that is on screen *always*, and a
monitor's alarm colours carry meaning precisely because they are absent until
something is wrong. A permanent element painted in a high- or medium-priority
alarm colour would teach the opposite of the convention it borrowed. The
divergence is also chosen for its own sake: a teaching tool that looks
unmistakably unlike a monitor cannot be mistaken for one, which is the reading
this project's disclaimers already take.

The interface runs that as a signal economy one level down. The
supported-run-length boundary is `MUTED`, not `WARNING`, because colouring a
correct model's declared boundary as a fault teaches a reader to distrust a
number that is sound, and would spend the one signal this interface has.

Two things bind regardless, and neither is in question: any colour chosen still
has to clear the contrast target `tools/contrast_check.py` enforces, and the
ISO 5360 agent colours are untouched — they identify an agent and carry no
urgency, which is why Table 2 footnote b obligates them and nothing obligates
this one. **The decision binds the Qt port as much as the current interface**: the
port redecides the palette and is the moment an indicator-shaped surface could
first appear, and it must not arrive carrying a monitor's priority palette.

*The priority-to-colour mapping itself is deliberately not recorded here.* It
could not be established from a primary source, and the secondary sources
disagree — cyan, blue, and "green or blue" from three independent reports of
the low-priority colour. Writing down a value that is wrong at least twice over
would be worse than recording none, and the decision above does not depend on
it.

### MAC multiples as a display unit

Every compartment is displayed twice: as a percent of one atmosphere, and as
a multiple of the running agent's 1 MAC. Both are shown at once, on every
compartment, on the delivered-agent control, and on the chart, which carries a
percent axis on the left and a MAC axis on the right. Each axis states its own
unit in its title — `% of 1 atm` and `×MAC` — rather than in a caption above
the plot, which is where both stood until PL-6580. `% of 1 atm` and not
`vol %`: a volumes percent is a gas-phase volume fraction, which the circuit
and alveolar compartments have and the mixed-venous, vessel-rich, muscle and
fat compartments do not, holding instead a partial pressure that convention
quotes as a percentage of an atmosphere. An axis titling all six as a volume
fraction would assert of four of them a quantity they do not have.

**Why the second unit exists.** A percent axis silently changes meaning when
the agent changes. 2% is 1 MAC of sevoflurane and about a third of a MAC of
desflurane, so two runs plotted in percent are two different clinical
situations drawn at the same height, and a learner comparing a desflurane
wash-in to a sevoflurane one in percent is comparing nothing. MAC multiples
are the unit that survives the agent change, and the unit clinicians reason
in.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- derived: a third of a MAC of desflurane from data/agents/desflurane.json mac_percent = 6 -->

**What a MAC multiple on a compartment asserts.** This is the whole difficulty
of the unit, and it is not the arithmetic. MAC is defined for the *alveolar*
(end-tidal) concentration at one atmosphere in a nominal 40-year-old, as the
population ED50 for immobility to a standardized surgical stimulus. So:

- On the **alveolar** compartment, a MAC multiple is the conventional
  reading, subject to every limitation of the divisor recorded below.
- On the **circuit, mixed-venous, vessel-rich, muscle and fat** compartments
  it means only *this compartment's partial pressure equals N times the
  alveolar partial pressure that would be 1 MAC*. It is a partial-pressure
  ratio. It is **not** a statement that the patient is at N MAC of anesthetic
  depth, and the two read identically on a label unless the label says which.

The ratio is never presented as a depth, and the notation is what carries
that on the display: the unit is written `×MAC` on every readout and on
the chart's right-hand axis, for the reason given below. Until PL-6580 the
distinction was also stated in prose beside the chart, in the terms above.
That paragraph was removed with the rest of the panel's explanatory copy:
the reader of this display is an anesthesia provider, for whom what MAC is
defined against is fundamental knowledge rather than something to be taught
at the top of a chart, and a dozen lines of text between the reader and the
plot cost more than they bought. This section is now the only full statement
of the convention, which is why it is stated here at length.

Three further limitations hold for every compartment including the alveolar
one, and none of them is modeled here: MAC falls about 6% per decade of age (Mapleson 1996; cited in each
agent's `sources`) and this model's reference adult has no age parameter;
MAC multiples of co-administered agents are additive and this model runs one
agent at a time; and MAC is modified by opioids, temperature, and patient
factors none of which are represented.

**The unit is written `×MAC`, not `MAC`.** "0.80 MAC" is read as a depth;
"0.80 ×MAC" is read as what the number is. The multiplication sign is doing
safety work rather than typographic work, and it is why the readouts carry it.
The chart's right-hand axis is titled `×MAC` for the same reason and in the
same words: its ticks read bare numbers — `0.5`, `1.0` — so the title is the
only thing on the plot that says what they are, and it labels six traces at
once, five of which are not the compartment MAC is defined for. One unit, one
token, everywhere it appears.

**The divisor is displayed.** A MAC multiple has exactly one free parameter,
and `CLAUDE.md` requires a clinically meaningful displayed value to be
traceable to the transformation that produced it. The interface therefore
states the running agent's 1 MAC in percent beside the chart — "1 MAC
sevoflurane = 2.0%" — so a reader who disagrees with the divisor can see that
they disagree, and can convert back to the percent the model actually
computes.

**Nothing in `core/` computes a MAC multiple.** The transformation lives in
`app/formatting.py` and takes the divisor as an argument; the divisor reaches
it through `SimulationSnapshot.agent_mac_percent`, beside the concentrations
it scales and the agent it belongs to, so a frame cannot pair one agent's
compartment with another agent's MAC. The chart's plotted points remain in
percent — the MAC axis relabels that same coordinate rather than carrying a
second series, so the two axes cannot come to disagree about where a trace
is. Both units are always shown rather than selected, because a unit selector
would make the axis unit a mode, and a chart read under the wrong assumed
unit is a misreading no disclaimer catches.

**The chart's vertical range is denominated in MAC, and fixed.** The axis
runs from 0 to **3 ×MAC** of the running agent, ruled every half MAC, for
every agent. It is therefore one ruler: the same case drawn under two agents
is drawn at the same height, which is the property the second unit exists to
give and which the axis previously took away. Until PL-CC23 the top was the
agent's vaporizer dial maximum — 3.00 ×MAC of desflurane, 4.00 of
sevoflurane, 4.17 of isoflurane — so a learner comparing a desflurane wash-in
to a sevoflurane one was comparing shapes silently rescaled by 1.39×, and the
horizontal rules were a fixed 2 percent, which is every 0.33 ×MAC under
desflurane and every 1.67 ×MAC under isoflurane.
<!-- derived: 3.00 from data/agents/desflurane.json max_delivered_concentration_percent = 18, mac_percent = 6 -->
<!-- derived: 4.00 from data/agents/sevoflurane.json max_delivered_concentration_percent = 8, mac_percent = 2 -->
<!-- derived: 4.17 from data/agents/isoflurane.json max_delivered_concentration_percent = 5, mac_percent = 1.2 -->
<!-- derived: 1.39 from data/agents/isoflurane.json max_delivered_concentration_percent = 5, mac_percent = 1.2 -->
<!-- derived: 1.39 from data/agents/desflurane.json max_delivered_concentration_percent = 18, mac_percent = 6 -->
<!-- derived: 0.33 from data/agents/desflurane.json mac_percent = 6 -->
<!-- derived: 1.67 from data/agents/isoflurane.json mac_percent = 1.2 -->

**Why 3, and why fixed.** Three is exactly desflurane's dial maximum divided
by its 1 MAC, so the shared ceiling is anchored to a real device limit rather
than to a preference, and the agent whose vaporizer is most limited gets no
dead band above its reachable range. It puts the 1 MAC line at a third of the
plot height — inside the plot rather than on its frame, which a ceiling of 2
could not do — and leaves the 2-3× MAC range that overpressure induction
works in on the plot. Fixed rather than fitted for the reason "Why the axis is
fixed rather than fitted" gives for the wash-in plot below: an axis that grew
to fit an excursion would redraw a rising curve at a smaller height partway
through a lesson, and a reader would attribute that shape change to the model.
It is fixed across the session rather than only within a run, so two
consecutive runs are comparable too.

**A trace above the ceiling is named, not left to look like a plateau.** A
fixed ceiling can be exceeded where a dial-maximum one could not, and the
setting that exceeds it is in common use rather than an edge case: sevoflurane's
8% dial is 4.00 ×MAC and is a common inhalational-induction setting. A
clipped trace draws as a horizontal line at the top of the frame, and a
horizontal line is what a plateau looks like — so a reader would conclude the
concentration stopped rising at 3 ×MAC when the model says it did not, which
is a wrong clinical reading of a correct model. The chart therefore names the
compartments that are above the ceiling and says that the readouts, which are
not clipped, hold their values. The comparison is against the displayed
resolution rather than against zero, so a trace sitting exactly at the
ceiling is not reported: isoflurane's ceiling is 3 × 1.2, which in binary
floating point is 3.5999999999999996.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- derived: 4.00 from data/agents/sevoflurane.json max_delivered_concentration_percent = 8, mac_percent = 2 -->

**What the divisor is worth.** `mac_percent` is a tier-3 value, and this
section is where that matters most: it is now the divisor of every MAC number
on the display rather than only the vaporizer's starting position. "Delivery-
limit and MAC parameters" carries the provenance and the size of the gap
against the primary literature, including the consequence for the
cross-agent comparison this unit exists to support.

### The chart's time base

**What it is.** How much simulated time the chart shows at once. The reader
either picks a width from a fixed ladder or leaves the default, which fits the
whole run so far. The horizontal axis is simulated time under both, and the
time base decides only how much of it is on the plot and how finely that span
is ruled. `app/chart_time_base.py` is where this section terminates: it is
arithmetic over durations that reads no simulation state and imports no toolkit,
so the widths and the rule this section reasons about can be read, cited and
tested without loading the interface. The section above governs the vertical
axis; this one governs the horizontal.

**Why a case needs one.** The compartments this model exists to teach are
slow, and the moment a learner is most likely to be watching is not. Muscle's
time constant is about 135 min for sevoflurane at the reference settings and
fat's about 42 h, while induction is minutes long. A five-minute window hides
everything slower than the vessel-rich group; a twelve-hour one puts a
five-minute induction in the leftmost 0.7% of the plot. The playback rate
is what makes a long case watchable in a sitting, and this is what makes it
readable — the two are separate controls because they answer separate
questions, how fast the run advances and how much of it is in view.

**A time base is a view control and reaches no model state.** Choosing one
changes which part of the run is drawn, and at what column spacing, and
nothing else: no step is resized, nothing in the run definition is added,
discarded or altered, and the run is not re-stepped. "The reproducibility
guarantee" is therefore untouched by it, and the same case watched at fifteen
minutes and at twelve hours is the same run, keyframe for keyframe. Every
point drawn at any width is still a state the run reached at the instant it
is drawn at, evaluated from the run definition under the constraint
"Interface boundary" places on a plotted trace, so a wider window is a
coarser *grid* of exact states and never a resampling, an interpolation or a
stored image zoomed into.

**Why a fixed ladder rather than a free zoom.** The selected width is the
width of the window at every point of every run, so seconds per pixel is a
property of the reader's choice rather than of how long the run has been
going. A trace's slope on the plot is then a fixed multiple of its rate, and
stays comparable between two moments of one run and between two runs. A window
that grew continuously with the run would rescale every slope while the
underlying rates did not — a misleading visual encoding of rate of rise, which
is the one quantity uptake and distribution are taught by, and the same
argument the fixed vertical range rests on. Discrete steps also make one step a
meaningful change rather than a nudge: each rung is at least half again as wide
as the one below it.

**The ruling derives from the width.** Each rung carries the interval its
gridlines and labels fall at, and every rung is ruled into four to six
intervals — the range that reads as a grid rather than as either a bare axis
or a hatch. A single fixed interval cannot do that across the ladder: the 60 s
interval this replaced would rule a twelve-hour axis into 720 lines and a solid
block. Ticks stand at multiples of the interval measured from the case's zero
rather than from the window's left edge, so a gridline holds the same
simulated time as the window slides underneath it — and holds it for every run
on the axis, since a branch is on the same clock as the trunk it came from.

**Fitting always fits.** It is the default mode, and past the widest declared
rung the ladder continues by doubling rather than holding at the widest and
showing part of the case. A mode named for showing the whole run that silently
showed the most recent twelve hours of a fourteen-hour one would assert
something false about what the reader is looking at, which is why the honesty
of the name is a requirement on the mode rather than a property of the ladder's
reach. The ladder also carries rungs below the narrowest width the selector
offers, reachable by fitting and not by choosing: fitting has to answer at ten
seconds as well as at ten hours, and choosing a span with nothing in it is not
a reading anyone wants.

**Every axis label carries its own unit, and the width in force is stated.** A
tick reads `0`, `45s`, `3m`, `1m30s` or `1h30m` rather than a bare number under
a captioned unit. The axis spans anything from a minute to half a day, so a
bare `12` would mean twelve minutes on one time base and twelve hours on
another while looking identical on both, and a reader who missed the caption
would have nothing in the label to correct them. Beside the plot the chart
names the width in words and says whether it is a width the reader chose or the
whole run so far, because those are different claims about what is on screen.
The time base is a mode in exactly the sense the playback rate is, and it is
displayed for the same reason: a span nobody can see is one a reader supplies
their own assumption for.

### MAC-awake as a chart reference

The compartment chart carries two horizontal clinical references: a **band**
at the running agent's population MAC-awake, and a **line** at its nominal
1 MAC. Neither is a modeled quantity. Both are published constants drawn at a
height the chart's own percent axis gives meaning to, and `core/` computes
neither — no governing equation reads MAC-awake, exactly as none reads
`mac_percent`.

**Why two rather than one.** Chortkoff et al. state that "along with
pharmacokinetics, the ratio of the awakening concentration to the
anesthetizing concentration (MAC-awake/MAC) determines time to awakening".
Drawing both makes that ratio the visible gap between them, so the chart
shows the *decrement required for arousal* rather than only the endpoint —
which is what makes a twenty-minute case and a three-hour one answerable side
by side, and is the context-sensitive emergence lesson stated geometrically.

**The mark type carries the distinction, not the colour.** The two references
differ in epistemic status and the marks say so: MAC-awake is a measured
population value with real spread, so it is a band; 1 MAC is a definitional
anchor rather than a distribution of the same kind, so it is a line.
Band-versus-line survives greyscale and every colour-vision deficiency, which
"Color contrast" below requires of any encoding carrying meaning, and it is a
stronger separation than any colour pair. Both are drawn in the interface's
own ink and label colours rather than in a seventh and eighth hue, so neither
reads as another compartment.

**The band's geometry, and why it is two strokes rather than a thicker mark.**
The band is drawn as a stroke on each of its two boundaries with a light fill
between them, and both strokes sit on the published values, so the drawn
extent is the data extent exactly. Nothing pads it outward. A band drawn
thicker than one standard deviation would assert a wider population spread
than the sources support — a claim about the evidence rather than a styling
choice — so a minimum drawn height is specifically excluded, whatever it would
do for legibility.

The second stroke is load-bearing because no axis range can supply the
separation. On the fixed `CHART_AXIS_TOP_MAC` range the band spans 3.33% of the
plot height for sevoflurane and 4.20% for desflurane, and no ceiling this chart
can take changes that: at 2 MAC the band is unambiguous but the 1 MAC anchor
sits at mid-plot with no room above it for the overpressure induction the chart
has to be able to show, and at 4 MAC the band is back to the 2.50% it had on
the dial-maximum axis this one replaced. A mark stroked on its upper edge only,
over an unstroked fill, is the geometry of a line with a shadow beneath it
however wide the fill is, which is what made this band read as a line and would
have flattened the band-versus-line distinction above into no distinction at
all. Two strokes with a gap between them is the geometry of an interval and
stays one at any thickness the axis leaves, so what a reader sees between the
two rules is the population spread rather than a decoration around a threshold.

<!-- derived: 3.33 percent from data/agents/sevoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- derived: 4.20 percent from data/agents/desflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.063 -->

**What the band asserts.** MAC-awake is the concentration at which half of a
population responds to verbal command. That is a *different endpoint* from
MAC, which is immobility to a standardized surgical incision, and the label
says which. The band's extent is one standard deviation either side of the
published mean, so it spans roughly the middle two thirds of a population and
not its range.

**What the band does not assert, and what the interface therefore never
shows.** It is not a prediction for the patient on the screen, and the
interface displays no time-to-wake-up figure of any kind. A readout of the
form "time to wake-up: 14 min" would read as a per-patient prediction that
this model does not support, and no surrounding disclaimer undoes that: the
number would be acted on and the disclaimer would not. A band is the strongest
claim the evidence carries, which is why it is the form the reference takes.

**Which trace the band is read against, and why that is the load-bearing
part.** The band must be read against the **vessel-rich** trace. This model
has no effect-site compartment and defines $`F_a \equiv F_A`$ (see "Model
boundary"), so the alveolar trace is the fastest curve on the chart and the
furthest from where responsiveness actually returns. Measured on a 3-hour
1 MAC sevoflurane case with the vaporizer turned off at 10 L/min, the
alveolar trace crosses the band's centre at 2.83 min and the vessel-rich
trace at 6.51 min — 2.30 times later.

<!-- derived: 2.83 min from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->

The primary literature makes this a question of *which number is correct*
rather than only of how one is read. Katoh et al. determined sevoflurane and
isoflurane MAC-awake by both a slow, equilibrated washout and a fast one, and
the two disagree: 0.34 and 0.31 of MAC by slow washout against 0.22 for both
by fast washout. The paper attributes the difference to
end-tidal-to-arterial and arterial-to-cerebral anesthetic differences — which
is precisely what this model represents as the alveolar-to-vessel-rich
difference — and measures the brain concentration directly rather than
leaving it to inference: cerebral concentration at first eye opening during
fast washout was 0.34 of MAC for sevoflurane and 0.30 for isoflurane,
"nearly equal to MAC-Awake obtained by slow alveolar washout". The stored
values are therefore the slow-washout ones, and the trace they belong against
is the vessel-rich one.

<!-- provenance: data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34 -->
<!-- provenance: data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31 -->

**Every way of getting this wrong runs in the same direction, and it is the
consequential one.** Concentration falls during emergence, so a trace crosses
a higher reference sooner and a faster-falling trace crosses any reference
sooner. Three distinct errors therefore all shorten the apparent time to
awakening — reading the band against the alveolar trace instead of the
vessel-rich one, drawing the slow-washout value against a fast-washout
alveolar trace where 0.22 would be the matching figure, and the denominator
mistake below. A learner who takes any of them away concludes that emergence
is faster than this model says, and carries into practice the belief that a
patient is more awake than they are. That is why the reference is specified
here rather than left to the chart.

**The value is stored as a fraction of MAC, never as a percent of one
atmosphere, and that is a safety decision rather than a schema preference.**
Each source expresses MAC-awake as a ratio to MAC — Katoh explicitly "as a
ratio to age-adjusted MAC" — and a published *percent* is anchored to
whichever MAC its own population was measured against. Desflurane is the
worked example: Chortkoff's MAC-awake of 2.60% is 36% of a MAC of about
7.25%, which is Rampil's 18-30 year figure, while this project stores
Rampil's 31-65 year figure of 6.0%. Dividing the absolute percent by the
stored MAC would give 0.433 rather than the published 0.36 — 20% high, and
therefore a band drawn 20% too high and crossed too soon. Storing the
fraction removes the trap outright, and stays correct if `mac_percent` is
ever changed or made age-aware.

<!-- derived: 0.433 from data/agents/desflurane.json mac_percent = 6, mac_awake.fraction_of_mac = 0.36 -->

Because a fraction with no stated denominator is the correct number in the
wrong context, each agent's `mac_awake.mac_reference_basis` records the MAC
its fraction was derived against, and the interface states the divisor it is
multiplied by. Applying the fraction to this project's own `mac_percent` is
what keeps the band and the axis consistent by construction, and it
corroborates independently for desflurane: 0.36 of the stored 6.0% is 2.16%,
against the 2.17% Song et al. measured in the non-jaundiced control arm of a
population that the 31-65 year divisor describes.

<!-- derived: 2.16 percent from data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36, mac_percent = 6 -->

**The 1 MAC line is the nominal value, not the dialled one.** A fixed
reference stays comparable across runs, which is what makes two cases of
different length answerable side by side; a line tracking the concentration
the learner happened to dial would only restate where the trace already
starts. It is the flat adult `mac_percent` and is labelled as a reference
adult rather than as a patient-specific value: this model has no age
parameter, while Katoh expressed MAC-awake as a ratio to age-adjusted MAC.

One consequence is expected rather than a rendering fault: on a short case
the vessel-rich trace never reaches the 1 MAC line, because it never
equilibrated. That is true of the patient and is worth teaching.

**What the references inherit, and one methodological limitation.** The
fractions are tier 1, from primary measurements in humans; `mac_percent` is
tier 3, so the *absolute height* of both references inherits every limitation
"Delivery-limit and MAC parameters" records for the divisor, and the
interface displays that divisor so a reader who disagrees with it can see
that they do. Separately, the three fractions were not determined by one
method: Katoh's slow-washout arm is *descending*, while Chortkoff and Song
both determined desflurane MAC-awake by *ascending* stepwise equilibration.
All three are equilibrated determinations rather than fast-washout ones,
which is why all three belong against the vessel-rich trace, but ascending
and descending determinations are not interchangeable and no
descending-washout desflurane MAC-awake was found. The three fractions
(0.31 isoflurane, 0.34 sevoflurane, 0.36 desflurane) sit in a narrow range,
so each agent carries its own value rather than one fraction covering all
three.

<!-- provenance: data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36 -->

### The control-input timeline

**What it is.** A record of the settings a run was given, held with the run
and cleared with it. Each entry is one change the model actually ran under:
the simulated time it took effect, which user adjustment it belongs to,
which control, the values before and after, and the unit both are in.

**Why the model needs one at all.** A curve without its inputs is not a
result anybody can check. The exercises this simulator exists to support
are all of the form "change one thing and look at what happened" —
overpressure then dial back, drop the flow, halve the cardiac output — and a
learner who cannot see where they dialled back cannot read their own
experiment. The stronger requirement is reconstruction: the recorded
timeline, re-applied to a fresh run at the recorded times, must reproduce
the run it describes. That is what makes a recorded run a result rather
than a picture of one, and it is what the design decisions below are for.

**Recorded values are the model's, not the interface's.** Each value is
read back off the compartment that holds it after the core has accepted it,
in the unit the core is set in — so the delivered dial is stored as a
fraction of one atmosphere and displayed as the percent every other
concentration on the page is displayed as, converted once at the display.
A record of what was *asked for* rather than of what took effect would
diverge from the run the first time the two differed, and the core rejects
an out-of-range setting rather than clamping it precisely so that they
cannot differ silently.

**A refused setting is not recorded**, because it never took effect. The
recording happens after the core's setter returns, so this is structural
rather than a check that could be forgotten.

**Only what the model saw is recorded.** A setting equal to the one already
in place is not a change. Neither is one superseded before the next
simulation step: only the value standing when a step runs is integrated, so
a control moved twice between two steps is one change from the first value
to the last, and one moved and moved back within a step is no change at
all. Recording the intermediate values would describe a run that did not
happen; omitting the collapse would leave the timeline a record of the
input device rather than of the simulation.

**What a displayed adjustment is, and why it is not the same object.** A
slider reports its value continuously while it is dragged, so one turn of
one control reaches the model as a run of settings — each of them a setting
the run really was computed under, and all of them one act by the person.
The record keeps every setting, because reconstruction needs them; the
display groups them into adjustments, because a reader needs the act. The
grouping is exact rather than inferred: the interface declares where an
adjustment begins, at the moment a drag starts, and every change carries
the number it was assigned. Nothing infers a gesture from the spacing of
the entries, and nothing may: a playback multiplier changes how much
simulated time one drag spans, so any threshold would group correctly at
one rate and wrongly at another. A change arriving with no adjustment
declared — a keyboard press on a slider, a programmatic call — becomes an
adjustment of its own, which is the honest reading of a discrete input.

A displayed adjustment states the interval it spans and how many settings
the model was stepped under during it. The count is displayed rather than
hidden because an adjustment made over eight settings is not the same run
as one made in a single step, even where the endpoints match.

**What it asserts, and what it does not.** That the named control moved
between the stated values over the stated simulated interval. It says
nothing about the patient. It is a record of an *input*, never of a
measurement or of a modelled quantity, which is why the chart's marks are
labelled as such and why the list beside them says so in terms: a vertical
rule on a chart of patient concentrations is otherwise an invitation to
read an event into the curves.

**Stability of the recorded identifiers.** Each control is recorded under a
fixed string chosen from the domain — `fresh_gas_flow`, `delivered`,
`alveolar_ventilation`, `cardiac_output` — rather than from whatever the
accessor that applies it is called. An identifier taken from the code would
retire the vocabulary of every already-recorded run the next time the code
was renamed. A fifth string, `circuit_volume`, was recorded here until the
circuit volume was established as a fixed model parameter rather than a
control (§ "What is not bounded this way"); retiring it cost no
already-recorded timeline, because a timeline is held in memory and cleared
with its run rather than persisted.

**Bounds are displayed, not silent.** The chart carries a fixed number of
marks and the list a fixed number of lines, so a run may record more
adjustments than either can show. What is not shown is counted on the
display. A chart that quietly stops annotating, or a list that quietly
ends, is a statement that nothing else happened.

**The record itself carries no ceiling, and that is a decision rather than
an omission.** The two bounds above are on what is *shown*. Dropping the
oldest entries would retire the beginning of a case — which is the part a
learner returns to, since "where did I dial back?" is the question this
record exists to answer — and it would bound nothing, because the run
definition of "The run is that record, and every state is derived from it"
above holds one stretch and one keyframe per accepted change and is not
bounded either. Capping the display record alone would cost the
reconstruction claim above and leave the larger structure growing.

What makes that affordable is that the record grows with time spent
*changing settings* rather than with the length of the run. Only the value
standing when a step runs is recorded, so a drag contributes at most one
entry per simulation step however fast the slider reports — and that rate
is a property of the tick rather than of simulated time, so it is the same
at every playback multiplier. Measured on 2026-09-14 under `PL-1PSX`: ten
entries per real second of continuous dragging at 1×, 5×, 20×, 60× and
300× alike, and one entry for a drag made while the run is paused. The
grouping behind the display costs 0.9 ms per frame at a thousand entries
and 8.8 ms at ten thousand, against a 200 ms frame, and is recomputed only
when the record changes; reaching the hundred thousand entries at which it
would cost half a frame takes some three hours of unbroken dragging, at
which point the record is under 9 MB.

### F_A/F_I as a displayed ratio

**What it is.** A second plot under the compartment chart, on the same time
window, drawing $`F_A/F_I`$ — the modelled alveolar fraction divided by the
modelled inspired fraction — on a dimensionless axis fixed from 0 to 1. It is
a *displayed* quantity: `core/` computes it nowhere, no governing equation
reads it, and it is no part of the run's definition. `app/wash_in.py` is
where this section terminates, the way `app/formatting.py` terminates
"Displayed precision": it holds the arithmetic, the domain, and nothing else,
and `tests/unit/test_wash_in.py` pins both.

**Why the interface owes it.** This is the curve the uptake literature is
taught from and the one every wash-in figure a reader has seen is drawn as.
It is also the quantity this model has been compared against human
measurement on — "Published wash-in and elimination validation test" is $`F_A/F_I`$ at
30 minutes for all three shipped agents — so the trace and the validation are
the same number, which
`test_the_displayed_ratio_is_the_quantity_this_file_validates` asserts rather
than leaves to inspection. Six absolute concentrations cannot be laid beside a
published figure; this can.

**The denominator is the modelled inspired concentration, not the vaporizer
dial.** The inspired fraction here is the breathing circuit's own, which is an
assumption of this circuit model rather than a general fact — see "Model
boundary". The
distinction from the dial is not pedantic: the circuit only approaches the
delivered concentration over its own time constant, so early in a run the two
differ substantially, and dividing by the dial would understate the ratio for
as long as that lasted. The interface states which one it is at the point of
display.

**The curve is the textbook wash-in curve only while the inspired
concentration is held constant.** Move the vaporizer, or the fresh gas flow,
mid-run and $`F_A/F_I`$ remains a well-defined ratio of two modelled states
but stops being a wash-in fraction of anything a reader can name. A rise
across such a change is the setting moving, not uptake slowing. The control
marks of "The control-input timeline" are drawn on this plot as well as on the
compartment chart above it, in the same pass over the same adjustments, so the
plot that would be misread is the plot that carries the annotation.

**The plotted domain, and why it has two boundaries.** A drawn column
contributes a point only where both hold:

1. $`F_I \geq 10^{-4}`$, one displayed unit of concentration. $`F_I`$ is
   exactly zero before any agent reaches the circuit — at the start of every
   run, and throughout a run whose vaporizer is never opened — so the quotient
   is $`0/0`$ there. The floor is derived from
   `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` rather than chosen beside it, so
   the ratio is never formed from a denominator the interface itself renders as
   `0.00%`.
2. $`F_A/F_I \leq 1`$. $`F_A \leq F_I`$ is exactly the uptake regime: alveolar
   gas gives agent up to blood, so the alveolar fraction stays below the
   inspired one and reaches it only at equilibrium. Above 1 the tissues are
   returning agent faster than it is being delivered, which is elimination and
   not wash-in. Equilibrium is drawn on the chart as a labelled reference line.

Outside either boundary nothing is drawn. The value is not clamped to the
axis, not interpolated across, and not replaced by a default: a ratio pinned
to 1.0 would draw a completed wash-in the run never reached, and a line joining
the wash-in either side of a washout would draw values the run never produced.
The trace is therefore a set of segments rather than one polyline, and it
breaks where the domain does.

**One point past the boundary, so the ending is legible.** A stretch is
extended by its *crossing* column at each end — the neighbouring drawn column
that has a ratio but sits outside the domain — because without it the curve
stops at the last column at or below equilibrium, which can sit a whole column
spacing's rise below the line it stopped at. A trace halting in clear space
short of a boundary is indistinguishable from one the frame cut off, and this
one is still climbing steeply when it stops; with the crossing column drawn it
meets the equilibrium reference and terminates on it, carrying a point marker
that says the series ended rather than ran out of view. The stretches are
classified over the columns each frame draws rather than maintained as the
run goes, so a boundary can fall only on an instant the chart actually plots
(`app/chart_frame.py`, PL-2FM6).

That extension is bounded by a stated ceiling rather than by a property of the
model. A run stepped at 0.1 s crosses equilibrium by a hair — measured across
every shipped agent and every supported alveolar ventilation and cardiac
output at the maximum fresh gas flow, the first stepped state above
equilibrium reaches 1.00235 — but the ratio is not continuous in general:
`BreathingCircuit.set_circuit_volume` conserves the agent in the circuit while
changing the volume it is divided by, so a circuit volume doubled between two
steps halves $`F_I`$ and doubles the ratio. No interface control does that
today, and a rule holding only because a slider is absent is not one to build
on. A crossing column above the ceiling is therefore not drawn at all, and the
stretch ends where it would have: not clamped onto the ceiling, not
interpolated onto it.

**A blank stretch says which boundary it is.** "No agent has reached the
circuit yet" and "the patient is returning agent" are opposite situations, and
a reader shown only an absent trace has neither. The line beside the plot
names the case, and where the trace is drawing it carries the same value the
trace's right-hand end stands at — one evaluation of one rule produces both,
so the sentence and the curve cannot disagree.

**Why the axis is fixed rather than fitted, and why it does not stop at 1.**
0 to 1 is the scale of every published wash-in figure, which is the point of
drawing this curve at all — so that is where the ruling and the labels stop.
The axis itself stands a little above it, and that headroom is a legibility
requirement rather than a margin: with the axis topping out at equilibrium the
trace's ending lands on the frame, where a line that stopped and a line the
plot cut off look exactly alike. The top of the frame is deliberately
unlabelled, so the readable scale remains 0 to 1 and the space above it is not
read as range the ratio can reach. An axis that instead grew to accommodate
the elimination excursion would redraw the wash-in curve at a smaller height
partway through a lesson — a shape change a
reader would attribute to the model rather than to the axis — and it would
have no stable height to grow to. During elimination the circuit is fed by
agent-free fresh gas and by rebreathed alveolar gas, so the ratio settles near
$`1 + \dot V_{\mathrm{FGF}} / \dot V_A`$, which the supported input ranges do
not bound: measured on sevoflurane, closing the vaporizer at 10 L/min after a
30-minute wash-in gives 3.47 at the reference adult's 4.0 L/min of alveolar
ventilation, 1.83 at 12.0, 5.93 at 2.0 and 20.11 at 0.5, against predictions of
3.50, 1.83, 6.00 and 21.00. Values above 1 are excluded because they are not
wash-in fractions; that they are also unbounded is why no fitted axis would
help.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4.0 -->

**Displayed precision.** Two decimals, and *not* derived from the
concentration resolution, deliberately: the quotient's own resolution depends
on its denominator, so a run early in wash-in knows it far less finely than
one at equilibrium and a single derived figure would over-claim at one end.
The figure is set instead by what the quantity is read against — Yasuda et al.
report 0.850, 0.733 and 0.90 with standard deviations of 0.018, 0.027 and 0.01
— so a third decimal would be finer than the published spread. See
"Published wash-in and elimination validation test".

**What it does not assert.** It is a modelled ratio, not a measurement; it
carries the alveolar compartment's own limitation, that this model has no
airway sampling delay and no dead space; and it is not a depth of anesthesia,
a time to any endpoint, or a prediction for an individual patient.

### Color contrast, and the standard this interface is held to

**The target is WCAG 2.2 Level AA**, with two places this project deliberately
holds itself higher and a set of criteria explicitly deferred. WCAG 2.2 is the
current W3C Recommendation (published 2023-10-05); WCAG 3.0 is a Working Draft
whose scoring model replaces pass/fail entirely and is not designed against
here. Conforming to 2.2 AA also satisfies the 2.1 AA that EN 301 549 and the
2024 ADA Title II rule reference and the 2.0 AA that Section 508 does, though
none of those instruments binds this project — AA is chosen as the right
engineering bar for a teaching tool, not as a compliance obligation.

Two criteria carry most of the weight:

- **SC 1.4.3, Contrast (Minimum)** — 4.5:1 for text. Every readout, every label
  naming a readout, and every agent name over its identification color is held
  to this. The large-text exception (18pt, or 14pt bold) is not claimed
  anywhere: the interface's default text size is 14px, so bold status text is
  judged at 4.5:1 like everything else, and the one genuinely large string —
  the application title — clears the stricter bar regardless.

  **Text is measured against the surface it is actually drawn on, and there are
  two.** The run-status word, the halted-run notice and the educational-use
  disclaimer sit in the top-level column, so the page background shows through
  behind them; the readouts, their labels, the axis description and the
  accounting lines sit inside panels. The page background is the darker of the
  two, so it is the binding surface wherever a color appears on both. Assuming
  the panel is what hid the shortfall `PL-X0RG` fixed: the label color measured
  4.28:1 on the panel and 3.98:1 on the page, and only the second is what a
  reader of the run-status word actually sees.
- **SC 1.4.11, Non-text Contrast** — 3:1 for graphical objects. Each chart trace
  against the panel it is drawn on, each agent swatch read as a shape, and the
  active track of each parameter slider, which is how a control shows where its
  value sits in its range.

**A color that carries meaning as text and as a graphic needs two values, not
one.** The two minima differ by half again, so a single constant serving both
roles fails one of them. This interface has one such case, and it is recorded
here because the roles are not obvious from the constant's name: `ACCENT` is
graphical — the sliders' active track — while
`ACCENT_TEXT` is the same hue darkened until it is legible as text, and it
carries the affirmative status words "Running" and "Valid" whose counterpart is
the warning color. Distinguishing a running from a halted run is safety-critical
for the reason given above, so the word announcing it is held to the text
minimum on the surface it is actually drawn on, and is never the only cue: the
words themselves differ, so a reader who cannot separate the colors still reads
the state.

Held **above** AA in two places:

- **Color is never the sole channel.** SC 1.4.1 (Level A) requires this, but the
  reason here is stronger than the criterion: ISO 5360 Table 2 footnote b makes
  displaying a color an obligation to display the *correct* one, so a second cue
  is what keeps a mis-seen color from becoming a mis-identified agent. The agent
  name always accompanies the color; the chart's traces require a non-color
  channel for the reason below.
- **Chart traces are held to pairwise separation, which WCAG does not cover.**
  SC 1.4.11 only asks 3:1 against the *background*; it says nothing about how
  far apart two adjacent series must be, and reading one compartment against
  another is the whole lesson of this chart. **Confirmed against the source on
  2026-09-07** (`PL-JX0Z`), the Understanding document having been supplied by
  the project owner after five routes to it were refused by the egress proxy.
  Its line-graph example (Figure 38) is explicit: *"The lines should have 3:1
  contrast against their background, but as there is little overlap with other
  lines they do not need to contrast with each other or the graduated lines."*
  Its "Graphical Objects" section makes each line in a graph a graphical object
  in its own right, and allows the Gestalt "law of continuity" to ignore
  **minor** overlaps between them. Note what both carve-outs are conditioned on:
  an absence of overlap. This chart does not have it — six traces start
  together, converge toward equilibrium and cross through wash-in and washout —
  so the exemption that would excuse pairwise separation is one this chart does
  not qualify for. That makes the bar below a supported exceedance rather than
  an arbitrary strictness, and it is why `tools/contrast_check.py` reports the
  pairwise matrix without failing on it while enforcing the panel floor that the
  criterion does require. This bar cannot be met on
  luminance: contrast ratios compose along a bounded axis — black to white is
  21:1 — so sorting $`n`$ traces by luminance, the smallest adjacent gap is
  largest when the gaps are equal, and no arrangement of six traces gives every
  pair more than $`21^{1/5}\approx1.84`$. The floor in the bullet below tightens
  it further, to 1.48. Both are under SC 1.4.11's 3:1, so a redundant non-color
  channel (line style or marker) is a **requirement** for this chart rather than
  an embellishment, and no palette choice can remove it. The next section is
  what that requirement is discharged by.
- **Each chart trace clears 3:1 against the panel under simulated dichromacy as
  well as as displayed.** SC 1.4.11 is defined on the color the display emits,
  so this is the project's bar rather than the criterion's; the reason is that
  the criterion's *purpose* — that a graphical object be findable against its
  background — is not served by measuring one observer. It is not a
  hypothetical strictness: the muscle trace passed at 3.19:1 as displayed and
  failed at 2.98:1 simulated for deuteranopia, a shortfall no normal-vision
  check could see.

**Deferred, and named so the deferral is visible** rather than silently
unlisted: SC 2.4.11 (Focus Not Obscured), 2.5.8 (Target Size), 1.4.10 (Reflow)
and 1.4.12 (Text Spacing). Each needs a settled interface before it can be
answered, and what the rendering backend can deliver for keyboard and
screen-reader support is an open question rather than a commitment.

**The ratios are computed, not asserted.** `tools/contrast_check.py` runs in
`make check`, reads the color constants out of `app/theme.py` - which holds
every one of them since `PL-2CS8`, and is where `check_colors_live_in_the_theme`
requires them to stay - and holds each declared requirement to its declared
minimum using WCAG 2.2's own relative-luminance and contrast-ratio
definitions. Its requirement table names the colors, the criterion and the
reason they are held to that number; the judgment of *which* colors matter
stays in that table, and the tool only evaluates it. Most entries are one
foreground against one background; an element whose edge either of two
channels can carry declares both and is held to the better of them. Each agent
identification badge is that case — a fill outlined in the agent's own text
color — and is perceivable by whichever of the two clears the minimum, so
measuring one channel at a time misreports it. Requirements that do not meet
their minimum today are listed there against the item that closes each one,
and a listed shortfall that starts passing is reported as an error, so a fix
cannot leave its excuse behind.

### The six compartment traces: what separates them

Six curves share one plot, and taking a value off the wrong one is a misreading
of a clinical quantity rather than an aesthetic complaint. What separates them
is **line style**, with color as a second cue and never the first. This section
records why that ordering is forced, and what the colors are held to instead.

**Line style is the separating channel.**

| Compartment | Line style | Dash pattern (px) | Width (px) |
| --- | --- | --- | --- |
| Circuit | solid | — | 3 |
| Alveolar | long dash | 10 on, 4 off | 3 |
| Mixed venous | short dash | 4 on, 3 off | 2 |
| Vessel-rich | even dash | 6 on, 6 off | 2 |
| Muscle | dotted | 2 on, 3 off | 2 |
| Fat | dash-dot | 12 on, 4 off, 2 on, 4 off | 2 |

All six differ, and the legend entry beside each checkbox names its style in
words, so the style is legible without reference to the plot. Circuit and
vessel-rich were both solid until `PL-GVXP`: for that one pair the redundant
channel was redundant in name only.

**Which style goes on which compartment is decided by the colors.** The two
traces hardest to separate by color get the two marks easiest to separate by
shape, and so on outward. The closest pairs in the matrix below — vessel-rich
against fat, and mixed venous against fat — are an even dash against an
alternating dash-dot and a short uniform dash against that same dash-dot, each
differing from its partner in mark length, gap length and rhythm at once. The
one genuinely confusable pair in the set, the 2 px dots against the 4 px short
dash, is spent on mixed venous against muscle, which is the widest separation
any pair of these six has.

**Color is a second cue, and the arithmetic says it cannot be the first.**
Every trace clears SC 1.4.11's 3:1 against the panel, as displayed and as
simulated for each dichromacy:

| Trace | sRGB | Normal | Protanopia | Deuteranopia | Tritanopia |
| --- | --- | --- | --- | --- | --- |
| Circuit | `#176B87` | 6.02 | 5.67 | 6.21 | 6.02 |
| Alveolar | `#159789` | 3.61 | 3.23 | 3.84 | 3.63 |
| Mixed venous | `#7C3AED` | 5.70 | 5.96 | 4.68 | 5.55 |
| Vessel-rich | `#DC2626` | 4.83 | 7.18 | 4.14 | 4.84 |
| Muscle | `#D17206` | 3.43 | 3.96 | 3.22 | 3.46 |
| Fat | `#64748B` | 4.76 | 4.74 | 4.76 | 4.77 |

Trace against trace, it is a different picture, and this is the table the
design rests on:

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
assumed.** The ceiling above is $`21^{1/5}\approx1.84`$; requiring 3:1 against
a white panel caps every trace's luminance at 0.30, which shortens the axis and
brings the ceiling to **1.48**. Searching lightness with each hue and
saturation held fixed reaches **1.28** as the best worst-pair across the four
vision models, and gets there only by driving four of the six traces to
near-black — losing the hue identity that makes a trace nameable, to buy a
number still less than half of 3:1. So the colors here are chosen to name their
compartment and to clear the floor against the panel, and the line style does
the separating. `.claude/rules/ui-color.md` carries this as a standing
judgment so the search is not re-run every time a color is touched.

**Two colors were re-picked, for the floor and not for separation.** The
alveolar trace was `#18A999` (2.93:1 as displayed, 2.61:1 simulated for
protanopia) and the muscle trace `#D97706` (3.19:1 as displayed, 2.98:1
simulated for deuteranopia). Each keeps its hue and saturation exactly and is
darkened to the lightest shade clearing 3.2:1 in all four models — 3:1 plus two
tenths, so the shipped value is not itself a boundary case. The alveolar trace
also draws the $`F_A/F_I`$ wash-in plot, which carries a single line and never
had a separation problem; it inherited the shortfall from the shared constant
and is fixed by the same change.

**What changes when two runs share the axis, and what does not.** Nothing about
a compartment's appearance changes: it keeps the line style and the colour the
table above gives it, because colour already means "compartment" here and a
channel meaning something else either side of a mode change is a misread of a
clinical value waiting to happen. What is added is the **run, on line width, at
two levels**, which the arithmetic above makes possible only under a cap — at
six compartments the width column above is already spent across 2 px and 3 px,
so **at most two compartments are drawn while two runs are shown** (`PL-HLD5`,
`PL-8PSW`). Two compartments times two runs is four curves. The cap is a
colour-capacity limit on the chart and never a reduction of what the display
owes: § "Minimum displayed outputs" keeps all six readouts on screen for both
runs, and says so naming this cap.

**The first run is the wider, and the second keeps the single-run width.** This
is forced rather than chosen. A branch reproduces its parent element-wise up to
the fork (planned-milestone item 12), so before the branch point the two curves
do not merely run close together — they coincide exactly, and whichever is drawn
thicker hides the other completely over that stretch. The narrower curve
therefore has to be the one drawn last and on top. Widening rather than
narrowing also keeps every trace at or above the 2 px the table above gives it:
a 1 px antialiased line renders lighter than its declared colour, which would
walk back into the 3:1 floor against the panel that this section treats as an
error rather than a tracked shortfall. The two levels are read *locally* —
between two curves of one compartment, which are adjacent by construction —
rather than decoded across the plot.

**Two marks that are not traces, and how they are separated.** A control change
and a branch point are both vertical, both annotate an instant rather than
showing any part of the run, and both are drawn in the control mark's colour.
What separates them is the dash pattern — the control mark is finely dashed and
the branch point solid — and the words in the legend, which name both. Neither
rests on a hue, which is deliberate for a pair a reader must not confuse: a fork
is where two runs stop being the same run, and reading one as a setting change
would attribute a divergence to the wrong cause.

**The dichromacy simulation.** Brettel, Viénot and Mollon's projection onto the
reduced stimulus surface each dichromacy leaves — the surface defined by the
neutral axis and the monochromatic stimuli a dichromat and a normal trichromat
see as the same hue.[^brettel1997] The two-half-plane form is used rather than
the single-matrix simplification of Viénot, Brettel and Mollon (1999), because
that simplification is not accurate for tritanopia and all three are reported
here.[^vienot1999] The coefficients are the precomputed sRGB-space forms
published by libDaltonLens, derived from Brettel's construction over the Smith
and Pokorny (1975) cone fundamentals.[^daltonlens]

Three limits on how far these numbers may be read. The simulation renders, for
a normal observer, an approximation of a dichromat's *appearance*; it is not a
measurement of dichromatic perception, and it models the three dichromacies
rather than the far commoner anomalous trichromacies, whose milder losses it
does not represent. WCAG's relative-luminance formula is then applied to that
simulated output, which is a use the formula was not defined for — SC 1.4.11 is
defined on the color the display emits. And the whole calculation is about
luminance, so it says nothing about the hue difference a reader with normal
color vision actually uses. What the numbers are good for is the comparative
claim they are used for here: that no arrangement of these six colors separates
them, whichever observer is assumed.

`tools/contrast_check.py` computes every figure in this section, `make check`
runs it, and `tests/unit/test_contrast_check.py` pins them; run it with
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
fixed resolution of **0.01 percentage points** — two decimals of a percent —
uniformly across all six compartments. The delivered-agent setting uses the
same resolution — in the readout beside its slider and in the slider's own
drag label alike — so the value a reader dials and the values it produces
are read at one scale. A positive value that would round to `0.00%` is
displayed as `<0.01%` rather than as zero.

This is a recorded decision (PL-040), not a formatting convention, because
displayed precision is a claim about what the model can support. Earlier
revisions displayed three decimals, and were reduced to two while the operator
split shipped, on the ground that the third decimal and part of the second sat
below the solver's own error.

**That ground is gone, and the decision is re-derived here rather than
inherited** (`PL-X9KD`, 2026-09-06). `PL-GS5X` replaced the split with an exact
propagator, so the solver no longer limits anything a reader can see: measured
against the independent solution, the shipped step's own residual is at most
$`1.6\times10^{-12}`$ percentage points anywhere in the reference gate's
trajectories, and $`5.2\times10^{-12}`$ over a held hour. That is about one
two-billionth of the last displayed digit. **A third decimal would no longer be
numerical noise**, and every figure the previous version of this section quoted
in counts of the last digit described a method that has been retired.

So the constraint that decides the resolution had to be found again, and it is
not the one that used to. It is **model fidelity** — what the parameters can
support — bounded from the other side by **legibility**.

**Two questions the old section ran together, and the distinction now carries
the whole derivation.** Asked as *how finely can two moments within one run be
told apart*, the answer is now about nine decimal places finer than the readout
shows: within a run the parameters are fixed, the simulation is deterministic,
and nothing in the arithmetic is within nine orders of the last displayed
digit. Asked as *how finely does this model resolve a concentration in a
patient*, the answer is very much coarser, and it is the question a clinician
reading a percent sign is actually asking. The old section answered the first
and presented it as the second; it could do that because the solver error
happened to sit near the readout, and it cannot any more.

**The ceiling: one measured standard deviation of a partition coefficient is
worth about one to seven counts of the last displayed digit.** Perturbing a
single stored coefficient by one published SD and re-running at 1 MAC with the
reference adult's flows displaces a displayed compartment by:

| Coefficient perturbed by one SD | Displacement, worst over 3600 s |
| --- | --- |
| Fat tissue:gas | 8.7×10⁻⁴ to 6.7×10⁻³ pp |
| Blood:gas | 1.5×10⁻² to 5.4×10⁻² pp |
| Vessel-rich tissue:gas | 1.3×10⁻² to 5.0×10⁻² pp |
| Muscle tissue:gas | 1.3×10⁻² to 6.8×10⁻² pp |

Each range runs over the three shipped agents, desflurane always the largest.
The SDs are the measured ones "Parameter provenance" already records: Yasuda,
Targ and Eger's human tissue coefficients, whose SDs are 3.9% of the mean for
desflurane, 5.3% for sevoflurane and 6.4% for isoflurane, and — for
desflurane's blood:gas — Eger's $`0.424 \pm 0.024`$, 5.7%.

Against that, the last digit of a two-decimal readout is between about a
seventh of one parameter SD and seven times it. A third decimal would put the
last digit at one seventieth to seven tenths of one SD: it would be asserting
resolution in a quantity whose own measured spread is one to two orders of
magnitude wider, in the readouts where a reader has least ability to notice.
That is false precision in the sense `CLAUDE.md` forbids, and it is what stops
the count at two.

**Parameter uncertainty governs the ceiling and still does not govern the
within-run reading, and both halves matter.** A partition coefficient's SD
displaces a whole trajectory: it moves where the curve sits, not how finely two
points on it can be distinguished. So a reader comparing 09:14 against 09:16 of
one run is not limited by it, which is why the readout may honestly carry a
digit finer than the SD — the seventh-of-an-SD end of the range above. What the
SD does forbid is carrying digits *far* finer than it, because a reader cannot
tell which of the two questions a printed digit is answering, and the interface
must not invite the second reading while only supporting the first. "Known
limitations" is where the consequence is made good: no displayed value may be
read as accurate to its last digit as a prediction about a patient. It is
accurate to its last digit as a statement about this model with these
parameters.

**The floor: one decimal is legible enough to be tempting and erases the
teaching.** At 0.1 percentage points the sevoflurane and isoflurane fat
fractions read `0.0%` for the whole hour (0.032% and 0.015% at 3600 s);
desflurane's stays `0.0%` for its first 19.3 minutes and reaches 0.2%. Muscle
reads `0.0%` for its first 2.9 minutes (desflurane), 8.5 minutes (sevoflurane)
and 14.8 minutes (isoflurane). At two decimals the same compartments come alive
at 57, 125 and 190 seconds (muscle) and 236, 780 and 1474 seconds (fat). What
one decimal erases is the slow-compartment wash-in that is the reason for
displaying those compartments at all.

**That floor is a teaching judgment, and it is the project owner's rather than
the model's** (decided 2026-09-03, `PL-88GQ`). The accuracy argument does not
reach it: one decimal is comfortably supported by both the solver and the
parameters, so nothing numerical rules it out. What rules it out is that a
simulator built to show uptake and distribution would show a flat zero where
the uptake is happening. Stated as a pedagogical objection so that a future
revisit knows exactly what it has to beat, and does not mistake it for a model
constraint it cannot touch.

**So the band is one to two decimals, and two is the chosen count.** The band
is what the error budget licenses; the count inside it is a presentation
decision the owner may revise without re-deriving anything in `core/`. Nothing
in the model is computed from it: `MAXIMUM_SIMULATION_STEP_S` is a tolerance in
seconds and the supported input ranges are intervals in L/min, and
"Supported simulation step" and "Supported input ranges" derive both without
reference to how many decimals the readout shows. Moving the readout to one
decimal would change what a reader sees and nothing else. That independence is
new: until `PL-X9KD` both were justified through this count, so a purely
presentational change would, by the reasoning as written, have licensed a step
ten times longer and wider input intervals.

**The MAC resolution is derived from this one, not chosen beside it.** A MAC
multiple is a percent divided by the agent's own `mac_percent`, so the
resolution above already fixes how finely the quotient is known, and stating
a second resolution independently would mean re-deriving two numbers whenever
this one is re-measured. The rule is one line: **the finest power of ten that
is nowhere finer than the percent resolution converted into MAC.** That
conversion is agent-specific — 0.01 percentage points is 0.005 MAC for
sevoflurane, 0.0083 for isoflurane and 0.0017 for desflurane — so the binding
agent is isoflurane at 0.0083 MAC, and **0.01 MAC** is the finest power of ten
at or above it.

One count of the MAC line is therefore 0.02 percentage points of sevoflurane,
0.012 of isoflurane and 0.06 of desflurane: coarser than the percent readout
beside it for every agent, which is the property that keeps the two units from
contradicting each other. A reader must never be able to watch the MAC digit
move while the percent digit stands still, because that would assert the model
resolved something it does not. The unit conversion is not
information-preserving across agents, which is why the MAC resolution is
uniform in MAC rather than being the percent resolution restated: a
per-agent MAC resolution would put different magnitudes at the same glyph
position, which is the failure "Why the resolution is uniform rather than
per-compartment" rejects below, arriving across agents instead of across
compartments.

The below-resolution form applies to the MAC line for the same reason it
applies to the percent line, and matters more rather than less: a compartment
clears 0.01 MAC later than it clears 0.01 percentage points, so `0.00 ×MAC`
under a percent line already showing the compartment filling would be the two
readouts contradicting each other. `<0.01 ×MAC` states what is known.
`tests/unit/test_formatting.py` re-runs the derivation against every shipped
agent, so adding an agent or changing the percent resolution fails there
rather than silently over-claiming.

**The resolution is a property of the display alone.** Everything upstream of
the formatter carries full binary64: the compartment states, every
integration step, the mixed-venous and tissue transfers, and every state of
the `DrawnWindow` the chart is drawn from. Nothing in `core/` rounds,
the snapshot fields the interface reads are raw fractions, and a slider's
value reaches the model unquantized — the rounding happens exactly once, in
the readout. So the two decimals are a statement about what is worth
*showing*, never about what the model computes or stores.
`test_the_model_keeps_precision_the_display_throws_away` holds this: two runs
whose delivered concentration differs four orders of magnitude below the
display resolution must reach states that differ, and must still read
identically on the display.

That test is worth more now than when it was written, not less. While the
solver error sat near the readout, "the model keeps more precision than the
display shows" was a small claim; under the exact step the gap is nine orders,
and the rounding in the readout is the only place resolution is lost anywhere
between a slider and a pixel.

**What the last digit does not cover, and what it still does.**
~~The error is a systematic sequencing bias rather than noise, and its sign is
opposite at the two ends of the transfer chain. A *difference* between two of
the six readouts therefore carries the sum of two displacements, up to 1.8
times the error in either reading alone, worst measured at 0.030 percentage
points, so the numeric gap between two readouts is the least certain thing on
the display.~~ **Withdrawn 2026-09-06 (`PL-GS5X`).** That bias was a property
of the operator split's sub-step ordering. The exact step drives no compartment
from an already-moved upstream value, so there is no displacement with a sign
and a gap between two readouts is no less accurate than either reading it is
taken from; "Independent-solution test" above records the withdrawal in full.

The comparison the interface actually invites is therefore no longer at risk
from the solver, and that is a measurement rather than an assurance. The six
readouts are placed in one row — where seven panels fit it; § "The row has a
width condition, and both arguments above rest on it" below states what happens
under that — to be read *ordinally*: the circuit leads the
alveoli lead the tissues. An ordinal reading is corrupted only if the
error can invert which of two compartments is displayed as higher. Across every
trajectory in "Independent-solution test", all three agents, comparing every
pair of the six readouts at every step — 1 485 000 pair comparisons —
the shipped and reference solutions **never** disagree about the displayed
ordering, anywhere, at any gap. Under the split they disagreed on the worst
reachable trajectory for 0.2 s of a 900 s run with sevoflurane and 1.7 s with
desflurane, at gaps up to 1.73 counts of the last displayed digit.

That is a measurement on one platform rather than a guarantee, and the
arithmetic behind it says why the gate keeps a threshold rather than asserting
zero. Rounding to a fixed number of decimals is monotone, so it can never
produce an ordering opposite to the raw one; an inversion therefore needs the
two solutions to be genuinely reordered, which needs a true gap below the sum
of the two displacements. The widest pairwise differential measured anywhere is
$`1.1\times10^{-12}`$ in fraction, and true gaps that small do occur while two
compartments cross, so an inversion is arithmetically reachable there even
though none was observed.

That is why the interface marks nothing here. A reader who compares the
readouts the way the row is designed to be compared cannot be misled by solver
error; a reader who subtracts two of them is doing arithmetic the interface
does not perform, and the paragraph above is the disclosure for it.
`test_displayed_ordering_reverses_only_at_a_crossing` holds the claim, now
against a threshold derived from the absolute gate rather than fitted to a
measurement: twice the tolerance, which is $`1.0\times10^{-7}`$ counts against
the 3.0 counts the split's bound allowed.

**Why the resolution is uniform rather than per-compartment.** The six
readouts sit together — in one row where seven panels fit the window, in a
grid below that — and are read comparatively; the reason for showing them together
is that a reader can see the circuit lead the alveoli lead the
tissues. Different decimal counts across those tiles would put different
magnitudes at the same glyph position, so a value scanned rather than read
would be misjudged by a factor of ten. That is a property of the reading task
and holds whatever the solver does.

What used to be offered beside it — that the split's error was itself bounded
in absolute percentage points and stayed within a factor of four across the
four fast compartments, so one absolute resolution expressed it directly — is
withdrawn with the split. The replacement is that **parameter uncertainty is
also absolute in its effect across the row**: the one-SD displacements tabulated
above run from $`8.7\times10^{-4}`$ to $`6.8\times10^{-2}`$ percentage points
across all six compartments and all four coefficients, a spread of under two
orders on a row whose *values* span four. A single absolute resolution is the
direct expression of that, set by the compartments where the displacement is
largest and conservative in the ones where it is not.

**The row has a width condition, and both arguments above rest on it.** The
interface is responsive, and until now this section stated the one-row
arrangement without qualification, which a reader is entitled to take as a
commitment. `readout_columns` in `src/anesthesia_sim/app/dashboard_frame.py`
sets the row's column count from its width and every panel spans exactly one
column — `test_every_readout_reserves_a_qualifier_line_and_an_equal_column`
holds both — so the seven panels seat **side by side wherever seven panels'
reserved widths fit the row, four per line where seven do not, two where
four do not, and one below that** (`READOUT_ROW_LADDER`). The reservation is
the widest value each column can show, measured in the rendering font
(`PL-3355`) - the clock's column its widest elapsed form, each compartment's
its widest percent and MAC multiple, so the clock's width costs no other
column - and the widths at which the row steps down belong to the font and
the display scale rather than to this document: on the offscreen font the
test suite renders with, the row is seven across from 1068 logical pixels,
four from 632 and two from 336, and
`test_the_readout_row_reflows_where_its_panels_stop_fitting` reads those
widths from the row rather than asserting them. Those figures are an example
of the rule, not a specification of it. The Flet build recorded 1200, 992
and 768 as a rendered measurement at Flet's sizes (`PL-8M05`); the port
derives the same ladder from what it draws with, so no pixel figure is
asserted that a font or a HiDPI scale would falsify.

The two arguments are not affected equally, and neither is withdrawn.

- **The ordinal reading is the one that weakens.** Below the seven-across
  width the six readouts are on two or more lines, and the comparison the row invites
  stops being a single glance and becomes a scan across them. The *measurement*
  behind the claim is untouched — it compares displayed values, not their
  positions, and the 1 485 000 pair comparisons say nothing about layout — so
  what narrows is the claim that the arrangement invites the comparison, not
  the claim that the ordering is faithful.
- **The uniform resolution holds at every width**, and the reflow does not
  weaken its argument. That argument is that differing decimal counts would put
  different magnitudes at the same glyph position; the grid aligns value glyphs
  within a column at every rung, so a reader scanning two panels reads
  them against a common position whether they are side by side or stacked. It
  never rested on the six being in a single line.

**In practice the row opens at whichever rung the screen affords.**
`src/anesthesia_sim/app/main.py` opens the window at `WINDOW_SCREEN_FRACTION`
of the screen's available area and centred (`PL-005`, with the Qt port), so on
a display whose available width, at that fraction and less the page's own
padding, falls short of the seven-across width — an available width of
roughly 1375 logical pixels on the offscreen font above, and a different
figure on any other — the
interface starts below the widest rung and the conditional arrangement is the
ordinary case rather than the resized one. Until that port the window opened
full screen and the widest breakpoint was the only one a reader met without
resizing.

**Why not a significant-figures rule.** A significant-figures rule gives the
smallest values the most decimal places, and the small values are exactly
where this model supports the least. The evidence for that is no longer the
solver — under the exact step the sparsely filled compartments carry at most
$`2\times10^{-4}`$ relative error anywhere in the first ten seconds of a run,
and $`8\times10^{-11}`$ at ten seconds itself. It is the parameters. Their
measured SDs are 3.9% to 6.4% of the mean and are *relative*, so they apply
undiminished to a compartment holding a thousandth of a percent. Three
significant figures on the fat fraction would imply a relative resolution of
0.1% on a number whose parameters are known to about 5%, over-claiming by a
factor of fifty — and doing so most severely in the readouts where a reader has
least ability to notice.

**Why not the 0.1 percentage points clinical monitors report.** Agent
monitors display end-tidal and inspired concentrations to a tenth of a
percentage point, and the circuit and alveolar readouts alone would be well
matched to that. This simulator, though, displays compartments no monitor
shows, and the floor argument above is the answer: at monitor resolution the
sevoflurane and isoflurane fat fractions read `0.0%` for an entire hour and
muscle reads `0.0%` for its first 2.9 to 14.8 minutes. Rounding to clinical
convention would erase the slow-compartment wash-in that is the reason for
displaying those compartments at all. 0.01 percentage points is the coarsest
resolution that keeps every displayed compartment legible; that it is also
close to what the parameters support is a coincidence worth naming rather than
a second constraint meeting the first, since the two are measured entirely
independently.

**Why a below-resolution value is marked rather than shown as zero.** Even
at 0.01 percentage points the slow compartments start below the last digit.
At 1 MAC with default flows, muscle first rounds to a nonzero value at 57 s
(desflurane), 125 s (sevoflurane), and 190 s (isoflurane); fat at 237 s,
780 s, and 1474 s respectively. Displaying `0.00%` across those intervals
would state that the compartment holds no agent, which the model does not
say — it says the compartment is filling, below what the display resolves.
`<0.01%` states exactly that, and it keeps `0.00%` meaning the one thing it
should: nothing has arrived yet, as before a run starts. This is the
distinction between a value the model asserts and a value the display cannot
carry, and the interface must preserve it rather than adding a decimal the
model cannot support.

A negative fraction is deliberately excluded from the below-resolution form.
The compartment guards make one impossible, so a negative reaching the
formatter means something upstream is wrong, and it must remain visible as
an anomaly rather than be absorbed into a plausible small positive reading.

**How this section changed when the solver did, stated so a reader comparing
versions is not misled.** Through v0.4.2 this section carried a paragraph
headed "Why parameter uncertainty does not govern this", which argued that the
decimal count was set by the per-step solver error and that parameter
uncertainty, displacing a whole trajectory rather than limiting within-run
resolution, was disclosed in "Parameter provenance" instead of being encoded in
a decimal count. The second half of that is still true and is kept above; the
first half is not, because there is no longer a per-step solver error of a size
any readout could express. So the roles have swapped: parameter uncertainty is
now what bounds the count from above, and the trajectory-versus-within-run
distinction is what explains why the bound is loose enough to permit a digit
finer than one SD rather than forbidding it.

Two things did *not* change, and neither depended on the solver: the resolution
that ships, and the reason a reader may not treat it as a claim about a
patient. Nothing in this document has ever licensed the second reading, and
"Known limitations" is where it is made good — no displayed value may be read
as accurate to its last digit as a prediction about a patient. It is accurate
to its last digit as a statement about this model with these parameters.

**Precision elsewhere in the interface, and why it differs.** Simulated
time is displayed to 0.1 s, which is exactly `SIMULATION_STEP_S`: the
display resolves one step and no finer, and every recorded control change is
stamped at that same resolution so the timeline and the clock cannot be read
against each other in two forms. The chart's own time axis is labelled
differently and deliberately: a compound duration carrying its own units, and
no finer than the whole second every tick on the ladder falls on. It labels a
span a reader is scanning rather than stamping an instant they are reading
off, so a tenth on every label would be width spent on a digit that is always
zero at every width the ladder offers. "The chart's time base" carries the
form and why it is not the clock's. Fresh gas flow, alveolar
ventilation, and cardiac output are displayed to 0.1 L/min, matching the
resolution of the flow controls that set them. A slider and the readout beside
it show one quantity, so the Qt sliders are integer-valued with steps at the
display resolution — 0.1 L/min for the three flows, 0.01 percentage points for
the delivered dial — and the value applied to the model is exactly the value
printed beside the control (`PL-25KS`); a control that could apply a value its
own label rounds away would leave a reader unable to tell which value is the
setting in force.

**The agent-accounting panel's three amounts are displayed to 0.1 L, and its
two residual lines in scientific notation, because they answer different
questions** (`PL-TG60`, 2026-09-15). The residual lines are a numerical
diagnostic whose job is to make a residual of order 10⁻¹² L visible against
amounts of order 1 to 100 L, which no fixed decimal count can do. The amounts
are read against each other — delivered against exhausted plus stored — and
against a reader's sense of scale, so they take one uniform resolution on the
same argument as the readouts above. Perturbing one stored coefficient by one
published SD, as the readouts' derivation does, moves the exhaust total by
0.016 to 0.042 L at 3600 s and by 0.18 to 0.23 L at the 24 h supported limit
(sevoflurane 0.024 and 0.19 L, isoflurane 0.016 and 0.18 L, desflurane 0.042
and 0.23 L; blood:gas dominant throughout; measured at 1 MAC with the
reference adult's flows). One count of 0.1 L therefore sits between a quarter
of an SD and six SDs across the whole supported span, inside the band the
readouts' derivation admits, while a count of 0.01 L falls to a fiftieth of an
SD by 24 h. The six decimals printed until `PL-TG60` asserted a millilitre of
a quantity the parameters place to within a decilitre, and the justification
this section carried for them — that the amounts made the residual visible —
did not hold, since a residual twelve orders below the last printed digit is
visible only on the lines that print it in scientific notation. Delivered
agent carries no parameter uncertainty, being the dial times the flow times
the time, and takes the same resolution so the three amounts read at one
scale. The unit is stated on the panel as this document states it, litres of
equivalent pure agent gas, because a bare "L" beside an anaesthetic agent
invites the liquid reading. `AGENT_VOLUME_DISPLAY_DECIMALS` holds the count,
`format_agent_volume` the form, and `test_agent_amounts_precision` pins both.
Precision in this interface is set by what each number is for, and the rule
above governs the clinical readouts.

The chart plots the same percentages on a shared linear axis running from 0 to
3 ×MAC of the running agent, and carries a second axis on the right reading
the identical coordinate in MAC multiples. Its resolution is set by pixels
rather than by decimals, and it is coarser than the numeric readouts
throughout: a trace is where a *shape* is read, and every number the chart
offers is rendered at the resolution above rather than at the axis's — the
readout row, and the hover readout § "The chart's hover readout: what the
tooltip may show" derives below. The MAC axis is labelled on round MAC values
rather than on round percentages — half-MAC steps, which the fixed 3 ×MAC
range gives for every agent, so the gridline a reader learns under one agent
means the same thing under the next. "The chart's
vertical range is denominated in MAC, and fixed" above carries why the range
is what it is. Its horizontal extent is the selected time base rather than a
fixed span, so seconds per pixel is the reader's choice; "The chart's time
base" carries how a width is chosen and how it is ruled.

`app/formatting.py` is where this section terminates: it holds the
resolution as a single constant, derives the formatter, the below-resolution
marker, the MAC decimal count and the MAC axis placement from it, and imports
no toolkit, so the functions this section reasons about can be read, cited and
tested without loading the interface. `tests/unit/test_formatting.py` pins the constant and every
string the formatter produces; `tests/unit/test_dashboard_frame.py` holds
the end-to-end path — real controller, real step, the string on the panel.
`app/dashboard_frame.py` reads the constant for the delivered dial's slider
position, which is why the value the slider applies and the readout beside it
cannot drift apart.

`tests/reference/test_coupled_dynamics.py` restates the same constant and
checks it against `app/formatting.py`, because the ordering claim above is a
property of the rounded values and adding a decimal would change what that
claim proves without changing anything it reads. A change to the resolution
is a change to this section.

### The chart's hover readout: what the tooltip may show

A pointer held over a trace is answered with a small floating readout. This
section derives its contents as § "Displayed precision" above derives the
numeric readouts', and for the same reason: what a hover reports is a
clinically meaningful displayed value, so what it may show is a claim about the
model rather than a formatting convention.

**It needs a derivation of its own because it is read detached from everything
that qualifies it.** The six numeric readouts sit under a heading naming the
agent and calling the values modelled, beside a legend naming each compartment,
on a panel whose alveolar entry carries the `end-tidal-equivalent` gloss this
document requires above. A floating box carries none of that. It appears over
the plot, it can cover the heading it would otherwise be read under, and it is
the one place in this interface where a number is presented with nothing around
it. Every qualifier the readout row gets from its surroundings, the box has to
supply itself.

**And it is the display a reader has most deliberately stopped to consult.** A
value in the readout row is glanced at while a run plays; a value under a
cursor is one somebody went looking for. That makes it the display most likely
to be written down, and the one where being mistaken for a measurement costs
most.

#### What it shows

Three lines: run context, then what the value is, then the value.

```
Modelled sevoflurane · 20m8s
Alveolar (end-tidal-equivalent)
1.43%   0.71 ×MAC
```

**The order carries the safety argument and is not typographic.** The
qualifiers precede the number, so a reader reaches `1.43%` through "modelled"
and through the compartment it belongs to rather than meeting them afterwards.
`.claude/rules/expert-review.md` states the general form — prefer an interface
that prevents an error to one that warns after it — and a hedge placed below
the number it hedges is a warning: the number has already been read.

Each line, and what obliges it:

1. **Run context — the modelled marker, the agent, the run where more than
   one is drawn, and the instant.** The
   marker is on every hover, not only on the compartments with a measured
   twin, because the box is detached from the heading that would otherwise
   carry it. The agent is there because the same percentage means different
   things under different agents — 1.43% is 0.71 MAC of sevoflurane and 0.24
   MAC of desflurane — and a floating box cannot rely on the header being
   visible behind it. The instant is `format_elapsed`'s compound form, the
   same form the clock, every control stamp and the time axis use.
2. **What the value is — the compartment, with its gloss where the readout row
   has one.** `Alveolar (end-tidal-equivalent)` and `Circuit (inspired)`; the
   other four carry none, because the readout row carries none. Those two
   glosses exist for the two compartments a clinician would most readily set
   beside a monitor reading, which § "Minimum displayed outputs" decided and
   this reuses rather than re-takes.
3. **The value, in both units the chart carries.** Percent and MAC multiple,
   the same pair the readout panel shows, because the chart itself has two
   axes and a single number could be read against either.

**Every number in it is produced by `app/formatting.py`, never by the chart
library.** `format_percent`, `format_mac_multiple` and `format_elapsed` are the
whole of it. This is the rule that the rest of this section exists to justify,
and it is not a style preference: a charting library formats a coordinate,
which is a different thing from formatting a clinical value, and every default
this project has met formats the coordinate.

The MAC multiple resolves against the snapshot's own `mac_percent`, exactly as
the MAC axis and the readout row do. A hover reporting a MAC multiple computed
from any other divisor would be the traceability failure `CLAUDE.md` forbids,
arriving through the one display that looks least like a calculation.

#### The hover and the run it belongs to

**While more than one run is drawn, the first line names the run; while one is,
it does not** (project owner, 2026-09-17, ratified, over giving the run a
fourth line of its own and over holding the curve's line width and the legend
to be sufficient).

```
Modelled sevoflurane · Run 2 · 20m8s
Alveolar (end-tidal-equivalent)
1.43%   0.71 ×MAC
```

**The hover is a displayed concentration, so § "Minimum displayed outputs"
already decides the principle**: "The run is named in text, not carried by
colour or by position… Text has no width analogue… A concentration that does
not say which management produced it is the correct number under the wrong
patient context." That paragraph is written against the numeric readouts, and
every reason it gives applies here with more force rather than less — the
readouts sit in a labelled block beside the run's own panel, and this box
floats over the plot with nothing around it, which is the argument the top of
this section already makes for why the modelled marker travels with the value.

**The argument that the pointer is already over one curve is false, and was
measured.** `nearest_trace_point` keeps the single globally nearest drawn point
across *every* run on the frame, so the pointer is within reach of both runs
wherever their curves for one compartment run close together. Measured
2026-09-17 on a branched sevoflurane case — reference adult, trunk held at
1 MAC, branch forked at 10 min, a 60-minute axis 900 px wide and 360 px tall,
so 4.00 s/px and 0.0167 %/px — the share of the shared axis on which both runs'
points for one compartment sit inside the 12 px hover radius:

| Branch's management at the fork | Alveolar | Fat |
| --- | ---: | ---: |
| doubled to 2 MAC | 1.6% | 100% |
| raised to 1.25 MAC | 8.5% | 100% |
| vaporizer turned off | 1.6% | 100% |

The fat row is total in every case, including against the widest management
difference the interface permits, because the percent axis is scaled by the
alveolar peak and the slow compartments are compressed near zero. Those are the
compartments this chart exists to teach. It is consequential rather than
cosmetic: of the hovers that could answer for either run, 83.3–95.3% (alveolar)
and 43.8–81.4% (fat) would print *different* text. On the emergence case the
fat hover at 3492 s reads either `0.03%   0.02 ×MAC` or `0.01%   <0.01 ×MAC`
depending on which run answered — a threefold difference in stored agent
between a run still carrying it and one 48 minutes into emergence.

**It goes on line 1 rather than on a fourth line** because line 1 is the line
this section already calls *run context*, so naming the run completes it rather
than changing the three-line form the rest of this section derives. While two
runs are compared it is also the only token on that line that tells them apart:
`assemble_chart_frame` refuses a frame whose runs differ on agent, because they
share one MAC axis and one set of clinical references, so the agent is constant
across the runs being compared and the line would otherwise spend its
distinguishing slot on a constant. The one argument for a fourth line is that a
distinct line is scanned where a mid-line token may not be, which matters
because the run under a resting pointer can change; it is answered by the value
on line 3 changing at the same moment, so the reader has two cues rather than
none.

**It is conditional, and that is not a hidden mode.** A single run has nothing
to be told apart from, and a name on the only run drawn implies a comparison
that is not on screen. The condition is the same one the width channel already
carries — `run_trace_style` widens nothing until a second run exists — and it
is visible on its face: a second run brings a second legend entry, a second
readout panel and a second set of curves with it. A reader cannot be in the
two-run state without seeing the two runs.

**What this does not fix.** Naming the run makes the choice between runs
*visible*; it does not make the hover answer for the curve the reader aimed at.
On the measurement above, a 2 px movement of the pointer flips which run
answers on 75.4–99.9% of the fat axis. That is a targeting rule rather than a
readout question, and it is `PL-JVHL`.

#### Resolution: the readouts' derivation applies unchanged

Two decimals of a percent and two decimals of a MAC multiple, with the
below-resolution forms `<0.01%` and `<0.01 ×MAC`. § "Displayed precision"
derives both and nothing in it is a property of where the number appears: the
ceiling is one measured standard deviation of a partition coefficient, which
displaces a trajectory rather than a display, and the floor is a teaching
judgment about what a reader can learn from the slow compartments.

**The one argument for a finer hover readout is answered rather than
inherited.** That section separates two questions a printed digit could be
answering — how finely two moments *within one run* can be told apart, which
is about nine decimal places finer than the readout shows, and how finely
this model resolves a concentration *in a patient*, which is much coarser. A
hover is closer to the first than the readout row is: it reports one trace at
one instant, which is the shape of a within-run comparison, and the within-run
question would license a third decimal.

It does not get one, and the reason is the same sentence that settles the
readouts: a reader cannot tell which of the two questions a printed digit is
answering. The hover makes that worse rather than better. It is the display
most likely to be transcribed, it appears over a chart whose whole subject is a
patient, and it is read without the row of five other compartments that make a
within-run comparison obviously what is on offer. So the display most exposed
to the patient reading is the last one that should carry a digit only the
within-run reading supports.

**The below-resolution form is required here, not optional.** Fat sits under
0.01% for the first thirteen minutes at 1 MAC sevoflurane and muscle for the
first two; those minutes are the slow-compartment wash-in the chart exists to
show. `<0.01%` says what is known. A hover printing a number there would assert
resolution the model does not have, on the compartment where a reader has least
ability to notice.

#### What a chart library prints instead, measured

The default matters because it is what ships if nothing overrides it, and
because both toolkits this project has used default to formatting the
coordinate. `flet_charts.LineChartDataPoint` defaults to a
`LineChartDataPointTooltip` whose `text` this application never writes into;
`pyqtgraph.ScatterPlotItem` defaults `tip` — the hoverable-points route's
formatter — to `'x: {x:.3g}\ny: {y:.3g}\ndata={data}'.format`.

Measured 2026-09-14: the reference adult, sevoflurane delivered at 0.02
(1 MAC), the shipped column budget over a one-hour axis, `.3g` applied to the
drawn y as `ScatterPlotItem` would apply it and `format_percent` applied to the
same value. Four instants of the first hour:

| Instant | Compartment | `.3g` on the drawn y | This readout |
| --- | --- | ---: | ---: |
| 48.3 s | Alveolar | `0.262` | `0.26%` |
| 48.3 s | Muscle | `0.000656` | `<0.01%` |
| 48.3 s | Fat | `3.52e-05` | `<0.01%` |
| 289.9 s | Fat | `0.00116` | `<0.01%` |
| 1208.1 s | Fat | `0.00888` | `0.01%` |
| 3600.0 s | Alveolar | `1.54` | `1.54%` |

Three separate defects, and the third is the one that would not be noticed:

- **Resolution.** `3.52e-05` carries five decimal places past the resolution
  this document derives, on the compartment where the readout row deliberately
  refuses to print a number at all. A reader comparing the hover against the
  panel would find them disagreeing about whether the value is known.
- **Units.** `.3g` prints no unit. The chart carries a percent axis and a MAC
  axis, so a bare `1.54` is ambiguous between two scales that differ by a
  factor of about two for sevoflurane; `3.52e-05` is worse, being equally
  readable as a fraction of an atmosphere, a hundredfold out.
- **A varying number of decimals.** Three significant figures gives two
  decimals at `1.54`, three at `0.262` and six at `0.000656`. The readout row
  is fixed at two, and the whole of § "Displayed precision" is the argument for
  a *uniform* resolution: a display whose precision changes with the magnitude
  of what it shows asserts the model resolves small values more finely than
  large ones, which is the opposite of true.

#### Which series answer a hover, and which do not

The six compartment traces answer, in the form above. The wash-in trace answers
in its own units, because $`F_A/F_I`$ is dimensionless and has neither a
percent nor a MAC reading:

```
Modelled sevoflurane · 20m8s
Wash-in F_A/F_I (alveolar / modelled circuit)
0.71
```

`format_wash_in_ratio` produces the number, and the parenthesis is the caption
`app/wash_in.py` already carries, for the reason stated there: $`F_I`$ is the
modelled circuit rather than the vaporizer dial. A solidus rather than a
division sign, because every non-ASCII character that reaches a reader has to
have been rendered and seen first (`tools/glyph_check.py`), and the sign has
not been.

**The clinical references and the control marks do not answer, and the reason
is interaction rather than content.** The 1 MAC line spans the plot
horizontally and the MAC-awake band is a horizontal region; the control marks
are vertical and full height. All three cross every trace, so making them
hoverable would put an annotation under the pointer whenever a reader aims at a
trace that passes behind one — and the annotations are exactly where a reader
is most likely to want a reading, since a trace crossing 1 MAC is the event the
reference is drawn for. What they would report is also already on screen: the
divisor is stated beside the chart, and each control change is listed with its
old and new value in the input timeline.

#### When it answers

Whenever the pointer is over the plot, running or paused.

**This reverses a restriction that was a property of the toolkit rather than of
the affordance.** `PL-KP7H` withdrew the hover while a run plays, because
Flet's control-tree diff descends into every point's tooltip object on every
frame and the tooltips were half the cost of a saturated frame. A hover that
answers only while paused is a hidden mode: a reader who tries it during a run
gets nothing, concludes the chart is not interactive, and never finds it again.

Qt has no such cost to avoid, by either route the readout could be built on. A
crosshair is driven by the scene's own `sigMouseMoved`, rate-limited through a
`SignalProxy`; hoverable points carry a `tip` callable evaluated when the
pointer arrives rather than a tooltip object stored per point. Both cost per
pointer event, and neither is a function of how many points are drawn. Nothing
has to be withdrawn, so there is no mode to announce and no caption to write:
the affordance is discoverable by being present.

**It is not a default, though, and that is what has to be checked rather than
assumed.** `ScatterPlotItem` ships `hoverable` set to `False`, and a plotted
line carries no hover of its own at all, so a port that says nothing about
this loses the affordance outright rather than inheriting it. "Every
capability the Flet build has, the Qt build has" is the parity it is owed
under.

At high playback the reported value moves as the run does, and that is correct
rather than a defect to design around — every other readout in the interface
moves too, and a reader who wants to study a value pauses, which is what they
would do in any case. What is not acceptable is the affordance being absent
while they look for it.

**Built on pyqtgraph as the nearest drawn point** (`PL-G59B`, 2026-09-14):
`app/chart_frame.py` holds the derivation above as code — `format_trace_hover`
and `format_wash_in_hover` produce the three lines, and `nearest_trace_point`
answers only for a compartment the reader has left shown, within a pixel
radius of a point the plot actually draws — and `app/qt_chart.py` shows it
wherever the pointer is, running or paused. The instant on the first line is
stated at the step the run advances by, `HOVER_INSTANT_RESOLUTION_S`: a drawn
column sits wherever the anchored grid puts it, and the state reported is the
state at exactly that instant, but printing it to four decimals would claim a
resolution no other display on the screen has. `tests/unit/test_chart_frame.py`
holds the worked example above verbatim, and
`tests/integration/test_qt_chart.py` holds the rendered readout against a real
run.

## Assumptions

Version v0.1.0 assumes:

- every modeled compartment is perfectly mixed;
- each tissue group is perfusion limited;
- partition coefficients are constant;
- tissue volumes and flow fractions are constant;
- outgoing pulmonary blood equilibrates with alveolar gas;
- the alveolar gas volume is constant — uptake removes agent from the
  compartment without removing volume from it, and no inspired flow replaces
  what left. This is the assumption that excludes nitrous oxide, simultaneous
  gases and the concentration and second-gas effects, and "Alveolar gas"
  measures what it costs and what lifting it would take;
- inspired gas is circuit gas — one gas-phase state $`F_I`$ between the
  vaporizer and the alveoli, there being one perfectly mixed circuit with no
  dead space and no separate limbs (see "Model boundary");
- tissue venous blood equilibrates with its tissue group;
- carrier gases do not affect agent kinetics;
- temperature is constant;
- ambient pressure is constant, and it is one atmosphere — 760 mmHg. Every
  concentration in this model is a fraction of that pressure, so the model is
  specified at sea level and nowhere else; the note below this list is what
  that buys and what it costs;
- there is no metabolism;
- there is no chemical degradation;
- there is no anesthetic reaction with circuit materials;
- there is no vaporizer or machine delivery delay beyond the modeled circuit;
- settings remain constant within each numerical step; and
- the selected reference patient does not change physiologically during a run.

**What one atmosphere buys, and why nothing in the model is wrong today.** A
gas-phase fraction and a partial pressure are the same quantity up to the
ambient pressure, so fixing that pressure at 760 mmHg makes the two
interchangeable: $`F_A = 0.02`$ is 15.2 mmHg, and no statement in this
document has to say which of them it means. That identity is what the rest of
the specification is built on — "Concentrations" stores every state as a
dimensionless fraction on its strength, the interface displays each one as a
percent of one atmosphere, and $`\mathrm{MAC}_\%`$ divides one sea-level
percent by another.

**The delivered-concentration control is where that assumption does the most
work.** It is a vaporizer dial rather than a modeled gas state
(`app/control_record.py`'s `ControlInput.DELIVERED`, whose recorded changes carry
the unit *fraction of 1 atm*), and a dial position means a partial pressure
— the quantity that produces the anesthetic effect — only once the ambient
pressure is known. At 760 mmHg it means the *same* partial pressure whichever
class of vaporizer the dial belongs to, which is why this model needs no
device-class parameter and why no equation, stored value or displayed number
here is wrong. Away from 760 mmHg the two classes diverge, and in opposite
directions: that is a limit on where this model applies rather than a defect
in it, and "Known limitations" below records it. A later reader should not
"fix" this.

## Known limitations

This model does not model:

- a separate arterial blood-mixing compartment (arterial blood is flow-limited and equals alveolar gas at every instant, matching the Gas Man reference simulator's mammillary structure — see "Model boundary");
- lung tissue and pulmonary blood — no compartment represents either, and together they are a store worth about a fifth of every agent's fast pool (the note below this list sizes it);
- halothane, enflurane, ether, or xenon (isoflurane and desflurane were added in v0.2.0; see "Parameter provenance");
- nitrous oxide;
- simultaneous gases;
- concentration or second-gas effects;
- absorption of agent by the breathing circuit's own plastics and rubber (the note below this list measures it, and it is strongly agent-dependent);
- vaporizer interlocks;
- switching between volatile agents;
- direct anesthetic injection;
- automated end-tidal control;
- dead space;
- airway sampling delay;
- multiple alveolar units;
- shunt;
- ventilation-perfusion mismatch;
- diffusion limitation;
- metabolism;
- compound A or other degradation products;
- renal or hepatic dysfunction;
- cardiopulmonary bypass;
- ECMO;
- hypothermia;
- altitude, or any ambient pressure other than the 760 mmHg fixed under "Assumptions" — the notes below this list are what that excludes;
- age-dependent MAC;
- individual variation in awakening concentration (the chart's MAC-awake band is a population value at one standard deviation, never a threshold for the simulated patient — see "MAC-awake as a chart reference");
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
(`PL-L2F2`). Nitrous oxide, simultaneous gases, and concentration or second-gas
effects read as three independent features to be added, and are not: all three
are blocked by the fixed alveolar volume that "Alveolar gas" and "Assumptions"
declare, and lifting it reaches all three at once. The distinction is worth
stating because the shortcut it rules out looks reasonable — a session scoping
nitrous oxide from this list alone would plan it as a second agent object
beside the volatile, meet the coupling late, and be tempted into a partial fix
whose $`F_A`$ curve is plausible and wrong by tens of percent through
induction. "Alveolar gas" carries the arithmetic that separates the two cases
and the two standard formulations that lift the constraint.

**Lung tissue and pulmonary blood are an omitted store worth about a fifth of
the fast pool.** The gas-exchange boundary here is the alveolar gas
compartment, whose partial pressure arterial blood is taken to carry unchanged;
the lung's own tissue, and the pulmonary blood in transit through it, are
represented by nothing. Sized on round physiologic figures while working
`PL-73G7` — 1 kg of lung tissue at a tissue:blood ratio of 1.2, and 1.8 L of
pulmonary and arterial blood — that store is worth 20.1% of desflurane's fast
pool, 19.7% of sevoflurane's and 23.4% of isoflurane's.

It is invisible in the wash-in direction, which is why nothing before the
open-circuit diagnostic surfaced it: the store equilibrates fully within about
thirty minutes, so it does not appear in $`F_A/F_I`$ at all, and it acts only
early in an elimination. The figures stay where they were measured —
"Desflurane's residual, and why the parameter file was not changed" weighs them
against the other candidate explanations of one specific disagreement, and a
second copy here would be a second thing to keep true. What this list carries is
the magnitude, because a reader sizing what the model leaves out should not have
to find it inside an argument about one agent.

**The circuit's own walls absorb agent, and the model's circuit is inert.**
`BreathingCircuit` solves an ideal, well-mixed volume whose walls do nothing —
agent enters with fresh gas and leaves with the exhaust. Targ, Yasuda and Eger
measured what a real one does (*Anesth Analg* 1989 Aug;69(2):218–25, PMID
2764290; the companion of the tissue paper this project's coefficients come
from). Their Table 1 gives plastic/gas and rubber/gas partition coefficients
after 6–9 weeks' equilibration, in the order desflurane, sevoflurane,
isoflurane, halothane:

| component | desflurane | sevoflurane | isoflurane | halothane |
| --- | ---: | ---: | ---: | ---: |
| Y-piece (polypropylene) | 6.67 | 7.68 | 10.6 | 19.1 |
| circuit tube (polyethylene) | 16.2 | 31.2 | 57.9 | 128 |
| reservoir bag (latex) | 19.3 | 29.1 | 48.9 | 190 |
| bellows (black rubber) | 10.4 | 22.6 | 42.9 | 199 |
| endotracheal tube (PVC) | 34.7 | 68.5 | 114 | 233 |
| mask pad (PVC) | 51.7 | 104 | 170 | 323 |

The ranking held at every equilibration time from 7.5 min to 9 weeks, so **the
inert circuit is most nearly true for desflurane and least for halothane** — an
omission whose size depends on which agent is loaded, which is unusual on this
list and is why it is stated rather than left implied. Measuring washin and
washout in a real circuit at 0.5–5 L/min inflow against the ideal exponential,
the same study found desflurane's curves "closely approximated the maximal
possible theoretical rates" while the more soluble agents lagged.

Two things a reader should take from that and no more. The authors' own
conclusion is that this absorption "should not hinder induction of or recovery
from anesthesia" for desflurane, so the simplification is defensible rather than
a defect; and the coefficients above **overstate** the effect during a case,
because equilibration is nowhere near complete in the hours an anesthetic lasts
— the paper says so directly. What the model cannot show is the early lag a real
circuit adds for sevoflurane and isoflurane relative to the curve drawn here
(`PL-LS3H`). Adding a wall term is not planned: it would be a second gas store
with its own time constant, and no teaching objective in `ROADMAP.md` asks for
one.

**Desflurane's five-minute washout disagrees with the published human
measurement, and no admissible parameter closes it.** With the rebreathing
circuit removed as a diagnostic, this model reproduces sevoflurane's and both
isoflurane cohorts' published $`F_A/F_{A0}`$ at five minutes and washes
desflurane out 2.33 published standard deviations too *fast*. It is the one
place in this repository where a comparison against a human measurement fails
in the direction that overstates recovery, and a learner reading desflurane's
early washout as a physiologic prediction would expect a faster fall than
Yasuda's volunteers showed. "Desflurane's residual, and why the parameter file
was not changed" carries what was ruled out — the tissue and blood
solubilities, the operating point, the fast capacity this model omits, a
non-ideal lung, both readings of the published apparatus (circuit-style
rebreathing and the 50 ml of series dead space its methods section actually
describes), and end-tidal sampling bias, struck on a human measurement of that
gradient which runs the other way with solubility and reverses sign through an
elimination. One hypothesis is left and this project cannot test it: the
published value itself. It is
recorded rather than corrected because every value that would close it is
outside what the human measurements support.

**Dead space is an omission with a known exchange rate, which is unusual on
this list.** The model ventilates the alveolar compartment continuously and
has no tidal structure, so neither anatomic nor apparatus dead space is
represented. But a *series* dead space is exactly equivalent to a reduction in
alveolar ventilation: over one breath the dead-space volume re-enters the
alveoli at $`F_A`$ and leaves at $`F_A`$, netting to nothing, so a dead space
$`V_D`$ at rate $`f`$ is worth $`\dot V_A - V_D f`$ and nothing else.
"Desflurane's residual, and why the parameter file was not changed" carries the
derivation and the measurement that used it. Two consequences for a reader.
First, the alveolar ventilation control already *is* the dead-space control,
provided the value entered is a true alveolar ventilation rather than a minute
ventilation; the interface names it "Alveolar ventilation" for that reason, and
a user who enters a minute ventilation there has overstated gas exchange by the
whole of the dead space. Second, what this model
cannot represent is not dead space but **parallel** inhomogeneity: unequal
ventilation-perfusion ratios across alveolar units, which the next three
bullets name and which no single ventilation figure reproduces.

**Cardiac output and the three perfusion fractions are held fixed under
anesthesia, and a real anesthetic moves them.** $`Q`$ and each
$`\text{perfusion fraction}_i`$ are constants for the whole of a run. $`Q`$ is
a user control and nothing else can change it; the three fractions are not a
control at all. A volatile anesthetic is itself a cardiovascular depressant,
so the model holds fixed exactly the quantities its own subject matter acts
on, and the consequence lands on the curve a learner is reading: the tissue
time constants are $`\tau_i = V_i\lambda_{i:b}/Q_i`$, so a flow that fell
under anesthesia would *lengthen* every tissue's equilibration for as long as
the agent was being given. That direction is against the intuition that more
agent means faster equilibration, which is why it is stated here rather than
left to the "hemodynamic response" bullet above.

**It is not modeled because the human volunteer data do not describe a
function this model could carry.** Three studies of healthy volunteers,
anesthetized without surgery and measured against their own awake baseline:

- Weiskopf RB, Cahalan MK, Eger EI 2nd, Yasuda N, Rampil IJ, Ionescu P,
  Lockhart SH, Johnson BH, Freire B, Kelley S. *Cardiovascular actions of
  desflurane in normocarbic volunteers.* Anesth Analg 1991;73(2):143-56.
  PMID 1854029. Desflurane alone at 0.83, 1.24 and 1.66 MAC in 12 men:
  **cardiac index did not change**, although stroke volume index fell and
  filling pressure rose at every concentration - myocardial depression with
  cardiac output maintained.
- Cahalan MK, Weiskopf RB, Eger EI 2nd, Yasuda N, Ionescu P, Rampil IJ,
  Lockhart SH, Freire B, Peterson NA. *Hemodynamic effects of
  desflurane/nitrous oxide anesthesia in volunteers.* Anesth Analg
  1991;73(2):157-64. PMID 1854030, doi:10.1213/00000539-199108000-00008. The
  **same** volunteers, in the same crossover, with 60% nitrous oxide carrying
  0.5 MAC of the total: cardiac index now fell dose-dependently.
- Malan TP Jr, DiNardo JA, Isner RJ, Frink EJ Jr, Goldberg M, Fenster PE,
  Brown EA, Depa R, Hammond LC, Mata H. *Cardiovascular effects of sevoflurane
  compared with those of isoflurane in volunteers.* Anesthesiology
  1995;83(5):918-28. PMID 7486177, doi:10.1097/00000542-199511000-00004.
  Sevoflurane: cardiac index fell at 1.0 and 1.5 MAC and **returned to
  baseline at 2.0 MAC** as systemic vascular resistance fell. Isoflurane
  behaved similarly, and in both the depression diminished with prolonged
  administration and with spontaneous rather than controlled ventilation.

Read together: the *sign* of the cardiac-output change depends on the carrier
gas, the dose-response is **not monotonic**, and the effect changes with time
at a fixed dose and with the mode of ventilation. This model has no second
gas, no ventilation mode, no surgical stimulus and no pharmacodynamic layer of
any kind, so it could carry none of those dependencies - it could only carry a
monotonic, time-invariant $`Q(\text{dose})`$, which is a relationship the
literature above does not show. Teaching one would be worse than holding the
flow fixed and saying so. The regional half is weaker still: the reachable
measurements of how anesthesia redistributes flow between the vessel-rich,
muscle and fat groups are largely animal, and the note below on the fat
group's perfusion is what the human record supports even at rest.

**What a learner gets instead is the control.** Cardiac output is on the
interface, so the lesson - a higher output carries more agent away from the
lung, stores more of it and slows the rise of $`F_A`$ - is reachable by moving
it and watching, which is also how the model's own directional gates assert it
(`tests/reference/test_sevo_patient.py`). What is absent is the *automatic*
coupling from the agent to the flow, and a reader should supply that
themselves.

**This is where the model stands, not a question closed.** `ROADMAP.md`'s
planned-milestone item 35 carries the coupling as a possible future feature,
and carries it as an *option* a user would turn on rather than as a change to
what a run does by default - which is the disposition the evidence above
argues for, since an overlay may state its own uncertainty where a model's
standing behaviour cannot. `PL-8GV5` records how that was decided: the
measurements here are a session's, the direction is the project owner's
(2026-09-13).

**The MAC divisor is a limitation of the display, and a named one.** The
second display unit divides by a tier-3 `mac_percent`, and "Delivery-limit
and MAC parameters" measures the gap: against Mapleson's age-40 meta-analytic
values the stored sevoflurane MAC reads 10% low and the stored desflurane MAC
10% high, so a sevoflurane-versus-desflurane comparison in MAC multiples is
displaced by about 22% purely by the choice of MAC source. The direction is
consistent within an agent and does not change any curve's shape or timing —
it rescales one agent's MAC axis against another's — but it is larger than
either source's own confidence limits, and a reader comparing two agents at
"1 MAC" is comparing two doses that the primary literature would not call
equipotent to that precision. The interface displays the divisor for exactly
this reason. Moving all parameters to primary sources is `ROADMAP.md`'s
planned-milestone item 31.

**The two omissions above are what bound the supported run length.** Metabolism
and the fat group's flow are both negligible over a case and neither is
negligible over days, which is why a run is supported to 24 hours and the step
past it is refused rather than taken. "Supported run length" argues the number
and gives the measured extent of sevoflurane's metabolism; a longer run is not
merely unvalidated but increasingly a display of what this model leaves out.

**The fat group is perfused about twice as fast as the reachable resting
measurement, and that acts on the shape of a curve.** The fat flow fraction is
tier 3 like every other parameter in the reference patient, and
`reference_adult.json` now carries the comparison: Heinonen et al.'s positron-
emission-tomography measurement of resting subcutaneous adipose perfusion in
healthy young women is close to half what this model's stored fraction
implies, with the file's note giving both figures and the volume-to-mass
conversion between them. The fat group's time constant is proportional to its
volume and partition coefficient and inversely proportional to its flow, so
halving the flow would roughly double that constant. Both values are long
against any simulated case, so the fat compartment stays far from equilibrium
either way and no displayed curve reaches a wrong endpoint; what moves is how
much agent fat has taken up by the end of a case, and therefore the slow tail
of washout, by something close to a factor of two. A learner reading the fat
trace as a physiologic prediction rather than as this parameter set's
behaviour would over-estimate fat loading. The measurement does not settle it
— one depot in six subjects against a whole-body lumped compartment — which is
why nothing was changed and the gap is recorded instead.

**Cardiac output does not scale with the patient, and the reference weight is
a label rather than an input.** `default_cardiac_output_l_min` is a stored
5.0 L/min and `weight_kg` is read by no equation, so editing the weight changes
nothing this model computes. Two published figures sit either side of the
stored value, **and they are not evidence of the same kind.** Lowe and Ernst's
own cardiac-output relation — the upstream the Gas Man Workbook names, now read
at the source — gives $`0.2M^{3/4}`$, which is 4.84 L/min at 70 kg; it is
**derived rather than measured**, being Brody's 1945 interspecies
oxygen-consumption allometry divided by an arteriovenous oxygen content
difference assumed constant across mammals, and "Parameter provenance" above
carries the derivation step by step. Cattermole et al.'s 686 subjects in the
50–75 kg band give a **measured** median of 5.51 L/min in the weight band this
file's patient sits in. So the stored 5.0 is not bracketed by two comparable
observations: one side is a human measurement and the other is an interspecies
extrapolation, and a reader weighing them equally would be weighing them wrongly.
**The fixed value is kept, on the project owner's decision of 2026-09-08**
(`PL-YKSM`), and the reason is structural rather than a preference between those
two numbers — but the asymmetry is worth stating, because the number being
declined is the weaker of the two.

A time constant is $`V_i \lambda_{i:b} / Q_i`$ and this model stores
compartment volumes as fixed litres, so scaling only the flow would make
$`\tau \propto M^{-3/4}`$: a heavier patient would equilibrate *faster* and a
lighter one more slowly, which is an artifact of scaling one half of a coupled
pair rather than a physiologic prediction. Measured at the shipped sevoflurane
coefficients, a 20 kg child under a weight-scaled cardiac output alone would
equilibrate about 2.6 times more slowly than the reference adult — the opposite
of the direction paediatric inhalational uptake runs in. (Salanitre and
Rackow's *Anesthesiology* 1969;30(4):388–94 study of pulmonary exchange in
infants and children is the classic reference for that direction; its PubMed
record was retrieved here and its text has not been read, so no figure is taken
from it.) Doing half of the scaling is therefore worse than doing none of it,
and adopting the relation on the one patient that exists would have lengthened
every time constant by 3.32% and changed nothing else.

**What follows from that is narrower than "the weight is unused".** This model
describes one 70 kg adult. It is not a paediatric, obese, or otherwise
weight-varying model, and no field in the interface makes it one — a run is
that adult's run whatever the reference weight reads. Weight-varying physiology
is `ROADMAP.md`'s planned-milestone item 30, and it is a package: compartment
volumes, alveolar volume, alveolar ventilation, the perfusion fractions and MAC
by age move together or none of them should.

**Ambient pressure is not modelled, and away from one atmosphere the
delivered-concentration dial stops meaning one partial pressure.**
"Assumptions" above fixes ambient pressure at 760 mmHg and says what that
identity buys. What it costs is stated here: this model is specified for sea
level. A user in Denver (about 630 mmHg) or Mexico City (about 585 mmHg) who
sets 6% desflurane in this simulator and 6% on the corresponding real device
is not delivering the same anesthetic, and nothing else in the simulator says
so. The reason is that the delivered-concentration control is a vaporizer
dial, and the two classes of vaporizer this project's three agents are drawn
from respond to falling ambient pressure in opposite directions.

**Variable bypass — sevoflurane and isoflurane here.** The class of the
Dräger Vapor 2000, Sevotec 5, Isotec 5 and Penlon Sigma Delta. Fresh gas is
split between a bypass channel and a vaporizing chamber whose effluent leaves
saturated at the agent's saturated vapour pressure, which is set by
temperature and not by ambient pressure. The dial sets the splitting ratio, so
as ambient pressure falls the output rises in volumes percent while the
delivered *partial pressure* is approximately preserved, and the dial needs no
altitude correction. Boumphrey and Marshall give the approximation as
$`\%_1 = \%_\mathrm{cal} \times P_\mathrm{cal} / P_1`$, worked as isoflurane
dialled 2% at 101.3 kPa delivering 4.05% at 50 kPa — 2.026 kPa of isoflurane
either way.

**Gas–vapour blender — desflurane here.** The class of the Tec 6 and Tec 6
Plus, which desflurane needs at all because it boils at 22.8 °C. The sump is
held at about 39 °C, which fixes desflurane's vapour pressure at about
1460 mmHg — a temperature chosen so that the resulting pressure would clear
the vaporizer's own internal resistances — and pure vapour is injected into
the fresh gas stream; a differential pressure transducer holds the vapour
circuit at the fresh-gas circuit's pressure, so the two flows stay in the
fixed *ratio* the dial sets — "The pressure in the vapor circuit is
electronically regulated to equal the pressure in the fresh gas circuit…
vaporizer output is constant because the amount of flow through each circuit
is proportional" (Andrews and Johnston). Output is therefore a constant
volumes percent and the delivered partial pressure falls with ambient
pressure. Datex-Ohmeda states the
consequence for the operator directly: "Decreased atmospheric pressure, with
altitude, does not significantly affect the concentration of agent delivered
(V/V), but decreases the partial pressure of the agent in the ratio of the
atmospheric pressure to the calibrated pressure of 760 mm Hg. To compensate
for the reduction of vapor pressure output at altitude, the rotary valve must
be advanced to maintain the required agent partial pressure."

**The MAC divisor is a sea-level percent for the same reason.** 1 MAC is a
partial pressure that convention quotes as a percentage of one atmosphere, so
at reduced ambient pressure the percentage needed to reach it rises while the
partial pressure does not. James and White proposed MAPP — minimum alveolar
*partial pressure* — in place of MAC on exactly this ground, which is a
further sense in which the unit described under "MAC multiples as a display
unit" is a sea-level unit rather than a universal one.

**No correction factor is stored, and the $`1/P`$ form above must not become
one.** $`\%_\mathrm{cal} \times P_\mathrm{cal} / P_1`$ is the dilute-vapour
limit of the flow-splitting physics, whose fuller form is
$`F \approx k\,\mathrm{SVP}/(P - \mathrm{SVP})`$ and which reduces to
$`k\,\mathrm{SVP}/P`$ only where $`\mathrm{SVP} \ll P`$. Isoflurane's
saturated vapour pressure is about 240 mmHg at 20 °C, which is not small
against 760: carrying the denominator through gives a delivered partial
pressure that *overshoots* rather than holds — about 16% high at 585 mmHg on
that arithmetic alone, against the flat line the $`1/P`$ form predicts. The
direction of each class's response, and the contrast between the two, are not
in doubt; the magnitude of the variable-bypass compensation is approximate,
which is why this section says *approximately* preserved and why no number is
stored anywhere for it. An implementation of ambient pressure should derive
the variable-bypass case from the agent's saturated vapour pressure rather
than from the $`1/P`$ shortcut, and would owe each agent's SVP a source of its
own; none is stored today.

**Sources for the notes above**, none of which is the authority for any
stored value, there being none:

- Weiskopf RB, Sampson D, Moore MA. The desflurane (Tec 6) vaporizer: design,
  design considerations and performance evaluation. *Br J Anaesth*
  1994;72:474–479. Primary, and the authority for every figure attributed to
  it here: the 22.8 °C boiling point, the 39 °C sump, the 1460 mmHg it fixes
  and why that pressure was chosen, and the ±15% relative (or ±0.5% absolute)
  output accuracy. Supplied by the project owner; read at the source
  2026-09-06 and re-read against the full text 2026-09-08, which is where the
  1460 mmHg is stated twice — once for the sump and once for the regulator
  that reduces it to the fresh-gas pressure. The paper says nothing about
  ambient pressure or altitude, so it is not the source for that behaviour.
- Andrews JJ, Johnston RV. The new Tec6 desflurane vaporizer. *Anesth Analg*
  1993;76:1338–1341. Primary; the flow-ratio mechanism quoted above, which is
  in the abstract.
- James MF, White JF. Anesthetic considerations at moderate altitude. *Anesth
  Analg* 1984;63:1097–1105. Primary; the case for reasoning in partial
  pressures rather than percentages at altitude, and the MAPP proposal. It
  predates desflurane, so it covers the variable-bypass class only.
- Datex-Ohmeda. *Tec 6 Plus Vaporizer* specification sheet AN3307-A/1100,
  © 2000 Datex-Ohmeda Division, Instrumentarium Corp. Manufacturer statement,
  quoted above; it also gives the 1–18% concentration range that
  `max_delivered_concentration_percent` carries for desflurane. Supplied by
  the project owner and read in full 2026-09-06. **Owner-attested**: see the
  note below.
- Boumphrey S, Marshall N. Understanding vaporizers. *Contin Educ Anaesth
  Crit Care Pain* 2011;11:199–203. **Tier 2** under "Source hierarchy": a
  secondary synthesis, taken here for the shape of the explanation and the
  worked example and never as the authority for a number. Its § "Altitude"
  carries both classes side by side. Supplied by the project owner and read in
  full 2026-09-06. **Owner-attested**: see the note below.

**Two of those five are owner-attested rather than checkable, and this says
which.** `docs/references/` cannot hold them: the repository is public, so a
file placed there is redistributed rather than read privately, and
`docs/references/README.md` § "Redistribution" is the rule that follows from
it — two publisher-copyright full texts were removed on 2026-09-06 for exactly
that reason (`PL-SHG5`). The three journal articles above are reachable by any
reader through their DOI or PMID, and the Weiskopf figures were re-read
against the full text on 2026-09-08. The Datex-Ohmeda specification sheet and
the Boumphrey and Marshall article were not: both were read in a working
session from copies the project owner supplied, and nothing in this repository
can re-open either. So the passage quoted from Datex-Ohmeda, the 1–18% range
beside it, and the worked example attributed to Boumphrey and Marshall rest on
that reading alone. Nothing stored depends on any of them; a reader wanting to
verify one has to reach the document itself.

## Release gate

**This is the standing gate every release passes, not one version's.** It was
written as v0.1.0's and kept that lead-in for four releases while entries were
added to it — most recently the published wash-in validation, which arrived in
the v0.3.0 window — and several criteria name agents and cohorts that did not
exist until v0.2.0. A heading naming a version is a second thing to keep true,
which is the failure `PL-C1KK` records one section over; the criteria beneath
were already generic, so the lead-in is what changed (`PL-8PZ1`).

A release is complete only when:

- all parameter values and sources are present;
- no scientific `TBD` markers remain;
- v0.0.2 circuit reference tests still pass;
- unit, integration, invariant, and independent reference tests pass;
- the published wash-in validation passes for every agent and cohort (the
  elimination comparison in the same module is a regression band, not an
  agreement claim, and is deliberately not a release gate);
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
