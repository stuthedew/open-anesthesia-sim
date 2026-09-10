---
id: PL-005
title: Replace the full-screen startup window with a sized, centered one
priority: P2
effort: S
status: ready
classes: ux
feature: vaporizer-controls
touches: src/anesthesia_sim/app/main.py
added: 2026-08-23
---

> **This fix rides the Qt port (`v0.5.1`), not Flet.** `ROADMAP.md` § "v0.5.1 -
> the interface moves to Qt" names this item under "Fixes this port carries":
> the defect lives in code that milestone rewrites from scratch, so fixing it
> on Flet means writing the same lines twice. Project owner, 2026-09-10.

**Problem.** `app/main.py` sets `page.window.full_screen = True` on
startup.
**Why it matters.** Full-screen-on-launch is a hostile default and hides
the window controls on some platforms. Prior project decision is to replace
it.
**Where.** `app/main.py`.
**First step.** Choose the sizing approach. Constraints from the prior
decision: no magic pixel dimensions, no monitor-specific assumptions, and
no native display-probing dependency.
**Done when.** The app opens in an adequately sized, centered window that
remains fully visible on different displays.
