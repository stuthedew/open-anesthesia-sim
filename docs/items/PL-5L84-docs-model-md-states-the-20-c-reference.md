---
id: PL-5L84
title: docs/MODEL.md states the 20 °C reference condition in 29 paragraphs with no marker tying them to core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS, so the numeric-paragraph check cannot read °C as a unit until each is tied
status: untriaged
feature: model-claims-held-by-tests
added: 2026-11-03
---

**Problem.** `docs/MODEL.md` states the 20 °C reference condition, behind every displayed millilitres-of-liquid figure, in 29 paragraphs. The value lives in `core/liquid_agent.py` as `REFERENCE_TEMPERATURE_CELSIUS = 20.0`, and in each agent file as `liquid_density.measured_at_celsius = 20.0`. Nothing ties those paragraphs to it, so a change to the reference temperature would leave them stale with no refusal.

**Found by.** Both blind review passes on `PL-XQXK` (#1976). That branch first listed °C as a unit no value is stored in, which would have made "20 °C" unmatchable for good. Reading °C as a stored unit instead raised 29 untied-restatement errors, all this one value. `PL-XQXK` left °C and grams in no unit list, which keeps the reading `main` had: a figure in °C is read as a bare number.

**Done when.** `tools/doc_check.py` maps the `_celsius` ending to °C in `UNIT_ENDINGS` and lists °C in `PROSE_UNITS`. Each of the 29 paragraphs carries a `provenance:` marker naming `core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS = 20.0`, or a `not-restated:` marker where 20 °C only coincides (such as the 37 °C comparison's companion figure). `doc_check.py check` reports no errors.
