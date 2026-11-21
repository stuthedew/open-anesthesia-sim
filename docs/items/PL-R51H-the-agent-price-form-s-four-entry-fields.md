---
id: PL-R51H
title: The agent price form's four entry fields declare no colours, and neither colour sweep test builds four of the eight Views, so a control added to one of them passes both tests undeclared
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
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
