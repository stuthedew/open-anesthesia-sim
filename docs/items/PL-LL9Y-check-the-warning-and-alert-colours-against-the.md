---
id: PL-LL9Y
title: Check the warning and alert colours against the medical alarm-colour convention
priority: P3
effort: S
status: needs-decision
classes: ux
feature: presentation-safety
touches: src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md
added: 2026-09-02
---

**Problem.** `app/theme.py:12` defines `WARNING = "#8A4B08"` — a dark brown-orange
— and the halted-run banner introduced by PL-018 ("Stopped — simulation error",
`ROADMAP.md:213-218`) is the surface that uses this class of colour. The value
was picked for text contrast against a light panel. It was not picked against
any convention for what an alert colour means on medical equipment, and nobody
has checked whether it should have been.

**Why it matters.** The project has already settled the general principle for
itself, in `app/theme.py:30-37`: displaying a colour obligates displaying the
*right* one, which is why the ISO 5360 agent colours are honoured even where
separability suffers. The same reasoning may apply here. Anaesthesia monitors
and ventilators in the environments this simulator teaches for signal alarm
priority by colour under IEC 60601-1-8, and a learner who has internalised that
mapping brings it to this screen whether or not the screen intends it. A
simulator that uses a monitor's alarm colour to mean something else, or uses a
different colour for something a monitor would flag, is teaching against the
equipment — an educational defect by the same logic that makes a wrong agent
colour a safety defect, and one WCAG says nothing about.

**Decision needed.** Whether this simulator follows the medical alarm-colour
convention for its alert surfaces, deliberately departs from it, or has no
alert surface significant enough for the question to bite yet. All three are
defensible; what is not defensible is the current state, where the colour was
picked for contrast alone and the question was never asked.

**Not a compliance claim.** IEC 60601-1-8 governs alarm systems on medical
*electrical equipment*. This is an educational simulator and the standard does
not bind it. The question is whether to follow the convention anyway for
educational fidelity, and it is genuinely open — the opposite argument, that a
simulator should look unmistakably unlike a monitor so nobody mistakes it for
one, is also reasonable and consistent with the project's disclaimers.

**Do not resolve this from memory.** Check the actual priority-to-colour mapping
against the standard's own text or an authoritative secondary source before
writing anything down; a colour convention recalled rather than read is exactly
the failure mode the ISO 5360 provenance chain in `theme.py` was built to avoid.

**Approach.** Establish the mapping from the source. Decide whether the
simulator follows it, deliberately departs from it, or has no alert surface
significant enough to matter yet. Record the decision and its reasoning beside
the ISO 5360 note, since it is the same class of question. Whatever colour
results still has to clear `PL-MMYM`'s contrast target — convention and contrast
are both binding, not alternatives.

**Where.** `app/theme.py:12`; the halted-run banner in
`src/anesthesia_sim/app/simulation_view.py`; `docs/MODEL.md` beside the agent
colour section.

**Done when.** The alert colours are either aligned to the convention or
documented as a deliberate departure with the reason, and the choice is
traceable to a source rather than to a preference.
