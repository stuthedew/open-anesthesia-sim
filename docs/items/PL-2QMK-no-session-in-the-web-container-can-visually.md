---
id: PL-2QMK
title: No session in the web container can visually confirm a chart change, because Flet's web renderer fetches its Flutter assets from a host the egress proxy denies
status: untriaged
added: 2026-09-05
---

**Problem.** `docs/worker.md` and the `run` skill both assume a session can
start the application and look at it. In the Claude-Code-on-the-web container
it cannot. Measured 2026-09-05 while closing `PL-90Y6` (the MAC-awake band
drawing as a line), which is a `ux` item about how a mark *reads*:

- `ft.run(build_app, view=ft.AppView.WEB_BROWSER)` serves fine - the Flet
  HTTP server answers 200 on `127.0.0.1:8550` and the Flutter bootstrap
  loads;
- the page then requests
  `https://www.gstatic.com/flutter-canvaskit/<hash>/skwasm.js` and
  `skwasm.wasm`, which the container's egress proxy refuses:
  `curl` reports `CONNECT tunnel failed, response 403` and the proxy logs
  `www.gstatic.com:443 - connect_rejected`;
- so a headless Chromium screenshot captures the Flutter splash logo and
  never the application. The pre-installed Chromium and Playwright are not
  the problem and neither is the app.

**Why it matters.** Everything in `app/` that is about *appearance* rather
than about numbers is currently unverifiable in the environment most sessions
run in, and the failure is silent in the worst way: a screenshot is produced,
it just is not of the application. A session that does not open the image, or
opens it and reads a coloured splash as "something rendered", reports a visual
check it did not make. `PL-90Y6`, `PL-3355` (readouts wrapping at some window
widths), `PL-W8DQ`, `PL-GVXP` and the rest of `presentation-safety` all want
this.

The gap also falls exactly where this project's standard is strictest.
`CLAUDE.md` treats a misleading visual encoding as a defect rather than
polish, so "the tests assert the geometry" is not the whole of a `ux` item -
whether the mark *reads* as what it asserts is the question, and it is the
half that needs an eye.

**Where.** Not in this repository's own code. The candidate fixes, cheapest
first, and none yet tried:

- **Serve the Flutter assets locally.** Flet ships a web bundle; if
  `canvaskit`/`skwasm` are in it, pointing Flutter's
  `flutterConfiguration.canvasKitBaseUrl` at the local server removes the
  external fetch entirely. This is the one to try first - it is a
  configuration change, needs no allowlist, and would work in any offline
  checkout.
- **Ask for `www.gstatic.com` on the egress allowlist**, which is a project
  owner action outside the repository and fixes only this environment.
- **Record that visual confirmation happens on the owner's machine**, and say
  so in `docs/worker.md` and the `run` skill so a session stops attempting it
  and reports the limitation instead of a screenshot it cannot read. This is
  the honest fallback rather than a fix, and it should land whatever else
  does.

**Worked around for `PL-90Y6`** by rendering the mark's exact geometry - the
shipped `CHART_AXIS_TOP_MAC`, plot height, stroke width, fill opacity and each
agent's own `mac_awake` spread - to SVG and photographing that. It answered
the question and it is not the same evidence: it shows what the constants
describe, not what Flet draws from them.

**Done when.** A session in this container can produce a screenshot of the
running application, or `docs/worker.md` and the `run` skill state that it
cannot and say what to do instead.
