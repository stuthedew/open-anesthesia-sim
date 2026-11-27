---
id: PL-7LZ7
title: With a concentration chart at 1.5 or 4.5 xMAC, the compartment schematic still fills against the standard 3 xMAC scale, so the two Views can disagree about whether one tension is off the scale; decide whether the schematic should follow a chart's top
priority: P2
effort: S
status: needs-decision
classes: defect
feature: chart-readout
touches: src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/views.py, docs/INTERFACE.md
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
filed-pr: 2270
payoff: the schematic and a chart cannot seem to disagree about whether a tension is off the scale
---

**Problem.** With a concentration chart at 1.5 or 4.5 xMAC, the compartment schematic still fills against the standard 3 xMAC scale, so the two Views can disagree about whether one tension is off the scale; decide whether the schematic should follow a chart's top

**Found on 2026-11-22** by pass 2 of the blind review of `PL-K1VH` (the reader-chosen chart top). Each concentration chart View now holds its own top, and the compartment schematic keeps the standard 3 ×MAC scale, because it has no chart to follow and a Workspace may show two charts at different tops. So with a chart at 4.5 ×MAC and an 8% sevoflurane circuit, the schematic marks Circuit "Above the top of the scale" while the chart shows the trace inside the plot with no notice. At 1.5 ×MAC the opposite happens for an alveolar tension of 1.67 MAC. Each View's caption describes its own scale correctly, so a user who reads both can work this out. The question is whether the schematic should carry an axis-top control of its own, follow one chart, or keep the standard scale and say so beside the chart's control.

**Why it matters.** Two Views of one run can disagree about whether a tension is off the scale. A user who trusts the schematic's "Above the top of the scale" may doubt the chart, or the reverse, though each is right about its own scale.

**Decision needed.** Should the compartment schematic keep the standard 3 ×MAC scale, follow one chart's top, or carry an axis-top control of its own?

**Recommendation (provisional).** Keep the standard scale on the schematic, and state it beside each chart's top control, because the schematic cannot know which of two charts to follow. The design round for `chart-readout` owes research on how linked views share a scale before this reaches the owner.

**Done when.** The decision is recorded here, and a test shows the schematic and a chart at a non-standard top cannot be read as disagreeing without a visible statement of each scale.

**Generator check.** A one-off: a consequence of `PL-K1VH` giving each chart its own top.

**Reproduced 2026-11-23.** `src/anesthesia_sim/app/compartment_schematic.py` still fills against the standard scale with no reference to a chart's top.
