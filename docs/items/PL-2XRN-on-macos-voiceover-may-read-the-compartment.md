---
id: PL-2XRN
title: On macOS, VoiceOver may read the compartment schematic's description without the run and instant its name gives
priority: P1
effort: M
status: done
classes: defect, safety
feature: presentation-safety
touches: src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/qt_schematic.py
added: 2026-11-28
closed: 2026-11-28
pr: 2363
payoff: a VoiceOver user on a Mac is told which run and which instant each picture's modelled values belong to
tests: tests/unit/test_compartment_schematic.py::test_the_schematic_s_description_opens_with_its_run_and_instant, tests/integration/simulation_view/test_simulation_view_charts.py::test_each_compared_schematic_s_description_starts_with_its_own_run_and_instant, tests/integration/simulation_view/test_simulation_view_charts.py::test_each_schematic_tells_a_screen_reader_its_run_its_instant_and_its_values
---

**Problem.** Qt 6.12's macOS bridge returns a widget's accessible name as the element's `accessibilityTitle` and its accessible description as its `accessibilityLabel` (`src/plugins/platforms/cocoa/qcocoaaccessibilityelement.mm` at tag v6.12.0 of `qt/qtbase`, read 2026-11-28). Apple's documentation calls the title "a button's visible text" and the label "a short description of the accessibility element" (`NSAccessibilityProtocol`, read 2026-11-28). That page does not say which of the two VoiceOver reads, and the paragraph "What VoiceOver reads" below gives the sources that do. The Windows bridge hands the name over as the element's name and the description as its full description (`qwindowsuiamainprovider.cpp`), and the Linux bridge hands the description over as the description (`atspiadaptor.cpp`, `GetDescription`), so only macOS is in question.

Every widget whose description differs from its name is affected where VoiceOver reads the label before the title, or in place of it. The approved wording list, `tests/integration/approved_interface_strings.json`, lists them:

1. The three pictures. `schematic_description` in `app/compartment_schematic.py` gives each container's tension, amount and share with no run and no instant; only `schematic_name` carries them, such as "Compartment schematic, Run 2, at 10m of simulated time". So while two runs are compared, a Mac user could hear one run's modelled tensions without being told which run or when. The concentration chart's and the wash-in plot's descriptions (`dashboard_frame.concentration_chart_description` and `wash_in_plot_description`) reach VoiceOver the same way, and whether each names its runs and instant itself is still to be checked.
2. Five layout controls: `ViewChooser`, `AreaMenu`, `_AreaHandle` and `_CornerZone` in `app/area_layout.py`, and `LayoutMenu` in `app/workspace_tabs.py`. A Mac user could hear "Drag it to split or join the Area." where Linux and Windows read "Area corner, Wash-in 2, bottom left".
3. Three buttons whose description Qt takes from their tool tip: each plot's "Show an earlier part of the run" and "Show a later part of the run", and "Duplicate the current Workspace".

**Narrowed 2026-11-28.** The controls in points 2 and 3 above moved to `PL-26K2`, which carries their research and direction, because none of them shows a clinical value. This item keeps the pictures.

**What VoiceOver reads, from sources (2026-11-28).** Apple's "Accessibility Programming Guide for OS X", § "The OS X Accessibility Model", says a screen reader asks a button for "A label (defaults to the button's title)". Qt's bug report QTBUG-140871 (open, reported against Qt 6.9.3, read 2026-11-28 from `bugreports.qt.io`) records VoiceOver reading a Qt Quick item's description in place of its name, on macOS and on no other platform. With the bridge's mapping above, that says VoiceOver reads a widget's description in place of its name.

**The two plots checked.** `latest_values_lines` and `latest_wash_in_lines` in `app/chart_frame.py` open each value line with the run while more than one is drawn, and the instant of its last drawn point, such as "Modelled sevoflurane, Run 2, at 10m: ...". So the concentration chart's and the wash-in plot's descriptions already name the run and instant of every value, and only the schematic needed a change. The plots' names also give the window, whether it is held, and the Area's name while another Area shows a copy, and a Mac user does not hear those. That is `PL-26K2`'s, because no value is heard without its run and instant.

**Why it matters.** A modelled value read without its run and instant is a value in the wrong context, which `CLAUDE.md`'s safety standard counts as a safety failure. A control's name read as its description leaves a VoiceOver user unable to tell which corner, border or menu they are on (WCAG 2.2 SC 4.1.2), and a Voice Control user unable to say the words it shows (SC 2.5.3).

**Generator check.** No head states the fact misread here, which is how each platform's bridge maps a widget's name and description.

**Found** by `PL-PN2C`'s blind review, 2026-11-28, which gave the legend boxes no description for this reason. Its second round found the pictures' share of it.

**Direction.** Two parts, either of which removes the hazard. First, find what VoiceOver reads for a picture and for a control that carry both, from Apple's documentation or a run on macOS. Second, whatever it reads, make each picture's description name its run and instant itself, so the values carry their context whichever text a screen reader gives. A description of a control can move to Qt's help text, which the macOS bridge hands over as `accessibilityHelp`.

**Gate.** The bridge's mapping and the descriptions were both present before v0.7.0's debt list froze, so the item re-enters that list. It is not deferred, because whether a Mac user hears values without their run and instant is not yet known.

**Done when** each picture's description names the run and the instant its values belong to, a test writes that out by hand for two compared runs, and VoiceOver's reading is recorded here from a source. The controls' half is `PL-26K2`'s.

**Fixed 2026-11-28.** `schematic_description` in `app/compartment_schematic.py` now takes the run's name and opens with the run and the instant, such as "Run 2, at 10m of simulated time.", "At 10m of simulated time." for a lone run, and "Run 3, simulated time not shown." while the instant is withheld. `_spoken_instant` builds those words once, and `schematic_name` reads them too, so the name and the first line cannot disagree. `SchematicCanvas.graphic_description` in `app/qt_schematic.py` passes the run's name, which `show_name` already set and already reported to a screen reader as a text change. `docs/INTERFACE.md`'s paragraph on the schematic's text alternative says so and names the sources for what VoiceOver reads.

**Regression check.** With the two source files stashed (`git stash push src/anesthesia_sim/app/compartment_schematic.py src/anesthesia_sim/app/qt_schematic.py`), `pytest tests/integration/simulation_view/test_simulation_view_charts.py -k schematic` fails both changed tests, with "assert 'Diagram of t... the alveoli.' == 'Run 1, at 10...mulated time.'" for the two compared runs. The new unit test fails there only with a TypeError, because `schematic_description` took no run name then, so the two-run integration test above is its variant that runs on the code before.

**Blind review.** Two passes ran, and each found one gap, which `PL-26K2` now holds.

1. Pass 1, optional: the plots' names give the window and whether it is held, which a Mac user does not hear, and `docs/INTERFACE.md` said the plots needed nothing. Filed into `PL-26K2`, and the sentence now says what the plots' descriptions leave out.
2. Pass 2, optional: no picture's description gives the Area's name that its name adds while another Area shows a copy. Filed into `PL-26K2`.
