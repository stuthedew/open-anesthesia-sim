---
id: PL-NKFD
title: The charts redraw on a 0.2 s render tick while a dial is held, twice the 0.1 s that Nielsen Norman Group gives as the limit for a user to feel they are directly manipulating the display; measure the frame cost and whether a 0.1 s tick fits it
status: untriaged
added: 2026-11-22
filed-pr: 2257
---

**Problem.** The charts redraw on a 0.2 s render tick while a dial is held, twice the 0.1 s that Nielsen Norman Group gives as the limit for a user to feel they are directly manipulating the display; measure the frame cost and whether a 0.1 s tick fits it

**Found 2026-11-22** while researching the frame timing for `PL-2WVC` (a dial
input's frame drawn at once). `RENDER_INTERVAL_S` in `app/dashboard_frame.py`
is 0.2 s. Nielsen Norman Group, "Response Times: The 3 Important Limits"
(https://www.nngroup.com/articles/response-times-3-important-limits/, read in
full on 2026-11-22), gives "0.1 second: Limit for users feeling that they are
directly manipulating objects in the UI". While a dial is held, the readouts
follow the dial at once but the charts follow it only every 0.2 s.

**Done when.** The cost of one full frame is measured on the reference
machine and in CI, and the render tick is set to 0.1 s if a frame fits in
it, or the item records why it cannot.
