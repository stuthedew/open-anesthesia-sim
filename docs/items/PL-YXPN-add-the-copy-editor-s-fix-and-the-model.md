---
id: PL-YXPN
title: Add the copy editor's fix and the model-specification rewrites it holds to v0.7.0's Required scope, at the project owner's word of 2026-11-04 20:12Z
priority: P2
effort: S
status: ready
classes: planning
touches: ROADMAP.md
added: 2026-11-04
payoff: v0.7.0 is not cut until the copy editor works and the model-specification sections it holds are written for a clinician
verify: grep -q "The copy editor, fixed, and the rewrites it holds" ROADMAP.md
---

**Problem.** The project owner asked for the copy editor work to belong to
v0.7.0 (project owner, 2026-11-04 20:12Z: "Refresh main and in flight. At the
copy editor stuff to .7 release new patch release in the meantime."). The
message was voice-typed, and "At" is read as "Add".

**Reading.** v0.7.0 is not cut until the copy editor is fixed, so its fix joins
v0.7.0's Required scope, and the patch release, v0.6.15 (`PL-8B6Z`), ships what
is finished meanwhile. "The copy editor stuff" is read as `PL-HGZS`, the live
generator that records the copy editor's fault, and the five `docs/MODEL.md`
rewrites its `root-cause-of` names: `PL-HRPK`, `PL-PS5H`, `PL-XBJ3`, `PL-XT53`
and `PL-YVL0`. Each of those waits on the copy editor and describes text a
learner reads beside the schematic. The other items that `#2035` groups under
the `copy-editor` feature are not named one by one, because the feature
changes as the copy editor is debugged. The reading was stated to the owner in
the thread before this landed, with an invitation to correct it.

**Change.** `ROADMAP.md` § "v0.7.0 - the schematic" gains Required scope item
12 and one Definition of done bullet.
