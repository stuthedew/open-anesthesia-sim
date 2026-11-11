# Anesthesia machines: the variables that change a simulated result

## What this document is, and what it is not

This survey asks **which differences between real anesthesia machines change a
number that this simulator computes or displays**. A difference counts if it
changes such a number today, or will once two planned additions are in place: a
modular model of the anesthesia machine (`ROADMAP.md`, planned-milestone item 1,
called the machine milestone below), and a patient model that tracks several
substances at once (planned-milestone item 6, which adds nitrous oxide).
§ "The machines surveyed, and why those" lists the eight machines, and
§ "How a value gets into this document" says which kinds of source were used.

The survey is not an inventory. Beside each specification, it states how that
specification changes a computed or displayed value. A specification that changes
no such value is left out. Where someone would otherwise raise it again, it gets
one line under § "Ruled out", written once for the whole survey rather than per
machine.

**The design of the machine milestone (`PL-FG9D`), in
`docs/machine-abstraction.md`, builds on this survey.** The design covers the
machine classes, the format of a machine profile, and interlocks. A machine
profile is the data file that describes one machine. Today the only one is
`src/anesthesia_sim/data/machines/reference_circle_system.json`. An interlock
is a machine feature that prevents an unsafe setting, such as the
single-halogenated-agent interlock that the milestone's entry in `ROADMAP.md`
names. § "What `PL-FG9D` needs: data, behavior, and what is neither" lists
what the design needs: which variables are per-machine *data*, such as
apparatus volume, which are *behavior* that differs between machines, such as
where agent enters the circuit, and which fit neither. The survey changes no
code.

## The headline finding, because it decides the machine milestone's design

**Apparatus volume alone does not explain the measured differences between
machines, and the evidence for that is direct.** Two studies measured, in
patients or on a bench, quantities that this model computes:

- Shin et al. (Shin 2017) measured time to a target sevoflurane concentration
  of 4% on three Dräger workstations: the Primus, the Perseus A500 and the Zeus
  IE. For each machine, they added the apparatus volume given in Dräger's
  manual to their 1.2 L patient circuit, and computed a time constant from the
  sum (their Table 3). The Perseus A500 and the Zeus IE came to 3.3 L and
  3.2 L, and to 6.6 min against 6.4 min at 0.5 L/min fresh gas flow. The
  apparatus volumes are tier 2 here (rule 2 under § "How a value gets into this
  document"). Circuit volume is the only property of the machine in this
  model's circuit equation, and on it the two are effectively the same
  circuit. Their times to target still differed significantly, between the
  Perseus and the Zeus in its fresh gas mode: medians of 920 s against 1590 s
  at 0.5 L/min, and 134 s against 255 s at 3 L/min (their Table 2). The
  authors posit that the difference comes from equipment
  factors other than circuit volume and fresh gas flow. Both machines have a
  blower-driven ventilator and neither has fresh gas decoupling. The factors
  the authors name that differ between the two are the fresh gas inlet, which
  sits closer to the patient on the Perseus, and the Zeus's injection
  vaporizer, which in fresh gas mode mixes the agent in a chamber next to the
  ventilator and so adds a delay. § "(b3)" sets that delay against the
  manufacturer's account of the mode.
- In patients, Fukuda et al. (Fukuda 2006) compared two positions of the
  **fresh gas inlet** during low-flow anesthesia: between the inspiratory valve
  and the absorber, and between the inspiratory valve and the patient. On the
  two decoupling-style machines of the three they studied, the ACOMA
  KMA-1300-III and the Dräger Fabius GS, the inlet next to the patient gave a
  significantly higher inspired/delivered ratio. It did so for sevoflurane on
  both, and for isoflurane on the ACOMA. On the third machine, a Dräger NM-GS,
  the abstract reports no significant change. That ratio, $`F_I/F_D`$, is
  exactly what this model's circuit equation computes. The abstract is the only
  part of the paper this project has read. It gives no fresh gas flow and no
  values of the ratio, and it does not say whether moving the inlet changed the
  circuit's volume.

So, on Shin et al.'s measurements alone, a machine profile that holds only a
volume and flow limits is falsified by the data before it is written. Fukuda et al.
show that one of the other factors, the inlet's position, changes $`F_I/F_D`$
on some machines. This does not mean that the profile must carry the
circuit's topology, such as where the fresh gas inlet sits. It means that the
design of the machine milestone has to decide, explicitly, either to carry
topology or to state that machines differing only in topology are
indistinguishable in this model. § "What `PL-FG9D` needs: data, behavior, and
what is neither" sets out that decision under (b7).

## The machines surveyed, and why those

**A machine is here if it is the subject or comparator of a peer-reviewed study
published between 2006 and 2025, and if it contributes an axis of variation, or
a direct comparison with another machine in the set, that the rest of the set
does not already cover.** The study is evidence that the machine was in service
somewhere and studied there. It stands in for evidence of current clinical use,
because no installed-base or market-share source was reachable on 2026-09-19
(see § "How a value gets into this document" below). The survey that set the
window (`PL-4DCG`) records no reason for its start year. A study published
before 2006 is listed in the table for the axis it shows, and does not count
toward a machine's inclusion.

**The table is a map of the variation, not a list of machines to implement.**
Because each machine adds an axis or a comparison that the others lack, the set as a whole is
the range of real behavior that the format of a machine profile has to be able
to express. Nothing here commits the project to building a profile for any of
the eight machines in the table.

| Machine | Studies | Axes or comparisons it contributes |
| --- | --- | --- |
| Dräger Primus | Kern 2012; Shin 2017; Zumsande 2023 | Piston ventilator; fresh gas decoupling; large apparatus volume |
| Dräger Perseus A500 | Shin 2017; Morimoto 2020 | Turbine (blower) drive; small apparatus volume; inlet close to the patient; no decoupling |
| Dräger Zeus IE | Shin 2017; Candries 2022; Bashraheel 2022 | Direct injection of agent (fresh gas mode and auto control mode); automated end-tidal control |
| Dräger Apollo | Lerman 2025 | Piston drive with decoupling; compared with the GE Aisys in children |
| Dräger Fabius (GS/Plus) | Fukuda 2006; Morimoto 2020 | Decoupling-style circle; one of the two machines on which moving the fresh gas inlet raised $`F_I/F_D`$ |
| GE Aisys / ADU family | Hendrickx 2001; Jakobsson 2017; Leijonhufvud 2017; Lerman 2025; Hoffmann 2025 | Electronically controlled cassette vaporizer; bellows; automated agent control |
| GE Avance | Kern 2012 | Compared directly with a Primus at neonatal settings |
| Getinge FLOW-i | Jakobsson 2017; Leijonhufvud 2017; Candries 2022; Kalmar 2022 | Injector-type agent delivery; automated gas control with a speed setting |

Each axis has an entry under § "The variables", which cites its sources.

**What is deliberately absent.** Mindray's A-series, Penlon and Spacelabs
machines are out. This survey cites no study of them, so they do not meet the
rule above, and including them would mean writing rows that no source here can
fill. Each can be added once a study and a source for its rows are found, as
§ "What is missing, and how the next session gets it" describes.

## How a value gets into this document

**The survey could not take machine behavior from manufacturers' manuals.**
The brief for this survey (`PL-4DCG`, 2026-09-19) asked that machine behavior be taken from the
manufacturer's operator or technical manual, cited by document and revision.
A test on 2026-09-19 followed the method in the project's rule on citing
sources (`.claude/rules/citing-sources.md`). On 2026-09-19 the session's egress
gateway refused `www.draeger.com`, `www.gehealthcare.com`, `www.iso.org`,
`webstore.ansi.org`, `standards.iteh.ai` and every manual-hosting mirror tried.
It reached `www.ncbi.nlm.nih.gov`, `link.springer.com`, `doi.org` and
`search.worldcat.org`, though `search.worldcat.org` rate-limited the one query
put to it. On 2026-10-06 the gateway still refused `draeger.com`,
`www.draeger.com`, `www.iso.org`, `webstore.ansi.org` and `standards.iteh.ai`.
Three routes to a source remain: the PubMed MCP server, the project owner's
private reference corpus, and direct identifier checks. A web search found the
standards' identifiers (rule 4), but it is not a source. So values get into this
document by these rules:

1. **A measured quantity is cited to the measurement.** A peer-reviewed study is
   the authority for a quantity that it measured and the model uses, such as an
   inspired concentration, a time to target, or a vaporizer's output against
   its dial. It is a stronger authority than a manual would have been. Such a study is
   tier 1, a primary measurement, under § "Source hierarchy: what may be cited
   as the authority for a value" in `docs/MODEL.md`. That section ranks a
   review or textbook as tier 2 and another simulator's parameter set as
   tier 3. A specification sheet is not a measurement.
2. **A figure that a paper reports but did not measure is marked as such.** Shin
   et al. print the apparatus volumes of three Dräger machines and cite Dräger's
   instructions for use for each (their refs 12 to 14). Those manuals are still
   unread, because the network that this project's sessions run on refuses
   `www.draeger.com` (checked 2026-11-09). The volumes are recorded here as
   tier 2, a secondary synthesis, and not as measurements.
3. **A manufacturer's own technical account is used where one is held, and
   quoted.** The private reference corpus holds *Modern Anesthetics*,
   whose chapter on inhalational dosing technology is written by five Dräger
   authors and describes the vaporizers, the injector, the gas module and the
   Zeus breathing system directly. It is a textbook chapter and therefore
   tier 2. But for *what a device does*, as opposed to a measured quantity, it
   is the manufacturer speaking, which is the class of source the brief asked
   for.
4. **A standard is named by number, title, edition and date only, and the route
   to those details is stated because it is a weak one.** The texts were not
   reachable and neither were the ISO catalogue pages, so the editions and dates
   come from **national adoption records surfaced by a web search**. The
   project's rule on citing sources says that a web search is not a source.
   This document therefore states what each standard *is* and never what a
   clause requires. Every claim that would need the text says that the text was not read.
   § "Sources" records the route beside the two entries.
5. **Anything else is `unknown`.** A machine whose apparatus volume is unknown
   cannot be added yet. It does not get a plausible apparatus volume instead.

**Every claim in this document that has been
adopted into the model specification or a data file has been checked against the depth its source was read at**
(2026-11-11, `PL-KZ60`). The rest are checked one claim at a time, by the
change that adopts them. The check corrected two claims in § "The headline
finding". Fukuda et al. had been cited for a rise in $`F_I/F_D`$ on every
machine they studied and at a fixed circuit volume, and their abstract supports
neither. Shin et al.'s reasons for the difference between the Perseus and the
Zeus had been listed with two features that do not differ between them.
`docs/MODEL.md` and `docs/machine-abstraction.md` still repeat the Fukuda
claim, and `docs/machine-abstraction.md` also repeats the old list of Shin et
al.'s reasons. `PL-4G3N` corrects both.

## The variables

Each entry carries its bucket and, for (a) and (b), the reason it reaches a
number:

- **(a)** changes a number the simulator computes today;
- **(b)** changes a number once a planned milestone lands: the machine
  milestone for most entries, and the entry names any other;
- **(c)** ruled out, collected in § "Ruled out" with the condition under which
  each stops being ruled out.

### (a1) Apparatus gas volume

**Why it reaches a number.** `circuit_volume_l` is $`V_C`$ in the circuit
equation, so it sets the fresh-gas wash-in time constant
$`\tau_C = V_C/\dot V_F`$, where $`\dot V_F`$ is the fresh gas flow — the part of the early rise in inspired
concentration that belongs to the machine rather than to uptake. It is the
single most-taught point about a circle system and the model already carries it.

**Where it lives today.** `src/anesthesia_sim/data/machines/reference_circle_system.json`,
6.0 L, with its provenance and the deliberate departure from Gas Man's published
8.0 L recorded there (`PL-4YY1`).

**What the survey found.** The apparatus volume of a workstation is roughly half
the stored 6.0 L on the two most recent Dräger designs and roughly equal to it
on the older one, once a disposable patient circuit is added:

| Machine | Apparatus incl. absorber, excl. patient circuit | With a 1.2 L Hudson RCI circuit, without the 3 L reservoir bag | $`\tau_C`$ at 4 L/min |
| --- | --- | --- | --- |
| Dräger Primus | 4.7 L | 5.9 L | 89 s |
| Dräger Perseus A500 | 2.1 L | 3.3 L | 50 s |
| Dräger Zeus IE | 2.0 L | 3.2 L | 48 s |
| GE Aisys / Avance / ADU | unknown | unknown | — |
| Getinge FLOW-i | unknown | unknown | — |
| Dräger Apollo, Fabius | unknown | unknown | — |

**On the table's figures, machine choice moves the circuit time constant by a
factor of about 1.8 at any given flow**. At the default 4 L/min, where the
time constants are 48 to 89 s, the difference shows in the first two minutes of
a run.

The apparatus figures are Shin et al.'s, taken from Dräger's manuals. Those
manuals are unread, so the figures are tier 2 here and not measurements.
The 1.2 L is the internal volume of the Hudson RCI breathing circuit (Teleflex)
in Shin et al.'s set-up. Their with-circuit sum is "the internal volume of AM +
the volume of breathing circuit 1.2 L", which leaves out the set-up's 3 L
reservoir bag. The with-circuit column omits the bag too, and so do the time
constants, which are computed here from that column at this simulator's default
flow.

**The stored 6.0 L was not chosen to represent a Primus.** It sits within 2% of
the Primus-with-circuit figure of 5.9 L by coincidence. It predates this survey.
The project owner ruled on 2026-09-01 that the value is not critical, and the
data file's note on its Gas Man source records that ruling (`PL-4YY1`). This
survey is not its source.

**A design consequence for `PL-FG9D`.** The model has one well-mixed circuit
compartment, so its $`V_C`$ is apparatus *plus* patient circuit. The patient
circuit is a consumable chosen per case, not a property of the machine. A
machine profile therefore cannot own $`V_C`$ outright: it owns an apparatus
volume, and something else supplies the circuit.

### (a2) Default fresh gas flow

**Why it reaches a number.** It is the flow every run starts at, so it sets
$`\tau_C`$ at $`t = 0`$, and for the whole of any run in which the flow is not
changed. `PL-8DJ7` established that it is a machine setting rather than a patient
or agent property, and the project owner's recorded decision was to wait for
the machine milestone's design.

**Where it lives today.** The same machine data file, at 4.0 L/min, declared in
that file's `provenance_gap` as a **teaching default, not a clinical
recommendation**, with no published counterpart. (The item's brief describes it as a literal in
`src/anesthesia_sim/core/circuit.py`; that stopped being true when `PL-4YY1`
moved both constants into the data file, and the literal that remains is a
default for a bare unit-test construction, guarded by a test that fails if it
disagrees with the file.) Since `PL-QW19` that literal is named
`TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN` and is also the flow a run opens at when
a machine profile states none, because the field is now optional; this section's
finding is why.

**What the survey found: no machine default, and one recommendation that is not
a survey of practice.** No reachable source states a startup fresh gas flow for
any surveyed machine. What the literature carries is normative rather than
descriptive. Kalmar et al. conclude in those words that *"routine clinical
practice using what historically is called 'low flow anaesthesia' (e.g. 2 L/min
FGF) should be abandoned"* in favour of automated minimal-flow delivery — a
recommendation drawn from a single-centre retrospective of 25 cases per group on
one workstation, the FLOW-i, not a measurement of what flows are used. What it does
establish about practice is its own comparator: a fixed 2 L/min group the paper
calls conventional low flow, which already sits below this simulator's 4 L/min
default.

**Two papers this section first cited beside it do not support a claim about
practice, and the correction is recorded rather than quietly dropped**
(`PL-NM7X`, 2026-09-20). Candries et al. randomised 0.2 to 6 L/min and Hoffmann
et al. ran 0.3 to 6 L/min, and until 2026-09-20 this section read those two
ranges as establishing that *"4 L/min is at the high end of contemporary
practice rather than the middle of it"*. Neither supports it. Candries' range is
the protocol of a Gas Man validation study, chosen to span a wide envelope;
Hoffmann's is a bench protocol run *in vitro* into a 2 L test lung, whose
settings that paper describes as reflecting clinical conditions and whose range
contains 4, 5 and 6 L/min — so it reads, if anything, the other way. **A study's
chosen flow range is not a report of practice**, which is the error
`reference_circle_system.json`'s De Wolf entry already guards against for its
1 L/min.

**The decision, and what it turned on** (project owner, 2026-09-20, ratified,
over lowering the default to match contemporary low-flow practice). The
simulator keeps 4.0 L/min, relabelled in the data file as a **teaching default,
not a clinical recommendation**. An unlabelled default teaches a norm whatever
number it holds, so moving to 0.5 L/min would relocate the problem rather than
remove it, and would carry the same absent provenance this section objects to,
since no source found gives a startup flow for any machine either. What 4 L/min buys is a
$`\tau_C`$ near 90 s, which makes the machine's own lag a separable phase ahead
of patient uptake inside a run a learner will sit through; at 0.5 L/min it is
about 12 minutes and the demonstration no longer completes. What was wrong was
the sentence, not the number.

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
  flow ranges. Their conclusion is the one that matters for the machine milestone's design:
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
(a) for that reason and no other. The fixed-volume-percentage half changes a number
only away from one atmosphere, and `docs/MODEL.md` § "Assumptions" records that
the model holds at sea level (`PL-5K5C`).

### (b2) Vaporizer dial range and maximum, and where that number belongs

**The dial maximum caps the delivered concentration, $`F_D`$.** The code
enforces the cap in `src/anesthesia_sim/core/circuit.py`.

**The maximum is set by the delivery device, not by the agent alone.** The
model stores this maximum per agent (`max_delivered_concentration_percent`):
desflurane 18.0%, sevoflurane 8.0% and isoflurane 5.0%. `docs/MODEL.md`
§ "Delivery-limit and MAC parameters" names the vaporizers behind each maximum,
and each agent's data file cites its source. The 18% is the calibrated maximum of one
device, the Tec 6 desflurane vaporizer. Johnston et al. characterised the Tec 6
across *"all integer dial settings from 1% to 18%"*. The breathing-circuit
section of `docs/MODEL.md` cites them for this value. Nothing about desflurane
itself sets the 18%, so a different maximum may apply to a vaporizer of another
design or to a machine with an electronically controlled injector. The stored
maximum therefore has to depend on the machine as well as on the agent. It is
the first concrete case of the data-or-behavior question in `PL-FG9D`.

**Real vaporizers' dial increments are unknown.** `PL-043` decided to keep the simulator's on-screen vaporizer dial continuous, and recorded that the fidelity argument reverses if the simulator comes to model real machines: a faithful dial would then have each vaporizer's own increments. No source
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
the survey's clearest case of machines that differ in **behavior rather than data**. It is also the tidiest, because the same machine's fresh gas mode is the equation this model already has. A design that gets the mode boundary right gets one half of the Zeus with no new equation.

**The Zeus IE machine offers both kinds of delivery, as separate modes.** Meyer
et al. describe its injector as a reservoir, a dosing chamber and a heating
unit. A pulsed valve injects liquid agent from a pressurised chamber into a
heated vaporising chamber, and a heated pipe carries the vapour to the breathing
system. In Meyer et al.'s account, the two modes differ in where the vapour
enters:

- **Fresh gas mode.** The user sets a fresh gas agent concentration, and the
  vapour mixes with fresh gas before it enters the breathing system. *"In this
  dosing mode the agent dosage performance is equivalent to a conventional
  vaporizer."* On that account, the model's existing term describes this mode.
  Shin et al. posit a delay in it, from the chamber where the agent is mixed,
  as one reason the Zeus reached its target more slowly than the Perseus at
  nearly the same circuit volume (§ "The headline finding"). They did not
  measure the delay, and Meyer et al. do not mention one. Until a source
  settles it, a Zeus profile in fresh gas mode may not be described as fully
  reproduced by the existing term.
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
control and cannot be modelled as one. Shin et al. found the Zeus's auto control
mode reaching about 3.6% sevoflurane very rapidly and then taking a
considerable further delay to settle at its 4% target, because the controller
slows its approach to avoid overshooting the target — so at 3 L/min auto
control mode was *slower* to target than fresh gas mode. Kalmar et al. found
the FLOW-i's automated gas control consumes sevoflurane as a function of its speed setting (6.0 mL at speed 2 to
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
once the machine milestone gives the machine a ventilator.

**Decoupling also changes the agent's path.** It routes fresh gas through the reservoir bag before the gas reaches the circle. Shin et al. name the absence of a decoupling system as one reason the Perseus machine reached target fastest, because without it the fresh gas does not take that route.

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

**Inlet position changes the inspired/delivered ratio, $`F_I/F_D`$, during
low-flow anesthesia on some machines.** The simulator's circuit equation computes
this ratio. See the headline finding above.

**One study measured an effect, and another inferred one.** In a randomised study in
patients, Fukuda et al. moved the inlet from between the inspiratory valve and the
absorber to between the inspiratory valve and the patient. During low-flow anesthesia
on two decoupling-style machines, the move significantly raised $`F_I/F_D`$ for
sevoflurane on both, and for isoflurane on the one where it was compared, the ACOMA
KMA-1300-III. On a third machine, a Dräger NM-GS, the abstract reports no significant
change. It does not say whether the move changed the circuit's volume. Shin et al. rank their three machines by inlet proximity
to account for differences that their volume calculation did not explain.

**Inlet position is the variable that tests the honesty of the machine milestone's design: the simulator cannot represent it, and must not fake it.** It
treats the circuit as a single well-mixed compartment, in which the inlet has no
position. An "effective volume" calibrated to the observed kinetics would reproduce
the curves, but it would attribute to volume a difference that volume did not
cause. The comparison table between machines (`PL-WZVZ`) is a planned display
that shows a learner which parameter makes two machines' results differ. It
would then print a number that looks sourced but that no measurement supports.

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

**Why it reaches a number.** Checking that a machine can deliver the chosen
agent is model-compatibility logic, which `CLAUDE.md`'s clinical-output
standard treats as safety-critical. Choosing an agent a machine cannot
mount should be refused rather than simulated, because simulating it attaches a
trade name to a delivery that machine cannot perform.

**What the survey found.** The hazard behind agent-specific filling is
quantified.
Andrews et al. modelled the consequence of misfilling a conventional vaporizer
with desflurane: the calculated output of a misfilled enflurane vaporizer at a
1% dial setting and 22 °C is 57.8%, or 9.6 MAC, and misfilled enflurane,
isoflurane and halothane vaporizers at one-MAC dial settings compute to 14.0,
10.2 and 7.8 MAC of desflurane respectively. They conclude that safe delivery of
desflurane requires engineering safeguards. That is the design pressure behind
agent-specific filling, standardised as **ISO 5360:2016**, *Anaesthetic
vaporizers — Agent-specific filling systems*, fourth edition, 2016-02-15. A
catalogue abstract for that standard states that dimensions for desflurane are
not specified in it, on the grounds of that agent's properties; **the standard's
text was not read here**, so that sentence is a lead to check once the text can
be read (§ "What is missing, and how the next session gets it"), not a fact
this document establishes.

**So desflurane is not an agent with different numbers; it is its own case**,
and on this the reachable sources agree without needing the standard. It needs a
heated, pressurised, electromechanically coupled delivery device — Andrews and
Johnston's description of the Tec 6 is the primary account, and Meyer et al. give
the working figures: the agent is electrically heated in a sealed chamber to
39 °C, *"creating a pressure of approximately 1,550 mmHg"*, with agent flow cut
off entirely on tilt, power failure, low liquid level, or disagreement between
the two differential pressure sensors. A machine without such a device cannot
deliver desflurane at all, which is a capability question rather than a
parameter.

**Per-machine agent lists: unknown**, and they are exactly the kind of fact a
manufacturer's technical data states plainly.

### (b10) Sidestream sample flow

**Whether the analyser's sample is lost depends on the machine or monitor.** A
sidestream analyser removes gas from the circuit when its sample is scavenged,
and none when it returns the sample. A mainstream sensor draws no gas at all.
For each surveyed machine, the analyser's configuration is **unknown**, so ask
about it first, and then about the sample flow.

**Where the sample is scavenged, the loss is continuous and can be large.** In
Shin et al.'s study, the 200 mL/min sample was 40% of the fresh gas at their
lowest flow, 0.5 L/min. Today the model's circuit loses gas only
through its exhaust, and a scavenged sample would be a second loss.

**The survey found two sample flows.** Shin et al. sampled at the Y-piece at
200 mL/min with a bench analyser, and state that *"the gas samples were not
returned to the system"*. Meyer et al. describe Dräger's ILCA (infrared low-cost
analyzer), an integrated multi-gas sensor module, which also samples in a side
stream. They put its sample flow
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

