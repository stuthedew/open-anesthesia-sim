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

The release tolerance, as implemented in `core/agent_simulation_validation.py`:

```text
MASS_BALANCE_ABSOLUTE_TOLERANCE = 1e-12 L
MASS_BALANCE_RELATIVE_TOLERANCE = 1e-9
```

A step passes if either tolerance is satisfied. The relative error uses `max(initial + delivered, 1e-15 L)` as its denominator to avoid division by zero when no agent has yet been delivered.

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
ceiling deliberately; "Supported simulation step" below derives the bound and
says why those two coincide.

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
coupled trajectory and does not; carried as a state it is integrated exactly
by the same propagator, which is what requirement 4 of "Numerical method"
above asks for and what puts the mass-balance residual at rounding.

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

**The value is carried forward rather than re-derived, and that is deliberate
rather than an omission.** It was set by inverting an error bound that no
longer exists, so it is now conservative by an unknown margin — which is the
safe direction to be wrong in, and not a reason to move it without measuring.
Re-deriving it, together with the displayed resolution it used to invert, is
queue item `PL-X9KD`. Until that lands the supported step and the shipped step
are the same number and the interface runs at it.

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

`src/anesthesia_sim/data/patients/reference_adult.json` has no primary
citation to place beside its values, so it records that instead, in those
words: no primary source has been adopted for any of its eleven parameters.
Mapleson's papers are named there as the primary lineage, and explicitly as
located-but-unread rather than as a citation — writing one for a paper nobody
has opened would be the same failure in a different tier.

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
| Venous blood-pool volume | 1.0 | L | `data/patients/reference_adult.json` · `venous_blood_volume_l` |
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
5\times10^{-12}
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

**Derived from the exact step's own error, not inherited.** Measured
2026-09-06 across all three agents, the horizons above and every trajectory
below, taking the maximum over the whole trajectory: 5.2e-14 at the endpoint
of a 3600 s default run, 1.9e-13 at the envelope corner, 3.2e-13 on the
*unperfused load, then dial off* trajectory, and 7.7e-13 — the worst — on a
*ventilator start*. The bound allows 6.5 times that. Against the operator
split, whose worst over the same domain was 2.29e-4 at this step, the exact
step is eight orders of magnitude closer to the independent solution.

**The residual is rounding, not truncation, and that is checked rather than
asserted.** Refining the oracle's own step eightfold — 0.05 s to 0.00625 s —
leaves it unchanged to three figures for every agent. RK4 is fourth order, so
a residual dominated by the oracle's truncation would have fallen by about
four thousand; one that does not move is the floating-point floor.

The margin is wider than the 1.22 the splitting bound carried, deliberately: a
systematic coefficient reproduces between machines and accumulated rounding
does not, since a different `exp` implementation or a contracted multiply-add
moves the last bits of both solutions. Six and a half times is still eight
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

Isoflurane is compared against both cohorts rather than one. The model must
land inside the published standard deviation for every row, and must also
reproduce the ordering by solubility the two studies were run to test —
$`F_A/F_I`$ higher for desflurane than sevoflurane than isoflurane — because
three tolerances that happen to overlap are not a model.

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
carrying the result: every agent stays inside its published spread at every
fresh gas flow from 1 to 10 L/min. One delivered fraction serves four
different published $`F_I`$ values because the governing equations are linear
in it, which the test asserts across the published range rather than assumes.

**Two caveats bound how strongly a pass may be stated.** Both belong beside
any statement of this result, wherever it is restated - the root README used to
carry one and no longer exists (`PL-WB5K`), so the obligation transfers to
whatever `PL-N092` writes in its place.

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

**How sharp a gate this is, measured rather than assumed.** Perturbing each
agent's blood:gas partition coefficient until the comparison fails, with
every other parameter shipped:

| Agent | $`\lambda_{b:g}`$ | Reference point alone | With the flow sweep |
| --- | --- | --- | --- |
| Sevoflurane | 0.65 | −14% / +21% | −14% / +6% |
| Isoflurane | 1.3 | −12% / +24% | −12% / +13% |
| Desflurane | 0.42 | −4% / +30% | −4% / +11% |
<!-- provenance: data/agents/sevoflurane.json blood_gas_partition_coefficient = 0.65 -->
<!-- provenance: data/agents/isoflurane.json blood_gas_partition_coefficient = 1.3 -->
<!-- provenance: data/agents/desflurane.json blood_gas_partition_coefficient = 0.42 -->

