---
id: PL-KXTL
title: Ship the three default Workspaces - the central-graph default, induction, and big-picture maintenance - as validated versioned JSON beside the other shipped parameter files
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: S
blocked-by: PL-WV9K, PL-SSQW
classes: feature
touches: src/anesthesia_sim/data/, tests/unit
---

**Problem.** Ship the three default Workspaces - the central-graph default, induction, and big-picture maintenance - as validated versioned JSON beside the other shipped parameter files

**Why it matters.** Item 34 asks for task-oriented presets by example - an
induction Workspace with the concentration graph zoomed in, a big-picture
Workspace to switch to during maintenance - and a default with a central graph
of the compartments and the other Editors around it. They are also what a
learner's "reset" restores to, and what Blender's refusal to delete the last
Workspace needs in order to have something to fall back on.

**Done when.** The three ship as validated versioned JSON beside the other
parameter files under `src/anesthesia_sim/data/`, load through the same path a
learner's own Workspaces do, round-trip under test, and carry the provenance
line `docs/interface-provenance.md` asks of anything modelled on Blender's own
named task Workspaces.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 13.

**The accounting Editor is not in the shipped defaults** (project owner,
2026-09-16). Asked whether the agent-accounting panel should report liquid
millilitres, the owner's position was that "the info on the panel is not info
the user really needs or cares to see. At most, we could turn it into an
optional area widget a user could add back down the road." Stated tentatively
and recorded as stated, but it agrees with `docs/MODEL.md` § "Reachable rather
than simultaneously visible", which already puts the accounting in the one
required tier "a layout may leave them out", so nothing in that document needs
to change for it.

**Consequence for these three Workspaces:** none of the central-graph default,
induction or big-picture maintenance presets names the accounting Editor. It
is reached through the chooser (`PL-50PZ`) instead.

**It cannot be acted on before `PL-50PZ`.** The panel is structurally present
in today's single dashboard, so removing it from the default view before the
chooser exists would make it unreachable and violate the tier's second half —
"must not be removable from the application". The order is the chooser first,
then the defaults that omit it.
