---
id: PL-YSZN
title: page.update() diffs every chart point control every frame whether or not it moved: 24.5 us per point x ~2080 points = 20-52 ms of the 200 ms frame, and 98% of it is Flet's Python-side object_patch walk rather than the 3-5 KiB patch it produces
status: dropped
added: 2026-09-08
closed: 2026-09-12
reason: A measurement, not work. Its table is the Flet baseline of record and stays in this file for whoever later asks why the interface left Flet. Everything it was filed to drive has since been taken up elsewhere: PL-QXSB consumed it and decided to leave Flet, v0.5.1 scopes the port, and each consequence it names is a live item of its own - PL-SQJ1 (delivered playback rate), PL-CNCF (drawn_window's 6.2 ms, which survives the port), PL-KP7H (closed, the per-point tooltip) and PL-C92D (the one correction its table still owes). Nothing is left here that is not one of those.
---

**Problem.** The project owner reported the interface feeling laggy, worse at
higher playback rates, and asked whether the cause was the simulation or the
interface. Measured headless on 2026-09-08 — a real `SimulationController` and
a real `SimulationView` on a real `flet.messaging.session.Session` whose
connection serializes each outbound message exactly as the WebSocket transport
does, which is the harness `tests/integration/test_chart_patching.py`
established. **It is not the simulation.**

Per rendered frame at each rate, `RENDER_INTERVAL_S` = 200 ms of budget:

| Rate | Steps/frame | `controller.advance` | `_refresh_view` | `page.update` | Patch |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1x | 2 | 0.18 ms | 1.6 ms | 26.6 ms | 2.0 KiB |
| 5x | 10 | 0.58 ms | 4.2 ms | 44.1 ms | 3.1 KiB |
| 20x | 40 | 1.95 ms | 4.9 ms | 51.2 ms | 3.1 KiB |
| 60x | 120 | 5.16 ms | 3.9 ms | 41.4 ms | 3.8 KiB |
| 300x | 600 | 26.2 ms | 4.6 ms | 45.5 ms | 3.8 KiB |

The model alone is 28.8 us/step and the controller 40.5 us/step, the 11.7 us
difference being the history record and the score's reach. At 40.5 us/step the
simulation could sustain about 2 470x real time; at 300x it occupies 12% of a
tick. It is the second cost here, not the first.

`page.update()` splits 98/2 between Flet's Python-side control-tree diff and
the msgpack encode — 45.0 ms against 1.0 ms at 300x. The wire is not the
constraint either: 3-5 KiB a frame.

**The cost is the walk, not the changes it finds.** Saturating the chart and
then calling `page.update()` with *nothing changed since the last one*:

| Visible traces | Point controls | Idle `update` | Frame `update` |
| ---: | ---: | ---: | ---: |
| 0 | 54 | 10.3 ms | 12.0 ms |
| 1 | 336 | 16.3 ms | 15.3 ms |
| 2 | 618 | 22.2 ms | 22.3 ms |
| 4 | 1 182 | 36.5 ms | 32.7 ms |
| 6 | 1 746 | 51.8 ms | 50.5 ms |

Idle equals frame at every width, and both are linear in the point count at
about 24.5 us per point. `cProfile` puts 64% of the frame in
`flet/controls/object_patch.py`'s `_compare_dataclasses`, called ~7 800 times
per frame over ~2 080 `LineChartDataPoint` controls across the two charts.

**Why it matters.** It bounds everything the interface can do, and it does so
whether or not the run is moving. Two consequences measured the same day:
`PL-SQJ1` (the delivered playback rate is 73-91% of the rate displayed) and
`PL-R2YM` (one slider `on_change` triggers a whole-page walk).

**Relation to `PL-YDKJ`** (decide whether the chart should keep patching one
control per plotted point). `PL-Q197` and `PL-YDKJ` both located this cost on
the *client*: "the Flet (Flutter) client process was pegged at 100% CPU while
the Python process was not". That was true of the ~17 900 ops/s that saturated
the client, and `PL-Q197` fixed it. What these measurements add is that a
second, independent cost sits on the *Python* side and `PL-Q197` did not touch
it, because it is not a function of how many operations come out — it is a
function of how many point controls are in the tree. `PL-YDKJ`'s "after
`PL-Q197` the sustained rate is 98 ops/s growing... so the app works"
understates the position by that term.

**Measured on** a 4-vCPU Intel Xeon @ 2.10 GHz cloud container, which is
slower and noisier than the owner's machine; run-to-run spread on the same
variant reached 2x. The ratios travel, the absolute figures do not.

**First step.** Decide `PL-YDKJ` with this evidence in hand, and price the two
levers it does not depend on: `PL-KP7H` (the per-point tooltip is half the
per-point cost) and the drawn column budget.
