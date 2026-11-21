---
id: PL-7KXN
title: A refused agent price entry is written back at every save and named at every launch, and the interface offers no way to clear it: Preferences.without_refused_entries has no caller
priority: P3
effort: M
status: done
classes: defect
feature: interface-matches-its-spec
touches: src/anesthesia_sim/app/preferences.py, src/anesthesia_sim/app/view_contract.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/views.py, src/anesthesia_sim/app/qt_agent_price.py, src/anesthesia_sim/app/agent_cost.py, docs/INTERFACE.md, docs/ARCHITECTURE.md, tests/unit/test_preferences.py, tests/integration/test_agent_cost_view.py, tests/integration/test_view_contract.py, tests/integration/test_layout_adapter.py, tests/integration/test_layout_keyboard.py
added: 2026-11-21
closed: 2026-11-21
pr: 2196
payoff: A learner whose preferences file holds an entry that no new price replaces can clear it from the agent cost View, and is no longer told about it at every launch
tests: tests/unit/test_preferences.py::test_preferences_say_whether_they_keep_a_refused_entry, tests/integration/test_agent_cost_view.py::test_the_reader_can_discard_refused_entries_and_the_next_launch_names_none, tests/integration/test_agent_cost_view.py::test_keeping_the_refused_entries_changes_nothing, tests/integration/test_agent_cost_view.py::test_no_discard_is_offered_while_no_entry_is_refused
---

**Problem.** A refused agent price entry is written back at every save and named at every launch, and the interface offers no way to clear it: Preferences.without_refused_entries has no caller

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/ARCHITECTURE.md` § "User state: the reader's preferences" says that a price entry which names no agent is refused, written back at every save, and named in the notice at every launch. That is what the code does. The docstring of `Preferences.without_refused_entries` in `app/preferences.py` says "The interface offers this so that the reader can clear a refused entry". No code under `src/` calls it. Only `tests/unit/test_preferences.py` does.

**Why it matters.** A reader whose preferences file holds a refused entry reads the same notice at every launch and cannot clear it without editing the file by hand.

**Decided here** (2026-11-21, over deleting the method): the agent cost View offers to discard the refused entries beside the notice that names them, and asks the reader to confirm, because the discard cannot be undone.

**Done when.** The reader can discard refused entries from the agent cost View, a test discards one and reads a launch with no notice, and the docstring says what the interface offers.

**Built 2026-11-21.** Under the notice that names the refused entries, the agent cost View shows a button, "Discard the refused entries", while the preferences hold one (`Preferences.holds_refused_entries`). Pressing it replaces the button, in its own place, with the warning "Discarding removes the refused entries from the preferences file. This cannot be undone." and two buttons, "Discard them" and "Keep them". "Keep them" takes the keyboard focus. "Discard them" asks the dashboard through the new `ViewRequests.refused_entries_discard`, and the dashboard saves the preferences without the refused entries and draws at once. The widget is `RefusedEntriesDiscard` in `app/qt_agent_price.py`. The question is asked in the View, not in a dialog, so nothing opens over the readouts while a run plays (`PL-CHX0` records that concern for the window that edits marks). The wording and the placement are placeholders.

**Generator check.** One-off. The fact is whether the interface offers the discard that `Preferences.without_refused_entries` documents. The method was written with its docstring and no View was given the control. Found by `PL-5FMC`, the check of the interface documents that the project owner asked for.

**Documents checked.** `docs/INTERFACE.md` § "A cost at the reader's price" (changed), `docs/ARCHITECTURE.md` § "User state: the reader's preferences" and its file list (both changed), `docs/MODEL.md` and `README.md` (neither describes refused entries).

**Blind review, 2026-11-21.** Both passes found two things. Discarding the refused entries emptied a price that the reader had typed and not yet set, because the form filled its fields again whenever the agent's refused entry came or went. The form now fills them again only when the stored price changes. The button that discards stood where the offer had stood, so a second click on the offer could confirm the discard. "Keep them" now stands there, and "Discard them" stands after it. `test_discarding_a_refused_entry_keeps_what_the_reader_has_typed` and `test_the_button_that_keeps_refused_entries_stands_where_the_offer_stood` check them.
