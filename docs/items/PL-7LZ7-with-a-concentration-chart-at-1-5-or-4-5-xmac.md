---
id: PL-7LZ7
title: With a concentration chart at 1.5 or 4.5 xMAC, the compartment schematic still fills against the standard 3 xMAC scale, so the two Views can disagree about whether one tension is off the scale; decide whether the schematic should follow a chart's top
status: untriaged
feature: chart-readout
touches: src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/views.py, docs/INTERFACE.md
added: 2026-11-23
filed-pr: 2270
---

**Problem.** With a concentration chart at 1.5 or 4.5 xMAC, the compartment schematic still fills against the standard 3 xMAC scale, so the two Views can disagree about whether one tension is off the scale; decide whether the schematic should follow a chart's top

**Found on 2026-11-22** by pass 2 of the blind review of `PL-K1VH` (the reader-chosen chart top). Each concentration chart View now holds its own top, and the compartment schematic keeps the standard 3 ×MAC scale, because it has no chart to follow and a Workspace may show two charts at different tops. So with a chart at 4.5 ×MAC and an 8% sevoflurane circuit, the schematic marks Circuit "Above the top of the scale" while the chart shows the trace inside the plot with no notice. At 1.5 ×MAC the opposite happens for an alveolar tension of 1.67 MAC. Each View's caption describes its own scale correctly, so a learner who reads both can work this out. The question is whether the schematic should carry an axis-top control of its own, follow one chart, or keep the standard scale and say so beside the chart's control.
