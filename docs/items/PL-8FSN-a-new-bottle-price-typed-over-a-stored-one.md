---
id: PL-8FSN
title: A new bottle price typed over a stored one keeps the stored price's date unless the reader changes it, so the cost reads 'as of' the earlier date
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
---

**Problem.** A new bottle price typed over a stored one keeps the stored price's date unless the reader changes it, so the cost reads 'as of' the earlier date

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `PriceEntry._fill` in `app/qt_agent_price.py` sets the date field to today for an agent with no stored price, and to the stored price's date for an agent that has one. `test_a_price_change_redraws_the_cost_at_once_while_paused_and_survives_a_restart` in `tests/integration/test_agent_cost_view.py` asserts the stored date, `QDate(2008, 3, 5)`, for an agent with a stored price. A reader who types a new bottle price over the stored one and leaves the date alone therefore saves the new price under the earlier date. Nothing on the form points at the date.

**Why it matters.** `docs/INTERFACE.md` § "A cost at the reader's price" shows a cost with the date its price applies from, because a price goes stale from the day it was quoted. A new price saved under an old date is shown as older than it is.

**Decided here** (2026-11-21, over leaving the date and marking the field): when the reader changes the price or the bottle volume of a stored entry and has not edited the date, the form sets the date to the day of entry before saving. A reader who edits the date keeps the date they typed.

**Done when.** A test types a new price over a stored one without touching the date and reads the day of entry from the saved price, a second test edits the date and reads that date, and the document's paragraph on the date field says what the form does.
