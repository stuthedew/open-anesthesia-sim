---
id: PL-R51H
title: The agent price form's four entry fields declare no colours, and neither colour sweep test builds four of the eight Views, so a control added to one of them passes both tests undeclared
priority: P3
effort: S
status: done
classes: defect, test
feature: interface-matches-its-spec
milestone: v0.6.19
touches: src/anesthesia_sim/app/qt_agent_price.py, docs/INTERFACE.md, tests/integration/simulation_view/simulation_view_support.py, tests/integration/simulation_view/test_simulation_view_foreground.py, tests/integration/test_dark_appearance.py
added: 2026-11-21
closed: 2026-11-21
pr: 2196
payoff: A control added to any View that declares no colour now fails both colour tests, so a learner on a dark desktop does not meet a dark field in a light form
tests: tests/integration/simulation_view/test_simulation_view_foreground.py::test_every_control_that_paints_its_own_content_declares_a_foreground, tests/integration/simulation_view/test_simulation_view_foreground.py::test_no_control_kind_is_exempted_from_declaring_a_foreground_without_cause, tests/integration/test_dark_appearance.py::test_no_content_widget_in_the_interface_paints_from_the_host_palette
---

**Problem.** The agent price form's four entry fields declare no colours, and neither colour sweep test builds four of the eight Views, so a control added to one of them passes both tests undeclared

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` § "Color contrast, and the standard this interface is held to" says that the foreground test "catches any control that declares no color, including one added later", and that the dark-appearance test "fails on any content widget that resolves to that palette". `PriceEntry.__init__` in `app/qt_agent_price.py` builds three `QLineEdit` fields and one `QDateEdit`, and passes none to `declare_interface_colours`. Both tests (`tests/integration/simulation_view/test_simulation_view_foreground.py` and `tests/integration/test_dark_appearance.py`) build the shipped Default Workspace, which holds four of the eight registered kinds of View. Neither builds `WashInView`, `AccountingView`, `AgentCostView` or `CompartmentSchematicView`.

Reproduction: build the dashboard as the two tests do, put the agent cost View into Area 1 with `view.layout_container.choose_view(AreaId(1), view_registry.AGENT_COST)`, and run each test's own walk (`_content_painters` and `_undeclared`). Output:

```
Default Workspace (what the tests build): foreground walk -> []
Default Workspace (what the tests build): dark-host walk  -> []
Default Workspace + agent cost View: foreground walk -> ['QDateEdit draws in #FF00FF', 'QLineEdit draws in #FF00FF']
Default Workspace + agent cost View: dark-host walk  -> ['QLineEdit Base=#1E1E1E Text=#FFFFFF', 'QLineEdit Base=#1E1E1E Text=#FFFFFF', 'QLineEdit Base=#1E1E1E Text=#FFFFFF', 'QDateEdit Base=#1E1E1E Text=#FFFFFF', 'QLineEdit Base=#1E1E1E Text=#FFFFFF']
with main()'s application palette: dark-host walk -> []
```

With all four extra Views shown, the foreground walk also names `SchematicCanvas` and `ShareBar`. Both paint with explicit theme pens, so they need entries in `FOREGROUND_NOT_DECLARED`, not a colour. `PL-VHBW` (the two dialogs missing from the foreground walk) is the related open item.

**Why it matters.** A learner sees nothing wrong today, because `main()` sets an application palette that covers the fields. The two tests do not give the guarantee that the document states: a control added to any of the four unbuilt kinds of View passes both.

**Done when.** Both tests build every registered kind of View, the four entry fields declare their colours, and the reproduction above prints two empty walks.

**Built 2026-11-21.** `every_registered_view` in `tests/integration/simulation_view/simulation_view_support.py` builds one Workspace with an Area for each kind in the registry, so a kind registered later is drawn with no edit to a test. Both colour tests now build the dashboard on it, over a case that can be branched, and each asserts that every registered kind is drawn and that no Area is too small for its View. The four entry fields of the price form declare this interface's colours with `declare_interface_colours`. `FOREGROUND_NOT_DECLARED` gains `SchematicCanvas` and `ShareBar`, each with its reason: both paint from pens and brushes they set themselves, and `tools/contrast_check.py` already measures those colours. Each test failed before the fields were declared and passes now.

One statement above is corrected. Before this change the foreground test built six of the eight kinds, through its own "Every View" Workspace, and missed the agent cost View and the compartment schematic. The dark-appearance test built four.

**Generator check.** No generator. The fact is which Views the two colour tests draw. Each test drew a layout written by hand, which stopped being every View when a kind was registered after it. `PL-VHBW` (the foreground test draws neither dialog) is the same fact for the two dialogs and stays open. Two items share the fact, and this change removes its cause for Views by reading the kinds from the registry. `PL-4L49`, which wrote the foreground test, closed on 2026-09-22, more than 30 days ago, so this is not recorded as a re-entry. Found by `PL-5FMC`, the check of the interface documents that the project owner asked for.

**Documents checked.** `docs/INTERFACE.md` § "Color contrast, and the standard this interface is held to" (changed), `docs/ARCHITECTURE.md`, `docs/MODEL.md` and `README.md` (none describes what the two tests draw).
