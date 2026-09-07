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
delivered sevoflurane
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
- explicit conservation of sevoflurane mass.

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

- sevoflurane entering through fresh gas;
- carrier gas entering through fresh gas;
- an equal volume of mixed circuit gas leaving through the circuit exhaust; and
- no metabolism or other chemical destruction of sevoflurane.

The circuit and patient form a closed recirculating exchange path except for fresh-gas inflow and circuit exhaust.

## Conventions

### Time

Simulation time is explicit state and is measured internally in seconds.

Flows entered in liters per minute are converted to liters per second:

$$
\dot V_{\mathrm{s}} = \frac{\dot V_{\mathrm{min}}}{60}
$$

Wall-clock time may schedule interface updates, but it must never be used as simulation time.

Seconds are the unit everywhere this document, the core, and the recorded
history state a time. The interface renders that one stored quantity in more
than one form and introduces no second unit doing so: the clock and every
recorded control stamp read in seconds, while the chart states both its axis
ticks and the width it is drawing as compound durations whose every component
carries its own unit. "The chart's time base" is why the chart differs and
"Displayed precision" is what each form is resolved to.

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
needs a single step to multiply by, and a history recorded at two cadences
has a sample spacing that is not a constant of the run — which every reader
that maps a recorded sample index to a time assumes it is. Reset clears the
count and the step together, so a fresh run may take a different one.

#### The reproducibility guarantee

**A run is a function of its inputs and of the number of steps taken, and of
nothing else.** The interface schedules its ticks with the wall clock, but
how many steps a tick takes is a setting the reader chooses and never a
measurement the loop makes: no tick takes extra steps to make up simulated
time a slow tick lost, and the run loop reads no clock. A machine
that wakes the loop late, drops a frame, or runs the whole session slowly
therefore produces a run that reaches a given step *later in real time* and
is identical in every recorded sample. It runs slower; it does not run
differently.

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
identical** recorded histories and snapshots — identical, not agreeing
within a tolerance — and recorded sample *n* is at simulated time *n* times
the step in both. This is the property a comparison of one run against
another rests on, including the planned comparison of a branched run against
the run it branched from at every sample they share.

**Playing a run faster does not make it a different run.** The interface
offers a playback rate — how much simulated time advances per second of real
time — and it is implemented as the number of *whole steps* a tick takes,
never as a larger step. The same case played at real time and at three
hundred times real time is therefore the same steps, in the same order, at
the same size: element-wise identical recorded histories, reached at
different real times. A rate that resized the step instead would fall under
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

The interface alone converts between fraction and percent:

$$
\text{percent} = 100F
$$

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

Every compartment stores sevoflurane as an equivalent gas volume at one documented reference temperature and pressure.

The implementation must use the same reference conditions everywhere. It must not add gas fractions, dissolved blood concentrations, and tissue concentrations directly.

Let $`M_x`$ denote the equivalent gas volume of sevoflurane stored in
compartment $`x`$.

The unit used in code is liters of equivalent pure sevoflurane gas unless the implementation document explicitly selects another consistent unit.

## Symbols