This is a coarse gate. At the reference point alone a solubility error of a
fifth survives for two of the three agents — wider than the spread between
published human measurements of the same coefficient — so a pass excludes a
structurally wrong model rather than a mis-parameterized one. The flow sweep
roughly halves the tolerated upward error and is therefore part of the gate
rather than decoration. Desflurane is the tightest row and is tight in one
direction only, because it already sits at +0.79 SD with little room above
the mean; a change that moves it out of the band is a disagreement to
explain, not a tolerance to widen.

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

#### What is not bounded this way

The two gas volumes — the circuit's and the alveolar compartment's — are
model parameters taken from the data files rather than controls, and are
validated as positive and finite rather than against a measured domain. The
interface offers no control for either, and every reference measurement in
this document holds both at their data-file values. `SimulationController`
does expose `set_circuit_volume`, which no interface control reaches; a
caller using it is outside the verified domain in a way this section does not
yet bound (PL-GYH2).

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
ranges; "Supported simulation step" above derives it. The two bounds are
coupled in one direction: the coefficient the step bound inverts is measured
over the trajectories *these* ranges produce, so widening a range means
re-deriving both.

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
— so the interface may play a run faster by taking more steps per tick. Two
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

The second is human factors, and it is why the rate is a required displayed
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
vision deficiency. Under simulated protanopia, deuteranopia, and tritanopia the
two fills fall to a luminance contrast of 1.1-1.4 against each other, and they
already differ by only 1.09 for normal color vision — they are separated by hue
alone. Choosing more separable colors would break the correspondence to real
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
`alveolar_ventilation`, `cardiac_output`, `circuit_volume` — rather than
from whatever the accessor that applies it is called. An identifier taken
from the code would retire the vocabulary of every already-recorded run the
next time the code was renamed.

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
graphical — the alveolar chart trace and the sliders' active track — while
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
  pair more than $`21^{1/5}\approx1.84`$. That is below SC 1.4.11's 3:1, so a
  redundant non-color channel (line style or marker) is a **requirement** for
  this chart rather than an embellishment, and no palette choice can remove it.

**Deferred, and named so the deferral is visible** rather than silently
unlisted: SC 2.4.11 (Focus Not Obscured), 2.5.8 (Target Size), 1.4.10 (Reflow)
and 1.4.12 (Text Spacing). Each needs a settled interface before it can be
answered, and what the rendering backend can deliver for keyboard and
screen-reader support is an open question rather than a commitment.

**The ratios are computed, not asserted.** `tools/contrast_check.py` runs in
`make check`, reads the color constants out of `app/theme.py` and
`app/simulation_view.py`, and holds each declared pair to its declared minimum
using WCAG 2.2's own relative-luminance and contrast-ratio definitions. Its
requirement table names the pair, the criterion and the reason the pair is held
to that number; the judgment of *which* pairs matter stays in that table, and
the tool only evaluates it. Pairs that do not meet their minimum today are
listed there against the item that closes each one, and a listed shortfall that
starts passing is reported as an error, so a fix cannot leave its excuse behind.

### Displayed precision

> **Re-derivation owed (`PL-X9KD`).** Everything below that justifies the
> displayed resolution *numerically* was derived from the operator split's
> first-order error, and `PL-GS5X` replaced that method with an exact
> propagator whose error is many orders smaller. The chosen resolution has not
> moved and the legibility half of the argument is untouched; what no longer
> holds is the claim that two decimals is the finest the numerics support, and
> every figure quoted in counts of the last displayed digit. Read the figures
> below as describing the method that shipped through v0.4.2. "Selected method
> (as implemented)" states what ships.

Every modeled concentration and relative partial pressure is displayed at a
fixed resolution of **0.01 percentage points** — two decimals of a percent —
uniformly across all six compartments. The delivered-agent setting uses the
same resolution — in the readout beside its slider and in the slider's own
drag label alike — so the value a reader dials and the values it produces
are read at one scale. A positive value that would round to `0.00%` is
displayed as `<0.01%` rather than as zero.

This is a recorded decision (PL-040), not a formatting convention, because
displayed precision is a claim about what the model can support. Earlier
revisions displayed three decimals; the third and part of the second were
below the solver's own error, which is to say the interface was rendering
numerical noise as though it were model output.

