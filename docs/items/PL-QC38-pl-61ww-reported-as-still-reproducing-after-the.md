---
id: PL-QC38
title: PL-61WW reported as still reproducing after the fix merged: establish whether it is a stale build or a second element
status: untriaged
added: 2026-09-08
---

**Problem.** PL-61WW reported as still reproducing after the fix merged: establish whether it is a stale build or a second element

The project owner reported on 2026-09-08, after `PL-61WW` (the agent name
losing contrast in the disabled selector) merged as `8d46af8` / `#460`, that
the symptom is still present. Not yet reproduced, and the cause is not known.

**What the source says on `eac6877`, which is what makes this worth a second
look rather than a reopen.** Only three controls are ever assigned `disabled`
in `app/simulation_view.py`: `_start_button`, `_pause_button` and
`_agent_dropdown`. Of the three only the dropdown carries an agent colour, and
`_refresh_view` sets `visible = not snapshot.is_running` on it while showing
`_running_agent_display` in its place. `tools/agent_identity_check.py` (added
by `PL-97VB`) now fails `make check` if that pairing is broken, and it passes.
So the specific path `PL-61WW` fixed cannot produce a greyed agent name on the
current default branch.

**Two hypotheses, and the test that separates them.** Ask whether a *dropdown*
- a control with a chevron, openable - is still on screen during a run.

1. **A build predating the fix.** `pyproject.toml` is still at `0.4.9` and no
   release has been cut since the fix landed, so anything installed as 0.4.9
   carries the old code. If a dropdown is still visible during a run, the new
   code is not the code running. This is the likelier of the two.
2. **A second element nobody has looked at.** If a run shows the chip - an
   agent-coloured box reading the agent name over "Locked while running", and
   no dropdown - and something is *still* hard to read, then the reported
   symptom was never the selector. `_subtitle_text` in `_agent_header_badge`
   is the next candidate: it carries the agent name in the same
   `foreground`/`fill` pair, is never disabled, and is drawn at the default
   text size on a saturated fill. `tools/contrast_check.py` measures that pair
   and it passes, so this would be a legibility complaint the ratio does not
   capture - size, weight, or the pair being right at the 4.5:1 floor rather
   than comfortably above it.

**Not reproducible in a Claude Code web container**, which is worth recording
so the next session does not spend the same turns: the app is Flet, its
Flutter renderer (`skwasm.wasm`, `skwasm.js`) is fetched from
`www.gstatic.com`, no copy ships inside the `flet` package, and the
environment's egress policy answers 403 to Google hosts at the gateway.
`no_cdn=True` does not change this. Serving the app on `127.0.0.1:8550` and
driving it with the container's Chromium gets as far as the Flet splash screen
and no further. Verification of anything visual has to happen on the owner's
own machine, or through a screenshot they supply.

**Done when.** Either the report is traced to a stale build and this closes
with that recorded, or the second element is identified and gets its own fix.