**Like delivery mode (b3), this entry changes an equation rather than a
parameter**, so it is at risk of being implemented wrongly as a parameter. A closed-circuit mode needs a different mass-balance identity, not
the same one with a small exhaust.

## Ruled out

These are the bucket (c) items. Each line gives the condition that would bring
its item back into the survey. An item that needs more than a line of
explanation has its own entry under § "The variables" instead.

- **Screens, layouts, alarms and alarm limits, menu structure, workflow.** They
  change no computed quantity. What the *simulator's own* display may imply is
  governed by the clinical-output standard in `CLAUDE.md` and by the work item
  for the comparison table (`PL-WZVZ`), not by what a machine's screen looks
  like. Back if a milestone ever sets out to reproduce a specific machine's
  interface.
- **Pre-use self-test, checkout procedure, calibration and service intervals.**
  They gate whether a machine may be used, not what it delivers once it is. Back
  if a milestone models machine readiness or failure.
- **Cart, mounting, drawers, mobility, mains and battery, pipeline and cylinder
  supply pressures.** No path to a concentration. Back if a milestone models
  supply failure.
- **Scavenging system type.** Downstream of the circuit exhaust, with no
  back-effect on circuit concentration in this model. Back if a milestone
  models circuit pressure or a closed system where the exhaust is not free.
