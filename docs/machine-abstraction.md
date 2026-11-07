# The anesthesia-machine abstraction: what a machine module is

## What this document is, and what it is not

This document is the design of a modular anesthesia-machine abstraction, meant
to let **a real commercial machine be added as a module**. The roadmap's first
planned milestone commits to that abstraction (`ROADMAP.md` planned-milestone
item 1). The design covers what a module is, what the base owns and what each
machine supplies, where the line between parameters and strategies falls, and
what adding a second machine costs. It builds on the machine survey
(`docs/machine-survey.md`), which found the differences between real machines
that change a number the simulator computes.

**This document changes nothing in `src/`.** The milestone's work includes the
machine classes, the interlocks, the data migration and each task that a
decision below names. This design makes the milestone possible to scope.

**This document is not checked against the repository.** The model document
(`docs/MODEL.md`) describes the model *as implemented*. A script checks that each
of its current statements links to something in the repository (`docs/MODEL.md`
§ "How this document is held to the tree"). This design is not implemented, so
its statements have nothing to link to. They join the model document when the
milestone implements them.

## The finding the whole design rests on

**A machine contributes exactly two rates and one volume** to the breathing
circuit's row of the system matrix, and nothing else anywhere in the model. The
two rates are the agent delivery rate $`\dot m_{\mathrm{in}}`$ and the circuit
gas removal rate $`\dot m_{\mathrm{out}}`$, both in L/s. The volume $`V_C`$ is
the space that the circuit gas occupies in the apparatus. Everything the survey
found falls under one of the three.

The model is one system matrix $`A`$ over nine states, built in
`src/anesthesia_sim/core/governing_equations.py`. Its exact propagator is
$`\exp(A\,\Delta t)`$. Five entries of that matrix involve the fresh gas flow
$`\dot V_F`$, and the breathing circuit's own row has exactly three:

$$
A_{F_I,F_I} = -\frac{\dot V_F + \dot V_A}{V_C},\qquad
A_{F_I,F_A} = \frac{\dot V_A}{V_C},\qquad
A_{F_I,\mathbf 1} = \frac{\dot V_F F_D}{V_C}
$$

with two more in the accounting rows,
$`A_{M_{\mathrm{delivered}},\mathbf 1} = \dot V_F F_D`$ and
$`A_{M_{\mathrm{exhausted}},F_I} = \dot V_F`$.

**$`\dot V_F`$ is doing two different jobs in those five entries**:

- **Delivery** is $`\dot V_F F_D`$, the litres of agent vapour arriving per
  second. It is a constant over the step, so it enters through the column of
  the unit state $`\mathbf 1`$.
- **Removal** is $`\dot V_F`$, the litres of mixed circuit gas leaving per
  second at the current fraction $`F_I`$. It is a coefficient on $`F_I`$, so it
  enters the diagonal and the $`M_{\mathrm{exhausted}}`$ row.

Today one symbol carries delivery and removal, because they are one stream on
the reference machine, a semi-closed circle with a bypass vaporizer. Every other
machine that the survey found separates them:

| Survey entry | Delivery | Removal |
| --- | --- | --- |
| (b3) direct injection into the circle | independent of $`\dot V_F`$ | unchanged |
| (b11) surplus gas valve closed | unchanged | zero |
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
today.** The change that introduces the two rates is safe to merge, because it
changes no computed value. The existing reference tests in `tests/reference/`
prove this with their expected values unchanged.

### Two admissibility conditions, both structural

The three conditions below decide which machines fit this abstraction. The
exact propagator, $`\exp(A\,\Delta t)`$, needs the first two. If a machine fails
either one, it does more than reduce accuracy: it breaks a guarantee that the
solver rests on.

1. **Linear and time-invariant across a step.** $`\exp(A\,\Delta t)`$ is exact
   only because every setting is held constant within the step. When a
   machine's rates change with the state *during* the step, the matrix $`A`$
   becomes a function of the state $`y`$ and the propagator stops being exact.
   One such machine is a closed-loop controller that reads $`F_A`$ and moves
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

