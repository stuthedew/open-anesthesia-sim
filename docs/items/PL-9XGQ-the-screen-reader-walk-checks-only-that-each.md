---
id: PL-9XGQ
title: The screen-reader walk checks only that each control a reader can reach has a name, so a plot with no name or description and two controls with one name both pass it, and each is found by reading one widget (PL-T9RB, PL-R1M6, PL-YSFX)
priority: P1
effort: S
status: ready
classes: defect
feature: presentation-safety
touches: tests/integration/test_keyboard_focus.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; its members are deferred from the same gate, and the release waits only on the owner's test drive (triage 2026-11-28)
added: 2026-11-28
filed-pr: 2353
payoff: a plot, a schematic or a control added later fails a test when a screen reader would get no name for it, or a name it shares with another, instead of waiting for someone to read that widget
root-cause-of: PL-RK9Z, PL-T9RB, PL-R1M6, PL-YSFX
generator: live - the walk PL-RK9Z built checks only that a node which takes the focus has a name, so PL-R1M6 and PL-YSFX were found the day it closed and PL-XV64 the day after; nothing checks a plot or compares two names
misread: What a screen reader is told about each element: its role, and a name unique in its window
---

**Problem.** The walk in `tests/integration/test_keyboard_focus.py` (`_unnamed`, built by `PL-RK9Z`) reads the tree that Qt hands each platform's accessibility interface. It fails on a node that takes the focus and has no name, and it checks nothing else. A plot takes no focus (`test_a_plot_is_not_a_tab_stop` holds every `PlotWidget` at `Qt.FocusPolicy.NoFocus`), so a plot with no name and no description passes it. The concentration chart did until `PL-T9RB`, and the wash-in plot and the compartment schematic still do (`PL-R1M6`). The walk never compares two names, so two controls with one name pass it too. Each compared run's playback selector is "Playback", and the Induction Workspace's two window selectors are both "Time base" (`PL-YSFX`). So each gap is found only when someone happens to read that widget.

**Why it matters.** A screen-reader user who reaches an unnamed plot learns nothing of what it draws. One who reaches two controls with one name cannot tell which run or which plot the next key press changes. `PL-R1M6` and `PL-YSFX` cite the WCAG 2.2 success criteria that ask for each (1.1.1, 2.4.6 and 4.1.2, read 2026-11-27). A View or control added later carries the same risk, and no test fails on it.

**Reproduced 2026-11-28.** `_unnamed` keeps only nodes whose state is focusable (`node.state().focusable`), and no line of `tests/integration/test_keyboard_focus.py` compares the names of two nodes. In `src/anesthesia_sim/app/qt_chart.py` only the concentration chart installs an accessible interface (`_ConcentrationChartAccessible`, role `Graphic`). `WashInChart` and the schematic's widgets in `qt_schematic.py` install none.

**Approach.** Widen the one walk rather than fixing widgets one at a time. Over every shipped Workspace, with one run and with two compared, fail on a plot or schematic widget that has no name or no description, and on two visible nodes of one role in one window that have the same name. Keep the new-case question in the walk, as now. The widened test fails until `PL-R1M6`, `PL-YSFX` and `PL-XV64` (the Area corners and borders share one name, filed on the defects thread's branch on 2026-11-28) are fixed, so land it with the last of them.

**Done when.** A test walks the accessible tree of every shipped Workspace, with one run and with two compared. It fails on any plot or schematic with no name or no description, and on any two visible elements of one role in one window that share a name. It passes on `main` once `PL-R1M6`, `PL-YSFX` and `PL-XV64` are fixed.

**Generator check.** This item is the head of one fact: what a screen reader is told about each element on screen, its role and a name that tells it apart from the others in its window. Each widget's writer misread it: `PL-RK9Z` (61 controls with no name, closed 2026-11-27), `PL-T9RB` (the concentration chart, closed 2026-11-27), `PL-R1M6` and `PL-YSFX`. No head's `misread:` states it (`bin/docket generators --misread`, read 2026-11-28).
