---
id: PL-5JTH
title: PL-X7D5's default-include guard compares a RunView's widgets only: the dashboard's own panels a halt must restate - the fork panel (PL-MMNX) and the bookmark panel (PL-YHR3) - are restated by hand in _halt_every_run, so a dashboard panel added later is restated on a halt only if someone remembers to add it there (found closing PL-X7D5)
status: untriaged
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
added: 2026-10-17
---

**Problem.** PL-X7D5's default-include guard compares a RunView's widgets only: the dashboard's own panels a halt must restate - the fork panel (PL-MMNX) and the bookmark panel (PL-YHR3) - are restated by hand in _halt_every_run, so a dashboard panel added later is restated on a halt only if someone remembers to add it there (found closing PL-X7D5)
