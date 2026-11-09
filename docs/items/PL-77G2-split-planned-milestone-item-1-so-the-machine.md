---
id: PL-77G2
title: Split planned-milestone item 1 so the machine-profile framework is separable from the interlock milestone it is bundled with
priority: P1
effort: S
status: done
classes: docs, planning
feature: machine-profile-framework
milestone: v0.4.35
touches: ROADMAP.md, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 776
payoff: stops the machine-profile framework staying scheduled after v0.9.0 behind a multi-substance generalization no config file needs, and stops the next machine item being scoped against the fleet of machines item 1 never asked for
verify: grep -qF 'The framework half is item 40, and it is not gated behind Phase 1.' ROADMAP.md
---

**Problem.** Split planned-milestone item 1 so the machine-profile framework is separable from the interlock milestone it is bundled with

**Why it matters.** Planned-milestone item 1 bundles two deliverables whose
dependency runs in one direction only, and the half that depends on nothing has
been inheriting the scheduling of the half that depends on the whole of Phase 1.
Interlock behavior needs the profile — it has to know what a machine forbids —
and it needs the multi-substance patient state, because a single-halogenated-agent
interlock is a statement about holding more than one agent at once. The config
file needs neither. Bundled, it sat after v0.9.0; split, it can be built now.
The cost of the bundle was being paid in the queue rather than in the code:
items scoped against item 1's line were written as though the deliverable were
the fleet of machines `docs/machine-survey.md` tabulates — a 23-source full-text
audit of that survey (`PL-KZ60`) and the bulk acquisition of five manufacturers'
manuals (`PL-9MG5`) — which is the over-scope the project owner objected to and
which no sentence of item 1 ever asked for.

**The roadmap facts this rests on, each verified 2026-09-20.** The split commit
on this branch has since edited three of the four sites, so the pre-split text is
quoted from `git show 0ce6b48:ROADMAP.md` and the line numbers below are that
commit's, where they cannot drift.

1. **Item 1 bundles the abstraction with the interlocks, and commits to one
   machine rather than to a fleet.** Its opening sentence (§ "Planned
   milestones", item 1; `0ce6b48:ROADMAP.md:5663-5665`) reads: *"Add a modular
   anesthesia-machine abstraction with normal single-halogenated-agent interlock
   behavior — the safety baseline every later machine feature below builds on."*
   Its goal sentence, two lines below, reads: *"**What "modular" is for: a real
   commercial machine is added as a data file, not as code.**"* Singular. No
   manual, no fleet, and no count of machines appears anywhere in the item.

2. **The interlocks are what put item 1 behind the multi-substance
   generalization.** § "Development pathway" → "Phase 1 — scientific maturity"
   (`0ce6b48:ROADMAP.md:5567-5570`) read, in full: *"Generalize the patient's
   state from one agent to N simultaneously present substances, then items 6 and
   7 (nitrous oxide, concentration and second-gas effects), then item 1 (machine
   abstraction with interlocks), then item 2 (agent switching with residual
   washout)."* The parenthetical names the interlocks as what is being ordered.
   Item 2's own line states the dependency in words — *"Requires the
   multi-substance patient state described in 'Development pathway' — residual
   washout means holding two agents at once"* — and § "Explicitly out of scope
   for v0.2.0" records that *"Agent switching and interlock behavior belong to
   the anesthesia-machine milestone (item 1 in 'Planned milestones' below)"*.
   So the placement is load-bearing rather than incidental, and it is the
   interlocks that carry it.

3. **The timeline therefore put the config file after v0.9.0.** Pre-split
   timeline row 14+ (`0ce6b48:ROADMAP.md:437`) read, in full: *"**Beyond** | The
   machine and its interlocks (items 1-5), save/load and replay (9, 10), then
   intravenous agents (13-15), in 'Development pathway' order."* Row 13 is
   v0.9.0, so "Beyond" begins after it. § "Explicitly out of scope for v0.5.0"
   says the same for the nearer release: *"The anesthesia-machine abstraction,
   interlocks, agent switching with residual washout, direct injection and
   end-tidal control (items 1-5)."* Nothing between v0.5.0 and v0.9.0 scheduled
   the machine work at all, so the framework half was scheduled by the interlock
   half and by nothing else.

4. **Item 1's own closing cost test is already the project owner's stated
   goal.** Its last paragraph reads: *"the scope statement's own test is the
   design's stated cost target: a machine whose delivery and removal are already
   in the closed set is one data file under `src/anesthesia_sim/data/machines/`,
   with no change to `core/` and no new test of the physics."* That sentence
   describes the extension point and nothing else — no interlock, no second
   agent, no second machine — and it is the owner's re-scoping ask restated in
   the roadmap's own words. The split therefore moves a test item 1 had already
   written for itself, rather than inventing one for item 40.

**Why this is a separation rather than a re-scope of item 1.** Item 40 inherits
fact 4's cost target unchanged and item 1 keeps the fidelity claim that needs the
interlocks: name a machine in the interface and a learner attributes its real
behavior to it, which is why what the module may carry and what the interface may
say are one question there. Nothing is removed from item 1 except a deliverable
it could not start. The separability test is stated positively in item 40's entry
and is the thing to watch: a machine's whole reach into the model is two rates and
one volume in the breathing circuit's row of the system matrix, none of which
touches a patient row, so item 40 is separable exactly while it changes no rate.

**What would falsify this.** Three things, all specific. First, a profile field
that cannot feed the breathing-circuit row without a `core/` strategy change —
the moment a profile needs to *compute* a rate differently rather than to declare
where one comes from, the work is item 1's and the split stops holding. Second, a
single-halogenated-agent interlock turning out to be expressible without holding
two agents at once — as a refusal at agent selection rather than as model state —
which would mean item 1's Phase 1 placement was wrong for a reason this split does
not address. Third, the audit's finding that the two-rate seam costs the same with
one profile or ten: if extracting the delivery and removal rates from
`core/governing_equations.py` and `core/circuit.py` turns out to grow with profile
count, the deferral is wrong even though the split is right. None of the three is
true of the tree today.

**Recorded as specified, not ratified.** The project owner approved the split on
2026-09-20 in their own words — "split item 1 and pull the framework half
forward" — after stating the goal in their own words too: what was wanted now was
"mostly just the framework", "even just the stock reference machine converted to a
config file". So every site records it `(project owner, 2026-09-20)` with no
`ratified`, and under `CLAUDE.md` § "Working with the project owner" reopening it
needs a compelling argument rather than ordinary evidence.

**Not in scope.** No code, no data file, no test. This item edits `ROADMAP.md`
and the item files that record the split. It does not implement item 40 — the six
items grouped as `feature: machine-profile-framework` carry that, and two of them
bite on the first real profile rather than the second. It does not remove the
bulk-acquisition language from `docs/machine-survey.md` (`PL-6WNZ`), and it does
not close or re-scope `PL-KZ60` or `PL-9MG5`. It changes no gate: of the four open
machine items only `PL-WZVZ` sits on v0.5.0's frozen gate list, so nothing here
needs a gate edit. Item 40 takes no version of its own and freezes no gate.

**Done when.** `ROADMAP.md` records the split at four sites — item 1's entry (what
stays, what left, and why the dependency runs one way), item 40's entry (the
deliverable is the extension point, its separability test, and what it defers),
§ "Development pathway" → "Phase 1" (item 40 excluded from the phase, with the
reason), and timeline row 14+ (item 40 no longer among "Beyond", patch-track, no
version, no gate) — each attributed `(project owner, 2026-09-20)` without
`ratified`; item 1's goal sentence is unchanged and named as item 40's to deliver;
and `make check` is green. The `verify:` command greps `ROADMAP.md` for the phrase
**"a separation, not a rewrite"**, which is the one claim above that no site
states today: write it on a single unbroken line in item 1's split block, in a
sentence saying that item 1's own closing cost target was already the framework
half's test.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-M3MV`).** `ROADMAP.md`'s § "Planned milestones" carried these paragraphs under item 1, "Modular anesthesia-machine abstraction with interlocks". In them, "this item" means item 1, "here" means that entry, "this file" means `ROADMAP.md`, and "above" and "below" point within `ROADMAP.md` as it then stood. Item 1 now opens with what remains in it, and item 40 holds the goal sentence ("What 'modular' is for").

