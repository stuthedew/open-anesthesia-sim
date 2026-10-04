---
id: PL-HSFV
title: RunDefinition propagates an UptakeEquationSettings whose flows are outside the supported ranges - cardiac output 1000 L/min, a hundred times the supported maximum, ran on 2026-10-04 - because the settings record checks only that the tissue flows sum to cardiac output, and the range guards run only in the compartments' constructors and setters, which a run built from a settings record never calls
status: untriaged
feature: numerical-domain
added: 2026-10-04
---

**Problem.** RunDefinition propagates an UptakeEquationSettings whose flows are outside the supported ranges - cardiac output 1000 L/min, a hundred times the supported maximum, ran on 2026-10-04 - because the settings record checks only that the tissue flows sum to cardiac output, and the range guards run only in the compartments' constructors and setters, which a run built from a settings record never calls
