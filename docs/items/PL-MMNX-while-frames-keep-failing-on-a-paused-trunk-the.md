---
id: PL-MMNX
title: While frames keep failing on a paused trunk, the Branch here button stays live over the failed run: _halt_every_run restates the halt on each RunView but not on the fork panel, and a press is refused with the refusal swallowed by the next failing frame
status: untriaged
feature: every-control-restates-the-halt
added: 2026-10-12
---

**Problem.** While frames keep failing on a paused trunk, the Branch here button stays live over the failed run: _halt_every_run restates the halt on each RunView but not on the fork panel, and a press is refused with the refusal swallowed by the next failing frame

**Found by the adversarial review of `PL-Y2SL`** (2026-10-12), reproduced
offscreen: with every frame failing, the trunk read "Stopped - simulation
error" with Start and Pause disabled, while the fork panel still showed a live
"Branch here: 1m"; a press added no run and the refusal never reached the
notice, because `present(False)` after it raised again. Before `PL-Y2SL` this
reached only a trunk standing on a halt; the button is now offered at every
pause, so any paused trunk whose frames keep failing shows it. The fork panel
is one more control `_halt_every_run` does not restate, the group this item is
filed under.
