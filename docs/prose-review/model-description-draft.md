# The model, described for a clinician (draft)

**Status of this file.** This is a draft for the project owner to read. It is
not the specification, which is still `docs/MODEL.md`. It was written on
2026-11-11 from the paragraphs of `docs/MODEL.md` at commit `50af1a2e` that a
clinician needs in order to trust or interpret a displayed value. It leaves out
test descriptions, interface requirements, code names and decision history.
Where the two disagree, `docs/MODEL.md` is right. Sources are cited by
author and year, and § "References" at the end gives each one in full.

## 1. What the simulator is for

The simulator is a teaching model of how a volatile anesthetic moves between
the breathing circuit, alveolar gas, blood and the tissues, under management
that the learner chooses. It is intended for anesthesia clinicians, trainees
and students. It shows the compartments that no clinical monitor displays:
vessel-rich, muscle, fat and mixed venous.

It is not a clinical prediction, a dosing tool, a patient monitor or a medical
device.

**The simulator is not intended for use with an identifiable patient's data.**
It is meant to be run on hypothetical or illustrative values. It is not
intended for entering, importing or reproducing an identifiable patient's
values, or for informing the management of a specific patient. Keeping the
simulator open on a computer during a case is ordinary teaching use. A run
built from a particular patient's weight, age and cardiac output is a
prediction about that patient, whatever the window is labelled.

A learner can still set cardiac output or alveolar ventilation to a value
measured in a real patient, because changing them is a core teaching feature.
The run then shows the reference adult at that flow. It is not a prediction
for that patient, and only this statement of intended use guards against
reading it as one.

The project adopts software safety Class C for the whole application as an
engineering standard. It claims no conformance to IEC 62304 or to a quality
management system, and no regulatory status.

## 2. What the model represents

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

The model has six compartments:

1. one ideal, perfectly mixed breathing circuit;
2. one ideal, perfectly mixed alveolar gas compartment;
3. one venous blood pool;
4. one vessel-rich tissue group;
5. one muscle tissue group; and
6. one fat tissue group.

It represents:

- circuit wash-in and washout;
- ventilation between the breathing circuit and alveolar gas;
- uptake from alveolar gas into blood;
- delivery to the tissues in proportion to cardiac output;
- perfusion-limited distribution into the three tissue groups;
- mixed-venous return to the lungs; and
- changes during a run in fresh gas flow, delivered concentration, alveolar
  ventilation and cardiac output.

Sevoflurane, isoflurane and desflurane share one set of equations, one set of
compartments and one reference adult patient. An agent enters the equations
only through four partition coefficients: one blood:gas and three tissue:gas.
Because the equations are shared, lower solubility only makes an agent
equilibrate faster (blood:gas 0.42 for desflurane, 0.65 for sevoflurane, 1.3
for isoflurane). The equations and compartments have not changed since v0.1.0.

**Agent enters and leaves in one way each.** Agent and carrier gas enter only
with the fresh gas, and mixed circuit gas leaves only through the circuit
exhaust. Apart from that, the circuit and the patient form a closed path in
which gas recirculates. The model has no metabolism or other chemical
destruction of the agent.

**Exchange with blood is perfusion-limited.** Blood leaves the lung, or a
tissue, at equilibrium with it, so the barrier between them never limits how
fast agent moves. The rate is set by the blood flow, the blood:gas partition
coefficient and the difference in partial pressure. The model does not
represent diffusion-limited exchange, in which blood leaves before it has
equilibrated. Jones and Rowland-Yeo call the two "perfusion rate-limited" and
"permeability rate-limited", and give the first as typical of small lipophilic
molecules, which the volatile agents are (Jones and Rowland-Yeo 2013). Yasuda
et al. assumed perfusion-limited delivery to the tissues when they fitted
sevoflurane and isoflurane kinetics in volunteers (Yasuda et al. 1991a,
p. 319).

**Arterial blood is not a separate compartment.** The model has no shunt and
one alveolar compartment, so all arterial blood has equilibrated with alveolar
gas. Arterial partial pressure, as a fraction, is defined as the alveolar
fraction, $`F_a \equiv F_A`$, with no arterial volume or mixing delay. This is
a simplification of the model. In patients, arterial partial pressure runs
below end-tidal during administration, as Carpenter and Eger (1989) measured.

**Inspired gas is circuit gas.** The circuit is perfectly mixed, with no dead
space and no separate inspiratory and expiratory limbs. The gas the patient
inspires is therefore the circuit gas, with no transport delay. The model
tracks one concentration between the vaporizer and the alveoli, the inspired
fraction $`F_I`$. This is an assumption of this circuit model and does not
hold for breathing systems in general. It makes the displayed $`F_A/F_I`$
ratio the textbook curve of inhaled-anesthetic uptake.

**The structure follows Gas Man.** The sevoflurane and patient values come
from the Gas Man simulator. In Gas Man, as here, each tissue group exchanges
agent only with blood, at a perfusion-limited rate, and arterial partial
pressure is displayed without being tracked as a compartment. Gas Man tracks
alveolar gas and the vessel-rich, muscle and fat groups (Philip, Gas Man
Version 4.1; Hendrickx, Lemmens and Shafer 2006).

**The three tissue groups are Eger's five-compartment model without its lung
and intertissue-diffusion compartments.** Eger grouped the body's tissues by
capacity and blood flow into vessel-rich, muscle, fat and vessel-poor groups.
His later five-compartment model deletes the vessel-poor group "because its
contribution to uptake is considered insignificant" (Carpenter et al. 1986, as
Hendrickx and De Wolf report it on p. 163). Eger and Saidman describe that
group as "ligaments, tendons, cartilage, bone, and other avascular tissues",
which "does not contribute to uptake because of its minimal or absent
perfusion" (Eger and Saidman 2005, p. 1023). Gas Man also has exactly three
tissue groups (Philip, Workbook, Model Parameters table, p. 168). The
three groups here hold 6.0, 33.0 and 14.5 L, which is 53.5 L in a 70 kg
patient. That total is the sum of three compartments and is not a body
composition.

## 3. Units and symbols

**Time** is in seconds. The model keeps its own simulation time and never
takes it from the computer's clock.

**Concentration.** Every concentration that the model computes is a
dimensionless fraction, equivalent to a partial pressure divided by one
atmosphere. $`F = 0.02`$ is a 2% gas-phase concentration, and
$`\text{percent} = 100F`$. Ambient pressure is fixed at 760 mmHg, so a
fraction and a partial pressure differ only by that factor: $`F_A = 0.02`$ is
15.2 mmHg. The vaporizer dial and MAC are given in percent of one atmosphere.

**Agent amount.** Every compartment stores its agent as an equivalent gas
volume: litres of pure agent gas at 20 °C and 760 mmHg, dry. The ideal-gas
molar volume at that condition is 24.055 L/mol. The condition defines the unit
only, and does not mean that any of the agent is physically at 20 °C. The
agent in blood and fat is dissolved, so the volume expresses an amount of
agent and not gas present in the body. The condition matters only when an
amount is converted into moles, mass or millilitres of liquid. It changes no
concentration, because every equation works with fractions, physical volumes
and partition coefficients, which are ratios.

The model physically has two conditions under that one label. The circuit
volume is at ambient temperature and the fresh gas flow is a flow at the
common gas outlet, so the circuit, delivered and exhausted amounts are at the
stated condition and are exact there. The alveolar gas volume is at body
temperature, and the partition coefficients behind the venous and tissue
amounts were measured at 37 °C, where the molar volume is 25.450 L/mol. Those
three stores hold 5.5% fewer moles than their 20 °C label implies, so
converting an alveolar, venous or tissue amount at 20 °C overstates it by
5.8% (a factor of 1.058).

| Symbol | Meaning | Unit |
| --- | --- | --- |
| $`t`$ | Elapsed simulation time | s |
| $`\Delta t`$ | Simulation step | s |
| $`F_D`$ | Delivered fresh-gas agent fraction | dimensionless |
| $`F_I`$ | Inspired agent fraction, which is the fraction in the breathing circuit | dimensionless |
| $`F_A`$ | Alveolar agent fraction | dimensionless |
| $`F_a`$ | Arterial fraction, defined as $`F_a \equiv F_A`$ | dimensionless |
| $`F_v`$ | Venous blood fraction | dimensionless |
| $`F_i`$ | Fraction in tissue group $`i`$ | dimensionless |
| $`V_C`$ | Mixed breathing-circuit volume | L gas |
| $`V_A`$ | Alveolar gas volume | L gas |
| $`V_v`$ | Venous blood-pool volume | L blood |
| $`V_i`$ | Volume of tissue group $`i`$ | L tissue |
| $`\dot V_F`$ | Fresh gas flow at the common gas outlet | L gas/min |
| $`\dot V_A`$ | Alveolar ventilation | L gas/min |
| $`Q`$ | Cardiac output | L blood/min |
| $`Q_i`$ | Blood flow to tissue group $`i`$, equal to $`f_iQ`$ | L blood/min |
| $`f_i`$ | Fraction of cardiac output reaching tissue group $`i`$ | dimensionless |
| $`\mathrm{MAC}_\%`$ | The agent's alveolar concentration at 1 MAC, at age 40. Used only as a display divisor | percent |
| $`\lambda_{b:g}`$ | Blood:gas partition coefficient | dimensionless |
| $`\lambda_{i:g}`$ | Tissue:gas partition coefficient for group $`i`$ | dimensionless |
| $`\lambda_{i:b}`$ | Tissue:blood partition coefficient for group $`i`$, equal to $`\lambda_{i:g}/\lambda_{b:g}`$ | dimensionless |
| $`M_C`$, $`M_A`$, $`M_v`$, $`M_i`$ | Agent stored in the circuit, alveolar gas, venous blood and tissue group $`i`$ | L equivalent gas |

The symbols for the inspired fraction, $`F_I`$, and a tissue group's fraction,
$`F_i`$, differ only in case.

Symbols and the gas-phase cascade $`F_D \rightarrow F_I \rightarrow F_A`$
follow Hendrickx and De Wolf (2008, pp. 161-162). They attribute the
$`F_D - F_I`$ gradient to rebreathing (p. 169) and the $`F_I - F_A`$ gradient
to uptake (p. 171), and describe the teaching role of the $`F_A/F_I`$ curve (p.
167).

## 4. Assumptions

Every value the model computes rests on these assumptions.

- Every compartment is perfectly mixed.
- Each tissue group exchanges agent only with the blood flowing through it.
  No agent passes directly from one tissue group to another.
- Partition coefficients, tissue volumes and flow fractions are constant.
- Blood leaving the lung has equilibrated with alveolar gas, and venous blood
  leaving a tissue group has equilibrated with that group.
- There is no metabolism, no chemical degradation, and no reaction of the
  agent with circuit materials.
- The reference patient does not change physiologically during a run.
- The alveolar gas volume is constant. Uptake draws agent out of the alveolar
  gas without reducing its volume, and no inspired flow replaces the gas that
  blood absorbs. This excludes nitrous oxide, simultaneous gases, and the
  concentration and second-gas effects (§ 10.2).
- Carrier gases do not affect agent kinetics.
- The breathing system is a semi-closed circle whose surplus gas valve is
  open. Exhaust outflow equals fresh-gas inflow at every instant, so one fresh
  gas flow, $`\dot V_F`$, is both the delivery rate and the removal rate.
- There is no vaporizer or machine delivery delay beyond the modeled circuit.
- Settings are constant within each calculation step of 0.1 s.
- Temperature is constant. Every stored gas volume is at 20 °C and 760 mmHg,
  dry, and no equation converts between ambient and body conditions.
- Inspired gas reaches the alveoli undiluted by water vapor, because the
  modeled alveoli hold no water (§ 10.12).
- Ambient pressure is 760 mmHg, so the model applies only at sea level. More
  than anything else in the model, the vaporizer control depends on this
  (§ 10.13).

## 5. Equations

### 5.1 Blood flow to the tissue groups

Each tissue group receives a fixed fraction of cardiac output:

$$
Q_i = f_iQ, \qquad f_i > 0, \qquad \sum_i f_i = 1
$$

so the three groups together receive the whole cardiac output. The fractions
must sum to 1 within one part in a million million. This is the model's whole
representation of perfusion, and it comes from one assumption in Appendix 1 of
Mapleson (1963): "it has been thought legitimate to assume that **the blood
flow to any region is a fixed fraction of the total cardiac output** from 20 to
70 years of age."

### 5.2 How much agent each compartment holds

$$
M_C = V_C F_I, \qquad M_A = V_A F_A, \qquad M_v = V_v \lambda_{b:g} F_v, \qquad M_i = C_iF_i
$$

The capacity of tissue group $`i`$ is its volume times its tissue:gas
coefficient:

$$
C_i = V_i\lambda_{i:b}\lambda_{b:g} = V_i\lambda_{i:g}
$$

The simulated patient has one blood:gas partition coefficient. The lung's
uptake term and every tissue:blood coefficient use that one value.

### 5.3 Breathing circuit

Fresh gas enters the circuit at flow $`\dot V_F`$ and concentration $`F_D`$.
An equal volume of mixed circuit gas leaves through the exhaust at $`F_I`$.
Ventilation exchanges gas between the circuit and the alveoli:

$$
\frac{dM_C}{dt} = \dot V_F(F_D-F_I) - \dot V_A(F_I-F_A)
$$

$$
\frac{dF_I}{dt} = \frac{\dot V_F}{V_C}(F_D-F_I) - \frac{\dot V_A}{V_C}(F_I-F_A)
$$

With constant fresh gas and no patient connected ($`\dot V_A = 0`$), the
circuit alone has the exact solution

$$
F_I(t+\Delta t) = F_D+\left[F_I(t)-F_D\right]\exp\left(-\frac{\dot V_F\Delta t}{V_C}\right)
$$

with time constant $`V_C/\dot V_F`$.

**The fresh gas flow is the flow at the common gas outlet, which is higher
than the flowmeter setting.** $`\dot V_F`$ is the whole gas stream delivered
to the circuit: the carrier gas plus the vapor that the vaporizer adds. With
carrier flow $`\dot V_c`$ (the flowmeter setting) and added vapor flow
$`\dot V_v`$, the delivered fraction is
$`F_D = \dot V_v/(\dot V_c + \dot V_v)`$, and

$$
\dot V_F = \dot V_c + \dot V_v = \frac{\dot V_c}{1-F_D}
$$

At 2% delivered, $`\dot V_F`$ is 2% above the flowmeter setting. At the top of
the desflurane dial, 18%, it is 22% above, so flowmeters set to 2 L/min
deliver about 2.44 L/min. A reader who takes the simulator's fresh gas flow
control for a flowmeter setting misjudges the circuit time constant by the
same factor.

**The circuit volume is that of the assembled breathing system.** The model
has one well-mixed gas compartment in front of the patient, so $`V_C`$ is the
sum of the apparatus volume (the workstation's internal volume, including its
absorber) and the patient circuit (the disposable limbs and Y-piece). It
leaves out the reservoir bag. § 6.4 gives its value.

### 5.4 Alveolar gas

Pulmonary blood enters the lungs at the venous concentration $`F_v`$ and
leaves in equilibrium with alveolar gas, at $`F_A`$:

$$
\frac{dM_A}{dt} = \dot V_A(F_I-F_A) - Q\lambda_{b:g}(F_A-F_v)
$$

$$
\frac{dF_A}{dt} = \frac{\dot V_A(F_I-F_A) - Q\lambda_{b:g}(F_A-F_v)}{V_A}
$$

The pulmonary uptake rate is

$$
\dot M_{\mathrm{pulmonary}} = Q\lambda_{b:g}(F_A-F_v)
$$

A positive value is net uptake into blood. A negative value is net return from
blood to alveolar gas during washout.

### 5.5 Tissue groups

Arterial blood enters tissue group $`i`$ at $`F_a`$, and venous blood leaves
in equilibrium with the tissue, at $`F_i`$:

$$
\frac{dM_i}{dt} = Q_i\lambda_{b:g}(F_a-F_i), \qquad
\frac{dF_i}{dt} = \frac{Q_i}{V_i\lambda_{i:b}}(F_a-F_i)
$$

so each tissue group's time constant is

$$
\tau_i = \frac{V_i\lambda_{i:b}}{Q_i}
$$

### 5.6 Venous blood

Blood from the tissue groups enters the venous pool and leaves for the lungs
at $`F_v`$:

$$
\frac{dM_v}{dt} = \lambda_{b:g}\left(\sum_i Q_iF_i-QF_v\right), \qquad
\frac{dF_v}{dt} = \frac{\sum_i Q_iF_i-QF_v}{V_v}
$$

When $`Q>0`$, the flow-weighted concentration entering the pool is
$`F_{\mathrm{tissue\ return}} = \sum_i Q_iF_i / Q`$.

### 5.7 Conservation of agent

$$
M_{\mathrm{delivered}}(t) = \int_0^t \dot V_FF_D\,dt, \qquad
M_{\mathrm{exhausted}}(t) = \int_0^t \dot V_FF_I\,dt, \qquad
M_{\mathrm{stored}} = M_C+M_A+M_v+\sum_i M_i
$$

$$
M_{\mathrm{initial}} + M_{\mathrm{delivered}} = M_{\mathrm{stored}} + M_{\mathrm{exhausted}} + \varepsilon_M
$$

where $`\varepsilon_M`$ is the numerical residual of the mass balance.

### 5.8 Time constants

**Alveolar gas has no single time constant.** Ventilation alone, at $`Q = 0`$,
would turn the alveolar volume over with $`\tau = V_A/\dot V_A`$, which is
37.5 s for the reference adult ($`V_A = 2.5`$ L, $`\dot V_A = 4`$ L/min). The
simulator does not display that figure, because it matches no rate in the
simulation. Blood uptake acts alongside ventilation. If $`F_I`$ and $`F_v`$
were held fixed, $`F_A`$ would change with the time constant
$`V_A/(\dot V_A + Q\lambda_{b:g})`$, which is 20.7 s for the reference adult
on sevoflurane. But $`F_I`$ and $`F_v`$ move together with $`F_A`$.

**Six time constants set the pace of every run.** Each compartment's
concentration is the level that the delivered fraction sets, plus six
exponential terms. The time constants depend on the three flows, the volumes
and the partition coefficients, and not on the delivered fraction. The table
gives them at the reference adult's default flows and at the maximum supported
flows, with the 6 L circuit.

| Flows (L/min): fresh gas, $`\dot V_A`$, $`Q`$ | Agent | $`\tau_1`$ (s) | $`\tau_2`$ (s) | $`\tau_3`$ (s) | $`\tau_4`$ (s) | $`\tau_5`$ (s) | $`\tau_6`$ (s) | Oscillation period (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4, 4, 5 (defaults) | sevoflurane | 15.8 | 15.8 | 63.1 | 365 | 10 300 | 167 000 | 753 |
| | isoflurane | 13.7 | 13.7 | 54.5 | 426 | 11 500 | 187 000 | 466 |
| | desflurane | 16.6 | 16.6 | 66.1 | 264 | 6 020 | 95 500 | 1 540 |
| 10, 12, 10 (maximums) | sevoflurane | 6.89 | 6.89 | 27.2 | 161 | 4 890 | 81 300 | 398 |
| | isoflurane | 6.02 | 6.21 | 22.4 | 190 | 5 280 | 89 500 | none |
| | desflurane | 7.17 | 7.17 | 29.1 | 114 | 2 890 | 47 000 | 384 |

- The fastest time constant is 13.7 to 16.6 s at the default flows and 6.02 to
  7.17 s at the maximum flows. The fastest at any supported setting is
  isoflurane's 5.83 s, at 10 L/min of fresh gas, 12 L/min of ventilation and
  9.32 L/min of cardiac output. Nothing in the model changes faster.
- The slowest is the fat group's, at 47 000 s (13 hours) to 187 000 s
  (52 hours).
- In five of the six rows, the two fastest terms form one oscillation, because
  agent circulates from circuit to alveoli to tissues and back. It cannot be
  seen. Its period is 384 to 1 540 s, and over half a period it shrinks by a
  factor of at least $`e^{17}`$, about $`2.5\times10^{7}`$.

### 5.9 How the equations are solved

The model advances in steps of 0.1 s of simulated time and holds every setting
constant over each step. Within a step the six fractions follow fixed linear
equations, which have an exact solution, so each step solves the whole model
at once, exactly. The same step updates the running totals of agent delivered
and agent exhausted.

**Two runs with the same inputs are exactly identical** in every stored value
at every step. The inputs are the starting state, the parameters, the step
size, the setting changes and the order of events. A slow computer reaches
each step later in real time but computes the same values. Playing a run
faster takes more whole steps per screen update and never a larger step, so a
case played at real time and at three hundred times real time gives exactly
the same results.

## 6. Parameters: values and sources

### 6.1 How sources are ranked

A citation records where a number was found. It does not say whether anything
was measured there. The project ranks sources in three tiers:

1. **Primary measurement.** A study that measured the quantity in the species,
   population and conditions that the model claims to represent, and reports
   the value, its dispersion and its reference conditions. An example is Strum
   and Eger's sevoflurane blood:gas measurement (0.686 ± 0.047 at 37 °C,
   n=19).
2. **Secondary synthesis.** A review, textbook, monograph or consensus
   document that collects primary measurements without making one, such as the
   textbook blood:gas coefficient of 1.4 for isoflurane.
3. **Reference implementation.** Another simulator's parameter set. Gas Man is
   this project's. Its set is complete and internally consistent, but it was
   assembled to make a program behave, and nobody can recover from the program
   which measurement each number descends from. A peer-reviewed paper that
   prints such a set is still tier 3.

Only a tier-1 source is an authority on its own. A tier-2 or tier-3 value may
be adopted when no primary measurement of that quantity in that population
exists, or when the value belongs to a set whose internal consistency is part
of what is modelled. In both cases the data file records the primary
measurements and how far the stored value sits from them.

**Of the 49 stored values, 27 are tier 1, four are tier 2, 16 are tier 3, and
two adopt no source.** The 16 tier-3 values all come from Gas Man: the three
blood:gas coefficients, ten of the eleven patient parameters, and the three
MAC values. The two unsourced values are the circuit volume and the default
fresh gas flow.

The two tier-3 citations are Gas Man simulation studies. Table 1 of De Wolf et
al. 2012 is the parameter set that the authors fed to Gas Man, and Weber et
al. 2021 describe the product's standard 70 kg patient. The two do not agree
on Gas Man's MAC: Weber et al. print 2.1% sevoflurane and 1.1% isoflurane, and
De Wolf et al. state 2.0% and 1.2%, which this simulator stores. Every
partition coefficient the two print is the same.

### 6.2 The agents

| Value | Sevoflurane | Isoflurane | Desflurane | Source and tier |
| --- | ---: | ---: | ---: | --- |
| Blood:gas partition coefficient | 0.65 | 1.3 | 0.42 | Gas Man, as De Wolf et al. 2012 Table 1 prints it (tier 3) |
| Vessel-rich tissue:gas | 1.1 | 2.1 | 0.54 | Yasuda, Targ and Eger 1989 (tier 1), as Gas Man's figures |
| Muscle tissue:gas | 2.4 | 4.5 | 0.97 | as above |
| Fat tissue:gas | 34.0 | 70.0 | 13.0 | as above |
| Vessel-rich tissue:blood (derived) | 1.6923 | 1.6154 | 1.2857 | tissue:gas ÷ blood:gas |
| Muscle tissue:blood (derived) | 3.6923 | 3.4615 | 2.3095 | tissue:gas ÷ blood:gas |
| Fat tissue:blood (derived) | 52.3077 | 53.8462 | 30.9524 | tissue:gas ÷ blood:gas |
| 1 MAC, 40-year-old adult (percent) | 2.0 | 1.2 | 6.0 | Gas Man, as De Wolf et al. 2012 state it (tier 3) |
| MAC-awake (fraction of 1 MAC) | 0.34 ± 0.05 | 0.31 ± 0.05 | 0.36 ± 0.063 | Katoh et al. 1993 for sevoflurane and isoflurane; Chortkoff et al. 1995 for desflurane (tier 1) |
| Maximum delivered concentration (percent) | 8.0 | 5.0 | 18.0 | Dräger Vapor 2000 specification; Kelly and Kong 2011; Johnston et al. 1994 on the Tec 6 (tier 1) |
| Molar mass (g/mol) | 200.05 | 184.49 | 168.04 | ChEMBL formula masses (tier 2, because a molar mass is computed from the formula) |
| Liquid density at 20 °C (g/mL, mean ± SD) | 1.5203 ± 0.0008 | 1.5019 ± 0.0006 | 1.4651 ± 0.0004 | Laster, Fang and Eger 1994 (tier 1) |

