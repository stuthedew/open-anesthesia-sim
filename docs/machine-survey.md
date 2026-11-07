# Anesthesia machines: the variables that change a simulated result

## What this document is, and what it is not

This survey asks **which differences between real anesthesia machines change a
number that this simulator computes or displays**. A difference counts if it
changes such a number today, or will once two planned additions are in place: a
modular model of the anesthesia machine (`ROADMAP.md`, planned-milestone item 1),
and a patient model that tracks several substances at once.

The survey is not an inventory. Beside each specification, it states how that
specification changes a computed or displayed value. A specification that changes
no such value is left out, or gets one line under § "Ruled out" if someone would
otherwise raise it again.

**The design of the planned machine model (`PL-FG9D`) builds on this survey.**
The design covers the machine classes, a profile schema and interlocks. The
survey's last section lists what the design needs: which variables are
per-machine *data*, and which are *behavior* that differs between machines. The
survey changes no code.

## The headline finding, because it decides the abstraction

**Circuit volume alone does not explain the measured differences between
machines.** Two studies show this directly. Each measured, in patients or on a
bench, a quantity that this model computes.

- Shin et al. measured time to a target sevoflurane concentration on three
  Dräger workstations and computed each one's circuit volume and time constant.
  The Perseus A500 and the Zeus IE had circuit volumes of 3.3 L and 3.2 L, and
  time constants of 6.6 min and 6.4 min at a fresh gas flow of 0.5 L/min. In
  this model, volume is the only machine parameter, so the two are effectively
  the same circuit. Their times to target still differed significantly. The
  authors attribute the remaining difference to the position of the fresh gas
  inlet relative to the patient, the presence of a fresh-gas-decoupling system,
  the ventilator drive, and the vaporizer's delivery mode.
- On otherwise unchanged machines, Fukuda et al. moved the **fresh gas inlet**
  from between the inspiratory valve and the absorber to between the inspiratory
  valve and the patient. For both isoflurane and sevoflurane, the
  inspired/delivered ratio ($`F_I/F_D`$) then rose significantly during low-flow
  anesthesia. This model's circuit equation computes that ratio. Moving the
  inlet left the circuit volume the same.

The data therefore rule out a machine profile that holds only a volume and a set
of bounds. Whoever designs the profile must choose one of two options: carry
the circuit's topology, such as where the fresh gas inlet sits, or state that
this model cannot distinguish machines that differ only in topology. The choice
must be visible (`PL-WZVZ`), because the project's standard for clinical output
in `CLAUDE.md` treats a curve as unsafe when it attributes a difference to a
trade name but the model lacks the parameter that produced the difference.

## The machines surveyed, and why those

**A machine is in this survey if it was the subject or the comparator of a
peer-reviewed study published between 2006 and 2025, and if it adds an axis of
variation that no other machine in the set covers.** An axis is a way machines
differ, such as how the ventilator is driven. No installed-base or market-share
source could be reached when this survey was written
(see § "How a value gets into this document" below). Instead, a study counts as
evidence of current clinical use, because it shows that the machine was in
service somewhere.

**The table maps how machines differ, and is not a list of machines to build.**
Together, its rows give the range of real behavior that the format of a machine
profile must be able to express.

| Machine | In because | Axes it contributes |
| --- | --- | --- |
| Dräger Primus | Kern 2012; Shin 2017; Zumsande 2023 | Piston ventilator; fresh gas decoupling; large apparatus volume |
| Dräger Perseus A500 | Shin 2017; Morimoto 2020 | Turbine (blower) drive; small apparatus volume; inlet close to the patient; no decoupling |
| Dräger Zeus IE | Shin 2017; Candries 2022; Bashraheel 2022 | Direct injection of agent (in-circle *and* out-of-circle modes); automated end-tidal control |
| Dräger Apollo | Lerman 2025 | Piston drive with decoupling, measured against a GE machine in patients |
| Dräger Fabius (GS/Plus) | Biro 1997 (decoupling); Fukuda 2006; Morimoto 2020 | Decoupling-style circle; the fresh-gas-inlet experiment's platform |
| GE Aisys / ADU family | Hendrickx 2001; Jakobsson 2017; Leijonhufvud 2017; Lerman 2025; Hoffmann 2025 | Electronically controlled cassette vaporizer; bellows; automated agent control |
| GE Avance | Kern 2012 | Measured directly against a Primus at neonatal settings |
| Getinge FLOW-i | Jakobsson 2017; Leijonhufvud 2017; Candries 2022; Kalmar 2022 | Injector-type agent delivery; automated gas control with a speed setting |

**The survey leaves out Mindray's A-series, Penlon and Spacelabs, because no
source here could fill their rows.** When this survey was written, no evidence
was found that these machines are in current use in the US. Each becomes a
candidate once someone can reach its manufacturer's technical data.

## How a value gets into this document

The survey was meant to take machine behavior from each manufacturer's operator
or technical manual, cited by document and revision, but no manual could be
reached. On 2026-09-19 the network used for this survey blocked `www.draeger.com`,
`www.gehealthcare.com`, `www.iso.org`, `webstore.ansi.org`, `standards.iteh.ai`
and every site tried that hosts copies of manuals. It could still reach
`www.ncbi.nlm.nih.gov`, `link.springer.com`, `doi.org` and `search.worldcat.org`.
That left three routes to sources: PubMed, the project owner's private reference
corpus, and direct identifier checks. The survey records values by these rules:

1. **A measured quantity is cited to the measurement.** The model uses quantities
   such as an inspired concentration, a time to target, and a vaporizer's output
   against its dial. Where a peer-reviewed study measured such a quantity, that
   study is the authority, and a stronger one than a manual would have been. The
   model's documentation (`docs/MODEL.md`) likewise puts a primary measurement
   above a specification sheet.
