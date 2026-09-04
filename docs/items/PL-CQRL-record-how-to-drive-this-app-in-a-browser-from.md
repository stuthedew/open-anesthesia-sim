---
id: PL-CQRL
title: Record how to drive this app in a browser from a container session
priority: P2
effort: S
status: ready
classes: docs, infra
feature: dev-tooling
touches: .claude/skills, docs/WORKING_NOTES.md
added: 2026-09-02
verify: python3 tools/doc_check.py check && grep -rqF 'FLET_WEB_NO_CDN' .claude/skills/
---

**Problem.** PL-010 was gated on confirming that a live Flet client repaints
a mutated chart point, and the brief assumed that gate might not be passable.
It was - the container has everything needed - but working out how took most
of the session's early cost, and none of it is written down. The next session
that needs to see the interface will rediscover it.

**Why it matters.** `docs/WORKING_NOTES.md` recorded for three releases that
a live Flet client "was not available", which is what left PL-010 sitting in
the gate. That belief was wrong and cost the project an unclosed item. More
generally, `CLAUDE.md` holds displayed values to a presentation-correctness
standard that a headless test can only partly reach: whether a badge is
legible, whether a trace is visible against its grid, whether a label wraps,
are questions only a rendered frame answers.

**What was actually needed** (measured 2026-09-02, Flet 0.86.5):

- `FLET_FORCE_WEB_SERVER=true` makes `ft.run` serve over HTTP instead of
  looking for a desktop client. `FLET_SERVER_PORT` and `FLET_SERVER_IP` set
  the address.
- `FLET_WEB_NO_CDN=true` is the one that is not obvious and fails silently
  without it. Flutter's bootstrap loads its renderer from
  `https://www.gstatic.com/flutter-canvaskit/...` unless `flet.noCdn` is set,
  and the agent proxy refuses that host: the page loads, no canvas is ever
  created, and there is no error on the page. `flet_web` already ships the
  renderer locally; this is the flag that makes it use it.
- Chromium is preinstalled at `/opt/pw-browsers/chromium-1194/chrome-linux/`
  with `node` available, so `npm install playwright` (with
  `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`) drives it, launched with an explicit
  `executablePath` rather than letting Playwright resolve a revision. What
  worked was `--no-sandbox --disable-dev-shm-usage --no-proxy-server
  --use-gl=swiftshader --enable-unsafe-swiftshader`; which of those are
  strictly required was not established one at a time, so treat the set as a
  starting point rather than a minimum.
- Flutter draws to a canvas, so there is no DOM to click. Screenshot, read
  the coordinates off the image, click by position. That worked for Start,
  Pause and the agent dropdown.

**Where.** Somewhere a session finds it when it needs it rather than
resident: a skill is the obvious home, since the trigger is its own trigger,
and there is already a built-in `run` skill this would specialise.

**Done when.** A session that needs to see the app running finds the
procedure instead of deriving it, and `docs/WORKING_NOTES.md` no longer
implies a live client is out of reach.

**Confirming evidence, 2026-09-04 (PL-F52R).** A session that needed to look at
a chart change hit exactly the failure this item predicts. Without
`FLET_WEB_NO_CDN`, the page served, Chromium loaded it, and the screenshot came
back as the Flutter splash with no error anywhere - so the first conclusion was
that the app was broken rather than that a flag was missing. The recipe was
found by grepping `docs/items/` for "chromium", which is not a place a session
looks when it wants to run the app.

That is the silent-wrong-answer shape: the check appears to run and returns
something plausible. It cost roughly a quarter of the session's tool calls
before the grep. The `run` skill specialisation this item proposes is the fix,
and this is a second measurement in favour of doing it.

**A wrong conclusion is already in the queue, and this item is what prevents
another.** `PL-0PSX` (captured 2026-09-04, in flight on
`origin/claude/triage-n7hzpe`) states that "the app cannot be rendered, driven
or screenshotted from a Claude Code web session" and diagnoses the proxy's 403
on `www.gstatic.com` as the reason. The first half of that is false and the
second half is true: the proxy does refuse gstatic, and `flet_web` ships the
CanvasKit renderer locally so nothing needs to be fetched from it.
`FLET_WEB_NO_CDN=true` is the whole difference.

Rendered here on 2026-09-04 with
`FLET_FORCE_WEB_SERVER=true FLET_WEB_NO_CDN=true FLET_SERVER_PORT=8551`, driven
over the Chrome DevTools Protocol (`--remote-debugging-port`, `Page.navigate`,
`Input.dispatchMouseEvent` to press Start by coordinate,
`Page.captureScreenshot` with a `clip`) using the `websockets` package the
project venv already has - so not even Playwright is required. The run reached
31.5 s of simulated time with all six traces drawn.

This is the second time the belief has taken hold: `docs/WORKING_NOTES.md`
carried it for three releases and it left PL-010 sitting in a gate. That is the
argument for the recipe living in a skill rather than in an item nobody greps.
