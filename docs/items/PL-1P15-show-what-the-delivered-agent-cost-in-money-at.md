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

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): still true.** Nothing under `src/` holds a price, a currency or an agent cost View, and its three blockers are open. The Gas Man Workbook quotation was not re-read, because the reference corpus is not in this tree.

**A sanity check on the calculated price** (project owner, 2026-10-26: "Make
sure there is a sanity check for calculated agent price"). The project owner
asked for this in their own words. The three parts below are `PL-KZ99`'s
recommendation for how to meet it, and the session that builds this item
decides the details.

1. **The cost matches a published worked example.** The Gas Man Workbook
   prints delivered costs for two isoflurane exercises, at its default price
   of US$20.47 per 100 mL (Appendix C, printed p. 171). Exercise 14-1 runs 2 %
   at 8 L/min for 13 min, then 1.5 % to 60 min. The book gives $2.17 at
   13 min and $8.06 at 60 min (printed pp. 133-134). Exercise 14-2 runs 5 % at
   1 L/min for 13 min, then 2.7 % to 60 min, and gives $0.68 and $2.00
   (printed pp. 135-136). Both read at full text from the private reference
   corpus on 2026-10-26. A reference test runs both exercises end to end, from
   the simulator's delivered amount to the displayed text. Gas Man's
   isoflurane factor is 196 mL of vapour per mL of liquid, rounded to a whole
   number, and this model derives 195.8. So the test allows the cent's
   rounding plus 0.26 %, the most that rounding to 196 can move a cost. At
   60 min, Exercise 14-1 gives $8.07 here against the book's $8.06, inside
   that allowance. `PL-KZ99` checks the conversion half against the same four
   figures, with the delivered vapour worked out by hand.
2. **The readout shows its working.** Beside the cost, it shows the liquid
   volume and the price per mL that it multiplied, for example
   "39.4 mL x US$0.2047/mL". A reader can then check the product by eye.
3. **No cost is shown when one cannot be trusted.** The readout says why
   instead of showing a number when the price is unset, zero, negative or not
   finite, or when the delivered amount cannot be converted. Gas Man takes a
   bottle price and a bottle volume (`Set Cost...`, printed p. 15). Taking the
   price the same way, and showing the price per mL it implies, makes a bottle
   price typed into a per-mL field visible. That mistake multiplies the cost by the
   bottle volume in mL, which is 100 to 250 for the volatile agents in Gas
   Man's defaults (Appendix C, printed pp. 171-172). Whether to take the
   price per bottle is `PL-VJZK`'s decision, because `PL-VJZK` stores the
   price.

**Checked 2026-10-27 (`PL-0S0V`): a cost has no displayed precision yet.** `docs/MODEL.md` § "Displayed precision" now derives one precision per agent amount and unit, and leaves money to this item, because a cost's resolution depends on the reader's price. A cost readout needs its own derivation here, and `app/formatting.py`'s `AgentAmountPrecision` is the type for an agent amount that refuses a count finer than the derivation admits.
