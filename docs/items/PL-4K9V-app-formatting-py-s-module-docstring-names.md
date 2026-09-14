---
id: PL-4K9V
title: app/formatting.py's module docstring names SimulationHistorySample, which was deleted with the sample store
status: untriaged
added: 2026-09-14
---

**Problem.** app/formatting.py's module docstring names SimulationHistorySample, which was deleted with the sample store

`src/anesthesia_sim/app/formatting.py:24` reads "Everything upstream carries
full binary64 - the compartment states, every integration step, every
`SimulationHistorySample` - and the rounding happens exactly once, here." That
class was deleted with the sample store (`PL-2FM6`) and the name appears
nowhere else in `src/`. The sentence's point survives; only its last example
has to change to whatever the drawn window is now called.

Found while working `PL-TFX5`, and left rather than fixed because the file is
outside that item's declared `touches` — the second test of `CLAUDE.md`'s
fix-now rule. `PL-9KP5` is the same rot in `docs/ARCHITECTURE.md`, and the two
are worth doing together.