**What the solver's error was.** The step that shipped through v0.4.2 was a
first-order operator split (see "Selected method (as implemented)"), and its
disagreement with the independent solution is what sets the floor. Measured
against a from-scratch RK4 integration of the governing equations — the same
oracle construction as `tests/reference/test_coupled_dynamics.py`, extended
across the settings the interface exposes and across the setting *changes* it
allows — the worst disagreement in any of the six displayed states is:

| Run | Worst error |
| --- | --- |
| Default flows, dial at 1 MAC | 1.7×10⁻³ percentage points |
| Default flows, dial at 1 MAC, ventilator started mid-run | 2.2×10⁻³ percentage points |
| Default flows, dial at the agent's maximum | 5.0×10⁻³ percentage points |
| Maximum flows, dial at the agent's maximum | 1.2×10⁻² percentage points |
| Maximum flows and dial, ventilator started mid-run | 1.5×10⁻² percentage points |
| The worst reachable trajectory | 2.3×10⁻² percentage points |

Default flows are 4 L/min fresh gas with the reference adult's default
alveolar ventilation and cardiac output; maximum flows are the supported
maxima for fresh gas, alveolar ventilation, and cardiac output — which are
also the sliders' — and the maximum dial is each agent's
`max_delivered_concentration_percent`.
The held rows run for 3600 s, the setting-change rows for 600 s; extending
either changes nothing, because the worst case in every row is an alveolar or
mixed-venous value inside a transient rather than at an endpoint. The last
row is the *unperfused load, then dial off* trajectory of
"Independent-solution test", which is the worst the four sliders can reach.

The last row is the same measurement the release gate in
"Independent-solution test" bounds, expressed in percentage points instead of
as a coefficient: $`2.29\times10^{-3}\ \mathrm{s^{-1}}`$ at the shipped 0.1 s
step. **The two are coupled and must be revised together** — the resolution
chosen here rests on that measured error, and the gate is set only 1.22 times
above it precisely so that a change large enough to invalidate this section
fails the gate rather than passing it silently.

**Why 0.01 percentage points follows.** At that resolution the last
displayed digit is uncertain by roughly a fifth of a count in ordinary use —
whether or not a setting is changed during the run — half a count at a
maximum dial setting, one count at the extreme corner of the settings
envelope, and about two counts on the worst trajectory the sliders can reach,
which requires holding cardiac output at zero. That is the conventional and
honest relationship between an instrument's last digit and its error: the
final digit is the uncertain one, and it is most uncertain where the settings
are least physiological. At the previous 0.001 percentage points the last
digit was uncertain by two to twenty-three counts and the digit before it by
up to two, so two of the three displayed decimals carried no information
about the model.

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
the readout. So the two decimals below are a statement about what is worth
*showing*, never about what the model computes or stores, and the quantity
that actually limits the model is the splitting error above, which is a fifth
of the last displayed digit in ordinary use.
`test_the_model_keeps_precision_the_display_throws_away` holds this: two runs
whose delivered concentration differs four orders of magnitude below the
display resolution must reach states that differ, and must still read
identically on the display.

**Re-affirmed 2026-08-30 against the widened measurement** (PL-74TX). The
figures above are larger than the ones PL-040 chose two decimals on, because
the solver error has since been re-measured over trajectories rather than
over held operating points: about two counts at the extreme where the earlier
measurement gave one. The decision stands, and the alternative is what
settles it. A one-decimal readout would be uncertain by a fifth of a count at
the extreme — but at 0.1 percentage points the fat fraction reads `0.0%` for
an entire hour and muscle for its first three to fifteen minutes, which is
the failure this section rejects two paragraphs below. Two decimals remains
the coarsest resolution that keeps every compartment legible and the finest
the numerics support; the widened measurement moved where inside that window
the answer sits, not which side of it.

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
The rest of this section still derives the displayed resolution from the
split's error, and re-deriving it is queue item `PL-X9KD` — the figures below
should be read as describing the method that shipped through v0.4.2, not the
one that ships now.

