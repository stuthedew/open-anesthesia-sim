---
id: PL-RF2S
title: Every widget, painted canvas and chart keeps the last value written to it, and three separate paths each write a part of the screen, so a value from an earlier run or the other compared run stays wherever a path does not reach: the cause under PL-X7D5, PL-J5GC, PL-5JTH and PL-GTH6, whose four fixes each added a test over a hand-kept list
priority: P1
effort: L
status: needs-decision
classes: safety, refactor
feature: every-view-in-run-state-tests
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/view_contract.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/run_surfaces.py, tests/integration, docs/ARCHITECTURE.md
deferred-from: v0.7.0 - a new problem, not present at the freeze (817a4d88, 2026-10-25): its three members were filed on 2026-11-10; not live: checked 2026-11-10, the audit found no wrong value on screen behind any member, and the gap is in the tests
added: 2026-11-11
payoff: a value from an earlier run, or from the other compared run, has no widget to stay in, because every View and panel is drawn whole from one value on every path
root-cause-of: PL-B8DL, PL-0G2P, PL-G2WC
generator: live - three members, PL-B8DL, PL-0G2P and PL-G2WC, were filed on 2026-11-10, 14 days after PL-J5GC closed, and each new View or panel is another place for the next
misread: Which widgets state a run's current state, and that each is restated on every path that changes it
---

**Problem.** Every widget, painted canvas and chart keeps the last value written to it, and three separate paths each write a part of the screen, so a value from an earlier run or the other compared run stays wherever a path does not reach: the cause under PL-X7D5, PL-J5GC, PL-5JTH and PL-GTH6, whose four fixes each added a test over a hand-kept list

**Asked for by the project owner on 2026-11-11**, as a fresh look at a cause fixed four times. The request named a direction to test: build the interface so that a View cannot hold a run's value, for example by drawing every View from one snapshot of run state. It asked for the design on one screen before any code. This item holds that design and waits for the answer.

**What each fix built, and what got past it.** Each row was checked against the code on 2026-11-11 at `origin/main`.

| Fix | What it built | What got past it |
| --- | --- | --- |
| `PL-X7D5` | `RunView._write_statement`, one writer for a run's status, transport, agent identity, record and dials, called by `refresh` and by `present_halt`. A test compares every widget attribute of a `RunView` on a drawn run and a halted one, except five named in `FRAME_WIDGETS`. | The test walks one `RunView`. The dashboard's own panels were outside it (`PL-YHR3`, then `PL-5JTH`). It compares a widget with itself on two screens, so two widgets on one screen that disagree pass it (`PL-J5GC`). |
| `PL-5JTH` | `SimulationView.halt_restatements`, one list of the dashboard panels a halt restates, and a test that every dashboard control is in a `RunView`, in that list or in `NOT_RESTATED_ON_A_HALT`. | The test walks the layout that the test file builds. That layout, `_EVERY_VIEW`, holds four of the six registered View kinds (`PL-B8DL`). |
| `PL-J5GC` | A test that each value and what qualifies it describe one step, over 12 scenarios. Three groups of widgets are checked, and 23 other attributes are listed in `UNGROUPED_WIDGETS` with a reason each. `present_halt` withholds the cards, the clock, the accounting panel, the schematic and the delivered agent when `_started_over_since_the_cards` is set. | The groups name attributes of `RunView` by hand. `_widget_state` reads the text of labels, buttons, combo boxes and sliders, so an amount the schematic paints is in no comparison (`PL-0G2P`). The agent cost View's unit selector and price form are written only by `AgentCostView.refresh`, which a halt never calls. |
| `PL-GTH6` | Nothing. It recorded eight defects and closed because none was filed for 34 days. | No test compares a value with the run it is shown under (`PL-G2WC`). `ViewTick` carries `snapshots` and `runs` as two tuples paired by position, the run's name is written by `set_run_name` on a path of its own, and three readers take `snapshots[0]`. |

**The cause.** The screen is where the displayed values are stored. Every label, painted canvas and chart keeps the last value written to it until some code writes it again. At least three paths write, each from a different input and each to a part of the screen:

1. A frame that draws: `SimulationView._refresh_view` hands each View a `ViewTick`, then calls `RunView.refresh` with the run's snapshot, then writes the bookmark and fork panels.
2. A halt: `RunView.present_halt` writes from `SimulationController.record()`, and `halt_restatements` writes two panels. No View is handed a tick.
3. Writes outside both: `_rename_runs` calls `set_run_name` and `set_comparing`, and a dragged dial calls `_refresh_against_last_frame`.

A View is also written through two channels. Its `refresh` takes the tick. The copies it shows of a run's controls, accounting panel, schematic and agent cost are written by `RunView` through `RunSurfaces`, on `RunView`'s own schedule.

