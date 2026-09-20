---
id: PL-439V
title: Make the Tec 6 the concrete second device class the machine abstraction is designed against
priority: P2
effort: S
status: done
classes: docs, anticipated
feature: anesthesia-machine
touches: docs/MODEL.md, ROADMAP.md, docs/machine-abstraction.md
added: 2026-09-06
closed: 2026-09-20
payoff: closes the design question the machine abstraction had to answer before a second machine could be added - the Tec 6 is named as its own device class rather than flattened into a variable-bypass vaporizer with an 18 in the maximum field
verify: grep -q 'fixed_volume_percent.*dial is volumes percent' docs/machine-abstraction.md
---

**Problem.** `PL-FG9D` (design the base anesthesia-machine abstraction so a
real commercial machine is a data-plus-plugin addition) names the failure mode
this item is about, in the abstract: *"If a machine is only a bag of numbers,
then a machine whose vaporizer is a fundamentally different device is
represented as a variable-bypass one with different numbers, and the interface
will show a trade name attached to behavior that machine does not have."* It
does not name a machine, and a design principle with no worked example against
it is a principle that passes.

This project already ships the example. Its three agents come from two device
classes: sevoflurane and isoflurane from variable-bypass vaporizers, desflurane
from the Datex-Ohmeda Tec 6, an electromechanical gas–vapour blender. Today the
difference is representable as a bag of numbers, because the only vaporizer
property the model carries is `max_delivered_concentration_percent` — 8, 5, 18
— and 18 really is just a larger number. The moment ambient pressure becomes a
parameter, or a machine module names a trade name, it stops being one:
a variable-bypass dial approximately holds delivered *partial pressure* as
ambient pressure falls, while the Tec 6 holds delivered *volumes percent* and
its partial pressure falls with ambient pressure. `PL-5K5C` (record the model's
sea-level assumption) carries that physics with its sources.

**Why it matters.** The discriminating test of `PL-FG9D`'s abstraction is
whether a Tec 6 can be added to it without either (a) becoming bespoke code
with its own calculation path, or (b) being flattened into a variable-bypass
vaporizer with an 18 in the maximum field. Both failures are the ones
`PL-FG9D` already anticipates; what this item adds is a case that decides
between designs rather than a criterion that any design can claim to meet.
`PL-043` (decide whether the vaporizer dial should move in real increments)
made the matching observation from the interface side — *"the Tec 6 is a
different device class"* — and left its fidelity trade-off explicitly
reversible if real machine simulation is ever built.

`ROADMAP.md` already excluded this once, on v0.2.0: *"Vaporizer-specific
delivery-device physics (e.g. desflurane's heated, pressurized vaporizer
requirement) — this milestone models uptake and distribution only, not the
delivery device."* That exclusion is recorded as a milestone boundary and never
as an intent to return, so nothing in "Planned milestones" carries it forward.

**Why it is `anticipated` rather than ready.** The work is `PL-FG9D`'s to do,
and `PL-FG9D` is itself blocked. Nothing here should be built before that
design round; this item exists so the design round has the case in front of it
rather than rediscovering it afterwards, when the second machine is always the
one that fits.

**Where.** `PL-FG9D`'s brief and whatever specification it produces; then
`docs/MODEL.md` where the machine abstraction is documented. Possibly one line
in `ROADMAP.md`'s "Planned milestones" item 1, which today says only "a modular
anesthesia-machine abstraction with normal single-halogenated-agent interlock
behavior" — that is the project owner's call, not this item's.

**Done when.** The machine abstraction's specification names the Tec 6 as a
device class distinct from variable bypass, states which behaviour a module
supplies rather than inherits, and shows how each of the two classes is
expressed under it — or records, with reasons, that delivery-device class is
deliberately outside the abstraction and what a machine module may therefore
not claim.

## Satisfied by `PL-FG9D`'s specification, 2026-09-20 (`PL-8G48`)

Read against the tree after `PL-FG9D` (design the base anesthesia-machine
abstraction) closed as `#748`. `docs/machine-abstraction.md` § "Dial mapping"
answers all three clauses of the first disjunct in "Done when" above, so this item is `done`
rather than promotable:

- **Names the Tec 6 as a device class distinct from variable bypass.** The dial
  mapping table carries two members, `variable_bypass` ("dial is a
  partial-pressure fraction", from today's model) and `fixed_volume_percent`
  ("dial is volumes percent"), the second sourced to survey section (b1) and
  named as the Tec 6.
- **States which behaviour a module supplies rather than inherits.** `dial_mapping`
  is one of the fields in that document's "fields the survey's evidence admits"
  table, whose consumer is the model and whose effect is "which strategy runs" -
  so a profile supplies its mapping by name and inherits the rest.
- **Shows how each class is expressed under it.** The same table, plus the
  paragraph stating that the two mappings differ by
  $`P_{\mathrm{ambient}}/P_{\mathrm{reference}}`$.

**And it records the part this item most wanted recorded**, which is that the
distinction is currently a declared coincidence rather than a working one: the
model has no ambient pressure, so in its present domain the two functions agree
everywhere, and `PL-5K5C` (record the model's sea-level assumption) is what
separates them. That is the discriminating test this item asked for, answered
honestly rather than by a principle any design could claim to meet.

**The `ROADMAP.md` half was never this item's to do.** The brief already says
the possible line in § "Planned milestones" item 1 "is the project owner's call,
not this item's", so nothing is outstanding here. Item 1 now names `PL-FG9D` and
`PL-4DCG` outright, which `PL-Z4WL` added.
