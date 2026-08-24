# Volatile-agent patient uptake and distribution model

## Status

This document specifies the scientific model implemented starting in
v0.1.0 and still in force in v0.2.2, the current released baseline (see
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
fraction is defined as \(F_a \equiv F_A\), with no arterial volume, mixing
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

For example:

$$
F = 0.02
$$

represents a 2% gas-phase concentration.

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

Let:

$$
M_x
$$

denote the equivalent gas volume of sevoflurane stored in compartment \(x\).

The unit used in code is liters of equivalent pure sevoflurane gas unless the implementation document explicitly selects another consistent unit.

## Symbols

| Symbol | Meaning | Unit |
| --- | --- | --- |
| \(t\) | Explicit simulation time | s |
| \(\Delta t\) | Simulation step | s |
| \(F_D\) | Delivered fresh-gas sevoflurane fraction | dimensionless |
| \(F_C\) | Breathing-circuit sevoflurane fraction | dimensionless |
| \(F_A\) | Alveolar sevoflurane fraction | dimensionless |
| \(F_a\) | Arterial partial-pressure-equivalent fraction (flow-limited: \(F_a \equiv F_A\); not an independent state) | dimensionless |
| \(F_v\) | Venous blood partial-pressure-equivalent fraction | dimensionless |
| \(F_i\) | Tissue group \(i\) partial-pressure-equivalent fraction | dimensionless |
| \(V_C\) | Mixed breathing-circuit volume | L gas |
| \(V_A\) | Modeled alveolar gas volume | L gas |
| \(V_v\) | Venous blood-pool volume | L blood |
| \(V_i\) | Volume of tissue group \(i\) | L tissue |
| \(\dot V_F\) | Fresh gas flow | L gas/min |
| \(\dot V_A\) | Alveolar ventilation | L gas/min |
| \(Q\) | Cardiac output | L blood/min |
| \(Q_i\) | Blood flow to tissue group \(i\) | L blood/min |
| \(\lambda_{b:g}\) | Sevoflurane blood:gas partition coefficient | dimensionless |
| \(\lambda_{i:b}\) | Tissue:blood partition coefficient for group \(i\) | dimensionless |
| \(M_C\) | Sevoflurane stored in the breathing circuit | L equivalent gas |
| \(M_A\) | Sevoflurane stored in alveolar gas | L equivalent gas |
| \(M_v\) | Sevoflurane stored in venous blood | L equivalent gas |
| \(M_i\) | Sevoflurane stored in tissue group \(i\) | L equivalent gas |

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

Arterial blood is flow-limited (see "Model boundary") and has no capacity or amount balance of its own: \(F_a \equiv F_A\) at every instant.

Venous blood stores:

$$
M_v = V_v \lambda_{b:g} F_v
$$

Therefore:

$$
F_v = \frac{M_v}{V_v\lambda_{b:g}}
$$

### Tissue compartments

For tissue group \(i\):

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

- a tissue volume \(V_i\);
- a fraction of cardiac output \(f_i\);
- a tissue blood flow \(Q_i\);
- a sevoflurane tissue:blood partition coefficient \(\lambda_{i:b}\);
- a stored sevoflurane amount \(M_i\); and
- a derived partial-pressure-equivalent fraction \(F_i\).

Tissue flow is:

$$
Q_i = f_iQ
$$

The flow fractions must satisfy:

$$
f_i > 0
$$

and:

$$
\sum_i f_i = 1
$$

within a documented validation tolerance.

Consequently:

$$
\sum_i Q_i = Q
$$

## Governing equations

All flow terms below must use liters per second after conversion from user-facing liters per minute.

### Breathing circuit

Fresh gas enters at concentration \(F_D\). An equal fresh-gas volume leaves through the exhaust at the current mixed-circuit concentration \(F_C\).

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

Pulmonary blood flow enters the lungs at venous concentration \(F_v\) and leaves in equilibrium with alveolar gas at \(F_A\).

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

The pulmonary uptake rate is:

$$
\dot M_{\mathrm{pulmonary}} = Q\lambda_{b:g}(F_A-F_v)
$$

A positive value represents net uptake from alveolar gas into blood. A negative value represents net return from blood to alveolar gas during washout.

### Arterial blood

Arterial blood is flow-limited: blood leaving the lungs equilibrates instantaneously with alveolar gas, so \(F_a \equiv F_A\) at every instant (see "Model boundary"). There is no separate arterial amount balance, capacity, or time constant. Every equation below that references \(F_a\) uses the current alveolar fraction \(F_A\) directly.

### Tissue uptake and return

For tissue group \(i\), arterial blood enters at \(F_a\) and venous blood leaves in equilibrium with the tissue at \(F_i\).

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

Blood leaving the tissue groups enters the venous pool. Venous blood leaves that pool for the lungs at \(F_v\).

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

when:

$$
Q>0
$$

At zero cardiac output, pulmonary and tissue perfusion transfers are zero and no division by \(Q\) is performed.

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

For an initial stored amount \(M_{\mathrm{initial}}\):

$$
M_{\mathrm{initial}} + M_{\mathrm{delivered}} = M_{\mathrm{stored}} + M_{\mathrm{exhausted}} + \varepsilon_M
$$

where \(\varepsilon_M\) is the numerical mass-balance residual.

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

Here \(M_{\mathrm{scale}}\) is a documented small positive reference amount that prevents division by zero.

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

The initial supported simulation step is:

```text
SIMULATION_STEP_S = 0.1
```

### Selected method (as implemented)

Each simulation step is advanced by exact analytic solution of every pairwise
exchange, composed by first-order operator splitting rather than a generic
numerical integrator:

1. the circuit exchanges exactly with fresh gas (`BreathingCircuit.advance_fresh_gas`), holding ventilation fixed for the step;
2. the circuit and alveolar compartments then exchange exactly with each other (`RespiratorySystem._exchange_circuit_and_alveoli`), a closed-form solution of the two-compartment linear exchange that conserves \(M_C+M_A\) exactly;
3. each tissue group exchanges exactly with arterial blood (`TissueGroup.advance`), holding the arterial fraction (\(=F_A\)) fixed for the step;
4. venous blood mixes exactly with the flow-weighted tissue outflow (`VenousBloodCompartment.advance`); and
5. the net patient uptake is applied back to alveolar gas (`AlveolarCompartment.apply_blood_uptake`).

Because each sub-exchange is solved exactly while temporarily holding the
other flows constant, this is a first-order (Lie/Godunov) operator split of
the fully coupled system: the splitting error is \(O(\Delta t)\) relative to
the true simultaneous solution, even though each individual sub-step is
exact. This is why the step-refinement test (`test_step_refinement_converges`)
is a release gate rather than an optional diagnostic — it is the only check
that bounds this error empirically across supported step sizes. A
fourth-order Runge–Kutta method would remove the splitting error but was not
required to pass the documented tolerances at `SIMULATION_STEP_S = 0.1`.

The split has an applicability domain, and stepping outside it must fail
rather than produce a number. At a large enough \(\Delta t\) the
sequential composition drives an amount negative — step 5 tries to remove
more agent from alveolar gas than step 2 left in it — and the compartment
guard rejects the result. `RespiratorySystem.advance()` reports that as
`SimulationNumericalError`: the step is abandoned, simulation time does not
advance, and the caller must stop the run rather than read the partially
applied state as a result. Preferring an obvious failure to a
plausible-looking number is the required behavior here, not a defensive
extra. The step at which this first occurs depends on the agent and the
current state; at the shipped `SIMULATION_STEP_S = 0.1` it does not occur,
and the step-refinement gate is what keeps the shipped step well inside the
domain.

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
- the tissue-group mapping; and
- a brief justification for selecting that source.

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
drawn from the same source table (Stadler et al. 2012, Table 1 — the paper
already cited for sevoflurane), so the three data files are directly
comparable rather than assembled from unrelated sources.

Desflurane is markedly less soluble than sevoflurane, which is itself less
soluble than isoflurane (blood:gas 0.42 < 0.65 < 1.3). This does not change
any equation: lower solubility only means faster equilibration through the
same closed-form solutions, which `tests/reference/test_multi_agent.py`
checks directly by comparing simulated alveolar/circuit ratios rather than
only comparing the static coefficient values.

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
limit for the agent in use (set by `RespiratorySystem.for_agent()`) and
**must reject** any delivered concentration above it, at construction and
at every later change, rather than clamping to it. A clamp would run,
display, and chart a dial position the caller never requested, which is
indistinguishable on screen from one they did. Zero is always accepted: it
is the vaporizer turned off, which is how washout begins. Its purpose is to
keep the simulator from offering a dial position that does not exist on the
corresponding real device. It is a device limit, not a physiologic or
safety limit: it says nothing about whether a given concentration is
appropriate for a patient.

`mac_percent` is 1 MAC for a 40-year-old adult. It is used for exactly one
thing: choosing the starting position of the delivered-concentration control
when a run begins, so that a new run starts from a recognizable clinical
anchor rather than an arbitrary number. `RespiratorySystem.for_agent()`
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

If all initial stores are zero and:

$$
F_D=0
$$

then every stored amount and concentration must remain zero.

### Zero-ventilation test

If:

$$
\dot V_A=0
$$

the circuit may wash in, but the patient compartments must receive no new agent through ventilation.

### Zero-cardiac-output test

If:

$$
Q=0
$$

alveolar gas may change through ventilation, but arterial blood, venous blood, and tissue stores must not change through perfusion.

### Zero-tissue-flow test

For any tissue \(i\):

$$
Q_i=0
$$

must imply:

$$
\frac{dM_i}{dt}=0
$$

### Equilibrium test

If all connected compartments have the same partial-pressure-equivalent fraction:

$$
F_C=F_A=F_a=F_v=F_i
$$

then all internal transfer rates must be zero.

### Directional ventilation test

With otherwise identical conditions, increasing alveolar ventilation must accelerate the approach of \(F_A\) toward \(F_C\).

### Directional solubility test

In controlled synthetic cases, increasing \(\lambda_{b:g}\) must increase blood capacity and slow the rise of \(F_A/F_C\).

### Directional tissue-capacity test

Increasing either \(V_i\) or \(\lambda_{i:b}\), with flow held constant, must lengthen the tissue time constant:

$$
\tau_i =
\frac{V_i\lambda_{i:b}}{Q_i}
$$

### Washout test

After loading the compartments, setting:

$$
F_D=0
$$

must produce finite, nonnegative washout without spontaneous increases in total system mass.

Individual tissue concentrations may temporarily rise through redistribution, so the test must not incorrectly require every compartment to decrease monotonically.

### Step-refinement test

Reference simulations using supported smaller steps must converge toward the same solution.

At minimum, compare:

```text
dt = 0.1 s
dt = 0.05 s
dt = 0.025 s
```

The release comparison tolerance must be documented before tagging.

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
- delivered sevoflurane concentration;
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
- continue a run past a step the core could not complete; or
- present a run halted by a failure as though it were paused.

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

Arterial concentration is deliberately **not** in this list. Arterial blood
is flow-limited in this model and holds no independent state: $F_a \equiv
F_A$ (see "Model boundary"). A separate arterial readout would therefore
display the alveolar number a second time under a different name, which
would present a definitional identity as though it were an independently
modeled quantity. Earlier revisions of this document required an arterial
readout; that requirement predates the arterial simplification being made
explicit and is withdrawn rather than being satisfied by a duplicate label.

Showing which agent is running is a required output, not a convenience: a
correct concentration attributed to the wrong agent is a presentation
failure, and the same number means a different clinical depth for each agent
(2% is about 1 MAC of sevoflurane but roughly a third of a MAC of
desflurane).

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
reason. Both stop the numbers advancing, but a pause leaves state the
reader can trust while a halt may leave a compartment partway through a
step that never completed. A halted run displayed as "Paused" therefore
gives the reader no cue that anything is wrong with the values beside it —
the stale-state failure this specification's interface rules exist to
prevent — and a display that is merely frozen, with no state change at all,
is worse still.

The phrase “end-tidal-equivalent” must not imply that airway sampling dynamics, dead space, or capnography are modeled.

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

As of v0.2.2, this model does not model:

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
