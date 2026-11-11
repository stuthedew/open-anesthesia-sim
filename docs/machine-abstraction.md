# The anesthesia-machine abstraction: what a machine profile is

## What this document is, and what it is not

`ROADMAP.md` § "Planned milestones" numbers the milestones the project plans.
Its item 1, "Modular anesthesia-machine abstraction with interlocks", commits
to an abstraction under which **a real commercial machine can be added as a
module**. This document is the design for that abstraction, and answers the
seven questions in its design brief, the work item `PL-FG9D`. In this design
the module is a **machine profile**: one data file under
`src/anesthesia_sim/data/machines/` that gives the machine's values and names
the behaviors it uses from a fixed set in `core/`. The simulator models one
breathing system today, the reference breathing system described in
§ "The reference breathing system", so the first real machine added is the
"second machine" of Question 7.

A survey written for this design, `docs/machine-survey.md`, found which
differences between real machines affect a number this simulator computes. This
document cites the survey's findings by the labels of its § "The variables":
(a1) and (a2) for differences in data, and (b1) to (b11) for the rest. Each
label is given with its finding in words.

The sections come in this order:

- § "A machine changes only two rates and one volume" gives the finding the
  whole design rests on.
- Question 3: how a machine composes with the existing core, that is, what the
  simulator's existing code owns and what each machine supplies.
- Question 1: where the line falls between a difference that is a stored value
  (a parameter) and one that needs its own formula (a strategy).
- Question 2: what keeps the machine profile small.
- § "Which values belong to the machine, the run and the model".
- Question 4: validation and provenance per machine.
- § "Fresh gas inlet position is not modelled".
- Question 5: naming a real machine in the interface.
- Question 6: every difference between machines traces to a named field.
- Question 7: what the second machine costs.
- § "What this design does not decide" lists the open matters.

**Mostly design, with two parts built.** This document changes no code.
`ROADMAP.md` split the building of it in two on 2026-09-20. Item 40, "An
anesthesia machine as a config file", builds the framework: loading a profile
from its data file, and refusing one that is not admissible (Question 4). Item 1
keeps the interlocks and the solver work: the strategy registry, computing the
two rates from it, and splitting the circuit volume between machine and run.
"The machine milestone" below means the two together. Where a decision below
implies work, the work is named and left to them. Two parts are already in the
code, and § "What is built so far" records them: a machine's deliverable fresh
gas flow range (`PL-8PS6`) and the flow a run opens at when a profile states
none (`PL-QW19`). `docs/MODEL.md` specifies both, in § "Runtime controls" and
§ "Parameter provenance".

**Not held to the tree.** `docs/MODEL.md` specifies the model *as implemented*
and its § "How this document is held to the tree" binds every live assertion in
it to something a script can resolve. The unbuilt parts of this design would be
unresolvable assertions inside that bound document, so the design sits beside
`docs/machine-survey.md` instead, and `docs/MODEL.md` gains each statement when
the machine milestone builds it.

## A machine changes only two rates and one volume

**A machine contributes exactly two rates and one volume** to the system
matrix: to the breathing circuit's row, and to the two rows that count the
agent delivered and exhausted. It changes nothing else in the model. The two
rates are the agent delivery rate $`\dot m_{\mathrm{in}}`$ and the circuit gas
removal rate $`\dot m_{\mathrm{out}}`$, both in L/s. The volume $`V_C`$ is the
gas volume of the whole breathing circuit: the machine's apparatus plus the
patient circuit (the disposable limbs and Y-piece). The machine supplies only
the apparatus part, and § "Which values belong to the machine, the run and the
model" says where the rest comes from. Every difference the survey found that
this model can represent falls under one of the three. The survey found two it
cannot represent, fresh gas inlet position (b7) and ventilator drive (b6), and
this design declines both in § "Fresh gas inlet position is not modelled" and
§ "What this design does not decide".

The model is one system matrix $`A`$ over nine states, built in
`src/anesthesia_sim/core/governing_equations.py`. Six states are the fractions
of agent in the circuit, the alveolar gas, the mixed venous blood and the three
tissue groups. Two accumulate the litres of agent vapour delivered into the
circuit ($`M_{\mathrm{delivered}}`$) and exhausted from it
($`M_{\mathrm{exhausted}}`$); their rows are the accounting rows. The ninth is
the constant one, written $`\mathbf 1`$, through whose column a term that does
not depend on any state enters. The alveolar, venous and tissue rows are the
patient rows. The exact propagator is $`\exp(A\,\Delta t)`$. The symbols are those of `docs/MODEL.md`
§ "Symbols": $`\dot V_F`$ is the fresh gas flow, $`\dot V_A`$ the alveolar
ventilation, $`F_D`$ the delivered fraction set at the vaporizer, $`F_I`$ the
inspired fraction and $`F_A`$ the alveolar fraction. Five entries of the matrix
belong to the breathing circuit. The circuit's own row has three of them:

$$
A_{F_I,F_I} = -\frac{\dot V_F + \dot V_A}{V_C},\qquad
A_{F_I,F_A} = \frac{\dot V_A}{V_C},\qquad
A_{F_I,\mathbf 1} = \frac{\dot V_F F_D}{V_C}
$$

with two more in the accounting rows,
$`A_{M_{\mathrm{delivered}},\mathbf 1} = \dot V_F F_D`$ and
$`A_{M_{\mathrm{exhausted}},F_I} = \dot V_F`$.

**$`\dot V_F`$ appears in four of those five entries, and it does two
different jobs there**:

- **Delivery** is $`\dot V_F F_D`$, the litres of agent vapour arriving per
  second. It is a constant over the step, so it enters through the column of
  the unit state $`\mathbf 1`$.