- **Absorbent chemistry** — Compound A, carbon monoxide from desiccated
  absorbent, absorbent dust. Real and safety-relevant, and this model carries no
  chemistry at all: agent is conserved, never consumed or transformed. Back the
  moment any milestone adds a reaction. The absorbent canister's *volume* is not
  ruled out — it is inside the apparatus volumes in (a1).
- **Circuit component absorption of agent.** Targ, Yasuda and Eger measured
  how readily agent dissolves in the masks, bellows, bags, airways and circuit
  tubes of a conventional circuit (Targ 1989). The model treats the circuit
  walls as inert, and `docs/MODEL.md` § "Known limitations" records that
  (`PL-LS3H`). Most of these parts are disposable, but a bellows is part of the
  machine's ventilator (§ "(b6)"). Back if the model gives the circuit walls an
  uptake of agent, because a machine's own parts would then make that uptake
  differ between machines.
- **Data export, record-keeping and network integration.** No path to a value.
  Back if a milestone feeds a machine's recorded data into the model.

## What `PL-FG9D` needs: data, behavior, and what is neither

The evidence, not taste, decides where the line falls. A difference between machines is data when a file can store it, and behavior when only code can express it. Two differences fit neither, and need a decision
before implementation begins. Each difference below carries the code of its
entry under § "The variables", which gives its sources.

