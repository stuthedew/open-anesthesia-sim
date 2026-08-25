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
