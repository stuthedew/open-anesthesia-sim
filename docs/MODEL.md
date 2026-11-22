# Volatile-agent patient uptake and distribution model

## Status

The simulator is an educational model (§ "Intended use").

This document specifies the scientific model that the simulator implements. Its
equations and compartment structure have not changed since v0.1.0, and every
supported agent shares them.

A separate document, `docs/INTERFACE.md`, states what the interface must show
and do, including its controls and the outputs that must be displayed. It
also gives the ranges of the settings, and the length of a run, over which the
model is claimed to represent a patient (`docs/INTERFACE.md`
§ "Supported input ranges" and `docs/INTERFACE.md` § "Supported run length").

A second document, `docs/VERIFICATION.md`, states how the simulator is shown
to solve these equations correctly: the numerical method and the simulation
step it supports, the conservation of agent mass, the required invariants and
tests, and the release gate. It also holds two things a clinician may want
before trusting a displayed value. The comparison of the model's output with
measurements in volunteers is in `docs/VERIFICATION.md` § "Published wash-in
and elimination validation test". The ways the display could be misread, and
what prevents each, are in `docs/VERIFICATION.md` § "Reasonably foreseeable
misuse, and the hazards the presentation carries".

A statement here that gives a version has been true *since* that version. The
project's roadmap (`ROADMAP.md`) lists the current release in its version table.

Release v0.0.2 modelled the wash-in and washout of an ideal breathing circuit
with no patient. Its reference tests are in `docs/VERIFICATION.md` § "Preserved circuit reference tests". v0.1.0, the “Sevo works” milestone, was the first sevoflurane model with a patient. The agent follows this path:

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

### What a named test, a missing test and a date tell the reader

When a statement in this document, in `docs/VERIFICATION.md` or in
`README.md` is about the simulator's code, data or output, it names the thing
it describes. Where no test covers the
statement yet, it says so in a fixed form, ``no test yet (`PL-XXXX`)``, and the
parenthesis names the open work item for adding the test.

Each name is set in fixed-width type and points to a test, a file, or a part of
the code or its data. A number repeated from the simulator's data is linked to
the stored value. An automatic documentation check looks up each name and link.
Without that check, a sentence would still read as true after the test it names
was renamed, the data it describes was removed or the value it repeats was
changed.

When a statement carries a date, sits under a dated heading or sits in a
released version's section, it records what was true on that date. It need not
name a test, and nothing checks it against the code. A later fact gets its own
date, and the dated statement is never changed to carry it.

## Purpose

The “Sevo works” milestone (v0.1.0) must demonstrate:

- circuit wash-in and washout;
- ventilation between the breathing circuit and alveolar gas;
- uptake from alveolar gas into blood;
- cardiac-output-dependent delivery to tissues;
- perfusion-limited distribution into vessel-rich, muscle, and fat groups;
- mixed-venous return to the lungs;
- dynamic changes in fresh gas flow, delivered concentration, alveolar ventilation,
  and cardiac output;
- identical results from identical inputs; and
- explicit conservation of agent mass.

v0.1.0 modeled sevoflurane only. v0.2.0 added isoflurane and desflurane as
selectable agents, using the same equations (see § "Status" and
"v0.2.0: isoflurane and desflurane" under § "Parameter provenance").

## Intended use, and the safety class this project holds itself to

Two medical-device standards judge every hazard and every software safety class
against what the product is intended for: ISO 14971, for risk management, and
IEC 62304, for software.

### Intended use

This is a teaching simulator for volatile-agent uptake and distribution. It is
not intended for clinical prediction, dosing, monitoring a patient, or any other
use as a medical device. It is intended for anesthesia clinicians, trainees,
and students. It helps them
build intuition about how agent concentration moves between the breathing
circuit, alveolar gas, blood, and the tissue groups, under management that the
learner chooses. In particular, it makes visible the compartments that no
clinical monitor displays: vessel-rich, muscle, fat, and mixed venous.

**The simulator is not intended for use with an identifiable patient's data.**
It is meant to be run on hypothetical or illustrative parameters. It is not
intended for entering, importing, or reproducing an identifiable patient's
parameter values, or for informing the management of a specific patient.

This limit concerns the *data*, not nearness to a patient. Keeping the
simulator open on a computer during a case is ordinary teaching use, with no
hazard of its own. A run built from a particular patient's weight, age, and
cardiac output is a prediction about that patient, whatever the simulator's
window is labelled.

### What keeps a real patient's data out of a run

Two safeguards protect today against the misuse that § "Intended use"
excludes:

1. The use statement at the foot of the window says that the simulator is for
   teaching and is not a clinical prediction, monitoring or dosing tool. In
   each built-in Workspace it stays in view, however the page scrolls.
2. The simulated patient is always the same reference adult. No control accepts
   a weight, age, sex, height or body composition. Every run keeps that
   patient's compartment volumes and perfusion fractions, whatever the learner
   sets. The planned patient factors (`ROADMAP.md` planned-milestone item 30)
   will remove this safeguard.

A learner can still set cardiac output or alveolar ventilation to a value
measured in a real patient, because changing them is a core teaching feature.
The run then shows the reference adult at that flow, not a prediction for that
patient. Only the use statement guards against reading the run as one.

**For developers.** The use statement is `USE_DISCLAIMER_TEXT` in `app/dashboard_frame.py`,
and the reference adult is stored in `data/patients/reference_adult.json`. A test checks each
way a patient could get into a run today, so adding patient factors will make it fail
(`test_every_run_simulates_the_shipped_reference_adult`). The change that adds them must then
rewrite this section and the hazard table's row for a real patient's data.

### Software safety classification: Class C, for the whole application

This project assigns **Class C to the whole application**, the interface
included. IEC 62304 § 4.3 classifies software by the severity of the harm that
its failure could contribute to. **Class A** applies where no injury or damage
to health is possible, **Class B** where injury is possible but not serious, and
**Class C** where death or serious injury is possible. The class depends on
severity alone (Annex B.4.3). Where software sits in a sequence of events
leading to a hazardous situation, the standard sets the probability of its failure to 1, rather than estimating it. So an argument that a failure would rarely happen does not justify a lower class.

A failure of the interface could contribute to injury, which rules out Class A.
A correct number is still a safety failure if the interface shows it with the
wrong units, label, patient context or model version, or after it has gone out
of date. The interface also has safety features, such as the distinction
between a halted and a paused run, the rule on displayed precision and the
ISO 5360 agent colours.

**For developers.** A lower class for any part of the application would save no
work, because this project checks all its code the same way. Class A, for
example, excuses software from detailed design, unit verification and
integration testing.

Code that looks cosmetic cannot be split off into a lower class, because it
carries clinical meaning. The chart's frame (`app/chart_frame.py`) decides what
a chart line claims about a run. The styling file (`app/theme.py`) defines the
ISO 5360 agent colours. The rule for which instants the chart draws is a safety
feature of the interface. The chart computes the run's exact state at each
instant that it draws, and every control change is one of those instants
(`docs/INTERFACE.md` § "Interface boundary").

A split would pay off only where the exempted part is large, genuinely
non-clinical and costly to verify. None of those holds now.

### This is an engineering bar, not a regulatory status

