---
id: PL-QXYW
title: docs/interface-provenance.md says a reader can never be wrong about what context a displayed value belongs to, in two places, and neither names the document that sets the requirement (copy editor structure read, 2026-11-05)
priority: P3
effort: S
status: done
classes: defect, docs
feature: interface-provenance-structure
touches: docs/interface-provenance.md
added: 2026-11-05
closed: 2026-11-16
pr: 2168
payoff: a contributor designing the handling of modes reads the context requirement at its true strength, with the document that sets it
verify: ! grep -qF "The project's safety standard needs one" docs/interface-provenance.md
---

**Problem.** docs/interface-provenance.md says a reader can never be wrong about what context a displayed value belongs to, in two places, and neither names the document that sets the requirement (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/interface-provenance.md at cfb15a4a, before the line edit):

- **Query on the requirement about a displayed value's context:** rows 803-814 and rows 917-920 both state that "a reader can never be wrong about … what context a displayed value belongs to". It should be stated in one place, and neither place says where the project sets this requirement. Which document sets it?

**Checked 2026-11-09:** `grep -n 'never be wrong' docs/interface-provenance.md` finds one statement, in § "There is no mode-awareness doctrine to borrow": "The project's safety standard needs one, because it requires that a user can never be wrong about what state the application is in, or about what context a displayed value belongs to." The restructure (`PL-T8RL`) removed the second statement, so half of the finding is fixed. The other half still applies. "The project's safety standard" names no document, though § "Blender's reason for non-overlapping is not this project's reason" names "the safety-critical standard in `CLAUDE.md`" and `docs/INTERFACE.md` § "Minimum displayed outputs". The sentence is also stronger than its source. `CLAUDE.md`'s safety-critical clinical-output standard asks that "units, model identity, relevant assumptions, simulation state, and context cannot be easily misread".

**Why it matters.** A contributor designing the handling of modes needs the requirement at its true strength and where to read it. "Can never be wrong" sets a bar that no design can be shown to meet, and gives no source to check it against.

**Done when.** The sentence names the safety-critical clinical-output standard in `CLAUDE.md`, and `docs/INTERFACE.md` § "Minimum displayed outputs" where it applies. It states the requirement as that standard does: state and context cannot easily be misread.

**Generator check.** One-off: a finding from the `docs/interface-provenance.md` structure read (`PL-ZMBN`).

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/interface-provenance.md` already states that a reader "can never be wrong" about state or context in two places (rows 730 and 787), with no document named. So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.

**Done 2026-11-16.** § "There is no mode-awareness doctrine to borrow" now names the safety-critical clinical-output standard in `CLAUDE.md` as the source of the requirement, and states it at that standard's strength: a clinically meaningful display is designed so that its simulation state and context cannot easily be misread, along with its units, model identity and relevant assumptions. It also names `docs/INTERFACE.md` § "Minimum displayed outputs" (heading checked to exist exactly) as the list of state and context the interface must always show, such as the run state, the running agent and each setting changed during the run. A docs sweep (`grep -n -i 'never be wrong\|can never\|safety standard'`) found one more overstatement of the same requirement, in § "Adopted"'s "Context sits above tools" paragraph ("a user can never mistake which context a displayed value belongs to"). It was brought to the same strength and now points back to the mode-awareness section rather than restating the source, so the requirement is stated in one place. Files checked: `docs/interface-provenance.md`, `CLAUDE.md` § "Safety-critical clinical-output standard", `docs/INTERFACE.md` § "Minimum displayed outputs".
