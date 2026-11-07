# Volatile-agent patient uptake and distribution model

## Status

The simulator is an educational model (§ "Intended use").

This document specifies the scientific model that the simulator implements. Its
equations and compartment structure have not changed since v0.1.0, and every
supported agent shares them.

A statement here that gives a version has been true *since* that version. The
project's roadmap (`ROADMAP.md`) lists the current release in its version table.

Release v0.0.2 modelled the wash-in and washout of an ideal breathing circuit
with no patient. Its reference tests are in § "Preserved circuit reference tests". v0.1.0, the “Sevo works” milestone, was the first sevoflurane model with a patient. The agent follows this path:

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

When a statement in this document or in `README.md` is about the simulator's
code, data or output, it names the thing it describes. Where no test covers the
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
not a clinical prediction, dosing tool, patient monitor, or medical device. It is
intended for anesthesia clinicians, trainees, and students. It helps them
build intuition about how agent concentration moves between the breathing
circuit, alveolar gas, blood, and the tissue groups, under management that the
learner chooses. In particular, it makes visible the compartments that no
clinical monitor displays: vessel-rich, muscle, fat, and mixed venous.

**It is not intended for use with an identifiable patient's data.** It is meant
to be run on hypothetical or illustrative parameters. It is not intended for
entering, importing, or reproducing an identifiable patient's parameter values,
or for informing the management of a specific patient.

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
ISO 5360 agent colours. The extreme-preserving decimation is a safety feature of
the interface.

A split would pay off only where the exempted part is large, genuinely
non-clinical and costly to verify. None of those holds now.

### This is an engineering bar, not a regulatory status