The project adopts Class C for the whole application as an engineering standard,
like WCAG 2.2 AA for accessibility (`docs/INTERFACE.md` § "Color contrast, and the standard this
interface is held to"). The project claims no conformance to IEC 62304 or to a
quality management system, and no regulatory status. Writing the class down gives
anyone reviewing the code a bar to hold it to.

The class does not settle whether the simulator is a medical device. FDA
publishes examples of software functions that are *not* medical devices. They
include software intended for health care professionals as educational tools
for medical training. One example is "games that simulate various cardiac
arrest scenarios to train health professionals in advanced cardiopulmonary
resuscitation (CPR) skills" ([FDA, Examples of Software
Functions That Are NOT Medical Devices](https://www.fda.gov/medical-devices/device-software-functions-including-mobile-medical-applications/examples-software-functions-are-not-medical-devices),
and the guidance "Policy for Device Software Functions and Mobile Medical
Applications"). Whether software is excluded depends on its intended use, not
on which physiologic parameters it accepts. To qualify, the software must not
support a health professional's assessment of a *specific patient*. That is why
the intended-use boundary above is drawn at a specific patient's data.

Using this simulator outside the intended use above is **reasonably foreseeable
misuse** under ISO 14971:2019, the risk-management standard for medical devices.
Its clause 5.2 requires documenting such misuse. The hazard table
(`docs/VERIFICATION.md` § "Reasonably foreseeable misuse, and the hazards the presentation carries")
has a row for it. Two safeguards protect against this misuse, and tests
enforce them (§ "What keeps a real patient's data out of a run").

**For developers.** Before you revise this section, check IEC 62304 and ISO 14971
directly. They are not open access, so the project read their clause structure,
the three class definitions and Annex B.4.3's probability rule from secondary
summaries. The Class C conclusion does not depend on the standards' wording, but
the clause numbers cited here do. The project read the FDA material at the source.

## Model boundary

The modeled system contains:

1. one ideal, perfectly mixed breathing circuit;
2. one ideal, perfectly mixed alveolar gas compartment;
3. one venous blood pool;
4. one vessel-rich tissue group;
5. one muscle tissue group; and
6. one fat tissue group.

Agent and carrier gas enter only with the fresh gas, and mixed circuit gas
leaves only through the circuit exhaust. Apart from this inflow and outflow, the
circuit and the patient form a closed path in which gas recirculates. The model
has no metabolism or other chemical destruction of the agent.

**The breathing circuit is semi-closed.** The exhaust runs whenever fresh gas
flows, at exactly the fresh-gas rate. The model's equations do not describe
closed-circuit operation, whose balance of agent in and out differs. § "Breathing circuit"
explains this limit and estimates its size, and § "Known limitations" lists it.

**Exchange with blood is perfusion-limited.** Agent moves between blood and
alveolar gas, and between blood and each tissue group. Blood leaves the lung or
the tissue at equilibrium with it, so the barrier between them never limits how
fast agent moves. The rate is set by the blood flow, the agent's blood:gas
partition coefficient and the difference in partial pressure, as the uptake
equations in § "Governing equations" show. The model does not represent
diffusion-limited exchange, in which blood leaves before it has equilibrated and
the barrier limits the rate. Jones and Rowland-Yeo call perfusion-limited and
diffusion-limited tissue exchange "perfusion rate-limited" and "permeability
rate-limited". They give the first as typical of small lipophilic molecules,
which the volatile agents are (Jones HM, Rowland-Yeo K. Basic concepts in
physiologically based pharmacokinetic modeling in drug discovery and development.
*CPT Pharmacometrics Syst Pharmacol* 2013;2:e63, doi:10.1038/psp.2013.41).
Yasuda et al. assumed perfusion-limited delivery to the tissues when they
fitted sevoflurane and isoflurane kinetics in volunteers (*Anesth Analg*
1991;72:316-24, p. 319).

Arterial blood is not a separate mixing compartment. The model has no shunt and
only one alveolar compartment, so it has no ventilation-perfusion mismatch, and
all arterial blood has passed through the lung's perfusion-limited exchange with
alveolar gas. Arterial partial pressure, as a fraction, is therefore defined as
the alveolar fraction, $`F_a \equiv F_A`$, with no arterial volume, mixing delay,
or value of its own. This identity is a deliberate simplification of the model,
not a property of the agents. In patients, the arterial partial pressure runs
below the end-tidal one during administration, as Carpenter and Eger measured
(`docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not changed").
§ "Known limitations" lists this simplification.

Most of this project's agent and patient parameters come from the Gas Man
simulator (§ "Parameter provenance" says which), whose structure matches this
model's in two respects. In Gas Man,
each tissue group exchanges agent only with blood, at a perfusion-limited rate,
and arterial partial pressure is displayed without being tracked as a
compartment. The *BMC Anesthesiology* paper below describes Gas Man's patient
as four compartments, the lung and the vessel-rich, muscle and fat groups, with
the circuit as a fifth. Gas Man's parameter file also gives a venous volume
(§ "Parameter provenance"). See:

- Philip JH. Gas Man Version 4.1 Teaches Inhalation Kinetics. Society for
  Technology in Anesthesia. <https://www.stahq.org/files/7913/2743/1066/Abstract_57.pdf>
- Do distribution volumes and clearances relate to tissue volumes and blood
  flows? A computer simulation. BMC Anesthesiology.
  <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1508141/>

Inspired gas is not a separate compartment. The circuit is perfectly mixed and
has no dead space and no separate inspiratory and expiratory limbs, so the gas
the patient inspires *is* the circuit gas, with no transport delay between the
two. The model therefore tracks one gas concentration between the vaporizer and
the alveoli. That concentration is the **inspired fraction** $`F_I`$, the middle
term of the literature's $`F_D \rightarrow F_I \rightarrow F_A`$ cascade.
$`V_C`$ is the circuit's volume, and $`M_C`$ is the amount of agent it holds, so
$`M_C = V_CF_I`$.

Equating inspired gas with circuit gas is an assumption of this circuit model,
not a property of breathing systems in general. It makes the displayed
$`F_A/F_I`$ ratio the textbook curve of inhaled-anesthetic uptake
(`docs/INTERFACE.md` § "F_A/F_I as a displayed ratio").

**For developers.** Before extending the model to a multi-limb system, record
the change in this document. Such a system separates inspired gas from mean
circuit gas, as Lerou and Booij's three-part model does. The two would then be
tracked separately, and this model's single $`F_I`$ would no longer describe
both.

## Assumptions

Every value the model computes rests on these assumptions.

- Every modeled compartment is perfectly mixed.
- Each tissue group exchanges agent only with the blood flowing through it. The
  model therefore omits intertissue diffusion, the direct passage of agent from
  one tissue group to another (see § "Known limitations").
- Partition coefficients, tissue volumes and flow fractions are constant.
- Outgoing pulmonary blood equilibrates with alveolar gas.
- Tissue venous blood equilibrates with its tissue group.
- There is no metabolism.
- The selected reference patient does not change physiologically during a run.
- The alveolar gas volume is constant. Uptake draws agent out of the alveolar
  gas without reducing its volume, and no inspired flow replaces the gas that
  the blood absorbs. This assumption excludes nitrous oxide, simultaneous gases,
  and the concentration and second-gas effects. § "Alveolar gas" gives the size
  of the error and what lifting the assumption would take.
- Carrier gases do not affect agent kinetics.
- Inspired gas is circuit gas (see § "Model boundary").
- The breathing system is a semi-closed circle whose surplus gas valve is open.
  Exhaust outflow equals fresh-gas inflow at every instant, so one fresh gas
  flow, $`\dot V_F`$, is both the delivery rate and the removal rate (see
  § "Breathing circuit").
- There is no chemical degradation.
- There is no anesthetic reaction with circuit materials.
- There is no vaporizer or machine delivery delay beyond the modeled circuit.
- Settings remain constant within each calculation step.
- Temperature is constant. Every stored gas volume is at the one reference
  condition that § "Agent amount" states: 20 °C and 760 mmHg, dry (with no water
  vapour). No equation converts between ambient and body conditions.
  § "Known limitations" gives the size of the resulting error.
  <!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->
- Inspired gas reaches the alveoli undiluted by water vapour, because the
  modeled alveoli hold no water. "Dry" in the reference condition above means
  this same absence of water vapour. Real alveolar gas is saturated with water
  vapour at body temperature. § "Known limitations" gives the size of this
  omission, 47/760, and what correcting it would cost.
- Ambient pressure is constant at one atmosphere, 760 mmHg. Every concentration
  in this model is a fraction of that pressure, so the model applies only at sea
  level.

**At one atmosphere, a fraction and a partial pressure are interchangeable.**
They differ only by a factor of the ambient pressure, so with that pressure
fixed at 760 mmHg, $`F_A = 0.02`$ is 15.2 mmHg. The model relies on this in
three places. It stores every modeled concentration as a fraction with no
unit (see § "Concentrations"). The interface displays each concentration as a
percent of one atmosphere. And a MAC multiple is one sea-level percent divided by
another, the displayed percent over $`\mathrm{MAC}_\%`$.

**More than anything else in the model, the vaporizer control depends on the
ambient pressure being 760 mmHg.** At 760 mmHg, both classes of vaporizer deliver the
same partial pressure at a given dial position, so no equation, stored value
or displayed number here is wrong at sea level. Away from 760 mmHg, the two
classes respond differently, as § "Known limitations" describes.

**For developers.** The vaporizer control is `ControlInput.DELIVERED` in
`app/control_record.py`. Each recorded change to it carries the unit *percent
of 1 atm*. The model has no parameter for the class of vaporizer and needs none
at sea level. A model that adds ambient pressure will need one.

## Conventions

### Time

Times are in seconds in the equations, the model's code and a saved run.
The model keeps its own simulation time and never takes it from the computer's
clock. That clock may still decide when the screen updates.

A run stores each flow as it was set, in liters per minute. Each time the
equations need a flow, the model converts it to liters per second:

$$
\dot V_{\mathrm{s}} = \frac{\dot V_{\mathrm{min}}}{60}
$$

**For developers.** The per-second value of each flow is never stored because
multiplying it by 60 can give a number that differs from the setting. The tissue
flows formed from cardiac output share that difference. Settings rebuilt from
per-second values could therefore describe a run that nobody set up.

#### Simulated time is a count of steps, not a running total

A run moves forward in steps of 1 s, and it takes no step of any other
length. Simulated time is the number of steps the run has completed, so it is
always a whole number of seconds. A computer holds a whole number exactly. So
no instant of a run is a rounded value, and two instants can be compared
exactly.
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->

A run's settings change only between two steps. So a control change takes
effect at the next whole second, and the run records it at that second.
`docs/VERIFICATION.md` § "Supported simulation step" gives what that delay can cost a displayed value.

**For developers.** The model stores the count of completed steps
(`SimulationState.step_count`) and returns it as the simulated time
(`SimulationState.elapsed_s`), a whole number of seconds. A branched run
continues the count of the run it branched from. So its time is still one
count, and is not the instant of the branch plus a second total. Reset sets the
count to zero.

#### The reproducibility guarantee

Two runs with the same inputs are **exactly identical** in every stored value at
any step *n*, which falls at *n* seconds in both. Those inputs are the
starting state, parameters, setting changes and order of events.
Every comparison of one run with another relies on the guarantee. That includes
comparing a branched run with the run it branched from, at every instant they
share. `docs/INTERFACE.md` § "What a branch comparison asserts, and what it does not" says what such
a comparison may and may not claim.

**A slow or busy computer reaches each step later in real time, but computes and
stores the same values as a fast one.** The screen uses the computer's clock to
decide when to update. But the number of steps in each update follows from the
playback rate the user chooses, and is never measured from the clock. The simulation never takes
extra steps to catch up after a slow update, and it reads no clock. An automatic
check keeps the model's code from reading the clock, and from drawing a random
number that differs from run to run.

**Playing a run faster does not make it a different run.** The playback rate is
how much simulated time passes per second of real time. A faster rate takes
more *whole steps* per second of real time, never a larger step. So a case played at
real time and at three hundred times real time takes the same steps, in the
same order, at the same size, and gives exactly the same results sooner.

The guarantee does not cover three things, and none of them is a defect:

- **A different model version.** The guarantee applies within one version of
  the equations and one parameter set. That is why both are versioned.
- **A different installation.** Basic arithmetic gives identical results on
  every computer. But each step also uses an exponential function, whose last
  digit can differ from one installation of the simulator to another.
- **Elapsed real time.** How long a computer takes to reach step *n* is a
  property of the computer. So is how many steps it has reached when a
  wall-clock minute is up. Neither is a property of the model.

**Every value shown, compared or branched from is a state the run stored.** A run
stores the state that each step wrote, one for each second it reaches, and every
reader of a reached second takes that state rather than computing it again
(`docs/INTERFACE.md` § "Each second has one stored state"). So two readers of one
second get exactly the same bits. The one computed state is a preview of a setting
not yet applied, which is only drawn.

**For developers.** Faster playback never enlarges the step, because a larger
step would compute a second solution of the same equations, one that the
guarantee does not cover. A displayed value would then depend on how fast the
user was watching, and no label could fix that.

The check on the model's code is `tools/import_boundary_check.py`. It runs in
`make check` and CI, and it fails the build when any module under
`src/anesthesia_sim/core/` imports `time`, `datetime`, `random`, `secrets` or
`uuid`. If it missed any of these imports, a run could stop being reproducible
while the check still passed. The check stops at `core/` so that the screen
code outside it may use the clock. A table in the check (`BOUNDARIES`) gives
the reason for each entry.

Seeding cannot make `secrets` or `uuid` repeatable. Python's `secrets` module
draws from `random.SystemRandom`, whose `seed()` is documented to do nothing
and whose `getstate()` raises an error. The function `uuid.uuid1()` mixes the
current time with the host's hardware address, so a run that used it would
differ between *machines* as well as between runs.

A caller cannot ask for a step of another length. The method that takes a step
(`SimulationState.advance()`) takes no argument, and the step is the constant
`SIMULATION_STEP_S` in `core/simulation_step.py`.

The model stores each flow in the unit the user set it in
(`UptakeEquationSettings` in `core/governing_equations.py`). Converting to a
per-second flow and multiplying by 60 does not always return the setting. On a
0.1 L/min grid across the supported 0 to 10 L/min range, the round trip fails
for 7 of the 101 cardiac outputs (1.9, 3.8, 3.9 and 7.6 to 7.9 L/min).
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->

The exponential in each step is one `exp()` call, a library function whose last
bit can differ between platforms, Python builds and math libraries. The
propagator is also built from a series and a sequence of squarings, and a
compiler may change the order in which their terms are summed.

### Concentrations

Every concentration that the model computes is a dimensionless
partial-pressure-equivalent fraction. For example, $`F = 0.02`$ represents a 2%
gas-phase concentration.
<!-- not-restated: 2 % -->

The vaporizer dial and MAC are given in percent of an atmosphere. The
conversion between a fraction and a percent is:

$$
\text{percent} = 100F
$$

The conversion has only two uses. Where the equations need $`F_D`$, the model
derives it from the dial's percent. The screen converts for display. The model
treats a fraction and a percent as different kinds of number, and rejects one
where the other is wanted.

**The vaporizer setting is stored as the percent dialled.** It is the only
concentration that is set rather than computed. Converting a fraction back to a
percent does not always return the setting, so a value kept as a fraction could
not give back what a learner dialled. A new run starts the dial at the agent's
published percent, without converting it. An error message about a setting
gives it in percent, beside the vaporizer maximum, which is also stored in
percent. Like the vaporizer setting, the flows are stored as set (§ "Time").

**A concentration's range is checked once, when the concentration is created.**
A fraction must always be finite and satisfy:

$$
0 \leq F \leq 1
$$

A percent must be finite and lie from 0 to 100. Every place that stores a
concentration accepts only a checked value.

Each fraction computed in a step is checked before a compartment stores it. A
value outside 0 through 1 halts the run and names the compartment, instead of
being stored or shown. Supported settings never lead to such a value. The
delivered concentration and each starting fraction must be at or below 0.99 of
ambient pressure (`docs/VERIFICATION.md` § "The numerical envelope").
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

**For developers.** The conversion between a fraction and a percent is written
only in `src/anesthesia_sim/core/concentration.py`, in both directions. The two
forms are distinct types there, `Fraction` and `Percent`, so a type checker
rejects a percent where a fraction is wanted before the program runs. When the
program runs, a value of the wrong form is rejected as a missed conversion
rather than as a value out of range. The code also rejects a value that is
already converted, or one that does not say which form it is in.

The breathing circuit stores the dial's percent, and so do the record of control
changes and the settings that a run records for each stretch. The model derives
$`F_D`$ from that percent in both the circuit and the recorded settings. A new
run's dial is set in `AgentUptakeSystem.for_agent()`.

On a 0 to 8% dial in 0.01% steps, multiplying a fraction by 100 fails to return
the percent it came from for 126 of the 801 settings. The first failure is at
0.23%, and 0.9% comes back as 0.9000000000000001.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

The agent's MAC is stored as a `MacPercent`, a `Percent` that rejects zero when
it is built. Every formatter that computes a MAC multiple accepts only that
kind of percent as its divisor. No other lower limit is set on the MAC, so a MAC
far below any real agent's would still give multiples too large to read. The
shipped MACs are 1.2% to 6.0%.
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- provenance: data/agents/desflurane.json mac_percent = 6 -->

The rules that the fraction and percent types share with the flows are written
once, in `core/checked_number.py` (`docs/INTERFACE.md` § "Supported input ranges"): what counts as a
number, that one checked quantity is never created from another, and that minus
zero is stored as zero.

The places that store a concentration are these:

- each compartment's setter
- the driving fraction that a compartment's own closed form takes
- the breathing circuit, when it is built or set (`BreathingCircuit`)
- the saved state that a rollback restores the circuit from
  (`BreathingCircuitState`)
- the settings that a run is built from (`UptakeEquationSettings`)
- the parameters that an agent's data file is parsed into, which hold its MAC
  and vaporizer maximum (`AgentParameters`)

Each computed fraction is checked in `AgentUptakeSystem._write_state_vector`.
The 0.99 input limit is there because rounding can carry a step's result a
little above the largest fraction that the step started from. The figures
behind the limit are recorded in `core/concentration.py`.

### Agent amount

Every compartment stores its agent as an equivalent gas volume, in litres of
pure agent gas at one reference condition: **20 °C and 760 mmHg, dry**. At that
condition the ideal-gas molar volume is 24.055 L/mol. The condition defines the
unit only. It does not mean that any of the agent is physically at 20 °C and
760 mmHg. $`M_x`$ is the equivalent gas volume of the agent stored in
compartment $`x`$.
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**The reference condition matters only when an amount is converted out of the
unit**, into moles, mass, or the millilitres of liquid that a vaporizer is filled
from. Every governing equation works with dimensionless fractions and physical
volumes, and every partition coefficient is a ratio. So the condition changes no
concentration curve, mass balance or displayed concentration, and no other
number under § "Governing equations" or "Conservation of agent mass", or
under `docs/INTERFACE.md` § "Minimum displayed outputs". The ideal-gas molar volume is 25.450 L/mol at
37 °C, so declaring 37 °C instead would change each converted amount by a
factor of 1.058.

**Converting an alveolar, venous or tissue amount at 20 °C overstates it by
5.8 %** (§ "Known limitations", under § "One reference condition, where the
model physically has two").
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**Three reasons favour a 20 °C reference condition.**
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

1. **The published vapour-to-liquid constants are 20 °C constants.** The
   consumption literature quotes one number per agent, the vapour volume
   obtained from 1 mL of liquid. Biro gives isoflurane 195 mL, sevoflurane
   184 mL and desflurane 210 mL. The same number can be derived from the
   liquid's measured density, its molar mass and the molar volume. At 20 °C the
   derivation reproduces all three within 0.7 %. At 37 °C it runs 5.1–6.3 %
   high:

   | Agent | Liquid density at 20 °C, g/mL | Molar mass, g/mol | Derived mL vapour per mL liquid, 20 °C | Biro's constant | Derived, 37 °C |
   | --- | --- | --- | --- | --- | --- |
   | Sevoflurane | 1.5203 | 200.05 | 182.8 | 184 | 193.4 |
   | Isoflurane | 1.5019 | 184.49 | 195.8 | 195 | 207.2 |
   | Desflurane | 1.4651 | 168.04 | 209.7 | 210 | 221.9 |

   The densities are those of Laster, Fang and Eger, measured in four 50-mL
   volumetric flasks at 20 °C, with a temperature coefficient of
   −0.00250 ± 0.00014 g/mL per °C over 0–25 °C. The molar masses are formula
   masses, which the ChEMBL chemistry database gives to two decimals.

   A model that declared 37 °C would either convert its 37 °C litres with 20 °C
   constants, or print consumption figures 5.5 % below the published ones.
   That 5.5 % is $`1 - 1/1.058`$, the same for every agent. For sevoflurane,
   1 L of vapour comes from 5.47 mL of liquid at 20 °C, and would come from
   5.17 mL at 37 °C.

2. **A consumption figure is converted from amounts of fresh gas, and fresh gas
   is at room temperature.** The delivered amount $`M_{\mathrm{delivered}}`$
   and the exhausted amount $`M_{\mathrm{exhausted}}`$ both accumulate from
   $`\dot V_F`$, the fresh gas flow at the common gas outlet. That flow is
   carrier gas plus the vapour that the vaporizer added. It is on the machine
   side of the patient, at operating-room temperature, not at 37 °C. A cost
   or waste figure is computed from those two amounts (`ROADMAP.md`
   "Planned milestones" item 28). Declaring 20 °C makes them exact. Declaring
   37 °C would leave them approximate, and would need a correction from room
   to body temperature on $`\dot V_F`$. That correction would change the
   governing equations, not just a label.

3. **Gas Man's own constants are 20 °C constants, and its litres carry no
   condition at all.** This model takes its partition coefficients, MACs and
   reference patient from Gas Man (§ "Source hierarchy"), so its amounts follow
   Gas Man's arithmetic. A different reference condition would make this
   model's litre and Gas Man's litre different quantities, although every
   parameter behind them is shared.

   Gas Man states a condition in one place only, the line
   `Volatility=209 Vapor/Liquid volume ratio (20'C)` in its settings file,
   `GASMAN.INI`. It states none for the litres of uptake and of delivered agent
   that it displays. This model likewise uses the condition only where vapour is
   converted to liquid. The 20 °C derivation reproduces all five of Gas Man's
   printed vapour-to-liquid constants within 0.35 %, and the 37 °C derivation
   runs 5.6–6.2 % high:

   | Agent | Gas Man | Derived, 20 °C | Derived, 37 °C |
   | --- | --- | --- | --- |
   | Halothane | 228 | 227.7 (−0.15 %) | 240.9 (+5.6 %) |
   | Enflurane | 198 | 198.6 (+0.29 %) | 210.1 (+6.1 %) |
   | Isoflurane | 196 | 195.8 (−0.09 %) | 207.2 (+5.7 %) |
   | Sevoflurane | 183 | 182.8 (−0.10 %) | 193.4 (+5.7 %) |
   | Desflurane | 209 | 209.7 (+0.35 %) | 221.9 (+6.2 %) |

   The table adds halothane and enflurane to the three agents this model
   carries, because Laster, Fang and Eger measured their densities in the same
   experiment.

<!-- provenance: data/agents/sevoflurane.json liquid_density.g_ml = 1.5203 -->
<!-- provenance: data/agents/isoflurane.json liquid_density.g_ml = 1.5019 -->
<!-- provenance: data/agents/desflurane.json liquid_density.g_ml = 1.4651 -->
<!-- provenance: data/agents/sevoflurane.json molar_mass_g_mol = 200.05 -->
<!-- provenance: data/agents/isoflurane.json molar_mass_g_mol = 184.49 -->
<!-- provenance: data/agents/desflurane.json molar_mass_g_mol = 168.04 -->
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->
<!-- provenance: data/agents/sevoflurane.json liquid_density.measured_at_celsius = 20 -->
<!-- provenance: data/agents/isoflurane.json liquid_density.measured_at_celsius = 20 -->
<!-- provenance: data/agents/desflurane.json liquid_density.measured_at_celsius = 20 -->
<!-- derived: 182.8 from data/agents/sevoflurane.json liquid_density.g_ml = 1.5203, molar_mass_g_mol = 200.05 -->
<!-- derived: 195.8 from data/agents/isoflurane.json liquid_density.g_ml = 1.5019, molar_mass_g_mol = 184.49 -->
<!-- derived: 209.7 from data/agents/desflurane.json liquid_density.g_ml = 1.4651, molar_mass_g_mol = 168.04 -->

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
  server) on 2026-10-26. The database is tier 2 under § "Source hierarchy",
  because a molar mass is computed from the formula and the standard atomic
  weights, not measured on the agent.
- Mohr PJ, Newell DB, Taylor BN, Tiesinga E. *CODATA recommended values of the
  fundamental physical constants: 2022.* Rev Mod Phys 2025;97(2):025002.
  doi:10.1103/RevModPhys.97.025002. Table XXXII gives the gas constant as the
  product of the exact Avogadro and Boltzmann constants. Table XXXIII gives
  the standard atmosphere, 101 325 Pa exactly, and the molar volume of an
  ideal gas at 0 °C, which the tests use to check the 24.055 L/mol above.
  Read in full from arXiv:2409.03787v1 on 2026-10-26.
- Biro P. *Calculation of volatile anaesthetics consumption from agent
  concentration and fresh gas flow.* Acta Anaesthesiol Scand
  2014;58(8):968-72. PMID 25060161, doi:10.1111/aas.12374. Retrieved from
  PubMed and verified against the abstract on 2026-09-17. The abstract gives
  the four constants but does not state their temperature, so the
  reproduction above is what shows they are 20 °C constants.
  <!-- not-restated: 20 °C -->
- Philip JH. *Workbook for Gas Man*. Appendix C's `GASMAN.INI` listing is the
  source for the `Volatility` setting. Chapter 10's closed-circuit
  liquid-injection section (printed pp. 103-105) is the source for the five
  vapour-to-liquid constants. There the constants convert an *input*, the volume
  of liquid injected, rather than a displayed amount. Both were read from the
  project owner's private reference library on 2026-09-16. The reading notes are
  in `docs/references/README.md` § "Philip — *Workbook for Gas Man*". The
  workbook is tier 3 under § "Source hierarchy": it defines what Gas Man does,
  and it measures nothing.

**For developers.** The code must use the one reference condition everywhere,
and must never add gas fractions, dissolved blood concentrations and tissue
concentrations directly. It works in litres.

## Symbols

The **Code** column names the one place in the model's code that holds each
symbol.

| Symbol | Meaning | Unit | Code |
| --- | --- | --- | --- |
| $`t`$ | Elapsed simulation time | s | `SimulationState.elapsed_s` |
| $`\Delta t`$ | An interval of simulated time. A run's step is one second (`docs/VERIFICATION.md` § "Supported simulation step") | s | — the code reads the constant `SIMULATION_STEP_S` for a run's step; a compartment stepped on its own takes its interval as an argument |
| $`F_D`$ | Delivered fresh-gas agent fraction | dimensionless | `BreathingCircuit.delivered_partial_pressure_fraction` |
| $`F_I`$ | Inspired agent fraction, taken as the fraction in the breathing circuit (§ "Model boundary" states the assumption that makes circuit gas and inspired gas one quantity, and what would break it) | dimensionless | `BreathingCircuit.inspired_partial_pressure_fraction` |
| $`F_A`$ | Alveolar agent fraction | dimensionless | `AlveolarCompartment.partial_pressure_fraction` |
| $`F_a`$ | Arterial partial-pressure-equivalent fraction, defined as $`F_a \equiv F_A`$ (§ "Model boundary") | dimensionless | — the code reads `AlveolarCompartment.partial_pressure_fraction` wherever an arterial fraction is required |
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
| $`f_i`$ | Fraction of cardiac output reaching tissue group $`i`$ | dimensionless | `TissueGroup.perfusion_fraction` |
| $`\mathrm{MAC}_\%`$ | The agent's alveolar concentration at 1 MAC, a single adult value whose source states no age. It sets the dial's starting position and is the divisor for the display in MAC multiples. No governing equation reads it | percent | `AgentParameters.mac_percent` |
| $`\lambda_{b:g}`$ | Agent blood:gas partition coefficient, read from the agent data files and stored once per patient in the venous pool | dimensionless | `PatientCompartments.blood_gas_partition_coefficient` |
| $`\lambda_{i:g}`$ | Tissue:gas partition coefficient for group $`i`$, read from the agent data files | dimensionless | `TissueGroup.tissue_gas_partition_coefficient` |
| $`\lambda_{i:b}`$ | Tissue:blood partition coefficient for group $`i`$, derived as $`\lambda_{i:g}/\lambda_{b:g}`$ and never stored | dimensionless | `TissueGroup.tissue_blood_partition_coefficient_for` |
| $`M_C`$ | Agent stored in the breathing circuit | L equivalent gas | `BreathingCircuit.agent_amount_l` |
| $`M_A`$ | Agent stored in alveolar gas | L equivalent gas | `AlveolarCompartment.agent_amount_l` |
| $`M_v`$ | Agent stored in venous blood | L equivalent gas | `VenousBloodCompartment.agent_amount_l` |
| $`M_i`$ | Agent stored in tissue group $`i`$ | L equivalent gas | `TissueGroup.agent_amount_l` |

The symbols for the two tissue coefficients name both phases in order, because
the primary literature has no convention that would let a reader supply a
missing phase. Baker and Farmery's 2011 review gives one quantity three names in
a single chapter: the tissue-gas partition coefficient (p. 569), the
tissue-blood partition coefficient (p. 570) and the blood tissue partition
coefficient (Table 2). The review's Eq. (4) shows that the quantity is the
tissue:blood coefficient. The full citation is in the reference list,
`docs/references/README.md`.

The gas-phase symbols follow the inhaled-anesthetic literature:
$`F_D \rightarrow F_I \rightarrow F_A`$. Symbols and the gas-phase cascade
($`F_D`$, $`F_I`$, $`F_A`$) follow Hendrickx and De Wolf (pp. 161-162). They
attribute the $`F_D - F_I`$ gradient to rebreathing (p. 169) and the
$`F_I - F_A`$ gradient to uptake (p. 171), and describe the teaching role of
the $`F_A/F_I`$ curve (p. 167) (Hendrickx JFA, De Wolf A. Special aspects of
pharmacokinetics of inhalation anesthesia. In: Schüttler J, Schwilden H, eds.
Modern Anesthetics. Handbook of Experimental Pharmacology 182. Springer,
2008:159-186).

The breathing circuit's quantities carry the subscript $`C`$: $`V_C`$ is its
volume and $`M_C`$ is the amount of agent in it.

**The symbols for inspired and tissue fractions differ only in case.** $`F_I`$
is the inspired fraction, and $`F_i`$ is tissue group $`i`$'s fraction. Where
both appear in one expression, the tissue index is written out.

**For developers.** Each Code cell is written `ClassName.accessor`. Where a
symbol has no place of its own in the code, its Code cell shows an em dash
followed by what the code reads instead. $`F_a`$ is the only such symbol.

A reader who knows the model's symbols should be able to follow the code
without the Code column, so code that needs the column to be understood has a
defect.

The code's names for the two tissue coefficients give both phases in order, as
their symbols do.

The case-only difference between $`F_I`$ and $`F_i`$ stays because both are
standard in the literature. Renaming either would make this model's symbols
disagree with every source a reader is likely to come from.

## Tissue groups

Version v0.1.0 contains exactly three perfusion-limited tissue groups:

- vessel-rich group;
- muscle; and
- fat.

Each group has the volume, fraction of cardiac output, blood flow, partition
coefficients, stored agent amount and fraction that § "Symbols" lists for
tissue group $`i`$.

The fractions of cardiac output must satisfy $`f_i > 0`$ and $`\sum_i f_i = 1`$
within one part in a million million, so the three groups together receive the
whole cardiac output:

$$
\sum_i Q_i = Q
$$

**For developers.** In the code, the tolerance on $`\sum_i f_i = 1`$ is
`FLOW_FRACTION_TOLERANCE = 1e-12`, defined in `core/rounding.py`.

## Compartment capacities

### Gas compartments

The equivalent agent amount in the breathing circuit is:

$$
M_C = V_C F_I, \qquad \text{so} \qquad F_I = \frac{M_C}{V_C}
$$

The equivalent agent amount in the alveolar gas compartment is:

$$
M_A = V_A F_A, \qquad \text{so} \qquad F_A = \frac{M_A}{V_A}
$$

### Blood compartments

**The simulated patient has one blood:gas partition coefficient.** It relates
the concentration of agent dissolved in blood to the gas-phase concentration at
equilibrium. The coefficient comes from the agent's data. The lung's uptake
term and every tissue group's tissue:blood coefficient use that one value.

Arterial blood has no compartment, capacity or amount balance of its own.
Instead, $`F_a \equiv F_A`$ at every instant, for the reasons § "Model
boundary" gives.

The agent amount stored in venous blood is:

$$
M_v = V_v \lambda_{b:g} F_v
$$

Solving for $`F_v`$ gives:

$$
F_v = \frac{M_v}{V_v\lambda_{b:g}}
$$

**For developers.** The model writes the blood:gas coefficient once, into the
venous pool, and the tissue groups store none. The pool refuses a second value,
and the patient refuses a replacement pool with a different one. If each tissue
group kept its own copy, the copies could disagree and no check would fire. A
pool at 0.1 beside groups at sevoflurane's 0.65 would still conserve agent, and
the run would give uptake curves that look plausible and are wrong.
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->

### Tissue compartments

The effective tissue capacity $`C_i`$ of tissue group $`i`$ is the group's
volume times its tissue:blood partition coefficient and the agent's blood:gas
partition coefficient:

$$
C_i =
V_i\lambda_{i:b}\lambda_{b:g}
$$

The product of the two coefficients is the group's stored tissue:gas
coefficient, so:

$$
C_i =
V_i\lambda_{i:g}
$$

The capacity relates $`M_i`$ to $`F_i`$:

$$
M_i = C_iF_i
$$

Dividing $`M_i`$ by the capacity gives $`F_i`$:

$$
F_i =
\frac{M_i}
{V_i\lambda_{i:b}\lambda_{b:g}}
$$

**For developers.** The code computes the capacity from the tissue:gas
coefficient, in one multiplication (`TissueGroup.capacity_l`). When the model
sets up the patient's compartments (`PatientCompartments.from_parameters`), it
stores the agent's blood:gas coefficient once, in the venous pool. The code
takes that value (`PatientCompartments.blood_gas_partition_coefficient`) from
there for the lung's uptake term and for each tissue group's tissue:blood
coefficient.

## Governing equations

All flow terms below must be in liters per second, converted from the liters
per minute that a run stores (§ "Time").

### Breathing circuit

Fresh gas enters the circuit at flow $`\dot V_F`$ and concentration $`F_D`$. A
volume of gas equal to the fresh gas volume leaves through the exhaust, at the
current concentration of the mixed circuit gas, $`F_I`$. Ventilation exchanges
gas between the circuit and the alveolar compartment. The amount of agent in the
circuit, $`M_C`$, therefore changes as:

$$
\frac{dM_C}{dt} = \dot V_F(F_D-F_I) - \dot V_A(F_I-F_A)
$$

Since $`M_C = V_CF_I`$, where $`V_C`$ is the circuit volume, the concentration
equation is:

$$
\frac{dF_I}{dt} = \frac{\dot V_F}{V_C}(F_D-F_I) - \frac{\dot V_A}{V_C}(F_I-F_A)
$$

With no alveolar ventilation, this reduces to the equation for the circuit
alone:

$$
\frac{dF_I}{dt} = \frac{\dot V_F}{V_C}(F_D-F_I)
$$

When the fresh gas is constant and no patient is connected, this equation has an
exact solution over a time $`\Delta t`$:

$$
F_I(t+\Delta t) = F_D+\left[F_I(t)-F_D\right]\exp\left(-\frac{\dot V_F\Delta t}{V_C}\right)
$$

**The fresh gas flow, $`\dot V_F`$, is the flow at the common gas outlet, not the
flowmeter setting.** The equation for $`M_C`$ uses one $`\dot V_F`$ for the agent
that arrives, at $`\dot V_F F_D`$, and for the mixed circuit gas that leaves.
$`\dot V_F`$ is therefore the whole gas stream delivered to the circuit: the
carrier gas plus the vapour that the vaporizer adds to it. Let $`\dot V_c`$ be the
carrier flow, which is what the flowmeters are set to, and let $`\dot V_v`$ be the
added vapour flow. The delivered fraction is then
$`F_D = \dot V_v/(\dot V_c + \dot V_v)`$, and $`\dot V_F`$ is related to the
flowmeter setting by:

$$
\dot V_F = \dot V_c + \dot V_v = \frac{\dot V_c}{1-F_D}
$$

At ordinary dial settings $`\dot V_F`$ is only slightly higher than the
flowmeter setting, by 2% at 2% delivered. The model sets the top of the
desflurane dial at 18%, the calibrated maximum of the Tec 6 vaporizer. At that
setting $`\dot V_F`$ is 22% higher, so gas from flowmeters set to 2 L/min leaves
the common gas outlet at about 2.44 L/min. If a reader takes the simulator's
fresh gas flow control for a flowmeter setting, they misjudge the circuit time
constant, $`V_C/\dot V_F`$, by the same factor. The wash-in curve depends on
that time constant.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- derived: 22 percent from data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- derived: 2.44 L/min from data/agents/desflurane.json max_delivered_concentration_percent = 18 -->
<!-- not-restated: 2 % -->

The simulator therefore labels that control "Fresh gas flow", with "common gas
outlet" on the line below it. On a real machine, "Fresh gas flow" alone is the
name on the flowmeter bank. The alveolar readout uses the same two-line form for
"end-tidal-equivalent", for the same reason.

**The circuit volume, $`V_C`$, is that of the assembled breathing system, never a
manufacturer's apparatus figure.** The model has one well-mixed gas compartment
in front of the patient, so the corrugated limbs and the Y-piece can only be
inside $`V_C`$. $`V_C`$ is therefore the sum of two volumes:

- The *apparatus* is the workstation's internal volume, including its
  absorber and excluding the patient circuit. This project's survey of
  anesthesia machines found every apparatus volume stated that way
  (`docs/machine-survey.md` § "(a1) Apparatus gas volume").
- The *patient circuit* is the disposable limbs and Y-piece fitted for the
  case.

Where a machine's $`V_C`$ is built from an apparatus figure, it includes 1.2 L
for the patient circuit, unless the machine's data assumes a circuit with a
stated volume of its own. The 1.2 L is the internal volume of the Hudson RCI
circuit that Shin et al. added to each machine's figure (*BMC Anesthesiol*
2017;17(1):10, PMID 28103806; read at full text 2026-10-04 from PubMed Central,
PMC5248460). Shin et al. cite Dräger's instructions for use for their apparatus
volumes.

$`V_C`$ leaves out the reservoir bag, whatever the source of the volume.
Shin et al.'s totals also leave out the 3 L bag of their set-up. Adding that bag
would nearly double a Perseus A500's assembled 3.3 L.

The circuit volume that the simulator ships with, 6.0 L, is an assembled total,
and no source divides it between apparatus and patient circuit
(§ "Parameter provenance").
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

**The model's exhaust works like a semi-closed circle's, and it vents whenever
fresh gas flows.** Two of the model's assumptions keep the outflow equal to the
inflow, as in a circle while gas is passing through its surplus gas valve. Both
gas compartments have fixed volumes. The modeled patient takes up no net volume,
because the model removes agent from a constant alveolar volume, $`V_A`$,
without removing gas from it (§ "Alveolar gas"). Every litre admitted therefore
has to leave, and the exhaust is the only way out.

**A real circle spills less than it is given**, by the volume the patient
removes: the oxygen consumed, the vapour taken up, and any nitrous oxide.
Carbon dioxide nets to nothing, because the absorbent removes as much as the
patient breathes out. The gap is an absolute rate, not a share of the flow, so
it is small where the flow is large and is the whole of the model's spill where
the flow is small. For the simulator's reference adult it is on the order of
0.3 L/min early in a case. About 240 ml/min of that is oxygen, from the
$`10M^{3/4}`$ allometry on page 17 of Lowe and Ernst (§ "Parameter provenance").
That allometry is Brody's interspecies metabolic relation, not a measurement in
an anaesthetised adult, and the caution given in that section applies to it.
The rest is the 65 ml/min of sevoflurane vapour that the model computes at the
early induction gradient (§ "Alveolar gas"), a figure that falls as uptake
slows. At the opening fresh gas flow of 4.0 L/min, the gap is 6 to 8% of the
flow. At 0.5 L/min, which the simulator also allows, it is half or more.
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- derived: 6 to 8 percent from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->

**When fresh gas is titrated down to uptake, nothing is left to vent and the
surplus gas valve shuts.** This is closed-circuit technique. A machine may also
shut the valve as a mode of its own. Meyer et al. wrote for the manufacturer of
one of the surveyed machines. They state: *"In the automatic controlled mode of
the Zeus anesthesia machine, the surplus gas valve can be closed to prevent any
loss of gas volume"* (Meyer J-U, Kullik G, Wruck N, Kück K, Manigel J. Advanced
technologies and devices for inhalational anesthetic drug dosing. In:
Schüttler J, Schwilden H, eds. *Modern Anesthetics.* Handbook of Experimental
Pharmacology vol. 182. Berlin: Springer; 2008:451–470; read at full text
2026-09-19, with the record and route in `docs/machine-survey.md` § "Sources").

