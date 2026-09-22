---
id: PL-NVT4
title: The native scroll bar's handle is ~1.9:1 against its own groove, a style-derived shade no requirement measures
priority: P3
effort: S
status: ready
classes: ux, docs
feature: chrome-colour-audit
touches: src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_dark_appearance.py, docs/MODEL.md
added: 2026-09-22
payoff: docs/MODEL.md's claim to hold SC 1.4.11 is true of the scroll bar, or says why the scroll bar is outside it
not-delegable: the done state forks on what WCAG's Understanding text for SC 1.4.11 says, read at source, and one branch is a route choice the brief reserves for the project owner, so no command can state it in advance
---

**Problem.** The native scroll bar's handle is ~1.9:1 against its own groove, a style-derived shade no requirement measures

**Measured 2026-09-22, while implementing `PL-KRZW`** (the application-palette
declaration), with `tools/contrast_check.py`'s own `contrast_ratio`:

| Surface the style shaded from | Handle on groove | Ratio |
| --- | --- | --- |
| Today's light host, undeclared | `#B1B1B1` on `#F3F3F3` | 1.93:1 |
| PANEL, after `declare_application_colours` | `#BCBCBC` on `#FFFFFF` | 1.90:1 |

**This is pre-existing rather than introduced.** The two rows are within 0.03
of each other, so the low-contrast handle is what every reader on a light host
already sees; `PL-KRZW` moved dark hosts onto the same rendering rather than
creating the shortfall. Filed because the measurement was taken, not because
the change caused it.

**Why no requirement covers it.** The requirement table measures colours this
project *declares*. A scroll bar's groove, handle and edges are derived by the
platform style - Fusion, here - from the `Button` role, so the handle's
`#BCBCBC` is arithmetic this project does not author and cannot name in
`app/theme.py`, where `check_colors_live_in_the_theme` requires every declared
colour to live. Adding a requirement for it would be measuring a value the
project does not control, and the ratio would change with the style.

**The open question is whether SC 1.4.11 reaches it.** WCAG 2.2 SC 1.4.11
(Non-text Contrast) asks 3:1 for "visual information required to identify user
interface components and their states". Whether a scroll bar handle against its
own groove is that, or whether the bar as a whole against the page is the pair
that matters, has not been read at source from this container -
`www.w3.org` is refused at the gateway (`.claude/rules/citing-sources.md`,
measured 2026-09-19), so the Understanding document has not been consulted. Do
not settle this from memory. `docs/MODEL.md` § "Color contrast, and the
standard this interface is held to" lists SC 1.4.11 as held rather than
deferred, so if it does reach native chrome this is a gap in the claim and not
only in the pixels.

**Done when** the criterion's own text has been read at source on whether it
reaches a style-derived sub-control; and either `docs/MODEL.md` records that
native chrome is outside the measured set with the reason, or - if it is inside
it - the scroll bar is styled to a declared, measured pair and the requirement
table gains the entry. The second route costs the native bar, so it is a
decision rather than a fix.

**Why it matters.** `docs/MODEL.md` § "Color contrast, and the standard this
interface is held to" states SC 1.4.11 as held. A scroll bar is how a reader
reaches everything below the fold. If the criterion reaches a handle against its
groove, the section claims a conformance the interface does not have, which is a
false statement in the authoritative specification. If the criterion does not
reach it, the section should say so. Otherwise a reader who measures the bar
finds 1.9:1 under a claim that reads as covering it.
