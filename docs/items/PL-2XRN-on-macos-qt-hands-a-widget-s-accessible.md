---
id: PL-2XRN
title: On macOS, Qt hands a widget's accessible description to VoiceOver as the element's label, so five controls that carry a description may be announced by it in place of their name
priority: P3
effort: S
status: ready
classes: defect
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/workspace_tabs.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it: it changes only what a screen reader on a Mac may say for five layout controls (triage 2026-11-28)
added: 2026-11-28
payoff: a VoiceOver user on a Mac hears each Area control's name, not only its description
---

**Problem.** Qt 6.12's macOS bridge returns a widget's accessible name as the element's `accessibilityTitle` and its accessible description as its `accessibilityLabel` (`src/plugins/platforms/cocoa/qcocoaaccessibilityelement.mm` at tag v6.12.0 of `qt/qtbase`, read 2026-11-28). Apple's documentation calls the title "a button's visible text" and the label "a short description of the accessibility element" (`NSAccessibilityProtocol`, read 2026-11-28). Five widgets set both: `ViewChooser`, `AreaMenu`, `_AreaHandle` and `_CornerZone` in `app/area_layout.py`, and `LayoutMenu` in `app/workspace_tabs.py`. Where VoiceOver or Voice Control reads the label before the title, or in place of it, a Mac user hears "Drag it to split or join the Area." where Linux and Windows read "Area corner, Wash-in 2, bottom left". The Windows bridge hands the name over as the element's name and the description as its full description (`qwindowsuiamainprovider.cpp`), and the Linux bridge hands the description over as the description (`atspiadaptor.cpp`, `GetDescription`), so only macOS is in question.

**Why it matters.** A name that a screen reader replaces with a description leaves a VoiceOver user unable to tell which corner, border or menu they are on, and a Voice Control user unable to say the words the control shows (WCAG 2.2 SC 4.1.2 and SC 2.5.3). No Apple document read so far says which of the two VoiceOver reads first, so this is unconfirmed.

**Generator check.** No head states the fact misread here, which is how each platform's bridge maps a widget's name and description.

**Found** by `PL-PN2C`'s blind review, 2026-11-28. `PL-PN2C` gave its legend boxes no description for this reason.

**Done when** what VoiceOver reads for one of the five widgets is known, from Apple's documentation or a run on macOS, and either the descriptions move where macOS reads them after the name, such as Qt's help text, or this item records that VoiceOver reads the title first.
