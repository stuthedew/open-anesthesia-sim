---
id: PL-PKLR
title: An Area keeps no stack of the Views previously open in it, though docs/interface-provenance.md adopts that from Blender, so switching an Area to another View and back loses the first View's state
status: dropped
feature: interface-provenance-adoptions
added: 2026-11-10
closed: 2026-11-11
reason: Contradicted by measurement (PL-QKDV, 2026-11-11): AreaLayout.view_states keeps one saved state per View kind per Area. A concentration chart set to a 15 minute time base, switched to Wash-in and back, came back at 15 minutes.
---

**Problem.** An Area keeps no stack of the Views previously open in it, though docs/interface-provenance.md adopts that from Blender, so switching an Area to another View and back loses the first View's state