Automated end-tidal control fails the first and third conditions, so it is
planned separately (planned-milestone item 5) rather than as a machine in this
abstraction.

## Question 3: how a machine composes with the existing core

**The machine is a boundary condition.** It supplies the two rates above and
the apparatus volume. It appears nowhere in the state vector, holds no agent,
and touches no patient row. Adding a machine cannot change a patient row,
because a machine has no way to write one. The item asks for this guarantee.

In this design, which the matrix suggests, the machine supplies the fresh gas
exchange: delivery and removal integrated over one step. The circuit code
already has a record for the exchange (`FreshGasExchange`, which
`advance_fresh_gas()` in `core/circuit.py` returns). Today the circuit computes
that record from its own fields, and so hard-codes one machine.

A machine could instead contain or configure the circuit, and both fail:

- **A machine that *contains* the circuit** makes the circuit one of its
  components. Every new machine would then reach into the compartments of the
  validated uptake model (`AgentUptakeSystem`). The item asks the design to
  avoid this.
- **A machine that *configures* the circuit** sets the circuit's volume and
  fresh gas flow (`circuit_volume_l`, `fresh_gas_flow_l_min`) at construction
  and then plays no further part. Today's code does this implicitly: the uptake
  model reads `data/machines/reference_circle_system.json` when it is built for
  an agent (`AgentUptakeSystem.for_agent()`). This arrangement cannot express
  (b3) or (b11), because those change the *form* of the exchange rather than
  its coefficients.

## Question 1: where the parameter/strategy line falls

**A difference between machines is data (a parameter) when it changes the
*value* of one of the three quantities. It is behavior (a strategy) when it
changes the *formula* producing them.**

A machine affects the simulation only through the three quantities, so each
difference either enters one of the two rate expressions as a coefficient or
selects which expression is used.

Data files may not hold executable equations (`CLAUDE.md`), so a strategy
cannot go in one. The design gives it a place of its own.

### The closed set of behaviors

A machine profile chooses its behavior in three independent slots: delivery,
removal and dial mapping. For each slot it names one strategy from a registry
in `core/`, and it cannot supply a strategy of its own. A strategy joins the
registry only with a row in its slot's table below. The registry is the closed
set, so a strategy that these tables do not list would make the set "too
permissive", the failure that the item names.

**A strategy reads only the profile fields it declares.** It is a pure
function of those fields, the run's current controls and $`F_I`$. Question 6
rests on what each strategy declares.

**Delivery** strategies set $`\dot m_{\mathrm{in}}`$:

| Name | Rate | From | Status |
| --- | --- | --- | --- |
| `fresh_gas_bypass` | $`\dot V_F F_D`$ | today's model | implemented, as the only path |
| `in_circle_injection` | injector rate, independent of $`\dot V_F`$ | (b3) | planned-milestone item 4 |

A machine with two delivery modes is described by two profiles, or by one
profile with a mode selection. One such machine is the Zeus IE, whose
*fresh gas mode* is already built as `fresh_gas_bypass`. The manufacturer's
own description, in Meyer et al., says: *"In this dosing mode the agent
dosage performance is equivalent to a conventional vaporizer."*

**Removal** strategies set $`\dot m_{\mathrm{out}}`$:

| Name | Rate | From | Status |
| --- | --- | --- | --- |
| `fresh_gas_displacement` | $`\dot V_F + \dot V_S`$ | today's model, plus (b10) | implemented, with $`\dot V_S = 0`$ |
| `closed_circuit` | $`\dot V_S`$ | (b11), surplus valve shut | not implemented |

The sample draw $`\dot V_S`$ is *data* rather than a third strategy, because
one expression covers all three of the survey's sampling configurations. A
mainstream sensor and a returned sidestream sample both give $`\dot V_S = 0`$,
and a scavenged sidestream sample gives the sample flow. A third strategy would
add nothing but a hidden branch on whether $`\dot V_S`$ is zero.

