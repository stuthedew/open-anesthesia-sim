---
id: PL-SRP7
title: Research the established practice for making the interface localizable, so that a later build can translate its text and format numbers, dates and money for the reader's region without rework (owner, 2026-11-22)
priority: P3
effort: M
status: ready
classes: planning
feature: preferences-store
touches: src/anesthesia_sim/app/formatting.py
added: 2026-11-22
payoff: the project knows how to make the interface translatable and regional before more strings and formatters are written in a way that would need rework
---

**Problem.** Research the established practice for making the interface localizable, so that a later build can translate its text and format numbers, dates and money for the reader's region without rework (owner, 2026-11-22)

The owner asked on 2026-11-22, while setting the rule that display units live in one Settings window (`PL-TLW6`): "don't need to implement now but research best practice for allowing localization" (project owner, 2026-11-22). The interface's strings are English literals in `src/anesthesia_sim/app/`, held word for word by `tests/integration/approved_interface_strings.json`, and numbers are formatted by hand in `app/formatting.py`.

**Why it matters.** Text, number formats and units that are built into the code now become a rewrite later. Knowing the established route first, such as Qt's own translation tools and the Unicode CLDR locale data, lets each new string and formatter be written so translation and regional formats can be added without touching the clinical values.

**Done when.** The brief records, from sources read in the session, the established practice for a Qt for Python application: how strings are marked and translated, how numbers, dates and money follow the reader's region, how units fit with the Settings window of `PL-TLW6`, and what this project would have to change in how it writes strings and formatters today. It ends with a recommendation for the owner, with no code changed.

**Generator check.** A one-off: research the owner asked for.