**Neither closed-circuit technique nor a machine mode that shuts the valve is
modeled, and the exhaust term is not the reason.** The circuit equation still
applies with the valve shut. Gas that the patient's uptake pulls out of the
circuit leaves at $`F_I`$, exactly as spilled gas does. The term
$`\dot V_F(F_D-F_I)`$ is therefore the same either way, and so is $`F_I`$. Two
other things change.

- **Where the agent in the outflow goes.** The model counts the whole of
  $`\dot V_FF_I`$ as leaving the system (`docs/VERIFICATION.md` § "Circuit exhaust"). With the valve
  shut, that agent is carried into the alveolar compartment and kept there.
  Carrying it there needs the extra inspired gas that § "Alveolar gas" writes as
  $`\dot V_A + \sum_k \dot M_{\mathrm{uptake},k}`$, and this model does not
  include that term.
- **What sets the flow.** A closed circuit's fresh gas flow *is* the
  patient's total uptake, so $`\dot V_F`$ stops being a setting and becomes a
  result. This model cannot compute that total. It does not track oxygen,
  which is the largest part. It computes the agent's uptake, but its fixed
  alveolar volume assumes that this uptake removes no volume at all.

**For developers.** The tests from v0.0.2 that check the equation for the
circuit alone against its exact solution are in `docs/VERIFICATION.md` § "Preserved circuit reference
tests".

Desflurane's dial maximum is stored in `data/agents/desflurane.json` as
`max_delivered_concentration_percent`.

Never shorten the "Fresh gas flow" label to its first line to fit a layout.

A machine's $`V_C`$ is stored as `circuit_volume_l` in its file in
`data/machines/`. It holds the assembled total of apparatus and patient circuit
until the split planned in `docs/machine-abstraction.md` stores the apparatus
volume separately, as `apparatus_volume_l`.

An apparatus figure stored alone shortens the circuit time constant by the
patient circuit's share. At 4.0 L/min, a Perseus A500's 2.1 L apparatus volume
gives a time constant of 31.5 s, 36% shorter than the 49.5 s from its assembled
3.3 L. No automatic check can catch that error, because both are correctly cited
volumes (§ "How this document is held to the tree" says what the documentation
check confirms).
<!-- derived: 31.5 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- derived: 49.5 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->

Closed-circuit operation needs both a variable alveolar volume and a patient who
consumes oxygen, so it is not among the three entries in § "Known limitations"
that come from the fixed alveolar volume alone.

Setting only the exhaust's removal rate to zero does not model a closed circuit.
The changed model runs without error and gives a plausible curve. Its circuit
settles at $`F_I = F_A + \dot V_FF_D/\dot V_A`$.
At the opening fresh gas flow of 4.0 L/min, with the reference adult's 4 L/min
alveolar ventilation and a 2% dial, that is two percentage points above
alveolar. In the steady state every litre of delivered agent reaches the
patient, as in a closed circuit, but nothing ties the fresh gas flow to uptake.
At 4.0 L/min and the same dial, the vaporizer adds agent about thirteen times
faster than at the 0.3 L/min that this patient's uptake would set.
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- not-restated: 2 % -->

Closed-circuit operation is a property of the machine, and one coefficient
switched by a condition is the wrong way to model it. The machine design in
`docs/machine-abstraction.md` reserves a place for it, a removal strategy named
`closed_circuit`, recorded there as not implemented.

### Alveolar gas

Ventilation moves gas between the circuit and the alveolar compartment.
Pulmonary blood flow enters the lungs at the venous concentration $`F_v`$ and
leaves in equilibrium with alveolar gas, at $`F_A`$.

The alveolar amount balance is:

$$
\frac{dM_A}{dt} = \dot V_A(F_I-F_A) - Q\lambda_{b:g}(F_A-F_v)
$$

Because $`M_A = V_AF_A`$, the alveolar concentration equation is:

$$
\frac{dF_A}{dt} = \frac{\dot V_A(F_I-F_A) - Q\lambda_{b:g}(F_A-F_v)}{V_A}
$$

Blood exchanges agent with alveolar gas at the pulmonary uptake rate:

$$
\dot M_{\mathrm{pulmonary}} = Q\lambda_{b:g}(F_A-F_v)
$$

A positive value is net uptake from alveolar gas into blood. A negative value is
net return from blood to alveolar gas during washout.

**Alveolar gas has no single time constant.** If ventilation acted alone, at
$`Q = 0`$, it would turn the alveolar volume over with the time constant:

$$
\tau_A^{\mathrm{vent}} =
\frac{V_A}{\dot V_A}
$$

For the reference adult, where $`V_A = 2.5`$ L and $`\dot V_A = 4`$ L/min, this
is 37.5 s.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->
<!-- derived: 37.5 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->

The model does not offer 37.5 s as a derived output. Shown as "the alveolar
time constant", it would look plausible but match no rate in the simulation.
Blood uptake acts on alveolar gas alongside ventilation. If $`F_I`$ and $`F_v`$
were held fixed, $`F_A`$ would change with the time constant
$`V_A/(\dot V_A + Q\lambda_{b:g})`$, which is 20.7 s for the reference adult on
sevoflurane. But $`F_I`$ and $`F_v`$ are not fixed, because the model computes
them together with $`F_A`$. The alveolar trajectory is therefore a sum of
exponentials over all six compartments, and no single time constant describes
it. The six compartments are the circuit, the alveolar gas, the venous blood,
and the vessel-rich, muscle and fat groups.
<!-- derived: 20.7 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4, default_cardiac_output_l_min = 5 -->
<!-- derived: 20.7 s from data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->

**Six time constants set the pace of every run.** The model computes the
concentrations in its six compartments together. Each is the level that the
delivered fraction sets plus six exponential terms, one for each time constant.
These time constants depend only on fresh gas flow, alveolar ventilation,
cardiac output, the volumes and the partition coefficients, and not on the
delivered fraction. The table gives them at the reference adult's default flows
and with all three flows at their supported maximums: fresh gas flow 10 L/min,
alveolar ventilation 12 L/min and cardiac output 10 L/min. The circuit volume is
the reference circle system's 6 L in both.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12, MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

| Flows (L/min): fresh gas, $`\dot V_A`$, $`Q`$ | Agent | $`\tau_1`$ (s) | $`\tau_2`$ (s) | $`\tau_3`$ (s) | $`\tau_4`$ (s) | $`\tau_5`$ (s) | $`\tau_6`$ (s) | Oscillation period (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4, 4, 5 (defaults) | sevoflurane | 15.8 | 15.8 | 63.1 | 365 | 10 300 | 167 000 | 753 |
| | isoflurane | 13.7 | 13.7 | 54.5 | 426 | 11 500 | 187 000 | 466 |
| | desflurane | 16.6 | 16.6 | 66.1 | 264 | 6 020 | 95 500 | 1 540 |
| 10, 12, 10 (maximums) | sevoflurane | 6.89 | 6.89 | 27.2 | 161 | 4 890 | 81 300 | 398 |
| | isoflurane | 6.02 | 6.21 | 22.4 | 190 | 5 280 | 89 500 | none |
| | desflurane | 7.17 | 7.17 | 29.1 | 114 | 2 890 | 47 000 | 384 |
<!-- derived: 15.8 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, venous_pool_volume_l = 1.222, default_alveolar_ventilation_l_min = 4, default_cardiac_output_l_min = 5, tissue_groups.vessel_rich.volume_l = 6, tissue_groups.vessel_rich.perfusion_fraction = 0.76, tissue_groups.muscle.volume_l = 33, tissue_groups.muscle.perfusion_fraction = 0.18, tissue_groups.fat.volume_l = 14.5, tissue_groups.fat.perfusion_fraction = 0.06 -->
<!-- derived: 15.8 s from data/machines/reference_circle_system.json circuit_volume_l = 6, default_fresh_gas_flow_l_min = 4 -->
<!-- derived: 15.8 s from data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65, tissue_gas_partition_coefficients.vessel_rich = 1.1, tissue_gas_partition_coefficients.muscle = 2.4, tissue_gas_partition_coefficients.fat = 34 -->
<!-- derived: 13.7 s from data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3, tissue_gas_partition_coefficients.vessel_rich = 2.1, tissue_gas_partition_coefficients.muscle = 4.5, tissue_gas_partition_coefficients.fat = 70 -->
<!-- derived: 16.6 s from data/agents/desflurane.json blood_gas_partition_coefficient = 0.42, tissue_gas_partition_coefficients.vessel_rich = 0.54, tissue_gas_partition_coefficients.muscle = 0.97, tissue_gas_partition_coefficients.fat = 13 -->

- **The fastest time constant is 13.7 to 16.6 s at the default flows, and 6.02
  to 7.17 s at the maximum flows.** For sevoflurane and desflurane, the maximum
  flows give the fastest time constant of any supported setting. Isoflurane's
  fastest is 5.83 s, at 10 L/min of fresh gas, 12 L/min of ventilation and
  9.32 L/min of cardiac output. Nothing in the model changes faster.
  `docs/VERIFICATION.md` § "Supported simulation step" compares the one-second step with this 5.83 s.
- **The slowest time constant is the fat group's, at 47 000 s (13 hours) to
  187 000 s (52 hours).**
- **In five of the six rows, the two fastest terms form one oscillation, so
  their time constants are equal.** Gas moves both ways between the circuit and
  the alveoli, and blood carries agent from the alveoli through the tissues and
  back. Exchange around such a loop allows an oscillation, but it cannot be
  seen. Its period is 384 to 1 540 s, and over half a period it shrinks by a
  factor of at least $`e^{17}`$, about $`2.5\times10^{7}`$. At the maximum
  flows, isoflurane's two fastest time constants differ, and there is no
  oscillation.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->

A test recomputes every figure in the table from an independent copy of the
equations. It fails when a change to a stored parameter or to the equations
moves any of them.

**The alveolar volume is held constant, and that is what excludes nitrous
oxide.** The concentration equation above divides by $`V_A`$ as a constant.
Ventilation carries the same volume in and out. No term adds inspired gas to
replace the agent that blood takes up. A fixed volume is correct for the agents
the model includes and wrong for nitrous oxide.

The table below compares the pulmonary uptake rate with alveolar ventilation
early in induction, when $`F_v \approx 0`$. It uses the reference adult, with
$`Q = 5`$ L/min, $`V_A = 2.5`$ L and $`\dot V_A = 4`$ L/min.
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5, alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->

| Gas | $`\lambda_{b:g}`$ | $`F_A - F_v`$ | $`\dot M_{\mathrm{pulmonary}}`$ | Of $`\dot V_A`$ |
| --- | --- | --- | --- | --- |
| Sevoflurane at 2% | 0.65 | 0.02 | 0.065 L/min | 1.6% |
| Nitrous oxide at 70% | 0.47 | 0.50 | 1.18 L/min | 29% |
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 1.6 percent from data/patients/reference_adult.json default_cardiac_output_l_min = 5, default_alveolar_ventilation_l_min = 4 -->
<!-- derived: 1.6 percent from data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- not-restated: 2 % -->

For sevoflurane, uptake removes 1.6% of the volume that ventilation brings into
the alveoli. A fixed volume can ignore that, and this model does. For nitrous
oxide, uptake removes 29%, and that removal *is* the concentration effect. The
gas left behind is concentrated by the volume that departed, and inspired gas is
drawn in to replace that volume. A fixed-volume compartment represents neither
half of the effect.

**Nitrous oxide's $`\lambda_{b:g} = 0.47`$ above is the conventional textbook
figure and is not a stored parameter.** The project has no parameter file for
nitrous oxide at all. The value is used here only for the comparison in the
table.

**The fixed alveolar volume blocks three features.** They are nitrous oxide,
simultaneous gases, and concentration or second-gas effects, each listed
separately in "Known limitations". Lifting the fixed-volume constraint would
unblock all three.

**For developers.** With the delivered fraction set to zero, the six equations
become $`d\mathbf{F}/dt = A_6\mathbf{F}`$. $`A_6`$ is the 6×6 block of the
matrix of the model's equations (`build_system_matrix` in
`core/governing_equations.py`), in that module's state order. Each of the six
exponential terms is $`e^{\lambda_k t}`$ for one eigenvalue $`\lambda_k`$ of
$`A_6`$, with time constant $`\tau_k = -1/\operatorname{Re}\lambda_k`$. The
5.83 s figure comes from a search over a grid of 11 fresh gas flows, 13
ventilations and 21 cardiac outputs for each agent, refined along cardiac
output.

