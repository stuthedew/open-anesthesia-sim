---
id: PL-B396
title: Agent amounts are displayed in litres of vapour, which is not the unit a reader buys, fills or wastes agent in - report a liquid-equivalent millilitre figure
priority: P2
effort: M
status: needs-decision
classes: ux, docs
feature: liquid-agent-consumption
touches: ROADMAP.md, docs/items
added: 2026-09-16
---

**Problem.** Agent amounts are displayed in litres of vapour, which is not the unit a reader buys, fills or wastes agent in - report a liquid-equivalent millilitre figure

**Raised by the project owner, 2026-09-16.** Reading the accounting panel's
"Delivered: 0.4 L": a clinician fills a vaporizer from a 250 mL bottle of
liquid, so litres of vapour is a unit with no handle on it, while "you put 25
mL into the patient and sent 100 mL to the scavenger" lands against something
they have physically held. The observation is right and the goal is not in
question. What is open is where the figure goes.

**The unit today is correct, and the caption says so.** `delivered_agent_l` is
$\dot V_F F_D \Delta t$ — litres of *pure agent vapour* at the model's
reference conditions, which is the vaporizer's vapour output, not liquid.
`ACCOUNTING_UNIT_CAPTION` reads "Litres of equivalent pure agent gas" and
`docs/MODEL.md` § "Displayed precision" records that it is worded that way
"because a bare 'L' beside an anaesthetic agent invites the liquid reading"
(`PL-TG60`). So this is an addition, not a correction.

**Two options, and they are not close in cost.**

1. *Re-unit the existing panel.* Cheapest. But "Agent accounting validation"
   is a numerical-conservation diagnostic — its status word rules on the
   solver, not on the case — and its last two lines are a residual at 1e-14,
   which is meaningless in millilitres and meaningless to a clinician in any
   unit. Putting a figure a reader would act on clinically under a heading
   that names a developer instrument is the mode-confusion
   `.claude/rules/expert-review.md` lists under human factors.
2. *A consumption readout of its own,* with the validation panel left in gas
   litres. Delivered as mL of liquid equivalent — the bottle figure — a
   current burn rate in mL/h, and the exhausted/stored split labelled for what
   it is (`PL-H4N8`). This is the display that can carry the low-flow lesson,
   because the lesson is a comparison of delivered totals at equal alveolar
   concentration and needs the rate beside the flow that sets it.

**Either way: "liquid equivalent", never "liquid".** The agent in fat is not
liquid; the millilitre figure is a mass expressed as the liquid volume that
would produce it. Same rule as "modelled, not measured" elsewhere in the
interface.

**Displayed precision has to be re-derived, not carried over.**
`AGENT_VOLUME_DISPLAY_DECIMALS` is 0.1 L of vapour, derived in `PL-TG60` from
one published SD of a partition coefficient moving the exhaust total by
0.016-0.042 L at 1 h and 0.18-0.23 L at 24 h. In sevoflurane liquid
equivalent at a 20 °C reference (5.47 mL per L of vapour) that band is
0.09-0.23 mL at 1 h and 0.98-1.26 mL at 24 h, so 0.1 mL and 1 mL sit on
opposite sides of it and the choice is a fresh derivation. Note also that the
conversion factor is agent-specific, so one resolution has to hold for all
three.

**Blocked by `PL-S6WW` and `PL-KZ99`.** No displayed millilitre figure is
defined until the gas volumes' reference temperature is on record and the two
physical constants are stored with theirs.

**Out of the current milestone.** v0.4.26 is the Qt port, whose definition of
done is parity against a closed enumeration; a new readout is not parity. This
is interface work for after the port.

**THE TWO OPTIONS ABOVE ARE SUPERSEDED, 2026-09-16.** Put the choice between
re-unitting the accounting panel and building a consumption readout beside it,
the project owner answered neither: "the info on the panel is not info the
user really needs or cares to see. At most, we could turn it into an optional
area widget a user could add back down the road." So option 1 is dead — there
is no reader-facing panel here to re-unit — and option 2 turns out not to be
this item's to invent.

**Because the consumption display already exists as intent.** `ROADMAP.md`
§ "Planned milestones" item 28, "Add agent cost ... The economic argument for
low fresh gas flow is a standard teaching point and currently the one lesson in
this class of simulator that the application has the numbers for and does not
draw." That is the home for a liquid-millilitre figure, and `PL-H4N8` carries
the correction item 28 needs before it is built (it names the wrong quantity).

**What is left of this item, then.** Only the accounting View's own unit, and
the answer is that it does not change: litres of equivalent pure agent gas is
the natural unit of a mass-conservation instrument, its residual lines are
meaningless in millilitres, and its reader — whoever opens it from the chooser
— is asking whether the model conserves mass, not what the case cost.