- **Removal** is $`\dot V_F`$, the litres of mixed circuit gas leaving per
  second at the current fraction $`F_I`$. It is a coefficient on $`F_I`$, so it
  enters the diagonal and the $`M_{\mathrm{exhausted}}`$ row.

Today one symbol carries delivery and removal, because they are one stream on
the reference machine, a semi-closed circle with a bypass vaporizer. The survey
found four ways a machine departs from it. Each changes the formula for one of
the two rates, and the first three give the two rates different formulas.
Whether a given machine departs in a given way is recorded per machine in the
survey, and for the sampling configuration (b10) it is unknown for every
machine:

| Survey entry | Delivery | Removal |
| --- | --- | --- |
| (b3) direct injection into the circle | independent of $`\dot V_F`$ | unchanged |
| (b11) surplus gas valve closed | same formula, but $`\dot V_F`$ becomes an output: the patient's total uptake | zero |
| (b10) sidestream sample, not returned | unchanged | $`\dot V_F + \dot V_S`$ |
| (b1) dial is not the delivered concentration | $`F_D`$ is a function, not the dial | unchanged |

Written with the two rates, four of the five entries become

$$
A_{F_I,F_I} = -\frac{\dot m_{\mathrm{out}} + \dot V_A}{V_C},\qquad
A_{F_I,\mathbf 1} = \frac{\dot m_{\mathrm{in}}}{V_C},\qquad
A_{M_{\mathrm{delivered}},\mathbf 1} = \dot m_{\mathrm{in}},\qquad
A_{M_{\mathrm{exhausted}},F_I} = \dot m_{\mathrm{out}}
$$

The ventilation entry $`A_{F_I,F_A}`$ is unchanged, because it belongs to the
patient.

**On the reference machine, $`\dot m_{\mathrm{in}} = \dot V_F F_D`$ and
$`\dot m_{\mathrm{out}} = \dot V_F`$, so the matrix is entry-for-entry what it is
today.** So the change that introduces the two rates, which item 1 makes,
changes no computed value. The existing reference tests in `tests/reference/`
will show it by passing with their expected values unchanged.

### Three admissibility conditions

The three conditions below decide which machines fit this abstraction. The
exact propagator, $`\exp(A\,\Delta t)`$, needs the first two, and rolling back a
failed step needs the third. If a machine fails any one, it does more than
reduce accuracy: it breaks a guarantee that the solver rests on. The volume a
machine supplies needs no condition of its own here, because every volume the
model holds is already checked to be finite and inside a stated range when it
is built (`CompartmentVolume` in `core/numerical_envelope.py`).

1. **Linear and time-invariant across a step.** $`\exp(A\,\Delta t)`$ is exact
   only because every setting is held constant within the step. When a
   machine's rates change with the state *during* the step, the matrix $`A`$
   becomes a function of the state $`y`$ and the propagator stops being exact.
   One such machine has a closed-loop controller that reads $`F_A`$ and moves
   the dial.
2. **Nonnegative off-diagonal entries in $`A`$ (a Metzler matrix).** They keep
   every compartment from going negative. The matrix-exponential routine
   (`core/matrix_exponential.py`) requires them. Both $`A_{F_I,\mathbf 1}`$ and
   $`A_{M_{\mathrm{exhausted}},F_I}`$ are off-diagonal, so **both rates must be
   nonnegative and finite**. A machine must not remove agent by delivering a
   negative rate.
3. **Stateless.** A failed step is rolled back to the run state that the
   breathing circuit captured (`BreathingCircuit.capture_state()`). If a
   machine kept state of its own, such as a controller's integrator or a
   vaporizer's thermal mass, that state would have to be captured too.
   Otherwise a rollback would silently restore a different machine from the
   one the step began with. A machine with state of its own therefore needs a
   design change first, to extend what is captured and restored.

Automated end-tidal control fails the first and third conditions: its
controllers read the patient's state during the step, and one of them runs a
simplified patient model of its own, which is state outside the run's (survey
entry (b4), automated end-tidal or target control). So it is planned
separately, as planned-milestone item 5, "Automated end-tidal control", rather
than as a machine in this abstraction.

## Question 3: how a machine composes with the existing core

**The machine is a boundary condition.** It supplies the delivery and removal
rates above and the apparatus volume. It appears nowhere in the state vector
and holds no agent. It has no way to write a patient row of the system matrix,
so adding a machine cannot change one. That is true by construction rather than
by review, and it is the guarantee that the design brief asks for (`PL-FG9D`).

In this design, which the matrix suggests, the machine supplies the fresh gas
exchange: delivery and removal integrated over one step. The circuit code
already has a record for the exchange (`FreshGasExchange`, which
`advance_fresh_gas()` in `core/circuit.py` returns). Today the circuit computes
that record from its own fields, and so hard-codes one machine.

A machine could instead contain or configure the circuit, and both fail:

- **A machine that *contains* the circuit** makes the circuit one of its
  components. Every new machine would then reach into the compartments of the
  validated uptake model (`AgentUptakeSystem`). The design brief asks that this
  be avoided (`PL-FG9D`).
- **A machine that *configures* the circuit** sets the circuit's volume and
  fresh gas flow (`circuit_volume_l`, `fresh_gas_flow_l_min`) at construction
  and then plays no further part. Today's code does this implicitly: the uptake
  model reads `data/machines/reference_circle_system.json` when it is built for
  an agent (`AgentUptakeSystem.for_agent()`). This arrangement cannot express
  direct injection (b3) or a closed surplus gas valve (b11), because those
  change the *form* of the exchange rather than its coefficients.

## Question 1: where the parameter/strategy line falls

**A difference between machines is data (a parameter) when it changes the
*value* of the delivery rate, the removal rate or the apparatus volume. It is
behavior (a strategy) when it changes the *formula* producing them.**

