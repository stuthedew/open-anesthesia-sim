---
id: PL-CQRL
title: Record how to see and drive the Qt interface from a container session
priority: P2
effort: S
status: done
classes: docs, infra
feature: dev-tooling
milestone: v0.5.21
touches: .claude/skills/run-the-app/SKILL.md, docs/worker.md, docs/WORKING_NOTES.md, docs/ARCHITECTURE.md
added: 2026-09-02
closed: 2026-10-01
pr: 1257
verify: grep -rqF 'view.present(False)' .claude/skills/ && grep -qF '.claude/skills/run-the-app/SKILL.md' docs/worker.md && ! grep -qF 'step it before the grab' docs/worker.md && grep -qF 'FLET_WEB_NO_CDN' docs/WORKING_NOTES.md && ! grep -qF 'renderer cannot load' docs/WORKING_NOTES.md
---

**Re-confirmed 2026-10-01: changed shape.** Filed against the Flet build. The
interface moved to Qt at v0.4.26 and Flet left the tree with `PL-3SQT`, so the
browser recipe this brief carried (`FLET_FORCE_WEB_SERVER`, `FLET_WEB_NO_CDN`,
Chromium over the DevTools protocol) drives nothing that exists. The problem it
named is still live, in a new place.

**Problem.** The procedure for seeing the Qt interface lives in one place,
`docs/worker.md` § "Seeing the interface", and its second half gives a silently
wrong answer. "To see a run rather than the starting state, call
`view.runs[0].controller.start()` and step it before the grab" leaves out the
`view.present(False)` that draws the advanced state. Followed literally on
2026-10-01, the controller reached 120.0 s and the PNG showed `0s`, `Paused`,
every readout at 0.00% and a flat chart, with no error - the shape `PL-F52R`
hit under Flet, a check that runs and returns something plausible. The same
command also composes the dashboard differently from `main.py`: no
`BranchedCase`, so the Branch section that ships is hidden
(`SimulationView` hides `_fork_section` when `case` is None), and no
`declare_application_colours`. And it is findable only by a worker, who reads
that file in full. A Claude session asked to run or screenshot the app gets the
built-in `run` skill, which looks for a project skill that covers launching the
app and finds none.

**Why it matters.** `CLAUDE.md` holds what the interface displays to a
presentation-correctness standard that a headless test only partly reaches:
whether a label wraps, a trace stands out from its grid or a readout is clipped
is answered by a rendered frame. A stale frame answers it wrongly in both
directions - a change that works reads as broken, and a broken one is passed
because the frame looked fine - and a dashboard built without `BranchedCase`
reviews a layout that does not ship. While product focus holds, interface work
is the main lane, so every session that needs a look pays the derivation again.

**Measured here, 2026-10-01.** `QT_QPA_PLATFORM=offscreen` renders the real
widgets with no setup beyond `uv run`: the documented one-liner prints `True`
on a fresh container in about 10 s. `xvfb-run` is installed, but
`uv run anesthesia-sim` under it aborts at startup, because Qt's `xcb` plugin
needs `libxcb-cursor0` and other xcb libraries this container lacks. So the
offscreen grab is the route.

**Approach.** A project skill, `.claude/skills/run-the-app/SKILL.md`, as this
brief proposed from the start: the trigger is its own, a session wanting to see
the app, and the built-in `run` skill defers to a project skill that covers
launching the app. It carries one verified command that builds the dashboard as
`main.py` does, presses Start through its button, advances the run, presents
and paints a frame and grabs it to `out/`; the stale-frame trap, stated where it
bites; how to drive through widgets and through the controller; and what an
offscreen frame cannot settle. `docs/worker.md` § "Seeing the interface" points
at it rather than carrying a second copy, and loses its false Flet sentence.
`docs/WORKING_NOTES.md`'s two records that Flet's renderer could not load here
are corrected where they stand.

**Done when.** A session that needs to see the app running finds the procedure
instead of deriving it, the procedure presents the state it claims to, and
neither `docs/worker.md` nor `docs/WORKING_NOTES.md` says that either interface
could not be seen from this container.

**What the Flet-era brief recorded** (2026-09-02 to 2026-09-04; the full text
is this file as it stood at `5deda3f8`). Rendering the Flet build took most of
`PL-010`'s early session and a quarter of `PL-F52R`'s tool calls.
`FLET_WEB_NO_CDN=true` was the flag nobody would guess: without it the page
served the Flutter splash and no error, because the proxy refuses
`www.gstatic.com` and `flet_web` ships the renderer locally only for a bootstrap
told to use it. `PL-0PSX` concluded the app could not be rendered from a web
session and was dropped on that evidence. The belief took hold twice, which is
the argument for a skill over an item nobody greps, and it holds unchanged for
Qt.