**So this item is a candidate for `dropped`**, with `PL-S6WW` (the
undocumented reference temperature) and `PL-KZ99` (molar mass and liquid
density) surviving it and re-pointing at item 28. That disposition is the
project owner's: it turns on whether item 28 stays on the roadmap, which is a
scope question rather than a display one. Do not drop it on a session's own
judgment.

**WHAT GAS MAN ACTUALLY DOES, READ 2026-09-16** (project owner: "See gasman
workbook on reference repo for their implementation"). Read from
`stuthedew/open-anesthesia-sim-references`,
`text/gasman_workbook/`. It answers the unit question, and the answer is
neither of the two this item started with.

**Gas Man's economic pair is Uptake and Delivered, and its unit toggles
between litres of vapour and money — never millilitres of liquid.** Appendix,
printed p. 180: a setting displays "uptake and delivered anesthetic quantities
in currency (checked) or liters (unchecked)". Printed p. 196: the exportable
per-instant list carries "uptake in liters, delivered in liters, uptake in
dollars, and delivered in dollars". So the reference implementation resolves
"the bottle is the thing a clinician has a handle on" by going one step past
the bottle, to what the bottle costs.

**Its cost basis is DELIVERED.** Printed p. 174 states the model's own
formulae: `Feff = FGF (1+Del)`, `DELIVERED Flow = DEL x Feff`, and
`Cost = DELIVERED Flow x Cost/mL vapor`. That is independent confirmation of
`PL-H4N8` — `ROADMAP.md` planned-milestone item 28's "from the exhausted-agent
amount" disagrees with the reference implementation as well as with the
accounting identity.

**Liquid millilitres appear in Gas Man as an INPUT, not an output.** Chapter
10, printed pp. 103-105: liquid anaesthetic injection into the breathing
circuit for closed-circuit technique, in 0.5 mL unit doses ("about four
injections, or 2 mL, of liquid anesthetic is required to elevate..."). The
expansion constants are printed there for exactly that purpose: desflurane
209, enflurane 198, halothane 228, isoflurane 196, sevoflurane 183 mL of
vapour per mL of liquid. Millilitres are the unit of the clinical *act* of
injecting, not the unit of the consumption readout.

**Those constants corroborate `PL-KZ99`'s derivation.** Deriving from
Laster/Fang/Eger's measured densities at 20 C and the ideal-gas molar volume
gives sevoflurane 182.8, isoflurane 195.8, desflurane 209.7 against Gas Man's
183, 196 and 209 — within 0.6% on all three, and exact for sevoflurane. Gas
Man's figures sit closer to the 20 C derivation than Biro 2014's do, which is
weak evidence for a 20 C reference and is recorded in `PL-S6WW` as such rather
than as an answer.

**Two hazards before copying any of it.** Money means a stored price: Gas
Man's defaults are "USA bottle volume and bottle cost as of March 5, 2008",
with `BottleSize=240` in `GASMAN.INI` (printed p. 171). A shipped price goes
stale and is institution-specific, so it would have to be reader-set rather
than a shipped constant, and a stale one displayed as a clinical-economic fact
is the kind of thing this project's safety standard is about. And the toggle
is a mode: `.claude/rules/expert-review.md` requires hidden modes minimised, so
a unit that switches under a toolbar button has to be legible on the value
itself, not only in the button's state.

**So this item is no longer a candidate for `dropped`.** It is the design
input for planned-milestone item 28, and the question it now carries is which
of Gas Man's three units this project offers, with what provenance for a price
if money is one of them.

**A fourth candidate unit Gas Man predates.** Gas Man's cost display is from a
2008 price list, and in the years since, the argument for low fresh gas flow
has become at least as much environmental as economic — desflurane's global
warming potential is the usual headline. CO2-equivalent is therefore a
candidate unit for item 28 alongside litres, millilitres of liquid equivalent
and money, and it has the same shape as money: a stored per-agent factor, from
a source that has to be cited and can go stale. It is listed here so the unit
decision is taken over the whole field rather than over the three Gas Man
happened to implement. No source has been consulted for it yet; doing so is
part of whatever item 28 becomes.

**DECIDED: liquid agent volume, millilitres by default** (project owner,
2026-09-16). "The values we care about are liquid agent volume, and mL is a
fine default, can add price down road (want user settable price eventually so
user can simulate cost at their institutions price)."

So the unit question this item carried is closed. Of the four candidates —
litres of vapour, millilitres of liquid equivalent, money, CO2-equivalent —
the answer is millilitres of liquid equivalent now, money later as a
reader-set option (`PL-VJZK` carries what that owes), and CO2-equivalent
undecided and not in the way.

**The Gas Man reading above stands: its litres are vapour** (project owner,
2026-09-16: "I misunderstood liters of vapor"). The Workbook's own text does
not name the substance at pp. 180 and 196, but `Cost = DELIVERED Flow x Cost/mL
vapor` (p. 174) does, and `GASMAN.INI`'s per-agent `Volatility` ratio exists to
convert out of it. No ambiguity is left in the record.

**The shape decided is Gas Man's, the default is not** (project owner,
2026-09-16): "ok to do what gas man does, but default unit can be ml of liquid
for now. Will eventually flesh out a widget for more precise control of what's
displayed down road." So the readout offers the same set Gas Man does and
opens on millilitres of liquid equivalent rather than on litres of vapour,
with a display-control widget as later work. That default is a *preference* in
`PL-MQHN`'s sense — it belongs in the preferences store, not in a Workspace —
and it is what `PL-GL5X`'s Load Factory Preferences restores to.

**What is left of this item** is building the readout, which is
planned-milestone item 28's, and it now has its unit.

**Why it matters.** The item is worth reading after it closes rather than
deleting, because it is where the unit decision was actually taken and where the
reference implementation was read. Four candidate units were on the table -
litres of vapour, millilitres of liquid equivalent, money, CO2-equivalent - and
the record of why the answer is the second, with the third deferred and the
fourth left open, is here and nowhere else.

**Done when.** Not applicable: dropped at triage, 2026-09-17, with its question
answered rather than abandoned. The `reason` above names what survives it.

**On dropping it rather than leaving it open.** The earlier paragraph in this
brief that reserved the disposition to the project owner turned on whether item
28 stays on the roadmap. That condition has lapsed - the owner's 2026-09-16
answer places the readout there explicitly ("ok to do what gas man does, but
default unit can be ml of liquid for now"). Reopening it costs one line if that
reading is wrong.

**NOT DROPPED AFTER ALL, 2026-09-17, and the reason is a dependency this item
turned out to be carrying.** Triage had it as a drop - its unit question is
answered and building the readout is planned-milestone item 28's work, not a
queue item's. Then `PL-0S0V` and `PL-VJZK` were read: both are `safety,
anticipated` and both are `blocked-by: PL-B396`. Closing this item would have
reported them as ready to promote, and promoting an `anticipated` safety item is
precisely the event that returns it to the debt gate (`PL-ZF2G`), while the
hazard it describes - a reader-selectable unit, a reader-set price - still does
not exist. So the drop would have pushed two safety findings into a gate that
cannot clear them, on a technicality of queue bookkeeping.

**Decision needed.** Whether `ROADMAP.md` planned-milestone item 28 - the agent
consumption readout - is scoped into a release now, and which.

*Recommendation: not yet, and keep this item open as the handle until it is.*
Five items now depend on item 28 and none of them can say so in `blocked-by`,
because `docket check` accepts only an item id or a version the roadmap names,
and item 28 has neither: `PL-0S0V` and `PL-VJZK` (blocked here), `PL-KZ99` (the
two physical constants), `PL-H4N8` (cost is delivered, not exhausted) and
`PL-DWHV` (uptake is computed and discarded). Scoping item 28 would give all five
a real blocker and let this one close. Leaving it unscoped is also a defensible
answer - the current step is v0.5.0 and item 28 is an addition rather than a
prerequisite - but then this item stays open as the stand-in, which is what the
recommendation asks for rather than a drop.

**Why it matters.** Everything the owner decided on 2026-09-16 about the unit is
recorded here, together with the Gas Man reading behind it. Whichever way the
decision goes, this file is where a session building item 28 finds out why the
answer is millilitres of liquid equivalent, why money is later and reader-set,
and why the accounting Editor keeps litres of vapour.

**Done when** item 28 is either scoped - at which point the five items above are
re-pointed at it and this one closes - or explicitly left unscoped with this item
recorded as the stand-in.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation): still real, with stale numbers corrected here rather than in the text above.** The display facts are unchanged -
`ACCOUNTING_UNIT_CAPTION` at `dashboard_frame.py:251`,
`AGENT_VOLUME_DISPLAY_DECIMALS = 1` at `formatting.py:138`, the "bare L invites
the liquid reading" rationale at `docs/MODEL.md:6626` - and the scope decision
is still open: `ROADMAP.md:3837` says outright that item 28 is named by no
release. Three attributions moved. `PL-S6WW` closed 2026-09-17 (#669), so only
`PL-KZ99` of the two blockers stands - and `PL-KZ99` now names a closed item in
its own `blocked-by`. `PL-H4N8` closed 2026-09-19 (#709) and **already made the
correction this brief says it carries**: `ROADMAP.md:5422` now reads "from the
delivered-agent amount", with the note at `:5429` recording that it read
"exhausted-agent" until 2026-09-19. So the dependants are four rather than
five. The reason to keep this open is untouched: `PL-0S0V` and `PL-VJZK` are
both `safety`-classed and both blocked on it, so closing it promotes two
anticipated safety items into the gate.
