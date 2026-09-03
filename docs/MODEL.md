# Volatile-agent patient uptake and distribution model

## Status

This document specifies the scientific model implemented starting in
v0.1.0 and still in force in v0.2.3, the current released baseline (see
`ROADMAP.md`). The title is deliberately version-generic: the governing
equations and compartment structure have not changed since v0.1.0, and are
shared by every agent this model supports.

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

### Concentrations

All model concentrations are stored internally as dimensionless partial-pressure-equivalent fractions from 0 through 1.

For example, $`F = 0.02`$ represents a 2% gas-phase concentration.

The interface alone converts between fraction and percent:

$$
\text{percent} = 100F
$$

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
| $`F_C`$ | Breathing-circuit sevoflurane fraction | dimensionless |
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
M_C = V_C F_C
$$

The equivalent sevoflurane amount in the alveolar gas compartment is:

$$
M_A = V_A F_A
$$

Therefore:

$$
F_C = \frac{M_C}{V_C}
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

Fresh gas enters at concentration $`F_D`$. An equal fresh-gas volume leaves through the exhaust at the current mixed-circuit concentration $`F_C`$.

Ventilation transfers gas between the breathing circuit and alveolar compartment.

The circuit amount balance is:

$$
\frac{dM_C}{dt} = \dot V_F(F_D-F_C) - \dot V_A(F_C-F_A)
$$

Because:

$$
M_C = V_CF_C
$$

the concentration equation is:

$$
\frac{dF_C}{dt} = \frac{\dot V_F}{V_C}(F_D-F_C) - \frac{\dot V_A}{V_C}(F_C-F_A)
$$

When alveolar ventilation is zero, this reduces to the v0.0.2 circuit equation:

$$
\frac{dF_C}{dt} = \frac{\dot V_F}{V_C}(F_D-F_C)
$$

For constant input and no patient connection, the exact v0.0.2 solution remains:

$$
F_C(t+\Delta t) = F_D+\left[F_C(t)-F_D\right]\exp\left(-\frac{\dot V_F\Delta t}{V_C}\right)
$$

The existing v0.0.2 analytic reference tests must continue to pass unchanged.

### Alveolar gas

Ventilation moves gas between the circuit and alveolar compartment.

Pulmonary blood flow enters the lungs at venous concentration $`F_v`$ and leaves in equilibrium with alveolar gas at $`F_A`$.

The alveolar amount balance is:

$$
\frac{dM_A}{dt} = \dot V_A(F_C-F_A) - Q\lambda_{b:g}(F_A-F_v)
$$

Because:

$$
M_A = V_AF_A
$$

the alveolar concentration equation is:

$$
\frac{dF_A}{dt} = \frac{\dot V_A(F_C-F_A) - Q\lambda_{b:g}(F_A-F_v)}{V_A}
$$

Alveolar gas has no single time constant. Ventilation acting alone — that is, at $`Q = 0`$ — would turn the alveolar volume over with:

$$
\tau_A^{\mathrm{vent}} =
\frac{V_A}{\dot V_A}
$$

using compatible time and flow units, which is 37.5 s for the reference adult, where $`V_A = 2.5`$ L and $`\dot V_A = 4`$ L/min.
<!-- provenance: data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->
<!-- derived: 37.5 s from data/patients/reference_adult.json alveolar_gas_volume_l = 2.5, default_alveolar_ventilation_l_min = 4 -->

That quantity is not the time constant of the coupled system, and it is recorded here — as a limitation of any single-mechanism description of alveolar kinetics — rather than exposed as a derived output, because two things separate it from what a run exhibits. First, blood uptake is a second exchange term acting on the same compartment: holding $`F_C`$ and $`F_v`$ fixed, $`F_A`$ relaxes with $`V_A/(\dot V_A + Q\lambda_{b:g})`$, which is 20.7 s for the reference adult on sevoflurane rather than 37.5 s. Second, $`F_C`$ and $`F_v`$ are not fixed — they are state variables of the same system — so the alveolar trajectory is a sum of exponentials over all six modeled compartments and no single constant describes it. A $`\tau_A^{\mathrm{vent}}`$ presented as "the alveolar time constant" would be a plausible number for a rate the simulation does not exhibit.
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
M_{\mathrm{exhausted}}(t) = \int_0^t \dot V_FF_C\,dt
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
3. apply equal and opposite internal transfers to their source and destination compartments;
4. integrate fresh-gas delivery and exhaust using the same numerical method;
5. advance the cumulative delivery and exhaust amounts;
6. advance explicit simulation time; and
7. calculate the post-step mass-balance residual.

