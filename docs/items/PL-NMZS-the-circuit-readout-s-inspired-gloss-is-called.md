---
id: PL-NMZS
title: The Circuit readout's 'inspired' gloss is called a safety requirement in app/dashboard_frame.py, but no specification document states it or says why
status: untriaged
feature: presentation-safety
touches: docs/INTERFACE.md, src/anesthesia_sim/app/dashboard_frame.py
added: 2026-11-22
---

**Problem.** The Circuit readout's 'inspired' gloss is called a safety requirement in app/dashboard_frame.py, but no specification document states it or says why

**Where.** The module docstring of `src/anesthesia_sim/app/dashboard_frame.py`
names three strings as safety requirements: the "Alveolar" readout with the
gloss "end-tidal-equivalent", the "Circuit" readout with the gloss
"inspired", and the "Fresh gas flow" control with the gloss "common gas
outlet". `docs/INTERFACE.md` § "Minimum displayed outputs" states the first
and, since `PL-48MX`, the third, each with its reason. No specification
document states the "inspired" gloss or says why the circuit readout needs
it. An exact-string test keeps all three on screen.

**Fix.** Find the reason in the item that added the gloss and the git
history (`git log -S '"inspired"' -- src/anesthesia_sim/app/`), then state the
requirement and its reason beside the other two in `docs/INTERFACE.md`, and
update the docstring.

**Found by** the documentation sweep of `PL-48MX`, 2026-11-22.
