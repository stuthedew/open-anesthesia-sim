---
id: PL-Q2DK
title: The View contract's module docstring says pinning a View to one run is left to PL-7Z84, which is done, and cites a ROADMAP heading that has since gained the word Completed
status: untriaged
touches: src/anesthesia_sim/app/view_contract.py
added: 2026-11-11
---

**Problem.** The View contract's module docstring says pinning a View to one run is left to PL-7Z84, which is done, and cites a ROADMAP heading that has since gained the word Completed

The copy editor found both while reading `PL-9YPR`'s changed prose
(2026-11-11). Neither sentence was written by that item, so neither was
changed there.

1. `src/anesthesia_sim/app/view_contract.py`, the last paragraph of the module
   docstring: "Where a Workspace pins a View to one run, that binding is left
   to `PL-7Z84`. Until then, every View draws every displayed run." `PL-7Z84`
   is done, and `app/simulation_view.py`'s module docstring says "A Workspace
   pinned to a run draws that run alone". The sentence should say how a pinned
   Workspace reaches a View today.
2. The same docstring cites `ROADMAP.md` § "v0.6.0 - the layout is the
   reader's" twice. The heading is now "Completed: v0.6.0 - the layout is the
   reader's".
