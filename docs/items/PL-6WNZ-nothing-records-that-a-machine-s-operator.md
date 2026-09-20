---
id: PL-6WNZ
title: Nothing records that a machine's operator manual is gathered as that machine's profile is built, so the survey's eight-machine table reads as a list of machines to implement
priority: P3
effort: S
status: ready
classes: docs
feature: anesthesia-machine
touches: docs/machine-survey.md, docs/items
added: 2026-09-20
payoff: stops a later session reading the machine survey as eight profiles to build, and stops the milestone blocking on manuals nobody needs yet
verify: grep -qF 'sought as that machine' docs/machine-survey.md
---

**Problem.** Nothing records that a machine's operator manual is gathered as that machine's profile is built, so the survey's eight-machine table reads as a list of machines to implement

`docs/machine-survey.md` names eight machines and gives each one an axis of
variation it contributes. That is a survey of what *varies*, not a commitment to
ship eight machine profiles — but nothing in the document says so, and the
project owner had to say it out loud instead (2026-09-20): *"Just because you
discovered all the machines out there doesn't mean we need to implement them
all. More just wanted the functionality, to be able to implement them."*

The same correction applies to the reference material. `PL-4DCG`'s survey
session ended its handoff asking for machine operator's manuals to be added to
`open-anesthesia-sim-references`, and that session is now archived, so the ask
existed nowhere in the tree. Restated here in the form the owner chose: **one
manual at a time, as the profile that needs it is built** — not a bulk
collection ahead of the milestone.

**Why it matters.** `PL-FG9D` (design the base machine abstraction so a real
machine is a data-plus-plugin addition) already has the right shape: the
deliverable is the extension point, and each machine is an addition against it.
A later session reading the survey's table without that framing has two ways to
go wrong, and both are expensive. It can treat eight profiles as the milestone's
scope, which is work nobody asked for. Or it can block on manuals it cannot
obtain — the acquisition step needs vendor or institutional access a session
does not have — and stall a milestone whose first machine needs exactly one
manual.

**Done when.** `docs/machine-survey.md` states, where the machine table is
introduced, that the set is a map of the variation a machine profile has to be
able to express rather than a list to implement, and that each machine's manual
is sought as that machine's profile is built. `PL-FG9D`'s brief carries the same
sentence about acquisition, so the design item and the survey agree.

**Explicitly not this item.** Obtaining any manual, and building any machine
profile. This item only writes down the rule so the next session does not have
to ask again.