2. **A figure that a paper reports but did not measure is marked as such.** Shin
   et al. print the three Dräger apparatus volumes and cite them onward to sources
   that could not be opened. The survey records those volumes as tier 2, meaning a
   secondary synthesis.
3. **A manufacturer's own technical account is used, and quoted, where the
   project has one.** The private reference corpus
   (`stuthedew/open-anesthesia-sim-references`) holds *Modern Anesthetics*. Five
   Dräger authors wrote its chapter on inhalational dosing technology, which
   describes the vaporizers, the injector, the gas module and the Zeus breathing
   system directly. As a textbook chapter it is tier 2, but for what a device does,
   it is the manufacturer's own account, the kind of source the survey was meant
   to use.
4. **A standard is named by number, title, edition and date only, and its edition
   and date come by a weak route.** Neither the standards' texts nor the ISO
   catalogue pages could be reached. Each edition and date therefore comes from
   **national adoption records surfaced by a web search**. Under this project's
   rule, a web search is not a source. Without the standards' texts, the survey
   says what each standard *is*, never what one of its clauses requires. Every
   claim that would need a standard's text is marked as a gap.
5. **Anything else is `unknown`.** A machine whose apparatus volume is unknown
   cannot be added yet, even with a plausible guess at the volume.

## The variables

Each entry carries its bucket and, for (a) and (b), the reason it reaches a
number:

- **(a)** changes a number the simulator computes today;
- **(b)** changes a number once planned-milestone item 1 (machine and
  interlocks) and the multi-substance patient state land;
- **(c)** ruled out — collected in one section at the end, with the condition
  under which each stops being ruled out.

### (a1) Apparatus gas volume

**The circuit volume sets the part of the early rise in inspired concentration
that comes from the equipment rather than from uptake.** The model treats the
apparatus and the patient circuit as one well-mixed compartment, whose volume is
$`V_C`$ (`circuit_volume_l`). The compartment's fresh-gas wash-in time constant
is $`\tau_C = V_C/\dot V_F`$, where $`\dot V_F`$ is the fresh gas flow.

**The simulator's circuit volume is currently 6.0 L.** The value and its source
are stored in `src/anesthesia_sim/data/machines/reference_circle_system.json`.
That file also records that the value departs on purpose from Gas Man's
published 8.0 L (`PL-4YY1`).

**Choosing a different machine can change the wash-in time constant $`\tau_C`$ by
a factor of about 1.8 at any given flow.** The difference shows in the first two
minutes of every run. With a 1.2 L patient circuit, the Perseus A500 and the
Zeus IE hold about half the stored 6.0 L. They are the two most recent Dräger
designs.

| Machine | Apparatus incl. absorber, excl. patient circuit | With a 1.2 L patient circuit | $`\tau_C`$ at 4 L/min |
| --- | --- | --- | --- |
| Dräger Primus | 4.7 L | 5.9 L | 89 s |
| Dräger Perseus A500 | 2.1 L | 3.3 L | 50 s |
| Dräger Zeus IE | 2.0 L | 3.2 L | 48 s |
| GE Aisys / Avance / ADU | unknown | unknown | — |
| Getinge FLOW-i | unknown | unknown | — |
| Dräger Apollo, Fabius | unknown | unknown | — |

Shin et al. report the apparatus volumes and the 1.2 L patient circuit. Their
figures are tier 2, a secondary synthesis
(§ "How a value gets into this document"). The time constants are the volumes
with the patient circuit divided by 4 L/min, the simulator's default fresh gas
flow.

**The stored 6.0 L is within 2% of the Primus's 5.9 L with a 1.2 L patient
circuit, but only by coincidence.** The value predates this survey and was kept
because it was ruled not critical.

**A machine profile can supply only the apparatus part of $`V_C`$
(`PL-FG9D`).** The patient circuit is a disposable chosen for each case, not
part of the machine.

### (a2) Default fresh gas flow

**Every run starts at the default fresh gas flow, 4.0 L/min.** The flow sets the
circuit time constant $`\tau_C`$ at $`t = 0`$ and every value in the default-flow
column of the accuracy table. It is a setting of the machine, not a property of
the patient or the agent (`PL-8DJ7`). The machine data file stores the value and
records that no published source gives it (`provenance_gap`).

**No source that the survey could obtain gives a default fresh gas flow for any
surveyed machine, or reports the flows used in practice.** The literature recommends
flows instead. Kalmar et al. conclude that *"routine clinical practice using what
historically is called 'low flow anaesthesia' (e.g. 2 L/min FGF) should be
abandoned"* in favour of automated minimal-flow delivery. That recommendation
rests on a single-centre retrospective study of 25 cases per group, on one
workstation. What the paper does show about practice is its comparator: a group
held at 2 L/min, which it calls conventional low flow. That flow is already
below the simulator's 4 L/min.

**Candries et al. and Hoffmann et al. do not show where 4 L/min sits in practice**
(`PL-NM7X`). Candries et al. randomised fresh gas flows of 0.2 to 6 L/min, a range
chosen to be wide for a study validating the Gas Man simulator. Hoffmann et al. ran
0.3 to 6 L/min *in vitro*, into a 2 L test lung. They describe their settings as
reflecting clinical conditions. Those settings include 4, 5 and 6 L/min, so if
anything the paper places 4 L/min in the middle of practice rather than at its high
end. A study's chosen flow range does not report practice.

**The simulator keeps 4.0 L/min, labelled in the machine data file as a teaching
default, not a clinical recommendation** (project owner, 2026-09-20, ratified, over
lowering the default to match contemporary low-flow practice). Without a label, any
default teaches learners that its value is the norm. Lowering the default to
0.5 L/min would only change the norm it teaches. As a machine default, that value
would lack a published source, just as 4.0 L/min does. At 4 L/min, $`\tau_C`$ is
near 90 s, so the machine's own lag shows as a distinct phase before patient uptake,
within a run that a learner will sit through. At 0.5 L/min, $`\tau_C`$ is about
12 minutes, and that phase no longer fits in such a run.