A step is all-or-nothing. Steps 1 through 7 write compartment state as they
go, and a guard can reject a value produced by a later one after an earlier
one has already written; so a step that cannot be completed must leave every
dynamic value exactly as it was before the step, rather than as the operators
left it. "Step atomicity" below says why, and what a caller is left holding.

### Step atomicity

A partially applied step is not a solution of the model at any time. Its
numbers are an artifact of the order the sub-exchanges ran in — the fifth
having run against the second's output — rather than evidence of where the
model broke down, and they are indistinguishable, in the interface, from
numbers the model produced. Preferring an obvious failure to a
plausible-looking number therefore requires undoing the step, not annotating
it.

`RespiratorySystem.advance()` captures every dynamic value before the step
and restores it on any failure. What the model holds afterwards is the last
completed step: a real solution, at a real simulation time, which the
interface may display and a reader may reason about. The diagnosis that would
otherwise have to be inferred from those numbers is carried in the raised
`SimulationNumericalError` message instead, which names the invariant that
failed and the step size it failed at.

The dynamic values are the eight the trajectory is carried in — the circuit
concentration fraction, the alveolar amount, each of the three tissue
amounts, the venous amount, and the cumulative delivered and exhausted
amounts — plus the accounting period's initial amount. Settings and
parameters are deliberately not captured: a rollback that restored cardiac
output would undo a change the run had accepted. Each compartment captures
its own, so a dynamic field added later without a matching capture is a local
omission rather than a partial restore that looks complete.

Rolling back does not make the run resumable. The model reached a state it
could not step from, so the same step would fail again; the caller must stop
either way. What the rollback settles is what the caller may *show* while
stopped.

Two constants describe the step, and they are different kinds of statement:

```text
MAXIMUM_SIMULATION_STEP_S = 0.1   # core/uptake_system.py
SIMULATION_STEP_S         = 0.1   # app/simulation_view.py
```

`MAXIMUM_SIMULATION_STEP_S` is the model's supported domain, closed at its
endpoint: any positive step at or below it is supported, and both
`AgentUptakeSystem.advance()` and `SimulationState.advance()` refuse a larger
one. `SIMULATION_STEP_S` is the interface's own tick cadence, which sits at
that ceiling deliberately. "Supported simulation step" below derives the
bound and says why the two coincide.

### Selected method (as implemented)

Each simulation step is advanced by exact analytic solution of every pairwise
exchange, composed by first-order operator splitting rather than a generic
numerical integrator:

1. the circuit exchanges exactly with fresh gas (`BreathingCircuit.advance_fresh_gas`), holding ventilation fixed for the step;
2. the circuit and alveolar compartments then exchange exactly with each other (`AgentUptakeSystem._exchange_circuit_and_alveoli`), a closed-form solution of the two-compartment linear exchange that conserves $`M_C+M_A`$ exactly;
3. each tissue group exchanges exactly with arterial blood (`TissueGroup.advance`), holding the arterial fraction ($`=F_A`$) fixed for the step;
4. venous blood mixes exactly with the flow-weighted tissue outflow (`VenousBloodCompartment.advance`); and
5. the net patient uptake is applied back to alveolar gas (`AlveolarCompartment.apply_blood_uptake`).