**Blood:gas.** Each agent's data file cites primary measurements beside the
stored tier-3 value and marks them as not adopted. Against the older
measurements (Strum and Eger 1987 for sevoflurane, Lerman et al. 1984 for
isoflurane, Eger 1987 for desflurane) the stored values are 5.2%, 11.0% and
0.9% low. Esper et al. 2015 measured all three in 120 surgical patients at 37
°C. Only its abstract was read. Against its means the stored values are 12.2%,
10.3% and 26.3% low. Desflurane's gap is the widest in the project, about 3.8
of Esper's standard deviations. Weber et al. note in their own Table 1 that Gas
Man's blood/gas coefficients "differ from them observed by Esper et al." The
Gas Man values were kept because all twelve partition coefficients then come
from one table, so the three agents can be compared directly.

**Tissue:gas.** All nine coefficients are Gas Man's figures for the human
measurements of Yasuda, Targ and Eger (1989). That
study measured all three agents in the same specimens, in one laboratory with
one technique, so a systematic error in the technique affects every agent
alike. The specimens were from 14 autopsies, 6 to 10 per tissue, with a mean
age of 65.8 ± 14.4 yr, equilibrated at 37 °C. Each cell below gives the stored
value, the paper's mean ± SD, and the difference in SDs.

| | Vessel-rich (Yasuda's brain) | Muscle | Fat |
| --- | ---: | ---: | ---: |
| Sevoflurane | 1.1 vs 1.15 ± 0.07 (−0.71 SD) | 2.4 vs 2.38 ± 1.03 (+0.02 SD) | 34.0 vs 34.0 ± 6.0 (exact) |
| Isoflurane | 2.1 vs 2.09 ± 0.10 (+0.10 SD) | 4.5 vs 4.40 ± 1.97 (+0.05 SD) | 70.0 vs 64.2 ± 12.3 (+0.47 SD) |
| Desflurane | 0.54 vs 0.54 ± 0.02 (exact) | 0.97 vs 0.94 ± 0.35 (+0.09 SD) | 13.0 vs 12.0 ± 2.0 (+0.50 SD) |

The vessel-rich coefficient is Yasuda's *brain* value (isoflurane's stored 2.1
against 2.09, desflurane's 0.54 against 0.54). A learner reading the
vessel-rich trace is reading a brain trace. Yasuda's paper measured no
blood:gas coefficient. Its tissue:blood figures divide the tissue:gas values
by published blood:gas values adjusted for the cohort's age, and those
blood:gas values are 4.9 to 9.4% above the three stored here.

**Maximum delivered concentration.** This is the calibrated dial maximum of
the vaporizers that each source names: the Dräger Vapor 2000 and Datex-Ohmeda
Sevotec 5 for sevoflurane, the Penlon Sigma Delta and Datex-Ohmeda Isotec 5
for isoflurane, and the Tec 6 for desflurane. It sets the top of the
delivered-concentration dial. It is a device limit. It is not a physiologic or
safety limit, and it says nothing about whether a concentration is appropriate
for a patient. Another desflurane vaporizer, or an injector that delivers into
the circle, is not bound by 18%.

**MAC.** The stored MAC is 1 MAC for a 40-year-old adult, with no adjustment
for age. No equation uses it. It sets the dial's starting position, so each
run opens at 1 MAC, and it is the divisor for every value shown in MAC
multiples. The simulator refuses any agent whose own vaporizer cannot deliver
its 1 MAC. § 8.2 gives what the stored MAC costs the display.

**MAC-awake.** Katoh et al. (1993) determined sevoflurane and isoflurane
MAC-awake by a slow, equilibrated washout and by a fast one. Slow washout gave
0.34 of MAC for sevoflurane and 0.31 for isoflurane, against 0.22 for both by
fast washout. Katoh attributes the disagreement to end-tidal-to-arterial and
arterial-to-cerebral differences, which this model represents as the gap
between the alveolar and vessel-rich traces. The stored values are the
slow-washout ones, and they belong against the vessel-rich trace. Katoh's brain
concentration at awakening during fast washout (0.30 and 0.26 of MAC with
arterial pressure set equal to end-tidal, 0.34 and 0.30 with a correction for
20% dead-space gas) was calculated from a one-compartment brain model and was
not measured. So the stored values, and the choice of the vessel-rich trace,
rest on a modelled estimate that agrees with an equilibrated measurement.

The three agents' fractions were not determined by one method. Katoh's
slow-washout arm is descending. Chortkoff et al. and Song et al. (2005)
determined
desflurane MAC-awake by ascending stepwise equilibration. All are equilibrated
determinations, so all three belong against the vessel-rich trace, but each
agent keeps its own value.

MAC-awake is stored as a fraction of MAC and never as a percent, because a
published percent is tied to the MAC of its own population. Chortkoff's
desflurane MAC-awake of 2.60% is 36% of a MAC of about 7.25%, the figure of
Rampil et al. (1991) for ages 18-30. Dividing 2.60% by the stored 6.0%
(Rampil's figure for ages 31-65) would give 0.433, and the band would be drawn
20% too high. At 0.36 of 6.0% the band's centre is 2.16%, and Song et al.
measured 2.17% in a population that Rampil's 31-65 year MAC describes.

### 6.3 The reference adult

| Parameter | Value | Unit |
| --- | ---: | --- |
| Reference patient weight | 70.0 | kg |
| Alveolar gas volume | 2.5 | L |
| Venous blood-pool volume | 1.222 | L |
| Vessel-rich tissue volume | 6.0 | L |
| Muscle tissue volume | 33.0 | L |
| Fat tissue volume | 14.5 | L |
| Vessel-rich flow fraction | 0.76 | dimensionless |
| Muscle flow fraction | 0.18 | dimensionless |
| Fat flow fraction | 0.06 | dimensionless |
| Default alveolar ventilation | 4.0 | L/min |
| Default cardiac output | 5.0 | L/min |

Ten of the eleven come from the Gas Man default patient (tier 3). The venous
pool is the eleventh.

**The reference patient adopts no primary source.** The longest chain behind it
runs Gas Man (tier 3) to Lowe and Ernst 1981 (tier 2) to ICRP Committee II 1960
(tier 2), and contains no measurement. The volumes and flows are the source's
absolute values for a 70 kg adult. They are not scaled from the weight, which
no equation uses, so changing the weight alone would change nothing.

**Five parameters have a measurement cited beside them and not adopted:**

- *Alveolar gas volume.* Hudgel and Devadatta (1984) measured FRC by helium
  dilution in ten healthy awake men. Read with Wahba's (1991) review of the
  roughly 20 percent reduction under general anesthesia, that brackets the
  stored volume.
- *Cardiac output.* Cattermole et al. (2017) measured a median of 5.51 L/min in
  686 subjects of 50 to 75 kg. The stored 5.0 L/min is 9.3 percent below it.
  Lowe and Ernst's relation, $`0.2M^{3/4}`$ for body mass $`M`$ in kg, gives
  4.84 L/min at 70 kg, and is derived and not measured.
- *Muscle volume.* Janssen et al.'s (2000) whole-body MRI gives a
  skeletal-muscle mass that appears to agree with the stored volume. The
  agreement is a coincidence, because those men averaged about 86 kg.
- *Fat flow fraction.* Heinonen et al.'s (2012) PET measurement of resting
  adipose perfusion is about half of what the stored fraction implies. This is
  the largest of the five gaps, and it changes the shape of a displayed curve
  (§ 10.8).
- *Muscle flow fraction.* Frayn and Karpe's (2014) review supplies the
  comparison. It shows that the fat gap concerns the absolute flow and not the
  muscle-to-fat ratio, which the stored fractions get right.

**The other six have no comparison.** The weight is a label. The default
alveolar ventilation is Gas Man's program default. The vessel-rich volume and
flow fraction and the fat volume each combine several tissues, and no single
measurement exists of what the model means by them. The venous pool is a
well-mixed volume and is not the physiologic venous blood volume, which is
several times larger.

**Venous pool, 1.222 L.** Davis and Mapleson (1981) state on p. 400 that for
models of inhaled anesthetics the venous pools may be combined, "in which case
it would be marginally more accurate to make ... the combined venous pool 1222
ml (23.6%)" of the blood volume of a 70 kg standard man. They derive it from
the ICRP (1975) blood distribution, so it is tier 2. It replaced Gas Man's
program default of 1.0 L. At 5.0 L/min of cardiac output, the mixed-venous time
constant is 14.7 s, against 12.0 s at 1.0 L.

### 6.4 The breathing circuit

| Parameter | Value | Unit |
| --- | ---: | --- |
| Breathing-circuit volume | 6.0 | L |
| Default fresh gas flow | 4.0 | L/min |

**Neither value adopts a source of any tier.**

**Circuit volume.** Gas Man's Workbook (p. 168) and De Wolf et al. 2012 both
give 8.0 L. No record gives a reason for 6.0 L. At the default flow the
circuit time constant, $`V_C/\dot V_F`$, is 90 s here and 120 s at 8.0 L, so
the apparatus lag is 25% shorter. That lag is the part of the inspired curve
that a learner is most likely to attribute to uptake. A run meant to reproduce
a published Gas Man trajectory has to set the volume to 8.0 L. The 6.0 L is an
assembled total, and no source divides it between apparatus and patient
circuit.

Machines in current use hold less. Shin et al. (2017) print apparatus volumes
of 4.7 L for a Dräger Primus, 2.1 L for a Perseus A500 and 2.0 L for a Zeus IE.
With the 1.2 L patient circuit they used, the assembled totals are 5.9, 3.3 and
3.2 L, without the 3 L reservoir bag. At the default flow the circuit time
constant therefore runs from 89 s to about 50 s, a factor of about 1.8 across
machines that a learner could meet in one department.

Volume is not the whole difference between machines. Fukuda et al. (2006)
moved only
the fresh gas inlet, with the machine and its volume fixed, and the
inspired-to-delivered ratio of isoflurane and sevoflurane rose significantly
at low flow. That ratio, $`F_I/F_D`$, is what
the circuit equation computes, and the model does not represent the layout of
a machine's internal gas paths.

**Default fresh gas flow.** The 4.0 L/min is a teaching default. It is not a
clinical recommendation and makes no claim about clinical practice. No
published counterpart exists in any source the project has reached. De Wolf et
al. used 1 L/min, and Weber et al. used 10 L/min for washout. At 4.0 L/min the
circuit time constant is 90 s: long enough for the machine lag to show as a
distinct phase of the early rise, and short enough to resolve within the first
minutes of a run. A default of 0.5 L/min would have no source either, and
would put the apparatus lag at 12 minutes.

## 7. Controls and their limits

### 7.1 The four controls

Four settings are the model's only inputs. Each can be changed during a run
without resetting the model's state.

| Control | Supported range (both ends included) |
| --- | --- |
| Fresh gas flow | 0 to 10 L/min |
| Delivered concentration | 0 to the maximum of the agent's vaporizer |
| Alveolar ventilation | 0 to 12 L/min |
| Cardiac output | 0 to 10 L/min |

A change affects transfers from the next step on. Changing the delivered
concentration does not alter the concentration already in the circuit.
Changing ventilation does not alter what the circuit or the alveoli already
hold. Changing cardiac output does not alter what blood or tissues already
hold, but it recalculates the tissue flows, $`Q_i = f_iQ`$.

The maxima for the three flows come from no source. Each is the edge of the
settings that the interface offers and that the model's checks cover.

**The simulator refuses a setting outside these ranges.** The model's results
have been compared with an independent calculation and with measured human
data only across them. Solved for a cardiac output of 1000 L/min, the
equations would give a precise answer to a question that physiology does not
ask, and nothing on the display would invite doubt.

**Fresh gas flow has a second limit: what the attached anesthesia machine can
deliver.** A machine can narrow the flows a run accepts and can never widen
them. The machine that ships with the simulator declares no deliverable range,
because no operator's manual or manufacturer specification giving one could be
obtained for any of the eight machines surveyed. No declared range means no
claim. It does not mean a machine known to be unlimited.

**Zero is a supported setting on every control.** A zero flow removes a
transfer term and divides nothing by zero. At $`Q=0`$ the tissue and venous
compartments stop changing, and the alveolar equation loses its uptake term.
The low end of each flow is also where the teaching is. Reducing cardiac
output accelerates alveolar wash-in, because less agent is carried away from
the lungs. With sevoflurane at 1 MAC and the other defaults, $`F_A/F_I`$ at
five minutes is 0.41 at 10 L/min, 0.49 at 5 L/min, 0.58 at 2.5 L/min, 0.70 at
1 L/min and 0.86 at zero. Zero alveolar ventilation is apnea.

A run at zero cardiac output shows where the agent goes when perfusion stops,
and nothing else. It does not model circulatory arrest, cardiopulmonary bypass
or ECMO, and nothing about a patient's condition follows from it.

The circuit volume and the alveolar gas volume are fixed parameters. Neither
is a control.

### 7.2 When a control change takes effect

A control change takes effect at the start of the next 0.1 s step, so its
timing is accurate to a tenth of a second and no better. A ventilator start
shifts the alveolar reading by up to 0.14 percentage points while its effect
settles. That is about twice the shift from one standard deviation of a
partition coefficient, which makes an abrupt ventilation change the one case
where the step adds more error than the parameters do. It is small beside
desflurane's 1 MAC of 6.0%. Keeping it within one standard deviation would
need a step near 0.05 s.

**Above 1× playback, a control change can wait longer than one step.** The
program computes a whole screen update's worth of steps at once, so a setting
changed during playback first acts at the next update, up to
`multiplier × 0.1` s later. The same slider moves made at two playback rates
are therefore different inputs and produce different runs. An ordinary dial
change costs far less than the worst abrupt maneuver: about 21 times less at
1×, 19 times at 20×, 16 times at 60× and about 7 times at 300×, where it
reaches 1.5 percentage points.

- Each recorded control change carries the simulated time at which it acted,
  so the record is exact to the step at every rate.
- An exact route exists at every rate: pause, change, resume. Use it to time a
  maneuver, and use faster playback to watch one.

### 7.3 Run length

**A run is supported for 24 hours of elapsed simulated time.** Past that
point the equations still solve exactly. What stops is the claim that the
solution represents a patient. The 24 hours belong to the case: a branch
taken at 23 h has one hour left.

Two omissions set the limit, and both are negligible over a case and not over
days:

- **Metabolism.** Sevoflurane constrains the limit, because 2% to 5% of the
  absorbed dose is metabolized, against far less for isoflurane and desflurane.
  Its metabolism begins immediately. Kharasch's review reports these figures
  and finds that metabolism "does not contribute to the termination of clinical
  drug effect" (Kharasch 1995). That holds while ventilation and perfusion
  dominate the trace, and becomes progressively false once only the slow tail
  is still moving.
- **The fat group's flow** (§ 10.8), which acts directly on the slow tail of
  washout.

The 24 hours are not inside the exposure range over which sevoflurane's
metabolism was measured. Kharasch's review covers 0.35 to 9.5 MAC-hours. A run
whose alveolar fraction is held near 1 MAC gains about one MAC-hour per hour,
so it leaves the measured range at about 9.5 hours and reaches about 24
MAC-hours at the limit. Counted at the dial, a run held at sevoflurane's 8%
maximum reaches at most about 96 MAC-hours. Past the measured range, even the
size of the omission is unmeasured.

Within the 24 hours, the washout tail already lacks its largest measured term
(§ 10.9).

**Volatile sedation in intensive care is out of scope.** It runs for days
through an anesthetic-conserving device, which is the regime in which this
model is wrong. Supporting it needs metabolism first.

## 8. Reading the display

### 8.1 Concentrations

The alveolar readout is labelled "Alveolar", with "end-tidal-equivalent"
below. It shows the concentration in the model's one well-mixed alveolar
compartment, which is the value a monitor's end-tidal reading estimates in a
patient. The model has no dead space, airway sampling delay or shunt, so the
readout is not a simulated end-tidal measurement.

No arterial concentration is displayed, because $`F_a \equiv F_A`$ and a
separate readout would show the alveolar number twice.

The percent unit is `% of 1 atm` and not `vol %`. Only the circuit and
alveolar compartments have a gas-phase volume fraction. The mixed-venous,
vessel-rich, muscle and fat compartments hold a partial pressure, which
convention quotes as a percent of one atmosphere.

**A compartment's concentration is not its amount.** With sevoflurane at a
1 MAC dial, fat holds a fifth of all the agent in the run at 60 minutes, at a
partial pressure of 0.03% of an atmosphere. Across the three agents at a 1 MAC
dial, fat holds a fifth of the stored agent at one hour and a third at three
hours, which the fat trace cannot show.

### 8.2 MAC multiples

$$
\text{MAC multiple} = \frac{100F}{\mathrm{MAC}_\%}
$$

The MAC multiple is a display unit only. The model does not:

- compute MAC-hours or an age-adjusted MAC, or sum MAC fractions across
  agents;
- model an effect-site compartment or any depth-of-anesthesia endpoint; or
- imply that an alveolar concentration equal to the stored MAC corresponds to
  any clinical state in a particular patient.

The display therefore shows a ratio to 1 MAC, written `×MAC`, and never a
depth.

**What a MAC multiple means depends on the compartment.** MAC is defined for
the alveolar (end-tidal) concentration at one atmosphere in a nominal
40-year-old, as the population ED50 for immobility in response to a
standardized surgical stimulus.

- On the **alveolar** compartment, a MAC multiple has its conventional
  meaning, subject to the limits below.
- On the **circuit, mixed-venous, vessel-rich, muscle and fat** compartments,
  it means only that the compartment's partial pressure is N times the
  alveolar partial pressure that would be 1 MAC. It does not mean that the
  patient is at N MAC of anesthetic depth.

Three limits apply to every compartment:

1. MAC falls about 6% per decade of age (Mapleson 1996), and the reference
   adult has no age.
2. The MAC multiples of co-administered agents add, and the model runs one
   agent at a time.
3. Opioids, temperature and patient factors modify MAC, and the model
   represents none of them.

**The stored MACs differ from Mapleson's, and the difference distorts a
comparison of sevoflurane with desflurane.** Mapleson's meta-analysis gives
values for age 40 with 95% confidence limits of about ±7% (±10% for
desflurane).

| Agent | Stored MAC | Mapleson age-40 | Displayed MAC multiples read |
| --- | --- | --- | --- |
| Sevoflurane | 2.0% | 1.80% | 10% low |
| Isoflurane | 1.2% | 1.17% | 2.5% low |
| Desflurane | 6.0% | 6.6% | 10% high |

The errors run in opposite directions for sevoflurane and desflurane, so a
comparison of the two in MAC multiples differs by about 22% between the stored
MACs and Mapleson's. That is larger than either source's confidence limits, so
by the primary literature two agents at "1 MAC" are not equipotent to that
precision. The shift is constant within an agent and changes no curve's shape
or timing. The interface displays the divisor, so a reader can compare it with
the value they would use.

### 8.3 The MAC-awake band and the 1 MAC line

The compartment chart carries two horizontal references for the agent in use.
A **band** marks MAC-awake, the concentration at which half of a population
responds to verbal command. A **line** marks the nominal 1 MAC. Neither is
modelled. Both are published constants drawn on the chart's percent axis.

The gap between them shows the decrement required for arousal. Chortkoff et
al. state that "along with pharmacokinetics, the ratio of the awakening
concentration to the anesthetizing concentration (MAC-awake/MAC) determines
time to awakening".

**The band spans one standard deviation either side of the published mean.**
It covers roughly the middle two thirds of a population. It is not a
prediction for the patient on the screen, and the interface shows no
time-to-wake-up figure of any kind.

**Read the band against the vessel-rich trace.** The model has no effect-site
compartment, so the alveolar trace is the fastest curve on the chart and the
furthest from where responsiveness returns. In one simulation, sevoflurane ran
for 3 hours at the opening dial of 2.0% and 4 L/min of fresh gas, which
brought the alveolar fraction to 1.69%, or 0.84 MAC. The vaporizer was then
turned off and the fresh gas flow raised to 10 L/min. The alveolar trace
crossed the band's center at 2.86 min and the vessel-rich trace at 6.55 min,
2.29 times later.

**At a 1 MAC dial, no patient trace reaches the 1 MAC line, however long the
case runs.** Muscle and fat keep taking up agent for many hours, so the blood
returning to the lungs stays below alveolar gas. That keeps the alveolar
fraction below the inspired fraction, and rebreathing keeps the inspired
fraction below the dial. This happens in real patients too.

**Three misreadings of the band all make emergence look faster than the model
says:**

1. reading the band against the alveolar trace;
2. using a slow-washout MAC-awake value against a fast-washout alveolar trace,
   where 0.22 would be the matching figure;
3. dividing a published MAC-awake percent by a MAC other than the one its
   population was measured against.

A learner who takes away any of these carries into practice the belief that a
patient is more awake than they are.

**The stored MAC is a fourth source of error in the band's height.** The
traces are absolute partial pressures and do not depend on MAC, so wherever
the stored MAC departs from the literature, the band moves against the traces
in proportion. Against Mapleson's age-40 values, the stored MAC is 11.1% high
for sevoflurane, 2.6% high for isoflurane and 9.1% low for desflurane. Only
sevoflurane's gap is larger than Mapleson's confidence limits, so the
sevoflurane band probably sits about 11% too high, and a band drawn too high
teaches an earlier wake-up. In the washout run above, the vessel-rich trace
crosses the drawn center of 0.68% at 6.55 min, and crosses 0.612%, the same
fraction of Mapleson's 1.80%, at 7.30 min. Katoh's own age-adjusted MAC
(2.56 − 0.0156 × age percent for sevoflurane, 1.43 − 0.0061 × age for
isoflurane) gives 1.94% and 1.19% at age 40. The stored MAC is 3.3% and 1.2%
above those. The drawn centers are 0.68% and 0.372%, against 0.658% and
0.368%. Both differences are much less than the standard deviation of Katoh's
fractions, 0.05 of MAC.

### 8.4 The $`F_A/F_I`$ plot

A second plot draws the modelled alveolar fraction divided by the modelled
inspired fraction, on a fixed axis from 0 to 1. The uptake literature is
taught from this curve, so the plot can be laid beside a published figure.

- **The ratio is a modelled value.** It has the alveolar compartment's limits:
  no airway sampling delay and no dead space. It is not a depth of anesthesia,
  a time to any endpoint, or a prediction for a patient.
- **The denominator is the modelled inspired concentration and not the
  vaporizer dial.** The circuit approaches the delivered concentration only
  over its own time constant, so early in a run the two differ substantially.
- **The curve is the textbook wash-in curve only while the inspired
  concentration is held constant.** If the vaporizer setting or the fresh gas
  flow changes mid-run, a rise across the change shows the setting moving and
  does not show uptake slowing. The plot carries marks where each setting
  changed.
- The ratio is shown to two decimals. Yasuda et al. (1991a, 1991b) report
  0.850, 0.733 and 0.90 with standard deviations of 0.018, 0.027 and 0.01, so a
  third decimal would be finer than that spread.

### 8.5 Precision

| Quantity | Displayed to |
| --- | --- |
| Concentrations and the delivered dial | 0.01 percentage points |
| MAC multiple | 0.01 MAC (0.02 percentage points of sevoflurane, 0.012 of isoflurane, 0.06 of desflurane) |
| Simulated time | 0.1 s, one step |
| Fresh gas flow, alveolar ventilation, cardiac output | 0.1 L/min |
| Agent amounts | 0.1 L of equivalent pure agent gas |

A positive concentration that would round to `0.00%` is displayed as
`<0.01%`, so `0.00%` means that no agent has arrived. Each slider moves in
steps of its display resolution, so the value applied to the model is exactly
the value printed beside the control. Amounts are labelled as litres of
equivalent pure agent gas, because a bare "L" beside an anesthetic invites a
reader to take it as litres of liquid.

**Each digit shown is accurate for this model with its parameters. No
displayed value can be trusted to its last digit as a prediction about a
patient.** Within a run the simulation resolves about nine decimal places more
than the readout shows. How finely the model resolves a concentration in a
patient is much coarser. One standard deviation of a partition coefficient
moves a reading, at worst over the first 3600 s, by:

| Coefficient changed by one SD | Change in the reading |
| --- | --- |
| Fat tissue:gas | 0.00087 to 0.0067 percentage points |
| Blood:gas | 0.015 to 0.054 percentage points |
| Vessel-rich tissue:gas | 0.013 to 0.050 percentage points |
| Muscle tissue:gas | 0.013 to 0.068 percentage points |

A reader can rely on which of two compartments the readouts show as higher,
except possibly while the two cross. A gap worked out from two readings can
differ from the true gap by up to one count of the last displayed digit.

### 8.6 Comparing two runs

A comparison shows two managements of one case. The first run is the
**trunk**. A **branch** continues it in another way from an instant the trunk
passed through, the **fork**.

Before the fork, the two runs are exactly equal. After it, a difference
between them is caused by the settings that differ and by nothing else in the
model. Both runs share the patient, the agent, the equations and parameters,
the circuit volume, the step, every setting up to the fork, and the time
frame, which counts from induction. The difference does not come from
rounding, the playback rate or the computer.

**A comparison can teach only the mechanism:** which way a curve moves when
one thing changes, why, and roughly how fast. It does not say what the
difference means for a patient.

- **The model has one patient and no variability around it.** No equation
  takes weight, age, sex or body composition. The two runs are two
  trajectories of one modelled patient. They are not two patients, two samples
  from a population, or a range. The difference carries no interval, because
  the model contains nothing that could supply one.
- **A branch that differs in cardiac output is still not a second patient.** A
  patient who differs in cardiac output differs in compartment volumes too,
  and the model keeps those fixed. Changing cardiac output alone shifts every
  tissue time constant, $`V_i \lambda_{i:b} / Q_i`$, in a direction that flow
  and volume changing together need not take.
- **Do not read a comparison as "low flow woke this patient twelve minutes
  sooner."** There is no "this patient". The model has no measure of
  responsiveness in which two runs could differ, so nothing "woke". And the
  model does not claim to get a difference in emergence time right to the
  minute.

## 9. How the model compares with measurements in people

The model's arithmetic is checked against exact and independent solutions of
its own equations. Those checks show that it solves the equations correctly.
They do not show that the equations describe a patient. The comparisons below
are the only ones against published human measurements.

**For most stored values, passing these comparisons rules out only large
errors.** A pass does rule out a model whose structure is wrong.

### 9.1 Wash-in at 30 minutes: agrees

Yasuda et al. published $`F_A/F_I`$ at 30 minutes for all three agents in two
volunteer studies: Yasuda et al. 1991a, in *Anesth Analg*, and Yasuda et al.
1991b, in *Anesthesiology*. The sections below name each paper by its journal.
The figures are mean ± SD, read from the two abstracts.

| Agent | $`F_A/F_I`$ at 30 min | Cohort | Published $`F_I`$ | Source |
| --- | --- | --- | --- | --- |
| Sevoflurane | 0.850 ± 0.018 | n=7 | 1.0% | *Anesth Analg* 1991 |
| Isoflurane | 0.733 ± 0.027 | n=7 | 0.6% | *Anesth Analg* 1991 |
| Desflurane | 0.90 ± 0.01 | n=8 | 2.0% | *Anesthesiology* 1991 |
| Isoflurane | 0.73 ± 0.03 | n=8 | 0.4% | *Anesthesiology* 1991 |

The model lands inside the published standard deviation for every row, and
reproduces the ordering by solubility (desflurane above sevoflurane above
isoflurane). It does so at every fresh gas flow from 1 to 10 L/min.

- **The settings were not fitted.** Alveolar ventilation and cardiac output
  are the shipped defaults, 4.0 and 5.0 L/min, fixed before the comparison
  existed. The agreement is sensitive to both. A change of 1 L/min of alveolar
  ventilation either way puts all three agents outside their published spread,
  and 1 L/min of cardiac output moves every agent by more than one SD.
- **One standard deviation tests a plausible individual, not the cohort
  mean.** The standard error of the mean is 2.6 to 2.8 times narrower.
  Desflurane's wash-in sits at +0.79 SD, which is +2.2 SEM. A passing wash-in
  must not be restated as "reproduces the published mean".

### 9.2 The first 25 minutes of wash-in

Compared point by point with the published curves, with $`F_I`$ held fixed
from the first breath as the studies' non-rebreathing circuits held it (which
no setting of the simulator does), the model sits this far from each published
mean:

| Cohort | 1 to 3 min | 5 min | 7.5 to 25 min |
| --- | --- | --- | --- |
| Sevoflurane, n=7 | −0.54 to −0.69 SD | −0.22 SD | +0.48 to +0.77 SD |
| Isoflurane, n=7 | −0.70 to −0.83 SD | −0.19 SD | +0.34 to +0.76 SD |
| Isoflurane, n=8 | −0.60 to −0.67 SD | +0.08 SD | +0.32 to +1.06 SD |
| Desflurane, n=8 | +1.79 to +1.82 SD | +1.82 SD | +2.10 SD at 10 min, then +0.94 to +0.28 SD |

Sevoflurane and isoflurane follow the published curves within one SD. Their
only point beyond it is isoflurane at 12.5 minutes, +1.06 SD, which is within
a reading error of one SD.

**Desflurane rises faster than its cohort.** Its $`F_A/F_I`$ runs 0.034 to
0.042 above the published curve from 1 to 10 minutes and agrees from 12.5
minutes on. The cause is probably something only desflurane has, because the
same eight volunteers breathed isoflurane from the same cylinder and the model
follows their isoflurane curve. No single stored coefficient, varied within
its measured range, closes the gap. Blood:gas brings the early points within
one SD at about 0.55 or higher, where Eger's 0.424 ± 0.024 does not reach and
Esper et al.'s 0.57 ± 0.04 does. But the 30-minute ratio stays within one SD
at every flow only while blood:gas is about 0.46 or lower. At 0.57 it falls
outside at every flow, from −1.35 SD at 10 L/min to −2.61 SD at 1 L/min. The
vessel-rich and muscle coefficients cannot close the gap at any value within
Yasuda, Targ and Eger's measurements (brain 0.54 ± 0.02, muscle 0.94 ± 0.35).

### 9.3 Elimination at five minutes: does not agree

The same volunteers gave $`F_A/F_{A0}`$ after five minutes of elimination,
where $`F_{A0}`$ is the last alveolar fraction of the 30-minute
administration. At the default settings and 10 L/min of fresh gas, the model
holds more alveolar agent at five minutes than every cohort did.

| Agent | Cohort | Published | Model as shipped | Model with rebreathing removed |
| --- | --- | --- | --- | --- |
| Sevoflurane | n=7 | 0.157 ± 0.020 | 0.2328, +3.79 SD | 0.1541, −0.15 SD |
| Isoflurane | n=7 | 0.223 ± 0.024 | 0.3227, +4.15 SD | 0.2388, +0.66 SD |
| Desflurane | n=8 | 0.14 ± 0.02 | 0.1626, +1.13 SD | 0.0935, −2.33 SD |
| Isoflurane | n=8 | 0.22 ± 0.02 | 0.3227, +5.13 SD | 0.2388, +0.94 SD |

**Most of the gap is the breathing system.** $`F_A/F_I`$ has the inspired
fraction in its denominator, so whatever a breathing system does to $`F_I`$
divides out. $`F_A/F_{A0}`$ has no such term, so agent that returns to the
alveoli from the circuit counts as though it had come out of the patient. The
model always rebreathes. During elimination its $`F_I`$ settles near
$`\dot V_A/(\dot V_A + \dot V_F)`$ of $`F_A`$, which is 0.29 at the highest
supported flow (0.30 to 0.32 in the run). The studies did not rebreathe. Each
gave the agents through a non-rebreathing circuit and exchanged it for a fresh
one at exactly 30 minutes (*Anesth Analg* p. 317, *Anesthesiology* p. 490).
Neither paper states the inspired fraction during elimination, so a fraction
at or near zero is inferred.

**The last column exists only as a diagnostic. No fresh gas flow, dial
position or patient setting of the simulator produces it.** With the
rebreathing removed, three of the four cohorts land inside the published
spread, so the model's tissue return does reproduce a human elimination once
the breathing systems are matched. With the circuit in place, the elimination
moves by 11.5 to 21.6 SD between 1 and 10 L/min of fresh gas. Neither column
validates the elimination that a user watches, which is the rebreathing one.

**Desflurane then washes out 2.33 SD too fast.** This is the one comparison
against a human measurement that fails in the direction that overstates
recovery. A learner who took desflurane's early washout as a physiologic
prediction would expect a faster fall than Yasuda's volunteers showed. No
parameter value that the human measurements support closes the gap. Raising
blood:gas to 0.57 moves it only from −2.33 SD to −1.97 SD. The cause is not
identified, and the disagreement is left uncorrected.

### 9.4 Four caveats that go with any statement of these results

1. **The volunteers were breathing nitrous oxide.** Both protocols ran 65 to
   70% N₂O with the potent agents, so the measured curves carry a second-gas
   effect that the model cannot reproduce. The volunteers had breathed 70%
   nitrous oxide for 30 minutes before the potent agents started, so their
   nitrous oxide uptake was already low and the effect was probably small. Its
   size was not measured.
2. **The parameters descend from the same lineage as the measurements.** These
   are Gas Man parameters, derived to reproduce Eger's data. A pass shows that
   the implementation reproduces the intent of its parameter set. It does not
   show that the set is independently right, which is weaker than "validated
   against a human measurement".
3. **The breathing systems differ**, by 3.5 to 4.2 published standard
   deviations per cohort at five minutes of elimination.
4. **The model has no metabolism and no fourth compartment.** Neither matters
   over five minutes. The papers report recovery of the agent taken up as
   101 ± 7% for sevoflurane and 101 ± 6% for isoflurane in the first study,
   and 105 ± 25% for desflurane and 102 ± 13% for isoflurane in the second.
   Halothane gave 64 ± 9%, so the method does detect a metabolized agent. At
   five minutes the fourth compartment's term is about one part in twenty of
   what remains.

### 9.5 What these comparisons can and cannot detect

- For sevoflurane and isoflurane, they detect an error of 1% to 15% in either
  direction in blood:gas and in the vessel-rich group.
- They detect an alveolar gas volume that is too large. A volume a fifth to a
  third larger takes the first minute of wash-in outside one SD for every
  agent. Doubling it moves sevoflurane's 1-minute $`F_A/F_I`$ from 0.537 to
  0.429, which is −2.85 SD. They do not detect a smaller volume for
  sevoflurane.
- **They detect no change at all in fat for sevoflurane or isoflurane.** Fat
  solubility and fat volume set the hours-long tail of washout, from which a
  learner judges emergence, and nothing checks them against a measurement.
- They constrain muscle only loosely.
- They do not detect a smaller circuit for sevoflurane or isoflurane, down to
  a tenth of the stored value.

### 9.6 The first 24 hours of elimination

This comparison measures an omission and claims no agreement. Against the
curves fitted to the volunteers' washout, the shipped model's alveolar tail:

- sits above the fitted curve at five minutes;
- falls below it from 6 to 13 minutes until 0.8 to 2.0 hours, by 15 to 44% at
  the widest, around 15 to 25 minutes;
- runs above it until 3.4 hours for desflurane and 6.9 to 8.4 hours for the
  others, by 12 to 52% at the widest;
- runs below it until 15.3 hours for desflurane and 20.7 to 21.8 hours for the
  others, by a third at the widest near 13 hours, and by a half for desflurane
  near 8 hours; and
- finishes above it, by 12 to 24% at 23.5 hours and by a factor of 2.1 for
  desflurane.

In every fitted curve, a fourth compartment that the model lacks carries the
largest term over most of the middle stretch (§ 10.9). Until the seventh hour
the rebreathing circuit and the muscle group's slow return hold the shipped
tail above the curve. With the rebreathing removed, the model's tissue return
alone is a third to a half of the mean curve between hours 8 and 13.

Two limits apply to those figures:

1. **The fitted curve runs above the measured mean where the two can be
   compared.** At five minutes the fitted values are 0.194, 0.243, 0.147 and
   0.228, which are 1.84, 0.83, 0.33 and 0.39 published SD (3.5 to 24%) above
   the measured means. So every ratio above understates the model against the
   volunteers' mean. No measured mean was taken at the later times to correct
   against.
2. **The fourth compartment's term is as uncertain between subjects as it is
   large.** The SDs of its amplitude are 59 to 112% of the means. A tail a
   third to a half below the mean curve over those hours is inside the spread
   of the volunteers' own curves. The direction is settled, and the size is
   known to about a factor of two.

**What a learner sees of this.** At a 1% dial, the alveolar trace falls below
the readouts' 0.01 percentage points at 2.8, 4.2 and 1.9 hours for
sevoflurane, isoflurane and desflurane, before the stretch over which it runs
below the measured mean. A higher dial keeps the trace readable for longer. A
6% desflurane dial keeps it there until about the fifth hour, which is inside
desflurane's stretch. So a learner who runs a case long can reach the
shortfall.

### 9.7 Gas Man in patients

The model's parameters and compartment structure descend from Gas Man. A
prospective study measured how closely Gas Man tracks end-expired sevoflurane
in patients (Candries, De Wolf and Hendrickx 2022; abstract read). Twenty-eight
ASA I-II adults having gynecologic or urologic surgery were maintained on
sevoflurane in O₂/air, fourteen on a Dräger Zeus and fourteen on a Getinge
FLOW-i. Fresh gas flow was re-randomised every fifteen minutes over 0.2 to 6
L/min. Each case was re-run in Gas Man with the patient's weight and the same
flows, vaporizer settings and minute ventilation, and with cardiac output at
the Gas Man default. Over the whole hour Gas Man tracked both workstations to
within 10% on both measures, with a drift of −0.96%/h [−1.14, −0.88] on the
FLOW-i and −0.57%/h [−0.85, −0.16] on the Zeus. By phase:

| Workstation | Phase | Median performance error | Median absolute performance error |
| --- | --- | --- | --- |
| FLOW-i (n = 14) | wash-in, 0-15 min | 18% [1, 51] | 21% [8, 51] |
| FLOW-i (n = 14) | maintenance, 15-60 min | 0% [−7, 5] | 6% [2, 10] |
| Zeus (n = 14) | wash-in, 0-15 min | 7% [−6, 28] | 13% [6, 32] |
| Zeus (n = 14) | maintenance, 15-60 min | −1% [−5, 5] | 5% [2, 9] |

The brackets are interquartile ranges. A quarter of FLOW-i patients were
tracked worse than 51% through the first fifteen minutes, against worse than
10% over the last forty-five. The authors conclude that Gas Man predicts
end-expired sevoflurane "with better relative performance for simulating
maintenance than wash-in".

The study measures Gas Man and not this implementation, and nothing in this
project has been compared with a Gas Man trajectory. It bounds what Gas Man's
lineage is worth in patients, and it is worth least in the phase the simulator
displays most: the first minutes of the $`F_A/F_I`$ rise. "Agrees with Gas
Man" may not be read as "agrees with a patient" anywhere in a case, and least
of all in the first fifteen minutes.

The gap is not necessarily the patient model's. The two workstations differ in
how they deliver agent into the circle, and their wash-in median absolute
errors differ by a factor of about 1.6, with overlapping interquartile ranges
in different patients. A percentage error is also most sensitive when its
denominator is small and rising, which is the condition of wash-in. The study
does not separate these.

## 10. Limitations that can change what a displayed value means

### 10.1 What the model does not represent

- a separate arterial blood-mixing compartment;
- lung tissue and pulmonary blood (§ 10.5);
- a vessel-poor tissue group (§ 2);
- halothane, enflurane, ether or xenon;
- nitrous oxide, simultaneous gases, and concentration or second-gas effects
  (§ 10.2);
- absorption of agent by the circuit's plastics and rubber (§ 10.4);
- vaporizer interlocks, switching between volatile agents, direct anesthetic
  injection, and automated end-tidal control;
- closed-circuit operation, or any machine mode that shuts the surplus gas
  valve (§ 10.3);
- dead space and airway sampling delay (§ 10.6);
- multiple alveolar units, shunt and ventilation-perfusion mismatch;
- diffusion-limited exchange, in the lung or in a tissue group;
- intertissue diffusion, which is agent passing directly from a lean tissue
  into fat lying against it (§ 10.9);
- uncertainty in the tissue:gas partition coefficients (§ 10.10);
- metabolism, compound A and other degradation products;
- renal or hepatic dysfunction, cardiopulmonary bypass, ECMO and hypothermia;
- alveolar humidification (§ 10.12);
- the difference between ambient and body conditions (§ 3);
- altitude, or any ambient pressure other than 760 mmHg (§ 10.13);
- age-dependent MAC, and individual variation in awakening concentration;
- anesthetic potency, BIS or hypnosis, nociceptive response and hemodynamic
  response;
- IV anesthetics and effect-site models;
- clinical alarms, dosing recommendations and patient-specific predictions.

### 10.2 Nitrous oxide and the fixed alveolar volume

Nitrous oxide, simultaneous gases, and the concentration and second-gas
effects are one constraint: the alveolar volume is constant. The table
compares pulmonary uptake with alveolar ventilation early in induction, when
$`F_v \approx 0`$, for the reference adult.

| Gas | $`\lambda_{b:g}`$ | $`F_A - F_v`$ | $`\dot M_{\mathrm{pulmonary}}`$ | Of $`\dot V_A`$ |
| --- | --- | --- | --- | --- |
| Sevoflurane at 2% | 0.65 | 0.02 | 0.065 L/min | 1.6% |
| Nitrous oxide at 70% | 0.47 | 0.50 | 1.18 L/min | 29% |

For sevoflurane, uptake removes 1.6% of the volume that ventilation brings
into the alveoli, and a fixed volume can ignore that. For nitrous oxide it
removes 29%, and that removal is the concentration effect: the gas left behind
is concentrated, and inspired gas is drawn in to replace the volume. Adding
nitrous oxide without lifting the constraint would give an $`F_A`$ curve that
looks plausible and is wrong by tens of percent through induction.

### 10.3 Low flow and the closed circuit

**The model's exhaust vents whenever fresh gas flows, at exactly the fresh-gas
rate.** Both gas compartments have fixed volumes and the modeled patient takes
up no net volume, so every litre admitted has to leave.

**A real circle spills less than it is given**, by the volume the patient
removes: the oxygen consumed, the vapor taken up, and any nitrous oxide. The
gap is an absolute rate, so it is small where the flow is large and is the
whole of the model's spill where the flow is small. For the reference adult it
is on the order of 0.3 L/min early in a case. About 240 ml/min of that is
oxygen, from the $`10M^{3/4}`$ relation on page 17 of Lowe and Ernst (1981),
which is
Brody's interspecies metabolic relation and not a measurement in an
anesthetized adult. The rest is the 65 ml/min of sevoflurane vapor that the
model computes early in induction. At the opening fresh gas flow of 4.0 L/min,
the gap is 6 to 8% of the flow. At 0.5 L/min, which the simulator also allows,
it is half or more.

**Closed-circuit technique is not modeled, nor is a machine mode that shuts
the surplus gas valve.** Meyer et al. describe one: "In the automatic
controlled mode of the Zeus anesthesia machine, the surplus gas valve can be
closed to prevent any loss of gas volume" (Meyer et al. 2008). With
the valve shut, two things change that the model cannot follow. The agent that
the model counts as exhausted is instead carried into the alveoli and kept.
And the fresh gas flow stops being a setting and becomes the patient's total
uptake, which the model cannot compute because it does not track oxygen.

### 10.4 Absorption by the circuit

The modeled circuit's walls hold no agent. Targ, Yasuda and Eger (1989)
measured what a real circuit holds. Their
Table 1 gives plastic/gas and rubber/gas partition coefficients after 6 to 9
weeks' equilibration:

| Component | Desflurane | Sevoflurane | Isoflurane | Halothane |
| --- | ---: | ---: | ---: | ---: |
| Y-piece (polypropylene) | 6.67 | 7.68 | 10.6 | 19.1 |
| Circuit tube (polyethylene) | 16.2 | 31.2 | 57.9 | 128 |
| Reservoir bag (latex) | 19.3 | 29.1 | 48.9 | 190 |
| Bellows (black rubber) | 10.4 | 22.6 | 42.9 | 199 |
| Endotracheal tube (PVC) | 34.7 | 68.5 | 114 | 233 |
| Mask pad (PVC) | 51.7 | 104 | 170 | 323 |

The ranking held at every equilibration time from 7.5 min to 9 weeks, so the
inert circuit is most nearly true for desflurane. In a real circuit at 0.5 to
5 L/min, desflurane's wash-in and washout "closely approximated the maximal
possible theoretical rates", while the more soluble agents lagged. The authors
conclude that for desflurane this absorption "should not hinder induction of
or recovery from anesthesia". The coefficients overstate the effect during a
case, because equilibration is nowhere near complete in the hours an
anesthetic lasts. What the model cannot show is the early lag that a real
circuit adds for sevoflurane and isoflurane.

### 10.5 Lung tissue and pulmonary blood

Together these are an omitted store worth about a fifth of the fast pool. On
round figures (1 kg of lung tissue with a tissue:blood ratio of 1.2, and 1.8 L
of pulmonary and arterial blood), it is 20.1% of desflurane's fast pool, 19.7%
of sevoflurane's and 23.4% of isoflurane's. It takes up agent in the first
minutes of wash-in and equilibrates within about thirty minutes, so it barely
changes $`F_A/F_I`$ at 30 minutes. It acts mainly early in an elimination.

### 10.6 Dead space

The model ventilates the alveolar compartment continuously, with no separate
breaths and no anatomic or apparatus dead space. A series dead space is
exactly equivalent to a reduction in alveolar ventilation: a dead space
$`V_D`$ at respiratory rate $`f`$ acts as an alveolar ventilation of
$`\dot V_A - V_D f`$. The alveolar ventilation control is therefore already
the dead-space control, provided the value entered is a true alveolar
ventilation. **A minute ventilation entered there overstates gas exchange by
the whole of the dead space.** What the model cannot represent is unequal
ventilation-perfusion ratios across alveolar units, which no single
ventilation figure reproduces.

### 10.7 Cardiac output and flow distribution are fixed

Cardiac output is a control, and nothing else changes it. The three perfusion
fractions are constant for a whole run. A volatile anesthetic is itself a
cardiovascular depressant, so the model holds fixed the quantities its own
subject acts on. A flow that fell under anesthesia would lengthen every
tissue's time constant, $`\tau_i = V_i\lambda_{i:b}/Q_i`$. The learner can
move cardiac output and watch: a higher output carries more agent away from
the lung, stores more of it and slows the rise of $`F_A`$. The automatic
coupling from the agent to the flow is absent, and the reader has to supply
it.

### 10.8 The fat group's blood flow

The stored fat flow fraction implies 2.07 mL of blood per 100 mL of fat per
minute: 0.06 of the 5.0 L/min default cardiac output, flowing into 14.5 L. Two
human sources disagree about which way that errs.

- Heinonen et al. (2012) measured resting subcutaneous adipose perfusion in
  the thigh of six healthy young women by PET. Their figure is close to half
  of what the stored fraction implies.
- The two Yasuda 1991 papers fitted five compartments to each volunteer's
  washout and read the slowest as fat. They estimate its flow as 2.4 ± 0.6 and
  2.2 ± 0.5 mL per 100 mL per minute for sevoflurane and isoflurane (*Anesth
  Analg* Table 5, p. 322), and 2.1 ± 0.4 and 2.2 ± 0.2 for desflurane and
  isoflurane (*Anesthesiology* Table 5, p. 496), at the fat:blood coefficients
  of Yasuda, Targ and Eger (1989). At this model's stored fat solubilities,
  their fitted time constants give 2.5, 2.5, 2.3 and 2.6.

Read as evidence about the fat group's flow, the PET measurement puts the
stored figure at about twice the truth, and the washout fits put it at or a
little below the truth. Neither settles it. The PET figure is one depot in one
small cohort, awake and at rest, set against a whole-body compartment whose
depots differ (Frayn and Karpe 2014). The fitted compartment is fat only by
the authors' assignment. Its volume is a third to two fifths of the fat this
model stores, and the analysis "only accounts for about 25 L of the body
volume" (*Anesth Analg* p. 323). The PET measurement is not adopted.

The fat group's time constant is long compared with any simulated case
whichever is right, so no displayed curve reaches a wrong endpoint. What moves
with the flow is how much agent fat has taken up by the end of a case, which
sets the slow tail of washout, and it moves by up to about a factor of two. **A
learner who reads the fat trace as a physiologic prediction should treat its
fat loading as uncertain by about that much, in an unsettled direction.**

### 10.9 Intertissue diffusion: the missing fourth compartment

Fat fills here only through its own blood supply. Human washout finds a
second, faster fat-like store. Gas Man omits it too: "Inter-tissue diffusion
may occur between fat and muscle; this effect has been ignored in the Gas Man
model" (Workbook, Appendix B, p. 170). Carpenter et al. needed a fifth
compartment to fit human washout in 27 of 36 data sets, with a time constant
that "lies between the time constants predicted for muscle and fat"
(Carpenter et al. 1986). Both Yasuda papers found five compartments
in every washout they fitted, and interpreted the fourth as "a layer of fat
that receives anesthetic from adjacent vessel-rich organs by intertissue
diffusion" (*Anesth Analg* p. 320, *Anesthesiology* p. 493). Their time
constants and estimated volumes (Tables 4 and 5 of each paper, mean ± SD),
beside this model's fat group at the default cardiac output:

| Cohort | Fourth compartment: time constant (min) | Fourth compartment: volume (L) | Fat group: time constant (min) | Fat group: volume (L) | This model's fat group: time constant (min) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sevoflurane, *Anesth Analg* 1991 | 377 ± 123 | 2.5 ± 0.6 | 2,120 ± 690 | 4.1 ± 3.0 | 2,528 |
| Isoflurane, *Anesth Analg* 1991 | 383 ± 119 | 3.0 ± 0.7 | 2,130 ± 680 | 5.1 ± 4.1 | 2,603 |
| Isoflurane, *Anesthesiology* 1991 | 435 ± 131 | 5 ± 2 | 2,090 ± 230 | 6 ± 3 | 2,603 |
| Desflurane, *Anesthesiology* 1991 | 273 ± 88 | 6 ± 3 | 1,340 ± 230 | 5 ± 3 | 1,496 |

The model's fat trace is the fitted fat group. Its time constant is within one
standard deviation of the fitted one in three cohorts and 2.2 standard
deviations above it in the fourth. It is 5.5 to 6.8 times the fourth
compartment's. The muscle group equilibrates in 85 to 135 minutes, so nothing
in the model has a time constant on the fourth compartment's scale. Leaving it
out biases four things:

- **Fat holds too little agent.** If the fourth compartment is fat at the
  model's stored fat solubility, then over any case from half an hour to four
  hours it takes up 0.9 to 2.2 times as much agent as the model's whole fat
  group, or 2.6 to 5.6 times as much as the studies' fitted fat group. The
  missing store is as large as the modelled fat group's uptake, or larger.
- **The fat trace shows only the slowly filling fat.** Fat lying against
  well-perfused tissue runs at four to six and a half times the trace's
  partial pressure throughout such a case. After an hour it is at 13 to 20% of
  arterial, against the trace's 2.3 to 3.9%.
- **The late washout loses its largest measured term.** After a 30-minute
  administration, the fourth compartment's term becomes the largest in the
  measured washout at 1.8 to 3.1 hours and stays the largest until 20.7 to
  29.4 hours. § 9.6 gives how far the shipped tail departs from the measured
  curves, and when.
- **The muscle trace probably runs ahead of the tissue it represents.** Eger
  and Saidman's Table 3 (p. 1024) gives intertissue diffusion a group of its
  own, "a subset of the FG", of 2.9 L against the fat group's 14.5 L, with
  time constants of 230, 412 and 396 minutes for desflurane, sevoflurane and
  isoflurane against bulk fat's 1,226, 2,198 and 2,114. They write that 50
  minutes into desflurane, "[w]ere it not for losses by intertissue diffusion,
  the desflurane partial pressure in the MG [muscle group] would reach 74% of
  the partial pressure delivered to it from the lungs" (p. 1025). Yasuda et
  al. suggest that the route may also enlarge the apparent delivery to muscle
  (*Anesth Analg* p. 323), which acts the other way, and nothing says which
  effect wins.

The brain is spared. The review draws it apart from the rest of the
vessel-rich group "for reasons related to intertissue diffusion" (p. 1022),
and the model's vessel-rich group uses brain coefficients.

Eger and Saidman put the effect on late recovery: agent stored this way
"returns to the circulation to delay recovery in normal-weight and obese
patients, particularly with more soluble anesthetics. However, the increased
anesthetic in fat occurs at a lower partial pressure and thus might not
influence emergence materially" (p. 1032). What the model misses is the tail
and not the early fall.

The fat-flow uncertainty of § 10.8 may act against this omission or may not.
Nothing measures whether the two cancel, and neither may be read as correcting
the other.

### 10.10 The tissue:gas coefficients are carried as exact

The stored values differ from Yasuda, Targ and Eger's means in seven of nine
cells, by up to 9% (isoflurane fat, 70.0 against 64.2). Hendrickx and De Wolf
state the general case: "Tissue solubilities vary up to 150% between authors
(Yasuda et al. 1989), and the tissue homogenates used to determine these
coefficients may not represent in vivo conditions" (p. 165). Yasuda, Targ and
Eger compare their values with two other laboratories on p. 373.
Fiserova-Bergerova et al.'s values for sevoflurane, isoflurane and halothane
were similar for brain and for fat (except halothane's fat coefficient, 65%
greater), 115% to 150% greater for kidney, and 10% to 30% less for muscle.
Lowe's isoflurane values were 50% to 75% greater. The authors could not
explain the differences. They make no such comparison for desflurane.

The 150% is the kidney, which the model does not use on its own. **Muscle is
where the coefficient is least certain.** The other laboratories disagree with
it in both directions, and Yasuda's own muscle measurements spread the most:
the standard deviation is 43% of the mean for sevoflurane (2.38 ± 1.03), 45%
for isoflurane (4.40 ± 1.97) and 37% for desflurane (0.94 ± 0.35), against 17%
to 19% for fat. Eger and Saidman's best figure for sevoflurane muscle is 1.7,
with a range of 1.1 to 2.4 across the studies they cite (p. 1022), where the
model stores 2.4. At 1.7 the sevoflurane muscle time constant would be 29%
shorter. That is how much the choice of source can move the intermediate part
of every wash-in and washout curve.

### 10.11 One 70 kg adult

No equation reads the patient's weight, age, sex or body composition, and
nothing scales a volume, a flow or a coefficient from one. A run is the
reference adult's run, whatever value the reference weight shows. The model is
not a pediatric, obese or otherwise weight-varying model.

### 10.12 Dry alveoli

Real alveolar gas is saturated with water vapor at 47 mmHg, which leaves
713 mmHg for everything else. A dry inspired fraction is therefore diluted by
47/760, or 6.2% of an atmosphere, on reaching the alveoli. Equivalently, the
undiluted figure is 6.6% above the humidified one (47/713). The model applies
no such dilution. This changes no displayed percent or MAC multiple.
The measurements the model is compared with are end-tidal, and MAC is defined
on the end-tidal concentration, so the comparison is like with like. But there
is no water anywhere in the model, so no question about airway humidification
has an answer in it, whether it concerns an HME or a heated humidifier.

### 10.13 Altitude

Ambient pressure is fixed at 760 mmHg. At sea level, both classes of vaporizer
deliver the same partial pressure at a given dial position, so no displayed
number is wrong there. A user in Denver (about 630 mmHg) or Mexico City (about
585 mmHg) who sets 6% desflurane in the simulator and 6% on the real device is
not delivering the same anesthetic, and nothing else in the simulator says so.

**Sevoflurane and isoflurane come from variable-bypass vaporizers** (Dräger
Vapor 2000, Sevotec 5, Isotec 5, Penlon Sigma Delta). The gas leaving the
vaporizing chamber is saturated at a vapor pressure that temperature sets and
ambient pressure does not. As ambient pressure falls, the output rises in
volumes percent while the delivered partial pressure is approximately
preserved, and the dial needs no altitude correction. Boumphrey and Marshall
give $`\%_1 = \%_\mathrm{cal} \times P_\mathrm{cal} / P_1`$: isoflurane
dialled to 2% at 101.3 kPa delivers 4.05% at 50 kPa, which is 2.026 kPa either
way (Boumphrey and Marshall 2011).

**Desflurane comes from a gas-vapor blender** (Tec 6, Tec 6 Plus). Desflurane
boils at 22.8 °C, so the sump is kept at about 39 °C and about 1460 mmHg, and
pure vapor is injected into the fresh gas in the ratio that the dial sets. "The
pressure in the vapor circuit is electronically regulated to equal the pressure
in the fresh gas circuit… vaporizer output is constant because the amount of
flow through each circuit is proportional" (Andrews and Johnston 1993). Output
is a constant volumes percent, so the delivered partial pressure falls with
ambient pressure. Datex-Ohmeda's specification sheet for the Tec 6 Plus states:
"Decreased atmospheric pressure, with altitude, does not significantly affect
the concentration of agent delivered (V/V), but decreases the partial pressure
of the agent in the ratio of the atmospheric pressure to the calibrated
pressure of 760 mm Hg. To compensate for the reduction of vapor pressure output
at altitude, the rotary valve must be advanced to maintain the required agent
partial pressure."

**The MAC that the display divides by is a sea-level percent too.** 1 MAC is a
partial pressure quoted as a percentage of one atmosphere, so at reduced
ambient pressure the percentage needed to reach it rises while the partial
pressure does not. James and White proposed MAPP, minimum alveolar partial
pressure, on this ground (James and White 1984).

## References

Two entries carry a suffix that the text uses: Yasuda et al. 1991a and 1991b.
Four sources appear in the text only as another source cites them, and have no
entry: the ICRP (1975) blood distribution (in Davis and Mapleson 1981), Brody's
metabolic relation (in Lowe and Ernst 1981), and Fiserova-Bergerova et al.'s
and Lowe's tissue coefficients (in Yasuda, Targ and Eger 1989, p. 373).

- Andrews JJ, Johnston RV. The new Tec6 desflurane vaporizer. *Anesth Analg*
  1993;76:1338-1341.
- Boumphrey S, Marshall N. Understanding vaporizers. *Contin Educ Anaesth Crit
  Care Pain* 2011;11:199-203.
- Candries E, De Wolf AM, Hendrickx JFA. Prospective validation of Gas Man
  simulations of sevoflurane in O2/air over a wide fresh gas flow range.
  *J Clin Monit Comput* 2022;36(6):1881-1890. PMID 35318567,
  doi:10.1007/s10877-022-00842-0.
- Carpenter RL, Eger EI 2nd. Alveolar-to-arterial-to-venous anesthetic partial
  pressure differences in humans. *Anesthesiology* 1989;70(4):630-5.
  PMID 2930000.
- Carpenter RL, Eger EI 2nd, Johnson BH, Unadkat JD, Sheiner LB.
  Pharmacokinetics of inhaled anesthetics in humans: measurements during and
  after the simultaneous administration of enflurane, halothane, isoflurane,
  methoxyflurane, and nitrous oxide. *Anesth Analg* 1986;65(6):575-82.
  PMID 3706798.
- Cattermole GN, Leung PYM, Ho GYL, Lau PWS, Chan CPY, Chan SSW, Smith BE,
  Graham CA, Rainer TH. The normal ranges of cardiovascular parameters
  measured using the ultrasonic cardiac output monitor. *Physiol Rep*
  2017;5(6):e13195. doi:10.14814/phy2.13195.
- ChEMBL database, release 34 (EMBL-EBI). Compounds CHEMBL1200694
  (sevoflurane, C4H3F7O), CHEMBL1256 (isoflurane, C3H2ClF5O) and CHEMBL1200733
  (desflurane, C3H2F6O).
- Chortkoff BS, Eger EI 2nd, Crankshaw DP, Gonsowski CT, Dutton RC, Ionescu P.
  Concentrations of desflurane and propofol that suppress response to command
  in humans. *Anesth Analg* 1995;81(4):737-743.
  doi:10.1097/00000539-199510000-00014.
- Datex-Ohmeda. *Tec 6 Plus Vaporizer* specification sheet AN3307-A/1100,
  © 2000 Datex-Ohmeda Division, Instrumentarium Corp.
- Davis NR, Mapleson WW. Structure and quantification of a physiological model
  of the distribution of injected agents and inhaled anaesthetics.
  *Br J Anaesth* 1981;53(4):399-405. doi:10.1093/bja/53.4.399.
- De Wolf AM, Van Zundert TC, De Cooman S, Hendrickx JF. Theoretical effect of
  hyperventilation on speed of recovery and risk of rehypnotization following
  recovery - a Gas Man simulation. *BMC Anesthesiol* 2012;12:22.
  doi:10.1186/1471-2253-12-22.
- Dräger Vapor 2000 sevoflurane vaporizer specification: calibrated
  concentration range 0.2-8%.
  <https://zurichcorp.com/product/drager-vapor-2000-sevoflurane-precise-anesthesia-vaporization-for-optimal-patient-care/>
- Eger EI 2nd. Partition coefficients of I-653 in human blood, saline, and
  olive oil. *Anesth Analg* 1987;66(10):971-973. PMID 3631593.
- Eger EI 2nd, Saidman LJ. Illustrations of inhaled anesthetic uptake,
  including intertissue diffusion to and from fat. *Anesth Analg*
  2005;100(4):1020-33. PMID 15781517,
  doi:10.1213/01.ANE.0000146961.70058.A1.
- Esper T, Wehner M, Meinecke C-D, Rueffert H. Blood/Gas partition
  coefficients for isoflurane, sevoflurane, and desflurane in a clinically
  relevant patient population. *Anesth Analg* 2015;120(1):45-50.
  doi:10.1213/ANE.0000000000000516.
- Frayn KN, Karpe F. Regulation of human subcutaneous adipose tissue blood
  flow. *Int J Obes* 2014;38(8):1019-1026. doi:10.1038/ijo.2013.200.
- Fukuda T, Fukunaga A, Toyooka H. Site of fresh gas inlet and ratios of the
  delivered fraction and inspired fraction of inhaled isoflurane and
  sevoflurane in low-flow anesthesia. *J Anesth* 2006;20(4):268-273.
  PMID 17072690, doi:10.1007/s00540-006-0417-6.
- Heinonen I, Bucci M, Kemppainen J, Knuuti J, Nuutila P, Boushel R,
  Kalliokoski KK. Regulation of subcutaneous adipose tissue blood flow during
  exercise in humans. *J Appl Physiol* 2012;112(6):1059-1063.
  doi:10.1152/japplphysiol.00732.2011.
- Hendrickx JFA, De Wolf A. Special aspects of pharmacokinetics of inhalation
  anesthesia. In: Schüttler J, Schwilden H, eds. *Modern Anesthetics.*
  Handbook of Experimental Pharmacology 182. Springer, 2008:159-186.
- Hendrickx JFA, Lemmens HJM, Shafer SL. Do distribution volumes and
  clearances relate to tissue volumes and blood flows? A computer simulation.
  *BMC Anesthesiol* 2006;6:7. PMID 16772041, doi:10.1186/1471-2253-6-7.
- Hudgel DW, Devadatta P. Decrease in functional residual capacity during
  sleep in normal humans. *J Appl Physiol* 1984;57(5):1319-1322.
  doi:10.1152/jappl.1984.57.5.1319.
- International Commission on Radiological Protection. Report of Committee II
  on Permissible Dose for Internal Radiation (1959). Recommendations of the
  International Commission on Radiological Protection. Oxford: Pergamon Press;
  1960.
- James MF, White JF. Anesthetic considerations at moderate altitude.
  *Anesth Analg* 1984;63:1097-1105.
- Janssen I, Heymsfield SB, Wang ZM, Ross R. Skeletal muscle mass and
  distribution in 468 men and women aged 18-88 yr. *J Appl Physiol*
  2000;89(1):81-88. doi:10.1152/jappl.2000.89.1.81.
- Johnston RV, Andrews JJ, Deyo DJ, Trahan LA, Savrick MD, Grady JJ, Prough
  DS. The effects of carrier gas composition on the performance of the Tec 6
  desflurane vaporizer. *Anesth Analg* 1994;79(3):548-552. PMID 8067562.
- Jones HM, Rowland-Yeo K. Basic concepts in physiologically based
  pharmacokinetic modeling in drug discovery and development.
  *CPT Pharmacometrics Syst Pharmacol* 2013;2:e63. doi:10.1038/psp.2013.41.
- Katoh T, Suguro Y, Kimura T, Ikeda K. Cerebral awakening concentration of
  sevoflurane and isoflurane predicted during slow and fast alveolar washout.
  *Anesth Analg* 1993;77(5):1012-1017.
  doi:10.1213/00000539-199311000-00024.
- Kelly JM, Kong K-L. Accuracy of ten isoflurane vaporisers in current
  clinical use. *Anaesthesia* 2011;66(8):682-688. PMID 21749341.
- Kharasch ED. Biotransformation of sevoflurane. *Anesth Analg* 1995;81(6
  Suppl):S27-38. PMID 7486145, doi:10.1097/00000539-199512001-00005.
- Laster MJ, Fang Z, Eger EI 2nd. Specific gravities of desflurane, enflurane,
  halothane, isoflurane, and sevoflurane. *Anesth Analg* 1994;78(6):1152-3.
  PMID 8198275, doi:10.1213/00000539-199406000-00022.
- Lerman J, Gregory GA, Willis MM, Eger EI 2nd. Age and solubility of volatile
  anesthetics in blood. *Anesthesiology* 1984;61(2):139-143.
  doi:10.1097/00000542-198408000-00005.
- Lowe HJ, Ernst EA. *The Quantitative Practice of Anesthesia: Use of Closed
  Circuit.* Baltimore: Williams & Wilkins; 1981. ISBN 0683052004.
- Mapleson WW. An electric analogue for uptake and exchange of inert gases and
  other agents. *J Appl Physiol* 1963;18(1):197-204.
  doi:10.1152/jappl.1963.18.1.197.
- Mapleson WW. Effect of age on MAC in humans: a meta-analysis.
  *Br J Anaesth* 1996;76(2):179-185. doi:10.1093/bja/76.2.179.
- Meyer J-U, Kullik G, Wruck N, Kück K, Manigel J. Advanced technologies and
  devices for inhalational anesthetic drug dosing. In: Schüttler J, Schwilden
  H, eds. *Modern Anesthetics.* Handbook of Experimental Pharmacology
  vol. 182. Berlin: Springer; 2008:451-470.
- Philip JH. Gas Man Version 4.1 Teaches Inhalation Kinetics. Society for
  Technology in Anesthesia.
  <https://www.stahq.org/files/7913/2743/1066/Abstract_57.pdf>
- Philip JH. *Workbook for Gas Man(R): a simulation and teaching tool.*
  Chestnut Hill, MA: Med Man Simulations, Inc.; document dated 2012-05-16,
  preface dated October 2010. <https://gasmanweb.com/Workbook.pdf>
- Rampil IJ, Lockhart SH, Zwass MS, Peterson N, Yasuda N, Eger EI 2nd,
  Weiskopf RB, Damask MC. Clinical characteristics of desflurane in surgical
  patients: minimum alveolar concentration. *Anesthesiology*
  1991;74(3):429-433. doi:10.1097/00000542-199103000-00007.
- Shin HW, Yu HN, Bae GE, Huh H, Park JY, Kim JY. The effect of fresh gas flow
  rate and type of anesthesia machine on time to reach target sevoflurane
  concentration. *BMC Anesthesiol* 2017;17(1):10. PMID 28103806,
  doi:10.1186/s12871-016-0294-y.
- Song J-G, Cao Y-F, Yang L-Q, Yu W-F, Li Q, Song J-C, Fu X-Y, Fu Q. Awakening
  concentration of desflurane is decreased in patients with obstructive
  jaundice. *Anesthesiology* 2005;102(3):562-565.
  doi:10.1097/00000542-200503000-00014.
- Strum DP, Eger EI 2nd. Partition coefficients for sevoflurane in human
  blood, saline, and olive oil. *Anesth Analg* 1987;66(7):654-656.
  PMID 3605675.
- Targ AG, Yasuda N, Eger EI 2nd. Solubility of I-653, sevoflurane,
  isoflurane, and halothane in plastics and rubber composing a conventional
  anesthetic circuit. *Anesth Analg* 1989;69(2):218-225. PMID 2764290.
- Wahba RW. Perioperative functional residual capacity. *Can J Anaesth*
  1991;38(3):384-400. doi:10.1007/BF03007630.
- Weber J, Schmidt J, Wirth S, Schumann S, Philip JH, Eberhart LHJ.
  Context-sensitive decrement times for inhaled anesthetics in obese patients
  explored with Gas Man. *J Clin Monit Comput* 2021;35(2):343-354.
  PMCID PMC7943506.
- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Liu J, Laster M, Taheri S,
  Peterson NA. Comparison of kinetics of sevoflurane and isoflurane in humans.
  *Anesth Analg* 1991;72(3):316-24. PMID 1994760,
  doi:10.1213/00000539-199103000-00007. Cited as Yasuda et al. 1991a.
- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Johnson BH, Freire BA,
  Fassoulaki A. Kinetics of desflurane, isoflurane, and halothane in humans.
  *Anesthesiology* 1991;74(3):489-98. PMID 2001028,
  doi:10.1097/00000542-199103000-00017. Cited as Yasuda et al. 1991b.
- Yasuda N, Targ AG, Eger EI 2nd. Solubility of I-653, sevoflurane,
  isoflurane, and halothane in human tissues. *Anesth Analg*
  1989;69(3):370-373. PMID 2774233.