**The code keeps a copy of 4.0 L/min, and a test fails if the copy and the machine
data file differ.** The copy is the constant `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`
in `src/anesthesia_sim/core/circuit.py`. A machine profile may leave the flow out,
because the survey found no source that gives it. A run on such a profile starts at
this constant (`PL-QW19`), and a unit test that builds a circuit without giving a
flow uses it too.

### (b1) Delivered concentration is not the dial setting

**Why it reaches a number.** $`F_D`$ enters the circuit equation as the
concentration arriving with fresh gas, and the interface presents it as a set
value a learner maps onto a real dial. A machine whose output differs from its
dial by 20% is delivering a different $`F_D`$ than the model assumes, and the
error is a function of agent, carrier gas and flow — all three of which the
model either has or will have.

**What the survey found.** Two bench characterisations, both tier 1, of the two
device classes that matter:

- **GE's cassette vaporizer (ADU/Aladin family).** Hendrickx et al. measured
  output against dial across the whole range of each agent: within 10% of dial
  at 0.3–10 L/min for isoflurane, within 10% at 0.5–5 L/min for sevoflurane, and
  within 13% at 0.5–1 L/min for desflurane, with larger deviations outside those
  flow ranges. Their conclusion is the one that matters for the abstraction:
  *"Despite a different design and the use of complex algorithms to improve
  accuracy, the same physical factors affecting the performance of conventional
  vaporizers also affect the ADU vaporizer."*
- **The Tec 6 desflurane vaporizer.** Johnston et al. measured eight vaporizers
  and found output highest with oxygen and lowest with nitrous oxide as carrier,
  the effect accentuated at low flow and correlated with carrier gas viscosity.
  At 1.0 L/min and a 10% dial setting: 10.3 ± 0.66 vol% in 100% oxygen,
  9.4 ± 0.58 in air, 8.7 ± 0.52 in 30% oxygen with 70% nitrous oxide, and
  8.1 ± 0.44 in 100% nitrous oxide — the last 19% below the dial.

**And the two device classes do not even deliver the same *kind* of quantity.**
Meyer et al., writing for the manufacturer of one of the surveyed machines,
state it in one sentence: *"The desflurane vaporizer principle described here
delivers a fixed volume percentage, making it different from conventional
vaporizers, which deliver fixed partial pressures."* The same chapter gives the
mechanism behind the carrier-gas effect above independently of Johnston et al.:
*"Desflurane vaporizers are calibrated for operation with an FGF of 100% O2
concentration, resulting in differences between set and actual concentrations
for other FGF mixtures."*

This one is a units question rather than a magnitude question, which puts it
squarely inside `CLAUDE.md`'s clinical-output standard — the correct number
carrying the wrong units is a safety failure, and this model works in partial
pressure fractions throughout (`delivered_partial_pressure_fraction`). A dial
number means a partial pressure on one device class and a volume fraction on
the other, and the two diverge wherever ambient pressure is not one atmosphere.

**What it needs.** The flow-dependence half needs only the machine milestone.
The carrier-gas half needs nitrous oxide in the model, which is planned-milestone
item 6 and the multi-substance state beneath it, so it is bucket (b) rather than
(a) for that reason and no other. The fixed-volume-percentage half needs only a
decision about whether this model claims to hold at one ambient pressure.

### (b2) Vaporizer dial range and maximum, and where that number belongs

**The dial maximum caps the delivered concentration, $`F_D`$.** The code
enforces the cap in `src/anesthesia_sim/core/circuit.py`.

**The maximum belongs to the device, not to the agent.** The model stores this
maximum per agent (`max_delivered_concentration_percent`): desflurane 18.0%,
sevoflurane 8.0% and isoflurane 5.0%. The 18% is the calibrated maximum of one
device, the Tec 6 desflurane vaporizer. Johnston et al. characterised the Tec 6
across *"all integer dial settings from 1% to 18%"*. The breathing-circuit
section of `docs/MODEL.md` cites them for this value. Nothing about desflurane
itself sets the 18%, so a different maximum may apply to a vaporizer of another
design or to a machine with an electronically controlled injector. The stored
maximum therefore has to depend on the machine as well as on the agent. It is
the first concrete case of the data-or-behavior question in `PL-FG9D`.

**Real vaporizers' dial increments are unknown.** The simulator's on-screen
vaporizer dial is continuous (`PL-043`). If the simulator comes to model real
machines, a faithful dial would have each vaporizer's own increments. No source
available to the survey gives those increments. Johnston et al. *tested* the
integer settings, which does not show that the Tec 6 dial has integer detents.

### (b3) Delivery mode: bypass vaporizer against direct injection

**Where agent enters the breathing system changes the model's equation.** A
conventional bypass vaporizer sits in the fresh gas stream, so its agent arrives
with the fresh gas. The model describes that delivery with the term
$`\dot V_F F_D`$. A direct-injection machine can put agent into the breathing
system itself, downstream of the fresh gas inlet. There is then no $`F_D`$ at
the inlet, and the model needs a different term for agent that arrives this way.
No stored value for a machine can express that difference, so delivery mode is
the survey's clearest case of machines that differ in
**behavior rather than data**.

**The Zeus IE machine offers both kinds of delivery, as separate modes.** Meyer
et al. describe its injector as a reservoir, a dosing chamber and a heating
unit. A pulsed valve injects liquid agent from a pressurised chamber into a
heated vaporising chamber, and a heated pipe carries the vapour to the breathing
system. In Meyer et al.'s account, the two modes differ in where the vapour
enters:

- **Fresh gas mode.** The user sets a fresh gas agent concentration, and the
  vapour mixes with fresh gas before it enters the breathing system. *"In this
  dosing mode the agent dosage performance is equivalent to a conventional
  vaporizer."* The model's existing term therefore describes this mode.
- **Auto control mode.** Agent enters the breathing system through a separate
  inlet, and its delivery is *"independent of the FGF settings"*. A closed
  feedback loop adjusts the dose to reach an expiratory target.

In Shin et al.'s measurements, which mode reached the target faster depended on
flow. Auto control mode was faster than fresh gas mode at 0.5 and 1 L/min, and
slower at 3 L/min.

### (b4) Automated end-tidal or target control

**Why it reaches a number.** It inverts the control direction. The user sets a
target end-tidal concentration and the machine sets the dial and the flow, so
the simulator's two most-used controls stop being inputs and become the
machine's outputs. It is planned-milestone item 5.

**What the survey found.** The behavior is not a faster version of manual
control and cannot be modelled as one. Shin et al. found the Zeus's automatic
mode reaching about 3.6% very rapidly and then taking a considerable further
delay to settle at 4%, because the controller slows its approach to avoid
overshooting the target — so at 3 L/min the automatic mode was *slower* to
target than the manual one. Kalmar et al. found the FLOW-i's automated gas
control consumes agent as a function of its speed setting (6.0 mL at speed 2 to
7.3 mL at speed 8 over 45 min at a 2% end-tidal target), so even the same
machine in the same mode is not one behavior.

**Two structural facts from Meyer et al.'s description of the Zeus, either of
which on its own decides how this is modelled.**

- **Fresh gas flow stops being an input.** Three feedback loops run in parallel,
  and fresh gas flow is an *output* of two of them: the volume controller's
  *"output control variable … is the amount of FGF, including agent flow"*, set
  from the reservoir bag's filling level to hold the system volume constant; the
  oxygen controller's is *"the oxygen concentration and the amount of FGF"*. The
  agent controller sets injected liquid when the level is low and, when it is
  high, flushes with fresh gas instead. So on an automated machine the
  simulator's two principal controls are not settings at all.
- **The machine runs a patient model of its own.** *"Based on a simplified
  physiological model of the patient, a feedback controller calculates the
  amount of agent from the deviation between the expiratory target value and the
  expiratory concentration."* Simulating such a machine means running a
  controller whose own model differs from this one's, which is a scope decision
  for planned-milestone item 5 and not a parameter.

### (b5) Fresh gas decoupling

**Decoupling stops fresh gas flow from changing the delivered tidal volume.** It
diverts fresh gas to the reservoir bag during inspiration and returns it during
expiration. Biro measured minute volume in a circle system with and without a
decoupling device. Without the device, fresh gas flow and inspiratory duration
markedly changed minute volume, and the effect was statistically significant
above 4 L/min. With the device, neither changed minute volume.

**The effect on tidal volume changes no simulated value today, because
ventilation is a patient setting in the model, not a machine setting.** It will
once the planned machine milestone gives the machine a ventilator.

**Decoupling also changes the agent's path.** It routes fresh gas through the
reservoir bag before the gas reaches the circle. Shin et al. name the absence of
a decoupling system as one reason the Perseus machine reached target fastest.

**Decoupling brings a hazard that the simulator's design should account for.**
Križmarić et al. showed that, with decoupling, disconnecting the reservoir bag
entrains room air into the breathing circuit. Decoupling is therefore a hidden
mode, a machine feature that silently changes what is in the circuit. One of the
project's rules asks that the design guard against hidden modes
(`.claude/rules/expert-review.md`). For the machine milestone, decoupling is a
candidate scenario, not only a parameter.

### (b6) Ventilator drive

**Ventilator drive can change a simulated value through mixing rate and
apparatus volume.** Shin et al. attribute part of the Perseus and Zeus advantage
to blower-driven ventilators *"with rapid mixing"*, compared with the Primus's
classical piston. If the machine milestone represents mixing rate at all, a
machine's profile should store the quantity that the model uses for mixing rate,
not the kind of drive, such as "piston".

Jain and Swaminathan's review is the standard description of the three kinds of
drive: double-circuit bellows, single-circuit piston, and turbine. It also says
which of them usually comes with decoupling.

### (b7) Fresh gas inlet position

**Inlet position changes the inspired/delivered ratio, $`F_I/F_D`$, even at a
fixed circuit volume and fresh gas flow.** The simulator's circuit equation computes
this ratio. See the headline finding above.

**One study measured an effect, and another inferred one.** In a randomised study in
patients, Fukuda et al. moved the inlet from between the inspiratory valve and the
absorber to between the inspiratory valve and the patient. During low-flow anesthesia
on two decoupling-style machines, the move significantly raised $`F_I/F_D`$ for both
isoflurane and sevoflurane. Shin et al. rank their three machines by inlet proximity
to account for differences that their volume calculation did not explain.

**The simulator cannot represent inlet position, and must not fake it.** It
treats the circuit as a single well-mixed compartment, in which the inlet has no
position. An "effective volume" calibrated to the observed kinetics would reproduce
the curves, but it would attribute to volume a difference that volume did not
cause. The comparison table between machines (`PL-WZVZ`) would then print a
number that looks sourced but that no measurement supports.

### (b8) Flow bounds, minimum oxygen flow, and the hypoxic guard

**A machine can refuse flow settings that the model currently accepts.** These
settings are a flow below the machine's minimum total flow and a hypoxic
mixture. The model's supported range for fresh gas flow is 0.0 to 10.0 L/min
(`src/anesthesia_sim/core/supported_ranges.py`). It is the range over which the
model is valid, not any machine's deliverable flow range.