Because each sub-exchange is solved exactly while temporarily holding the
other flows constant, this is a first-order (Lie/Godunov) operator split of
the fully coupled system: the splitting error is $`O(\Delta t)`$ relative to
the true simultaneous solution, even though each individual sub-step is
exact. Two release gates bound that error empirically, and they answer
different questions. The step-refinement test
(`test_step_refinement_converges`) asks whether the shipped composition is
self-consistent across supported step sizes; the independent-solution test
(`tests/reference/test_coupled_dynamics.py`) asks whether it converges to
the right answer at all, by comparing all six states against a from-scratch
integration of the equations above. Neither the mass-balance gate nor the
step-refinement gate can answer the second question: every internal transfer
is applied as an equal-and-opposite pair, so a wrong transfer *rate* leaves
the accounting residual at ~2e-15 L, and a wrong rate applied consistently
at every step size still refines consistently. A fourth-order Runge–Kutta
method would remove the splitting error but was not required to pass the
documented tolerances at `SIMULATION_STEP_S = 0.1`.

**The exact alternative, and why it is not taken.** Because every setting is
held constant across a step, the six-state system is linear and time-invariant
*within* that step, so a single matrix exponential of the system matrix solves
it exactly — with no splitting error at any step size. Measured against the
same from-scratch RK4 oracle at 5% delivered, over horizons of 60 s and
3600 s, the exponential's worst disagreement across all six states is
$`1.3\times10^{-16}`$ to $`4.8\times10^{-14}`$, against
$`5.2\times10^{-6}`$ to $`1.7\times10^{-5}`$ for the shipped split.
**The split is kept nonetheless** (project owner, 2026-08-30). Its error is
not unknown but bounded — by the two release gates above across the settings
envelope, and quantified in percentage points under "Displayed precision"
below, which sets the displayed resolution from it. What an exact step would
buy is therefore the removal of the applicability-domain bound under
"Supported simulation step" below, not the correction of a wrong value — and
no planned work wants that. `ROADMAP.md` scopes v0.4.0's playback multiplier
as steps per tick with the step fixed at 0.1 s, and fixes it there for
*determinism* — removing the step-size divergence and the machine-speed
dependence that make a run irreproducible on another computer — rather than
for accuracy, so an exact solver would not change that design either. Revisit
only if some future requirement genuinely wants a larger step. The
measurements are carried in queue item PL-6GS0; they were produced by the
v0.2.0 architecture review's verification harness, retired under PL-STNV.

#### Supported simulation step

The split has an applicability domain, and stepping outside it fails rather
than producing a number. `MAXIMUM_SIMULATION_STEP_S` is that domain's upper
bound, and a step above it is refused as a `SimulationConfigurationError`
before anything is calculated — nothing is miscalculated, the argument is
simply not one the model has an error bound for, and a caller can retry
inside the domain with the run it already has intact.

**The bound is not the breakdown.** "Applicability domain" hides several
different questions, and their answers are two orders of magnitude apart.
Measured on the worst trajectory the four sliders can reach (the *unperfused
load, then dial off* run of "Independent-solution test" below), across all
three agents:

| Criterion | Largest step it allows |
| --- | --- |
| Every claim "Displayed precision" makes about the last displayed digit stays true | **0.1 s** |
| The error stays within *one* count of the last displayed digit | 0.044 s |
| The first-order coefficient $`C`$ is still flat to about 1% | 0.6 s (isoflurane) to 2.5 s (the other two) |
| The compartment capacity guard fires | 12 s (isoflurane), 25 s (sevoflurane), 50 s (desflurane) |

Only the first is a bound worth carrying, and the other three are each
unusable for a different reason.

The **capacity guard** is what the implementation relied on before this
domain check existed, and it is not a domain check at all: it fires when the
sequential composition drives an amount negative — step 5 tries to remove
more agent from alveolar gas than step 2 left in it — which is a statement
about capacity, not accuracy. It is agent-dependent by a factor of four — the
figures above are grid-resolved, the coarsest step accepted below each being
10, 20 and 30 s — and it says nothing whatever about the range below it. A
600 s sevoflurane wash-in at default settings runs to completion at a 30 s
step and lands 0.205 percentage points from the same run at 0.1 s, twenty
times the resolution the interface displays, so the readout is wrong in its
*first* decimal while presenting itself as a settled value.

