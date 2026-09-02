---
id: PL-5WFS
title: docket next cannot see a brief's stated prerequisite, so it offers PL-F52R ahead of the PL-WB0X extraction that gates it
status: untriaged
feature: planning-cadence
touches: subprojects/docket/src/docket/plan.py, docs/items/
added: 2026-09-02
---

**Problem.** Inside the current step, `docket next` ranks by priority band and
by which feature is nearest finishing. It does not read a brief's body, so a
stated prerequisite — "do this after PL-WB0X stage 1", "depends on PL-DHV7 for
the unit" — is invisible to it.

v0.4.0 is the live instance, as of 2026-09-02. `docket next` offers, in order,
`PL-F52R` (draw the MAC-awake reference band), `PL-ZRSP` (plot the F_A/F_I
ratio) and `PL-DHV7` (express concentrations in MAC multiples) — all `P1`, all
in scope. But `PL-F52R`'s brief says it depends on `PL-DHV7` for the unit, and
`PL-DHV7`'s says to do it after `PL-WB0X` stage 1 (the Flet-free formatting
module). So the first three suggestions are in close to the reverse of the
order the briefs state, and `PL-WB0X` — the item that actually goes first —
is offered nowhere near the top, being `P2`.

**Why it matters.** A session that trusts the ranking starts `PL-F52R`, and
either discovers the dependency after reading the brief (one lookup, the cheap
outcome) or does not, and rewrites formatters that `PL-WB0X` is about to move.
The cost is small per session and paid by every session that picks up v0.4.0
work, which is the whole of the milestone now that it is the current step.

**A mechanism already exists and may be the whole answer.** `status: blocked`
with `blocked-by:` removes an item from `docket next` entirely; `PL-B9PY` uses
it. The open question is whether it is the right instrument here. It is a
strong statement — "cannot be started" rather than "goes second" — and it takes
the item out of the ranking rather than reordering it, so a milestone worked
strictly in dependency order would show most of itself as blocked. The
alternative is a weaker `after:` field that reorders without excluding, which
is new surface for a problem that may not recur.

**Decide before building anything.** Whether this happens often enough to earn
a mechanism at all is the first question, and the honest answer today is one
instance. Using `blocked-by` on `PL-DHV7` and `PL-F52R` costs nothing and would
have prevented this one; that may be the entire fix, with no code.

**Where.** `subprojects/docket/src/docket/plan.py` (the ranking), and the
briefs of `PL-DHV7` and `PL-F52R`, which state the prerequisites in prose.

**Found.** 2026-09-02, recording v0.4.0's scope decisions. `docket next` was
run immediately afterwards and offered `PL-F52R` first, against the sequencing
the same change had just written into `PL-WB0X`.

**Done when.** Either v0.4.0's dependent items carry the prerequisite in a
field `docket next` reads, so the ranking matches the briefs; or the item is
`dropped` with the reason that one instance does not earn a mechanism, leaving
this brief as the record and the prose as the only statement.
