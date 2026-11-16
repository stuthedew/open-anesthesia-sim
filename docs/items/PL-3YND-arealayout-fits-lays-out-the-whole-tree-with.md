---
id: PL-3YND
title: AreaLayout._fits lays out the whole tree with apportion twice per Area on every bisection step of a stopped border drag, about 9 ms a pointer move at 6 Areas and 56 ms at 20 (blind review of PL-501T); the start layout depends only on the drag's start and could be laid out once per drag
status: untriaged
touches: src/anesthesia_sim/app/area_layout.py
added: 2026-11-16
---

**Problem.** AreaLayout._fits lays out the whole tree with apportion twice per Area on every bisection step of a stopped border drag, about 9 ms a pointer move at 6 Areas and 56 ms at 20 (blind review of PL-501T); the start layout depends only on the drag's start and could be laid out once per drag