A **flat coefficient** is not reassurance either. $`C`$ is flat because the
error is first order, and the error is $`C\,\Delta t`$: at a 5 s step $`C`$ is
within 2% of its value at 0.1 s while the alveolar error is 1.12 percentage
points, 112 counts of the last displayed digit. $`C`$ also *falls* for
desflurane beyond about 20 s — $`1.91\times10^{-3}\ \mathrm{s^{-1}}`$ at a
30 s step against $`2.29\times10^{-3}`$ at 0.1 s — so a flat or falling
coefficient does not even indicate that the step is still inside the regime
the coefficient was measured in.

**One count** of the last displayed digit is the intuitive criterion and is
stricter than anything this model claims. "Displayed precision" states the
last digit as uncertain by about *two* counts on this trajectory — that is
what a last digit being the uncertain one means — so a one-count rule would
make the shipped 0.1 s step illegal against a claim the project does not
make.

**So the bound inverts "Displayed precision".** The split is first order, so
its error is $`C\,\Delta t`$ with
$`C \leq 2.29\times10^{-3}\ \mathrm{s^{-1}}`$ over the reachable input domain,
and every figure in that section — a fifth of a count of the last digit in
ordinary use, half a count at a maximum dial setting, one count at the
envelope corner, about two counts on the worst reachable trajectory — is that
error at exactly $`\Delta t = 0.1\ \mathrm{s}`$. Doubling the step doubles all
four, and
each of them then reads false. `MAXIMUM_SIMULATION_STEP_S` is therefore the
largest step at which what the interface shows is still what the model
supports, and **the supported step and the shipped step are the same
number**. There is no headroom for a deliberately coarser run, which is the
intended outcome and not an oversight: a coarser run's numbers would not
survive being displayed, and preferring an obvious failure to a
plausible-looking number is the required behavior here. Raising the bound is
a safety-critical change to every displayed value — re-measure the
coefficient, re-derive the displayed resolution with it, and revise both
sections together.

**The capacity guard remains, and reports something else.** Where a supported
step still drives an amount negative, `AgentUptakeSystem.advance()` reports
`SimulationNumericalError`: the step is rolled back in full, simulation time
does not advance, and the caller must stop the run — from a state that is the
last completed step rather than a partially applied one. No supported step
reaches that on the reference
adult with any shipped agent, so the guard is now cover for a parameter set
that could — a smaller alveolar gas volume, a far more soluble agent — rather
than for a caller stepping too coarsely. The two failures are deliberately
distinct: `SimulationConfigurationError` says the setting was refused and the
run is still trustworthy, `SimulationNumericalError` says a run in progress
is not.

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
De Wolf et al. state they used in their Gas Man simulations, with an
age-related iso-MAC paper cited alongside but not adopted. The three
exceptions are the vaporizer maxima, which cite manufacturer device
specifications — the primary source for a device capability, since no
measurement is at issue.

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
coefficients a measured value. Each agent file records the primary
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

`mac_percent` is 1 MAC for a 40-year-old adult. It is used for exactly one
thing: choosing the starting position of the delivered-concentration control
when a run begins, so that a new run starts from a recognizable clinical
anchor rather than an arbitrary number. `AgentUptakeSystem.for_agent()`
applies it, so the starting dial position is agent-specific in the core
rather than in the controller, and every agent file **must** declare a
`mac_percent` its own vaporizer can deliver — a cross-field check in
`core/parameters.py` enforces that, and runs after every field is
populated so it cannot be defeated by field declaration order. It is
deliberately not carried into the simulation. Specifically, the model does **not**:

- compute or display a MAC fraction, MAC-hours, or age-adjusted MAC;
- model an effect-site compartment or any depth-of-anesthesia endpoint; or
- imply that an alveolar concentration equal to `mac_percent` corresponds to
  any particular clinical state in a particular patient.

