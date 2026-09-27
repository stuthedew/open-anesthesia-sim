---
id: PL-DB64
title: Defer PL-WZVZ, PL-B396, PL-0S0V, PL-VJZK and PL-KZ99 from Gate 2 to Gate 3 in ROADMAP.md, recording why none can clear before v0.6.0 begins and that none of their hazards is live
priority: P2
effort: S
status: done
classes: docs
milestone: v0.5.15
touches: ROADMAP.md, docs/items/PL-WZVZ-make-an-inter-machine-difference-attributable.md
added: 2026-09-27
closed: 2026-09-27
pr: 1163
payoff: stops five entries that no work before v0.6.0 can close from holding Gate 2 open, and puts the owner's decision to defer them in the gate section beat 3 reads rather than in a thread report alone
verify: grep -qF '**Deferred to Gate 3 on 2026-09-27' ROADMAP.md
---

**Problem.** Defer PL-WZVZ, PL-B396, PL-0S0V, PL-VJZK and PL-KZ99 from Gate 2 to Gate 3 in ROADMAP.md, recording why none can clear before v0.6.0 begins and that none of their hazards is live

**Where this came from.** The Projects thread reporting what v0.6.0 still needs
found five Gate 2 entries that no work before v0.6.0's implementation can close,
and recommended deferring all five to Gate 3 on § "The cadence" beat 3's terms.
The project owner answered "1 agree" on 2026-09-27, so the deferral is recorded
as **(project owner, 2026-09-27, ratified, over keeping the five on Gate 2,
where they would hold the gate open until planned-milestone item 28 and a
machine chooser are scheduled)**. On when to write it, the owner answered
"Whenever you recommend", and the report recommended now: until the gate
section says so, the decision lives only in a thread report, and beat 3 counts
only what the gate's own section records.

**Why none of the five can clear before v0.6.0 begins.**

- `PL-WZVZ` (say which machine parameter separates two machines' curves) is
  `blocked-by` this milestone's own View contract `PL-TH35` and view registry
  `PL-R1WQ`, so it is unworkable until implementation has begun, and by
  `PL-TBMK` (a second machine profile) and `PL-4TWW` (the surface that selects
  between profiles), which no release schedules. It is Gate 1's one deferred
  entry already, sent here by `PL-S5Q9`.
- `PL-B396` (report agent amounts as a liquid-equivalent millilitre figure) is
  held open as the stand-in for planned-milestone item 28, agent cost, whose
  readout it decided: millilitres of liquid equivalent by default, and a
  reader-set price later. Its question is whether a release schedules item 28,
  and none does before v0.6.0 (§ "Planned milestones" item 28 is named by no
  row of the timeline).
- `PL-0S0V` (display precision per unit), `PL-VJZK` (a reader-set agent price)
  and `PL-KZ99` (molar mass and liquid density) are each `blocked-by: PL-B396`,
  because each is work item 28 would create: a reader-selectable unit, a price,
  and the constants a vapour-to-liquid conversion needs.

**The hazards are not live, read against the tree at `19af95d`** (2026-09-27),
which beat 3 requires before a `safety`- or `science`-classed entry may be
deferred. Four of the five are: `PL-WZVZ`, `PL-0S0V` and `PL-VJZK` `safety`,
`PL-KZ99` `science`. `PL-B396` is `ux, docs`.

- `src/anesthesia_sim/data/machines/` holds one profile,
  `reference_circle_system.json`, loaded by name through
  `core/parameters.py`'s `load_reference_circle_system_parameters`; nothing in
  `src/` selects between profiles, and no label in `src/anesthesia_sim/app/`
  names a machine. The trade names under `src/anesthesia_sim/data/` sit in
  provenance notes, which nothing in `app/` reads.
- Agent amounts are displayed in one fixed unit, `app/dashboard_frame.py`'s
  `ACCOUNTING_UNIT_CAPTION` ("Litres of equivalent pure agent gas"), at
  `app/formatting.py`'s `AGENT_VOLUME_DISPLAY_DECIMALS`, with no selector.
- A search of `src/` for price, currency, cost, liquid, density, molar mass and
  millilitres finds none as a stored or displayed quantity - only prose (a
  frame's cost, a plot's density, and one docstring's "24.1 mL" of residual
  circuit gas in `core/circuit.py`). Nothing under `src/anesthesia_sim/` writes
  a file, so no reader-set value can be stored either.

**Why it matters.** Beat 3 clears a gate before its milestone's implementation
begins, and these five cannot close before then, so without a recorded
deferral Gate 2 can never be called clear and v0.6.0 can never begin by the
roadmap's own rule. An entry deferred to nowhere is what holds a release open
(`PL-S5Q9`): the v0.6.0 cut would otherwise meet three `safety` entries and a
`science` one with no destination written anywhere the gate is read, and have
to decide at cut time what the owner has already decided.

**What changes.** `ROADMAP.md` § "v0.6.0 - the layout is the reader's" ->
"Debt gate: the frozen list" gains a paragraph that says so and why, names
Gate 3 and that v0.6.0 ships without the five, and records the hazards above.
The five stay written on the frozen list, moved out of the two lane groups
whose headings say their entries clear before v0.6.0 begins and into a group of
their own, which is what the section already did for `PL-Y04W`. The two
sentences the move makes false are corrected: the "Three kinds of group"
paragraph's "single entry deferred to Gate 3", and `PL-WZVZ`'s "appears below in
the group its lane puts it in". `PL-WZVZ`'s own brief, whose 2026-09-21 section
still says the entry clears in Gate 2, gains a dated note that it no longer
does - a repair to a live brief under `.claude/rules/citation-drift.md`, not a
change to its front matter.

**What `bin/docket wave` reads, measured rather than assumed.** The report and
the brief that started this item expected the paragraph to take the five out of
`wave`'s "this gate can clear". It cannot: `roadmap.gate_status` counts an entry
out only where its `blocked-by` chain leaves the frozen list or the milestone's
own `Required scope` names it, and its docstring says the section's group
headings "are not read, and are not the test". `PL-WZVZ`'s chain leaves at
`PL-TBMK` and `PL-4TWW`, so `wave` already agrees for it. `PL-B396` is at
`needs-decision` with no blocker, and the other three wait only on it, an entry
on the list, so `wave` goes on counting those four as work this gate can clear,
and item 28 has no id or version a `blocked-by` could hold. Measured on
2026-09-27: `bin/docket wave --no-fetch` prints the same gate line on `main` at
`19af95d` and on this item's branch after the edit, `78 cleared, 112 open - 95
this gate can clear, 3 the milestone clears itself, 14 waiting on 5 open items
outside it, and on 5 open items the milestone's Required scope names`, with
`PL-0S0V`, `PL-B396`, `PL-KZ99` and `PL-VJZK` among the 95 and `PL-WZVZ` among
the 14, and the same again after `main` moved to `25e5711`. The paragraph says so rather than claiming agreement,
and the gap is `PL-18BD`, filed with the decision it needs.

**Done when.** `ROADMAP.md`'s v0.6.0 gate section defers the five to Gate 3:
it says so and why for each, names Gate 3 and that v0.6.0 ships without them,
keeps all five written on the frozen list in a group of their own, records for
`PL-WZVZ`, `PL-0S0V`, `PL-VJZK` and `PL-KZ99` that the hazard is not live, read
against the tree, and states how `bin/docket wave` reads the five.

**Explicitly not this item.** Changing any of the five items' front matter,
removing any of them from the frozen list, doing any of their work, scheduling
planned-milestone item 28 or machine selection, or changing how `wave` counts a
deferred entry.
