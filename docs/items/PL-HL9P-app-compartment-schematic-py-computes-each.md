---
id: PL-HL9P
title: app/compartment_schematic.py computes each compartment's share of the agent held and each container's fill, but it imports app/dashboard_frame.py, which loads PySide6, so .claude/rules/ui-calculations.md's rule that a display derivation sits in a module loading no toolkit does not hold for it
status: untriaged
added: 2026-11-10
---

**Problem.** app/compartment_schematic.py computes each compartment's share of the agent held and each container's fill, but it imports app/dashboard_frame.py, which loads PySide6, so .claude/rules/ui-calculations.md's rule that a display derivation sits in a module loading no toolkit does not hold for it
