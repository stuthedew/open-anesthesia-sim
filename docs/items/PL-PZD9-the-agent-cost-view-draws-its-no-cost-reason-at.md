---
id: PL-PZD9
title: The agent cost View draws its no-cost reason at the size of a value, larger than any figure on screen, and its price form's fields stretch across the whole Area, 1086 px wide at 1920 by 1080
priority: P3
effort: S
status: done
classes: ux
feature: interface-design-review
milestone: v0.6.19
touches: src/anesthesia_sim/app/qt_agent_cost.py, src/anesthesia_sim/app/qt_agent_price.py, src/anesthesia_sim/app/agent_cost.py, src/anesthesia_sim/app/theme.py, tests/integration/test_agent_cost_view.py
added: 2026-11-22
closed: 2026-11-22
pr: 2206
payoff: with no price set, the largest text on screen is no longer an instruction, and the price form fits its content
tests: tests/integration/test_agent_cost_view.py::test_a_reason_for_no_cost_is_drawn_smaller_than_a_cost, tests/integration/test_agent_cost_view.py::test_no_price_field_stretches_across_a_wide_area
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

**Built 2026-11-22.** `CostShown` gains `is_reason`, and the panel draws a reason at the line-above's size, unbolded. The price fields stop at `PRICE_FIELD_MAX_WIDTH`, 320 px, a placeholder.

**Regression run.** The two new tests were run against the code before the fix, with the cap written as the literal 320: the reason test failed with `assert 22 < 22` (the reason's font against the amount's), and the width test with every field wider than the cap.

**Docs swept 2026-11-22.** `docs/INTERFACE.md`, `docs/ARCHITECTURE.md` and `README.md`, searched for the changed wording and for the element's look; none states it, so none changed.

**Blind review 2026-11-22.** One pass, one optional finding: the cost line was restyled on every frame. Fixed on this branch, so the label is restyled only when it changes between a cost and a reason.