The line is decidable rather than a matter of judgment. A machine affects the
simulation only through those three quantities (§ "A machine changes only two
rates and one volume"). So each difference the model can represent either
gives one of them a value, or selects which expression produces a rate. The
two differences the model cannot represent are neither, and that section names
them.

Data files may not hold executable equations (`CLAUDE.md`), so a strategy
cannot go in one. The design gives it a place of its own.

### The closed set of behaviors

A machine's behavior has three independent slots: delivery, removal and dial
mapping. A named strategy from a registry in `core/` fills each slot. Item 1
builds the registry; until then each slot has the one path that today's code
hard-codes, as the Status columns below say. A machine profile names one
strategy for each slot, and cannot supply its own.

**A strategy is a pure function** of the profile fields it declares, the run's
current controls, and $`F_I`$, and it declares which fields it reads. Question
6's answer rests on that declaration: every difference between machines traces
to a named field.

**Two refusals apply to every strategy, recorded so that they are not proposed
again.** A strategy may not read a field it did
not declare. It may not be added to the registry without an entry in the tables
below, because the registry *is* the closed set. A registry member that this
document does not list is the "too permissive" failure that the design brief
names (`PL-FG9D`).

#### Delivery

The delivery strategy sets $`\dot m_{\mathrm{in}}`$:

| Name | Rate | From | Status |
| --- | --- | --- | --- |
| `fresh_gas_bypass` | $`\dot V_F F_D`$ | today's model | implemented, as the only path |
| `in_circle_injection` | injector rate, independent of $`\dot V_F`$ | (b3), agent injected into the circle | planned-milestone item 4, "Direct agent injection into the circuit" |

Dräger's Zeus IE workstation has both delivery modes. Its *fresh gas mode* is
`fresh_gas_bypass` on the manufacturer's own description — Meyer et al.: *"In
this dosing mode the agent dosage performance is equivalent to a conventional
vaporizer."* **A machine with two delivery modes is two profiles, one per
mode**, because a profile names one strategy for each slot. Half of the Zeus
is therefore already built. Switching mode during a run would need a run
control that changes the delivery strategy, which this design does not have;
adding one is a design event under Question 7.

#### Removal

The removal strategy sets $`\dot m_{\mathrm{out}}`$:

| Name | Rate | From | Status |
| --- | --- | --- | --- |
| `fresh_gas_displacement` | $`\dot V_F + \dot V_S`$ | today's model, plus (b10), sidestream sample flow | implemented, with $`\dot V_S = 0`$ |
| `closed_circuit` | $`\dot V_S`$ | (b11), surplus valve shut | not implemented |

$`\dot V_S`$ is the flow of circuit gas that a sidestream gas monitor draws and
does not return to the circuit.

An implementation of `closed_circuit` owes a second thing besides the removal
rate. With the surplus gas valve shut, the fresh gas flow equals the patient's
total uptake, so it must compute $`\dot V_F`$ instead of taking it from the
dial. Paired with `fresh_gas_bypass` at a dialled flow, the vaporizer keeps
adding agent at that flow, and the run gives a plausible curve and a wrong
number. Computing the total uptake needs a patient who consumes oxygen and a
variable alveolar volume, which this model does not have (`docs/MODEL.md`
§ "Breathing circuit").

The sample draw $`\dot V_S`$ is *data* rather than a third strategy, because
one expression covers all three of the survey's sampling configurations: a
mainstream sensor and a returned sidestream sample both give
$`\dot V_S = 0`$, and a scavenged sidestream sample gives the sample flow. Two
formulas would be one formula and a branch nobody can see.

#### Dial mapping

The dial-mapping strategy produces $`F_D`$ from the dial position:

| Name | Mapping | From | Status |
| --- | --- | --- | --- |
| `variable_bypass` | dial is a partial-pressure fraction | today's model | implemented, as identity |
| `fixed_volume_percent` | dial is volumes percent | (b1), delivered concentration is not the dial setting; the Tec 6 | see below |

**The dial-mapping slot is where the design is put to the test, and that test
has not happened yet.** An item asks that the Tec 6 desflurane vaporizer be the
concrete second device class that the abstraction is designed against
(`PL-439V`). Meyer et al. state the difference in one sentence: *"The desflurane
vaporizer principle described here delivers a fixed volume percentage, making it
different from conventional vaporizers, which deliver fixed partial pressures."*
The two mappings differ by a factor of
$`P_{\mathrm{ambient}}/P_{\mathrm{reference}}`$. **This model fixes the ambient
pressure at one atmosphere, 760 mmHg, so in its present domain the two agree
everywhere** (`docs/MODEL.md` § "Assumptions", which `PL-5K5C` wrote). The slot
is real and its second member is named, but today the two mappings are a
declared coincidence, not a distinction. Only a model whose ambient pressure
can differ from 760 mmHg separates them, and no item or roadmap entry plans
one. Until one does, a profile that names `fixed_volume_percent` gets the same
numbers as one that names `variable_bypass`, and the test meant to tell the two
apart (`PL-439V`) passes on paper only.

How a vaporizer's output depends on fresh gas flow is **not** in the mapping,
and must not be quietly added to it. Hendrickx et al. measured it for the
vaporizer of the Datex-Ohmeda ADU (Anesthesia Delivery Unit), which the
survey's (b1) lists as GE's cassette vaporizer: output stayed within 10% of
the dial for isoflurane at 0.3–10 L/min, within 10% for sevoflurane at
0.5–5 L/min and within 13% for desflurane at 0.5–1 L/min, and deviated more
outside those ranges. It is a declared limitation of both strategies, and no
item or roadmap entry plans to model it. A flow-dependent correction fitted
here would move every wash-in ratio that `docs/MODEL.md` § "Published wash-in
and elimination validation test" checks against published data, without any
measurement of *this* model saying it should.

## Question 2: what keeps the machine profile small

**The admission rule is that a field exists only if something consumes it.** The
schema says what consumes each field and what the field changes. A field whose
consumer and effect nobody can state is not added: it is neither recorded as
interesting nor carried "because the manual has it".

**A field names its consumer, which is either the model or the comparison
table.** The comparison table sets one machine's fields beside another's, in
the machine's own panel that Question 5 describes; the work item `PL-WZVZ`
builds it. A field is admitted for the model as a coefficient in a declared
expression. A field for the table changes no number, but disambiguates one that
does, such as which of the survey's three sampling configurations (b10) a
$`\dot V_S`$ of zero *is*. That is the only ground on which a field for the table
is admitted. Naming the consumer stops this second ground becoming an escape
hatch for the first.

**If the admission rule is wrong, the cost is one field added late.** The rule
leaves out every specification in the survey's § "Ruled out". That section
has seven categories, and the survey put each there by its own test: none has a
path to a computed value under the model as it will be through the machine
milestone.
The rule is a mistake only if one of the seven turns out to change a number the
model computes. Each category already states the condition that would bring it
back, and those conditions are the monitoring for that mistake. The opposite
error costs a profile of specifications that nothing reads, which is the failure
that the design brief names (`PL-FG9D`).

**In testable form, adding a machine adds a row, not a column.** Once the
abstraction is right, a new machine is values for fields that already exist. A
machine that needs a *new field* or a *new strategy* is a design event: either
the survey missed an axis, or the field is trivia. Question 7 gives the order
in which each is added, and in both the survey comes first and the machine
last.

**A script will check that every profile has the same fields, each with a
consumer declared in the schema.** This is the column check. The testable form
above is decidable, so the check belongs in a script. The script reads every
file in `data/machines/`, and fails the moment a machine is added as a column.
As `CLAUDE.md` asks of a rule that a script can decide, the script runs from a
bare checkout with no virtualenv, returns the same result on every run, and
states its rule where a reviewer can read it. Building the script under
`tools/` is work for item 40.

**Unknown is not a value.** A machine whose apparatus volume is unknown cannot
be added yet, and it is never given a plausible apparatus volume instead. This
rule comes from the survey, and Question 4's second refusal enforces it when a
profile is loaded.

### The schema

Per field, matching what `data/machines/reference_circle_system.json` already
does and adding the two bindings the rules above need:

```text
value, unit                what the model reads
consumer                   "model" or "attribution" (the comparison table)
effect                     one clause: which rate or bound this changes
source, tier, adopted      docs/MODEL.md's source hierarchy, unchanged
```

The fields the survey's evidence admits. "Required" means a profile must give a
known value; an optional field may be `null`, which means the profile declares
nothing for it.

| Field | Consumer | What it changes | Survey |
| --- | --- | --- | --- |
| `apparatus_volume_l` | model | $`V_C`$, hence the circuit time constant $`\tau_C = V_C/\dot V_F`$ | (a1), apparatus gas volume |
| `deliverable_fresh_gas_flow_range` (optional) | model | the flow bound, intersected with the model envelope in `core/supported_ranges.py`; its floor is the machine's minimum total flow | (b8), flow bounds |
| `default_fresh_gas_flow_l_min` (optional) | model | the flow a run opens at, where the machine publishes one | (a2), default fresh gas flow |
| `agents` | model | which agents may be mounted at all | (b9), deliverable agents |
| `agent_limits` | model | per-agent dial maximum | (b2), dial range and maximum |
| `sample_gas_flow_l_min` | model | $`\dot m_{\mathrm{out}}`$ | (b10), sidestream sample flow |
| `sample_gas_configuration` | attribution | which sampling a zero means | (b10) |
| `delivery`, `removal`, `dial_mapping` | model | which strategy runs | (b3), (b11), (b1) |
| `not_modelled` | attribution | what this profile does not claim | Question 4 |

**Two of the survey's (b8) quantities are not fields.** A machine's minimum
total fresh gas flow is the floor of `deliverable_fresh_gas_flow_range`, and
`CLAUDE.md` keeps one copy of a fact, so it is never stored a second time
under its own name. A minimum oxygen flow has no consumer: this model carries
no oxygen, so it reaches nothing the model computes until a hypoxic guard
consumes it. A profile author stores neither.

The per-agent dial maximum (`agent_limits`) is one field, a mapping keyed by
agent, rather than a column per agent. Adding an agent adds a key inside every
profile, and that is work for the milestone that adds the agent, not machine
work.

**The maximum delivered concentration (`max_delivered_concentration_percent`)
is in the wrong place today**, and the survey proves it: desflurane's 18% is the
calibrated maximum of the Tec 6, which Johnston et al. characterised *"from 1%
to 18%"*, and `docs/MODEL.md` already names that provenance. Nothing about
desflurane itself sets its maximum at 18%. It belongs on the (machine, agent)
pair, as `agent_limits`. Today it is a field of each agent's data file under
`src/anesthesia_sim/data/agents/`, and no machine limits the dial. Moving it
from there into `agent_limits` is the data migration that the machine
milestone makes. Until then nothing displayed changes.

## Which values belong to the machine, the run and the model

The abstraction separates three things one file currently holds together.

**The machine owns what a machine specifies.** Apparatus volume, flow range and
floor, agents it can mount, per-agent dial maxima, sampling, and the three
strategy names.

**The run owns its opening conditions**: the opening fresh gas flow, the opening
dial position, and the patient circuit volume. None of these is a machine
specification, and the reason differs for each. A machine that does publish a
startup flow may state it in the optional `default_fresh_gas_flow_l_min`, and
the run then opens at it; § "What is built so far" records how a run opens
when the profile states none.

- **Opening fresh gas flow.** An earlier item deferred this field's home to
  this design, reasoning that a fresh gas flow is a machine setting rather than
  a patient or agent property (`PL-8DJ7`). That
  rightly rules out the patient and the agent, but does not settle where the
  field lives. The survey supplies the fact that does: **no reachable source
  states a startup fresh gas flow for any surveyed machine.** A per-machine
  field would therefore be `unknown` on every real profile. Question 4's second
  refusal rejects a machine with an unknown required field, so a required
  machine field would either block every machine or force each one to
  fabricate a number. The opening flow is instead an opening condition of a
  run: a teaching choice, as the provenance note of the reference breathing
  system's data file (its `provenance_gap` field) already calls it. Where the
  field lives and what value it takes are independent questions, and a
  separate item decides the value (`PL-NM7X`).
- **Opening dial position** is the same kind of condition, and the code already
  treats it so: building the uptake model for an agent
  (`AgentUptakeSystem.for_agent()`) starts the vaporizer at that agent's 1 MAC.
  That is a convention about where a run opens, not a property of the agent or
  of any device.
- **Patient circuit volume.** The reason comes from the survey's section on
  apparatus volume (a1). $`V_C`$ is apparatus *plus* patient circuit, and the
  patient circuit is a consumable chosen per case. A machine profile cannot own
  $`V_C`$ outright.

**The apparatus volume (`apparatus_volume_l`) and the shipped circuit volume
(`circuit_volume_l`) are two quantities, not two names for one** (project
owner, 2026-09-27, ratified, over recording `circuit_volume_l` as the apparatus
alone, `PL-HGB6`). The apparatus volume is the machine's half of the split this
section describes. It includes the absorber and excludes the disposable patient
circuit, which is how the survey's section (a1) records every figure it found.
The circuit volume is $`V_C`$ whole, apparatus plus patient circuit, because the
model has one well-mixed gas compartment in front of the patient and the limbs
and Y-piece have nowhere else to be. A profile written today from Shin et al.'s
figures for a Perseus A500 therefore stores the 3.3 L that includes the patient
circuit, never the 2.1 L apparatus figure. The 2.1 L would give a
$`\tau_C = V_C/\dot V_F`$ of 31.5 s at 4 L/min, where 49.5 s is right. **The two
names stay distinct until the split is made:** the milestone that implements
this design moves the patient circuit to the run. From then, a machine profile
carries `apparatus_volume_l`, and the run supplies the rest of $`V_C`$. Today's
meaning of `circuit_volume_l` is written where a profile author reads it: in the
schema docstring, the data file and `docs/MODEL.md` (`PL-TBMX`).

**The model keeps its envelope.** The bounds in `core/supported_ranges.py` are
the domain the compartment model is claimed over, and they stay exactly where
they are. The effective limit on a control is the **intersection** of the model
envelope and the machine's deliverable range, each with its own name, source
and refusal message. The intersection is what stops a machine profile silently
widening the model's claimed validity. This design adopts that framing unchanged
from an earlier item (`PL-8PS6`).

### What is built so far

**Built, for the fresh gas flow alone, on 2026-09-20** (`PL-8PS6`). The
intersection of the model envelope and the machine's deliverable range,
described in the paragraph above, is in the tree:
`deliverable_fresh_gas_flow_range` is a field on `BreathingCircuitParameters`
carrying a `DeliverableFreshGasFlowRange`, and `BreathingCircuit` holds both
claims and refuses in each one's own words. `reference_circle_system.json`
declares `null`, the survey's (b8) having found no reachable range for any
surveyed machine, so the envelope alone binds and nothing displayed changed.
Two consequences for the machine milestone's own work, recorded here because
this document is where its scope is read. The field is **optional, defaulting to `None`**,
which means *declares no range* rather than *unlimited*; Question 4's refusal
of an `unknown` applies to required fields, and this is not one. And neither
of the survey's other (b8) quantities was built beside it, for the reasons
under § "The schema".

**Built, for the opening fresh gas flow, on 2026-09-27** (`PL-QW19`), which
brings the tree into line with § "The run owns its opening conditions" above.
`default_fresh_gas_flow_l_min` stays on the machine profile as the optional
field in § "The schema", **defaulting to `None`**, read as *this profile states
no startup flow* and never as *this machine has none*. So Question 4's refusal
of an `unknown` does not reach it: a real profile states a startup flow only
where a source publishes one, and no source the survey reached gives one for
any machine. A run built from a profile that states none
opens at `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN` in `core/circuit.py`, the
4.0 L/min `reference_circle_system.json` stores, whose authority is that file's
teaching-default rationale and not any source. The file keeps its value and its
provenance row, so nothing displayed changed, and a profile whose declared
deliverable range excludes the fallback is refused when the run is built, as a
stated flow outside the range would be. The object that would own all three
opening conditions was not built, and this did not need it: the dial already
opens at the agent's 1 MAC by convention, the patient-circuit volume stays
inside `circuit_volume_l` until item 1's split, and the object, once built,
subsumes the fallback without undoing it.

### The reference breathing system

**The reference profile is a breathing system, not a machine, and stays one.**
Its file, `reference_circle_system.json`, is named for what it is. There the
circuit volume
(`circuit_volume_l`) of 6.0 L is the assembled total of apparatus and patient
circuit, for three reasons:

1. The model has one well-mixed gas compartment in front of the patient, so the
   limbs and Y-piece can only be inside $`V_C`$, as the survey's section (a1)
   says.
2. Targ et al. measured 9.86 L by filling with water their whole assembled
   circle system, with a latex reservoir bag at the Y-piece standing in for
   the patient's lungs. The data file's note on that source (the `note` of
   its Targ entry) does not adopt the figure, chiefly because of the bag.
   That system's corrugated limbs and Y-piece were part of what was measured,
   so the note's "the apparatus alone" meant without the lung, not without the
   hoses, and the note now says so (`PL-TBMX`). The note adds the reference
   adult's 2.5 L alveolar compartment, the lung, to the stored figure before
   setting the sum against 9.86 L. The comparison therefore bears on counting
   a lung twice, and says nothing about how the 6.0 L divides between
   apparatus and patient circuit.
3. `docs/MODEL.md` compares the 6.0 L with Shin et al.'s totals that include the
   patient circuit, the Primus's 5.9 L, rather than with their apparatus figures.

**No source divides the 6.0 L between apparatus and patient circuit**, so
splitting it would invent two numbers where one is recorded. The profile
therefore keeps the stored figure. Its provenance note (`provenance_gap`)
declares that the figure is the sum (`PL-TBMX`). Real
machines are added beside the reference profile, not made by retrofitting it
into a machine it never claimed to be. Once the machine and the patient
circuit get separate volumes, a profile built from Shin et al.'s figures will
store a true apparatus volume and take its 1.2 L patient circuit from the
run. Until then, such a profile stores the total with the patient circuit, as
the paragraph on the two volumes above says.

## Question 4: validation and provenance per machine

**A machine profile with no provenance fails to load rather than runs.** The
requirement comes from the item behind this design (`PL-FG9D`), and follows
from `CLAUDE.md`'s preference for an obvious failure state over a
plausible-looking number. The profile loader that item 40 builds in
`core/parameters.py` refuses a profile that:

1. **carries a field with no `source` and no entry in a `provenance_gap`** —
   the discipline `reference_circle_system.json` already meets, and the reason
   that file exists;
2. **carries `unknown` in a required field the model reads** — the survey's
   rule, and the honest statement that most surveyed machines cannot be added
   yet. An optional field states that the profile declares nothing with
   `null`, never with `unknown` (§ "The schema");
3. **names a strategy not in the registry** — the closed set, enforced;
4. **declares an empty `not_modelled` list**; or
5. **declares a `schema_version` the loader does not know.**

Nothing in this adds vocabulary. `tier` and `adopted` are `docs/MODEL.md`
§ "Source hierarchy"'s, checked by `make check` against the existing closed
vocabulary, and a machine constant is held to the same three tiers as a
partition coefficient: a measurement outranks a specification sheet, and a
specification sheet is not a measurement. The survey already applies that
ruling to itself — Shin et al.'s apparatus volumes are recorded tier 2 because
that paper carries them from Dräger's manuals rather than measured them.

Refusal 4 is the one worth arguing for. **Every machine has a non-empty
`not_modelled` list, and the survey is what proves it**: fresh gas inlet
position, ventilator drive, decoupling and the control loop all reach a number
and none is represented here. A profile claiming otherwise is claiming a
fidelity the model does not have, so an empty list is a defect rather than a
tidy result — and requiring it non-empty makes the omission a positive
statement the author had to write, which is what Question 5 then displays.

## Fresh gas inlet position is not modelled

**Decline to represent internal topology, and say so where a machine is
chosen.** Two machines differing only in inlet position are, in this model, the
same machine — and the interface states that rather than offering two names
that produce one curve. Nothing in the interface states it yet: the machine
chooser and the machine's own panel that carry the statement are built by
the machine milestone and by the comparison table's item (`PL-WZVZ`), and the
test that the statement is on screen belongs to that work.

**The decision not to represent inlet position is an instance, not a rule, and
its condition is named.** It stops being true when either of two things
happens, and both let inspired gas differ from mean circuit gas. One is
planned-milestone item 39, "Gas-phase conditions for each compartment", which
`ROADMAP.md` names as where the circuit's internal topology would go. The other
is a multi-limb circuit entering the model by any other route.
Written as a rule it would outlive its own evidence and be obeyed by sessions
that were not here. The statement in the interface is a different matter: the
last paragraph of this section says why it outlives the decision.

The survey's headline finding is that **apparatus volume alone does not explain
the measured differences between machines**, and its sharpest instance is
Fukuda et al.'s randomised patient study: moving only the fresh gas inlet
significantly raised the inspired/delivered ratio of isoflurane and of
sevoflurane during low-flow anesthesia. $`F_I/F_D`$ is the ratio this model's
circuit equation *is*, and a machine changed it with volume held fixed.

A single well-mixed compartment has no place to put that. The survey named
three options and refused one. Besides the decline above, they are:

- **Refused: fold it into an effective volume.** The survey's refusal stands
  and is worth restating, because it is the option an implementation reaches
  for. Calibrating a volume to reproduce observed kinetics would fit the curves
  and attribute to volume a difference volume did not cause. `PL-WZVZ`'s table
  would then print a sourced-looking number no measurement supports, which is
  the exact failure that table exists to prevent.
- **Not now: represent inlet position.** A multi-limb circuit separates inspired
  gas from mean circuit gas. Lerou and Booij's system model represents an
  actual circle-absorber breathing system rather than an idealized one (Lerou
  2001, in § "Sources"), and under a model of that kind the two become
  distinct states, so this model's single $`F_I`$ stops describing both.
  `docs/MODEL.md` § "Model boundary" already names that consequence, and the
  departure has to be recorded there before the model is extended that way.
  Representing inlet position changes the model boundary, so it belongs to
  planned-milestone item 39, not to item 1.

**Declining is not merely the cheap option: it is needed under *either*
answer.** Even once planned-milestone item 39 is built, a machine whose inlet
position is unknown still needs the interface's statement that inlet position
is not modelled. Every surveyed machine is such a machine, except the two that
Fukuda et al. instrumented. Building item 39 first would change which machines
the statement covers, not whether the statement is required.

## Question 5: naming a real machine in the interface

**Decided (project owner, 2026-09-20, ratified, recorded in `PL-FG9D`)**, on
this session's recommendation and over naming the machine by its trade name in
the running interface. It is what a learner sees, so the decision was theirs;
the case below is the one they ratified rather than one they authored, which is
the distinction `CLAUDE.md` asks to be recorded — **ordinary evidence reopens it**:
a measurement, a cost this case did not carry, or a constraint that appears
later.

**Show the archetype in the running interface, and attach the trade name to the
parameter set.** The machine chooser and the dashboard name a machine by what
the model represents, such as
"circle system · 3.3 L with patient circuit · variable-bypass vaporizer". The
trade name appears in the machine's own panel, beside its parameters, its
sources and its `not_modelled` list. There it is a citation rather than a
claim.

**The decision binds the comparison table, planned-milestone item 1 and the
`not_modelled` list.** The item behind the comparison table between machines
(`PL-WZVZ`) builds that panel, so the table and the machine's own parameter set
are the same surface. A trade name may appear there and may not appear on a
curve, a chooser entry or a dashboard readout. For planned-milestone item 1,
that is a scope constraint, not a preference. The `not_modelled` list becomes
more than a provenance record: a trade name may appear only where that list is
on screen beside it.

Three facts decide where the trade name goes, and none is a matter of taste:

1. **The model reproduces a known-incomplete subset, and Shin et al. measured
   the shortfall.** Shin et al. found the Perseus A500 and Zeus IE
   indistinguishable on volume: 2.1 L against 2.0 L of apparatus, 3.3 L
   against 3.2 L with the 1.2 L patient circuit, and time constants of 6.6
   against 6.4 min at 0.5 L/min. The two still differed significantly in time
   to target, and Shin et al. attributed the remaining difference to inlet
   position, decoupling, ventilator drive and delivery mode. Every one of those
   is in this model's `not_modelled` list.
2. **The decline in § "Fresh gas inlet position is not modelled" makes some
   machines identical here.** Under a trade-name label the interface would
   offer two names that produce one curve, with nothing saying why. Under an
   archetype label it offers one entry, correctly.
3. **`CLAUDE.md`'s clinical-output standard already governs the choice.** The
   correct number with the wrong model identity is a presentation failure, and
   a learner who reads a trade name on a curve attributes the curve to the
   machine on the wall in their operating room.

The two other options are weaker:

- **Full trade name everywhere** makes the feature feel real, and users will
  ask for it. It claims the most and has the least support, and Shin et al.'s
  measurement argues directly against it.
- **Archetype only, no trade name anywhere** is safe but throws away the
  provenance: a reader cannot check a parameter against a manual for a machine
  nobody names.

The decision is the middle one because it keeps the trade name exactly where
the evidence for it is on screen.

## Question 6: every difference between machines traces to a named field

**Every difference a machine makes to a curve can be traced to declared
fields.** The item behind this design (`PL-FG9D`) asks for this as a constraint
on the design, not only on the display: *design so that the parameter set is the
explanation*. A machine affects the model only through the three quantities that
§ "A machine changes only two rates and one volume" names, and each comes from
declared fields:

- the volume $`V_C`$: once item 1 splits it, the apparatus volume
  (`apparatus_volume_l`) plus the run's patient-circuit volume. Until then the
  whole of $`V_C`$ is one stored field, the assembled circuit volume
  (`circuit_volume_l`);
- the inflow $`\dot m_{\mathrm{in}}`$: the `delivery` strategy, the
  `dial_mapping` strategy that produces the $`F_D`$ it reads, and the fields
  each declares;
- the outflow $`\dot m_{\mathrm{out}}`$: the `removal` strategy and the sample
  gas flow (`sample_gas_flow_l_min`).

**There is nowhere else for a difference to hide**, because the design forbids
two things: a strategy that reads an undeclared field, and one outside the
registry. Question 1 explains both.

**The comparison table between machines (`PL-WZVZ`) is therefore derived.** For
any two machine profiles, the fields that differ can be computed, and the
`effect` clause that the schema already requires says what each one does. A
derived table stays true, while one maintained by hand can go out of date.

**The design rules out a difference that nobody could explain to a learner.**
Such a difference would arise if a machine changed a result through something
unnamed, for example a default inside a strategy or a branch on an undeclared
field. The interface would then attribute it to the machine's trade name. That
is an unsafe display, and the item behind the comparison table (`PL-WZVZ`)
exists to prevent it. With this design, that item does not have to catch it.

## Question 7: what the second machine costs

A second machine falls into one of three cases, and only the first is a
data-entry task. The costs below are the target that the item behind this
design (`PL-FG9D`) asks for.

**A machine whose delivery, removal and dial-mapping strategies are all
already in the closed set: one data file and its provenance rows, and nothing
else.** The machine needs one JSON file under
`src/anesthesia_sim/data/machines/`, naming one strategy for each of the three
slots, with every field sourced and a non-empty `not_modelled` list. The
documentation check requires a provenance row in `docs/MODEL.md` for every
number in a data file, so the machine also needs one row there for each of its
numbers; `ROADMAP.md`'s item 1 counts those rows in this cost. **It needs no
change to `core/`, no change to any patient row and no new test of the
physics.** The physics is the matrix, which is already tested, and the new
machine can reach it only through the two rates and the volume. The checks
that a profile owes run over every file in `data/machines/`: the loader's
refusals under Question 4, and the column check under Question 2, "what keeps
the machine profile small". They therefore cover the new file without a test
of its own. The comparison table between machines (`PL-WZVZ`) is derived from
the profiles (Question 6), so nobody writes a row for it. The cost can be
checked: the diff touches one file under `data/machines/` and the provenance
rows in `docs/MODEL.md`.

**A machine needing a new strategy, in any of the three slots: a design event,
and a bounded one.** It is added in this order. The survey gains the entry for
the behavior, with its source. Then this document's closed set gains a row,
and the registry in `core/` gains one entry and one pure function, which
returns a rate or, for a dial mapping, a delivered fraction. Its tests show
that the result meets the three admissibility conditions: it is nonnegative
and finite, it is constant across a step, and it keeps no state. Only then is
the machine added. Such a machine changes `core/` by that entry and that
function, and changes no patient row and not the solver.

**A machine needing a new profile field: a design event that starts in the
survey.** The field is added to `docs/machine-survey.md` with the stated path
from it to a computed value, then to the schema with its consumer and effect,
then to every existing profile, and only then is the machine added, never the
other way round. Adding the field to every existing profile is the cost that
keeps the schema honest: a field added for one machine must be answerable for
all of them, or it is trivia.

**If the design cannot state what a second machine costs, it is not
finished.** That is the test set by the item behind this design (`PL-FG9D`).
The design states the cost, and the column check under Question 2 can verify
the statement.

## What this design does not decide

None of the following is settled. Each entry records what is already known, so
that nobody works it out again from scratch.

- **The value of the opening fresh gas flow.** It is the project owner's
  decision (`PL-NM7X`). Where the opening flow belongs is decided in
  § "Which values belong to the machine, the run and the model".
- **Whether the model gains an ambient pressure.** `docs/MODEL.md`
  § "Assumptions" fixes it at 760 mmHg (`PL-5K5C`), and no item or roadmap
  entry plans to vary it. Until one does, Question 1's § "Dial mapping" says
  what follows.
- **Flow-dependent vaporizer output.** No item or roadmap entry plans to model
  it. Question 1's § "Dial mapping" records it as a limitation of both mapping
  strategies, with Hendrickx et al.'s measurements (Hendrickx 2001, in
  § "Sources").