**Data.** Each field below belongs in each machine's profile, a validated, versioned data file.

| Field | Bucket | Status |
| --- | --- | --- |
| Apparatus gas volume, including absorber, excluding the patient circuit | (a1) | Known for three Dräger machines, tier 2; unknown elsewhere |
| Deliverable total fresh gas flow range, whose lower limit is the minimum total flow | (b8) | Unknown for every machine |
| Minimum oxygen flow | (b8) | Unknown for every machine |
| Agents the machine can deliver | (b9) | Unknown for every machine |
| Per-agent dial maximum, qualified by the delivery device | (b2) | Tec 6 desflurane 18%; otherwise unknown |
| Sidestream sample flow, and whether the sample returns | (b10) | Unknown for every machine |
| Default fresh gas flow | (a2) | No source found gives one |

**Behavior.** For each of these differences, the code needs a fixed set of
alternatives, and each machine uses one.

- **Whether the circuit exhaust runs at all** (b11). With the surplus valve
  shut, closed mode needs a different mass-balance identity in `docs/MODEL.md`.
  A small exhaust flow cannot stand in for closed mode. Decide how to model
  closed mode before any code is written, or an implementation will quietly
  represent it as a coefficient.
- **Where agent enters the circle** (b3). Agent either joins the fresh gas
  stream through a bypass, or is injected directly into the circle
  independently of fresh gas flow. The two routes need different equations.
  The Zeus anesthesia machine has both. Its manufacturer describes the fresh
  gas mode as equivalent to a conventional vaporizer (Meyer et al., quoted
  in (b3)). Shin et al. posit a mixing delay in that mode, which (b3) sets
  against it.
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