**Dial mapping** strategies turn the dial position into $`F_D`$:

| Name | Mapping | From | Status |
| --- | --- | --- | --- |
| `variable_bypass` | dial is a partial-pressure fraction | today's model | implemented, as identity |
| `fixed_volume_percent` | dial is volumes percent | (b1), the Tec 6 | see below |

**This slot is meant to test the design against a second device class, and for
now it does not.** The Tec 6 represents that class (`PL-439V`). Meyer et al.
contrast the two device classes: *"The desflurane vaporizer principle described
here delivers a fixed volume percentage, making it different from conventional
vaporizers, which deliver fixed partial pressures."* The two mappings differ by
a factor of $`P_{\mathrm{ambient}}/P_{\mathrm{reference}}`$. This model has no
ambient pressure, so a profile that names `fixed_volume_percent` gets the same
numbers as one that names `variable_bypass`. Recording the model's sea-level
assumption (`PL-5K5C`) will separate the two mappings.

**Neither dial mapping includes the flow dependence of vaporizer output.**
Hendrickx et al. measured it for both device classes: output is within 10% of
the dial setting for isoflurane at 0.3–10 L/min and within 13% for desflurane
at 0.5–1 L/min, and worse outside those ranges. The flow dependence stays a
declared limitation of both mappings until a milestone models it. Before that
milestone, do not add a flow-dependent correction to either mapping. A
correction fitted here would move every validated wash-in ratio without any
measured data showing that this model needs it.

## Question 2: what keeps the machine profile small

**A machine profile gains a field only when something consumes it.** The schema
records what consumes each field and what the field changes. A field without
that record is not added, even when it is interesting or appears in the
machine's manual.

**Only two things can consume a field.** The model consumes a field that is a
coefficient in one of its declared expressions. The comparison table
(`PL-WZVZ`) can consume a field that affects no computed number, but only when
the field settles the meaning of one that does. For example, such a field can
say which of the survey's three sampling configurations a $`\dot V_S`$ of zero
stands for. Recording the consumer keeps the comparison table from becoming a
way round the rule that a field be a coefficient in the model.

**Adding a machine adds a row, not a column.** When the abstraction is right, a
new machine only supplies values for fields that already exist. A machine that
needs a new field calls for a design decision, because either the survey missed
a way in which machines differ or the field is trivia. To add the field, first
give the survey an entry for it, then add it to this document's closed set or
to the schema, and only then add the machine.

**A script can check that a new machine adds no column.** The script will live
under `tools/` and read every file in `data/machines/`. It will fail as soon as
a machine is added with a new field, because it asserts that every profile has
the same set of fields and that the schema records a consumer for every field.
It will run from a bare checkout with no virtualenv, give the same result on
every run, and state its rule where a reviewer can read it. The repository's
instructions in `CLAUDE.md` ask these three things of any part of a rule that a
script can check. Building the script is item 1.

**Unknown is not a value, here as in the survey.** A machine whose apparatus
volume is unknown cannot be added until the volume is known. Do not give it a
plausible volume in the meantime. Question 4 describes how this rule applies
when a profile is loaded.

**Requiring a consumer could be wrong only about what the survey ruled out.**
The requirement leaves out every machine specification in the survey's "Ruled
out" section: seven categories, each with the condition that would bring it
back. The survey ruled them out because none of them affects a number that the
model will compute during this milestone. If a category's condition is met, the
requirement was wrong about that category, and the cost is one field added
late. The opposite error would leave a profile full of specifications that
nothing consumes.

### The schema

Per field, matching what `data/machines/reference_circle_system.json` already
does and adding the two bindings the rules above need:

```text
value, unit                what the model reads
consumer                   "model" or "attribution"
effect                     one clause: which rate or bound this changes
source, tier, adopted      docs/MODEL.md's source hierarchy, unchanged
```

The fields the survey's evidence admits:

| Field | Consumer | What it changes | Survey |
| --- | --- | --- | --- |
| `apparatus_volume_l` | model | $`V_C`$, hence $`\tau_C`$ | (a1) |
| `deliverable_fresh_gas_flow_range` | model | the flow bound, with the model envelope | (b8) |
| `minimum_total_flow_l_min`, `minimum_oxygen_flow_l_min` | model | refusals below the floor | (b8) |
| `agents` | model | which agents may be mounted at all | (b9) |
| `agent_limits` | model | per-agent dial maximum | (b2) |
| `sample_gas_flow_l_min` | model | $`\dot m_{\mathrm{out}}`$ | (b10) |
| `sample_gas_configuration` | attribution | which sampling a zero means | (b10) |
| `delivery`, `removal`, `dial_mapping` | model | which strategy runs | (b1), (b3), (b11) |
| `not_modelled` | attribution | what this profile does not claim | Question 4 |

`agent_limits` is a mapping keyed by agent, which is one field rather than a
column per agent: adding an agent adds a key inside every profile, and that is
agent-milestone work, not machine work.

**`apparatus_volume_l` and the tree's `circuit_volume_l` are two quantities,
not two names for one** (project owner, 2026-09-27, ratified, over recording
`circuit_volume_l` as the apparatus alone, `PL-HGB6`). `apparatus_volume_l` is
the machine's half of the split under § "Three homes, and why the shipped
constants move" below: the apparatus including its absorber and excluding the
disposable patient circuit, which is how the survey's section (a1) records every
figure it found. `circuit_volume_l`, the field the tree ships, is $`V_C`$ whole:
it is the assembled total, apparatus plus patient circuit, because the model has
one well-mixed gas compartment in front of the patient and the limbs and Y-piece
have nowhere else to be. So a
profile written today from Shin et al.'s figures for a Perseus A500 stores the
with-circuit 3.3 L, never the 2.1 L apparatus figure, which would give a
$`\tau_C = V_C/\dot V_F`$ of 31.5 s at 4 L/min where 49.5 s is right. **The
condition is the split itself:** the two names stay distinct until item 1 moves
the patient circuit to the run, and from then a machine profile carries
`apparatus_volume_l` and the run supplies the rest of $`V_C`$. `PL-TBMX` wrote
today's meaning where a profile author reads it — the schema docstring, the
data file and `docs/MODEL.md`.

### Three homes, and why the shipped constants move

The abstraction separates three things one file currently holds together.

**The machine owns what a machine specifies.** Apparatus volume, flow range and
floor, agents it can mount, per-agent dial maxima, sampling, and the three
strategy names.

**The run owns its opening conditions.** The opening fresh gas flow, the
opening dial position, and the patient circuit volume. None of these is a
machine specification, and the reasoning differs per field:

- **Opening fresh gas flow.** `PL-8DJ7` deferred this field's home to this
  abstraction, on the reasoning that a fresh gas flow is a machine setting
  rather than a patient or agent property. That reasoning is right about which
  side of the patient/agent split it falls on and does not settle the home,
  and the survey supplies the fact that does: **no reachable source states a
  startup fresh gas flow for any surveyed machine.** A per-machine field would
  therefore be `unknown` on every real profile — and under the rule directly
  above, a machine with an unknown required field cannot be added. So making
  it a machine field would either block every machine or force each one to
  fabricate a number. It is an opening condition of a run: a teaching choice,
  which is exactly what the shipped file's own `provenance_gap` already calls
  it. `PL-NM7X` decides the *value* and is unaffected by this; the two
  questions are independent.
- **Opening dial position** is the same shape and is already in the tree:
  `AgentUptakeSystem.for_agent()` starts the vaporizer at that agent's 1 MAC,
  which is a convention about where a run opens rather than a property of the
  agent or of any device.
- **Patient circuit volume** is the survey's (a1) consequence. $`V_C`$ is
  apparatus *plus* patient circuit, and the patient circuit is a consumable
  chosen per case. A machine profile cannot own $`V_C`$ outright.