- **Ventilation, decoupling and the ventilator.** Fresh gas decoupling (b5) and
  ventilator drive (b6) have a path to a computed value only once the machine
  owns the ventilator, and this abstraction does not give it the ventilator.
  Ventilation stays a patient-side control. Decoupling would be a fourth
  strategy slot, opened by the milestone that moves the ventilator to the
  machine. No item or roadmap entry plans that move.
- **Automated end-tidal control.** It is left to planned-milestone item 5, for
  the reason that ends § "A machine changes only two rates and one volume".
- **Every `unknown` in the survey.** The survey records apparatus volumes, flow
  floors, agent lists and sample flows as unknown for the GE and Getinge
  machines, and for three of the five Dräger ones. Its § "What is missing, and
  how the next session gets it" names the manuals and the route. **These
  unknowns are a condition on each profile, not on this abstraction.**
  Question 4's refusal 2 rejects a profile with `unknown` in a required field
  the model reads, so such a machine stays out until its fields are known.
  That machine's manual is sought when its profile is built, not in advance
  (project owner, 2026-09-20). The design is complete without any of these values:
  meanwhile it runs on the reference profile by construction, not for want of
  evidence.

## Sources

Every source below except Lerou and Booij is cited in
`docs/machine-survey.md`, which records the retrieval route, the depth of
reading and the full bibliographic record for each, and remains the authority
for them. The Lerou and Booij entry gives its own route and depth. This list
names only the sources this document reasons from.