**The survey could not obtain the minimum oxygen flow, minimum total flow or
deliverable flow range of any machine it covered.** The governing standard is
**ISO 80601-2-13:2022**, *Medical electrical equipment — Part 2-13: Particular
requirements for basic safety and essential performance of an anaesthetic
workstation*, second edition, 2022-04, amended by
ISO 80601-2-13:2022/Amd 1:2026. **Its text was not available to the survey, so
what it requires is unknown.**

**A machine profile now has a field for the machine's deliverable flow range,
`deliverable_fresh_gas_flow_range`** (2026-09-20, `PL-8PS6`). The simulated
breathing circuit (`BreathingCircuit`) refuses a flow outside that range,
separately from the check against the model's supported range. The field is
empty (`null`) in the reference circle system's profile,
`reference_circle_system.json`, because the survey found no value. When someone
finds a real machine's deliverable flow range, it goes into that field in the
machine's profile. The minimum total flow is the lower limit of that range, so
it has no field of its own.

**The model has no hypoxic guard yet, so nothing it computes depends on the
minimum oxygen flow.**

### (b9) Which agents a machine can deliver, and the single-agent interlock

**The simulator should refuse an agent that a machine cannot deliver.**
Simulating it would attach the machine's trade name to a delivery that the
machine cannot perform. Under the project's standard for clinical output,
choosing a machine model is safety-critical (`CLAUDE.md`).

**Andrews et al. quantified the hazard behind the interlock.** They calculated
the output of conventional vaporizers filled with desflurane by mistake. An
enflurane vaporizer set to 1% at 22 °C would give 57.8% desflurane, or 9.6 MAC.
Enflurane, isoflurane and halothane vaporizers at one-MAC dial settings would
produce 14.0, 10.2 and 7.8 MAC of desflurane respectively. They conclude that
safe delivery of desflurane requires engineering safeguards.

**This misfilling hazard drove agent-specific filling, standardised as
ISO 5360:2016**, *Anaesthetic vaporizers — Agent-specific filling systems*,
fourth edition, 2016-02-15. A catalogue abstract says that the standard
specifies no dimensions for desflurane, because of that agent's properties.
**The standard's text was not read**, so this statement is unconfirmed until
someone checks the standard.

**Delivering desflurane is a capability that a machine has or lacks, not a
parameter of the agent.** Desflurane needs a heated, pressurised,
electromechanically coupled delivery device, and a machine without one cannot
deliver it at all. This finding does not depend on the unread standard, because
the sources available to the survey agree on it. Andrews and Johnston give the
primary description of one such device, the Tec 6. Meyer et al. report that it
heats desflurane electrically in a sealed chamber to 39 °C, *"creating a
pressure of approximately 1,550 mmHg"*. They add that it cuts off agent flow
entirely on tilt, power failure, low liquid level, or disagreement between its
two differential pressure sensors.

**Which agents each machine can deliver is unknown.** A manufacturer's technical
data would state it plainly.

### (b10) Sidestream sample flow

**Whether the analyser's sample is lost depends on the machine or monitor.** A
sidestream analyser removes gas from the circuit when its sample is scavenged,
and none when it returns the sample. A mainstream sensor draws no gas at all.
For each surveyed machine, the analyser's configuration is **unknown**, so ask
about it first, and then about the sample flow.

**Where the sample is scavenged, the loss is continuous and can be large.** At
the fresh gas flows the literature now uses, such as 300 mL/min, a 200 mL/min
sample is two thirds of the fresh gas. Today the model's circuit loses gas only
through its exhaust, and a scavenged sample would be a second loss.

**The survey found two sample flows.** Shin et al. sampled at the Y-piece at
200 mL/min with a bench analyser, and state that *"the gas samples were not
returned to the system"*. Meyer et al. describe a surveyed machine's integrated
multi-gas module, which also samples in a side stream. They put its sample flow
at *"a continuous gas flow in the order of 100 ml/min or more"*. In the section
that gives this flow, they name the alternative: a **mainstream** sensor between
the Y-piece and the tracheal tube, which measures in place.

### (b11) Whether the circuit exhaust is unconditional

**The model's exhaust runs whenever fresh gas flows.** A semi-closed circle
behaves this way, but not every surveyed machine does in every mode. The
exhaust removes as much gas as the fresh gas flow adds, at the current
mixed-circuit concentration, so the circuit loses agent at $`\dot V_F F_I`$.
The circuit's mass-balance identity and the `Circuit exhaust` accounting in
`docs/MODEL.md` assume this loss.

**The Zeus anesthesia machine can close its exhaust.** Meyer et al. describe
its surplus gas valve venting excess volume to the scavenging system in
ordinary operation. They go on: *"In the automatic controlled mode of the Zeus
anesthesia machine, the surplus gas valve can be closed to prevent any loss of
gas volume."* With that valve closed, the Zeus's circuit has no exhaust flow, so
it does not lose agent at $`\dot V_F F_I`$.

**This is the only survey entry that affects an equation rather than a
parameter**, so it is the one most likely to be implemented wrongly as a
parameter. A closed-circuit mode needs a different mass-balance identity, not
the same one with a small exhaust.

## Ruled out

The survey leaves out the features below for every machine it covers. Features
that need a longer explanation are ruled out in bucket (b), above.

- **Screens, layouts, alarms and alarm limits, menu structure, workflow.** They
  do not affect any value the simulator computes. They come back if a milestone
  reproduces a specific machine's interface. What the simulator's own display
  may imply is set by the clinical-output standard in `CLAUDE.md` and by the
  work item for the machine panel (`PL-WZVZ`), not by any machine's screen.
- **Pre-use self-test, checkout procedure, calibration and service intervals.**
  They decide whether a machine may be used, not what it delivers. They come
  back if a milestone models machine readiness or failure.
