---
id: PL-5XVQ
title: Decide whether to adopt Blender's Maximize Area (one Area fills the Area region and a second press restores the layout): no menu, key or model operation offers it, docs/interface-provenance.md's adopted, diverged and refused lists do not disposition it, and it is the one Blender layout operation a teacher projecting a single chart would use most
priority: P3
effort: S
status: ready
classes: planning
feature: window-is-the-frame
touches: ROADMAP.md, docs/interface-provenance.md
added: 2026-11-11
payoff: the roadmap names Maximize Area, so a teacher's way to show one chart large is built after the Areas fill the window and is not forgotten
verify: grep -qF 'Maximize Area' ROADMAP.md
---

**Problem.** Decide whether to adopt Blender's Maximize Area (one Area fills the Area region and a second press restores the layout): no menu, key or model operation offers it, docs/interface-provenance.md's adopted, diverged and refused lists do not disposition it, and it is the one Blender layout operation a teacher projecting a single chart would use most

**Decided: adopt Maximize Area** (project owner, 2026-11-11, ratified, over
leaving it out). The owner agreed to the session's recommendation: record it
as one line of intent in `ROADMAP.md` § "Planned milestones", under item 34,
and build it after the Areas fill the window exactly (`PL-CBYS`). The roadmap
line is not written yet. The session that takes this item writes it, and adds
the operation to the adopted list in `docs/interface-provenance.md`.

**Triaged, 2026-11-11.** What is left is two document edits. Building the
operation waits until `PL-CBYS` has landed (project owner, 2026-11-11), and
gets an item of its own when it is scoped.

**Why it matters.** A teacher projecting one chart has no way to give it the
whole Area region and then get the layout back. Until the roadmap names the
operation, the decision to adopt it lives only in this item.

**Done when.** `ROADMAP.md` § "Planned milestones" item 34 carries one line
of intent for Maximize Area, and `docs/interface-provenance.md` lists it as
adopted and not yet built.
