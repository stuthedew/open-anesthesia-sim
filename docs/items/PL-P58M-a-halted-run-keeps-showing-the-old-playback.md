---
id: PL-P58M
title: A halted run keeps showing the old playback rate on the clock's second line after the playback-rate dropdown changes, because present_halt does not write the readout row and PL-X7D5's guard exempts _readout_row (reproduced offscreen by PL-K88Z's inventory: 5x in the dropdown, 1x real time in the readout)
status: untriaged
feature: one-source-of-truth
added: 2026-10-19
---

**Problem.** A halted run keeps showing the old playback rate on the clock's second line after the playback-rate dropdown changes, because present_halt does not write the readout row and PL-X7D5's guard exempts _readout_row (reproduced offscreen by PL-K88Z's inventory: 5x in the dropdown, 1x real time in the readout)