So "everything on screen describes one state of the run it is shown under" is true only if every path reaches every widget. That is a table of paths against widgets, and nothing owns it. Each earlier fix added a test that lists one side of the table from the widgets a test file happens to build: a `RunView`'s attributes, a hand-kept layout, a hand-kept exemption list, the widget classes whose text the test knows how to read. Each escape is a place the list did not reach. The run a value belongs to has the same defect one level up: the value is a bare string, and its run is known only from its position in a tuple and from a name another path wrote.

The repository's own principle names this: a shared fact has one source of truth. What the screen should show now is a fact with no home. It is worked out in pieces at the moment of each write and then lives only in the widgets.

**What established practice does about it.** Read on 2026-11-11. Each quotation was checked against a downloaded copy of the page. Five of the sites were outside this session's network, so their pages were read from the publisher's own source repository on `raw.githubusercontent.com`.

- **Android's guide to the UI layer** is the closest match to this design. "The UI state is an immutable snapshot of the details needed for the UI to render." "Use a single UI state object to handle states that are related to each other." "If you expose the list of news items and the number of bookmarks in two different streams, you might end up in a situation where one was updated and the other was not." "Never modify the UI state in the UI directly unless the UI itself is the sole source of its data." It allows separate streams for unrelated data, and states the cost: "every emission causes an update to the UI element." https://developer.android.com/topic/architecture/ui-layer
- **Redux, "Three Principles".** One store, read-only state, and one path for changes: "This ensures that neither the views nor the network callbacks will ever write directly to the state." https://redux.js.org/understanding/thinking-in-redux/three-principles
- **React, "Choosing the State Structure".** "When the same data is duplicated between multiple state variables, or within nested objects, it is difficult to keep them in sync." Its example of two flags set by separate calls is this item's partial write. https://react.dev/learn/choosing-the-state-structure
- **The Elm Architecture.** The view is "a way to turn your state into HTML", a function of one model. https://guide.elm-lang.org/architecture/
- **Dear ImGui's wiki, "About the IMGUI paradigm"** (marked a draft). "An IMGUI API favors the application code owning its data and being the single source of truth for it", and retained-mode interfaces "often require synchronization mechanisms because the UI system retain more application data." It also says that "IMGUI does not mean that the library doesn't retain data", which is why point 3 under "What could still get past it" stays true in Qt. https://github.com/ocornut/imgui/wiki/About-the-IMGUI-paradigm
- **Moseley and Marks, "Out of the Tar Pit" (2006), sections 7.1.1 and 7.2.3.** Derived state that the program's logic must keep up to date puts the system "at risk of the possibility of the system entering an inconsistent state". The paper allows such state where performance needs it.
- **Alexis King, "Parse, don't validate" (2019).** "Duplicating the same data in multiple places introduces a trivially representable illegal state: the places getting out of sync." Where a copy is needed, "a small, trusted module holds sole responsibility for keeping the representations in sync." https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/

Martin Fowler's "GUI Architectures" and "Passive View" could not be fetched, so nothing here rests on them. No source on medical-device displays was read.

**Why it matters.** A value left from an earlier run, or shown under the other compared run, is a correct number in the wrong context, which `CLAUDE.md`'s safety-critical standard treats as a safety failure. The audit of 2026-11-10 found none on screen. It found that no test would catch one in the compartment schematic, in the agent cost View, in any painted value or under the wrong run's name, and each View added later widens that.

**Done when.** The decision below is answered and recorded here. If the answer is to build, this item is rewritten to the built form, with a `verify:` that names the test of point 6 of the design, and `PL-B8DL`, `PL-0G2P` and `PL-G2WC` close under it or say why they stay.

**The design: one value for the whole screen, and one call that shows it.**

