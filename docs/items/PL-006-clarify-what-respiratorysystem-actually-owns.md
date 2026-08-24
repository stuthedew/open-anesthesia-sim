---
id: PL-006
title: Clarify what `RespiratorySystem` actually owns
priority: P2
effort: M
status: needs-decision
classes: refactor
touches: src/anesthesia_sim/core/respiratory_system.py
added: 2026-08-23
---

**Problem.** `core/respiratory_system.py` bundles concerns beyond what its
name suggests. "Respiratory system" clinically means the patient's own
lungs and airways, which maps only to `alveoli`. `circuit` is the
anesthesia machine's breathing circuit — equipment, not patient physiology
— and `set_cardiac_output()` forwards to `patient.set_cardiac_output()`,
which is a circulatory concern.
**Why it matters.** The class is the entry point to the scientific core, so
a misleading name and boundary is what a cold reader hits first.
**Where.** `core/respiratory_system.py` and its call sites.
**Decision needed.** Either keep it a thin coordinator (its `advance()` and
accounting already mostly are) and drop the setter delegation so callers
reach `patient`, `circuit`, or `alveoli` directly; or rename it to name the
coupled machine-plus-patient system rather than just the respiratory piece.
**Done when.** The naming and the delegation boundary agree with each
other, call sites are updated, and reference tests are unchanged in
behavior.
