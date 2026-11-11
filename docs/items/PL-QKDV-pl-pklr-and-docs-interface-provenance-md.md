---
id: PL-QKDV
title: PL-PKLR and docs/interface-provenance.md § 'Adopted' both say an Area keeps no state for the Views previously open in it, but AreaLayout.view_states keeps one state per View kind per Area: on 2026-11-11 a concentration chart set to a 15 minute time base, switched to Wash-in and back, came back at 15 minutes; drop PL-PKLR and correct the sentence 'This project has no code yet'
priority: P3
effort: S
status: done
classes: docs
feature: interface-provenance-adoptions
touches: docs/interface-provenance.md
added: 2026-11-11
closed: 2026-11-11
pr: 2103
payoff: the adopted list says what the Area container keeps, so nobody builds a second state stack
verify: grep -qF 'keeps one saved state for each View kind' docs/interface-provenance.md
reenters: PL-4FBP
---

**Problem.** PL-PKLR and docs/interface-provenance.md § 'Adopted' both say an Area keeps no state for the Views previously open in it, but AreaLayout.view_states keeps one state per View kind per Area: on 2026-11-11 a concentration chart set to a 15 minute time base, switched to Wash-in and back, came back at 15 minutes; drop PL-PKLR and correct the sentence 'This project has no code yet'

**Why it matters.** A contributor who reads the adopted list builds a state
stack that the Area container already has, and `PL-PKLR` sat in the queue as
work to do.

**Done when.** `docs/interface-provenance.md` says what the code keeps, and
`PL-PKLR` is dropped with the measurement as its reason.

**Generator check.** An instance of a closed head's fact: the link between a
document sentence and the tree fact it restates (`PL-4FBP`). The sentence was
true when it was written, and nothing failed when `AreaLayout.view_states`
made it false.

**Done, 2026-11-11.** The sentence now reads "This project keeps one saved
state for each View kind in each Area (`AreaLayout.view_states`), so the
number of registered kinds bounds an Area's list." `PL-PKLR` is dropped.