1. **One value.** A frozen `Presentation` holds everything a reader can see that depends on a run: for each displayed run a `RunPresentation` (the run's id and name, its statement, its dials, and its values), the chart frame for each window, the selection, the preferences, the bookmark standings and the branch offer. One pure function builds it from the controllers. The pure parts exist already in `app/dashboard_frame.py`: `readouts`, `schematic_shown`, `delivered_shown`, `accounting`, `run_statement`, `setting_readouts`, `notice` and `halt_notice`.
2. **A halt is a state in the value, not a second writer.** A run's values are one of three kinds: drawn from this step, kept from the last frame that drew, or withheld with the reason. The builder chooses the kind once, by comparing which case the kept frame belongs to with the case the run holds now. That replaces `_started_over_since_the_cards` and `_withhold_the_discarded_run_s_values`. The builder does not raise for a run that failed: a part it cannot build becomes a withheld part. What a learner sees after a halt stays as it is today.
3. **One call.** `SimulationView` shows the value to the unconditional region, to every View and to its own panels in one pass, on every path. `RunView.refresh` and `RunView.present_halt` become one `RunView.show`. A halt shows the same value through the same call, so `halt_restatements` goes.
4. **A View is drawn from the tick alone.** `ViewTick.runs` becomes the tuple of `RunPresentation`, and `ViewTick.snapshots` and `RunSurfaces` go. A View builds its per-run widgets itself and writes them whole from the tick. A dial in a View asks for its change through `ViewRequests`, with the run's id.
5. **The run travels with the value.** One helper builds a View's block for one run from one `RunPresentation`, and writes the run's name from that same value in the same call. A View never handles two runs' values at once, so it has no way to pair a name with the other run's number. The three `snapshots[0]` readers take a field of the `Presentation` that exists only when the runs agree.
6. **One test replaces the lists.** For every kind in `view_registry.REGISTERED`, and for the whole dashboard, show state A and then state B to one instance, show state B to a new instance, and compare the pixels each draws. Any value left from A is a difference, whether a label holds it or a canvas paints it. The states come from a table that includes a halt, a Reset and an agent change that no frame draws, and two runs. A check requires each pair to differ in every field of the `Presentation`, so a field added later fails until a pair covers it. The scenarios of `PL-J5GC`'s test, which check that the builder chose the right step for each group, become tests of the pure builder with no widget.

**What it replaces.** `RunView.refresh`, `present_halt`, `_withhold_the_discarded_run_s_values` and the copy lists in `RunView`; `RunSurfaces`; `halt_restatements` and `_rename_runs`' name writes; in the tests, `FRAME_WIDGETS`, `VALUE_GROUPS`, `UNGROUPED_WIDGETS`, `SURFACE_FRAME_WIDGETS`, `NOT_RESTATED_ON_A_HALT`, the four copies of `_EVERY_VIEW` and the tests that walk them. `PL-B8DL`, `PL-0G2P` and `PL-G2WC` close under it.

**What it costs.** These are estimates from counting call sites, not from a build. `present_halt` is named 32 times under `src/` and 19 under `tests/`, and the four `build_` methods of `RunSurfaces` 16 and 7.

- Source: about 1,500 changed lines in `app/run_view.py`, `app/views.py`, `app/view_contract.py`, `app/simulation_view.py`, `app/area_layout.py`, `app/dashboard_frame.py`, `app/run_surfaces.py`, `app/qt_schematic.py` and `app/qt_agent_cost.py`. No equation, parameter or displayed value's computation changes.
- Tests: about 2,500 changed lines. `tests/integration/test_simulation_view.py` holds 302 tests, and those that call `refresh` or `present_halt` directly are rewritten to show a value.
- Four pull requests, each leaving the application working and each waiting for the owner's read: the value and `RunView.show`; Views drawn from the tick on every path; the run in the value; the pixel test and the removals.
- Risk, highest first. (a) The halt must be on screen before anything that can raise (`PL-25KS`, `PL-7DJK`). Today that is an order of writes. In the design the builder must not raise, and a write that raises is a defect that the halt gate still catches. The existing tests for those items stay as they are. (b) A dragged dial rewrites the run's own widgets at once while the chart waits for the render tick (`PL-018`, `PL-R2YM`). The value has to carry the kept chart frame so that this stays one pass. (c) Comparing pixels has not been tried here across two instances. `tests/integration/test_qt_rendering.py` already grabs images. If focus or layout makes equal states draw unequal pixels, the fallback compares each View's text, painted strings and frame, which is weaker for a value drawn as a shape.

**What could still get past it.**

1. A controller that itself holds a mixed state, as in `PL-3B34` and `PL-HF4B`. One value built from a mixed state is still wrong. The builder's tests cover it, and no interface structure can.
2. State a View keeps of its own: its time window, a hover readout, a scroll position, an open dialog. The hover reads the one frame the chart holds, which is replaced whole.
3. A slot added later that writes a widget outside `show`. Python does not forbid it. The pixel test finds it only for the states in its table.
4. A dialog that is not made a reader of the value, such as the bookmark editor or a question about a new case.

**Decision needed.** Whether to replace the three write paths with one value and one call, in the four pull requests above. **Recommended:** yes. The count that decides it: the table of paths against widgets grows with every View and every panel, six Views now and more on the roadmap, and each of the four earlier fixes cost a design round and then leaked within a month. The cheaper route is to build `PL-B8DL`, `PL-0G2P` and `PL-G2WC` as filed, about 600 lines of tests. It closes today's three gaps and keeps the shape that produced them, since each is another walk over built widgets. The choice is the owner's because it is a large refactor of working code, with a real risk to the halt path.

**Replays, each written to fail first.** The three open escapes are gaps in tests, and the audit of 2026-11-10 found no wrong value on screen behind them. So each replay plants the escaped defect in the code as it stands, shows that today's tests pass, and shows that the new test fails:

- `PL-B8DL`: the schematic is left out of the withhold after a Reset that no frame draws.
- `PL-0G2P`: the same, read from the painted amounts.
- `PL-G2WC`: two compared runs' agent cost panels are written from each other's delivered amount.
- `PL-VZ57`'s lead: after an agent change that no frame draws, the price form names the agent the run no longer holds. Whether that one is on screen today is not yet checked.

**Generator check.** This item is the head for the three open members of `every-view-in-run-state-tests`, and states the cause beneath the four closed heads it names.

