---
id: PL-V6NL
title: Reset, an agent change and a Workspace change discard a run with no undo, so each must ask first; the Apple, GNOME and Windows design guides prefer an undo to a confirmation where one can be offered, and keeping the discarded run so the user could undo the discard would remove the question (found in PL-JV5H's research, 2026-11-28)
priority: P3
effort: L
status: dropped
classes: feature
feature: scenario-branching
touches: src/anesthesia_sim/app/simulation_view.py, docs/INTERFACE.md
deferred-from: v0.7.0 - a feature idea whose open question is whether it enters ROADMAP.md at all; not safety or science, and the three questions it would replace already guard every discard; the release waits only on the owner's test drive (triage 2026-11-28)
added: 2026-11-28
closed: 2026-11-28
reason: Wanted after v0.8.0, not in any release yet (project owner, 2026-11-28, ratified). A feature wanted but not ready to build is one line of intent in ROADMAP.md planned milestones rather than a queue item nobody can start, so it is planned-milestone item 45, which cites this brief for the sources.
payoff: a user who discards a run by mistake can get it back, and is no longer asked to confirm each Reset, agent change or Workspace change
---

**Problem.** Reset, an agent change and a Workspace change discard a run with no undo, so each must ask first; the Apple, GNOME and Windows design guides prefer an undo to a confirmation where one can be offered, and keeping the discarded run so the user could undo the discard would remove the question (found in PL-JV5H's research, 2026-11-28)

**Why it matters.** Each of the three actions throws away the run on screen and every control change in it, so a user who confirms by mistake loses the run. The questions that guard them are the only protection: `docs/INTERFACE.md` § "Discarding a run, and the questions that guard it" says there is no undo. `PL-JV5H`'s research, recorded in its brief on 2026-11-28 with each source read in full, quotes the GNOME Human Interface Guidelines, "Dialogs": "Destructive actions should always be accompanied by either a confirmation dialog or an offer to undo the action", and "undo is typically a better option than a confirmation dialog". It records that Apple's and Microsoft's guides ask for a confirmation where an action cannot be undone, and that Microsoft lists "Provide undo" among the alternatives. The same research found that Gas Man confirms before a substantive change truncates its simulation, and that Blender asks in a pop-up before it discards unsaved changes. Neither, as that research records them, offers an undo for that action.

**What an undo would take.** The discarded run would be kept, with its stored states, its control changes and the runs compared with it, until the user starts something new. An Undo would then put the same screen back, and the three questions would go.

**Decision needed.** Should undoing a discarded run enter `ROADMAP.md`, and if so, in which milestone? It changes what a user sees and does, and it is new scope beyond v0.7.0, so it is the owner's (`CLAUDE.md` § "Architecture and development discipline": an out-of-milestone idea is built when the owner approves the scope change).

**Recommendation:** add it to `ROADMAP.md` as a planned-milestone candidate after v0.8.0, and keep the three questions until it is built. The questions already meet the first half of the GNOME rule, and they are what Gas Man and Blender do for the same kind of action, so nothing a user does today is unguarded. All three platform guides rank an undo above a confirmation, so the idea earns a roadmap line rather than a drop. v0.8.0 is the patient on the five-compartment model, and this is not part of it.

**Answered 2026-11-28.** Add it to `ROADMAP.md` as a planned-milestone candidate after v0.8.0, and keep the three questions until it is built (project owner, 2026-11-28, ratified, over leaving it off the roadmap). It is planned-milestone item 45 in `ROADMAP.md` § "Items added later", which cites this brief. So this item is dropped, as `PL-YBZJ` was for item 42.

**Done when.** The owner's answer is recorded here. If the answer is to build it, then Reset, an agent change and a Workspace change each discard the run without asking, a test shows that Undo puts back the same runs with the same values, and `docs/INTERFACE.md` no longer describes the three questions.
