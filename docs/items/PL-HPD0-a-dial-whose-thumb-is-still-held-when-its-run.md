---
id: PL-HPD0
title: A dial whose thumb is still held when its run starts over (an agent change or a Reset) applies its release value to the new run, though the preview of that value ended at the start-over (found building PL-1WFW)
status: untriaged
added: 2026-11-22
---

**Problem.** A dial whose thumb is still held when its run starts over (an agent change or a Reset) applies its release value to the new run, though the preview of that value ended at the start-over (found building PL-1WFW)

**Found 2026-11-22** by the worker building `PL-1WFW`. That item ends a held preview when its run starts over or is renamed, so no label names an agent or run that is gone. The thumb is still down, though, and its release applies the value to the new run as an ordinary change. Whether a release after a start-over should apply is open: a learner who held the dial through a key press that reset the run may not mean to set the new run. The behaviour is unchanged from before `PL-1WFW`.