| Symbol | Meaning | Unit |
| --- | --- | --- |
| $`t`$ | Explicit simulation time | s |
| $`\Delta t`$ | Simulation step | s |
| $`F_D`$ | Delivered fresh-gas sevoflurane fraction | dimensionless |
| $`F_I`$ | Inspired sevoflurane fraction, which is the gas in the breathing circuit (see "Model boundary") | dimensionless |
| $`F_A`$ | Alveolar sevoflurane fraction | dimensionless |
| $`F_a`$ | Arterial partial-pressure-equivalent fraction (flow-limited: $`F_a \equiv F_A`$; not an independent state) | dimensionless |
| $`F_v`$ | Venous blood partial-pressure-equivalent fraction | dimensionless |
| $`F_i`$ | Tissue group $`i`$ partial-pressure-equivalent fraction | dimensionless |
| $`V_C`$ | Mixed breathing-circuit volume | L gas |
| $`V_A`$ | Modeled alveolar gas volume | L gas |
| $`V_v`$ | Venous blood-pool volume | L blood |
| $`V_i`$ | Volume of tissue group $`i`$ | L tissue |
| $`\dot V_F`$ | Fresh gas flow | L gas/min |
| $`\dot V_A`$ | Alveolar ventilation | L gas/min |
| $`Q`$ | Cardiac output | L blood/min |
| $`Q_i`$ | Blood flow to tissue group $`i`$ | L blood/min |
| $`\mathrm{MAC}_\%`$ | Agent's 1 MAC, age-40 alveolar (display divisor only; not in any governing equation) | percent |
| $`\lambda_{b:g}`$ | Sevoflurane blood:gas partition coefficient | dimensionless |
| $`\lambda_{i:b}`$ | Tissue:blood partition coefficient for group $`i`$ | dimensionless |
| $`M_C`$ | Sevoflurane stored in the breathing circuit | L equivalent gas |
| $`M_A`$ | Sevoflurane stored in alveolar gas | L equivalent gas |
| $`M_v`$ | Sevoflurane stored in venous blood | L equivalent gas |
| $`M_i`$ | Sevoflurane stored in tissue group $`i`$ | L equivalent gas |

## Compartment capacities

### Gas compartments

The equivalent sevoflurane amount in the breathing circuit is:

$$
M_C = V_C F_I
$$

The equivalent sevoflurane amount in the alveolar gas compartment is:

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

so the same relationship may be written:

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
- a sevoflurane tissue:blood partition coefficient $`\lambda_{i:b}`$;
- a stored sevoflurane amount $`M_i`$; and
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

## Conservation of sevoflurane

### External delivery

The cumulative delivered sevoflurane amount is:

$$
M_{\mathrm{delivered}}(t) = \int_0^t \dot V_FF_D\,dt
$$

### Circuit exhaust

