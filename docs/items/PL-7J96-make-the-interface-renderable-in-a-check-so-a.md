---
id: PL-7J96
title: Make the interface renderable in a check, so a presentation change can be looked at
status: untriaged
added: 2026-09-02
---

**Problem.** Nothing in this repository draws the interface. `make check` runs
1038 tests over the control *tree* — what strings exist, what colour each is,
what pairs with what — and every one of them passed while the interface was
displaying a defect. Two, in one session:

- PL-NV9W's own fix. The required label `"Alveolar / end-tidal-equivalent"`
  did not fit its column and wrapped to `Alveolar / end-tidal-` over
  `equivalent`, restoring the unhedged phrase the item existed to remove for
  anyone reading the row rather than studying it. The test asserting the exact
  string passed, because the string was correct; it was the rendering that was
  not.
- PL-8M05. Four of the seven readout labels wrapped at narrow widths and three
  did not, so the readings sat on two baselines and *which* ones dropped
  changed with the window width. This had been shipping for some time.

Both were found by serving the app over HTTP and screenshotting it, and
neither was reachable from the control tree: text wrapping is a function of
the rendered glyph widths, the panel width and the font, and none of the three
is knowable from the dataclasses the tests read.

**Why it matters.** `CLAUDE.md`'s safety-critical standard is largely a
standard about what a reader *sees*: "the correct number with the wrong units,
label, patient context, stale state, model name/version, or provenance is
still a safety failure", and "for plots and dashboards, optimize first for
accurate interpretation". The suite currently verifies everything up to the
last step of that chain and stops one short of it. That is the gap both
defects fell through, and the second had survived every prior review.

**Where.** A new `tools/` entry plus a `make` target; `docs/ARCHITECTURE.md`'s
tools map and `README.md`'s CI description would name it.
`src/anesthesia_sim/app/main.py` already builds the page, so the app needs no
change to be served.

**How it was done by hand, which is the starting point.** Flet serves the real
app over HTTP with
`ft.run(build_app, view=ft.AppView.WEB_BROWSER, host="127.0.0.1", port=8550,
no_cdn=True)` under `FLET_FORCE_WEB_SERVER=1`. Chromium is already installed
at `/opt/pw-browsers/chromium`. One wrinkle is worth recording because it
costs an hour to rediscover: the Flutter engine fetches `skwasm.js` and
`skwasm.wasm` from `www.gstatic.com`, which the agent network policy blocks —
but `flet_web/web/canvaskit/` ships the same files, so a Playwright `page.route`
handler fulfilling `https://www.gstatic.com/flutter-canvaskit/**` from that
directory renders the page without disabling TLS verification or reaching the
network. Roboto is blocked the same way and falls back to a serif that is
*wider*, which makes a wrapping check conservative rather than optimistic.

**The judgment this item is really about.** Screenshots are easy to produce
and hard to gate on: a pixel-diff check fails on every intentional change and
gets disabled within a month, which is worse than no check. Two narrower
targets are worth considering instead, and they are not exclusive:

1. *A `make screenshot` target that captures the interface at the breakpoint
   widths and writes the files somewhere a person looks at them.* No pass/fail,
   no gate — it makes the last step cheap enough that a session actually takes
   it, which is the whole failure here. Closest to what
   `CLAUDE.md`'s tooling section calls the decidable part being small: the
   scripting is decidable, the looking is not.
2. *An assertion on measured geometry rather than on pixels.* The rendered DOM
   can report a label's line count, and "no readout label wraps at any
   breakpoint width" is a genuine pass/fail that does not fire on an
   intentional redesign. This is the one that would have caught both defects
   automatically, and it is the harder of the two to build.

**Done when.** A session can render the running interface with one command,
and the project has decided — with the reason recorded — whether anything
about the rendering is gated in `make check` or whether the target exists only
to be looked at.