MAC is a population ED50 for immobility to a standardized stimulus, varying
with age and modified by other agents, opioids, temperature, and patient
factors none of which are modeled here. Presenting a single-agent alveolar
concentration as though it indexed anesthetic depth would be exactly the
kind of plausible-but-wrong clinical inference `CLAUDE.md` forbids. The
values are cited to age-related iso-MAC data in each agent's `sources`
array; the reasoning for treating them as a starting default only, rather
than as a modeled quantity, is recorded here.

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
- identical runs produce identical state and history;
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
F_C(t) = F_D+\left[F_C(0)-F_D\right]e^{-t/\tau_C}
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
fraction, $`F_C=F_A=F_a=F_v=F_i`$, then all internal transfer rates must be
zero.

### Directional ventilation test

With otherwise identical conditions, increasing alveolar ventilation must accelerate the approach of $`F_A`$ toward $`F_C`$.

### Directional solubility test

In controlled synthetic cases, increasing $`\lambda_{b:g}`$ must increase blood capacity and slow the rise of $`F_A/F_C`$.

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

Reference simulations using supported smaller steps must converge toward the same solution.

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
requires that the second gap be smaller than the first. Two step sizes can
only show that a pair of runs agree; three show that refining the step moves
the solution toward a limit rather than merely somewhere else nearby.

The release comparison tolerance is 5e-3 relative or 1e-8 absolute, either
satisfying, on the alveolar, vessel-rich and mixed-venous fractions after
60 s of the default sevoflurane wash-in. Comparing 0.1 s straight to 0.025 s
would exceed it in mixed venous alone — that compartment has barely begun to
fill at 60 s, so a difference of 1.4e-6 in fraction, a seventh of a count of
the last displayed digit, is 0.55% of it.

This gate is self-consistency across the supported steps, not correctness: a
wrong transfer rate applied consistently at every step size refines
consistently and passes here. "Independent-solution test" below is what asks
whether the composition converges to the right answer at all.

### Independent-solution test

The coupled six-state solution must be checked against an integration of the
governing equations that shares no solver with the implementation
(`tests/reference/test_coupled_dynamics.py`). The oracle may load the
parameter files and nothing else from the package under test; a comparison
against code derived from the implementation is a tautology, not a
verification, so the test enforces that restriction on its own imports.

The comparison covers every shipped agent, and its tolerance is a bound on
the first-order splitting coefficient rather than a value fitted to a
particular run:

$$
\max_i \left| F_i^{\mathrm{shipped}} - F_i^{\mathrm{reference}} \right|
\leq
C_{\max}\,\Delta t,
\qquad
C_{\max} = 2.8\times10^{-3}\ \mathrm{s^{-1}}
$$

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

**$`C_{\max} = 2.29\times10^{-3}\ \mathrm{s^{-1}}`$ is the worst measured
coefficient over the whole reachable domain**, and is the figure any later
work on step size should start from rather than re-deriving. The gate allows
a factor of 1.22 over it. That margin is deliberately narrower than the
factor of two an earlier revision used, and the reason is that the two things
a wider margin would buy are already covered elsewhere: a parameter revision
fails the pinned reference states first, which forces the re-derivation and
review it should have; and domain variation no longer needs absorbing now
that the bound follows a measurement across the settings envelope *and*
across setting changes.

Domain variation is exactly what made each previous bound wrong, twice over,
one dimension at a time. Set at $`5\times10^{-4}\ \mathrm{s^{-1}}`$ from the
reference point alone, it was exceeded by a factor of about 2.4 at settings
three sliders could reach. Reset at $`1.5\times10^{-3}\ \mathrm{s^{-1}}`$
from the envelope but still measured only on runs that hold one operating
point, it was exceeded by a ventilator start at that same corner — a
manoeuvre a user performs — and again by a factor of 1.5 at the worst
reachable trajectory. Neither gate ever failed, because nothing it drove
ever went where the error was.

