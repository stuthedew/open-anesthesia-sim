---
id: PL-HL9P
title: app/compartment_schematic.py computes each compartment's share of the agent held and each container's fill, but it imports app/dashboard_frame.py, which loads PySide6, so .claude/rules/ui-calculations.md's rule that a display derivation sits in a module loading no toolkit does not hold for it
status: dropped
added: 2026-11-10
closed: 2026-11-11
reason: Premise false: importing app/compartment_schematic.py loads no PySide6 or pyqtgraph module, on main on 2026-11-11 and at 50af1a2eb, the commit that filed this item. app/dashboard_frame.py imports no toolkit and names PySide6 only in its docstring.
---

**Problem.** app/compartment_schematic.py computes each compartment's share of the agent held and each container's fill, but it imports app/dashboard_frame.py, which loads PySide6, so .claude/rules/ui-calculations.md's rule that a display derivation sits in a module loading no toolkit does not hold for it