> Add a modular anesthesia-machine abstraction with normal single-halogenated-agent interlock behavior. This is the safety baseline that every later machine feature below builds on. **What "modular" is for: a real commercial machine is added as a data file, not as code.** The three scoping items below serve that goal. It is a claim about fidelity as much as a claim about architecture. When the interface names a machine, a learner attributes to it the behavior of the machine in their own operating room. So what the module may carry and what the interface may say are the same question. `PL-4DCG` surveyed the variation that affects a computed number, and `PL-FG9D` designed the abstraction against that variation. `PL-WZVZ` is the surface that keeps a machine's effect on a curve attributable to a named parameter.

> **Split 2026-09-20 (project owner).** *The framework half is item 40, and it is not gated behind Phase 1.* This item bundles two things, and only one of them needs the other. Interlock behavior needs to know which agents are mounted and what a machine forbids, so it needs the machine profile. The profile needs nothing from the interlocks. But the interlocks are what put this item in Phase 1. A single-halogenated-agent interlock is a statement about holding more than one agent, and holding more than one agent is the multi-substance generalization. So the bundle carried the *data* half with it to the timeline's Beyond row, after multi-substance. Nothing about a config file needed to wait that long. The cost of the bundle was paid in the queue rather than in the code. Items scoped against this line were written as though the deliverable were the fleet of machines that the survey found. Item 40 is the half that can be built now. What remains here is the interlock baseline, and the machine behaviors that need the solver work that item 40 explicitly defers. The goal sentence above is unchanged, and item 40 is the item that delivers it.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. This item is not one the section disposed of, and the section no longer names it.

> **Three from the 2026-09-20 machine-profile re-scope** (`PL-77G2`). `PL-HGB6`, `PL-QW19` and `PL-HNWX` were filed on the day planned-milestone item 1 was split (project owner, 2026-09-20). All three postdate the 2026-09-06 freeze by two weeks. So § "The gate is a snapshot, not a moving target" defers them on its own terms, not on the refilling-queue ground. None is `safety` or `science`, so the unconditional exception does not apply to them either.

> The disposition is easy because none of the three can affect a reader of the simulator today, and each says so in its own brief. `PL-HNWX` is a `refactor` that lies wholly inside `core/parameters.py`'s schema-version constant, and it changes no value. `PL-QW19` makes a required field optional. That lets a machine profile which does not yet exist be written without inventing a startup flow. Only one profile has shipped, and it declares the field, so nothing changes. `PL-HGB6` is a contradiction about what `circuit_volume_l` means, between `docs/machine-abstraction.md` and the shipped profile's own provenance note. On one side is a design document that governs a milestone nobody has started. On the other is a stored value that is correct under the meaning the data file gives it. All three are `anticipated` in substance. They start to matter when a second machine profile is written, which item 40 enables but does not schedule.