- **Fresh gas inlet position and internal topology** (b7). Fukuda et al.
  measured a rise in $`F_I/F_D`$ when the inlet moved, on two of the three
  machines they studied. Shin et al. point to the inlet's distance from the
  patient to explain differences that their volume calculation did not. No
  study here measured the effect of the rest of the topology. The comparison
  table (`PL-WZVZ`) makes this decision visible. When the parameter that
  produced a difference is not in the model at all, a curve that shows the
  difference and attributes it to a trade name is therefore a
  presentation-safety failure under the clinical-output standard in
  `CLAUDE.md`. `docs/machine-abstraction.md` § "Fresh gas inlet position is
  not modelled" records the choice. The model leaves inlet position and
  topology out, and says so where a machine is chosen. Representing them waits
  for a per-compartment gas-phase model (`ROADMAP.md` planned-milestone item
  39) or a multi-limb circuit. Folding them into an effective volume is
  refused, because the comparison table would then attribute a real difference
  to the effective volume, which did not cause it.
- **Ventilator drive** (b6) needs the same decision, with less at stake. It
  matters through mixing, which the model does not represent.

## What is missing, and how the next session gets it

Every value marked `unknown` above has the same fix: **someone who can reach
manufacturer technical data, or a project owner who can supply it.** Try the
private reference corpus first (rule 3 under § "How a value gets into this
document"). It answered the vaporizer, injector, gas-module and closed-circuit
questions outright.

**Seek each unknown value one at a time, only when a machine profile needs it**
(project owner, 2026-09-20). Ask for that machine's operator or technical manual
then, rather than gathering manuals in bulk ahead of the machine milestone. No
unknown value here blocks the milestone's design.

The places to look are:

- Dräger *Instructions for Use* for the Perseus A500, Primus, Apollo, Fabius and
  Zeus IE: the technical data sections, for apparatus volume, flow ranges,
  minimum oxygen flow and sample gas flow. The Perseus manual was found at
  `draeger.com/Content/Documents/Content/IfU_Perseus_A500_SW_1.1n_EN_9054101.pdf`.
  The network used for this survey refused the download on 2026-09-19.
- GE *User's Reference Manual* for the Aisys CS², Avance and Carestation
  families, and the Aladin cassette's specification, for the same fields.
- Getinge *User's Manual* for the FLOW-i, for the same fields, and for whether
  the part Getinge calls the volume reflector counts toward apparatus volume. No
  source read here describes it.
- **ISO 80601-2-13:2022** and its Amendment 1:2026, for what a workstation
  must guarantee about oxygen concentration and flow.
- **ISO 5360:2016**, for agent-specific filling, and to confirm that it
  specifies no dimensions for desflurane.

The comparison table (`PL-WZVZ`) takes its rows from this survey, so the sources
above are where to look for each row it shows as `unknown`.

## Sources

**Route and depth, per `.claude/rules/citing-sources.md`.** Every article below
was retrieved through the PubMed MCP server, on 2026-09-19 unless its entry
gives another date, and its bibliographic record — PMID, DOI, journal, volume,
issue and pages — read there rather than from a search summary; each entry's
DOI links the original. The depth of reading
is stated on each entry, because the abstract is as far as that route goes for a
paywalled article: **full text read**, **abstract read**, or **metadata only**. Later readings,
some by other routes, are dated on their entries. One source was read at full text from the project owner's private reference
corpus and says so.

**Measurements (tier 1, as rule 1 under § "How a value gets into this document"
defines it).**

- Biro P. [The effect of fresh-gas decoupling on respiratory volume. Dräger
  Sulla 808V anesthesia ventilator]. *Anaesthesist.* 1997;46(11):949–952.
  PMID 9490582; [DOI 10.1007/s001010050491](https://doi.org/10.1007/s001010050491).
  English abstract read; article in German.
- Fukuda T, Fukunaga A, Toyooka H. Site of fresh gas inlet and ratios of the
  delivered fraction and inspired fraction of inhaled isoflurane and sevoflurane
  in low-flow anesthesia. *J Anesth.* 2006;20(4):268–273.
  PMID 17072690; [DOI 10.1007/s00540-006-0417-6](https://doi.org/10.1007/s00540-006-0417-6).
  Abstract read, and read again on 2026-11-11 (`PL-KZ60`). The full text was
  not reachable that day: PubMed Central does not hold it, the private
  reference corpus does not either, and Springer's article page answered with a
  redirect. The abstract names the three machines and reports which comparisons
  were significant. It does not say whether moving the inlet changed the
  circuit's volume, so this document does not cite the study for a change at a
  fixed volume.
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
  **Full text read** (PMC5248460; reference list read through NCBI efetch,
  2026-11-09). It prints the three Dräger apparatus volumes and cites them to
  Dräger's instructions for use for the Primus IE (2014), the Perseus A500
  (2013) and the Zeus IE (2015), its refs 12 to 14. Those manuals are unread,
  because `www.draeger.com` was refused on 2026-11-09, so the volumes are tier 2
  here. Its times to target are its own measurement. Read at full text again
  on 2026-11-11 (`PL-KZ60`) to check the apparatus volumes, the circuit and
  bag set-up, the circuit volumes and time constants, and the authors' reasons
  for the difference between the Perseus and the Zeus. Its Tables 2 and 3 were
  read again on 2026-11-11 (`PL-8ZD7`) for the times to target cited in
  § "The headline finding".
- Targ AG, Yasuda N, Eger EI II. Solubility of I-653, sevoflurane, isoflurane,
  and halothane in plastics and rubber composing a conventional anesthetic
  circuit. *Anesth Analg.* 1989;69(2):218–225. PMID 2764290; PubMed lists no
  DOI for it. Abstract read 2026-11-11 through the PubMed MCP server.
  `docs/MODEL.md` cites the same study, read at full text on 2026-09-13 from
  the private reference corpus.

**Descriptions of devices and their behavior, and other studies.** Each entry
says what it is cited for. A review or a textbook chapter is tier 2.

- Andrews JJ, Johnston RV. The new Tec 6 desflurane vaporizer. *Anesth Analg.*
  1993;76(6):1338–1341.
  PMID 8498675; [DOI 10.1213/00000539-199376060-00027](https://doi.org/10.1213/00000539-199376060-00027).
  Abstract read.
- Andrews JJ, Johnston RV, Kramer GC. Consequences of misfilling contemporary
  vaporizers with desflurane. *Can J Anaesth.* 1993;40(1):71–76.
  PMID 8425247; [DOI 10.1007/BF03009323](https://doi.org/10.1007/BF03009323). Abstract read;
  its figures are a mathematical model's output, not a measurement.
- Candries E, De Wolf AM, Hendrickx JFA. Prospective validation of Gas Man
  simulations of sevoflurane in O2/air over a wide fresh gas flow range. *J Clin
  Monit Comput.* 2022;36(6):1881–1890.
  PMID 35318567; [DOI 10.1007/s10877-022-00842-0](https://doi.org/10.1007/s10877-022-00842-0).
  Abstract read; identifiers and the 0.2–6 L/min protocol range re-confirmed
  against the PubMed record 2026-09-20 (`PL-NM7X`). No PubMed Central full text,
  and a check of the private reference corpus the same day did not find it.
  Directly relevant to this project: it compares Gas Man's predictions with
  measured sevoflurane concentrations on two workstations, the FLOW-i and the
  Zeus, and reports materially worse agreement during wash-in than during
  maintenance. Gas Man is the program this simulator is compared against, tier 3
  under `docs/MODEL.md`'s source hierarchy.
  Its flow range is a protocol, not a report of practice — see § "(a2)". The
  abstract was read again on 2026-11-11 (`PL-KZ60`). It gives a median absolute
  performance error of 21% over the first 15 minutes against 6% over the last
  45 on the FLOW-i, and 13% against 5% on the Zeus.
- Hendrickx JFA, De Wolf AM. The anesthesia workstation: quo vadis? *Anesth
  Analg.* 2018;127(3):671–675.
  PMID 29239956; [DOI 10.1213/ANE.0000000000002688](https://doi.org/10.1213/ANE.0000000000002688).
  Metadata only; the full text was not reachable. Named here as the review a
  later session should read first, not cited for any figure.
- Jain RK, Swaminathan S. Anaesthesia ventilators. *Indian J Anaesth.*
  2013;57(5):525–532.
  PMID 24249886; [DOI 10.4103/0019-5049.120150](https://doi.org/10.4103/0019-5049.120150).
  Abstract read; open access.
- Kalmar AF, Van Der Vekens N, De Rydt F, Allaert S, Van De Velde M, Mulier J.
  Minimizing sevoflurane wastage by sensible use of automated gas control
  technology in the Flow-i workstation: an economic and ecological assessment.
  *J Clin Monit Comput.* 2022;36(6):1601–1610.
  PMID 34978655; [DOI 10.1007/s10877-021-00803-z](https://doi.org/10.1007/s10877-021-00803-z).
  **Read at full text 2026-09-20** from PubMed Central (PMC9637609) for
  `PL-NM7X`. The sentence quoted in § "(a2)" is the abstract's closing one. The
  body's Conclusion states it again without the parenthesised 2 L/min figure.
  The study's design limits what it may be cited for: a retrospective review of
  one centre's records, 25 cases per group, on Flow-i workstations alone,
  comparing automated gas control (AGC) speed settings against a fixed 2 L/min
  group and a manual minimal-flow group. § "(a2)" says what that design lets it
  show about practice. The full text was read again on 2026-11-11 through
  NCBI's efetch service (`PL-KZ60`). Its Methods analyse one institution's
  charting records under one ethics approval, and it calls its fixed 2 L/min
  group "conventional low flow anaesthesia".
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
  section dump `modern_anesthetics/08_Part_IV_Ch5-6_Index`); every passage
  quoted above is from printed pages 453–468, and the page each sits on is
  recoverable from the dump's page markers. The chapter is from a textbook and
  so is tier 2, but for what a device does it is the manufacturer's own
  technical account. Rule 3 under § "How a value gets into this document" says
  what it may be cited for. The sentence quoted in § "(b11)" was checked
  against the dump again on 2026-11-11 (`PL-KZ60`).

**Evidence that a machine was in service and studied, used to select the
machines surveyed.**

- Bashraheel MK, Eerlings SA, De Wolf AM, et al. Memsorb, a novel CO2 removal
  device part I: in vitro performance with the Zeus IE. *J Clin Monit Comput.*
  2022;36(6):1591–1600.
  PMID 35089526; [DOI 10.1007/s10877-021-00802-0](https://doi.org/10.1007/s10877-021-00802-0).
  Abstract read 2026-11-11; it studies the Zeus IE.
- Hoffmann M, Jouwena J, De Wolf AM, Carette R, Lauwers RSH, Hendrickx JFA. In
  vitro performance of a charcoal-capturing device with desflurane.
  *Anesthesiology.* 2025;142(6):1038–1046.
  PMID 40073301; [DOI 10.1097/ALN.0000000000005445](https://doi.org/10.1097/ALN.0000000000005445).
  Abstract read; identifiers and the 0.3–6 L/min bench protocol re-confirmed
  against the PubMed record 2026-09-20 (`PL-NM7X`). No PubMed Central full text,
  and a check of the private reference corpus the same day did not find it. It
  is an *in vitro* study using a 2 L test lung. § "(a2)" says why it is **not**
  evidence about clinical practice, and records that it was once cited as such
  here.
- Jakobsson P, Lindgren M, Jakobsson JG. Wash-in and wash-out of sevoflurane in
  a test-lung model: a comparison between Aisys and FLOW-i. *F1000Res.*
  2017;6:389.
  PMID 28529707; [DOI 10.12688/f1000research.11255.2](https://doi.org/10.12688/f1000research.11255.2).
  Abstract read 2026-11-11; it compares the GE Aisys with the FLOW-i on a test
  lung.
- Leijonhufvud F, Jöneby F, Jakobsson JG. The impact of fresh gas flow on
  wash-in, wash-out time and gas consumption for sevoflurane and desflurane,
  comparing two anaesthesia machines, a test-lung study. *F1000Res.*
  2017;6:1997.
  PMID 29333245; [DOI 10.12688/f1000research.13064.2](https://doi.org/10.12688/f1000research.13064.2).
  Abstract read 2026-11-11; it compares the GE Aisys with the FLOW-i on a test
  lung.
- Zumsande S, Thoben C, Dennhardt N, et al. Rebounds of sevoflurane
  concentration during simulated trigger-free pediatric and adult anesthesia.
  *BMC Anesthesiol.* 2023;23(1):196.
  PMID 37291484; [DOI 10.1186/s12871-023-02148-3](https://doi.org/10.1186/s12871-023-02148-3).
  Abstract read 2026-11-11; it studies a Dräger Primus on test lungs.

**Standards, named by number and edition only; texts not reachable.**

- ISO 80601-2-13:2022, *Medical electrical equipment — Part 2-13: Particular
  requirements for basic safety and essential performance of an anaesthetic
  workstation*, second edition, 2022-04; Amendment 1:2026.
- ISO 5360:2016, *Anaesthetic vaporizers — Agent-specific filling systems*,
  fourth edition, 2016-02-15. The edition and date are those a CSA adoption
  record states for the standard it adopts.

**Neither standard was read, and the route to both was a web search**, because
the standards bodies' sites could not be reached (§ "How a value gets into this
document" records which sites, and when). The identifiers in these two entries
come from catalogue and adoption records that the search surfaced. The
project's rule on citing sources (`.claude/rules/citing-sources.md`) says
explicitly that a web search is not a source. The entries are pointers for a
session that can open the texts, and nothing in this document rests on what
either standard requires.