- **Cart, mounting, drawers, mobility, mains and battery, pipeline and cylinder
  supply pressures.** They do not affect any concentration. They come back if a
  milestone models supply failure.
- **Scavenging system type.** It sits downstream of the circuit exhaust and
  does not affect the circuit concentration in this model. It comes back if a
  milestone models circuit pressure, or a closed system where the exhaust is
  not free.
- **Absorbent chemistry: Compound A, carbon monoxide from desiccated absorbent,
  absorbent dust.** These are real hazards, but the model has no chemistry: it
  never consumes or transforms agent. They come back as soon as a milestone adds
  a chemical reaction. The absorbent canister's *volume* stays in the survey,
  among the apparatus volumes in (a1).
- **Circuit component absorption of agent.** It is a property of the disposable
  circuit, not of the machine, so it is outside this survey's scope. The
  absorption has been measured, but the model's circuit walls absorb no agent,
  a known limitation (`PL-LS3H`).
- **Data export, record-keeping and network integration.** They do not affect
  any value the simulator computes.

## What `PL-FG9D` needs: data against behavior

A difference between machines is data when a file can store it, and behavior
when only code can express it. Two differences fit neither, and need a decision
before implementation begins.

**Data.** Each field below belongs in a validated, versioned file for each machine.

| Field | Bucket | Status |
| --- | --- | --- |
| Apparatus gas volume, including absorber, excluding the patient circuit | (a1) | Known for three Dräger machines, tier 2; unknown elsewhere |
| Deliverable total fresh gas flow range | (b8) | Unknown for every machine |
| Minimum total flow and minimum oxygen flow | (b8) | Unknown for every machine |
| Agents the machine can deliver | (b9) | Unknown for every machine |
| Per-agent dial maximum, qualified by the delivery device | (b2) | Tec 6 desflurane 18%; otherwise unknown |
| Sidestream sample flow, and whether the sample returns | (b10) | Unknown for every machine |
| Default fresh gas flow | (a2) | No machine publishes one |

**Behavior.** For each of these differences, the code needs a fixed set of
alternatives, and each machine uses one.

- **Whether the circuit exhaust runs at all** (b11). With the surplus valve
  shut, closed mode needs a different mass-balance identity in `docs/MODEL.md`.
  A small exhaust flow cannot stand in for closed mode. Decide how to model it
  before any code is written, or an implementation will quietly represent it as
  a coefficient.
- **Where agent enters the circle** (b3). Agent either joins the fresh gas
  stream through a bypass, or is injected directly into the circle
  independently of fresh gas flow. The two routes need different equations.
  The Zeus anesthesia machine has both. Its manufacturer describes the fresh
  gas mode as equivalent to a conventional vaporizer.
- **Who runs the control loop** (b4). A manually dialled machine takes $`F_D`$
  and $`\dot V_F`$ as inputs. An automated machine produces both as the outputs
  of parallel feedback controllers, one of which runs its own simplified patient
  model.
- **How the dial maps to delivered concentration** (b1). The mapping depends on
  agent, carrier gas and flow, and is characterised per device class rather
  than tabulated. One class delivers a fixed volume percentage and the other a
  fixed partial pressure, so the two map the dial into different units.
- **Whether fresh gas is decoupled from the tidal volume** (b5), when the
  machine controls ventilation.

**Neither data nor behavior.** The model's circuit is a single well-mixed
compartment, which has no place for these two differences.

- **Fresh gas inlet position and internal topology** (b7) measurably change
  $`F_I/F_D`$. Choose option 1 or 2, and record the choice in the work item
  (`PL-FG9D`):
  1. Represent them with a multi-compartment circuit. The closest existing plan
     is `ROADMAP.md` planned-milestone item 39.
  2. Leave them out, and say so wherever a machine is chosen.
  3. Fold them into an effective volume. Refuse this option, because the
     comparison table (`PL-WZVZ`) would then attribute a real difference to
     the effective volume, which did not cause it. Preventing that error is
     what the table is for.
- **Ventilator drive** (b6) needs the same decision, with less at stake. It
  matters through mixing, which the model does not represent.

## What is missing, and how the next session gets it

Every value marked `unknown` above has the same fix: **someone who can reach
manufacturer technical data, or a project owner who can supply it.** Try the
private reference corpus first. It answered the vaporizer, injector, gas-module
and closed-circuit questions outright.

**Seek each unknown value one at a time, only when a machine profile needs it**
(project owner, 2026-09-20). Ask for that machine's manual then. No unknown value
here blocks the machine abstraction.

The places to look are:

- Dräger *Instructions for Use* for the Perseus A500, Primus, Apollo, Fabius and
  Zeus IE: the technical data sections, for apparatus volume, flow ranges,
  minimum oxygen flow and sample gas flow. The Perseus manual was found at
  `draeger.com/Content/Documents/Content/IfU_Perseus_A500_SW_1.1n_EN_9054101.pdf`.
  The network used for this survey refused the download on 2026-09-19, and
  still refused connections to `draeger.com` and `www.draeger.com` on
  2026-10-06.
- GE *User's Reference Manual* for the Aisys CS², Avance and Carestation
  families, and the Aladin cassette's specification, for the same fields.
- Getinge *User's Manual* for the FLOW-i, for the same fields and for the
  volume reflector's contribution to apparatus volume.
- **ISO 80601-2-13:2022** (second edition, 2022-04) and its Amendment 1:2026,
  for what a workstation must guarantee about oxygen concentration and flow.
- **ISO 5360:2016** (fourth edition, 2016-02-15), for agent-specific filling,
  and to confirm that it specifies no dimensions for desflurane.

The comparison table (`PL-WZVZ`) takes its rows from this survey, so the sources
above are where to look for each row it shows as `unknown`.