The cumulative exhausted sevoflurane amount is:

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
MASS_BALANCE_ABSOLUTE_TOLERANCE = 1e-12 L
MASS_BALANCE_RELATIVE_TOLERANCE = 1e-9
```

A step passes if either tolerance is satisfied. The relative error uses `max(initial + delivered, 1e-15 L)` as its denominator to avoid division by zero when no agent has yet been delivered. Exceeding both stops the run: this is the point past which the model refuses to show a number, not the standard the shipped model is held to.

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
SIMULATION_STEP_S          = 0.1   # app/simulation_view.py
SIMULATION_TICK_INTERVAL_S = 0.1   # app/simulation_view.py
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

| Playback rate | Control grid | Frames are | Worst displacement per grid step |
| --- | --- | --- | --- |
| 1× | 0.1 s | 0.2 s | 1.4×10⁻¹ pp |
| 5× | 0.5 s | 1 s | 7.0×10⁻¹ pp |
| 20× | 2 s | 4 s | 2.5 pp |
| 60× | 6 s | 12 s | 5.8 pp |
| 300× | 30 s | 60 s | 1.0×10¹ pp |

Every column is in simulated seconds except the last, which is the same
measurement the table above reports, re-run at each rate over the same three
manoeuvres and all three agents (2026-09-06, `PL-NBWP`). The binding case is
the ventilator start with desflurane throughout; the case opening is about 21×
milder at 1×, and **the gap narrows as the grid coarsens** — to 19× at 20×, 16×
at 60× and about 7× at 300×, where an ordinary dial change reaches 1.5 pp. The
narrowing is the same effect as the row above it: **the binding manoeuvre's
displacement saturates rather than scaling with the delay** — its transient has
largely run by the time a 30 s grid step has passed — so extrapolating the 1×
figure linearly over-states 300× by about four times, while the case opening's
displacement is still nearly linear in the delay and so keeps growing. The
measured values are the ones to use, and the ratio is not one of them to
extrapolate either.

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
- Flet;
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
whether anything was measured there. Three tiers are distinguished, and only
the first may be named as the authority for a stored value.

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
   Never the authority for a stored value: the rounding and the selection
   between disagreeing measurements happened somewhere the reader cannot see.
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

**Where this project stands, stated rather than implied.** Of the 29 rows in
the provenance table below, 26 are tier 3. All twelve partition coefficients
are the Gas Man set as published by De Wolf et al.; all eleven physiologic
parameters in `src/anesthesia_sim/data/patients/reference_adult.json` are the
Gas Man default patient; and the three `mac_percent` values are the MAC values
De Wolf et al. state they used in their Gas Man simulations, with two
tier-2 sources cited alongside but not adopted — Mapleson's 1996 meta-analysis
and the age-related iso-MAC charts built on it. The three
exceptions are the vaporizer maxima, which cite manufacturer device
specifications — the primary source for a device capability, since no
measurement is at issue.

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
`PL-7HDS` carries reading Lowe and Ernst, which is the link that decides
whether this chain ends in a measurement or in another compilation. Neither is
assumed here: a 1981 monograph nobody has opened is recorded as located and
unread, which is the discipline the Mapleson entries were removed for failing.

**Lowe and Ernst has since been read at one remove, and is still not opened.**
On 2026-09-06 the project owner supplied two peer-reviewed papers that used the
book — Lerou and Booij's system model (*Br J Anaesth* 2001;86:12–28) and Couto
da Silva, Mapleson and Vickers' study of Lowe's method (*Br J Anaesth*
1997;79:103–12) — both read here at full text. The initial is `HJ`; the
Workbook's `HF` is a misprint. More usefully, the book supplies this material as
**fractions of body mass and of cardiac output, with cardiac output itself
allometric** — 0.2 times body mass to the three-quarter power, which is
4.84 L/min at 70 kg rather than the 5.0 stored here. Lerou and Booij's Table 6
prints eight such compartments, captioned as data given by Lowe and Ernst and
cited to **page 57** of the book.

**Checked against that table, the Workbook's attribution holds for two of the
seven values.** At 70 kg the kidney, heart, brain and liver rows sum to 6.02 kg
at a flow fraction of 0.760, reproducing the stored vessel-rich pair; muscle
(29.8 kg at 0.130) and adipose (10.5 kg at 0.050) do not reproduce the stored
33.0 at 0.18 and 14.5 at 0.06, and no grouping of the eight compartments does.
Alveolar volume is untouched, Lerou and Booij deriving their alveolar space
rather than taking it from the book. That arithmetic is this project's, from a
table read at second hand, and it convicts the Workbook of nothing — Gas Man may
lump compartments differently, or read a different page. The data file carries
the figures and the per-value detail.

**Nothing is promoted by any of it, and the stake is narrower than the chain's
length suggests.** A second-hand report of a book's table is not the book, so
all seven stay tier 3 and unadopted. And the hierarchy above admits only tier 1
as the authority for a stored value, so opening the book changes what this
document may claim **only if it turns out to have measured these volumes and
flows rather than collected them**. It could not be reached from a session
container — the egress proxy refuses the Internet Archive, HathiTrust, Open
Library and Google Books alike, and PubMed does not index monographs — so it
still needs the project owner's institutional or library access, as the Workbook
did; `PL-XJ5P` carries that gap. What changed is the size of the ask: page 57,
with page 83 next.

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

**Where 1.0 L actually came from is now answerable, and the answer is: from
here.** The value entered the repository on 2026-08-22 in `875ba08`, "Build
v0.1.0 sevo patient simulation", the tenth commit — written into the data file
alongside the rest of the reference patient and carrying the citation "Gas Man
Workbook and Laboratory Manual. Default Options: Patient Defaults", whose note
read "The default 70 kg patient uses alveolar volume 2.5 L, venous volume 1.0 L,
alveolar ventilation 4 L/min, cardiac output 5 L/min, tissue volumes
6/33/14.5 L, and flow percentages 76/18/6". `PL-XTMB` later read that section at
the source: it is Appendix E, page 183, and it describes the interface controls
without carrying a number. The table that does carry numbers, Appendix B page
168, has a `Blood` row of 5.00 L and nothing at 1.0.

**So the citation belonged to its neighbours.** Every other value in that
sentence is in the Appendix B table or is an interface default; 1.0 L is the one
that is in neither, and it inherited the reference the others had earned. All
four sources ever cited for it have since been read — the Workbook at the source
(`PL-XTMB`), Meybohm et al. at full text, Lowe and Ernst at one remove
(`PL-7HDS`), and Davis and Mapleson at the source — and **none of them contains
it**. It is this project's own modelling choice, and the only round number in
the file with no counterpart anywhere.

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
scaled from a weight, so changing the weight alone would not rescale them.

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
coefficients differ. All three agents' blood:gas and tissue:gas values are
drawn from the same source table (De Wolf et al. 2012, Table 1 — the paper
already cited for sevoflurane), so the three data files are directly
comparable rather than assembled from unrelated sources.

That shared table is the Gas Man parameter set, and it is tier 3 under
"Source hierarchy" above: the comparability is real, and it is the
comparability of three agents carrying one reference implementation's
choices, not of three agents each traced to its own measurement. It buys a
cross-agent comparison in which every agent shares the same error, which is
the property a MAC-normalized axis needs; it does not make any of the twelve
coefficients a measured value. That shared-error argument covers the
*coefficients*, which is what this paragraph is about. It does **not** extend
to the three `mac_percent` divisors, whose deviations from the primary
literature run in opposite directions between sevoflurane and desflurane;
"Delivery-limit and MAC parameters" measures that separately. Each agent file records the primary
measurement alongside its stored number and states the difference.

Desflurane is markedly less soluble than sevoflurane, which is itself less
soluble than isoflurane (blood:gas 0.42 < 0.65 < 1.3). This does not change
any equation: lower solubility only means faster equilibration through the
same closed-form solutions, which `tests/reference/test_multi_agent.py`
checks directly by comparing simulated alveolar/circuit ratios rather than
only comparing the static coefficient values.
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->

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
under "Source hierarchy", and tier 2 may never be the authority for a stored
value. Second, every other parameter in this model is the Gas Man set, so a
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
- derived concentration fractions remain finite and nonnegative;
- no compartment creates agent spontaneously;
- internal transfers remove and add equal amounts;
- identical runs produce identical state and history, element for element,
  however the steps were grouped in real time;
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

### Published wash-in validation test

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
(`tests/reference/test_published_wash_in.py`). The distinction matters to a
reader of the two sections: "Independent-solution test" above and this one
answer different questions, and conflating them over-reads both.

**This section covers two comparisons, in opposite directions**, although its
heading names only the first — the name is kept because five other passages
in this document and in `src/` cite it, and a citation that no longer
resolves is a worse defect than a heading that under-describes. The two are
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
agent at five minutes than every cohort did (measured 2026-09-06):

| Agent | Cohort | Model | Published | Distance |
| --- | --- | --- | --- | --- |
| Sevoflurane | n=7 | 0.2303 | 0.157 ± 0.020 | +3.67 SD |
| Isoflurane | n=7 | 0.3195 | 0.223 ± 0.024 | +4.02 SD |
| Desflurane | n=8 | 0.1603 | 0.14 ± 0.02 | +1.02 SD |
| Isoflurane | n=8 | 0.3195 | 0.22 ± 0.02 | +4.98 SD |

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
not in PubMed Central and are not held in `docs/references/`. Holding $`F_I`$
at zero through the elimination — a diagnostic, not a configuration — moves
the three agents from +3.67, +4.02 and +1.02 SD to −0.25, +0.54 and −2.40 SD,
so the two conditions bracket the published values and desflurane's residual
disagreement changes sign.

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
   spread.* The paragraphs above measure it. Any statement that this model
   eliminates more slowly than these volunteers did has to carry it, because
   most of that difference is a rebreathing circuit rather than a patient.
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

### Deterministic replay test

Two runs with identical:

- initial state;
- parameters;
- setting changes;
- event ordering; and
- simulation steps

must produce identical snapshots and histories.

Identical means element for element — every recorded sample of one run equal
to the sample at the same index of the other, not merely equal endpoints and
not agreement within a tolerance. Comparing endpoints would pass a pair of
runs that diverged and returned, and the comparison a branched run will make
against its parent is sample-by-sample.

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
none of them reaches model state: no step is resized, no recorded sample is
added, discarded or altered, and identical inputs still produce identical
results. "Interface boundary" is where they are bounded. The distinction is
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
recorded against the simulated time it took effect, alongside the
concentration history, and cleared with it. What that record is for, what
it does and does not assert, and why it is shaped the way it is are under
"The control-input timeline" below, with the display rules the rest of the
interface section carries.

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
"Published wash-in validation test" compares against measured human data, and
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
review, so under "Source hierarchy" it may not be the authority for a stored
value — and it is not one: 24 hours is not computed from 2% to 5%, and no
parameter in this model descends from that paper. What it supplies is the
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
The circuit volume is a *machine* parameter and is not in a data file at all:
it is the default `circuit_volume_l: float = 6.0` on `BreathingCircuit`, and
it has no recorded source. That is a real gap in this document's provenance
coverage rather than a property of the parameter — the value sets the
fresh-gas wash-in time constant that every displayed concentration passes
through — and it is queue item `PL-4YY1`, which moves the constant into a
data file and gives it a row above without changing it.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5 -->

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
by mistake, it says nothing about the physiological question above, and far
enough down it stops firing at all. Circuit volume has no such point: it was
advanced up to $`10^{300}`$ L with accounting passing throughout.

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
- clear concentration and mass-accounting history;
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
the interface rather than only on the controller. The recorded history, the
control-input timeline and the simulated time a run reached are the whole of
what a learner has to look back at, nothing in this application stores them,
and there is no undo. So:

- the interface must not discard a run holding recorded state — any elapsed
  simulated time, or any recorded control change — without first stating that
  it will be discarded and obtaining the user's confirmation;
- the statement must name what is lost in the terms the display already uses
  for it, so that it can be checked against the readouts it describes;
- declining must leave the run, its history, its timeline and the control
  that offered the change exactly as they were; and
- a selection that resolves to the agent already running must change nothing,
  since it proposes no new case.

A run that holds no recorded state is exempt: there is nothing to discard, and
a confirmation that fires where nothing is at stake is answered without being
read by the time one is. Reset is therefore also the way to make a change of
agent free.

## Interface boundary

The Flet interface may:

- display values;
- convert fractions to percent;
- collect user settings;
- issue Start, Pause, and Reset commands;
- choose how many simulation steps each tick of its own loop takes, so that a
  run can be played faster than real time, subject to the constraint below;
- halt a run and record why when the core raises, and report a value the
  core refused;
- render the run's recorded history;
- choose how wide a window of the run the chart draws, and how that window is
  ruled, subject to the constraint below;
- select which recorded samples a plotted trace draws, subject to the
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

**What a recorded sample is.** The recorded history is one sample per
simulation step, and each sample is a simulated time together with one entry
*per substance* — each entry carrying that substance's six compartment
values, as fractions of one atmosphere, under the stable identifiers
`app/controller.py`'s `RecordedQuantity` names. A run records one substance
today, the agent it is a run of; changing agent starts a new run rather than
adding to this one, so the mapping is one entry wide.

It is keyed by substance rather than by six named fields because a
compartment fraction asserts nothing without the substance it is a fraction
of. A record naming the six flatly can hold exactly one substance, so a
second would have to arrive either as six more names or as values pooled
with the first's, and pooled values are the correct-number-wrong-label
failure this document forbids elsewhere. The chart addresses the store the
same way — one trace is bound to one substance-and-quantity pair — so a
trace can draw only what it names, and a frame asking for a substance the
run does not record fails rather than drawing whichever substance it does
hold. The wash-in quotient below is formed from one substance's own two
fractions and is recorded per substance for the same reason.

A plotted trace need not draw every recorded sample — the recorded history
grows by one sample per simulation step, well beyond what a chart can
resolve — but every point it does draw must be a recorded sample. The
interface must not interpolate, smooth, average, or otherwise synthesize a
plotted value, and the most recent recorded sample must always be drawn, so
that the end of a trace and the numeric readouts cannot disagree. Selection
must also preserve the extremes of the samples it omits, so that decimation
cannot hide an excursion the model produced.

The selection that meets those constraints is **M4** (Jugel U, Jerzak Z,
Hackenbroich G, Markl V. M4: A Visualization-Oriented Time Series Data
Aggregation. *Proceedings of the VLDB Endowment*. 2014;7(10):797-808 — held
in `docs/references/` and read there in full, 2026-09-04). The visible
window is divided into groups of consecutive samples, and each group
contributes four recorded samples: its lowest value, its highest, its first
and its last. Naming the algorithm is part of the constraint rather than
commentary on it — a chart that says which published reduction it draws can
be checked against that reduction, and one that says "something that keeps
the extremes" cannot.

**The chart is not exact, and this document says so rather than implying
otherwise.** M4's Theorem 1 — that a line visualization of the reduced
series equals one of the whole series — holds under the condition its § 6
states: the number of groups drawn must be an integer multiple of the
chart's pixel-column count. This interface groups on a grid anchored to
absolute sample index instead, because a grid that followed the viewport
would move on every scroll and resize and so rewrite the whole chart on
every frame. It therefore buys stability at the cost of that condition and
lands in the paper's general case rather than its exact one. What the
departure costs here is bounded: of the paper's three error classes, the two
driven by gaps in the sampling cannot arise, because this simulation records
one sample every step and has no gaps at all, leaving only a spurious pixel
where the line between two consecutive extrema crosses a column boundary.
`app/chart_downsampling.py` carries the same statement for a reader of the
code.

**Which compartment traces are drawn is the reader's to choose, and the
choice may not change anything else.** Two compartments cannot be compared
against four other lines crossing them, so the interface may draw a subset of
the six. Three things bound it. The selection is presentation only: it reaches
no model state, changes no recorded sample, and leaves identical inputs
producing identical results. Every compartment's concentration stays in the
numeric readouts whatever is drawn, so a chart showing two curves is a chosen
view of six modelled compartments rather than a model with two. And the
display must state, for every compartment, whether its trace is currently
drawn — a legend entry for a line that is not on the plot is a claim about the
run the run does not support, which is the defect an unlabelled reference
would be arriving from the other direction.

A **reference** is not a trace and is deliberately exempt from the rule
above: it draws no recorded sample, because it is a published constant
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
recorded sample, and nothing about it may be interpolated, smoothed or
averaged. What it needs in addition is a **stated domain**, because a
quotient of two modelled states can be undefined (a zero denominator) or
outside what the plot claims to show, and neither case has a number the
interface may substitute. So: the domain is documented here and enforced in
one place in code; a sample outside it contributes no point, rather than a
clamped, extrapolated or defaulted one; the trace breaks where the domain
does, rather than joining across the samples it skipped, which would draw
values the run never produced; the display states which two quantities the
ratio is of, in the terms this document uses for them; and where the trace
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
state, alters no recorded sample, and leaves identical inputs producing
identical results, so it sits outside "Runtime controls" with the other
interface settings. The width in force must be a fixed property of the
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
solution: identical inputs still produce identical recorded histories, and
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

The Flet interface must not:

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

### MAC multiples as a display unit

Every compartment is displayed twice: as a percent of one atmosphere, and as
a multiple of the running agent's 1 MAC. Both are shown at once, on every
compartment, on the delivered-agent control, and on the chart, which carries a
percent axis on the left and a MAC axis on the right.

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

The interface states the distinction beside the chart, in those terms, and
the ratio is never presented as a depth. Three further limitations hold for
every compartment including the alveolar one, and none of them is modeled
here: MAC falls about 6% per decade of age (Mapleson 1996; cited in each
agent's `sources`) and this model's reference adult has no age parameter;
MAC multiples of co-administered agents are additive and this model runs one
agent at a time; and MAC is modified by opioids, temperature, and patient
factors none of which are represented.

**The unit is written `×MAC`, not `MAC`.** "0.80 MAC" is read as a depth;
"0.80 ×MAC" is read as what the number is. The multiplication sign is doing
safety work rather than typographic work, and it is why the readouts carry it.

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
arithmetic over durations that reads no simulation state and imports no Flet,
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
changes which part of the recorded run is drawn and nothing else: no step is
resized, no sample is added, discarded or altered, and no calculation is
re-run. "The reproducibility guarantee" is therefore untouched by it, and the
same case watched at fifteen minutes and at twelve hours is the same run,
sample for sample. Every point drawn at any width is still a recorded sample,
selected under the constraint "Interface boundary" places on a plotted trace,
so a wider window is a coarser *selection* of real samples and never a
resampling, an interpolation or a stored image zoomed into.

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
block. Ticks stand at multiples of the interval measured from the run's own
start rather than from the window's left edge, so a gridline holds the same
simulated time as the window slides underneath it.

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

**What it is.** A record of the settings a run was given, kept beside the
concentration history and cleared with it. Each entry is one change the
model actually ran under: the simulated time it took effect, the index of
the history sample it took effect at, which control, the values before and
after, and the unit both are in.

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
control (§ "What is not bounded this way"); retiring it cost no recorded
history, because a timeline is held in memory and cleared with its run
rather than persisted.

**Bounds are displayed, not silent.** The chart carries a fixed number of
marks and the list a fixed number of lines, so a run may record more
adjustments than either can show. What is not shown is counted on the
display. A chart that quietly stops annotating, or a list that quietly
ends, is a statement that nothing else happened.

### F_A/F_I as a displayed ratio

**What it is.** A second plot under the compartment chart, on the same time
window, drawing $`F_A/F_I`$ — the modelled alveolar fraction divided by the
modelled inspired fraction — on a dimensionless axis fixed from 0 to 1. It is
a *displayed* quantity: `core/` computes it nowhere, no governing equation
reads it, and it is not recorded in the run's history. `app/wash_in.py` is
where this section terminates, the way `app/formatting.py` terminates
"Displayed precision": it holds the arithmetic, the domain, and nothing else,
and `tests/unit/test_wash_in.py` pins both.

**Why the interface owes it.** This is the curve the uptake literature is
taught from and the one every wash-in figure a reader has seen is drawn as.
It is also the quantity this model has been compared against human
measurement on — "Published wash-in validation test" is $`F_A/F_I`$ at
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

**The plotted domain, and why it has two boundaries.** A sample contributes a
point only where both hold:

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
extended by its *crossing* sample at each end — the neighbouring sample that
has a ratio but sits outside the domain — because without it the curve stops
at the last sample at or below equilibrium, which is up to one simulation step
below the line it stopped at. A trace halting in clear space short of a
boundary is indistinguishable from one the frame cut off, and this one is
still climbing steeply when it stops; with the crossing sample drawn it meets
the equilibrium reference and terminates on it, carrying a point marker that
says the series ended rather than ran out of view.

That extension is bounded by a stated ceiling rather than by a property of the
model. A run stepped at 0.1 s crosses equilibrium by a hair — measured across
every shipped agent and every supported alveolar ventilation and cardiac
output at the maximum fresh gas flow, the first sample above equilibrium
reaches 1.00235 — but the ratio is not continuous in general:
`BreathingCircuit.set_circuit_volume` conserves the agent in the circuit while
changing the volume it is divided by, so a circuit volume doubled between two
steps halves $`F_I`$ and doubles the ratio. No interface control does that
today, and a rule holding only because a slider is absent is not one to build
on. A crossing sample above the ceiling is therefore not drawn at all, and the
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
— so a third decimal would be finer than the published spread. See "Published
wash-in validation test".

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
  another is the whole lesson of this chart. This bar cannot be met on
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
`make check`, reads the color constants out of `app/theme.py` and
`app/simulation_view.py`, and holds each declared requirement to its declared
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
integration step, the mixed-venous and tissue transfers, and every
`SimulationHistorySample` the chart is drawn from. Nothing in `core/` rounds,
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
readouts are placed in one row to be read *ordinally* — the circuit leads the
alveoli lead the tissues — and an ordinal reading is corrupted only if the
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
readouts sit in one row and are read comparatively — the reason for showing
them together is that a reader can see the circuit lead the alveoli lead the
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
resolution of the flow controls that set them. A slider's drag label must
carry the same number of decimals as the readout beside it: the two show one
quantity, and a label that rounds where the readout does not leaves a reader
unable to tell which value is the setting in force. The agent-accounting panel
displays amounts to 10⁻⁶ L and its residual in scientific notation, and that
is deliberately finer than any clinical reading: the panel is a numerical
diagnostic whose job is to make a residual of order 10⁻¹⁵ L visible, not a
value a reader interprets clinically. Precision in this interface is set by
what each number is for, and the rule above governs the clinical readouts.

The chart plots the same percentages on a shared linear axis running from 0 to
3 ×MAC of the running agent, and carries a second axis on the right reading
the identical coordinate in MAC multiples. Its resolution is set by pixels
rather than by decimals, and it is coarser than the numeric readouts
throughout; the readouts, not the traces, are where a value is read. The MAC
axis is labelled on round MAC values rather than on round percentages — half-MAC
steps, which the fixed 3 ×MAC range gives for every agent, so the gridline a
reader learns under one agent means the same thing under the next. "The chart's
vertical range is denominated in MAC, and fixed" above carries why the range
is what it is. Its horizontal extent is the selected time base rather than a
fixed span, so seconds per pixel is the reader's choice; "The chart's time
base" carries how a width is chosen and how it is ruled.

`app/formatting.py` is where this section terminates: it holds the
resolution as a single constant, derives the formatter, the below-resolution
marker, the MAC decimal count and the MAC axis placement from it, and imports
no Flet, so the functions this section reasons about can be read, cited and
tested without loading the interface. `tests/unit/test_formatting.py` pins the constant and every
string the formatter produces; `tests/unit/test_simulation_view.py` holds
the end-to-end path — real controller, real step, the string on the panel.
`app/simulation_view.py` imports the constant for the delivered-agent
slider's drag label, which is why that label and the readout beside it
cannot drift apart.

`tests/reference/test_coupled_dynamics.py` restates the same constant and
checks it against `app/formatting.py`, because the ordering claim above is a
property of the rounded values and adding a decimal would change what that
claim proves without changing anything it reads. A change to the resolution
is a change to this section.

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
- carrier gases do not affect sevoflurane kinetics;
- temperature is constant;
- pressure is constant;
- there is no metabolism;
- there is no chemical degradation;
- there is no anesthetic reaction with circuit materials;
- there is no vaporizer or machine delivery delay beyond the modeled circuit;
- settings remain constant within each numerical step; and
- the selected reference patient does not change physiologically during a run.

## Known limitations

This model does not model:

- a separate arterial blood-mixing compartment (arterial blood is flow-limited and equals alveolar gas at every instant, matching the Gas Man reference simulator's mammillary structure — see "Model boundary");
- halothane, enflurane, ether, or xenon (isoflurane and desflurane were added in v0.2.0; see "Parameter provenance");
- nitrous oxide;
- simultaneous gases;
- concentration or second-gas effects;
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

## Release gate

Version v0.1.0 is complete only when:

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
