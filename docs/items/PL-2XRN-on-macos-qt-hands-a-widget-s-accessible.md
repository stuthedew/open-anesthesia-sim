---
id: PL-2XRN
title: On macOS, Qt hands a widget's accessible description to VoiceOver as the element's label, so a picture's description may be read without the run and instant its name gives, and a control's description in place of its name
priority: P1
effort: M
status: ready
classes: defect, safety
feature: presentation-safety
touches: src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/workspace_tabs.py
added: 2026-11-28
payoff: a VoiceOver user on a Mac is told which run and which instant each picture's modelled values belong to, and each control's name
---

**Problem.** Qt 6.12's macOS bridge returns a widget's accessible name as the element's `accessibilityTitle` and its accessible description as its `accessibilityLabel` (`src/plugins/platforms/cocoa/qcocoaaccessibilityelement.mm` at tag v6.12.0 of `qt/qtbase`, read 2026-11-28). Apple's documentation calls the title "a button's visible text" and the label "a short description of the accessibility element" (`NSAccessibilityProtocol`, read 2026-11-28), and says nothing about which of the two VoiceOver reads first. The Windows bridge hands the name over as the element's name and the description as its full description (`qwindowsuiamainprovider.cpp`), and the Linux bridge hands the description over as the description (`atspiadaptor.cpp`, `GetDescription`), so only macOS is in question.

Every widget whose description differs from its name is affected where VoiceOver reads the label before the title, or in place of it. The approved wording list, `tests/integration/approved_interface_strings.json`, lists them:

1. The three pictures. `schematic_description` in `app/compartment_schematic.py` gives each container's tension, amount and share with no run and no instant; only `schematic_name` carries them, such as "Compartment schematic, Run 2, at 10m of simulated time". So while two runs are compared, a Mac user could hear one run's modelled tensions without being told which run or when. The concentration chart's and the wash-in plot's descriptions (`dashboard_frame.concentration_chart_description` and `wash_in_plot_description`) reach VoiceOver the same way, and whether each names its runs and instant itself is still to be checked.
2. Five layout controls: `ViewChooser`, `AreaMenu`, `_AreaHandle` and `_CornerZone` in `app/area_layout.py`, and `LayoutMenu` in `app/workspace_tabs.py`. A Mac user could hear "Drag it to split or join the Area." where Linux and Windows read "Area corner, Wash-in 2, bottom left".
3. Three buttons whose description Qt takes from their tool tip: each plot's "Show an earlier part of the run" and "Show a later part of the run", and "Duplicate the current Workspace".

**Why it matters.** A modelled value read without its run and instant is a value in the wrong context, which `CLAUDE.md`'s safety standard counts as a safety failure. A control's name read as its description leaves a VoiceOver user unable to tell which corner, border or menu they are on (WCAG 2.2 SC 4.1.2), and a Voice Control user unable to say the words it shows (SC 2.5.3).

**Generator check.** No head states the fact misread here, which is how each platform's bridge maps a widget's name and description.

**Found** by `PL-PN2C`'s blind review, 2026-11-28, which gave the legend boxes no description for this reason. Its second round found the pictures' share of it.

**Direction.** Two parts, either of which removes the hazard. First, find what VoiceOver reads for a picture and for a control that carry both, from Apple's documentation or a run on macOS. Second, whatever it reads, make each picture's description name its run and instant itself, so the values carry their context whichever text a screen reader gives. A description of a control can move to Qt's help text, which the macOS bridge hands over as `accessibilityHelp`.

**Gate.** The bridge's mapping and the descriptions were both present before v0.7.0's debt list froze, so the item re-enters that list. It is not deferred, because whether a Mac user hears values without their run and instant is not yet known.

**Done when** each picture's description names the run and the instant its values belong to, a test writes that out by hand for two compared runs, and either VoiceOver's reading order is recorded here from a source or every control's description has moved where macOS reads it after the name.