Many numerical methods need steps short compared with the fastest time constant
to keep their errors from growing. The slowest time constant is about 5 700 to
14 900 times the fastest, so these methods would take many steps over a run
long enough for the slowest to matter. The exact method of
`docs/VERIFICATION.md` § "Selected method (as implemented)" does not need such short steps.

The test that recomputes the table is
`test_modal_time_constants_are_the_pinned_ones` in
`tests/reference/test_coupled_dynamics.py`. That file holds the test's own copy
of the equations. When the test fails, its message says to re-derive the table.
On 2026-11-01, the eigenvalues of the matrix of the model's equations agreed
with the table's figures, and with the values from the test's copy, to within a
relative difference of 3e-15.

In the matrix of the model's equations, the alveolar row divides each of its
terms by the alveolar volume (`alveolar_volume_l`), which the equation settings
hold fixed for the whole step. Two standard formulations lift the fixed-volume
constraint, and a milestone that adds several gases could adopt either one. They
are equivalent to first order. The first lets $`V_A`$ change over time, and the
concentration equation gains a volume term:

$$
\frac{dV_A}{dt} = \dot V_{A,\mathrm{in}} - \dot V_{A,\mathrm{out}} - \sum_k \dot M_{\mathrm{uptake},k}
\qquad
\frac{dF_A}{dt} = \frac{dM_A/dt - F_A\,dV_A/dt}{V_A}
$$

The second keeps $`V_A`$ constant and replaces the volume lost to total uptake
with inspired gas, so the effective inspired ventilation becomes
$`\dot V_A + \sum_k \dot M_{\mathrm{uptake},k}`$. This formulation is the
smaller change to the model, and the one that the classical treatment uses.

Either way, the second-gas effect follows from the alveolus holding more than
one gas, and needs no machinery of its own. Because the gases are coupled
through the alveolar volume, the roadmap says to model the patient as a set of
substances instead of bolting nitrous oxide on beside a volatile agent
(`ROADMAP.md` planned item 6). A patient model built that way makes planned
item 7 nearly free. Bolting nitrous oxide on instead would leave item 7
unreachable.

Adopting the 0.47 figure for nitrous oxide would need an entry of its own that
meets the standard set in "Source hierarchy".

### Arterial blood

In this model, the arterial fraction $`F_a`$ equals the alveolar fraction
$`F_A`$ at every instant, for the reasons given in § "Model boundary". There is
no equation for an arterial amount of agent, and no arterial capacity or time
constant. Every equation below that contains $`F_a`$ uses the current $`F_A`$ in
its place.

### Tissue uptake and return

Tissue group $`i`$ receives a blood flow $`Q_i`$. Arterial blood enters at
$`F_a`$, and venous blood leaves in equilibrium with the tissue, at $`F_i`$.

The tissue's amount of agent, $`M_i`$, changes as:

$$
\frac{dM_i}{dt} = Q_i\lambda_{b:g}(F_a-F_i)
$$

Substituting the tissue capacity gives:

$$
\frac{dF_i}{dt} = \frac{Q_i}{V_i\lambda_{i:b}}(F_a-F_i)
$$

With time and flow in compatible units, the tissue time constant is therefore:

$$
\tau_i =
\frac{V_i\lambda_{i:b}}{Q_i}
$$

When the tissue's blood flow is zero, its amount of agent must remain unchanged:

$$
Q_i = 0
\quad\Longrightarrow\quad
\frac{dM_i}{dt}=0
$$

**For developers.** A blood flow can be above zero and still so small that $`\tau_i`$ is larger
than any number the computer can hold. Then the method that computes $`\tau_i`$
(`TissueGroup.time_constant_s`) returns infinity, as it does at zero flow, and a tissue group
stepped on its own is left unchanged. The exact change in the agent it holds is far smaller than
any amount the simulator displays. A test in `tests/unit/test_blood_flow.py` checks this at the
smallest flow that can be created. The venous pool's time constant
(`VenousBloodCompartment.time_constant_s`) is infinite in the same way at a cardiac output that
small, and a second test there checks it.

### Venous blood

Blood from the tissue groups enters the venous pool. Venous blood leaves
that pool for the lungs at concentration $`F_v`$.

The venous amount balance is:

$$
\frac{dM_v}{dt} = \lambda_{b:g}\left(\sum_i Q_iF_i-QF_v\right)
$$

Because $`M_v = V_v\lambda_{b:g}F_v`$, the venous concentration equation is:

$$
\frac{dF_v}{dt} = \frac{\sum_i Q_iF_i-QF_v}{V_v}
$$

When $`Q>0`$, the instantaneous flow-weighted concentration entering the venous
pool is:

$$
F_{\mathrm{tissue\ return}} = \frac{\sum_i Q_iF_i}{Q}
$$

At zero cardiac output, the pulmonary and tissue perfusion transfers are zero,
and the model does not divide by $`Q`$.

## Parameter provenance

No scientific parameter may be added without:

- a full source citation;
- the value and unit used;
- the definition used by the source;
- the temperature or reference conditions when relevant;
- any conversion performed;
- the tissue-group mapping;
- a brief justification for selecting that source;
- the source's tier in the hierarchy below; and
- where the source is not a primary measurement, what the primary literature
  reports and how far that differs from the source's value.

### Source hierarchy: what may be cited as the authority for a value

A citation records where a number was found, and does not on its own say
whether anything was measured there. This project ranks sources in three tiers.
Only a source in the first tier may be named as the authority for a stored
value on its own strength. A lower tier may be adopted only on a recorded
decision, under the rule set out after the three tiers.

1. **Primary measurement.** A study in this tier measured the quantity in the
   species, population and conditions that the model claims to represent, and
   reports the value, its dispersion and its reference conditions. Examples
   are Strum and Eger's sevoflurane blood:gas measurement
   (0.686 ± 0.047 at 37 °C, n=19) and Yasuda, Targ and Eger's human
   tissue:gas coefficients.
2. **Secondary synthesis.** A source in this tier is a review, textbook,
   monograph or consensus document that collects primary measurements without
   making one. It is a good way to find the primary source, and to record the
   figure the field usually quotes, such as the textbook blood:gas coefficient
   of 1.4 for isoflurane. It cannot by itself be the authority for a stored
   value, because the reader cannot see how it rounded values or chose between
   measurements that disagree.
3. **Reference implementation.** This tier holds another simulator's
   parameter set, the numbers that a working program was built to run on.
   Gas Man, a widely used teaching tool, is this project's reference
   implementation. Its parameter set is useful in two ways. The set defines
   Gas Man's behavior, so this simulator can be compared with it. The set is
   also complete and internally consistent, whereas the primary literature
   supplies scattered measurements made in different laboratories on
   different cohorts. **A parameter set is still not a source of
   measurements.** It is assembled to make a program behave. Nobody can
   recover from the program which measurement each number descends from, or
   what was adjusted to make the set consistent. **Gas Man's behavior has been
   compared with measurements in patients**, and the agreement is materially
   worse during wash-in than during maintenance. § "Known limitations" gives
   the figures and the limits they set.

**A tier-2 or tier-3 source may be adopted, but never silently.** The ranking
says which tier a reader may trust without examining it. Nearly half of this
project's provenance table is tier-2 or tier-3 numbers (§ "Where this project
stands", below, gives the counts). The ranking forbids an adoption the reader
cannot see, so a stored value whose authority is not a primary measurement must
have three things recorded. Every such value has all three today:

- **The tier, on the source's own entry in the simulator's data files, with
  the stored values that rest on that source.**
- **Why no tier-1 source was adopted.** The reason is recorded on the source
  entry, or once for the whole data file where no tier-1 source was adopted
  for any value in it.
- **The date and whose decision it was**, where a lower tier was adopted in
  preference to an available primary source rather than for want of one. The
  three blood:gas coefficients are an example: the project owner decided on
  2026-09-03 to keep the Gas Man values and label them.

The bar for adopting a lower tier is higher than for citing a tier-1 source.
Only two reasons are allowed, and the work of finding a primary source is not
one of them:

1. **No primary measurement of *this quantity, in this population* exists or
   is reachable.** This applies to every parameter of the reference patient,
   including those with a primary citation beside them. Hudgel and Devadatta
   measured awake functional residual capacity, whereas the stored volume
   describes an anaesthetised lung. Cattermole et al. measured a different
   population. Janssen et al. report a muscle mass, whereas this model stores
   a volume. Each parameter's note says which of these cases applies, so its
   citation serves as a comparison and not as a source.
2. **The value belongs to a set whose internal consistency is part of what is
   being modelled**, and replacing it would mean mixing primary measurements
   from different laboratories and cohorts. This is the argument for tier 3
   given above. The three blood:gas coefficients are an example. Between them, Eger, Strum and Eger, Lerman et al., and
   Esper et al. 2015 measured all three in this population, so the first
   reason does not cover them. But placing one laboratory's blood:gas figure
   among Gas Man's tissue values would make the simulated curve a mix of two
   parameter sets with different origins. The same objection applies to
   dividing a Gas Man curve by a MAC taken from Mapleson, as discussed later in
   this document.

The second reason is the narrower of the two. It applies only where the source
entry cites the primary measurements with their values and records how far the
stored value differs from them, so that the reader can see what the choice
costs. For the three blood:gas coefficients, the stored values are 0.9% to
26.3% below the measured ones. A later part of this section gives each
difference, the date of the decision, and the planned route to measured
coefficients for all three, which would remove this reason for them.

A stored value can name a source and state its tier while no measurement of
that quantity supports it, and in this simulator that is the ordinary case.
Where a primary measurement *is* available and simply has not been adopted,
the source entry says so in those words.

**Holding a source's full text does not change its tier.** The project owner
keeps the full texts in a private corpus, so that a claim can be checked
against the source itself. `docs/references/` holds no full text. It records
each source's full citation, in `docs/references/README.md`, and notes of the
values taken from it. Baker and Farmery's 2011 *Comprehensive
Physiology* review of inert gas transport in blood and tissues is the closest
published statement of what this document specifies. For any individual number
in it, the review is still a tier-2 synthesis.

**Republication does not promote a value between tiers.** A peer-reviewed
paper that prints a reference implementation's parameter table is still a
tier-3 citation. Two of this project's three tier-3 citations are of that kind, and
neither measured a coefficient. Both are Gas Man simulation studies, and the
third citation is the Gas Man Workbook itself. Table 1
of De Wolf et al. 2012 is the parameter set that the authors fed to Gas Man,
and Weber et al. 2021 describe the product's standard 70 kg patient. The two
papers do not even agree on what Gas Man's set holds. Weber et al.'s Table 1
prints Gas Man 4.2's 1 MAC as 2.1% sevoflurane and 1.1% isoflurane. De Wolf et
al. state 2.0% and 1.2%, which are the values this simulator stores on De
Wolf's authority. Yet every partition coefficient the two print is the same.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- not-restated: 70 kg -->

**For developers.** Each entry under `sources` in a data file must record its
tier in a `tier` field, and the project's checks reject a tier outside the fixed
list. The entry's `authority_for` field lists the stored values that rest on
it. Where the reason why no tier-1 source was adopted covers a whole file, it
goes in the file's `provenance_gap` field. Where a primary measurement is
available and has not been adopted, the entry's `adopted` field records that no
primary measurement backs the value. The field exists because of the ordinary
case described above.

Three rules apply to an entry under `sources`:

- Where the stored value is not a primary measurement, say in the entry's note
  which value the primary literature reports and by how much the two differ.
  Use words that a reader comparing against a textbook can act on.
- Do not let a primary citation stand in for a primary value. Citing a
  measurement *alongside* a tier-3 number does not source that number. A file
  that looks sourced while its number came from somewhere else is worse than
  one that cites nothing, because it stops the reader checking.
- Where no primary source has been adopted, record it as an open gap. "No
  primary source has been adopted for this value" is a legitimate provenance
  state for an educational simulator, and one that can later be fixed. A
  tier-3 citation presented as settled is neither legitimate nor marked for
  fixing.

Saying that a constant comes from Gas Man, or from a paper that reprints Gas
Man's table, presents a tier-3 source as though it were a measurement. Citing
De Wolf et al. 2012 or Weber et al. 2021 as though a value had been measured is
the same error.

#### Where each stored value comes from

**Where this project stands.** Of the 49 rows in the table of stored values
below, 27 are tier 1, four are tier 2, 16 are tier 3, and two adopt no source
of any tier. The 16 tier-3 rows
all come from Gas Man: the three blood:gas partition coefficients, ten of the
eleven parameters of the reference adult patient, and the three MAC values. The
blood:gas coefficients are the Gas Man set as published by De Wolf et al., and
the ten patient parameters come from the Gas Man default patient. The two rows
that adopt no source are the anesthesia machine values: a circuit volume that
departs deliberately from the published Gas Man figure, and a default fresh gas
flow with no published counterpart.

**Of all the stored values, MAC (`mac_percent`) is the only one used as a
divisor for a displayed concentration.** The liquid density is the divisor for
the displayed millilitres of liquid agent (§ "Agent amount"). The three stored
MAC values are the ones that
De Wolf et al. state they used in their Gas Man simulations. MAC divides every
value shown in MAC multiples, so its tier affects a displayed clinical value as
well as a starting dial position. § "Delivery-limit and MAC parameters" states
what that costs, and § "Known limitations" records it. Two tier-2 sources are
cited beside the MAC values but not adopted: Mapleson's 1996 meta-analysis and
the age-related iso-MAC charts built on it.

**The thirty-one rows that adopt a source other than Gas Man are of six kinds.**

1. **All nine tissue:gas partition coefficients**, three per agent, from Yasuda,
   Targ and Eger 1989. They are human autopsy measurements at 37 °C, adopted as
   primary on 2026-09-13 after the stored values were checked against that
   paper's Table 1. § "v0.2.0: isoflurane and desflurane" says how they were
   checked, and why the published figures were *not* substituted for the stored
   ones.
2. **The eleventh reference-patient parameter, the venous pool volume**
   (`venous_pool_volume_l`), from Davis and Mapleson 1981. It is tier 2, adopted
   on 2026-09-07 on the project owner's decision.
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
   <!-- provenance: data/agents/sevoflurane.json liquid_density.measured_at_celsius = 20 -->
   <!-- provenance: data/agents/isoflurane.json liquid_density.measured_at_celsius = 20 -->
   <!-- provenance: data/agents/desflurane.json liquid_density.measured_at_celsius = 20 -->
6. **Three molar masses**, ChEMBL's formula masses, adopted the same day. They
   are tier 2 because a molar mass is computed from the molecular formula and the
   standard atomic weights, not measured on the agent, so no tier-1 source exists
   for one (§ "Agent amount").

**Each agent's data file cites primary blood:gas measurements beside its tier-3
blood:gas value, and marks each one as not adopted.** The sources are Strum and
Eger for sevoflurane, Eger for desflurane, Lerman et al. 1984 for isoflurane,
and Esper et al. 2015 for all three. Each entry records the measured value and
how far the stored number differs from it. Against the older measurements the
stored values are sevoflurane −5.2%, isoflurane −11.0% and desflurane −0.9%.
Esper et al. 2015 measured all three agents in 120 surgical patients at 37 °C.
Only its abstract was read. Against its means the stored values are sevoflurane
−12.2%, isoflurane −10.3% and desflurane −26.3%, so desflurane has the widest
gap in the project, about 3.8 of Esper's standard deviations.

The Gas Man study that prints this parameter set notes the gap in its own
footnote: its blood/gas coefficients "differ from them observed by Esper et al."
(Weber et al. 2021, Table 1). `docs/VERIFICATION.md` § "The early wash-in curve against the published
figures" records what Esper's desflurane value would do in this model. The Gas
Man values were kept and labelled on 2026-09-03, rather than moved to the
textbook 1.4 or to Lerman's measured 1.46 for isoflurane. The route to primary
values for all three agents is a planned milestone (`ROADMAP.md`
planned-milestone item 31).

**The reference patient's data file still adopts no primary source for any of
its eleven parameters, and records that in those words.** A measurement cited
beside a tier-3 number does not source it, which is the second of the three
rules below. So none of the five comparisons in the next paragraph changes or
promotes a stored value.

**Five of the eleven patient parameters have a measurement cited beside them
and explicitly not adopted.** For each, the patient's data file gives the
measured value, its reference conditions, and how far the stored number sits
from it. Hudgel and Devadatta measured FRC by helium dilution in ten healthy
men. Read with Wahba's review of the roughly 20 percent reduction under general
anaesthesia, that measurement brackets the lung gas volume. Cattermole et al.'s
686 subjects in the 50–75 kg band give a median cardiac output of 5.51 L/min,
and the stored value is 9.3 percent below it. Janssen et al.'s whole-body MRI
gives a skeletal-muscle mass. Its apparent agreement with the stored muscle
volume is a coincidence, since those men averaged about 86 kg rather than 70.
Heinonen et al.'s PET measurement of resting adipose perfusion is about half
what the stored fat flow fraction implies. Frayn and Karpe's review supplies the
muscle comparison. It also shows that the fat gap concerns the absolute flow,
not the muscle-to-fat ratio, which the stored fractions get right. The fat gap
is the largest of the five, and § "Known limitations" records it as well,
because it changes the shape of a displayed curve and not only a number in a
file.

**The other six patient parameters have no comparison, and their data file says
why for each**, so that a missing comparison is not taken for an oversight. Two
are not measurements. The reference weight is a label that no equation uses. The
venous pool is a well-mixed volume that sets the 14.7-second mixed-venous time
constant. It is not the physiologic venous blood volume, which is several times
larger. One, the default alveolar ventilation, is a convention: Gas Man's
program default. The remaining three each combine several tissues into one
group: the vessel-rich volume and flow fraction, and the fat volume. No single
measurement exists of what this model means by each of them.

**Nothing on the longest provenance chain behind the reference patient was
measured by anybody this document can name.** The chain runs Gas Man (tier 3)
→ Lowe and Ernst (tier 2) → ICRP Committee II (tier 2), a committee of the
International Commission on Radiological Protection.

**The lineage is Lowe and Ernst's, not Mapleson's.** The note beneath the Gas
Man Workbook's Model Parameters table (Appendix B, page 168) reads: "Values for
volume, flow and relative flow are taken from Lowe and Ernst, 1981". The book is
*The Quantitative Practice of Anesthesia: Use of Closed Circuit*, Williams &
Wilkins. The Workbook attributes nothing to Mapleson.