**The model keeps its envelope.** `core/supported_ranges.py`'s bounds are the
domain the compartment model is claimed over, and they stay exactly where they
are. The effective limit on a control is the **intersection** of the model
envelope and the machine's deliverable range, each with its own name, source
and refusal message. That is `PL-8PS6`'s framing and this design adopts it
unchanged; it is also what stops a machine profile silently widening the
model's claimed validity.

**Built, for the fresh gas flow alone, on 2026-09-20** (`PL-8PS6`). The row
above is in the tree: `deliverable_fresh_gas_flow_range` is a field on
`BreathingCircuitParameters` carrying a `DeliverableFreshGasFlowRange`, and
`BreathingCircuit` holds both claims and refuses in each one's own words.
`reference_circle_system.json` declares `null`, section (b8) having found no
reachable range for any surveyed machine, so the envelope alone binds and
nothing displayed changed. Two consequences for item 1's own work, recorded
here because this document is where its scope is read: the field is
**optional, defaulting to `None`**, which reads as *declares no range* rather
than as *unlimited*, so Question 4's refusal of an `unknown` in a field the
model reads applies to the required fields a real machine profile must supply
and not to this one; and `minimum_total_flow_l_min` was **not** built beside
it, because a machine's minimum total fresh gas flow is the same number as
that range's floor and the admission rule above forbids storing it twice.
`minimum_oxygen_flow_l_min` was not built either, on the same rule: it reaches
nothing the model computes until there is a hypoxic guard to consume it.

**Built, for the opening fresh gas flow, on 2026-09-27** (`PL-QW19`), which
brings the tree into line with § "The run owns its opening conditions" above.
`default_fresh_gas_flow_l_min` stays on the machine profile and is **optional,
defaulting to `None`**, read as *this profile states no startup flow* and never
as *this machine has none*, so Question 4's refusal of an `unknown` no longer
reaches it: a real profile states a startup flow only where a source publishes
one, and no surveyed machine has. A run built from a profile that states none
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

**The reference profile is a breathing system, not a machine, and stays one.**
`reference_circle_system.json` is named for what it is. Its `circuit_volume_l`
of 6.0 L is the assembled total, apparatus plus patient circuit, on three
grounds. The model has one well-mixed gas compartment in front of the patient,
so the limbs and Y-piece can only be inside $`V_C`$, as the survey's section
(a1) says. The file's Targ et al. note refuses the measured 9.86 L chiefly
because that system held a reservoir bag standing in for the lung, while its
corrugated limbs and Y-piece were part of the system measured, so the note's
"the apparatus alone" meant without the lung, not without the hoses, which is
what `PL-TBMX` reworded it to say. And
`docs/MODEL.md` sets it beside Shin et al.'s with-circuit totals, the Primus's
5.9 L, rather than beside their apparatus figures. What the note's comparison
adds to the stored figure before setting it against the measured 9.86 L is the
reference adult's 2.5 L alveolar compartment, the lung, so it bears on counting
a lung twice and says nothing about how the 6.0 L divides between apparatus and
patient circuit. **No source apportions it**, so splitting it into an apparatus
volume and a patient-circuit volume would invent two numbers where one is
recorded. It therefore keeps its stored figure with a declared statement that
it is the sum, which `PL-TBMX` wrote into its `provenance_gap`, and real
machines are added beside it
rather than by retrofitting it into a machine it never claimed to be. A profile
built from Shin et al.'s figures carries a true apparatus volume once the split
lands and takes its 1.2 L patient circuit from the run; until then it stores
the with-circuit total, as the paragraph under the schema table says.

**`max_delivered_concentration_percent` is mislocated today**, and the survey
proves it rather than arguing it: desflurane's 18% is the calibrated maximum of
the Tec 6, which Johnston et al. characterised *"from 1% to 18%"*, and
`docs/MODEL.md` already names that provenance. Nothing about desflurane binds
it to 18%. It belongs on the (machine, agent) pair as `agent_limits`. Moving it
is item 1's work and a data migration; until then the intersection rule above
holds the two together and nothing displayed changes.

