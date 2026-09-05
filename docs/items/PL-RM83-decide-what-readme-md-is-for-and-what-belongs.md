---
id: PL-RM83
title: Decide what README.md is for and what belongs in it before the rewrite starts
priority: P2
effort: S
status: needs-decision
classes: docs
feature: project-introduction
touches: README.md
added: 2026-09-05
---

**Problem.** `README.md` has no stated audience or scope, so every session that
touches it applies its own, and the result is 236 lines that read as accumulated
implementation notes. `PL-N092` (rewrite README as a human-readable
introduction) names the symptom but not the target: "human-readable
introduction" does not by itself say who the reader is or where the boundary
with `docs/MODEL.md` falls, which is why a rewrite started against it would be
one more session's guess.

**Why it matters.** This is the file a first-time reader meets, and the project
owner has stopped README work over it (2026-09-05). Until the audience and the
boundary are fixed, no rewrite can be judged right or wrong, so no rewrite
should start — `PL-QTN6` (freeze README edits) blocks both `PL-N092` and
`PL-RCTQ` on this item.

**Decision needed.** Three questions, from the project owner:

1. **Who is the reader?** A clinician-educator evaluating whether the simulator
   is worth their residents' time; a developer deciding whether to build and
   run it; or the owner's own future self returning after months away. These
   want different documents, and the current README half-serves all three.
2. **Where is the boundary with `docs/MODEL.md`?** The README currently
   descends into numerical detail — display precision, the resolution the
   method supports — that `docs/MODEL.md` already specifies authoritatively.
   The candidate rule is that `README.md` states *what the simulator does and
   what it is not for*, and every quantitative claim lives in `docs/MODEL.md`
   behind a link.
3. **Does it carry current status at all?** `PL-Z4GF` removed a version number
   from the "Current status" heading because it went stale every release. The
   same argument reaches the rest of the status section: `ROADMAP.md` is the
   authoritative milestone map, so the README could link to it and stop
   restating it.

**Done when.** The audience, the `docs/MODEL.md` boundary and the status
question are recorded in this item's body, `PL-N092` is unblocked and its brief
restated against them, and `.claude/rules/readme-hold.md` is deleted in the
commit carrying the first README change.
