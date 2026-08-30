---
id: PL-9PMV
title: Two readings of the gate's re-entry rule disagree, and a real finding now sits between them
priority: P2
effort: S
status: done
closed: 2026-08-30
commit: 47b1077
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

**Decided (project owner, 2026-08-30), and the answer was smaller than the
question.** Reading the whole of "The gate is a snapshot, not a moving target"
rather than its first paragraph shows the project already has one coherent
rule, stated correctly in two places and wrongly in a third:

- *"The gate is a snapshot"* — presence is a **presumption**, favoured but not
  absolute; a session may defer a presence-qualifying finding where a specific
  reason argues otherwise, provided it says so and says why. `P0` and
  `safety`/`science` re-enter regardless of presence.
- *"The cadence", step 4* — presence **or** `P0`/`safety`/`science` re-enters.
  Agrees.
- *"Explicitly out of scope for v0.3.0"* — named only the
  `P0`/`safety`/`science` half and omitted presence entirely. **This was the
  defect**: one bullet narrower than the rule it summarised.

So no third form was needed, and the "closes in the same batch that adds it"
clause proposed above was withdrawn before implementation. It would have
replaced a judgment the document already provides for — and provides for
better, since a mechanical batch test would exclude an urgent pre-existing
defect merely for being `M`, while the stated-reason discretion handles the
same case without a size proxy.

PL-WB0X's placement follows from the repaired rule rather than from a class
label: the presumption admits it, and it is deferred to Gate 1 under the
discretion the rule grants, with the reason recorded both in `ROADMAP.md`'s
gate notes and in PL-WB0X's own brief.

**Found.** While placing PL-WB0X on the plan (2026-08-30), immediately after
adding PL-NV9W to the frozen list — which is the same rule applied where both
readings agreed.

**Done when.** `ROADMAP.md` states one re-entry rule, the two passages agree,
the entry notes beneath the frozen list cite the single form, and PL-WB0X's
placement follows from it rather than from a judgment call.