- Fukuda T, Fukunaga A, Toyooka H. *J Anesth.* 2006;20(4):268–273 — inlet
  position changes $`F_I/F_D`$ at fixed volume, the measurement behind
  § "Fresh gas inlet position is not modelled".
- Hendrickx JF, De Cooman S, Deloof T, et al. *Anesth Analg.*
  2001;93(2):391–395 — output against dial across fresh gas flow for the
  vaporizer of the Datex-Ohmeda ADU; used in Question 1's § "Dial mapping".
- Lerou JG, Booij LH. Model-based administration of inhalation anaesthesia.
  1. Developing a system model. *Br J Anaesth.* 2001;86(1):12–28. PMID
  11575385; [DOI 10.1093/bja/86.1.12](https://doi.org/10.1093/bja/86.1.12) —
  a system model whose breathing system is an actual circle-absorber system
  with a standing bellows ventilator, rather than an idealized one; used in
  § "Fresh gas inlet position is not modelled". Abstract read 2026-11-11
  through the PubMed MCP server, which holds no full text for it.
  `docs/MODEL.md` cites the same paper, read at full text on 2026-09-06.
- Johnston RV, Andrews JJ, Deyo DJ, et al. *Anesth Analg.* 1994;79(3):548–552 —
  the Tec 6 desflurane vaporizer characterised from 1% to 18%, the provenance
  of desflurane's 18% maximum dial setting; used in Question 2's
  § "The schema".
- Meyer J-U, Kullik G, Wruck N, Kück K, Manigel J. In: Schüttler J, Schwilden
  H, eds. *Modern Anesthetics.* Springer; 2008:451–470 — Dräger's Zeus IE
  workstation and its two dosing modes, the closed surplus gas valve, the gas
  module's sample draw, and the fixed-volume-percentage principle; used in
  Question 1.
- Shin HW, Yu HN, Bae GE, et al. *BMC Anesthesiol.* 2017;17(1):10 — the three
  Dräger apparatus volumes, and machines indistinguishable on volume that still
  differ significantly in time to target; used in § "Which values belong to the
  machine, the run and the model", Question 4 and Question 5.
- Targ AG, Yasuda N, Eger EI II. *Anesth Analg.* 1989;69(2):218–225 — the
  9.86 L that they measured by water filling for an assembled circle system
  with a reservoir bag standing in for the lungs, which the note on this
  source in the reference breathing system's data file reasons against; used
  in § "The reference breathing system".