**The Workbook's Model Parameters table gives seven of the patient's eleven
values.** Alveolar volume, the three tissue volumes and the three flow fractions
are in the table and equal what is stored. Cardiac output appears only as the
sum of the flow column. Reference weight and alveolar ventilation are not in the
table. **The venous pool's 1.0 L is not in the table at all**: its `Blood` row
reads 5.00 L. Page 183's "Patient default options" describes the interface
controls and carries no numbers.

**The Workbook's Appendix C gives three of the four values that its Model
Parameters table does not supply.** Appendix C, "Gas Man System Defaults", pages
171–72, was read on 2026-09-15 from the private corpus. It prints the program's
defaults file, `GASMAN.INI`, verbatim. Its `[Volumes]` block gives `CKT=8.0`,
`ALV=2.5`, `VRG=6.0`, `MUS=33.0`, `FAT=14.5` and `VEN=1.0`. `[Ratio]` gives
`76`, `18`, `6`. `[Defaults]` gives `VA=4` and `CO=5`. So alveolar ventilation
is stated as a number, cardiac output does not rest on a column sum, and the
venous pool's 1.0 L is in the Workbook after all. Only the reference weight
(`weight_kg`) is in neither appendix. The Workbook's prose states it, together
with the 4 L/min alveolar ventilation, in Chapter 13, page 127.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->

**None of the Workbook pages above promotes a value to a higher tier.** Their
values are one program's defaults written down more than once, tier 3 each time.
The stored venous pool no longer uses Gas Man's value at all.

**Pages 55–60 and 82–84 of Lowe and Ernst were read at the source**, on
2026-09-08, from an interlibrary-loan scan. Two papers that use the book had
cited it at pages 57 and 83: Lerou and Booij's system model (*Br J Anaesth*
2001;86:12–28) and Couto da Silva, Mapleson and Vickers' study of Lowe's method
(*Br J Anaesth* 1997;79:103–12). Both were read at full text on 2026-09-06. This
repository does not hold the scan, because it is under publisher copyright and
the repository is public. The scan's own record gives the author as Lowe, Harry
J., so his initials are `HJ`, and the Workbook's `HF` is a misprint.

**Lowe and Ernst collects its volumes and flows and cites them onward to four
references, so it is tier 2, a secondary synthesis.** On page 56 it says of
figure 4.1b, the table in which the volumes and flows are printed: "The figure
models a 100-kg patient with normal physiologic organ volumes and blood flows
(9, 19, 20, 26)." Chapter 4's own narrative names three of those references:
Mapleson, Smith et al. and Zwart et al. The reference patient's only provenance
chain goes on past Lowe and Ernst, and still ends in nobody's measurement.

**All four references behind Lowe and Ernst have been identified, and three of
them, references 9, 19 and 20, are uptake-and-distribution models.** Chapter 4's
reference list, on pages 64–65, was read on 2026-09-10 from a second
interlibrary-loan scan, and each reference was matched to its PubMed record.
PubMed holds no abstract and no PubMed Central text for any of the three journal
papers.

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

A model takes organ volumes and blood flows as inputs and does not measure
them, so none of references 9, 19 and 20 can be where the values in figure 4.1b
were measured. Reference 26 is the only one of the four that is not an
anesthetic model. It is cited to a single page, and that page ends the chain.

**The chain from Gas Man through Lowe and Ernst to the ICRP report ends at
tier 2, and never reaches tier 1.** Page 151 of the ICRP report was read on
2026-09-10. It carries **Table 8, "Organs of standard man — Mass and effective
radius of organs of the adult human body"**, tabulated for a total body of
70,000 g. A "standard man" is a reference specification agreed by a committee,
and the document's own title is *Report of Committee II*. The table gives no
citation, sample count or dispersion for any row, while each tissue row of
Table 7, on the facing page 150, carries a count in parentheses. Under the
hierarchy at the head of this section, a consensus document that collects
primary measurements without making one is **tier 2**.

**Four of the ten rows in Lowe's figure 4.1b correspond to ICRP's Table 8
closely enough to be an inheritance.** The comparison is at 100 kg, where his
kilogram column can be treated as per cent of body weight: brain 2.1 against
2.1, kidney 0.4 against 0.43, heart 0.4 against 0.43, and muscle 42.6 against
43. Five rows do not correspond: skin 10.0 against 8.7, adipose 15.0 against 14,
blood 7.0 against 7.7, lung 0.8 against 1.4, and bone 12.0 against a skeleton of
10 without marrow or 14.2 with marrow. **The liver is the outlier that matters:
5.7 against 2.4.**
<!-- not-restated: 2.1, 2.4 -->

**The gap in the liver row has a candidate explanation, from this project's
arithmetic rather than from the book.** Liver 1,700 g plus gastrointestinal
tract 2,000 g plus spleen 150 g plus pancreas 70 g is 3,920 g. That is **5.60%
of 70 kg against Lowe's 5.7%**. This group of organs is the hepatoportal
compartment, which an uptake model lumps together because the splanchnic bed
drains through the liver. No other grouping of Table 8 comes as close. Neither
document says that this is what happened, and the match is no evidence against
either author.
<!-- not-restated: 70 kg -->

**The stored vessel-rich volume rests on a lumping decision made one link up the
chain.** The vessel-rich volume (`tissue_groups.vessel_rich.volume_l`) is stored
as 6.0 L. The only grouping of Lowe's compartments that reproduces both that
volume and the stored 0.76 perfusion fraction is kidney + heart + brain + liver,
at 8.6% of body weight. On ICRP's own rows those four organs are **5.36%, which
is 3.75 L at 70 kg**, 38% below what is stored. **No stored value changes
because of this, and none should.** Lumping the splanchnic bed into the liver
compartment is ordinary modelling. § "Tissue compartments" above already treats
the vessel-rich group as one lumped tissue. Nothing here is sourced to ICRP.
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.volume_l = 6 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**ICRP's Table 8 has no blood flows.** It gives mass and effective radius, and
nothing else. Yet Lowe and Ernst cite all four references together for "organ
volumes *and blood flows*". So reference 26 cannot be the origin of any of the
perfusion fractions, which set every time constant this model computes. The
fractions must come from reference 9, 19 or 20, and all three of those are models.

**References 19 and 20 measured nothing.** Both were read in full text on
2026-09-10. They share one parameter set. Reference 20's Appendix says its
tables "are the same as used by N. Ty Smith in his article … where he gives the
rationals for our choice", so the provenance lies in reference 19. Reference 19
says that the table this chain would need "lists the **assumed** blood volumes,
tissue volumes, and partition coefficients", and it gives no source for any of
these values. Its *flows* are compiled from "several sources, most of which can
be found in a recent review", which is the authors' own handbook chapter. The
awake cardiac output of 5,800 ml/min is taken from Milnor's chapter in *Medical
Physiology*, 12th edition. The compiled flows did not balance, and the authors
made them balance. Total cardiac output was 3,480 ml/min, against regional flows
summing to 3,290 ml/min, and "the discrepancy was compensated for by adjusting
the values for skin and skeletal muscle flows". **A stated assumption is not a
source, and an adjusted sum is not a measurement.** So neither paper can be
promoted to a higher tier, and neither is a candidate for adoption.

**References 19 and 20 are not the origin of figure 4.1b.** Reference 19
models a 75 kg man in twelve compartments: arterial, brain grey, brain white,
heart, well-perfused organs, poorly-perfused tissue, fat and fatty marrow,
splanchnic, skeletal muscle, skin shunt, vena cava, and lung. Lowe has ten rows
for a 100 kg patient, and the numbers do not correspond. The vessel-rich
equivalent in reference 19 is 64.0% of cardiac output, against Lowe's 76%. Its
fat is 16.3% of body mass, against Lowe's 15.0%.

**The perfusion fractions therefore still have no identified origin.**
References 19 and 20 give different flows for different compartments. Reference
20 names Mapleson 1963, reference 9, only as the source of the model
*concept*. The paragraphs below record what reading it found.

**For developers.** The reference patient's data file is
`src/anesthesia_sim/data/patients/reference_adult.json`, and the anesthesia
machine's is `src/anesthesia_sim/data/machines/reference_circle_system.json`.

The counts of stored-value rows in this section appear at its head and in the
list of the thirty-one rows that adopt a source other than Gas Man. Recompute
all of them with `python3 tools/source_tier_counts.py` rather than by hand. The
script counts the stored values that each source is the authority for (the
`authority_for` list of each `sources` entry), per data file and in total, and
names the source behind every row. Each data file gives the tier of every source
it lists. No check compares the counts in either place with the text, so they
can go stale silently. Whoever changes a count must check that the sentence
around it is still true.

**Mapleson 1963, Lowe and Ernst's reference 9, closes the chain of sources.
Their references 19 and 20 are its Table 1, lumped and relabelled, and most of
its volumes come from their reference 26, an ICRP report.** Mapleson 1963 was
read on 2026-09-10. His Appendix 1 opens:
"*Tissue volumes and blood supplies.* With the following exceptions the volumes
in Table 1 are those for the 'standard man' of the International Commission on
Radiological Protection (I.C.R.P.) (23)…". His reference 23 is that report at
**page 151**, which is Lowe and Ernst's reference 26. So Lowe and Ernst very
likely took the ICRP citation from Mapleson's own reference list. When Table 1
is lumped as Smith's own footnotes describe, it reproduces **all nine rows** of
references 19 and 20. Those nine rows sum to 58.04 litres, against Mapleson's
own 58.04.

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
Mapleson's Appendix 1: "it has been thought legitimate to assume that **the
blood flow to any region is a fixed fraction of the total cardiac output** from
20 to 70 years of age."

**The perfusion fractions this model runs on have no identified origin in any
reference the book names for them.** Reference 26 has no flows at all, and the
other three do not match. Figure 4.1b's flow column cannot be reproduced from
any of the four. On Mapleson's own rows, kidney + heart + brain + liver is 3,820
of 6,480 ml/min, which is **59.0%**. Every well-perfused organ together is
**63.0%**. Lowe has **76%**, and Smith and Zwart have 64.0%. Muscle plus skin
nutritive is 10.2%, against Lowe's 13%. Fat plus fatty marrow is 4.0%, against
Lowe's 5%. **This finding covers only the four documents that have been read.**
An origin may still exist: the book prints more than one table, and Gas Man may
lump differently.
<!-- not-restated: 5 % -->

**Three stored values also appear in those tables, but none of them comes from
there.** They are an alveolar ventilation of 4 l/min, a functional residual
capacity of 2.5 l in reference 20's table only, and a skeletal muscle tissue
volume of 33 litres. Two of the three figures in those tables descend from
Mapleson, and one is a coincidence. The 2.5 L is Mapleson's functional residual
capacity. It is a mean of published human measurements, cited to Dittmer and
Grebe's *Handbook of Respiration*, and not a round number somebody chose. It is
still not the stored value's source. Mapleson's row is FRC plus half the tidal
volume, whereas this model stores an alveolar gas volume. The stored value also
reaches this project through Gas Man. Gas Man's upstream source is Lowe and
Ernst, who state no alveolar gas volume at all. The 33 is Mapleson's muscle 30
plus skin nutritive 3, which is exactly how Smith prints it. It is *not* the
stored 33.0, because Lowe's muscle row is 29.8 L at 70 kg and reproduces the
stored value under no grouping. Alveolar ventilation of 4 l/min stays a
coincidence, because Mapleson gives a formula, not a figure. **No stored value
changes because of these findings.**
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

Mapleson 1963 is one of the four documents read, but that does not make
Mapleson the *Workbook's* source. The Workbook attributes nothing to Mapleson.
Lowe and Ernst cite him for a table they collected, two links further up the
chain.

**The book's model patient weighs 100 kg, which is why the material arrives in
this project as fractions.** Page 56 picks that weight so that "the organ
weights can also be read as per cent of total body weight". So Lerou and
Booij's Table 6 of fractions is the book's own table divided by 100, not a
normalization they performed. Nothing in the book states a 70 kg parameter set.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**The book's cardiac-output relation gives 4.84 L/min at 70 kg, against the
5.0 L/min stored here.** Page 59, read at the source, gives the cardiac output
for its worked prime dose as $`2M^{3/4}`$ dl/min, "or 63.25 dl" for the 100 kg
patient. That is 0.2 times body mass to the three-quarter power in L/min. The
stored 5.0 would need 73.1 kg. The worked value of 63.25 dl determines the
exponent on its own, without reading a superscript off a scan. The stored
cardiac output stays a fixed 5.0, and § "Known limitations" below gives the
reasoning.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->

**The cardiac-output relation is derived, not measured, and pages 17–19 show
how.** Page 59 states $`2M^{3/4}`$ without citing anything. Chapter 2 builds the
relation in three steps, and neither of its two constants is a cardiac-output
measurement:

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
- **Figure 2.4, page 19** does the arithmetic. kg^(3/4) × 10 gives O₂ use in
  ml/min. O₂ use ÷ 5 gives cardiac output in dl/min, and the figure annotates
  that divisor as "(a–v)DO₂ = 5 ml/dl". The figure also draws the two steps
  combined, kg^(3/4) × 2 → $`\dot{Q}`$ in dl/min, which is page 59's constant.

<!-- not-restated: 2.4 -->

So $`0.2M^{3/4}`$ is Brody's mammalian metabolic allometry divided by an
arteriovenous difference that is assumed constant across mammals. **4.84 L/min
at 70 kg is therefore a derived interspecies extrapolation and must not be
treated as a measured human cardiac output.** This matters in § "Known
limitations" below, the only place in this document that sets the figure beside
Cattermole et al.'s measured median.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**Checked against the book itself, the Workbook's attribution survives for
three of the seven values and fails for four.** The seven are the volume and
perfusion fraction of the vessel-rich, muscle and fat groups, and the alveolar
gas volume. The vessel-rich pair reproduces exactly and *uniquely*. Kidney,
heart, brain and liver are 8.6% of body weight at 76% of cardiac output. That
is 6.02 L at 70 kg against the stored 6.0, and 0.76 against the stored 0.76.
Of all 1023 non-empty groupings of the book's ten compartments, no other
matches both values to within half a percentage point. The same search finds
**no** grouping for the stored muscle pair (33.0 L at 0.18, against the book's
muscle row at 29.8 L and 0.130), and none for the stored fat pair (14.5 L at
0.06, against adipose at 10.5 L and 0.050). The alveolar gas volume is the
third value that survives, and it survives in a negative sense. The book states
no alveolar gas volume at all. It lumps the circuit and the patient's FRC into
a single ventilatory volume of "about 100 dl". So the Workbook cannot have
taken 2.5 L from it.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.volume_l = 33 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.muscle.perfusion_fraction = 0.18 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.fat.volume_l = 14.5 -->
<!-- provenance: data/patients/reference_adult.json tissue_groups.fat.perfusion_fraction = 0.06 -->
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->
<!-- not-restated: 0.050 -->

**For the four muscle and fat values, the book's split of cardiac output
survives, but the values do not.** The book's five non-vessel-rich compartments
take 13 + 3 + 2 + 1 + 5 = 24% of cardiac output, and the stored muscle and fat
fractions sum to exactly 0.24. Their volumes do not follow: 83.6% of body
weight is 58.5 L at 70 kg, against the stored 47.5 L. So Gas Man appears to
have kept the book's 76/24 flow split, and to have redistributed the 24 across
two compartments where the book has five, over a smaller tissue volume. That
arithmetic is this project's, and it does not prove the Workbook wrong. Gas Man
may lump differently, or may work from a page outside the range supplied. The
data file carries the figures and the detail for each value.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**Nothing is promoted or adopted because of any of it.** All seven values stay
tier 3, with the Workbook as their adopted authority, and Lowe and Ernst stays
cited and not adopted. Learning where Gas Man's numbers came from is not
evidence that they were measured. For the four that do not reproduce, there is
nothing here to adopt. For the ones that do, adopting would mean naming as the
authority a compilation, not a measurement. What the reading
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
one well-mixed venous pool that carries tissue return. Their Appendix derives
it from the ICRP (1975) blood distribution rather than measuring it, so it is
tier 2. **It was adopted on 2026-09-07, on the project owner's decision**, and
is stored as 1.222 L (`venous_pool_volume_l`). It is called a pool because
"venous blood volume" would suggest the physiologic venous blood volume, which
this is not. At the stored 5.0 L/min cardiac output, the mixed-venous time
constant is 14.7 s, against 12.0 s at Gas Man's 1.0 L. That 1.0 L is a program
default, tier 3. Appendix C's `GASMAN.INI` listing, on page 172, reads
`[Volumes] … VEN=1.0`. Davis and Mapleson's 1222 ml is tier 2 and is the same
object this model has, so the stored pool is a considered replacement for that
default. Nothing argues for restoring 1.0 L.
<!-- provenance: data/patients/reference_adult.json venous_pool_volume_l = 1.222 -->
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5 -->
<!-- not-restated: 70 kg -->

**The larger pool leaves the wash-in comparison unchanged and moves elimination
further from published data.** The 30-minute $`F_A/F_I`$ wash-in distances
from the published cohort means move by 0.01 SD or less (+0.16, +0.31, +0.79, +0.38 SD
at the stored pool). The pool has long since equilibrated by then. So the
published wash-in comparison cannot discriminate between the two values. The
5-minute $`F_A/F_{A0}`$ elimination ratios move **0.11 to 0.13 published SD
further from** their cohort means in each agent's first cohort: sevoflurane
+3.67 to +3.79, isoflurane +4.02 to +4.15, and desflurane +1.02 to +1.13. They move because a larger pool returns
more agent to the lungs. `docs/VERIFICATION.md` § "Published wash-in and elimination validation test"
already attributes a shift in the same direction to this model's rebreathing
circuit rather than to tissue return. This shift is between a thirtieth and a tenth of
the gap it adds to.
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

The following table records every stored value. Each value is
loaded from a versioned data file and validated against its schema, rather than
written into the program. That file records full citations, definitions and
reference conditions in its `sources` entries, and the table does not repeat
them.

Each row names the file and the exact key path that locates its value in that
file, so a row traces to one stored value, not to a file that happens to
contain a matching number. A check compares each row's key path and value with
its file, as § "How this document is held to the tree" describes. A row for a
derived value states the stored value beside it. The tissue:blood coefficients
are computed from the tissue:gas and blood:gas values when a file is loaded, so
their rows name the key path of the stored tissue:gas value and show the
division.

| Parameter | Selected value | Unit | Source (data file · key path) |
| --- | ---: | --- | --- |
| Blood:gas partition coefficient (sevoflurane) | 0.65 | dimensionless | `data/agents/sevoflurane.json` · `blood_gas_partition_coefficient` |
| Vessel-rich tissue:blood coefficient (sevoflurane) | 1.6923 (= 1.1 / 0.65) | dimensionless | `data/agents/sevoflurane.json` · `tissue_gas_partition_coefficients.vessel_rich` |
| Muscle tissue:blood coefficient (sevoflurane) | 3.6923 (= 2.4 / 0.65) | dimensionless | `data/agents/sevoflurane.json` · `tissue_gas_partition_coefficients.muscle` |
| Fat tissue:blood coefficient (sevoflurane) | 52.3077 (= 34.0 / 0.65) | dimensionless | `data/agents/sevoflurane.json` · `tissue_gas_partition_coefficients.fat` |
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
| 1 MAC, single adult value with no age stated by its source (sevoflurane) | 2.0 | percent | `data/agents/sevoflurane.json` · `mac_percent` |
| 1 MAC, single adult value with no age stated by its source (isoflurane) | 1.2 | percent | `data/agents/isoflurane.json` · `mac_percent` |
| 1 MAC, single adult value with no age stated by its source (desflurane) | 6.0 | percent | `data/agents/desflurane.json` · `mac_percent` |
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
describe, and no equation in this model uses it. The compartment volumes and
flows are the source's absolute values for a 70 kg adult, not quantities scaled
from a weight, so changing the weight alone would not rescale them. The litres
are Gas Man's form of the data. The Workbook names Lowe and Ernst as its
source, and that book prints the same material as per cent of a 100 kg body,
with cardiac output an allometric function of mass.
<!-- provenance: data/patients/reference_adult.json weight_kg = 70 -->

