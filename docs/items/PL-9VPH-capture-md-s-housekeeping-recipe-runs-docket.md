---
id: PL-9VPH
title: capture.md's housekeeping recipe runs docket new before it sets touches, on a clean tree, so the near-duplicate search has no paths and never runs: PL-4CPP duplicated PL-BYN2 at similarity 0.29 against the 0.15 floor
status: untriaged
touches: .claude/skills/docket/modes/capture.md
added: 2026-09-23
---

**Problem.** capture.md's housekeeping recipe runs docket new before it sets touches, on a clean tree, so the near-duplicate search has no paths and never runs: PL-4CPP duplicated PL-BYN2 at similarity 0.29 against the 0.15 floor

**Mechanism.** `near_duplicates` in `subprojects/docket/src/docket/duplicates.py`
returns nothing without paths ("No paths means no answer"), and `PL-THLT`
supplies them from the working tree only when the capture declares none. A tree
is clean when an item is filed before its work starts, which is the order
`.claude/skills/docket/modes/capture.md` § "Mode: housekeeping nobody filed"
prescribes: `bin/docket new "..."`, then `bin/docket set ... --touches
docs/items`. So an item filed by that recipe never meets the search.

**Measured on the instance, 2026-09-22.** `similarity` between the two titles
is 0.29, and `docs/items` covers `PL-BYN2`'s declared path, so `bin/docket new
--touches docs/items "..."` would have printed `PL-BYN2`. The flag already
exists on `new`; the recipe's example simply does not use it.