The project adopts Class C for the whole application as an engineering standard,
like WCAG 2.2 AA for accessibility (§ "Color contrast, and the standard this
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
(§ "Reasonably foreseeable misuse, and the hazards the presentation carries")
has a row for it. Two safeguards protect against this misuse, and tests
enforce them (§ "What keeps a real patient's data out of a run").

**Sources for this section.** Because IEC 62304 and ISO 14971 are not open
access, the project read their clause structure, the three class definitions, and
Annex B.4.3's probability rule from secondary summaries. The Class C conclusion
does not depend on the standards' wording, but the clause numbers cited here do.
The project read the FDA material at the source.

**For developers.** Before you revise this section, check the standards directly.

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
the barrier limits the rate. Jones and Rowland-Yeo call the two tissue cases perfusion rate-limited and permeability rate-limited, and give the first as typical of small lipophilic molecules, which the
volatile agents are (Jones HM, Rowland-Yeo K. Basic concepts in physiologically
based pharmacokinetic modeling in drug discovery and development.
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
(§ "Desflurane's residual, and why the parameter file was not changed").
§ "Known limitations" lists this simplification.

This project's sevoflurane and patient parameters come from the Gas Man
simulator, whose structure matches this model's in two respects. In Gas Man,
each tissue group exchanges agent only with blood, at a perfusion-limited rate,
and arterial partial pressure is displayed without being tracked as a
compartment. Gas Man tracks four compartments: alveolar gas and the vessel-rich,
muscle, and fat groups. See:

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
(§ "F_A/F_I as a displayed ratio").

**For developers.** Before extending the model to a multi-limb system, record
the change in this document. Such a system separates inspired gas from mean
circuit gas, as Lerou and Booij's three-part model does. The two would then be
distinct states, and this model's single $`F_I`$ would no longer describe both.

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
  and the concentration and second-gas effects. "Alveolar gas" gives the size of
  the error and what lifting the assumption would take.
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
  condition that "Agent amount" states: 20 °C and 760 mmHg, dry. No equation
  converts between ambient and body conditions. § "Known limitations" gives the
  size of the resulting error.
- Inspired gas reaches the alveoli undiluted by water vapour, because the
  modeled alveoli hold no water. "Dry" in the reference condition above means
  this absence of water vapour. Real alveolar gas is saturated at body
  temperature. "Known limitations" gives the size of this omission, 47/760, and
  what correcting it would cost.
- Ambient pressure is constant at one atmosphere, 760 mmHg. Every concentration in this model is a fraction of that pressure, so the model applies only at sea level.

**At one atmosphere, a fraction and a partial pressure are interchangeable.**
They differ only by a factor of the ambient pressure, so with that pressure
fixed at 760 mmHg, $`F_A = 0.02`$ is 15.2 mmHg. The model relies on this in
three places. It stores every modeled concentration as a fraction with no
unit (see § "Concentrations"). The interface displays each concentration as a
percent of one atmosphere. And $`\mathrm{MAC}_\%`$ is one sea-level percent
divided by another.

**More than anything else in the model, the vaporizer control depends on the
ambient pressure being 760 mmHg.** At 760 mmHg, both classes of vaporizer deliver the
same partial pressure at a given dial position, so no equation, stored value
or displayed number here is wrong at sea level. Away from 760 mmHg, the two
classes diverge in opposite directions, as § "Known limitations" describes.

**For developers.** The vaporizer control is `ControlInput.DELIVERED` in
`app/control_record.py`. Each recorded change to it carries the unit *percent
of 1 atm*. The model has no parameter for the class of vaporizer and needs none
at sea level. A model that adds ambient pressure will need one.

## Conventions

### Time

Times are in seconds throughout this document, the model's code and a saved run.
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

Simulated time is the number of completed steps multiplied by the step size,
which a run keeps for its whole length. At the app's 0.1 s step, the product
and a running total of the step sizes agree within about 35 nanoseconds over
a four-hour run. That is far below anything displayed, so multiplying gains
no accuracy.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**For developers.** The advantage of multiplying is that the product is rounded
once and depends only on how far the run has gone. A running total also depends
on the order and number of the additions that produced it. Ten steps of 0.1 s
sum to 0.9999999999999999 and multiply to 1.0.
<!-- not-restated: 0.1 s -->

When a step differs in size from the run's earlier steps, it is rejected with
an error and not counted, because the count of steps gives the time only while
every step is the same size. Reset clears the count and the step size together,
so a fresh run may use a different step size.

#### The reproducibility guarantee

Two runs with the same inputs are **exactly identical** in every stored value at
any step *n*, which falls at *n* times the step size in both. Those inputs are
the starting state, parameters, step size, setting changes and order of events.
Every comparison of one run with another relies on the guarantee. That includes
comparing a branched run with the run it branched from, at every instant they
share. § "What a branch comparison asserts, and what it does not" says what such
a comparison may and may not claim.

**A slow or busy computer reaches each step later in real time, but computes and
stores the same values as a fast one.** The screen uses the computer's clock to
decide when to update. But the number of steps in each update is a setting the
user chooses, and is never measured from the clock. The simulation never takes
extra steps to catch up after a slow update, and it reads no clock.

**Playing a run faster does not make it a different run.** The playback rate is
how much simulated time passes per second of real time. A faster rate takes
more *whole steps* per screen update, never a larger step. So a case played at
real time and at three hundred times real time takes the same steps, in the
same order, at the same size, and gives exactly the same results sooner.

**An automatic check keeps the model's code from reading the clock.** It also
stops that code from drawing a random number that differs from run to run.

The guarantee does not cover four things, and none of them is a defect:

- **A different step size.** Between setting changes, runs at two step sizes
  differ only by computer rounding, because each step solves the equations
  exactly. A test bounds that difference. A setting change takes effect at the
  next step, and steps of different sizes end at different times. So the moment
  a change takes effect moves with the step size, and after any setting change
  the two runs differ by more than rounding.
- **A different model version.** The guarantee applies within one version of
  the equations and one parameter set. That is why both are versioned.
- **A different installation.** Basic arithmetic gives identical results on
  every computer. But each step also uses an exponential function, whose last
  digit can differ from one installation of the simulator to another.
- **Elapsed real time.** How long a computer takes to reach step *n* is a
  property of the computer. So is how many steps it has reached when a
  wall-clock minute is up. Neither is a property of the model.

**A state computed from a saved run has a guarantee of its own.** The guarantee
above holds because two runs with the same inputs take every step at the same
size, so only one sequence of calculations reaches step *n*. A saved run stores
no samples and no step size. Its states are computed on request, and more than
one sequence of calculations can reach the same instant. The guarantee for
these states comes from a rule for computing them
("The canonical evaluation rule" under § "Runtime controls"). That rule is
stronger in one way: two computations of one saved run at one instant give
exactly the same bits. It is narrower in another: only values computed by that
rule may be stored, exported or branched from.

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

Taking a step whose length differs from the run's earlier steps raises a
`SimulationConfigurationError`, because the model computes the elapsed time
(`elapsed_s`) as the step count times one step length.

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

**The vaporizer setting is stored as the percent dialled.** The vaporizer dial
is the only concentration that is set rather than computed. The circuit stores
that percent, as do the settings that a run records for each stretch and the
record of control changes. The flows are stored as set, too (§ "Time").
Converting a fraction back to a percent does not always return the setting, so
a value kept as a fraction could not give back what a learner dialled. A new run
starts the dial at the agent's published percent, without converting it. An
error message about a setting gives it in percent, beside the vaporizer maximum,
which is also stored in percent.

The conversion has only two uses. Where the equations need $`F_D`$, the model
derives it from the dial's percent, both in the circuit and in the recorded
settings. The screen converts for display.

A concentration fraction must always be finite and satisfy:

$$
0 \leq F \leq 1
$$

**The range is checked once, when a concentration is created.** A fraction must
be finite and lie from 0 to 1, and a percent must be finite and lie from 0 to 100. The model treats a fraction and a percent as
different kinds of number, and rejects one where the other is wanted. Every
place that stores a concentration accepts only a checked value.

Each fraction computed in a step is checked before a compartment stores it. A
value outside 0 through 1 halts the run and names the compartment, instead of
being stored or shown. Supported settings never lead to such a value. The
delivered concentration and each starting fraction must be at or below 0.99 of
ambient pressure (§ "The numerical envelope").
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

**For developers.** The conversion between a fraction and a percent is written
only in `src/anesthesia_sim/core/concentration.py`, in both directions. The two
forms are distinct types there, `Fraction` and `Percent`, so a type checker
rejects a percent where a fraction is wanted before the program runs. When the
program runs, a value of the wrong form is rejected as a missed conversion
rather than as a value out of range. The code also rejects a value that is
already converted, or one that does not say which form it is in.

On a 0 to 8% dial in 0.01% steps, multiplying a fraction by 100 fails to return
the percent it came from for 126 of the 801 settings. The first failure is at
0.23%, and 0.9% comes back as 0.9000000000000001. A new run's dial is set in
`AgentUptakeSystem.for_agent()`.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

The agent's MAC is stored as a `MacPercent`, a `Percent` that rejects zero when
it is built. Every formatter that forms a MAC multiple rejects a divisor that
was not built as a `MacPercent`. No other lower limit is set on the MAC, so a
MAC far below any real agent's would still give multiples too large to read. The
shipped MACs are 1.2% to 6.0%.
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- provenance: data/agents/desflurane.json mac_percent = 6 -->

The fraction and percent types raise a `TypeError` for anything other than an
`int` or a `float`, such as a `bool`, a `Decimal` or a string, before they check
the range. The rules they share with the flows are written once, in
`core/checked_number.py` (§ "Supported input ranges"): what counts as a number,
that one checked quantity is never built from another, and that minus zero is
stored as zero.

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

**The reference condition matters only when an amount is converted out of the
unit**, into moles, mass, or the millilitres of liquid that a vaporizer is filled
from. Every governing equation works with dimensionless fractions and physical
volumes, and every partition coefficient is a ratio. So the condition changes no
concentration curve, mass balance or displayed concentration, and no other
number under § "Governing equations", "Conservation of agent mass" or
"Minimum displayed outputs". The ideal-gas molar volume is 25.450 L/mol at
37 °C, so declaring 37 °C instead would change each converted amount by a
factor of 1.058.

**Three reasons favour 20 °C.**

1. **The published vapour-to-liquid constants are 20 °C constants.** The
   consumption literature quotes one number per agent, the vapour volume
   obtained from 1 mL of liquid. Biro gives isoflurane 195 mL, sevoflurane
   184 mL and desflurane 210 mL. The same number can be derived from the
   liquid's measured density, its molar mass and the molar volume. At 20 °C the
   derivation reproduces all three within 0.7 %. At 37 °C it runs 5.1–6.3 %
   high:

   | Agent | Liquid density at 20 °C, g/mL | Molar mass, g/mol | Derived mL vapour per mL liquid, 20 °C | Biro's constant | At 37 °C |
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
   $`\dot V_F`$, the flow at the common gas outlet. That flow is carrier gas
   plus the vapour that the vaporizer added. It is on the machine side of the
   patient, at operating-room temperature, not at 37 °C. A cost or waste
   figure is computed from those two amounts (`ROADMAP.md` "Planned milestones"
   item 28). Declaring 20 °C makes them exact. Declaring 37 °C would leave them
   approximate, and would need a correction from room to body temperature on
   $`\dot V_F`$. That correction would change the governing equations, not just
   a label.

3. **Gas Man's own constants are 20 °C constants, and its litres carry no
   condition at all.** Gas Man states a condition in one place only, the line
   `Volatility=209 Vapor/Liquid volume ratio (20'C)` in its settings file,
   `GASMAN.INI`. It never states a condition on the litres of uptake and of
   delivered agent that it displays. This model likewise uses the condition
   only where vapour is converted to liquid. The 20 °C derivation reproduces all
   five of Gas Man's printed vapour-to-liquid constants within 0.35 %, and the
   37 °C derivation runs 5.6–6.2 % high:

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

   This model takes its partition coefficients, MACs and reference patient from
   Gas Man (§ "Source hierarchy"), so its amounts follow Gas Man's arithmetic. A
   different reference condition would make this model's litre and Gas Man's
   litre different quantities, although every parameter behind them is shared.

<!-- provenance: data/agents/sevoflurane.json liquid_density.g_ml = 1.5203 -->
<!-- provenance: data/agents/isoflurane.json liquid_density.g_ml = 1.5019 -->
<!-- provenance: data/agents/desflurane.json liquid_density.g_ml = 1.4651 -->
<!-- provenance: data/agents/sevoflurane.json molar_mass_g_mol = 200.05 -->
<!-- provenance: data/agents/isoflurane.json molar_mass_g_mol = 184.49 -->
<!-- provenance: data/agents/desflurane.json molar_mass_g_mol = 168.04 -->
<!-- derived: 182.8 from data/agents/sevoflurane.json liquid_density.g_ml = 1.5203, molar_mass_g_mol = 200.05 -->
<!-- derived: 195.8 from data/agents/isoflurane.json liquid_density.g_ml = 1.5019, molar_mass_g_mol = 184.49 -->
<!-- derived: 209.7 from data/agents/desflurane.json liquid_density.g_ml = 1.4651, molar_mass_g_mol = 168.04 -->

**Converting an alveolar, venous or tissue amount at 20 °C overstates it by
5.8 %** (§ "Known limitations", under § "One reference condition, where the
model physically has two").

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
  measured on the agent.
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
concentrations directly. It works in litres unless the implementation document
explicitly selects another consistent unit.

## Symbols

The **Code** column names the one place in the model's code that holds each
symbol.

| Symbol | Meaning | Unit | Code |
| --- | --- | --- | --- |
| $`t`$ | Elapsed simulation time | s | `SimulationState.elapsed_s` |
| $`\Delta t`$ | Simulation step | s | `SimulationState.simulation_step_s` |
| $`F_D`$ | Delivered fresh-gas agent fraction | dimensionless | `BreathingCircuit.delivered_partial_pressure_fraction` |
| $`F_I`$ | Inspired agent fraction, taken as the fraction in the breathing circuit (see § "Model boundary") | dimensionless | `BreathingCircuit.inspired_partial_pressure_fraction` |
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
| $`\mathrm{MAC}_\%`$ | The agent's alveolar concentration at 1 MAC, at age 40. It is used only as a display divisor | percent | `AgentParameters.mac_percent` |
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
$`F_D \rightarrow F_I \rightarrow F_A`$. The middle one, $`F_I`$, is the
inspired fraction, taken from the gas in the breathing circuit. The circuit's
quantities carry the subscript $`C`$: $`V_C`$ is its volume and $`M_C`$ is the
amount of agent in it. § "Model boundary" above states the assumption that
makes circuit gas and inspired gas one quantity, and what would break it.

Symbols and the gas-phase cascade ($`F_D`$, $`F_I`$, $`F_A`$) follow Hendrickx
and De Wolf (pp. 161-162). They attribute the $`F_D - F_I`$ gradient to
rebreathing (p. 169) and the $`F_I - F_A`$ gradient to uptake (p. 171), and
describe the teaching role of the $`F_A/F_I`$ curve (p. 167) (Hendrickx JFA,
De Wolf A. Special aspects of pharmacokinetics of inhalation anesthesia. In:
Schüttler J, Schwilden H, eds. Modern Anesthetics. Handbook of Experimental
Pharmacology 182. Springer, 2008:159-186).

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
within one part in a million million (`FLOW_FRACTION_TOLERANCE = 1e-12`), so the three groups together receive
the whole cardiac output:

$$
\sum_i Q_i = Q
$$

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

The blood:gas partition coefficient relates the concentration of agent
dissolved in blood to the gas-phase concentration at equilibrium.

**The simulated patient has one blood:gas coefficient.** It comes from the
agent's data. The lung's uptake term and every tissue group's tissue:blood coefficient read that one value, and the tissue groups store none.

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
venous pool. The pool refuses a second value, and the patient refuses a
replacement pool with a different one. If each tissue group kept its own copy,
the copies could disagree and no check would fire. A pool at 0.1 beside groups
at sevoflurane's 0.65 would still conserve agent, and the run would give uptake
curves that look plausible and are wrong.
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

**$`\dot V_F`$ is the flow at the common gas outlet, not the flowmeter
setting.** The balance uses one $`\dot V_F`$ for the agent that arrives, at
$`\dot V_F F_D`$, and for the mixed circuit gas that leaves. $`\dot V_F`$ is
therefore the whole gas stream delivered to the circuit: the carrier gas plus
the vapour that the vaporizer adds to it. Let $`\dot V_c`$ be the carrier flow,
which is what the flowmeters are set to, and let $`\dot V_v`$ be the added
vapour flow. The delivered fraction is then
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

**$`V_C`$ is the assembled breathing system, never a manufacturer's apparatus
figure.** The model has one well-mixed gas compartment in front of the
patient, so the corrugated limbs and the Y-piece can only be inside $`V_C`$.
$`V_C`$ is therefore the sum of two volumes:

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

**The exhaust is a semi-closed circle's, and it vents whenever fresh gas
flows.** Two of the model's assumptions keep the outflow equal to the inflow, as
in a circle while gas is passing through its surplus gas valve. Both gas
compartments have fixed volumes. The modeled patient takes up no net volume,
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
slows. At the opening fresh gas flow of 4.0 L/min, the gap is 6 to 8%. At
0.5 L/min, which the simulator also allows, it is half or more.
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

**Neither is modeled here, and the reason is not the exhaust term.** The
circuit equation still applies with the valve shut. Gas that the patient's
uptake pulls out of the circuit leaves at $`F_I`$, exactly as spilled gas does.
The term $`\dot V_F(F_D-F_I)`$ is therefore the same either way, and so is
$`F_I`$. Two other things change.

- **Where the agent in the outflow goes.** The model counts the whole of
  $`\dot V_FF_I`$ as leaving the system (§ "Circuit exhaust"). With the valve
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
circuit alone against its exact solution are in § "Preserved circuit reference
tests".

Desflurane's dial maximum is stored in `data/agents/desflurane.json` as
`max_delivered_concentration_percent`.

Never shorten the "Fresh gas flow" label to its first line to fit a layout.

A machine's $`V_C`$ is stored as `circuit_volume_l` in its file in
`data/machines/`. It holds the assembled total of machine and patient circuit until the split planned in `docs/machine-abstraction.md` stores the apparatus volume separately, as `apparatus_volume_l`.

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
Closed-circuit operation is a property of the machine, and one coefficient
switched by a condition is the wrong way to model it. The machine design in
`docs/machine-abstraction.md` reserves a place for it, a `closed_circuit`
removal strategy, recorded there as not implemented.
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4 -->
<!-- not-restated: 2 % -->

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
it.
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
  § "Supported simulation step" compares the simulation step with this 5.83 s.
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
moves any of them. On 2026-11-01, the model's code and the independent copy
agreed to within a relative difference of 3 × 10⁻¹⁵.

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
figure and is not a stored parameter.** This project ships no nitrous oxide parameter file at all. The value is used here only to size the comparison.

**The fixed alveolar volume blocks three features.** "Known limitations" lists
them separately: nitrous oxide, simultaneous gases, and concentration or
second-gas effects. Lifting the fixed-volume constraint would unblock all three.

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
§ "Selected method (as implemented)" does not need such short steps.

The test that recomputes the table is
`test_modal_time_constants_are_the_pinned_ones` in
`tests/reference/test_coupled_dynamics.py`. It recomputes every figure from
that module's own transcription of the equations, independent of
`core/governing_equations.py`. When it fails, its message says to re-derive the
table. On 2026-11-01 the eigenvalues of the matrix that `build_system_matrix`
assembles agreed with the table's figures to within a relative difference of
3e-15.

In the matrix of the model's equations, the alveolar row divides each of its
terms by the alveolar volume (`alveolar_volume_l`), which the equation settings
hold fixed for the whole step. Two standard formulations lift this constraint,
and a milestone that adds several gases could adopt either one. They are
equivalent to first order. The first lets $`V_A`$ change over time, and the
concentration equation gains a volume term:

$$
\frac{dV_A}{dt} = \dot V_{A,\mathrm{in}} - \dot V_{A,\mathrm{out}} - \sum_k \dot M_{\mathrm{uptake},k}
\qquad
\frac{dF_A}{dt} = \frac{dM_A/dt - F_A\,dV_A/dt}{V_A}
$$

The second keeps $`V_A`$ constant and replaces the volume lost to total uptake
with inspired gas, so the effective inspired ventilation becomes
$`\dot V_A + \sum_k \dot M_{\mathrm{uptake},k}`$. This second form is the
smaller change to this model, and the classical treatment uses it.

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

In this model, $`F_a \equiv F_A`$ at every instant, for the reasons
§ "Model boundary" gives. There is no equation for an arterial amount of agent, and
no arterial capacity or time constant. Every equation below that contains
$`F_a`$ uses the current alveolar fraction $`F_A`$ in its place.

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

## Conservation of agent mass

### External delivery

The cumulative amount of agent delivered is:

$$
M_{\mathrm{delivered}}(t) = \int_0^t \dot V_FF_D\,dt
$$

### Circuit exhaust

In the semi-closed circle system, the amount of agent sent to the exhaust by
time t is:

$$
M_{\mathrm{exhausted}}(t) = \int_0^t \dot V_FF_I\,dt
$$

A machine with its surplus gas valve shut sends no agent to the exhaust. It
needs a different model. See § "Breathing circuit".

### Stored amount

The total stored amount of agent is:

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

The model advances in explicit simulation time, in steps, and holds every setting constant over each step (piecewise-constant settings).

The implementation must:

1. derive concentrations from the current stored amounts;
2. evaluate every transfer from one consistent state;
3. make each transfer between two compartments remove from one exactly what it adds to the
   other, so that such transfers leave the total stored amount unchanged;
4. calculate fresh-gas delivery and exhaust in the same step as the compartments whose boundary
   they cross, by the same method and over the same time course;
5. update the cumulative amounts delivered and exhausted;
6. advance explicit simulation time; and
7. calculate the post-step mass-balance residual.

The method in § "Selected method (as implemented)" meets the requirements for transfers and for
fresh-gas delivery and exhaust. It advances every compartment together in one step, so no
transfer is applied before another, and nothing is held fixed while another value moves. Every rate is computed from the same state, which meets requirement 2.

A step is all-or-nothing. A step that cannot be completed must leave every tracked value exactly
as it was before the step. § "Step atomicity" explains why, and what the run is left with.

**The model works within these limits.** § "Supported simulation step" gives the results behind
the step limits, and § "The numerical envelope" gives those behind the other limits.

- **The largest step, 0.1 s.** Each step is exact, so this limit is set by how late a dial
  change reaches the model rather than by accuracy. For an ordinary dial change, the delay
  causes about a tenth of the error from one standard deviation in a measured partition
  coefficient. For an abrupt ventilation change, it causes about twice that error.
- **Compartment volumes from 0.01 to 10 000 L, and partition coefficients from 0.001 to
  10 000.** These limits sit far outside any real patient or agent. The arithmetic has been
  checked against a high-precision calculation across the whole range.
- **Delivered and stored fractions up to 0.99.**
- **The tolerance on the mass-balance residual, one part in 10⁹.**
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_VOLUME_L = 0.01 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_VOLUME_L = 10000 -->
<!-- provenance: core/numerical_envelope.py MINIMUM_PARTITION_COEFFICIENT = 0.001 -->
<!-- provenance: core/numerical_envelope.py MAXIMUM_PARTITION_COEFFICIENT = 10000 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

**For developers.** In the system matrix, each transfer between two compartments is a pair of
off-diagonal entries whose contributions to the total stored amount cancel. A test checks this
cancellation as a property of the matrix (`tests/unit/test_governing_equations.py`).

The all-or-nothing rule is there because a step writes each compartment in turn, and a check
can reject a value after earlier compartments have been written.

Each limit is set where it is for these reasons:

- Lowering the largest step would make no visible difference, because the screen is redrawn
  every 0.2 s.
- The smallest step is 1 ms because it is the finest step whose results have been tested and
  found to match those at the largest step.
- The smallest volume is no lower because, at 0.001 L, the error at the hardest settings grew
  to 0.049% of the state over 24 hours.
- The fraction limit is below 1 so that rounding near the top cannot carry a fraction above 1.
- The tolerance is at least 25 times a correct 24-hour run's residual, which stayed below 4e-11.
  A looser tolerance would let a real accounting error pass.
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->
<!-- not-restated: 24 hours -->

### Step atomicity

When a step of simulated time fails, the model undoes it. The run then stops, because the same
step would fail again. The model is left at the last completed step, which is a real result at a
real simulation time. Undoing the step decides only what the screen may show while the run is stopped: that result, which a reader may reason about. The error message names the check that failed and the step size, so nobody has
to infer the cause from the numbers.

The model puts back the eight values that change from step to step: the circuit's inspired
fraction, the alveolar amount, the three tissue amounts, the venous amount, and the running
totals of agent delivered and exhausted. Settings and parameters keep their current values.
Restoring cardiac output, for example, would undo a change that the run had accepted. If the
circuit volume has changed, the volume stays at its new setting, and the model puts back the
circuit's saved amount of agent rather than its saved fraction.

A failed step is undone because a partly applied step would leave some compartments at the new
time and others at the old time. The model never produced that set of numbers at any instant,
yet on screen they could not be told apart from numbers it did produce. The project prefers an
obvious failure to a plausible-looking number.

**For developers.** Before each step, the model saves the eight values listed above and the
starting amount of the mass-balance check, and it restores them if the step fails
(`AgentUptakeSystem.advance()`). A failed step raises an exception (`SimulationNumericalError`).

The step type (`SimulationStep`) cannot be built with a value below 1 ms or above the largest
step. Each limit is a named constant (`MINIMUM_SIMULATION_STEP_S` and
`MAXIMUM_SIMULATION_STEP_S`). The two methods that advance the model accept only the step type
(`AgentUptakeSystem.advance()` and `SimulationState.advance()`).
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

### Selected method (as implemented)

Each step solves the **whole model at once, exactly**. Every setting is held constant during a
step, so within that step the six modelled fractions follow fixed linear equations, which have
an exact solution. The same step also updates two running totals: the agent delivered to the
circuit and the agent exhausted from it, at the rates in § "External delivery" and
§ "Circuit exhaust".

**The only error this method leaves is rounding.** In a 3600 s run at 1 MAC on 2026-09-06, the
agent left unaccounted for at any step was at most 13 picolitres, for desflurane, and less than
one part in a trillion of the agent handled for every agent.

**The exact step has two consequences.**

First, **a step cannot drive a fraction negative**, whatever the step size and the parameters,
because the solution is exact and every transfer rate is zero or positive. The calculation keeps
this true after rounding.

Keeping each fraction below 1 depends on what the model accepts as input. Without rounding, no
fraction exceeds the larger of the delivered fraction and the largest fraction the run started
with. Rounding could still carry a fraction just above 1 from a state already at 1. No supported
setting reaches that state, because every vaporizer in the simulator keeps each fraction far
below 1, even at its maximum. The model also refuses such a state as an input: the delivered
concentration and every starting fraction are limited to 0.99 of the ambient pressure.
§ "The numerical envelope" gives the largest overshoot measured from that limit.
<!-- provenance: core/supported_ranges.py MAXIMUM_INPUT_FRACTION = 0.99 -->

Second, **a shorter step does not change the result**. A test checks that all supported step
sizes agree to within rounding. That test cannot show the result is *right*, because a wrong
transfer rate would give the same error at every step size. Nor can a check that no agent goes
unaccounted for, because every transfer between compartments adds exactly what it removes.
Another test checks that the result is right. It compares all six modelled fractions with an
independent solution of the governing equations (§ "Independent-solution test").

**For developers.** Within a step, the six fractions follow $`dy/dt = Ay + b`$, where $`A`$
holds the rate constants and $`b`$ the constant inputs. The two running totals are the seventh
and eighth states. Adding a ninth state whose value is always 1 folds $`b`$ into $`A`$, giving
$`dy/dt = Ay`$. The exact solution is

$$
y(t+\Delta t) = \exp(A\,\Delta t)\,y(t)
$$

The model builds $`A`$ in `core/governing_equations.py`. Each entry of $`A`$ is one term of one
balance equation in § "Governing equations", in the order this document gives them. The model
computes $`\exp(A\Delta t)`$ in `core/matrix_exponential.py`, which contains no physiology. That
module's docstring gives the method's source and how its constants were derived. Neither module
needs an outside library.

The totals' rates are $`\dot M_{\mathrm{delivered}} = \dot V_FF_D`$ and
$`\dot M_{\mathrm{exhausted}} = \dot V_FF_I`$. Delivered agent has a simple formula of its own.
Exhausted agent does not, because it depends on the inspired fraction as that fraction changes.
It is $`\dot V_F\int F_I\,dt`$ along the coupled solution. The step matrix that advances the
fractions also computes it, which meets requirement 4 of § "Numerical method".

On 2026-09-06, the largest amount of agent left unaccounted for was 1.0e-12 L for sevoflurane,
2.4e-12 L for isoflurane and 1.3e-11 L for desflurane, and as a share of the agent handled it was at most 9.2e-13 for every
agent. Conservation is built into the matrix. Because the arithmetic is done in fractions, each
transfer's equal-and-opposite terms cancel only to within rounding.

The check on agent accounting (`check_agent_accounting`) accepts an error within either of two
limits: a fixed 1 picolitre, set in `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L`, or a share of the
agent handled. The fixed limit catches a gross error early, while little agent has been
delivered, and the share limit takes over after that. The rounding error is a thousand times
smaller than the share limit, so no accuracy is lost.

In litres, though, that error scales with the largest amount in play, which over an hour at
desflurane's dial setting is about 43 L of delivered agent. A long run therefore routinely
exceeds the fixed limit and passes on the share limit alone. In runs on 2026-09-06, the fixed
limit was first exceeded after 3452 s at the reference settings, and after 538 s at the most
extreme sevoflurane settings the model accepts.

The reference runs test against the share limit, `MASS_BALANCE_RELATIVE_GATE`
(§ "Mass-balance identity"). A release test on the error in litres would rest on a claim that
depends on the dial setting and stops being true after about an hour of simulated time.

Every off-diagonal entry of $`A`$ is a transfer rate, so it is nonnegative. That makes $`A`$ a
Metzler matrix and $`\exp(A\Delta t)`$ an entrywise nonnegative matrix, whatever the parameters.
Shifting the matrix before summing the exponential's series keeps that true in floating point.

The capacity guard and the rollback in § "Step atomicity" cover two cases to which the reasons
above do not apply. The first is a state at the top of the range, which a caller can pass when
resuming a run (`resume_at`) or opening a run definition (`RunDefinition`). Those two routes
check only that a state lies from 0 through 1. The second is a model extension whose matrix is
not a pure transfer system.

The step-size test is `test_step_refinement_converges`.

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
update. So the same slider moves made at two playback rates are different inputs,
and they produce different runs. The simulated instants that a reader can reach are
`multiplier × 0.1` s apart:

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

The program advances the model in steps of 0.1 s of simulated time, the largest step the model
allows. The program updates every 0.1 s of real time, the same as the step, so that real-time playback runs
one step per update. At a faster playback speed, each update runs more steps of the same size.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MAXIMUM_SIMULATION_STEP_S = 0.1 -->

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

Three constants have the same value and mean different things:

```text
MAXIMUM_SIMULATION_STEP_S  = 0.1                   # core/simulation_step.py
SIMULATION_STEP_S          = SimulationStep(0.1)   # app/dashboard_frame.py
SIMULATION_TICK_INTERVAL_S = 0.1                   # app/dashboard_frame.py
```

The step the program uses (`SIMULATION_STEP_S`) is set separately from the largest step and
equals it only in this configuration, so the two have separate names.

The tick interval, the time between updates, has a name of its own
(`SIMULATION_TICK_INTERVAL_S`). Each update runs `multiplier × tick interval ÷ step` whole steps,
so a test can check a playback speed such as "60× real time". If the interval shared the step's
name, someone could change how often the program updates to suit a different computer, without
recomputing the speeds. Every speed on screen would then be false, and nothing would fail.

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
- a brief justification for selecting that source;
- the source's tier in the hierarchy below; and
- where the source is not a primary measurement, what the primary literature
  reports and how far that differs from the source's value.

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

#### Where each stored value comes from

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
silently. Whoever changes a count must check
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

The following table records the values selected for v0.1.0. Each value is
loaded from a versioned data file and validated against its schema, rather
than hardcoded. Full citations, definitions and reference conditions are
recorded as `sources` entries in that file, not duplicated here.

Each row names the file and the exact JSON key path of the value it documents,
so a row traces to one stored value, not to a file that happens to contain a
matching number. `tools/doc_check.py` checks each row's key and value against
its file (§ "How this document is held to the tree"). A derived row states
the stored value beside the derived one. The tissue:blood coefficients are
computed when a file is loaded, from the tissue:gas and blood:gas values, so
their rows name the stored tissue:gas key and show the division.

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
75.8 + 18 + 6 = 99.8. The model requires the flow fractions to sum to 1 within
the tolerance that § "Tissue groups" gives, so the published set could not be
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

There is no "arterial blood-pool volume" row, because arterial blood has no
volume of its own in this model (see § "Model boundary").

**Dividing tissue:gas by blood:gas is the literature's own operation, and one
published table reproduces its results.** Eger and Saidman state the operation in these words:
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
whose sum lies outside `FLOW_FRACTION_TOLERANCE` of 1.0 (§ "Tissue groups").
`default_fresh_gas_flow_l_min` is optional in a machine profile. A run built
from a profile that omits it starts at `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`
in `core/circuit.py`
(`test_a_profile_omitting_the_default_fresh_gas_flow_falls_back_to_the_teaching_default`).
`test_the_flow_default_matches_the_shipped_machine_file` fails if the constant
and the file's value ever differ. The tissue:blood coefficients are computed in
the `AgentParameters` properties in `core/parameters.py`, and the tissue-blood
partition-coefficient tests in `tests/unit/test_parameters.py` guard that
division.

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
coefficient, which makes that coefficient the obvious suspect. It is not the cause. § "Desflurane's residual, and
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
only away from sea level** (§ "Assumptions", § "Known limitations"). So the model does not need
to know which kind of device a limit came from.

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

Presenting a single-agent alveolar concentration as if it indicated anesthetic
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

## Runtime controls

Four settings can be changed during a run without resetting the model's state:

- fresh gas flow;
- delivered agent concentration;
- alveolar ventilation; and
- cardiac output.

From the next simulation step on, a change affects transfers. Changing delivered
concentration does not alter the existing circuit concentration. Changing
ventilation does not alter existing circuit or alveolar stores. Changing cardiac
output does not alter existing blood or tissue stores, but it recalculates
tissue flows:

$$
Q_i=f_iQ
$$

**The four settings above are the model's only inputs.** The interface has
settings of its own that can also be changed during a run: the playback rate,
the chart's time base, and which compartment traces are drawn. None of them
affects the model's state. Identical inputs still produce identical results, so
a case played at sixty times real time is the same run watched faster.

**The playback rate does decide when an input acts.** A control changed
*during* a run first acts at the next tick, so the same slider moves made at
two playback rates produce different runs. § "Supported simulation step"
quantifies this.

**For developers.** § "Interface boundary" sets the constraints on the
interface's own settings. § "The reproducibility guarantee" rules out treating
the playback rate as a model input.

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

The record lists each change to a control that the model runs under, with the
simulated time at which it took effect. The record is kept with the run and
cleared with it. § "The control-input timeline" and the display rules below
explain what the record is for, what it shows and why it takes this form.

#### The run is that record, and every state is derived from it

**A run is stored as two things.** The first is the settings in force at each
moment: the four controls above, together with the patient and agent parameters
that the equations use. The second is one *keyframe* per change, which is the
state at the instant that change took effect. Flows are stored as they were set,
in liters per minute (§ "Time" explains why). Nothing else about the run is
stored. The chart is drawn from this record, so there is no second record that
could disagree with it.

**The program computes the state at a single instant in one calculation.** It starts from the keyframe that opens the stretch of constant settings containing that instant, so no value has to have been recorded for the state to be recoverable. Between two
changes, the method in § "Selected method (as implemented)" solves the
equations exactly over any length of time, not only over one simulation step.
Each keyframe is computed the same way from the keyframe before it, starting at
the beginning of the run.

**The chart's values are computed a second way, and the two ways agree well
within the last displayed digit.** To draw the chart, the program computes the
state at evenly spaced instants, one per column, each from the one before it
while the settings stay the same. Both ways solve the same equations exactly.
They differ only in the order of the arithmetic, which changes the rounding. On
2026-09-07 both were compared with a step-by-step run of the simulation. Their
differences from it were about ten orders of magnitude below 0.01%, the
smallest difference that the two-decimal percent readout can show
(§ "Displayed precision"). A test checks the record against the step-by-step
simulation that advances the run. § "The canonical evaluation rule" below
states which of the two ways a stored, exported or branched value may be
taken from.

**For developers.** The record is defined in `core/run_definition.py`. The
method is exact because the equations are linear and time-invariant while every
setting is held constant.

The step-by-step run used for the 2026-09-07 comparison simulated 600 s of
sevoflurane with two setting changes and reached a fraction of 0.0316. The
state at a single instant stayed within 1.8e-14 of that run, and the drawn
chart within 3.7e-15, both as absolute differences in a fraction of one
atmosphere. The test of the record against the step-by-step simulation is the
"Closed-form agreement test".

A *propagator* is the matrix that carries the state across one interval at
fixed settings. A *stretch* is the time between two changes. Drawing the chart
reuses one propagator across the columns inside a stretch, chaining from the
first column, and that reuse is what makes a frame cheap.

Storing the run as a record keeps it small. At one sample per fixed 0.1 s
step, a 30-day case takes 3.16 GiB: 25 920 000 samples of 130.8 bytes each
(measured over 20 000 samples of a live run). Stored as its settings and their
changes, the same case takes 1.6 MiB, about two thousand times less. The
1.6 MiB assumes that every day is a busy ICU day with 50 setting changes, which
gives 1 501 stretches over the case.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

With the run stored as a record, the time to draw a chart window does not grow
with the run's length. A one-hour window at 600 columns costs 10.6 ms to draw on
a two-hour run and 13.0 ms on a thirty-day run. Drawing from per-step samples
cost 62.6 ms at four hours and 207.7 ms at twelve.

The number of changes in view does raise the cost of a frame, because each
stretch in view needs its own propagator. A window spanning the whole thirty-day
run at 600 columns costs 14.2 ms with two changes in view, 231 ms with sixty and
about 1.1 s with six hundred, when no propagators are kept from an earlier frame.
Once the changes outnumber the columns, sampling 600 instants is the wrong way
to draw the run. What to draw instead is a question for the interface.

The number of changes in view sets the cost of the first frame only. Drawing a
window keeps the propagators it used (`RunDefinition.evaluate_anchored`), and
the next window can reuse them. All but three of them cover an interval that
the grid fixes: either the column spacing, set by the time base, or a stretch's
offset to its first grid column, set by the anchoring. The three that change
are the two for the window's bounds and the one for the offset in the stretch
where the window opens. In that stretch, the first grid column is the first one
past the window's left edge. So, for a window that follows the run, the program
forms two new propagators every frame. It forms the third only when the
window's left edge has passed a grid column since the frame before. It also
forms those of any stretch newly in view. A change of column spacing makes it
form every propagator again.

The first-frame and later costs were measured on 2026-10-04 on a 24-hour run,
the longest that § "Supported run length" allows, with every setting distinct.
The window spanned the whole run at 600 columns, with its left edge fixed at the
run's opening. With two, sixty and six hundred changes in view, it cost 13.2 ms,
179 ms and 819 ms on its first frame, and 6.3 ms, 5.9 ms and 8.3 ms on each
frame after.

Only the last window's propagators are kept. Each is about 3.1 KB, and six
hundred take 1.8 MiB, so their memory is bounded by one window and does not grow
with the run. A kept propagator is identical, bit for bit, to one formed again
from the same inputs, because it is looked up by all of them: the settings and
the interval. Which propagators are kept depends on the window drawn last, but
no drawn value can depend on that. So the kept propagators are not a second
record of the run, and the function that returns the state at an instant
(`state_at`) reads none of them.

At the dashboard's settings, with kept propagators, the column count sets the
cost of a frame and the number of changes in view does not (measured
2026-10-04). The dashboard redraws every 200 ms (`RENDER_INTERVAL_S` in
`app/dashboard_frame.py`) and shows at most two runs (`MAX_DISPLAYED_RUNS`). It
draws each run with one call (`SimulationController.drawn_window`) at
`max(150, plot width in pixels + 1)` columns (`chart_columns` in
`app/chart_frame.py`). Each cell of the table gives one run's cost per frame
without kept propagators, then with them. The costs are medians of 40 frames,
with a 15-minute window following a 30-minute run at 1x:
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

| Changes in view | 150 columns | 1 069 columns | 2 401 columns |
| --- | --- | --- | --- |
| None | 6.6 ms → 3.9 ms | 12.3 ms → 10.1 ms | 20.3 ms → 18.6 ms |
| Ten | 25.0 ms → 3.5 ms | 28.6 ms → 9.4 ms | 35.5 ms → 18.0 ms |
| Sixty | 135 ms → 3.7 ms | 119 ms → 9.1 ms | 129 ms → 18.8 ms |

With kept propagators, three costs are left. The propagators for the window's
two bounds cost about 1.4 ms each on every frame. Each column costs one chained
product, at about 7 µs. The third cost is forming the propagator for the offset
in the stretch where the window opens. At 1x, it is formed on about one frame in
forty at 150 columns, one in four at 1 069 and one in two at 2 401. From 5x up,
at 1 069 columns or more, it is formed on nearly every frame.

Even so, playing faster adds little. In a later measurement of one run with
sixty changes in view, a frame at 1 069 columns cost 13.0 ms at 20x against
12.0 ms at 1x. At 2 401 columns, it cost 23.9 ms against 22.8 ms. That
measurement's times ran about a quarter above the table's.

Two runs at 2 401 columns therefore take about 40-50 ms of the 200 ms between
redraws. Without kept propagators, two runs with sixty changes in view at
1 069 columns take about 240 ms, which is longer than the time between redraws.
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

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
fraction (§ "Reset behavior"). Putting the fractions back, or
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

Code in `app/` changes settings only through the simulation controller, which saves the whole
settings record at each change. Before each step, the controller compares the current settings
key (`AgentUptakeSystem.settings_key()`) against the key saved with the last settings record.
It makes the comparison in the method that advances the run, `SimulationController.advance()`.

The agent selector and the sliders read the snapshot only inside handlers guarded by
`halt_gate` in `app/halt_gate.py`. A halt resets the selector from the run's settings record,
because the selector would otherwise read the agent from the refused snapshot. If a halt comes
before the screen is redrawn, every withheld value is hidden before the dials are written,
because writing a dial can raise an exception.

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

**The simulator refuses a setting outside the ranges, because neither its code nor its
model has been checked there.** The ranges are the model's **verification domain**.
Across them, its results have been compared with an independent calculation
(§ "Independent-solution test") and with measured human data
(§ "Published wash-in and elimination validation test"). Every model result in this
document comes from settings within the ranges.

Outside the ranges, the simulator must refuse rather than show a plausible-looking number. A cardiac output
of 1000 L/min is not a patient, and the model's equations were never proposed to describe
one. Solving them exactly for that setting would give a precise answer to a question that
physiology does not ask. Nothing on the display would invite doubt.

**For developers.** Each limit was chosen as the edge of the settings that the interface
offers and that the two tests above cover. Nothing in the equations breaks at 10.01 L/min,
because the calculation is exact at any flow. Widening a limit is a legitimate change, and
a safety-critical one. First extend the verification domain. Then re-run the test described
in § "Independent-solution test" over the wider range, and revise this section with the
results.

#### The model's envelope and a machine's deliverable range are two claims

A run accepts a fresh gas flow only when the flow lies inside two separate ranges. The model's
envelope is the range of fresh gas flows over which the model is claimed to represent a patient.
The model is built on lumped compartments, the reference adult's fixed volumes and constant
partition coefficients. A machine's deliverable range is what its flowmeters, minimum flow and
fresh gas delivery can physically set. A machine can therefore narrow the flows a run accepts, but
never widen them beyond the envelope.

**The machine that ships with the simulator declares no deliverable range, so the model's
envelope is the only limit on the flow.** It declares none because, for all eight machines
surveyed, no operator's manual or manufacturer specification giving a deliverable range could be
reached (`docs/machine-survey.md` § "(b8) Flow bounds, minimum oxygen flow, and the hypoxic guard").
The survey names ISO 80601-2-13:2022 as the governing standard. That standard could not be
reached either, so the survey does not say what it requires. No declared range means **no claim,
not a machine known to be unlimited**. With the shipped machine, nothing displayed depends on a
machine's range.

**The fresh gas flow slider offers only flows inside both ranges.** It moves in steps of
0.1 L/min, the flow's displayed resolution. Where an end of the offered range falls between two
steps, the slider offers the step just inside it. For a machine with a minimum flow of 0.25 L/min,
the slider's lowest setting is 0.3 L/min, never the 0.2 L/min that the machine would refuse. An
offered range that contains no step is an error, because otherwise the slider could offer only a
flow that the run refuses.

**A machine whose starting flow is not one of the slider's steps is refused when the dashboard
sets up its controls.** A user reads the slider's position like a displayed value. If a run
started between two steps, the slider would sit on a neighbouring step beside a rounded readout,
and both would show a flow that the run does not have.

**Each refusal says which of the two ranges the setting is outside.** The model's refusal names
its envelope. The machine's refusal names the machine and says, in the same sentence, that the
model did not refuse the setting.

**A machine whose range does not overlap the model's envelope at all is refused when the
simulated breathing circuit is built.** If such a machine were accepted, every setting would be
refused, each time correctly, but no refusal would say that the pairing itself cannot be simulated.

**A machine's minimum oxygen flow is not stored.** It would affect nothing the model calculates,
because the model carries one volatile agent in one gas phase and no oxygen.

**For developers.** The two ranges are declared and enforced here:

| Claim | Declared in | Refused by |
| --- | --- | --- |
| The model's envelope | `MINIMUM_FRESH_GAS_FLOW_L_MIN` and `MAXIMUM_FRESH_GAS_FLOW_L_MIN` in `core/supported_ranges.py` | `FreshGasFlow`, which runs `require_supported_fresh_gas_flow` when it is built |
| A machine's deliverable range | `deliverable_fresh_gas_flow_range` in that machine's `data/machines/*.json` profile | `BreathingCircuit._require_deliverable_flow` |

The two ranges are kept apart because one merged pair of limits fails in two ways. A profile whose
flowmeter reaches 15 L/min would extend the range that every reference test was run over,
without any change to `core/supported_ranges.py`. The result would be an exact number, computed outside everything that was checked and shown exactly like one inside it. Take a machine with no true off position
at its common gas outlet and a minimum flow of 0.5 L/min. The merged pair would either fail to
represent it or move the model's lower limit for every other machine.

A test checks both refusals
(`test_machine_deliverable_flow_range_is_separate_from_model_envelope` in
`tests/unit/test_supported_ranges.py`). A machine range that does not overlap the envelope is
refused when it is reassigned on a built circuit, as well as when the circuit is built
(`test_a_machine_that_overlaps_the_envelope_nowhere_is_refused_when_built` in
`tests/unit/test_circuit.py`).

The circuit gives, in one place, the range of flows that both the model and the machine accept
(`BreathingCircuit.accepted_fresh_gas_flow_range_l_min`), and the slider reads it from there. The
slider is limited to that range because offering a flow the attached machine cannot set would
invite a refusal instead of preventing one.

The shipped profile (`data/machines/reference_circle_system.json`) records its deliverable range
(`deliverable_fresh_gas_flow_range`) as `null` and gives the reason in its `provenance_gap` field.
A test checks that the file still declares no range and says why
(`test_the_shipped_machine_declares_no_deliverable_flow_range_and_says_why` in
`tests/unit/test_parameters.py`).

The field table in `docs/machine-abstraction.md` lists a minimum total flow and a minimum oxygen
flow (`minimum_total_flow_l_min` and `minimum_oxygen_flow_l_min`) under the machine survey's
section (b8). Neither is stored in a machine profile, because that document allows a field only
where something uses it. A minimum total flow *is* the lower end of the deliverable range, so a
field of its own would store one number under two names in a safety-critical data file. A minimum
oxygen flow can be added when a hypoxic guard needs it, as an extension of the model rather than a
change to the data.

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
limitations" weighs do not agree about which way the stored flow errs. Either way,
the flow acts directly on the slow tail of washout. A run beyond this boundary
therefore displays a trace whose slow component is increasingly the two
omissions rather than the model.

**Inside the limit, the washout tail already lacks its largest measured term, and the
displayed number does not say so.** Every washout that the two Yasuda papers fitted needed
five compartments. Their authors took the fourth to be fat filled by diffusion from the
well-perfused tissue beside it. This model has no such route. The fourth compartment
carries the largest term in the measured curve over most of the supported span. The
intertissue-diffusion note under § "Known limitations" has the hours, the coefficients and the
arithmetic. All else equal, a tail without that store falls faster than the measured one
from about the third hour of elimination. Measured against the published mean curves over
the whole supported run, the shipped tail does so (§ "The first 24 hours of elimination
against the published mean curves").
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
and machine files and passes them on. The fresh gas flow keeps a default for a machine
profile that states no startup flow (§ "Source hierarchy: what may be cited as the
authority for a value" gives its reason, its constant and its tests).
`test_for_agent_builds_the_circuit_at_the_machine_file_s_values` and
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
  § "Required tests" below already specifies that behavior in the
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

**These ranges define the verification domain.** § "Independent-solution test" below runs
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

Reset pauses the simulation and keeps the user's selected settings. It also:

- sets simulation time to zero;
- clears the agent amounts in the circuit, alveoli, blood and tissues;
- discards the run, so that none of its states can be computed or drawn;
- clears the recorded timeline of control inputs;
- sets the cumulative amounts delivered and exhausted, and the mass-balance
  residual, back to zero; and
- clears any recorded failure, so that a session halted by a failed step can
  start again from a clean state.

**Reset on a branch returns it to its fork rather than to zero**, because a
branch never held the case's induction (§ "The canonical evaluation rule"). A
branch is a run taken from a point in a parent run, and that point is called the
fork. The branch's simulation time, state and accounting go back to the fork. Its
timeline of control inputs then holds the entries that the branch first opened
with, followed by each kept setting that differs from the one that the branch
opened under.

**The simulator refuses Reset when the tissue flows no longer sum to the cardiac
output.** Only a perfusion fraction written past its range check can cause
that. A refused Reset leaves the run exactly as it was. The interface then
halts the run, as it does when a step fails (`PL-M4M0`), and records the
refusal as its failure. If the run had already failed for another reason, that
failure stays the reason, and the banner's advice on recovery mentions the
refusal. The status word, the run controls and the banner state the halt. For
other failures, its banner names Reset as the way to recover. For a refused
Reset, the banner says instead that no setting can repair the run, because a
new cardiac output scales every flow by one factor. It also says that closing
and reopening the application starts a new run (`PL-01GY`). It names neither
the refused Reset nor a dial. The refusal message gives the two flows as they
were set, in L/min, the unit every readout shows.

**For developers.** Reset sets simulation time to zero by clearing the count of
steps taken. It releases the step length that the run was using, so that a fresh
run may use a different one. It discards the run by opening a fresh run
definition at the cleared state. A run definition is the stored record of a run: the
settings in force at each moment, and the state at each change of setting, from
which every other state is computed (§ "The run is that record, and every state
is derived from it"). The timeline is cleared because it belongs to
the run that recorded it.

A fresh run definition opens under the user's settings. On a branch, it opens
instead on the stretch of the parent run that the branch was taken from, and
those settings are recorded in it as a change at the fork. The branch's timeline
and provenance then agree on its settings (`PL-K5BS`, `PL-ZR49`).

Reset is refused when it cannot build the settings record that the fresh run
definition opens on. It builds that record from the compartments before it
changes anything (`SimulationController.reset()`). The build fails when the
tissue flows do not sum to the cardiac output, which can happen only when a
perfusion fraction is written in a way that bypasses its guard (`PL-HQF5`,
`PL-Z0HN`). The next simulation step (`AgentUptakeSystem.advance()`) refuses the
same record. It reports a failed step rather than a refused setting, because a
run whose record cannot be built is not worth continuing.

## Agent-change behavior

Changing the running agent must begin a new run. Switching between volatile
agents is not modeled (see § "Known limitations"), so there is no residual
washout to carry over. The model's values for the old agent would mean nothing
under the new agent's partition coefficients. A change of agent must therefore
do everything Reset does, and rebuild every compartment with the new agent's
parameters. It must also set the delivered concentration to 1 MAC of the new
agent rather than keep the old agent's percentage, because the same percentage
is a different clinical depth for each agent.

Beginning a new run **discards the current one**. All a user has to look back
at is the run's definition, its timeline of control changes and the simulated
time it reached. Nothing in the simulator saves them, and there is no undo. So
the interface must follow these rules:

- Before the interface discards a run that has any elapsed simulated time or
  any recorded control change, it must say so and ask the user to confirm.
- The question must name what will be lost in the terms that the display
  already uses, so that the user can check it against the readouts.
- Declining must leave the run, its definition, its timeline and the control
  that offered the change exactly as they were.
- Choosing the agent that is already running is not a change of agent, so it
  must do nothing.

A run with no elapsed simulated time and no recorded control change is
discarded without a question, so a user who presses Reset first can then
change agent without one.

**Pressing a run's Reset confirms discarding that run, and no other run**
(project owner, 2026-10-18, ratified, over extending it to every run the press
takes with it, `PL-W5WX`). A branch is a run taken from another run, the trunk,
at a moment called its fork. The display draws each branch beside its trunk.
Pressing the trunk's Reset also discards every branch, because a branch cannot
outlive its trunk. When a branch has run past its fork, or has had a control
change since then, the trunk's Reset says what that branch holds and asks before
it discards any run. Setting a dial back to a value the trunk had before the
fork is still a control change, because the branch started from what the dial
said at the fork. The trunk's Reset also asks about a branch when the simulator
cannot tell what that branch holds. Any other branch is discarded without a
question.

**Every run waits while a question is open, and carries on as it was when the
question closes** (project owner, 2026-10-31, ratified, over letting the runs
go on stepping, `PL-TPBH`). Each of these questions blocks the rest of the
window: the trunk's Reset question, the question asked before a change of
agent starts a new case, and the questions from the Workspace strip. While one
is open, the user cannot press Pause on any run. A run that was running
resumes at the same playback rate, and a paused run stays paused. The wait
changes nothing in a run, so each run follows the same course as if the user
had answered at once, as § "The reproducibility guarantee" requires. The
bookmark editor does not block the window, so runs go on as usual while it is
open.

**For developers.** Runs with nothing to lose get no question because a
question asked when nothing is at stake teaches the user to answer it without
reading it. By the time something is at stake, the question would go unread.

Four tests in `tests/integration/test_simulation_view.py` enforce the rule for
branches: `test_resetting_the_trunk_asks_before_dropping_a_branch_that_holds_work`,
`test_resetting_the_trunk_asks_before_dropping_a_branch_set_back_to_the_earlier_flow`,
`test_declining_the_trunks_reset_leaves_every_run_as_it_was` and
`test_confirming_the_trunks_reset_starts_the_case_over_without_the_branch`.

Runs wait during a question because otherwise a user who spent ten seconds on
it at 300× playback would come back to a case 50 simulated minutes further on.
The wait works by skipping ticks of the step timer. One test enforces the wait
during the trunk's Reset question
(`test_the_run_does_not_advance_while_a_reset_question_is_open`), and two tests
beside that one do the same for the question asked before a change of agent
and the Workspace strip's questions.

## What a branch comparison asserts, and what it does not

**A difference between two runs is real, but a comparison does not say what it
means for a patient.** The difference does not come from rounding, from the
order of the program's arithmetic, from the playback rate or from the computer
(§ "The reproducibility guarantee", § "The canonical evaluation rule"). What a
comparison can teach is the mechanism: which way a curve moves when one thing
changes, why it moves that way, and roughly how fast, in a model whose
structure makes the reason easy to see. That is the only educational claim that
two runs support.

### What is compared, and what the two runs share

**A comparison shows two managements of one case.** The first run is the
**trunk**. A **branch** continues it in another way from an instant that the
trunk passed through, and that instant is the **fork**.

**The display shows at most two runs.** While two are shown, another branch is
refused rather than replacing the one on screen. No branch is compared with
another branch, only with the trunk it was taken from. Nothing on screen
surveys a range of managements or ranks them, because only two were run.

**The program guarantees that both runs share the following:**

- **The patient.** Both runs use the same reference adult, which the branch
  takes from the trunk at the fork.
- **The agent.** The branch takes the trunk's agent at the fork, and neither
  run's agent can be changed while the comparison is shown.
- **The equations, the parameter set and the model version.** Both runs come
  from the same program.
- **The circuit volume.** The branch takes the trunk's circuit volume, which
  cannot be changed during a run.
- **The simulation step.** The branch uses the trunk's step, and a fork between
  two steps is refused rather than approximated.
- **Every setting up to the fork.** The branch's settings are replayed from the
  trunk's record of setting changes, then checked against the trunk's own
  settings at the fork.
- **The bookmarks set before the fork.** A bookmark marks an instant or a height
  on a curve, and a run halts when it reaches one. The branch opens with the
  trunk's bookmarks. A bookmark added after the fork belongs only to the run it
  was added to.
- **The time frame.** Both runs count time from induction. The chart anchors
  both to induction rather than to either run's own start, so the two traces
  are compared at the same instants.

**After the fork, a difference between the two runs is caused by the settings
that differ between them, and by nothing else in the model.** Taking a branch
leaves the trunk unchanged. The branch's record of setting changes opens with
copies of the trunk's changes at the fork, and holds none of the trunk's
earlier changes. A reset branch keeps those copies and can record the learner's
settings after them (§ "Reset behavior"). So everything that either run records
after the fork is what its learner did to it.

**For developers.** The architecture document describes a branch's structure
(`docs/ARCHITECTURE.md` § "What a branch is, and what it shares with its
parent").

The roadmap leaves a third run and a comparison of two branches out of scope
for v0.5.0 (`ROADMAP.md` § "Explicitly out of scope for v0.5.0"). A test checks
that another branch is refused while two runs are shown
(`test_a_second_fork_is_refused_while_two_runs_are_shown`).

The code enforces what the two runs share as follows:

- The reference adult is stored in
  `src/anesthesia_sim/data/patients/reference_adult.json`. Two tests check that
  a branch carries the trunk's patient and agent
  (`test_a_branch_is_the_agent_and_patient_its_parent_was`,
  `test_a_case_s_branches_carry_the_trunk_s_agent_and_patient_at_the_fork`).
- A branch refuses an agent change outright (`set_agent`,
  `test_a_branch_cannot_change_its_agent_out_from_under_the_case`). On the
  trunk, the agent selector is locked
  (`test_the_trunks_selector_is_locked_while_two_runs_are_shown`). Changing
  the agent begins a new run (§ "Agent-change behavior"), so an agent change
  during a comparison would end one of the two runs rather than vary it.
- Exact reproducibility is not guaranteed across model versions or platforms
  (§ "The reproducibility guarantee"), and the two runs of a comparison always
  share one model version and one platform.
- The circuit volume is a build-time parameter with no live setter
  (`test_the_circuit_volume_is_a_build_time_parameter_with_no_live_setter`).
  It is applied to a branch before any state is.
- A branch carries the trunk's step in its resume point (`ResumePoint`). A test
  checks this and the refusal of a fork between two steps
  (`test_a_branch_steps_to_where_its_parent_stepped`). Exact reproducibility is
  not guaranteed between runs at different steps (§ "The reproducibility
  guarantee"), so carrying the step keeps a comparison within the guarantee.
- A test checks the replayed settings
  (`test_a_branch_inherits_its_parent_s_settings_at_the_fork`).
- A test checks that a branch carries the trunk's bookmarks
  (`test_a_branch_opens_carrying_the_marks_of_the_case_it_continues`).
- Each column of the chart stands for an instant at which it draws a value. A
  test checks that a branch uses the trunk's columns
  (`test_a_branch_is_drawn_on_the_same_columns_as_the_run_it_forked_from`). A
  fork at a bookmark adds exactly one column, the fork itself
  (`test_a_bookmark_branch_draws_one_column_its_parent_does_not_and_it_is_the_fork`).

In the code, a run's record of setting changes is its control timeline. Two
tests check what a branch's control timeline opens with and that forking leaves
the trunk untouched
(`test_a_branch_opens_with_only_the_change_it_runs_under_in_its_timeline`,
`test_forking_leaves_the_trunk_untouched`).

Each entry that a reset branch keeps states a setting in force from the fork
on, so a reset does not change what can cause a difference after the fork.

Building the case twice instead of forking would leave the two runs differing
by everything that was not reproduced identically, and a learner could not see
which differences they had caused.

### The shared history is identical by construction, not by measurement

**Before the fork, a branch and its trunk are exactly equal.** The branch
repeats the trunk's arithmetic, operation for operation, at every instant they
share. This holds for every branch the program builds
(§ "What this requires of a branch"). There is no error to allow for, and none
is shown.

**Exact equality applies to the values the model computes, and not always to
the values the chart draws.** Where the fork was at a setting change, the two
drawn traces agree exactly at every point they share. Where it was at a
bookmark, they can differ by a rounding error that is orders of magnitude too
small to move any displayed digit (§ "The canonical evaluation rule",
§ "Displayed precision").

**Equality before the fork sets no bound on anything after it.** Only the
settings and the model decide how far the two runs diverge, in which direction,
how quickly, and whether they converge again.

**For developers.** A keyframe is the state at the instant a setting change
took effect, and a segment is the stretch of a run between two changes
(§ "The run is that record, and every state is derived from it"). A branch's
run definition carries the trunk's own keyframe. It forms each propagation interval as the instant minus the opening
of the segment that holds the instant. The branch repeats the trunk's
arithmetic because both use the same keyframe and the same subtraction.
§ "What this requires of a branch" sets this out as a rule with two conditions,
and says which condition a fork at a bookmark relaxes.

**For developers.** Exact equality rests on this construction, and the tests
only detect when it breaks. Two
tests cover a fork on a keyframe and a fork between two keyframes
(`test_a_fork_opening_from_a_keyframe_reproduces_its_parent`,
`test_a_fork_opening_between_two_keyframes_reproduces_its_parent`). Two more
test both through the controller, at case instants and at drawn columns
(`test_a_branch_reproduces_its_parent_at_every_instant_they_share`,
`test_a_bookmark_branch_and_its_parent_agree_at_every_column_they_share`).
Over the 251 shared columns that the last of these tests compares, the worst
difference between a branch forked at a bookmark and its trunk was 5.3e-16 on
2026-10-26, a rounding error from the order of the floating-point operations.
Before `PL-T5NJ` put the columns on whole hundredths of a second, it was 2.7e-15
over 240 columns, the figure § "The canonical evaluation rule" tabulates. A
branch that restarts at the fork would not reproduce its trunk
(`test_a_fork_opening_at_the_instant_it_was_taken_does_not_reproduce_its_parent`).
No branch that this program builds takes that route.

### Neither run is a prediction for a patient

**This model has one patient, and no variability around it.** No equation takes
a covariate that distinguishes one patient from another, such as weight, age,
sex or body composition. Nothing scales a volume, a flow or a coefficient from
such a covariate (§ "Known limitations"). The two runs are two trajectories of
*one* modelled patient under two managements. They are not two patients, not
two samples from a population, and not a range.

**So a difference between the runs is a property of the model, not an expected
clinical difference.** It carries no interval, spread or distribution, because
the model contains nothing that could supply one. It does not say how much two
patients managed those two ways would differ, how far a real patient would
depart from either curve, or how likely either management is to reach a given
state by a given time. It says what these equations do under these two
managements, within the limits that § "Supported input ranges" and
§ "Supported run length" declare, and with the fidelity that § "Published
wash-in and elimination validation test" establishes.

**A branch that differs in cardiac output is still not a second patient.** This
is the case most likely to be misread, because cardiac output is both a setting
the learner can adjust during a run and the quantity by which a clinician most
readily tells one patient from another. Dialling it changes this patient's
circulation. Its effect on uptake is a real property of these equations, and
setting it differently in the two runs is legitimate. But a patient who differs
in cardiac output differs in compartment volumes too, and this model keeps
those volumes fixed. So changing cardiac output alone shifts every tissue time
constant $`V_i \lambda_{i:b} / Q_i`$ in a direction that flow and volume
changing together need not take. § "Known limitations" gives the size of the same
artifact for a cardiac output scaled to body weight with the volumes kept fixed,
and the same arithmetic applies here.

**Do not read a comparison as "low flow woke this patient twelve minutes
sooner."** Three separate things are wrong with that reading, and only the
first is about variability.

- **"this patient"**: there is one modelled patient and no population around
  it, so nothing on screen is about a patient at all.
- **"woke"**: this model has no effect-site compartment and defines
  $`F_a \equiv F_A`$ (§ "Model boundary"), so it has no measure of
  responsiveness in which two runs could differ. The nearest thing the chart
  shows is the vessel-rich trace read against the MAC-awake band. That band is
  one standard deviation either side of a published population mean, and it is
  not a prediction for the patient on the screen (§ "MAC-awake as a chart
  reference").
- **"twelve minutes"**: a duration read between two curves inherits every
  limitation of the model that drew them, and this model does not claim to get
  a difference in emergence time right to the minute (§ "Known limitations").

### What the interface may assert about a comparison

The interface may mark the fork. It may name the run that each displayed value
and each record of setting changes belongs to (§ "Reasonably foreseeable
misuse, and the hazards the presentation carries", the row on reading one run's
value as the other's). And it may show the two standing disclaimers beside the
readouts, one on interpretation and one on use.

**It must not draw the conclusion for the reader.** That rules out a
difference trace between the two runs, a score or ranking of one management
against the other, a time-to-wake-up figure, and a sentence stating what the
comparison shows. As checked on 2026-09-21, the interface draws none of them.
Each would state a conclusion that the model does not support. A qualifier
beside any of them would not repair that, because the reader would act on the
conclusion and not on the qualifier. § "MAC-awake as a chart reference" makes
the same argument about a wake-up readout.

**Two features of the interface come close to drawing a conclusion, and
neither does:**

- A run halts on the step that crosses a bookmark, and the clock then shows
  where that run actually stopped (§ "Halting on a marked crossing"). Two runs
  halted at one marked height therefore show two instants. Each is an instant
  that its run *reached*, not a predicted time for an endpoint that the run has
  not reached.
- Each run's record of setting changes states what that run's learner did, not
  a difference between the two runs. That is why the record's heading names its
  run rather than the comparison.

**For developers.** The fork's mark is `BRANCH_POINT_LEGEND_LABEL` in
`src/anesthesia_sim/app/dashboard_frame.py`, and the two disclaimers are
`INTERPRETATION_DISCLAIMER_TEXT` and `USE_DISCLAIMER_TEXT`. The check on
2026-09-21 covered `src/anesthesia_sim/app/dashboard_frame.py`,
`src/anesthesia_sim/app/chart_frame.py` and
`src/anesthesia_sim/app/qt_chart.py`.

A difference trace would mislead even before the fork, where the two runs are
identical. If the fork was at a bookmark, the trace would show a tiny nonzero
difference there instead of zero, and a reader would take that for a
disagreement about the case.

## Interface boundary

The interface shows the model's results and controls the run, but it does none
of the model's calculations. It may:

- display values;
- convert fractions to percent;
- collect user settings;
- issue Start, Pause, and Reset commands;
- halt a run, and record why, when the model stops with an error;
- report a value that the model refused; and
- display mass-balance status.

Under the conditions set out below, it may also:

- draw the run's states over a window of time, computed by the model at
  instants that the interface chooses;
- choose how wide a window of the run the chart shows, and how its time axis
  is ruled;
- draw only some of the compartment traces, when the user asks;
- draw a published clinical constant as a chart reference, at a height that
  the chart's own axis gives meaning to;
- form the ratio of two modelled fractions where this document names it as a
  displayed quantity;
- declare where one adjustment of a control begins, so that the run's record
  of its inputs can be read as the user's actions that produced it; and
- choose how many simulation steps to take at a time, so that a run can be
  played faster than real time.

It must not:

- calculate uptake, partitioning, tissue flow, mixed-venous return or mass
  balance;
- integrate the model's equations;
- correct negative stores;
- change the model's state directly;
- continue a run past a step that the model could not complete;
- take extra simulation steps to catch up when it falls behind real time, or
  otherwise let elapsed real time decide how many steps a run takes;
- change the simulation step size in response to a playback control, or
  advance a run at a rate other than the one it displays;
- let a display choice, such as the chart's window width, change what a run
  recorded, or present a chart window narrower than the run as though it
  showed the whole run;
- present a run halted by a failure as though it were paused;
- discard a run that holds recorded state without stating what will be lost
  and asking the user to confirm, as "Agent-change behavior" requires;
- display a concentration at a finer resolution than "Displayed precision"
  justifies, or show a value that the model does not resolve as though the
  model asserted it; or
- predict when the simulated patient would wake, or display a
  time-to-awakening figure of any kind (§ "MAC-awake as a chart reference").

**Every trace and every readout names the substance it shows.** A chart trace
shows one compartment of one substance, because a compartment fraction means
nothing without the substance it is a fraction of. Today a run contains one
substance, its agent, and changing the agent starts a new run rather than
adding to this one. A trace draws only the substance it names. The readout row
names the substance itself, so the user need not carry it over from the agent
selector. A compartment value and the trace beside it always name the same
substance.

**Every point that a chart trace draws is a state the run reached, at the
instant where it is drawn.** The interface never interpolates, smooths,
averages or otherwise makes up a plotted value. A trace need not draw every
instant, because the run advances one step every 0.1 s of simulated time, more
often than a chart can resolve. The instant that the numeric readouts show is
always drawn, so the end of a trace always agrees with the readouts beside it.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

**What the chart draws.** The model computes each point that the chart draws
from the run's definition, which gives the run's state at any instant directly,
by formula. No stored series of values lies behind a trace, so none can disagree
with it.
The chart draws the run's state at one instant for each pixel boundary of its
widest plot, and at never fewer than 150 instants. When a plot becomes wider,
after the user resizes the application window or drags an area's border, it is
redrawn at its new width on the next screen update, whether the run is running
or paused. Two rules set where the drawn instants fall:

- **The drawn instants lie on a grid that starts at the case's time zero.**
  A run branched from another therefore draws at the same instants as the run
  it branched from, and the two can be compared point for point. Each drawn
  instant falls on a whole hundredth of a second, so the hover readout can give
  the exact time of the state it shows.
- **Every control change inside the window is a drawn instant.** Between
  control changes each compartment's value is a sum of exponentials, with
  bounded curvature and no hidden transients, so every sharp feature of a run
  is at a control change. A grid that stepped over one would draw a straight
  line through the very instant that the user is looking for. The point drawn
  there is the state that the run's definition stores for that instant. The
  chart therefore shows every control change exactly, to the last digit the
  readouts display.

**Between control changes, the drawn line is never further from the run than the
time that one pixel of the plot spans, except at a peak or a trough.** It passes
through the run's exact state at every drawn instant, and drawn instants are no
more than a pixel apart. The only exception to that spacing is a one-minute axis
more than 6000 px wide, where drawn instants a hundredth of a second apart span
more than a pixel. Where the run only rises or only falls between two drawn
instants, the run and the straight segment drawn between them cross every level
inside the same pixel. This one-pixel guarantee is in time, not in percentage
points. Where a trace is steep, the run can change by many percentage points
within one pixel of time. No display shows a value between drawn instants, the
hover readout included (§ "The chart's hover readout").

The straight segment between two drawn instants starts and ends on the run's
curve, but can lie above or below the curve in between. The table gives that
vertical gap at the middle of a segment, in percentage points (pp), computed on
a plot 1 000 px wide. A time base is a window width that the chart offers, and
the spacing between drawn instants is that width divided by 1 000.

| Time base | Spacing | Sevoflurane 2% to 4%, worst trace | Desflurane 0% to 12% to 6%, worst trace | Desflurane, alveolar |
| --- | ---: | ---: | ---: | ---: |
| 15 min | 0.9 s | 0.0004 pp | 0.0025 pp | 0.0025 pp |
| 1 h | 3.6 s | 0.0052 pp | 0.032 pp | 0.032 pp |
| 4 h | 14.4 s | 0.048 pp (circuit) | 0.28 pp (circuit) | 0.21 pp |
| 12 h | 43.2 s | 0.21 pp (circuit) | 1.21 pp (circuit) | 0.26 pp |

<!-- provenance: app/chart_time_base.py SELECTABLE_TIME_BASE_FLOOR_S = 900 -->

<!-- not-restated: 2 %, 6 % -->

The gaps grow with the spacing, so a narrower plot has larger gaps and a wider
plot smaller ones. They bound the error in a trace's *shape* inside one pixel
column, never in a displayed value.

**Between two control changes, the drawn line can miss the top of a peak or
the bottom of a trough.** Because the alveoli and the venous blood keep filling
for a moment after the vaporizer is turned down, the run can peak between two
drawn instants, above both drawn values. Over five simulated runs, the largest
gap at a peak or a trough on any time base is 0.0028 pp, on the mixed venous
trace at the desflurane dial-down on the twelve-hour time base. That is less
than a third of the readout's resolution of 0.01 pp.

The values that a chart draws are for display only, and the program prevents
their use for anything else (§ "The canonical evaluation rule" above).

**The user chooses which compartment traces are drawn and how wide a window
of the run the chart shows, and neither choice changes the run.** The two
choices change no model state and nothing in the run's definition, and
identical inputs still produce identical results. The window width therefore
sits outside "Runtime controls", with the other interface settings.

A user cannot compare two compartments while four other lines cross them, so
the interface may draw only some of the six traces. When it does:

1. The numeric readouts still show every compartment's concentration
   (§ "Minimum displayed outputs"). A chart
   with two curves is a chosen view of six modelled compartments, not a model
   with two.
2. The display states, for every compartment, whether its trace is drawn. A
   legend entry for a line missing from the plot claims something about the
   run that the run does not support.

A case runs for hours, but the moment a learner is most likely to be watching
lasts minutes, and no single window width serves both. Two conditions apply to
the width that the user chooses:

1. The width is fixed by the selection, never by how long the run has been
   going. A window that grew with the run would change the slope of every trace
   while the underlying rates stayed the same.
2. A setting that claims to show the whole run shows all of it, at every
   length. A narrower window labelled as the whole run misstates what the user
   is looking at.

See § "The chart's time base" for the widths, the ruling and the labels that
meet these conditions.

A **chart reference** is not a trace. It draws a published constant, not a
state of the run, so the rule that every drawn point is a state the run reached
does not apply to it. Instead, it must be labelled. Its label states the value
and the divisor it was drawn from, and names the compartment it is to be read
against. The reference differs in kind from a compartment trace by its type of
mark, not by colour alone. A user with no reason to think otherwise takes an
unlabelled horizontal line for a modelled quantity, and so mistakes a measured
value for a modelled one.
See § "MAC-awake as a chart reference".

A **displayed ratio** of two modelled fractions is a trace, so the rule that
every drawn point is a state the run reached applies to it. Each point is formed
from one substance's two fractions in one state of the run, at the instant
where it is drawn. A ratio also needs a stated **domain**: the states of the run
for which it is drawn. A ratio of two modelled values can be undefined, when its
denominator is zero, or can fall outside what the plot claims to show. In
neither case may the interface substitute a number. Four rules follow:

1. A drawn instant outside the domain gives no point, rather than a clamped,
   extrapolated or defaulted one.
2. The trace breaks where the domain does, and does not join across the
   instants it skipped, because a join would draw values the run never
   produced.
3. The display states which two quantities the ratio is of, in the terms this
   document uses for them.
4. Where the trace is absent, the display says at which boundary it stopped,
   because otherwise an absent trace looks like a run that stopped.

See § "F_A/F_I as a displayed ratio", the only such quantity today.

A **control mark** shows the instant on the time axis at which the user moved
a control. It draws no value and says nothing about the vertical axis, so the
rule that every drawn point is a state the run reached does not apply to it.
Instead, it must be labelled. It differs in kind from both a trace and a
reference, by something other than colour. The display identifies it as a
record of a user input, not of anything measured or modelled, and states which
control moved and to what setting. A bare mark says only that something
happened, and invites the user to supply their own explanation for the change
in the curves beside it.
See § "The control-input timeline".

Declaring where one adjustment of a control begins concerns the input device,
not the model. A slider reports continuously while it is dragged, so only the
interface can tell one turn of a control from two. The declaration records no
value. It must not change the simulation state, what the run records or what
the model computes.

**A playback rate is a number of steps, never a step size, and it must be on
screen.** Real time is too slow to watch the two compartments that make uptake
and distribution worth teaching. At the reference settings, sevoflurane's
muscle group has a time constant of about 135 min, and fat one of about 42 h.
The interface advances the run in ticks, one every 0.1 s, and at real time each
tick takes one step. To play a run faster, it takes more steps per tick, under
three conditions of different kinds.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

The first condition is arithmetic. The interface refuses a rate that does not
come to a whole number of steps per tick, because rounding it would give either
a step of a different size or a run advancing at a rate other than the one
displayed. So faster playback stays within "The reproducibility guarantee":
identical inputs still produce identical run definitions, and two learners
comparing the same case at different speeds are comparing the same arithmetic.

The second condition is control resolution, and it limits that last claim. The
two learners are comparing the same *case* only if neither of them touches a
control. The same slider moves made at two rates land at two different
simulated instants and produce two different runs. The runs differ because the
inputs differed, not because the arithmetic did. § "Supported simulation step" gives the grid of
tick boundaries for each rate, and how far a delay of one tick can shift a
displayed compartment. It also gives the route that is exact at every rate:
pause, change the setting, then resume.

The third condition is human factors, and it is why the rate is a required
display rather than a preference. A rate is a mode. A clock is easy to misread
at a glance when it advances at sixty times real time beside numbers that look
like a live case. So the rate is shown wherever simulated time is shown, at
every rate, including real time. If the label were absent at 1×, its presence
would become the signal, and a user would have to be taught that convention
instead of reading the rate off the screen. The rate states only how fast the
interface is playing the run. It implies nothing about the model or the
patient, and it is not a second reading of the clock beside it.

**The rate label shows the rate that was set: the multiple of real time chosen
with the playback control.** The interface computes the steps per tick from
that setting, so the label always agrees with the number of steps each tick
takes. The simulated clock is exact at every rate, because simulated time is a
count of the steps taken. Whether the run keeps pace with real time depends on
the computer. When the computer cannot run a tick in time, the tick is lost,
and no extra steps make it up. The **delivered rate** is the set rate times the
fraction of ticks that ran. In a measurement on 2026-09-27, every rate from 1×
to 300× delivered 99.0 to 99.9% of its setting over 8 to 30 s, and the tick
period stayed at 100 ms to within 4 ms. On a computer that loses ticks, the run
plays slower than the label says, and nothing on screen shows the delivered
rate.
<!-- not-restated: 100 ms -->

**For developers.** A chart draws from a window of states (`DrawnWindow` in
`app/run_series.py`), one for each instant that a frame plots. The controller
evaluates them from the run's definition (`SimulationController.drawn_window`,
`core/run_definition.py`). Keeping no stored samples of the run is a decision
(project owner, 2026-09-05, recorded here when the sample store was deleted).
Each state carries its substance's six compartment values, as fractions of one
atmosphere, under stable identifiers (`RecordedQuantity`). A trace addresses one
of them as a substance-and-quantity pair (`RecordedSeries`). When a frame asks
for a substance that the run does not contain, it fails rather than drawing
whichever substance is in the run. The window is keyed by substance rather than
by six named fields, because six flat names can describe only one substance. A
second substance would then need six more names, or values pooled with the
first substance's, and pooled values show a correct number under the wrong
label.

A frame is rendered from the running agent's state at one instant
(`SimulationSnapshot` in `app/controller.py`), which carries the six compartment
values as flat named fields. This difference from the window is a decision, not
unfinished work (`PL-TCD1`, 2026-09-13). Unlike the run's definition, a snapshot
is never stored, never compared with a later run and never read back, so giving
it a second substance later adds a field and invalidates nothing already
written. The roadmap's test for a change like this is "whether retrofitting
invalidates recorded runs or merely adds a field"
(`ROADMAP.md` § "Designed for forking"). By that test, the roadmap declines
per-compartment agent amounts in the snapshot. The snapshot gains the
per-substance mapping with `ROADMAP.md` Phase 1, which generalizes the patient
to N simultaneously present substances. The six fields travel with the
`agent_id` and `agent_display_name` they belong to, as `agent_mac_percent`
travels beside the concentrations it scales. The controller exposes immutable
snapshots, and immutable windows onto the recorded run, rather than mutable
compartment objects.

**For developers.** The two rules for where drawn instants fall are
requirements of this document, not optimisations. A function sets the number of
drawn instants (`chart_columns` in `app/chart_frame.py`, `PL-GS3R`). The spacing
is the time base divided by that number. It is rounded down onto whole
hundredths of a second, and onto whole tenths of a second where that adds at
most 10% more instants (`grid_spacing_s` in `app/chart_time_base.py`,
`PL-T5NJ`). Rounding down keeps each segment within a pixel of time, except on
a one-minute axis more than 6000 px wide. Where the spacing is 1 s or more,
rounding onto tenths puts each drawn instant on a time that the clock also
shows. The minimum of 150 drawn instants is the fixed count the chart used
before, kept because no smaller count has been measured. A plot is redrawn when
it grows wider than the width its frame was sampled for (`resample_owed`,
`PL-9LNF`).
<!-- not-restated: 1 s -->

The grid sits at absolute multiples of the spacing, so a window that follows the
run keeps every drawn instant it had and gains at most one, and a steady trace
is not redrawn on every frame. A grid anchored to the viewport would move on
every scroll and resize, and rewrite the whole chart on every frame. A grid
anchored to each run's own start put a branch forked at 55.3 s on 55.3, 65.3,
75.3 … while the run it branched from drew 0, 10, 20 ….

Each control change is a drawn instant because the run has a kink there: the
derivative of the circuit fraction is discontinuous. Without a drawn instant
there, the interpolation error at that instant would scale as O(h), in
proportion to the spacing h between drawn instants, rather than as O(h²), in
proportion to its square. The stored state drawn at a control change is a
keyframe, not one propagated from an earlier instant.

The pixel in the one-pixel guarantee is a logical pixel of the plot, the
resolution at which the axis is ruled and labelled.

The one-pixel guarantee (`PL-GS3R`, decided 2026-09-14) replaced a fixed budget
of 150 drawn instants at every width. Across the twelve-hour time base, that
budget spaced drawn instants 290 s apart, and it drew the steep early wash-in
below the run. For sevoflurane 2% to 4% at the fastest supported settings
(FGF 10 L/min, V_A 12 L/min, Q 10 L/min), the line fell below the run by
0.53 pp on the alveolar trace (0.26 MAC) and 0.89 pp on the circuit trace. For
a desflurane overpressure induction, 0% to 12% then 6% at 600 s, it fell below
by 3.8 pp on the alveolar trace (0.64 MAC) and 5.5 pp on the circuit. Keeping
every trace within the readout's resolution everywhere would instead need a 2 s
spacing on the desflurane case: 21 601 drawn instants across twelve hours. No
hardware this project has measured can draw that many inside its frame budget.
All of the old budget's error lies within 1 800 s of a dial change, and beyond
that the 290 s spacing itself is within 0.0024 pp. These values were computed
on 2026-09-14 against the run's exact state every 0.1 s, the step the run
advances by, over five twelve-hour runs built by formula.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10 -->
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- not-restated: 2 %, 6 % -->

The five simulated runs for the gap at a peak or a trough were sevoflurane
2% to 4% and 4% to 0% at the fastest settings, the desflurane case at the
fastest settings and at slow settings (FGF 0.5 L/min, V_A 2 L/min, Q 2 L/min),
and the reference adult at 1 to 2 MAC. A test checks that the gap at the peak
in the desflurane dial-down case stays below half the readout's resolution
(`tests/unit/test_run_definition.py`).
<!-- not-restated: 2 % -->

Bounding the gap at a peak or a trough by the readout's resolution is
deliberate. It does not break the rule of § "Supported simulation step" that the
readout's number of decimals must not feed back into the model. That rule is why
the step tolerance and the supported ranges are stated in absolute percentage
points. This bound is about the chart, in the units that the readout shows. The
two-decimal readout itself follows from the model's fidelity
(§ "Displayed precision"): one published SD of a partition coefficient displaces
a compartment by 8.7e-4 to 6.8e-2 percentage points.

The one-pixel guarantee works in pixel columns, as Jugel, Jerzak, Hackenbroich
and Markl do for recorded data: they prove that a line chart is fixed by at
most four values per pixel column (M4: A Visualization-Oriented Time Series
Data Aggregation, *Proceedings of the VLDB Endowment* 2014;7(10):797-808).
Their method of selecting values from a store is not used. The run is
evaluated at the drawn instants, and a control change is always one of them
whatever the pixel width. A selection of recorded extremes could not guarantee
that (`PL-4RBD`).

The code enforces a displayed ratio's domain in one place.

The steps per tick are derived in `app/playback.py`, and a precise timer starts
each tick (`PreciseTimer`, `RunView.step_tick`). A count of more than 1 000
steps per tick is refused (`PL-T6P0`). A tick takes all of its steps before the
interface can respond, so a count with no bound would freeze the application
with no error. The bound is set by time: one step took about 53 microseconds
when measured on 2026-10-26, so 1 000 steps take about half of the 0.1 s tick.
A tick lasts as long in real time as one step does in simulated time, so the
fastest offered rate, 300×, takes 300 steps per tick whatever the step size.
<!-- provenance: app/playback.py MAXIMUM_STEPS_PER_TICK = 1000 -->
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

The 2026-09-27 measurement used the real dashboard on the offscreen platform,
with both timers running. Showing only the set rate is a decision (project
owner, 2026-09-27, ratified, over qualifying the label as "up to 300×", which
trades a precise claim that is true for a vague one, and over building the
disclosure now). A proposed change would show the delivered rate beside the set
one when fewer than 95% of ticks run over a 50-tick window (`PL-2NYN`). If a
delivered rate below 99% is measured on the owner's own machine, the decision
is reopened (`PL-SQJ1`).

## Minimum displayed outputs

The interface must show the following outputs. The tests in brackets after each
entry check that the output is drawn on the display.

- simulated time (`test_refresh_view_formats_every_concentration_metric`,
  `test_the_clock_panel_reads_in_the_chart_axis_form_past_an_hour`);
- the playback rate that is set, as a multiple of real time. It is drawn
  wherever simulated time is drawn, and at every rate, including real time
  (`test_the_playback_rate_is_drawn_under_the_clock_it_governs`). A paused,
  reset or halted run still shows the rate it would play at. The status word in
  the row of playback controls says whether the clock is moving. See
  § "Interface boundary" for what the rate does and does not assert;
- how much simulated time the chart is showing, and whether that span was the
  reader's choice or fits the whole run so far
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
  `test_refresh_view_reports_failed_agent_accounting`);
- every concentration above, including the delivered concentration, also shown
  as a multiple of the running agent's 1 MAC, with that agent's 1 MAC in percent
  stated on the display (`test_every_compartment_is_readable_in_mac_multiples`,
  `test_the_dial_is_readable_in_the_unit_its_compartments_are`,
  `test_the_display_names_the_mac_the_readouts_were_divided_by`). See
  § "MAC multiples as a display unit" for what the multiple asserts, and for
  why both units are shown rather than one;
- the running agent's population MAC-awake, drawn on the chart as a band. The
  band was derived from two numbers, and its label gives both: MAC-awake as a
  fraction of the agent's 1 MAC, and that 1 MAC in percent. The label also names
  the trace to read the band against. A visually distinct line on the chart
  marks the agent's nominal 1 MAC
  (`test_the_band_states_the_fraction_and_the_divisor_it_was_drawn_from`,
  `test_the_interface_says_which_trace_the_band_is_read_against`,
  `test_no_trace_dash_is_as_wide_as_the_one_mac_reference_line`). See
  § "MAC-awake as a chart reference" for what the band asserts and what it does
  not, and for why no time-to-wake-up figure is displayed anywhere in the
  interface;
- every setting changed during the current run. Each change is listed with the
  simulated time at which it took effect, the control and its old and new
  values. The chart marks each change at that time
  (`test_the_list_states_what_was_changed_and_to_what`,
  `test_a_recorded_change_is_marked_on_the_chart_at_its_own_time`). See
  § "The control-input timeline"; and
- $`F_A/F_I`$ over the run, on a dimensionless axis of its own. The plot is
  labelled as a ratio against the modelled inspired concentration, not against
  the vaporizer dial. It carries the marks for setting changes, has a line at
  the equilibrium that the curve approaches, and states where the ratio is not
  defined
  (`test_the_wash_in_axis_is_ruled_at_quarters_and_the_window_is_the_chart_s`,
  `test_the_wash_in_plot_says_what_its_denominator_is`,
  `test_the_wash_in_trace_draws_nothing_before_agent_reaches_the_circuit`). See
  § "F_A/F_I as a displayed ratio" for the part of the run over which the curve
  is drawn, and for what it does and does not assert.

The six compartment concentrations above are requirements on the **numeric
readouts**, not on the chart. The reader may show and hide the chart's
compartment traces (see § "Interface boundary"), but a required value must stay
on the display when its trace is hidden. The MAC-awake band, the 1 MAC line, the
marks for setting changes and the $`F_A/F_I`$ plot are requirements on the chart
itself, and the reader cannot hide them. Of the chart entries, only the span of
simulated time is the reader's choice, and no particular span is required.

Arterial concentration is **not** in this list. In this model the arterial
fraction is defined as the alveolar one, $`F_a \equiv F_A`$ (see
§ "Model boundary"). A separate arterial readout would show the alveolar number
a second time under another name, as though the model computed an arterial
value of its own.

The alveolar readout is labelled "Alveolar", with "end-tidal-equivalent" on the
line below. It shows the concentration in the model's one well-mixed alveolar
compartment, which is the value a monitor's end-tidal reading estimates in a
real patient. The model has no dead space, airway sampling delay or shunt, so
this readout is not a simulated end-tidal measurement.

**No difference readout is required, and none may be added without a stated
sign convention.** The arithmetic difference of two alveolar fractions has no
conventional clinical reading, because clinicians reason about depth in MAC
multiples and time to target. Displaying it would imply a standard meaning that
it does not have, which § "Displayed precision" rules out on grounds of
interpretability. The chart already shows the comparison continuously, on the
axis the reader is looking at.

Telling a halted run from a paused one is a required output. Both stop the
numbers advancing, and under § "Step atomicity" both leave the simulation in a
state that the reader can trust. A paused run continues when the reader asks,
but a halted run cannot. A halted run shown as "Paused" would offer a Start
control that fails at the first simulation step, and would present a stopped
trajectory as one still in progress. That is the mode confusion that this
document's interface rules exist to prevent. A display that merely freezes, with
no change of state at all, is worse still.

Showing which agent is running is also a required output. A correct
concentration attributed to the wrong agent is a display failure, and the same
number means a different clinical depth for each agent (§ "MAC multiples as a
display unit").

**For developers.** Testing the display matters because a required output can
stay in the simulation snapshot (`SimulationSnapshot`) long after the widget
that draws it has gone. Three entries have no field in the snapshot at all. The
playback rate and the chart's span are view settings, and $`F_A/F_I`$ is
computed when the plot is drawn.

**For developers.** The names in parentheses after each entry are the tests
that check it. The documentation check reads this list (§ "How this document is
held to the tree"), and fails when an entry names nothing that backs it, or
names a test that does not exist.

### Every value and what qualifies it come from one step

Where the screen shows a value with what qualifies it, both come from a single
simulation step. A test checks each of these groups:

- the readout cards, with their heading and 1 MAC line;
- the dials, with the delivered line;
- the accounting verdict, with the totals it judges.

A run stops when it fails or reaches the supported run length, the longest run
the model allows.

**If an agent change or a Reset starts a new run, and the new run stops before
the screen is redrawn**, the last values drawn belong to the discarded run. Each
card therefore withholds its percent and ×MAC number ("—%", "— ×MAC") under the
new run's heading and 1 MAC line. The clock reads "—", and the accounting panel
shows no verdict or amounts. The banner says that the readouts are withheld and
that the chart still shows the discarded run.

**After a step fails its accounting check**, the accounting panel shows the
check: "Validation failed", with that step's totals. The run stops, and the
model undoes the step, so the run's own accounting passes again. The banner
names the panel as the one exception to "the values shown are the last
completed step". If the screen is not redrawn after the failure, the panel
shows the same check from the run's record.

**A dial moved on a stopped run is refused** before anything is applied, and
springs back to the run's setting. The model computes no step after a stop, so
the new setting would sit beside values it never produced, and the run's record
would claim a change that never acted on the patient. A run can also fail on the
first step after a setting was accepted. Then none of its values was computed
under that setting either.

The banner states the refusal and the way out: Reset, which keeps every setting.
At the supported run length, a branch is a second way out: a new run from an
earlier instant, with each dial at its setting from that instant. The banner
names a branch only when one can be taken. It names Reset alone on a dashboard
with no branch control, and while the run is compared with another, because
comparison locks the branch control.

**For developers.** For each scenario, the test requires every screen element in
a group to describe the step that the scenario names. It also requires every
other screen element to be listed with the reason it belongs to no group.

### Naming the run in a comparison

While two or more runs are drawn, each of these places names its run in text:

1. Each run's own readout panel (§ "Minimum displayed outputs").
2. The chart's hover readout. With one run under the pointer, its name is on
   the readout's first line (§ "The hover and the run it belongs to"). With
   several, each value line gives its run's name. The readout reports every run
   inside the hover radius, so a small pointer movement cannot swap which run is
   read (§ "Where more than one trace answers").
3. The three advisory lines inside a chart: the wash-in state, the off-scale
   notice, and the count of control changes the chart could not mark. They
   stack one line per run.
4. The headings of the two record panels: the agent-accounting validation in
   the sidebar, and the control-change record ("What was changed during this
   run") in the right column of the always-shown region of the window. Each
   record stacks one whole panel per run, so a run's name is in its panel's
   heading and moves with that panel.
5. The notice banner, between the runs' control rows and their readouts. Both
   runs use this one place, and an empty banner is hidden and takes no room. A
   banner's position therefore does not show which run it belongs to.
6. The heading over each run's compartment schematic, taken from the name on
   the run's own panel.
7. The heading over each run's agent cost panel, in the same way.

With only one run drawn, the hover readout, the chart's advisory lines, the
sidebar panel headings and the banner show no run name.

Without the run names, a learner could misread a comparison in three ways:

- One run's F_A/F_I could be read as the other's, or its off-scale notice could
  be attributed to a run whose traces are all inside the axis.
- If read as the other run's, the control-change record says that run received
  an intervention it never got.
- If read as covering the whole dashboard, a halt banner says both runs are
  frozen. "The values shown are the last completed step" then claims both runs
  stopped at a failed step when one is still going. "The simulation is
  unchanged and still running its previous setting" is false of the run that
  accepted the setting.

**The run is named in text, not by colour or position.** Colour already
identifies the compartment in both modes, so it cannot also identify the run.
The worst contrast between two compartment traces is 1.01:1, against the 3:1
required (§ "The six compartment traces"). The chart therefore shows the run by
line width instead (`PL-HLD5`). Text has no equivalent of line width. Position
alone fails a reader who looks away and back, which is the stale-context failure
this requirement exists to prevent.

**A run's name gives its identity, not its place** (`PL-7Z84`). Each run placed
in a session gets a number, counting from 1, and its name is "Run" followed by
that number. A run keeps its number for as long as it holds its place on screen.
Branches fork from a run called the trunk, which holds its place from when the
dashboard opens. A branch holds its place from its fork until it is dropped.
Resetting a run and changing its agent both keep the number, because both start
the run afresh in the same place, after any confirmation that
§ "Agent-change behavior" asks for. No number is given out twice in a session,
so a branch taken after a dropped one is "Run 3", never a second "Run 2". A
Workspace can be pinned to a run, so that it shows that run. If a name were
reused, a Workspace pinned to the dropped run would find a new run of that name
and show its values as the dropped run's.

A view shows its run's name whenever a reader could mistake its values for
another run's: while another run is drawn anywhere in the application, while the
view is pinned to a run, and always in a window broken out of the main one.
Break-out windows are not built yet, so the dashboard is the only window that
draws a run. In this version, therefore, the names appear when two runs are
compared, and a pinned Workspace shows its run's name in the header of every
area (`PL-2KXB`).

**A Workspace pins a run by its identity, and says when that run is absent**
(`PL-WV9K` Q6). The pin is saved with the Workspace as two values: the run's
number, and a random code for the session that placed the run. A run with the
same number in a later session is therefore a different run. When the pinned
run is not open, the Workspace's areas show a named "run not present" state.
They never show another run in its place, and the simulation is left untouched.
The reader sets a pin on the row of Workspace tabs, and sees the absent state
there (`PL-2KXB`).

**For developers.** Colour cannot name the run, because the hover readout is
separate from the legend. Line width cannot, because it has no text equivalent.
Drawing order cannot, because nothing shows which run is drawn on top. The run
names sit in the always-shown region above the charts.

The run identity is defined in `src/anesthesia_sim/layout/run_identity.py`, and
the one place that renders a run's name is `dashboard_frame.run_label`. A
Workspace's views show the runs that `Workspace.shown_runs` returns. An earlier
rule showed run names only when more than one run was on the dashboard. That
rule fails for a run shown alone in a pinned area or in a window of its own
(`PL-2KXB`).

### The statement that the readouts are model outputs

The heading row of the readout section shows **"Model outputs — not
measurements."** beside "Modelled concentrations:" and the agent's name. The
chart's hover text labels every value as modelled. No monitor displays the
compartments that this simulator exists to show, so a user cannot check these
readouts against a measured value. A polished display makes them easy to
mistake for measurements.

**For developers.** The statement is required by the hazard row for reading a
modelled compartment value as a measured one. It sits beside the values it
qualifies, as the timeline's "Settings only — not a measurement." does for
control marks. The statement is not on the chart because people stop reading a
repeated disclaimer.

### What this list requires once the layout is the reader's

Since v0.6.0, the reader can add, resize and remove the interface's areas, the
parts of the window that each show one view, such as a chart (`ROADMAP.md`
planned-milestone item 34). This list was written for one fixed layout. It now
divides its values into three parts, by what a reader could misread without
them. Unconditional values stay on screen in every layout. From any layout, the
reader can bring on screen the agent accounting, which tracks how much agent the
model has delivered, exhausted and stored. Conditional values appear only with
the chart they belong to.

The division stops a rearranged layout from breaking this list unnoticed.
Hiding a compartment trace is safe because its value stays in the numeric
readouts. A layout that could remove the readouts would make every show/hide
control that this document permits unsafe at once, while the chart still
behaved exactly as documented.

**A value is unconditional when a reader could misread the run's other
displayed numbers without it.** Nothing may cover such a value. The set is
defined by this criterion, not by a fixed list, and the criterion gives two
tiers.

**The invariant tier is the same whatever is simulated.** It holds simulated
time, the rate at which it is advancing, the run state, why the run halted (when
it has), and what is being administered. A concentration shown with no time, no
run state and no named drug is the correct number under the wrong patient, which
is a display failure.

**The per-substance tier depends on what the run models** (project owner,
2026-09-16). For the inhaled-agent model that this document specifies, the
criterion selects the delivered concentration and the six compartment
concentrations, each in both units, with the agent's 1 MAC in percent. A run
that gives no volatile agent need not show them, because it has no vaporizer
dial, circuit concentration or MAC multiple to misread. That applies to a run
of the planned intravenous models (`ROADMAP.md` planned-milestone item 13), and
to a run of any later substance. The same criterion selects such a run's own
values, which are named where its substance's model is specified.

**The agent accounting must stay reachable, though not always visible.** It
consists of cumulative agent delivered, cumulative agent exhausted, total agent
stored, and the mass-balance residual with its absolute error. These five
amounts show whether the model is conserving mass, and a reader does not
titrate against them. A Workspace is a saved layout, chosen by its tab. A
Workspace may leave the amounts out, because their absence makes no clinical
reading wrong. Nothing may remove them from the application.

**"Reachable" means the reader can bring a view on screen through the interface
alone** (`PL-50PZ`). They must be able to do it from the Workspace they are in,
in a bounded number of steps, without dragging anything or editing a file.
Every area's header has a view chooser, whose menu lists every kind of view the
application has, whatever the Workspace. Choosing a view shows it in that area.
The page grows to give the view the space it needs, so the reader sees the view
itself, never only a notice that the area is too small (`PL-K285`). The
application will not start if the accounting view is missing from the chooser's
menu. Every layout has at least one area, so a chooser always offers the
accounting view. None of the Workspaces supplied with the simulator includes the
accounting view, so the chooser is how a reader reaches it.

**Conditional values are required only on a chart or plot that is shown.** A
concentration chart shows the MAC-awake band, the 1 MAC line and the marks of
control changes. It also states how much simulated time it shows, and whether
that span was chosen or fits the run. An $`F_A/F_I`$ plot shows its equilibrium
line and states where the ratio is not defined. These references exist so that a
trace is never read without its clinical anchor. Where no trace is drawn there
is nothing to anchor, so leaving the chart out loses nothing.

**The control-input record is unconditional, and its chart marks are
conditional.** The record lists every change to a setting during the run, with
the simulated time it took effect, the control it changed and the values it
moved between. It gives the facts, and the marks place them against the curve.

**The unconditional values sit outside the areas.** Each run's unconditional
values are in one band across the top of the dashboard, the unconditional
region. The setting sections are in a plain column between that region and the
areas, so they are outside the areas too (`PL-W9P6`). Neither is affected by a
change to the areas or a switch of Workspace, so no saved layout has to be
checked against this list. The dashboard will not place a run whose region
lacks a required value (`PL-NWTM`, laid out to `PL-J8K2`).

**The educational-use disclaimer is a line across the foot of the window,
outside the layout** (`PL-JSY5`, `PL-J8K2` Q1). Like the unconditional region,
it is unaffected by any change to the areas, so it is present in every Workspace
a reader builds. Once a run can be shown in a separate window, each window will
carry the line in its own frame, beside its invariant tier. A window read alone
needs the statement of what the tool is for as much as it needs the run's time
and agent.

**The disclaimer line and the unconditional region are always in view**
(`PL-NNML`). The line sits below the part of the dashboard that scrolls, and
the region sits above it. Only the Workspace tabs, the areas and the case's
controls scroll between them. The interpretation statement on the region's
readout heading row stays in view with the line and the region, at any window
height and through any scrolling. This is what "always" means in the paragraphs
on the alert colour in § "Color contrast, and the standard this interface is
held to".

**No value this list requires may be covered while the application treats it
as shown.** This occlusion rule applies to a panel drawn over the dashboard, a
separate window dragged over another window's invariant tier or over the main
window's per-substance readouts, and any floating element added later. It is a
property of the display, so it is the same for every kind of window.

**The occlusion rule applies only to the application's own windows and panels**
(2026-09-16). The application creates and places these, and can check their
state. A window of another program or of the operating system can still cover a
value, and no application can prevent that. The application can tell when one of
its windows is minimized or hidden, but it has no reliable signal that a window
is covered. It must never go on treating a value as shown once it can see that
the value's window is minimized or hidden.

**A separate window shows the invariant tier, not the whole set** (project
owner, 2026-09-16, ratified - a recommendation put to them and agreed, chosen
over the two live readings `PL-W54S` had written, and reopenable on ordinary
evidence per `CLAUDE.md`; the occlusion rule above is not, being the safety
requirement rather than the arrangement). Breaking an area out into a window
of its own is the second half of `ROADMAP.md` planned-milestone item 34, and it
is wanted but not yet scheduled (project owner, 2026-09-26). Such a window is a
full window, with areas of its own. The two tiers are unconditional for
different reasons, so each goes where its reason applies:

- **Every window of the application carries the invariant tier and the name of
  the run it shows**, in a region outside that window's areas. Any view that
  shows a concentration needs its time, run state and drug, so the tier goes
  with the concentration into whatever window shows it. Five values and a name
  fit, without squeezing, in a window that holds one chart.
- **The per-substance tier appears once, in the main window**, which cannot be
  closed while any other window is open. Closing the main window closes the
  others. A reader could misread the run's other displayed numbers without this
  tier, so it concerns the display as a whole rather than any one view.
- **The agent accounting is unchanged**, because its requirement already applies
  to the application rather than to any layout or window.

**The invariant tier answers a documented failure.** Correct data read in the
wrong context is an established class of clinical-information-system error.
Ash, Berg and Coiera describe the "silent errors" that such systems foster
rather than prevent (*J Am Med Inform Assoc* 2004;11(2):104-112,
doi:10.1197/jamia.M1471). Magrabi and colleagues classified 42,616 reported
incidents, and their classification makes information *output* a category of
its own, at 20% of computer-related problems (*J Am Med Inform Assoc*
2010;17(6):663-670, doi:10.1136/jamia.2009.002444). The closest measured
analogue is the wrong-patient order. Restoring one piece of patient context, a
photograph, to the display banner was associated with fewer wrong-patient
orders across 2,558,746 orders (adjusted OR 0.57, 95% CI 0.52-0.61; Salmasian
et al., *JAMA Netw Open* 2020;3(11):e2019652,
doi:10.1001/jamanetworkopen.2020.19652). That is the invariant tier's argument
in another clinical setting: context carried in the frame of the view, not
assumed from elsewhere on the screen.

**The division of this list is a first version** (project owner, 2026-09-15).
The fixed unconditional region and the conditional remainder were chosen to be
correct while the tools for arranging the layout are built, and the division is
expected to change as those tools mature. Any change must keep the occlusion
rule, because that rule is the safety requirement and the division is only the
arrangement.

**While two runs are shown, every readout names its run, and all six
compartments keep their readouts for both runs** (`PL-1XPX`). A required value
must not leave the display with the curve that draws it. That applies to the
chart's limit of two compartments in compare mode (`ROADMAP.md` v0.5.0,
`PL-HLD5`) just as it does when a reader hides a trace. The limit comes from how
many colours the chart can use, and it does not reduce what the display must
show.

**Both runs' values are shown, not only the selected run's.** Showing only the
selected run would make the readout block a mode. The block would look the same
whichever run was selected, so a stale selection would have no visual sign. A
reader who had forgotten the selection would take one management's number for
the other's. Stating the selection would only warn after the fact, whereas
showing both runs prevents the error.

Each compartment's panel holds both runs' values. The second run's value and its
second unit sit under the first run's, and each value has its run's name on the
line above it. The block therefore stays one row of seven panels and grows only
by those name lines (`PL-F2YS`). The single row keeps the comparison for which
this document requires uniform resolution: a reader sees the circuit lead the
alveoli, and the alveoli lead the tissues. Each readout panel reserves the width
of the widest value it can show, so a value is never wrapped away from its unit
at any width at which the row is laid out (`PL-3355`).

Each run's delivered concentration sits on that run's own line, beside its name
and its controls, such as Start. The values the two runs share appear once, on
the heading line above the block: the substance, the agent's 1 MAC, and the
version and model. They are the same for both runs because a second run must use
the first run's agent, and a branch's MAC is checked against its trunk's when
the branch is opened (`PL-QLZ5`).

**For developers.** The unconditional tiers and the control-input record are
stated as data in `app/unconditional_set.py`, with the inhaled-agent tier as
`INHALED_AGENT`. The educational-use disclaimer is a standing statement
(`USE_DISCLAIMER_TEXT`) rather than one of this list's values, so that file
does not declare it. The interpretation statement is
`INTERPRETATION_DISCLAIMER_TEXT`.

A code change that moves a required value into an area fails at once, because
the dashboard then refuses to place the run. Otherwise the reader could close
the value along with its area. Checking each saved Workspace and rejecting the
ones that fail is the fallback for anything that cannot sit outside the areas.
It is the weaker guarantee, because a check warns after the fact, while the
structure prevents the failure.

The view chooser is built in `app/area_layout.py`. The view registry marks the
accounting view `required_reachable` (`app/view_registry.py`), and a build that
does not register that view fails when the module is imported. Each area that
shows the accounting view builds a copy of its own, so two such areas both show
the five amounts (`PL-TH35`).

A test checks the chooser's route to the accounting view from every area of
each Workspace supplied with the simulator
(`tests/integration/test_view_chooser.py`). Another checks that the disclaimer
line is present in every Workspace
(`test_the_dashboard_carries_the_educational_disclaimer`). A third checks that
the unconditional region and the disclaimer line stay in view in windows 700,
900 and 1100 px tall, in each supplied Workspace
(`test_the_region_and_the_use_disclaimer_stay_in_the_viewport`). The region and
the line must also stay in view through the scroll to the concentration chart
that happens when a branch is taken (`PL-562Z`).

Before the region and the line were fixed outside the scrolling part
(`PL-NNML`), the whole page scrolled. At 1366 px wide, the page was 1087 px tall
in the Default Workspace and 1505 px in Induction and Maintenance (measured
offscreen, 2026-10-20). In a 700 or 900 px window, the disclaimer line was
therefore below the visible part, and scrolling down to it moved the region off
the top.

Blender is the model for the region's structure, a region outside the areas,
and not for its persistence. Blender's Topbar and Status Bar sit outside its
areas as this region does, but neither is always present. Focus Mode (View ->
Area -> Focus Mode, Ctrl-Alt-Spacebar) hides the Topbar, the Status Bar and the
editor's secondary regions together, for maximum screen space (Blender Manual,
"Interface -> Window System -> Areas", read at the source 2026-09-16). That is
the right trade for a 3D application and the wrong one here. Blender has no
value whose absence is a safety failure, and this application does. Take the
structure, and leave out any way to hide the region, such as Focus Mode. Say so
wherever a reader would otherwise assume that the whole precedent was copied.

The toolkit can report less about a covered window than first appears (measured
on PySide6 6.11.2 / Qt 6.11.2, 2026-09-16). A widget's visibility flag
(`QWidget.isVisible()`) is documented to stay true for a widget "obscured by
other windows on the screen", so it reports the application's own show/hide
bookkeeping and never occlusion. A window's visibility state
(`QWindow.visibility()`) says which of Hidden, Windowed, Minimized, Maximized or
FullScreen the window is in, so it catches a minimized or hidden window and
nothing else. The one signal close to occlusion (`QWindow.isExposed()`) is
documented only as something that *might* change when a window is "made totally
obscured by another window", and the platform plugins disagree about it. The
macOS plugin drives it from `NSWindow.occlusionState`, while the Windows plugin
deliberately keeps it true under occlusion for compatibility. No safety rule may
rest on that signal, which is why the occlusion rule asks only what the
application can see.

The region built in v0.6.0 must already have the right shape for separate
windows, because its protection from changes to the areas stops at the frame of
its own window.

Two other readings of what a separate window must show were refused, and should
not be proposed again. Giving every window the whole unconditional region fails
because a broken-out window is typically small, such as one chart on a second
screen. Seven concentrations in two units would either dominate it, which
defeats breaking it out, or be squeezed, which
§ "Diverged, and each divergence has a specific cause" of
`docs/interface-provenance.md` rules out. Giving the main window everything, and
a broken-out window only its run's name, leaves a window drawing compartment
traces with no time, no rate, no run state and no agent. It also rests the
guarantee on a window that the reader may not be able to see. In a third
reading, the requirement applies to the application rather than to each window.
It was ruled out on the same ground (`PL-WLWY`), because it too rests the
guarantee on where the window manager has put things.

The evidence checked does not name duplicating a live readout across windows
as a hazard in itself. The one randomised trial of concurrently open records
found no difference in wrong-patient errors (Adelman et al., *JAMA*
2019;321(18):1780-1787, doi:10.1001/jama.2019.3698). Nor does the evidence show
a published preference for non-overlapping areas over overlapping windows, and
the only controlled comparison does not support one. The case for
non-overlapping areas rests on this project's own reasoning about covered
values, as `ROADMAP.md` planned-milestone item 34 records.

Stacking the two runs' values leaves each panel at its one-run width, so the row
stays seven panels across at 1366 px. Placed side by side, the values would make
each panel roughly twice as wide (`PL-F2YS`).

### MAC multiples as a display unit

Every compartment is shown in two units at once: a percent of one atmosphere,
and a multiple of 1 MAC of the agent in use. Both units appear on the readouts,
on the delivered-agent control and on the chart. The chart has a percent axis
on the left, titled `% of 1 atm`, and a MAC axis on the right, titled `×MAC`. It
plots each trace once, in percent, and the MAC axis relabels that scale, so the
two axes always agree about where a trace is.

The MAC multiple of a concentration is its percent divided by 1 MAC of the
agent in use:

$$
\text{MAC multiple} = \frac{100F}{\mathrm{MAC}_\%}
$$

The MAC multiple introduces no new state and defines no modeled quantity.

The percent unit is `% of 1 atm`, not `vol %`, because `vol %` is a gas-phase
volume fraction and only the circuit and alveolar compartments have one. The
mixed-venous, vessel-rich, muscle and fat compartments hold a partial pressure,
which convention quotes as a percent of one atmosphere.

**MAC multiples keep their meaning when the agent changes, and clinicians reason
in them.** A percent changes meaning with the agent: 2% is 1 MAC of sevoflurane
and about a third of a MAC of desflurane. A desflurane wash-in and a sevoflurane
wash-in drawn at the same height in percent therefore show two different
clinical situations.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- derived: a third of a MAC of desflurane from data/agents/desflurane.json mac_percent = 6 -->

**What a MAC multiple means depends on the compartment.** MAC is defined for the
*alveolar* (end-tidal) concentration at one atmosphere in a nominal
40-year-old. It is the population ED50 for immobility in response to a
standardized surgical stimulus. So:

- On the **alveolar** compartment, a MAC multiple has its conventional
  meaning, subject to the limitations listed below.
- On the **circuit, mixed-venous, vessel-rich, muscle and fat** compartments,
  it means only *this compartment's partial pressure equals N times the
  alveolar partial pressure that would be 1 MAC*. It is a ratio of partial
  pressures, **not** a statement that the patient is at N MAC of anesthetic
  depth.

Three limitations apply to every compartment, including the alveolar one:

1. MAC falls about 6% per decade of age (Mapleson 1996), and the model's
   reference adult has no age parameter.
2. The MAC multiples of co-administered agents are additive, and the model runs
   one agent at a time.
3. Opioids, temperature and patient factors modify MAC, and the model
   represents none of them.
<!-- not-restated: 6 % -->

**The unit is written `×MAC`, not `MAC`.** A clinician reads "0.80 MAC" as a
depth of anesthesia, and "0.80 ×MAC" as a multiple of 1 MAC, which is what the
number is. Every readout carries the multiplication sign, and so does the MAC
axis title. The axis ticks show bare numbers, such as `0.5` and `1.0`, so only
the title says what they are. That title labels six traces at once, and five of
them are not the alveolar compartment. No text on the display explains the
difference between a ratio and a depth, so the sign is the only thing that
marks it.

**The agent's 1 MAC is shown beside the chart**, for example as "1 MAC
sevoflurane = 2.0%". Every MAC multiple on the display is a percent divided by
the 1 MAC of the agent that produced that percent. A reader can compare the
1 MAC shown with the value they use, and can convert back to the percent that
the model computes. The 1 MAC is also the vaporizer's starting position.
§ "Delivery-limit and MAC parameters" gives the source of each agent's 1 MAC,
how far it is from the primary literature, and what that gap means for
comparing agents.
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->

**The chart's vertical range is set in MAC, and fixed.** For every
agent, the axis runs from 0 to a ceiling of **3 ×MAC** of the agent in use, with
a gridline every half MAC. A given MAC multiple is therefore drawn at the same
height under any agent. The axis never grows to fit a trace. An axis that grew
would redraw a rising curve smaller partway through a lesson, and a reader would
take that change of shape for something the model did. The axis stays the same
for the whole session, not only within a run, so two consecutive runs are
comparable too.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**The chart names each compartment whose trace is above the ceiling.** A trace
above 3 ×MAC is cut off at the top of the frame, where it runs flat as a plateau
would. If the chart did not name the compartment, a reader would conclude that
the concentration stopped rising at 3 ×MAC when the model says it did not. The
chart also says that the readouts are not cut off and keep showing their values.
Sevoflurane's 8% dial setting is 4.00 ×MAC, above the ceiling, and is common for
inhalational induction.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- derived: 4.00 from data/agents/sevoflurane.json max_delivered_concentration_percent = 8, mac_percent = 2 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

**The chart keeps its linear percent axis, which crowds the slow compartments
together** (project owner, 2026-09-23, ratified, over a reader-selected
logarithmic scale, `PL-QYBW`). Only fat stays crowded for long. At a 1 MAC dial,
across the simulator's three agents, muscle spans 25–48 px of the 360 px plot at
one hour, and fat spans 1.5–3.7 px. Fat's trace near zero is its true partial
pressure, and partial pressure drives effect, so one linear axis serves all six
compartments. Because the hover readout reports every trace in reach, the
crowding needs no change of scale. The fat trace cannot show how much agent fat
holds: a fifth of the stored agent at one hour, and a third at three hours. The
compartment schematic shows that amount (§ "The compartment schematic: what its
heights, amounts and share bar assert").

**For developers.** Nothing in the model's code (`core/`) computes a MAC
multiple. The display code converts percent to MAC multiples
(`app/formatting.py`) and takes the agent's 1 MAC as an argument. That 1 MAC
travels in each snapshot of the simulation's state, beside the concentrations
it scales and the agent it belongs to (`SimulationSnapshot.agent_mac_percent`).
The display code therefore cannot pair one agent's concentrations with another
agent's 1 MAC.

Both units are shown because a unit selector would make the axis unit a mode,
and a chart read under the wrong assumed unit is a misreading that no
disclaimer catches. The agent's 1 MAC is shown because the project's rules
(`CLAUDE.md`) require a clinically meaningful displayed value to be traceable to
the transformation that produced it. The display carries no text explaining MAC
because its reader, an anesthesia provider, knows what MAC is defined against,
and a dozen lines of text between the reader and the plot cost more than they
gave (`PL-6580`).

In each agent's data file, the authority for the stored 1 MAC is De Wolf et al.
2012, which reports the flat adult MAC that Gas Man uses. Each data file also
cites Mapleson 1996, the source for the fall in MAC with age.

**For developers.** The stored 1 MAC (`mac_percent`) is a tier-3 value under
§ "Source hierarchy: what may be cited as the authority for a value", and
Mapleson 1996 is in each data file's `sources` list.

The ceiling (`CHART_AXIS_TOP_MAC` in `app/formatting.py`) is exactly
desflurane's dial maximum divided by its 1 MAC. It therefore rests on a real
device limit. Desflurane's vaporizer is the most limited, and the ceiling leaves
no empty band above the range that vaporizer can reach. The ceiling puts the
1 MAC line at a third of the plot height, inside the plot rather than on its
frame, which a ceiling of 2 could not do. It also keeps on the plot the
2-3 ×MAC range that overpressure induction works in. A ceiling at each agent's
own dial maximum could never be exceeded. But it would draw the same MAC
multiple at different heights for different agents, because the dial maxima
run from 3.00 ×MAC for desflurane to 4.17 ×MAC for isoflurane (`PL-CC23`).
<!-- derived: 3.00 from data/agents/desflurane.json max_delivered_concentration_percent = 18, mac_percent = 6 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->
<!-- derived: 4.17 from data/agents/isoflurane.json max_delivered_concentration_percent = 5, mac_percent = 1.2 -->

A gridline every half MAC (`CHART_GRID_INTERVAL_MAC`) falls on the values that
the MAC axis labels, so the axis names every gridline on the plot.

The chart compares a trace's excess over the ceiling with the displayed
resolution rather than with zero, so it does not name a compartment whose trace
sits exactly at the ceiling. This matters for isoflurane, whose ceiling,
3 × 1.2, is 3.5999999999999996 in binary floating point.
<!-- provenance: data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

### The chart's time base

**The time base is how much simulated time a chart shows at once.** The reader
either picks from a fixed ladder of widths, from fifteen minutes to twelve
hours, or leaves the default, which fits the whole run so far. Either way, the
horizontal axis is simulated time. A separate control, the playback rate, sets
how fast the run advances, so that a long case can be watched in one sitting.

**A time base changes the view and never the run.** No simulation step is
resized or taken again. Nothing that defines the run is added, discarded or
altered. A case watched at a width of fifteen minutes or of twelve hours is the
same run, so § "The reproducibility guarantee" still applies. Every point drawn
at any width is a state that the run reached at the simulated instant where the
point sits. In a wider window, these states lie further apart in simulated time.
No drawn value is estimated from its neighbours, and no stored image is
enlarged.

**No one width suits a whole case.** The compartments this model exists to teach
are slow, but the moment a learner is most likely to be watching is not. At the
reference settings, muscle's time constant for sevoflurane is about 135 min and
fat's is about 42 h, while induction lasts minutes. A five-minute window hides
everything slower than the vessel-rich group. A twelve-hour window puts a
five-minute induction in the leftmost 0.7% of the plot.

**A chosen width keeps slopes comparable within a run and between runs.** It
stays the same at every moment of every run. Seconds per pixel then depend on
the reader's choice alone, not on how long the run has gone on. A trace's slope
on the plot is therefore a fixed multiple of its rate of change. A window that
widened continuously with the run would rescale every slope while the rates
stayed the same. That would misrepresent rate of rise, the one quantity by which
uptake and distribution are taught. The vertical axis has a fixed range for the
same reason (see the section above).

**The gridlines follow from the width.** Each width on the ladder sets the
interval at which gridlines and labels fall, so that the axis holds four to six
intervals. Gridlines fall at multiples of that interval counted from the start
of the case, not from the window's left edge, so a gridline stays at the same
simulated time as the window slides under it. The gridlines are the same for
every run drawn on the axis, because a run branched from another keeps the clock
of the run it came from.

**The default always shows the whole run.** It uses the narrowest width that
holds the run, so the width steps up as the run grows, and slopes on the plot
change scale at each step. Past the widest width on the ladder, it keeps
doubling the width. Early in a run, it can also use widths narrower than any the
reader can choose.

**Every axis label carries its own unit, and each chart states its width.** A
label reads `0`, `45s`, `3m`, `1m30s` or `1h30m`. Beside the plot, the chart
names the width in words and says whether the reader chose it or it is the whole
run so far.

**Each chart has its own time base** (project owner, 2026-10-19, ratified, over
one shared window saved per Workspace; `PL-L59K`). The concentration chart and
the F_A/F_I plot each have a time-base control, and a choice in one sets that
chart alone. One chart can show the first fifteen minutes of a case while
another fits the whole run. Each notice that depends on a chart's window
describes that window and appears on that chart. These are the notice naming
traces above the top of the axis, the count of control changes the chart could
not mark, and the count of F_A/F_I stretches it could not draw. Two charts at
the same width show the same instants.

**A chart saves its width with its other settings.** The Induction Workspace
that comes with the simulator saves its concentration chart at the 15-minute
width. That width follows the run, so the current values stay on the plot after
the first fifteen minutes. Switching to the Induction tab opens the chart at that
width (`PL-2KXB`).

**For developers.** The time base's code is in `app/chart_time_base.py`. The
module does arithmetic on simulated time. It reads no simulation state and
imports no interface toolkit, so the widths and gridline intervals can be read,
cited and tested without loading the interface.

Each drawn point is evaluated from the run's definition, under the constraint
that § "Interface boundary" places on a plotted trace.

Each width on the ladder is at least half again as wide as the one below it, so
one step up or down visibly changes the view.

Four to six intervals look like a grid rather than a bare axis or a hatch
pattern. No single fixed interval does that across the whole ladder. The 60 s
interval used before would draw 720 gridlines across a twelve-hour axis, enough
to look like a solid block.

The doubling is there because a mode named for showing the whole run would
misstate what is on screen if it showed only the last twelve hours of a
fourteen-hour run. The narrower widths let the default work ten seconds into a
run as well as at ten hours. The reader cannot pick them, because a span with
nothing in it gives a view nobody wants.

Each label carries its unit because the axis spans anything from a minute to
half a day. A bare `12` would mean twelve minutes at one width and twelve hours
at another. Like the playback rate, the width is displayed because a reader who
cannot see the span supplies their own assumption for it. The chart also says
how the width was set, because a chosen width and the whole run so far mean
different things about what is on screen.

The roadmap for v0.6.0 asks for a time base per chart (`ROADMAP.md`
§ "v0.6.0 - the layout is the reader's", Required scope entry 11). Each chart's
notices describe its own window, because a notice naming a clipped trace that
the chart does not draw would be false for that chart. Charts at the same width
are drawn from one frame.

### MAC-awake as a chart reference

The compartment chart carries two horizontal clinical references for the agent
in use. A **band** marks its population MAC-awake, and a **line** marks its
nominal 1 MAC. Neither is modelled. Both are published constants, drawn at
their values on the chart's percent axis.

**With both references drawn, the chart shows the *decrement required for
arousal*, not only the endpoint.** Chortkoff et al. state that "along with
pharmacokinetics, the ratio of the awakening concentration to the
anesthetizing concentration (MAC-awake/MAC) determines time to awakening".
That ratio becomes the visible gap between the two references. So a reader can
compare a twenty-minute case with a three-hour case side by side, and see the
lesson of context-sensitive emergence.

**Shape, not colour, tells the two references apart.** MAC-awake is a measured
population value with real spread, so it is drawn as a band. 1 MAC is a
definitional anchor, not a distribution of the same kind, so it is drawn as a
line. The difference between a band and a line survives greyscale and every
colour-vision deficiency. Both references are drawn in the interface's own ink
and label colours, so neither is mistaken for a compartment.

**The band spans one standard deviation either side of the published mean
MAC-awake.** It covers roughly the middle two thirds of a population, not its
full range. A rule marks each edge, on its published value, with a light fill
between the two. Nothing pads the band outward, even where it is thin, so the
space between the rules is exactly the published spread.

MAC-awake is the concentration at which half of a population responds to verbal
command. The band's label names that endpoint. MAC's endpoint is different:
immobility in response to a standardized surgical incision.

**The band is not a prediction for the patient on the screen.** It is the
strongest claim that the evidence supports. The interface shows no
time-to-wake-up figure of any kind, because this model does not support a
per-patient prediction.

**Read the band against the vessel-rich trace.** This model has no effect-site
compartment and defines $`F_a \equiv F_A`$ (see § "Model boundary"). So the
alveolar trace is the fastest curve on the chart, and the furthest from where
responsiveness returns. One simulation shows the size of the gap. It ran
sevoflurane for 3 hours at the opening dial of 2.0%, which is the stored 1 MAC,
and the default fresh gas flow of 4 L/min. That brought the alveolar fraction
only to 1.69%, or 0.84 MAC. The vaporizer was then turned off and the fresh gas
flow raised to 10 L/min. The alveolar trace crosses the band's centre at
2.86 min, and the vessel-rich trace crosses it at 6.55 min, 2.29 times later.
These figures are from a run on 2026-10-26, repeated on 2026-10-31 (`PL-39KH`,
`PL-PTDZ`). An automated test reruns this protocol and checks each figure to
the decimal places printed here.
<!-- not-restated: 10 L/min -->
<!-- provenance: data/agents/sevoflurane.json mac_percent = 2 -->
<!-- provenance: data/machines/reference_circle_system.json default_fresh_gas_flow_l_min = 4 -->

<!-- derived: 2.86 min from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->

**The choice of trace also decides which published value is correct.** Katoh
et al. determined sevoflurane and isoflurane MAC-awake by a slow, equilibrated
washout and by a fast one, and the two methods disagree. Slow washout gave
0.34 of MAC for sevoflurane and 0.31 for isoflurane, against 0.22 for both by
fast washout. Katoh attributes the disagreement to end-tidal-to-arterial and
arterial-to-cerebral anesthetic differences. This model represents those
differences as the gap between the alveolar and vessel-rich traces. The stored
values are the slow-washout ones, and they belong against the vessel-rich
trace.
<!-- provenance: data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34 -->
<!-- provenance: data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31 -->

Katoh also estimated the brain concentration at awakening. That estimate is
not a measurement, because cerebral concentration cannot be sampled in these
patients. The abstract says the brain concentrations were "calculated with
end-tidal anesthetic concentrations", and the title calls them "predicted".
So they come from Katoh's own model of brain uptake (`PL-YDRT`). That model
treats the brain as one well-mixed compartment perfused by arterial blood. Its
equation 1 (p. 1013) is:

$$
\frac{dP_{Brain}}{dt} = \frac{CBF \cdot \lambda_{B/G} \cdot (P_{Art} - P_{Brain})}{V_{Brain} \cdot \lambda_{T/G}}
$$

This is the perfusion-limited form that § "Tissue uptake and return" uses for
each tissue group. Katoh's compartment is the brain alone, though, while this
model's vessel-rich group pools the brain with the heart, liver, kidney and
viscera. Katoh computed every patient's flow and volume from the same
formulas. Cerebral blood flow $`CBF`$ is 14.3% of a cardiac output set by a
cardiac index of 3.5 L/min/m², so it scales with body surface area. Brain
volume $`V_{Brain}`$ is 21 mL/kg, so it scales with body weight. The brain's
time constant therefore varied a little from patient to patient. The
coefficients were the same for everyone. The blood:gas coefficient
$`\lambda_{B/G}`$ is 0.63 for sevoflurane and 1.36 for isoflurane, and the
brain:gas coefficient $`\lambda_{T/G}`$ is 1.15 and 2.09.

Katoh did not measure the arterial partial pressure. Equation 2 sets it equal
to the end-tidal value. Equation 3 (p. 1016) corrects the end-tidal value for
20% dead-space gas, as $`P_{Art} = (P_{ET} - 0.2\,P_I)/0.8`$. The two give
different results. During fast washout, the calculated cerebral concentration
at first eye opening was 0.30 of MAC for sevoflurane and 0.26 for isoflurane
under equation 2 (Table 1, p. 1014). Under equation 3 it was 0.34 and 0.30
(Table 3, p. 1016). The abstract quotes the equation 3 figures and calls them
"nearly equal to MAC-Awake obtained by slow alveolar washout". Neither set
differs significantly from the slow-washout values. So the stored values and
the choice of the vessel-rich trace rest on a modelled estimate that agrees
with an equilibrated measurement. That is weaker evidence than a direct
measurement of the brain would be.

<!-- not-restated: 0.34 -->

**The band is drawn at a fraction of the stored MAC.** MAC-awake is stored as
that fraction, never as a percent of one atmosphere. Each source expresses
MAC-awake as a ratio to MAC, and Katoh does so explicitly, "as a ratio to
age-adjusted MAC". A published *percent*, by contrast, is tied to whichever MAC
its own population was measured against. Desflurane shows the risk. Chortkoff's
MAC-awake of 2.60% is 36% of a MAC of about 7.25%, Rampil's figure for ages
18-30. The stored MAC is Rampil's figure for ages 31-65, 6.0%. Dividing 2.60% by
6.0% would give 0.433 instead of the published 0.36, so the band would be drawn
20% too high and crossed too soon. Storing the fraction avoids that error. The
chart's MAC axis is also scaled by the stored MAC, so the band sits at its
published fraction on that axis. For desflurane, storing the fraction also
allows an independent check. The band's centre is 0.36 of the stored 6.0%, or
2.16%, and Song et al. measured 2.17% in the non-jaundiced control arm of a
population that Rampil's 31-65 year MAC describes.

<!-- derived: 0.433 from data/agents/desflurane.json mac_percent = 6, mac_awake.fraction_of_mac = 0.36 -->
<!-- derived: 2.16 percent from data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36, mac_percent = 6 -->

**Three misreadings of the band all make emergence look faster than this model
says.** Concentration falls during emergence. So a trace crosses a higher
reference sooner, and a faster-falling trace crosses any reference sooner. The
first error is reading the band against the alveolar trace instead of the
vessel-rich one. The second is drawing the slow-washout value against a
fast-washout alveolar trace, where 0.22 would be the matching figure. The
third is dividing a published MAC-awake percent by a MAC other than the one
its population was measured against, as in the desflurane example above. A
learner who takes away any of these errors carries into practice the belief
that a patient is more awake than they are.

**The band's height has a fourth source of error, and its direction differs by
agent** (`PL-GCGX`). The stored MAC is Gas Man's flat adult value. The traces
are absolute partial pressures and do not depend on MAC. So wherever the
stored MAC departs from the literature, the band moves against the traces by
the same proportion. § "Delivery-limit and MAC parameters" compares the stored
MAC with Mapleson's age-40 values. Against them, the stored MAC is 11.1% high
for sevoflurane, 2.6% high for isoflurane and 9.1% low for desflurane. All
three are gaps from Mapleson's MAC, not from the MAC that each source used.
Mapleson's 95% confidence limits are about ±7%, and ±10% for desflurane. Only
sevoflurane's gap is larger than its limits. So the sevoflurane band probably
sits too high, by about 11% if Mapleson is right, and a band drawn too high
teaches an earlier wake-up. In the run above, the vessel-rich trace crosses
sevoflurane's drawn band centre of 0.68% at 6.55 min. It crosses 0.612%, the
same fraction of Mapleson's 1.80%, at 7.30 min.
The isoflurane and desflurane gaps are inside the limits, so Mapleson does not
show either band to be off. Song et al.'s measurement agrees with the drawn
desflurane band as well.
<!-- derived: 0.68 percent from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->

The comparison with Katoh's own MAC at age 40 points the same way as the
Mapleson one. The band sits slightly high, so it teaches a slightly early
wake-up (`PL-P319`). Katoh's denominator is each patient's age-adjusted MAC,
from two linear equations on p. 1013. For isoflurane it is
1.43 − 0.0061 × age (yr) percent, and for sevoflurane
2.56 − 0.0156 × age (yr) percent. The paper cites four MAC studies for them
and does not say how the equations were derived from those studies. At age 40
the equations give 1.94% for sevoflurane and 1.19% for isoflurane. The stored
MAC is 3.3% above Katoh's for sevoflurane and 1.2% above it for isoflurane, so
the band sits above Katoh's own age-40 awakening concentration by the same
proportions. The drawn centres are 0.68% sevoflurane and 0.372% isoflurane,
where Katoh's fractions times Katoh's age-40 MAC give 0.658% and 0.368%. Both
differences are much less than the standard deviation of Katoh's fractions,
0.05 of MAC. Katoh's slow-washout patients themselves woke at a mean end-tidal
0.63 ± 0.11% sevoflurane and 0.36 ± 0.08% isoflurane (Table 1, p. 1014).
Those figures are lower than the band mostly because the patients were older,
with mean ages of 45.9 and 45.1 years. So they are not a like-for-like check
of a band drawn for age 40.
<!-- not-restated: 0.36 -->
<!-- provenance: data/agents/sevoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- provenance: data/agents/isoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- derived: 3.3% from data/agents/sevoflurane.json mac_percent = 2 -->
<!-- derived: 1.2% from data/agents/isoflurane.json mac_percent = 1.2 -->
<!-- derived: 0.68 percent from data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34, mac_percent = 2 -->
<!-- derived: 0.372 percent from data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31, mac_percent = 1.2 -->

**The 1 MAC line marks the nominal value, not the dialled one.** A fixed line
sits at the same height in every run, so runs stay comparable. A line that
tracked the dialled concentration would only restate where the trace already
starts. The line sits at the stored MAC. It is labelled as a reference adult
value, not as this patient's MAC, because this model has no age parameter.

At a 1 MAC dial, no patient trace reaches the 1 MAC line, however long the case
runs. This is expected and is not a display fault. Muscle and fat keep taking
up agent for many hours, so the blood returning to the lungs stays below the
alveolar gas. That keeps the alveolar fraction below the inspired fraction, and
rebreathing keeps the inspired fraction below the dial (`PL-39KH`). In the
3-hour run above, the alveolar and vessel-rich traces both reached only
0.84 MAC. This shortfall happens in real patients too, and it is worth teaching.

**The *absolute height* of both references inherits every limitation of the
stored MAC.** The fractions come from primary measurements in humans (tier 1).
The stored MAC is tier 3: it is Gas Man's parameter, not a measurement
(§ "Source hierarchy: what may be cited as the authority for a value").
§ "Delivery-limit and MAC parameters" records its limitations. The interface
shows that MAC, so a reader can compare it with the value they would use.

**The three fractions were not determined by one method.** Katoh's
slow-washout arm is *descending*. Chortkoff and Song both determined
desflurane MAC-awake by *ascending* stepwise equilibration. All of these are
equilibrated determinations, not fast-washout ones, so all three fractions
belong against the vessel-rich trace. But ascending and descending
determinations are not interchangeable, and no descending-washout MAC-awake
for desflurane was found. The three fractions (0.31 isoflurane, 0.34
sevoflurane, 0.36 desflurane) sit in a narrow range, so each agent carries its
own value rather than one fraction covering all three.
<!-- provenance: data/agents/isoflurane.json mac_awake.fraction_of_mac = 0.31 -->
<!-- provenance: data/agents/sevoflurane.json mac_awake.fraction_of_mac = 0.34 -->

<!-- provenance: data/agents/desflurane.json mac_awake.fraction_of_mac = 0.36 -->

**For developers.** The model's code (`core/`) computes neither reference, and
no governing equation uses MAC-awake or the stored MAC (`mac_percent`). Each
agent's data file records the MAC that its MAC-awake fraction was derived
against (`mac_awake.mac_reference_basis`). Storing the fraction is a safety
decision. It also keeps the band correct if `mac_percent` is ever changed or
made age-aware.

Telling the references apart by shape meets the requirement in
§ "Color contrast" below for any encoding that carries meaning. Shape also
separates them more strongly than any pair of colours would. Using the ink and
label colours avoids a seventh and eighth hue on the chart.

The band has no minimum drawn height, even though one would help legibility.
A padded band would claim a wider population spread than the sources support.

The band is ruled on both edges because no axis range that the chart can use
gives it enough height to look like a band on its own. On the fixed axis range
(`CHART_AXIS_TOP_MAC`, 3 ×MAC), it spans 3.33% of the plot height for
sevoflurane and 4.20% for desflurane. A 2 MAC ceiling would make the band
unambiguous, but § "MAC multiples as a display unit" gives the reasons the
ceiling is 3 MAC. A 4 MAC ceiling would shrink the band to 2.50%, as on the earlier axis, whose top was
the vaporizer dial's maximum. A band ruled on its upper edge only, over an
unruled fill, looks like a line with a shadow beneath it, whatever the fill's
height. The two references would then no longer differ in shape. Two rules with
a gap between them look like an interval at any height the axis leaves.

<!-- derived: 3.33 percent from data/agents/sevoflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.05 -->
<!-- derived: 4.20 percent from data/agents/desflurane.json mac_awake.standard_deviation_fraction_of_mac = 0.063 -->
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

There is no time-to-wake-up readout because a figure such as "time to
wake-up: 14 min" would be taken as a per-patient prediction. No disclaimer
beside it would undo that, because readers act on the number and not on the
disclaimer.

The washout figures come from simulating sevoflurane uptake
(`AgentUptakeSystem.for_agent("sevoflurane")`) at 0.1 s steps. Since the
2026-10-31 run, each crossing time is interpolated between the two steps on
either side of it. The automated test reads the protocol and its figures from
this section (`tests/reference/test_mac_awake_washout_figures.py`). So a
parameter change that moves a figure fails it, and so does an edit to the
protocol or to a figure on its own.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->

### The control-input timeline

**The timeline records the settings that a run was given.** Each entry is one
change that the model ran under. It gives the simulated time at which the
change took effect, the control, the values before and after, the unit of both
values, and the user adjustment that the change belongs to, such as one drag of
a slider. The timeline is kept with the run and cleared with it. It is shown as
marks on the charts and as a list beside them. Settings of the delivered
concentration appear in the same format as every other concentration on the
page.

**A curve can be checked only against the settings that produced it.** The
exercises that this simulator exists to support all take the form "change one
thing and look at what happened". Examples are overpressuring and then dialling
back, dropping the flow, and halving the cardiac output. A learner who cannot
see where they dialled back cannot read their own experiment. Given the
recorded settings at the recorded times, a fresh run must reproduce the run
that the timeline describes.

**Each recorded value is the one that took effect.** The model refuses a
setting outside its allowed range rather than replacing it with the nearest
allowed value, so the value that took effect never differs silently from the
value asked for. A refused setting is not recorded.

**Only what the model saw is recorded.** A setting equal to the one already in
place is not a change. Nor is a setting that is replaced before the next
simulation step, because the model uses only the value in place when a step
runs. A control moved twice between two steps is therefore one change, from the
first value to the last. A control moved and moved back within one step is no
change at all. Recording the values in between would describe a run that did
not happen.

**One drag of a control is one adjustment, and it applies once.** While the
slider's handle is held, the run keeps its setting and the chart draws a preview
(§ "A preview of an unapplied setting"). Releasing the handle applies the value
once, so a drag records one setting change. A key press, one notch of the scroll
wheel or a click on the slider away from its handle is a single input, and is an
adjustment of its own.

A displayed adjustment states the interval it spans and how many settings the
model ran under during it. The count is shown because an adjustment made over
eight settings is a different run from one made in a single step, even when
the two start and end at the same values.

**A timeline entry records an input, and says nothing about the patient.** The
marks on the charts are labelled as inputs, and the list says so, because a
vertical line on a chart of patient concentrations would otherwise invite the
reader to see an event in the curves.

**Bounds are displayed, not silent.** A chart shows at
most a fixed number of marks, and the list of setting changes at most a fixed
number of lines, so a run may record more adjustments than either can show. A
chart or a list that ended without a count would tell the reader that nothing
else happened. Each chart shows the count of adjustments it leaves unmarked,
because each chart has a window of its own (§ "The chart's time base").

**The timeline itself has no limit.** The limits above apply only to what is
shown. Dropping the oldest entries would remove the start of the case, which is
the part a learner returns to.

**For developers.** The two display limits are `MAX_CHART_CONTROL_MARKS` in
`app/chart_frame.py` and `MAX_LISTED_ADJUSTMENTS` in `app/dashboard_frame.py`.
No record gives the reason for either value (`PL-N8G4`).

The timeline reads each value from the compartment that
holds it, after the model's setter for that control returns. A setter returns
only when the model accepts the value, so no separate check is needed to keep a
refused setting out.

Every value is stored in the unit the model is set with, which for the
delivered concentration is the percent of one atmosphere (`PL-NJPB`). The
formatter for concentrations (`format_percent`) takes a fraction, so the stored
percent is converted to a fraction on its way in and back to a percent for
display.

The interface declares an adjustment when a drag starts, and each change
carries the number of its adjustment. A change that arrives with no declared
adjustment, such as a call from code, gets a number of its own. Code must never
group changes by the time between them. A playback multiplier changes how much
simulated time one drag spans, so any time threshold would group correctly at
one multiplier and wrongly at another.

Each control is recorded under a fixed name from the clinical vocabulary:
`fresh_gas_flow`, `delivered`, `alveolar_ventilation` and `cardiac_output`. A
name taken from the accessor that applies the setting would change whenever the
code was renamed, and those accessors have been renamed three times (`PL-3TLK`,
`PL-9SH6`, `PL-NJPB`). The circuit volume was recorded as a fifth control,
`circuit_volume`, until it became a fixed model parameter (§ "What is not
bounded this way"). Removing that name broke no recorded timeline, because a
timeline is held in memory and is never saved.

Capping the timeline would lose the settings needed to reproduce the run. It
would also leave memory use unbounded, because the run itself holds one stretch
and one keyframe for each accepted change and has no limit either
(§ "The run is that record, and every state is derived from it").

The timeline can be unlimited because it grows with the number of settings
changed, not with the length of the run. Until a drag was recorded only on its
release (`PL-5B1N`), each drag added at most one entry per simulation step,
however fast the slider reported. The number of entries per real second then
depended on the tick rather than on simulated time, so it was the same at every
playback multiplier. On 2026-09-14, under `PL-1PSX`, continuous dragging gave
ten entries per real second at 1×, 5×, 20×, 60× and 300× alike, and a drag made
while the run was paused gave one entry. Grouping the entries for display costs
0.9 ms per frame at a thousand entries and 8.8 ms at ten thousand, against a
200 ms frame. The grouping is recomputed only when the timeline changes. At a
hundred thousand entries it would cost half a frame. Reaching that many took
about three hours of unbroken dragging under the old behaviour, and the
timeline would then be smaller than 9 MB.
<!-- provenance: app/dashboard_frame.py RENDER_INTERVAL_S = 0.2 -->

### F_A/F_I as a displayed ratio

**A second plot, under the compartment chart, draws $`F_A/F_I`$.** It shows the
modelled alveolar fraction divided by the modelled inspired fraction, over the
same time window, on a fixed, dimensionless axis labelled from 0 to 1. The
uptake literature is taught from this curve, and the wash-in figures a reader
has seen show it. The plot can therefore be laid beside a published figure. The
six compartment concentrations on the chart above cannot. A validation test
compares the plotted ratio with human measurements at 30 minutes, for all three
agents in the simulator (§ "Published wash-in and elimination validation
test"). The ratio is computed only for display, and no equation of the model
uses it.

**The ratio is a modelled value, not a measurement.** It has the alveolar
compartment's limitation: this model has no airway sampling delay and no dead
space. It is not a depth of anesthesia, a time to any endpoint, or a
prediction for an individual patient.

**The denominator is the modelled inspired concentration, not the vaporizer
dial.** This model assumes that the inspired fraction is the concentration in
the breathing circuit (§ "Model boundary"). The circuit approaches the
delivered concentration only over its own time constant, so early in a run the
two differ substantially. Dividing by the dial would understate the ratio for
as long as they differed. The interface says beside the plot which denominator
the ratio uses.

**The curve is the textbook wash-in curve only while the inspired
concentration is held constant.** If the vaporizer setting or the fresh gas
flow changes mid-run, the ratio is no longer the wash-in fraction of anything a
reader can name. A rise across such a change shows the setting moving, not
uptake slowing. This plot therefore carries the compartment chart's control
marks, which show where each setting changed (§ "The control-input timeline").

**A point is drawn only inside two boundaries.** The plot samples the run at a
series of instants, called columns. A column is inside the boundaries when both
of these conditions are true:

1. $`F_I \geq 10^{-4}`$ (0.01%), the smallest step of the concentration
   display. $`F_I`$ is exactly zero until agent reaches the circuit: at the
   start of every run, and throughout a run whose vaporizer is never opened.
   There the ratio is $`0/0`$. With this limit, the ratio is never formed
   from an inspired concentration that the display shows as `0.00%`.
2. $`F_A/F_I \leq 1`$, which is the uptake regime. Alveolar gas gives up agent
   to blood, so the alveolar fraction stays below the inspired one and reaches
   it only at equilibrium. Above 1, the tissues are returning agent faster
   than it is delivered, which is elimination, not wash-in. The chart draws
   equilibrium as a labelled reference line.

   This boundary allows the ratio up to 1.000001. At zero cardiac output the
   exact ratio rises to 1 and stops, but the simulation's rounding can leave
   it a hair above 1. If the ratio stayed at 1.000001 for a whole run of the
   longest supported length, the run would lose less than 1% of the agent in
   alveolar gas, venous blood and the vessel-rich group.

Outside either boundary nothing is drawn, so the trace breaks into separate
stretches. No value is pinned to the edge of the axis or replaced by a
default, and no line bridges a gap. A ratio held at 1.0 would show a completed
wash-in that the run never reached. A line joining the wash-in on either side
of a washout would show values that the run never produced.

**Each stretch is extended by one column at each end, so a reader can see
where it stops.** That extra column is the stretch's *crossing column*: the
neighbouring column that has a ratio but lies outside the boundaries. Without
it, the trace would stop at its last column inside the boundaries. That
column can lie below the equilibrium line by as much as the trace rises between
two columns. A trace that stops in clear space short of the line looks exactly
like one cut off by the edge of the plot. This trace is still climbing steeply
when it stops. With the crossing column drawn, the trace meets the equilibrium
line and ends on it, with a point marker that shows the trace ended rather than
ran out of view.

A crossing column whose ratio is above a fixed ceiling is not drawn at all. Its
stretch then ends at its last column inside the boundaries, with no point moved
onto the ceiling and no line drawn toward it.

**The crossing column is drawn, but its value is not shown as wash-in.** Its
ratio is above 1. Hovering over it shows "Past equilibrium: not a wash-in
fraction" under the wash-in label, in place of the ratio. A value such as 1.03
shown there would teach a wash-in past completion, at the point marker, where
a reader is most likely to look.

**The caption beside the plot says why the trace is blank.** "No agent has
reached the circuit yet" and "the patient is returning agent" are opposite
situations, and an absent trace alone cannot show which applies. While the
trace is drawn, the caption gives the value at its right-hand end. One
calculation produces both the caption and the trace, so they cannot disagree.

**The gridlines and labels stop at 1, with a little space above them.** Every
published wash-in figure uses a scale of 0 to 1, and matching those figures is
the point of this plot. The space above keeps a trace that ends at equilibrium
off the top edge, where it would look cut off. Because that space is
unlabelled, a reader does not take it for a range the ratio can reach.

**The axis is fixed rather than fitted.** An axis that grew to fit the ratio
during elimination would redraw the wash-in curve at a smaller height partway
through a lesson, and a reader would attribute that change of shape to the
model. Such an axis would also have no stable height. During elimination the
circuit is fed by agent-free fresh gas and by rebreathed alveolar gas, so the
ratio settles near $`1 + \dot V_{\mathrm{FGF}} / \dot V_A`$, which the
supported input ranges do not bound.

**The ratio is shown to two decimals, to match the published spread.** Yasuda
et al. report 0.850, 0.733 and 0.90, with standard deviations of 0.018, 0.027
and 0.01, so a third decimal would be finer than that spread. See
§ "Published wash-in and elimination validation test".

**For developers.** The ratio and its two boundaries are computed only in
`app/wash_in.py`, a module that contains nothing else. Unit tests cover both
(`tests/unit/test_wash_in.py`). The ratio is no part of a run's definition. A
test checks that the plotted ratio is the quantity that the validation compares
(`test_the_displayed_ratio_is_the_quantity_this_file_validates`).

The control marks on both plots are drawn in one pass over the same
adjustments.

The 0.01% limit on $`F_I`$ is derived from the concentration display's
resolution (`CONCENTRATION_DISPLAY_RESOLUTION_PERCENT`), so it follows that
resolution if the display changes.

The rounding allowance of 1e-6 (`WASH_IN_ROUNDING_ALLOWANCE`, `PL-N559`) is
there because, at zero cardiac output, the stepped run settles on a
floating-point fixed point within about 1e-13 of the exact solution. A fixed
point is a state that every later step returns unchanged. In some runs that
state has $`F_A`$ above $`F_I`$. An isoflurane run at a fresh gas flow of
10 L/min settles at a ratio of 1 + 2.2e-14, which the plot once captioned as
the patient returning agent. Because later steps return the same state, the
overshoot does not grow with run length. On 2026-10-26 it was the same at 96 h
as at 1 h. A test checks the fixed point against the exact solution for each
shipped agent
(`test_a_zero_cardiac_output_steady_state_is_not_read_as_elimination`).
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

The allowance is sized from the 1% limit above, a clinical requirement, rather
than from the rounding (project owner, 2026-10-26, ratified, over 1e-9 sized
from the rounding and over deriving the value in code). At a ratio of
1 + 1e-6, agent leaves at a rate of alveolar ventilation times $`F_I`$ times
1e-6. The agent held in alveolar gas, venous blood and the vessel-rich group
also scales with $`F_I`$, so the fraction lost is the same at any $`F_I`$. The
worst case is desflurane at an alveolar ventilation of 12 L/min, where a run
loses about 0.3% in 24 h. A test checks the loss for every shipped agent from
the run-length limit, the ventilation limit and the data files, so extending
any of them fails it
(`test_the_rounding_allowance_hides_no_clinical_change_over_a_whole_run`). The
allowance is also about 10 million times the largest overshoot seen in a run,
9.6e-14.
<!-- provenance: core/supported_ranges.py MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

The chart code works out the stretches again in each frame, from the columns
that frame draws, rather than keeping them as the run goes. A boundary can
therefore fall only on an instant that the chart plots (`app/chart_frame.py`,
PL-2FM6).

**For developers.** The column at which the $`F_A/F_I`$ curve crosses
equilibrium has a ceiling, because the ratio can jump. In runs stepped at 0.1 s,
the first value above equilibrium is at most 1.00235, across every shipped agent
and every supported alveolar ventilation and cardiac output, at the maximum
fresh gas flow. Changing the circuit volume
(`BreathingCircuit.set_circuit_volume`), however, keeps the agent in the circuit
and changes the volume it is divided by. Doubling the volume between two steps
therefore halves $`F_I`$ and doubles the ratio. No interface control changes the
circuit volume today, but the plot should not rely on that. The ceiling is 1.05
(`WASH_IN_TERMINUS_CEILING` in `app/chart_frame.py`), below the axis top of 1.15
(`WASH_IN_AXIS_MAXIMUM`), so even the widest crossing it allows still has clear
space above it.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: app/chart_frame.py WASH_IN_TERMINUS_CEILING = 1.05 -->
<!-- provenance: app/chart_frame.py WASH_IN_AXIS_MAXIMUM = 1.15 -->

The hover text past equilibrium is set in the chart code
(`WASH_IN_HOVER_PAST_EQUILIBRIUM_TEXT` in `app/chart_frame.py`, `PL-YH6Z`).

The formula for the ratio during elimination was checked on sevoflurane by
closing the vaporizer at a fresh gas flow of 10 L/min after a 30-minute wash-in.
The ratio was 3.47 at the reference adult's 4.0 L/min of alveolar ventilation,
1.83 at 12.0, 5.93 at 2.0 and 20.11 at 0.5, against predictions of 3.50, 1.83,
6.00 and 21.00.
<!-- provenance: data/patients/reference_adult.json default_alveolar_ventilation_l_min = 4.0 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

The two decimals are not derived from the concentration display's resolution,
because the ratio's resolution depends on its denominator. It is far coarser
early in wash-in than at equilibrium, so any single derived figure would
over-claim at one end.

### Color contrast, and the standard this interface is held to

**The target is WCAG 2.2 Level AA.** WCAG 2.2 is the current W3C
Recommendation (published 2023-10-05). Meeting its Level AA also satisfies the
2.1 AA that EN 301 549 and the 2024 ADA Title II rule reference, and the 2.0 AA
that Section 508 references. None of those applies to this project. AA was
chosen as the right engineering bar for a teaching tool. The interface does not
target WCAG 3.0, a Working Draft whose scoring model replaces pass and fail.
<!-- not-restated: 2.1 -->

The project defers four criteria until the interface is settled enough to
assess them: SC 2.4.11 (Focus Not Obscured), 2.5.8 (Target Size), 1.4.10
(Reflow) and 1.4.12 (Text Spacing). Keyboard and screen-reader support is an
open question, not a commitment, because it depends on what the software that
draws the window can deliver.

Two criteria carry most of the weight:

- **SC 1.4.3, Contrast (Minimum)**, requires 4.5:1 for text. Every readout,
  every label naming a readout, and every agent name over its identification
  color must meet it. The project never uses the large-text exception (18pt, or
  14pt bold), so the larger readout values must meet 4.5:1 too, and so must the
  bold status text, set at the default size of 14px.

  **Text is measured against the surface it is drawn on, and there are two
  such surfaces.** The run-status word, the halted-run notice and the
  educational-use disclaimer sit directly on the page background. The
  readouts, their labels, the axis description and the accounting lines sit
  inside panels, which are lighter than the page. Where a color appears on
  both, the page background is the stricter test, and it is the one that
  counts.
- **SC 1.4.11, Non-text Contrast**, requires 3:1 for graphical objects. Here
  that means each chart trace against the panel it is drawn on, each agent
  swatch treated as a shape, and the active track of each parameter slider,
  which shows where the slider's value sits in its range.

<!-- not-restated: 4.5 -->

**Color is never the only cue.** SC 1.4.1 (Level A) requires this, and ISO
5360 Table 2 footnote b gives a stronger reason: it makes displaying a color an
obligation to display the *correct* one. A second cue keeps a mis-seen color
from becoming a mis-identified agent, so the agent name always accompanies the
color. Telling a running simulation from a halted one is safety-critical. The
status words "Running" and "Valid" differ from the words for the opposite
states, which appear in the warning color. A reader who cannot tell the colors
apart therefore still reads the state.

The agent selector and the header back the written name with the
agent-identification colour of ISO 5360:2016 Table 2 ("Dimensions and colours
of agent-specific bottle collars and connectors"): yellow for sevoflurane,
purple for isoflurane, and blue for desflurane. Footnote b of that table is why
the colour appears at all: "if a colour is used on a vaporizer, bottle, or
package label to facilitate correct identification, it is important that only
the colour for the appropriate anaesthetic agent be used".

The displayed fills are two approximations away from the standard's own colour.
Table 2 footnote c states that "Munsell colour is the original" and that the
other colour systems it lists "show the nearest available colour sample". The
Pantone reference is therefore already ISO's approximation, and each displayed
fill is a screen colour (sRGB) that approximates the Pantone in turn. The
sevoflurane and desflurane originals lie outside the range of sRGB colours, so
no display can reproduce them exactly. Converting each Munsell original to sRGB
directly gives each displayed fill's difference from the standard's original
(ΔE00):

| Agent | ISO Munsell original | Munsell as sRGB | Displayed fill | ΔE00 |
| --- | --- | --- | --- | --- |
| Sevoflurane | 6.25Y 8.5/12 | `#F2D600` | `#FEDB00` | 2.1 |
| Isoflurane | 7.5P 4/12 | `#8D4192` | `#981D97` | 5.7 |
| Desflurane | 10B 4/10 | `#0069A0` | `#00629B` | 2.6 |

<!-- not-restated: 2.1 -->

Table 2 specifies a *colour* for desflurane, and this application uses it,
even though the Scope of ISO 5360 excludes desflurane's *dimensions* and its
row in that table records "N.S." for the collar angle.

This application keeps a known limitation of the standard. A reader with a
colour vision deficiency cannot tell isoflurane's purple from desflurane's blue.
With normal colour vision the two differ by only 1.09 in luminance, so hue alone
separates them. Simulating the three dichromacies removes the hue without
supplying the luminance difference needed to tell them apart: 1.48 for
protanopia, 1.06 for deuteranopia, and 1.11 for tritanopia. More separable
colours would break the match with real vaporizers, so they are the worse
option. For a reader with a colour vision deficiency, the agent name beside each
colour identifies the agent instead.

**The alert colour deliberately does not follow the medical alarm-colour
convention** (project owner, 2026-09-14). This interface uses the alert colour
only for bold coloured text: the run-status word, a transient notice line, the
agent-accounting status word, the permanent educational disclaimer, and the
case-discard dialog. The agent colours above follow a standard because it
requires them, and nothing requires the alert colour.

IEC 60601-1-8 governs *visual alarm signals*, which are indicators that encode
priority by colour together with a flash rate. This interface has no indicator
lamp, filled banner, flashing element or priority tier, so the convention has
nothing to apply to.

The disclaimer settles the question against the convention. The alert colour
marks a line that is on screen *always*, while a monitor's alarm colours carry
meaning because they are absent until something is wrong. A permanent element
painted in a high- or medium-priority alarm colour would teach the opposite of
the convention it borrowed. Departing from the convention is also wanted for its
own sake. A teaching tool that looks unmistakably unlike a monitor cannot be
mistaken for one, which is the view this project's disclaimers already take.

*"Always" names where the line lives, not that it is in view on every screen
today* (`PL-JSY5`, 2026-10-18). Where the line lives, and the one gap in that,
are stated in the paragraphs on the disclaimer line in § "What this list requires
once the layout is the reader's". The argument above
needs only that the line is a permanent statement, not a conditional one, and
that is true at every window size.

The boundary of the supported run length is shown in the muted colour, not the
alert colour. Colouring a correct model's declared boundary as a fault would
teach a reader to distrust a sound number. § "Supported run length" gives the
rest of the argument.

The interface goes beyond AA in two places:

- **Chart traces can be told apart from each other, which WCAG does not
  cover.** SC 1.4.11 asks only for 3:1 against the *background*, yet reading
  one compartment against another is the whole lesson of this chart. W3C's
  Understanding document for that criterion excuses lines from contrasting
  with each other only where they overlap little. This chart's six traces
  start together, converge toward equilibrium and cross during wash-in and
  washout. No choice of colors can give every pair of six traces 3:1 against
  each other, so each trace also has a line style or marker, which the next
  section describes.
- **Each chart trace clears 3:1 against the panel, both as displayed and under
  simulated dichromacy.** SC 1.4.11 is defined on the color the display emits,
  so this bar is the project's own. Its reason is the criterion's purpose: a
  graphical object must be findable against its background, and a check that
  models only normal color vision cannot show that for a reader with
  dichromacy.

**The gridline grey is exempt from SC 1.4.11** (project owner, 2026-09-27,
ratified, over darkening the grey to 3:1; `PL-HKTB`). It colors the plot's
gridlines, the axis lines, the line between sections of the chart column and
the sliders' unfilled groove, at 1.31:1 against the panel. The criterion
applies only to a graphical object *required to understand the content*. The
values that the gridlines mark are shown in three other ways: each gridline
stands at an axis tick labeled in text at 5.00:1, the readouts state every
compartment's current value, and hovering over any drawn point shows its exact
value. The section line sits over a bold heading or a titled panel that
already marks the boundary. The groove is the edge of a slider whose handle
and filled track identify it.

**The ratios are computed from the interface's own colors**, with WCAG 2.2's
definitions of relative luminance and contrast ratio, each time the project's
checks run. Each requirement is a minimum ratio that named colors must reach,
such as 4.5:1 for a readout's text on its panel. A requirement whose colors
miss its minimum today is a shortfall. Each shortfall is recorded with the work
item that will fix it.
<!-- not-restated: 4.5 -->

**The window is always light, even on a computer set to dark appearance**
(project owner, 2026-09-20, ratified - chosen over leaving the host appearance
alone, and over growing a second palette for dark appearance). All 24
requirements are measured on the light theme's panel and page background. The
six compartment trace colors were chosen to meet their minimums under simulated
dichromacy on those same surfaces. A window drawn on other surfaces would show
color pairs that nothing has measured. A disabled control still takes its
colors from the computer's setting, apart from one disabled color that the
interface declares. That color's contrast is checked too.

**For developers.** The contrast check (`tools/contrast_check.py`) runs in
`make check`. It reads the color constants from `app/theme.py`, which contains
every one of them. A second check (`check_colors_live_in_the_theme`) keeps them
there. Each entry in the contrast check's requirement table names the colors,
the criterion and the reason for the minimum. The table records which colors
matter, and the check only evaluates it. Most entries are one foreground
against one background. Some elements show their edge in either of two colors,
such as an agent badge, which is a fill outlined in the agent's own text color.
The entry for such an element declares both colors. The element passes when
the better of the two meets the minimum, because a reader finds the edge by
whichever color contrasts more. Shortfalls are listed in the same table. The
check reports an error when a listed shortfall starts passing, so a fix cannot
leave its listing behind.

A color that a criterion does not apply to goes in the contrast check's
exemption table (`EXEMPT`), with one entry per use. Each entry gives the
criterion's grounds and cites the drawing code by symbol. An entry must rest on
an exemption that the criterion itself grants, never on a failing ratio. A
color that fails its minimum is listed as a shortfall. The checks that
`make check` runs count the exempt uses into the contrast report line. They
refuse an exempt name that `app/theme.py` does not define, and a color that is
both required and exempt on one surface.

Measuring text on the panel alone once hid a shortfall, fixed in `PL-X0RG`.
The label color gave 4.28:1 on the panel and 3.98:1 on the page, where the
run-status word is drawn.

A color that carries meaning both as text and as a graphic needs two
constants, because text needs 4.5:1 and a graphic 3:1, and one constant serving
both roles fails one of them. The accent color is the only such case. The
sliders' active track uses `ACCENT`, and "Running" and "Valid" use
`ACCENT_TEXT`, the same hue darkened until it is legible as text.
<!-- not-restated: 4.5 -->

The excuse for lines that overlap little comes from the Understanding document
for SC 1.4.11, read on 2026-09-07 in a copy the project owner supplied
(`PL-JX0Z`). Its line-graph example (Figure 38) says: *"The lines should have
3:1 contrast against their background, but as there is little overlap with
other lines they do not need to contrast with each other or the graduated
lines."* Its "Graphical Objects" section makes each line in a graph a graphical
object in its own right. Citing the Gestalt "law of continuity", it lets
**minor** overlaps between lines be ignored.

Because the criterion does not require pairwise separation, the contrast check
reports the contrast between every pair of traces without failing on it. It
enforces the 3:1 minimum against the panel, which the criterion does require.

The gridline grey's exemption (`GRIDLINE`) rests on the Understanding document
for SC 1.4.11. The document's line-graph example does ask 3:1 of a chart's
"background lines for the values", but there the gridlines are how a value is
perceived at all. Under the heading "Required for understanding", the document
says the criterion does not apply when "a graphic with text embedded or
overlaid conveys the same information, such as labels and values on a chart".
This chart passes the criterion's own test: imagine the gridlines invisible,
and ask whether the chart is still understood. The criterion's paragraph on
boundaries expressly excuses cases such as the section line and the groove.

Darkening the grey was refused because of the chart's visual order, in which a
gridline sits below a reference line and a reference line below a trace. A
gridline at 3:1 would be 87% as dark as the lightest trace (3.43:1), and that
order would collapse. Line widths of 1 / 1.5 / 2-3 px also carry that order.

Supporting dark appearance would mean measuring every requirement again on a
second pair of surfaces, and choosing all six trace colors again under four
vision models.

A declared color reaches the screen by one of three mechanisms. Most of the
interface is drawn by stylesheets, all composed in one module
(`app/stylesheets.py`) from the theme's color constants (`PL-Y4YX`). Some
widgets are painted from Qt palette roles instead: an entry's fill, a spin
box's stepper, a list's rows and its scroll bar, a check box's indicator and a
dialog's own surface. A stylesheet would cost them the native stepper and the
check box's tick. For those widgets, a function
(`qt_widgets.declare_interface_colours`) declares the same theme colors as
palette roles. It maps PANEL and INK to `Base` and `Text`, MUTED to
`PlaceholderText`, and PRIMARY and PANEL to `Highlight` and `HighlightedText`,
so the pairs on screen are pairs that the requirement table already measures.
It writes only the `Active` and `Inactive` color groups.

The third mechanism is the fallback that keeps the window light under a dark
host: a function (`qt_widgets.declare_application_colours`) writes the same
roles on the `QApplication` itself. Without the fallback, Qt's application
palette follows the host appearance. On a machine set to Dark, everything this
interface did not name would then take a dark theme's surfaces, around a light
window. No per-widget declaration can cover all of that, because every widget
beneath a styled widget resolves its colors from the application palette
rather than from the styled ancestor.

The interface sets a palette, which is authoritative at any depth, and does not
rely on a color-scheme hint. Qt 6.8 documents its color-scheme setting
(`styleHints().setColorScheme`) as a hint: "overriding the color scheme is not
supported on all platforms". On 2026-09-20 the setting was seen to be ignored
outright: it still reported `Unknown` after being set.

Disabled controls follow the host because all three mechanisms leave the
`Disabled` color group to the platform. Declaring a disabled color is a
decision that the project's rule for interface colors governs
(`.claude/rules/ui-color.md`). The splitter handles are enabled (`PL-W9P6`), so
the border between two areas shows the page's `BACKGROUND` under a dark host
too, rather than the host's dark surface. A test
(`test_the_border_between_two_areas_shows_the_page_rather_than_the_host`)
checks this (`PL-05M4`).

Tooltips also follow the host, because they draw from `ToolTipBase` and
`ToolTipText`, which are outside the declared roles. This interface uses no
tooltip today.

The dark-appearance test (`tests/integration/test_dark_appearance.py`) renders
the dashboard and both dialogs under the palette a dark host supplies. It
fails on any content widget that resolves to that palette, and it checks the
chrome and the untouched `Disabled` group against the same host. Under that
host palette, 94.3% of the page scroll bar's pixels are darker than mid-grey
without the interface's own palette, and none are with it.

A second test (`tests/integration/test_simulation_view.py`) catches any control
that declares no color, including one added later. It builds the whole
dashboard under a foreground color that this interface never uses, and fails
on any control that paints its own content and resolves to that color. It
exempts only kinds of control that draw no text, and names each kind with its
reason. A requirement exists only where somebody wrote a color down, so the
contrast check counts those kinds into its report line. Without that count, a
control that declares no color would appear on neither side of the report
line, and the line would show it as covered (`PL-4L49`).

The cited standard references, the screen-colour approximations and the
accessible foregrounds are kept together in `app/theme.py`, so that the
agent-colour mapping can be audited as one unit. Every foreground and background
pair must meet WCAG 2.2 AA contrast. Each Munsell original was converted to sRGB
via Illuminant C, chromatically adapted to D65. The dichromacy figures were
computed by `tools/contrast_check.py` with the Brettel 1997 projection recorded
under § "The six compartment traces". A test pins them, so a colour change
cannot leave them out of date (`tests/unit/test_contrast_check.py`). Tests in
`tests/unit/` check that the agent name is shown beside its colour in the
selector's options and in the header badge.

The alert colour is `WARNING` in `app/theme.py`, and the muted colour is
`MUTED`. Two requirements apply whatever alert colour is chosen. The chosen
colour must still meet the interface's contrast target, which
`tools/contrast_check.py` enforces. The ISO 5360 agent colours stay as they are,
because they identify an agent and carry no urgency.

The alert-colour decision applies to the Qt port as much as to the current
interface. The port chooses its palette afresh, and an indicator-shaped element
could first appear in it, so the port must not arrive with a monitor's priority
palette.

IEC 60601-1-8's mapping of priority to colour could not be established from a
primary source, and the secondary sources disagree. Three independent reports
give the low-priority colour as cyan, as blue, and as "green or blue". The
alert-colour decision does not depend on the mapping.

### The six compartment traces: what separates them

Each compartment's trace has its own line style, and color is only a second
cue. Six traces share one plot, and a trace mistaken for another gives a wrong
clinical value.

| Compartment | Line style | Dash pattern (px) | Width (px) |
| --- | --- | --- | --- |
| Circuit | solid | — | 3 |
| Alveolar | long dash | 10 on, 4 off | 3 |
| Mixed venous | short dash | 4 on, 3 off | 2 |
| Vessel-rich | even dash | 6 on, 6 off | 2 |
| Muscle | dotted | 2 on, 3 off | 2 |
| Fat | dash-dot | 12 on, 4 off, 2 on, 4 off | 2 |

The legend entry beside each checkbox names its trace's style in words, so a
reader can learn every style from the legend alone.

**Color cannot be the first cue, because some pairs of trace colors are almost
equally bright.** The closest pairs are vessel-rich and fat, and mixed venous and
fat. No other choice of colors fixes this. Each color has at least the 3:1
contrast against the panel that WCAG success criterion 1.4.11 requires, both as
displayed and as simulated for protanopia, deuteranopia and tritanopia. The
colors are chosen to label their compartment and to clear that minimum.

**The colors decide which line style goes on which compartment.** The two traces
whose colors are hardest to separate get the two styles that are easiest to
separate by shape. The next pair gets the next easiest, and so on. Fat's
dash-dot therefore differs in dash length, gap length and rhythm from both the
vessel-rich even dash and the mixed venous short dash. The one pair of styles
that a reader could confuse is dotted, with 2 px dots, and short dash, with 4 px
dashes. That pair goes to muscle and mixed venous, whose colors are the second
most widely separated pair among these six (1.45 in the table below, after
circuit and alveolar at 1.62).

**With two runs on the plot, at most two compartments are drawn** (`PL-HLD5`,
`PL-8PSW`). The cap applies to the plot only. All six readouts stay on screen for
both runs (§ "Minimum displayed outputs").

**Line width shows the run.** Each compartment keeps its line style and color.
The first run's traces are wider, and the second run's keep the width in the
table above. A reader compares the two widths only between the two traces of one
compartment, which are always adjacent. A branched run repeats its parent exactly
up to the branch point, where the two runs diverge (planned-milestone item 12).
Before that point the two traces of a compartment coincide, so the narrower one
is drawn on top, where the wider one cannot hide it.

**A solid vertical line marks a branch point, and a finely dashed one marks a
control change.** Both lines are the same color, so only their dash pattern and
the legend's words tell them apart. A reader must not confuse the two, because
reading a branch point as a control change would attribute the runs' divergence
to the wrong cause.

**For developers.** A script computes every figure in this section
(`tools/contrast_check.py`), and a unit test checks the script's results against
these figures (`tests/unit/test_contrast_check.py`). The script runs as part of
`make check`, and its `--matrix` option prints the pairwise table below.

Each trace has this contrast against the panel, as displayed (Normal) and as
simulated for each dichromacy:

| Trace | sRGB | Normal | Protanopia | Deuteranopia | Tritanopia |
| --- | --- | --- | --- | --- | --- |
| Circuit | `#176B87` | 6.02 | 5.67 | 6.21 | 6.02 |
| Alveolar | `#159789` | 3.61 | 3.23 | 3.84 | 3.63 |
| Mixed venous | `#7C3AED` | 5.70 | 5.96 | 4.68 | 5.55 |
| Vessel-rich | `#DC2626` | 4.83 | 7.18 | 4.14 | 4.84 |
| Muscle | `#D17206` | 3.43 | 3.96 | 3.22 | 3.46 |
| Fat | `#64748B` | 4.76 | 4.74 | 4.76 | 4.77 |

The contrast between each pair of traces is far lower, and the design in this
section rests on it:

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

Other colors would not help, because the closest pair among any six colors has a
contrast ceiling of $`21^{1/5}\approx1.84`$. Contrast ratios multiply along a
bounded scale: black to white is 21:1. With $`n`$ traces sorted by luminance, the
smallest gap between adjacent traces is largest when the gaps are equal. Requiring 3:1 against the white panel
caps each trace's luminance at 0.30, which lowers that ceiling to **1.48**. A
search over lightness, with each hue and saturation held fixed, reaches **1.28**
at best for the worst pair across the four vision models. It gets there only by
making four of the six traces nearly black, which loses the hue that lets a
reader name a trace. Even then, 1.28 is less than half of 3:1. A project rule
(`.claude/rules/ui-color.md`) records this result, so that the search is not
re-run each time a color changes.

Two colors were darkened to meet the 3:1 minimum against the panel, not to
improve separation. The alveolar trace was `#18A999`, at 2.93:1 as displayed
and 2.61:1 simulated for protanopia. The muscle trace was `#D97706`, at 3.19:1
as displayed and 2.98:1 simulated for deuteranopia. Each new color keeps the
old hue and saturation exactly, and is darkened to the lightest shade that
clears 3.2:1 in all four vision models. The extra 0.2 keeps the shipped color
off the 3:1 boundary. The $`F_A/F_I`$ wash-in plot takes its single line's
color from the alveolar trace's constant, so it had the same shortfall, and
darkening the alveolar color fixed it.

The dichromacy figures use Brettel, Viénot and Mollon's projection onto the
reduced stimulus surface that each dichromacy leaves. That surface is defined by
the neutral axis and by the monochromatic stimuli that a dichromat and a normal
trichromat see as the same hue.[^brettel1997] The simulation uses the
two-half-plane form, because the single-matrix simplification of Viénot,
Brettel and Mollon (1999) is not accurate for tritanopia.[^vienot1999] The
coefficients are the precomputed sRGB-space forms published by libDaltonLens,
which derives them from Brettel's construction over the Smith and Pokorny (1975)
cone fundamentals.[^daltonlens]

The figures support one comparative claim: no arrangement of these six colors
separates the traces, whichever observer is assumed. The figures have three
limits:

1. The simulation renders, for a normal observer, an approximation of a
   dichromat's *appearance*. It does not measure dichromatic perception. It
   models the three dichromacies, not the far commoner anomalous trichromacies,
   so it does not represent their milder losses.
2. The script applies WCAG's relative-luminance formula to the simulated output.
   The formula was not defined for that use, because success criterion 1.4.11 is
   written for the color the display emits.
3. The calculation concerns luminance only, so it says nothing about the
   difference in hue that a reader with normal color vision uses.

Color stays with the compartment when a second run is added, because a cue
whose meaning changed between one run and two would invite misreading a clinical
value.

Because the colors cannot separate the traces, width can show the run only under
a cap on the compartments drawn. The six compartments already use two widths,
2 px and 3 px, which sets the cap at two.

The first run is widened, rather than the second narrowed, so that no trace is
drawn narrower than 2 px. A 1 px antialiased line renders lighter than its color
and would fall below the 3:1 minimum against the panel that every trace must
meet.

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

In all six compartments, every modeled concentration and relative partial
pressure is displayed to **0.01 percentage points**. The delivered-agent
setting uses the same resolution, in the readout beside its slider and in the
label shown while the slider is dragged, so the setting and the values it
produces are read at one scale. A positive value that would round to `0.00%`
is displayed as `<0.01%`, so `0.00%` means only that no agent has arrived, as
before a run starts.

Each digit shown is accurate for this model with its parameters. No displayed
value can be trusted to its last digit as a prediction about a patient
(§ "Known limitations").

**For developers.** One test enforces the display resolution
(`test_format_percent_uses_the_documented_display_resolution`), and another
enforces the `<0.01%` form
(`test_format_percent_marks_a_value_below_the_resolution`).

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

**The MAC readout shows the MAC multiple to 0.01 MAC.** The smallest change it can
show is 0.02 percentage points of sevoflurane, 0.012 of isoflurane and 0.06 of
desflurane. Each is at least the percent readout's 0.01 percentage points, because the
MAC multiple is calculated from the percent concentration and can be no more precise
than it. The two readouts round separately, so the MAC readout can occasionally change
while the percent readout stays the same. The three per-agent figures have no test yet
(`PL-19W8`).
<!-- not-restated: 0.06 -->

A MAC multiple above zero but below 0.01 MAC shows as `<0.01 ×MAC`. The `<` sign
matters more on the MAC readout than on the percent readout, because a filling
compartment reaches 0.01 percentage points before it reaches 0.01 MAC. In between,
`0.00 ×MAC` would contradict the percent readout above it, which already shows the
compartment filling.

**For developers.**
The MAC resolution is derived from the percent resolution rather than stored beside
it, so that re-measuring the percent resolution never leaves a second number to
update. Divided by the agent's MAC in percent (`mac_percent`), 0.01 percentage
points is 0.005 MAC for sevoflurane, 0.0083 for isoflurane and 0.0017 for desflurane.
The MAC resolution is the finest power of ten at or above the coarsest of these,
isoflurane's 0.0083. A test repeats this arithmetic for every shipped agent
(`test_the_mac_resolution_is_derived_from_the_percent_resolution`) and fails if
adding an agent or changing the percent resolution would make the MAC readout finer
than the percent supports. Another test checks the `<0.01 ×MAC` form
(`test_format_mac_multiple_marks_a_value_below_the_resolution`).

#### What the model keeps that the display rounds

**Only the display rounds a value, and only once.** The model computes and keeps
every value at full precision, including the values the chart is drawn from. A slider's value reaches the model without rounding. The readout is the only place between a slider and a pixel where resolution is lost. The model keeps about nine
orders of magnitude more precision than the display shows.

**For developers.** Everything upstream of the formatter carries full binary64
precision: the compartment states, every integration step, the mixed-venous and
tissue transfers, and the states the chart is drawn from (`DrawnWindow`). Nothing
in the model's code (`core/`) rounds. The snapshot fields that the interface
reads are raw fractions. The figure of nine orders of magnitude applies to the
exact method that the simulator uses. A test runs the model twice, with delivered
concentrations that differ by an amount four orders of magnitude smaller than
the display resolution (`test_the_model_keeps_precision_the_display_throws_away`).
The two runs must reach different states and must still look identical on the
display.

#### Comparing two readouts

**A reader can rely on which of two compartments the readout row shows as higher,
except possibly while the two cross.** The interface therefore adds no warning or
marker when readouts are compared. Where seven panels fit, the six compartment readouts
and the clock sit in one row, so that the readouts can be read *in order*: the circuit
leads the alveoli, and the alveoli lead the tissues.
§ "The readout row's width condition" below says what happens when seven panels do not
fit.

When a reader compares two readouts, the simulator's calculation error could mislead them
only by reversing which of the two is shown as higher. A test compared every pair of the
six readouts at every time step, for all three agents, in every run that
§ "Independent-solution test" describes: 1 485 000 pairs of readings in all. The
simulator's readings **never** disagreed with those of the independent solution about
which compartment is higher, even where the gap was tiny (checked 2026-10-17).

This result comes from runs on one computer platform and is not a guarantee.
Because rounding to a fixed number of decimals never reverses the order of two
values, the display can show two compartments in the wrong order only where the
simulator and the independent solution put them in opposite order. Such a reversal needs
a true gap smaller than the two compartments' calculation errors added together. In
every run, the simulator's gap between any two compartments differed from the
independent solution's by at most $`1.1\times10^{-12}`$ as a fraction, not a
percent. True gaps that small do occur while two compartments cross, so a reversal
is arithmetically possible there.

**A gap that a reader works out from two readings can differ from the true gap by
up to one count of the last displayed digit.** Each reading is rounded to that
digit. The gap carries the rounding of both readings and the solver limit in the paragraph above. The simulator's calculation error does not make the gap less accurate than either reading. The interface shows no gap between two readouts.

**For developers.** Two tests enforce the claim about which compartment is shown
as higher. Each covers one half of the path from the model to the readout and can
fail on its own. The first bounds the simulator's calculation error against the
independent solution
(`test_exact_step_matches_the_independent_solution_everywhere`). The second checks
that the interface's formatter, `format_percent`, never shows a higher fraction as
a lower percent (`test_format_percent_preserves_order` in
`tests/unit/test_formatting.py`). It covers the "<0.01%" reading below the display
resolution and both sides of every value at which the last displayed digit changes.
Together the two tests mean that no reversal can occur at a true gap above twice the
first test's tolerance: $`1.0\times10^{-7}`$ counts of the last displayed digit. A
third test makes the comparisons described above, reading each value through the
interface's formatter (`test_displayed_ordering_reverses_only_at_a_crossing`). It
allows a reversal where the true gap is below the first two tests' threshold of
$`1.0\times10^{-7}`$ counts, because one is possible at a crossing. It fails only when
one of those tests fails, so it records the result and adds no evidence of its own.

The claim about a gap's calculation error rests on one property of the model: within one
time step, it updates every compartment from the values at the start of that step.

#### One resolution for all six readouts

**All six compartment readouts show the same number of decimal places, for two
reasons.**

- **The six readouts are compared with one another.** If they showed different
  numbers of decimal places, digits of different place value would sit in the
  same position, and someone scanning the row would misjudge a value by a factor of ten. That is a property of the reading task, whatever the solver does.
- **The effect of parameter uncertainty varies much less across the row than the
  values do.** The one-SD displacements tabulated above run from
  $`8.7\times10^{-4}`$ to $`6.8\times10^{-2}`$ percentage points across all six
  compartments and all four coefficients. That is a spread of less than two
  orders of magnitude, on a row whose *values* span four. One number of decimal
  places therefore fits all six readouts. It is set by the compartments where
  the displacement is largest, so it is conservative where the displacement is
  smaller.

#### The readout row's width condition

**The readout row's width decides how many panels share a line.** Every panel
takes exactly one column. The panels sit seven across wherever all seven columns
fit the row, four per line where they do not, two where four do not fit, and one
below that. Each column is as wide as the widest value its panel can show: the
clock's longest elapsed time, or a compartment's widest percent and MAC
multiple. The clock's width therefore widens no other column. In every
arrangement each panel keeps that width, so no value is wrapped away from its
unit. The widths at which the row steps down depend on the font and the display
scale. With the font that the project's tests use, for example, the row is seven
across from 1005 px, four across from 591 px and two across from 310 px (measured 2026-10-18). Those figures illustrate the rule and do not specify it.

When fewer panels share a line, both reasons given above for the row still
apply, but not equally.

- **Reading the row in order becomes harder.** When the row is too narrow for
  seven across, the six readouts other than the clock sit on two or more lines,
  so comparing them takes a scan across the lines instead of a single glance.
  The readouts' ordering is still faithful, because it depends on the displayed
  values, not on where they sit.
- **The uniform resolution still applies at every width.** The grid aligns the
  values within each column, so a reader compares two panels against a common
  position, whether they sit side by side or stacked.

**The row's width follows the window, never the layout below it.** The readouts
sit in a region above the part of the window that the reader divides into Areas
(§ "Minimum displayed outputs" -> "What this list requires once the layout is
the reader's"). The row's width therefore stays the same when the reader splits
or joins an Area, drags a border or switches Workspace. Only two things change
it: the window's width, and how the region divides that width between the
readouts and the control-change record.

**The window opens maximized, so the row starts in the widest arrangement that
the screen allows.** Maximized is not full screen: the title bar and window
controls stay, and on macOS the window is zoomed. A maximized window gives the
region the screen's available width less the window's frame. A reader who
un-maximizes the window returns it to its normal size: a fixed fraction of the screen's available area, centred. At that size the row steps down the arrangements above wherever its width requires. A screen too narrow for seven across even when maximized opens on a narrower arrangement, because maximizing changes the row's width, never the rule that picks the arrangement.

**On a 1366 px laptop screen, one of the commonest widths, the row opens seven
across, with one run or two** (measured 2026-10-18). In compare mode the two
runs share one readout row. On that screen the longest control-change lines do
not fit the record's column, so the record wraps them. It breaks them only after
the time or after the arrow, so every value stays beside its unit.

On a 1280 px screen the control-change record takes part of the region's width,
and whether the row still opens seven across has no test yet (`PL-LKX7`).

**For developers.** A function sets the row's column count from its width
(`readout_columns` in `src/anesthesia_sim/app/dashboard_frame.py`). A constant
lists the four arrangements (`READOUT_ROW_LADDER`). Column widths come from the
font that the interface draws with, so the code fixes no pixel width that
another font or display scale would make wrong. The step-down widths above are
in logical pixels, and the tests draw with an offscreen font. One test reads
those widths from the row instead of asserting them
(`test_the_readout_row_reflows_where_its_panels_stop_fitting`). Another enforces
the column count and each panel's one-column span
(`test_every_readout_reserves_a_qualifier_line_and_an_equal_column`).

The readouts sit in their own region (`SimulationView.unconditional_region`). A
test checks that the region stays outside the Areas
(`test_no_unconditional_value_sits_inside_the_layout_container`). The region
gives 0.82 of its width to a left column for the readouts and 0.18 to a right
column for the control-change record. These are the shares that the chart
panel's Area and the sidebar's Area had in the layout that the dashboard first
opened on. In that layout the record was as wide as the sidebar beneath it. The
Workspaces that ship now divide the width differently, and the region keeps its
own shares. The left column never narrows below its own minimum width.
<!-- not-restated: 0.18 -->

The window is opened maximized (`showMaximized()` in
`src/anesthesia_sim/app/main.py`). A constant in the same file gives the
window's normal size as a fraction of the screen's available area
(`WINDOW_SCREEN_FRACTION`). Opening maximized matches the default window state of
the reference design that the interface follows (`docs/interface-provenance.md`
§ "Adopted").

With the tests' font, a 1366 px window gives the region 1320 px (measured
2026-10-18). The right column takes 235 px and the left column 1073 px, which is
68 px more than the 1005 px that seven across needs. A 1280 px screen gives the
region about 1234 px (measured 2026-09-27, with the tests' font). Two tests
check that a 1366 px window opens the row seven across in compare mode
(`test_two_runs_share_one_readout_block_whose_values_name_their_runs` and
`test_a_1366_px_window_opens_one_run_s_readout_row_on_seven_columns`). A function
wraps the control-change record (`wrapping_between_parts`).

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

The screen shows time in one form. The displayed clock, the time stamp on each
recorded control change and the chart's axis ticks are all durations. Each part
of a duration carries its own unit: `45s`, `1m30s`, `1h23m45.6s`, `24h`. A part
that is zero is left out. Tenths of a second appear only where there are some.

The one exception is the time span that the chart draws. It is written out in
words, such as `15 minutes` above an axis whose last tick reads `15m`. The
reader picks that phrase from a selector and sees it again in a caption.
§ "Displayed precision" sets the precision at which each form is shown.

**For developers.** The displayed clock and the stamps use the axis's form because all three are on
screen together. A control mark stamped `5400.0 s` on an axis reading `1h30m`
would leave the reader to convert between the two by hand. At the supported
24-hour run length, a clock in seconds would read `86400.0 s`. That figure shows
false precision for a limit that this document states in hours. The tenths of
a second are there so that a stamp identifies the simulation step at which it
was taken.

The span's wording does not have to fit in a tick's width, because neither the
selector nor the caption is a tick label. § "The chart's time base" explains why
the span is written in words.

**The chart is read for shape, so its resolution is coarser than the
readouts'.** It plots the same percentages on a shared linear axis that runs
from 0 to 3 ×MAC of the agent in use, and a second axis on the right shows the
same position in MAC multiples. Its resolution is set by pixels rather than by
decimals. Every number the chart offers, in the readout row and in the hover
readout that § "The chart's hover readout: what the tooltip may show" derives
below, is shown at the resolutions above. The MAC axis is labelled on round MAC
values, in half-MAC steps, which the fixed 3 ×MAC range gives for every agent,
so a gridline that a reader learns under one agent means the same thing under
the next. § "The chart's vertical range is set in MAC, and fixed" above
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
reference adult's flows, and have no test yet (`PL-19W8`). At those settings,
one step of 0.1 L therefore lies between about two-fifths of an SD and six SDs,
from 1 h to the 24 h limit, which is inside the band the readouts' derivation
admits. A step of 0.01 L would fall to about a twentieth of an SD by 24 h. At a
higher dial setting the shifts are larger, and no test yet derives the step
there (`PL-0P3F`). Delivered agent carries no
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
| The delivered total | Millilitres of liquid | 0 | 1 mL | One SD of the measured liquid density |
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
coefficients give the same answer. At 24 h, the one-SD shifts measured above at
1 MAC with the reference adult's flows, 0.19 L of sevoflurane vapour, 0.18 L of
isoflurane and 0.23 L of desflurane, are 1.04, 0.92 and 1.10 mL of liquid. So
at those settings one step of 1 mL is about one SD, and a step of 0.1 mL would
be a tenth of one.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**The delivered total in millilitres of liquid is shown in whole millilitres.**
The delivered agent is the dial times the flow times the time, and its
conversion to liquid at the 20 °C reference is exact. Its only uncertainty in
liquid is the measured density's, which grows in proportion to the total. At
sevoflurane's largest supported total, 8% at 10 L/min for 24 h, one SD is about
3.3 mL. So a step of 1 mL is about 0.3 SD, and no supported setting makes it
finer than the readouts' seventh of an SD. A step of 0.1 mL would be about a
thirtieth.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

**A cost is shown to three significant figures, and a price per millilitre to
four.** A cost is the delivered agent in liquid times the reader's price per
millilitre (§ "A cost at the reader's price"). The price is the reader's own
figure, so it carries no modelled uncertainty. The cost's only modelled
uncertainty is therefore the liquid figure's. The largest relative SD of a
stored density is sevoflurane's, 0.0008 g/mL against 1.5203 g/mL,
or 0.053 %. That SD is relative, so the cost's precision is a count of
significant figures, not of decimals. A count of n figures has a smallest
relative step of 1 in (10^n - 1), at a value such as 999. At three figures that
is 0.10 %, coarser than one SD of the density, which the one-sided bound allows.
At four it would be 0.010 %, finer than one SD. A cost is never shown finer than
**a hundredth** of its currency, which is the smallest unit of most currencies.
For example, 0.68 reads `USD 0.68`, not `USD 0.680`. A positive cost below a
hundredth reads `USD <0.01`, and a run that has delivered nothing reads `USD 0`.
The price per millilitre takes four figures, the fewest at which its rounding
moves the product of the figures shown by at most half of the cost's smallest
step. At four figures that rounding is at most 0.5 in 1000 of the price, and
half of the cost's smallest step is 0.5 in 999 of the cost. The liquid volume's
whole millilitre is then the only rounded figure in the reader's multiplication
that is coarse enough to matter. It can make the product miss the cost by up to
about half a millilitre's price, and the readout says that the figures are
rounded (§ "A cost at the reader's price").
<!-- provenance: data/agents/sevoflurane.json liquid_density.standard_deviation_g_ml = 0.0008 -->
<!-- provenance: data/agents/sevoflurane.json liquid_density.g_ml = 1.5203 -->

**The stored total has no liquid precision, and is refused in liquid.** A store
converted to liquid reads 5.8% high (§ "Known limitations"). That error grows
with the amount. At 17 mL of liquid it is already a whole step of 1 mL, and in
a long run it is several steps. No number of decimals can make a figure with a
known bias of several steps read correctly, so the stored total keeps litres of
vapour, as the accounting panel shows it.

The agent cost display is the only part of the simulator that converts an amount
to liquid. It converts only the delivered agent, so no figure it shows carries
the 5.8 % error. It reads the delivered amount and the vapour-to-liquid ratio of
the agent in use from the same moment of the run, so it cannot pair one agent's
vapour with another agent's ratio. Using desflurane's ratio would misstate
sevoflurane by about 13 %. The same display multiplies the liquid figure by the
reader's price to give a cost (§ "A cost at the reader's price").

**The simulator derives each agent's vapour-to-liquid ratio, as the first table
in § "Agent amount" does.** It stores the liquid density and the molar mass, each with its
source, and the temperature at which the density was measured. It refuses to
load a density measured at any temperature other than 20 °C, because it has no
temperature correction. It computes the molar volume from the gas constant,
20 °C and one standard atmosphere. Neither the molar volume nor the published
constants are stored.

A test checks the derived ratios against Biro's within 1 % and against Gas
Man's within 0.5 %. It also computes the cost of the isoflurane delivered in
the Gas Man Workbook's Exercises 14-1 and 14-2 with the derived ratio. Those
costs must match the book's, allowing for rounding to the cent and for Gas
Man's constant, which is rounded to a whole millilitre.

**For developers.** `app/formatting.py` keys each precision by the amount and
the unit, in `AGENT_AMOUNT_DISPLAY_PRECISION`. Each entry is an
`AgentAmountPrecision`, which holds the amount, the unit and the count shown. It
reads the finest count from the derivation for that amount and unit, so no
caller can pass a looser bound. It refuses a finer count when it is built. A
precision that a reader could set would be built the same way.
`test_the_exhausted_total_in_millilitres_of_liquid_claims_no_more_than_in_litres`
repeats the litre-to-millilitre conversion for every shipped agent from the
stored molar mass and density.
`test_the_delivered_total_in_millilitres_of_liquid_is_shown_in_whole_millilitres`
computes each agent's largest supported total and its SD from the stored
densities. Whole millilitres replaced a tenth on 2026-11-04 (project owner,
ratified, over keeping the tenth and over four significant figures, `PL-SP6H`).
`test_the_cost_s_and_the_price_s_precisions_follow_from_the_density_and_the_cost`
computes both counts from the stored densities.
`test_a_unit_with_no_derived_precision_is_refused` enforces the refusal of the
stored total in liquid.

Each agent's file in `data/agents/` stores the density as `liquid_density`,
with its spread and measurement temperature, and the molar mass as
`molar_mass_g_mol`. The `sources` entry for each says why no tier-1 source
(§ "Source hierarchy") exists. The vapour-to-liquid ratio is derived in
`core/liquid_agent.py` and checked in
`tests/reference/test_published_vapour_to_liquid.py`, within 1% of Biro's
constants (`test_the_derived_ratio_is_within_one_percent_of_biros_published_constant`)
and within 0.5% of Gas Man's
(`test_the_derived_ratio_is_within_half_a_percent_of_gas_mans_20_celsius_constant`). The agent cost display reads the
amount and the ratio from one snapshot of the run, which pairs the ratio with
the running agent (`SimulationSnapshot.agent_vapour_per_liquid`). A unit test fails if any other
code under `src/` calls the conversion to liquid (`liquid_volume_ml`).

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
millilitres of vapour. Each of the four stored partition coefficients was
perturbed by one published SD, one at a time, at 1 MAC with the reference
adult's flows. The amounts were read every second for the first 20 minutes, and
at 60 min, 180 min and 24 h. The shift runs from almost nothing, in the circuit
in the first seconds, to 216 mL, in desflurane's fat at 24 h, because the
amounts themselves span that many orders of magnitude. So no single number of
decimals keeps every amount's step inside the band that the readouts'
derivation admits. A step of 1 mL is a two-hundredth of one SD in desflurane's
fat at 24 h, the kind of false precision that stopped the run totals at 0.1 L.
A step of 10 mL is still a twenty-second of an SD there. It would also print
sevoflurane's and isoflurane's venous blood as "<10 mL" for almost the whole
first hour, which is the flat reading that the readouts' lower limit refuses.
That blood holds about 0.18 mL at 1 min, 6.6 mL of sevoflurane at 10 min, and
9.7 to 10.0 mL at 60 min.
<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->
<!-- not-restated: 10 mL, 10.0 mL -->

Relative to the amount, the shift is narrow. In venous blood and the three
tissue groups it is 1.4% to 12% of the amount. In the circuit and the alveoli it
is below 3%, because the dial sets them and a coefficient barely moves them. Two
significant figures put the last digit at 1% to 10% of the amount. As measured,
one step of that digit lies between a tenth of one SD, in desflurane's venous
blood at 79 s when it holds 0.99 mL, and many SDs in the circuit. These figures
have no test yet (`PL-19W8`). The one-sided bound allows the coarse end. The
fine end is finer than the readouts' seventh of an SD, but only in the first two
minutes, while venous blood fills. Three significant figures would put one step
at a hundredth of an SD. That is finer than the readouts' third decimal, which
was refused at a seventieth of an SD, and the totals' second decimal, which was
refused at about a twentieth. One significant figure would print fat's amount in
steps of 1000 mL by 24 h. So two is the finest number of figures the parameters
support, and it is the number chosen.
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

When the pointer rests over a trace, a small box appears with the value under the
pointer. This box, the hover readout, supplies for itself every qualifier that the
readout panel takes from its surroundings. The panel's six values sit under a
heading that names the agent and calls them modelled, beside a legend that names
each compartment. The panel's alveolar entry also carries the gloss
`end-tidal-equivalent`. The box floats over the plot and can cover the heading it
would otherwise be read under. It is the one place in the interface where a number
appears with nothing around it.

The box is also the display that a reader consults most deliberately. A value in
the readout panel is glanced at while a run plays, but a value under the pointer
is one that somebody went looking for. So the box is the display most likely to
be written down, and the one where a value mistaken for a measurement costs most.

#### What it shows

The box has three lines: the run context, what the value is, and the value.

```
Modelled sevoflurane · 20m8s
Alveolar (end-tidal-equivalent)
1.43%   0.71 ×MAC
```

The qualifiers come first, so a reader reaches `1.43%` only after passing
"Modelled" and the compartment. A qualifier below the number would come too late,
because the number has already been read.

1. **Run context: "Modelled", the agent, the run when more than one is drawn, and
   the instant.** "Modelled" appears on every hover, not only for the compartments
   that a monitor also measures. The agent is there because one percentage means
   different things under different agents: 1.43% is 0.71 MAC of sevoflurane and
   0.24 MAC of desflurane. The instant is printed to the hundredth of a second, in
   the form that the clock, the time axis and the time stamp of each control change
   also use, such as `20m8s`. It is the exact instant of the value beside it, not a
   rounding of it.
2. **What the value is: the compartment, with its gloss where the readout panel
   has one.** Two compartments carry a gloss, `Alveolar (end-tidal-equivalent)`
   and `Circuit (inspired)`, because a clinician would most readily set those two
   beside a monitor reading (§ "Minimum displayed outputs"). The other four carry
   none, as in the readout panel.
3. **The value, in percent and as a MAC multiple.** The readout panel shows the
   same pair. The chart has an axis for each, and a single number could be read
   against either.

Every number in the box is formatted as the readout panel formats it, never left to
the charting software's default (§ "What a chart library prints instead, measured").
The MAC multiple divides by the same MAC as the MAC axis and the readout panel.

**For developers.** Two functions in `app/chart_frame.py` produce the three-line
form (`format_trace_hover` and `format_wash_in_hover`). Every number in it comes
from `app/formatting.py`: `format_percent`, `format_mac_multiple` and
`format_elapsed`. The multiple divides by the snapshot's own MAC (`mac_percent`).
Any other divisor would be the traceability failure that `CLAUDE.md` forbids,
arriving through the display that looks least like a calculation. The qualifiers
lead because of the general rule in `.claude/rules/expert-review.md`: prefer an
interface that prevents an error to one that warns after it.

**For developers.** The instant that the box prints is exact, because the
chart's columns fall on whole hundredths of a second (`PL-T5NJ`) and every other
drawn instant falls on a simulation step. The box rounds each instant to a
hundredth of a second (`HOVER_INSTANT_RESOLUTION_S`), which removes only
floating-point noise.

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

The box follows the rule for naming the run (§ "Naming the run in a
comparison"): a concentration that does not say which management produced it is
the correct number under the wrong patient context. The rule matters more for the box than for the panel, which sits
in a labelled block.

Pointing at one trace does not pick out one run. Where two runs' traces for one
compartment lie close together, the pointer is within the hover radius, 12 pixels
(px), of both. The percent axis tops out at 3 MAC for every agent, so the slow
compartments lie close to zero (§ "MAC multiples as a display unit"). All along the time axis, a pointer within reach
of one run's fat trace is within reach of the other's too, even under the widest
difference in management that the interface permits. The two runs' fat values
can still differ. Take a sevoflurane case held at 1 MAC, with a second run (the
branch) forked from the first (the trunk) at 10 min with the vaporizer turned
off. At 3492 s the fat value reads either `0.03%   0.02 ×MAC` or
`0.01%   <0.01 ×MAC`, depending on the run. That is a threefold difference in
stored agent, between a run still carrying agent and a run 48 minutes into
emergence. The slow compartments are the ones this chart exists to teach.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

A single run goes unnamed because there is nothing to tell it apart from, and a
name would suggest a comparison that is not on screen. A reader always sees when
a second run is drawn, because it brings a second legend entry, a second readout
panel and a second set of traces.

**For developers.** The run goes on line 1, which already gives the run context,
so the box keeps its three lines. While two runs are compared, the run name is
the only part of that line that tells them apart. The agent is always the same:
the code that assembles the chart refuses runs that differ in agent
(`assemble_chart_frame`), because they share one MAC axis and one set of clinical
references. The one argument for a fourth line is that a reader scans a separate
line but may miss a word in the middle of one. That matters because the run under
a resting pointer can change. But the value on line 3 changes at the same moment,
so the reader gets two cues.

The run name appears on the same condition as the difference in line width
between runs: the code that styles each run's trace widens none until a second
run exists (`run_trace_style`).

The table gives the share of the axis on which both runs' points for one
compartment lie inside the hover radius. The figures come from simulating the
branched case on 2026-09-17 on the reference adult, with the branch's management
at the fork varied. The 60-minute axis was 900 px wide and 360 px tall, a scale of
4.00 s and 0.0167% per pixel. The percent axis had its shipped top
(`CHART_AXIS_TOP_MAC`). At the time, the hover reported the single drawn point
nearest the pointer across every run (`nearest_trace_point`).

| Branch's management at the fork | Alveolar | Fat |
| --- | ---: | ---: |
| doubled to 2 MAC | 1.6% | 100% |
| raised to 1.25 MAC | 8.5% | 100% |
| vaporizer turned off | 1.6% | 100% |

Of the hovers that could report either run, 83.3–95.3% (alveolar) and
43.8–81.4% (fat) would print different text. Naming the run made visible which
run the nearest-point rule chose, but did not make the box report the trace the
reader aimed at: a 2 px move changed which run it reported on 75.4–99.9% of the
fat axis. § "Where more than one trace answers" gives the rule that replaced the
nearest-point rule (`PL-JVHL`).

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

**Every compartment whose drawn point is inside the radius is also reported**
(project owner, 2026-09-20, ratified, over recording the measurement and leaving
the flip to the axis fix). Where every reading in reach belongs to one
compartment, which is most hovers, the box keeps the form above: the agent, the
compartment, then one value line per run. Where the readings span several
compartments, the compartment line is dropped. Each value line then opens with
its own compartment, with its gloss where it has one, followed by the run while
more than one run is drawn:

```
Modelled sevoflurane
Muscle · Run 1 · 20m   0.19%   0.10 ×MAC
Muscle · Run 2 · 20m   0.09%   0.04 ×MAC
Fat · Run 1 · 20m   0.01%   0.01 ×MAC
Fat · Run 2 · 20m   0.01%  <0.01 ×MAC
```

The box reports every trace in reach because, where traces crowd together, no
hand can aim at one rather than another. Two runs' fat traces lie 0.2–1.4 px
apart, and at that separation no rule for picking one trace can follow the
reader's aim (`PL-QYBW`). The earlier rule reported only the nearest point, so a
2 px movement could switch the box to another run or compartment, and to a
different number. The box itself stayed put. Only the name and the numbers
changed, and the reader had already read past the name. Now no movement too
small to aim with decides what the box shows.

Lines are ordered by compartment and then by run, both in the chart's drawing
order, so the box follows the legend and the readout panels beside it. Distance
from the pointer never sets the order, because lines ordered by distance would
swap places under movements too small to aim with. The box is placed at the first
reported run's point.

A dot marks every reported point, because a single dot would mark one run's trace
while the text reported several.

Once the reader has aimed the pointer, usually only one run is in reach. With
one run in reach, the hover readout's box uses the three-line form, and names
that run if two are drawn. The box gains a line when a run comes into reach and
loses it when the reader moves away, so the reader sees each run arrive and
leave. In the cases measured below, it held at most four value lines on a
two-run chart, and at most three on a single-run chart.

**The pointer's place along the time axis names the instant, and the radius
decides only what is in reach** (`PL-1K9G`, 2026-09-22). The chart draws each
run as columns of points: one column every 4 s on a 60-minute axis and every
48 s on a 12-hour axis, plus a column at each of that run's control changes. A
branch draws none before its fork. Each run is reported at its drawn instant
nearest the pointer in time, and a tie goes to the earlier instant. Each of that
run's compartments is reported if its point at that instant is inside the
radius. So every compartment of one run is reported at one instant. Moving the
pointer up or down can change what is in reach, but never the instant printed.
The wash-in plot follows the same rule.

Each line prints its own instant, because two runs' nearest instants can differ
by up to one column, and the printed form shows the difference. One instant
above several values would claim that they are simultaneous when they may not be.

The percent axis stays linear, which crowds the slow compartments together.
Because the hover readout reports every trace in reach, the crowding needs no
change of scale (§ "MAC multiples as a display unit").

**For developers.** Five targeting rules were scored on the branched case, with
alveolar and fat displayed, a pair that the limit on a two-run chart's
compartments allows (`COMPARED_COMPARTMENT_CAP`). The score is the share of
hovers whose reported run changed after a 2 px move, among hovers with both runs
inside the radius before and after the move. It counts hovers that could go
either way, so it cannot be compared with the 75.4–99.9% figure under
§ "The hover and the run it belongs to", which is a share of axis columns.

| Targeting rule | fat, 2 MAC | fat, 1.25 MAC | fat, vaporizer off |
| --- | ---: | ---: | ---: |
| the single globally nearest drawn point | 9.2% | 9.0% | 9.2% |
| nearest trace measured along its length | 9.2% | 9.0% | 9.2% |
| the pointer inside a run's own band, 2 px or 4 px | 9.2% | 9.0% | 9.2% |
| distance, near-ties broken toward the trunk | 0.0% | 0.0% | 0.0% |
| every run inside the radius is reported | 0.0% | 0.0% | 0.0% |

The first three rules score the same to the digit, for two reasons that belong
to this chart's geometry. First, the trace is drawn at about one sample per 4 s
against a 12 px radius, so the pointer's distance to the polyline and to the
nearest vertex differ by a fraction of a pixel. Nearest along the length would
differ from nearest drawn point only on a sparse, steep trace. Second, both
runs' fat points lie inside the radius over 94.5–98.0% of the hoverable area, so
a band rule must break its tie by the nearest-point rule it was meant to
replace, exactly where the reported run flips.

Breaking near-ties toward the trunk scores 0.0%, as reporting every run does, but
was refused for its costs. A tie window keeps the boundary between the runs and
adds a second one, where the pointer leaves the window. Among axis columns with
both runs in reach on the alveolar trace of the 1.25 MAC case, it raises the share
on which the reported run flips from 58.5% to 98.4%. It also makes the branch's
value unreachable wherever the two runs' traces lie inside the window, which is
most of the fat trace. A value that a reader cannot reach is worse than one that
is hard to aim at.

Before every compartment in reach was reported (`PL-0RZ0`), the nearest drawn point
picked the compartment, on the reasoning that a reader aims at a trace. The
crowding near zero defeats that reasoning. Two or more compartments lie inside the
radius over 15.2–45.7% of the two-run chart's hoverable area, and over 37.0% of
the single-run chart's. Across pairs of pointer positions 2 px apart with more
than one compartment in reach, the compartment reported changed on 6.6–13.6% of
pairs. On 99.9% of those, the box printed a different number, by a median of
17.1–17.9× for muscle against fat. At a change, the two nearest points were a
median 0.9 px apart, and all were within 2 px.

| Chart | Compartments | Two or more in reach | 2 px flips the compartment |
| --- | --- | ---: | ---: |
| one run | all six | 37.0% | 12.7% |
| two runs, vaporizer off | muscle + fat | 45.7% | 7.5% |
| two runs, 1.25 MAC | muscle + fat | 19.1% | 9.2% |
| two runs, 1.25 MAC | mixed venous + vessel rich | 29.4% | 6.6% |
| two runs, 2 MAC | alveolar + fat | 0.5% | 13.6% |

The nearest-point rule never made a value unreachable, which matters because the
tie-break above was refused partly for doing so. Across the same cases, every
compartment was reported on 98% or more of the axis columns where it is drawn.
The worst was muscle on the single-run chart, unreported on 2.0% of its columns.
<!-- not-restated: 2.0 % -->

Reporting every trace in reach was affordable because the box stays short. One
compartment alone is in reach on 54.3–99.5% of hovers across these cases, and
63.0% on the single-run chart. The box carries one value line on 21–93% of hovers.

Before the pointer's time alone named the instant (`PL-1K9G`), each trace reported
its own drawn point nearest the pointer in both dimensions, so on a sloped trace
the pointer's height chose the column. The scan behind that change covered the
branched case, and a two-hour single run on its fitted 2-hour axis and on the
12-hour axis, where a dial change draws a near-vertical step. It tried every pixel
of height at four sub-pixel phases per column, and its selection was checked
against the shipped function before any number was kept. The whole scan is in
`PL-1K9G`.

| Chart | Boxes holding 2+ of one run's readings that mixed instants | Spread, median / max | A vertical 2 px move changed the instant / the printed value |
| --- | ---: | ---: | ---: |
| one run, 60 min | 70.1% | 16 s / 72 s | 44.9% / 35.1% |
| two runs, mixed venous + vessel-rich | 88.3–94.7% | 12–16 s / 32–52 s | 50.6–62.8% / 36.9–52.8% |
| two runs, muscle + fat | 13.0–16.8% | 4 s / 4 s | 3.0–5.4% / 0.3–0.8% |
| one run, 12 h axis | 84.5% | 288 s / 912 s | 37.3% / 33.3% |

<!-- not-restated: 13.0 -->

Mixed instants matter because adjacent columns often print different values. On
the 60-minute axis, the share of adjacent columns that differ is 44.0–93.3% on the
circuit, alveolar, mixed venous and vessel-rich traces, against 3.3–16.0% on
muscle and 0.7–1.3% on fat. Under the old rule, a sloped trace's nearest point
could lie as far to the side as the radius reaches, which is fifteen minutes on
the 12-hour axis.

The alternative to measuring the radius at the named instant was to keep the old
reach and report the point at that instant. Like the chosen rule, that would have
made the instant depend on time alone, and it would have kept every value that
the old rule reported. But where the chosen rule reports nothing, the alternative
would have reported a point a median 13.5 px and up to 42.5 px from the pointer on
the 60-minute axis, and up to 146 px on the 12-hour axis. The dot and the box would
then hang on a value the reader is nowhere near. The chosen rule's cost comes
beside a steep segment, where a pointer level with a point several columns along
no longer reports that point. Even so, the chosen rule keeps 84–100% of the area
over which the old rule reported each trace on the 60-minute and 2-hour axes, and
45–54% for the four fast compartments on the 12-hour axis. It reports nothing the
old rule did not, and leaves no drawn instant unreachable.

On the wash-in plot, the old rule let 23.9–44.4% of vertical 2 px moves change a
box's instant. No box there mixed instants, because the plot draws one trace per
run. The plot treats a run's stretches as one set of drawn instants.

**For developers.** A logarithmic axis fixed from 0.001 to 3 MAC would put two
runs' fat traces 23–75 px apart, but it has three costs. It draws below the
0.01-point resolution of § "Displayed precision". It is a display mode on a
chart of clinical values. It would also arrive ahead of the v0.6.0 View
contract, which decides where a View's own settings live. Its strongest use,
the washout tail, is a candidate for the catalogue of views (planned-milestone
item 36) rather than a mode on this chart.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

Two functions produce the forms above that list several runs or compartments
(`chart_frame.format_compared_trace_hover` and
`chart_frame.format_compared_wash_in_hover`), and their numbers come from
`app/formatting.py` like every other number in the box. Two more collect the
traces within reach at the instant that the pointer names (`nearest_trace_point`
and `nearest_wash_in_point`), and the first of them skips hidden compartments.
The unit tests in `tests/unit/test_chart_frame.py` contain both worked examples
above verbatim. They also contain the fat and muscle cases behind the decisions to
report every run and every compartment in reach, and the geometry behind the
decision that the pointer's time alone names the instant
(`test_every_compartment_of_one_run_answers_at_one_instant`).

#### Resolution: the readouts' derivation applies unchanged

The box prints a percent and a MAC multiple to two decimals each, as `<0.01%`
and `<0.01 ×MAC` below that. § "Displayed precision" derives both forms for the
readout panel, and nothing in that derivation depends on where the number
appears. Its upper limit on precision is one measured standard deviation of a
partition coefficient, which shifts the modelled trajectory itself, whatever
display shows it. Its lower limit is a teaching judgment about what a reader can
learn from the slow compartments.

**The box gets no third decimal.** A printed digit could answer either of two
questions. One is how finely two moments within one run can be told apart, which
is about nine decimal places finer than the readout panel shows. The other is how
finely this model resolves a concentration in a patient, which is much coarser.
The box is closer than the readout panel to the first question, because it reports
one trace at one instant, the form a within-run comparison takes. That question
alone would justify a third decimal. But a reader cannot tell which question a
digit answers, and the box makes the confusion worse. It is the display most
likely to be written down, it floats over a chart whose whole subject is a
patient, and it is read without the readout panel's five other compartments,
which show that a within-run comparison is on offer.

**The below-resolution form is required here.** At 1 MAC sevoflurane, fat stays
below 0.01% for the first thirteen minutes, and muscle for the first two. Those
minutes are the slow-compartment wash-in that the chart exists to show. `<0.01%`
says what is known. A number there would claim a resolution the model does not
have, on the compartment where a reader is least able to notice.

#### What a chart library prints instead, measured

Left to its default, the charting software's own tooltip prints the plotted
coordinate instead of a clinical value. It prints no unit, it prints a number where
the box prints `<0.01%`, and it prints more decimals the smaller the value.

**For developers.** The default matters because it is what ships if nothing
overrides it, and both toolkits this project has used format the coordinate. In
Flet, a chart's data point (`flet_charts.LineChartDataPoint`) defaults to a
tooltip (`LineChartDataPointTooltip`) whose `text` this application never writes
into. In pyqtgraph, a scatter plot (`pyqtgraph.ScatterPlotItem`) defaults its
formatter for hoverable points, `tip`, to
`'x: {x:.3g}\ny: {y:.3g}\ndata={data}'.format`. The table shows `.3g` applied to
the drawn y, as that scatter plot would apply it, and `format_percent` applied to
the same value, at four instants of the first hour. The values come from a run on
2026-09-14 on the reference adult, with sevoflurane delivered at 0.02 (1 MAC) and
the shipped number of columns over a one-hour axis.

| Instant | Compartment | `.3g` on the drawn y | This readout |
| --- | --- | ---: | ---: |
| 48.3 s | Alveolar | `0.262` | `0.26%` |
| 48.3 s | Muscle | `0.000656` | `<0.01%` |
| 48.3 s | Fat | `3.52e-05` | `<0.01%` |
| 289.9 s | Fat | `0.00116` | `<0.01%` |
| 1208.1 s | Fat | `0.00888` | `0.01%` |
| 3600.0 s | Alveolar | `1.54` | `1.54%` |

- `3.52e-05` carries five decimal places beyond the resolution of § "Displayed
  precision", on the compartment where the readout panel prints no number at all.
  A reader comparing that number with the panel would find them disagreeing about
  whether the value is known.
- With no unit, a bare `1.54` could belong to either axis, and the two differ by a
  factor of about two for sevoflurane. `3.52e-05` is worse, because it reads
  equally well as a fraction of an atmosphere, a hundredfold out.
- Three significant figures give two decimals at `1.54`, three at `0.262` and six
  at `0.000656`. A display whose precision changes with the size of the value
  claims that the model resolves small values more finely than large ones, the
  opposite of the truth. This fault is the one that would go unnoticed.

#### Which series answer a hover, and which do not

The six compartment traces respond to a hover in the form above, unless the
reader has hidden the compartment. The wash-in trace responds with a plain ratio,
because $`F_A/F_I`$ is dimensionless and has neither a percent nor a MAC reading:

```
Modelled sevoflurane · 20m8s
Wash-in F_A/F_I (alveolar / modelled circuit)
0.71
```

The caption in parentheses says that $`F_I`$ is the modelled circuit, not the
vaporizer dial.

The 1 MAC line, the MAC-awake band and the control marks do not respond. The line
and the band run across the plot, and the control marks are vertical and full
height, so all three cross every trace. If they responded, an annotation would
appear under the pointer wherever a reader aims at a trace that passes behind one
of them. That is exactly where a reading is most wanted: a trace crossing 1 MAC is
the event the line is drawn for. What the three would report is already on
screen. The MAC value that the MAC multiples divide by is stated beside the chart,
and the input timeline lists each control change with its old and new value.

**For developers.** The ratio has its own formatter (`format_wash_in_ratio`), and
the caption is the one in `app/wash_in.py`. It uses a solidus rather than a
division sign because every non-ASCII character that reaches a reader must first
have been rendered and seen (`tools/glyph_check.py`), and the division sign has
not been.

#### When it answers

The box appears whenever the pointer is over a trace, whether the run is playing
or paused. At high playback speed its value moves with the run, as every other
readout does, and a reader who wants to study a value pauses. Moving the pointer
off the plot removes the box at once, so a value that moves with the run is always
one that the reader is pointing at.

**For developers.** The box is built on pyqtgraph and reports the drawn points
within the hover radius (`PL-G59B`, 2026-09-14). The code that shows it is in
`app/qt_chart.py`, and an integration test checks the rendered box against a real
run (`tests/integration/test_qt_chart.py`).

A hover that responds only while paused is a hidden mode: a reader who tries it
during a run gets nothing, concludes that the chart is not interactive, and never
finds the hover again. An earlier change had withdrawn the hover while a run plays
(`PL-KP7H`), because Flet's control-tree diff visits every point's tooltip object
on every frame, and the tooltips were half the cost of a saturated frame.

Qt has no such cost by either route the box could be built on. One route drives a
crosshair from the scene's own mouse-move signal (`sigMouseMoved`), rate-limited
through a signal proxy (`SignalProxy`). The other gives each hoverable point a
callable (`tip`) that runs when the pointer arrives, with no tooltip object stored
for each point. Both cost work per pointer event, whatever the number of points
drawn.

The Qt build must provide the hover, under the parity rule "Every capability the
Flet build has, the Qt build has", and it does not come by default. A pyqtgraph
scatter plot (`ScatterPlotItem`) ships with `hoverable` set to `False`, and a
plotted line has no hover of its own, so a port that says nothing about the hover
loses it.

Besides removing the box, leaving the plot discards any pointer move still waiting
to be handled. A box left at the last point the pointer crossed would recompute
its value every frame. While a run played, it would climb with the run like a live
readout, for an instant that nobody is looking at (`PL-LTKL`).

### A preview of an unapplied setting

While a learner holds a slider's handle, the chart draws the trajectory that the
run would take if the value under the handle were applied at the run's current
time (`PL-5B1N`). Both plots draw it, so they never show two different futures.
On the F_A/F_I plot the preview is the predicted ratio. A dot marks where a
stretch of it stops, as on the run's curve.

**A preview is a prediction.** The run has not passed through it, so it is not a
modelled state of the run. It is not a measurement either. It depends on a
setting that the learner has not applied and may never apply. Drawn with the
run's line width and no label, it would look like a run that happened.

**Four cues mark a preview, and none of them is colour.** Its curves keep each
compartment's colour and dash pattern, because those are what tell the six
compartments apart.

1. **Position.** The preview lies wholly to the right of the run's current time,
   inside a tinted region. A line at the run's current time is the region's left
   edge. The preview ends at the right edge of the time axis, or at the end of the
   longest run the simulator supports if that comes first. The run that the
   preview belongs to never enters the region, but when runs are compared, a run
   that has gone further may be drawn inside it.
2. **A label in the plot**, such as "Preview: Fresh gas flow 6.0 L/min, not
   applied". It names the control and the value tried, in the slider's own words.
   It is drawn inside the region, so a screenshot taken during a drag includes
   it. Each compared run has its own controls, so only the run whose slider
   handle is held shows a preview. The label names that run.
3. **Width.** Each preview curve is one pixel thinner than the same compartment's
   curve in a run shown alone, but never thinner than 2 px. The two compartments
   drawn at 3 px therefore have 2 px preview curves, and so do the four drawn at
   2 px. For those four, the other three cues mark the preview. When runs are
   compared, the first run's curves are drawn one step wider, but its preview
   curves keep the width they have when the run is shown alone. The preview is
   then no wider than the other run's curve of the same compartment.
4. **Timing.** The preview exists only while the handle is held. It appears at
   the press and is gone from the frame drawn at release.

**The preview comes from the same model and version as the run.** It starts from
the run's state at its current time, as § "The canonical evaluation rule"
defines that state. The value goes through the same checks as when it is
applied. A new cardiac output moves every tissue flow exactly as applying it
would. The same inputs always give the same preview. Computing a preview changes
nothing in the run. When the value under the handle is the setting already in
force, the preview matches what the run then draws, to within the computer's
rounding error. While the run plays, the preview is computed again on every
frame from the run's new current time.

**A drag applies its value only when the handle is released.** The run records
one setting change at that moment. Until then the run keeps the setting in force,
and the value printed beside the slider is that setting. The value is applied
before the preview ends, so the frame drawn at release already shows the run
under its new setting. A key press, one notch of the scroll wheel or a click on
the slider away from its handle is a single input, so it applies at once and
draws no preview. A run stops when it fails or reaches the end of the longest
run the simulator supports. A stopped run accepts no new setting and draws no
preview.

**The time window keeps its width during a preview.** It slides so that the
run's current time sits at mid-plot: half the window shows the run that
happened, and half shows the prediction. Early in a run the window stops at
zero, and the current time sits left of the middle. Widening the window to make
room would rescale every slope, which § "The chart's time base" rules out. When
runs are compared, the window centres on the current time of the run whose
slider handle is held. At release, the window goes back to following the run.

**No value on a preview curve is printed as a reading.** A value shown when the
pointer hovers over the chart never comes from a preview. A preview that goes
above the top of the concentration axis is cut off there, as a run's curve is.
The off-scale notice then names each preview curve that is cut off, with its
highest value in view, because the readouts give only the run's values.

**For developers.** The preview has a run definition of its own
(`SimulationController.preview_window`). It is evaluated on the run's own time
grid. Its settings are built the way a branch, a run taken from another run,
builds its own (`SimulationController.preview_settings`). A trial run is rebuilt
from the settings in force and checked to match the run in every value. It then
takes the new value through the same setter that applies a value to the run. The
centred time window comes from `chart_time_base.preview_window`, and the wording
of the off-scale notice from `dashboard_frame.PREVIEW_OFF_SCALE_NOTICE_TEMPLATE`.

The 2 px minimum width for a preview curve is there because an antialiased line
thinner than 2 px has less than 3:1 contrast against the panel
(§ "The six compartment traces: what separates them").

Neither dash pattern nor reduced opacity can mark a curve as predicted. The
muscle curve is already dotted, and drawing the run solid with a dotted preview
would flatten the five dashed curves into one style. At 0.85 opacity, the
alveolar and muscle curves fall to contrasts of 2.93 and 2.83 against the panel,
less than the 3:1 that WCAG success criterion 1.4.11 sets. At 0.75, four of the
six fall below 3:1.

The region's tint is decoration, as the MAC-awake band's is, because the
region's edge and the label carry the information. Its opacity is
`theme.PREVIEW_REGION_FILL_OPACITY`.

### A cost at the reader's price

The agent cost View shows what the delivered agent costs, at a price that the
reader sets in its form. The readout shows which part of the cost is the model's
and which part is the reader's (`PL-VJZK`). A price is neither modelled nor
measured, because the reader supplies it. Every other value the interface shows
today is modelled. A cost is a modelled amount times that price, so a wrong
price makes a correct amount lead to a wrong conclusion.

**The project ships no price.** Until the reader sets a price, the readout says
that no price is set, and it shows no cost. A shipped price goes stale, and it
differs from one institution to the next. Gas Man shows both problems. Its
default price for isoflurane is $20.47 for a 100 mL bottle (Philip JH,
*Workbook for Gas Man*, Appendix C, printed p. 171). The book calls its
defaults "USA bottle volume and bottle cost as of March 5, 2008" (printed
p. 105). Chapter 14 gives $78.00 per 100 mL bottle "on March 5, 2008" (printed
p. 141).

**What a cost readout shows.** A cost is never shown alone. Beside it, the
readout shows these six things:

1. the delivered agent in millilitres of liquid equivalent, labelled as
   delivered and as liquid. This is the modelled figure that the cost is
   computed from. It stays on screen even where the reader has chosen to show
   the View's amounts in litres of vapour (`ROADMAP.md`, v0.7.0 entry 8), so
   that the modelled amount never appears only inside a figure that includes
   the reader's price;
2. the price per millilitre of liquid that the cost uses, so that the reader
   can check the product by eye;
3. the bottle price and the bottle volume that the price per millilitre came
   from;
4. the currency's code, on the cost and on each price;
5. the date on which the price applied; and
6. words saying that the cost is at the reader's price, not only a colour or a
   style, so that no reader misses the statement.

**A bare "mL" does not say whether it means liquid or vapour.** The schematic
labels its amounts in millilitres of vapour (`ROADMAP.md`, v0.7.0 entry 1).
Gas Man quotes its price as "Cost/mL vapor" (printed p. 174). One millilitre
of liquid isoflurane gives about 196 mL of vapour, so a volume or a price read
as vapour is wrong by that factor.

**The simulator reproduces the costs of both of Gas Man's isoflurane
exercises.** It does so at the price that the book prints beside the costs of
Exercise 14-1, "a bottle cost of US$20.47 per 100 ml" (printed p. 134). For
Exercise 14-1 at 60 min, the readout could show "39 mL of liquid x USD 0.2047
per mL of liquid = USD 8.07, at your price of USD 20.47 per 100 mL bottle, as
of 2008-03-05". The wording and the layout are placeholders. The book
prints $8.06, because Gas Man rounds isoflurane's vapour-to-liquid ratio to
196 (§ "Agent amount").

**The figures beside a cost are rounded, and the readout says so.** It also
says that the cost is computed from the unrounded liquid volume and price per
millilitre (`PL-1P15`). § "Agent amounts in millilitres, and the cost" sets the
precision of each figure. The liquid volume is shown in
whole millilitres, so the product of the figures shown can differ from the cost
by more than one unit of the cost's last digit. In the example above, 39 mL
times USD 0.2047 is USD 7.98. The cost is USD 8.07 because it uses the
unrounded 39.42 mL. At USD 115.13 per 240 mL bottle, 60 min of desflurane at
6 % and 1 L/min costs USD 8.23. Shown as 17 mL and USD 0.4797 per mL, the two
figures multiply to USD 8.15.

<!-- not-restated: 6 % -->

**How the cost is computed.** The cost is the delivered agent's liquid
equivalent times the price per millilitre. It uses the delivered agent because
that is what left the bottle (`ROADMAP.md`, planned-milestone item 28, and
`PL-H4N8`). The conversion to liquid is exact (§ "Agent amount"). The cost
depends only on the delivered amount, the agent's vapour-to-liquid ratio and
the price stored for that agent. That same stored price supplies the bottle
price and volume, the price per millilitre, the currency and the date shown
beside the cost. The date is never used to compute the cost, and neither is
today's date. When two runs are compared, each run's cost uses the price of its
own agent. A cost is never added to, or subtracted from, a cost in another
currency.

**What a stored price carries.** The simulator keeps at most one price for
each agent. Each price records five things:

- the agent it prices;
- the price of one bottle, in the price's currency;
- the volume of that bottle, in millilitres of liquid agent;
- the currency, as its three-letter ISO 4217 code, such as `USD` or `EUR`;
  and
- the date on which the price applied, as an ISO 8601 calendar date, such as
  `2008-03-05`. The form's date field writes dates this way and fills in the
  day of entry. The reader should change it to the day the price was quoted,
  because a price goes stale from that day, not from the day it was typed in.

**The price is taken per bottle, and the price per millilitre is derived**
(decided by `PL-VJZK` on 2026-10-26, over asking for a price per millilitre).
An institution buys agent by the bottle, and its pharmacy quotes a price per
bottle. The price per millilitre is never stored, so it cannot disagree with
the bottle price and volume. The form still allows three mistakes:

- a price per millilitre typed as the bottle price. The cost is then 100 to
  250 times too low, because the bottles in Gas Man's defaults hold 100 to
  250 mL of the volatile agents (printed pp. 171-172);
- a bottle volume typed in litres, such as 0.25, or as 1 for one bottle. The
  cost is then 100 to 1000 times too high; and
- the price and the volume swapped. The price per millilitre is then inverted.

The field for the bottle volume therefore names its unit, millilitres of liquid.
The first mistake makes the price per millilitre on the readout 100 to 250 times
too low, and the second makes it 100 to 1000 times too high. A swap stands out
only where the two numbers differ widely. At Gas Man's sevoflurane default of
240.34 for a 250 mL bottle (printed p. 172), a swap changes the cost by 8 %, and
nothing on screen would show it.

<!-- not-restated: 8 % -->

**What is refused.** A bottle price or a bottle volume must be a positive
finite number. A price of zero is refused because it is far more likely to be
an empty field than an agent given away. The currency must be three capital
letters, and the date a real calendar date. The simulator checks each of these
at entry, and again when it reads its preferences file. The three letters are
not checked against the codes that ISO 4217 assigns, but a mistyped code shows
beside every cost and price, where the reader sees it. The reader types the
bottle price and the bottle volume as digits with at most one decimal point. A
sign, an exponent, a thousands separator or a decimal comma is refused rather
than guessed at, because "1,250" could mean 1250 or 1.25.

**A refused entry changes nothing.** The form says why it refused the entry,
and the readout goes on showing the cost at the price already stored, with
that price beside it.

**When no cost is shown.** The readout shows no cost, and says why, in each of
these cases:

- no price is set for the agent;
- the stored price was refused when the simulator read its preferences file.
  No default replaces it, and the readout says that no valid price is set for
  the agent;
- the price per millilitre is not a positive finite number, or the cost is not
  finite, which extreme entries can cause, such as a bottle price of 10 to the
  power 308 for a 0.5 mL bottle; or
- the delivered amount cannot be converted to liquid (§ "Agent amount").

The readout never shows a cost of zero in place of one of these cases. Nor does
it show a cost left over from an earlier instant, another agent or an earlier
price. When the price changes, the readout redraws the cost at once, whether or
not the run is advancing.

**For developers.** The agent cost View and its form live in
`app/agent_cost.py` (`PL-1P15`). The preferences module in `app/preferences.py`
stores each price (`PL-93B3`). The safety standard in `CLAUDE.md` applies to a
cost, although money is not a clinical quantity.

A stored price has no field that says who set it, because the project ships
none. If a release ever ships a default price, each stored price gains that
field, and the readout must then mark a default price as one the project
supplied, with its date.

The form asks for a bottle price because a field for a price per millilitre
would make the reader divide first, and a bottle price typed into it would
multiply every cost by the bottle's volume in millilitres. Gas Man's Set Cost
command likewise takes "the bottle volume and bottle cost" (printed p. 15). One
function derives the price per millilitre from the bottle price and volume. The
preferences module accepts any positive finite bottle volume, because no source
gives the sizes in which the agents are sold (`PL-93B3`, 2026-11-01).

The readout names a currency by its code because the sign "$" names the United
States, Canadian and Australian dollars, among others. Gas Man shows the
problem. Its defaults label each bottle cost "Bottle cost in $US" (printed
p. 171). Its menu says the cost is typed "in the local currency" (printed
p. 15). A code from ISO 4217:2015 names exactly one currency. The currency check
stops at three capital letters (`PL-93B3`, 2026-11-01) because ISO 4217's list
of codes changes several times a year. Checking against the list would need a
dated copy of it with a record of its source, and a copy that fell out of date
would refuse a real currency. Any three letters still remove the ambiguity of
"$".

The date follows ISO 8601-1:2019, as in 2008-03-05, because 03/05/2008 means
March or May depending on the reader's country. Neither this standard nor
ISO 4217:2015 was read for this section.

The product of the liquid volume and the price per millilitre, as shown,
differs from the cost by at most half a unit of the volume's last shown digit
times the price per millilitre, plus the volume times half a unit of the
price's last shown digit. The cost's precision is not a fixed count of
decimals, because how many decimals a cost can justify depends on the price
(§ "Displayed precision", `PL-0S0V`).

When the simulator runs Gas Man's two isoflurane exercises from their patient
inputs, at US$20.47 per 100 mL bottle, the displayed cost reproduces the four
costs printed in them. The conversion to liquid alone is checked against the
same exercises.

**For developers.** The two rows in the hazard table (§ "Reasonably foreseeable
misuse, and the hazards the presentation carries") name the tests for this
section. The cost is checked in `tests/integration/test_agent_cost_view.py`
(`test_the_displayed_cost_reproduces_gas_man_s_printed_costs`), and the
conversion to liquid in `tests/reference/test_published_vapour_to_liquid.py`.

### The compartment schematic: what its heights, amounts and share bar assert

The compartment schematic draws six compartments as containers: the circuit,
the alveoli, venous blood, the vessel-rich group, muscle and fat, in the
readout row's order (`PL-RNYV`). Like Gas Man's Picture, it shows where the
tension is. It also shows where the agent is, which neither the readouts nor
the concentration chart does. It prints the amount of agent each container
holds, and its share bar gives each compartment's part of all the agent.

**A container's fill height is the compartment's modelled tension, not an
amount.** All containers of one run fill against one scale: the concentration
chart's percent axis, from zero at the bottom to 3 MAC of the running agent at
the top. So a height on the schematic and a height on the chart show the same
tension. A container that holds more agent can stand lower than one that holds
less. At 60 min in a run with sevoflurane at a 1 MAC dial, fat holds a fifth of
all the agent in the run, but its tension of 0.03% atm fills less than 1% of
its container's height (`ROADMAP.md` § "v0.7.0 - the schematic"). Every
container is drawn at one width, so its filled area is not an amount either.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

A tension above the top of the scale fills its container to the top, and the
schematic marks the container as off the scale. The concentration chart does
the same for a trace above its axis, in its off-scale notice. The container's
label still prints the tension. The circuit reaches 4 MAC, above the top, when
a sevoflurane dial is at its 8% maximum.
<!-- provenance: data/agents/sevoflurane.json max_delivered_concentration_percent = 8 -->

**A container's amount is the agent that the model holds in that compartment,
counted as vapour.** It is the equivalent volume of pure agent vapour at a
reference condition of 20 °C and 760 mmHg, dry, shown in millilitres ($`M_x`$ in
§ "Agent amount"). The agent in blood and fat is dissolved, so the volume
expresses an amount of agent, not gas present in the body. This subsection's
rules for an agent amount also apply to every other View that shows one,
including the share bar (`PL-S79P`) and the agent cost View (`PL-B396`). §
"Displayed precision" derives the precision at which amounts are shown.

**An agent amount's unit always names vapour or liquid, and is never a bare
"mL".** Millilitres of vapour and millilitres of liquid differ by a factor of
about 180 to 210, depending on the agent. At the reference condition, 1 mL of
liquid gives about 183 mL of sevoflurane vapour or about 210 mL of desflurane
vapour (§ "Agent amount"). A vapour amount is written "mL vapour", as in
"38 mL vapour". A liquid amount is written "mL of liquid", as in
"4.2 mL of liquid". The model holds no liquid, so this number is worked out
from a vapour amount. It is the volume of liquid agent that would give that
vapour, which is what a vaporizer uses up. A caption under the number says
that the vaporizer used this liquid. The accounting View shows amounts in
litres, under the caption "Litres of equivalent pure agent gas", which marks
them as vapour. The agent cost panel writes its delivered amount as "mL of
liquid" or "L vapour", whichever unit the reader chose, and its caption says
what that unit measures. These spellings may change while the interface is
being built.

**The share bar shows each compartment's share of all the agent the run holds,
circuit included.** The bar is divided into six segments, in the containers'
order. Each segment's length is that compartment's amount divided by the sum of
the six amounts:

```math
s_x = \frac{M_x}{\sum_y M_y}
```

The six segments therefore fill the whole bar. Each segment is named in text,
never by colour alone. A share printed in text is shown in whole percent
(§ "Displayed precision"). A run holds no agent when it starts, so the bar is
then drawn empty and prints no share.

**Lines between the containers show ventilation and blood flow.** The
containers stand in one row. A line joins the circuit to the alveoli for
ventilation. A line above the row carries arterial blood from the alveoli to
each tissue group. A line below the row carries each tissue group's venous
blood to the venous blood container, and a line joins that container back to
the alveoli. So the three tissue groups are drawn in parallel, as the model
perfuses them (§ "Assumptions"). The containers are not joined one to the next,
because that would draw agent passing from the vessel-rich group through muscle
into fat, a route between tissues that this model omits (`PL-RNYV`).

**No container is drawn for arterial blood.** The model sets arterial tension
equal to alveolar tension at every instant ($`F_a \equiv F_A`$,
§ "Blood compartments"), so it gives arterial blood no volume, capacity or
amount of its own. The alveolar container therefore shows arterial tension as
well. Gas Man's Picture draws an arterial container. Here such a container
would show agent that the model does not hold.

**Each schematic shows its run at the same instant as the readouts.** A line
of text above the schematic gives that instant as the readouts' clock prints
it. While runs are compared, that line also names the run, so that a reader
does not take one run's value for the other's. Two compared runs can be at
different times, as when one is a branch taken at an earlier point. A
difference between their schematics may then come from elapsed time rather
than from the change the branch made. The schematic withholds its values
whenever the readouts withhold theirs: after a Reset or an agent change, until
the screen is next redrawn.

**Every height, amount and share on the schematic is a model output.** The
schematic therefore prints "Model outputs — not measurements." once, in its
own heading, as the readout section does. No amount is a prediction about a
patient to its last digit, for the reason § "Displayed precision" gives for
the readouts.

**For developers.** The schematic takes the top of its scale from the function
that sets the concentration chart's top (`chart_axis_top_percent`) and sets no
top of its own. The top's MAC multiple is a constant (`CHART_AXIS_TOP_MAC`), and
§ "MAC multiples as a display unit" gives the reason for 3 MAC.
<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

The containers' common width is there because fat's container, drawn to scale,
would take about 500 px of a View 600 px wide, and four of the others would
take between 1 and 7 px each. The roadmap records the designs that the
schematic was chosen over (`ROADMAP.md` § "v0.7.0 - the schematic").

The run writes the schematic where it writes its readouts, from the same
snapshot of its state. Each amount comes from the snapshot's record for its
compartment (`PL-KFTM`), and that record is read from the amount of agent that
the model holds in the compartment (`agent_amount_l` in `core/`). The schematic
computes no amount of its own. The sum in the share formula is the snapshot's
total of stored agent (`stored_agent_l`).

Each spelling of an amount's unit is defined once, in `app/display_units.py`
(`DisplayUnit`). Whoever writes the first View to print a spelling adds it
there. Every View reads its spellings from that file and defines none of
its own.

The empty bar at a run's start is there because computing a share would then
divide by zero, and six zeros would look like real shares.

Shares are shown on a bar rather than by the containers' areas because a
position along a common scale is judged more accurately than an area
(Cleveland WS, McGill R, "Graphical perception: theory, experimentation, and
application to the development of graphical methods", *J Am Stat Assoc*
1984;79(387):531-554, https://doi.org/10.1080/01621459.1984.10478080). Only the
first segment starts at the bar's baseline, but each of the others is judged by
its length, which Cleveland and McGill's ranking still places above area.

The hazard table requires the run's name in the line above the schematic, in
its row on reading one run's value as the other's.

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
| reading a run whose Reset the model refused as one still running, or as one that was reset | a refused Reset leaves the run exactly as it was, and the interface halts the run and states the halt (§ "Reset behavior") | `test_a_reset_the_core_refuses_halts_the_run_visibly`, `test_a_reset_the_core_refuses_leaves_the_run_exactly_as_it_was`, `test_a_refused_reset_names_the_way_out_in_the_banner`, `test_a_tissue_flow_mismatch_is_stated_in_litres_per_minute` |
| comparing readouts with a chart that was drawn from different settings | the readouts come from the model's steps, and the chart from the recorded settings of the run. Before each step, the two sets of settings are compared. If a setting reaches the model without being recorded, the run halts on the last step on which the two agree, and a banner says why. The interface never changes a setting that way. Reset then starts a new run from the model's settings. A recorded change after such a write brings the record back into line with the model without halting the run | `test_a_setting_written_onto_the_core_past_the_controller_refuses_the_next_step`, `test_a_setting_written_onto_a_branch_s_core_past_its_controller_refuses_its_next_step`, `test_reset_after_a_setting_written_past_the_controller_runs_at_that_setting`, `test_a_run_whose_core_setting_moved_past_its_controller_halts_on_the_last_recorded_step` |
| reading the agent selector or a slider, used on a run whose values cannot be read, as a control that took effect | if reading the run's values fails while the selector or a slider is in use, the run halts and the halt is stated from the run's record, so the failure cannot pass unseen. The selector goes back to the agent that record names. The banner still names Reset as the way to recover, unless a refused Reset has left its own instructions. The controls stay usable on a halted run, because locking them would show the agent selector as disabled. A slider moved on a run that has already stopped is refused, as the row on values from different steps says | `test_an_agent_change_on_a_halted_run_restates_the_halt`, `test_a_slider_moved_on_a_run_whose_snapshot_refuses_halts_it` |
| reading the value printed beside a dial dragged into a halt as the value the run holds | after writing its banner, the halt sets every dial from the run's record (`SimulationController.record()`), which gives the agent and the four settings in force. The record takes them from the settings the compartments hold, not from any compartment value. So the label beside the dial whose drag caused the halt shows the value that both the dial and the run hold. A run whose values cannot be read draws no new screen that could rewrite the label | `test_a_drag_that_halts_the_run_leaves_its_label_on_the_dial`, `test_a_halt_is_stated_before_its_dials_are_written` |
| reading a value under a label, a 1 MAC divisor or a verdict that describes a different step of the run | each value and what qualifies it come from one step, and values a halt leaves stale are withheld. § "Every value and what qualifies it come from one step" lists the groups and the cases | `test_every_value_and_its_qualifiers_on_screen_come_from_one_state`, `test_a_halt_after_an_agent_change_shows_no_mac_multiple_beside_another_agent_s_1_mac`, `test_the_accounting_panel_reports_the_failure_after_an_accounting_halt`, `test_a_setting_changed_on_a_halted_run_is_not_shown_as_the_setting_its_values_ran_under`, `test_a_setting_refused_at_the_supported_run_length_names_a_branch_only_while_one_can_be_taken`, `test_a_halt_that_no_frame_draws_after_the_run_started_over_says_its_readouts_are_withheld`, `test_a_stopped_run_refuses_every_setting_and_records_nothing` |
| believing a setting above the vaporizer maximum was simulated | such a setting is **rejected, not capped**, so no run continues on a value the user did not choose. The maximum itself is accepted by the circuit and by the record of settings a run is built from. That record carries the maximum beside the dial setting | `test_rejects_delivered_concentration_above_the_vaporizer_maximum`, `test_explicit_delivered_concentration_above_the_agent_max_is_rejected`, `test_accepts_delivered_concentration_exactly_at_the_vaporizer_maximum`, `test_rejects_a_dial_above_the_vaporizer_maximum`, `test_a_run_cannot_open_or_change_under_a_dial_above_the_vaporizer_maximum` |
| reading a displayed value as resolved to its last digit | the number of decimals shown is a recorded choice within a justified range. Only the display rounds. The model keeps the precision that the display discards | `test_the_model_keeps_precision_the_display_throws_away`, `test_concentration_decimals_are_a_choice_within_a_recorded_band` |
| reading a control mark on the timeline as a measurement | the timeline labels its marks "Settings only — not a measurement." | `test_the_interface_says_a_control_mark_is_an_input_not_a_measurement` |
| reading a modelled compartment value as a measured one | the readout section states, beside its values, that they are model outputs and not measurements (`INTERPRETATION_DISCLAIMER_TEXT`; § "The statement that the readouts are model outputs"). The chart's hover names every value it reports as modelled (§ "The chart's hover readout: what the tooltip may show") | `test_the_interface_says_the_readouts_are_model_outputs_not_measurements`, `test_the_readouts_say_they_are_model_outputs_beside_the_values`, `test_the_hover_reports_the_drawn_state_through_the_formatters` |
| reading one compartment's concentration as another's where two traces are drawn on top of each other | the compartment is named in text on every value line. The hover reports every compartment whose drawn point at the pointer's instant is inside the hover radius, each under its own name. It does not pick the nearest trace for the reader (§ "Where more than one trace answers"). This matters because the top of the percent axis is fixed at 3 MAC for every agent (`CHART_AXIS_TOP_MAC`), so the slow compartments are drawn within a pixel or two of one another, and no pointer position can pick one out from the others (§ "MAC multiples as a display unit") | `test_two_compartments_within_one_hover_radius_answer_under_their_own_names`, `test_a_contended_hover_names_no_run_while_only_one_is_drawn` |
| comparing two compartments of one run in one hover box as one moment when the box took them from different instants | every compartment of one run is reported at the run's drawn instant nearest the pointer in time. So the instant that labels a value depends only on the pointer's position along the time axis, and the pointer's height decides only which traces are in reach (§ "Where more than one trace answers") | `test_every_compartment_of_one_run_answers_at_one_instant`, `test_a_vertical_hand_movement_never_moves_the_instant_a_hover_reports`, `test_a_trace_answers_only_where_its_point_at_the_named_instant_is_in_reach` |
| reading the hover's value as a live readout after the pointer has left the plot | the hover box shows only while the pointer is over the plot (§ "When it answers"). When the pointer leaves the plot, the box closes at once, and no later screen update brings it back. A box left open would change with every screen update. While a run plays, its values would climb with the run, at an instant the reader is not looking at | `test_the_hover_hides_when_the_pointer_leaves_and_a_later_frame_does_not_bring_it_back` |
| reading one run's displayed value, or the record of what was changed on it, as the other's while two are compared | while more than one run is drawn, every place that shows a value, or the record of what was changed, names its run in text. § "Naming the run in a comparison" lists the seven places | `test_the_hover_names_the_run_only_while_more_than_one_is_drawn`, `test_two_runs_within_the_hover_radius_answer_under_their_own_names`, `test_a_small_pointer_movement_never_swaps_which_run_the_hover_answers`, `test_the_wash_in_state_and_off_scale_lines_name_their_run`, `test_a_lone_run_leaves_the_shared_chart_lines_unnamed`, `test_each_run_s_unmarked_changes_line_is_named_while_runs_are_compared`, `test_the_sidebar_panels_name_the_run_they_record`, `test_a_lone_run_leaves_the_sidebar_panel_headings_unnamed`, `test_the_halt_and_refusal_banners_name_their_run`, `test_a_halt_stated_without_a_frame_still_names_the_run_it_stopped`, `test_a_lone_run_leaves_the_notice_banner_unnamed`, `test_hidden_notice_banners_take_no_height`, `test_the_schematic_follows_its_run_through_a_reset_an_agent_change_and_a_comparison`, `test_the_panel_follows_its_run_through_an_agent_change_and_a_comparison` |
| reading a preview of a dragged setting as part of the run that happened | the preview is drawn only while the slider handle is held, inside a tinted region with a label saying the value is not applied, and the hover never reports from it (§ "A preview of an unapplied setting") | `test_a_held_thumb_previews_the_setting_without_applying_it`, `test_a_preview_is_drawn_only_inside_its_region_with_its_label`, `test_the_hover_never_answers_from_a_preview` |
| reading a cost as a figure the project supplies, or as computed at a price other than the one it used | the project supplies no price. A cost is shown only beside the two rounded numbers it multiplied and the price they came from, with words saying that the price is the reader's (§ "A cost at the reader's price") | `test_no_cost_is_shown_until_the_reader_sets_a_price`, `test_the_cost_is_the_delivered_liquid_times_the_bottle_price_over_the_bottle_volume`, `test_the_displayed_cost_reproduces_gas_man_s_printed_costs`, `test_the_cost_is_computed_from_the_unrounded_figures_not_the_ones_shown`, `test_each_run_is_priced_at_its_own_agent_s_price`, `test_no_cost_is_shown_where_one_cannot_be_trusted` |
| reading a cost computed from a price entered in the wrong form: a price per millilitre typed as the bottle price, a bottle volume typed in litres or as a count of bottles, the price and the volume swapped, or a price in another currency | the price is entered as a bottle price and a bottle volume in named units, and the readout shows the price per millilitre of liquid they give and the currency's ISO 4217 code (§ "A cost at the reader's price") | `test_an_entry_that_is_not_a_plain_positive_price_is_refused_with_its_reason`, `test_a_refused_entry_changes_nothing_and_says_why`, `test_a_price_per_millilitre_is_shown_to_four_figures_in_millilitres_of_liquid`, `test_a_currency_that_is_not_three_capital_letters_is_refused` |
| reading a container's fill height, or its filled area, as the amount of agent it holds | a container's height shows the compartment's tension on the concentration chart's own scale, and its amount is printed beside it and on a share bar (§ "The compartment schematic: what its heights, amounts and share bar assert") | `test_a_container_s_height_is_its_tension_and_not_its_amount`, `test_fat_s_share_grows_through_the_first_hour_while_its_container_stays_nearly_empty`, `test_the_share_bar_is_painted_to_each_share_and_named_in_text`, `test_the_circuit_fills_to_its_closed_form_tension_on_the_chart_s_scale`, `test_a_tension_above_the_chart_s_top_fills_the_container_and_keeps_its_value` |
| reading an amount of agent vapour as millilitres of liquid, or a liquid-equivalent amount as vapour, which misreads it by a factor of about 180 to 210, depending on the agent | no panel prints a bare "mL" beside an agent amount: every amount says vapour or liquid (§ "The compartment schematic: what its heights, amounts and share bar assert") | `test_no_agent_amount_is_printed_with_a_bare_millilitre_unit`, `test_the_delivered_agent_is_shown_at_its_derived_precision_with_its_unit_named`, `test_patient_inputs_reach_the_drawn_liquid_figure_through_the_model`, `test_a_unit_picked_in_one_view_reaches_every_view_and_survives_a_restart` |

<!-- provenance: app/formatting.py CHART_AXIS_TOP_MAC = 3 -->

## Required invariants

The simulator must always meet the following conditions:

- all volumes are finite and positive;
- fresh gas flow, alveolar ventilation, cardiac output, and tissue flows are finite and nonnegative;
- partition coefficients are finite and positive;
- tissue flow fractions sum to one within tolerance (§ "Tissue groups");
- stored agent amounts remain finite and nonnegative;
- derived partial-pressure-equivalent fractions remain finite and within 0 through 1;
- no compartment creates agent spontaneously;
- internal transfers remove and add equal amounts;
- changing a setting does not reset dynamic state;
- Pause stops simulated time from advancing;
- Reset clears dynamic state while preserving settings;
- a delivered concentration above the agent's vaporizer maximum is refused, not capped;
- zero fresh gas flow prevents new external delivery;
- zero ventilation prevents circuit-to-patient ventilatory exchange;
- zero cardiac output prevents pulmonary and tissue perfusion;
- zero tissue flow prevents uptake by that tissue; and
- equilibrium produces no net internal transfer.

**For developers.** The simulator must also meet these conditions on its time steps:

- identical runs produce identical state and run definition, element for
  element, however the steps were grouped in real time;
- simulated time is the number of completed steps times the run's step length;
- a step is refused when its length is outside the allowed range
  (`MINIMUM_SIMULATION_STEP_S` to `MAXIMUM_SIMULATION_STEP_S`) or differs
  from the length of the run's earlier steps; and
- a step that cannot be completed leaves simulated time and dynamic state
  exactly as the last completed step left them.

## Required tests

### Preserved circuit reference tests

The v0.0.2 analytic wash-in and washout tests must remain unchanged and continue to pass.

With no patient ventilation, tests check that the simulated circuit washes in and out as

$$
F_I(t) = F_D+\left[F_I(0)-F_D\right]e^{-t/\tau_C}
$$

where

$$
\tau_C =
\frac{V_C}{\dot V_F}
$$

in compatible time and flow units.

**For developers.** The wash-in and washout tests from v0.0.2 must stay unchanged and keep passing.
The tests for wash-in are `test_circuit_matches_analytic_wash_in` and
`test_wash_in_is_monotonic_and_never_overshoots` in `tests/reference/test_circuit_wash_in.py`,
and the test for washout is `test_zero_delivered_concentration_washes_out_circuit` in
`tests/unit/test_circuit.py`.

### Zero-agent test

If the model starts with no agent and none is delivered ($`F_D=0`$), every
stored amount and concentration must remain zero.

**For developers.** A test in `tests/reference/test_sevo_patient.py` enforces
this requirement (`test_no_delivered_agent_keeps_every_store_zero`).

### Zero-ventilation test

If $`\dot V_A=0`$, the circuit may wash in, but the patient compartments must receive no new agent through ventilation.

**For developers.** A test checks the zero-ventilation case
(`test_zero_ventilation_prevents_patient_delivery` in
`tests/reference/test_sevo_patient.py`).

### Zero-cardiac-output test

If $`Q=0`$, alveolar gas may change through ventilation, but arterial blood, venous blood, and tissue stores must not change through perfusion.

**For developers.** A test enforces this requirement
(`test_zero_cardiac_output_prevents_patient_uptake` in `tests/reference/test_sevo_patient.py`).

### Zero-tissue-flow test

For any tissue $`i`$, $`Q_i=0`$ must imply $`\frac{dM_i}{dt}=0`$. Two tests
check this.

**For developers.** One test checks the coupled system's matrix
(`test_a_zero_tissue_flow_leaves_that_group_alone` in
`tests/unit/test_governing_equations.py`). The other checks that a tissue's
state stays unchanged at zero flow (`test_zero_flow_preserves_tissue_state` in
`tests/unit/test_tissue.py`).

### Equilibrium test

If all connected compartments have the same partial-pressure-equivalent
fraction, with $`F_I=F_A=F_a=F_v`$ and every tissue group at the same value,
then all internal transfer rates must be zero. A test checks this for
sevoflurane, isoflurane and desflurane.

**For developers.** The test is
`test_equilibrium_produces_no_net_internal_transfer`, in
`tests/reference/test_sevo_patient.py` for sevoflurane and in
`tests/reference/test_multi_agent.py` for isoflurane and desflurane.

### Directional ventilation test

When all else is equal, more alveolar ventilation must make $`F_A`$ approach
$`F_I`$ faster. A test runs the default sevoflurane wash-in at 2 and 8 L/min of
alveolar ventilation, and requires $`F_A/F_I`$ to be higher at 8 L/min at every
whole second of the first minute. In these runs, $`F_I`$ rises more slowly at
the higher ventilation, because the circle system rebreathes and more
ventilation carries more agent into the patient.

**For developers.** The test is
`test_higher_ventilation_closes_the_alveolar_to_inspired_gap_faster` in
`tests/reference/test_sevo_patient.py`. It compares $`F_A/F_I`$ because $`F_A`$
alone shows the approach to $`F_I`$ only when $`F_I`$ is the same in both runs.

### Directional solubility test

In controlled synthetic cases, raising $`\lambda_{b:g}`$ must increase blood capacity and slow the rise of $`F_A/F_I`$.

**For developers.** That test is
`test_higher_blood_gas_solubility_slows_alveolar_to_circuit_rise` in
`tests/reference/test_sevo_patient.py`.

### Directional tissue-capacity test

With the tissue's blood flow $`Q_i`$ unchanged, the tissue time constant $`\tau_i`$ must lengthen when the tissue is larger ($`V_i`$) or the agent is more soluble in it
($`\lambda_{i:b}`$):

$$
\tau_i =
\frac{V_i\lambda_{i:b}}{Q_i}
$$

**For developers.** The test is
`test_a_larger_or_more_soluble_tissue_has_a_longer_time_constant` in
`tests/unit/test_tissue.py`.

### Washout test

After loading the compartments, setting $`F_D=0`$ must produce a finite,
nonnegative washout in which the total mass of agent in the system never rises.
Individual tissue concentrations may rise for a time through redistribution.

**For developers.** The washout test therefore must not require every
compartment to decrease monotonically. It is
`test_washout_never_increases_total_system_mass` in
`tests/reference/test_sevo_patient.py`.

### Step-refinement test

**The time step changes the model's results only by computer rounding.** The
simulation advances in steps of time. The model solves its equations exactly
over each step. It accepts steps from 1 ms up to 0.1 s, the step the
application uses.
<!-- provenance: app/dashboard_frame.py SIMULATION_STEP_S = 0.1 -->
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

Two tests compare runs at different steps and require their results to agree
to within rounding. The first uses the application's step and two smaller
steps, each half the one before, and compares the alveolar, vessel-rich and
mixed-venous concentrations after 60 s. The second compares the application's
step with the smallest step the model accepts, over the same 60 s.

Passing these tests shows only that the application's step is short enough for
the model's equations to be solved accurately. It does not show that the model
matches a patient. A model with a wrong transfer rate would pass, because it
gives the same answer at every step. § "Independent-solution test" below checks
that the equations are solved correctly, and § "Published wash-in and
elimination validation test" compares the model with measured patients.

**For developers.** The first test is `test_step_refinement_converges`, and the
second is `test_the_smallest_supported_step_lands_on_the_ceilings_solution`.
Both are in `tests/reference/test_sevo_patient.py`. The first compares at least
these steps:

```text
dt = 0.1 s
dt = 0.05 s
dt = 0.025 s
```

The coarsest is the largest step the model accepts (`MAXIMUM_SIMULATION_STEP_S`),
and the finest is 25 times the smallest (`MINIMUM_SIMULATION_STEP_S`). Two step
sizes can show only that a pair of runs agree, and three show that the step does
not change the result.

The first test compares successive halvings (0.1 against 0.05, then 0.05
against 0.025) rather than each step against the finest.
<!-- not-restated: 0.05 -->

The first test requires every gap to stay below 1e-14, a bound at the level of
rounding error. Gaps are absolute differences in concentration, expressed as a
fraction. The worst gap between successive halvings is 3.4e-16, in the alveolar
concentration (from a run on 2026-11-01). The 1e-14 limit was set on 2026-09-06
at about twelve times the worst gap then, 8.1e-16. The run behind that figure
reported four values, and no record names the fourth. The test has compared the
same three concentrations since the method became exact.

A method that does not solve the equations exactly fails the 1e-14 limit,
because its result moves with the step. Euler's method, for example, gives gaps
up to 1.8e-6 at the first test's steps (from a run on 2026-11-03). To test such
a method, check that each halving of the step shrinks every gap by a predicted
factor. The factor is about two when the error is proportional to the step, as
Euler's is. The model's own gaps do not shrink with the step.

The second test allows 3e-14 in each compared concentration. That is wider than
1e-14 because its minute takes 60 000 steps rather than at most 2 400, and
rounding builds up once per step. Its worst gap is 2.4e-15, in the alveolar
concentration (from a run on 2026-10-03), so the limit is about twelve times
that gap, the same margin as the first test's. The gap does not change smoothly
with the step. It depends on how the calculation happens to round at each step
size. At steps near 1 ms the gap reaches 1.2e-14, so on a machine that rounds
differently, the margin could be nearer two and a half times. The test expects
the smallest step to be 1 ms, so whoever changes that step must find these gaps
again with a new run.
<!-- provenance: core/simulation_step.py MINIMUM_SIMULATION_STEP_S = 0.001 -->

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
   the published mean coefficients, that compartment's term is the largest in the measured
   curve for most of the supported span (the intertissue-diffusion note under § "Known
   limitations" gives the hours). At five minutes, that term is about one part in twenty of what remains. A comparison over those
   hours would measure an omission rather than a parameter. So the gap over those hours is
   measured beside this comparison and is not part of it. § "The first 24 hours of elimination
   against the published mean curves" records its size and direction hour by hour, and claims
   no agreement.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

<!-- not-restated: 6 % -->

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
here, for three separate reasons, any one of which is sufficient.**

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

**Over the first 25 minutes, sevoflurane and isoflurane follow the published
wash-in curves within one SD** (simulated 2026-10-18). Desflurane's $`F_A/F_I`$
runs 0.034 to 0.042 above its published curve from 1 to 10 minutes, and agrees
from 12.5 minutes on. This early gap is a known limitation of the model. The
model is compared with each curve point by point because $`F_A/F_I`$ at 30
minutes alone would barely show an error in the lung's gas volume or the circuit.

Neither paper tabulates its $`F_A/F_I`$ curve, so the published values were read
from page scans of each paper's Figure 2. Both figures plot the curve during
administration as mean ± SD, with each SD drawn on one side of the marker. Each
30-minute point read from them lies within 0.006 of the value stated in the
paper's text, so a reading error here is about 0.006. Three of the 1-minute SDs
are hidden among overlapping marks near the axis, so the comparison uses the
next readable SD of the same cohort instead. A separate note records how the
figures were read and every value taken from them
(`docs/references/yasuda-1991-figure-2-wash-in.md`).

**The comparison holds $`F_I`$ fixed from the start, which no setting of the
simulator does.** Both papers gave the agents as a square wave from a
non-rebreathing circuit, so $`F_I`$ was the cylinder's fraction from the first
breath (*Anesth Analg* p. 317, *Anesthesiology* p. 490). The simulator's circuit
instead fills at its own time constant, so its $`F_I`$ lags the dial for the
first minute or more. In every other respect, the comparison runs the simulator
as released.

Simulated on 2026-10-18, as the model's distance from each published mean, in
units of that point's SD:

| Cohort | 1 to 3 min | 5 min | 7.5 to 25 min |
| --- | --- | --- | --- |
| Sevoflurane, n=7 | −0.54 to −0.69 SD | −0.22 SD | +0.48 to +0.77 SD |
| Isoflurane, n=7 | −0.70 to −0.83 SD | −0.19 SD | +0.34 to +0.76 SD |
| Isoflurane, n=8 | −0.60 to −0.67 SD | +0.08 SD | +0.32 to +1.06 SD |
| Desflurane, n=8 | +1.79 to +1.82 SD | +1.82 SD | +2.10 SD at 10 min, then +0.94 to +0.28 SD |

<!-- not-restated: 0.34 -->

<!-- not-restated: 0.54, 0.76, 2.10 -->

**The model's sevoflurane and isoflurane curves sit a little below the published
ones in the first 3 minutes and a little above from 7.5 minutes on.** Their only
point beyond one SD is isoflurane at 12.5 minutes, +1.06 SD, which is within a
reading error of one SD.

**The desflurane gap likely comes from something that only desflurane has**,
such as its blood:gas or a tissue:gas coefficient. The model's settings are an
unlikely cause, because the eight volunteers in the desflurane cohort breathed
isoflurane from the same cylinder as desflurane, and the model follows their
isoflurane curve. An error in ventilation or lung volume would move every agent
the same way, but sevoflurane and isoflurane sit slightly below their curves
early on.

**No single stored coefficient closes the gap when it is varied only within its
measured range** (simulated 2026-10-18). The runs changed one desflurane
coefficient at a time and left every other value as stored:

- **Blood:gas is the only coefficient that brings the early points within one
  SD, and it does so only at values where the 30-minute comparison fails.** The
  1-to-10-minute points come within one SD once blood:gas is about 0.55 or
  higher. Eger's 0.424 ± 0.024 falls short of 0.55 even at the edge of its
  spread. Esper et al. 2015 measured 0.57 ± 0.04 in surgical patients, and at
  0.57 every early point lies within 0.83 SD. But the 30-minute ratio stays
  within one SD at every fresh gas flow from 1 to 10 L/min only while blood:gas
  is about 0.46 or lower. At 0.57 it falls outside one SD at every flow, from
  −1.35 SD at 10 L/min to −2.61 SD at 1 L/min. Raising blood:gas to 0.57 moves
  desflurane's open-circuit 5-minute washout ratio only from −2.33 SD to
  −1.97 SD.
- **The vessel-rich and muscle coefficients cannot close the gap** at any value
  within Yasuda et al. 1989's measurements (brain 0.54 ± 0.02, muscle
  0.94 ± 0.35).

<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->
<!-- not-restated: 0.54 -->

No stored value is changed. Using Esper's blood:gas value for desflurane alone
would mix coefficients from two sources. Esper's values for all three agents
would put the sevoflurane and isoflurane points in the first 3 minutes 1.0 to
1.4 SD below their curves. The stored values would be weighed again in the
planned primary-literature coefficient set (`ROADMAP.md` planned-milestone item 31).

**The model has no second-gas effect, and the early curve is where one would
show first.** Caveat 1 above applies here too. The effect's size in these
volunteers was not measured. They had breathed 70% nitrous oxide for 30 minutes
before the potent agents started, and 65% throughout, so their nitrous oxide
uptake was already low and the effect was probably small.

**For developers.** The comparison runs in a driver that only the tests use
(`_clamped_wash_in()` in `tests/reference/test_published_wash_in_and_elimination.py`).
After every step, the driver sets the circuit back to the fixed $`F_I`$ and
records the agent it adds or removes, so the model's check that the amount of
agent is conserved still passes.

The five desflurane points from 1 to 10 minutes and the isoflurane point at 12.5
minutes are checked against a regression band, from −1 to +2.5 SD, instead of within one SD. A regression band guards the model's own result against change and claims no agreement with the data. The band's upper edge is above the largest distance simulated, +2.10 SD,
so the gap cannot grow past +2.5 SD without a test failing.
<!-- not-restated: 2.10 -->

#### What the published-data gate can and cannot resolve

**For most stored values, passing the published-data gate rules out only large
errors** (from model runs on 2026-10-18). The gate is the set of checks that
compare the model with published measurements in people. A pass does rule out a
model whose structure is wrong.

The gate contains the early wash-in points from 1 to 25 minutes, run with F_I
held at the airway (§ "The early wash-in curve against the published figures"
above). It also contains the 30-minute wash-in band for each cohort at every
fresh gas flow from 1 to 10 L/min, the sign of the elimination disagreement for
each cohort, and both solubility orderings.
<!-- provenance: core/supported_ranges.py MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10 -->

The regression pins are not part of the gate, because they compare the model
with its own output. They include the 5-minute elimination pin above and the
late-washout tables. A pin fails on any change at all, so it catches an
accidental edit. It cannot show whether a comparison with published data would
have caught a wrong stored value.

Each cell of the table below covers one stored parameter for one agent. It gives
the lower and upper edges of the range of change over which the gate still
passes (from model runs on 2026-10-18). Each parameter was varied from a tenth
to four times its stored value, with every other value unchanged. The edges
were found to the nearest half a percentage point. An edge marked "past", such
as "past −90%", means that the gate still passed at a tenth or at four times the
stored value.

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

The first row's percentages apply to the stored blood:gas coefficients: 0.65
for sevoflurane, 1.3 for isoflurane and 0.42 for desflurane. The tissue:gas
coefficients stay as shipped when blood:gas changes, so each tissue:blood
coefficient moves inversely, as it would if the stored blood:gas value alone
were wrong.
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->

A tissue's volume and its tissue:gas coefficient give the same edges, because a
run depends only on their product, the tissue's capacity.

**Two tests keep the table in step with the code.** One fails if the gate stops
detecting a change that it detects today. The other fails if the gate starts to
detect a change that this section says it cannot.

**The table supports these conclusions about a pass of the gate:**

- **A narrow edge is not a narrow uncertainty.** Most of the narrowest edges
  come from the 12.5- and 15-minute points, where the shipped model already sits
  at +0.75 to +0.94 SD. There, a change that raises the curve by a few tenths of
  an SD takes it past the gate's limit of +1 SD. So isoflurane's −1% edge for
  blood:gas means that the shipped model has little room left there, not that
  the stored coefficient is known to 1%. The published figure can be read to
  about 0.3 SD, so an edge reached by a smaller movement of the curve is within
  the reading error.
- **For sevoflurane and isoflurane, the gate detects both a rise and a fall in
  blood:gas and in the vessel-rich group.** The edges lie between 1% and 15%.
  The 12.5- and 15-minute points set every lower edge. The 2- and 3-minute
  points set isoflurane's upper blood:gas edge and both agents' upper
  vessel-rich edges. The 30-minute wash-in band at 1 L/min sets the other upper
  edges, and most of desflurane's.
- **The gate detects an alveolar gas volume that is too large.** Making the
  volume a fifth to a third larger slows the first minute of wash-in enough to
  take it outside one SD for every agent. Doubling the volume moves
  sevoflurane's 1-minute F_A/F_I from 0.537 to 0.429, which is −2.85 SD. The
  gate does not detect a smaller volume for sevoflurane.
- **Desflurane's edges reflect its disagreement with the published data.**
  Its points from 1 to 10 minutes sit at +1.7 to +2.1 SD. They are checked
  only against a looser regression band, which ends at +2.5 SD. So its −8% lower edge for
  alveolar gas volume is set by that band, not by a limit of one published SD.
- **The gate detects no change at all in fat for sevoflurane or isoflurane.**
  That is expected of checks that cover 30 minutes of wash-in and 5 minutes of
  washout. Fat solubility and fat volume set the hours-long tail of washout,
  from which a learner judges emergence. Nothing here checks them against a
  measurement. § "The first 24 hours of elimination against the published
  mean curves" compares that tail with the published fits, but does not
  require the two to agree.
- **The gate constrains muscle only loosely.**
- **The gate does not detect a smaller circuit** for sevoflurane or isoflurane,
  down to a tenth of the stored value. The early points are run with F_I held
  at the airway, so the circuit does not affect them.

<!-- provenance: core/supported_ranges.py MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86400 -->

<!-- not-restated: 2.1, 8 % -->

The wash-in ratio at 30 minutes and the elimination ratio at 5 minutes respond
to almost separate sets of parameters, which is why the edges fall where they
do. The table below shows how far each ratio moves when one coefficient is
raised by 10%, in units of that ratio's own published SD (from model runs on
2026-09-06):

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
offset fixed by the reference settings.

**For developers.** The regression pins include the reference states recorded
in `tests/reference/test_coupled_dynamics.py` (`PINNED_REFERENCE_STATES`). No
pin may be cited as validation of a stored value.

The test that expects the gate to fail checks every agent at blood:gas ×0.90
and ×1.15, vessel-rich tissue:gas ×0.80 and ×1.75, and alveolar gas volume
×1.50 (`test_the_published_data_gate_fails_at_a_stated_perturbation`). It does
not use ×1.10 for blood:gas, because that is too close to desflurane's edge at
×1.097.
<!-- not-restated: 1.10 -->

The test that expects the gate to pass checks every agent at fat tissue:gas
×0.50 and ×2.00, fat volume ×2.00, muscle tissue:gas ×1.50 and circuit volume
×0.50 (`test_the_published_data_gate_passes_at_a_stated_perturbation`). It also
checks alveolar gas volume ×0.50 for sevoflurane, venous pool volume ×0.50 for
sevoflurane and desflurane, and venous pool volume ×2.00 for desflurane. The
other agents have an edge at or inside those factors.

Each factor in the two tests sits well clear of its edge, because a test placed
at an edge would be 0.01 to 0.03 SD from flipping. Both tests run the gate at
its shipped limit (`AGREEMENT_TOLERANCE_SD`). The limit is the published
spread, not the band.

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
the fourth compartment's term is the largest over most of these hours (the
intertissue-diffusion note under § "Known limitations" gives them). This model has no such term.
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

**The result does not bear on § "Supported run length"**, which gives the full reasoning.

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

Long wash-in, steady-delivery, and washout simulations must satisfy either
condition below, with the release tolerances documented above:

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

**For developers.** A sevoflurane test enforces these conditions
(`test_long_wash_in_and_washout_validate_agent_simulation` in
`tests/reference/test_sevo_patient.py`). A second test applies them to
isoflurane and desflurane (`test_wash_in_and_washout_validates_agent_simulation`
in `tests/reference/test_multi_agent.py`).

### Closed-form agreement test

The closed form computes a run's state directly from the run definition. The
stepped solver advances the run one time step at a time. For a run driven
through its own controls, the two must give identical states at each instant
that the stepped solver passed through. The stepped solver was written
independently of the closed form to solve the same equations, so agreement is
the evidence that the closed form solves them correctly.

The comparison covers every compartment at every instant probed, not only the
first and the last (§ "Deterministic replay test" explains why). It must also
cross at least two setting changes, because a stretch of constant settings is
the easy case, and the run definition has to get each change right.

The comparison's tolerance is far smaller than the second decimal place of a
displayed percentage (§ "Displayed precision"), and far larger than the
rounding error of computer arithmetic. A real divergence therefore fails the
test, and a rounding difference does not.

**For developers.** The tolerance is absolute, in fractions of one atmosphere,
because that is what the compartments contain and what a readout converts. A
relative tolerance would tighten without limit on the near-zero tissue fractions
of an induction, and it would say nothing about a displayed digit.

Two tests compare the closed form's functions (`state_at` and `evaluate`) with
a run stepped alongside its definition. Both use one run that crosses two
setting changes
(`test_evaluate_matches_a_stepped_run` and `test_state_at_matches_a_stepped_run`
in `tests/unit/test_run_definition.py`). Other tests make the same comparison in
two more cases: a system started at a keyframe and stepped from there, and a
branch compared against its parent (`tests/unit/test_resume_at.py` and
`tests/integration/test_controller.py`). Each test records the difference it
found and the headroom left below the tolerance.

### Parameter-recovery test

The model must return a stored value, such as the alveolar volume, when this
test simulates a procedure that measures that value. Each procedure is derived
from a physical law, not from the equations in this document. Like the other
verification tests, this test checks that the equations are the ones intended.
It cannot show that a stored value is right, because each procedure recovers
whatever value the data files hold.

**This test catches a class of error that the other verification tests miss.**
The test in § "Independent-solution test" solves the equations as written in
this document, so it reproduces any error in them and still agrees with the
code. The test in § "Mass-balance test" catches an error only when agent is lost
or created. Suppose this document gave the tissue capacity as $`V_i\lambda_{i:b}`$,
leaving out the blood:gas factor $`\lambda_{b:g}`$, and used that capacity in the
tissue's rate equation. Agent would still be conserved, and the independent
solution would agree with the code. The tissue volume recovered by the Fick
principle would be the stored volume divided by $`\lambda_{b:g}`$.

The test runs two procedures for each of the three agents. The first recovers
the alveolar volume by closed-circuit dilution. Lerou and Booij checked their
own system model by simulating this measurement with helium (Lerou JG, Booij LH.
Model-based administration of inhalation anaesthesia. 1. Developing a system
model. *Br J Anaesth* 2001;86:12–28, doi:10.1093/bja/86.1.12; PMID 11575385,
retrieved from PubMed and read at the abstract 2026-10-25). The circuit fills
while ventilation is stopped. Setting the fresh gas flow to zero then closes the
circuit, and the lungs are ventilated from it with the cardiac output at zero.
With no blood flow, the agent behaves as an insoluble tracer, like helium in the
real measurement. Conservation then gives $`V_A = V_C(F_1-F_2)/F_2`$, where
$`F_1`$ is the circuit's fraction when it is closed and $`F_2`$ is the fraction
that the circuit and lungs share once they have mixed.

The first procedure is not the closed-circuit technique that § "Breathing
circuit" says this model does not represent. That technique needs fresh gas
matched to the patient's uptake. The procedure has no fresh gas and, at zero
cardiac output, no uptake.

The second procedure recovers each tissue group's volume from its uptake over
the initial wash-in. It adds up the uptake that the Fick principle gives,
$`\dot U_i = Q_i\lambda_{b:g}(F_a-F_i)`$. It then divides the total by the
amount of agent that one litre of the tissue holds at the end of the run,
$`\lambda_{i:g}F_i`$, where $`F_i`$ is the tissue's own fraction.

**For developers.** The tests for the two procedures are
`test_an_alveolar_volume_recovered_by_closed_circuit_dilution_matches_the_stored_value`
and `test_a_tissue_volume_recovered_from_its_washin_matches_the_stored_value`,
in `tests/reference/test_parameter_recovery.py`. The tolerance on each recovered
value is relative and at the level of rounding. The test module gives each
tolerance beside the difference between the recovered and stored values from a
run of the test.

### Deterministic replay test

When two runs have the same initial state, parameters, setting changes, order
of events and simulation steps, they must produce identical results over the
whole run. Agreement within a tolerance is not enough. A run branched from
another must be identical to it at every instant the two share.

The results must not depend on how the run was paced in real time, as
§ "The reproducibility guarantee" states. They must be the same at every
playback rate that the interface offers.

**For developers.** The two runs' snapshots must match in every field, and each
segment and keyframe of one run's definition must equal the matching one in the
other's. Comparing only the end values would pass two runs that diverged and
then came back together.

To vary the pacing, one run takes one step per tick and the other takes its
steps in uneven bursts. Between ticks, the interface reads one run more often
than the other. Pacing both runs the same way would test one trajectory twice,
so it could not show that pacing has no effect.

A playback rate paces a run in bursts of steps. One test takes its rates from
the interface's own list, so a rate added to that list is tested from the day it
is added.

The tests for this section are
`test_identical_runs_produce_identical_snapshots`,
`test_a_run_reaches_the_same_definition_however_the_ticks_fell` and
`test_a_run_reaches_the_same_definition_at_every_playback_rate`, in
`tests/integration/test_sevo_controller.py`.

### Canonical evaluation test

A run must give the same result, called its canonical result, whether or not
values are read from it while it is computed. The two results must match value
for value, in every quantity the model tracks, at every instant checked and in
every state the run stores. The canonical result therefore depends only on how
the run is defined.

When a run starts from a state that its parent run stored, it must match the
parent value for value at every instant they share.

Values computed for the display can differ from the canonical result.
§ "The canonical evaluation rule" publishes the difference. A test checks it
against a bound for each quantity, so a change to how values are computed
cannot silently move a figure this document prints. The program must refuse a display value wherever it needs a canonical one. That makes the rule a property of the program rather than of the reader.

**For developers.** The tests are in `tests/reference/test_canonical_evaluation.py`.
Two of them check that reading a run changes neither its results nor the states
it stores, called keyframes (`test_querying_a_run_does_not_change_what_it_answers`,
`test_querying_a_run_does_not_change_the_keyframes_it_stores`). A cache, a
memoised propagator or a reused buffer would cause such a change, while looking
like an optimisation. Another test checks that a run started from a stored state
matches its parent (`test_a_fork_opening_from_a_keyframe_reproduces_its_parent`).
That match is what § "The canonical evaluation rule" owes the work planned in `ROADMAP.md` item 12. The refusal
of display values has its own test (`test_a_display_value_cannot_open_a_run_definition`).

The test of the bounds fails on a change to the equations, to the propagator or
to how a window is walked (`test_the_display_path_stays_within_its_measured_separation`).
The compartment fractions and the cumulative accumulators have separate bounds
because their displays differ in resolution by four orders of magnitude. A single
bound for both would have to be the looser one.

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
gives what was ruled out. The one hypothesis left is the published value itself, which this project cannot test,
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
display.** Each agent's stored MAC is tier 3 under § "Source hierarchy".
§ "Delivery-limit and MAC parameters" measures its gap from Mapleson's age-40
meta-analytic values, and how much the choice of MAC source alone shifts a
sevoflurane-versus-desflurane comparison in MAC multiples. The shift is consistent within an agent and changes no curve's shape or
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
  note, carries the largest term in the measured washout over most of the
  supported span. All else equal, the modelled tail
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
  run length").
  `test_the_fourth_compartment_is_the_largest_term_over_the_recorded_hours`
  re-derives those hours from the coefficients. Without that store the modelled
  tail should fall faster, and it does. § "The first 24 hours of elimination
  against the published mean curves" gives where the shipped tail falls below
  the mean curves, and by how much. The size is known to about a factor of two, which is the fourth
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
kg, which is 4.84 L/min at 70 kg. It is **derived, not measured**
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
- no scientific `TBD` markers remain (none remain as of this revision);
- simulated wash-in passes validation against published data for every agent
  and cohort;
- mass balance closes within the documented tolerance;
- deterministic replay passes (§ "Deterministic replay test");
- changing a setting during a case keeps the simulation's current state;
- the interface contains the educational and non-clinical warning; and
- this document describes the behavior actually present in the tagged release.

The comparison of simulated elimination with earlier versions is not a
condition of release. It checks only that the results have not changed, and
does not show that they agree with published data.

**For developers.** A release also needs these checks to pass:

- the circuit reference tests from v0.0.2;
- the unit, integration, invariant and independent reference tests;
- the convergence and nonnegativity tests at every supported step size;
- Ruff formatting and linting;
- strict mypy;
- pytest; and
- GitHub Actions.

The comparison of simulated elimination with earlier versions is in the same
test module as the wash-in validation.

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
table, every output in the displayed-outputs list and every subsection of the
required tests. It does not yet check the entries of the required invariants.

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

**For developers.** These rules apply in part to the project's other documents.
The frozen lists in `ROADMAP.md` and the package map in `docs/ARCHITECTURE.md`
also promise an entry for each member, and each has checks of its own. The check
of a frozen list reads only the lines that open with an item id. The prose of
`ROADMAP.md` is treated as dated. Every thread in `docs/WORKING_NOTES.md` is
dated, so only the rule for dated statements applies to it. The rules do not
apply to prose about the project's workflow tooling, in `.claude/`,
`CONTRIBUTING.md` and `docs/resident-instructions.md`, where the rule on counts
is only advice.

A statement is about the code or its data when it says, for example, that a test
enforces a rule, that a field exists, that a value is *N*, or that a job runs
something. It names that thing as a test, path, symbol or field in fixed-width
type, or with a `<!-- provenance: -->` marker over a restated number. In the
documentation check (`tools/doc_check.py`), the functions that look up these
forms are `check_named_tests`, `check_citations`, `check_prose_provenance` and
`check_make_targets`. The strongest link for a figure from the model is a test
that reads it from this document, as
`tests/reference/test_mac_awake_washout_figures.py` does.

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
or note, and stops at the first paragraph that passes on its own. A date or a
source in the note covers only the note.

A paragraph with no test, fixed form, date or source passes only if a marker
covers each number that it states with a unit. A `provenance:` marker covers a
value the paragraph states, in that value's unit. A `derived:` marker covers a
figure that the paragraph works out, in the unit it writes, and each input the
paragraph states. A `not-restated:` marker covers nothing, because it says that
the paragraph's numbers are not stored values. So a computed figure cannot pass
on a marker written for a figure beside it.

Outside the lists and sections where the check looks for a missing name, a
command for the documentation review (`tools/doc_check.py candidates`) prints a
number without a marker, or a claim without a name in fixed-width type, when
the thing that the number or claim describes changes.

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

### What the data-file format requires of a `sources` entry

**The first and third of the rules for a `sources` entry in
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
that read the tier alone would report all four of this project's data files as
primary-sourced, although the reference patient adopts no primary source and
many of the table's rows are tier 3 (§ "Where this project stands" gives
the counts). That is the failure the second rule for a `sources` entry exists to prevent, so
the check reads the adoption and not the citation list. Today each agent file
declares two adopted primary sources, for `mac_awake` and for the vaporizer
maximum. `src/anesthesia_sim/data/patients/reference_adult.json` declares
none and records the gap.

**What the check does not decide is whether a citation labelled `primary`
really is one.** That needs somebody who has read the paper. A tool that
guessed, from the author, the journal or a product name in the title, would
look authoritative and be wrong. The tool checks that a claim was made and is
well-formed, and a reviewer checks that the claim is true.
