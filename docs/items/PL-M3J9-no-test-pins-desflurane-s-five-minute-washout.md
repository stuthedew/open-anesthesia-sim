---
id: PL-M3J9
title: No test pins desflurane's five-minute washout ratio at the default fresh gas flow of 4 L/min (0.285), which docs/MODEL.md Known limitations quotes; only the 10 L/min figure is pinned, in MODELLED_ELIMINATION_RATIOS
status: untriaged
feature: model-spec-accuracy
added: 2026-11-21
---

**Problem.** No test pins desflurane's five-minute washout ratio at the default fresh gas flow of 4 L/min (0.285), which docs/MODEL.md Known limitations quotes; only the 10 L/min figure is pinned, in MODELLED_ELIMINATION_RATIOS

**Found by.** The two blind review passes on `PL-S64T` (the desflurane washout limitation), 2026-11-21. `docs/MODEL.md` § "Known limitations", in the paragraph that opens "Desflurane's five-minute washout disagrees with the published human measurement", now quotes the five-minute $`F_A/F_{A0}`$ at the default settings, 0.285 at a fresh gas flow of 4 L/min, and the faster falls 0.126 (8 L/min of fresh gas and of alveolar ventilation) and 0.130 (10 L/min of fresh gas, cardiac output 2 L/min). They are dated simulations. `MODELLED_ELIMINATION_RATIOS` in `tests/reference/test_published_wash_in_and_elimination.py` pins only the 10 L/min figure, and `test_elimination_is_dominated_by_the_rebreathing_circuit` asserts only the 1 and 10 L/min ends. A change to the circuit, the patient or the method of stepping would leave the three quoted figures wrong with no failing test.

**Done when.** A test in `tests/reference/test_published_wash_in_and_elimination.py` asserts the three figures to the precision the paragraph prints, using `_eliminate("desflurane", ...)` after its 30-minute wash-in, and the paragraph's note for developers names it.
