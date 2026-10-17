---
id: PL-8LQZ
title: A TissueGroup whose volume and tissue:gas coefficient multiply to a capacity that underflows to 0.0 (1e-200 x 1e-200) passes construction and require_room_for_the_agent_held, and partial_pressure_fraction then raises ZeroDivisionError rather than a refusal: the mirror of PL-FNH3's capacity overflowing to inf (found reviewing PL-19Y0)
status: untriaged
added: 2026-10-17
---

**Problem.** A TissueGroup whose volume and tissue:gas coefficient multiply to a capacity that underflows to 0.0 (1e-200 x 1e-200) passes construction and require_room_for_the_agent_held, and partial_pressure_fraction then raises ZeroDivisionError rather than a refusal: the mirror of PL-FNH3's capacity overflowing to inf (found reviewing PL-19Y0)