**The vessel-rich flow fraction is 0.76 here and 75.8% in one of the two
reachable publications of the same parameter set.** Weber et al. 2021's Table 2
prints 76.00%. The stored value comes from the
Workbook's own page-168 table, which gives the vessel-rich relative flow as
0.76 (read at the source on 2026-09-06). The twelve partition coefficients come
from De Wolf et al. 2012. Their Table 1 prints 75.8, and 75.8 + 18 + 6 = 99.8.
The model requires the flow fractions to sum to 1 within the tolerance that
§ "Tissue groups" gives, so the published set could not be stored as printed,
even if it were preferred. The difference changes the vessel-rich time constant
by 0.26%, below the resolution of anything a learner reads off the curve. The
De Wolf entry in the reference patient's data file (`reference_adult.json`)
records the difference in full.
<!-- provenance: data/patients/reference_adult.json tissue_groups.vessel_rich.perfusion_fraction = 0.76 -->

There is no "arterial blood-pool volume" row, because arterial blood has no
volume of its own in this model (see § "Model boundary").

**The circuit volume and the default fresh gas flow adopt no source of any
tier.** The reference patient adopts no primary source but does adopt tier-3
ones, so these two machine rows have the wider gap. Both describe the
apparatus in front of the patient, so they are stored in a third kind of
parameter file, `data/machines/reference_circle_system.json`.

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
  and cannot assume that value. Like every circuit volume in this model, the
  6.0 L is one total for the apparatus and the patient circuit together
  (§ "Breathing circuit"). No source says how it divides between the two.
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
  measurement. **The default is also the flow a run starts at when a machine
  profile states none**, because no surveyed machine publishes a startup flow.
  The authority for that fallback is this rationale, not a source. The
  rationale applies to the stored 6.0 L circuit. A smaller circuit gives a
  shorter lag at the same flow, as § "What real workstations hold" below
  computes.

<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->
<!-- not-restated: 10 L/min -->

**The project holds one measured circle-system volume, and it bounds the
circuit-volume row rather than replacing it.** Targ, Yasuda and Eger measured a
conventional circle system by water filling at **9860 ml** (*Anesth Analg*
1989 Aug;69(2):218–25, PMID 2764290). The same study lies behind the
inert-circuit entry under § "Known limitations". It was read in full text on
2026-09-13 from the private reference corpus. The value is not adopted, because
the measured system included a latex reservoir bag at the Y-piece **standing in
for the patient's lungs**. Adopting 9.86 L as the circuit volume would
therefore put a lung inside the circuit, and then model it again as the 2.5 L
alveolar compartment. The bag cannot be subtracted, because the paper states no
bag volume, and a latex bag full of water distends past whatever it holds as a
gas reservoir.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->

What the measurement supplies instead is a **bound and an ordering**. A real
conventional circle system has an assembled volume of at most 9.86 L, apparatus
and patient circuit together. That bound leaves both the stored 6.0 L and the
Workbook's 8.0 L admissible. It also puts the three figures in one order,
6.0 L, 8.0 L and 9.86 L, of which only the last was measured. At 4.0 L/min the
implied circuit time constants are 90 s, 120 s and 148 s.
<!-- derived: 148 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->

**Compare the measured 9.86 L with the model's circuit and lung together, not
with the circuit alone.** Targ measured an assembled system *plus* a lung. This
model's corresponding total is $`V_C + V_A`$ = 6.0 + 2.5 = 8.5 L, which is
13.8% below the measured 9.86 L. Comparing the circuit alone, 6.0 against 9.86,
would show 39% below. The study itself invites the comparison with circuit and
lung together. Its Figures 3 and 5 draw the ideal wash-in and washout as
$`100[1 - e^{-(\dot V/V_S)t}]`$ with $`V_S`$ = 9.86 L. So its own time
constant is total system volume over inflow, the same $`V/\dot V_F`$ that this
document uses. The 9.86 L is compared, not adopted, because a latex bag is not
a lung, and that apparatus had no patient taking up agent.
<!-- derived: 8.5 L from data/machines/reference_circle_system.json circuit_volume_l = 6.0 -->
<!-- derived: 8.5 L from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->

**What real workstations hold, and why that does not settle the circuit-volume
row either.** The project's survey of machines in current clinical use
(`docs/machine-survey.md`) covers the variables that affect a number this model
computes. The assembled volumes it gives sit below both figures above. Shin et
al. print apparatus volumes of 4.7 L for a Dräger Primus, 2.1 L for a Perseus
A500 and 2.0 L for a Zeus IE. Each includes the absorber and excludes the
disposable patient circuit. Adding the 1.2 L circuit that they computed their
totals with gives 5.9, 3.3 and 3.2 L. At the default flow, the circuit time
constant therefore runs from 89 s on the oldest of the three machines to about
50 s on the newest. That is a factor of about 1.8 across machines that a
learner would meet in the same department. The stored 6.0 L lies within 2% of
the Primus's assembled 5.9 L. The match is a coincidence: the stored value
predates the survey, and was kept under the project owner's ruling of
2026-09-01.
<!-- derived: 89 s from data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4.0 -->
<!-- provenance: data/machines/reference_circle_system.json circuit_volume_l = 6 -->
<!-- not-restated: 2 % -->

**Volume is not the whole of the difference between machines**, as the survey
found. Fukuda et al. moved only the fresh gas inlet, with the machine and the
volume held fixed. The inspired/delivered ratio of both isoflurane and
sevoflurane rose significantly at low flow (*J Anesth* 2006;20(4):268–73).
That ratio, $`F_I/F_D`$, is what the circuit equation above computes, so a real
machine changed it through a property this model does not represent: the layout
of its internal gas paths. A future per-machine circuit volume
(`circuit_volume_l`) will therefore reproduce only part of the difference
between machines, and must not be described as reproducing all of it. The
model will not fold that layout into an effective volume either, because that
would attribute to volume a difference that volume did not cause. The survey
sets out the consequence for modelling several machines.

**A search for a published source of the default fresh gas flow found a
recommendation, not a convention.** The survey looked for a startup fresh gas
flow published by any machine in current clinical use, and found none
(`docs/machine-survey.md` § "(a2)"). So the flow row still adopts no source,
and no published startup convention appears to exist. Kalmar et al. conclude
that *"routine clinical practice using what historically is called 'low flow
anaesthesia' (e.g. 2 L/min FGF) should be abandoned"* in favour of automated
minimal-flow delivery (*J Clin Monit Comput* 2022;36(6):1601–1610,
PMID 34978655). The paper was read in full text on 2026-09-20 from PubMed
Central, PMC9637609, where the quoted sentence closes the abstract. The
conclusion is the recommendation of a single-centre retrospective study, not a
measurement of what flows are used. But the study's own comparator is a fixed
2 L/min group that it calls conventional low flow, and that flow already sits
below this model's 4.0.

**The 4.0 L/min default makes no claim about clinical practice**, because
no source this project holds supports one. Under the project's safety-critical
standard, a correct number with a wrong provenance is still a presentation
failure. A different default would not remove the problem, because an
unlabelled default teaches a norm whatever value it has. A default of
0.5 L/min would have no source either. It would also put the apparatus lag at
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

**Dividing tissue:gas by blood:gas is the literature's own operation, and one
published table reproduces its results.** Eger and Saidman state the operation
in these words: "a tissue/blood partition coefficient for a given anesthetic is
calculated by dividing a tissue/gas partition coefficient by the blood/gas
partition coefficient for that anesthetic" (p. 1023). Yasuda, Targ and Eger
computed their own tissue:blood table the same way, as the next subsection
records. Both papers were read in full text from the private reference corpus.
Eger and Saidman's p. 1023 was read on 2026-10-25. The full citation of Eger
and Saidman is in § "Known limitations".

Baker and Farmery's 2011 review publishes the results as well as the
operation. Its Table 2 (p. 572) prints two sets of tissue:blood coefficients
for the vessel-rich, muscle and fat groups. The set that matches the derived
rows is the one in brackets, which the table's footnote d attributes to Eger
and Shafer's 2005 tutorial. Desflurane has only that set. The table was read in
full text from the private reference corpus on 2026-10-25. In each cell below,
the first figure is the derived value from the parameter table above, and the
second is Baker's bracketed figure:

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
precision. Desflurane's fat coefficient is the exception: 30.9524 rounds to
31.0, and Baker prints 30.9. The difference is 0.05, or 0.17%, in the last
printed digit. That is too small to come from a different operation, and Baker
does not say how the figures were rounded.
<!-- not-restated: 0.05 -->
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- derived: 30.9524 from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13, blood_gas_partition_coefficient = 0.42 -->

**The agreement with Baker's table checks that the division is the right
operation and was done correctly, not that the coefficients are right.** It
shows that the stored tissue:gas values, divided by the stored blood:gas
values, give the coefficients as the literature publishes them, which confirms
the operation and its arithmetic. It is not a second measurement. Eger and
Shafer's tutorial ran its simulations in Gas Man, according to its abstract.
The stored tissue:gas values are Gas Man's figures for Yasuda, Targ and Eger's
measurements, and the stored blood:gas values are De Wolf et al.'s. In all
seven cells where Gas Man's figure differs from Yasuda's mean, Baker's
bracketed figure follows Gas Man's. Isoflurane fat is the clearest: 53.8 is
70.0 divided by 1.3, where Yasuda's 64.2 would give 49.4. So the match is one
parameter set divided twice, not two sources agreeing. Eger and Shafer's paper
is not held here, so it is not known which of the two took its figures from
the other. A reader should take the table as evidence that the division is the
right operation, and not as evidence that the coefficients are right.
§ "Known limitations" says how far other laboratories' coefficients differ
from these.
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->

**Baker's other set of coefficients is not a check on the division.** The
unbracketed figures are "Data from Fiserova-Bergerova and Diaz (26)", a 1986
paper. They come with their own blood:gas values, 0.6 for sevoflurane and 1.4
for isoflurane, and they differ from the derived rows by far more than
rounding. § "Known limitations" gives the differences.

The citations of Baker and Farmery 2011, Eger and Shafer 2005 and
Fiserova-Bergerova and Diaz 1986 were checked in PubMed on 2026-10-25 (PMIDs
23737195, 16115976 and 3721592). Only Baker and Farmery was read in full text,
and its full citation is in `docs/references/README.md`.

**For developers.** The patient weight (`ReferenceAdultParameters.weight_kg`) is
loaded and checked to be positive and finite, and nothing else reads it.

Two checks each reject a set of flow fractions whose sum differs from 1.0 by
more than the tolerance in § "Tissue groups" (`FLOW_FRACTION_TOLERANCE`). One
runs on the reference patient's data file
(`_ReferenceAdultPayload._perfusion_fractions_must_sum_to_one`), and the other
runs when the patient's compartments are built (`PatientCompartments.__post_init__`).
The tolerance stays as it is, because one loose enough to admit De Wolf's 99.8%
would also admit a transcription error silently.

The fallback starting flow comes from a constant in `core/circuit.py`
(`TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`). One test checks that fallback
(`test_a_profile_omitting_the_default_fresh_gas_flow_falls_back_to_the_teaching_default`),
and another fails if the constant and the shipped machine file's value ever
differ (`test_the_flow_default_matches_the_shipped_machine_file`).

A design document records the decision not to fold gas-path layout into an
effective volume (`docs/machine-abstraction.md`), and the roadmap says when
that decision is revisited (`ROADMAP.md` planned-milestone item 39).

The tissue:blood coefficients are computed by properties of the class for an
agent's parameters (`AgentParameters`, in `core/parameters.py`). One test in
`tests/unit/test_parameters.py`, `test_derives_tissue_blood_coefficients`,
checks the division of tissue:gas by blood:gas, for sevoflurane.

### v0.2.0: isoflurane and desflurane

Sevoflurane, isoflurane and desflurane share one set of equations, compartments and reference
adult patient (§ "Governing equations"). An agent enters those equations only through its four
partition coefficients: one blood:gas and three tissue:gas. Its other stored values, such as its
MAC and its vaporizer's maximum, set a control or convert a displayed amount, and the equations do
not use them (§ "Delivery-limit and MAC parameters", § "Agent amount"). All twelve coefficients
come from one table, so the three agents' values can be compared directly. The table is De Wolf
et al. 2012, Table 1, from the paper already cited for sevoflurane.

Desflurane is markedly less soluble than sevoflurane, which is itself less soluble than
isoflurane (blood:gas 0.42 < 0.65 < 1.3). Because the equations are shared, lower solubility
only makes the agent equilibrate faster.

<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->

**The nine tissue:gas coefficients of sevoflurane, isoflurane and desflurane all come from one
study.** In De Wolf's table, they are the Gas Man simulation program's figures for the human
measurements of Yasuda, Targ and Eger 1989. That study measured all three agents' tissue:gas
coefficients side by side in the same specimens, in *one laboratory, with one technique and one
cohort*. Any systematic error in that technique therefore affects every agent alike. When values
are shown as multiples of MAC to compare agents, an error that all three share cannot make one
agent look different from another.

The three blood:gas values can be compared only because they come from one published table. They
are Gas Man's set, at tier 3 of the source grades in § "Source hierarchy".

The argument from a shared source covers the partition coefficients only. It does not cover the
stored MAC values, which differ from Mapleson's age-40 values in opposite directions for sevoflurane
and desflurane. § "Delivery-limit and MAC parameters" gives the differences.

**Gas Man's Workbook says the nine tissue:gas coefficients come from Yasuda, Targ and Eger, and
the paper confirms it.** The note under the Workbook's page-168 parameter table reads "Values for
isoflurane, halothane, desflurane and sevoflurane are taken from Yasuda, Targ and Eger". That
note alone could not raise the coefficients' source grade, because a program's statement about its
own sources is not independent evidence (§ "Republication does not promote a value between tiers").
The note had two further weaknesses. The Workbook's reference 45 is the 1988 ASA annual-meeting
abstract `Anesthesiology 69:A615`, not Yasuda, Targ and Eger's 1989 *Anesthesia & Analgesia*
paper. And the same Workbook paragraph credits sevoflurane's values to Yasuda and, one sentence
later, to "the package insert and Abbott data".

So the 1989 paper itself was read in full on 2026-09-13. Its Table 1 reports tissue:**gas**
coefficients, the quantity that the model stores. They come from 14 autopsy specimens, 6 to 10
per tissue, with a mean age of 65.8 ± 14.4 yr, equilibrated at 37 °C. In the table below, each
cell gives the stored value, then the paper's mean ± SD, then the difference in SDs.

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

All nine stored values lie within 0.71 SD of the measured mean. Two match it exactly. Two more lie
within 1% of it: isoflurane vessel-rich (+0.5%) and sevoflurane muscle (+0.8%). The other five
differ from it by 2.3% to 9.0%, the most for isoflurane fat, which lies above the mean. Values from
another source could not match this closely by chance, so the comparison confirms the Workbook's
attribution. For sevoflurane, it also settles the Workbook's contradiction: the three stored values
match this paper, not a package insert.

Two further points matter for the model:

- **The vessel-rich coefficient is Yasuda's *brain* value.** Table 1 gives
  brain, heart, liver and kidney separately (sevoflurane 1.15, 1.21, 1.25,
  0.78). Sevoflurane's stored 1.1 is 4.3% below its brain value and 0.2% above
  the equal-weight mean of its four organ values, 1.0975, so sevoflurane alone
  does not show whether Gas Man used the brain value or the mean. Isoflurane's
  stored 2.1 is 0.5% above its brain value, 2.09, and desflurane's stored 0.54
  equals its brain value (the table above). These two matches indicate that
  the vessel-rich compartment uses the brain values, and a learner reading its
  trace is reading a brain trace.
  <!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1 -->
  <!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.vessel_rich = 2.1 -->
  <!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.vessel_rich = 0.54 -->
- **Yasuda's paper is not a source for the stored blood:gas values.** It
  measured none. Its Table 2 tissue:blood figures are calculated "by dividing
  the tissue/gas partition coefficient by the published values for the
  blood/gas coefficients adjusted for age". So Table 1 ÷ Table 2 recovers the
  age-adjusted blood:gas of the 65.8-year-old cohort. Those recovered values
  are 4.9–9.4% above the three round figures stored here.

**For the nine tissue:gas coefficients, the source grade changed and the stored values did not**
(project owner, 2026-09-13). These were two separate decisions.

*Adopted.* The nine tissue:gas coefficients trace back to a primary human measurement. So for all
three agents, the recorded source of these coefficients is now Yasuda, Targ and Eger, at tier 1,
the grade for a primary measurement. De Wolf et al. stays the source for the three blood:gas
values, which this study did not measure. Only the recorded source and grade changed. No number
did.

*Declined.* Storing Yasuda's published figures instead of Gas Man's for the nine coefficients
would change seven of the nine stored values, and the time constant of each compartment they
belong to. Three changes are large. Sevoflurane's vessel-rich time constant would move +4.5%
(coefficient 1.15 instead of 1.1), isoflurane's fat −8.3% (64.2 instead of 70.0), and
desflurane's fat −7.7% (12.0 instead of 13.0). The other four move by 3.1% or less. The accuracy
gained would be smaller than the error the model already makes by lumping brain, heart, liver,
kidney and viscera into one vessel-rich compartment. A lumped compartment cannot use a difference
of 0.05 in a brain measurement. So the Gas Man values are kept.
<!-- provenance: data/agents/sevoflurane.json tissue_gas_partition_coefficients.vessel_rich = 1.1 -->
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->
<!-- provenance: data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13 -->
<!-- not-restated: 0.05 -->

