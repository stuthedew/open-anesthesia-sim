---
id: PL-FNH3
title: VenousBloodCompartment and TissueGroup accept a volume and partition coefficient whose product overflows capacity_l to inf, so the venous pool's advance stores nan (an equilibrium of inf * 0.0) rather than refusing at build, and the pool accepts nan written straight onto agent_amount_l; the tissue refuses the nan at its __setattr__ (found reviewing PL-XWFP)
status: untriaged
added: 2026-10-12
---

**Problem.** VenousBloodCompartment and TissueGroup accept a volume and partition coefficient whose product overflows capacity_l to inf, so the venous pool's advance stores nan (an equilibrium of inf * 0.0) rather than refusing at build, and the pool accepts nan written straight onto agent_amount_l; the tissue refuses the nan at its __setattr__ (found reviewing PL-XWFP)
