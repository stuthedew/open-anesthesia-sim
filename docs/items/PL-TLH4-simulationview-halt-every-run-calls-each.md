---
id: PL-TLH4
title: SimulationView._halt_every_run calls each RunView.present_halt in an unguarded loop, and present_halt documents a ValueError, so a raise there skips _restate_fork_panel and _restate_bookmark_panel and leaves both panels on the last frame's state (found reviewing PL-YHR3)
status: untriaged
feature: every-control-restates-the-halt
added: 2026-10-19
---

**Problem.** SimulationView._halt_every_run calls each RunView.present_halt in an unguarded loop, and present_halt documents a ValueError, so a raise there skips _restate_fork_panel and _restate_bookmark_panel and leaves both panels on the last frame's state (found reviewing PL-YHR3)