## Question 4: validation and provenance per machine

**A machine module with no provenance fails to load rather than runs.** That is
the item's requirement and it follows from `CLAUDE.md`'s preference for an
obvious failure state over a plausible-looking number. Concretely, `core/parameters.py`
refuses a profile that:

1. **carries a field with no `source` and no entry in a `provenance_gap`** —
   the discipline `reference_circle_system.json` already meets, and the reason
   that file exists;
2. **carries `unknown` in a field the model reads** — the survey's rule, and
   the honest statement that most surveyed machines cannot be added yet;
3. **names a strategy not in the registry** — the closed set, enforced;
4. **declares an empty `not_modelled` list**; or
5. **declares a `schema_version` the loader does not know.**

Item 4 is the one worth arguing for. **Every machine has a non-empty
`not_modelled` list, and the survey is what proves it**: fresh gas inlet
position, ventilator drive, decoupling and the control loop all reach a number
and none is represented here. A profile claiming otherwise is claiming a
fidelity the model does not have, so an empty list is a defect rather than a
tidy result — and requiring it non-empty makes the omission a positive
statement the author had to write, which is what Question 5 then displays.

Nothing in this adds vocabulary. `tier` and `adopted` are `docs/MODEL.md`
§ "Source hierarchy"'s, checked by `make check` against the existing closed
vocabulary, and a machine constant is held to the same three tiers as a
partition coefficient: a measurement outranks a specification sheet, and a
specification sheet is not a measurement. The survey already applies that
ruling to itself — Shin et al.'s apparatus volumes are recorded tier 2 because
that paper carries them rather than measured them.

## Question 6: attributability

The structure above meets the item's request for a constraint on the design, not
only on the display: *design so that the parameter set is the explanation*.

**Every difference a machine makes to a curve is a difference in one of three
quantities**, because a machine affects the model only through those three. Each
resolves to declared fields:

- the volume $`V_C`$: the apparatus volume (`apparatus_volume_l`) plus the run's
  patient-circuit volume, which today is the assembled circuit volume
  (`circuit_volume_l`);
- the inflow $`\dot m_{\mathrm{in}}`$: the `delivery` strategy and the fields it
  declares;
- the outflow $`\dot m_{\mathrm{out}}`$: the `removal` strategy and the sample
  gas flow (`sample_gas_flow_l_min`).

**There is nowhere else for a difference to hide**, because the design forbids
two things: a strategy that reads an undeclared field, and one outside the
registry. Question 1 explains both.

**The comparison table between machines (`PL-WZVZ`) is therefore derived.** For
any two machine profiles, the fields that differ can be computed, and the
`effect` clause that the schema already requires says what each one does. A
derived table stays true, while one maintained by hand can go out of date after
the day it is written.

**The design rules out a difference that nobody could explain to a learner.**
Such a difference would arise if a machine changed a result through something
unnamed, for example a default inside a strategy or a branch on an undeclared
field. The interface would then attribute it to the machine's trade name. That
is an unsafe display, and the item behind the comparison table (`PL-WZVZ`)
exists to prevent it. With this design, that item does not have to catch it.

## The inlet-position decision, taken on the record

**The model does not represent a machine's internal topology, and the interface
says so where a machine is chosen.** In this model, two machines that differ
only in inlet position are the same machine, and the interface does not offer
two names that produce one curve.

The survey's headline finding is that **apparatus volume alone does not explain
the measured differences between machines**. Its sharpest instance is Fukuda et
al.'s randomised patient study, in which moving only the fresh gas inlet
significantly raised the inspired/delivered ratio ($`F_I/F_D`$) of isoflurane
and of sevoflurane during low-flow anesthesia. This model's circuit equation
describes exactly that ratio. It treats the circuit as a single well-mixed
compartment, so it cannot represent where the inlet sits.

The survey named two ways the model could account for inlet position:

- **Refused: fold the inlet's effect into an effective volume.** Although it is
  the obvious option to implement, the survey's refusal still applies.
  Calibrating a volume to reproduce observed kinetics would fit the curves, but
  it would attribute to volume a difference that volume did not cause. That
  volume would then appear as a sourced-looking number that no measurement
  supports, in the table built to keep such numbers out (`PL-WZVZ`).
- **Not now: represent the topology.** A multi-limb circuit separates inspired
  gas from mean circuit gas. Under a model such as Lerou and Booij's, the two
  become distinct states, and this model's single $`F_I`$ no longer describes
  both. `docs/MODEL.md` § "Model boundary" already says this. Representing the
  topology therefore changes the model boundary, so it belongs to the planned
  per-compartment gas-phase condition (planned-milestone item 39), not to
  item 1. Record the new boundary in that section of `docs/MODEL.md` before
  extending the model this way.

**The interface's statement is needed even after a per-compartment gas-phase
model is built (item 39).** It still applies to each machine whose inlet
position is unknown. Of the surveyed machines, only the two that Fukuda et al.
instrumented have a known inlet position.

**This decision is for the present model only.** It stops applying when a
per-compartment gas-phase model is built (item 39), or when any multi-limb
circuit enters the model. Written as a general rule, it would outlive its
evidence, and later contributors who never saw that evidence would follow the
rule.

## Question 5: naming a real machine in the interface

**Decided (project owner, 2026-09-20, ratified).** The machine chooser and the
dashboard name a machine by its archetype, meaning what the model represents,
such as "circle system · 3.3 L with patient circuit · variable-bypass vaporizer".
The trade name appears in the machine's own panel, beside its parameters and its
sources. There it is a citation for the parameters, not a claim that the model
reproduces that machine. Ordinary evidence can reopen the decision: a
measurement, a cost the reasons below did not weigh, or a constraint that
appears later.

**A change must keep the trade name off every curve, chooser entry and dashboard
readout.** The trade name may appear only where the machine's list of what the
model leaves out (`not_modelled`) is on screen beside it. The machine panel
(`PL-WZVZ`) shows that list together with the machine's parameter set and a
comparison table, so a trade name may appear in that table too. Planned-milestone
item 1 must keep to these rules.

Three facts decide the question:

1. **The model reproduces only part of what makes machines differ.** Shin et al.
   found the Perseus A500 and the Zeus IE indistinguishable in volume: 2.1 L
   against 2.0 L of apparatus, 3.3 L against 3.2 L with the 1.2 L patient circuit,
   and time constants of 6.6 against 6.4 min at 0.5 L/min. The two machines still
   differed significantly in time to target. Shin et al. attributed the difference
   to inlet position, decoupling, ventilator drive and delivery mode, and the model
   leaves out all four (`not_modelled`).
2. **Some machines are therefore identical in the model.** With trade-name labels,
   the interface would offer two names that produce one curve, and nothing would
   say why. With archetype labels, it correctly offers one entry.
3. **The project's clinical-output standard (`CLAUDE.md`) counts a correct number
   under the wrong machine's name as a presentation failure.** A learner who reads
   a trade name on a curve takes the curve to come from the machine in their own
   operating room.

**Both other options are weaker.** Showing the trade name everywhere would make
the feature feel real, and users will ask for it. It claims the most with the
least support, and Shin et al.'s result argues directly against it. Showing only
the archetype, with no trade name anywhere, is safe but discards the provenance:
a reader cannot check a parameter against the manual of a machine that nobody
names.

## Question 7: what the second machine costs

The design sets a target cost for adding a second machine in each of three
cases, and only the first case is data entry. A strategy is a pure function that
returns a rate. The closed set is this document's table of strategies.

**When a machine's delivery and removal strategies are already in the closed
set, it needs one data file and nothing else.** The data file is the machine's
profile, one JSON file under `src/anesthesia_sim/data/machines/`. It names one
strategy for each of the three slots, gives a source for every field, and has a
non-empty list of what the simulator does not model for that machine
(`not_modelled`). Adding the machine also takes a schema test and a row for it
in the machine comparison (`PL-WZVZ`). The diff touches the data file and one
test file. Nothing in `core/` or in any patient row changes. The physics needs
no new test, because the matrix that describes it is already tested and a
machine affects it only through the two rates.

