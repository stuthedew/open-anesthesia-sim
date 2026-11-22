---
id: PL-TLW6
title: Set display units, the currency among them, once in the app's Settings window, instead of a currency typed with each price and a unit chosen in the agent cost View (owner, 2026-11-22)
priority: P3
effort: L
status: ready
classes: feature, ux
feature: preferences-store
touches: src/anesthesia_sim/app/preferences.py, src/anesthesia_sim/app/agent_cost.py, docs/INTERFACE.md
added: 2026-11-22
payoff: a learner sets each unit once, in the app's Settings, and every View shows prices, costs and amounts in that unit
---

**Problem.** Display units are chosen in two scattered places. Each agent's price is typed with its own three-letter currency code (`app/preferences.py`, the price's `currency` field), so two agents can be priced in two currencies. The agent cost View keeps its own unit for the delivered agent (`agent_cost_unit`, one of `AGENT_COST_VIEW_UNITS`). The project owner said on 2026-11-22: "It will be one unit throughout app. But can be changed which unit it would be", and "Like you would set a unit in main program settings (e.g. temperature or whatever). ... Wouldn't be setting one off units here and there." (project owner, 2026-11-22)

**What the platform guidance says.** Apple's Human Interface Guidelines, Settings page (read 2026-11-22, https://developer.apple.com/design/human-interface-guidelines/settings): on macOS an app's settings open from "the Settings item in your app's or game's App menu", people "often use the standard Command-Comma (,) keyboard shortcut", and an app should "Put general, infrequently changed settings in your custom settings area" and "Avoid adding settings buttons to a window's toolbar". It also says to "Respect people's systemwide settings and avoid including redundant versions of them", naming language and region, and to "provide default settings that give the best experience to the largest number of people".

**Why it matters.** One place for units means a learner sets the currency and the amount unit once and every View agrees, so no two costs or amounts on screen are in different units. Today a second price in another currency, or a View left on another unit, puts mixed units side by side.

**Done when.**

1. The app has one Settings window, opened from the App menu's Settings item and Command-comma on macOS and from the platform's usual place elsewhere, and it holds every display unit the reader can choose: the currency, and the unit the agent cost View now keeps for itself.
2. No View carries a unit control of its own, and a price is entered without a currency of its own.
3. Each unit's default is the one the system's region gives, so a reader who never opens Settings sees their own currency, and the reader can change it in Settings (project owner, 2026-11-22: "Region would be default but would allow to change if desired").
4. A test shows that changing each unit in Settings changes the unit printed in every View that shows it.
5. `docs/INTERFACE.md` says where units are set, and what happens to prices already saved in another currency. The building session decides that and records it here.

**Generator check.** A one-off: work the owner asked for, with no fact misread behind it.

**A limit on which units Settings holds** (found 2026-11-22 by the localization research thread, `PL-SRP7`). A region's default is unsafe for some clinical units. CLDR's unit preferences give pounds as the United States unit for a person's weight, and NCC MERP's recommendation adopted 2018-10-25, "Recommendations to Weigh Patients and Document Metric Weights", says screens should list or prompt for weight in metric units only. So a patient's weight and any drug amount never follow the region and never appear in Settings. Settings holds only units that are in real use in more than one form, each with its regional default cited. The agent cost View's liquid unit and the currency are the two this item covers today. The NCC MERP source has not been read in this session; the building session reads it before citing it.
