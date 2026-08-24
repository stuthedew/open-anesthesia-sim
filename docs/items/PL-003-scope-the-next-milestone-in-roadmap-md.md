---
id: PL-003
title: Scope the next milestone in ROADMAP.md
priority: P1
effort: M
status: ready
classes: planning
touches: ROADMAP.md
added: 2026-08-23
---

**Problem.** No milestone after v0.2.0 is scoped (v0.2.1 is a validation
hotfix on that baseline and v0.2.2 a hardening release on it, neither of
them a milestone). `ROADMAP.md`'s
development rules require a goal, required scope, definition of done, and
an explicit out-of-scope list before implementation begins, and the next
candidate is the modular anesthesia-machine abstraction with normal
single-halogenated-agent interlock behavior.
**Why it matters.** This is the gate on all feature work: items 2-5 of the
planned-milestone list all build on it, and nothing in that direction can
start until it exists. It is also the answer to "are we in a good spot to
move on to the next roadmap feature?"
**Where.** `ROADMAP.md` ("Next milestone" and "Planned milestones").
**First step.** Draft the goal and the out-of-scope list first; the
out-of-scope list is what keeps the milestone narrow.
**Done when.** `ROADMAP.md` carries a fully specified milestone with a
version number assigned, matching the structure of the completed v0.1.0 and
v0.2.0 sections.
