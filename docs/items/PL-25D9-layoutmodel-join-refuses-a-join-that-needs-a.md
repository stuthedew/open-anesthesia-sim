---
id: PL-25D9
title: LayoutModel.join refuses a join that needs a cut beside an Area narrower than BORDER_ALIGNMENT_TOLERANCE, though a tree holding the result exists: column[row(0.5, 5e-10, 0.5-5e-10)[1,2,3], row[4,5]] refuses joining 1 and 4, where a 2e-9 sliver joins
status: untriaged
feature: layout-sliver-areas
added: 2026-10-18
---

**Problem.** LayoutModel.join refuses a join that needs a cut beside an Area narrower than BORDER_ALIGNMENT_TOLERANCE, though a tree holding the result exists: column[row(0.5, 5e-10, 0.5-5e-10)[1,2,3], row[4,5]] refuses joining 1 and 4, where a 2e-9 sliver joins
