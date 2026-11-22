---
id: PL-M3J9
title: No test pins desflurane's five-minute washout ratio at the default fresh gas flow of 4 L/min (0.285), which docs/MODEL.md Known limitations quotes; only the 10 L/min figure is pinned, in MODELLED_ELIMINATION_RATIOS
status: done
feature: model-spec-accuracy
touches: tests/reference/test_published_wash_in_and_elimination.py, docs/MODEL.md
added: 2026-11-21
closed: 2026-11-22
pr: 2199
tests: tests/reference/test_published_wash_in_and_elimination.py::test_desflurane_washout_at_the_default_fresh_gas_flow_regression_pin
---

**Problem.** No test pins desflurane's five-minute washout ratio at the default fresh gas flow of 4 L/min (0.285), which docs/MODEL.md Known limitations quotes; only the 10 L/min figure is pinned, in MODELLED_ELIMINATION_RATIOS

**Generator check.** Not a generator. A figure was quoted in `docs/MODEL.md` before any test pinned it, once, in `PL-S64T`'s rewrite on the same branch.

**Found by.** The two blind review passes on `PL-S64T` (the desflurane washout limitation), 2026-11-21. `docs/MODEL.md` § "Known limitations", in the paragraph that opens "Desflurane's five-minute washout disagrees with the published human measurement", now quotes the five-minute $`F_A/F_{A0}`$ at the default settings, 0.285 at a fresh gas flow of 4 L/min, and the faster falls 0.126 (8 L/min of fresh gas and of alveolar ventilation) and 0.130 (10 L/min of fresh gas, cardiac output 2 L/min). They are dated simulations. `MODELLED_ELIMINATION_RATIOS` in `tests/reference/test_published_wash_in_and_elimination.py` pins only the 10 L/min figure, and `test_elimination_is_dominated_by_the_rebreathing_circuit` asserts only the 1 and 10 L/min ends. A change to the circuit, the patient or the method of stepping would leave the three quoted figures wrong with no failing test.

**Done when.** A test in `tests/reference/test_published_wash_in_and_elimination.py` pins the figure at the default fresh gas flow to the precision the paragraph prints, using `_eliminate("desflurane", ...)` after its 30-minute wash-in, and the paragraph's note for developers names it. The 8 L/min and low cardiac output figures were dropped from the paragraph on 2026-11-22 (see below), so they need no pin.

**Built 2026-11-22.** The project owner answered the question on `PL-S64T`'s pull request, whether the paragraph should give figures or describe the regions in words, with "Whatever best practice is. Look it up." The guidance read for it asks for the validation results themselves, the conditions they hold under and the limitations. The ISPOR-SMDM task force on model transparency and validation lists "validation methods and results; and limitations" in the non-technical description every model should have (Eddy et al., Med Decis Making 2012;32(5):733-43, doi:10.1177/0272989X12454579, abstract read through PubMed). The FDA guidance "Assessing the Credibility of Computational Modeling and Simulation in Medical Device Submissions" (17 November 2023, full text read from fda.gov) recommends judging the model's agreement with the comparator against quantitative accuracy targets where they can be set, assessing how far the validation conditions apply to the conditions of use, and stating each limitation explicitly (§ VI.D "Adequacy Assessment", pages 34 and 35, and the glossary's definition of applicability). A quoted figure that no test checks can go wrong silently, so the figures stay and are pinned.

**Revised 2026-11-22.** The second blind review of the pull request found that comparing each on-screen figure with the volunteers' mean compares unlike conditions: the volunteers breathed through a non-rebreathing circuit, and the screen always includes the circle system. That is the applicability question the FDA guidance asks about. The paragraph now gives the figures at the default fresh gas flow and at 10 L/min beside the circuit-removed figure, states that the two conditions differ, and drops the settings at which the screen falls faster than the volunteers. So `test_desflurane_washout_at_the_default_fresh_gas_flow_regression_pin` replaces the three-figure test. It reads the default flow from the circuit's parameter file and pins 0.2852 to `ELIMINATION_RATIO_PIN_TOLERANCE`. It was checked to fail with the stored figure moved by 0.001. The 10 L/min and circuit-removed figures were already pinned, and the note for developers names all three tests.

