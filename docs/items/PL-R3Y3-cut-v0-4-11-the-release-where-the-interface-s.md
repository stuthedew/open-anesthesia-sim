---
id: PL-R3Y3
title: Cut v0.4.11 - the release where the interface's cost was measured rather than guessed
priority: P2
effort: S
status: done
classes: planning
feature: release-process
milestone: v0.4.12
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases/v0.4.11.md
added: 2026-09-08
closed: 2026-09-08
pr: 486
verify: python3 tools/doc_check.py check && grep -q 'Current baseline: v0.4.11' ROADMAP.md
---

**Problem.** Cut v0.4.11 - the release where the interface's cost was measured rather than guessed

**Cut on the project owner's instruction, 2026-09-08**, in answer to "Should we
cut version first?" — asked before approving the Qt spike, and the answer is
yes for a reason the spike supplies: a spike churns `app/`, and a release cut
after it would describe a half-migrated tree rather than the work that is
actually finished.

Twenty-one items since v0.4.10, completing the `delegation` feature. `0.4.11`
rather than a minor because no capability boundary is crossed: `core/` is
byte-identical to v0.4.10 and `data/` changes only in what two provenance
entries say about their own numbers.

Three sessions independently recommended `0.4.11` and the mechanical guess
agreed; two of those sessions had gone to `need_input` on the version name and
were archived by the time this one asked, so nothing was in flight against it.

`ROADMAP.md`'s version-table row, the current-baseline mark and the baseline
section were written by hand, which is the half `bin/docket release` stops
before and says so.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.11 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> No equation, parameter, numerical method or solver step moves: `src/anesthesia_sim/core/` is byte-identical to v0.4.10, and `src/anesthesia_sim/data/` changes only in what two provenance entries say about their own numbers - one of them recording that the stored 5.0 L/min cardiac output is *kept* against Lowe and Ernst's allometric 4.84, because this file stores compartment volumes as fixed litres and scaling only the flow would make every time constant proportional to M^(-3/4), an artifact of scaling one half of a coupled pair (`PL-YKSM`). **The project owner reported the interface as laggy at speed, and the first finding was that it is not the simulation.** The model is 42 us a step, enough to sustain about 2 400x real time, and at 300x it occupies 12% of a tick; `page.update()` cost 20-52 ms of a 200 ms frame, 98% of it Flet's Python-side control-tree walk against 2% for the msgpack encode, on a patch of 3-5 KiB. **The cost is the walk rather than the changes it finds**: an update on a chart where nothing had changed since the last one costs what a full frame costs, both linear in the number of point controls at about 24.5 us each, with 64% of a frame in `object_patch._compare_dataclasses` (`PL-YSZN`). **Half of it was a tooltip nothing ever wrote text into.** Every `LineChartDataPoint` carries a default `LineChartDataPointTooltip` holding a full seventeen-field `TextStyle`, and Flet's diff descends into both on every point on every frame. The hover is now offered while the run is paused and withdrawn while it plays - which costs nothing, because `_run_render_timer` takes no frame while the run is stopped, and a value read under a cursor on a trace advancing a simulated minute per frame was never readable anyway (`PL-KP7H`). **And a dragged slider was drawing a whole frame per pointer move**, 59.1 ms each, so a drag emitting thirty a second asked for 1.8 s of event-loop time per second and the readouts arrived *later* than a tick rather than sooner; the frame is coalesced onto the render tick, leaving 3.4 ms, with a refusal and the frame that clears one still drawn immediately because those are the only states where a dial and the simulation disagree (`PL-R2YM`). Together: delivered playback rises from 73-91% of the rate the dropdown claims to 84-94%, and input-delay p90 roughly halves. **`PL-YDKJ` is decided rather than deferred**, both escape routes having been measured: a server-rendered chart is 44.4 ms a frame in the mode this chart is in, and a sweep display buys this path nothing because the walk is indifferent to what moved - O(1) in operations sent, which was `PL-Q197`'s bottleneck, and O(n) in the walk, which is today's. The accepted ceiling is written at `CHART_COLUMN_BUDGET_PER_SERIES`, where a session sizing the chart will be holding it. **What none of that reaches is a floor**: an idle page of about a hundred controls still costs 10.3 ms, five times a second, to discover that nothing moved - so `PL-QXSB` asks whether the interface should stay on Flet at all and is admitted to v0.5.0's gate, because that milestone's defining feature is a second chart. PySide6 with pyqtgraph measures 0.51 ms for the same frame and barely scales - 380 times the points costs four times the frame - while PyQt is ruled out by licensing rather than preference, this project being Apache-2.0 against PyQt6's GPLv3-or-commercial. **The interface also says less, and says who it is for.** The concentration chart's explanatory prose is cut to legend and labels (`PL-6580`), the reader it is written for is named in a rule every session editing `app/` loads (`PL-B89V`), and the running build is on screen so a fix verified by eye can be attributed to the build that drew it (`PL-YKF8`). **Beside them, the apparatus caught its own checks reporting more than they checked.** `bin/docket verify`'s item-front-matter guard compared `git show <base>:<bare filename>`, so the lookup always failed, the miss was swallowed as a new item file, and the check reported PASS on every branch including one that marked its own item done (`PL-20PT`); forty-two open items carried neither a gate placement nor a recorded deferral, which is the one disposition the presence rule forbids (`PL-36R4`), and the check that closes that hole immediately turned `main` red on the first item to arrive after it, because that item had merged on a base whose CI predated the check (`PL-33WM`). Twenty-one items, one of which is the v0.4.10 cut itself, completing the `delegation` feature.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.12 carried this text after its first sentence until then. This item cut v0.4.12 as well as v0.4.11 (`#489`). The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> The chart drew by summarising a store of recorded samples; it now evaluates the run's score at the instants it plots, and the store is gone with the summariser. `RunHistory`, `HistoryWindow`, `SimulationHistorySample` and the M4 decimation module are deleted - 671 lines of a careful implementation, removed because the architecture deleted the problem it solved rather than because it was wrong - along with the Jugel et al. 2014 paper it was founded on and every citation of both. Net 860 lines out. **The change was made for a safety reason rather than for tidiness.** `PL-4RBD` was banded a `P2` fidelity defect on a 0.04 percentage-point error measured at a chart window the interface had not had for four releases; re-measured against the shipped time bases, the alveolar trace departed from the run by 0.65 pp at a 12-hour base - 0.32 MAC of sevoflurane - drawn with nothing to say the shape between plotted points was inferred. It is `P1` `safety`, and the fix is structural: a control event now gets its own column, read from the keyframe the score already holds, so it is exact rather than placed. **What that did and did not buy is measured and recorded.** The kink at a dial change is gone. The curvature is not: columns sit at the spacing the time base implies and the chart rules a straight line between them, so the worst departure fell to 0.53 pp, 0.26 MAC, and moved to the steep early wash-in where a learner watching an induction is looking. `PL-GS3R` carries that measurement, the three routes out of it, and the decision the project owner owes. Beside the simulator work, the branch-id rule stops failing the owner's own web edits and any contributor's pull request, and `CONTRIBUTING.md` exists now the repository is public. No equation, parameter, numerical method or solver step moves.