The comparison the interface actually invites survives this, and that is a
measurement rather than an assurance. The six readouts are placed in one row
to be read *ordinally* — the circuit leads the alveoli lead the tissues — and
an ordinal reading is corrupted only if the error can invert which of two
compartments is displayed as higher. Across every trajectory in
"Independent-solution test", all three agents, comparing every pair of the
six readouts at every step: the shipped and reference solutions never
disagree about the displayed ordering at ordinary settings, at the reference
point, at the envelope corner, or across a ventilator start. They disagree
only on the worst reachable trajectory, for 0.2 s of a 900 s run with
sevoflurane and 1.7 s with desflurane, and only where the two compartments
are within 1.73 counts of the last displayed digit of each other — that is,
only while they are crossing, which is where the ordering is genuinely
ambiguous and not where a real gradient would be misread.

That is why the interface marks nothing here. A reader who compares the
readouts the way the row is designed to be compared cannot be misled by the
splitting error; a reader who subtracts two of them is doing arithmetic the
interface does not perform, and the paragraph above is the disclosure for it.
`test_displayed_ordering_reverses_only_at_a_crossing` holds this claim: it
fails if the error ever inverts a displayed ordering between two compartments
that are further apart than that.

**Why the resolution is uniform rather than per-compartment.** The six
readouts sit in one row and are read comparatively — the reason for showing
them together is that a reader can see the circuit lead the alveoli lead the
tissues. Different decimal counts across those tiles would put different
magnitudes at the same glyph position, so a value scanned rather than read
would be misjudged by a factor of ten. The solver's error is also bounded in
*absolute* percentage points, and across the runs measured above it stays
within a factor of four across the four fast compartments — 0.006 to 0.023
percentage points in circuit, alveolar, mixed venous and vessel rich — while
muscle is an order of magnitude smaller and fat two to three. A single
absolute resolution is therefore the direct expression of it, set by the
compartments where the error is largest and conservative in the two where it
is not.

**Why not a significant-figures rule.** A significant-figures rule gives the
smallest values the most decimal places, and the small values are exactly
where this model supports the least. Relative to their own magnitude the
sparsely filled compartments are the least accurate states in the system:
in the first ten seconds of a run the mixed-venous, muscle, and fat
fractions carry 3–6% relative error, falling below 0.1% only after several
minutes. Three significant figures on the fat fraction at ten seconds would
imply a relative resolution of 0.1% on a number whose relative error is 3%,
over-claiming by a factor of thirty — and doing so most severely in the
readouts where a reader has least ability to notice.

**Why not the 0.1 percentage points clinical monitors report.** Agent
monitors display end-tidal and inspired concentrations to a tenth of a
percentage point, and the circuit and alveolar readouts alone would be well
matched to that. This simulator, though, displays compartments no monitor
shows. At 1 MAC the fat fraction reaches only 0.032% (sevoflurane) and
0.015% (isoflurane) after a full hour, so at monitor resolution both would
read `0.0%` for the entire run, and muscle would read `0.0%` for its first
three minutes (desflurane) to fifteen minutes (isoflurane). Rounding to
clinical convention would erase the slow-compartment wash-in that is the
reason for displaying those compartments at all. 0.01 percentage points is
the coarsest resolution that keeps every displayed compartment legible and
the finest the numerics support; the two constraints meet at one value
rather than being traded off.

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

**Why parameter uncertainty does not govern this.** A partition coefficient
is a measured population quantity carrying real uncertainty, and this
model's absolute agreement with any individual patient is limited by that
far more than by any solver error. It is nonetheless not what sets the
number of decimals, and the distinction is worth stating: parameter
uncertainty displaces a whole trajectory, while displayed resolution governs
how finely two moments *within one run* can be told apart. Within a run the
parameters are fixed and the simulation is deterministic, so what limits
resolution is the per-step solver error, which the table above measures.
Parameter uncertainty is disclosed where it belongs — in "Parameter
provenance", which records each value's source, definition, and reference
conditions — rather than encoded in a decimal count. The consequence for a
reader is explicit, and the "Known limitations" list is where it is made
good: no displayed value may be read as accurate to its last digit as a
prediction about a patient. It is accurate to its last digit as a statement
about this model with these parameters.

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

## Release gate

Version v0.1.0 is complete only when:

- all parameter values and sources are present;
- no scientific `TBD` markers remain;
- v0.0.2 circuit reference tests still pass;
- unit, integration, invariant, and independent reference tests pass;
- the published wash-in validation passes for every agent and cohort;
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
