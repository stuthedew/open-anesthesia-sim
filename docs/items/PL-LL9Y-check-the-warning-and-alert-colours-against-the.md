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

## Worked 2026-09-13: the third option is right today, established from the code rather than from the standard's table

**Answer, on the code: this interface has no visual alarm signal, so the
convention has nothing to bind.** IEC 60601-1-8 governs *visual alarm signals* —
indicators that encode priority by colour together with a flash rate. Every use
of `WARNING` in this tree is `ft.Text(...)`, bold, coloured. There is no
indicator lamp, no filled banner, no flashing element, and no priority tier.
Checked exhaustively, not sampled — all five surfaces:

| surface | what it is |
| --- | --- |
| `_status_text` | the run-status word, "Stopped — simulation error" |
| `_notice_text` | a transient notice line |
| `_agent_accounting_status_text` | the agent-accounting status word |
| the persistent disclaimer | "Educational simulation only. This idealized model is not a clinical prediction, monitoring, or dosing tool." |
| the case-discard dialog | confirmation text before discarding a run |

**The fourth row is the one that settles it, and it points the opposite way from
adoption.** `WARNING` is the colour of a disclaimer that is on screen *always*.
A monitor's alarm colours are meaningful precisely because they are absent until
something is wrong; a permanent element painted in a high- or medium-priority
alarm colour would teach the opposite of the convention it borrowed — an alarm
colour that means nothing, on screen from the moment the app opens. Adopting the
mapping onto this constant would be a worse educational outcome than the current
state, not a better one, which is the answer this brief could not have without
looking at where the colour is actually used.

**The interface already runs a deliberate signal economy**, which is the same
reasoning one level down and was found in place at `simulation_view.py:2325-2330`:
the supported-run-length boundary is `MUTED`, not `WARNING`, because "colouring a
correct model's declared boundary as a fault teaches a reader to distrust a
number that is sound, and would spend the one signal this interface has for a
real one." That is a one-signal design, not a priority scheme, and it is the
right shape for a surface with one failure state.

**So `WARNING = #8A4B08` is not changed, and the reason is recorded rather than
the colour being left unexamined** — which is what this brief correctly said was
indefensible about the previous state.

### What was sourced, and what could not be — stated rather than implied

**Established** from two independent searches: high priority is **red**, medium
priority is **yellow**.

**Not established here, and it must not be written into this repository until it
is:** the low-priority colour (cyan and blue are both reported in secondary
material, and they are not the same claim), the flash frequencies and duty
cycles, and any rule reserving colours for information signals.

The standard is paywalled (ISO/IEC store, `iso.org/standard/41986.html`) and was
not reached from here. Every candidate authoritative secondary source was blocked
by this container's egress proxy — `ti.com`, `sameskydevices.com`, `puiaudio.com`,
`60601-1.com`, `jbth.com.br` — and a PubMed search on the standard number returned
zero records. So what is above is the reachable fragment and is labelled as such,
on the precedent `PL-BLHV` set in this same gate: cite what was checked, and say
plainly what was not, rather than implying a reading of a text nobody opened.

**This does not weaken the answer**, because the answer does not depend on the
table. "There is no visual alarm signal in this interface" is established from
`simulation_view.py`, and no priority-to-colour mapping changes it. A session
that *does* need the table — the one answering the question below — has to reach
the standard first, and should say so if it cannot.

### Still open, and only this: what happens when the Qt port gives us a real one

The answer above is bounded to the surface that exists today. `v0.5.1` rewrites
the dashboard, the chart and the theme in PySide6, and `ROADMAP.md` records that
the port "redecides palette, type scale, spacing and layout regardless" — so it
is the moment an indicator-shaped surface could appear, and the moment this
question actually bites.

**The question is the project owner's**, and this brief already states why: it
rests on what the simulator is *for*. Both answers are defensible and they are
genuinely opposed — follow the monitor convention so a learner's trained
colour-to-urgency mapping transfers, or deliberately diverge so nobody mistakes
a teaching tool for a monitor. That is a call about the product, not about the
code, and `.claude/skills/docket/SKILL.md` puts it on the owner's side of the
line: "an item whose answer rests on what the project is for is the owner's,
however obvious the answer seems from inside the session."

Two things bound whichever answer is taken, and neither is in question:
`PL-MMYM`'s contrast target still binds any colour chosen, and the ISO 5360
agent colours are untouched by this — they identify an agent and carry no
urgency.

**Left `needs-decision` rather than closed**, because closing it on today's
surface would lose the question at exactly the milestone that raises it.
