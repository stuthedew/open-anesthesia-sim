---
id: PL-1P15
title: Show what the delivered agent cost in money, at a price per agent the reader sets, on the agent cost View
priority: P2
effort: M
status: blocked
classes: safety, anticipated
feature: liquid-agent-consumption
touches: src/anesthesia_sim/app, tests/integration, tests/unit, docs/MODEL.md
blocked-by: PL-B396, PL-VJZK, PL-93B3
added: 2026-10-25
payoff: a learner sees what the delivered agent cost at their own institution's price, labelled with its currency and the price's date
verify: grep -rq 'def test_the_cost_is_the_delivered_liquid_volume_times_the_price' tests
---

**Where this came from.** `PL-LF0P` scoped v0.7.0 on 2026-10-25, and the
project owner put planned-milestone item 28, agent cost, inside it (project
owner, 2026-10-25, ratified, over leaving item 28 unscheduled and deferring its
four entries to Gate 4). `PL-B396` builds the readout in millilitres of liquid
equivalent. The owner asked on 2026-09-16 for a price the reader sets, "so
user can simulate cost at their institutions price" (recorded in `PL-B396`).

**Problem.** The low-flow lesson is economic, and the agent cost View will
show only a volume.

**What to build.** On the agent cost View, the delivered agent's cost in money
at a price per agent that the reader sets. Gas Man bills delivered agent too
(Workbook, printed p. 174: `Cost = DELIVERED Flow x Cost/mL vapor`). The price
is stored with its currency and the date it was set, as `PL-VJZK` specifies,
in the preferences file `PL-93B3` builds. The project ships no price, because
a shipped price goes stale and differs by institution. With no price set, the
View says so rather than showing a cost.

**Why it matters.** Planned-milestone item 28 calls the economic argument for
low fresh gas flow "the one lesson in this class of simulator that the
application has the numbers for and does not draw", and a volume alone does
not draw it.

**Tests.** An end-to-end test sets a price and checks the displayed cost
against delivered liquid-equivalent volume times price, computed
independently. A test checks that no cost shows before a price is set.

**Done when.** A learner can set a price per agent and see the cost of the
delivered agent, labelled with its currency and the price's date.
