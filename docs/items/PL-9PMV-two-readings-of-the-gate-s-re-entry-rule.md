---
id: PL-9PMV
title: Two readings of the gate's re-entry rule disagree, and a real finding now sits between them
priority: P2
effort: S
status: needs-decision
classes: defect, docs
feature: planning-cadence
touches: ROADMAP.md
added: 2026-08-30
---

**Problem.** `ROADMAP.md` states the gate's re-entry rule twice, and the two
statements are not the same rule:

- *The narrow one*, under "Explicitly out of scope for v0.3.0": "Any item
  captured after Gate 0 was frozen, unless it is `P0` or classed
  `safety`/`science`, which re-enter by the rule below."
- *The broad one*, the presence rule under "The gate is a snapshot, not a
  moving target": a finding re-enters "when the problem it describes was
  already present at the freeze, whatever id it is filed under or however long
  after the freeze it was noticed."

Under the narrow reading, class decides. Under the broad one, the problem's age
decides. Every entry added since the freeze has satisfied *both*, so the
disagreement has never been forced.

**Why it matters.** It is being forced now. PL-WB0X (split `simulation_view.py`)
is `refactor`-classed — outside the narrow rule — but describes a module that
has been oversized since long before 2026-08-25, so the broad rule admits it.
The two readings give opposite answers, and the answer decides whether v0.3.0
grows by an `M` item.

The precedent points at the broad reading: PL-N2N1 and PL-K79K both re-entered
on presence alone and both are `defect`-classed, not `safety`/`science`. But
both were also closed in the same batch that added them — the entry recording
them says so explicitly — so applying the broad rule cost nothing there. The
first case where it costs something is the first case that tests it.

Left as-is, the broad reading has no stopping condition: any pre-existing debt
noticed at any later date re-enters, which makes "the gate is a snapshot"
mean nothing, and a gate that can always grow cannot be finished. The narrow
reading has the opposite failure: a genuine pre-existing defect can be excluded
on a class label alone.

**Where.** `ROADMAP.md`, "Explicitly out of scope for v0.3.0" and "The gate is
a snapshot, not a moving target"; the notes beneath "Debt gate: the frozen
list" that invoke both.

**Decision needed.** Which reading governs a post-freeze capture whose problem
predates the freeze but whose class is outside `P0`/`safety`/`science`?

The recommendation is a third form that keeps what each is for: presence is
*necessary* for re-entry, and `P0`/`safety`/`science` is *sufficient*; anything
else that is merely present re-enters only when it is closed in the same batch
that adds it — which is what actually happened with PL-N2N1 and PL-K79K, and
which cannot grow the gate's remaining work by construction. That makes the
precedent and the stopping condition the same rule, and it decides PL-WB0X:
out, because it is `M` and would not close in the batch that added it.

**Found.** While placing PL-WB0X on the plan (2026-08-30), immediately after
adding PL-NV9W to the frozen list — which is the same rule applied where both
readings agreed.

**Done when.** `ROADMAP.md` states one re-entry rule, the two passages agree,
the entry notes beneath the frozen list cite the single form, and PL-WB0X's
placement follows from it rather than from a judgment call.