**A new strategy takes a design change, but a limited one.** The change adds the
strategy's function, its registry entry and a row in the closed set. It also
adds a proof that the returned rate is nonnegative, finite and constant across a
step. The patient rows and the solver stay as they are.

**A new profile field takes a design change that starts in the machine survey
(`docs/machine-survey.md`).** Add the field there first, and state how it leads
to a computed value. Then add it to the schema, with the code that reads it and
the effect it has. Then add it to every existing profile. That last step is the
cost: a field added for one machine belongs in the schema only if every profile
can give it a value.

The column check described under Question 2 can verify these costs.

## What this design does not decide

Recorded so the milestone does not mistake them for settled, and so nothing
below is re-derived from scratch.

- **The value of the opening fresh gas flow.** `PL-NM7X`, the project owner's.
  This document decides only that it is an opening condition of a run rather
  than a machine specification.
- **Whether the model gains an ambient pressure.** `PL-5K5C`. Until it does,
  `variable_bypass` and `fixed_volume_percent` agree everywhere in the model's
  domain, and `PL-439V`'s discriminating test passes on paper only.
- **Flow-dependent vaporizer output.** Hendrickx et al. measured it; no
  milestone models it; both mapping strategies declare it as a limitation.
- **Ventilation, decoupling and the ventilator.** (b5) and (b6) reach a number
  only once the machine owns the ventilator, which this abstraction does not
  give it. Ventilation stays a patient-side control, and decoupling is a fourth
  strategy slot opened by whichever milestone moves it.
- **Automated end-tidal control.** Planned-milestone item 5. It fails two of
  this design's three admissibility conditions, which is the reason it is a
  milestone rather than a strategy, and that reason is now recorded rather than
  assumed.
- **Every `unknown` in the survey.** Apparatus volumes, flow floors, agent
  lists and sample flows for the GE and Getinge machines, and for three of the
  five Dräger ones. The survey's last section names the manuals and the route.
  **That is a condition on each profile, not on this abstraction.** A machine
  whose fields are `unknown` is a machine that cannot be added yet, and its
  manual is sought when that machine's profile is built rather than in advance
  (project owner, 2026-09-20). The design is complete without any of them: the
  reference profile is what it runs on meanwhile by construction, not for want
  of evidence.

## Sources

Each source below is cited in `docs/machine-survey.md`, which is the authority
for all of them. That file gives each source's full bibliographic record, how it
was retrieved and how deeply it was read.

- Fukuda T, Fukunaga A, Toyooka H. *J Anesth.* 2006;20(4):268–273 — inlet
  position changes $`F_I/F_D`$ at a fixed volume, the measurement behind the
  decline recorded above.
- Hendrickx JF, De Cooman S, Deloof T, et al. *Anesth Analg.*
  2001;93(2):391–395 — cassette-vaporizer output against the dial setting at
  different flows.
- Johnston RV, Andrews JJ, Deyo DJ, et al. *Anesth Analg.* 1994;79(3):548–552 —
  the Tec 6 characterised from 1% to 18%, the source of the 18%.
- Meyer J-U, Kullik G, Wruck N, Kück K, Manigel J. In: Schüttler J, Schwilden
  H, eds. *Modern Anesthetics.* Springer; 2008:451–470 — the Zeus's two dosing
  modes, the closed surplus gas valve, the gas module's sample draw, and the
  fixed-volume-percentage principle.
- Shin HW, Yu HN, Bae GE, et al. *BMC Anesthesiol.* 2017;17(1):10 — the three
  Dräger apparatus volumes, and the finding that machines with indistinguishable
  volumes differed significantly in time to target.
- Targ AG, Yasuda N, Eger EI II. *Anesth Analg.* 1989;69(2):218–225 — the
  measured 9.86 L that the reference profile's provenance note argues against.
