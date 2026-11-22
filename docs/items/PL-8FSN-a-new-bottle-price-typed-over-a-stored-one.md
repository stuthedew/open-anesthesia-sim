---
id: PL-8FSN
title: A new bottle price typed over a stored one keeps the stored price's date unless the reader changes it, so the cost reads 'as of' the earlier date
priority: P3
effort: S
status: done
classes: defect
feature: interface-matches-its-spec
milestone: v0.6.19
touches: src/anesthesia_sim/app/agent_cost.py, src/anesthesia_sim/app/qt_agent_price.py, docs/INTERFACE.md, tests/unit/test_agent_cost.py, tests/integration/test_agent_cost_view.py
added: 2026-11-21
closed: 2026-11-21
pr: 2196
payoff: A learner who types a new bottle price over a stored one sees the date move to today before saving, so the cost is not shown as older than it is
tests: tests/unit/test_agent_cost.py::test_an_entry_that_states_another_price_is_dated_at_the_day_of_entry, tests/unit/test_agent_cost.py::test_an_entry_that_states_the_stored_price_keeps_its_date, tests/integration/test_agent_cost_view.py::test_a_price_typed_over_a_stored_one_is_dated_at_the_day_of_entry, tests/integration/test_agent_cost_view.py::test_a_date_the_reader_edits_is_kept_for_a_price_typed_over_a_stored_one
---

**Problem.** A new bottle price typed over a stored one keeps the stored price's date unless the reader changes it, so the cost reads 'as of' the earlier date

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `PriceEntry._fill` in `app/qt_agent_price.py` sets the date field to today for an agent with no stored price, and to the stored price's date for an agent that has one. `test_a_price_change_redraws_the_cost_at_once_while_paused_and_survives_a_restart` in `tests/integration/test_agent_cost_view.py` asserts the stored date, `QDate(2008, 3, 5)`, for an agent with a stored price. A reader who types a new bottle price over the stored one and leaves the date alone therefore saves the new price under the earlier date. Nothing on the form points at the date.

**Why it matters.** `docs/INTERFACE.md` § "A cost at the reader's price" shows a cost with the date its price applies from, because a price goes stale from the day it was quoted. A new price saved under an old date is shown as older than it is.

**Decided here** (2026-11-21, over leaving the date and marking the field): when the reader changes the price or the bottle volume of a stored entry and has not edited the date, the form sets the date to the day of entry before saving. A reader who edits the date keeps the date they typed.

**Done when.** A test types a new price over a stored one without touching the date and reads the day of entry from the saved price, a second test edits the date and reads that date, and the document's paragraph on the date field says what the form does.

**Built 2026-11-21.** The date moves when the reader types, not when they save. While the reader has not edited the date, typing another bottle price, bottle volume or currency over a stored price shows the day of entry in the date field, and a line under the form says "Price date set to today, because this is a new price. Change the date if the price was quoted on another day." Typing the stored values again puts the stored date back. A date that the reader edits is kept, whatever they type afterwards. So the date field always shows the date that Set price saves, and the form changes no date that the reader cannot see. `entry_date` in `app/agent_cost.py` decides the date, and `PriceEntry` in `app/qt_agent_price.py` shows it. The wording of the line is a placeholder.

Two things differ from the decision as first written. The date moves for a changed currency as well as a changed price or volume, because USD 20.47 and CAD 20.47 are different prices. The date moves before the save and in view. A date changed only at the save would have been a change the reader had not seen, and a reader who entered a second price quoted on the stored price's own day could not have kept that day.

**Generator check.** One-off. The fact is which date a price typed over a stored one carries. The form filled the date from the stored price and nothing connected it to the other fields. Found by `PL-5FMC`, the check of the interface documents that the project owner asked for.

**Documents checked.** `docs/INTERFACE.md` § "A cost at the reader's price" (changed), `docs/ARCHITECTURE.md` § "User state: the reader's preferences" (nothing to change), `docs/MODEL.md` and `README.md` (neither describes the form's date).

**Blind review, 2026-11-21.** Pass 2 found that a mouse wheel turned over the date field stepped the date without focus, and that the form then kept the stepped date as the reader's. The field is now a `FocusedDateEdit`, which ignores the wheel until it has focus, as the form's selector does. `test_a_mouse_wheel_over_the_price_date_changes_nothing_until_it_has_focus` checks it.