Keeping the margin narrow also keeps the gate consistent with "Displayed
precision" below: at the shipped 0.1 s step this bound is $`2.8\times10^{-4}`$
in fraction, or 0.028 percentage points, against a displayed resolution of
0.01. A much wider gate would let that section's claim — that the last
displayed digit is uncertain by about two counts at the worst reachable
trajectory — quietly become false while still passing.

**The error is a systematic sequencing bias, not noise, and it does not
cancel between compartments.** The shipped step applies its transfers in
order — fresh gas into the circuit, circuit to alveoli, alveoli to blood and
tissues — and each compartment is therefore driven across the interval by an
upstream value the same step has *already* moved. The measured consequence is
a bias whose sign depends on a compartment's position in that chain, and the
signs are opposite at the two ends. Through a 600 s wash-in at the envelope
corner, for all three agents, the circuit reads *below* the reference at
every sampled step while mixed venous, vessel rich, muscle and fat all read
*above* it at every sampled step; the alveolar fraction sits between the two
mechanisms and follows the blood-uptake term, below the reference for 95% or
more of the run. Reversing the trajectory reverses the bias where the
trajectory itself reverses: dialling to zero after that wash-in puts the
circuit above the reference for 97–99% of the washout and mixed venous and
vessel rich below it for 90–97%, while muscle and fat stay above throughout
because they are still filling. The pattern is reproducible, not random.

For a reader this is the difference between an error that cancels in a
comparison and one that does not, and it does not cancel. The six readouts
are placed in one row to be read comparatively — the circuit leads the
alveoli lead the tissues — and a difference between two of them carries the
*sum* of two displacements of opposite sign. Measured across the trajectories
above, the error in a displayed difference runs up to 1.8 times the error in
either reading it is taken from, and its worst value is 0.030 percentage
points — alveolar minus mixed venous, on the worst trajectory — against 0.023
for the worst single reading. A gradient between two compartments is
therefore the least accurate thing this interface displays, not the most.

A companion test confirms that halving $`\Delta t`$ halves the error, which
is what makes a bound established at one step size a bound on the
coefficient itself. The reference states are pinned in the test file: a
change to the oracle or to a parameter file must be re-derived and reviewed
rather than silently adopted. The supported ranges above are restated in the
test file and checked against `core/supported_ranges.py`, so widening the
model's declared domain cannot silently leave this gate measuring a subset
of it.

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
any statement of this result, including in `README.md`.

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

The ranges are not merely the domain nothing has measured. The shipped split
is first order, so its error is $`C\,\Delta t`$, and $`C`$ grows with the
flows roughly in proportion — doubling all three roughly doubles it. Measured
on desflurane over the *unperfused load, then dial off* trajectory of
"Independent-solution test" above, which is what the documented
$`2.29\times10^{-3}\ \mathrm{s^{-1}}`$ is measured on, and quoted at the
shipped 0.1 s step against the 0.01-percentage-point displayed resolution:

| Setting | $`C`$ (s⁻¹) | Multiple of the bound | Last displayed digit uncertain by |
| --- | --- | --- | --- |
| The documented maxima | $`2.29\times10^{-3}`$ | 1.0 | 2.3 counts |
| Alveolar ventilation 200 L/min | $`3.37\times10^{-3}`$ | 1.5 | 3.4 counts |
| Fresh gas flow 500 L/min | $`5.82\times10^{-3}`$ | 2.5 | 5.8 counts |
| All three flows at twice their maxima | $`4.57\times10^{-3}`$ | 2.0 | 4.6 counts |
| All three at ten times their maxima | $`2.28\times10^{-2}`$ | 10.0 | 23 counts |
| Cardiac output 1000 L/min | $`9.12\times10^{-2}`$ | 40 | 91 counts |

The last row is the setting PL-0MLQ found accepted. Ninety-one counts is an
alveolar readout wrong in its *first* decimal while presenting itself as a
settled two-decimal value, which is the plausible-but-wrong clinical number
`CLAUDE.md` requires an obvious failure in place of. Every other row fails a
claim "Displayed precision" below makes about the last displayed digit, by
the multiple in the third column. So a setting outside these intervals is not
an unverified number but a wrong one, and the amount it is wrong by is known.

