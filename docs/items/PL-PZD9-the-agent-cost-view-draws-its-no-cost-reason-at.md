---
id: PL-PZD9
title: The agent cost View draws its no-cost reason at the size of a value, larger than any figure on screen, and its price form's fields stretch across the whole Area, 1086 px wide at 1920 by 1080
priority: P3
effort: S
status: ready
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/app/qt_agent_cost.py, src/anesthesia_sim/app/qt_agent_price.py, src/anesthesia_sim/app/agent_cost.py, src/anesthesia_sim/app/theme.py, tests/integration/test_agent_cost_view.py
added: 2026-11-22
payoff: with no price set, the largest text on screen is no longer an instruction, and the price form fits its content
---

**Problem.** The agent cost View draws its no-cost reason at the size of a value, larger than any figure on screen, and its price form's fields stretch across the whole Area, 1086 px wide at 1920 by 1080

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What a learner sees.** With no price set, the cost line reads "No cost: set
your price for sevoflurane below." in the bold value size, so the largest text
on the whole screen is an instruction rather than a number
(`view-agent_cost-1920x1080.png`). The four price fields are 532 px wide at
1366 by 768 and 1086 px wide at 1920 by 1080, for a currency code of three
letters and prices of a few digits.

**Why it matters.** Size says "this is the value". A reason drawn at the size
of a value competes with the delivered amount above it, and a learner scanning
for the cost reads a sentence. A field far wider than its content makes the
eye travel across the Area for nothing, and the button row sits far from
the field it applies.

**What to do.** Draw a no-cost reason in the caption style, MUTED at the
qualifier size, and draw a cost in the value style. Cap the width of the
form's fields at a theme value. Both are look choices, so they are
placeholders the session decides.

**Done when.** A test shows the no-cost reason in a smaller font than the
delivered amount, and the cost in the delivered amount's font. A test opens
the agent cost View in a wide Area and finds no price field wider than the cap.

**Reproduced 2026-11-22** on `a7eb53f`, offscreen: the no-cost reason renders at the value size, and the price fields measure 532 px wide at 1366 by 768 and 1086 px at 1920 by 1080.

**Generator check.** A one-off: the cost line has one label for two kinds of text, a value and a reason, and only this View has a reason in a value's place.