**Desflurane's tissue coefficients were checked against a published measurement and kept.**
Desflurane's elimination at five minutes is the only comparison where the model misses a human
measurement by washing out too fast. That result is most sensitive to the vessel-rich
coefficient, which makes that coefficient the obvious suspect. It is not the cause.
`docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not changed" gives the reasoning.

**For developers.** Each agent's partition coefficients are in
`data/agents/*.json`, whose `tier` and `adopted` fields record each value's
source. The reference adult patient's physiologic parameters are in
`data/patients/reference_adult.json`. Storing Yasuda's figures would require
recomputing every pinned reference state under `tests/reference/`, because
those states are this parameter set's solution. `tests/unit/test_parameters.py` checks each
stored coefficient against a literal. `tests/reference/test_multi_agent.py`
checks mass balance and equilibrium for isoflurane and desflurane, and that
desflurane's alveolar-to-circuit ratio is above isoflurane's after one minute. Before changing any of desflurane's
coefficients, read `docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not changed".

### Delivery-limit and MAC parameters

This section specifies two of an agent's stored values that play no part in the model's
equations: its maximum delivered concentration and its MAC. A value that a clinician could read or
act on is safety-critical whether or not the model uses it. § "Agent amount" specifies the
agent's molar mass and liquid density, and `docs/INTERFACE.md` § "MAC-awake as a chart reference"
specifies its MAC-awake.

The maximum delivered concentration (`max_delivered_concentration_percent`) is the highest
concentration that the agent's real vaporizer can deliver: sevoflurane 8%, isoflurane 5% and
desflurane 18%. It sets the top of the delivered-concentration dial, so that the simulator offers
no dial position that the matching real device lacks. It is a device limit, not a physiologic or
safety limit, and it says nothing about whether a concentration is appropriate for a patient.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: data/agents/isoflurane.json max_delivered_concentration_percent = 5 -->
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

The simulator **must reject** any delivered concentration above the maximum, when a run is set up
and at every later change. It must not lower the value to the maximum instead, because it would
then simulate, display and chart a dial position that was never requested. On screen, that
position looks exactly like one that was requested. Zero is always accepted, because zero is the
vaporizer turned off, which is how washout begins.

**The maximum delivered concentration describes a vaporizer, although it is stored with the
agent.** Each agent's value is the calibrated dial maximum of the vaporizers that its source
names: the Dräger Vapor 2000 and Datex-Ohmeda Sevotec 5 for sevoflurane, the Penlon Sigma Delta
and Datex-Ohmeda Isotec 5 for isoflurane, and the Tec 6 for desflurane. So desflurane's figure
says how far a Tec 6 dial turns. Another desflurane vaporizer, or an injector that delivers into
the circle, is not bound by it.

**These vaporizers work in two different ways.** The sevoflurane and isoflurane vaporizers are
variable-bypass vaporizers: the dial splits the fresh gas between a bypass and a chamber in which
the gas flows over the liquid agent and leaves saturated with vapour. The Tec 6 is not a
variable-bypass vaporizer. Dosch and Tharp call it a gas–vapour blender, which heats desflurane
and adds pure vapour to the fresh gas (§ "Known limitations" gives their full
citation). Johnston et al. 1994, the source of desflurane's maximum, describe it in their abstract
as "an electrically heated, pressurized, electromechanically coupled dual-circuit blender". The two
designs behave differently away from sea level (§ "Known limitations"). The model fixes
ambient pressure at one atmosphere, 760 mmHg (§ "Assumptions"), so it does not need to know which
design each maximum comes from.

The stored MAC (`mac_percent`) is a single adult MAC. Its source, De Wolf et al. 2012, gives no age
for it. The age-referenced values are Mapleson's MACs at age 40, which the table below compares
with the stored ones. The stored MAC has two uses, and both are
presentation. First, it sets the dial's starting position, so that each new run begins at a
recognizable clinical anchor. Second, it is the divisor for the display in MAC multiples: every
displayed compartment value and the chart's second axis are divided by it. The simulator refuses
any agent whose own vaporizer cannot deliver its 1 MAC, because every run starts the dial
at 1 MAC.

No governing equation reads the stored MAC (`mac_percent`). The simulation code (`core/`) reads
it in two places: to refuse an agent whose MAC is above its vaporizer maximum, and to set the
dial's opening position. Specifically, the model does **not**:

- compute MAC-hours or an age-adjusted MAC, or sum MAC fractions across agents;
- model an effect-site compartment or any depth-of-anesthesia endpoint; or
- imply that an alveolar concentration equal to the stored MAC corresponds to any particular
  clinical state in a particular patient.

Presenting a single-agent alveolar concentration as if it indicated anesthetic depth would be
exactly the plausible but wrong clinical inference that the project's safety standard forbids. So
the display shows a *ratio to* 1 MAC, written `×MAC`, and never a depth
(`docs/INTERFACE.md` § "MAC multiples as a display unit").

**The stored MAC carries clinical weight.** An error in it would shift every value shown in MAC
multiples, not only a run's starting point.

The stored MACs are single adult values with no adjustment for age, which De Wolf et al. state
they used in their Gas Man simulations. § "Source hierarchy" grades them **tier 3**. They were
adopted for two reasons: they belong to the same parameter set as every partition coefficient in
this model, and the reference adult has no age to which an age-related MAC could be applied.

**The stored MACs differ from Mapleson's, and the difference distorts a comparison of sevoflurane
with desflurane.** Mapleson's meta-analysis of the published MAC literature gives values for
age 40, with 95% confidence limits of about ±7% (±10% for desflurane). The table compares the
stored values with them.

| Agent | Stored MAC | Mapleson age-40 | Displayed MAC multiples read |
| --- | --- | --- | --- |
| Sevoflurane | 2.0% | 1.80% | 10% low |
| Isoflurane | 1.2% | 1.17% | 2.5% low |
| Desflurane | 6.0% | 6.6% | 10% high |
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- provenance: data/agents/desflurane.json mac_percent = 6 -->

Because the errors run in opposite directions for sevoflurane and desflurane, a comparison of the
two in MAC multiples differs by about 22% between the stored MACs and Mapleson's. Comparing
agents is what the MAC-multiple display exists for. The 22% is larger than the confidence limits
of Mapleson's values. It is a limitation of the display, listed in § "Known limitations".

**The stored MACs are kept** (project owner, 2026-09-04, ratified, over adopting Mapleson's
age-40 values). Mapleson's values are not adopted, for three reasons:

1. Mapleson 1996 is a meta-analysis. It fits a regression to published studies and measures
   nothing, so § "Source hierarchy" grades it **tier 2**. A recorded decision may still
   adopt a lower-tier source, such as the stored values. Reasons 2 and 3 explain why the stored
   values were kept.
2. Every other parameter in this model comes from the Gas Man set. Dividing the model's Gas Man
   concentrations by a Mapleson MAC would make each displayed multiple a ratio between values
   from two different sources. Dividing by the model's own MAC is at least internally consistent.
3. With confidence limits of ±7-10%, no MAC source makes a comparison between agents exact. The
   display shows the MAC it divides by and states the limitation, instead of presenting another
   estimate as settled.

No planned milestone moves the MAC to a primary measurement. `ROADMAP.md`'s
planned-milestone item 30 moves it to Mapleson's age-40 values, and item 31
plans a primary-literature set of partition coefficients beside the stored one.

**For developers.** In the simulation code, the breathing circuit (`BreathingCircuit`) carries
the maximum delivered concentration for the agent in use. The circuit itself **must reject** any
delivered concentration above that maximum, at construction and at every later change, and must
not lower it to the maximum instead. The function that sets up the uptake simulation for an agent
(`AgentUptakeSystem.for_agent()`) gives the circuit that maximum and sets the dial's starting
position from the stored MAC. So the simulation code, not the controller, makes the starting
position agent-specific.

Every agent file **must** declare a MAC (`mac_percent`) that its own vaporizer can deliver. A
cross-field check in `core/parameters.py` rejects an agent file that does not
(`_AgentPayload._mac_percent_must_not_exceed_vaporizer_max()`). This MAC check runs after every
field is populated, so the order in which the fields are declared cannot defeat it.

Because the stored MAC divides every displayed compartment value, a change to it falls under the
safety-critical standard in `CLAUDE.md`. The list of sources in each agent's file (`sources`)
records the citation, the tier, the Mapleson value that was not adopted, and how far the stored
value differs from it.

The maximum is stored with the agent for two reasons:

- The reference breathing system in `data/machines/reference_circle_system.json` is not a
  machine and names no vaporizer, so a per-machine entry would only repeat the agent file's
  number.
- The MAC check needs the maximum and the MAC in the same file.

When a machine profile mounts a vaporizer whose maximum differs from the agent file's, the
maximum moves to the profile's per-agent limit, which `docs/machine-abstraction.md` names
`agent_limits`. Two things move with it:

- The MAC check moves to wherever the machine and the agent are paired. Otherwise a machine
  whose limit is below an agent's MAC would reject the run at construction.
- The code in `AgentUptakeSystem.for_agent()` that reads the maximum moves.

The controller reads the maximum from the circuit, and the interface draws its dial from that
value, so the dial follows the move.

Until a profile mounts such a vaporizer, the circuit and the dial read the same number from the
same file.

## Known limitations

This model does not represent:

- a separate arterial blood-mixing compartment. Arterial blood carries the
  alveolar partial pressure at every instant (see § "Model boundary"), because
  the lung's exchange with blood is perfusion-limited and the model omits shunt
  and ventilation-perfusion mismatch (both below);
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
  from the means of the one laboratory they come from
  (*Anesth Analg* 1989;69:370–373). Other laboratories
  report values for the same tissue that differ by up to 150% (below, with the
  tissues each difference applies to). Within the one laboratory, one SD of
  the muscle coefficient moves a displayed reading by up to 0.90 percentage
  points in the first hour at 1 MAC, so a reading can differ between patients
  by many times its last digit (`docs/INTERFACE.md` § "Why the readouts show
  two decimals");
- metabolism;
- compound A or other degradation products;
- renal or hepatic dysfunction;
- cardiopulmonary bypass;
- ECMO;
- hypothermia;
- alveolar humidification. Real alveolar gas is saturated with water vapour, and the modeled alveolus holds none, so no inspired fraction is
  diluted when it reaches the alveolus (sized below, with what correcting it
  would cost);
- the difference between ambient and body conditions. Every gas volume is
  carried at the single reference condition that "Agent amount" fixes, and no
  ambient-to-body correction is applied anywhere (sized below);
- altitude, or any ambient pressure other than the one atmosphere fixed under
  § "Assumptions" (what that excludes is below);
- age-dependent MAC;
- individual variation in awakening concentration. The chart's MAC-awake band
  is a population value at one standard deviation, never a threshold for the
  simulated patient (see `docs/INTERFACE.md` § "MAC-awake as a chart reference");
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
isoflurane's. These figures have no test yet (`PL-LP96`).

The store takes up agent in the first minutes of wash-in, but it equilibrates
fully within about thirty minutes. So it barely changes $`F_A/F_I`$ at 30
minutes, the value compared with the published wash-in data. It acts mainly
early in an elimination, and only a run with the rebreathing circuit removed
showed it. "Desflurane's residual, and why the parameter file was not changed"
weighs these figures against the other explanations of desflurane's
five-minute washout disagreement, described below. The thirty minutes has no
test yet (`PL-LP96`).

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

The ranking held at every equilibration time from 7.5 min to 9 weeks
(*Anesth Analg* 1989;69:218–225). So
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
published standard deviations too *fast*. No setting of the simulator removes
the circuit. Yasuda's volunteers breathed through a non-rebreathing circuit,
so a washout on screen cannot be compared with theirs directly. On screen, the
circle system returns exhaled desflurane to the patient, and that slows the
washout by an amount that depends on the fresh gas flow and the ventilation.
The figures below follow a 30-minute administration with every setting left
unchanged, and they are the model's own output. At the default alveolar
ventilation of 4 L/min and cardiac output of 5 L/min, desflurane's five-minute
ratio is 0.285 at the default fresh gas flow of 4 L/min and 0.163 at 10 L/min,
against 0.0935 with the circuit removed. At a high fresh gas flow with a raised
ventilation, the ratio on screen can fall below the volunteers' mean of 0.14.
It is 0.105 at 10 L/min of fresh gas and 8 L/min of alveolar ventilation. The
model's error was measured only at the settings of the published protocol. If
the error is present at other settings too, and the published measurement is
right, a real patient breathing through the same circuit at the same settings
would wash desflurane out more slowly than the screen shows. A learner should
not take early desflurane washout on screen as a prediction of how fast a
patient recovers.
"Desflurane's residual, and why the parameter file was not changed"
gives what was ruled out. The one hypothesis left is the published value itself, which this project cannot test,
so the disagreement is left uncorrected.

<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json default_cardiac_output_l_min = 5, default_alveolar_ventilation_l_min = 4 -->
<!-- not-restated: 10 L/min -->

**For developers.** `test_desflurane_washout_at_the_default_fresh_gas_flow_regression_pin`
in `tests/reference/test_published_wash_in_and_elimination.py` pins the figure
at the default fresh gas flow, reading that flow from the circuit's parameter
file. `test_desflurane_washout_at_a_high_flow_and_raised_ventilation_regression_pin`
pins the figure at 10 L/min of fresh gas and 8 L/min of alveolar ventilation.
`test_five_minute_elimination_ratio_regression_pin` pins the figure at
10 L/min, and
`test_five_minute_elimination_ratio_without_rebreathing_regression_pin` the
figure with the circuit removed.

<!-- not-restated: 10 L/min -->

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
display.** Each agent's stored MAC is tier 3 under § "Source hierarchy".
§ "Delivery-limit and MAC parameters" gives its gap from Mapleson's age-40
meta-analytic values, and how much the choice of MAC source alone shifts a
sevoflurane-versus-desflurane comparison in MAC multiples. The shift is consistent within an agent and changes no curve's shape or
timing. It rescales one agent's MAC axis against another's. The
sevoflurane-versus-desflurane shift is larger than the confidence limits of
Mapleson's values, so by Mapleson's meta-analysis two agents at one MAC each
are not equipotent to that precision. The interface displays
the divisor for this reason. `ROADMAP.md`'s planned-milestone item 30
moves the MAC to Mapleson's age-40 values, and item 31 plans a
primary-literature set of partition coefficients beside the stored one.

**Two omissions limit the supported run length, and a third limits the late
washout within it.** The first two are metabolism, in the list above, and the
fat group's flow, in the note below. Both are negligible over a case and not
over days, so a run is supported to 24 hours, and the simulator will not step
past that limit. A longer run would increasingly display what this model
leaves out. `docs/INTERFACE.md` § "Supported run length" argues for the number and gives the measured
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
and nor does the gap between the modelled tail and the published curves. `docs/INTERFACE.md` § "Supported run length" gives the reason that
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
constant (*Anesth Analg* 1991;72:319). For sevoflurane and isoflurane they found
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
below the truth. `test_the_fitted_fat_time_constants_imply_the_flows_printed`
repeats this arithmetic.
<!-- derived: 2.07 from data/patients/reference_adult.json tissue_groups.fat.perfusion_fraction = 0.06, default_cardiac_output_l_min = 5.0, tissue_groups.fat.volume_l = 14.5 -->
<!-- derived: 52 for sevoflurane from data/agents/sevoflurane.json tissue_gas_partition_coefficients.fat = 34.0, blood_gas_partition_coefficient = 0.65 -->
<!-- derived: 54 for isoflurane from data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70.0, blood_gas_partition_coefficient = 1.3 -->
<!-- derived: 31 for desflurane from data/agents/desflurane.json tissue_gas_partition_coefficients.fat = 13.0, blood_gas_partition_coefficient = 0.42 -->

Neither settles it, for different reasons. The PET figure is one depot in one
small cohort, awake and at rest, set against a whole-body lumped compartment,
and the depots within such a compartment really do differ (Frayn and Karpe).
The fitted compartment is fat only by the authors' assignment (see the
cautions below). Its volume is between a quarter and two fifths of the fat this model
stores, and the analysis "only accounts for about 25 L of the body volume"
(*Anesth Analg* 1991;72:323). The same paper's flow estimates ran too small for the
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
compartment's scale
(`test_the_muscle_group_equilibrates_in_the_minutes_printed`). Leaving that
compartment out biases three things. Each
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
  arterial, against the trace's 2.3 to 3.9%, figures that have no test yet
  (`PL-LP96`). It still stays below the lean
  tissue feeding it, because agent moves down that gradient into the fat.
- **The late washout loses its largest measured term.** On the coefficients of
  the published mean washout curves (Tables 1 and 2 of each paper), after a
  30-minute administration the fourth compartment's term becomes the largest
  in the measured washout at 1.8 to 3.1 hours. It stays the largest until 20.7
  hours for desflurane, and until 27.5 to 29.4 hours for the other three cohorts, past the end of
  the 24 hours that a run is supported for (`docs/INTERFACE.md` § "Supported run length").
  `test_the_fourth_compartment_is_the_largest_term_over_the_recorded_hours`
  re-derives those hours from the coefficients. Without that store the
  modelled tail should fall faster, and it does. Against the mean curves themselves (`docs/VERIFICATION.md` § "The first 24 hours of
  elimination against the published mean curves"), the shipped tail runs below
  them from about the seventh hour until about the twenty-first, and a third
  below at the widest, near hour 13. For desflurane it is below from 3.4 to
  15.3 hours, by about half at the widest point, near 8 hours. The shipped tail
  is above the curves before and after that span. With the rebreathing circuit
  taken away, the model's tissue return alone falls, after the first hour, as low as a third to a half of the mean
  curve, near hour 8 for desflurane and near hour 13 for the others. With the circuit in place, as shipped, the gap
  starts later than the third hour, because the rebreathing circuit and the
  muscle group's slow return hold the tail above the curve until the seventh
  hour. The size is known to about a factor of two, which is the fourth
  compartment's own between-subject spread.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**Eger and Saidman's review draws the same compartment, and names a fourth
bias.** Their Table 3 (*Anesth Analg* 2005;100:1024) gives intertissue diffusion a group of its
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
*Br J Anaesth* 1976;48:289). Eger and Saidman cite that as the direct demonstration (their ref 8),
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
  private reference corpus. The Workbook is tier 3 and the chapter is tier 2, and
  `docs/references/README.md` carries their entries.

**The tissue:gas coefficients rest on one laboratory's means, and other
laboratories disagree with them by up to 150% in some tissues.** The stored
values are Gas Man's. They differ from Yasuda, Targ and Eger's means in seven
of the nine cells, by up to 9% in isoflurane's fat coefficient, 70.0 against
64.2 (§ "Parameter provenance" has the table;
`test_the_stored_set_differs_from_yasudas_means_by_the_percents_printed`). Hendrickx and De Wolf state the
general case: "Tissue solubilities vary up to 150% between authors (Yasuda et
al. 1989), and the tissue homogenates used to determine these coefficients may
not represent in vivo conditions" (p. 165). The 150% is not spread evenly
across the tissues this model uses. Yasuda, Targ and Eger, whose measurements
the stored values rest on, compare their values with two other laboratories
(*Anesth Analg* 1989;69:373). Fiserova-Bergerova et al.'s values for sevoflurane, isoflurane and
halothane were similar to theirs for brain and for fat, except halothane's fat
coefficient, which was 65% greater. They were 115% to 150% greater for kidney
and 10% to 30% less for muscle. Those values are Fiserova-Bergerova, Tichy and
Di Carlo 1984, Yasuda's ref 8. Lowe's isoflurane values were 50% to 75%
greater. The authors could not explain the differences.
<!-- provenance: data/agents/isoflurane.json tissue_gas_partition_coefficients.fat = 70 -->

A third published set agrees less well. Baker and Farmery's 2011 review
prints tissue:blood coefficients from Fiserova-Bergerova and Diaz 1986 beside
the set that matches this model (*Compr Physiol* 2011;1:572, Table 2). On the tissue:blood scale,
that set puts sevoflurane's fat coefficient at 71.7, 37% above this model's
52.3, and isoflurane's muscle coefficient at 1.71, 51% below this model's
3.46. Its vessel-rich figures are 28% above this model's for both agents. The
set's own blood:gas values, 0.6 for sevoflurane and 1.4 for isoflurane, move
these gaps in opposite directions for the two agents, so the tissue:gas scale
that this model stores gives the fairer comparison. On that scale the set's
sevoflurane fat coefficient is 27% above this model's and its isoflurane
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
against 17% to 19% for fat
(`test_yasudas_fat_spreads_are_the_percents_printed`). Eger and Saidman's Table 1 makes the same point
from the literature as a whole. Their best figure for sevoflurane muscle is
1.7, with 1.1 to 2.4 as the range across the studies they cite (*Anesth Analg* 2005;100:1022),
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
3721592), and the 1984 paper not at all. The full Yasuda, Targ and Eger
citation is in `docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not
changed".

**Cardiac output does not scale with the patient, and the reference weight is
a label, not an input.** The default cardiac output is a stored 5.0 L/min. No
equation reads the patient's weight, so editing the weight changes nothing
this model computes. Two published figures sit either side of the stored
value, **and they are not evidence of the same kind.** The first is Lowe and
Ernst's cardiac-output relation, the upstream source that the Gas Man Workbook
names, read at the source. It gives $`0.2M^{3/4}`$ for a body mass $`M`$ in
kg, which is 4.84 L/min at 70 kg. It is **derived, not measured**
(§ "Parameter provenance" gives the derivation). The second is Cattermole et
al.'s **measured** median of 5.51 L/min, from 686 subjects in the 50–75 kg
band that this patient sits in (*Physiol Rep* 2017;5(6):e13195).
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
3.30% and changed nothing else.

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
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**The size is 5.8 %, and it applies to the stores, not to conservation.**
Every term is exact in the model's own arithmetic, and the mass balance closes
to a relative residual below $`10^{-10}`$ (`docs/VERIFICATION.md` § "Mass-balance identity"), whatever
condition the unit names. So no agent goes missing, and the question is what the litres
*mean*. Read as amounts of substance, the alveolar, venous and tissue stores
hold 5.5 % fewer moles than their 20 °C label implies, so the label overstates
them by 5.8 %. The ratio behind both figures is 25.450/24.055, the molar
volumes in litres at 37 °C and at 20 °C. The fresh-gas terms are unaffected.
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**It does not touch a concentration, and it does touch every amount held in
the body.** A partial-pressure fraction has no unit and carries no condition.
So $`F_A`$, $`F_A/F_I`$, the MAC multiple and every trace on the chart are
untouched by it. Every agent amount on screen names the condition it is stated
at, 20 °C and 1 atm: the accounting panel's unit caption, the compartment
schematic's caption and the agent cost View's captions. The accounting panel and
the schematic also say that the amounts held in the body are body-temperature
gas under that label, so they read high. The size, 5.8 %, is stated here and
not on screen. The circuit's amount and the delivered and exhausted totals are
exact. The conversion to liquid converts a delivered or exhausted amount
exactly and a stored amount 5.8 % high. The agent cost View converts only the
delivered amount, which is the figure that means cost, so its liquid figure is
exact. A stored total in millilitres of liquid is refused for this reason
(`docs/INTERFACE.md` § "Agent amounts in millilitres, and the cost"). Removing this limitation would need a gas-phase model that carries
explicit conditions per compartment, which is well outside the current
milestone.
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**For developers.** `test_the_reference_condition_gap_is_the_ratio_of_molar_volumes`
computes the molar volumes at 37 °C and 20 °C from the constants in
`core/liquid_agent.py`, and the 5.8 % and 5.5 % from their ratio.
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

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
<!-- provenance: core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20 -->

**For developers.** `test_the_humidification_dilution_follows_from_the_water_vapour_pressure`
computes the 713 mmHg, the 6.2 % and the 6.6 % from 47 mmHg and one
atmosphere.

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

These figures were computed on 2026-09-19, at the parameters stored then,
against the published means and standard deviations. The table's factor is
712.88/760, from the computed 47.12 mmHg.

**Humidification is real, and the factor fails because it would count it
twice.** In those studies, $`F_A/F_I`$ is a ratio of two analyser readings
taken from real airways. So whatever humidification does to alveolar agent is
already inside the measured 0.850, and a model that reproduces that number has
already absorbed it. The stored coefficients raise the same problem. The
tissue:gas ratios were equilibrated at 37 °C (*Anesth Analg*
1989;69:370–373). The blood:gas ratios are Gas Man's set as De Wolf et al.
print it (*BMC Anesthesiol* 2012;12:22), and no measurement behind them has
been adopted. How much water the gas phase held in either set's
determinations is recorded nowhere that this project has read. Applied to $`F_I`$ alone, against coefficients whose own gas-phase
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
and nothing else in the simulator says so. The two pressures have no test yet
(`PL-LP96`). The delivered-concentration control
is a vaporizer dial, and this project's three agents are drawn from two
classes of vaporizer that respond differently to falling ambient pressure.
<!-- not-restated: 6 % -->

**The real devices for sevoflurane and isoflurane are variable-bypass
vaporizers.** This class includes the Dräger Vapor 2000, Sevotec 5, Isotec 5
and Penlon Sigma Delta. Fresh gas is split between a bypass channel and a
vaporizing chamber. The gas leaving the chamber is saturated at the agent's
saturated vapour pressure, which temperature sets and ambient pressure does
not. The dial sets the splitting ratio. So as ambient pressure falls, the
output rises in volumes percent while the delivered *partial pressure* is
approximately preserved. Boumphrey
and Marshall (*Contin Educ Anaesth Crit Care Pain* 2011;11:199–203) give the
approximation as
$`\%_1 = \%_\mathrm{cal} \times P_\mathrm{cal} / P_1`$. Their worked example
is isoflurane dialled to 2% at 101.3 kPa, which delivers 4.05% at 50 kPa.
That is 2.026 kPa of isoflurane either way.
<!-- not-restated: 2 % -->

**The real devices for desflurane are gas–vapour blenders.** This class
includes the Tec 6 and Tec 6 Plus. Desflurane needs it because it boils at
22.8 °C. The sump is kept at about 39 °C, which fixes desflurane's vapour
pressure at about 1460 mmHg, a pressure chosen to clear the vaporizer's own
internal resistances (*Br J Anaesth* 1994;72:474–479). Pure vapour is injected into the fresh gas stream. A
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
reach it rises while the partial pressure does not. James and White (*Anesth Analg* 1984;63:1097–1105) proposed
MAPP, minimum alveolar *partial pressure*, in place of MAC on exactly this
ground. So the unit described under `docs/INTERFACE.md` § "MAC multiples as a display unit" is a
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
$`1/P`$ form predicts a flat line
(`test_the_variable_bypass_overshoot_at_altitude_follows_from_the_fuller_form`).
The Tec 6's response rests on its manufacturer's instruction and on Andrews and
Johnston's description of its mechanism, both quoted above. How large the
variable-bypass response is, and whether its dial needs correcting, is less
settled. Dosch and Tharp call the effect of altitude on vaporizer performance
"controversial". They write that "Some sources state that variable bypass types
need not be adjusted for moderate changes in barometric pressure, but the Tec 6
must be dialed up beyond the desired dose at higher altitudes. Other sources
disagree." They also report that Dorsch and Dorsch's *Understanding Anesthesia
Equipment* (5th edition, 2008) says to consult the operator's manual for each
model. That textbook could not be read for this document, so its advice is
cited only as Dosch and Tharp report it. The size of the
variable-bypass compensation is approximate, so no number is stored for it. An implementation of ambient pressure should
derive the variable-bypass case from each agent's saturated vapour pressure
rather than from the $`1/P`$ shortcut, and would owe each agent's SVP a source
of its own. None is stored today.
<!-- not-restated: 20 °C -->

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
  statement, quoted above. It also gives a 1–18% concentration range, whose upper
  end is the 18% that this model stores as desflurane's maximum delivered
  concentration. Read in full.
  **Owner-attested**: see the note below.
- Boumphrey S, Marshall N. Understanding vaporizers. *Contin Educ Anaesth
  Crit Care Pain* 2011;11:199–203. **Tier 2** under § "Source hierarchy". It
  is a secondary synthesis, taken here for the shape of the explanation and
  the worked example, and never as the authority for a number. Its "Altitude"
  section describes both classes side by side. Read in full.
  **Owner-attested**: see the note below.
- Dosch MP, Tharp D. *The Anesthesia Gas Machine*, chapter 5, "Processing:
  Vaporizers". University of Detroit Mercy, revised February 2026.
  https://healthprofessions.udmercy.edu/academics/na/agm/05. **Tier 2** under
  § "Source hierarchy": a teaching text that draws on other sources. It is the
  source of the two class names and of how each class works, as
  § "Delivery-limit and MAC parameters" states them, and of the disagreement
  about altitude quoted above. It is never the authority for a number. Read in
  full at that address.

<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

**Two of those six are owner-attested: they were read from the project
owner's copies, and no other reader can check them.** They are the
Datex-Ohmeda specification sheet and the Boumphrey and Marshall article. Any
reader can reach the three journal articles above through their DOI or PMID,
and Dosch and Tharp's chapter at its address.
`docs/references/` cannot hold copies of these two, because the repository is
public (`docs/references/README.md` § "Redistribution"). So three things rest
on that reading alone: the passage quoted from Datex-Ohmeda, the 1–18% range
beside it, and the worked example attributed to Boumphrey and Marshall.
Nothing stored depends on any of them. A reader who wants to verify one has to
reach the document itself.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->

**Gas Man's own agreement with patients depends on the phase of the case, and
wash-in is its worst phase.** This model's parameter set and its compartment
structure both descend from Gas Man, which § "Source hierarchy" ranks tier 3.
Its value there is that it fixes the behaviour of a widely used teaching tool
for this implementation to be compared against. A prospective in-patient study
(*J Clin Monit Comput* 2022;36:1881–1890) measured how closely that behaviour tracks real end-expired sevoflurane.
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

The brackets are the published interquartile ranges
(*J Clin Monit Comput* 2022;36:1881), and they carry more of
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
been compared against a Gas Man trajectory. The comparisons under `docs/VERIFICATION.md` § "Required
tests" are against published human data, and no figure in the table above is
a tolerance that anything here must meet. Caveat 2 under `docs/VERIFICATION.md` § "Published wash-in
and elimination validation test" says that passing shows this implementation
reproducing its parameter set's *intent*, not that the set is independently
right. The study measures what that intent is worth in patients, and it is
worth least in the phase that the simulator displays most: the first minutes
of the $`F_A/F_I`$ rise, which is the canonical teaching curve of
inhaled-anesthetic uptake (see § "Model boundary"). So "agrees with Gas Man"
may not be read as "agrees with a patient" anywhere in a case, and least of
all in the first fifteen minutes. `docs/VERIFICATION.md` § "The early wash-in curve against the
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
checks in `tests/reference/test_sevo_patient.py` assert that a higher cardiac
output slows the rise of $`F_A`$. The MAC-multiple display divides by each
agent's tier-3 `mac_percent`, and the Datex-Ohmeda 1–18% range is desflurane's
`max_delivered_concentration_percent`. `reference_adult.json` carries both
fat-flow comparisons. Its Heinonen et al. note gives both figures and the
volume-to-mass conversion between them, and says
that fat depots differ. The default cardiac output is
`default_cardiac_output_l_min`, and no equation reads `weight_kg`. The
reference-condition gap leaves the relative residual, which the mass-balance
tolerance bounds, untouched.
`core/liquid_agent.py` is where an amount leaves the unit. It converts a
delivered or exhausted amount exactly and reads a store 5.8 % high
(`test_the_reference_condition_gap_is_the_ratio_of_molar_volumes`), and its
docstring says so. The humidification table was computed with
`_wash_in_ratio` in `tests/reference/test_published_wash_in_and_elimination.py`,
against the published means and standard deviations that the module itself
holds.
<!-- provenance: data/agents/desflurane.json max_delivered_concentration_percent = 18 -->


## How this document is held to the tree

§ "What a named test, a missing test and a date tell the reader" gives the rules
that a reader of this document relies on. This section gives the rest, for the
people who write it.

For a figure that the model computes or the simulator displays, such as the time
at which a compartment first shows a nonzero reading, the sentence that gives
the figure names the test that computes it, or uses the fixed form. Where that
test also reads the figure from this document and compares it with the model's
output, the document cannot drift from the model without the test failing.

In some parts of this document, an automatic check makes sure that each claim
names in fixed-width type what it describes. It checks every row of the hazard
table and every subsection of the required tests, and every output in the
displayed-outputs list of `docs/INTERFACE.md`. It does not yet check the entries of the required invariants.

In the sections that the check reads paragraph by paragraph, every number with a
unit has something behind it. Its paragraph gives a test, the fixed form, a date
or a published source, or links the number to the simulator's data.

Outside these lists and sections, only the documentation review before a work
item closes finds a number with nothing behind it, or a claim that does not name
what it describes. The review does the same for a qualitative claim, such as
which value a readout shows beside a halt, because the check cannot read one.

A count in this document is dated, checked against what it counts, or copied
from a tool that prints it. For example, a check compares the count in a heading
with the entries under it. Nothing checks a copied count later, so it can go out
of date.

**For developers.** These rules apply in part to the project's other
documents. The frozen lists in `ROADMAP.md` and the package map in
`docs/ARCHITECTURE.md` promise an entry for each member of a set, and each has
checks of its own. The check of a frozen list reads only the lines that open
with an item id. The prose of `ROADMAP.md` is treated as dated. Every thread in
`docs/WORKING_NOTES.md` is dated, so only the rule for dated statements applies
to it. The rules do not apply to prose about the project's workflow tooling, in
`.claude/`, `CONTRIBUTING.md` and `docs/resident-instructions.md`, where the
rule on counts is only advice.

The rule that a claim names what it describes also applies to two documents that
describe the code: to every paragraph of `docs/ARCHITECTURE.md`, and to every
paragraph of `docs/interface-provenance.md` § "What this project adopts, diverges
from, and refuses". Each such paragraph names in fixed-width type the module,
symbol or test it describes, or uses the fixed form ``no code yet (`PL-XXXX`)``.
An item id alone names no code. The documentation check reads both paragraph by
paragraph (`check_bound_families`). When something that a paragraph names
changes, the command for the documentation review
(`tools/doc_check.py candidates`) prints the paragraph's first and last line
(`PL-BLN0`).

A statement is about the code or its data when it says, for example, that a test
enforces a rule, that a field exists, that a value is *N*, or that a job runs
something. It names that thing as a test, path, symbol or field in fixed-width
type, or with a `<!-- provenance: -->` marker over a restated number. In the
documentation check (`tools/doc_check.py`), `check_named_tests` looks up a
test, `check_citations` a path, `check_prose_provenance` a marker and
`check_make_targets` a `make` command. No check looks up a symbol or a field. The strongest link for a figure from the model is a test
that reads it from this document, as
`tests/reference/test_known_limitations_figures.py` does.

A writer may phrase the words before ``no test yet (`PL-XXXX`)`` freely, but the
form itself is fixed, so that the documentation check can tell a forgotten link
from a declared absence. Closing the named item without adding the link makes
the check fail.

The lists whose headings promise an entry for each member of a set are the
invariants list, the required-tests subsections, the displayed-outputs list, the
hazard table, a frozen gate list and a marked enumeration. The function that
checks them (`check_bound_families`) reads only the lists and sections named in
its table, each section paragraph by paragraph. A list or a section joins that
table only when the change that makes it conform is merged, so that work not
yet done never makes `make check` fail.

In those sections, a published source counts only when it is cited by a DOI, a
PubMed id, an ISBN or a journal locator such as "Anesth Analg 1991;72:316-324".
An author and a year alone, such as "Mapleson 1963", do not count, because no
pattern can tell them from a phrase such as "Until 2026".

A paragraph's test or fixed form may sit in the note for developers below it.
That note covers the paragraphs directly above it, back to the previous heading
or note, and stops at the first paragraph that has a test, the fixed form, a date or a
source of its own. A date or a
source in the note covers only the note.

A paragraph with no test, fixed form, date or source passes only if a marker
covers each number that it states with a unit. A `provenance:` marker covers a
value the paragraph states, in that value's unit. A `derived:` marker covers a
figure that the paragraph works out, in the unit it writes, and each input the
paragraph states. A `not-restated:` marker covers nothing, because it says that
the paragraph's numbers are not stored values. So a computed figure cannot pass
on a marker written for a figure beside it.

Outside the lists and sections where the check looks for a missing name, a
command for the documentation review (`tools/doc_check.py candidates`) prints
each line that names a file, a definition or a data key that a change touched.
Only the reviewer finds a number or a claim on a line that names none of these.

Besides a count in a heading, a check compares a count with what it counts only
through a marker over a data value. Any other count is dated, copied from a
tool, or left out. This document never states the number of entries in the
hazard table or in any other list named in this section. The function that
checks gate counts (`check_gate_counts`) applies the rule on counts in code. It
checks each count that a frozen list states about itself against the list: in a
group heading, in a release table, and in the sentence that says how many
entries are marked `not-delegable`. It refuses a count written into a lower
heading, which it cannot check. It leaves other counts in prose alone, because a
sentence such as "frozen at seventeen entries" records a dated fact that must
never change.

This section's rules follow requirements traceability, the established practice
for software of this application's safety class (§ "Software safety
classification: Class C, for the whole application"). Traceability links each
requirement to the tests and risk controls that cover it. IEC 62304 § 5.1.1
requires the software development plan to carry traceability between system
requirements, software requirements, software system tests and risk control
measures. The FDA's *General Principles of Software Validation* (2002) § 5.2.2
names traceability analysis among the validation tasks. Gotel and Finkelstein
set out the problem in *An analysis of the requirements traceability problem*,
ICRE 1994, pp. 94–101.

### The provenance table, and the markers over restated values

`tools/doc_check.py` (run by `make check` and CI) checks the provenance table
in § "Source hierarchy: what may be cited as the authority for a value" against
the data files in both directions. Every row must name a key that the file
contains and state the value stored there, and every numeric parameter in every
data file must have exactly one row. The function that does this,
`check_provenance`, confirms that a documented key exists and holds the stated
value, never that the value is right or which tier its source has.

Both directions start from a data file, so that check cannot see a constant
that never entered one, such as a field default on a `core/` dataclass.
`test_every_constant_a_core_dataclass_defaults_to_is_a_value_the_provenance_table_selects`
looks for such a constant. It reads every numeric field default on a `core/`
dataclass through `dataclasses.fields()`, including one written as a named
constant, and requires each to appear in the provenance table's Selected-value column.
It skips zero and a field's full scale (1, or 100 for a percent), which carry
no scientific content. It matches values, not names, so it can miss a
constant: a new one equal to a value the table already selects passes, and 6.0
is selected for both the circuit and the vessel-rich tissue.

The provenance table is not the only place these values appear. Some prose restates one:
the reference adult's alveolar volume and ventilation, and each agent's
blood:gas coefficient, vaporizer maximum and MAC. Each such sentence carries a
hidden marker, an HTML comment that names the file and key it restates:

```text
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
```

`doc_check.py` checks both sides of that link: the key against the data file,
and the stated value against the paragraph the marker sits under. So neither
the file nor the sentence can change without the other. Without the markers,
editing a data file would force an update to the provenance table but leave the prose
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

A marker can also name a constant in code, such as the simulation step. It is
written as the module's path under the package, followed by the constant's
name:

```text
<!-- provenance: core/simulation_step.py SIMULATION_STEP_S = 1 -->
```

**A figure that equals a stored value must carry a marker.**
`doc_check.py` finds each figure in this document, in `docs/INTERFACE.md` and in
`README.md` that equals a stored value, in that value's unit. The stored values are every
number in a parameter data file, and every public constant in the package
whose name ends in a unit, such as `_S` or `_L_MIN`. A figure that restates
its value carries a `provenance:` or `derived:` marker. A figure that only
coincides with one carries a `not-restated:` marker that lists it:

```text
<!-- not-restated: 2 %, 0.05 -->
```

The check never decides which kind a figure is. `2.5` appears in this document
as an alveolar volume in litres, a flow in litres per minute and a distance in
standard deviations, and `2%` is sevoflurane's MAC in one sentence and a dial setting in
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

### What the data-file format requires of a `sources` entry

**The second and third of the rules for a `sources` entry in
§ "Source hierarchy: what may be cited as the authority for a value"
are part of the data-file format, and `make check` enforces them.** Each
family of data file (agent, patient and
machine) has its own `schema_version`, checked against that family's
supported versions in `src/anesthesia_sim/core/parameters.py`, so a format
change affects only its own family. Version 2 gave every `sources` entry two
required fields and allowed one optional top-level string. Version 3 added a
third required field to each entry. Version 4, for agent files alone, added
`molar_mass_g_mol` and `liquid_density` (§ "Agent amount"). Agent files must
be version 4, and patient and machine files version 3. The fields are:

- `tier`, on each `sources` entry: `primary`, `secondary` or
  `reference-implementation`. It says which of the three tiers in § "Source
  hierarchy" the *document* belongs to.
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
that read the tier alone would report all five of this project's parameter data files as
primary-sourced, although the reference patient adopts no primary source and
many of the table's rows are tier 3 (§ "Where this project stands" gives
the counts). That is the failure the second rule for a `sources` entry exists to prevent, so
the check reads the adoption and not the citation list. Today each agent file
declares four adopted primary sources: for the tissue:gas coefficients, the
vaporizer maximum, `mac_awake` and the liquid density. `src/anesthesia_sim/data/patients/reference_adult.json` declares
none and records the gap.

**What the check does not decide is whether a citation labelled `primary`
really is one.** That needs somebody who has read the paper. A tool that
guessed, from the author, the journal or a product name in the title, would
look authoritative and be wrong. The tool checks that a claim was made and is
well-formed, and a reviewer checks that the claim is true.