Note what the table also shows: the error does *not* explode at the boundary.
Nothing breaks at 10.01 L/min, and the interval's exact endpoints are a
decision — they are the settings envelope the interface offers and the
verification measures over — rather than a discovered cliff. Widening one is
therefore a legitimate change and a safety-critical one: re-measure $`C`$ over
the new domain, re-derive the displayed resolution and the supported
simulation step from it, and revise this section, "Independent-solution
test", "Supported simulation step" and "Displayed precision" together.

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
above bounds the operator split's error over the trajectories these ranges
can produce, and its worst case — $`2.29\times10^{-3}\ \mathrm{s^{-1}}`$ — is
reached on a trajectory that holds cardiac output at zero. Narrowing a range
would take that worst case out of the reachable domain, and widening one
would admit trajectories never measured; either way the bound must be
re-measured. Three checks keep that from happening silently:
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
- set simulation time to zero;
- clear circuit, alveolar, blood, and tissue agent amounts;
- clear concentration and mass-accounting history;
- reset cumulative delivered and exhausted amounts;
- restore the mass-balance residual to zero;
- clear any recorded failure state, so a session halted by a failed step
  becomes startable again from a clean state; and
- preserve the user’s selected settings.

## Interface boundary

The Flet interface may:

- display values;
- convert fractions to percent;
- collect user settings;
- issue Start, Pause, and Reset commands;
- halt a run and record why when the core raises, and report a value the
  core refused;
- render snapshot histories;
- select which recorded samples a plotted trace draws, subject to the
  constraint below; and
- display mass-balance status.

A plotted trace need not draw every recorded sample — the recorded history
grows by one sample per simulation step, well beyond what a chart can
resolve — but every point it does draw must be a recorded sample. The
interface must not interpolate, smooth, average, or otherwise synthesize a
plotted value, and the most recent recorded sample must always be drawn, so
that the end of a trace and the numeric readouts cannot disagree. Selection
must also preserve the extremes of the samples it omits, so that decimation
cannot hide an excursion the model produced.

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
- present a run halted by a failure as though it were paused; or
- display a concentration at a finer resolution than "Displayed precision"
  justifies, or render a value the model does not resolve as though it were
  a value the model asserts.

The controller exposes immutable snapshots rather than mutable compartment objects.

## Minimum displayed outputs

The interface must show:

- simulated time;
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
- total stored amount; and
- mass-balance residual or status.

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

**What the solver's error actually is.** The shipped step is a first-order
operator split (see "Selected method (as implemented)"), and its
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

**What the last digit does not cover, and what it still does.** The error is
a systematic sequencing bias rather than noise, and its sign is opposite at
the two ends of the transfer chain (see "Independent-solution test"). A
*difference* between two of the six readouts therefore carries the sum of two
displacements, up to 1.8 times the error in either reading alone, worst
measured at 0.030 percentage points. **The numeric gap between two readouts
is accordingly the least certain thing on the display**, and its last digit
should be read as carrying no information.

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
display resolves one step and no finer. Fresh gas flow, alveolar
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

The chart plots the same percentages on a shared linear axis scaled to the
agent's maximum dial setting. Its resolution is set by pixels rather than by
decimals, and it is coarser than the numeric readouts throughout; the
readouts, not the traces, are where a value is read.

`app/simulation_view.py` holds the resolution as a single constant with the
formatter derived from it, and `tests/unit/test_simulation_view.py` pins
both. `tests/reference/test_coupled_dynamics.py` restates the same constant
and checks it against the interface, because the ordering claim above is a
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

As of v0.2.3, this model does not model:

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
- anesthetic potency;
- BIS, eBIS, or hypnosis;
- nociceptive response;
- hemodynamic response;
- IV anesthetics;
- effect-site models;
- clinical alarms;
- dosing recommendations; or
- patient-specific clinical predictions.

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