## Sources

**Each entry says how far its source was read: full text read, abstract read, or
metadata only.** Every article below was retrieved from PubMed on 2026-09-19,
through the PubMed MCP server, and its PMID, DOI, journal, volume, issue and
pages were read from its PubMed record. For a paywalled article, that route gives
only the abstract. Each DOI links the original. The one book chapter, by Meyer
et al., came instead from the project owner's private reference corpus.

**Measurements of quantities this model computes (tier 1).**

- Biro P. [The effect of fresh-gas decoupling on respiratory volume. Dräger
  Sulla 808V anesthesia ventilator]. *Anaesthesist.* 1997;46(11):949–952.
  PMID 9490582; [DOI 10.1007/s001010050491](https://doi.org/10.1007/s001010050491).
  English abstract read. The article is in German.
- Fukuda T, Fukunaga A, Toyooka H. Site of fresh gas inlet and ratios of the
  delivered fraction and inspired fraction of inhaled isoflurane and sevoflurane
  in low-flow anesthesia. *J Anesth.* 2006;20(4):268–273.
  PMID 17072690; [DOI 10.1007/s00540-006-0417-6](https://doi.org/10.1007/s00540-006-0417-6).
  Abstract read.
- Hendrickx JF, De Cooman S, Deloof T, Vandeput D, Coddens J, De Wolf AM. The
  ADU vaporizing unit: a new vaporizer. *Anesth Analg.* 2001;93(2):391–395.
  PMID 11473867; [DOI 10.1097/00000539-200108000-00031](https://doi.org/10.1097/00000539-200108000-00031).
  Abstract read.
- Johnston RV, Andrews JJ, Deyo DJ, Trahan LA, Savrick MD, Grady JJ, Prough DS.
  The effects of carrier gas composition on the performance of the Tec 6
  desflurane vaporizer. *Anesth Analg.* 1994;79(3):548–552.
  PMID 8067562; [DOI 10.1213/00000539-199409000-00025](https://doi.org/10.1213/00000539-199409000-00025).
  Abstract read.
- Kern D, Larcher C, Basset B, Alacoque X, Fesseau R, Samii K, Minville V,
  Fourcade O. Inside anesthesia breathing circuits: time to reach a set
  sevoflurane concentration in toddlers and newborns: simulation using a test
  lung. *Anesth Analg.* 2012;115(2):310–314.
  PMID 22584556; [DOI 10.1213/ANE.0b013e318257570f](https://doi.org/10.1213/ANE.0b013e318257570f).
  Abstract read.
- Lerman J, Correa AMR. Sevoflurane washin with the Dräger Apollo and GE Datex
  Ohmeda Aisys workstations in healthy children. *Paediatr Anaesth.*
  2025;35(7):535–541. PMID 40178391; [DOI 10.1111/pan.15106](https://doi.org/10.1111/pan.15106).
  Abstract read.
- Morimoto Y, Shiramoto H, Shimamoto Y. Perseus A500 enables faster recovery
  from desflurane general anesthesia. *J Anesth.* 2020;34(2):281–285.
  PMID 32020373; [DOI 10.1007/s00540-020-02740-8](https://doi.org/10.1007/s00540-020-02740-8).
  Abstract read.
- Shin HW, Yu HN, Bae GE, Huh H, Park JY, Kim JY. The effect of fresh gas flow
  rate and type of anesthesia machine on time to reach target sevoflurane
  concentration. *BMC Anesthesiol.* 2017;17(1):10.
  PMID 28103806; [DOI 10.1186/s12871-016-0294-y](https://doi.org/10.1186/s12871-016-0294-y).
  **Full text read** (PMC5248460). Its times to target are its own measurements.
  It also gives the three Dräger apparatus volumes, citing sources that could
  not be reached, so those volumes are tier 2 here.

**Model-relevant behavior (tier 2) and machine description.**

- Andrews JJ, Johnston RV. The new Tec 6 desflurane vaporizer. *Anesth Analg.*
  1993;76(6):1338–1341.
  PMID 8498675; [DOI 10.1213/00000539-199376060-00027](https://doi.org/10.1213/00000539-199376060-00027).
  Abstract read.
- Andrews JJ, Johnston RV, Kramer GC. Consequences of misfilling contemporary
  vaporizers with desflurane. *Can J Anaesth.* 1993;40(1):71–76.
  PMID 8425247; [DOI 10.1007/BF03009323](https://doi.org/10.1007/BF03009323). Abstract read.
  Its figures are a mathematical model's output, not a measurement.
- Candries E, De Wolf AM, Hendrickx JFA. Prospective validation of Gas Man
  simulations of sevoflurane in O2/air over a wide fresh gas flow range. *J Clin
  Monit Comput.* 2022;36(6):1881–1890.
  PMID 35318567; [DOI 10.1007/s10877-022-00842-0](https://doi.org/10.1007/s10877-022-00842-0).
  Abstract read. Its identifiers and its 0.2–6 L/min protocol range were
  re-confirmed against the PubMed record on 2026-09-20 (`PL-NM7X`). No full text
  was on PubMed Central, and the private reference corpus did not hold it when
  checked the same day. On two workstations, the study validates Gas Man, which
  this simulator is compared against. It reports materially worse agreement
  during wash-in than during maintenance. The flow range was set by the protocol
  and is not evidence of the flows used in practice (§ "(a2)").
- Hendrickx JFA, De Wolf AM. The anesthesia workstation: quo vadis? *Anesth
  Analg.* 2018;127(3):671–675.
  PMID 29239956; [DOI 10.1213/ANE.0000000000002688](https://doi.org/10.1213/ANE.0000000000002688).
  Metadata only. The full text was not reachable. It is the review to read first
  when continuing this survey. No figure here is cited to it.
- Jain RK, Swaminathan S. Anaesthesia ventilators. *Indian J Anaesth.*
  2013;57(5):525–532.
  PMID 24249886; [DOI 10.4103/0019-5049.120150](https://doi.org/10.4103/0019-5049.120150).
  Abstract read. The article is open access.
- Kalmar AF, Van Der Vekens N, De Rydt F, Allaert S, Van De Velde M, Mulier J.
  Minimizing sevoflurane wastage by sensible use of automated gas control
  technology in the Flow-i workstation: an economic and ecological assessment.
  *J Clin Monit Comput.* 2022;36(6):1601–1610.
  PMID 34978655; [DOI 10.1007/s10877-021-00803-z](https://doi.org/10.1007/s10877-021-00803-z).
  **Read at full text 2026-09-20** from PubMed Central (PMC9637609) for
  `PL-NM7X`. The sentence quoted in § "(a2)" closes the abstract, and the body's
  Conclusion repeats it without the parenthesised 2 L/min figure. The study is a
  retrospective review of one centre's records, with 25 cases per group, on
  Flow-i workstations alone. It compares automated gas control (AGC) speed
  settings with a fixed 2 L/min group and a manual minimal-flow group. Because
  of that design, it can be cited as a recommendation about what practice should
  be and as evidence that 2 L/min is the conventional comparator, but not as a
  measurement of which flows are used.
- Križmarić M, Maver U, Zdravković M, Mekiš D. Effects of the reservoir bag
  disconnection on inspired gases during general anesthesia: a simulator-based
  study. *BMC Anesthesiol.* 2021;21(1):32.
  PMID 33522905; [DOI 10.1186/s12871-021-01256-2](https://doi.org/10.1186/s12871-021-01256-2).
  Abstract read.
- Meyer J-U, Kullik G, Wruck N, Kück K, Manigel J. Advanced technologies and
  devices for inhalational anesthetic drug dosing. In: Schüttler J, Schwilden H,
  eds. *Modern Anesthetics.* Handbook of Experimental Pharmacology vol. 182.
  Berlin: Springer; 2008:451–470. **Read at full text 2026-09-19 from the
  private reference corpus** (`stuthedew/open-anesthesia-sim-references`,
  file `modern_anesthetics/08_Part_IV_Ch5-6_Index`). Every passage quoted above
  is from printed pages 453–468, and the page markers in that file show the page
  of each. Dräger authors wrote the chapter, so it is the manufacturer's own
  account of its devices. For any measured quantity, it is still tier 2.

**Evidence that a machine was in service and studied, used only for the
selection criterion.**

- Bashraheel MK, Eerlings SA, De Wolf AM, et al. Memsorb, a novel CO2 removal
  device part I: in vitro performance with the Zeus IE. *J Clin Monit Comput.*
  2022;36(6):1591–1600.
  PMID 35089526; [DOI 10.1007/s10877-021-00802-0](https://doi.org/10.1007/s10877-021-00802-0).
- Hoffmann M, Jouwena J, De Wolf AM, Carette R, Lauwers RSH, Hendrickx JFA. In
  vitro performance of a charcoal-capturing device with desflurane.
  *Anesthesiology.* 2025;142(6):1038–1046.
  PMID 40073301; [DOI 10.1097/ALN.0000000000005445](https://doi.org/10.1097/ALN.0000000000005445).
  Abstract read. Its identifiers and its 0.3–6 L/min bench protocol were
  re-confirmed against the PubMed record on 2026-09-20 (`PL-NM7X`). No full text
  was on PubMed Central, and the private reference corpus did not hold it when
  checked the same day. The study is *in vitro*, with a 2 L test lung, and is
  **not** evidence about clinical practice.
- Jakobsson P, Lindgren M, Jakobsson JG. Wash-in and wash-out of sevoflurane in
  a test-lung model: a comparison between Aisys and FLOW-i. *F1000Res.*
  2017;6:389.
  PMID 28529707; [DOI 10.12688/f1000research.11255.2](https://doi.org/10.12688/f1000research.11255.2).
- Leijonhufvud F, Jöneby F, Jakobsson JG. The impact of fresh gas flow on
  wash-in, wash-out time and gas consumption for sevoflurane and desflurane,
  comparing two anaesthesia machines, a test-lung study. *F1000Res.*
  2017;6:1997.
  PMID 29333245; [DOI 10.12688/f1000research.13064.2](https://doi.org/10.12688/f1000research.13064.2).
- Zumsande S, Thoben C, Dennhardt N, et al. Rebounds of sevoflurane
  concentration during simulated trigger-free pediatric and adult anesthesia.
  *BMC Anesthesiol.* 2023;23(1):196.
  PMID 37291484; [DOI 10.1186/s12871-023-02148-3](https://doi.org/10.1186/s12871-023-02148-3).

**Standards, named by number and edition only; texts not reachable.**

- ISO 80601-2-13:2022, *Medical electrical equipment — Part 2-13: Particular
  requirements for basic safety and essential performance of an anaesthetic
  workstation*, second edition, 2022-04; Amendment 1:2026.
- ISO 5360:2016, *Anaesthetic vaporizers — Agent-specific filling systems*,
  fourth edition, 2016-02-15. The edition and date are those that a national
  adoption record (CSA) gives for this standard.

**Neither standard was read, and nothing in this document rests on what either
requires.** Their identifiers come from catalogue and adoption records that a
web search found. On 2026-09-19 the network used for this survey refused
requests to `www.iso.org`, `webstore.ansi.org` and `standards.iteh.ai`, and it
still did on 2026-10-06. The one query sent to `search.worldcat.org` on
2026-09-19 was answered but rate-limited. The two entries are pointers for
anyone who can open the texts.
